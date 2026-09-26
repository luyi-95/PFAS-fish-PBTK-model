#!/usr/bin/env python3
"""Report-only derivative QC and leave-one-source-block-out diagnostics.

Reads the frozen v1 analysis outputs and preregistered low-tier specification.
It does not fit parameters, mutate scientific inputs, or launch calculations.
"""
import csv
import hashlib
import importlib.util
import json
import math
import pathlib
import sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent
ANALYSIS = ROOT / "final_analysis_v1"
REPO = ROOT.parent / "git_publish" / "PFAS_mito_membrane_pilot" / "qm" / "PFBS" / "reparameterization" / "pre_qm_audit_20260926_v2"
SPEC = REPO / "MVP_LOW_TIER_ROW_DIAGNOSTIC_SPEC.json"
CONTRACT = ROOT.parent / "executor" / "cc_shape_contracts.py"
OUT = ROOT / "supplemental_outputs_v1"
OUT.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("cc_shape_contracts", CONTRACT)
contracts = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = contracts
spec.loader.exec_module(contracts)


def read_tsv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv(path, rows):
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def keyed(name, cols):
    rows = read_tsv(ANALYSIS / name)
    return {r["observable_id"]: r for r in rows}, cols


ids = ["CC_FOURIER_1", "CC_FOURIER_2", "CC_FOURIER_3", "CC_FOURIER_4"]
sets = {
    "h": ("SELECTIVE_CC_JACOBIAN_NORMALIZED.tsv", "J_h_normalized__"),
    "2h": ("SELECTIVE_CC_JACOBIAN_2H_NORMALIZED.tsv", "J_2h_normalized__"),
    "tight": ("SELECTIVE_CC_JACOBIAN_TIGHT_NORMALIZED.tsv", "J_tight_normalized__"),
    "E": ("SELECTIVE_CC_UNCERTAINTY_NORMALIZED.tsv", "E_normalized__"),
}
tables = {}
for label, (name, prefix) in sets.items():
    rows = read_tsv(ANALYSIS / name)
    tables[label] = {r["observable_id"]: r for r in rows}
obs = list(tables["h"])
if any(set(tables[x]) != set(obs) for x in tables):
    raise SystemExit("normalized derivative row domains differ")
if len(obs) != 118:
    raise SystemExit(f"expected 118 primary observables; found {len(obs)}")

# Cellwise quality uses the exact frozen normalized finite differences and
# error bound E from the frozen analysis, applying the frozen contract to each
# scalar observable/parameter derivative.
qc = []
for oid in obs:
    hr, r2, tr, er = (tables[k][oid] for k in ("h", "2h", "tight", "E"))
    for v in ids:
        jh = float(hr["J_h_normalized__" + v])
        j2 = float(r2["J_2h_normalized__" + v])
        jt = float(tr["J_tight_normalized__" + v])
        e = float(er["E_normalized__" + v])
        status = contracts.finite_difference_status([jh], [j2], [jt], e, 0.10, 0.05)
        qc.append({
            "observable_id": oid,
            "source_id": hr["source_id"],
            "kind": hr["kind"],
            "variable_id": v,
            "J_h_normalized": f"{jh:.17g}",
            "J_2h_normalized": f"{j2:.17g}",
            "J_tight_normalized": f"{jt:.17g}",
            "E_normalized": f"{e:.17g}",
            "R_step": "" if status["R_step"] is None else f"{status['R_step']:.17g}",
            "R_step_limit": "0.10",
            "R_conv": "" if status["R_conv"] is None else f"{status['R_conv']:.17g}",
            "R_conv_limit": "0.05",
            "signal": f"{status['signal']:.17g}",
            "uncertainty": f"{status['uncertainty']:.17g}",
            "finite_difference_status": status["status"],
        })
write_tsv(OUT / "SELECTIVE_CC_DERIVATIVE_QC.tsv", qc)

# Full primary CC-only and combined matrices; rows are held in observable order.
def mat_from(table, prefix, rowids, cc_only=False):
    out = []
    for oid in rowids:
        row = table[oid]
        cols = [prefix + v for v in ids]
        if not cc_only:
            geom_cols = [k for k in row if k.startswith(prefix) and k not in cols]
            cols = geom_cols + cols
        out.append([float(row[c]) for c in cols])
    return np.asarray(out, dtype=float)

