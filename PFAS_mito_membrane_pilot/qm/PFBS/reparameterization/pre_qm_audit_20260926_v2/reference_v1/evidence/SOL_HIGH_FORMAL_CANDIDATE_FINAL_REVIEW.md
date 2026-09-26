# Sol High final review of the sole formal DP bonded candidate

Date: 2026-09-26. Independent read-only scientific adjudication of `formal_dp_candidate_01`. Sources, frozen candidate and executor records were not edited. Reviewer arithmetic extracts existing geometry comparisons; no new MM/QM/MD calculation or second candidate was performed.

## Final disposition

`BONDED_REFINEMENT_STATUS = INSUFFICIENT`

`TORSION_REFINEMENT_STATUS = PROTOCOL_REVIEW_REQUIRED`

`CANDIDATE_ADOPTION = NOT_VALIDATED_REJECTED_FOR_WORKING_USE`

`STOP_BEFORE_PROFILES = YES`

`FORMAL_BONDED_CYCLE_CONSUMED = YES`

The candidate substantially corrects the five edited bond-instance lengths in both conformers. It also reproducibly worsens the defining C1-C2-S1 angle and shortens unchanged junction/tail bonds further. The authorized objective was a minimally corrected local geometry sufficient for defensible torsion comparison. That objective is unmet. Do not release unchanged-torsion profiles, activate the suspended torsion fit, adopt the candidate, derive a second candidate, expand angle/UB scope or run MD. Preserve this candidate and valid calculation evidence for a separately reviewed escalation.

## Immutable evidence and execution integrity

Remote work root: `/home/ls/projects/PFAS_mito_membrane_pilot/qm/PFBS/task1_bonded_candidate_20260926_v1/formal_dp_v2`.

- Candidate ITP SHA256 `6a6c241bfeee38341b685c377171fc4d5be0d9e75d01f215f8abf4b26640d908`; freeze JSON `0aa37a46ab57232e0ffb2ac359ecc458cf6ca14a21b8a2c401aec64bb6f1fcee`. Original/candidate PRM remains byte-identical, SHA256 `24baf41553845380e9905f7419ca85cb0528dcd7652d596ca6ba83e003d05a56`.
- Full-precision response matrix SHA256 `b2f64dcc5057a650129b66432f275a5a385bf4a7fc30167aadc15fe9f5ecb3bc`; target record `c9350d0c89a12553840825273431617a45476e36d9f5839c1013a4877152e577`. Correct source-precision target/reader/builder bindings were used for the single declared LS solve.
- Semantic TPR proof SHA256 `0ee6e834a9d0fe11a27068791d29d6ba50669ceab32868838fb8a9b80788658b`: exactly five atom-instance bond r0 changes, fixed k, 17 original atom properties, unchanged exclusions, 16 bonds/30 U-B angles/38 proper terms/36 LJ-14 interactions. Shared force-field, charges/LJ and other physical terms remain unchanged. Source ITP k precision is preserved; rounded printed TPR parameters are not higher-precision source values.
- Candidate validation A run-record SHA256 `18d6c78a8518ff2f0fa3ebd07d52acd0b048bc8dfd687434db176a71a60cf0e0`; B `3a8dc5f043cf7529a7636c0a0d1de64dfe76a2e53526fde6bb66ec855d9e6081`. Executor complete comparison SHA256 `cecde48b75e7455d61d5048981d5ba3b4c20fdb22c8c1ec3ca6b311d715e983f`. Sol independently checked these available records and frozen candidate/proof/comparison hashes.
- Accepted QM start hashes match independently: A `bf6d3b621559c8a9eab217fdb97f1679c9dff8be0a8702542092e3f650516442`; B `fc99a7915d74ebe8529d1f6619ca528a33b14c721384b3fe84f65a1cf1678cb3`. Raw stage-final G96 and raw stage-log hashes match their records; final A G96 `e4d4dfb1df78705829f11cd8167b886396aefe53f30c6f2f4819a3cdb657737d`, final B `483bf1ff81e7d6a71f4934d6b8a1dd259ffa0f82d014db5aefa8f65fc3cdc9e7`.
- Both validations use the frozen DP executable SHA256 `910c195c43f12f35e44ff5ccfdafd3236bf86c6afb0774b550e0ccb5d5148c2d`, independent accepted-QM starts, same MDPs/isolated Cut-off settings and L-BFGS→CG schedule. Final CG Fmax A=4.520148992/B=5.192622965 kJ mol^-1 nm^-1, below the prescribed 10 gate. Sol checked raw convergence lines/log hashes. The exact L-BFGS efficiency-warning receipt is present; CG preprocessing/runtime inspected warning/fatal lists are empty. L-BFGS raw -1 step counters remain a reporting limitation; 72/117 energy evaluations and energy reductions demonstrate minimization, without inferring real iteration counts. Both CG logs print 0 steps and two energy evaluations.

