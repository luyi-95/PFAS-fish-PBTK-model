# Sol High final selective-CC shape adjudication

## Verdict

`SELECTIVE_CC_SHAPE_STATUS = C. IDENTIFIABLE_BUT_INSUFFICIENT_LEVERAGE`

### Required fields

- `PROVENANCE_FINAL_STATUS = PASS_DETERMINISTIC_METADATA_REPAIR`
- `DERIVATIVE_QC_STATUS = PASS_FOR_SUPPORTED_RANK1_DIRECTION; REVIEW_FOR_INDIVIDUAL_COMPONENTS`
- `SELECTIVE_CC_RANK_FULL = 1` (primary 118×4; threshold 0.1712695334)
- `SELECTIVE_CC_RANK_LOW_ENERGY = 1` (frozen low-tier 99×4)
- `COMBINED_RANK = 5` (118×8)
- `DIRECTION_ROBUSTNESS = MODERATELY_SOURCE_DEPENDENT`
- `MINIMAL_CC_SHAPE_DIMENSION = 1` (diagnostic supported dimension only)
- `SELECTED_CC_SHAPE_DIRECTION = supported rank-1 grouped direction: CC_FOURIER_1=0.794968842142, CC_FOURIER_2=−0.567158662075, CC_FOURIER_3=−0.214917656479, CC_FOURIER_4=−0.012883826682; use the opposite sign for the local CC180-vs-CC300 correction screen`
- `LOW_ENERGY_CC_LEVERAGE = INSUFFICIENT`
- `CC_PROFILE_SHAPE_STATUS = REVIEW`
- `GEOMETRY_CONFOUNDING = HIGH`
- `GEOMETRY_GUARD_STATUS = PASS` (only the prospective local response screen)
- `SHARED_CHAIN_GUARD_STATUS = PASS`
- `CS_GUARD_STATUS = PASS`
- `CC240_BRANCH_GUARD_STATUS = PASS`

## Basis

The primary CC-only matrix has exactly one supported singular direction; the second singular value (0.13915) is below the frozen 5δ threshold (0.17127), and the remaining two are much smaller. The low-energy subset remains rank 1. The geometry-only matrix has rank 0. In contrast, PES-only rank 4 is diagnostic and is not admissible as a replacement for the full primary design.

The correction-oriented supported ray is numerically stable under the frozen step and convergence tests. Its bounded first-order movement can improve the basin ordering, but the maximum preregistered, guard-feasible movement is +3.1178 kcal/mol versus the +3.6431 kcal/mol defect. The required movement is not reached inside the allowed local bounds, so leverage is insufficient. Neighboring energy responses are mixed; current grid minima at CC060, CC180 and CC270 remain as sampled local minima at the linear endpoint while CC300 becomes the grid global minimum. This does not validate the full PES or its barriers.

The source-block LOO audit finds CC-only supported rank 1 for each requested omission/reanchor; the CC-only leading direction remains nearly collinear with the full direction (absolute cosine ≥0.99957 where defined). However, the CC component of the combined geometry+CC leading direction varies more (≈0.707–0.850), and the max supported geometry overlap cosine is ≈0.719. The direction is therefore moderately source-dependent in the combined context, not a robust isolated torsion coordinate.

The correction ray passes all 92 prospective geometry endpoint budgets in both signs and creates no new major flags; a few preexisting major geometry errors increase slightly but remain within the preregistered local screen. The 112 shared-chain checks are `PASS_LOCAL_SMOOTH_DOMAIN` (maximum minimax wrapped change ≈0.2891° against the 30° domain gate). All 130 T_CS ray-point checks show no unsupported new well. All 24 CC240 branch checks pass; branches remain separate and unaveraged, with maximum change in residual about 1.71×10⁻⁵ kcal/mol, below the frozen 0.1 kcal/mol review trigger.

The scalar per-observable × parameter audit contains 472 cells: F1 26 PASS / 26 REVIEW / 66 UNIDENTIFIABLE; F2 24 / 20 / 74; F3 22 / 16 / 80; F4 22 / 6 / 90. These are cellwise finite-difference diagnostics, not 472 independent observations. The aggregate supported rank-1 direction passes the frozen full-vector step/convergence support test; F4 is individually unresolved and the other coefficients are not separately identified by the four-column primary model.

## Direction robustness and interpretation

The requested LOO blocks were CC180, CC300 with the preregistered CC180 reanchor, GEO_A, GEO_B, CC240 forward, CC240 reverse branch-only, and the frozen T_CS low-energy block (`T_CS_050/060/070/080`). CC-only rank stayed at 1 and its leading direction remained close to baseline. The combined-matrix CC projection shifted, and the high geometry overlap remains; classification is `MODERATELY_SOURCE_DEPENDENT`.

Term-level disposition: all four terms belong only to the same rank-1 grouped diagnostic direction; none is independently eligible for a fit. The CC_FOURIER_3-dominated second direction and CC_FOURIER_4-dominated third direction are unsupported. No fitted amplitudes are calculated or supplied. `NONSELECTED_TERMS = FREEZE`; all terms remain frozen for any later work unless separately authorized.

## Readiness and route reassessment

- `MVP_CONSTRAINED_FIT_DESIGN_READY = NO`
- `MVP_ROUTE_REASSESSMENT = GEOMETRY_PLUS_CC_REDESIGN`
- `NEW_QM_REQUIRED = NO` for this analysis-only conclusion.

The directional screen shows insufficient torsion-only leverage and high geometry overlap. Any later redesign would have to preserve both geometry and T_CC/T_CS PES jointly and must avoid compensating errors. This review does not execute or authorize that redesign.

## Final state

`SCIENTIFIC_VALIDATION_COMPLETE = YES_FOR_SELECTIVE_CC_ANALYSIS_ONLY`

`CURRENT_PARAMETER_STATUS = REJECTED`; `PARAMETER_FITTING_STARTED = NO`; `PARAMETER_EDITED = NO`; `NEW_QM_LAUNCHED = NO`; `MM_NEW_CALCULATIONS = NO`; `PRODUCTION_PARAMETER_REPLACEMENT = NOT_AUTHORIZED`; `WATER_PILOT = NOT_AUTHORIZED`; `MEMBRANE_PILOT = NOT_AUTHORIZED`; `MD_RUN_AUTHORIZATION = NOT_GRANTED`.

No parameter candidate was created. Stop after this adjudication and Git/hash freeze.
