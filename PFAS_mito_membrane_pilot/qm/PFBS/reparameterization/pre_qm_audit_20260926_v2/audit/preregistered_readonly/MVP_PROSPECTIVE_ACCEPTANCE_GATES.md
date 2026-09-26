# MVP prospective qualitative acceptance gates

NEW_MVP_PREREGISTERED_CRITERION. Fixed before any new repair fit or pilot result. These gates supplement MVP_SCOPE_OVERRIDE_AND_RED_FLAG_FRAMEWORK.md and supersede automatic use of full-broad accuracy budgets for the current intended-use question. Numerical derivative/noise gates remain unchanged.

## Geometry: major-defect screens and no compensation

Always flag broken graph/identity, chemically implausible bonds/contacts or atom-type/charge mismatch. For preserved source geometry compare both A/B, each instance and the same equivalent-atom mapping.

New major-geometry screening budgets:
- any heavy S-C or C-C backbone bond absolute fractional QM error>5%;
- any heavy-backbone valence angle C-C-C or S-C-C absolute QM error>6degrees;
- same mapped low-energy state acquires a chemically implausible contact/topology change under one model.

Five-percent backbone strain is substantially beyond historical approximate bond diagnostics for these1.5–1.9Angstrom bonds;6degrees is twice the historical3degree angular guidance and protects head-tail bending. These are newly chosen intended-use screens, not empirical membrane-effect thresholds or universal CGenFF gates. A flag calls for a focused explanation/repair; it does not by itself prove broad reparameterization is necessary. The preserved failed candidate's improvement of bonds while worsening the junction remains explicit evidence of compensation.

All bonds/angles/head/tail/pair geometry remain reported. Smaller residuals, complementary F-C-F discrepancies or full-spectrum defects do not independently drive more QM unless a specified intended-use structural consequence is demonstrated. Do not declare major flags NONE by hiding a >budget backbone defect. A focused exception, if ever scientifically justified, requires a new prospective version and actual relevant evidence before future validation; there is no exception now.

No compensation: a major flag cannot be removed by creating another major geometry flag, losing relevant low-energy states, changing graph/charges/LJ, producing a spurious low well or invalidating stability. This qualitative gate replaces automatic application of full-broad tiny-regression budgets; it does not waive physical integrity or the previously failed candidate.

## Dominant low-energy CC/CS behavior on existing evidence

Preregister a qualitative low tier as sampled QM energy<=1.0kcal/mol above that axis's lowest retained QM value. Report the entire profile and source uncertainty/branches, but use this newly chosen tier to test dominant rather than exhaustive high-energy agreement. It is a pragmatic low-conformer comparison budget, not a thermal probability or historical threshold.

CC qualitative consistency:
- MM's lowest retained sampled state lies within one CC grid step (30degrees) of a QM low-tier minimum under valid full atom-equivalence/parity mapping;
- no MM low minimum outside those neighborhoods is favored by>1.0kcal/mol relative to the best supported low-tier neighborhood;
- any branch/source ambiguity remains UNRESOLVED rather than falsely unique.
Current QM300 versus MM180 is a directly observed qualitative problem on the retained grid; do not call the grid an exhaustive isolated/global/condensed-phase free-energy surface.

CS no major artifact:
- MM low minimum within one CS step(10degrees) of a retained QM low-tier minimum, with actual achieved-angle/O mapping;
- no unsupported CS well outside the low-tier neighborhoods is preferred by>1.0kcal/mol;
- SO3 graph/contact/periodic relabelling remains valid; no branch disappearance mislabelled as exact120degree equivalence.
Full CS high-energy barrier mismatch alone does not fail MVP; an altered low-state accessibility/identity or obviously spurious trap needs a specified relevance argument.

The1.0kcal budgets and grid-neighborhood rules are NEW_MVP_PREREGISTERED_CRITERION chosen before repair results. They permit modest shape/high-energy approximation while rejecting a strongly wrong dominant low-conformer preference. They do not establish accurate conformer populations, PMFs or kinetic barriers.

## A/B stable enough: limited evidence claim

Existing MM evidence can establish converged, source-bound, graph/contact-preserving relaxation and reproducible baseline branch behavior. Convergence at small Fmax does not alone prove dynamical stability or a complete minimum classification. A/B merging under original MM is recorded as reduced information; it is a major flag only if it erases an intended-use relevant low-tier state or produces an implausible structure/trap.

Before future final adoption require the separately authorized pilot evidence below. Do not require full45-mode agreement or B frequency merely because it is absent; B curvature is warranted only for a specific major relevant ambiguity.

## Pilots and final adoption

SHORT_WATER_PILOT=NOT_RUN_NOT_AUTHORIZED.
SHORT_MEMBRANE_PILOT=NOT_RUN_NOT_AUTHORIZED.

A future pilot exact protocol must specify duration, conditions, source model, comparisons and artifact criteria BEFORE launch. Pilot PASS must mean no observed parameter-induced chemically implausible head/tail/graph/contact or obvious membrane/water structural artifact within those actual conditions. Absence of an observed artifact over a short pilot is bounded evidence; it does not validate absolute binding free energy or transferability.

These current files do not invent a pilot length, outcomes or authorization. Pilot design/execution remain a later user decision, so PFBS_PARAMETER_STATUS cannot yet be ACCEPTED_FOR_INTENDED_SUPPORTING_MEMBRANE_MD_WITH_CAUTION.

If all major screens/qualitative low-basin/stability/pilot conditions pass for a separately authorized repaired model: assign that cautious intended-use status and STOP further refinement. No numerical elegance/full2D/high-energy/spectral residual can extend refinement without a demonstrated intended-use effect.
