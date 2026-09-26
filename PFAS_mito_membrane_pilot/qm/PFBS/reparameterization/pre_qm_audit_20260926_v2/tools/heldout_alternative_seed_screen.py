"""Offline, no engine: prospective periodic-distance and rigid graph-rotation screen."""
import csv,json,hashlib,itertools,math
from pathlib import Path
import numpy as np
V1=Path(r'E:\AI-App-Data\PFAS_mito_membrane_pilot\broad_pre_qm_audit_work_20260926\package')
OUT=Path(__file__).resolve().parent/"alternative_seed_screen"
OUT.mkdir(exist_ok=False)
def rows(p):return list(csv.DictReader(p.open(encoding='utf-8'),delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write_tsv(p,data):
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]),delimiter='\t');w.writeheader();w.writerows(data)
geom={}
for r in rows(V1/'existing_qm/ACCEPTED_ABSOLUTE_QM_GEOMETRIES.tsv'):
    geom.setdefault(r['point_id'],[]).append(r)
sec=None;bonds=[]
for line in (V1/'current_parameters/pfbs_ani.itp').read_text().splitlines():
    t=line.split(';')[0].strip()
    if t.startswith('['):sec=t.strip('[] ').lower();continue
    if sec=='bonds' and t:
        a,b,*_=t.split();bonds.append((int(a)-1,int(b)-1))
graph={i:set() for i in range(17)}
for a,b in bonds:graph[a].add(b);graph[b].add(a)
def component(j,k):
    seen={k};stack=[k]
    while stack:
        a=stack.pop()
        for b in graph[a]:
            if {a,b}=={j,k}:continue
            if b not in seen:seen.add(b);stack.append(b)
    assert j not in seen
    return sorted(seen)
def dih(x,ids):
    a,b,c,d=x[np.array(ids)-1];u=c-b;u/=np.linalg.norm(u)
    v=a-b;v-=np.dot(v,u)*u;w=d-c;w-=np.dot(w,u)*u
    return math.degrees(math.atan2(np.dot(np.cross(u,v),w),np.dot(v,w)))
def delta(a,b,p=360):return (a-b+p/2)%p-p/2
def rotate(x,j,k,deg):
    y=x.copy();u=x[k]-x[j];u/=np.linalg.norm(u);ids=component(j,k)
    v=x[ids]-x[j];t=math.radians(deg)
    y[ids]=x[j]+v*math.cos(t)+np.cross(u,v)*math.sin(t)+np.outer(v@u,u)*(1-math.cos(t))
    return y
def setdih(x,ids,target):
    j,k=ids[1]-1,ids[2]-1;base=dih(x,ids)
    sign=delta(dih(rotate(x,j,k,1),ids),base)
    assert abs(abs(sign)-1)<1e-8
    y=rotate(x,j,k,delta(target,base)/sign)
    assert abs(delta(dih(y,ids),target))<1e-7
    return y
