#!/usr/bin/env python3
"""Read-only identity gate for the accepted GEO_A and revised GEO_B starts."""
import csv, hashlib, itertools, json, math
from pathlib import Path

ROOT = Path(r"E:\AI-App-Data\PFAS_mito_membrane_pilot")
V1 = ROOT / "broad_pre_qm_audit_work_20260926" / "package"
RUNS = ROOT / "deliverable" / "qm" / "PFBS" / "phase3_torsion_20260924" / "TASK1_BONDED_CANDIDATE_20260926_v1" / "payload" / "final_evidence_01" / "formal_dp_runs"
OUT = ROOT / "broad_pre_qm_v2_work_20260926" / "executor" / "inputs" / "GEOMETRY_SOURCE_GATE.json"

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def g96(p):
    lines=p.read_text().splitlines(); a=lines.index('POSITION')+1; b=lines.index('END',a)
    rows=[]
    for line in lines[a:b]:
        fields=line.split()
        atom=fields[2]
        xyz=[float(v) for v in fields[4:7]]
        rows.append((atom,xyz))
    if len(rows)!=17: raise ValueError(f'{p} atom count {len(rows)}')
    return rows

def archive(path):
    with path.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f,delimiter='\t'))
    if len(rows)!=17: raise ValueError(f'{path} archive atom count {len(rows)}')
    names=[r['atom_name'] for r in rows]
    xyz=[[float(r['x_A'])/10,float(r['y_A'])/10,float(r['z_A'])/10] for r in rows]
    return names,xyz

def pairdist(x):
    return {(i,j):math.dist(x[i-1],x[j-1]) for i,j in itertools.combinations(range(1,18),2)}

def check(label, run_name, archive_name):
    folder=RUNS/run_name/'base'
    start=folder/'start.g96'
    record=json.loads((folder/'run_record.json').read_text())
    if sha(start)!=record['input_g96_sha256']: raise ValueError(f'{label}: run-record hash mismatch')
    source=V1/'inputs'/archive_name
    gr=g96(start); n1=[a for a,_ in gr]; x1=[x for _,x in gr]
    n2,x2=archive(source)
    if n1!=n2: raise ValueError(f'{label}: atom order mismatch {n1} != {n2}')
    d1,d2=pairdist(x1),pairdist(x2)
    err=max(abs(d1[k]-d2[k]) for k in d1)
    # V1 archive has 0.1 pm coordinate precision; G96 uses 1e-5 A precision.
    if err>2e-7: raise ValueError(f'{label}: geometry identity difference {err:.3e} nm')
    return {'source_id':label,'g96_path':str(start),'g96_sha256':sha(start),
            'run_record_path':str(folder/'run_record.json'),'run_record_sha256':sha(folder/'run_record.json'),
            'archive_geometry_path':str(source),'archive_geometry_sha256':sha(source),
            'gromacs_binary_sha256':record['gmx_sha256'],'candidate_base_itp_sha256':record['candidate_parameters_sha256']['itp'],
            'candidate_base_prm_sha256':record['candidate_parameters_sha256']['prm'],
            'max_pair_distance_difference_nm':err,'atom_order_match':True,'status':'PASS'}

def main():
    rows=[check('GEO_A','GEO_A','existing_hessian/GEO_A_ARCHIVE_GEOMETRY_MASSES.tsv'),
          check('GEO_B_REVISED','GEO_B_REVISED_10nm','GEO_B_ACCEPTED_ARCHIVE_GEOMETRY.tsv')]
    result={'status':'PASS','sources':rows}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
