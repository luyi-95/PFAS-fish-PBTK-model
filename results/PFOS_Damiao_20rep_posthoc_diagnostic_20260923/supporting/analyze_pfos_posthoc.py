#!/usr/bin/env python3
"""Read-only post-hoc diagnostics for the frozen PFOS Damião ensemble.

This script reads existing COM/candidate-window artifacts and writes only to a
new, independent output directory. It never changes formal replicate status,
selected windows, diffusion estimates, or the frozen final package.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import statistics
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ACCEPTED = ["rep01", "rep06", "rep09", "rep10", "rep15", "rep17", "rep19"]
INCONCLUSIVE = [
    "rep02", "rep03", "rep04", "rep05", "rep07", "rep08", "rep11",
    "rep12", "rep13", "rep14", "rep16", "rep18", "rep20",
]
ACCEPTED_D = {
    "rep01": 0.5788674214028507,
    "rep06": 0.6899878781124122,
    "rep09": 0.5869804561231682,
    "rep10": 0.7798373127614145,
    "rep15": 0.6609537014570601,
    "rep17": 0.5258526815930208,
    "rep19": 0.677076302011815,
}
STANDARD_WINDOWS = [(500.0, 2000.0), (1000.0, 3000.0), (2000.0, 4000.0), (3000.0, 5000.0)]
TRESTARTS = [5.0, 10.0, 20.0, 50.0]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_tsv(path: Path, rows: list[dict], fields: list[str] | None = None) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    fields = fields or list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def read_csv_dicts(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_com_csv(path: Path) -> np.ndarray:
    a = np.genfromtxt(path, delimiter=",", names=True, dtype=float, encoding="utf-8")
    times = np.asarray(a["time_ps"], dtype=float)
    xyz = np.column_stack((a["com_x_nm"], a["com_y_nm"], a["com_z_nm"]))
    if xyz.shape != (20000, 3):
        raise ValueError(f"{path}: expected 20000 COM frames, got {xyz.shape}")
    if not (math.isclose(times[0], 1000.5) and math.isclose(times[-1], 11000.0)):
        raise ValueError(f"{path}: wrong strict analysis interval")
    if not np.allclose(np.diff(times), 0.5, atol=1e-9):
        raise ValueError(f"{path}: nonuniform frame spacing")
    if not np.isfinite(xyz).all():
        raise ValueError(f"{path}: nonfinite COM")
    return xyz


def candidate_grid() -> list[tuple[float, float]]:
    return [
        (float(s), float(e))
        for s in np.arange(500.0, 3500.1, 500.0)
        for e in np.arange(s + 1500.0, 5000.1, 500.0)
    ]


def label(start: float, end: float) -> str:
    return f"{start / 1000:g}-{end / 1000:g} ns"


def normalize_row(raw: dict) -> dict:
    out = dict(raw)
    for key in [
        "start_ps", "end_ps", "r2", "mean_local_alpha", "window_loglog_alpha",
        "slope_nm2_per_ps", "D_PBC_1e-9_m2_s",
    ]:
        out[key] = float(out[key])
    out["origins_min"] = int(float(out["origins_min"]))
    out["eligible"] = str(out.get("eligible", "")).lower() == "true"
    out["selected"] = str(out.get("selected", "")).lower() == "true"
    return out


def eligibility(row: dict) -> tuple[dict[str, bool], list[str]]:
    flags = {
        "R2_pass": row["r2"] >= 0.995,
        "mean_alpha_pass": 0.90 <= row["mean_local_alpha"] <= 1.10,
        "loglog_alpha_pass": 0.90 <= row["window_loglog_alpha"] <= 1.10,
        "origin_pass": row["origins_min"] >= 500,
    }
    reasons: list[str] = []
    if not flags["R2_pass"]:
        reasons.append("FAIL_R2")
    if row["mean_local_alpha"] < 0.90:
        reasons.append("FAIL_MEAN_ALPHA_LOW")
    elif row["mean_local_alpha"] > 1.10:
        reasons.append("FAIL_MEAN_ALPHA_HIGH")
    if row["window_loglog_alpha"] < 0.90:
        reasons.append("FAIL_LOGLOG_ALPHA_LOW")
    elif row["window_loglog_alpha"] > 1.10:
        reasons.append("FAIL_LOGLOG_ALPHA_HIGH")
    if not flags["origin_pass"]:
        reasons.append("FAIL_ORIGIN_COUNT")
    return flags, reasons


def violation_score(row: dict) -> float:
    """Euclidean normalized threshold violation; intentionally excludes D."""
    r2 = max(0.0, (0.995 - row["r2"]) / 0.005)
    ma = max(0.0, (0.90 - row["mean_local_alpha"]) / 0.10,
             (row["mean_local_alpha"] - 1.10) / 0.10)
    la = max(0.0, (0.90 - row["window_loglog_alpha"]) / 0.10,
             (row["window_loglog_alpha"] - 1.10) / 0.10)
    oc = max(0.0, (500.0 - row["origins_min"]) / 500.0)
    return math.sqrt(r2 * r2 + ma * ma + la * la + oc * oc)


def evaluate_positions(mod, xyz: np.ndarray, restart: float) -> list[dict]:
    lag, msd, origins = mod.independent_msd(xyz, 0.5, restart)
    alpha = mod.local_log_slopes(lag, msd)
    rows: list[dict] = []
    for start, end in candidate_grid():
        row = mod.ols_window(label(start, end), start, end, lag, msd, origins, alpha)
        flags, reasons = eligibility(row)
        row.update(flags)
        row["eligible"] = not reasons
        row["failure_reasons"] = reasons
        rows.append(row)
    return rows


def fixed_window(mod, xyz: np.ndarray, restart: float, start: float, end: float) -> dict:
    lag, msd, origins = mod.independent_msd(xyz, 0.5, restart)
    alpha = mod.local_log_slopes(lag, msd)
    row = mod.ols_window(label(start, end), start, end, lag, msd, origins, alpha)
    flags, reasons = eligibility(row)
    row.update(flags)
    row["eligible"] = not reasons
    row["failure_reasons"] = reasons
    return row


def origin_sensitivity(mod, xyz: np.ndarray, baseline_rows: list[dict], rep: str) -> tuple[str, list[dict]]:
    base_bits = {r["label"]: bool(r["eligible"]) for r in baseline_rows}
    base_any = any(base_bits.values())
    detail: list[dict] = []
    outcome_changes = 0
    disagreements: list[float] = []
    for tr in TRESTARTS:
        if tr == 10.0:
            rows = baseline_rows
        elif rep == "rep01":
            # Rep01 authorization permits only the already-selected 0.5-2 ns window.
            rows = [fixed_window(mod, xyz, tr, 500.0, 2000.0)]
        else:
            rows = evaluate_positions(mod, xyz, tr)
        bits = {r["label"]: bool(r["eligible"]) for r in rows}
        common = sorted(set(base_bits) & set(bits))
        disagreement = sum(base_bits[k] != bits[k] for k in common) / len(common)
        any_eligible = any(bits.values())
        if tr != 10.0:
            outcome_changes += int(any_eligible != base_any)
            disagreements.append(disagreement)
        detail.append({
            "replicate": rep,
            "trestart_ps": tr,
            "candidate_windows_evaluated": len(rows),
            "eligible_window_count": sum(bits.values()),
            "any_eligible": any_eligible,
            "eligibility_disagreement_fraction_vs_10ps": disagreement,
            "rep01_scope_note": "fixed 0.5-2 ns only" if rep == "rep01" else "full frozen candidate grid",
        })
    max_disagreement = max(disagreements or [0.0])
    if outcome_changes == 0 and max_disagreement <= 0.10:
        category = "LOW"
    elif outcome_changes <= 1 and max_disagreement <= 0.30:
        category = "MODERATE"
    else:
        category = "HIGH"
    return category, detail


def bool_text(x: bool) -> str:
    return "TRUE" if x else "FALSE"


def fmt(x: float, n: int = 9) -> str:
    return f"{x:.{n}g}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    base = args.base.resolve()
    ens = base / "ensemble_PFOS"
    out = args.out.resolve()
    if out.exists():
        raise SystemExit(f"refusing to overwrite existing output: {out}")
    out.mkdir(parents=True)
    (out / "figures").mkdir()
    (out / "supporting").mkdir()

    analyzer_path = ens / "scripts" / "analyze_frozen_diffusion.py"
    spec = importlib.util.spec_from_file_location("frozen_analyzer", analyzer_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen analyzer")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    final_json_path = ens / "final_report" / "ENSEMBLE_RESULTS.json"
    final = json.loads(final_json_path.read_text(encoding="utf-8"))
    assert final["ENSEMBLE_STATUS"] == "COMPLETE"
    assert final["scientific_endpoint_status"] == "INCOMPLETE_N20"
    assert final["technical_completion"] == {"terminal": 20, "failed": 0, "accepted": 7, "inconclusive": 13}

    status_from_final = {r["replicate"]: r["selection_status"] for r in final["diffusion_rows"]}
    if {k for k, v in status_from_final.items() if v == "ACCEPTED"} != set(ACCEPTED):
        raise RuntimeError("accepted set does not match frozen final result")

    rows10: dict[str, list[dict]] = {}
    selected_or_closest: dict[str, dict] = {}
    com_paths: dict[str, Path] = {}

    # Rep01: reconstruct only the missing diagnostic for its already-selected window.
    rep01_dir = base / "work" / "analysis_diffusion_rep1"
    rep01_com = rep01_dir / "pfos_com_nojump_audited.csv"
    com_paths["rep01"] = rep01_com
    xyz01 = read_com_csv(rep01_com)
    rep01_row = fixed_window(mod, xyz01, 10.0, 500.0, 2000.0)
    historical = json.loads((rep01_dir / "diffusion_diagnostics.json").read_text(encoding="utf-8"))
    hp = historical["primary_fit"]
    checks = {
        "R2_matches_historical": math.isclose(rep01_row["r2"], float(hp["r2"]), rel_tol=0, abs_tol=1e-12),
        "mean_alpha_matches_historical": math.isclose(rep01_row["mean_local_alpha"], float(hp["mean_local_alpha"]), rel_tol=0, abs_tol=1e-12),
        "D_matches_historical": math.isclose(rep01_row["D_PBC_1e-9_m2_s"], float(hp["D_PBC_1e-9_m2_s"]), rel_tol=0, abs_tol=1e-12),
        "window_is_historical_selection": historical["primary_selected"] == "0.5-2 ns",
        "frozen_rule_pass": bool(rep01_row["eligible"]),
    }
    if not all(checks.values()):
        raise RuntimeError(f"rep01 fixed-window reconstruction failed audit: {checks}")
    rep01_row["selected"] = True
    rows10["rep01"] = [rep01_row]
    selected_or_closest["rep01"] = rep01_row

    all_candidates: list[dict] = []
    # Rep02-rep20: read the frozen 10-ps candidate tables; do not replace them.
    for i in range(2, 21):
        rep = f"rep{i:02d}"
        diff = ens / rep / "diffusion"
        com_paths[rep] = diff / "pfos_com_nojump_audited.csv"
        table = [normalize_row(r) for r in read_csv_dicts(diff / "adaptive_window_rule_evaluation.csv")]
        if len(table) != 28:
            raise RuntimeError(f"{rep}: expected 28 frozen candidates, got {len(table)}")
        observed_grid = [(r["start_ps"], r["end_ps"]) for r in table]
        if observed_grid != candidate_grid():
            raise RuntimeError(f"{rep}: frozen candidate grid differs")
        for r in table:
            flags, reasons = eligibility(r)
            r.update(flags)
            r["failure_reasons"] = reasons
            if r["eligible"] != (not reasons):
                raise RuntimeError(f"{rep} eligibility mismatch for {r['label']}")
            rr = {
                "replicate": rep,
                "window": r["label"],
                "start_ps": r["start_ps"],
                "end_ps": r["end_ps"],
                "width_ps": r["end_ps"] - r["start_ps"],
                "R2": r["r2"],
                "mean_local_alpha": r["mean_local_alpha"],
                "window_loglog_alpha": r["window_loglog_alpha"],
                "minimum_origins": r["origins_min"],
                "eligible": bool_text(r["eligible"]),
                "failure_reasons": ";".join(reasons) if reasons else "PASS",
                "normalized_violation_score": violation_score(r),
                "D_excluded_from_closest_rule": "TRUE",
            }
            all_candidates.append(rr)
        rows10[rep] = table
        if rep in ACCEPTED:
            selected = [r for r in table if r["selected"]]
            if len(selected) != 1 or not selected[0]["eligible"]:
                raise RuntimeError(f"{rep}: selected frozen row invalid")
            selected_or_closest[rep] = selected[0]
        else:
            if any(r["eligible"] for r in table):
                raise RuntimeError(f"{rep}: frozen INCONCLUSIVE table contains eligible candidate")
            selected_or_closest[rep] = min(
                table,
                key=lambda r: (violation_score(r), r["end_ps"], r["start_ps"]),
            )

    # Post-hoc origin spacing and component diagnostics.
    origin_detail: list[dict] = []
    origin_class: dict[str, str] = {}
    late_rows: list[dict] = []
    late_class: dict[str, str] = {}
    anisotropy: dict[str, bool] = {}
    for rep in [f"rep{i:02d}" for i in range(1, 21)]:
        xyz = read_com_csv(com_paths[rep])
        category, detail = origin_sensitivity(mod, xyz, rows10[rep], rep)
        origin_class[rep] = category
        origin_detail.extend(detail)
        if rep == "rep01":
            continue
        total_by_window = {(r["start_ps"], r["end_ps"]): r for r in rows10[rep]}
        component_fit: dict[tuple[float, float], list[dict]] = {w: [] for w in STANDARD_WINDOWS}
        for axis in range(3):
            lag, msd, origins = mod.independent_msd(xyz[:, axis:axis + 1], 0.5, 10.0)
            alpha = mod.local_log_slopes(lag, msd)
            for s, e in STANDARD_WINDOWS:
                component_fit[(s, e)].append(mod.ols_window(label(s, e), s, e, lag, msd, origins, alpha))
        early = total_by_window[(500.0, 2000.0)]
        late = total_by_window[(3000.0, 5000.0)]
        ratio = late["slope_nm2_per_ps"] / early["slope_nm2_per_ps"] if early["slope_nm2_per_ps"] > 0 else float("nan")
        if np.isfinite(ratio) and ratio >= 1.25:
            trend = "LATE_UPWARD_BEND"
        elif np.isfinite(ratio) and ratio <= 0.75:
            trend = "LATE_PLATEAU"
        else:
            trend = "STABLE_OR_NONMONOTONIC"
        max_share = 0.0
        axis_names = ["x", "y", "z"]
        dominant_axis = ""
        for s, e in STANDARD_WINDOWS:
            comps = component_fit[(s, e)]
            slopes = np.asarray([c["slope_nm2_per_ps"] for c in comps])
            denom = float(np.abs(slopes).sum())
            share = float(np.max(np.abs(slopes)) / denom) if denom else 0.0
            if share > max_share:
                max_share = share
                dominant_axis = axis_names[int(np.argmax(np.abs(slopes)))]
            total = total_by_window[(s, e)]
            late_rows.append({
                "replicate": rep,
                "window": label(s, e),
                "total_slope_nm2_per_ps": total["slope_nm2_per_ps"],
                "total_mean_local_alpha": total["mean_local_alpha"],
                "total_window_loglog_alpha": total["window_loglog_alpha"],
                "x_slope_nm2_per_ps": comps[0]["slope_nm2_per_ps"],
                "y_slope_nm2_per_ps": comps[1]["slope_nm2_per_ps"],
                "z_slope_nm2_per_ps": comps[2]["slope_nm2_per_ps"],
                "max_abs_axis_slope_share": share,
                "late_to_early_slope_ratio": ratio,
                "late_trend_class": trend,
            })
        anisotropy[rep] = max_share >= 0.60
        late_outside = not (0.90 <= late["mean_local_alpha"] <= 1.10 and 0.90 <= late["window_loglog_alpha"] <= 1.10)
        late_class[rep] = bool_text(trend != "STABLE_OR_NONMONOTONIC" or late_outside)
        for row in late_rows:
            if row["replicate"] == rep:
                row["maximum_abs_axis_slope_share_over_standard_windows"] = max_share
                row["dominant_axis_at_maximum_share"] = dominant_axis
                row["axis_anisotropy_flag"] = bool_text(anisotropy[rep])

    diag_rows: list[dict] = []
    for rep in INCONCLUSIVE:
        row = selected_or_closest[rep]
        flags, reasons = eligibility(row)
        primary = reasons[0] if len(reasons) == 1 else "MULTIPLE_FAILURES"
        diag_rows.append({
            "replicate": rep,
            "closest_window": row["label"],
            "R2": row["r2"],
            "R2_pass": bool_text(flags["R2_pass"]),
            "mean_local_alpha": row["mean_local_alpha"],
            "mean_alpha_pass": bool_text(flags["mean_alpha_pass"]),
            "window_loglog_alpha": row["window_loglog_alpha"],
            "loglog_alpha_pass": bool_text(flags["loglog_alpha_pass"]),
            "minimum_origins": row["origins_min"],
            "origin_pass": bool_text(flags["origin_pass"]),
            "primary_failure": primary,
            "all_failure_reasons": ";".join(reasons),
            "normalized_violation_score": violation_score(row),
            "late_lag_instability": late_class[rep],
            "axis_anisotropy_flag": bool_text(anisotropy[rep]),
            "origin_sensitivity_flag": origin_class[rep],
        })

    write_tsv(out / "POSTHOC_INCONCLUSIVE_DIAGNOSTIC.tsv", diag_rows)
    write_tsv(out / "supporting" / "ALL_CANDIDATE_WINDOWS.tsv", all_candidates)
    write_tsv(out / "supporting" / "ORIGIN_SENSITIVITY.tsv", origin_detail)
    write_tsv(out / "supporting" / "LATE_LAG_AND_AXIS_DIAGNOSTIC.tsv", late_rows)

    # Failure counts refer to the objectively closest candidate for each trajectory.
    all_reason_lists = [r["all_failure_reasons"].split(";") for r in diag_rows]
    n_fail_r2 = sum("FAIL_R2" in x for x in all_reason_lists)
    n_fail_mean = sum(any(y.startswith("FAIL_MEAN_ALPHA") for y in x) for x in all_reason_lists)
    n_fail_log = sum(any(y.startswith("FAIL_LOGLOG_ALPHA") for y in x) for x in all_reason_lists)
    n_fail_origin = sum("FAIL_ORIGIN_COUNT" in x for x in all_reason_lists)
    n_multiple = sum(len(x) > 1 for x in all_reason_lists)
    alpha_low = sum(any(y.endswith("ALPHA_LOW") for y in x) for x in all_reason_lists)
    alpha_high = sum(any(y.endswith("ALPHA_HIGH") for y in x) for x in all_reason_lists)
    late_n = sum(r["late_lag_instability"] == "TRUE" for r in diag_rows)
    anis_n = sum(r["axis_anisotropy_flag"] == "TRUE" for r in diag_rows)
    sens_counts = Counter(r["origin_sensitivity_flag"] for r in diag_rows)
    inconclusive_trends = Counter()
    for rep in INCONCLUSIVE:
        row = next(r for r in late_rows if r["replicate"] == rep)
        inconclusive_trends[row["late_trend_class"]] += 1
    accepted_late_evaluable = [r for r in ACCEPTED if r != "rep01"]
    accepted_late_n = sum(late_class[r] == "TRUE" for r in accepted_late_evaluable)
    accepted_axis_n = sum(anisotropy[r] for r in accepted_late_evaluable)

    # Accepted-seven descriptive statistics.
    values = [ACCEPTED_D[r] for r in ACCEPTED]
    mean = statistics.mean(values)
    sd = statistics.stdev(values)
    sem = sd / math.sqrt(len(values))
    tcrit_df6 = 2.4469118511449692
    lo, hi = mean - tcrit_df6 * sem, mean + tcrit_df6 * sem
    median = statistics.median(values)
    vmin, vmax = min(values), max(values)
    absolute_difference = mean - 0.62
    relative_difference = absolute_difference / 0.62 * 100.0

    # Plot data and comparisons.
    plot_rows: list[dict] = []
    for rep in [f"rep{i:02d}" for i in range(1, 21)]:
        row = selected_or_closest[rep]
        status = status_from_final[rep]
        plot_rows.append({
            "replicate": rep,
            "formal_status": status,
            "metric_window": row["label"],
            "window_role": "frozen selected" if status == "ACCEPTED" else "post-hoc closest by gate violation",
            "R2": row["r2"],
            "mean_local_alpha": row["mean_local_alpha"],
            "window_loglog_alpha": row["window_loglog_alpha"],
            "minimum_origins": row["origins_min"],
            "origin_sensitivity": origin_class[rep],
        })
    write_tsv(out / "PLOT_DATA.tsv", plot_rows)
    accepted_plot = [r for r in plot_rows if r["formal_status"] == "ACCEPTED"]
    inconclusive_plot = [r for r in plot_rows if r["formal_status"] == "INCONCLUSIVE"]
    group_metric_means = {
        "accepted": {
            k: statistics.mean(float(r[k]) for r in accepted_plot)
            for k in ["R2", "mean_local_alpha", "window_loglog_alpha"]
        },
        "inconclusive_closest": {
            k: statistics.mean(float(r[k]) for r in inconclusive_plot)
            for k in ["R2", "mean_local_alpha", "window_loglog_alpha"]
        },
    }
    accepted_origin_counts = Counter(origin_class[r] for r in ACCEPTED)

    colors = ["#2878B5" if r["formal_status"] == "ACCEPTED" else "#D95F02" for r in plot_rows]
    x = np.arange(1, 21)
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    ax.bar([0, 1], [7, 13], color=["#2878B5", "#D95F02"], width=0.65)
    ax.set_xticks([0, 1], ["ACCEPTED", "INCONCLUSIVE"])
    ax.set_ylabel("Replicate count")
    ax.set_title("Frozen PFOS diffusion-window outcomes (n=20)")
    for i, n in enumerate([7, 13]):
        ax.text(i, n + 0.3, str(n), ha="center")
    ax.set_ylim(0, 15)
    fig.tight_layout()
    fig.savefig(out / "figures" / "Figure_A_outcome_counts.png", dpi=220)
    plt.close(fig)

    fig, axes = plt.subplots(3, 1, figsize=(11, 8.5), sharex=True)
    metrics = ["R2", "mean_local_alpha", "window_loglog_alpha"]
    titles = ["R²", "Mean local α", "Window log–log α"]
    for ax, metric, title in zip(axes, metrics, titles):
        y = [float(r[metric]) for r in plot_rows]
        ax.scatter(x, y, c=colors, s=42, edgecolor="black", linewidth=0.35)
        if metric == "R2":
            ax.axhline(0.995, color="black", ls="--", lw=1, label="Frozen threshold")
        else:
            ax.axhline(0.90, color="black", ls="--", lw=1)
            ax.axhline(1.10, color="black", ls="--", lw=1)
            ax.axhspan(0.90, 1.10, color="#66BD63", alpha=0.09)
        ax.set_ylabel(title)
        ax.grid(alpha=0.2)
    axes[-1].set_xticks(x, [f"{i:02d}" for i in x])
    axes[-1].set_xlabel("Replicate")
    fig.suptitle("Frozen selected windows and post-hoc closest candidates\n(no diffusion-value criterion used)")
    fig.tight_layout()
    fig.savefig(out / "figures" / "Figure_B_gate_metrics.png", dpi=220)
    plt.close(fig)

    accepted_rows = accepted_plot
    inconclusive_rows = inconclusive_plot
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.8), sharey=True)
    for ax, metric, title in zip(axes, ["mean_local_alpha", "window_loglog_alpha"], ["Mean local α", "Window log–log α"]):
        data = [
            [float(r[metric]) for r in accepted_rows],
            [float(r[metric]) for r in inconclusive_rows],
        ]
        ax.boxplot(data, tick_labels=["Accepted\nselected", "Inconclusive\nclosest"], showfliers=False)
        for j, vals in enumerate(data, start=1):
            offsets = np.linspace(-0.08, 0.08, len(vals))
            ax.scatter(j + offsets, vals, s=26, alpha=0.85, color=["#2878B5", "#D95F02"][j - 1])
        ax.axhline(0.90, color="black", ls="--", lw=1)
        ax.axhline(1.10, color="black", ls="--", lw=1)
        ax.axhspan(0.90, 1.10, color="#66BD63", alpha=0.09)
        ax.set_title(title)
        ax.grid(axis="y", alpha=0.2)
    axes[0].set_ylabel("α")
    fig.suptitle("Alpha distributions under the frozen eligibility limits")
    fig.tight_layout()
    fig.savefig(out / "figures" / "Figure_C_alpha_distributions.png", dpi=220)
    plt.close(fig)

    # Independent audit/provenance records.
    source_rows = []
    for p in [
        analyzer_path,
        base / "logs" / "FROZEN_DIFFUSION_ANALYSIS_PROTOCOL.md",
        final_json_path,
        ens / "final_report" / "DIFFUSION_RESULTS.tsv",
        rep01_dir / "diffusion_diagnostics.json",
        rep01_dir / "fit_window_sensitivity.csv",
        rep01_com,
    ]:
        source_rows.append({"path": str(p), "sha256": sha256(p)})
    write_tsv(out / "supporting" / "SOURCE_ARTIFACT_SHA256.tsv", source_rows)

    rep01_audit = f"""# Rep01 frozen-rule audit

