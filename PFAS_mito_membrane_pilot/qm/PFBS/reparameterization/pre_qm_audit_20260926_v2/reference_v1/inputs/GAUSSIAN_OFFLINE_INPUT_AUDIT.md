# Independent Gaussian offline input and existing-Hessian audit

Date: 2026-09-26. Scope: PREPARE_PFBS_BROAD_REPARAMETERIZATION_PRE_QM_AUDIT_PACKAGE. Mode: NEW_STUDY, preparation only.

## Status

- GEO_B proposed-input static audit: **PASS**.
- Existing GEO_A archive/parser integrity: **PASS**.
- GEO_A Hessian readiness for force-field target use: **REVIEW**. Coordinate transformations, mass weighting, external-motion projection, mode comparison and force-constant identification are NOT_DONE.
- Current Gaussian capability, current resources and runtime-effective input: **UNVERIFIED**.
- Gaussian/GROMACS invocation, benchmark, fitting, parameter edit and MD: **NONE**.
- PARAMETER_EDITED=NO; QM_RUN_AUTHORIZATION=NOT_GRANTED; MD_RUN_AUTHORIZATION=NOT_GRANTED.

The authoritative scope decision remains BROAD_PFBS_REPARAMETERIZATION_REQUIRED. This input does not reopen the consumed bonded cycle or adopt its failed candidate. Root packages the unchanged authoritative decision; this audit owns only Gaussian/Hessian preparation.

## Prepared GEO_B job

Files:

- GEO_B_FREQ_PROPOSED.gjf, SHA256 **7a67576b5165ab8a6cfbc61322fc09ef85b9223aee5edc880fb28aae424ae1b1**
- GEO_B_HESSIAN_JOB_SPEC.json
- GEO_B_ACCEPTED_ARCHIVE_GEOMETRY.tsv

Only the accepted optimized **PFBS_GEO_B_REVISED.log** supplies the geometry. Source SHA256 **dbe29c5f0da615e8e5d267c8614a7552044ba01dad1b43afc2eafcf50e7f5afa**. Its local existing checkpoint hash is **158ee77849735418e158a30f087bf5ed61785fc1d7a66d6e5022212d4222a1c9**. No checkpoint was converted, uploaded, copied into a runtime directory or used as an input dependency.

The parser reassembles the normally terminated final Gaussian archive across wrapped lines, selects its charge/geometry section, and preserves coordinate number strings without six-decimal orientation-table truncation. It confirms MP2/6-31+G(d), optimization-completed/stationary-point evidence, charge −1/multiplicity1, 17 expected ordered elements, and the accepted final Input orientation at its printed precision. The old invalid B and GEO_B_REVISED_270_0_NOT_RUN.xyz are not lineage inputs.

Atom order is S1, F1–F9, O1–O3, C1–C4; their indices are 1,2–10,11–13,14–17. Coordinates are Angstrom. The proposed frequency route is exactly:

`#P MP2/6-31+G(d) Freq SCF=Tight NoSymm`

The input has no Opt, Guess=Read, Geom=Check, ReadFC, Link1, extra constraint or model-chemistry substitution. New relative checkpoint name: GEO_B_FREQ_PROPOSED.chk. It computes frequencies at the accepted B minimum if later launched under its frozen gate; it is not a new geometry optimization.

Proposed %NProcShared=8 and %Mem=48GB copy the accepted GEO_A frequency GJF grammar/resource settings. They are RECONSTRUCTED proposal choices, not a current allocation or runtime proof. A single job, new job-local working directory and new empty GAUSS_SCRDIR would be assigned only at a separately authorized launch. This package creates no runtime/scratch directory and contains no launcher. Current host availability, licensed institutional use, exact executable/banner/environment, free memory/scratch and protected jobs need a fresh preflight before any run. No measured ETA or benchmark is claimed.

## Gaussian backend capability receipt, offline only

| Requirement | Capability basis | Status |
|---|---|---|
| MP2/6-31+G(d) Freq at −1 singlet | Accepted GEO_A G16C.02 log demonstrates that route; accepted revised B uses same method/basis | SUPPORTED_WITH_LIMITATIONS, previously_verified; current installation unverified |
| Freq at a stationary geometry | Gaussian-authored Freq manual specifies stationary-point requirement and second-derivative frequency analysis | SUPPORTED_WITH_LIMITATIONS; future B minimum still needs its own result |
| Input GJF syntax and ordered Cartesian geometry | Known accepted A GJF plus strict offline parsing | PASS_STATIC; engine acceptance not tested |
| Current resource/parallel behavior | No runtime invocation or live allocation audit in this task | UNKNOWN_CURRENT |
| Cartesian Hessian transformation to local CHARMM parameters | No projection, inversion, diagonalization or fit performed | UNKNOWN/NOT_DONE |

