# 29 — PFBS targeted QM acceptance and escalation rules

Date: 2026-09-23
Decision authority: Sol High. Luna may collect and tabulate results only.
QM_RUN_AUTHORIZATION = NOT_GRANTED
MD_RUN_AUTHORIZATION = NOT_GRANTED

## Integrity gate, before interpreting any target

PASS only if the 17-atom PFBS- connectivity and fixed atom map match the untouched CGenFF 5.0 stream, charge -1/multiplicity 1 are shown in every relevant job, the Gaussian 16 C.02 banner is captured, the installation is used with institutional permission, every input/output SHA256 is recorded, all expected outputs are present, and SCF/optimization convergence and warnings have been reviewed. An exact route/constraint mismatch or missing provenance is FAIL and stops this dataset. Any ambiguity is REVIEW by Sol High. Failure never licenses an unrecorded rerun, engine switch, altered charge, or parameter edit.

## Task 1: geometry and frequencies

PASS for the initial parameter model: the selected QM reference is a real minimum (no chemically meaningful imaginary mode), PFBS identity and charge are intact, and matched vacuum CGenFF-minimized S1-C2, C1-C2, S1-O1/O2/O3 and C1-C2-S1 geometry agrees within the CGenFF method's approximate diagnostic guidance of 0.03 A for focused bonds and 3 degrees for focused angles, without a distorted SO3 or junction. The guidance is a diagnostic, not an automatic optimizer target. Inspect low-frequency junction modes by character before judging force constants.

REVIEW: one or more local deviations exceed that guidance, A/B lead to different minima or markedly different junction geometry, a very small imaginary mode may be numerical, or a mode assignment is ambiguous. The reviewer decides whether the initial bond/angle can stand or requires a new parameter-refinement proposal.

FAIL: nonconverged reference, significant imaginary mode with no confirmed minimum, dissociation/changed connectivity, wrong charge/state, or a reproducible local geometry inconsistency that prevents the initial model from being released. Failed calculation quality is kept separate from a valid calculation demonstrating parameter failure.

## Task 2: electrostatics and water

PASS for the initial charges only after Sol High inspects all orientation-specific QM/MM interaction energies, distances, favorability and ordering, O1/O2/O3 symmetry checks, local ESP residual maps, preserved -1 total charge and equivalent O charges. The initial model must give a coherent favorable O-donor-water response and local electrostatic pattern across SO3 and the C1/C2 junction. Published CGenFF water deviations are context for judgment; no arbitrary ESP RMS, single-water energy threshold, neutral dipole multiplier, membrane result or ROS result is an automatic PASS gate.

REVIEW: diffuse-basis sensitivity changes the relative orientation ordering or magnitude enough to alter the charge judgment; a minimum lies at a distance-grid endpoint; an O-equivalence mismatch appears; MM has a systematic energy/distance or local-ESP bias; or the primary sulfur-water reference protocol gives conflicting signals. Sol High must adjudicate the QM reference and whether a CGenFF-compatible charge refinement is justified. The primary and diffuse results remain separately reported.

FAIL for the initial charge model: valid, replicated targets show qualitatively wrong favorable/unfavorable response or incompatible local charge distribution that cannot be reconciled while retaining -1 total charge, O equivalence and the fixed CGenFF topology. Invalid dimer fragments, counterpoise setup, water geometry, or charge bookkeeping fail data integrity and stop interpretation.

CHARGE_ACCEPTANCE_LOGIC = ACCEPT if all target classes support the present charges; REFINE_WITHIN_CGENFF_METHOD if a specific reproducible defect has a consistent charge-based remedy; BLOCK if the reference itself or required compatibility constraints are unresolved. The reviewer alone selects among these after seeing results. No RESP replacement, LJ edit, automatic fitted charge or membrane-based target is permitted.

## Task 3: C1-C2 axis

PASS for the initial torsion model: QM and frozen CGenFF adiabatic scans identify the same low-energy conformer basin and ordering, minima lie within the 30-degree sampling resolution (with geometry inspected), relative minima energies and low barriers are acceptably aligned, and reverse-seed checks reproduce the same branch. Compare full profile shape and barrier location, not only the highest barrier. The CGenFF emphasis on states within 5 kcal/mol of the QM minimum is a weighting priority, not permission to hide other points.

REVIEW: one-grid shift, changed ordering among near-degenerate minima, sizable barrier/profile discrepancy, scan discontinuity or reverse-seed hysteresis. Sol High may request a narrowly justified refinement plan. Do not automatically optimize the 122.9-penalty Fourier components.

FAIL for initial torsion release: valid QM/MM comparison gives a wrong global low-energy basin, severe relative-minimum inversion or qualitatively incorrect low-energy barrier/profile that would bias conformational populations. A failed QM optimization instead fails data integrity and stops the comparison.

## Task 4: C2-S1 axis

PASS for the initial torsion model: the 0-110-degree unique profile and 120-degree closure reproduce the O-permutation equivalence, both QM and MM identify the same low-energy pattern and acceptable barrier/relative-minimum behavior, and reverse seeds agree. Compare O1/O2/O3-permuted geometries, not raw atom-label RMSD.

REVIEW: closure energy/geometry mismatch after O permutation, unexplained break in 120-degree periodicity, hysteresis, ambiguous low-energy ordering or material QM/MM profile discrepancy. Sol High must resolve the symmetry interpretation before any fit.

FAIL for initial torsion release: valid data violate the required SO3 permutation symmetry under the fixed topology, or the initial MM model qualitatively misrepresents the validated low-energy surface. Invalid constraints or atom mapping fail data integrity first.

## Cross-target decision

A high CGenFF penalty is only the reason to test a term. If geometry and water/ESP pass and only one torsional axis fails, the minimal subsequent proposal is local torsion refinement; already adequate charges and bonds/angles stay as assigned. If charges require change, any separate approved fit must preserve total -1 and O equivalence, target CGenFF-compatible water interactions plus ESP, and recheck geometry and both torsion profiles. If bond/angle or torsion values are proposed for change, the affected target and coupled targets require a new Sol High review. No parameter value changes automatically. No membrane insertion, occupancy, cardiolipin contact, ROS or Damião diffusion value is a parameter acceptance target.

Four task families are the baseline minimum. A fifth tail-only scan is considered only if a concrete tail-specific discrepancy emerges in the baseline results and Sol High approves the added target. PFOS/PFHxS transfer is conditional on independent same-CGenFF-5.0 outputs, exact local SO3-CF2 mapping, matching atom types/charges/bonded terms and separate static audit of added chain terms.

STOP/ESCALATE_TO_SOL_HIGH on missing parameter, force-field conflict, unknown warning, nonconvergence, unexpected chemistry, protocol ambiguity, scientific ambiguity, numerical failure, provenance failure, or a failed symmetry/consistency gate. Luna has DESIGN_AUTHORITY=NO and PARAMETER_EDIT_AUTHORITY=NO. Current status remains QM_RUN_AUTHORIZATION=NOT_GRANTED and MD_RUN_AUTHORIZATION=NOT_GRANTED.

Sources: CGenFF 5.0 https://doi.org/10.1021/acs.jctc.5c00046 ; original CGenFF methodology https://pmc.ncbi.nlm.nih.gov/articles/PMC2888302/ . The approximate 0.03 A/3-degree guidance and <5 kcal/mol low-energy emphasis come from original CGenFF methodology. Pilot orientation/scan grids and qualitative adjudication categories are prespecified here, not presented as published universal cutoffs.

