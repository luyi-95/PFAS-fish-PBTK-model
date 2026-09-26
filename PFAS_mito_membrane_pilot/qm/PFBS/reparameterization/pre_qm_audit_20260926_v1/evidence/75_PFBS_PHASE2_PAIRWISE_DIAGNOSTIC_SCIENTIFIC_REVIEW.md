# 75 — PFBS Phase 2 pairwise diagnostic and scientific decision

Date: 2026-09-24. Scientific supervisor decision under the PFBS-only long-horizon validation authorization. The reviewed data are the frozen Phase 2 QM/MM comparison (68, 73–74), common-grid ESP (60–61), and the independent 22-geometry pair audit at `qm/PFBS/analysis/phase2_nonbonded_pair_audit_20260924/`. No parameter, structure, or prior result was changed for this decision.

## Numerical integrity

The 22 geometries contain 1,122 PFBS–TIP3P atom pairs (17 × 3 × 22). All 138 source-file hashes matched the project manifest. Independent pair sums match the existing analytical results within 1.1 × 10^-6 kJ/mol and the recorded GROMACS interaction results within 3.2 × 10^-4 kJ/mol. The audit used the effective frozen topology, including CHARMM TIP3P hydrogen LJ; it found no matching NBFIX override. Its pair decomposition therefore explains the recorded MM energy, without introducing an alternate force field.

## Physical diagnosis

At O1···Ow = 2.40 Å, W-A has Coulomb −59.8224 and LJ +42.8650 kJ/mol; W-B has −59.2395 and +42.7843. At 2.60 Å, W-A has −48.1348 and +10.5178; W-B has −47.7624 and +10.4520. The attractive Coulomb term exceeds the repulsive LJ term at both distances, while the steep LJ term sets much of the short-range wall. `MM_CONTACT_MECHANISM=MIXED_COULOMB_ATTRACTION_AND_LJ_WALL`.

The dominant repulsive LJ pair at W-A 2.40 Å is PFBS O1/OG2P1 × water OW/OT (+36.5820 kJ/mol). The same pair contributes +11.5709 kJ/mol at 2.60 Å. OG2P1 × water HT and nearby fluorine × OT also contribute; the latter includes F7/FGA3 × OW/OT. This localizes the MM wall but does not establish that OG2P1, OT, or their mixing rule is erroneous.

At matched target O···Ow distances, O1/O2/O3 have identical target oxygen charge/type (−0.550 e, OG2P1). Their direct target-oxygen Coulomb and LJ sums differ by less than 9 × 10^-7 and 8 × 10^-8 kJ/mol, respectively. Whole-molecule energies differ because the other 16 PFBS atoms have different distances and orientations to water. `SITE_DIFFERENCE=MULTIPAIR_GEOMETRY`, not unequal sulfonate-oxygen parameters.

The QM/MM residual remains distance dependent: W-A/W-B MM minus counterpoise-corrected QM is −5.988/−6.887 kcal/mol at 2.40 Å, −3.891/−4.569 at 2.60 Å, and −0.022/−0.019 at 3.60 Å. MM minima occur 0.15/0.20 Å closer than QM, with own-minimum energy differences −1.398/−1.676 kcal/mol. The QM repulsive 2.40 Å contact remains MM attractive. The common-grid ESP has a coherent local headgroup bias, but neither the ESP nor the classical pair split is a QM interaction-energy decomposition. `QM_MM_ERROR_CAUSE=UNRESOLVED`; a unique charge or LJ defect has not been demonstrated. The O2/O3 checks show the same residual sign with smaller magnitude.

## Decision and scope

`NONBONDED_PARAMETERS_ACCEPTED_WITH_CAUTION`. Retain the original CGenFF 5.0 charges and LJ values. The existing model preserves an interior favorable contact, W-A/W-B ordering, O-site parameter equivalence and near-exact long-distance interaction, while the localized short-contact bias is material and must be carried as a limitation. The evidence does not justify an identifiable smallest local parameter edit. Refitting one pair against the gas-phase curve could disturb the jointly calibrated CHARMM additive water/membrane balance without an independent condensed-phase target. This is a minimum-sufficient decision to continue *parameter validation*, not a claim that membrane behavior or transferability has been validated.

`CHARGE_STATUS=ACCEPT_CURRENT_CHARGES_WITH_CAUTION`.

`LJ_STATUS=ACCEPT_CURRENT_LJ_WITH_CAUTION`.

`PARAMETER_CHANGE_REQUIRED=NO_SPECIFIC_DEFECT_DEMONSTRATED`.

`PHASE2_STATUS=PASS_WITH_CAUTION`.

`PHASE3_TORSION_VALIDATION=AUTHORIZED_WITH_PRE_QM_GATE` under the current long-horizon PFBS-only authorization; use frozen 27/29/38, corrected graph-derived C2-side selection including F3/F4, and 4-way Gaussian resource gates.

`PFBS_MEMBRANE_READINESS=NOT_YET_DECIDED`; Phase 3 and final cross-target review remain.

`PARAMETER_EDITED=NO`.

`MD_RUN_AUTHORIZATION=NOT_GRANTED`.

The historical review at 73/74 correctly reported the evidence available then. This 75 review resolves its targeted pair-audit request and supersedes its intermediate Phase 2 status without altering the historical record.
