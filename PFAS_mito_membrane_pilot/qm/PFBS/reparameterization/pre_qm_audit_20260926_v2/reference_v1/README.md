# PFBS broad reparameterization pre-QM audit v1 — 2026-09-26

This lightweight, read-only evidence package prepares independent review before new QM resource use. It does not authorize new calculations or fitting.

The original `SOL_HIGH_PROTOCOL_REVIEW.md` and JSON are copied byte-for-byte. Its sole authoritative decision remains **BROAD_PFBS_REPARAMETERIZATION_REQUIRED**, NEW_QM_REQUIRED=YES, EXPECTED_SCOPE=LARGE. The requested class labels correspond to that report's bond equilibria, valence-angle equilibria, identified bond/angle force constants, conditional identifiable UB and coupled proper amplitudes; the source wording has not been edited.

## Audit navigation

- `CURRENT_*_TERMS.tsv`: exact current GROMACS source coefficients, emitted penalties (NOT_EMITTED is not zero), all instances and proposed initial states. Inherited FF rows are extracted with original file hash/line; printed TPR coefficients are separately reconciled at their finite printing precision. Bond/UB harmonic coefficients use the GROMACS1/2 convention; r0/r13nm, anglesdegrees, energykJ/mol; angle stiffness perradian squared. These are original parameters, not a candidate.
- `PARAMETER_INSTANCE_MAP.tsv`: all physical instances/fields share their type-level variable. Equal numbers in different families do not imply the same variable. No instance-specific fitting.
- `QM_OBSERVABLE_INVENTORY.tsv`:62existing observables with exact raw-source paths/hashes, roles and method/basis;25accepted absolute points,6reverse diagnostics, A/Bgeometry+Acurvature,24primary water jobs +2diffuse-basis water diagnostics +2ESP jobs. The accepted CC180 source is the retainedv4d sentinel and CC060 is attempt04. Existing development evidence is not blind validation. Forward CC240 is a main development point; its reverse branch remains diagnostic/excluded from numeric fitting.
- `inputs/`: exact proposed revisedB frequency input, static audit/specification; sourceA frequency input/log and raw51x51Cartesian Hessian/gradient provenance. No internal-coordinate force-target transformation, scaling, parameter inference or normal-mode fit has occurred. Checkpoints are hash references only; existing fchk availability is explicitly recorded.
- `JOINT_CC_CS_DESIGN.tsv`: exactly6development+4prospective holdouts. Accepted starting seeds are fully bound. Ten rotated two-target launch inputs are not prepared; `JOINT_INPUT_PREPARATION_SPEC.md` states the remaining pre-launch work.
- `PARAMETER_OBSERVABLE_MATRIX.tsv`:61type-field rows×77existing/proposed columns; qualitative expected information only. `IDENTIFIABILITY_REVIEW.md` explains correlation/underdetermination and initial freezes.
- `RELEASE_HIERARCHY.md` and `ACCEPTANCE_CRITERIA.tsv/md`: staged variable eligibility under one joint potential; inherited rules and explicit unfrozen decision gaps. No new outcome-tuned threshold.
- `failure_evidence/`:all32A/Bbond and60angle comparisons, ten improving targeted observations, worsening junction angles/untargeted chain, current PES failure and CC240branches. Earlier candidate is not adopted.
- `NEW_QM_JOBS_PROPOSED.tsv`:11coreproposals plus separatelyconditional tail/displacement families andoptional newminimum. All are NOT_AUTHORIZED. Cost is historical planning evidence, not a benchmark or completion promise.

## Immutable identity and reproduction

`PACKAGE_MANIFEST.json` lists auditable files and hashes, excluding itself and SHA256SUMS to avoid circular hashes. `SHA256SUMS` covers every payload file except itself, including the manifest. The **package SHA256** is the deterministic uncompressed ZIP of all payload files including SHA256SUMS, sorted by POSIX relative path with fixed1980timestamp/0644permissions. Run `python -B tools/verify_and_archive.py <output-ZIP-outside-package>` from any checkout to verify all hashes and reproduce that archive. Git commit identity is recorded in an external post-push receipt because a commit cannot contain its own SHA.

Dedicated branch: `provenance/pfbs-broad-pre-qm-audit-20260926-v1`.
Dedicated path: `PFAS_mito_membrane_pilot/qm/PFBS/reparameterization/pre_qm_audit_20260926_v1`.
Repository: https://github.com/luyi-95/PFAS-fish-PBTK-model

All mutable build intermediates remain outside this tree; Python uses-B. No scratch/rwf/int/d2e/chk/fchk/cache/credentials/license payload is included. Read-only current ITP/PRM/stream copies are evidence; operational parameter files remain unchanged. No launch intent, launch record or new runtime directory is created.

`PRE_QM_PACKAGE_PURPOSE = INDEPENDENT_AUDIT_ONLY`
`NEW_QM_LAUNCHED = NO`
`PARAMETER_EDITED = NO`
`FITTING_STARTED = NO`
`MD_RUN_AUTHORIZATION = NOT_GRANTED`

Upload and independent exact-commit/hash reproduction are the stopping point. Scientific execution readiness and a new fitting cycle require separate review/authorization.
