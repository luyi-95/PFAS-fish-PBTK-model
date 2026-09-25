# PFBS T_CC_060 attempt04 offline sentinel candidate

This directory records the frozen, hash-bound **offline candidate** for the T_CC_060 recovery sentinel. The six copied files are byte-for-byte copies of the frozen package. This Git commit records provenance only; it does not authorize or document a Gaussian run.

PACKAGE_SHA256 = 12778309db97ad518bc3a3a7e43f5f136a3b9e10361b3a608afce23f1486dc57
ATTEMPT04_GAUSSIAN_RUN = NOT_STARTED
AUTHORIZATION_CONSUMED = NO
STATIC_QA = PASS
GAUSSIAN_RUNTIME_ACCEPTANCE = UNVERIFIED
PARAMETER_EDITED = NO
MD_RUN_AUTHORIZATION = NOT_GRANTED

The package identifier is the SHA256 of `SHA256SUMS`. The five payload hashes are recorded in that file. The approved source checkpoint SHA256 is `95d413543e1270b1fd8a6f859c2268d966b21bc14c7be2740de3debe0aa0342d`; the checkpoint itself is not included here.

No successful local precedent was available for this same `Geom=(Checkpoint,ModRedundant)` input form. The package therefore requires an actual Gaussian 16 C.02 runtime parsing gate before scientific execution can be considered validated. `IOp(1/152=200)` is a sentinel-only run-control candidate, not a production protocol. Any invocation requires independent Sol High review and a separate explicit one-time user authorization.

The offline audits and review request describe the scientific input, checkpoint provenance, section layout, and remaining runtime uncertainties. No checkpoint, formatted checkpoint, scratch, runtime cache, license material, or large binary artifact is stored in this directory.