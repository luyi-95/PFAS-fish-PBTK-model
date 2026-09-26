"""Offline full-graph symmetry diagnostics; no fitting or engine execution."""
from pathlib import Path
import numpy as np,itertools,json,csv,hashlib
root=Path(__file__).resolve().parent
ns={ '__file__':str(root/'heldout_preflight.py') }
exec((root/'heldout_preflight.py').read_text().split('dev=list(')[0],ns)
geom=ns['geom'];setdih=ns['setdih'];dih=ns['dih'];delta=ns['delta'];write_tsv=ns['write_tsv']
held=[(90,60),(210,0),(330,60),(270,0)];dev=list(itertools.product([60,180,300],[30,90]))
def seed(cc,cs):
    rr=sorted(geom[f'T_CC_{cc:03d}'],key=lambda r:int(r['atom_id']))
    x=np.array([[float(r[k]) for k in ['x_nm','y_nm','z_nm']] for r in rr])
    return setdih(setdih(x,[16,14,15,1],cc),[14,15,1,11],cs)
xyz={p:seed(*p) for p in held+dev}
perms=[]
for os in itertools.permutations([10,11,12]):
  for cf3 in itertools.permutations([7,8,9]):
    for flip in itertools.product([False,True],repeat=3):
      perm=np.arange(17);perm[10:13]=os;perm[7:10]=cf3
      for start,f in zip([1,3,5],flip):
        if f:perm[start:start+2]=perm[start:start+2][::-1]
      perms.append(perm)
def best(a,b,reflect):
    a=a-a.mean(0);b=b-b.mean(0)
    if reflect:a=a*np.array([-1,1,1])
    ans=None
    for p in perms:
      x=b[p];u,s,vt=np.linalg.svd(a.T@x);d=np.linalg.det(u@vt);rot=u@np.diag([1,1,d])@vt
      dr=a@rot-x;rms=float(np.sqrt(np.mean(np.sum(dr*dr,axis=1)))*10)
      if ans is None or rms<ans[0]:ans=(rms,float(np.max(np.linalg.norm(dr,axis=1))*10),p.tolist())
    return ans
results=[]
for aa in held:
  for kind,bb in [('DEVELOPMENT',p) for p in dev]+[('HELDOUT',p) for p in held if p>aa]:
    normal=best(xyz[aa],xyz[bb],False);mirror=best(xyz[aa],xyz[bb],True)
    results.append(dict(CC_a=aa[0],CS_a=aa[1],comparison=kind,CC_b=bb[0],CS_b=bb[1],proper_symmetry_RMSD_A=normal[0],proper_max_atom_A=normal[1],mirror_symmetry_RMSD_A=mirror[0],mirror_max_atom_A=mirror[1],proper_atom_map=json.dumps([i+1 for i in normal[2]]),mirror_atom_map=json.dumps([i+1 for i in mirror[2]]),interpretation='DIAGNOSTIC_COORDINATE_SEPARATION_NOT_QM_BASIN_OR_ENERGY_EQUIVALENCE'))
write_tsv(root/'frozen_heldout_design/HELDOUT_FULL_GRAPH_SYMMETRY.tsv',results)
angles=[]
for p,x in xyz.items():
  angles.append(dict(CC=p[0],CS=p[1],actual_O1_CS_deg=dih(x,[14,15,1,11]),actual_O2_CS_deg=dih(x,[14,15,1,12]),actual_O3_CS_deg=dih(x,[14,15,1,13]),note='ActualOangularoffsets;120nominalfoldisnotassumedexact'))
write_tsv(root/'frozen_heldout_design/HELDOUT_O_PERMUTATION_ANGLES.tsv',angles)
print(json.dumps({'atom_graph_automorphisms':len(perms),'pairs':len(results),'minimum_proper_RMSD_A':min(r['proper_symmetry_RMSD_A'] for r in results),'minimum_mirror_RMSD_A':min(r['mirror_symmetry_RMSD_A'] for r in results),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}))
