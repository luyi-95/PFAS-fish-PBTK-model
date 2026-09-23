# Frozen PFOS diffusion-analysis protocol

Status: **FROZEN BEFORE ADDITIONAL REPLICATES**

## Trajectory and COM

- Use only the formal 11 ns NVT trajectory.
- Analyze `t > 1000 ps` through `11000 ps`.
- Use the 29-atom PFOS- mass-weighted molecular COM.
- Make PFOS whole and reconstruct a continuous no-jump COM path.
- Use laboratory-frame PFOS MSD as the primary method. System-COM-relative MSD is diagnostic only.

## Time origins and fit-window selection

- Time-origin spacing: `10 ps`.
- Candidate start times: 0.5-3.5 ns in 0.5 ns increments.
- Candidate end times: 0.5 ns increments, no later than 5.0 ns.
- Minimum window width: 1.5 ns.
- Eligible only if:
  - `R2 >= 0.995`;
  - mean one-octave local alpha is in `[0.90,1.10]`;
  - window log-log alpha is in `[0.90,1.10]`;
  - minimum contributing origins at every lag is at least 500.
- Select the earliest-ending eligible window; ties use earliest start.
- If no window qualifies, classify that replicate as `INCONCLUSIVE`. No manual fallback is permitted.
- Never use proximity to a published or expected D in eligibility or selection.

For the current replicate, this rule selects `0.5-2.0 ns`.

## Diffusion coefficient and finite-size correction

- Three-dimensional `D_i_PBC = slope(MSD)/6`.
- At 298.15 K, apply the paper-faithful correction to each accepted replicate:

```text
D_i_infinity = D_i_PBC + 0.23 x 10^-9 m2/s
```

- Recalculate the correction only if the actual fixed box length materially departs from the reconstructed protocol.

## Ensemble statistics

For 20 accepted independent replicates, calculate statistics from corrected `D_i_infinity` values:

```text
mean = sum(D_i_infinity) / 20
s_D  = sqrt(sum((D_i_infinity - mean)^2) / 19)
u95  = t(0.975,19) * s_D / sqrt(20)
report mean +/- u95
```

Regression SE, GROMACS half-fit difference, within-trajectory block SD, Cartesian variation, and time-origin sensitivity are QA diagnostics only and are not replicate uncertainty.