The observed scientific failure is a valid minimized candidate geometry outcome. Invalid mixed-derived drafts are excluded; they did not become this candidate or consume a second formal cycle.

The existing current parameter set remains REJECTED at its prior acceptance gate. This candidate is preserved as an evaluated artifact and is not adopted for working use. Exactly one valid formal DP LS/candidate cycle has been consumed. Angle/UB attribution remains unresolved; this review introduces no new acceptance thresholds or scientific variables.

## All ten fitted observations and nonlinear validation

Values and residuals below are in Angstrom. `_A` numeric-field suffix in worker JSON means the Angstrom unit; observation row suffix A/B identifies the conformer. Linear prediction is the sole LS hypothesis, not the primary accepted geometry result.

| Observation | QM target | Formal baseline | Linear prediction | Actual candidate | Actual minus QM | Actual minus prediction |
|---|---:|---:|---:|---:|---:|---:|
| SC_A | 1.873679 | 1.769055 | 1.873745 | 1.874603 | 0.000924 | 0.000858 |
| CC_A | 1.546334 | 1.486772 | 1.544623 | 1.546413 | 0.000080 | 0.001791 |
| SO1_A | 1.482405 | 1.451670 | 1.478198 | 1.480307 | -0.002098 | 0.002108 |
| SO2_A | 1.479536 | 1.453366 | 1.484569 | 1.481848 | 0.002312 | -0.002721 |
| SO3_A | 1.481335 | 1.452317 | 1.479541 | 1.480793 | -0.000541 | 0.001252 |
| SC_B | 1.877926 | 1.777124 | 1.877789 | 1.882345 | 0.004419 | 0.004556 |
| CC_B | 1.541473 | 1.489781 | 1.542953 | 1.548686 | 0.007213 | 0.005733 |
| SO1_B | 1.480466 | 1.453425 | 1.478669 | 1.481815 | 0.001349 | 0.003146 |
| SO2_B | 1.480666 | 1.453916 | 1.482311 | 1.482143 | 0.001477 | -0.000168 |
| SO3_B | 1.482324 | 1.452899 | 1.483285 | 1.481560 | -0.000764 | -0.001725 |

All ten absolute bond residuals improve from formal baseline; largest remaining fitted-bond residual is B C1-C2 +0.007213 A. Nonlinear discrepancies from the linear prediction reach +0.005733 A. These are reported without introducing a new Jacobian tolerance. The candidate's 15.6969/7.9843/3.3980 probe-sized increments were openly extrapolated; actual validation resolves that hypothesis for bond lengths but does not establish adequate complete bonded geometry.

## Decisive geometry trade-off

| Metric | QM A | Baseline A | Candidate A | QM B | Baseline B | Candidate B |
|---|---:|---:|---:|---:|---:|---:|
| C1-C2-S1, degrees | 119.969852 | 113.322100 | 110.451996 | 116.912102 | 111.871823 | 108.684180 |
| C1-C3, A | 1.553625 | 1.525934 | 1.521173 | 1.558265 | 1.523694 | 1.517233 |
| C3-C4, A | 1.548047 | 1.495364 | 1.493947 | 1.545069 | 1.494801 | 1.493989 |
| C2-F3, A | 1.375531 | 1.351433 | 1.344443 | 1.373731 | 1.352816 | 1.345850 |
| C2-F4, A | 1.371262 | 1.356631 | 1.348968 | 1.374642 | 1.352588 | 1.345924 |