The independent reviewer acts as the offline QM backend under scientific-md-orchestrator. That skill's scientific contract is preserved; a past successful job is not represented as a current engine handshake.

## Existing GEO_A Hessian: what was extracted

Source frequency log SHA256 **56b2bf0620ab18b1ee3517d3b2e1a7754adbba416f2737418938587fd34a4667**.
Local existing frequency checkpoint SHA256 **a4927633059acca2e2af469ed38acbfa7b27405ab628ec84d5b46fafe1e08b9e**.
The binary checkpoint was hashed read-only; no formchk or other engine was invoked.

The existing_hessian/ directory contains:

- PFBS_FREQ_GEO_A.gjf: exact original physical input copy, SHA256 d3b2a3e51b22e31c66c7818d62442e866a7c421a151c6a5c256136e96958ed58.
- PFBS_FREQ_GEO_A.log: exact lightweight raw frequency-log copy, SHA256 56b2bf0620ab18b1ee3517d3b2e1a7754adbba416f2737418938587fd34a4667.
- GEO_A_FCHK_AVAILABILITY.json: **NOT_AVAILABLE_ALREADY** for an identifiable A frequency FCHK in the reviewed local deliverable/remote PFBS filename inventory (79 remote FCHK paths, no frequency/FREQ_GEO_A path). Source FCHK hash is null. Local ESP_A/ESP_B FCHKs are distinct single-point data and are not Hessian substitutes. No claim about unrelated external records or anonymous paths not content-inspected. No formchk was run.

- prepare_gaussian_offline.py: standard-library parser and reproducible input preparation; no engine, scientific fit or eigenanalysis.
- GEO_A_ARCHIVE_EXACT.txt: reassembled archive, retaining source field strings.
- GEO_A_HESSIAN_PACKED_RAW.tsv: 1326 original lower-triangle number strings with index/Cartesian labels.
- GEO_A_CARTESIAN_HESSIAN_RAW.tsv: 51×51 symmetry expansion, retaining original number strings.
- GEO_A_ARCHIVE_GEOMETRY_MASSES.tsv: matching archive coordinates and printed isotope masses.
- GEO_A_GRADIENT_RAW.tsv: 51 gradient values and their sign/printing comparison with explicitly labeled force data.
- GEO_A_HESSIAN_PARSE_PROVENANCE.json: source hashes, field boundaries, exact packing/order, methods, limitations and generated-file hashes.

Identification does not rely only on 1326 being triangular. The source header/route say Freq/RMP2-FC/6-31+G(d); the property section ends in NImag=0; the first subsequent double-separator numeric field has the archive force-constant position documented by the independent GoodVibes developer parser; the following 51-number field agrees with the negative Cartesian force table. The complete reassembled archive also equals the separately punched fort.7 archive. The exact numbers, source line range and string fingerprints are retained.

Packing is row-major lower triangle: (x1,x1), (y1,x1), (y1,y1), (z1,x1), ..., with coordinate sequence x1,y1,z1,x2,...,z17. Full-matrix symmetry is produced by assigning each packed number to both positions; it is a representation check, not an independently calculated Hessian-symmetry error or evidence of rank. The 1326 entries are not 1326 independent physical targets.

Archive gradient strings have eight decimal places whereas the labeled force table has nine. Their maximum sign-adjusted difference is 5×10^-9 Hartree/Bohr and is within their **combined source-printing rounding**. An initial parser comparison incorrectly assumed nine-decimal precision for both fields; it failed before the Hessian products were written. The parser was mechanically corrected to derive each token's precision, and the complete extraction then passed. No source numbers, physical target or scientific tolerance changed.

The archive geometry matches the original A GJF exactly. The raw log states that its Z-matrix is all fixed cartesians and forces are copied. This ties the gradient/frame to the archive/input Cartesian geometry for this NoSymm job; no rotation into standard orientation was applied. The raw archive Hessian stays associated with this frame. It is not combined with a standard-orientation FCHK matrix without an independently checked rotation.

