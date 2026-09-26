#!/usr/bin/env python3
"""Build an immutable state/source manifest for the PFBS MM preflight.

This script only reads the frozen preregistration and audited v1 files. It
does not run GROMACS or edit any production/audit source.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(r"E:\AI-App-Data\PFAS_mito_membrane_pilot")
V1 = ROOT / "broad_pre_qm_audit_work_20260926" / "package"
WORK = ROOT / "broad_pre_qm_v2_work_20260926"
PRE = WORK / "preregistered_inputs"
OUT = WORK / "executor" / "inputs" / "MM_RUN_MANIFEST.json"
EXPECTED = {
    "NUMERICAL_IDENTIFIABILITY_PROTOCOL.md": "52dae28ac8b5484e39302323cd9f0eed75c0c779406c210072c64a41ccb0da59",
    "MM_IDENTIFIABILITY_VARIABLE_SPEC.json": "5b6e40bad2aa6cd683acd3ba04e3a8e9e019d70d23ae84913e8b14f938055c61",
    "INITIAL_DIAGNOSTIC_VARIABLES.tsv": "afb72bd4cbade810c005d0c9f1496883f7ed614c68542fc0d05d63fec7863db7",
    "BRANCH_CLASSIFIER_PREREGISTRATION_ADDENDUM.md": "21c9381e097fb8ef3e23ac2a3ab86ab4b71ab2f9629eaa7762f1e98702369d55",
    "BASIN_AND_MATHEMATICAL_RATIONALE_ADDENDUM.md": "ee4e963b5055fb8759032cb3991c8e2d70f1f4840d53b4a7d10135b3d8c29c13",
}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load_tsv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def term_source(term_id: str, table: list[dict], expected_value: float, value_index: int):
    matches = [r for r in table if r["term_id"] == term_id]
    if len(matches) != 1:
        raise ValueError(f"{term_id}: expected one audited source row, found {len(matches)}")
    row = matches[0]
    values = [float(x) for x in row["source_values_exact"].split()]
    if abs(values[value_index] - expected_value) > 5e-8:
        raise ValueError(f"{term_id}: preregistered base {expected_value} != v1 source {values[value_index]}")
    source = Path(row["source_file"]).name
    if source not in {"ffbonded.itp", "pfbs_ani.prm"}:
        raise ValueError(f"{term_id}: unsupported parameter source {source}")
    return {
        "term_id": term_id,
        "source_file": source,
        "source_line_1based": int(row["source_line"]),
        "source_values_exact": row["source_values_exact"],
        "source_sha256": row["source_sha256"],
        "atom_types": row.get("atom_types", ""),
    }


def main():
    for name, expected in EXPECTED.items():
        got = sha(PRE / name)
        if got != expected:
            raise SystemExit(f"FROZEN_PREREG_HASH_FAIL {name}: {got} != {expected}")
    manifest_v1 = json.loads((V1 / "PACKAGE_MANIFEST.json").read_text(encoding="utf-8"))
    if manifest_v1["authoritative_decision"] != "BROAD_PFBS_REPARAMETERIZATION_REQUIRED":
        raise SystemExit("v1 decision mismatch")
    spec = json.loads((PRE / "MM_IDENTIFIABILITY_VARIABLE_SPEC.json").read_text(encoding="utf-8"))
    bonds = load_tsv(V1 / "CURRENT_BOND_TERMS.tsv")
    angles = load_tsv(V1 / "CURRENT_ANGLE_TERMS.tsv")
    torsions = load_tsv(V1 / "CURRENT_TORSION_TERMS.tsv")
    v1_source_files = {
        "pfbs_ani.itp": V1 / "current_parameters" / "pfbs_ani.itp",
        "pfbs_ani.prm": V1 / "current_parameters" / "pfbs_ani.prm",
        "ffbonded.itp": ROOT / "broad_pre_qm_audit_work_20260926" / "source_readonly_cache" / "ffbonded.itp",
    }
    expected_files = {
        "pfbs_ani.itp": "c736e8e20ee778fd64dfc2b95da13040b6a49404c78dc1cf46dd7368b016aeca",
        "pfbs_ani.prm": "24baf41553845380e9905f7419ca85cb0528dcd7652d596ca6ba83e003d05a56",
        "ffbonded.itp": "cda750df0be35f862599f276f667be608b266a7a0aee085d2f623e82796403cf",
    }
    for name, path in v1_source_files.items():
        if sha(path) != expected_files[name]:
            raise SystemExit(f"AUDITED_SOURCE_HASH_FAIL {path}")

    tables = {
        "BOND_EQUILIBRIUM": bonds,
        "ANGLE_EQUILIBRIUM": angles,
        "GROUPED_TORSION_DIAGNOSTIC_ONLY": torsions,
    }
    field_index = {
        ("BOND_EQUILIBRIUM", "r0_nm"): 0,
        ("ANGLE_EQUILIBRIUM", "theta0_deg"): 0,
        ("GROUPED_TORSION_DIAGNOSTIC_ONLY", "proportional_amplitude_scale"): 1,
    }
    variables = []
    for var in spec["variables"]:
        tbl = tables[var["parameter_class"]]
        expected = [t["term_id"] for t in var["terms"]]
        if var["parameter_class"] == "GROUPED_TORSION_DIAGNOSTIC_ONLY":
            expected = [t["term_id"] for t in var["terms"]]
        mapped = []
        for term in var["terms"]:
            value_index = 1 if var["parameter_class"] == "GROUPED_TORSION_DIAGNOSTIC_ONLY" else 0
            src = term_source(term["term_id"], tbl, float(term.get("base", term.get("base_amplitude_kJ_mol"))), value_index)
            src["base_value"] = float(term.get("base", term.get("base_amplitude_kJ_mol")))
            src["parameter_token_index_0based"] = field_index[(var["parameter_class"], var["field"])] + (3 if var["parameter_class"] == "BOND_EQUILIBRIUM" else 4 if var["parameter_class"] == "ANGLE_EQUILIBRIUM" else 0)
            if var["parameter_class"] == "GROUPED_TORSION_DIAGNOSTIC_ONLY":
                src["parameter_token_index_0based"] = 6
                src["multiplicity"] = int(term["multiplicity"])
                src["phase_deg"] = float(term["phase_deg"])
            mapped.append(src)
        variables.append({**var, "source_rows": mapped})

    states = [{"stage": "primary", "state_id": "BASE", "variable_id": None, "multiplier": 0, "tolerance": 1.0}]
    for v in variables:
        for m in (-2, -1, 1, 2):
            states.append({"stage": "primary", "state_id": f"{v['id']}_{m:+d}h", "variable_id": v["id"], "multiplier": m, "tolerance": 1.0})
    states += [{"stage": "tight_audit", "state_id": "BASE", "variable_id": None, "multiplier": 0, "tolerance": 0.1}]
    for v in variables:
        for m in (-1, 1):
            states.append({"stage": "tight_audit", "state_id": f"{v['id']}_{m:+d}h", "variable_id": v["id"], "multiplier": m, "tolerance": 0.1})
    if len(states) != 62 or sum(s["stage"] == "primary" for s in states) != 41:
        raise SystemExit(f"unexpected state counts: {len(states)}")

    result = {
        "protocol_id": spec["protocol_id"],
        "protocol_hash": "52dae28ac8b5484e39302323cd9f0eed75c0c779406c210072c64a41ccb0da59",
        "variable_spec_hash": EXPECTED["MM_IDENTIFIABILITY_VARIABLE_SPEC.json"],
        "v1_zip_hash": "ddb9eac8347fe721e11b476a63daa4bff7617bf9a61217d95ff867d980b2cbd0",
        "source_files": {k: {"path": str(v), "sha256": expected_files[k]} for k, v in v1_source_files.items()},
        "variables": variables,
        "states": states,
        "expected_profile_sources": 26,
        "expected_total_sources": 28,
        "expected_runs": 1736,
        "gromacs": {
            "remote_binary": "/home/ls/projects/PFAS_mito_membrane_pilot/qm/PFBS/phase3_mm_relaxed_profiles_20260926_v1/gromacs_double_build/bin/gmx_d",
            "binary_sha256": "910c195c43f12f35e44ff5ccfdafd3236bf86c6afb0774b550e0ccb5d5148c2d",
            "mdp_physics_source": "NUMERICAL_IDENTIFIABILITY_PROTOCOL.md section 2; source v1 profile mdp settings",
            "cutoff_nm": 2.0,
            "box_nm": 10.0,
            "restraint_k_kj_mol_rad2": 500000.0,
            "restraint_semantics": "Only profile points; exact v1 dihedral_restraints semantics; physical energy from no-restraint topology",
            "max_workers": 16,
            "threads_per_worker": 1,
            "gpu": "disabled",
        },
        "geometry_start_candidates": {
            "GEO_A": {"path": "deliverable/qm/PFBS/phase3_torsion_20260924/TASK1_BONDED_CANDIDATE_20260926_v1/payload/final_evidence_01/formal_dp_runs/GEO_A/base/start.g96", "sha256": "bf6d3b621559c8a9eab217fdb97f1679c9dff8be0a8702542092e3f650516442"},
            "GEO_B": {"path": "deliverable/qm/PFBS/phase3_torsion_20260924/TASK1_BONDED_CANDIDATE_20260926_v1/payload/final_evidence_01/formal_dp_runs/GEO_B_REVISED_10nm/base/start.g96", "sha256": "fc99a7915d74ebe8529d1f6619ca528a33b14c721384b3fe84f65a1cf1678cb3"},
        },
        "warning_exception": "For efficient BFGS minimization, use switch/shift/pme instead of cut-off.",
        "branch_addendum_hash": EXPECTED["BRANCH_CLASSIFIER_PREREGISTRATION_ADDENDUM.md"],
        "math_addendum_hash": EXPECTED["BASIN_AND_MATHEMATICAL_RATIONALE_ADDENDUM.md"],
        "mm_profile_drift_max_deg": 0.020,
        "unrestrained_proper_minimax_max_deg": 30.0,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(OUT), "variables": len(variables), "states": len(states), "expected_runs": result["expected_runs"], "hashes": {k: sha(PRE / k) for k in EXPECTED}}, indent=2))


if __name__ == "__main__":
    main()
