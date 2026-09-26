# Parameter bounds and regularization — prospective preregistration

NEW_PREREGISTERED_CRITERION. No fit is run or authorized here. Source CGenFF values are weak structural priors, not observations proving parameter correctness. Priors are centered on immutable v1, never the failed candidate. Penalties are provenance; they do not automatically select fields or weights.

## Allowed bounds

For a later scientifically released reduced set only:
- r0: source +/-0.020 nm, intersect positive physical range [0.10,0.25] nm. Source-centered prior scale0.010 nm. Bounds contain the previously demonstrated S-C residual correction while preventing unlimited compensation; they are outer guards, not proof a source-local Jacobian extrapolates that far.
- theta0: source +/-10 degrees, intersect [60,160] degrees. Prior scale5 degrees. This permits correction of the documented 3–7-degree biases without unbounded reshaping.
- Group lambda_CS or lambda_CC: [0,2], source1, prior scale0.5. Original positive amplitudes/ratios, phases and multiplicities remain fixed. These groups are diagnostic-only now; this prospective bound does not release them.
- If k fields later become independently supported after A+B curvature: source ratio [0.70,1.30], prior log-ratio scale0.20. Initially every k has exact source/source bounds and cannot move. The prospective30% envelope is a conservative capped curvature adjustment, not a historical tolerance; bound contact triggers review instead of expansion.
- UB exact source/source by default. Any later explicit release must meet all four user conditions and select only one identifiable field. Prospective cap for such a separately approved field: r13 source +/-0.010 nm OR kUB source ratio [0.80,1.20]; never both by default. Zero UB remains zero.
- Other theta0, all C-F equilibria, tail-shared/CF3 amplitudes, zeros, phases/multiplicities, charges/LJ, types/topology/exclusions/1-4 have exact source/source bounds unless a separately adjudicated reduced-block update explicitly changes scope. Current task does not do so.

Finite-difference diagnostic perturbations are exactly those in the frozen protocol; fitting bounds cannot enlarge the derivative stencil. A local J at source cannot validate the whole fitting box. Every eventual candidate needs independent nonlinear geometry/energy validation and source-bound local identifiability review.

## Objective and prior

For eligible parameters z=(p-p_source)/s_p (log ratio for an independently released positive stiffness), use L_total=L_data+lambda_R*mean(z_j^2). Only supported directions enter; unresolved null directions are frozen/grouped before optimization. Regularization cannot substitute for identifiability.

Prospective development-only lambda grid is {0.01,0.1,1,10}. No additional grid values, bound changes or heldout-driven weight choice. After the six 2D development QM points exist, use three internal development folds: leave one complete CC level (both CS30 and90 points) out each time. Existing geometry/curvature/1D development data remain training in every fold. Score excluded development points with the fixed2D energy/geometry metric; use the largest lambda within one standard error of the smallest mean fold score (standard error across three fold scores). If only one score is finite, folds fail QC, grouping/rank differs between folds, or no choice satisfies all development geometry/PES/no-compensation gates: STOP/REVIEW; no adaptive grid extension.

This is internal model selection using development data; the four prospective heldouts remain sealed and never select variables, weights, regularization, restarts, bounds or grouping. The one-standard-error preference explicitly favors smaller source deviations when predictive development performance is indistinguishable. The outer scientific no-compensation gates remain independent of penalized loss.

For a future optimization implementation, deterministic start is the source projected into the frozen reduced parameter subspace. Solver/restart budget needs its own exact launch/fitting authorization; this document creates none. One final candidate is frozen before heldout results are generated/exposed.

[Official SciPy least-squares documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html) supports explicit variable scaling, bounds and rank-deficiency cautions. These parameter ranges, prior scales, ridge grid and selection rule are new PFBS design choices, not values prescribed by SciPy or historical acceptance gates.
