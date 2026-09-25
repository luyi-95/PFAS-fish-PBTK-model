#!/usr/bin/env python3
"""Frozen v8 candidate controller. Default action is OFFLINE AUDIT; --launch requires a future authorization receipt."""
import argparse, concurrent.futures, datetime, hashlib, json, os, re, shutil, signal, subprocess, sys, threading, time
from pathlib import Path
from v8_static_audit import audit, sha
from v8_qc import evaluate

BUNDLE=Path(__file__).resolve().parents[1]
CAP=re.compile(r'Number of steps in this run=\s*(\d+)\s+maximum allowed number of steps=\s*(\d+)\.',re.I)
SCF_START=re.compile(r'\(Enter /opt/g16/l(?:502|508|801|804)\.exe\)|SCF Done:|\bEUMP2\s*=',re.I)
VERSION=re.compile(r'Gaussian 16:\s+ES64L-G16RevC\.02')
PARSER_ERROR=re.compile(r'Error termination|QPErr|Wanted an integer|End of file in ZSymb|Unknown keyword',re.I)
MAX_CONCURRENT=4
EVENT_LOCK=threading.Lock()

def utc(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write_new(path,obj):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as f:
        json.dump(obj,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
def append(path,obj):
    with EVENT_LOCK:
        with Path(path).open('a',encoding='utf-8') as f:
            f.write(json.dumps(obj,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
def process_scan(proc_root=Path('/proc')):
    """Fail closed on Gaussian names, link executables, and ambiguous wrappers."""
    active=[]; ambiguous=[]
    try: entries=list(proc_root.iterdir())
    except Exception as e: return {'active':[],'ambiguous':['proc_enumeration:'+str(e)]}
    for p in entries:
        if not p.name.isdigit() or int(p.name)==os.getpid(): continue
        try: comm=(p/'comm').read_text(errors='replace').strip().lower()
        except (FileNotFoundError,ProcessLookupError): continue
        except Exception as e: ambiguous.append({'pid':p.name,'phase':'comm','error':str(e)});continue
        if comm in ('g16','g09') or re.fullmatch(r'l\d+\.exe',comm):
            active.append({'pid':p.name,'comm':comm,'detected_by':'comm'});continue
        try: exe=os.readlink(p/'exe').lower()
        except (FileNotFoundError,ProcessLookupError): exe=''
        except PermissionError: exe=''
        except Exception as e: ambiguous.append({'pid':p.name,'phase':'exe','error':str(e)});continue
        if re.search(r'/(?:g16|g09|l\d+\.exe)(?:\s|$)',exe):
            active.append({'pid':p.name,'comm':comm,'exe':exe,'detected_by':'exe'});continue
        if comm in ('bash','sh','dash','zsh','ksh','csh','tcsh'):
            try: argv=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')
            except (FileNotFoundError,ProcessLookupError): continue
            except Exception as e: ambiguous.append({'pid':p.name,'phase':'wrapper_cmdline','error':str(e)});continue
            if re.search(r'\b(?:exec\s+)?(?:/\S*/)?g(?:16|09)(?:\s|$)',argv):
                active.append({'pid':p.name,'comm':comm,'detected_by':'wrapper_cmdline'})
    return {'active':active,'ambiguous':ambiguous}
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
    auth=json.loads(Path(auth).read_text());review=auth.get('sol_high_review',{});user=auth.get('user_launch_authorization',{})
    commit=review.get('git_commit_sha','')
    if review.get('package_sha256')!=status['package_sha256'] or review.get('status')!='APPROVE_FOR_PRODUCTION_LAUNCH' or not re.fullmatch('[0-9a-f]{40}',commit):
        raise RuntimeError('missing exact hash-bound Sol High review')
    if user.get('package_sha256')!=status['package_sha256'] or user.get('git_commit_sha')!=commit or user.get('status')!='GRANTED_V8_20_ABSOLUTE':
        raise RuntimeError('missing separate user authorization bound to the reviewed Git commit and package hash')
    remote=subprocess.run(['git','ls-remote',m['git_remote'],'refs/heads/'+m['git_branch']],capture_output=True,text=True,check=True,timeout=30)
    observed=remote.stdout.split()[0] if remote.stdout.split() else None
    if observed!=commit: raise RuntimeError('reviewed Git commit does not match provenance branch HEAD')
    run=Path(m['external_run_root'])
    if run.exists(): raise RuntimeError('runtime root already exists; no retry')
    scan=process_scan()
    if scan['active'] or scan['ambiguous']: raise RuntimeError('active or ambiguous Gaussian process: '+json.dumps(scan))
    good,bad=profile_ok(m)
    if not good: raise RuntimeError('Gaussian C.02 executable profile mismatch: '+str(bad))
    if not disk_ok(run.parent): raise RuntimeError('shared filesystem free space below 20 GiB')
    return status,m,{'reviewed_git_commit_sha':commit,'raw':auth}

def stop_own(proc):
    if proc.poll() is None:
        os.killpg(proc.pid,signal.SIGTERM)
        try: proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            if proc.poll() is None: os.killpg(proc.pid,signal.SIGKILL)
            proc.wait()

def record_gaussian_invocation(run,row,proc,event_file,evidence):
    jid=row['job_id']
    commit=json.loads((run/'queue_launch_claim.json').read_text())['git_commit_sha']
    write_new(run/jid/'gaussian_invocation_evidence.json',{'job_id':jid,'pid':proc.pid,'evidence':evidence,'observed_utc':utc(),
        'input_sha256':row['input_sha256'],'package_sha256':sha(BUNDLE/'SHA256SUMS'),'git_commit_sha':commit})
    try:
        write_new(run/'queue_authorization_consumed.json',{'first_confirmed_job_id':jid,'evidence':evidence,'observed_utc':utc(),
            'package_sha256':sha(BUNDLE/'SHA256SUMS'),'git_commit_sha':commit})
    except FileExistsError: pass
    append(event_file,{'event':'GAUSSIAN_INVOCATION_CONFIRMED','job_id':jid,'pid':proc.pid,'evidence':evidence,'utc':utc()})

def one_point(bundle,row,run,event_file):
    jid=row['job_id']; d=run/jid; p=None; early=None; cap=None; confirmed=False; started=time.monotonic()
    try:
        d.mkdir(exist_ok=False)
        scratch=Path(row['scratch']); scratch.mkdir(exist_ok=False)
        if any(Path(row[k]).exists() for k in ('checkpoint','log','launch_record','runtime_qa')): raise FileExistsError('job-local artifact collision')
        inp=bundle/row['input_relative']
        if sha(inp)!=row['input_sha256']: raise RuntimeError('input hash mismatch')
        write_new(row['launch_intent'],{'job_id':jid,'input_sha256':row['input_sha256'],'package_sha256':sha(bundle/'SHA256SUMS'),'created_utc':utc(),'retry_count':0})
        env=os.environ.copy();env['g16root']='/opt';env['GAUSS_SCRDIR']=str(scratch)
        cmd='export g16root=/opt; source /opt/g16/bsd/g16.profile >/dev/null 2>&1 || exit 88; test -n "${GAUSS_EXEDIR:-}" || exit 88; exec /opt/g16/g16'
        with inp.open('rb') as fi, Path(row['log']).open('xb') as fo:
            p=subprocess.Popen(['/bin/bash','-c',cmd],stdin=fi,stdout=fo,stderr=subprocess.STDOUT,cwd=d,env=env,start_new_session=True,close_fds=True)
        write_new(row['launch_record'],{'job_id':jid,'pid':p.pid,'pgid':p.pid,'wrapper_started_utc':utc(),
            'state':'WRAPPER_STARTED_GAUSSIAN_UNVERIFIED','input_sha256':row['input_sha256']})
        append(event_file,{'event':'WRAPPER_STARTED_GAUSSIAN_UNVERIFIED','job_id':jid,'pid':p.pid,'utc':utc()})
        while True:
            log=Path(row['log']).read_text(errors='replace')
            if not confirmed:
                evidence=None
                if VERSION.search(log): evidence='C02_BANNER_IN_RAW_LOG'
                elif p.poll() is None:
                    try:
                        if os.readlink(f'/proc/{p.pid}/exe')=='/opt/g16/g16': evidence='PROC_EXE_IS_PINNED_G16'
                    except (FileNotFoundError,ProcessLookupError,PermissionError): pass
                if evidence:
                    record_gaussian_invocation(run,row,p,event_file,evidence);confirmed=True
            found=CAP.findall(log)
            if len(found)>1 and len(set(found))>1: early='CONFLICTING_EFFECTIVE_CAP';break
            if found:
                requested,allowed=map(int,found[0]);cap=allowed
                if requested!=200 or allowed!=200: early='EFFECTIVE_MAX_STEPS_NOT_200';break
                if not VERSION.search(log): early='C02_VERSION_NOT_CONFIRMED';break
                first_scf=SCF_START.search(log);first_cap=CAP.search(log)
                if first_scf and first_scf.start()<first_cap.start(): early='CAP_REPORTED_AFTER_SCF_START';break
                break
            if PARSER_ERROR.search(log): early='INPUT_PARSER_OR_EARLY_FAILURE';break
            if SCF_START.search(log): early='CAP_UNRESOLVED_BEFORE_SCF_MP2';break
            if time.monotonic()-started>300: early='CAP_UNRESOLVED_TIMEOUT';break
            if p.poll() is not None: break
            time.sleep(1)
        if cap!=200 or early:
            if early is None:
                if not confirmed and p.poll() in (88,126,127): early='PROFILE_OR_EXEC_FAILURE_PRE_GAUSSIAN'
                elif not confirmed: early='WRAPPER_OR_ENVIRONMENT_FAILURE_UNVERIFIED'
                else: early='EXITED_BEFORE_EFFECTIVE_CAP'
            stop_own(p)
            result={'job_id':jid,'point_state':'POINT_REVIEW','failure_class':early,'effective_max_steps':cap,'exit_code':p.returncode,
                    'log_sha256':sha(row['log']) if Path(row['log']).is_file() else None,'input_sha256':sha(inp),
                    'gaussian_invoked':True if confirmed else False if early=='PROFILE_OR_EXEC_FAILURE_PRE_GAUSSIAN' else 'UNVERIFIED',
                    'energy_profile_eligible':False,'authorization_retry':False}
        else:
            while p.poll() is None: time.sleep(5)
            result=evaluate(bundle,row,p.returncode,cap,formchk=True)
            result['gaussian_invoked']=confirmed;result['authorization_retry']=False
            if result['point_state']=='POINT_REVIEW': result['failure_class']='LOCAL_SCIENTIFIC_OR_TERMINAL_QC_REVIEW'
        result['package_sha256']=sha(bundle/'SHA256SUMS')
        result['git_commit_sha']=json.loads((run/'queue_launch_claim.json').read_text())['git_commit_sha']
        result['launch_intent_sha256']=sha(row['launch_intent'])
        result['launch_record_sha256']=sha(row['launch_record'])
        evidence_path=d/'gaussian_invocation_evidence.json'
        result['gaussian_invocation_evidence_sha256']=sha(evidence_path) if evidence_path.is_file() else None
        result['finished_utc']=utc();write_new(row['runtime_qa'],result)
        result['runtime_qa_sha256']=sha(row['runtime_qa'])
        append(event_file,{'event':'POINT_TERMINAL','job_id':jid,'point_state':result['point_state'],'failure_class':result.get('failure_class'),'utc':utc()})
        return result
    except Exception as e:
        if p is not None: stop_own(p)
        result={'job_id':jid,'point_state':'POINT_REVIEW','failure_class':'EXECUTION_OR_PROVENANCE_EXCEPTION','error':type(e).__name__+':'+str(e),
                'gaussian_invoked':True if confirmed else 'UNVERIFIED' if p is not None else False,
                'energy_profile_eligible':False,'authorization_retry':False,'finished_utc':utc()}
        if d.is_dir() and not Path(row['runtime_qa']).exists():
            write_new(row['runtime_qa'],result);result['runtime_qa_sha256']=sha(row['runtime_qa'])
        append(event_file,{'event':'POINT_EXCEPTION','job_id':jid,'error':result['error'],'utc':utc()})
        return result

def launch(bundle,auth_file):
    bundle=Path(bundle).resolve();status,m,auth=prelaunch(bundle,auth_file);run=Path(m['external_run_root']);run.mkdir(exist_ok=False)
    write_new(run/'queue_launch_claim.json',{'package_sha256':status['package_sha256'],'git_commit_sha':auth['reviewed_git_commit_sha'],
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
                    if fc in ('EXECUTION_OR_PROVENANCE_EXCEPTION','CONFLICTING_EFFECTIVE_CAP','PROFILE_OR_EXEC_FAILURE_PRE_GAUSSIAN',
                              'WRAPPER_OR_ENVIRONMENT_FAILURE_UNVERIFIED') or class_counts[fc]>=2 and fc in (
                              'EFFECTIVE_MAX_STEPS_NOT_200','C02_VERSION_NOT_CONFIRMED','INPUT_PARSER_OR_EARLY_FAILURE',
                              'CAP_UNRESOLVED_BEFORE_SCF_MP2','CAP_UNRESOLVED_TIMEOUT','EXITED_BEFORE_EFFECTIVE_CAP','CAP_REPORTED_AFTER_SCF_START'):
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
