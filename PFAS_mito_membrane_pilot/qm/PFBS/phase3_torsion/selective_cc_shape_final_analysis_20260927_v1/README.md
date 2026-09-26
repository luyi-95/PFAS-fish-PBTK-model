# PFBS selective-CC shape final analysis (analysis only)

This package records a source-bounded, report-only analysis of the recovered 728/728 selective-CC MM matrix and the already frozen v2/selective-CC preregistration. No fit, candidate amplitudes, new MM calculation, QM/Gaussian calculation, parameter edit, water/membrane pilot, or MD was performed.

## Final determination

`SELECTIVE_CC_SHAPE_STATUS = C. IDENTIFIABLE_BUT_INSUFFICIENT_LEVERAGE`

One supported, step-stable rank-1 CC direction exists in the 118-row primary matrix. Within the preregistered source-centered coefficient bounds and the prospective geometry/branch/CS screens, the correcting sign changes the sampled `T_CC_180 - T_CC_300` gap by about +3.1178 kcal/mol, against a +3.6431 kcal/mol defect. The remaining first-order gap is about +0.5253 kcal/mol; this is insufficient under the frozen leverage rule. This is not a fitted result or a parameter recommendation.

The combined geometry+CC matrix has supported rank 5/8, while the CC direction has high geometry overlap (maximum principal-angle cosine about 0.719; report-only category HIGH). The supported direction passes the prospective local geometry, shared-chain, T_CS and CC240 branch screens, but that does not remove the high geometry confounding or solve the leverage shortfall.

`MVP_CONSTRAINED_FIT_DESIGN_READY = NO`

`MVP_ROUTE_REASSESSMENT = GEOMETRY_PLUS_CC_REDESIGN`

`NEW_QM_REQUIRED = NO` for this source-bounded adjudication. This does not authorize a redesign, fit, new calculation, or production parameter change.

## Provenance and reproducibility

The recovered export contains 728 rows. The deterministic metadata-repair receipt records `rerun=false` and `numerical_calculations_changed=false`; `primary__BASE` is bound to `immutable_sources/pfbs_ani.prm` (SHA256 `24baf41553845380e9905f7419ca85cb0528dcd7652d596ca6ba83e003d05a56`). The original exporter source is preserved under `provenance/ORIGINAL_FROZEN_EXPORTER.py`; the separate V3 recovery exporter and receipt are preserved alongside it. Full source hashes are in the provenance review and manifests.

The package omits large runtime outputs, checkpoints, scratch, raw logs, and the original parameter file. The matrix identity, inventory, per-output hashes, run receipt, exporter lineage, and frozen analysis inputs are hash-bound by the accompanying receipts. `SHA256SUMS` covers every other package file. `PACKAGE_SHA256` is defined as SHA256 of the exact `SHA256SUMS` file bytes; it is reported with the Git commit in the release identity outside this package directory.

## State

- `PROVENANCE_FINAL_STATUS = PASS_DETERMINISTIC_METADATA_REPAIR`
- `DERIVATIVE_QC_STATUS = PASS_FOR_SUPPORTED_RANK1_DIRECTION; INDIVIDUAL_COMPONENTS_REVIEWED`
- `PARAMETER_FITTING_STARTED = NO`
- `PARAMETER_EDITED = NO`
- `SCIENTIFIC_VALIDATION_COMPLETE = YES_FOR_SELECTIVE_CC_ANALYSIS_ONLY`
- `NEW_QM_LAUNCHED = NO`
- `MM_NEW_CALCULATIONS = NO`
- `PRODUCTION_PARAMETER_REPLACEMENT = NOT_AUTHORIZED`
- `WATER_PILOT = NOT_AUTHORIZED`
- `MEMBRANE_PILOT = NOT_AUTHORIZED`
- `MD_RUN_AUTHORIZATION = NOT_GRANTED`

The detailed decision and limits are in `SOL_HIGH_FINAL_SELECTIVE_CC_SHAPE_REVIEW.md`; exact source binding is in `PROVENANCE_FINAL_REVIEW.md`.

The preserved `provenance/POSTRUN_RECOVERY_CONTEXT.md` records the earlier exporter-schema recovery context. It is retained verbatim. The later source adjudication and V3 receipt bind `primary__BASE` to the exact frozen parameter file; this package preserves both records and does not rewrite the earlier note.
