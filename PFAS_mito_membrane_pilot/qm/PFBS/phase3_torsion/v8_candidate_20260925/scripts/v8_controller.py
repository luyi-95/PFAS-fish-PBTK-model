#!/usr/bin/env python3
"""Frozen v8 candidate controller. Default action is OFFLINE AUDIT; --launch requires a future authorization receipt."""
import argparse, concurrent.futures, datetime, hashlib, json, os, re, shutil, signal, subprocess, sys, time
from pathlib import Path
from v8_static_audit import audit, sha
from v8_qc import evaluate

BUNDLE=Path(__file__).resolve().parents[1]
CAP=re.compile(r'Number of steps in this run=\s*(\d+)\s+maximum allowed number of steps=\s*(\d+)\.',re.I)
SCF_START=re.compile(r'\(Enter /opt/g16/l(?:502|508|801|804)\.exe\)|SCF Done:|\bEUMP2\s*=',re.I)
VERSION=re.compile(r'Gaussian 16:\s+ES64L-G16RevC\.02')
PARSER_ERROR=re.compile(r'Error termination|QPErr|Wanted an integer|End of file in ZSymb|Unknown keyword',re.I)
MAX_CONCURRENT=4

def utc(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write_new(path,obj):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as f:
        json.dump(obj,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
def append(path,obj):
    with Path(path).open('a',encoding='utf-8') as f:
        f.write(json.dumps(obj,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
def ps_gaussian():
    p=subprocess.run(['ps','-eo','pid=,args='],capture_output=True,text=True,check=True)
    out=[]
    for line in p.stdout.splitlines():
        if re.search(r'(^|\s)/opt/g16/(?:g16|l\d+\.exe)(?:\s|$)',line): out.append(line.strip())
    return out
def disk_ok(path): return shutil.disk_usage(path).free>=20*1024**3
def profile_ok(manifest):
    paths=manifest['gaussian_profile_sha256']
    for path,want in paths.items():
        p=Path(path)
        if not p.is_file() or not os.access(p,os.X_OK) or sha(p)!=want: return False,path
    return True,None
def prelaunch(bundle,auth):
    root=Path(bundle).resolve(); status=audit(root); m=json.loads((root/'package_manifest.json').read_text())
    if status['status']!='PASS': raise RuntimeError('static package audit failed')
    auth=json.loads(Path(auth).read_text())
    if auth.get('package_sha256')!=status['package_sha256'] or auth.get('sol_high_status')!='APPROVE_FOR_PRODUCTION_LAUNCH' or auth.get('user_authorization')!='GRANTED_V8_20_ABSOLUTE' or not re.fullmatch('[0-9a-f]{40}',auth.get('git_commit_sha','')):
        raise RuntimeError('missing exact Sol High and separate user launch authorization')
    run=Path(m['external_run_root'])
    if run.exists(): raise RuntimeError('runtime root already exists; no retry')
    if ps_gaussian(): raise RuntimeError('active or ambiguous Gaussian process')
    good,bad=profile_ok(m)
    if not good: raise RuntimeError('Gaussian C.02 executable profile mismatch: '+str(bad))
    if not disk_ok(run.parent): raise RuntimeError('shared filesystem free space below 20 GiB')
    return status,m,auth

def stop_own(proc):
    if proc.poll() is None:
        os.killpg(proc.pid,signal.SIGTERM)
        try: proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            if proc.poll() is None: os.killpg(proc.pid,signal.SIGKILL)
            proc.wait()

def one_point(bundle,row,run,event_file):
    jid=row['job_id']; d=run/jid; p=None; early=None; cap=None; started=time.monotonic()
    try:
        d.mkdir(exist_ok=False)
        scratch=Path(row['scratch']); scratch.mkdir(exist_ok=False)
        if any(Path(row[k]).exists() for k in ('checkpoint','log','launch_record','runtime_qa')): raise FileExistsError('job-local artifact collision')
        inp=bundle/row['input_relative']
        if sha(inp)!=row['input_sha256']: raise RuntimeError('input hash mismatch')
        write_new(row['launch_intent'],{'job_id':jid,'input_sha256':row['input_sha256'],'package_sha256':sha(bundle/'SHA256SUMS'),'created_utc':utc(),'retry_count':0})
        env=os.environ.copy();env['g16root']='/opt';env['GAUSS_SCRDIR']=str(scratch)
        cmd='export g16root=/opt; source /opt/g16/bsd/g16.profile >/dev/null 2>&1 || exit 88; exec /opt/g16/g16'
        with inp.open('rb') as fi, Path(row['log']).open('xb') as fo:
            p=subprocess.Popen(['/bin/bash','-c',cmd],stdin=fi,stdout=fo,stderr=subprocess.STDOUT,cwd=d,env=env,start_new_session=True,close_fds=True)
        write_new(row['launch_record'],{'job_id':jid,'pid':p.pid,'pgid':p.pid,'invoked_utc':utc(),'gaussian_invoked':True,'input_sha256':row['input_sha256']})
        append(event_file,{'event':'GAUSSIAN_INVOKED','job_id':jid,'pid':p.pid,'utc':utc()})
        while p.poll() is None:
            log=Path(row['log']).read_text(errors='replace')
            found=CAP.findall(log)
            if len(found)>1 and len(set(found))>1: early='CONFLICTING_EFFECTIVE_CAP';break
            if found:
                requested,allowed=map(int,found[0]);cap=allowed
                if requested!=200 or allowed!=200: early='EFFECTIVE_MAX_STEPS_NOT_200';break
                if not VERSION.search(log): early='C02_VERSION_NOT_CONFIRMED';break
                break
            if PARSER_ERROR.search(log): early='INPUT_PARSER_OR_EARLY_FAILURE';break
            if SCF_START.search(log): early='CAP_UNRESOLVED_BEFORE_SCF_MP2';break
            if time.monotonic()-started>300: early='CAP_UNRESOLVED_TIMEOUT';break
            time.sleep(1)
        if cap!=200 or early:
            if early is None: early='EXITED_BEFORE_EFFECTIVE_CAP'
            stop_own(p)
            result={'job_id':jid,'point_state':'POINT_REVIEW','failure_class':early,'effective_max_steps':cap,'exit_code':p.returncode,
                    'log_sha256':sha(row['log']) if Path(row['log']).is_file() else None,'input_sha256':sha(inp),'gaussian_invoked':True,
                    'energy_profile_eligible':False,'authorization_retry':False}
        else:
            while p.poll() is None: time.sleep(5)
            result=evaluate(bundle,row,p.returncode,cap,formchk=True)
            result['gaussian_invoked']=True;result['authorization_retry']=False
            if result['point_state']=='POINT_REVIEW': result['failure_class']='LOCAL_SCIENTIFIC_OR_TERMINAL_QC_REVIEW'
        result['finished_utc']=utc();write_new(row['runtime_qa'],result)
        append(event_file,{'event':'POINT_TERMINAL','job_id':jid,'point_state':result['point_state'],'failure_class':result.get('failure_class'),'utc':utc()})
        return result
    except Exception as e:
        if p is not None: stop_own(p)
        result={'job_id':jid,'point_state':'POINT_REVIEW','failure_class':'EXECUTION_OR_PROVENANCE_EXCEPTION','error':type(e).__name__+':'+str(e),
                'gaussian_invoked':p is not None,'energy_profile_eligible':False,'authorization_retry':False,'finished_utc':utc()}
        if d.is_dir() and not Path(row['runtime_qa']).exists(): write_new(row['runtime_qa'],result)
        append(event_file,{'event':'POINT_EXCEPTION','job_id':jid,'error':result['error'],'utc':utc()})
        return result

def launch(bundle,auth_file):
    bundle=Path(bundle).resolve();status,m,auth=prelaunch(bundle,auth_file);run=Path(m['external_run_root']);run.mkdir(exist_ok=False)
    write_new(run/'queue_launch_claim.json',{'package_sha256':status['package_sha256'],'git_commit_sha':auth['git_commit_sha'],
        'user_authorization':'GRANTED_V8_20_ABSOLUTE','job_ids':[r['job_id'] for r in m['jobs']],'created_utc':utc(),'max_concurrency':MAX_CONCURRENT})
    event=run/'controller_events.jsonl';results=[];pending=iter(m['jobs']);active={};systemic=None;class_counts={}
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENT) as pool:
        def submit_one():
            try: row=next(pending)
            except StopIteration: return False
            f=pool.submit(one_point,bundle,row,run,event);active[f]=row['job_id'];return True
        for _ in range(MAX_CONCURRENT): submit_one()
        while active:
            done,_=concurrent.futures.wait(active,return_when=concurrent.futures.FIRST_COMPLETED)
            for f in done:
                jid=active.pop(f);res=f.result();results.append(res);fc=res.get('failure_class')
                if fc:
                    class_counts[fc]=class_counts.get(fc,0)+1
                    if fc in ('EXECUTION_OR_PROVENANCE_EXCEPTION','CONFLICTING_EFFECTIVE_CAP') or class_counts[fc]>=2 and fc in ('EFFECTIVE_MAX_STEPS_NOT_200','C02_VERSION_NOT_CONFIRMED','INPUT_PARSER_OR_EARLY_FAILURE','CAP_UNRESOLVED_BEFORE_SCF_MP2','CAP_UNRESOLVED_TIMEOUT'):
                        systemic='SYSTEMIC_'+fc
                if not disk_ok(run): systemic='SYSTEMIC_FILESYSTEM_RESOURCE'
                if not systemic: submit_one()
    summary={'state':'STOPPED_SYSTEMIC' if systemic else 'COMPLETE_WITH_POINT_REVIEW' if any(x['point_state']!='PASS' for x in results) else 'ALL_20_PASS',
             'systemic_failure':systemic,'package_sha256':status['package_sha256'],'results':results,'submitted_count':len(results),
             'unsubmitted_job_ids':[r['job_id'] for r in m['jobs'] if r['job_id'] not in {x['job_id'] for x in results}],
             'completed_utc':utc(),'reverse_scan':'NOT_AUTHORIZED','MD_RUN_AUTHORIZATION':'NOT_GRANTED'}
    write_new(run/'terminal_summary.json',summary);return summary

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--bundle',type=Path,default=BUNDLE);ap.add_argument('--launch',action='store_true');ap.add_argument('--authorization-file',type=Path)
    args=ap.parse_args()
    if args.launch:
        if args.authorization_file is None: ap.error('future launch requires --authorization-file')
        print(json.dumps(launch(args.bundle,args.authorization_file),indent=2))
    else: print(json.dumps(audit(args.bundle),indent=2))
