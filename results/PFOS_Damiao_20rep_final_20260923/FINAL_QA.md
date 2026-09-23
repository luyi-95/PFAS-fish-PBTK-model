# Final QA

Generated: 2026-09-23T09:32:23+08:00

- Runtime: PASS — all 20 replicates reached a terminal workflow state; no failed replicate.
- Numerical: PASS — aggregate anomaly count 0 for LINCS, SETTLE/SHAKE, NaN/Inf, PME, constraint, fatal, segmentation fault, and OOM patterns.
- Thermodynamic: PASS — 100 bar NpT, 1 bar NpT, and NVT thermodynamic gates passed for rep02-rep20; rep01 retains its previously validated formal QA.
- Structural: PASS — all 28 PFOS bonds remained within the frozen 0.10–0.25 nm integrity gate for rep02-rep20; rep01 retains its validated PBC-aware QA.
- Trajectory: PASS — XTC, EDR, CPT, final GRO, final time, and 4026-particle evidence passed for every newly generated replicate.
- Provenance: PASS — frozen input, seed, scheduler, final-state per-replicate, and original 20/20 hash audits passed. The authorized legacy rep02–rep04 manifest-ordering repairs are explicitly preserved and audited; no scientific artifact changed.
- Scheduler: PASS — maximum worker overlap 0; swap 0.0 GiB; actual throttle samples 0; maximum GPU temperature 52.0 °C.
- Scientific endpoint: **INCOMPLETE_N20** — 7/20 met the prospectively frozen MSD-window rule.

Technical completion and scientific acceptance are reported separately. A completed replicate classified `INCONCLUSIVE` remains part of the pre-registered ensemble outcome and was not selectively rerun.
