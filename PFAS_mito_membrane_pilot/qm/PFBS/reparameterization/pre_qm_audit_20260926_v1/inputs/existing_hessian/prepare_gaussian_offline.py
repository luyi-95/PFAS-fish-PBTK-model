"""Offline source parsing/input preparation only; no engines, fitting, eigenanalysis."""
from pathlib import Path
import hashlib, json, re, math
from decimal import Decimal
BASE = Path(r"E:\AI-App-Data\PFAS_mito_membrane_pilot")
OUT = BASE / "broad_pre_qm_audit_work_20260926/package/inputs"
H = OUT / "existing_hessian"
A = BASE / "deliverable/qm/PFBS/frequency/PFBS_FREQ_GEO_A"
B = BASE / "deliverable/qm/PFBS/geometry/PFBS_GEO_B_REVISED.log"
EXPECTED = ["S"]+["F"]*9+["O"]*3+["C"]*4
NAMES = ["S1"]+[f"F{i}" for i in range(1,10)]+["O1","O2","O3","C1","C2","C3","C4"]
Z = {"S":16,"F":9,"O":8,"C":6}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,s): p.write_text(s,encoding="utf-8",newline="\n")
def jwrite(p,o): write(p,json.dumps(o,indent=2,ensure_ascii=False)+"\n")
def archive(p):
    lines=p.read_text(encoding="utf-8").splitlines()
    starts=[i for i,l in enumerate(lines) if l.strip().startswith("1\\1\\GINC")]
    assert len(starts)==1, (p,"archive count",len(starts))
    begin=starts[0]; chunks=[]
    for i in range(begin,len(lines)):
        chunks.append(lines[i].strip())
        if "@" in lines[i]: break
    raw="".join(chunks)
    assert raw.endswith("@")
    parts=raw.split("\\\\")
    return lines,raw,parts,{"first_line_1based":begin+1,"last_line_1based":i+1}
def geom(parts):
    tokens=parts[3].split("\\")
    assert tokens[0]=="-1,1"
    coords=[]
    for idx,t in enumerate(tokens[1:]):
        a=t.split(",")
        assert len(a)==4 and a[0]==EXPECTED[idx]
        assert all(math.isfinite(float(x)) for x in a[1:])
        coords.append({"atom_id":idx+1,"atom_name":NAMES[idx],"element":a[0],"atomic_number":Z[a[0]],"xyz_angstrom_lexemes":a[1:]})
    assert len(coords)==17
    return coords
OUT.mkdir(parents=True,exist_ok=True); H.mkdir(exist_ok=True)
al,ar,ap,aline=archive(A/"PFBS_FREQ_GEO_A.log")
bl,br,bp,bline=archive(B)
assert sha(A/"PFBS_FREQ_GEO_A.log")=="56b2bf0620ab18b1ee3517d3b2e1a7754adbba416f2737418938587fd34a4667"
assert sha(B)=="dbe29c5f0da615e8e5d267c8614a7552044ba01dad1b43afc2eafcf50e7f5afa"
assert "\\Freq\\" in ap[0] and ap[1]=="#P MP2/6-31+G(d) Freq SCF=Tight NoSymm"
assert "\\FOpt\\" in bp[0] and "MP2/6-31+G(d)" in bp[1]
assert "Normal termination of Gaussian 16" in "\n".join(al) and "Normal termination of Gaussian 16" in "\n".join(bl)
assert "Optimization completed." in "\n".join(bl) and "Stationary point found." in "\n".join(bl)
ag,bg=geom(ap),geom(bp)
abody="\n".join(x.split() and " ".join(x.split()) or "" for x in (A/"PFBS_FREQ_GEO_A.gjf").read_text().splitlines())
coordA="\n".join(g["element"]+" "+" ".join(g["xyz_angstrom_lexemes"]) for g in ag)
assert coordA in abody
coordsB="\n".join(g["element"]+" "+" ".join(g["xyz_angstrom_lexemes"]) for g in bg)
write(OUT/"GEO_B_FREQ_PROPOSED.gjf",
"%Chk=GEO_B_FREQ_PROPOSED.chk\n%NProcShared=8\n%Mem=48GB\n#P MP2/6-31+G(d) Freq SCF=Tight NoSymm\n\nPFBS_ani accepted revised GEO_B frequency PROPOSED NOT RUN\n\n-1 1\n"+coordsB+"\n\n")
write(OUT/"GEO_B_ACCEPTED_ARCHIVE_GEOMETRY.tsv","atom_id\tatom_name\telement\tx_A\ty_A\tz_A\n"+"\n".join(str(g["atom_id"])+"\t"+g["atom_name"]+"\t"+g["element"]+"\t"+"\t".join(g["xyz_angstrom_lexemes"]) for g in bg)+"\n")
# Verify final printed input orientation in B, independently at its printed 6-decimal precision.
def orientations(lines):
    res=[]
    for i,l in enumerate(lines):
        if l.strip()=="Input orientation:":
            rows=[]; j=i+5
            while j<len(lines) and not lines[j].strip().startswith("----"):
                t=lines[j].split()
                if len(t)==6: rows.append(t)
                j+=1
            if rows: res.append(rows)
    return res
