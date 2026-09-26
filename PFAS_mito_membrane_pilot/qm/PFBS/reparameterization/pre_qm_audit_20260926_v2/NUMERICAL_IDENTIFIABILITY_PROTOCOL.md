# Numerical MM identifiability protocol — preregistration V2_01

Status: PREREGISTERED_BEFORE_DERIVATIVE_RESULTS. NEW_PREREGISTERED_IDENTIFIABILITY_CRITERION applies to every new numeric rule below. This document and MM_IDENTIFIABILITY_VARIABLE_SPEC.json authorize the design only; root/executor verify the exact candidate, source hashes and implementation before running. No fit or candidate solve is permitted.

## 1. Minimal initial hypothesis

Ten diagnostic variables: four eligible type-wide r0 values, four theta0 values, two grouped proper-amplitude scales. INITIAL_DIAGNOSTIC_VARIABLES.tsv and JSON are the exact machine definition, including source values and all affected atom instances. This is not the final numerically adjudicated REDUCED_PARAMETER_BLOCK_V1.

The equilibrium block is deliberately smaller than all v1 eligible fields:
- Four bond families cover SO3, S-C2, both type-shared C1-C2/C1-C3, and terminal C3-C4.
- Four angular representatives cover the distinct persistent SO3 opening, CF2 F-C-F opening across all three centers, damaged S1-C2-C1 junction, and CF3 F-C-F opening. Their type families are OG2P1-SG3O1-OG2P1; FGA2-CG312-FGA2; CG312-CG312-SG3O1; FGA3-CG302-FGA3.
- Complementary C-S-O and C-C-F equilibria remain frozen initially because tetrahedral geometry relates their response to the selected opening directions. This is a parsimonious hypothesis, not proof they are redundant. All their instances remain measured; failure to preserve them stops the reduced model instead of secretly adding fields.
- FGA2-CG312-SG3O1 and CG302-CG312-FGA2 have smaller original errors; C2-C1-C3 was already reasonably reproduced. Tail C1-C3-C4 and complementary CF3 angles remain guards/CONDITIONAL_AFTER_HESSIAN. The whole-chain audit remains mandatory.

CS amplitude diagnostic: multiply both source n=3 SG3O1-OG2P1 families by one lambda_CS, preserving their source ratio and all equivalent-O instances. CC diagnostic: one lambda_CC multiplies the four SG3O1-specific nonzero rows (FGA2...SG n1 plus CG312...SG n1/n2/n3), preserving their source ratios. These are minimal directional tests of amplitude-versus-equilibrium confounding, not an assertion that one amplitude scale can reproduce a complete PES. Shared tail families, all zero amplitudes, phases and multiplicities remain untouched. If these two directions are insufficient, record the limitation; do not infer that every possible torsional combination is identifiable.

## 2. Exact perturbations and numerical execution

Every variable gets -2h,-h,+h,+2h from the original source independently:
- Bonds h=0.001 nm; normalization parameter scale s_p=0.01 nm.
- Angles h=1 degree; s_p=5 degrees.
- Group lambda h=0.05; s_p=0.5, source lambda=1.

These steps are small relative to source values, materially below the observed geometry defects, and large enough to test explicit convergence noise. Their adequacy is tested, never assumed. No step adjustment is allowed after outcomes. The same four endpoints are required even if the first pair appears favorable.

Primary numerical plan, newly preregistered: verified double-precision executable; LBFGS30000 -> CG30000, emtol1 kJ/mol/nm, emstep0.001 nm. Convergence audit: baseline and +/-h for every variable, same two-stage protocol at emtol0.1. All states start independently from the accepted QM source; only LBFGS->CG transfer within the same state is allowed. Stage precision, input/TPR semantic diff, real final Fmax and raw convergence evidence must be recorded. No state-to-state parameter continuation.

There are41 primary parameter states and21 convergence-audit states, each assessed on A, B,25 absolute profile structures and the retained CC240 branch diagnostic:28 starts/state. This is a bounded preregistered MM-only diagnostic set, not62 fitted candidates. No Gaussian/formchk/MD is allowed.

Preserve exact approved physical settings, atom graph, charges/LJ, types, exclusions/1-4 and existing profile-restraint semantics. A/B remain unrestrained. Keep isolated10nm box/2nm cutoff; verify all-pair geometry remains in the intended isolated interaction domain. All stiffness and UB remain frozen. The sole historical exact LBFGS cutoff-efficiency warning may retain its previously reviewed one-warning exception if its complete text/count/source binding matches; all other unapproved warnings STOP. Do not change cutoff/switch/PME physics for numerical convenience.

