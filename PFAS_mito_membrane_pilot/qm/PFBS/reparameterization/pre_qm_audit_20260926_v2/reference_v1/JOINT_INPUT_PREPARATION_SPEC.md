# Fixed mixed-junction design and future input preparation

The six development configurations are CC60/180/300 crossed with CS30/90. The four prospective heldouts are CC90/210 crossed with CS20/100. This partition reproduces the authoritative Sol High proposal and is fixed before new results. `JOINT_CC_CS_DESIGN.tsv` binds each accepted absolute seed, its actual achieved angles, coordinate/checkpoint paths and hashes. Independent starts are mandatory; no sequentially minimized/optimized geometry propagation is proposed.

This audit contains the **seed structures and design**, not ten launch-ready rotated inputs. The accepted seed has the correct CC but generally a different CS. A future execution package must define and validate a deterministic graph-preserving target placement for D16-14-15-1 and D14-15-1-11, then mechanically read back both target angles and apply the full PRE-QM geometry gate (graph, atom identity, all bond lengths, contact screen). On clash/ambiguous branch or topology failure, stop for review; do not choose another branch post hoc. No two-target rotated start is claimed PASS in this package.

Future scientific method remains MP2/6-31+G(d),charge-1,multiplicity1,SCF=Tight,NoSymm,OptTight with approved MaxCycles200/IOp(1/152=200) semantics; both target dihedrals are frozen, all other degrees relax. Exact route/ModRedundant grammar and actual runtime cap200 must be independently reviewed in a separate launch candidate. No Guess=Read/OptRestart/history inheritance is implied. Each output chk/scratch/log/claim belongs outside its immutable input package and is unique.

Mixed points probe off-valley coupling; they are not assumed to be unconstrained minima or barriers. Preserve every result and nonconvergence. Heldout results cannot influence fitting/weights/term selection or favorable seed replacement. The 240branch is preserved separately and not resolved by these ten nominal axes alone.

Input execution and parameter fitting readiness remain REVIEW pending exact input preparation and scientific acceptance-rule freeze. No QM is launched here.
