# Prospective heldout 2D design review

HELDOUT_DESIGN_STATUS=REVISED_AND_FROZEN. No new QM outcomes used. Six development points remain CC60/180/300 crossed with CS30/90.

## Frozen four points and separation

| CC | CS | Accepted existing seed | Coverage |
|---:|---:|---|---|
|90|60|T_CC_090|Interior CS midpoint, CC unseen in six-point development; prospective mixed-region test|
|210|0|T_CC_210|CS seam far from both development levels; alternate CC region|
|330|60|T_CC_330|Interior CS midpoint near CC300 basin region, off existing adiabatic trajectory|
|270|0|T_CC_270|CS seam and distinct CC transition region; not mirror duplicate of90/60|

HELDOUT_2D_DESIGN_FROZEN.tsv binds exact source geometry/checkpoint paths/hashes, partition and offline gate. It is a design/seed receipt, not four Gaussian-ready inputs.

For angular periodP define d_P(a,b)=min(abs(a-b)modP,P-(abs(a-b)modP)).
Ordinary labelled metric uses CC360/CS360; conservative equivalent-O screening uses CC360/CS120:
D=sqrt((d_CC/360)^2+(d_CS/120)^2).
Also report Euclidean degree distance and the minimum under nominal mirror(CC,CS)->(-CC,-CS). All four new points have nearest development deltas30/30degrees, degree-distance42.42640687 and conservative normalizedD=0.26352314. Old heldouts had30/10degrees,31.62277660 andD=0.11785113. The closest CS separation therefore rises from10 to30degrees. On the120 quotient,0 and60 are maximally distant from the two30/90 development levels; this is a transparent geometric design argument, not a promise of independent energetic constraints or rank.

Every heldout-to-each-development distance is preserved in root audit HELDOUT_PERIODIC_DISTANCES.tsv, with labelled360/360 and conservative360/120 metrics and mirror quotient. No future QM energy determined these coordinates.

## Symmetry and branch limits

Nominal CS120 periodicity is a conservative quotient for design redundancy screening, not proof an arbitrary120degree physical rotation of a distorted SO3 is an exact O permutation. Keep full O dihedral triplets and atom-equivalent geometry mapping.

Initial proposed CC150/CS0 was removed because it is nominal mirror-equivalent to CC210/CS0. An alternative CC0/CS0 failed the existing contact screen (minimum nonbonded1.91325094Angstrom with new short contact) and was rejected before QM; no gate waiver. CC270/CS0 passes and preserves2CS0+2CS60 coverage. Draft alternatives and rejection receipts remain in root audit.

The final four have no pairwise nominal mirror duplication. Root's full graph/charge-preserving288-automorphism proper/mirror alignment audit of heldout-vs-development and heldout pairs records minimum proper RMSD0.414806Angstrom and mirror RMSD1.067300Angstrom. These show the preview structures are not identical under those checked mappings; they do not certify separate dynamical basins or equal/different energies. The prospective four-point set is a stronger sparse generalization challenge, not a complete2D landscape.

## Offline feasibility, exact bound records

Final offline receipt SHA256 e3bd364e5deaf726e9110513e70cde6b313e8fb3fbf05d20d74578b595842bd4; rotation-script SHA256957c23c5c1c564acda2c452ca7c3f0cc49447ba53fba50a46a6a097d1a9a4a22. Coordinates come from the accepted17-atom table/source G96 texts; directed fourth-side graph-preserving Rodrigues rotation with CC thenCS, signed target readback. All four pass existing conservative short-contact/graph/bond-preservation screens; minimum nonbonded distances2.16890–2.18035Angstrom; achieved CC/CS agree at floating-point readback precision. This is an offline preview only: actual immutable Gaussian launch input grammar/coordinates/resources/hashes need fresh exact-package review.

Full symmetry table SHA c7ab3ea829d9a173404fd2b28507b994baf3e57eca91461b8577efc1939e8130; O-permutation-angle table SHA f9ff1f07c9d16f5e4e33e1aac890728c19a7e20bf29996a6cf80de691ad1cd0d; periodic-distance table SHA48e517894f9a22d55c9404460c4b7a4b650b823c80f0af3b493cdd3ddd179fb9.

## Sealing and failure policy

Freeze before new joint QM. Prefer calculate/expose these four only AFTER one final model is frozen from development data. If logistics later require early calculation, custodian must implement real encrypted/procedural access separation; readable files plus hashes do not constitute sealing. Heldouts never choose variables, weights, bounds, regularization, restarts, seeds or model form.

Nonconvergence, branch ambiguity, changed chemistry/source or clash invalidates the relevant validation and triggers STOP/REVIEW. No post-result substitution/averaging or second fit using these data. Existing A/B,25main profile points and CC240 branches have already been examined and remain development/diagnostic, not newly blind holdouts.

Current launch/QM authorization remains NOT_GRANTED; task stops after v2 upload/review.
