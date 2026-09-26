"""Finalize report-only artifacts for the completed frozen MM analysis."""
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path


def sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""): h.update(block)
    return h.hexdigest()


def read_tsv(path):
    with path.open(encoding="utf-8",newline="") as f:
        reader=csv.DictReader(f,delimiter="\t")
        return reader.fieldnames,list(reader)


def write_tsv(path,columns,rows):
    with path.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=columns,delimiter="\t",extrasaction="ignore")
        writer.writeheader();writer.writerows(rows)


def main():
    work=Path(r"E:\AI-App-Data\PFAS_mito_membrane_pilot\broad_pre_qm_v2_work_20260926")
    out=work/"executor"/"analysis"/"numerical_matrix_20260926T092541Z_v8_v7"
    prereg=work/"preregistered_inputs"
    script=work/"executor"/"scripts"/"analyze_numerical_identifiability.py"
    launch=work/"executor"/"receipts"/"matrix_launches"/"LAUNCH_RECORD_matrix_20260926T092541Z_v8.json"
    source_manifest=out/"SOURCE_PROVENANCE_MANIFEST.json"
    low_spec=prereg/"MVP_LOW_TIER_ROW_DIAGNOSTIC_SPEC.json"
    low=json.loads(low_spec.read_text(encoding="utf-8"))
    selected={r["primary_energy_source_id"] for r in low["selected_energy_rows"]}
    low_rows=[]
    for name in ("NUMERICAL_JACOBIAN_RAW.tsv","NUMERICAL_JACOBIAN_NORMALIZED.tsv",
                 "NUMERICAL_JACOBIAN_RAW_2H.tsv","NUMERICAL_JACOBIAN_NORMALIZED_2H.tsv",
                 "NUMERICAL_JACOBIAN_RAW_TIGHT.tsv","NUMERICAL_JACOBIAN_NORMALIZED_TIGHT.tsv",
                 "NUMERICAL_JACOBIAN_UNCERTAINTY_RAW.tsv","NUMERICAL_JACOBIAN_UNCERTAINTY_NORMALIZED.tsv"):
        cols,rows=read_tsv(out/name)
        chosen=[r for r in rows if r["kind"] in ("bond","angle","AB_energy") or
                (r["kind"] in ("profile_energy","profile_anchor") and r["source_id"] in selected)]
        if len(chosen)!=99 or len({r["observable_id"] for r in chosen})!=99:
            raise ValueError(f"frozen low-tier output should have 99 unique rows: {name} has {len(chosen)}")
        target=out/(name.replace(".tsv","_LOW_TIER_99.tsv"))
        write_tsv(target,cols,chosen)
        low_rows.append({"file":target.name,"rows":len(chosen),"sha256":sha(target)})

    # Condensed low-tier/submatrix manifest points to frozen numerical results.
    svdcols,svd=read_tsv(out/"MATRIX_SUPPORT_SUMMARY.tsv")
    minimal=[r for r in svd if r["matrix_id"].startswith("MVP_")]
    subcols,sub=read_tsv(out/"SVD_RIGHT_SINGULAR_VECTORS.tsv")
    subvec=[r for r in sub if r["matrix_id"].startswith("MVP_")]
    write_tsv(out/"MVP_DECLARED_MINIMAL_SUBMATRIX_SUPPORT.tsv",svdcols,minimal)
    write_tsv(out/"MVP_DECLARED_MINIMAL_SUBMATRIX_VECTORS.tsv",subcols,subvec)

    structural=out/"STRUCTURAL_DOMAIN_QC.md"
    pair=json.loads((out/"AB_PAIR_DISTANCE_SUMMARY.json").read_text(encoding="utf-8"))
    torsion=json.loads((out/"LOCAL_PROPER_TORSION_DOMAIN_SUMMARY.json").read_text(encoding="utf-8"))
    scan=json.loads((out/"SCAN_ANGLE_DRIFT_SUMMARY.json").read_text(encoding="utf-8"))
    structural.write_text(
        "# Structural and restraint QC\n\n"
        "These are separate preregistered quality gates; they do not alter the numerical matrices or issue a final route decision.\n\n"
        f"- Scan restraint centers: {scan['count']} checks, {scan['failed']} failures; maximum absolute drift "
        f"{scan['max_abs_drift_deg']:.8g} degrees against {scan['threshold_deg']:.3f} degrees.\n"
        f"- Local proper-torsion domain: {torsion['count']} variable/source checks, {torsion['failed']} failures; "
        f"maximum minimax change {torsion['max_minimax_change_deg']:.8g} degrees against {torsion['threshold_deg']:.1f} degrees. "
        f"The selected map is fixed across each direction's six endpoints; {torsion['automorphisms_general']} graph automorphisms "
        f"were permitted generally and {torsion['automorphisms_CS_O1_fixed']} with restrained CS O1 fixed.\n"
        f"- A/B pair geometry: {pair['rows']} values covering all 136 pairs at start, LBFGS final, and CG final for every state; "
        f"maximum {pair['max_distance_nm']:.8g} nm against the {pair['isolated_domain_limit_nm']:.1f} nm limit; "
        f"{pair['box_nm']} nm box checked.\n"
        "- The T_CC_300 common energy-anchor row is included in both 118-row primary and 99-row low-tier vectors with its frozen CC weight; "
        "subtracting the same physical-energy record from itself gives exact zero value, derivative, and serialization bound.\n",
        encoding="utf-8")

    launch_obj=json.loads(launch.read_text(encoding="utf-8"))
    old=json.loads(source_manifest.read_text(encoding="utf-8"))
    if sha(launch)!=old["input_hashes"]["launch_record"]["sha256"]:
        raise ValueError("local launch record no longer matches terminal export binding")
    runner=launch_obj["runner"]
    if runner["sha256"]!="cfc467e92d487c22e0e22a6fa5c6293eee46c1048aaad2a247221e2940b46587":
        raise ValueError("launch receipt runner SHA does not match approved frozen runner")
    old["input_hashes"]["launch_record_local"]={"path":str(launch),"sha256":sha(launch)}
    old["input_hashes"]["runner"]={"path":runner["path"],"sha256":runner["sha256"]}
    old["input_hashes"]["analysis_script"]={"path":str(script),"sha256":sha(script)}
    prereg_files=("BASIN_AND_MATHEMATICAL_RATIONALE_ADDENDUM.md",
                  "TERMINAL_CONVERGENCE_AND_PHYSICAL_ENERGY_ADDENDUM.md",
                  "TERMINAL_CONVERGENCE_AND_PHYSICAL_ENERGY_RECEIPT.json",
                  "FAILURE_SCOPE_PREREGISTRATION_ADDENDUM.md",
                  "FAILURE_SCOPE_PREREGISTRATION_RECEIPT.json",
                  "MVP_LOW_TIER_DIAGNOSTIC_ADDENDUM.md")
    for name in prereg_files:
        p=prereg/name
        old["input_hashes"][f"prereg_{name}"]={"path":str(p),"sha256":sha(p)}
    old["low_tier_anchor_policy"]="CC300 included as exact-zero common-anchor row in primary 118 and frozen low-tier 99; CC axis weight 1/sqrt(2*12); no row renormalization."
    old["analysis_script_sha256"]=sha(script)
    old["runner_sha256"]=runner["sha256"]
    old["matrix_launch_record_sha256"]=sha(launch)
    old["output_hashes_sha256"]={p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file() and p.name not in ("SOURCE_PROVENANCE_MANIFEST.json","ANALYSIS_EXECUTION_RECEIPT.json")}
    source_manifest.write_text(json.dumps(old,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")

    files=[]
    for p in sorted(out.iterdir()):
        if not p.is_file() or p.name=="ANALYSIS_EXECUTION_RECEIPT.json": continue
        entry={"path":str(p),"sha256":sha(p),"size_bytes":p.stat().st_size}
        if p.suffix==".tsv":
            with p.open(encoding="utf-8",newline="") as f: entry["data_rows"]=max(0,sum(1 for _ in f)-1)
        files.append(entry)
    receipt={"schema":"PFBS_MM_NUMERICAL_ANALYSIS_EXECUTION_RECEIPT_v1",
             "output_dir":str(out),"analysis_script":{"path":str(script),"sha256":sha(script)},
             "finalizer_script":{"path":str(Path(__file__).resolve()),"sha256":sha(Path(__file__).resolve())},
             "terminal_export_sha256":old["input_hashes"]["terminal_compact_export"]["sha256"],
             "launch_record_sha256":sha(launch),"approved_runner_path":runner["path"],"approved_runner_sha256":runner["sha256"],
             "matrix":{"status":"COMPLETE","runs":1736,"source_state_cells":62*28,"nonconverged_or_failed":0},
             "analysis_execution":{"mode":"offline read-only analysis","python_no_bytecode":True,
                                   "gromacs_invoked":False,"parameter_edits":False,"QM_or_MD":False},
             "row_counts":{"primary":118,"low_tier":99,"raw_observations":62*118,
                           "local_proper_torsion_checks":torsion["count"],"A_B_pair_distance_values":pair["rows"]},
             "low_tier_matrix_files":low_rows,"files":files}
    receipt_path=out/"ANALYSIS_EXECUTION_RECEIPT.json"
    receipt_path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"receipt":str(receipt_path),"receipt_sha256":sha(receipt_path),
                      "analysis_script_sha256":sha(script),"runner_sha256":runner["sha256"],
                      "file_count":len(files)+1,"low_tier_rows":low_rows},indent=2))


if __name__=="__main__": main()
