# 47 — PFBS GEO_A frequency warning review

Date: 2026-09-24 (Asia/Shanghai)  
Role: PFBS_FREQUENCY_WARNING_REVIEWER, Sol High  
Scope: read-only adjudication of the completed frozen `PFBS_FREQ_GEO_A` calculation. No calculation, parameter edit, or thermochemical correction was made.

## Evidence and identity

The primary record is `qm/PFBS/frequency/PFBS_FREQ_GEO_A/PFBS_FREQ_GEO_A.log`, SHA256 `56b2bf0620ab18b1ee3517d3b2e1a7754adbba416f2737418938587fd34a4667`. The frequency input is SHA256 `d3b2a3e51b22e31c66c7818d62442e866a7c421a151c6a5c256136e96958ed58`; its preflight records the accepted GEO_A source log SHA256 `92002b1beddcae4e673181f16df95afb4a50f62abf492b952c43325bd1bedc8e` and archive-coordinate SHA256 `9a1126654fb44b7f7fec281f6d3bd862451b30d2740bfabe6e94cae4eec45b6d`. The raw log reports Gaussian 16 Revision C.02, `#P MP2/6-31+G(d) Freq SCF=Tight NoSymm`, charge −1, multiplicity 1, 17 atoms, normal termination, and a stationary point. The job wrapper exited 0. Exact warning text and local context are preserved in `45_PFBS_FREQ_WARNING_EXACT_TEXT_AUDIT.tsv`; all frequencies and leading atomic displacement magnitudes are in `46_PFBS_FREQUENCY_SPECTRUM_AUDIT.tsv`. The extractor and its supporting JSON are retained under `qm/PFBS/analysis/`.

## Exact warnings

At raw-log lines 1393–1394:

```text
 Warning -- assumption of classical behavior for rotation
           may cause significant error
```

At raw-log lines 1399–1400:

```text
 Warning -- explicit consideration of  26 degrees of freedom as
           vibrations may cause significant error
```

Both are classified **THERMOCHEMISTRY_ONLY for this result**. This is a result-specific decision after checking the stationary point and the Hessian, not a general assertion that the second warning could never flag a poor structure. Gaussian's own thermochemistry guide explicitly says the second warning can arise from a nonminimum or internal rotations; its vibrational-analysis guide explains the separate preprojection and projected frequency lists. [Gaussian thermochemistry](https://gaussian.com/wp-content/uploads/dl/thermo.pdf), [Gaussian vibrational analysis](https://gaussian.com/wp-content/uploads/dl/vib.pdf).

## Minimum and numerical check

For a nonlinear 17-atom structure, 3N−6 = **45** vibrations are expected and **45** projected `Frequencies --` values are present. **Zero** projected frequencies are negative. The lowest ten, in cm⁻¹, are **32.2563, 58.9978, 78.7249, 113.8115, 119.9931, 141.0002, 172.7343, 188.9037, 221.7838, 238.1160**; the highest is **1392.1025**. The first three values in the raw low-frequency preview equal the first three projected vibrations exactly to printed precision. The six preceding preprojection roots are −0.1462, −0.0020, −0.0014, −0.0007, 0.0688, and 0.1184 cm⁻¹; they represent near-zero external motion, **not four imaginary vibrational modes**. All are far below the 32.2563 cm⁻¹ lowest projected vibration. Gaussian's guide says HF/MP2 external rotational roots should normally be around 10 cm⁻¹ or less; these satisfy that diagnostic. [Gaussian vibrational analysis](https://gaussian.com/wp-content/uploads/dl/vib.pdf).

The lowest projected mode is soft but positive, with reduced mass 17.5076 amu and force constant 0.0107 mDyne/Å. Its largest listed Cartesian displacement magnitudes involve O3, F9, O2, O1, and F8. Modes 2–3 also mix oxygen and fluorine displacement. These are coupled soft motions, not evidence that 26 separately identified torsions exist. The frequency job's printed maximum force is 0.000001 versus the 0.000450 convergence threshold; RMS force is printed 0.000000 versus 0.000300. Gaussian prints `Optimization completed.` and `Stationary point found.` near log lines 1650–1651. The frozen input geometry was verified against the accepted GEO_A archive before this job. `Freq` was the route; these status lines are treated as the program's stationary-point check, not as a newly authorized optimization. The one alpha-MO-coefficient warning at log line 511 (88.427803) remains within the range reviewed for GEO_A optimization in report 34; basis-conditioning caution remains on record.

**Minimum judgment:** `LOCAL_MINIMUM_WITH_NUMERICAL_CAUTION`. The positive projected Hessian, well-separated external roots, tiny force, consistent input geometry, and normal completion support a local minimum. This does not prove global-minimum identity or high-accuracy thermochemistry.

## Meaning of the 26-degree warning

