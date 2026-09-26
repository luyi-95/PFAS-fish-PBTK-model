# PFBS pre-QM V2 evidence package

This package records the completed, source-bound MM identifiability analysis and Sol High's V9 MVP-route adjudication. It is an evidence and review package; it contains no approved production parameter replacement or execution authorization.

## Final statuses

- `MVP_ROUTE_STATUS`: **A — EXISTING_QM_SUFFICIENT_FOR_MINIMAL_REPAIR**.
- Numerical matrix: **PARTIAL_SUPPORT**, 9/10 supported directions on the full 118-row primary block and 8/10 on the 99-row low-tier diagnostic.
- Current PFBS parameter status: **REJECTED**. `FIT_READY=NO`; `NEW_QM_REQUIRED=NO`; `PARAMETER_EDITED=NO`; `MD_GRANTED=NO`.
- The proposed first geometry hypothesis is the four-field joint block in `REDUCED_PARAMETER_BLOCK_V1.tsv`; this is not a fitted or adopted parameter set. The grouped CC amplitude is frozen.
- The immediate next gate is a separately authorized, prospectively frozen MM-only Fourier-shape sensitivity study using existing QM targets, with joint geometry and basin guards. Review the existing GEO_A Hessian before any force-constant or UB claim.
- No new QM, fitting, candidate solve, parameter adoption, water/membrane pilot, or production MD was performed or authorized by this package.

## Numerical evidence

The terminal matrix completed 1,736/1,736 runs. The full primary weighted Jacobian has effective rank 9/10 at the frozen 5δ threshold; the unresolved right-singular direction is dominated by `LAMBDA_CC` and the `TH_CG312-CG312-SG3O1` equilibrium angle. All ten full-block finite-difference step/convergence ratios pass their frozen numerical checks. The 99-row low-tier subset has rank 8/10; its common CC300 anchor remains an exact-zero row with the frozen CC weight and no renormalization. All 280 local proper-torsion checks, 1,612 scan-angle checks, and 50,592 A/B pair-distance checks pass.

See `NULL_DIRECTION_ANALYSIS.md`, `NUMERICAL_JACOBIAN_RAW.tsv`, `NUMERICAL_JACOBIAN_NORMALIZED.tsv`, `SVD_RESULTS.tsv`, `PARAMETER_CORRELATION.tsv`, `DERIVATIVE_STEP_STABILITY.tsv`, and `numerical_evidence/` for the complete matrices, noise envelope, declared submatrices, per-run compact receipts, and hashes. `PACKAGE_MANIFEST.json` and `SHA256SUMS` bind the complete tree.

## Scope and provenance

`reference_v1/` is retained as the immutable source baseline. The V2 additions are separately staged. Full raw MM run trees and engine binaries are not included; the terminal compact export and analysis receipts preserve the per-run numerical/provenance record. Superseded offline analysis attempts and the controller log remain outside the package under `executor/analysis_archive_prepackage/`, bound by its `MOVE_INVENTORY.json`.
