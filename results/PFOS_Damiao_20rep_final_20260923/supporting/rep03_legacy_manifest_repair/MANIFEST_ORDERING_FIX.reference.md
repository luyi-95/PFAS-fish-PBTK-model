# Manifest ordering and scheduler-affinity repair

Date: 2026-09-22

Scope: orchestration-only compatibility repair. No MD physics, seed, trajectory,
topology, force field, stage duration, or frozen diffusion-analysis rule is
changed.

## Manifest ordering defect

The historical runner generated `SHA256_MANIFEST.txt` while `qa/STATUS` still
contained `RUNNING`, then replaced the status with `COMPLETE_ACCEPTED` or
`COMPLETE_INCONCLUSIVE`. This caused the sole checksum mismatch observed for
rep03 and rep04. Their scientific artifacts are unchanged and remain part of
the preregistered ensemble.

For rep05 onward, the finalization order is:

1. Complete MD and frozen diffusion analysis.
2. Verify `original/` integrity.
3. Write `qa/finished_at.txt`.
4. Write the final `qa/STATUS` and close/sync it.
5. Generate `SHA256_MANIFEST.txt` through a temporary file.
6. Verify the completed manifest.
7. Make no further writes inside the replicate directory.

## CPU-affinity repair

The invalid rep03/rep04 performance run combined an external restricted
`taskset` mask with `gmx mdrun -pin on`. GROMACS native pinning overrode the
intended per-process placement and both worker groups occupied CPUs 0-23.

Future production runners accept scheduler-provided `GMX_PINOFFSET` and
`GMX_PINSTRIDE` values and invoke GROMACS native pinning directly:

```text
-pin on -pinoffset ${GMX_PINOFFSET} -pinstride ${GMX_PINSTRIDE}
```

The frozen workstation scheduler will use only offsets and worker CPU sets
validated by the independent benchmark-only branch. External `taskset` is not
combined with `-pin on`.

Historical runner SHA256 before this authorized orchestration repair:

```text
a25cb609f58e2ad19605b9de18ed762d86f55a53f97d17c007e8f12dceebe4f1
```