At 298.15 K, 26 of the 45 projected modes have vibrational temperatures below about 900 K, the low-frequency threshold described by Gaussian (about 625 cm⁻¹). The 26th is 601.3199 cm⁻¹; the 27th is 629.1914 cm⁻¹. This matches the warning count. Gaussian includes these modes as harmonic vibrations in its RRHO thermal calculation and warns that some low modes may behave as internal rotations. The count is a **thermochemical low-frequency heuristic**, not a count of proven independent rotors. No `Freq=HindRot` analysis, torsional barrier assessment, or mode-specific rotor reassignment was performed. `DOF_WARNING_INTERPRETATION = LOW_FREQUENCY_RRHO_LIMITATION`. [Gaussian thermochemistry](https://gaussian.com/wp-content/uploads/dl/thermo.pdf).

## Classical rotation and thermochemical impact

The molecule is an asymmetric top with rotational symmetry number 1. Gaussian prints principal moments of inertia 2566.7930, 4868.5697, and 5262.8211 atomic units; rotational constants 0.70311, 0.37069, and 0.34292 GHz; rotational temperatures 0.03374, 0.01779, and 0.01646 K; thermochemistry temperature 298.150 K and pressure 1 atm. Since the listed rotational temperatures are much smaller than 298.15 K, the rigid-rotor quantum-level spacing itself gives no evident reason for a poor classical limit. **The precise internal trigger of Gaussian's generic classical-rotation warning is not established by this output.** The warning concerns partition-function thermochemistry; it does not report an electronic-energy, geometry, or Hessian failure. Rotation-vibration coupling and low-frequency conformational motion still warrant caution for RRHO entropy. [Gaussian thermochemistry](https://gaussian.com/wp-content/uploads/dl/thermo.pdf).

| Quantity | Impact of these warning classes | Judgment |
|---|---|---|
| MP2 electronic energy | NO | Computed independently of the RRHO partition function; retain the separate MO-conditioning caution. |
| Optimized GEO_A geometry | NO | Stationary-point and coordinate checks stand. |
| Hessian sign / minimum identification | NO for this result | 45 projected modes positive; six external roots near zero. |
| Harmonic frequencies | CAUTION | Soft modes are real within this calculation, but low-mode values and harmonic model are sensitive; not spectroscopic claims. |
| Harmonic ZPE | CAUTION | Printed 169145.7 J/mol = 40.42679 kcal/mol, correction 0.064424 hartree, remains a usable harmonic diagnostic; soft-mode anharmonicity limits quantitative accuracy. It is not invalidated wholesale and was not used for A/B selection. |
| Entropy at 298.15 K | CAUTION | The 26 low modes, possible hindered rotations, and rigid-rotor assumptions can materially bias RRHO entropy; do not use as a validated conformational entropy. |
| Thermal enthalpy correction | CAUTION | Printed 0.080800 hartree is internally available, but its low-mode vibrational contribution retains RRHO-model uncertainty; usually less sensitive than entropy, without a quantified bound here. |
| Gibbs free-energy correction | CAUTION | Printed 0.021178 hartree inherits entropy uncertainty and is unsuitable for deciding A/B conformer ranking here. |

The log also prints total 298.15-K entropy 125.484 cal mol⁻¹ K⁻¹. These values are preserved as Gaussian output, not promoted to calibrated thermochemistry. Gaussian's documentation distinguishes harmonic ZPE from finite-temperature entropy and energy expressions. [Gaussian thermochemistry](https://gaussian.com/wp-content/uploads/dl/thermo.pdf).

## Reference selection firewall and verdict

The frozen reference choice used optimized **electronic** energies: GEO_A −1671.3418390772 hartree and revised GEO_B −1671.3410815607 hartree, with A lower by 0.0007575165 hartree (0.475349 kcal/mol). It did not use ZPE, entropy, or Gibbs free energy. `REFERENCE_SELECTION_IMPACT = NONE` from these two thermochemistry warnings. No A/B ranking is recomputed with frequency-derived free energy.

`FREQUENCY_WARNING_VERDICT = BENIGN_FOR_MINIMUM_THERMOCHEMISTRY_CAUTION`  
`REFERENCE_MINIMUM_STATUS = CONFIRMED_WITH_CAUTION`  
`QM_PHASE1_STATUS = PASS` for the **QM geometry/reference-minimum/frequency gate only**. The existing MO numerical caution remains documented. The separate CGenFF-versus-QM geometry, water/ESP, and torsion acceptance gates in report 29 have not been satisfied by this frequency job; no PFBS force-field parameter is released by this verdict.

No additional QM diagnostic is scientifically required **before the next frozen QM phase solely because of these two warnings**. Any downstream calculation still requires its own explicit authorization and normal preflight. No quasi-RRHO, mode cutoff, hindered-rotor, free-rotor, or manual-frequency correction is introduced.

`PARAMETER_EDITED = NO`  
`QM_RUN_AUTHORIZATION = NOT_GRANTED`  
`DOWNSTREAM_QM_AUTHORIZATION = NOT_GRANTED`  
`MD_RUN_AUTHORIZATION = NOT_GRANTED`