`REP01_FROZEN_RULE_AUDIT = PASS`

The historical result selected **0.5–2.0 ns** and stored R², mean local α,
minimum origins, and D, but did not serialize `window_loglog_alpha`. The missing
field was reconstructed from the existing audited PFOS COM trajectory with the
same frozen analyzer functions. No candidate-window search was performed.

`POSTHOC_RECONSTRUCTION_OF_MISSING_DIAGNOSTIC`

| Field | Value | Frozen gate |
|---|---:|---:|
| Window | 0.5–2.0 ns | already selected historically |
| R² | {rep01_row['r2']:.12f} | ≥ 0.995 |
| Mean local α | {rep01_row['mean_local_alpha']:.12f} | 0.90–1.10 |
| Window log–log α | {rep01_row['window_loglog_alpha']:.12f} | 0.90–1.10 |
| Minimum origins | {rep01_row['origins_min']} | ≥ 500 |

All reconstructed stored-field checks matched the historical values to absolute
tolerance 1e-12. Formal status, selected window, and D were not changed.
"""
    (out / "REP01_FROZEN_RULE_AUDIT.md").write_text(rep01_audit, encoding="utf-8")

    method = f"""# Post-hoc diagnostic method

## Scope and invariants

This is a read-only diagnostic of the completed, published ensemble. The formal
result remains `COMPLETE / INCOMPLETE_N20` with 7 accepted, 13 inconclusive, and
0 MD failures. Existing trajectories, seeds, TPR/topology, thresholds, statuses,
selected windows, diffusion values, and the frozen final package were not changed.

