# Numerical null-direction and support diagnostics
This is a preregistered MM numerical-identifiability analysis package. It does not fit parameters, edit force-field files, adopt a parameter set, or issue Sol's final acceptance decision. Covariance values are unit-normalized response proxies, not statistical uncertainty estimates.
- Terminal matrix: 1736 unique state/source cells; controller status `COMPLETE`.
- Primary observable vector: 118 rows; low-tier diagnostic: 99 rows.
- Full primary effective supported rank: 9/10 at threshold 0.13790796; Frobenius uncertainty bound δ=0.027581591; machine-only tolerance=3.9121838e-14.
- Low-tier full diagnostic effective supported rank: 8/10 at threshold 0.13781459; δ=0.027562918.
## Full-primary right singular vectors
- σ1=1.4931279 (supported): R_OG2P1-SG3O1=-0.2054, R_CG312-SG3O1=-0.2996, R_CG312-CG312=+0.8018, R_CG302-CG312=+0.0476, TH_OG2P1-SG3O1-OG2P1=-0.0120, TH_FGA2-CG312-FGA2=-0.4513, TH_CG312-CG312-SG3O1=+0.0858, TH_FGA3-CG302-FGA3=-0.0587, LAMBDA_CS=-0.0888, LAMBDA_CC=-0.0195
- σ2=1.371802 (supported): R_OG2P1-SG3O1=+0.6618, R_CG312-SG3O1=+0.2995, R_CG312-CG312=+0.5032, R_CG302-CG312=-0.0698, TH_OG2P1-SG3O1-OG2P1=-0.1246, TH_FGA2-CG312-FGA2=+0.3943, TH_CG312-CG312-SG3O1=-0.1299, TH_FGA3-CG302-FGA3=+0.0207, LAMBDA_CS=-0.1611, LAMBDA_CC=-0.0017
- σ3=1.2654832 (supported): R_OG2P1-SG3O1=+0.1245, R_CG312-SG3O1=-0.0018, R_CG312-CG312=-0.0328, R_CG302-CG312=+0.9902, TH_OG2P1-SG3O1-OG2P1=-0.0023, TH_FGA2-CG312-FGA2=-0.0067, TH_CG312-CG312-SG3O1=+0.0027, TH_FGA3-CG302-FGA3=+0.0399, LAMBDA_CS=-0.0349, LAMBDA_CC=-0.0098
- σ4=1.1681249 (supported): R_OG2P1-SG3O1=-0.2946, R_CG312-SG3O1=-0.2405, R_CG312-CG312=+0.2612, R_CG302-CG312=+0.0678, TH_OG2P1-SG3O1-OG2P1=+0.3075, TH_FGA2-CG312-FGA2=+0.6380, TH_CG312-CG312-SG3O1=-0.0825, TH_FGA3-CG302-FGA3=+0.0178, LAMBDA_CS=+0.5217, LAMBDA_CC=-0.0410
- σ5=1.1230701 (supported): R_OG2P1-SG3O1=-0.6042, R_CG312-SG3O1=+0.7211, R_CG312-CG312=+0.1653, R_CG302-CG312=+0.0745, TH_OG2P1-SG3O1-OG2P1=-0.0555, TH_FGA2-CG312-FGA2=+0.1271, TH_CG312-CG312-SG3O1=-0.0789, TH_FGA3-CG302-FGA3=+0.0251, LAMBDA_CS=-0.2364, LAMBDA_CC=+0.0098
- σ6=0.74121261 (supported): R_OG2P1-SG3O1=-0.2247, R_CG312-SG3O1=-0.4662, R_CG312-CG312=-0.0554, R_CG302-CG312=+0.0055, TH_OG2P1-SG3O1-OG2P1=-0.5102, TH_FGA2-CG312-FGA2=+0.4239, TH_CG312-CG312-SG3O1=+0.0107, TH_FGA3-CG302-FGA3=+0.0749, LAMBDA_CS=-0.5321, LAMBDA_CC=+0.0154
- σ7=0.45073846 (supported): R_OG2P1-SG3O1=-0.0031, R_CG312-SG3O1=+0.0006, R_CG312-CG312=+0.0366, R_CG302-CG312=-0.0326, TH_OG2P1-SG3O1-OG2P1=-0.0936, TH_FGA2-CG312-FGA2=-0.1132, TH_CG312-CG312-SG3O1=-0.1201, TH_FGA3-CG302-FGA3=+0.9682, LAMBDA_CS=+0.1325, LAMBDA_CC=+0.0820
- σ8=0.34621129 (supported): R_OG2P1-SG3O1=+0.0298, R_CG312-SG3O1=-0.1105, R_CG312-CG312=-0.0300, R_CG302-CG312=-0.0299, TH_OG2P1-SG3O1-OG2P1=+0.7848, TH_FGA2-CG312-FGA2=+0.0803, TH_CG312-CG312-SG3O1=+0.0308, TH_FGA3-CG302-FGA3=+0.1688, LAMBDA_CS=-0.5773, LAMBDA_CC=-0.0049
- σ9=0.28391553 (supported): R_OG2P1-SG3O1=-0.0332, R_CG312-SG3O1=-0.1136, R_CG312-CG312=-0.0309, R_CG302-CG312=+0.0113, TH_OG2P1-SG3O1-OG2P1=+0.0324, TH_FGA2-CG312-FGA2=-0.1260, TH_CG312-CG312-SG3O1=-0.9393, TH_FGA3-CG302-FGA3=-0.1416, LAMBDA_CS=-0.0460, LAMBDA_CC=+0.2521
- σ10=0.10149591 (unresolved / below preregistered 5δ threshold): R_OG2P1-SG3O1=+0.0046, R_CG312-SG3O1=+0.0134, R_CG312-CG312=+0.0319, R_CG302-CG312=+0.0126, TH_OG2P1-SG3O1-OG2P1=+0.0248, TH_FGA2-CG312-FGA2=+0.0536, TH_CG312-CG312-SG3O1=+0.2550, TH_FGA3-CG302-FGA3=-0.0460, LAMBDA_CS=+0.0286, LAMBDA_CC=+0.9629
## Preregistered low-tier and fixed reduced blocks
- `MVP_EQ_CORE`: 2/2 supported; n=118, δ=0.012975587, threshold=0.064877933; status `ALL_COLUMNS_SUPPORTED`.
- `MVP_EQ_CC_CORE`: 3/3 supported; n=118, δ=0.014783674, threshold=0.07391837; status `ALL_COLUMNS_SUPPORTED`.
- `MVP_EQ_CC_CS_CORE`: 4/4 supported; n=118, δ=0.018145858, threshold=0.090729289; status `ALL_COLUMNS_SUPPORTED`.
- `MVP_SHARED_CC_GUARD`: 4/4 supported; n=118, δ=0.02046316, threshold=0.1023158; status `ALL_COLUMNS_SUPPORTED`.
- `MVP_SHARED_CC_CS_GUARD`: 5/5 supported; n=118, δ=0.023009912, threshold=0.11504956; status `ALL_COLUMNS_SUPPORTED`.
## Interpretation boundaries
- The reported unsupported right-singular vectors identify parameter combinations not resolved by the selected MM observables at the preregistered noise envelope. A highlighted |coefficient|≥0.25 is a readability aid only.
- Every block-removal result uses unchanged original row weights; subsets were not renormalized. The low-tier set preserves the common CC300 energy anchor and uses the predeclared six profile rows plus all A/B geometry and the A/B energy row.
- Step/convergence ratios and branch/constraint gates remain separate evidence. A numerically high rank does not override a failed derivative stability or local-domain screen. No parameter release/adoption follows from this package alone.
