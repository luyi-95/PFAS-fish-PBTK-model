# Independent Sol High pre-QM audit completeness review

## Disposition and exact audit boundary

**PASS_FOR_PRE_QM_AUDIT_UPLOAD**

This disposition concerns the completeness, internal consistency, source traceability and upload suitability of the pre-QM audit package. **SCIENTIFIC_FITTING_READINESS=REVIEW; QM_EXECUTION_READINESS=REVIEW.** It does not approve a parameter set, a new fitting cycle, a Gaussian/GROMACS job or membrane MD.

Reviewer: independent user-requested Sol High scientific adjudicator. Date: 2026-09-26. User requirement source: attachment 2725a109-2449-4ad9-9c0e-c1b48ca4afc0, fully read. Root owns all payload construction; this reviewer wrote only this new review and its JSON companion during the final completeness audit.

Audited package root: E:\AI-App-Data\PFAS_mito_membrane_pilot\broad_pre_qm_audit_work_20260926\package

- Initial 67-file snapshot SHA256SUMS SHA256: ad9a9b87463eaf2e6c4a9be741fdc658e7b71a1f3cd5636dfce6fd4c53fe46d7.
- Corrected, accepted 67-file snapshot SHA256SUMS SHA256: **4809c23c5eb677377f2e296d24593fed965699f063d68ba58828da21b2af8df6**.
- Corrected README SHA256: 60a23720ebb89cb08a32977d98e165ab2f2ede12d7849eac245f4112c87c5f45.

The accepted SHA256SUMS predates these two review files. Root must regenerate PACKAGE_MANIFEST.json and SHA256SUMS to include them. The post-review archive SHA and Git commit belong in the external publication/reproduction receipt; this report cannot certify a future commit or include its own eventual manifest hash.

## Independent checks performed

Read-only standard-library parsing, exact string/number comparisons, file hashing and document inspection were used. No simulation, minimization, electronic-structure program, formchk, fitting or parameter mutation was performed.

All 67 physical files match the 66 SHA256SUMS entries plus SHA256SUMS itself. No unlisted or missing file exists in the accepted snapshot; every listed digest matches. PACKAGE_MANIFEST.json covers exactly the payload excluding itself and SHA256SUMS, with matching hashes. All 24 source-copy binding entries byte-match both their physical source and their included copy. Thirty-one locally accessible existing-QM inventory raw logs match their recorded hashes; their method/basis labels agree with the raw routes. Remote-only records are audited through the preserved hashed source receipts/snapshots, not represented as a new engine execution or a fresh content inspection of every remote raw log.

The 25 embedded accepted absolute G96 texts reproduce their own source hashes. Their machine geometry table has 25 points, each with the expected 17 ordered atoms. Every mixed-design seed geometry/checkpoint path and hash matches the preserved accepted source snapshot. CC060 uses accepted attempt04 and CC180 retained v4d; superseded/invalid starts are excluded from the design.

## Requirement coverage