## Frozen candidate evaluation

The existing frozen 10 ps candidate tables were read for rep02–rep20. The grid
uses starts 0.5–3.5 ns in 0.5 ns increments, ends through 5.0 ns, and width ≥1.5
ns. Gates were R² ≥0.995, both alpha measures in [0.90,1.10], and minimum origins
≥500. Rep01 was restricted to reconstruction of its already-selected 0.5–2.0 ns
diagnostic with the exact frozen analyzer implementation (SHA256 recorded).

## Closest-to-eligible rule

For an inconclusive trajectory, each gate violation was normalized as:

- R²: `max(0, (0.995-R²)/0.005)`
- each alpha: distance beyond [0.90,1.10], divided by 0.10
- origins: `max(0, (500-min_origins)/500)`

The Euclidean norm of those four components defined proximity. Deterministic
ties used earliest end then earliest start. **D was excluded completely.**

## Late-lag and Cartesian diagnostics

Frozen 10 ps-origin total-MSD fits at 0.5–2, 1–3, 2–4, and 3–5 ns were compared.
A 3–5/0.5–2 slope ratio ≥1.25 was called a late upward bend and ≤0.75 a late
plateau. Cartesian component fits used the same origin construction. A diagnostic
axis flag was set when one component contributed ≥60% of the summed absolute
component slopes in any standard window. This flag does not establish physical
anisotropy; it detects direction-dominated finite-trajectory excursions.

