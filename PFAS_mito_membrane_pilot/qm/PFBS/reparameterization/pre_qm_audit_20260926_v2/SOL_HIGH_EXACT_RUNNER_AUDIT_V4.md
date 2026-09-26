# Sol High exact-runner audit V4: REVISE

Decision: **REVISE** for runner SHA-256 73eba997304d7304b3826b8f8fcc295b768b14f3358fd8f9337eb60cf6fe7ede and offline test SHA-256 e2e4affbeffd024c7c19879180149aa8dfdae2dffcc4218d9e2ed609c9b36b6f. Exactly one new grompp/dump-only preflight is **not approved under this exact runner**. Full MM matrix remains blocked. No GROMACS, minimization, QM, fit, adoption or MD was invoked by this reviewer.

## Resolved V3 checks

The revised comparator resolves active iatoms through their functypes and compares canonical per-instance coefficient tuples. On the real preserved BASE dump it parsed 120 active instances: 16 bonds, 30 Urey-Bradley angles, 38 proper-dihedral terms and 36 LJ14 instances; the complete LJ table has 46 entries. The ten target maps match the preregistered counts 3,1,2,1,3,3,1,3,9,5. Shared baseline functype40 maps bonds (14,15), (14,16), (16,17); distinct perturbation targets cover the first two or last one. The CC torsion group resolves five occurrences (two F-C-C-S plus n=1/2/3 on the same C-C-C-S atom quartet); CS resolves nine O-equivalent occurrences. These were independently read from the real BASE dump and frozen manifest, not inferred only from test fixtures.

Running python -B executor/tests/test_active_instance_semantics.py completed six tests successfully in 0.037 s. Valid shared-type splits pass; changing all three bonds, one-sided A/B, wrong endpoint, other active bond/UB/proper/LJ14/LJ_SR, atom/type/charge/mass/exclusion/graph/setting, and torsion phase/multiplicity changes reject in synthetic fixtures. The same-DP historical reference hashes/bindings and source/prereg hashes remain fixed. Current code still uses the frozen 41+21 states, 28 starts, double binary, 10 nm/2 nm physical settings, LBFGS->CG 30,000/30,000 emtol1 or0.1, unchanged ±h/±2h, grouped proportional amplitudes, and restraint-free physical rerun. No science variable or job count changed in the inspected code.

## Blocking real-dump comparison defect

The new _topology_semantics.outer compares every line outside the topology block verbatim. Two **actual archived double-precision preflight dumps** from the same accepted source and source structure disagree outside topology in three nonphysical fields:
- generated inputrec ld-seed: BASE -119019618 vs R_CG312-SG3O1_-1h -1342717957;
- the GROMACS dump footer Working dir path, reflecting the distinct state directory;
- the GROMACS reminds you footer quotation.

The BASE dump SHA is 3dbaac64e638f2ed1d5b267bc11174a8b02560274be9d2873a293e75695013ee; the read-only copied perturbed dump SHA is c6170f5a3df89dc12d9999c9466ae2a2ac50f3ad90416093e496813f1b60e4fe. The outside-topology portions each contain269 lines; a direct diff found only those three differences. The actual physical TPRs use integrator=md,nsteps=1 with gen-vel=no, tcoupl=no, pcoupl=no, and no stochastic integrator. Here ld-seed is unused generated metadata. The footer directory and quotation are command-output metadata. Consequently, this runner will falsely reject a correct perturbation before its active-instance checks, despite the six synthetic tests passing. The test fixtures do not model these generated fields.

## Exact mechanical correction

Keep full, exact effective inputrec physics settings, x/v coordinates, box, processed-MDP physical configuration, source/TPR hashes, atom/exclusion/nonbonded and canonical active-instance checks. Normalize **only**:
1. generated ld-seed when the current physical-evaluation TPR is demonstrably nonstochastic (integrator=md, nsteps=1, gen-vel=no, tcoupl=no, pcoupl=no; check any relevant stochastic mode in the effective inputrec/processed MDP); otherwise compare it exactly or STOP;
2. the post-dump-banner Working dir path;
3. the post-dump-banner GROMACS reminds you quotation and its final blank footer line, if present.

Do not broadly ignore headers, inputrec rows, coordinates, velocity/box blocks, errors, warnings, executable/version/binary identity, or any other line. In these actual dumps the leading physical.tpr header, Executable, Data prefix, Command line, version, and reading-file lines agree and should stay checked. Bind any excluded metadata raw text/hashes in the report.

Add offline regressions with actual-format dump fixtures: an unused generated ld-seed plus the two listed footer differences must pass; a seed change in a used stochastic or velocity-generation context must reject; mutation of rlist/coulomb/vdW/modifier/cutoff or x/v/box must reject; all V3 per-instance and torsion tests remain. Then bind a new exact runner/test hash for independent approval before the one allowed grompp-only attempt.

MVP_ROUTE_STATUS=PENDING. FULL_MM_MATRIX_STATUS=BLOCKED. NEW_QM_LAUNCHED=NO. PARAMETER_FIT_OR_ADOPTION=NO. MD_RUN=NO.
