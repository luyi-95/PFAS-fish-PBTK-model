# Sol High protocol adjudication after the failed PFBS bonded cycle

Date: 2026-09-26. Independent scientific protocol review. All source evidence is read-only. Only this review and its JSON were created. No Gaussian/GROMACS invocation, fit, minimization, parameter generation or MD was performed.

## Unique decision

**BROAD_PFBS_REPARAMETERIZATION_REQUIRED**

`NEW_QM_REQUIRED = YES`

`EXPECTED_PARAMETER_CLASSES = BOND_EQUILIBRIA; VALENCE_ANGLE_EQUILIBRIA; IDENTIFIED_BOND_AND_ANGLE_FORCE_CONSTANTS; UREY_BRADLEY_REVIEW_WITH_CONDITIONAL_IDENTIFIABLE_CHANGE; COUPLED_PROPER_TORSION_AMPLITUDES`

`EXPECTED_SCOPE = LARGE` relative to the previously authorized three-r0/local-junction correction: systematic bonded coverage of this 17-atom PFBS molecule, including the fluorocarbon chain. This is not a general PFAS force-field development program.

`EXPECTED_SCIENTIFIC_VALUE_FOR_MEMBRANE_MD = MODERATE`

`PARAMETER_EDITED = NO`

`MD_RUN_AUTHORIZATION = NOT_GRANTED`

This decision identifies the scientific scope required if PFBS force-field development continues. It grants no new calculations or edits. The one valid formal DP bonded candidate cycle is consumed. The invalid mixed-derived draft is excluded. Current parameters remain REJECTED for release; the evaluated candidate is not adopted; torsion-only fitting and MD remain suspended.

## Why B is selected

The sole candidate improves all ten targeted bond observations, yet repeats a harmful local trade-off: C1-C2-S1 errors grow from −6.648/−5.040° to −9.518/−8.228° in GEO_A/B. This demonstrates coupled response of the total molecular potential. It does not uniquely establish a defective angle, UB, stiffness, torsion, charge or LJ term.

The full baseline already has discrepancies outside the two junction axes. C3-C4 is about 0.05 Å short in both minima. In GEO_A, F1-C1-F2 and F5-C3-F6 errors are −5.55/−5.90°, while terminal CF3 F-C-F angles are about −4 to −5.5°. These persist in the candidate. Its C1-C3 and C2-F3/F4 lengths also worsen. The shared fluorocarbon types and three non-equivalent C-C environments make a junction-only success insufficient to establish whole-molecule adequacy.

| Option | Adjudication |
|---|---|
| A: joint local bonds/angles/T_CC/T_CS | Joint treatment is methodologically appropriate, but the narrowly local scope is inadequate as the complete development protocol. It omits independently biased tail bonds/angles and a third internal rotation axis; type closure affects more than the junction. A could be a diagnostic block inside B, not a release plan by itself. |
| B: systematic CHARMM-compatible PFBS refinement | Selected. Inspect the entire PFBS bonded model, retain supported parameters, and constrain any revised blocks with geometry, curvature and coupled PES together. No assertion that every listed parameter must change. |
| C: terminate development | Scientifically permissible as a project-management choice, but not compelled by current evidence. A minimum, accessible Hessian and extensive validated scans already exist; no chemical or CHARMM functional-form impossibility has been demonstrated. The remaining work has moderate support value, not a demonstrated membrane effect. |

B does not supersede report 75: original CGenFF charges and LJ remain ACCEPTED_WITH_CAUTION. Neither the candidate response nor the gas-phase water residual identifies a nonbonded remedy. Reopening nonbonded parameters would require a separate identifiable defect and additional scope decision.

## Exact term inventory and the A-to-B boundary