| User requirement | Finding | Evidence |
|---|---|---|
| Authoritative Sol decision preserved | PASS | Original MD SHA 9f4c235312daf0ce24df7306f8154bf7789d18eed1ca7bcdc0da0f2c5f653b9b and JSON SHA 41a91dc78fc3f331f7e49946f3b222a54b554ea56bcf19cc307543e30b03b1cf byte-match their frozen delivery sources. Unique decision remains BROAD_PFBS_REPARAMETERIZATION_REQUIRED. |
| Exact current bond table | PASS | Six type families; all 16 instances; source values, units, penalties, r0/k status and rationale. |
| Exact current angle and UB tables | PASS | Eleven angle families / 30 instances and eleven associated UB families / 30 instances; nonzero and zero UB preserved distinctly. |
| Exact proper torsion table | PASS | Sixteen type-plus-multiplicity rows, including four source zero-amplitude rows; multiplicity, phase, amplitude and sharing explicit. Twelve active nonzero groups account for 38 Fourier instances. |
| Sharing topology map | PASS | 171 field-instance records; all entries forbid independent instance fitting. Bond/angle/nonzero torsion instance sets equal the effective source map, allowing atom-order reversal. |
| Existing QM inventory | PASS | 62 unique observables with source paths/hashes, method/basis, role and fitting status. Accounting is 2 geometries + 1 A curvature + 25 absolute PES + 6 reverse diagnostics + 24 primary water + 2 diffuse-water diagnostics + 2 ESP. |
| Existing A Hessian provenance | PASS for source-preserving parse; REVIEW for fitting target use | Original physical frequency GJF and raw log included; checkpoint hash referenced; FCHK NOT_AVAILABLE_ALREADY within declared searched scope; raw packed/symmetric Cartesian data, geometry/gradient and parser provenance included. |
| Proposed revised-B frequency input | PASS for offline preparation; runtime UNVERIFIED | Exact accepted revised-B geometry source/hash, MP2/6-31+G(d), charge -1 / multiplicity 1, Freq SCF=Tight NoSymm, no Opt/Guess=Read; job-local checkpoint proposal, expected outputs and gates explicit. |
| Mixed CC/CS design | PASS | Ten prospective design points, six development and four withheld; exact seed lineage, two target angles, selection/coverage rationale, branch ambiguity and off-adiabatic extrapolation explicit. Ten rotated launch-ready inputs are not claimed. |
| Parameter-observable matrix | PASS for qualitative design | 61 unique type-field rows by 77 columns: 62 existing plus 15 proposed job/family columns. Every cell is STRONG/MODERATE/WEAK/NONE. No numeric Jacobian, rank guarantee or independent-observable count is claimed. |
| Release hierarchy and identifiability | PASS | Joint geometry/curvature/energy guards; staged equilibria, identified stiffness, conditional UB and grouped amplitudes; shared 14-15/14-16 and equivalent-O risks documented. |
| Acceptance criteria | PASS for transparent pre-QM audit | Frozen source gates retained; unfrozen Hessian, global geometry, 2D energetics, rank/conditioning, weights/bounds and heldout criteria explicitly CRITERION_NOT_PREVIOUSLY_FROZEN. No invented numeric fit threshold. |
| Failed bonded cycle evidence | PASS | All 92 A/B bond/angle rows equal the original independent final-review JSON; focal improvements and worsening junction/chain geometry retained, along with original PES and CC240 branch evidence. |
| Proposed jobs, costs and stopping point | PASS | Eleven core proposals: one B frequency plus ten mixed points; conditional tail/displacements and optional new minimum remain separately conditional/unapproved. Frequency proposal uses 8 threads / 48 GB, matching actual A GJF resource settings. |
| Lightweight Git/reproduction plan | PASS for preparation; publication verification pending | Dedicated path/branch, immutable source copies, hashes, deterministic archive utility and exact-commit checkout plan present; archive avoids binary checkpoints/scratch/cache/secrets. Commit/ZIP receipt and independent checkout must be completed by root. |

## Physical parameter and failure checks

Every current coefficient string was independently matched to its stated physical PRM or inherited ffbonded source line, with the full source-file hash checked. Names, instance counts and sharing were cross-checked against the atom/type map. Source precision and rounded TPR evidence are distinguished.

CG312-CG312 r0=0.14563000 nm and k=227869.01 kJ/mol/nm2 are inherited active values shared by 14-15 and 14-16. Their penalty is NOT_EMITTED; the emitted CG302-CG312 analogue penalty 6 is not recast as a direct penalty on this inherited row. The proper table keeps n/phase explicit and preserves the four zero source terms.

The failed candidate improves all ten selected bond distances but worsens the S1-C2-C1 junction:

- GEO_A: signed error -6.6477513175 deg becomes -9.5178559110 deg.
- GEO_B: signed error -5.0402792357 deg becomes -8.2279224220 deg.

Both all-chain bond and angle tables retain the remaining tail bias. Existing CC energetics place the QM minimum at 300 deg and original MM at 180 deg. Both CC240 forward/reverse geometries and their energy difference remain separately represented. No averaging, nominal-dihedral-only branch identity or compensating-error acceptance is proposed.

