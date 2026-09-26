#!/usr/bin/env python3
"""Deterministic read-only finalizer for selective-CC RUN_RECEIPT matrices."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_FULL_FF_TREE_SHA256 = "6e55a031fb8285f9fa4734b3812a9c75ac0a1b3b71fb835afed475bc906895e2"
TERMINAL_STATUS = "DONE"
REQUIRED_RECEIPT_FIELDS = {
    "state_id", "state_stage", "variable_id", "multiplier", "emtol_kj_mol_nm",
    "source_id", "source_geometry_sha256", "start_g96_sha256", "state_key",
    "parameter_receipt_sha256", "branch_only", "geometry_only", "target_scanned_deg",
    "qm_scanned_deg", "status", "start_pair_domain", "lbfgs_fmax_kj_mol_nm",
    "lbfgs_final_g96_sha256", "lbfgs_pair_domain", "cg_fmax_kj_mol_nm",
    "final_g96_sha256", "cg_final_pair_domain", "physical_topology_sha256",
    "potential_kj_mol", "xvg_last_line", "xvg_sha256", "cg_converged",
    "minimization_converged", "warning_events"
}


def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def canonical_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def state_key(state):
    return f"{state['stage']}__{state['state_id']}"


def g96_coordinates(path):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    start = lines.index("POSITION") + 1
    end = lines.index("END", start)
    rows = []
    for line in lines[start:end]:
        fields = line.split()
        if len(fields) != 7:
            raise ValueError(f"malformed G96 POSITION row in {path}: {line!r}")
        raw = fields[4:7]
        rows.append({"atom": fields[2], "xyz_nm": [float(x) for x in raw], "xyz_raw_nm": raw})
    if len(rows) != 17:
        raise ValueError(f"{path}: expected 17 atoms, found {len(rows)}")
    expected = ["S1"] + [f"F{i}" for i in range(1, 10)] + [f"O{i}" for i in range(1, 4)] + [f"C{i}" for i in range(1, 5)]
    if [row["atom"] for row in rows] != expected:
        raise ValueError(f"{path}: atom identity/order mismatch")
    return rows


def _read_provenance(paths, manifest_hash):
    required = ("freeze", "capability", "preflight", "release")
    if set(paths) != set(required):
        raise ValueError(f"provenance paths must be exactly {required}")
    for path in paths.values():
        if not Path(path).is_file():
            raise ValueError(f"missing provenance record: {path}")
    hashes = {key: sha256_file(path) for key, path in paths.items()}
    freeze = json.loads(Path(paths["freeze"]).read_text(encoding="utf-8"))
    preflight = json.loads(Path(paths["preflight"]).read_text(encoding="utf-8"))
    release = json.loads(Path(paths["release"]).read_text(encoding="utf-8"))
    exporter_hash = sha256_file(Path(__file__).resolve())
    if freeze.get("status") != "EXECUTION_FROZEN" or freeze.get("execution_approved") is not True:
        raise ValueError("execution freeze is not approved")
    expected = {
        "manifest_sha256": manifest_hash,
        "exporter_sha256": exporter_hash,
        "engine_capability_receipt_sha256": hashes["capability"],
        "full_forcefield_tree_sha256": EXPECTED_FULL_FF_TREE_SHA256,
    }
    for key, value in expected.items():
        if freeze.get(key) != value:
            raise ValueError(f"freeze provenance mismatch: {key}")
    for key, value in expected.items():
        if preflight.get(key) != value:
            raise ValueError(f"preflight provenance mismatch: {key}")
    if release.get("status") != "PASS_SOL_HIGH_PREFLIGHT_RELEASE":
        raise ValueError("Sol High preflight release is not PASS")
    if release.get("preflight_receipt_sha256") != hashes["preflight"]:
        raise ValueError("Sol High release/preflight identity mismatch")
    for key, value in expected.items():
        if release.get(key) != value:
            raise ValueError(f"Sol High release provenance mismatch: {key}")
    return {
        "execution_freeze_sha256": hashes["freeze"],
        "engine_capability_receipt_sha256": hashes["capability"],
        "full_forcefield_tree_sha256": EXPECTED_FULL_FF_TREE_SHA256,
        "preflight_receipt_sha256": hashes["preflight"],
        "preflight_release_sha256": hashes["release"],
        "exporter_sha256": exporter_hash,
    }


def _validated_row(receipt_path, state, source_id):
    receipt_path = Path(receipt_path)
    rec = json.loads(receipt_path.read_text(encoding="utf-8"))
    missing = sorted(REQUIRED_RECEIPT_FIELDS - set(rec))
    if missing:
        raise ValueError(f"{receipt_path}: missing receipt fields {missing}")
    expected_state = state_key(state)
    if rec["state_key"] != expected_state or rec["source_id"] != source_id:
        raise ValueError(f"receipt logical identity/path mismatch: {receipt_path}")
    receipt_state = {"stage": rec["state_stage"], "state_id": rec["state_id"],
                     "variable_id": rec["variable_id"], "multiplier": rec["multiplier"],
                     "tolerance": rec["emtol_kj_mol_nm"]}
    if receipt_state != state:
        raise ValueError(f"receipt state definition mismatch: {expected_state}/{source_id}")
    if rec["status"] != TERMINAL_STATUS or not rec["cg_converged"] or not rec["minimization_converged"]:
        raise ValueError(f"nonterminal/nonconverged receipt: {expected_state}/{source_id}")
    job = receipt_path.parent
    state_dir = job.parents[1]
    if state_dir.name != expected_state or job.name != source_id:
        raise ValueError(f"receipt directory identity mismatch: {receipt_path}")
    artifacts = {
        "start.g96": rec["start_g96_sha256"],
        "lbfgs_final.g96": rec["lbfgs_final_g96_sha256"],
        "final.g96": rec["final_g96_sha256"],
        "topol_physical.top": rec["physical_topology_sha256"],
        "physical_potential.xvg": rec["xvg_sha256"],
    }
    actual_artifacts = {}
    for name, expected_hash in artifacts.items():
        path = job / name
        if not path.is_file() or sha256_file(path) != expected_hash:
            raise ValueError(f"receipt/artifact hash mismatch: {expected_state}/{source_id}/{name}")
        actual_artifacts[name] = expected_hash
    parameter_receipt = state_dir / "STATE_PARAMETER_RECEIPT.json"
    if not parameter_receipt.is_file() or sha256_file(parameter_receipt) != rec["parameter_receipt_sha256"]:
        raise ValueError(f"state parameter receipt mismatch: {expected_state}/{source_id}")
    parameter = json.loads(parameter_receipt.read_text(encoding="utf-8"))
    if parameter.get("state") != state:
        raise ValueError(f"state parameter definition mismatch: {expected_state}")
    if rec["source_geometry_sha256"] != rec["start_g96_sha256"]:
        raise ValueError(f"source/start geometry identity mismatch: {expected_state}/{source_id}")
    numeric = [line for line in (job / "physical_potential.xvg").read_text(encoding="utf-8").splitlines()
               if line.strip() and not line.startswith(("#", "@"))]
    if not numeric or numeric[-1] != rec["xvg_last_line"]:
        raise ValueError(f"physical energy last-line mismatch: {expected_state}/{source_id}")
    fields = numeric[-1].split()
    if len(fields) < 2 or float(fields[1]) != float(rec["potential_kj_mol"]):
        raise ValueError(f"physical energy value mismatch: {expected_state}/{source_id}")
    if any(not warning.get("approved") for warning in rec["warning_events"]):
        raise ValueError(f"unapproved warning in receipt: {expected_state}/{source_id}")
    if not isinstance(parameter.get("effective_hashes"), dict) or not isinstance(parameter.get("changed_source_lines"), list):
        raise ValueError(f"incomplete patched-parameter provenance: {expected_state}")
    row = dict(rec)
    row.update({
        "start_coordinates_nm": g96_coordinates(job / "start.g96"),
        "lbfgs_final_coordinates_nm": g96_coordinates(job / "lbfgs_final.g96"),
        "final_coordinates_nm": g96_coordinates(job / "final.g96"),
        "artifact_hashes": actual_artifacts,
        "effective_parameter_hashes": parameter.get("effective_hashes"),
        "changed_source_lines": parameter.get("changed_source_lines"),
        "run_receipt_sha256": sha256_file(receipt_path),
        "run_receipt_path": f"states/{expected_state}/runs/{source_id}/RUN_RECEIPT.json",
    })
    return row


def build_export(root, manifest_path, expected_source_ids, provenance_paths,
                 strict_selective=True):
    root = Path(root); manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    states = manifest.get("states", [])
    sources = list(expected_source_ids)
    if len(sources) != len(set(sources)):
        raise ValueError("duplicate expected source identifiers")
    if strict_selective and (len(states) != 26 or len(sources) != 28 or manifest.get("expected_runs") != 728):
        raise ValueError("selective-CC export must be exactly 26x28/728")
    expected = {(state_key(state), source): state for state in states for source in sources}
    receipt_paths = sorted(root.glob("states/*/runs/*/RUN_RECEIPT.json"), key=lambda p: p.as_posix())
    seen = {}
    unexpected = []
    for path in receipt_paths:
        rec = json.loads(path.read_text(encoding="utf-8"))
        key = (rec.get("state_key"), rec.get("source_id"))
        if key not in expected:
            unexpected.append({"path": str(path), "state_key": key[0], "source_id": key[1]})
            continue
        if key in seen:
            raise ValueError(f"duplicate run receipt cell: {key}")
        seen[key] = path
    missing = sorted(set(expected) - set(seen))
    if unexpected or missing:
        raise ValueError(f"run matrix mismatch: missing={missing} unexpected={unexpected}")
    rows = [_validated_row(seen[key], expected[key], key[1]) for key in sorted(expected)]
    control_path = root / "receipts" / "RUN_CONTROL.json"
    control = json.loads(control_path.read_text(encoding="utf-8"))
    if (control.get("status") != "COMPLETE" or control.get("total") != len(expected)
            or control.get("protocol_hash") != manifest.get("protocol_hash")
            or control.get("exporter_sha256") != sha256_file(Path(__file__).resolve())):
        raise ValueError("run control is not terminal COMPLETE for the exact matrix")
    manifest_hash = sha256_file(manifest_path)
    provenance = _read_provenance(provenance_paths, manifest_hash)
    return {
        "schema": "PFBS_SELECTIVE_CC_COMPACT_RUN_EXPORT_v1",
        "controller_status": "COMPLETE",
        "counts": {"rows": len(rows), "expected": len(expected), "missing_cells": 0,
                   "unexpected_receipts": 0, "by_status": {"DONE": len(rows)}},
        "manifest_sha256": manifest_hash,
        "manifest": {"sha256": manifest_hash, "states": len(states), "source_count": len(sources),
                     "expected_cells": len(expected), "protocol_hash": manifest.get("protocol_hash")},
        "execution_provenance": provenance,
        "run_control": {"sha256": sha256_file(control_path), "record": control},
        "rows": rows,
        "missing_cells": [], "unexpected_receipts": [],
    }


def write_export(export, output_path):
    output_path = Path(output_path)
    payload = canonical_bytes(export)
    with output_path.open("xb") as stream:
        stream.write(payload)
    digest = hashlib.sha256(payload).hexdigest()
    with output_path.with_suffix(output_path.suffix + ".sha256").open("x", encoding="ascii", newline="\n") as stream:
        stream.write(f"{digest}  {output_path.name}\n")
    return digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    binding = json.loads((args.source / "QM_SOURCE_BINDING.json").read_text(encoding="utf-8"))
    source_ids = [row["point_id"] for row in binding["points"]] + ["T_CC_240_FROM_REVERSE_QM", "GEO_A", "GEO_B_REVISED"]
    provenance = {"freeze": args.source / "SELECTIVE_CC_EXECUTION_FREEZE.json",
                  "capability": args.source / "ENGINE_CAPABILITY_RECEIPT.json",
                  "preflight": args.source / "ACTIVE_TPR_SEMANTIC_PREFLIGHT.json",
                  "release": args.source / "SOL_HIGH_PREFLIGHT_RELEASE.json"}
    export = build_export(args.root, args.manifest, source_ids, provenance, strict_selective=True)
    digest = write_export(export, args.output)
    print(json.dumps({"status": "PASS_COMPACT_EXPORT", "rows": len(export["rows"]),
                      "output_sha256": digest}, sort_keys=True))


if __name__ == "__main__":
    main()