Atom map: S1=1; O1/O2/O3=11/12/13; C1/C2/C3/C4=14/15/16/17; F1–F9=2–10. Molecular chain is S1–C2–C1–C3–C4. Reversed type strings describe the same term. The effective existing baseline TPR dump is the authority for inherited terms; the short converted PRM does not contain all active parameters. Tables are current GROMACS values, not proposed numbers or CHARMM convention values. Bond r0/UB r13 use nm, angles degrees, energies kJ/mol; harmonic coefficients include the GROMACS 1/2 convention. Full precision and source hashes reside in EXACT_EFFECTIVE_TERM_MAP.json.

### Bonds

| Type family | Exact atom instances | Existing effective coefficients |
|---|---|---|
| OG2P1–SG3O1 | 1-11; 1-12; 1-13 | b0= 1.44800e-01, cb= 4.51872e+05 |
| CG312–SG3O1 | 1-15 | b0= 1.80700e-01, cb= 1.54808e+05 |
| CG312–FGA2 | 2-14; 3-14; 4-15; 5-15; 6-16; 7-16 | b0= 1.35300e-01, cb= 2.92043e+05 |
| CG302–FGA3 | 8-17; 9-17; 10-17 | b0= 1.34000e-01, cb= 2.21752e+05 |
| CG312–CG312 | 14-15; 14-16 | b0= 1.45630e-01, cb= 2.27869e+05 |
| CG302–CG312 | 16-17 | b0= 1.45630e-01, cb= 2.27869e+05 |

Mandatory equilibrium-variable coverage for a future joint protocol: CG312–SG3O1, equivalent OG2P1–SG3O1, CG312–CG312 **both** 14–15 and 14–16, and CG302–CG312 16–17. The baseline discrepancies justify revisiting r0 as a block, rather than carrying the failed candidate's values forward. The two C–F bond families require all-instance checks; their r0 and k should initially remain fixed because the near-head C–F shifts can be a response to the changed junction, while other instances are close to QM. Unfreeze only if the new curvature/finite-displacement evidence separates a shared C–F defect from the angle/UB balance.

No bond force constant is proven wrong by equilibrium geometry. k is a candidate class for Hessian/finite-displacement identification, not an automatically free variable. A source-supported k should stay frozen. CG312–CG312 is shared; systematic B must judge a common PFBS-specific term across both bonds before permitting an explicitly justified environment split. Do not silently replace a global type or give every atom instance its own parameter.

Penalty provenance remains unchanged: the inherited CG312–CG312 14–15 term has no directly emitted PFBS penalty6. Stream penalty6 belongs to CG302–CG312 from an analogue. Inherited S–O has no directly emitted PFBS bond penalty. High penalty is a test priority, not proof of error.

### Angles and Urey-Bradley terms

| Type family | Exact atom instances | Existing effective coefficients |
|---|---|---|
| OG2P1–SG3O1–OG2P1 | 11-1-12; 11-1-13; 12-1-13 | theta= 1.09470000e+02, ktheta= 1.08784000e+03, r13= 2.45000000e-01, kUB= 2.92880000e+04 |
| CG312–SG3O1–OG2P1 | 11-1-15; 12-1-15; 13-1-15 | theta= 9.90000000e+01, ktheta= 6.69440000e+02, r13= 0.00000000e+00, kUB= 0.00000000e+00 |
| FGA2–CG312–FGA2 | 2-14-3; 4-15-5; 6-16-7 | theta= 1.07000000e+02, ktheta= 1.25520000e+03, r13= 2.17000000e-01, kUB= 8.36800000e+03 |
| CG312–CG312–FGA2 | 2-14-15; 2-14-16; 3-14-15; 3-14-16; 4-15-14; 5-15-14; 6-16-14; 7-16-14 | theta= 1.20931400e+02, ktheta= 4.18902080e+02, r13= 0.00000000e+00, kUB= 0.00000000e+00 |
| CG312–CG312–CG312 | 15-14-16 | theta= 1.18610000e+02, ktheta= 3.90701920e+02, r13= 0.00000000e+00, kUB= 0.00000000e+00 |
| FGA2–CG312–SG3O1 | 1-15-4; 1-15-5 | theta= 1.22000000e+02, ktheta= 4.18400000e+02, r13= 2.35700000e-01, kUB= 2.51040000e+04 |
| CG312–CG312–SG3O1 | 1-15-14 | theta= 1.22000000e+02, ktheta= 4.18400000e+02, r13= 2.35700000e-01, kUB= 2.51040000e+04 |
| CG302–CG312–FGA2 | 6-16-17; 7-16-17 | theta= 1.20930000e+02, ktheta= 4.18902080e+02, r13= 0.00000000e+00, kUB= 0.00000000e+00 |
| CG302–CG312–CG312 | 14-16-17 | theta= 1.18610000e+02, ktheta= 3.90701920e+02, r13= 0.00000000e+00, kUB= 0.00000000e+00 |
| FGA3–CG302–FGA3 | 8-17-9; 8-17-10; 9-17-10 | theta= 1.07000000e+02, ktheta= 9.87424000e+02, r13= 2.15500000e-01, kUB= 2.51040000e+04 |
| CG312–CG302–FGA3 | 8-17-16; 9-17-16; 10-17-16 | theta= 1.20930000e+02, ktheta= 4.18902080e+02, r13= 0.00000000e+00, kUB= 0.00000000e+00 |

