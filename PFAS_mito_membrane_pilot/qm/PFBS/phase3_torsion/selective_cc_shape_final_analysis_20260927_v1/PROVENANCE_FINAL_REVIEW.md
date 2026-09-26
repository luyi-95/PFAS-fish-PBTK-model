# Provenance final review

## Decision

`PROVENANCE_FINAL_STATUS = PASS_DETERMINISTIC_METADATA_REPAIR`

The frozen recovery receipt uniquely binds `primary__BASE` to `immutable_sources/pfbs_ani.prm`, SHA256 `24baf41553845380e9905f7419ca85cb0528dcd7652d596ca6ba83e003d05a56`. The recovered matrix has 728 rows and its SHA256 is `f3ce5cd0f5ba083b15acc6a1ffc87619cba01e189289d437f934b1b975af3b22`. The recovery input inventory SHA256 is `00f326b95b6c3c6a4c50d73560e1dc80b5bd4956f4c29eee125910cd98b3f267`; the recovery receipt SHA256 is `10a3b66465a7637fa8b3598e088ee87895c4728085ac9c8ecc50b5cc1f474225`.

The receipt states `rerun=false` and `numerical_calculations_changed=false`. No MM calculation was repeated. The original exporter SHA256 is `e16a3c630f240aafcce9473d958e708ffbedc5f10b9b2680bb5a7832ca802340`; the V3 recovery exporter SHA256 is `566b8b335836537162239512835a1cb744132326224be94d4a2b72e9f52e0b26`. The original exporter remains separately preserved and was not edited in place. The recovery class is `DETERMINISTIC_METADATA_REPAIR`.

## Checks performed for this package

- Recomputed SHA256 for recovered matrix, inventory, recovery receipt, original exporter, V3 exporter, and frozen analysis-rules file; all match the authoritative values above.
- Parsed the recovered compact export and verified exactly 728 output records.
- Verified receipt says 728 rows, PASS, no rerun, no numerical-output change, and exact BASE source binding.
- Verified matrix and frozen rules identities recorded by `SOURCE_PROVENANCE_MANIFEST.json`.
- Recomputed the package tables only from the existing recovered matrix derivatives and frozen output tables; no calculation engine was invoked.

## Limits

This establishes the provenance of the recovered export and derived analysis package. It does not assert that MM force-field parameters are scientifically acceptable. The current parameter status remains `REJECTED`; no parameter fitting or editing is authorized.

The preserved `provenance/POSTRUN_RECOVERY_CONTEXT.md` records the earlier exporter-schema recovery context. It is retained verbatim. The later source adjudication and V3 receipt bind `primary__BASE` to the exact frozen parameter file; this package preserves both records and does not rewrite the earlier note.
