# 26 — Minimum scientifically sufficient PFBS QM plan

Status: **design only**. `QM_RUN_AUTHORIZATION = NOT_GRANTED`; `MD_RUN_AUTHORIZATION = NOT_GRANTED`. No QM input was submitted or calculation run. This is a focused validation plan for the real PFBS CGenFF 5.0 initial stream, not a request to rebuild a general PFAS force field. All targets are gas-phase/explicit-water molecular targets independent of membrane insertion, cardiolipin contacts, mixture effects, ROS, or Damião diffusion.

## Rationale and task count

`MINIMUM_SCIENTIFICALLY_SUFFICIENT_QM_SET = 4 target families`:

1. PFBS− minimum geometry and local vibrational sanity (S1–C2, C1–C2, C1–C2–S1, S1–O1/O2/O3).
2. Sulfonate–water interaction and anion ESP checks for the existing charge assignment, emphasizing C2 charge penalty 54.3, C1 52.491, S1 46.488, and the three O atoms.
3. A relaxed C3–C1–C2–S1 scan about C1–C2 for the 122.9 and 117 torsion families.
4. A relaxed C1–C2–S1–O1 scan about C2–S1 for the 67 and 98 torsion families; O2/O3 symmetry and F3/F4-linked components are evaluated against the same rotation profile.

A fifth representative tail-only scan (F7–C4–C3–C1, assigned penalty 22.1) is **conditional**, triggered only by a tail-conformer discrepancy in tasks 1–4. No scan of every C–F/C–C torsion is planned. The two junction scans are required because the highest penalties span two different rotation axes.

## Proposed target chemistry and levels

Use unchanged PFBS− connectivity with total charge −1, singlet multiplicity, no counterion in the intrinsic-molecule calculations. Record exact input/output hashes, software/version, coordinates, constraints, charge/multiplicity, basis/ECP availability, convergence thresholds and all warnings before interpreting data.

| Target | Proposed QM method and basis | Why |
|---|---|---|
| Geometry and harmonic frequencies | MP2/6-31+G(d) for the anion; optimize at least two distinct starting conformers near the C1–C2 and C2–S1 rotations, then frequency-check each retained minimum | Original CGenFF methodology specifies diffuse functions for anions in geometry optimization. Frequency checks identify non-minima and inform local bond/angle stiffness. |
| Anion electrostatic potential | MP2/6-31+G(d) at the optimized conformer(s); compare the **existing** CGenFF charge model's ESP over the sulfonate/junction region | CGenFF 5.0 development used diffuse MP2/6-31+G(d) ESP for anions; retain integer charge and equivalent O constraints. |
| Explicit-water headgroup probes | Published CGenFF sulfur-contact reference: MP2/6-31G(d) with counterpoise BSSE correction, fixed TIP3P water geometry and restricted monohydrate approach-distance optimization. Also compute MP2/6-31+G(d) counterpoise sensitivity for the anion at the same orientations; report both before any fit. | CGenFF 5.0 treats sulfur-containing water interactions by MP2 with counterpoise and without the neutral-compound 1.16 energy scaling or −0.2 Å offset. Diffuse-basis sensitivity matters for PFBS−. |
| Junction potential-energy surfaces | Relaxed constrained MP2/6-31+G(d) scans on PFBS−; preserve total charge −1 and multiplicity 1 | Heavy-atom torsion PES is the CGenFF bonded target; diffuse basis is the anion adaptation. |

For water probes, construct two acceptor-directed H–water approaches around a representative sulfonate O, then rotate the same motifs over O1/O2/O3 to test equivalence and steric access: six prescribed monohydrate placements. Keep the PFBS geometry fixed to the selected QM minimum and the water internal geometry fixed while optimizing the approach distance; record interaction energy, minimum distance, orientation and counterpoise correction. The anion ESP supplements water interactions for the less directly solvent-exposed C1/C2/F1–F4 charge cluster. The CGenFF charge objective should prioritize water-contact energies/distances and ESP; an ionic dipole magnitude is not a neutral-molecule 30% scaling target.

## Prespecified scans and comparison

