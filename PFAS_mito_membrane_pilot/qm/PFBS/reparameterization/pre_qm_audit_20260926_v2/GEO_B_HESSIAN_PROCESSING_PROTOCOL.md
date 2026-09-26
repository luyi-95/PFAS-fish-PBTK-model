# Joint A+B Hessian processing protocol — preregistration

PROTOCOL_ONLY. No Gaussian/formchk/Hessian calculation/transformation/fitting performed. A raw Cartesian matrix exists; B frequency remains proposed, not launched. New numerical gates are NEW_PREREGISTERED_CRITERION, not historical.

## Source and units

Use A original frequency GJF/log/archive/checkpoint hashes and B exact accepted revised geometry/future frequency log only. Reassemble raw archive with the source-preserving parser; verify job/method/state/NImag/atom order/field grammar and numeric completeness independently. Entry count alone does not identify a Hessian. Prefer independently available source FCHK cross-check if already present; any future formchk conversion requires separate authorization and a checkpoint copy, never source mutation.

Cartesian geometry in archive is Angstrom. Raw Cartesian force constants are Hartree/Bohr^2; gradients Hartree/Bohr. Preserve original strings/coordinate frame. Use one explicitly version-bound CODATA conversion table for Hartree-to-kJ/mol and Bohr-to-nm; compare converted units analytically and on a documented test before target use. No values inferred from a frequency alone.

Gaussian official [Vibrational Analysis](https://gaussian.com/wp-content/uploads/dl/vib.pdf) specifies mass weighting, external-motion separation and internal-coordinate diagonalization. Its search-accessible official document was found; direct PDF fetch failed in this environment. The existing archive parser still records its full-field documentation limitation; do not erase that REVIEW flag solely because general vibrational-analysis documentation exists.

## Coordinate frame, rigid projection, masses

Atom-map source coordinates and isotopic masses exactly; never mix archive frame with a standard-orientation Hessian without rotation. If rigid alignment R is applied, transform all3x3 Hessian blocks R H_ij R^T and gradients consistently. No atom permutation beyond documented chemically equivalent O/F mapping; keep original mapping and chosen symmetry map in the receipt.

For each stationary basin build mass-weighted H_m=M^-1/2 H_x M^-1/2, center at mass-weighted center of mass, construct3 translation and3 rotation vectors from the source coordinates/masses, orthonormalize by rank-revealing QR/SVD, and retain the45-dimensional orthogonal complement Q. H_vib=Q^T H_m Q. Verify nonlinear17-atom external rank6. Preserve eigenvalues before projecting; do not delete inconvenient negative curvature.

Use the same source masses for QM/MM comparison. Mass weighting is for projection/mode matching; bond/angle force constants remain in physical energy/coordinate units. Global isotopic remapping is prohibited.

## Internal coordinates and attribution

Build explicit atom-mapped bond/angle/selected proper coordinate set and Wilson B=partial q/partial x. Bond coordinates use nm, angles/torsions radians. Redundant coordinates require SVD and a fixed supported subspace, not inversion of a singular B or treating every redundant element as independent. Report singular vectors and condition/error bounds.

At exact stationary geometry, the curvature pullback is H_x=B^T H_q B on the supported vibrational tangent space. For nonzero gradients include the coordinate-curvature term sum_a g_qa*partial^2 q_a/partial x_i partial x_j, or STOP interpretation if unavailable/not negligible under the preregistered noise gate. Do not equate a raw Cartesian diagonal or a normal-mode frequency with an individual ktheta/kUB.

Compare full joint potential curvature, including frozen nonbonded and torsional contributions. Geometry is assessed before stiffness attribution. Compare stationary QM A/B and corresponding independently minimized MM basins, aligned/mapped consistently; record geometry differences. MM at a nonstationary QM geometry cannot be used as an interchangeable normal-mode minimum. Hessian discrepancy caused by structural mismatch must not be repaired solely with k.

[CGenFF primary study](https://pmc.ncbi.nlm.nih.gov/articles/PMC2888302/) uses geometry, vibrational character and conformational energies together. Its scaled-spectrum convention is not automatically imported: here the harmonic-curvature reference is explicitly UNSCALED MP2/6-31+G(d), scale factor1.000000 fixed. No mode-specific, basin-specific or data-fitted scale. A separate physical scaling-policy revision would require prospective approval.

## Modes and low-frequency handling

Sort projected positive eigenvalues. Assign QM/MM modes using maximum total squared overlap of atom-mapped mass-weighted eigenvectors; retain assignment ambiguity. Nearly degenerate QM modes are grouped by adjacent separation<=10 cm^-1, transitively; compare subspace principal angles, not arbitrary eigenvector signs. This10 criterion is new and only defines matching clusters. A mode's physical bond/angle/torsion participation is reported through B and eigenvectors; redundant-coordinate PED convention must be explicit.

Low-frequency subset: QM frequency<200 cm^-1, defined before B results. Keep these modes, use absolute cm^-1 errors and subspace overlap; do not apply relative-frequency percentages near zero or exclude them to improve fit. Document torsion/junction/tail participation and harmonic-versus-rotamer limitations.

Prospective validation gates for each A/B after stable geometry:
- no chemically meaningful imaginary vibrational curvature (historical qualitative integrity gate); ambiguous tiny negative roots REVIEW.
- projected mass-weighted curvature Frobenius relative error<=0.20.
- all45 assigned mode MAE<=30 cm^-1; low-frequency subset MAE<=20 cm^-1.
- nondegenerate squared overlap>=0.70; each degenerate-cluster mean squared principal cosine>=0.80.
All are NEW_PREREGISTERED_CRITERION. They allocate20% aggregate curvature error and require recognizable mode character; absolute low-mode tolerance avoids a near-zero relative error singularity. They are conservative model-validation design targets, not experimental confidence intervals. If no low subset exists record NOT_APPLICABLE, not an invented zero score. Unresolvable mapping/degeneracy invalidates that target and triggers REVIEW rather than free reassignment.

## Release decision

A+B curvature is complementary, not1326+1326 independent observations. Recompute a supported reduced target Jacobian with documented uncertainty; every proposed k direction must pass the same preregistered rank/stability framework after a separately frozen stiffness perturbation design. Do not infer k identifiability from current equilibrium/amplitude J.

STIFFNESS_RELEASE_STATUS is SUPPORTED_REDUCED_SET / INSUFFICIENT_INFORMATION / ADDITIONAL_CURVATURE_QM_REQUIRED. UB stays frozen unless all four user conditions and explicit Sol approval are satisfied; theta0/ktheta/r13/kUB must not be freed simultaneously without independent support. No default tail QM, displacement or new-minimum batch.

Runtime resources/executable/licensing/current capability and exact B launch package remain unverified here. GEO_B_HESSIAN_STATUS before numerical preflight adjudication is REVIEW; no new QM is authorized.
