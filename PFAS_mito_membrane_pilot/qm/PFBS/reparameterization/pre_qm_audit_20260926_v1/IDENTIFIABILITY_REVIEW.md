# Identifiability review before new QM

Status: audit preparation; no Jacobian, optimization, fit or parameter release has been performed.

## Meaning of the matrix

`PARAMETER_OBSERVABLE_MATRIX.tsv` has one row per existing type-level field/group (including initially frozen guards), and one column per inventory observable or proposed job/family. `PARAMETER_OBSERVABLE_COLUMNS.tsv` binds column roles and availability. STRONG / MODERATE / WEAK / NONE denote **expected qualitative information**, not measured sensitivities, a numerical Jacobian, rank, uncertainty or proof of identification. Scores are deliberately conservative for unspecified finite-displacement directions. Conditional tail families are columns for proposals, not acquired data.

STRONG Hessian information does not show that every stiffness is separately identifiable. Likewise, a geometry-sensitive parameter can still be correlated with other fields. Held-out columns describe expected validation response; they are never permitted optimizer, variable-selection, weighting or restart input. Water validation is an already inspected compatibility guard, not prospective blind validation.

## Equilibria and curvature

GEO_A/B and all accepted constrained geometries provide direct evidence about **realized** bond lengths and valence angles. They constrain type-shared r0/theta0 combinations; they do not identify those parameters by copying QM distances/angles. Intramolecular nonbonded, torsion, angle and UB forces contribute to every minimum. The failed r0-only cycle demonstrates the risk: all ten targeted observations improve while junction angles and other chain bonds worsen.

CG312-SG3O1, equivalent OG2P1-SG3O1, CG312-CG312 across BOTH 14-15/14-16, and CG302-CG312 require joint equilibrium review. Biased junction/tail angle families are candidate classes. CF2/CF3 bond families and CG312-CG312-CG312 theta0 start frozen; they are guards, not automatically optimized because of an analogy penalty. Source coefficients remain unchanged in this package.

Geometry alone cannot identify bond/angle force constants. Raw A Hessian is available; B curvature is proposed. Before any numerical target use: verify frame/units/masses; project rigid rotations/translations consistently; recompute/check modes and characters; define any scaling once and retain raw values; then construct a reduced type-shared parameter-to-observable Jacobian and examine rank, correlations, uncertainty and stability across A/B. No mass weighting, mode comparison, internal-coordinate transform or force-target inference has yet been completed here. Numerical singular-value/correlation acceptance thresholds are not previously frozen.

## UB and torsion confounding

Five angle families contain nonzero UB. Endpoint distance r13 is a function of two bonds and their included angle. theta0/ktheta and r13/kUB can have similar local forces/curvature. Initially freeze both UB fields. Only independent curvature/finite-amplitude evidence that a reduced bond/angle representation is insufficient can justify one identifiable UB degree of freedom. Freeing both UB fields and angle equilibrium/stiffness together without rank evidence is underdetermined. Six zero-UB families remain zero.

T_CC contains several Fourier families around 14-15, including families also acting around 14-16. T_CS contains O-equivalent n=3 combinations around 15-1. Multiple physical dihedral rows are **shared instances**, not independently fitted amplitudes. Their summed Fourier columns may be collinear even with many PES points. Use identifiable grouped combinations; freeze a source amplitude or impose a scientifically prespecified grouping if individual terms cannot be distinguished. Preserve phases, multiplicities and four zero-amplitude n=3 components initially.

CC/CS relaxed surfaces include angle/UB/bond relaxation, and the unscanned torsion changes basin. Their energy differences cannot uniquely attribute a defect to Fourier amplitudes. Shared 14-16 amplitude release triggers the independently proposed C1-C3 axis evidence. Tail/CF3 terms start frozen; geometry error or penalty22.1 alone does not trigger that torsion scan.

## What current and new data can answer

- GEO_A: one geometry and one local Hessian, substantial local information but one curvature basin.
- Revised GEO_B: second geometry and conformer energy, currently no frequency/Hessian in the audited source inventory.
- Twelve CC and thirteen CS points: full geometries and adiabatic energies. CS120 is O-permutation closure rather than an independent new chemical state. These are already inspected development data.
- CC240 forward/reverse: full branch evidence and ~0.22530 kcal/mol difference. Preserve both; reverse is excluded from numerical fitting and used for branch consistency diagnosis. Already inspected branches are not a blind test.
- B Hessian plus six mixed development points: a necessary initial information expansion under the authoritative decision, **not** a proven sufficient/full-rank or smallest design.
- Four prospectively fixed mixed holdouts: unseen 2D response validation. Failure cannot be repaired by relabeling these points as training.

Some fields will remain underdetermined even after the core tranche. Reduce the variable set and keep source-supported fields fixed. Conditional displacements/tail targets require a separately justified exact design. The optional fresh minimum would add genuinely independent basin validation; it is not silently made a mandatory new job.

## Joint scientific requirement

One CHARMM-compatible potential must preserve local lengths/angles, global 17-atom geometry, curvature/mode behavior, conformer ordering and both relaxed PES profiles simultaneously, including branches and symmetry. A staged variable release is not sequential acceptance of independently fitted potentials. Reject compensation that improves one target class by harmful degradation of another. Charges, LJ, topology, masses, exclusions/1-4 semantics, combining rules, phases/multiplicities and force-field family remain frozen.

**FIT_READY = NO. NEW_QM_AUTHORIZATION = NOT_GRANTED.** This package supports an independent pre-QM decision, not parameter creation.
