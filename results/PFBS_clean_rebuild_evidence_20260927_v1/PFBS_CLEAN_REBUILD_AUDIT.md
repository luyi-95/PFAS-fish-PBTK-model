# PFBS clean CGenFF5 → GROMACS rebuild audit (2026-09-27)

## Source and implementation
- Remote build: /home/ls/projects/PFAS_mito_membrane_pilot/qm/PFBS/clean_rebuild_20260927
- Original CGenFF output: parameters/preflight/PFBS/raw_cgenff5_output/PFBS_input_canonical.str (SHA256 fe0e86404bb3857e2a3ecf7ae577001640a3f6010181a52899c09a18febe4eba) and PFBS_input_canonical.cgenff.mol2 (f5d09e21487580fa11b1ce95f575c1a8567b46234050ae0ba25b6c12f0d1af9b).
- Parent FF archive: release_audit/charmm36-feb2026_ljpme_cgenff-5.0.ff.tgz (b2221dcba73066b6b5c30a52b9894216d03ea6c3e68206d9ce43857dd8116c21). Converter: release_audit/cgenff_charmm2gmx.py (eb32b884d0db37dccc585c7a2b33894c7351600db1b3e90969a3f3601d880cb4).
- Converted afresh from the original stream/Mol2; no old ligand .itp/.prm was copied. New files differ from old actual inputs only in CRLF versus LF; diff --strip-trailing-cr reports no content differences. Parent FF trees are identical.
- GROMACS 2026.3 double precision grompp compiled 17 atoms, 30 angles (all function 5), 36 listed 1–4 pairs, nrexcl=3, fudgeLJ=fudgeQQ=1.0, 38 instantiated proper periodic terms. The TPR identifies C1–C2–S1 as UREY_BRADLEY with theta0=122 deg, ktheta=418.4 kJ mol^-1 rad^-2, r13=0.2357 nm, kUB=25104 kJ mol^-1 nm^-2. This maps the source CHARMM 50 kcal mol^-1 rad^-2, 30 kcal mol^-1 A^-2, and 2.357 A with the factor of 2 required by the GROMACS half-harmonic convention.
- The C3–C1–C2–S1 proper torsion appears as three actual TPR interactions: n=1 phase=180 deg k=3.93296 kJ/mol; n=2 phase=0 deg k=1.58992; n=3 phase=0 deg k=0.46024. These are exactly source 0.94/0.38/0.11 kcal/mol. C1/C2/C3 share atom type CG312. The C1–C2–S1 angle has one instance; S1–C2–F3/F4 has two related instances with the same numeric angle/UB values from separate source type entries.

## Minimal double-precision baseline
- Vacuum isolated-anion matched setup; existing accepted QM coordinates only. L-BFGS then conjugate-gradient minimization to Fmax<10 kJ mol^-1 nm^-1, with restrained scan torsion at scan points and unrestrained high-precision final single-point energy. No Gaussian or MD.
- Clean energies (kJ/mol): T_CC_180 386.553005; T_CC_300 397.654456; T_CS_000 433.047466; T_CS_070 397.402298. Old actual input outputs: 386.553004, 397.654456, 433.047466, 397.402298, respectively.
- T_CC: clean MM favors 180 over 300 by 2.65331 kcal/mol; accepted QM favors 300 over 180 by 0.99058 kcal/mol. T_CS: clean MM and QM both favor 70 over 0, with 8.5194 and 4.5994 kcal/mol gaps, respectively. Only these diagnostic points were recalculated, not the full scan.
- GEO_A C1–C2–S1: QM 119.970 deg, clean MM 113.322 deg (−6.648 deg); GEO_B_REVISED 116.912 vs 111.872 deg (−5.040 deg). GEO_A S1–C2: 1.87368 vs 1.76905 A; C1–C2: 1.54633 vs 1.48677 A. The clean topology preserves the old geometric discrepancy.
- At GEO_A, the source UB target C1···S1 is 2.357 A, while QM is 2.96589 A and clean MM is 2.72445 A. Its strong preference for a shorter 1–3 separation competes with the 122 deg angle target; this is a native CGenFF source term and a plausible contributor to the G4 angle discrepancy. These coupled observations do not isolate a unique defective parameter.

## Judgment
Clean conversion and topology do not explain the observed discrepancies. The mismatches persist in the unmodified CGenFF5 parameter model. A source parameter inadequacy is supported, especially around the high-penalty junction angle/UB and CC torsion, but the permitted baseline cannot assign causality to a single term or justify a numerical parameter change. Stop here; any reparameterization is a separate phase.