| Axis | Defining dihedral | Grid | Terms interrogated |
|---|---|---|---|
| C1–C2 | C3–C1–C2–S1 | 12 points: −180°, −150°, …, +150° (30° spacing) | `CG312–CG312–CG312–SG3O1` penalty 122.9, and coupled `SG3O1–CG312–CG312–FGA2` penalty 117. |
| C2–S1 | C1–C2–S1–O1 | 12 points: −180°, −150°, …, +150° | `CG312–CG312–SG3O1–OG2P1` penalty 67 and `FGA2–CG312–SG3O1–OG2P1` penalty 98. |

At each point, constrain only the named dihedral and relax other internal degrees of freedom; save the optimized structure and actual achieved angle. Compare **relative** QM and initial-MM energies on matched geometries and matched scan constraints. Treat the two scans as coupled: use one common global-minimum energy reference when judging relative conformers, and check for hysteresis or alternate minima. A failed or discontinuous point is preserved and reviewed, not silently omitted. No fit, parameter replacement, or extra scan is authorized by this plan.

## Prospective evaluation and possible fit, subject to new approval

1. Confirm minima have no imaginary vibrational mode; inspect S–C, S–O, C–C, and junction angles. Use the original CGenFF geometry guidance of approximately 0.03 Å and 3° as diagnostic targets, with particular attention to the S1–C2 bond and C1–C2–S1 angle. Compare relevant lower-frequency modes and mode character, rather than matching frequencies alone.
2. For the six water placements, report every QM versus initial-MM energy and distance residual, the ordering of orientations, and sensitivity to the diffuse basis. The 2010 CGenFF ideal of 0.2 kcal/mol energy agreement is a fitting aspiration, not an automatic pass threshold for this charged sulfonate. Large basis sensitivity or different orientation ranking triggers scientific review before charge fitting. Retain CGenFF 5.0 LJ values unless separate independent evidence justifies a new nonbonded model.
3. For each scan, compare minima locations, low-energy profile (within 5 kcal/mol of the global minimum) and barrier heights. If the initial model fails, any proposed CGenFF-style fit should change **only implicated local terms** while holding the total charge, base topology and unrelated C–F/C–C parameters fixed. Fit coupled Fourier components around an axis together against relative energies, with low-energy conformers weighted more heavily; preserve a table of QM/MM residuals before and after. A pilot review target is approximately ≤0.5 kcal/mol RMS in the low-energy scan region, without distorted conformer ordering; this is a proposed decision criterion, not a published universal cutoff.
4. If charge adjustment becomes necessary, fit the S/O/C1/C2/F1–F4 cluster against water energies/distances and MP2 anion ESP with a restraint toward the original CGenFF charges, preserve total −1 and the three O equivalents, and recheck geometry/scans after any change. Follow CGenFF's self-consistent iteration rather than using AMBER RESP charges. No numeric change occurs at this stage.
5. Add the optional tail-only F7–C4–C3–C1 scan only if the selected conformer energies/geometry show a fluorocarbon mismatch traceable to the 22.1-penalty analog. Do not expand to full-chain scans by default.

## Gates before any execution or homolog transfer

Execution requires a separately approved frozen QM protocol with exact QM software and version, inputs, method implementation, convergence settings, scan constraints, cost estimate, warning policy, and output/hashing plan. The 2025 CGenFF sulfur-water reference and the anion diffuse-basis sensitivity must remain distinct; if they disagree materially, the reviewer selects the fitting target before optimization. `TARGETED_QM_EXECUTION_ALLOWED_NOW = NO` because authorization has not been granted.

After PFBS passes target-independent validation, PFHxS/PFOS reuse remains conditional on same-version CGenFF streams, matching local atom types/connectivity, compatible charge environments and term-level comparisons. Additional CF2 units and terminal-end effects are separately reviewed. No membrane outcome may be used to choose charges, torsions, or acceptance thresholds.

## Method sources

- [CGenFF 5.0 development and target hierarchy](https://doi.org/10.1021/acs.jctc.5c00046): water/ESP/PES targets, sulfur-water MP2 counterpoise exception, anion ESP diffuse basis, hierarchical parameter transfer.
- [Original CGenFF parameterization methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC2888302/): MP2/6-31+G(d) anion geometry, explicit-water charge strategy, bond/angle geometry guidance, relaxed torsion scans and low-energy emphasis.
- [MacKerell Lab parameter-development guidance](https://mackerell.umaryland.edu/ff_dev.shtml): consistency of water interaction methods with CHARMM.
