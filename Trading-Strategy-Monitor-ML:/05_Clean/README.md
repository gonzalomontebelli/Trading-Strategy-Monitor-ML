# 05_Clean — Cleaned & Validated Dataset

## What happens here

The final dataset, ready for analysis. Result of applying `03_Normalization` rules and passing the `04_Validation` quality gate.

## What this dataset guarantees

- Columns renamed to canonical schema
- Rows with missing critical fields removed (documented in `rejected_rows.csv`)
- Dates in uniform format (UTC-consistent)
- Correct data types throughout
- Full transformation log available

## Typical files

```
05_Clean/
├── clean_data.csv               → Canonical cleaned dataset (CSV)
├── rejected_rows.csv            → Discarded rows with rejection reason
├── data_quality_log.csv         → Log of all transformations applied
└── phase4a_scope_manifest.json  → Scope manifest for this cleaning pass
```

**This dataset is never modified manually.** If corrections are needed, update the cleaning script and regenerate.