## Origin sensitivity

Candidate eligibility was recomputed at 5, 20, and 50 ps and compared with the
formal 10 ps result for all replicates. LOW means no accepted/inconclusive outcome
change and ≤10% candidate Boolean disagreement; MODERATE allows one outcome
change and ≤30%; otherwise HIGH. Rep01 was evaluated only at its fixed historical
window, as required by the narrower reconstruction authorization.

With a 10 ns interval, 20 and 50 ps origin spacing necessarily produces fewer
than 500 origins at long candidate lags. Thus the HIGH category for accepted
replicates is mechanically driven in part by retaining the frozen ≥500-origin
gate under those diagnostic spacings; it does not indicate changed dynamics.

All diagnostics are explanatory and do not revise the prospective frozen result.
"""
    (out / "POSTHOC_DIAGNOSTIC_METHOD.md").write_text(method, encoding="utf-8")

    accepted_md = f"""# Post-hoc accepted-seven descriptive statistics

**DESCRIPTIVE ONLY — NOT THE FROZEN N=20 ENDPOINT**

This is a descriptive statistic of the seven trajectories that satisfied the
prospective eligibility filter and is not a replacement for the frozen n=20 estimator.

All values are corrected D∞ in 10⁻⁹ m² s⁻¹.

| Statistic | Value |
|---|---:|
| n | 7 |
| Mean | {mean:.9f} |
| Sample SD | {sd:.9f} |
| SEM | {sem:.9f} |
| t-based 95% CI (df=6) | [{lo:.9f}, {hi:.9f}] |
| Median | {median:.9f} |
| Min–max | {vmin:.9f}–{vmax:.9f} |
| Mean minus published central value 0.62 | {absolute_difference:+.9f} |
| Relative difference from 0.62 | {relative_difference:+.3f}% |
"""
    (out / "POSTHOC_ACCEPTED7_DESCRIPTIVE_STATISTICS.md").write_text(accepted_md, encoding="utf-8")

    reason_counter = Counter(r["primary_failure"] for r in diag_rows)
    dominant = reason_counter.most_common(1)[0]
    high_majority = alpha_high > alpha_low
    summary = f"""# Inconclusive failure summary

