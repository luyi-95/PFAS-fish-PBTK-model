# Existing criteria and remaining pre-fit decisions

The machine-readable table binds each rule to an included exact source. Historical rules retain their original scope. They do not automatically become new universal reparameterization tolerances.

Report29's focused 0.03 angstrom /3degree guidance is a **diagnostic trigger**, not an automatic optimizer target. Existing CC30degree resolution and CS O-permutation closure rules remain scientific comparison criteria. Low-energy5kcal/mol emphasis is a weighting priority; no point may be hidden. The old report26 proposed <=0.5kcal/mol pilot RMS value was not adopted as a frozen acceptance gate and is expressly excluded from automatic decisions.

The v8 terminal QC rule preserves valid constrained QM execution: actual C.02 step cap200 for future optimization, exact restraints, target angle error<=0.01degree, normal termination/convergence, matched SCF/MP2 evidence, graph/order/provenance, embedded archive/chk and formchk-on-copy evidence. This cap is inapplicable to a frequency-only job; it does not retroactively invalidate previously accepted sentinel results. Existing conservative contact thresholds flag REVIEW; they do not prove connectivity failure solely from a distance.

No frozen numerical rule was found for full Hessian/mode matching, A/B conformer-energy error, 2D prediction errors, prospective heldout errors, whole-chain geometry aggregation, parameter Jacobian rank, acceptable field uncertainty, weighting or regularization. Those entries are `CRITERION_NOT_PREVIOUSLY_FROZEN`. Pre-QM audit completeness can PASS while these protocol decisions remain REVIEW. They must be frozen independently before fitting/acceptance; this package supplies no invented replacement tolerances.

After future independently validated calculation data, Sol High must jointly adjudicate local/global geometry, meaningful imaginary modes/mode character, conformer ordering, low-energy basins/barriers, CC/CS symmetry and branches, mixed holdouts and nonbonded compatibility. A fit that improves geometry at the expense of PES, or PES at the expense of equilibrium geometry, fails the no-compensation requirement.

No new run, fitting or parameter adoption is authorized by the package or upload.