A's minimally relevant angle set includes CG312–CG312–SG3O1, FGA2–CG312–SG3O1, CG312–CG312–FGA2, FGA2–CG312–FGA2, CG312–CG312–CG312, CG312–SG3O1–OG2P1 and OG2P1–SG3O1–OG2P1. That already includes shared chain terms. B additionally requires CG302–CG312–CG312, CG302–CG312–FGA2, CG312–CG302–FGA3 and FGA3–CG302–FGA3, covering the biased tail/CF3 geometry.

Theta0 is eligible for joint identification in the reproducibly biased families. CG312–CG312–CG312 is near its reference in GEO_A and should begin frozen as a guard, with B/scan geometries checked. ktheta is only eligible when mode-character/curvature information supports it. The original junction theta0=122° already exceeds the two QM realized angles; increasing it from the observed angular residual alone is unsupported.

Nonzero UB exists in five type families: O–S–O; FGA2–CG312–FGA2; FGA3–CG302–FGA3; CG312–CG312–SG3O1; FGA2–CG312–SG3O1. Their r13/kUB must be considered with bond/angle response. Start with source UB fixed. If the reduced bond/angle model cannot reproduce independently checked curvature, permit only an identifiable UB degree of freedom under a newly frozen variable list. Do not freely fit both r13 and kUB together with theta0/ktheta at every family, or invent UB terms in the six families whose UB is zero. These are conditional protocol choices, not numerical edits authorized now.

### Proper torsions