C1-C2-S1 errors worsen from -6.647751 to -9.517856 degrees in A and from -5.040279 to -8.227922 degrees in B. Candidate-versus-baseline decreases are 2.870105/3.187643 degrees, with little L-BFGS-to-CG angle movement, establishing a converged repeated trade-off. This is material under the original 3-degree diagnostic guidance and the predeclared no-compensation/no-new-distortion rule; no new automatic release threshold is used.

The unchanged C1-C3 instance further shortens, leaving errors -0.032452/-0.041032 A. C3-C4 remains about -0.054100/-0.051080 A short. These discrepancies existed in the formal baseline and are not silently reassigned as new editable terms; their additional worsening supports the inability of this three-r0 correction to give adequate coupled geometry. C2-F3/F4 shortening also increases in both cases.

The 30-angle audit shows adjacent C1-C2-F3/F4 residuals worsening: +9.319427/+7.251335 degrees in A and +7.180544/+8.549989 degrees in B. SO3 O-S-O and O-S-C2 biases remain around 3–5 degrees while equivalent S-O bond lengths improve. Many tail angles retain baseline bias. Complete term-level results are in the accompanying reviewer JSON; no global RMSD replaces these local findings.

## Connectivity, O equivalence, nonbonded geometry and basins

The original 17-atom/16-bond graph and parameter identities are preserved. All 136 pair distances were compared; these include 16 bonded, 30 two-bond-separated, 36 three-bond-separated and 54 farther graph pairs. They are not 136 independent nonbonded interactions. No dissociation, atom-map change or new severe close-contact collapse is indicated. Candidate graph-distance>3 pair minima are 2.631621/2.604214 A. No new cutoff/image interaction appears: maximum pair distance A=0.637925/B=0.707333 nm; image lower bounds A=9.362075/B=9.292667 nm, far outside 2 nm.

Identical S-O r0 and charges retain chemical O equivalence. Realized S-O spreads A=0.001542/B=0.000583 A and retained SO3 connectivity do not cure the O-S-O/O-S-C angular mismatch. Requiring identical O bond distances within one conformer would be an artificial target and is not imposed.

Candidate final junction torsions remain near the respective baseline basins: A T_CC=-63.772826/T_CS=71.324743 degrees; B=-169.329716/64.351403 degrees. No wholesale basin switch is indicated by these two independent minima. This does not validate sampled torsion profiles; none were released or assessed for this candidate.

## Attribution and remaining scope

The results demonstrate strong coupled geometry response when these bond equilibrium targets change. They do not uniquely isolate an angle theta0, UB r13/kUB, bond/angle stiffness, torsion or intramolecular nonbonded defect. In particular the original theta0=122 degrees already exceeds both QM realized junction angles, so a further arbitrary theta0 increase or UB replacement would require separate evidence and authorization. No matched normal-mode-character comparison supports a stiffness claim.

No unchanged-torsion profile calculation is scientifically released because material local geometry contamination remains. No Phase 2 candidate compatibility evaluation is promoted to completed validation. The next action is a separately scoped Sol/user escalation that preserves this failed candidate and all valid evidence. This review authorizes no extra QM, second bond solve, expanded angle/UB fit, force-constant change, charge/LJ edit, other-PFAS transfer or MD.

`PARAMETER_WORKING_STATE = REJECTED_FOR_RELEASE`

`TORSION_REFINEMENT_AUTHORIZATION = UNUSED_AND_SUSPENDED`

`UNMODIFIED_TORSION_PROFILE_VALIDATION = NOT_RELEASED`

`SECOND_BONDED_CANDIDATE = NOT_AUTHORIZED`

`MD_RUN_AUTHORIZATION = NOT_GRANTED`