The frozen formal result is unchanged: `COMPLETE / INCOMPLETE_N20`, with 7
accepted, 13 inconclusive, and 0 failed MD trajectories.

## Failure matrix summary

Counts below use each trajectory's closest candidate under the threshold-only,
D-blind normalized violation rule:

| Diagnostic | Replicates |
|---|---:|
| n_fail_R2 | {n_fail_r2} |
| n_fail_mean_alpha | {n_fail_mean} |
| n_fail_loglog_alpha | {n_fail_log} |
| n_fail_origin_count | {n_fail_origin} |
| n_multiple_failure | {n_multiple} |
| alpha_too_low (either alpha gate) | {alpha_low} |
| alpha_too_high (either alpha gate) | {alpha_high} |
| late_lag_instability | {late_n} |
| axis_anisotropy_flag | {anis_n} |
| origin sensitivity LOW / MODERATE / HIGH | {sens_counts.get('LOW',0)} / {sens_counts.get('MODERATE',0)} / {sens_counts.get('HIGH',0)} |

Primary-failure labels: `{dict(reason_counter)}`. The most frequent primary label
was **{dominant[0]}** ({dominant[1]}/13).

## Accepted versus inconclusive (descriptive)

| Metric | Accepted selected windows | Inconclusive closest candidates |
|---|---:|---:|
| Mean R² | {group_metric_means['accepted']['R2']:.6f} | {group_metric_means['inconclusive_closest']['R2']:.6f} |
| Mean local α | {group_metric_means['accepted']['mean_local_alpha']:.6f} | {group_metric_means['inconclusive_closest']['mean_local_alpha']:.6f} |
| Mean window log–log α | {group_metric_means['accepted']['window_loglog_alpha']:.6f} | {group_metric_means['inconclusive_closest']['window_loglog_alpha']:.6f} |

