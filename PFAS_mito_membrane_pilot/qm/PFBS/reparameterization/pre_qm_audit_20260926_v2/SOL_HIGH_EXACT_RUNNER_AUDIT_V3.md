# Sol High exact-runner audit V3: REVISE

Decision: REVISE. Runner SHA-256 766cb61700921e888e6b8b4060d0b316c2da2bd2e8444fd217848d8de8e9caa3 is **not approved for the next preflight or MM matrix**. No engine was invoked in this review.

## What passed

The approved same-precision formal-DP comparator is now named and hash-bound: baseline TPR 6f608585ecc607220692fbe875b4e07000c64d14bb5093c5af7130367ca7adc4, historical dump 2ec1f2360523c920d1f4c60f915f355300cb5a04ff0d20874dfa765d23f8600b, binding 96e04470e77a4f48ee34c99005fb7c7d75b91b52223357590de0ec79c6f35b07, historical run record f0eba98150199209e89b64744c29f012fdf68a3b5a0919001594ff0460096084, same gmx_d SHA 910c195c43f12f35e44ff5ccfdafd3236bf86c6afb0774b550e0ccb5d5148c2d and original ITP/PRM hashes c736e8e20ee778fd64dfc2b95da13040b6a49404c78dc1cf46dd7368b016aeca / 24baf41553845380e9905f7419ca85cb0528dcd7652d596ca6ba83e003d05a56. Its exact 15,595-line baseline topology signature matched the new DP BASE in the preserved failed attempt. The old mixed-reference failure remains preserved.

The authorized-field masking correction now checks both A and B fields against the preregistered endpoint and compares the complete remainder of each changed functype row. Frozen numerical constants and execution path observed in this script remain the ten manifest variables, primary/audit tolerances 1/0.1, LBFGS/CG 30,000, emstep .001, 10 nm box/2 nm cutoff, 500000 scan restraint, double binary, and restraint-free physical rerun. The exact old runner bytes are not locally available for a line-by-line change-only diff; this statement is a static check of present constants/code, not a complete file diff proof.

## Blocking active-instance semantic bug

The original DP BASE encodes three distinct active bonds with **one** functype[40], because two source type families have equal coefficients (b0=.14563 nm, k=227869.01 kJ mol^-1 nm^-2). Actual 0-based Bond iatoms records are (13,14), (13,15), (15,16), corresponding to 1-based (14,15), (14,16), (16,17). The frozen R_CG312-CG312 perturbation must affect the first two only; R_CG302-CG312 must affect the last one only.

The current tpr_parameter_diff compares functype indices and insists the whole functype inventory and all non-functype topology lines stay byte-identical. A legitimate perturbation splits the shared baseline coefficient into two active types and may renumber subsequent indices. The checker can reject that valid result. Worse, a synthetic in-memory change to functype[40] A/B b0 alone, which would alter **all three active bonds**, was accepted for either R_CG312-CG312 or R_CG302-CG312. This is a false pass of off-target physics. The same pure-function static test accepted an ordinary isolated S-C perturbation, confirming that the issue is the shared baseline functype. No TPR was generated or mdrun called for these tests.

## Required narrow mechanical repair

Canonicalize the **active interactions**, not raw functype indices. Resolve each active iatoms record through its referenced functype, compare baseline vs perturbed by (interaction class, actual atom-instance tuple, occurrence/multiplicity/phase where relevant) and per-instance full coefficient tuple. Keep atom identity/types/charges/masses, exclusions, LJ_SR/LJ14/1-4, all other bonded and UB scalars, active interaction multiplicities/counts, and physical restraint absence exact. For each variable, require exactly its preregistered atom instances and only its named scalar A/B field to move by the exact ±h endpoint; verify all other active instance coefficients unchanged. Equal-amplitude torsion source families may share a functype; prove all nine CS instances and the exact grouped CC instances rather than inferring scope from one numeric row. A split/renumber of the internal functype table is acceptable only when that complete per-instance comparison passes. Do not loosen endpoint value checks or change parameter/physics inputs.

Static regression cases required before new preflight:
1. Both valid split directions from the shared baseline type40: change (14,15)+(14,16) only, and change (16,17) only; reject changing all three.
2. Reject a one-sided A-only or B-only target change, and reject wrong step/amplitude ratio.
3. Reject an extra active bond, angle/UB, proper, LJ14 or LJ_SR mutation.
4. Reject an atom/type/charge/mass or exclusion mutation and any altered interaction count/instance graph.
5. Reject proper-torsion multiplicity or phase changes; verify O-equivalent CS instance coverage and CC group coverage.

These are offline comparator tests; they do not authorize an MM parameter candidate. After code correction, bind the new runner hash and re-review before the single previously approved grompp/dump-only attempt. That attempt and the full matrix remain blocked under this exact runner.

NEW_QM_LAUNCHED=NO. MM_MDRUN=NO. PARAMETER_FIT_OR_ADOPTION=NO. MVP_ROUTE_STATUS=PENDING.
