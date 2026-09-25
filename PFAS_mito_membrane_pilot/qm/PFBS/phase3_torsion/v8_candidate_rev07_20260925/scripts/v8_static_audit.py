#!/usr/bin/env python3
"""Offline, read-only verification of the frozen PFBS Phase-3 v8 candidate."""
import hashlib, json, re, sys
from pathlib import Path

if not __debug__:
    raise RuntimeError('v8 static audit requires Python assertions enabled')

IDS = [f'T_CC_{n:03d}' for n in (120,150,210,240,270,300,330)] + [f'T_CS_{n:03d}' for n in range(0,121,10)]
ROUTE = '#P MP2/6-31+G(d) Opt=(Tight,ModRedundant,MaxCycles=200) IOp(1/152=200) SCF=Tight NoSymm'
ELEMENTS = ['S']+['F']*9+['O']*3+['C']*4
FORBIDDEN = {'.pyc','.pyo','.chk','.fchk','.rwf','.log','.tmp','.bak','.swp','.swo'}

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def grammar(path, jid, checkpoint):
    s=Path(path).read_text(encoding='utf-8')
    lines=s.splitlines()
    assert s.endswith('\n\n'), (jid,'missing final blank line')
    assert len(lines)>=28, (jid,'short input')
    i=0; link=[]
    while i<len(lines) and lines[i].startswith('%'):
        link.append(lines[i]); i+=1
    assert len(link)==3 and link[0]==f'%Chk={checkpoint}' and link[1]=='%NProcShared=8' and link[2]=='%Mem=24GB', (jid,'Link0')
    assert lines[i]==ROUTE and lines[i+1]=='', (jid,'route or route terminator'); i+=2
    assert lines[i].startswith('PFBS_ani ') and lines[i+1]=='', (jid,'title'); i+=2
    assert lines[i]=='-1 1', (jid,'charge/multiplicity'); i+=1
    atoms=[]
    while i<len(lines) and lines[i]:
        z=lines[i].split()
        assert len(z)==4 and z[0] in ('S','F','O','C') and all(re.fullmatch(r'[+-]?\d+(?:\.\d+)?',v) for v in z[1:]), (jid,'Cartesian row')
        atoms.append(z); i+=1
    assert len(atoms)==17 and [a[0] for a in atoms]==ELEMENTS, (jid,'atom count/order')
    assert lines[i]=='', (jid,'geometry terminator'); i+=1
    want='D 16 14 15 1 F' if jid.startswith('T_CC') else 'D 14 15 1 11 F'
    assert i<len(lines) and lines[i]==want and i+1<len(lines) and lines[i+1]=='', (jid,'ModRedundant section')
    assert i+2==len(lines), (jid,'extra section')
    assert s.count('#P ')==1 and s.count('IOp(1/152=200)')==1 and s.count('MaxCycles=200')==1, (jid,'route count')
    assert not re.search(r'Guess\s*=\s*Read|Opt\s*=\s*Restart|Geom\s*=\s*Checkpoint',s,re.I), (jid,'inherited state')
    return {'status':'PASS','atom_count':17,'charge':-1,'multiplicity':1,'route':ROUTE,'modredundant':want,'expected_maxcycles':200,'iop_1_152':200}

def audit(root):
    root=Path(root).resolve(); m=json.loads((root/'package_manifest.json').read_text()); ids=[r['job_id'] for r in m['jobs']]
    assert ids==IDS and len(set(ids))==20 and m['gaussian_launch']=='NOT_AUTHORIZED'
    assert m['max_concurrency']==4 and m['external_run_root'] not in str(root)
    assert m['git_remote']=='https://github.com/luyi-95/PFAS-fish-PBTK-model'
    assert m['git_branch']=='provenance/pfbs-phase3-v8-candidate-rev07-20260925'
    forbidden=[]
    for p in root.rglob('*'):
        if '__pycache__' in p.parts or p.name in ('.pytest_cache','scratch','runtime') or p.suffix.lower() in FORBIDDEN or p.name.endswith('~'):
            forbidden.append(str(p.relative_to(root)))
    assert not forbidden, forbidden
    lines=(root/'SHA256SUMS').read_text().splitlines(); listed={}
    for line in lines:
        h,rel=line.split('  ',1)
        assert re.fullmatch('[0-9a-f]{64}',h) and rel not in listed and not Path(rel).is_absolute() and '..' not in Path(rel).parts
        listed[rel]=h
    actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.name!='SHA256SUMS'}
    assert actual==set(listed), {'missing':sorted(set(listed)-actual),'extra':sorted(actual-set(listed))}
    for rel,h in listed.items(): assert sha(root/rel)==h, rel
    checks=[]; paths=set()
    for row in m['jobs']:
        jid=row['job_id']; p=root/row['input_relative']; pair=root/row['pair_relative']
        assert sha(p)==row['input_sha256'] and sha(pair)==row['pair_sha256'], jid
        for key in ('checkpoint','scratch','log','launch_intent','launch_record','runtime_qa'):
            q=row[key]; assert q not in paths and q.startswith(m['external_run_root']+'/'+jid+'/'), (jid,key); paths.add(q)
        assert row['checkpoint']==m['external_run_root']+'/'+jid+'/'+jid+'.chk'
        checks.append({'job_id':jid,'input_sha256':sha(p),**grammar(p,jid,row['checkpoint'])})
    assert m['accepted_excluded']==['T_CC_000','T_CC_030','T_CC_060','T_CC_090','T_CC_180']
    return {'status':'PASS','package_sha256':sha(root/'SHA256SUMS'),'files':len(listed),'jobs':checks,'forbidden_artifacts':forbidden,'gaussian_invocations':0}

if __name__=='__main__':
    print(json.dumps(audit(Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]),indent=2,sort_keys=True))