The sole valid formal DP candidate cycle remains consumed, the invalid mixed draft excluded, the candidate not adopted, and current parameters REJECTED under the prior scientific disposition. This package requests preparation and independent audit of future systematic PFBS bonded work; it does not silently reopen that cycle.

## Hessian and input limits retained

GEO_A frequency source log SHA256: 56b2bf0620ab18b1ee3517d3b2e1a7754adbba416f2737418938587fd34a4667. Its 45 printed vibrational modes are positive in the existing accepted record. The packed matrix identification uses source archive field grammar, job provenance, coordinate order/frame and companion gradient evidence, rather than entry count alone.

Raw Cartesian Hessian parsing is source-preserving. Internal-coordinate transformation, mass weighting, external-motion projection, atom-mapped mode comparison, scaling and force-constant inference are NOT_DONE. Complete Gaussian16 archive-field documentation remains a declared REVIEW issue before interpreting fit targets. FCHK absence is bounded to the documented local/remote inventory search; no formchk was run and ESP FCHK files are not substituted.

B frequency input resource proposal is 48 GB, not 24 GB. Mixed-job 24 GB planning is a separate proposal. Existing A cost is a historical analogue, not a measured B or mixed-job prediction. Current licensed executable capability, resources and runtime-effective inputs remain UNVERIFIED.

## Remaining scientific and execution review

These are explicit pending work, not missing audit evidence:

1. Freeze a scientifically defensible reduced curvature/geometry/energy target protocol and unfrozen acceptance criteria before fitting. Qualitative matrix labels cannot establish rank or unique parameter attribution.
2. Audit A Hessian transforms and prospective B curvature; preserve coordinate frame, atom mapping and equivalent-O symmetry.
3. Prepare and validate exact graph-preserving two-target mixed starting structures and Gaussian inputs in a separate execution package. Hold four prospective points out of fitting/model choice; already inspected GEO_A/B, existing 1D scans, water/ESP guards and CC240 branches are not blind data.
4. Establish grouped torsion identifiability with fixed CHARMM phases/multiplicities and shared-instance constraints; do not fit every quartet freely or introduce non-CHARMM cross terms by default.
5. Use conditional tail or displacement batches only after their stated trigger. Eleven core jobs are a proposed initial design, not a proven smallest batch or rank guarantee. A whole-chain bonded audit does not imply all tail torsions must be refitted.
6. Root must complete the exact Git commit, final manifest/archive digest and independent checkout/hash/reproduction receipt. No GitHub publication success has been certified by this pre-publication review.

No compensating-error protocol is endorsed: improved torsion energetics must preserve local bonds/angles and global geometry, and geometry improvement must preserve CC/CS energetics, both CC240 branches and nonbonded compatibility guards. Charges/LJ remain the report75 ACCEPT_WITH_CAUTION decision; no demonstrated nonbonded defect or permission to refit them is inferred.

## Correction closed

The initial README omitted the two diffuse-water diagnostics in its prose enumeration of 62 inventory entries. Root corrected it to 24 primary water jobs + 2 diffuse-basis water diagnostics + 2 ESP jobs. The underlying inventory was already correct. The corrected README hash and regenerated 67-file manifest/hash listing were independently rechecked above. No other blocking factual defect was identified.

## Final flags

- PRE_QM_AUDIT_PACKAGE_STATUS=PASS_FOR_PRE_QM_AUDIT_UPLOAD
- AUTHORITATIVE_DECISION=BROAD_PFBS_REPARAMETERIZATION_REQUIRED
- NEW_QM_REQUIRED=YES
- EXPECTED_SCOPE=LARGE
- EXPECTED_SCIENTIFIC_VALUE_FOR_MEMBRANE_MD=MODERATE
- SCIENTIFIC_FITTING_READINESS=REVIEW
- QM_EXECUTION_READINESS=REVIEW
- NEW_QM_LAUNCHED=NO
- FITTING_STARTED=NO
- PARAMETER_EDITED=NO
- MD_RUN_AUTHORIZATION=NOT_GRANTED
- NEXT_AUTHORIZED_STOPPING_POINT=GITHUB_UPLOAD_AND_INDEPENDENT_EXACT_COMMIT_REPRODUCTION