[Official GROMACS energy minimization documentation](https://manual.gromacs.org/documentation/current/reference-manual/algorithms/energy-minimization.html) supports the force-based convergence interpretation and the cutoff-history concern. The particular1/0.1 force tolerances are new design choices, not historical fit gates. DP full-precision outputs are required.

## 3. Observable vector, normalization and independence

Raw rows include A/B all16 bond lengths in Angstrom and all30 valence angles in degrees;25 constrained-profile physical energies in kcal/mol relative to CC300 within the SAME parameter state; and E_B-E_A. Store all136 A/B pair distances, achieved constraints, proper dihedrals, graph/O-equivalence/whole-chain geometry, and CC240 branch energy/full geometry as diagnostics. Diagnostic pair rows are not included in the primary SVD because they duplicate internal geometry information.

Energy must remove the restraint-potential contribution and preserve one common CC300 anchor for both axes. No per-axis recentering, fitted energy offsets or omission of high-energy rows. No water/ESP bonded-fit rows.

J_raw(i,j)=[O_i(p+h_j)-O_i(p-h_j)]/(2h_j). J_2h uses4h_j in the denominator. J_norm(i,j)=w_i*J_raw(i,j)*s_pj/s_Oi.

Observable scales: bond0.03 Angstrom, angle3 degrees, energy1 kcal/mol. Historical0.03/3 guidance is used here only to choose readable dimensionless units; it remains diagnostic, not a universal optimization tolerance. Energy1 is a preregistered unit-scale convention, not a pass threshold or a measured QM error bar.

Each class block has total squared row weight1:
- Bonds: A/B equal; six source type families equal; instances equal within family. w=1/sqrt(2*6*n_family).
- Angles: A/B equal; eleven families equal; w=1/sqrt(2*11*n_family).
- PES: CC and CS half each, points equal within axis; w=1/sqrt(2*n_axis), with n_CC=12,n_CS=13.
- AB energy row w=1.
Weights/scales are fixed before outcomes. Shared reference induces correlated energy errors; covariance below is a sensitivity proxy, not a claim of independent statistical samples.

## 4. Noise, step reproducibility and rank

[Official SciPy derivative implementation](https://github.com/scipy/scipy/blob/main/scipy/differentiate/_differentiate.py) describes the second-order central formula and derivative-difference error estimate. This protocol fixes both step sizes in advance and uses a conservative envelope rather than adaptive step tuning.

For each normalized column:
R_step=||J_h-J_2h||/max(||J_h||,||J_2h||) must be<=0.10.
R_conv=||J_h-J_h_tight||/max(||J_h||,||J_h_tight||) must be<=0.05.
A zero/uncertain signal is UNIDENTIFIABLE; do not create a denominator floor that makes it pass. The10%/5% budgets require step/convergence changes to be a small fraction of the observed signal; they are new conservative quality rules, not physical acceptance thresholds.

Elementwise uncertainty E_ij=abs(J_h-J_2h)+abs(J_h-J_h_tight)+arithmetic-roundoff bound. Keep the whole difference; no Richardson division or optimistic cancellation. Arithmetic bound is derived from endpoint rounding/serialization precision and binary epsilon, propagated through subtraction/division/scaling. Exact raw numeric strings and energy precision must be kept. delta=||E||_F upper-bounds its spectral norm, but is an empirical uncertainty envelope, not a rigorous truncation-error theorem.

Report full singular values/vectors, raw and scaled condition numbers, and machine-only tolerance max(m,n)*epsilon*sigma_max. Effective supported rank uses sigma>5*max(delta,machine_tolerance). A perturbation of size delta can change a singular value by at most delta; the5delta margin limits inverse-direction amplification delta/(sigma-delta) to0.25. This is a newly preregistered conservative stability margin. A formally nonzero singular value below this margin is not counted as practically supported.

For supported directions report C=V diag(1/sigma^2)V^T, correlations and sqrt(Cjj). C assumes unit dimensionless response perturbations solely to compare parameter sensitivity; it is not a statistical covariance or confidence interval. Unique-parameter support requires sqrt(Cjj)<=1 parameter-scale unit plus stable supported directions. Report unresolved null components rather than replacing their variance with a pseudoinverse zero. Highlight |v_j|>=0.25 in null vectors only for readable reporting; all coefficients must remain available.

Classify each variable/group:
- IDENTIFIABLE: stable supported direction, finite unit-noise proxy<=1 and appropriate independent observable block support.
- WEAKLY_IDENTIFIABLE: stable nonzero response but insufficient uncertainty/independent support or proxy>1.
- COLLINEAR_GROUP: an unresolved joint direction involves multiple parameters; do not independently release its members. Correlation alone is not proof.
- UNIDENTIFIABLE: signal cannot be distinguished from noise, invalid branch response, or no supported information.

Report geometry-only, PES-only, A-only geometry, B-only geometry, remove-bonds, remove-angles, remove-CC, remove-CS and remove-AB checks. Use identical fixed weights restricted to the retained rows; do not renormalize after deletion. Full block support is necessary. Geometry parameters require geometry support; amplitude directions require PES support. Every subset need not be full rank: loss of a physically relevant block reveals where information originates. A/B conflicting sensitivities or a direction supported solely by shared-reference redundancy remain REVIEW.

Any graph/branch change makes a smooth finite derivative invalid for those rows. Preserve the data, stop the affected direction, and adjudicate PARTIAL/FAIL. No extra steps, extra amplitudes, tighter unplanned minimization or second candidate solve is allowed as a favorable-rank rescue.

## 5. Final reduction after results

Scientific reviewer, not executor, freezes REDUCED_PARAMETER_BLOCK_V1.tsv after inspecting source-bound numeric results. RELEASE/GROUP/FREEZE/CONDITIONAL_AFTER_HESSIAN must be explicit for all v1 candidates. Prefer fewer variables; no least-squares fit is authorized in this task.

Identifiable initial equilibria are only eligible for later release, not adopted. Diagnostic torsions remain diagnostics until curvature/sequencing review. All k remain CONDITIONAL_AFTER_HESSIAN. UB remains FROZEN unless all four user conditions are met. Tail/CF3 amplitudes, phases/multiplicities, zeros, charges/LJ and topology stay frozen.

Failure is an acceptable scientific result: it stops new QM escalation under the user's hard stops. Rank alone cannot make FIT_READY=YES.
