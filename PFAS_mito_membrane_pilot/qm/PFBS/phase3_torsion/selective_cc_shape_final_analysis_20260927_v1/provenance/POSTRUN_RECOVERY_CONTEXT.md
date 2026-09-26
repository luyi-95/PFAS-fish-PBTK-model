# PFBS selective CC post-run export recovery v1

This recovery-only package is separate from the frozen V5 execution code and immutable execution results. It addresses a deterministic provenance-schema defect after all 728 MM minimizations completed: the frozen runner records per-file `changed_source_lines` as a mapping, while its frozen exporter incorrectly requires a list.

Sol High's read-only adjudication bound `primary__BASE` to the exact frozen source `pfbs_ani.prm`, SHA-256 `24baf41553845380e9905f7419ca85cb0528dcd7652d596ca6ba83e003d05a56`, through the source-binding record, manifest, execution freeze, preflight evidence, state receipts, TPRs, and byte-level comparison. No calculation or parameter values are recreated by this utility.

The recovery exporter preserves the original exporter SHA in the legacy frozen provenance field and records its own SHA, the deterministic metadata-repair class, and the exact source binding in separate recovery provenance. It reads the original 728 run receipts and artifacts and writes only a derivative export and recovery receipt beneath `executor_runtime/recovery_v1/`.

It does not invoke GROMACS, change any run receipt, alter scientific rules, or rerun minimizations. `ANALYSIS` is still gated on review of the derivative export and its recovery receipt.