def rank_stats(h, err):
    if h.ndim != 2 or not len(h):
        return 0, 0.0, 0.0, 0.0, np.array([])
    s = np.linalg.svd(h, compute_uv=False)
    delta = float(np.linalg.norm(err, "fro"))
    machine = max(h.shape) * np.finfo(float).eps * (float(s[0]) if len(s) else 0.0)
    threshold = 5.0 * max(delta, machine)
    return int(np.sum(s > threshold)), delta, threshold, float(s[0]) if len(s) else 0.0, s

def svd_right(h, err, ncols):
    if not len(h):
        return 0, np.zeros(ncols), 0.0, 0.0, 0.0
    rank, delta, threshold, sigma, _ = rank_stats(h, err)
    _, _, vt = np.linalg.svd(h, full_matrices=True)
    vec = vt[0] if rank else np.zeros(ncols)
    return rank, vec, delta, threshold, sigma

allrows = tables["h"]
full_ids = list(obs)
meta = {r["observable_id"]: r for r in read_tsv(ANALYSIS / "SELECTIVE_CC_JACOBIAN_NORMALIZED.tsv")}
base_cc = mat_from(allrows, "J_h_normalized__", full_ids, True)
base_err = mat_from(tables["E"], "E_normalized__", full_ids, True)
base_rank, base_vec, base_delta, base_thresh, base_sigma = svd_right(base_cc, base_err, 4)

# Make a fixed row-order combined matrix from the frozen output. These columns
# are geometry first, then the exact four CC columns.
def comb_table(name):
    rows = read_tsv(ANALYSIS / name)
    return {r["observable_id"]: r for r in rows}
comb_h_t = comb_table("SELECTIVE_CC_JACOBIAN_COMBINED_NORMALIZED.tsv")
comb_err_t = comb_table("SELECTIVE_CC_COMBINED_UNCERTAINTY.tsv")
if any(set(t) != set(full_ids) for t in (comb_h_t, comb_err_t)):
    raise SystemExit("combined normalized matrix IDs differ from primary")
geom_ids = ["R_OG2P1-SG3O1", "R_CG312-SG3O1", "R_CG312-CG312", "TH_CG312-CG312-SG3O1"]
def array_from(d, prefix, ids0):
    return np.asarray([[float(d[oid][prefix + x]) for x in ids0] for oid in full_ids], dtype=float)
ch = array_from(comb_h_t, "J_combined_normalized__", geom_ids + ids)
ce = array_from(comb_err_t, "E_combined_normalized__", geom_ids + ids)
if ce.shape != ch.shape:
    # fallback to named output if header differs
    raise SystemExit(f"combined uncertainty shape mismatch: {ce.shape} vs {ch.shape}")
base_comb_rank, base_comb_vec, _, _, _ = svd_right(ch, ce, 8)

low_spec = json.loads(SPEC.read_text(encoding="utf-8-sig"))
low_tcs = {x["primary_energy_source_id"] for x in low_spec["selected_energy_rows"] if x["axis"] == "T_CS"}
if low_tcs != {"T_CS_050", "T_CS_060", "T_CS_070", "T_CS_080"}:
    raise SystemExit(f"unexpected preregistered T_CS low-tier block: {sorted(low_tcs)}")

branch = read_tsv(ANALYSIS / "CC_SHAPE_BRANCH_GAP.tsv")
branch_by_var = {r["variable_id"]: r for r in branch}
source_sets = [
    ("CC180_PROFILE_POINT", {"T_CC_180"}, "Delete the accepted T_CC_180 profile-energy row; the CC300 zero anchor remains."),
    ("CC300_ANCHOR_REANCHORED_TO_CC180", {"T_CC_300"}, "Physical anchor-dependence check: retain profile sources re-expressed relative to CC180 as specified in preregistration; no CC300 row is reconstructed."),
    ("GEO_A", {"GEO_A"}, "Delete all GEO_A observables, including its A/B energy row."),
    ("GEO_B", {"GEO_B_REVISED"}, "Delete all GEO_B observables, including its A/B energy row."),
    ("CC240_FORWARD", {"T_CC_240"}, "Delete the T_CC_240 forward profile-energy row."),
    ("T_CS_LOW_ENERGY_BLOCK", low_tcs, "Delete the exact four frozen T_CS low-tier selected profile-energy rows."),
]

