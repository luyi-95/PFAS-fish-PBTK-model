# PFBS clean rebuild: minimal scientific review package

This directory is a review snapshot of the 2026-09-27 clean rebuild. The report, three original source files, and two converter-generated clean files were copied byte for byte. The TSV files, this README, and manifest were generated for this package. Nothing in earlier evidence directories was replaced.

## Contents

- `PFBS_CLEAN_REBUILD_AUDIT.md`: the scientific judgment and minimal MM evidence.
- `source/`: the canonical input Mol2, CGenFF-processed Mol2, and unmodified CGenFF stream file. The stream states CGenFF program 4.0 with topology/parameter files 5.0.
- `clean/`: newly converted GROMACS PFBS ligand `.itp` and converter-generated `.top`.
- `tables/CGENFF_TO_GROMACS_MAPPING.tsv`: every 2 bond, 7 angle, and 15 proper torsion source parameter mapped to the clean converted values (24 rows).
- `tables/ANGLE_UREY_BRADLEY_MAPPING.tsv`: all seven CGenFF stream angle types, including both source UB entries, GROMACS units, and actual PFBS topology instances.
- `tables/GEO_A_GEO_B_QM_VS_CLEAN_MM_GEOMETRY.tsv`: QM vs clean MM junction geometry. GEO_B means the accepted GEO_B_REVISED structure.
- `tables/T_CC_QM_VS_MM_PROFILE.tsv` and `tables/T_CS_QM_VS_MM_PROFILE.tsv`: accepted QM and historical MM full profile values. The clean MM column is filled only at the four points actually recomputed during this clean rebuild. The T_CC reverse CC240 branch is identified as a diagnostic row.
- `tables/OLD_VS_CLEAN_IMPLEMENTATION.tsv`: structural/parameter and four-point energy comparison.
- `manifest.json`: file origins, hashes, and scope.
- `SHA256SUMS`: SHA-256 for every package file except itself.

The `.top` is preserved exactly as generated. It refers to the parent CHARMM36/CGenFF5 force-field tree and to the converter-generated `.prm`, which are not in this upload because they were outside the requested file list. This package supports independent scientific review; it is not a standalone runnable topology. The parameter mapping table records the converted `.prm` values. The parent archive SHA-256, converter SHA-256, and old implementation hashes are in the audit report and manifest.

## Units and interpretation

Source CHARMM harmonic bond and UB force constants are in kcal mol^-1 A^-2; source angle constants are in kcal mol^-1 rad^-2. GROMACS harmonic coefficients use the half-harmonic convention, requiring a factor of 2 in addition to kcal→kJ and A→nm conversion. Proper torsion amplitudes require kcal→kJ only. In `CGENFF_TO_GROMACS_MAPPING.tsv`, generic `source_k` and `gromacs_k` columns use the units corresponding to each row's `kind`; explicit angle/UB units appear in the separate angle table. A zero-amplitude source periodic torsion is retained in the mapping table but contributes zero energy.

Only isolated-anion MM minimizations and single-point evaluations were run for the clean baseline. No new Gaussian, parameter fitting, MD, or full clean torsion scan was performed. Source/QM validation data were read only.

## Verification

From this directory on a POSIX shell, run `sha256sum -c SHA256SUMS`. The package identifier reported as `PACKAGE_SHA256` is SHA-256 of the exact `SHA256SUMS` file bytes. Verification was also performed from a separate checkout of the pushed Git commit.
