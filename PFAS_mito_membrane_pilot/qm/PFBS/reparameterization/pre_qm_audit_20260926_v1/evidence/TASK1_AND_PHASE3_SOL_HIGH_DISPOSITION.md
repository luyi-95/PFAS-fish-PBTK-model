# PFBS Phase 3 MM profile and Task 1 geometry disposition

Date: 2026-09-26. Independent Sol High scientific review; no parameter or source QM result edited.

## Frozen evidence

The local MM review package `MM_SOL_HIGH_REVIEW_PACKAGE_20260926_v1` has `SHA256SUMS` SHA256 `375a1f1b5d0cf9035b9c890bcd0f25d95ed946e2aba0cb7a6d8108f5eba1c5ec`; all 36 listed files were checked. The frozen CGenFF source `pfbs_ani.itp` SHA256 is `c736e8e20ee778fd64dfc2b95da13040b6a49404c78dc1cf46dd7368b016aeca`; `pfbs_ani.prm` SHA256 is `24baf41553845380e9905f7419ca85cb0528dcd7652d596ca6ba83e003d05a56`. The pre-existing `source_receipt.json` has 70/70 source-copy matches; the MM review package separately binds the PRM. Local copies of the Task 1 files match their remote source SHA256 values.

The complete accepted-QM 25-point grid produced 25 independent restrained MM minimizations, plus an independent T_CC_240 reverse-QM-seed MM branch. All 26 double-precision minimizations converged under the documented Fmax<10 kJ/mol/nm execution check; physical unrestrained energies exclude artificial torsion restraint energy. MM@QM single points are secondary diagnostics. The 10 nm/2 nm versus 12 nm/2.5 nm box/cutoff energy check showed differences below 0.0001 kJ/mol for the tested state. No MD integration was run.

## Sol High profile decision

- `PHASE3_QM_MM_PROFILE_STATUS = VALID_COMPARISON`
- `T_CC_STATUS = FAIL_FOR_INITIAL_RELEASE`: QM global sampled minimum 300 degrees, MM 180 degrees; sampled barriers 10.0196 versus 25.9564 kcal/mol; common-anchor RMSE 7.0814 kcal/mol. Low-QM-energy-region RMSE 4.6206 kcal/mol.
- `T_CS_STATUS = REVIEW`: both sampled minima 70 degrees; sampled barriers 4.5994 versus 9.1334 kcal/mol; common-anchor RMSE 5.3598 kcal/mol. The separately series-aligned RMSE is 3.0604 kcal/mol and does not replace the frozen common-anchor comparison.
- `T_CC_240_BRANCH_STATUS = QM_HYSTERESIS_REVIEW_MM_CONVERGED`: reverse QM is 0.22530 kcal/mol above forward QM; relaxed MM branches differ by -0.00130 kcal/mol and converge to essentially the same geometry. Preserve both QM branches.
- `COUPLED_TORSION_REVIEW = REQUIRED`: the unscanned junction angle shifts by up to about 13.7 degrees in T_CC and 14.7 degrees in T_CS; source point values and basin changes are in the supplemental profile metrics.
- `CURRENT_CGENFF5_PARAMETER_STATUS = REJECTED`
- `TARGETED_TORSION_REFINEMENT_REQUIRED = YES` as a scientific target, subject to the separate Task 1 prerequisite below.

## Independent Task 1 geometry check

The pre-existing unconstrained GEO_A QM/MM geometry comparison (`geometry_metrics.json`, SHA256 `dcb2e0872a5cc0fef57172e0aac1e5200cb09ade38c54c653fb8b7e5d737ae12`) shows MM minus QM: S1-C2 -0.11149 Angstrom, C1-C2 -0.05795 Angstrom, S1-O1 -0.03849 Angstrom, and C1-C2-S1 -6.27547 degrees. The independent revised GEO_B source (QM checkpoint SHA256 `158ee77849735418e158a30f087bf5ed61785fc1d7a66d6e5022212d4222a1c9`) after its existing CG MM continuation (Fmax 4.9165 kJ/mol/nm; GRO coordinate precision 0.01 Angstrom) repeats S1-C2 -0.10488 Angstrom, C1-C2 -0.05184 Angstrom, and C1-C2-S1 -4.84204 degrees. Exact values and provenance are in `GEO_B_GEOMETRY_CROSSCHECK.json` and the copied raw files.

The frozen 0.03 Angstrom/3-degree guidance in `29_PFBS_QM_ACCEPTANCE_RULES.md` triggers review rather than an automatic numerical failure. Sol High judged the coherent GEO_A/GEO_B mismatch reproducible and consequential. Original equilibrium bond lengths strongly implicate local bonded geometry: CG312-SG3O1 r0=1.807 Angstrom versus QM 1.874–1.878, generic CG312-CG312 r0=1.4563 versus QM 1.541–1.546, and SG3O1-OG2P1 r0=1.448 versus QM about 1.480–1.482. Attribution to bond equilibrium targets is high confidence; angle/UB/torsion/intramolecular nonbonded coupling remains unresolved. No force constant, charge or LJ defect is inferred from this comparison alone. The GEO_A frequency result supports a true QM minimum but available records do not contain a matched QM/MM normal-mode-character comparison.

- `TASK1_GEOMETRY_STATUS = FAIL_FOR_INITIAL_CGENFF5_PARAMETER_RELEASE`
- `TORSION_ONLY_FIT_CAN_PROCEED = NO`
- `PROCEED_TO_CANDIDATE_FIT = NO`
- `SINGLE_BOUNDED_TORSION_REFINEMENT_AUTHORIZATION_CONSUMED = NO`

A torsion-only fit on the current distorted MM geometry could absorb a bonded error into Fourier terms. The authorized torsion-only cycle is therefore held. The next scientific work is a separately bounded PFBS-specific bond/angle proposal and review, with original source files preserved. Any future candidate would require GEO_A/GEO_B geometry and mode review, both coupled relaxed torsion profiles, and Phase 2 water/ESP checks. Numeric bond/angle changes are outside the existing torsion-only authorization.

## Terminal state

`PFBS_PARAMETER_STATE = REJECTED` for the present CGenFF5 parameter set. QM and MM calculation evidence remains valid and preserved; this is a parameter-model decision, not a Gaussian execution failure. No additional QM, reverse point, membrane MD or PMF was launched during this disposition.

`PARAMETER_EDITED = NO`
`SCIENTIFIC_RESULTS_CHANGED = NO`
`MD_RUN_AUTHORIZATION = NOT_GRANTED`
