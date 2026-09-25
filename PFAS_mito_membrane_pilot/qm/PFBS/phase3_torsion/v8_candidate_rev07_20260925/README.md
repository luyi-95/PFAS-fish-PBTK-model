# PFBS Phase-3 v8 candidate — offline only

Exact 20 absolute points: T_CC_120, T_CC_150, T_CC_210, T_CC_240, T_CC_270, T_CC_300, T_CC_330, T_CS_000, T_CS_010, T_CS_020, T_CS_030, T_CS_040, T_CS_050, T_CS_060, T_CS_070, T_CS_080, T_CS_090, T_CS_100, T_CS_110, T_CS_120. Accepted T_CC_000/030/060/090/180 are excluded; T_CC_060 attempt04 is authoritative and is never rerun. No reverse scans. T_CC_330 retains approved +30 degree oxygen-triad seed.

Source v7 SHA256SUMS SHA256: `97ad44a6894917be5b415c9c7595755c472e98533447f7b9c8946d5e03302bb5`. CGenFF-processed Mol2 SHA256: `f5d09e21487580fa11b1ce95f575c1a8567b46234050ae0ba25b6c12f0d1af9b`. Every input differs from its v7 counterpart only by the unique v8 checkpoint path, `IOp(1/152=200)` route addition, and terminal blank line for ModRedundant grammar. Geometry, atom ordering, charge -1, multiplicity 1, MP2/6-31+G(d), Tight settings, and ModRedundant restraint are unchanged.

`V8_PACKAGE_SHA256` is defined as SHA256 of this directory's `SHA256SUMS` file and is recorded externally after freeze to avoid a self-hash cycle. `python3 -B scripts/v8_static_audit.py .` verifies the complete file inventory and all 20 grammars. The default controller mode is offline audit. Future `--launch` requires an external exact-hash Sol High review and separate explicit user authorization.

`V8_GAUSSIAN_LAUNCH = NOT_AUTHORIZED`  
`REVERSE_SCAN = NOT_AUTHORIZED`  
`PARAMETER_EDITED = NO`  
`MD_RUN_AUTHORIZATION = NOT_GRANTED`