def canonical(v):
    x=np.asarray(v,float).copy(); nz=np.flatnonzero(np.abs(x)>1e-12)
    if len(nz) and x[nz[0]] < 0: x=-x
    return x

loo=[]
for name, remove_sources, method in source_sets:
    if name == "CC300_ANCHOR_REANCHORED_TO_CC180":
        cc180="T_CC_180"
        # Reanchor all profile energies to CC180. The actual CC180 row becomes
        # the zero-reference row and is omitted; non-profile observables remain.
        keep=[]
        for oid in full_ids:
            row=meta[oid]
            if row["kind"] == "profile_energy":
                if row["source_id"] == cc180: continue
                keep.append(oid)
            else: keep.append(oid)
        def transform(d, prefix, err=False):
            vals=[]
            ref=meta[next(oid for oid in full_ids if meta[oid]["source_id"]==cc180 and meta[oid]["kind"]=="profile_energy")]["observable_id"]
            for oid in keep:
                row=meta[oid]
                if row["kind"]=="profile_energy":
                    a=np.array([float(d[oid][prefix+v]) for v in ids])
                    b=np.array([float(d[ref][prefix+v]) for v in ids])
                    vals.append(a+b if err else a-b)
                else: vals.append(np.array([float(d[oid][prefix+v]) for v in ids]))
            return np.asarray(vals)
        h=transform(allrows,"J_h_normalized__")
        err=transform(tables["E"],"E_normalized__",True)
        # 2h/tight physical LOO outputs are retained in the record only via h
        # rank; direction is tested on the source-frozen primary derivative.
    else:
        keep=[oid for oid in full_ids if meta[oid]["source_id"] not in remove_sources]
        h=mat_from(allrows,"J_h_normalized__",keep,True)
        err=mat_from(tables["E"],"E_normalized__",keep,True)
    rank, vec, delta, threshold, sigma=svd_right(h,err,4)
    cos=abs(float(np.dot(canonical(base_vec),canonical(vec)))) if rank and base_rank else None
    # Combined geometry+CC matrix uses identical block deletion. On CC300
    # reanchor, only the CC columns are transformed; geometry columns unchanged.
    if name == "CC300_ANCHOR_REANCHORED_TO_CC180":
        g_keep=[]; cc_keep=[]; e_keep=[]
        ref=next(oid for oid in full_ids if meta[oid]["source_id"]=="T_CC_180" and meta[oid]["kind"]=="profile_energy")
        for oid in keep:
            gh=np.array([float(comb_h_t[oid]["J_combined_normalized__"+v]) for v in geom_ids])
            gc=np.array([float(comb_h_t[oid]["J_combined_normalized__"+v]) for v in ids])
            eh=np.array([float(comb_err_t[oid]["E_combined_normalized__"+v]) for v in geom_ids])
            ec=np.array([float(comb_err_t[oid]["E_combined_normalized__"+v]) for v in ids])
            if meta[oid]["kind"]=="profile_energy":
                rc=np.array([float(comb_h_t[ref]["J_combined_normalized__"+v]) for v in ids])
                re=np.array([float(comb_err_t[ref]["E_combined_normalized__"+v]) for v in ids])
                gc=gc-rc; ec=ec+re
            g_keep.append(np.r_[gh,gc]); e_keep.append(np.r_[eh,ec])
        hc=np.asarray(g_keep); ec=np.asarray(e_keep)
    else:
        hc=np.asarray([[float(comb_h_t[oid]["J_combined_normalized__"+v]) for v in geom_ids+ids] for oid in keep])
        ec=np.asarray([[float(comb_err_t[oid]["E_combined_normalized__"+v]) for v in geom_ids+ids] for oid in keep])
    cr, cv, cdelta, cthreshold, csigma=svd_right(hc,ec,8)
    ccpart=cv[4:] if cr else np.zeros(4)
    cc_cos=abs(float(np.dot(canonical(base_vec),canonical(ccpart)))) if cr and base_rank and np.linalg.norm(ccpart)>0 else None
    loo.append({
        "block_test":name,"removed_source_ids":";".join(sorted(remove_sources)),"row_handling":method,
        "retained_primary_rows":len(keep),"CC_only_supported_rank":rank,"CC_only_sigma_max":f"{sigma:.17g}",
        "CC_only_delta_frobenius":f"{delta:.17g}","CC_only_5delta_threshold":f"{threshold:.17g}",
        "CC_only_top_direction_abs_cosine_to_full": "" if cos is None else f"{cos:.17g}",
        "combined_supported_rank":cr,"combined_sigma_max":f"{csigma:.17g}","combined_delta_frobenius":f"{cdelta:.17g}",
        "combined_5delta_threshold":f"{cthreshold:.17g}","combined_CC_component_abs_cosine_to_full_CC_direction":"" if cc_cos is None else f"{cc_cos:.17g}",
        "interpretation":"DIAGNOSTIC_ONLY; restricted original row weights retained; rank change does not authorize fitting.",
    })