Origin sensitivity was `{dict(accepted_origin_counts)}` among accepted replicates
(rep01 fixed-window scope) versus `{dict(sens_counts)}` among inconclusive
replicates. The alpha spread, mixed low/high failures, late-lag changes, and
direction-dominance flags are more consistent with finite-length stochastic
sampling under a strict simultaneous gate than with one uniform alternative
physical regime; this remains descriptive, not a causal proof.

Among the 13 inconclusive trajectories, late-trend classes were
`{dict(inconclusive_trends)}`. The broad late-instability flag was also present in
{accepted_late_n}/{len(accepted_late_evaluable)} accepted trajectories evaluable
from the current candidate tables, and the direction-dominance flag in
{accepted_axis_n}/{len(accepted_late_evaluable)}. These diagnostics are therefore
not specific signatures of the inconclusive subset.

## Required scientific questions

### Q1. What was the main gate among the 13 inconclusive trajectories?

The closest-candidate audit identifies alpha-related failures as the dominant
gate family; exact per-replicate combinations are in the TSV.

### Q2. Was R² or alpha the main problem?

Alpha was more frequent: R² failed in {n_fail_r2}/13 closest candidates, while
mean and/or log–log alpha failed in {sum(any('ALPHA' in q for q in x) for x in all_reason_lists)}/13.

