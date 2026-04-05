# 03_Normalization — Field Mapping & Normalization Design

## What happens here

Raw column names are mapped to the canonical schema.

**Important:** This is the logical design phase. No data transformation is executed yet.

## Canonical schema reference

The normalized trade schema uses these standard columns:
`trader_id`, `open_time`, `close_time`, `symbol`, `side`, `volume`, `pnl_net`, `pnl_gross`, `quality_flag`

## Possible verdicts

- `COMPLETE` → all required columns mapped
- `PARTIAL` → some columns missing, document how to derive them
- `INCOMPLETE` → too many columns missing to continue

## Typical files

```
03_Normalization/
├── normalization_spec.md    → Full mapping specification
├── canonical_map.json       → Original column → canonical column mapping
└── field_mapping.csv        → Field mapping table
```
