# Preregistered branch and restraint classifier addendum

NEW_PREREGISTERED_IDENTIFIABILITY_CRITERION. No derivative outcomes used. This operationalizes the frozen requirement to reject discontinuous branch responses; no variable, perturbation, numerical minimization or scale is changed.

## Baseline and symmetry

For each accepted start, first establish its original-parameter relaxed MM baseline. Compare parameter states to that baseline, not directly to the pre-relaxation QM label. Record QM->baseline change separately. A/B or CC240 source labels may collapse to one baseline basin; then their information is duplicated and cannot be declared independent.

Build automorphisms preserving graph, types, charges, bonds/angle/proper parameter semantics and any active restraint atom mapping. For a CS restraint O1 must remain the restrained O atom unless an exact simultaneously transformed restraint proof exists; no silent O swap at fixed external restraint. Record full permutation and original labels. No nominal120 or n-fold proper phase fold substitutes for an actual atom-equivalence permutation. Use circular360degree differences on physical dihedrals; +/-180degree wrapping is not a branch jump.

## Smooth-local-domain diagnostic

Enumerate unique original ITP geometric proper quadruplets (Fourier duplicates counted once). For every parameter direction, include all +/-h,+/-2h and its tightened +/-h states. Exclude proper quadruplets whose central bond is the active restrained scan bond from the unrestrained response vector, but record their achieved angles separately.

For each permitted symmetry map, calculate the largest absolute wrapped360degree unrestrained-proper change across ALL that direction's states versus the baseline. Choose the single map minimizing this maximum, with lexicographic atom-index tie-break. The same map is used for all endpoints; do not independently remap signs/steps to hide a discontinuity.

Pass smooth-domain gate only if this minimax change<=30degrees and all source/graph/convergence gates pass. The30degree cap is a NEW local-response screen, not a historical basin identifier. It permits small continuous relaxation while flagging a rotamer-sized response; it does not prove a basin is unique. Above30 record BRANCH_OR_LARGE_ROTAMER_RESPONSE_REVIEW and invalidate smooth derivative interpretation for affected rows/direction. Preserve data, reviewer adjudicates PARTIAL/FAIL; no unplanned probe, map change, larger threshold or automatic restart rescue.

Report the complete torsion change vectors, chosen map, maximum-defining quartet/state, and full coordinates/pair geometry. Manual scientific reading can identify why the gate failed, but cannot retrospectively waive the preregistered smooth-domain gate to declare rank PASS.

If no unrestrained geometric proper remains, mark domain check NOT_INFORMATIVE; do not claim automatic independent support. Degenerate/undefined dihedral geometry or inconsistent mapping STOP.

## MM constraint readback

Historical phase3 QM achieved-angle gate remains<=0.01degree for valid QM source jobs. This is not automatically an MM minimization tolerance. Existing v1 MM profile maximum scan drift was0.0127971352degree; source profile records it explicitly.

For this new MM sensitivity preflight, preregister absolute scanned-angle drift<=0.020degree versus its exact accepted QM restraint center, using wrapped360difference. This NEW_MM_SPECIFIC_IDENTIFIABILITY_QC criterion is fixed before new MM outcomes, just above the preserved original maximum and tiny relative to CC30/CS10sampling. It is a constrained-observable-control gate, not a relaxed QM acceptance rule. No force/restraint adjustment is permitted to make it pass. Each failed row is invalid for its derivative block; preserve result and STOP affected direction.

Unrestrained A/B have no scanned-angle gate. Profiles retain the same source restraint settings and subtract only the actual restraint energy. A common-reference drift/error and branch evidence remain explicit in J uncertainty review.
