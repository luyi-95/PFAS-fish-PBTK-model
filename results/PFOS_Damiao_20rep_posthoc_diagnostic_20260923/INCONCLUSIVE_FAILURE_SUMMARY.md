# Inconclusive failure summary

The frozen formal result is unchanged: `COMPLETE / INCOMPLETE_N20`, with 7
accepted, 13 inconclusive, and 0 failed MD trajectories.

## Failure matrix summary

Counts below use each trajectory's closest candidate under the threshold-only,
D-blind normalized violation rule:

| Diagnostic | Replicates |
|---|---:|
| n_fail_R2 | 11 |
| n_fail_mean_alpha | 10 |
| n_fail_loglog_alpha | 11 |
| n_fail_origin_count | 0 |
| n_multiple_failure | 13 |
| alpha_too_low (either alpha gate) | 8 |
| alpha_too_high (either alpha gate) | 5 |
| late_lag_instability | 13 |
| axis_anisotropy_flag | 9 |
| origin sensitivity LOW / MODERATE / HIGH | 13 / 0 / 0 |

Primary-failure labels: `{'MULTIPLE_FAILURES': 13}`. The most frequent primary label
was **MULTIPLE_FAILURES** (13/13).

## Accepted versus inconclusive (descriptive)

| Metric | Accepted selected windows | Inconclusive closest candidates |
|---|---:|---:|
| Mean R² | 0.996753 | 0.987011 |
| Mean local α | 1.015924 | 0.852322 |
| Mean window log–log α | 1.034895 | 0.899445 |

Origin sensitivity was `{'HIGH': 7}` among accepted replicates
(rep01 fixed-window scope) versus `{'LOW': 13}` among inconclusive
replicates. The alpha spread, mixed low/high failures, late-lag changes, and
direction-dominance flags are more consistent with finite-length stochastic
sampling under a strict simultaneous gate than with one uniform alternative
physical regime; this remains descriptive, not a causal proof.

Among the 13 inconclusive trajectories, late-trend classes were
`{'LATE_PLATEAU': 8, 'LATE_UPWARD_BEND': 4, 'STABLE_OR_NONMONOTONIC': 1}`. The broad late-instability flag was also present in
6/6 accepted trajectories evaluable
from the current candidate tables, and the direction-dominance flag in
6/6. These diagnostics are therefore
not specific signatures of the inconclusive subset.

## Required scientific questions

### Q1. What was the main gate among the 13 inconclusive trajectories?

The closest-candidate audit identifies alpha-related failures as the dominant
gate family; exact per-replicate combinations are in the TSV.

### Q2. Was R² or alpha the main problem?

Alpha was more frequent: R² failed in 11/13 closest candidates, while
mean and/or log–log alpha failed in 13/13.

### Q3. Did alpha failures tend low or high?

Across trajectories, either alpha gate was low in 8/13 and high in
5/13. Thus the direction was **not predominantly high**.

### Q4. Did origin count limit eligibility?

No closest candidate failed the origin-count gate (0/13); it was
not the principal constraint under the frozen candidate grid.

### Q5. Was late-lag upward curvature general?

13/13 were flagged for a late-lag slope/alpha instability by the declared
diagnostic, but only 4/13 were
classified as upward bends; 8/13 were
plateaus and 1/13 were
stable/nonmonotonic by the slope-ratio rule. Upward curvature was not universal.

### Q6. Were excursions dominated by a small number of Cartesian axes?

9/13 crossed the direction-dominance diagnostic, versus
6/6 evaluable accepted trajectories.
Direction-specific excursions were common but not specific to failed eligibility,
and do not prove persistent physical anisotropy.

### Q7. Does the 10 ns analysis interval show finite-sampling limitations?

The combination of 13/13 late-lag flags, 9/13 direction-dominance
flags, and origin-sensitivity categories {'LOW': 13} is **evidence
consistent with finite-sampling limitations** in strict per-trajectory window
eligibility. It does not prove a single physical mechanism.

The alternate-spacing result requires a design caveat: keeping the ≥500-origin
gate makes every 20/50 ps candidate fail origin count by construction at long
lags. The formal 10 ps analysis itself did not fail origin count.

### Q8. Does rep01 satisfy the current frozen rule?

Yes. `REP01_FROZEN_RULE_AUDIT = PASS`; reconstructed window log–log alpha is
0.995094093710, and minimum origins is 800.

### Q9. How does the accepted-seven descriptive mean compare with 0.62?

The descriptive mean is 0.642793679 ×10⁻⁹ m² s⁻¹, differing by
+0.022793679 (+3.676%) from 0.62. This is not
the frozen n=20 estimator.

### Q10. What prospective study is most reasonable next?

Pre-register a longer-trajectory study and retain the present gate unchanged,
while adding estimator robustness as a co-primary design question: fixed-lag
ensemble MSD and a likelihood/Bayesian diffusion estimator can reduce unstable
single-trajectory adaptive-window decisions. An ensemble-MSD estimator should
preserve replicate identity for uncertainty; VACF/Green–Kubo is a useful
cross-check but can itself be noisy at long times. More replicates alone are less
direct than more independent trajectory length when late-lag/origin sensitivity
is the observed limitation. All choices must be frozen prospectively before new MD.