bo=orientations(bl)[-1]
assert len(bo)==17
for g,row in zip(bg,bo):
    assert int(row[0])==g["atom_id"] and int(row[1])==g["atomic_number"]
    assert all(abs(Decimal(x)-Decimal(y))<=Decimal("0.0000005") for x,y in zip(g["xyz_angstrom_lexemes"],row[3:]))
# Meaning is established by job kind, field grammar/developer documentation, not entry count alone.
assert re.search(r"(?:^|\\)NImag=0$",ap[4])
assert len(ap)>=8
packed=ap[5].split(","); grad=ap[6].split(",")
assert len(packed)==1326 and len(grad)==51
assert all(math.isfinite(float(s.replace("D","E"))) for s in packed+grad)
# Independent archive punch is byte-decoded and compared; no checkpoint conversion.
fort="".join((A/"fort.7").read_text().splitlines()).strip()
assert fort==ar
freq=[]
for l in al:
    if l.strip().startswith("Frequencies --"): freq.extend(l.split("--",1)[1].split())
assert len(freq)==45 and all(float(x)>0 for x in freq)
masses=[]
for l in al:
    if l.strip().startswith("AtmWgt="): masses.extend(l.split("=",1)[1].split())
assert len(masses)==17
# Gradient correspondence to explicitly labeled Cartesian force table, source printed rounding only.
forces=[]
for i,l in enumerate(al):
    if "Forces (Hartrees/Bohr)" in l:
        rows=[]
        for ll in al[i+3:]:
            if ll.strip().startswith("---"): break
            t=ll.split()
            if len(t)==5: rows.append(t)
        if len(rows)==17: forces=rows