## Units and documentation boundary

| Data | Unit and frame treatment |
|---|---|
| Input/archive coordinates in these jobs | Angstrom, verified against GJF and Input orientation; do not apply FCHK-coordinate Bohr convention to this geometry block |
| Raw Cartesian Hessian | Hartree/Bohr², not mass weighted, following documented Gaussian Cartesian derivative conventions and the developer archive parser |
| Archive gradient | Hartree/Bohr, checked against explicitly labeled forces with gradient=−force |
| Printed AtmWgt | Isotope masses in amu, retained from source; not substituted by classical topology masses |
| Printed normal-mode force constants | Different normal-mode quantities; not the raw Cartesian Hessian or individual bond/angle k |

Gaussian-authored [formatted-checkpoint specification, mirrored by Jagiellonian University](https://tungsten.ch.uj.edu.pl/doc/g09doc/g09ur/f_formchk.htm) states Cartesian derivative fields use atomic units and distinguishes their orientation. Gaussian-authored [Constants manual, mirror](https://theochem.mercer.edu/chm295/g03_man/g_ur/k_constants.htm) defines internal atomic-unit usage. The independent software author's [GoodVibes archive Hessian parser](https://goodvibespy.readthedocs.io/en/latest/_modules/goodvibes/io.html) documents the NImag field position, lower-triangle unpacking, Cartesian order and Hartree/Bohr² units. These independently support the chosen raw representation.

The Gaussian-authored [vibrational-analysis guide](https://gaussian.com/wp-content/uploads/dl/vib.pdf) distinguishes Cartesian Hessian, mass weighting/projection and printed normal-mode force constants. The [Gaussian-authored Freq manual, mirror](https://wanglab.hosted.uark.edu/g03guide/G03Guide/www.gaussian.com/g_ur/k_freq.htm) explains stationary-point requirements.

Current gaussian.com pages returned fetch errors during this audit; its guide search excerpt and hosted copies of Gaussian-authored manuals were available. A complete Gaussian16 C.02 archive-field specification was not located. This is recorded as **REVIEW** before using the extracted matrix as a force-field target; the raw numbers and source-preserving parser PASS remain useful. No internal-coordinate conversion, scaling, force-constant interpretation or spectral recomputation fills that documentation gap.

## Proposed outputs and acceptance

Expected future outputs: raw log, new job-local checkpoint, stdout/stderr, exit status, runtime input/environment receipt, hashes, full Hessian/gradient/modes and warning audit. No future output exists now.

Report29 supplies the integrity and qualitative minimum gates: fixed chemistry/order/state, exact method/banner/source, complete hashes, normal completion/convergence, reviewed warnings, and no chemically meaningful imaginary vibration. Report47 establishes GEO_A-specific numerical and thermochemical caution; it is not an unconditional warning waiver for B.

For nonlinear17-atom B, expect45 projected vibrational modes with atom-mapped eigenvectors. Keep external near-zero roots separate. A tiny imaginary mode, ambiguous character, an unexpected warning or nonminimum triggers REVIEW/STOP under report29; no automatic rerun, reoptimization, route change or data replacement is proposed. Thermochemical/classical-rotation warnings must be classified for B using its own source result, rather than copied as benign solely from A.

New parser/target-completeness criteria, coordinate-rounding mechanics and any proposed numerical gradient/Hessian/mode-overlap thresholds are explicitly marked **CRITERION_NOT_PREVIOUSLY_FROZEN** in the job spec. No new numerical acceptance threshold was chosen. Existing approximately0.03Å/3° guidance is diagnostic and does not identify k. Hessian-to-local-target transformation, mode correspondence, target scaling and force-constant identifiability need a separate frozen analysis protocol before fitting.

## Terminal preparation state

STATIC_INPUT_AUDIT=PASS
EXISTING_HESSIAN_PARSER=PASS
HESSIAN_TARGET_READY=REVIEW
CURRENT_RUNTIME_CAPABILITY=UNVERIFIED
GAUSSIAN_RUN=NOT_STARTED
FORMCHK_RUN=NOT_STARTED
TRANSFORMATION_TARGETS=NOT_DONE
PARAMETER_EDITED=NO
QM_RUN_AUTHORIZATION=NOT_GRANTED
MD_RUN_AUTHORIZATION=NOT_GRANTED
