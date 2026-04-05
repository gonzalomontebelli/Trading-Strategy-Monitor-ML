# 11_Code — Pipeline Source Code

## Purpose

All Python scripts for this project. The pipeline is split into numbered phases (data processing) and a monitoring layer (ML-based drift detection).

## Pipeline scripts (numbered phases)

```
11_Code/
├── phase0_schema_detective.py               → Auto-detect CSV structure, columns, time spans
├── phase1_structural_audit.py               → Validate row integrity, duplicates, nulls
├── phase2_generate_normalization_artifacts.py → Build canonical field mapping artifacts
├── phase3_validation_check.py               → Quality gate — Go/No-go decision
├── phase4a_clean_data.py                    → Apply cleaning rules, produce canonical dataset
├── phase5_quant_analysis.py                 → Full quantitative metrics computation
└── phase6_portfolio_builder.py              → Compound capital plan and scaling framework
```

## Monitoring scripts

```
11_Code/
├── pipeline_clean.py          → Standalone data validation and cleaning (production-ready)
├── metrics_engine.py          → Trade-level, weekly, monthly, quarterly metrics
├── portfolio_engine.py        → Portfolio backtesting with weights and hard limits
├── monitoring_engine.py       → ML drift detection, alert generation, traffic light logic
├── monitoring_ml_pipeline.py  → End-to-end monitoring pipeline entry point
└── config_case.json           → All paths, thresholds, and parameters
```

## Code rules

- Every script has a docstring explaining what it does
- `config_case.json` centralizes all parameters (paths, thresholds, filters)
- No hardcoded absolute paths — use paths relative to the project root
- Scripts validate required columns before operating

## Dependencies

- Python 3.10+
- pandas
- numpy
- scikit-learn (for `IsolationForest` in monitoring)

## Suggested execution order

```bash
python phase0_schema_detective.py
python phase1_structural_audit.py
python phase2_generate_normalization_artifacts.py
python phase3_validation_check.py
python phase4a_clean_data.py
python phase5_quant_analysis.py
python phase6_portfolio_builder.py

# Then run monitoring:
python monitoring_engine.py --config config_case.json
```
