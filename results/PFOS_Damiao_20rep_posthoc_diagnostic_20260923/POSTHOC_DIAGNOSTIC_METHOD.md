# Post-hoc diagnostic method

## Scope and invariants

This is a read-only diagnostic of the completed, published ensemble. The formal
result remains `COMPLETE / INCOMPLETE_N20` with 7 accepted, 13 inconclusive, and
0 MD failures. Existing trajectories, seeds, TPR/topology, thresholds, statuses,
selected windows, diffusion values, and the frozen final package were not changed.

## Frozen candidate evaluation

The existing frozen 10 ps candidate tables were read for rep02–rep20. The grid
uses starts 0.5–3.5 ns in 0.5 ns increments, ends through 5.0 ns, and width ≥1.5
ns. Gates were R² ≥0.995, both alpha measures in [0.90,1.10], and minimum origins
≥500. Rep01 was restricted to reconstruction of its already-selected 0.5–2.0 ns
diagnostic with the exact frozen analyzer implementation (SHA256 recorded).

## Closest-to-eligible rule

For an inconclusive trajectory, each gate violation was normalized as:

- R²: `max(0, (0.995-R²)/0.005)`
- each alpha: distance beyond [0.90,1.10], divided by 0.10
- origins: `max(0, (500-min_origins)/500)`

The Euclidean norm of those four components defined proximity. Deterministic
ties used earliest end then earliest start. **D was excluded completely.**

## Late-lag and Cartesian diagnostics

Frozen 10 ps-origin total-MSD fits at 0.5–2, 1–3, 2–4, and 3–5 ns were compared.
A 3–5/0.5–2 slope ratio ≥1.25 was called a late upward bend and ≤0.75 a late
plateau. Cartesian component fits used the same origin construction. A diagnostic
axis flag was set when one component contributed ≥60% of the summed absolute
component slopes in any standard window. This flag does not establish physical
anisotropy; it detects direction-dominated finite-trajectory excursions.

## Origin sensitivity

Candidate eligibility was recomputed at 5, 20, and 50 ps and compared with the
formal 10 ps result for all replicates. LOW means no accepted/inconclusive outcome
change and ≤10% candidate Boolean disagreement; MODERATE allows one outcome
change and ≤30%; otherwise HIGH. Rep01 was evaluated only at its fixed historical
window, as required by the narrower reconstruction authorization.

With a 10 ns interval, 20 and 50 ps origin spacing necessarily produces fewer
than 500 origins at long candidate lags. Thus the HIGH category for accepted
replicates is mechanically driven in part by retaining the frozen ≥500-origin
gate under those diagnostic spacings; it does not indicate changed dynamics.

All diagnostics are explanatory and do not revise the prospective frozen result.
