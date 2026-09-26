#!/usr/bin/env python3
"""Read-only post-run export recovery for the frozen 728-cell PFBS MM matrix."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

FROZEN_EXPORTER_SHA256 = "e16a3c630f240aafcce9473d958e708ffbedc5f10b9b2680bb5a7832ca802340"
FROZEN_MANIFEST_SHA256 = "3407ba87b7e655d70d3eba09a406316425060ae11df2b94490e983580db9b48d"
FROZEN_FREEZE_SHA256 = "91e9ded53499399d34c7593c7994f3f7909738bcefb3f620ae1392b1be142b46"
FROZEN_CAPABILITY_SHA256 = "74acdf35570a87fc2702cf3ad251a82b51a18c7137d0365919f0220fe80e7cd3"
FROZEN_PREFLIGHT_SHA256 = "9f4a07796cfd3c78fe6b9964d29d0974d7e40727162e234b2a8807f469b9d6ec"
FROZEN_RELEASE_SHA256 = "b0805ebe88cf3a8eba1ff73ba5df43a22f15a1f43e3a1dffabaa64f33a041620"
FROZEN_SOURCE_BINDING_SHA256 = "3db5405f9e61def94b99aba1b6edf6ea5620572d4a69ced384edf5094810e0ff"
FROZEN_QM_SOURCE_BINDING_SHA256 = "315a741f8441c0bf37657f2e6e477691ed85e78cdc8e6213de8e53d369bb8ded"
RECOVERY_CLASS = "DETERMINISTIC_METADATA_REPAIR"
SOURCE_BINDING = None


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def load_frozen_exporter(path):
    if sha256_file(path) != FROZEN_EXPORTER_SHA256:
        raise ValueError("frozen exporter hash mismatch")
    spec = importlib.util.spec_from_file_location("frozen_cc_exporter", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_source_binding(path, source_dir, manifest, module):
    global SOURCE_BINDING
    if sha256_file(path) != FROZEN_SOURCE_BINDING_SHA256:
        raise ValueError("frozen CC source binding hash mismatch")
    binding = json.loads(Path(path).read_text(encoding="utf-8"))
    if manifest.get("source_binding_hash") != FROZEN_SOURCE_BINDING_SHA256:
        raise ValueError("manifest source binding identity mismatch")
    source_file = binding.get("source_file")
    source_sha = binding.get("source_sha256")
    expected = manifest.get("source_files", {}).get(source_file, {}).get("sha256")
    if source_file != "pfbs_ani.prm" or source_sha != expected:
        raise ValueError("frozen source binding and manifest disagree")
    source_path = Path(source_dir) / source_file
    if not source_path.is_file() or sha256_file(source_path) != source_sha:
        raise ValueError("immutable source parameter file hash mismatch")
    SOURCE_BINDING = {
        "source_file": source_file,
        "source_sha256": source_sha,
        "source_relative_path": f"immutable_sources/{source_file}",
        "source_binding_sha256": FROZEN_SOURCE_BINDING_SHA256,
        "source_manifest_sha256": FROZEN_MANIFEST_SHA256,
    }
    return SOURCE_BINDING


def recovered_validated_row(module, receipt_path, state, source_id):
    receipt_path = Path(receipt_path)
    rec = json.loads(receipt_path.read_text(encoding="utf-8"))
    missing = sorted(module.REQUIRED_RECEIPT_FIELDS - set(rec))
    if missing:
        raise ValueError(f"{receipt_path}: missing receipt fields {missing}")
    expected_state = module.state_key(state)
    if rec["state_key"] != expected_state or rec["source_id"] != source_id:
        raise ValueError(f"receipt logical identity/path mismatch: {receipt_path}")
    receipt_state = {"stage": rec["state_stage"], "state_id": rec["state_id"],
                     "variable_id": rec["variable_id"], "multiplier": rec["multiplier"],
                     "tolerance": rec["emtol_kj_mol_nm"]}
    if receipt_state != state:
        raise ValueError(f"receipt state definition mismatch: {expected_state}/{source_id}")
    if rec["status"] != module.TERMINAL_STATUS or not rec["cg_converged"] or not rec["minimization_converged"]:
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
        if not path.is_file() or module.sha256_file(path) != expected_hash:
            raise ValueError(f"receipt/artifact hash mismatch: {expected_state}/{source_id}/{name}")
        actual_artifacts[name] = expected_hash
    parameter_receipt = state_dir / "STATE_PARAMETER_RECEIPT.json"
    if not parameter_receipt.is_file() or module.sha256_file(parameter_receipt) != rec["parameter_receipt_sha256"]:
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

    # V5 runner stores per-file provenance as a mapping; the frozen exporter
    # mistakenly required a list. Validate its exact file domain and its
    # equality to the independent allowed-line mapping, including empty BASE.
    effective = parameter.get("effective_hashes")
    changed = parameter.get("changed_source_lines")
    allowed = parameter.get("allowed_source_lines")
    source_names = {"ffbonded.itp", "pfbs_ani.itp", "pfbs_ani.prm"}
    if not isinstance(effective, dict) or set(effective) != source_names:
        raise ValueError(f"incomplete effective parameter hashes: {expected_state}")
    if not isinstance(changed, dict) or set(changed) != source_names or changed != allowed:
        raise ValueError(f"changed/allowed parameter-line provenance mismatch: {expected_state}")
    baseline = parameter.get("baseline_hashes")
    if not isinstance(baseline, dict) or set(baseline) != source_names:
        raise ValueError(f"incomplete baseline parameter hashes: {expected_state}")
    if baseline.get(SOURCE_BINDING["source_file"]) != SOURCE_BINDING["source_sha256"]:
        raise ValueError(f"source parameter identity mismatch: {expected_state}")

    row = dict(rec)
    row.update({
        "start_coordinates_nm": module.g96_coordinates(job / "start.g96"),
        "lbfgs_final_coordinates_nm": module.g96_coordinates(job / "lbfgs_final.g96"),
        "final_coordinates_nm": module.g96_coordinates(job / "final.g96"),
        "artifact_hashes": actual_artifacts,
        "effective_parameter_hashes": effective,
        "changed_source_lines": changed,
        "parameter_source_binding": dict(SOURCE_BINDING),
        "run_receipt_sha256": module.sha256_file(receipt_path),
        "run_receipt_path": f"states/{expected_state}/runs/{source_id}/RUN_RECEIPT.json",
    })
    return row


def inventory_matrix(root):
    records = []
    for receipt_path in sorted(Path(root).glob("states/*/runs/*/RUN_RECEIPT.json"), key=lambda p: p.as_posix()):
        rec = json.loads(receipt_path.read_text(encoding="utf-8"))
        job = receipt_path.parent
        records.append({
            "state_key": rec["state_key"], "source_id": rec["source_id"],
            "run_receipt_sha256": sha256_file(receipt_path),
            "parameter_receipt_sha256": rec["parameter_receipt_sha256"],
            "artifact_sha256": {name: sha256_file(job / name) for name in (
                "start.g96", "lbfgs_final.g96", "final.g96", "topol_physical.top", "physical_potential.xvg")},
            "potential_kj_mol": rec["potential_kj_mol"],
            "xvg_last_line": rec["xvg_last_line"],
            "status": rec["status"],
        })
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--source-binding", type=Path, required=True)
    parser.add_argument("--qm-source-binding", type=Path, required=True)
    parser.add_argument("--frozen-exporter", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--recovery-receipt", type=Path, required=True)
    args = parser.parse_args()

    module = load_frozen_exporter(args.frozen_exporter)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    validate_source_binding(args.source_binding, args.source, manifest, module)
    if sha256_file(args.qm_source_binding) != FROZEN_QM_SOURCE_BINDING_SHA256:
        raise ValueError("frozen accepted-QM source binding hash mismatch")
    if module.sha256_file(args.manifest) != FROZEN_MANIFEST_SHA256:
        raise ValueError("frozen manifest hash mismatch")
    if module.sha256_file(args.source / "SELECTIVE_CC_EXECUTION_FREEZE.json") != FROZEN_FREEZE_SHA256:
        raise ValueError("execution freeze hash mismatch")
    if module.sha256_file(args.source / "ENGINE_CAPABILITY_RECEIPT.json") != FROZEN_CAPABILITY_SHA256:
        raise ValueError("engine capability receipt hash mismatch")
    if module.sha256_file(args.source / "ACTIVE_TPR_SEMANTIC_PREFLIGHT.json") != FROZEN_PREFLIGHT_SHA256:
        raise ValueError("active TPR preflight hash mismatch")
    if module.sha256_file(args.source / "SOL_HIGH_PREFLIGHT_RELEASE.json") != FROZEN_RELEASE_SHA256:
        raise ValueError("Sol High release hash mismatch")

    # Capture hashes before processing; the post-pass inventory must match.
    before = inventory_matrix(args.root)
    module._validated_row = lambda receipt_path, state, source_id: recovered_validated_row(
        module, receipt_path, state, source_id)
    binding = json.loads(args.qm_source_binding.read_text(encoding="utf-8"))
    source_ids = [row["point_id"] for row in binding["points"]] + [
        "T_CC_240_FROM_REVERSE_QM", "GEO_A", "GEO_B_REVISED"]
    provenance_paths = {
        "freeze": args.source / "SELECTIVE_CC_EXECUTION_FREEZE.json",
        "capability": args.source / "ENGINE_CAPABILITY_RECEIPT.json",
        "preflight": args.source / "ACTIVE_TPR_SEMANTIC_PREFLIGHT.json",
        "release": args.source / "SOL_HIGH_PREFLIGHT_RELEASE.json",
    }
    export = module.build_export(args.root, args.manifest, source_ids, provenance_paths, strict_selective=True)
    export["recovery_provenance"] = {
        "class": RECOVERY_CLASS,
        "recovery_exporter_sha256": sha256_file(Path(__file__).resolve()),
        "original_frozen_exporter_sha256": FROZEN_EXPORTER_SHA256,
        "source_parameter_file": SOURCE_BINDING["source_file"],
        "source_parameter_sha256": SOURCE_BINDING["source_sha256"],
        "source_binding_sha256": SOURCE_BINDING["source_binding_sha256"],
        "repair": "Accept frozen runner's per-file changed_source_lines mapping; preserve all original receipt values and add explicit unique source binding.",
        "recalculation_performed": False,
    }
    if len(export.get("rows", [])) != 728 or export.get("controller_status") != "COMPLETE":
        raise ValueError("recovered export is not exactly the terminal 728-row matrix")

    after = inventory_matrix(args.root)
    if before != after:
        raise ValueError("existing MM output inventory changed during read-only export recovery")
    inventory = {
        "schema": "PFBS_CC_SHAPE_POSTRUN_INPUT_INVENTORY_V1",
        "status": "PASS_EXISTING_728_OUTPUTS_UNCHANGED",
        "rows": len(after),
        "run_control_sha256": sha256_file(Path(args.root) / "receipts" / "RUN_CONTROL.json"),
        "records": after,
    }
    inventory_payload = module.canonical_bytes(inventory)
    args.inventory.parent.mkdir(parents=True, exist_ok=True)
    with args.inventory.open("xb") as stream:
        stream.write(inventory_payload)
    inventory_sha = hashlib.sha256(inventory_payload).hexdigest()

    export["recovery_provenance"]["input_inventory_sha256"] = inventory_sha
    export_payload = module.canonical_bytes(export)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as stream:
        stream.write(export_payload)
    export_sha = hashlib.sha256(export_payload).hexdigest()
    with args.output.with_suffix(args.output.suffix + ".sha256").open("x", encoding="ascii", newline="\n") as stream:
        stream.write(f"{export_sha}  {args.output.name}\n")

    receipt = {
        "schema": "PFBS_CC_SHAPE_POSTRUN_EXPORT_RECOVERY_RECEIPT_V1",
        "status": "PASS_DETERMINISTIC_METADATA_REPAIR",
        "recovery_class": RECOVERY_CLASS,
        "rows": 728,
        "rerun": False,
        "numerical_calculations_changed": False,
        "run_control_sha256": inventory["run_control_sha256"],
        "input_inventory_sha256": inventory_sha,
        "recovered_export_sha256": export_sha,
        "recovery_exporter_sha256": export["recovery_provenance"]["recovery_exporter_sha256"],
        "original_frozen_exporter_sha256": FROZEN_EXPORTER_SHA256,
        "source_parameter_file": SOURCE_BINDING,
        "state_receipt_schema_audit": "changed_source_lines is a dict with exact 3-file key domain and equals allowed_source_lines for all states; baseline source hash is bound in every state receipt.",
        "execution_provenance": export["execution_provenance"],
    }
    args.recovery_receipt.parent.mkdir(parents=True, exist_ok=True)
    args.recovery_receipt.write_bytes(module.canonical_bytes(receipt))
    print(json.dumps({
        "status": receipt["status"], "rows": 728,
        "export_sha256": export_sha, "inventory_sha256": inventory_sha,
        "recovery_receipt_sha256": sha256_file(args.recovery_receipt),
        "recovery_exporter_sha256": receipt["recovery_exporter_sha256"],
        "source_parameter_sha256": SOURCE_BINDING["source_sha256"],
        "numerical_calculations_changed": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
