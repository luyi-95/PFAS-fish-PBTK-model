# Prospective interpretation of terminal convergence and physical energy

Status: PREREGISTERED_IMPLEMENTATION_CLARIFICATION_BEFORE_MM_RESULTS.
This addendum reads NUMERICAL_IDENTIFIABILITY_PROTOCOL.md section 2 without changing the ten variables, ±h/±2h endpoints, 41+21 state matrix, force tolerances, steps, physical model or branch/noise rules.

## Convergence interpretation

Acceptance of the completed two-stage minimization requires the terminal CG Fmax <= 1.0 kJ/mol/nm for primary states or <= 0.1 for the preregistered tight audit. LBFGS is the preparatory stage within the same state. Its finite normal termination above tolerance may transfer once to the already scheduled CG stage. Record the raw LBFGS termination and Fmax without labeling that stage converged.

Both stages must complete without execution error, nonfinite quantities or an unapproved warning. Terminal CG above tolerance is NONCONVERGED and stops the affected execution program; no added stage, step change, tighter unplanned tolerance or rescue restart is permitted. Preserve both stages and all unsuccessful records. CG is evaluated against the actual final force, not a textual inferred step count.

This interpretation is scientifically consistent with the planned sequential minimization: the final structure is the CG result. Requiring an intermediate result to pass the same tolerance would introduce an extra prerequisite absent from the frozen two-stage/final-Fmax wording. The original v1 profile helper likewise records both forces but gates final convergence on CG. Official GROMACS describes the force stopping criterion and the usefulness of CG closer to a minimum: [Energy minimization](https://manual.gromacs.org/current/reference-manual/algorithms/energy-minimization.html).

## Restraint-free physical energy

Use the prior v1 evaluation convention: physical topology without scan dihedral restraints, integrator md/nsteps1 TPR, and mdrun -rerun cg.trr. Read the final Potential row, bound to the final CG trajectory frame and its serialized final coordinates. This is an energy evaluation without coordinate updating. The physical TPR must preserve all selected parameter changes and every frozen interaction.

A zero-step energy evaluation can in principle be valid with exact same-coordinate/same-physics evidence. The current workflow adopts the already documented rerun convention to avoid an unverified alternative implementation. This is a mechanical evaluation clarification, not an additional minimization, MD trajectory, parameter variable or scientific repair cycle. Official GROMACS states that rerun evaluates supplied coordinates without update/constraint algorithms: [Rerun documentation](https://manual.gromacs.org/current/user-guide/mdrun-features.html#re-running-a-simulation).

## Execution boundary

This addendum does not approve a runner version. Independent approval must bind the corrected runner, manifest, source hashes and active TPR semantic preflight. No reviewer engine calculation, fitting, parameter adoption or MD is performed or authorized.
