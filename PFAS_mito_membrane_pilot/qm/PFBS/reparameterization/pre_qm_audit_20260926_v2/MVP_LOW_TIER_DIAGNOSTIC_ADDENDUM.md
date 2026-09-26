# Prospective MVP low-tier row diagnostic and dominant-minimum clarification

Status: PREREGISTERED_BEFORE_MM_RESULTS. This supplements the scoped MVP documents. The complete118-row primary Jacobian remains intact.

## Fixed row selection

Select from accepted QM evidence only, using the already preregistered axis-relative <=1.0kcal/mol tier:
T_CC_180, T_CC_300, T_CS_050, T_CS_060, T_CS_070, T_CS_080.
MVP_LOW_TIER_ROW_DIAGNOSTIC_SPEC.json binds full source values and hashes. CC180 is0.99058175kcal/mol above CC300 and is retained; this boundary is not moved.

Report six-row energy-only diagnostics and a99-row combined diagnostic: all original92 A/B geometry rows, these six original primary energy rows, and E_B-E_A. Preserve the original CC300 common anchor, observable/parameter scales and exact row weights. No row-weight renormalization, new endpoint, per-axis recentering or future-MM-dependent selection. Apply the same derivative step/convergence/noise/rank formulas on restricted rows and show them beside the full118-row result.

These diagnostics identify where relevant low-energy information resides. They cannot replace the primary matrix, conceal failed endpoints, rescue an invalid direction, or establish release by a favorable restricted rank alone. Numerical incompleteness and a deficiency of existing QM evidence remain separate judgments. Branch-only reverseCC240 stays separately reported rather than folded into primary rows.

## Dominant sampled minimum

The MVP phrase 'QM low-tier minimum' in the dominant-basin location gate means the lowest retained sampled QM minimum: CC300 and CS70 in the bound existing evidence. A secondary local minimum inside the <=1kcal tier is not automatically another global minimum. Thus CC180 remains useful low-tier evidence but does not make a dominant MM180 preference automatically location-consistent with QM300.

Keep the already chosen one-grid-step location neighborhoods and1kcal unsupported-well budgets. This clarification changes no budget and does not assert exhaustive/global molecular free energy, temperature-dependent populations or membrane behavior. All retained profiles and secondary minima remain reported.

Final MVP A/B/C/D remains pending the authorized numerical review. No new QM, fit, adoption or MD is approved.