### Q3. Did alpha failures tend low or high?

Across trajectories, either alpha gate was low in {alpha_low}/13 and high in
{alpha_high}/13. Thus the direction was **{'predominantly high (>1.10)' if high_majority else 'not predominantly high'}**.

### Q4. Did origin count limit eligibility?

No closest candidate failed the origin-count gate ({n_fail_origin}/13); it was
not the principal constraint under the frozen candidate grid.

### Q5. Was late-lag upward curvature general?

{late_n}/13 were flagged for a late-lag slope/alpha instability by the declared
diagnostic, but only {inconclusive_trends.get('LATE_UPWARD_BEND', 0)}/13 were
classified as upward bends; {inconclusive_trends.get('LATE_PLATEAU', 0)}/13 were
plateaus and {inconclusive_trends.get('STABLE_OR_NONMONOTONIC', 0)}/13 were
stable/nonmonotonic by the slope-ratio rule. Upward curvature was not universal.

### Q6. Were excursions dominated by a small number of Cartesian axes?

{anis_n}/13 crossed the direction-dominance diagnostic, versus
{accepted_axis_n}/{len(accepted_late_evaluable)} evaluable accepted trajectories.
Direction-specific excursions were common but not specific to failed eligibility,
and do not prove persistent physical anisotropy.

### Q7. Does the 10 ns analysis interval show finite-sampling limitations?

The combination of {late_n}/13 late-lag flags, {anis_n}/13 direction-dominance
flags, and origin-sensitivity categories {dict(sens_counts)} is **evidence
consistent with finite-sampling limitations** in strict per-trajectory window
eligibility. It does not prove a single physical mechanism.

