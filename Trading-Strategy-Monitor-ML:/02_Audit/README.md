# 02_Audit — Structural Audit

## What happens here

The structure of the exported trade history dataset is audited.

The goal is to detect **before running any code**:
- Whether the export contains the minimum required columns for quantitative analysis
- The source platform and export format
- Data quality issues (missing PnL, inconsistent dates, duplicates)

## Possible verdicts

- `PASS` → proceed to `03_Normalization`
- `FAIL` → list what must be fixed first. Do not continue.

## Typical files

```
02_Audit/
├── audit_report.md              → Full audit report
├── audit_summary.txt            → Executive summary
├── detected_columns.csv         → Detected vs required columns
├── intake_summary_phase0.md     → Phase 0 schema detection summary
├── source_inventory_phase0.csv  → Source file inventory
├── embedded_log_schemas_phase0.csv → Embedded log schemas detected
└── config_block_phase0.json     → Schema detection config output
```
