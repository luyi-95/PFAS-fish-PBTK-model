# CC profile shape review (first-order diagnostics only)

The accepted QM profile places its global minimum at `T_CC_300`; the current MM profile places its global minimum at `T_CC_180` (relative MM energy at CC180 = −2.6526 kcal/mol with CC300 as zero; QM `E180−E300` = +0.9906 kcal/mol). The signed basin-order defect is +3.6431 kcal/mol.

The sole supported normalized CC response direction is:

`CC_FOURIER_1 = 0.794968842142; CC_FOURIER_2 = −0.567158662075; CC_FOURIER_3 = −0.214917656479; CC_FOURIER_4 = −0.012883826682`.

The sign `supported_svd_1_minus` is the local direction that improves the CC180/CC300 ordering. At the frozen guard-feasible bound `t=2.515821871`, the first-order gap movement is +3.117813992 kcal/mol. This leaves `E180−E300≈+0.465249387 kcal/mol`, short of the QM gap by ≈0.525332363 kcal/mol. The frozen upper-gap test therefore classifies leverage `INSUFFICIENT`; do not extrapolate or call this a successful correction.

At this bounded first-order screen, CC300 becomes the lowest sampled grid point. Existing sampled local minima at CC060, CC180 and CC270 remain, so the screen does not establish full torsional-shape agreement or validate barrier locations/heights. No additional sampled minimum is introduced by the linear screen. This is a local directional diagnostic, not a parameter candidate and not a nonlinear re-minimization.

The neighboring low-energy gaps move in mixed amounts; only the CC180-vs-CC300 direction is clearly identified as the primary basin-order target. The direction has high overlap with the supported geometry response space (maximum principal-angle cosine ≈0.719; report-only category `HIGH`). Thus the CC response is not cleanly separable from geometry response, despite passing the preregistered local geometry endpoint bounds. Profile shape verdict: `CC_PROFILE_SHAPE_STATUS = REVIEW`.

Do not use the separately favorable 25-row PES-only rank 4 as a rescue: it excludes the full primary geometry/support domain and cannot replace the 118-row primary result. The 119-row CC240 branch extension remains diagnostic only and does not rescue primary rank.
