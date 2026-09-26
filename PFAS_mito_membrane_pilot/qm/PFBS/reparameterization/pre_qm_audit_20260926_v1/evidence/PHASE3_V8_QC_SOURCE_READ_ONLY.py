#!/usr/bin/env python3
"""Per-point terminal QC; never launches Gaussian or interprets profile energies."""
import csv, hashlib, json, math, re, shutil, subprocess
from pathlib import Path

NUM=r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][-+]?\d+)?'
ALPHA=re.compile(r'Warning!!:\s+The largest alpha MO coefficient is\s+('+NUM+r')',re.I)
ARCHIVE_ATOM=re.compile(r'^([A-Z][a-z]?),('+NUM+r'),('+NUM+r'),('+NUM+r')$')
NAMES=['S1']+[f'F{i}' for i in range(1,10)]+[f'O{i}' for i in range(1,4)]+[f'C{i}' for i in range(1,5)]

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def numeric(v): return float(v.replace('D','E').replace('d','e'))
def dist(a,b): return math.sqrt(sum((a[i]-b[i])**2 for i in range(3)))
def dih(p):
    p0,p1,p2,p3=p; sub=lambda a,b:[a[i]-b[i] for i in range(3)]; dot=lambda a,b:sum(a[i]*b[i] for i in range(3)); cross=lambda a,b:[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
    b0=sub(p0,p1);b1=sub(p2,p1);b2=sub(p3,p2);norm=math.sqrt(dot(b1,b1)); assert norm>0
    b1=[x/norm for x in b1];v=[b0[i]-dot(b0,b1)*b1[i] for i in range(3)];w=[b2[i]-dot(b2,b1)*b1[i] for i in range(3)]
    return math.degrees(math.atan2(dot(cross(b1,v),w),dot(v,w)))
def archive(log):
    start=log.rfind('1\\1\\GINC'); end=log.find(r'\@',start) if start>=0 else -1
    if start<0 or end<0: raise ValueError('embedded Gaussian archive absent')
    s=re.sub(r'\s+','',log[start:end]); cms=list(re.finditer(r'(-?\d+),(\d+)\\',s))
    if not cms: raise ValueError('archive charge/multiplicity absent')
    m=cms[-1]; endcoord=s.find('\\\\Version=',m.end())
    if endcoord<0: raise ValueError('archive Version boundary absent')
    atoms=[]
    for token in s[m.end():endcoord].split('\\'):
        q=ARCHIVE_ATOM.fullmatch(token)
        if not q: raise ValueError('malformed archive coordinate')
        atoms.append((q.group(1),[numeric(q.group(i)) for i in (2,3,4)]))
    return {'charge':int(m.group(1)),'multiplicity':int(m.group(2)),'atoms':atoms,'sha256':hashlib.sha256(s.encode()).hexdigest()}
def alpha_class(log):
    vals=[]; unknown=[]
    for line in log.splitlines():
        if re.search(r'\bWarning\b',line,re.I):
            m=ALPHA.search(line)
            if m: vals.append(numeric(m.group(1)))
            elif re.search(r'Warning\s*--\s*This program may not be used',line,re.I): pass
            else: unknown.append(line)
    return {'class':'KNOWN_ALPHA_MO' if vals and not unknown else 'NONE' if not unknown else 'UNKNOWN',
            'count':len(vals),'min':min(vals) if vals else None,'max':max(vals) if vals else None,'final':vals[-1] if vals else None,'unknown_lines':unknown}
def geometry(row,root,atoms):
    coords=[a[1] for a in atoms]; expected=['S']+['F']*9+['O']*3+['C']*4
    if len(atoms)!=17 or [a[0] for a in atoms]!=expected: return {'status':'REVIEW','reason':'atom order/element mismatch'}
    idx=(16,14,15,1) if row['axis']=='C3-C1-C2-S1' else (14,15,1,11)
    angle=dih([coords[i-1] for i in idx]); delta=(angle-float(row['target_deg'])+180)%360-180
    with (root/row['pair_relative']).open(newline='',encoding='utf-8') as f: pairs=list(csv.DictReader(f,delimiter='\t'))
    edge=[]; contacts=[]; final_bonds=[]; nonbond=[]
    for p in pairs:
        i=NAMES.index(p['atom_i']);j=NAMES.index(p['atom_j']);d=dist(coords[i],coords[j]);d0=float(p['distance_A'])
        if int(p['shortest_bond_path'])==1:
            edge.append((p['atom_i'],p['atom_j']));final_bonds.append(d)
            if abs(d-d0)>0.20: contacts.append({'pair':p['atom_i']+'-'+p['atom_j'],'class':'bond_change_review','input_A':d0,'final_A':d})
        elif int(p['shortest_bond_path'])>=2:
            nonbond.append(d)
            if d<2.0 and d<d0-0.30: contacts.append({'pair':p['atom_i']+'-'+p['atom_j'],'class':'new_short_contact_review','input_A':d0,'final_A':d})
    if len(edge)!=16: contacts.append({'class':'reference_graph_not_16_edges'})
    if final_bonds and nonbond and min(nonbond)<=max(final_bonds): contacts.append({'class':'bond_nonbond_separation_review','max_bond_A':max(final_bonds),'min_graph_nonbond_A':min(nonbond)})
    return {'status':'PASS' if abs(delta)<=0.01 and not contacts else 'REVIEW','torsion_deg':angle,'target_error_deg':delta,'target_tolerance_deg':0.01,
            'expected_graph_edges':edge,'max_bond_A':max(final_bonds) if final_bonds else None,'min_graph_nonbond_A':min(nonbond) if nonbond else None,'contact_flags':contacts,
            'contact_rule':'Conservative screening only; flagged geometries require scientific review.'}
def fchk_copy(chk,workdir):
    chk=Path(chk); workdir=Path(workdir); copied=workdir/'formchk_input_copy.chk'; output=workdir/'formchk_output.fchk'
    if copied.exists() or output.exists(): raise FileExistsError('formchk output path already exists')
    before=sha(chk); shutil.copyfile(chk,copied)
    if sha(copied)!=before: raise ValueError('checkpoint copy mismatch')
    with (workdir/'formchk_stdout.txt').open('xb') as out:
        p=subprocess.run(['/opt/g16/formchk',str(copied),str(output)],stdout=out,stderr=subprocess.STDOUT,cwd=workdir,check=False,timeout=300)
    if p.returncode!=0 or not output.is_file() or output.stat().st_size==0: raise RuntimeError('formchk failed')
    if sha(chk)!=before: raise ValueError('original checkpoint changed during formchk')
    ft=output.read_text(errors='replace')
    if 'RMP2' not in ft.splitlines()[1] or '6-31+G(d)' not in ft.splitlines()[1]:
        raise ValueError('fchk method/basis mismatch')
    if not re.search(r'(?m)^Number of atoms\s+I\s+17\s*$',ft) or not re.search(r'(?m)^Charge\s+I\s+-1\s*$',ft) or not re.search(r'(?m)^Multiplicity\s+I\s+1\s*$',ft):
        raise ValueError('fchk state/atom-count mismatch')
    am=re.search(r'(?m)^Atomic numbers\s+I\s+N=\s*17\s*\n((?:\s*\d+\s*){17})',ft)
    if not am or [int(x) for x in am.group(1).split()]!=[16]+[9]*9+[8]*3+[6]*4:
        raise ValueError('fchk atomic-number order mismatch')
    return {'status':'PASS','original_chk_sha256':before,'copy_chk_sha256':sha(copied),'fchk_sha256':sha(output),'fchk_path':str(output),'formchk_log_sha256':sha(workdir/'formchk_stdout.txt')}
def evaluate(root,row,exit_code,effective_cap,formchk=True):
    root=Path(root); log_path=Path(row['log']);chk=Path(row['checkpoint']); text=log_path.read_text(errors='replace') if log_path.is_file() else ''
    flags=[]; warnings=alpha_class(text); scf=len(re.findall(r'SCF Done:',text));mp2=len(re.findall(r'\bEUMP2\s*=',text)); opt=len(re.findall(r'Optimization completed\.',text))
    normal=len(re.findall(r'Normal termination of Gaussian 16',text)); err=len(re.findall(r'Error termination',text))
    if exit_code!=0 or normal!=1 or err or opt!=1 or scf<1 or scf!=mp2: flags.append('termination_optimization_or_SCF_MP2')
    if effective_cap!=200: flags.append('effective_cap_not_200')
    if warnings['class']=='UNKNOWN': flags.append('unknown_warning_class')
    if re.search(r'Convergence failure|Number of steps exceeded|Optimization stopped|out of memory|Erroneous write',text,re.I): flags.append('numerical_or_resource_failure')
    expected='D 16 14 15 1 F' if row['axis']=='C3-C1-C2-S1' else 'D 14 15 1 11 F'
    heads=list(re.finditer(r'The following ModRedundant input section has been read:',text))
    if len(heads)!=1: flags.append('restraint_readback_header_count')
    else:
        rest=[]
        for line in text[heads[0].end():].splitlines():
            q=line.strip()
            if not q:
                if rest: break
                continue
            if re.match(r'^[BD]\s+\d+',q,re.I): rest.append(' '.join(q.split()))
            elif rest: break
        if rest!=[expected]: flags.append('restraint_readback_mismatch')
    metrics={}
    for label in ('Maximum Force','RMS     Force','Maximum Displacement','RMS     Displacement'):
        pat=r'(?m)^\s*'+re.escape(label)+r'\s+('+NUM+r')\s+('+NUM+r')\s+(YES|NO)\s*$'
        found=re.findall(pat,text,re.I)
        if not found: flags.append('convergence_metric_missing:'+label)
        else:
            value,threshold,ok=found[-1];metrics[label]={'actual':numeric(value),'threshold':numeric(threshold),'pass':ok.upper()=='YES'}
            if ok.upper()!='YES' or numeric(value)>numeric(threshold): flags.append('convergence_metric_nonpass:'+label)
    ar=None;geo=None
    try:
        ar=archive(text)
        if ar['charge']!=-1 or ar['multiplicity']!=1: flags.append('archive_state_mismatch')
        geo=geometry(row,root,ar['atoms'])
        if geo['status']!='PASS': flags.append('geometry_or_contact_review')
    except Exception as e: flags.append('archive_parse:'+str(e))
    if not chk.is_file() or chk.stat().st_size==0: flags.append('checkpoint_missing')
    fchk_record=None
    if not flags and formchk:
        try: fchk_record=fchk_copy(chk,log_path.parent)
        except Exception as e: flags.append('formchk:'+type(e).__name__+':'+str(e))
    if not formchk: flags.append('formchk_not_verified')
    if fchk_record and fchk_record['status']!='PASS': flags.append('formchk_incomplete')
    energies=[numeric(v) for v in re.findall(r'\bEUMP2\s*=\s*('+NUM+r')',text,re.I)]
    if len(energies)!=mp2 or not energies or not all(math.isfinite(x) for x in energies): flags.append('energy_series_incomplete')
    if len(energies)>1 and max(abs(energies[i]-energies[i-1]) for i in range(1,len(energies)))>0.10:
        flags.append('large_MP2_step_change_review')
    return {'job_id':row['job_id'],'point_state':'PASS' if not flags else 'POINT_REVIEW','flags':flags,'effective_max_steps':effective_cap,
            'exit_code':exit_code,'normal_termination_count':normal,'optimization_completed_count':opt,'scf_count':scf,'mp2_count':mp2,
            'energy_hartree':energies[-1] if energies else None,'alpha_warning':warnings,'archive':ar and {k:v for k,v in ar.items() if k!='atoms'},
            'geometry':geo,'convergence_metrics':metrics,'checkpoint_sha256':sha(chk) if chk.is_file() else None,'log_sha256':sha(log_path) if log_path.is_file() else None,
            'input_sha256':sha(root/row['input_relative']),'formchk':fchk_record,'external_archive_required':False,
            'energy_profile_eligible':not flags}
