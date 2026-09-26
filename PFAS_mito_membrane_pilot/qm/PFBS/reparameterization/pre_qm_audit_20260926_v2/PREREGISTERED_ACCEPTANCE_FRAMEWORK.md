# Preregistered joint fitting and validation framework

Status: PREREGISTERED_PROSPECTIVELY; no fitting or new QM performed. New numeric criteria are explicitly NEW_PREREGISTERED_CRITERION. Current FIT_READY=NO. This framework is not an authorization to fit or expand the diagnostic variables.

## Roles and provenance

HARD_QC_GATE concerns valid source/method/state/atom map/runtime/numerical data.
FIT_OBJECTIVE concerns development-only joint residuals and source priors.
DIAGNOSTIC reports historical guidance, branch/shape/uncertainty context.
VALIDATION_GATE tests a frozen model against prospective targets.
NO_COMPENSATION_GATE rejects material deterioration despite a lower aggregate loss.

Historical report29 approximate0.03 Angstrom /3-degree guidance remains DIAGNOSTIC. Historical5kcal/mol emphasis remains a priority; the new weighting factor below is separately preregistered. No former pilot0.5kcal aspiration is presented as a frozen rule. [Primary CGenFF protocol](https://pmc.ncbi.nlm.nih.gov/articles/PMC2888302/) motivates joint geometries/curvature/conformational energies; the specific numerical design below is newly chosen for PFBS and is not prescribed by that study.

## Hard integrity QC

Immutable v1 hashes, exact molecular graph/order/types/charge-1/multiplicity1, MP2/6-31+G(d), CHARMM-compatible potential and frozen nonbonded/exclusions/1-4 are mandatory. Source logs/checkpoints/hashes and actual effective inputs must be bound. Double-precision MM, declared converged Fmax, accepted-source independent starts, warning review and full physical interaction domain are required.

New Gaussian source must normally terminate, satisfy approved Tight geometry/SCF criteria where applicable, and preserve exact achieved constraint angles under existing phase3 gates. Frequency jobs need minimum classification with chemically meaningful imaginary modes absent; ambiguous roots or unclassified warnings REVIEW. No blanket A warning waiver for B. Nonfinite, missing, nonconverged, source-mismatched or branch-unresolved target is a QC failure, not a large loss value, dropped point, zero residual or permission to select another seed.

No invented QM values or prospective heldout outcomes exist in this package.

## Joint development objective

Use weighted squared residuals with block means; each development block has coefficient1:
1. A/B all16 bonds: source-family-equal weights, A/B equal, scale0.03 Angstrom.
2. A/B all30 angles: source-family-equal weights, A/B equal, scale3 degrees.
3. A+B projected curvature: each basin equal; relative projected-matrix residual scale0.20. Internal-coordinate/mode-character checks remain independent gates; raw frequencies are not individual k targets.
4. Existing CC/CS relative physical PES: common immutable CC300 anchor; axes equal. All points retained. QM-relative energy<=5kcal/mol receives new factor2 in squared weights; others factor1; renormalize within each axis. This fixed2 weighting expresses historical low-energy priority without hiding high energies.
5. Six new2D development points: equal weights, common CC300 anchor, energy scale1kcal/mol; each point's all16bond/30angle geometry joins corresponding fixed geometry class means.
6. Conformer E_B-E_A: scale1kcal/mol.
Add fixed development-selected source-prior regularization as preregistered in PARAMETER_BOUNDS_AND_REGULARIZATION.md. All grids/weights/groupings/bounds are fixed before future outcomes.

Whole-chain136 pair distances, proper rotations, O mapping and CC240 alternate branch remain full diagnostics/validation guards, not redundant independent fitting equations. The forward CC240 main point stays development; reverse branch stays excluded from numeric fitting.

## New geometry gates

For A and B separately and each valid development/heldout2D structure:
- all16bond family-equal RMSE<=0.020 Angstrom; all30angle family-equal RMSE<=2.0 degrees;
- every bond absolute error<=0.040 Angstrom; every valence-angle absolute error<=4.0 degrees;
- geometry all136pair-distance RMSE<=0.050 Angstrom; maximum pair-distance error<=0.150 Angstrom;
- correct graph, atom/O-equivalence mapping and retained basin/branch assignment.
These are NEW_PREREGISTERED_CRITERION. Aggregate targets are tighter than historical approximate diagnostic guidance, while individual caps allow ordinary shared-type/model approximation without concealing a damaged junction/tail. Pair guards capture global conformation missed by local metrics and are not used to claim extra rank.

Report selected local families, complementary frozen families, head/junction/tail regions, each instance and A/B separately. No pooling A/B to hide one failure. If unconstrained A/B MM collapse into the same basin, declare shared information: labels do not create two independent states. Assess whether distinct QM basins can actually be represented before calling the model adequate.

## New PES gates

For each CC/CS axis, common-anchor energies:
- all-point RMSE<=1.0kcal/mol, MAE<=0.75, max absolute residual<=2.0;
- QM-relative energy<=5kcal/mol subset RMSE<=0.50kcal/mol (all points still reported);
- barrier-height absolute error<=1.0kcal/mol;
- global/local minimum and barrier grid locations within one approved sampling step (CC30degrees,CS10degrees), with no extra/missing low-energy minimum whose depth exceeds0.50kcal/mol;
- basin ordering preserved for QM energy gaps>0.50kcal/mol; smaller gaps reported unresolved rather than forced ordering;
- discrete profile shape Pearson correlation>=0.90, calculated on all points; flat/undefined correlation REVIEW rather than pass.
All numeric gates are NEW_PREREGISTERED_CRITERION. The energy budgets are small compared with original multi-kcal profile errors/barriers; they are model-accuracy budgets, not QM uncertainty or experimental error bars. The0.50low-energy budget is newly adopted, not silently inherited from report26 aspiration.

Use discrete sampled extrema with circular adjacency (CC360 and conservative CS120 domains), include endpoints/closure and achieved angles. Do not infer continuous barrier positions from a grid or fit smoothing curves to make locations pass. CS O-equivalence closure is checked with full geometry mapping, not assumed exact from nominal120degree rotation. A source-periodic relabelled identical physical configuration must produce equal energy within numerical uncertainty; independent nonidentical optimized endpoint branches remain branch diagnostics.

Conformer E_B-E_A absolute error must be<=0.50kcal/mol; ordering is required when the QM A/B gap>0.50kcal/mol, otherwise report unresolved near-degeneracy. This is a NEW_PREREGISTERED_CRITERION for relative basin behavior, not an experimentally measured uncertainty.

## 2D development and prospective validation

Development loss: equal-point energy MSE and family-equal geometry MSE using the fixed scales above. Holdout evaluation of ONE frozen model uses the same physical energy zero, equal four-point weights and full geometry/QC rules.

New2D development and heldout energy gates: RMSE<=0.75kcal/mol, MAE<=0.50, max absolute error<=1.50. Heldout RMSE minus development RMSE must be<=0.25kcal/mol. These are NEW_PREREGISTERED_CRITERION and deliberate small-error/generalization budgets relative to the documented1D defects, not a guarantee four points certify the complete2D surface.

Development mixed contrasts compare differences-in-differences between each pair of CC levels atCS30/90. Absolute mixed-contrast residual<=1.0kcal/mol. This is a new coupling diagnostic/validation gate, not a new cross term in the CHARMM potential. Report all contrasts; they are correlated, not three independent free coupling coefficients.

Heldout points are frozen before QM:90/60,210/0,330/60,270/0. No heldout-based variables, weights, regularization, seeds/restarts, bounds, grouping or model choice. Preferred sequencing computes them only after candidate freeze. Any heldout QC failure or ambiguous branch yields INCOMPLETE_VALIDATION/STOP; any metric failure rejects the candidate. No heldout-driven second fit is allowed by this protocol.

## Curvature gates and scaling

Use GEO_B_HESSIAN_PROCESSING_PROTOCOL.md exactly: unscaled factor1, source-frame Cartesian handling, rigid6-mode projection, explicit mass policy, redundant Wilson-B/SVD, coordinate-curvature term for nonstationarity, assignment/subspace character and low modes retained. Curvature and mode gates are newly preregistered there; no raw-frequency-only k fitting.

## No compensation — independent hard scientific gate

Reject a candidate with material regression in any protected class even if L_total improves:
- untargeted individual bond absolute error worsens by>0.005 Angstrom or angle by>0.50degree versus ORIGINAL v1 baseline for that same QM target;
- head/junction/tail class geometry RMSE worsens by>0.005 Angstrom or0.50degree;
- any A/B geometry class RMSE worsens by>0.005 Angstrom (bonds) or0.50degree (angles);
- same-anchor CC/CS/2D energy RMSE worsens by>0.25kcal/mol;
- original A improves while B violates its gates, junction improves while tail violates, or development passes while heldout fails;
- CC240 branch pair erased/misassigned, or branch energy gap error worsens by>0.25kcal/mol;
- nonbonded compatibility degrades beyond existing report75/76 approved caution/gates at the model's relaxed geometries.
The numerical regression budgets are NEW_PREREGISTERED_CRITERION, chosen as small fractions of normalization scales. Measure numerical uncertainty independently; if uncertainty itself reaches the budget, REVIEW/STOP rather than increasing the budget. Do not apply a kcal budget to a geometry unit.

CC240 branches need full atom/O-equivalent geometry and local rotamer identity; their nominal CC/CS values alone do not distinguish them. A claim to reproduce both requires both retained branches to be validated, not averaged. Explicit model-insufficiency is preferable to a compensating-error fit.

## Final decision and authorizations

All HARD_QC, geometry, curvature, PES, prospective2D and NO_COMPENSATION gates must pass jointly. Passing a scalar aggregate objective does not override any gate. One joint CHARMM-compatible model only; no default CMAP/non-CHARMM cross terms.

These rules are prospectively fixed before new QM/fitting. They may be scientifically revised only in a new version with explicit reason BEFORE accessing any affected heldout results; then old results/design remain preserved and any genuinely new holdout must be prospectively designated. Current task does not authorize such a revision or new QM.

FIT_READY remains NO until numerical identifiability, prospective design, bounds/criteria, A+B curvature and exact launch/fitting authorization are actually resolved. After v2 Git upload/review, STOP.
