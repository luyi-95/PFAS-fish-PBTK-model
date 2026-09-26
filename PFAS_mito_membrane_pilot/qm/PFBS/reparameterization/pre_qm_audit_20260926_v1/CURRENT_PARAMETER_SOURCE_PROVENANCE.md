# Exact current parameter provenance

The copied original molecule ITP SHA256 is c736e8e20ee778fd64dfc2b95da13040b6a49404c78dc1cf46dd7368b016aeca; PRM SHA25624baf41553845380e9905f7419ca85cb0528dcd7652d596ca6ba83e003d05a56. These are the current baseline, not the failed bonded candidate. The stream records CGenFF program4.0 output intended for force-field5.0; program and force-field version are different labels.

Inherited source: `/home/ls/projects/PFAS_mito_membrane_pilot/qm/PFBS/phase3_mm_preflight_20260924/sources/charmm36-feb2026_ljpme_cgenff-5.0.ff/ffbonded.itp`, SHA256 cda750df0be35f862599f276f667be608b266a7a0aee085d2f623e82796403cf. Read-only SCP placed an unchanged copy in an external audit cache. Only the matched lightweight rows, their original line numbers and full-source hash are included. Molecule PRM overrides precede inherited definitions; reversed type order is equivalent.

Source decimal precision is retained in CURRENT tables. The original effective TPR dump SHA2562ec1f2360523c920d1f4c60f915f355300cb5a04ff0d20874dfa765d23f8600b has finite printed precision. `evidence/SOURCE_TO_TPR_PRECISION_AUDIT.tsv` reconciles every active coefficient within its printed half-unit. It does not use a new scientific tolerance or round source coefficients into new parameters. Four zero n=3 components present in the PRM but absent from the compiled active list are explicitly retained.

GROMACS harmonic bond/UB k has a1/2 convention: CHARMM K(kcal/mol/angstrom²) converts×836.8 to kJ/mol/nm²; angleK converts×8.368 to kJ/mol/rad². Proper torsion amplitude converts×4.184 without that harmonic factor. No conversion is applied to generate candidate values here; current converted source values are reported directly.

All-instance topology closure is mandatory. There are16bonds,30angleinstances and38nonzero Fourier instance-components. Initial release status is proposal only; no global force-field file is edited. Atom charges,LJ/masses/exclusions/1-4/combining rules and proper phases/multiplicities/zero amplitudes remain source-frozen.