assert len(forces)==17
force_res=[]
for k,g in enumerate(grad):
    f=forces[k//3][2+k%3]
    assert int(forces[k//3][0])==k//3+1
    delta=abs(Decimal(g.replace("D","E"))+Decimal(f))
    # Archive gradient tokens have 8 decimals; printed forces have9. Compare
    # their combined source-rounding bounds rather than imposing9-decimal precision.
    gd=Decimal(g.replace("D","E")); fd=Decimal(f)
    rounding_bound=(Decimal(10)**gd.as_tuple().exponent+Decimal(10)**fd.as_tuple().exponent)/2
    assert delta<=rounding_bound, (k,g,f,delta,rounding_bound)
    force_res.append(str(delta))
labels=[n+"_"+axis for n in NAMES for axis in "xyz"]
matrix=[[""]*51 for _ in range(51)]
packed_rows=[]; k=0
for i in range(51):
    for j in range(i+1):
        raw=packed[k]
        matrix[i][j]=matrix[j][i]=raw
        packed_rows.append(f"{k+1}\t{i+1}\t{j+1}\t{labels[i]}\t{labels[j]}\t{raw}")
        k+=1
write(H/"GEO_A_ARCHIVE_EXACT.txt",ar+"\n")
write(H/"GEO_A_HESSIAN_PACKED_RAW.tsv","packed_index_1based\trow_1based\tcolumn_1based\trow_coordinate\tcolumn_coordinate\tvalue_Eh_per_a0_squared\n"+"\n".join(packed_rows)+"\n")
write(H/"GEO_A_CARTESIAN_HESSIAN_RAW.tsv","coordinate\t"+"\t".join(labels)+"\n"+"\n".join(labels[i]+"\t"+"\t".join(matrix[i]) for i in range(51))+"\n")
write(H/"GEO_A_ARCHIVE_GEOMETRY_MASSES.tsv","atom_id\tatom_name\telement\tx_A\ty_A\tz_A\tisotope_mass_amu\n"+"\n".join(str(g["atom_id"])+"\t"+g["atom_name"]+"\t"+g["element"]+"\t"+"\t".join(g["xyz_angstrom_lexemes"])+"\t"+masses[i] for i,g in enumerate(ag))+"\n")
write(H/"GEO_A_GRADIENT_RAW.tsv","coordinate\tgradient_Eh_per_a0\tnegative_printed_force_Eh_per_a0\tabsolute_difference\n"+"\n".join(labels[i]+"\t"+grad[i]+"\t"+str(-Decimal(forces[i//3][2+i%3]))+"\t"+force_res[i] for i in range(51))+"\n")
def receipt(p): return {"path":str(p),"sha256":sha(p),"bytes":p.stat().st_size}
provenance={
"operation":"OFFLINE_ARCHIVE_PARSE_ONLY","engine_invoked":False,"parameter_edited":False,
"parser_status":"PASS","target_readiness_status":"REVIEW_TRANSFORMATION_AND_MODE_COMPARISON_NOT_DONE",
"sources":{n:receipt(p) for n,p in {"frequency_log":A/"PFBS_FREQ_GEO_A.log","frequency_input":A/"PFBS_FREQ_GEO_A.gjf","frequency_checkpoint":A/"PFBS_FREQ_GEO_A.chk","archive_punch":A/"fort.7"}.items()},
"archive_line_range":aline,"archive_sections":[{"section":i,"prefix":v[:90],"length":len(v)} for i,v in enumerate(ap)],
"field_identification_evidence":["Header Freq/RMP2-FC/6-31+G(d)","Exact route","NImag=0 properties ends before double separator","First unlabeled numeric section after NImag: developer parser documents lower-triangle Cartesian force constants","Subsequent51 values match negative explicitly labeled Hartrees/Bohr force table at printed rounding","Full archive equals independently punched fort.7"],
"packed_count":1326,"Cartesian_dimension":51,"coordinate_order":labels,
"packing":"row-major lower triangle: (x1,x1),(y1,x1),(y1,y1),(z1,x1),...; symmetry expansion retains exact source lexemes",
"units":{"hessian":"Hartree/Bohr^2","gradient":"Hartree/Bohr","archive_geometry":"Angstrom confirmed identical to original GJF and printed Input orientation","isotope_masses":"amu from AtmWgt, not GROMACS topology masses"},
"coordinate_frame":"archive/input Cartesian frame for this NoSymm all-fixed Cartesian job; raw source states Z-matrix is all fixed cartesians, so copy forces; no rotate-to-standard applied",
"unit_documentation_status":"Gaussian primary-author manual explains atomic-unit Cartesian fields/derivatives; exact archive grammar+packing also independently documented by GoodVibes developer source; Gaussian16-specific full archive grammar not located, retain REVIEW before force-field target use",
"printed_modes":{"count":45,"negative_count":0,"values_cm_inverse":freq},
"unperformed":["mass-weighting","rotation/translation projection","internal-coordinate transformation","normal-mode recomputation","mode-character matching","force-constant inference","scaling","fit"],
"scaling_applied":False,
"generated":{p.name:receipt(p) for p in H.iterdir() if p.is_file() and p.name!="GEO_A_HESSIAN_PARSE_PROVENANCE.json"}
}
jwrite(H/"GEO_A_HESSIAN_PARSE_PROVENANCE.json",provenance)
criteria=[
{"id":"IDENTITY_AND_SOURCE","source":"29 integrity gate","status":"FROZEN","rule":"17 fixed ordered atoms; accepted revisedB source hash/coordinates; -1 singlet; expected G16C.02 route/state; no source replacement"},
{"id":"COMPLETION","source":"29 integrity gate","status":"FROZEN","rule":"Normal termination and all expected outputs/hashes; convergence/warnings reviewed"},
{"id":"MINIMUM","source":"29 Task1 and47 result-specific interpretation","status":"FROZEN_QUALITATIVE","rule":"No chemically meaningful imaginary vibrational mode; tiny imaginary/ambiguous mode REVIEW; nonminimum/failure STOP; retain six external roots separately"},
{"id":"EXPECTED_45_MODES","source":"17-atom nonlinear molecule and47","status":"DOCUMENTED_IDENTITY_CHECK","rule":"45 projected modes with eigenvectors and correct order; no arbitrary frequency cutoff introduced"},
{"id":"HESSIAN_FIELD_READINESS","source":"pre-QM audit proposal","status":"CRITERION_NOT_PREVIOUSLY_FROZEN","rule":"Parse 1326packed entries with labeled grammar evidence, 51gradient, atom/frame/units/masses; evaluate completeness without treating entrycount alone as proof"},
{"id":"GEOMETRY_ROUNDING","source":"source parser audit","status":"CRITERION_NOT_PREVIOUSLY_FROZEN","rule":"Input lexemes equal archive source; future printed-coordinate comparisons respect documented printed precision; no new scientific acceptance tolerance"},
{"id":"NUMERICAL_NEW_THRESHOLDS","source":"29/47","status":"CRITERION_NOT_PREVIOUSLY_FROZEN","rule":"No new numerical Hessian, eigenvalue, MO coefficient, gradient or mode-overlap threshold selected"}
]
spec={
"job_id":"GEO_B_FREQ_PROPOSED","status":"PREPARED_NOT_RUN","mode":"NEW_STUDY_PREPARATION_ONLY",
"input_file":receipt(OUT/"GEO_B_FREQ_PROPOSED.gjf"),
"accepted_geometry_source":receipt(B),"accepted_source_checkpoint":receipt(BASE/"deliverable/qm/PFBS/geometry/PFBS_GEO_B_REVISED.chk"),
"source_archive_lines":bline,"geometry_source_section":3,
"coordinate_payload_sha256":hashlib.sha256((coordsB+"\n").encode()).hexdigest(),
"geometry_payload_provenance":"archive coordinates from accepted revised optimized B; original10decimal-ish lexemes preserved; final Input orientation agrees at6decimal printed precision",
"atom_count":17,"ordered_atoms":bg,"charge":-1,"multiplicity":1,
"route":"#P MP2/6-31+G(d) Freq SCF=Tight NoSymm","units":"input Cartesian Angstrom; default no Units=Bohr",
"forbidden_route_features":["Opt","Guess=Read","Geom=Check","Freq=ReadFC","Link1","constraints","method/basis change"],
"engine":{"required":"Gaussian16C.02","basis":"previously_verified from accepted A frequency/B geometry logs; current runtime NOT_INSPECTED/NOT_INVOKED","runtime_capability_status":"UNVERIFIED"},
"resources":{"nprocshared":8,"memory":"48GB","status":"PROPOSED_REUSED_FROM_ACCEPTED_A_GJF_NOT_CURRENT_ALLOCATION","concurrency":1,"scratch_environment":"GAUSS_SCRDIR job-specific new empty directory to be defined/created only at separately authorized launch","working_directory":"NEW_JOB_LOCAL_DIRECTORY_NOT_CREATED","checkpoint":"GEO_B_FREQ_PROPOSED.chk","source_checkpoint_used_as_input":False,"ETA":"NOT_MEASURED_NO_BENCHMARK"},
"expected_outputs":["GEO_B_FREQ_PROPOSED.log","GEO_B_FREQ_PROPOSED.chk","wrapper_stdout_stderr","exit_status","runtime_effective_input_and_environment_receipt","source_and_output_SHA256_manifest","raw_archive_Hessian_gradient_and_mode_tables","warning_audit"],
"acceptance_criteria":criteria,
"warning_policy":{"unknown":"STOP_AND_REVIEW_NO_AUTOMATIC_RERUN","known_A_thermochemical":"not automatically accepted for B; classify result-specifically using minimum/force/Hessian evidence and47","MO_conditioning":"retain warning/conditioning caution; no new cutoff/threshold"},
"transformations_to_force_field":"NOT_DONE","parameter_edited":"NO","QM_RUN_AUTHORIZATION":"NOT_GRANTED","MD_RUN_AUTHORIZATION":"NOT_GRANTED"}
jwrite(OUT/"GEO_B_HESSIAN_JOB_SPEC.json",spec)
print(json.dumps({"input_sha":spec["input_file"]["sha256"],"parser_status":provenance["parser_status"],"Hessian_target_status":provenance["target_readiness_status"],"packed":1326,"modes":45,"gradient_force_max_difference":str(max(Decimal(x) for x in force_res))},indent=2))