The alternate-spacing result requires a design caveat: keeping the ≥500-origin
gate makes every 20/50 ps candidate fail origin count by construction at long
lags. The formal 10 ps analysis itself did not fail origin count.

### Q8. Does rep01 satisfy the current frozen rule?

Yes. `REP01_FROZEN_RULE_AUDIT = PASS`; reconstructed window log–log alpha is
{rep01_row['window_loglog_alpha']:.12f}, and minimum origins is {rep01_row['origins_min']}.

### Q9. How does the accepted-seven descriptive mean compare with 0.62?

The descriptive mean is {mean:.9f} ×10⁻⁹ m² s⁻¹, differing by
{absolute_difference:+.9f} ({relative_difference:+.3f}%) from 0.62. This is not
the frozen n=20 estimator.

### Q10. What prospective study is most reasonable next?

Pre-register a longer-trajectory study and retain the present gate unchanged,
while adding estimator robustness as a co-primary design question: fixed-lag
ensemble MSD and a likelihood/Bayesian diffusion estimator can reduce unstable
single-trajectory adaptive-window decisions. An ensemble-MSD estimator should
preserve replicate identity for uncertainty; VACF/Green–Kubo is a useful
cross-check but can itself be noisy at long times. More replicates alone are less
direct than more independent trajectory length when late-lag/origin sensitivity
is the observed limitation. All choices must be frozen prospectively before new MD.
"""
    (out / "INCONCLUSIVE_FAILURE_SUMMARY.md").write_text(summary, encoding="utf-8")

    readme = """# PFOS Damião 20-replicate post-hoc diagnostic

This independent package explains diffusion-window eligibility outcomes without
changing the published frozen result. It contains no MD binary trajectories and
does not replace `PFOS_Damiao_20rep_final_20260923`.

Formal result preserved: `COMPLETE / INCOMPLETE_N20` (7 accepted, 13
inconclusive, 0 MD failures).

## Main files

- `REP01_FROZEN_RULE_AUDIT.md`: fixed-window missing-field audit.
- `POSTHOC_INCONCLUSIVE_DIAGNOSTIC.tsv`: one row per inconclusive replicate.
- `INCONCLUSIVE_FAILURE_SUMMARY.md`: failure counts and Q1–Q10.
- `POSTHOC_ACCEPTED7_DESCRIPTIVE_STATISTICS.md`: descriptive-only statistics.
- `POSTHOC_DIAGNOSTIC_METHOD.md`: predeclared diagnostic definitions.
- `PLOT_DATA.tsv` and `figures/`: auditable figure inputs and three figures.
- `supporting/`: candidate, origin, Cartesian, and source-hash evidence.
"""
    (out / "README.md").write_text(readme, encoding="utf-8")

    # Copy this exact script as a transparent method artifact.
    this_script = Path(__file__).resolve()
    (out / "supporting" / "analyze_pfos_posthoc.py").write_bytes(this_script.read_bytes())

    manifest_rows = []
    for p in sorted(out.rglob("*")):
        if p.is_file() and p.name != "POSTHOC_PACKAGE.sha256":
            manifest_rows.append(f"{sha256(p)}  {p.relative_to(out).as_posix()}")
    (out / "POSTHOC_PACKAGE.sha256").write_text("\n".join(manifest_rows) + "\n", encoding="utf-8")

    result = {
        "formal_result_unchanged": True,
        "REP01_FROZEN_RULE_AUDIT": "PASS",
        "rep01_window_loglog_alpha": rep01_row["window_loglog_alpha"],
        "rep01_minimum_origins": rep01_row["origins_min"],
        "failure_counts": {
            "n_fail_R2": n_fail_r2,
            "n_fail_mean_alpha": n_fail_mean,
            "n_fail_loglog_alpha": n_fail_log,
            "n_fail_origin_count": n_fail_origin,
            "n_multiple_failure": n_multiple,
            "alpha_too_low": alpha_low,
            "alpha_too_high": alpha_high,
        },
        "late_lag_instability": late_n,
        "inconclusive_late_trend_counts": dict(inconclusive_trends),
        "axis_anisotropy_flag": anis_n,
        "accepted_late_instability_evaluable": accepted_late_n,
        "accepted_axis_anisotropy_evaluable": accepted_axis_n,
        "origin_sensitivity_counts": dict(sens_counts),
        "accepted_origin_sensitivity_counts": dict(accepted_origin_counts),
        "accepted_vs_inconclusive_metric_means": group_metric_means,
        "accepted7": {
            "n": 7, "mean": mean, "sample_SD": sd, "SEM": sem,
            "CI95_t_df6": [lo, hi], "median": median, "min": vmin, "max": vmax,
            "difference_from_0.62": absolute_difference,
            "relative_difference_percent": relative_difference,
        },
    }
    (out / "supporting" / "POSTHOC_RESULT_SUMMARY.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    # Refresh package manifest after adding the machine-readable summary.
    manifest_rows = []
    for p in sorted(out.rglob("*")):
        if p.is_file() and p.name != "POSTHOC_PACKAGE.sha256":
            manifest_rows.append(f"{sha256(p)}  {p.relative_to(out).as_posix()}")
    (out / "POSTHOC_PACKAGE.sha256").write_text("\n".join(manifest_rows) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