| Type family | n | Exact atom instances | Existing effective coefficients |
|---|---:|---|---|
| FGA2–CG312–SG3O1–OG2P1 | 3 | 11-1-15-4; 11-1-15-5; 12-1-15-4; 12-1-15-5; 13-1-15-4; 13-1-15-5 | phi= 0.00000000e+00, cp= 9.62320000e-01 |
| CG312–CG312–SG3O1–OG2P1 | 3 | 11-1-15-14; 12-1-15-14; 13-1-15-14 | phi= 0.00000000e+00, cp= 9.62320000e-01 |
| FGA2–CG312–CG312–SG3O1 | 1 | 2-14-15-1; 3-14-15-1 | phi= 1.80000000e+02, cp= 4.85344000e+00 |
| FGA2–CG312–CG312–FGA2 | 3 | 2-14-15-4; 2-14-15-5; 3-14-15-4; 3-14-15-5; 2-14-16-6; 2-14-16-7; 3-14-16-6; 3-14-16-7 | phi= 0.00000000e+00, cp= 1.84096000e+00 |
| CG312–CG312–CG312–SG3O1 | 1 | 16-14-15-1 | phi= 1.80000000e+02, cp= 3.93296000e+00 |
| CG312–CG312–CG312–SG3O1 | 2 | 16-14-15-1 | phi= 0.00000000e+00, cp= 1.58992000e+00 |
| CG312–CG312–CG312–SG3O1 | 3 | 16-14-15-1 | phi= 0.00000000e+00, cp= 4.60240000e-01 |
| CG312–CG312–CG312–FGA2 | 1 | 16-14-15-4; 16-14-15-5; 15-14-16-6; 15-14-16-7 | phi= 1.80000000e+02, cp= 4.85344000e+00 |
| CG302–CG312–CG312–FGA2 | 1 | 2-14-16-17; 3-14-16-17 | phi= 1.80000000e+02, cp= 4.85344000e+00 |
| CG302–CG312–CG312–CG312 | 3 | 15-14-16-17 | phi= 0.00000000e+00, cp= 5.98312000e+00 |
| FGA2–CG312–CG302–FGA3 | 3 | 6-16-17-8; 6-16-17-9; 6-16-17-10; 7-16-17-8; 7-16-17-9; 7-16-17-10 | phi= 0.00000000e+00, cp= 1.84096000e+00 |
| CG312–CG312–CG302–FGA3 | 1 | 14-16-17-8; 14-16-17-9; 14-16-17-10 | phi= 1.80000000e+02, cp= 4.85344000e+00 |

T_CC is C3–C1–C2–S1 (16–14–15–1), about 14–15. Its complete axis energy contains:
CG312–CG312–CG312–SG3O1 n=1,2,3;
FGA2–CG312–CG312–SG3O1 n=1;
CG312–CG312–CG312–FGA2 n=1;
and FGA2–CG312–CG312–FGA2 n=3.
T_CS is C1–C2–S1–O1 (14–15–1–11), about 15–1. Its complete axis energy contains CG312–CG312–SG3O1–OG2P1 n=3 and FGA2–CG312–SG3O1–OG2P1 n=3 over all O/F instances.

Some T_CC terms also act about C1–C3, 14–16. B requires whole-chain read-only evaluation first, including the C1–C3 axis C2–C1–C3–C4 and the C3–C4/CF3 axis C1–C3–C4–F7. This does not unconditionally require new tail QM grids: shared-amplitude release or a specific torsional energy/rotamer defect triggers the corresponding new targets below. Their type groups are in the table. A primary scan does not license independent fitting of each quadruplet sharing an axis. Existing zero-amplitude n=3 PRM components remain frozen initially; existing phases and multiplicities remain fixed. Only supported amplitudes become variables. No new high multiplicities, CMAP, non-CHARMM cross-term or environment split is assumed.

## Correlation and identifiability

1. Equilibrium r0/theta0 do not equal realized minima of a coupled force field. Torsions, UB and intramolecular nonbonded forces can shift a minimum. The observed r0-only response cannot identify their individual causes.
2. UB endpoint distance depends geometrically on two bonds and their included angle. At one minimum, theta0/ktheta and r13/kUB can produce nearly interchangeable force/curvature contributions. Multiple conformers and displaced configurations are needed; free four-field UB/angle fits are disallowed by default.
3. Several dihedrals around one bond differ mainly by fixed geometric offsets. Summed Fourier columns can be collinear or indistinguishable, especially the O-equivalent n=3 families. Fit identifiable grouped energy combinations; freeze a source amplitude or use a prespecified restrained group when individual components cannot be separated. A larger number of PES rows is not a guarantee of independent parameters.
4. The T_CS scan mostly samples T_CC near −60°. T_CC relaxes T_CS, sometimes on another branch. These adiabatic one-dimensional curves do not sample mixed CC/CS curvature independently. The CC240 forward/reverse pair is branch information at one angle, not a second independent rotation grid.
5. Hessians from a structure with MM/QM displacement cannot simply be matched element-by-element and called a force-constant determination. Coordinate/mass/units, nonbonded contributions, equilibrium displacement and mode mixing must be addressed. Curvature, mode character and finite-amplitude forces should jointly constrain the fit.
6. New sensitivity/rank analysis must use the complete target vector and the actual proposed variable list. Inspect singular directions and source-restraint dependence. The 1326 packed Hessian entries are not 1326 independent observables: rigid motions, coordinate correlations and internal redundancy reduce independent information. If identifiable reduced blocks cannot jointly satisfy targets, stop and return to protocol review; do not silently add variables, probes, torsion harmonics or new force-field classes.