# Branch reverse is branch-gap-only evidence and is absent from primary 118 rows.
base_m=json.loads((ANALYSIS/"SOURCE_PROVENANCE_MANIFEST.json").read_text(encoding="utf-8-sig"))
loo.append({
    "block_test":"CC240_REVERSE_BRANCH_ONLY","removed_source_ids":"T_CC_240_FROM_REVERSE_QM",
    "row_handling":"Remove branch-gap row from diagnostic 119 matrix; primary 118 rows are unchanged.",
    "retained_primary_rows":118,"CC_only_supported_rank":base_m["full_primary"]["rank"],
    "CC_only_sigma_max":f"{base_m['full_primary']['singular_values'][0]:.17g}",
    "CC_only_delta_frobenius":f"{base_m['full_primary']['delta_frobenius']:.17g}",
    "CC_only_5delta_threshold":f"{base_m['full_primary']['threshold_5delta']:.17g}",
    "CC_only_top_direction_abs_cosine_to_full":"1.0",
    "combined_supported_rank":base_m["combined_4plus4"]["rank"],
    "combined_sigma_max":f"{base_m['combined_4plus4']['singular_values'][0]:.17g}",
    "combined_delta_frobenius":f"{base_m['combined_4plus4']['delta_frobenius']:.17g}",
    "combined_5delta_threshold":f"{base_m['combined_4plus4']['threshold_5delta']:.17g}",
    "combined_CC_component_abs_cosine_to_full_CC_direction":"1.0",
    "interpretation":"DIAGNOSTIC_ONLY; branch row is not a primary source row; removal restores 118-row primary matrix.",
})
write_tsv(OUT / "SELECTIVE_CC_LEAVE_ONE_BLOCK_OUT.tsv", loo)

# Summaries for reproducibility and review.
counts = {}
for r in qc:
    counts.setdefault(r["variable_id"], {}).setdefault(r["finite_difference_status"], 0)
    counts[r["variable_id"]][r["finite_difference_status"]] += 1
summary = {
    "schema":"PFBS_SELECTIVE_CC_SUPPLEMENTAL_AUDIT_V1",
    "analysis_only":True,"parameter_fit":False,"new_calculations":False,
    "derivative_qc_rows":len(qc),"derivative_qc_counts_by_variable":counts,
    "leave_one_block_out_tests":len(loo),"low_tier_T_CS_source_ids":sorted(low_tcs),
    "frozen_contract_sha256":sha(CONTRACT),"low_tier_spec_sha256":sha(SPEC),
    "inputs":{n:sha(ANALYSIS/n) for n in [
        "SELECTIVE_CC_JACOBIAN_NORMALIZED.tsv","SELECTIVE_CC_JACOBIAN_2H_NORMALIZED.tsv",
        "SELECTIVE_CC_JACOBIAN_TIGHT_NORMALIZED.tsv","SELECTIVE_CC_UNCERTAINTY_NORMALIZED.tsv",
        "SELECTIVE_CC_JACOBIAN_COMBINED_NORMALIZED.tsv","SELECTIVE_CC_COMBINED_UNCERTAINTY.tsv",
        "SOURCE_PROVENANCE_MANIFEST.json"]},
    "outputs":{"SELECTIVE_CC_DERIVATIVE_QC.tsv":sha(OUT/"SELECTIVE_CC_DERIVATIVE_QC.tsv"),
               "SELECTIVE_CC_LEAVE_ONE_BLOCK_OUT.tsv":sha(OUT/"SELECTIVE_CC_LEAVE_ONE_BLOCK_OUT.tsv")},
}
(OUT/"SUPPLEMENTAL_AUDIT_RECEIPT.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print(json.dumps(summary,indent=2,sort_keys=True))
