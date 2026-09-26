#!/usr/bin/env python3
"""Read-only compact export of the frozen PFBS MM identifiability run.

This collector does not invoke GROMACS or modify the runtime tree. It refuses
to export while RUN_CONTROL.json is RUNNING, and records missing/failed cells
explicitly rather than dropping them.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path


ARTIFACTS = (
    "start.g96", "topol_min.top", "topol_physical.top", "pfbs_ani_restraint.itp",
    "lbfgs.mdp", "lbfgs_processed.mdp", "lbfgs.tpr", "lbfgs.log", "lbfgs.edr",
    "lbfgs.trr", "lbfgs_positionred.g96", "lbfgs_final.g96",
    "cg.mdp", "cg_processed.mdp", "cg.tpr", "cg.log", "cg.edr", "cg.trr",
    "final_positionred.g96", "final.g96", "physical.mdp", "physical_processed.mdp",
    "physical.tpr", "physical.log", "physical.edr", "physical_potential.xvg",
    "grompp_lbfgs.stdout_stderr.txt", "grompp_lbfgs.retry_maxwarn1.stdout_stderr.txt",
    "grompp_cg.stdout_stderr.txt", "grompp_physical.stdout_stderr.txt",
    "mdrun_lbfgs.stdout_stderr.txt", "mdrun_cg.stdout_stderr.txt",
    "mdrun_physical.stdout_stderr.txt", "energy_physical.stdout_stderr.txt",
    "trjconv_lbfgs.stdout_stderr.txt", "trjconv_cg.stdout_stderr.txt",
    "gmx_check_cg_trr.txt",
)
TERMINAL_CONTROL = {
    "COMPLETE", "COMPLETE_WITH_NUMERICAL_NONCONVERGENCE",
    "STOPPED_ON_EXECUTION_FAILURE", "INCOMPLETE",
}


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def g96_coordinates(path: Path):
    """Return ordered atom labels and raw parsed nm coordinates from named G96."""
    lines = path.read_text(encoding="ascii").splitlines()
    marker = "POSITION" if "POSITION" in lines else None
    if marker is None:
        raise ValueError(f"no named POSITION section: {path}")
    start = lines.index(marker) + 1
    end = lines.index("END", start)
    rows = []
    for line in lines[start:end]:
        fields = line.split()
        if not fields:
            continue
        if len(fields) != 7:
            raise ValueError(f"malformed named G96 row: {line!r}")
        atom = fields[2]
        xyz = [float(value) for value in fields[4:7]]
        if not all(math.isfinite(value) for value in xyz):
            raise ValueError(f"nonfinite G96 coordinate: {line!r}")
        rows.append({"atom": atom, "xyz_nm": xyz, "xyz_raw_nm": fields[4:7]})
    expected = ["S1"] + [f"F{i}" for i in range(1, 10)] + [f"O{i}" for i in range(1, 4)] + [f"C{i}" for i in range(1, 5)]
    if [row["atom"] for row in rows] != expected:
        raise ValueError(f"17-atom order mismatch in {path}")
    return rows


def expected_cells(runtime: Path):
    source = runtime / "immutable_sources"
    manifest = json.loads((source / "MM_RUN_MANIFEST.json").read_text(encoding="utf-8"))
    binding = json.loads((source / "QM_SOURCE_BINDING.json").read_text(encoding="utf-8"))
    state_rows = manifest["states"]
    source_ids = [point["point_id"] for point in binding["points"]]
    source_ids += ["T_CC_240_FROM_REVERSE_QM", "GEO_A", "GEO_B_REVISED"]
    if len(state_rows) != 62 or len(set(source_ids)) != 28 or manifest.get("expected_runs") != 1736:
        raise ValueError("frozen 62-state/28-source/1736-cell manifest invariant failed")
    cells = []
    for state in state_rows:
        stage = state["stage"]
        state_id = state["state_id"]
        state_key = f"{stage}__{state_id}"
        for source_id in source_ids:
            cells.append((state_key, source_id))
    return manifest, cells


def collect(runtime_root: Path, output_dir: Path):
    runtime = runtime_root.resolve(strict=True)
    control_path = runtime / "receipts" / "RUN_CONTROL.json"
    control = json.loads(control_path.read_text(encoding="utf-8"))
    if control.get("status") not in TERMINAL_CONTROL:
        raise RuntimeError(f"controller is not terminal: {control.get('status')!r}")

    manifest, cells = expected_cells(runtime)
    receipts = {}
    duplicate_keys = []
    for path in (runtime / "states").glob("*/runs/*/RUN_RECEIPT.json"):
        raw = path.read_bytes()
        rec = json.loads(raw)
        key = (rec.get("state_key", path.parents[2].name), rec.get("source_id", path.parent.name))
        if key in receipts:
            duplicate_keys.append(key)
            continue
        receipts[key] = (path, rec, hashlib.sha256(raw).hexdigest())
    if duplicate_keys:
        raise RuntimeError(f"duplicate state/source receipts: {duplicate_keys[:5]}")

    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    missing = []
    for state_key, source_id in cells:
        entry = receipts.get((state_key, source_id))
        if entry is None:
            missing.append({"state_key": state_key, "source_id": source_id})
            rows.append({"state_key": state_key, "source_id": source_id, "status": "MISSING_NOT_RUN"})
            continue
        path, rec, receipt_hash = entry
        row = dict(rec)
        row["run_receipt_path"] = str(path)
        row["run_receipt_sha256"] = receipt_hash
        row["run_directory"] = str(path.parent)
        row["artifact_hashes"] = {
            name: sha(path.parent / name)
            for name in ARTIFACTS if (path.parent / name).is_file()
        }
        for name in ("start.g96", "lbfgs_final.g96", "final.g96"):
            artifact = path.parent / name
            if artifact.is_file():
                try:
                    row[name.replace(".g96", "_coordinates_nm")] = g96_coordinates(artifact)
                except Exception as exc:
                    row[name.replace(".g96", "_coordinate_parse_error")] = f"{type(exc).__name__}: {exc}"
        row["raw_energy_xvg_last_line"] = rec.get("xvg_last_line")
        row["raw_warning_events"] = rec.get("warning_events", [])
        rows.append(row)

    seen = {(row.get("state_key"), row.get("source_id")) for row in rows}
    unexpected = sorted([list(key) for key in receipts if key not in set(cells)])
    status_counts = {}
    for row in rows:
        status = row.get("status", "UNKNOWN")
        status_counts[status] = status_counts.get(status, 0) + 1

    launch_record = None
    launch_dir = runtime / "matrix_launches"
    if launch_dir.exists():
        candidates = sorted(launch_dir.glob("*/LAUNCH_RECORD.json"))
        if candidates:
            candidate = candidates[-1]
            launch_record = {"path": str(candidate), "sha256": sha(candidate)}

    report = {
        "schema": "PFBS_MM_IDENTIFIABILITY_COMPACT_RUN_EXPORT_v1",
        "controller_status": control.get("status"),
        "run_control": {"path": str(control_path), "sha256": sha(control_path), "record": control},
        "manifest": {
            "path": str(runtime / "immutable_sources" / "MM_RUN_MANIFEST.json"),
            "sha256": sha(runtime / "immutable_sources" / "MM_RUN_MANIFEST.json"),
            "protocol_hash": manifest["protocol_hash"], "expected_cells": len(cells),
            "states": len(manifest["states"]), "source_count": 28,
        },
        "launch_record": launch_record,
        "counts": {"expected": len(cells), "receipts": len(receipts), "rows": len(rows),
                   "missing_cells": len(missing), "unexpected_receipts": len(unexpected),
                   "by_status": status_counts},
        "missing_cells": missing,
        "unexpected_receipts": unexpected,
        "rows": rows,
    }
    json_path = output_dir / "MATRIX_COMPACT_RUN_EXPORT.json"
    json_path.write_text(json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n", encoding="utf-8")

    columns = [
        "state_key", "state_stage", "state_id", "variable_id", "multiplier", "emtol_kj_mol_nm",
        "source_id", "status", "error", "started_epoch", "completed_epoch", "elapsed_seconds",
        "source_geometry_sha256", "start_g96_sha256", "parameter_receipt_sha256",
        "lbfgs_fmax_kj_mol_nm", "lbfgs_fmax_within_tolerance_diagnostic",
        "cg_fmax_kj_mol_nm", "cg_converged", "minimization_converged",
        "potential_kj_mol", "raw_energy_xvg_last_line", "xvg_last_time_ps",
        "xvg_precision_decimal_digits", "energy_output_option_dp",
        "cg_trr_sha256", "cg_trr_last_frame_index", "cg_trr_last_frame_time_ps",
        "xvg_sha256", "final_g96_sha256", "physical_topology_sha256",
        "start_pair_domain", "lbfgs_pair_domain", "cg_final_pair_domain",
        "raw_warning_events", "artifact_hashes", "run_receipt_sha256", "run_directory",
    ]
    with (output_dir / "MATRIX_COMPACT_RUN_EXPORT.tsv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(row.get(k), sort_keys=True, separators=(",", ":"))
                             if isinstance(row.get(k), (dict, list)) else row.get(k)
                             for k in columns})
    return json_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = collect(args.runtime_root, args.output_dir)
    print(output)


if __name__ == "__main__":
    main()