The literature supports these cautions: CHARMM/CGenFF uses geometry, vibrational information and PES for bonded development, including UB. Structural inconsistency can confound force-constant fitting. Separately successful fits for dihedrals sharing an axis can give an inaccurate combined energy. [Original CGenFF](https://pmc.ncbi.nlm.nih.gov/articles/PMC2888302/), [structural-inconsistency study](https://pubmed.ncbi.nlm.nih.gov/36112364/), [CGenFF optimizer practical considerations](https://docs.silcsbio.com/2025/cgenff/optimizer.html).

## Existing QM: substantial, but insufficient for B

| Existing evidence | Information supplied | Remaining limitation |
|---|---|---|
| GEO_A | MP2/6-31+G(d) minimum geometry, electronic energy, 45 positive modes, printed eigenvectors; accessible packed 51×51 Hessian | Only one local basin's curvature; extraction/projection/units still need validation, not a completed MM mode comparison |
| GEO_B revised | Distinct retained minimum geometry and relative electronic energy, about 0.47535 kcal/mol above A | No frequency/Hessian found in local deliverable or read-only remote PFBS filename inventory; no claim about unrelated external locations |
| T_CC relaxed PES | 12 constrained angles, achieved geometries, energies, branch changes and large initial MM error | One adiabatic path, unscanned torsions relax; energies cannot uniquely partition bond/angle/torsion error |
| T_CS relaxed PES | 13 points over 0–120°, O-permutation/closure information and barrier mismatch | Mostly one CC basin; closure is related by chemical symmetry, not 13 independent torsion modes |
| CC240 forward/reverse | Preserved branch discrepancy: QM 0.22530 kcal/mol, MM about 0.00130 kcal/mol; branch geometry evidence | Does not establish a unique 2D surface or independent local force constants; actual CS is 59.8697/59.6113° for the two branches, so full geometry/rotamers distinguish them, not their nominal axes alone |

GEO_A log SHA256 is 56b2bf0620ab18b1ee3517d3b2e1a7754adbba416f2737418938587fd34a4667, independently rechecked. Report47 confirms its minimum with numerical caution and thermochemical warnings. Root's read-only archive audit finds 1326 numeric Hessian entries after NImag=0 (51×52/2), followed by 51 gradient entries. This is a usable existing Hessian resource; no new GEO_A frequency is required merely to obtain one. Its atom ordering, Hartree/Bohr convention, coordinate frame, masses, projection and any frequency scaling must be checked before fitting. The original 0.89 Hessian scaling convention, if selected, must be prespecified with raw and scaled data retained; scaling cannot be adjusted to rescue a candidate.

All GEO_A/B and 25 main PES points have already influenced diagnosis and scope. They are development/training evidence and compatibility tests, not blind holdout data. The 26th profile row is the extra CC240 branch.

## Minimum new QM proposal for the selected scope

This staged proposal separates the core initial design from conditional and recommended additions. It is not a rank guarantee, execution authorization or promise that every parameter becomes identifiable. Use the same accepted anion method/state and evidence standards. Freeze exact inputs, starts, partitions, constraints, methods, cost and stop conditions before any execution. Existing A Hessian extraction is read-only preparation and does not require a new QM calculation.

1. **GEO_B frequency/Hessian at the accepted revised minimum.** One new frequency target with atom/order/coordinate binding and stationary-point checks supplies a second basin's curvature. If not a minimum, review that basin before using a harmonic target; do not change its identity silently.
2. **Sparse mixed-junction surface.** Six proposed training configurations: T_CC=60°,180°,300° crossed with T_CS=30°,90°; constrain both named rotations and relax remaining coordinates. These sample both rotations away from their adiabatic valleys. Four distinct prospective holdouts: T_CC=90°,210° crossed with T_CS=20°,100°. Keep all results including high energies and nonconvergence; do not force an additive energy fit to a functional-form failure. Some choices can produce high-energy states; their role is mixed-response diagnosis, with low-energy weighting prespecified and no discarded bad points.
3. **Conditional independent C1–C3 axis evidence.** If a proposed variable list changes CG312–CG312–CG312–FGA2 or FGA2–CG312–CG312–FGA2 amplitudes shared with 14–16, or an independent tail energy/rotamer defect emerges, independent axis evidence is mandatory before fitting/release: twelve 30° relaxed points for C2–C1–C3–C4, with initial other torsions and branch policy frozen. Prepartition eight for development and four angles (60°,150°,240°,330°) for prospective withholding. If all shared amplitudes remain source-frozen and new finite-displacement/holdout geometry supports the tail, do not add this full scan automatically. Preserve actual relaxed CC/CS/CF3 rotations and full geometry when triggered.
4. **Conditional terminal CF3 rotation.** Geometry bias alone does not establish a tail torsion defect. Keep its two original torsion families frozen initially. Only a demonstrated tail energy/rotamer defect, or a separately justified need to vary those amplitudes, triggers five training points 0°,30°,60°,90°,120° for C1–C3–C4–F7 with fluorine-permutation closure, plus four prospective interleaved holdouts 15°,45°,75°,105°. Report26's fifth-scan condition is preserved; penalty22.1 is not a trigger by itself.
5. **Conditional finite-displacement energies/gradients only for unresolved reduced blocks after A/B Hessian audit.** If curvature/parameter ambiguity remains, a proposed seed batch uses symmetric positive/negative displacements of a coupled junction stretch/bend direction and a tail F-C-F/C-C direction, with original coordinates otherwise fixed, to check finite-amplitude shape. This is not an unconditional new QM requirement. Use one predeclared small amplitude at A for development and a different predeclared amplitude at B for holdout (four configurations each). Choose normalized displacement vectors from identified weak directions without tuning to desired residuals. Exact amplitude/vector must be frozen before execution. Additional directions are not authorized automatically if these fail to identify the selected variables.
6. **Recommended additional holdout: one genuinely new minimum outside the retained A/B basins.** A separately selected tail/junction conformer with optimization and frequency/Hessian, withheld from fitting. This is a strong validation recommendation, not a demonstrated mandatory first-stage target before identifiability analysis. Select its starting geometry prospectively from the frozen graph/torsion protocol, not from the eventual candidate's favorable result.

The proposed necessary initial tranche is items1 and2: one GEO_B frequency target and ten sparse mixed-junction configurations (11 target configurations/families). The ten-point mixed selection is a defensible seed design, not a proven smallest grid. The exact smallest sufficient new QM batch cannot be determined before a target/parameter Jacobian and grouped identifiability audit. Items5 and6 add eight and one configurations/families only under their stated conditions or a separately accepted validation design. If the shared-chain torsion trigger in item3 occurs, add its 12 points; item4 adds nine only under its separate tail-torsion trigger. The conditional complete collection would contain 41 configurations/families, but it is not the currently required minimum. Neither count guarantees rank or a number of executable jobs: workflows may split stages, fail or reveal rank insufficiency. The core prospective holdouts are four mixed-junction configurations; conditional displaced configurations, the recommended new minimum and any triggered tail grids add their distinct holdouts. Existing targets may constrain development, but withheld targets must remain unused for fitting, term selection, weights and restart decisions.

No repeat of the existing 25 junction scan jobs or GEO_A frequency is required as a new QM target solely because the old candidate failed. Future MM validation would nevertheless need the full existing and new geometry/PES collection under the new candidate, independently minimized as appropriate; this review does not execute it.

## Joint objective, frozen fields and validation

A future protocol may computationally alternate blocks, but it must evaluate one joint CHARMM potential against geometry, curvature, both existing junction surfaces and any independently triggered chain-axis surfaces. Whole-bonded audit does not mean all four rotation axes must be refitted. It cannot declare bonded success before energetics, or torsion success while geometry worsens. Prespecify source restraint, unit/scaling choices, grouped variables and target weights. Do not optimize membrane outcomes, insertion depth, cardiolipin contact, ROS or diffusion to choose parameters.

Frozen: total charge −1/singlet; 17-atom topology and graph; masses/atom identity; O-equivalent charge/type and grouped S–O/angular/torsion symmetry; CGenFF additive potential; charges/LJ and combining rules; exclusions/1–4 conventions; water/membrane force fields; shared force-field files; existing phase/multiplicity/zero-amplitude torsion components until independently justified. Use PFBS-only overrides with explicit type/instance closure and a complete semantic diff if a later candidate is authorized. Do not transfer automatically to PFHxS/PFOS.

Required independent validation jointly includes: all 16 bonds and 30 angles, focal and whole-chain geometry, all 136 atom-pair distances categorized by graph separation, SO3/CF3 permutation consistency, no new contact collapse or branch loss, supported mode character/curvature, A/B relative electronic-conformer ranking, T_CC and T_CS profiles under one common energy anchor, CC240 branches, any triggered new chain-axis surfaces, mixed-junction holdouts and the new minimum. MM@QM energies are secondary to independently relaxed model comparisons. Preserve Phase2 water/ESP compatibility at changed geometries and its WITH_CAUTION limitations.

Reject a fit that improves PES through harmful local/whole-chain geometry compensation, improves geometry through degraded low-energy basins/barriers, or changes branch/symmetry to hide error. Existing report29 diagnostic guidance and qualitative gates remain the basis; no new automatic numerical acceptance threshold is invented here. A candidate must be independently adjudicated. Holdout failure cannot trigger refitting with the same data relabeled as validation; it requires a new protocol/cycle decision.

## Value and stopping boundary

Moderate value: a defensible PFBS conformational model can support a later membrane simulation comparison and avoid using the rejected initial model. This work cannot itself validate membrane interactions, and report75's short-contact nonbonded bias remains. Large bonded scope plus new QM/holdout work warrants an explicit resource decision before execution. Broad homolog development, nonbonded reoptimization or repeated unconstrained cycles would change the benefit/cost judgment.

If reduced parameters remain unidentifiable, CHARMM-compatible grouped terms cannot jointly preserve geometry and surfaces, or the required workload exceeds the membrane-support project's chosen budget, stop PFBS development rather than accept compensating errors. Such a later stopping decision does not change today's single scope verdict.

**Terminal state:** PROTOCOL_REVIEW_COMPLETED; NEW_QM_REQUIRED=YES; PARAMETER_EDITED=NO; NEW_CALCULATION_AUTHORIZATION=NOT_GRANTED; MD_RUN_AUTHORIZATION=NOT_GRANTED.

## Evidence files

- EXACT_EFFECTIVE_TERM_MAP.json and SOURCE_HASH_BINDING.json: approved original source parameters/effective dump, source hashes and exact instances.
- QM_DATA_AVAILABILITY.json and EXISTING_JUNCTION_COVERAGE.tsv: existing Hessian/mode availability and coupled scan coverage.
- SOL_HIGH_FORMAL_CANDIDATE_FINAL_REVIEW.md/.json: consumed cycle's verified candidate geometry and disposition.
- Reports26/29/47/75 and original MM_SOL_HIGH_REVIEW_PACKAGE_20260926_v1: target hierarchy, frozen gates, frequency caution and current nonbonded decision.