dev=list(itertools.product([60,180,300],[30,90]))
old=list(itertools.product([90,210],[20,100]))
new=[(0,60),(150,60),(270,0),(240,0),(120,0)]
distance=[];feas=[];starts={}
for partition,points in [('OLD_HELDOUT',old),('REVISED_HELDOUT',new)]:
    for cc,cs in points:
        for dc,ds in dev:
            a=abs(delta(cc,dc));b=abs(delta(cs,ds));q=abs(delta(cs,ds,120))
            distance.append(dict(design=partition,CC=cc,CS=cs,development_CC=dc,development_CS=ds,delta_CC_deg=a,delta_CS_360_deg=b,delta_CS_120_deg=q,euclidean_degrees_360_360=math.hypot(a,b),euclidean_degrees_360_120=math.hypot(a,q),normalized_torus_distance_360_120=math.hypot(a/360,q/120),normalized_torus_distance_360_360=math.hypot(a/360,b/360),mirror_quotient_distance_360_120=min(math.hypot(a/360,q/120),math.hypot(delta(-cc,dc)/360,delta(-cs,ds,120)/120))))
        seed=f'T_CC_{cc:03d}';rr=sorted(geom[seed],key=lambda r:int(r['atom_id']))
        x=np.array([[float(r[k]) for k in ['x_nm','y_nm','z_nm']] for r in rr])
        y=setdih(setdih(x,[16,14,15,1],cc),[14,15,1,11],cs)
        d0=np.linalg.norm(x[:,None]-x[None,:],axis=2)*10;d1=np.linalg.norm(y[:,None]-y[None,:],axis=2)*10
        bondmax=max(d1[a,b] for a,b in bonds);pairs=[(a,b) for a in range(17) for b in range(a+1,17) if (a,b) not in bonds and (b,a) not in bonds]
        short=[(a+1,b+1,float(d1[a,b]),float(d0[a,b]-d1[a,b])) for a,b in pairs if d1[a,b]<2 and d0[a,b]-d1[a,b]>.3]
        bondchange=max(abs(d1[a,b]-d0[a,b]) for a,b in bonds)
        minpair=min(pairs,key=lambda ab:d1[ab]);near=float(d1[minpair])
        review=bool(short) or near<=bondmax
        feas.append(dict(design=partition,CC=cc,CS=cs,seed=seed,seed_file=rr[0]['source_file'],seed_sha256=rr[0]['source_sha256'],actual_CC_deg=dih(y,[16,14,15,1]),actual_CS_deg=dih(y,[14,15,1,11]),max_bond_change_A=bondchange,minimum_nonbonded_A=near,minimum_pair='-'.join(str(i+1) for i in minpair),max_bond_A=bondmax,new_short_contacts=json.dumps(short),geometry_gate='REVIEW' if review else 'PASS_OFFLINE_CONTACT_SCREEN',symmetry_gate='120_DEG_IS_CONSERVATIVE_QUOTIENT_NOT_EXACT_ROTAMER_EQUIVALENCE'))
        starts[f'{partition}_CC{cc:03d}_CS{cs:03d}']={'seed':seed,'seed_sha256':rr[0]['source_sha256'],'coordinates_nm':y.tolist(),'atom_names':[r['atom_name'] for r in rr]}
write_tsv(OUT/'HELDOUT_PERIODIC_DISTANCES.tsv',distance)
symmetry=[]
for aa,bb in itertools.combinations(new,2):
    direct=math.hypot(delta(aa[0],bb[0])/360,delta(aa[1],bb[1],120)/120)
    mirrored=math.hypot(delta(-aa[0],bb[0])/360,delta(-aa[1],bb[1],120)/120)
    symmetry.append(dict(CC_a=aa[0],CS_a=aa[1],CC_b=bb[0],CS_b=bb[1],direct_distance_360_120=direct,mirror_distance_360_120=mirrored,nominal_mirror_duplicate=mirrored<1e-10))
write_tsv(OUT/'HELDOUT_PAIR_SYMMETRY.tsv',symmetry)
write_tsv(OUT/'HELDOUT_SEED_FEASIBILITY.tsv',feas)
(OUT/'OFFLINE_ROTATED_SEED_PREVIEWS.json').write_text(json.dumps(starts,indent=2)+'\n')
receipt={'operation':'OFFLINE_READ_ONLY_SOURCE_DERIVATION_NO_QM_OR_MM','coordinate_source_sha256':sha(V1/'existing_qm/ACCEPTED_ABSOLUTE_QM_GEOMETRIES.tsv'),'topology_source_sha256':sha(V1/'current_parameters/pfbs_ani.itp'),'script_sha256':sha(Path(__file__)),'new_results_available':False,'rotation_rule':'Rigid fourth-side connected component, remove central bond, directed j->k right-hand Rodrigues; sign calibrated by +1deg readback; CC thenCS','gates':'Historical conservative shortcontact<2A shortened>.3A, minnonbond<=maxbond REVIEW; allbondlengthspreserved','revised_points':feas[4:]}
(OUT/'HELDOUT_OFFLINE_PREFLIGHT_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'new_seed_gates':[(r['CC'],r['CS'],r['geometry_gate'],r['minimum_nonbonded_A']) for r in feas[4:]],'script_sha256':sha(Path(__file__))}))
