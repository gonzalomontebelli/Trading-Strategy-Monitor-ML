# 08_Monitoring — Continuous Performance Monitoring

## What happens here

**Ongoing monitoring** after the strategy enters active trading.

The ML pipeline runs on a weekly and monthly cadence, comparing current performance against the validated historical baseline.

## Monitoring frequency

- **Weekly:** drift detection on key metrics vs baseline
- **Monthly:** deep review of all metrics with compound capital update
- **Quarterly:** full system review — reassess edge validity

## Decision framework

| Decision | When |
|---|---|
| `MAINTAIN` | Performance in line with baseline — continue normally |
| `REDUCE` | Mild deterioration signal — reduce position size to 50% |
| `PAUSE` | Clear deterioration — stop trading until next review |
| `REACTIVATE` | Was paused and shows sustained recovery |

## Traffic light signal

| State | Condition |
|---|---|
| 🟢 Green | No hard breaches, severity score below warning threshold, ML anomaly score low |
| 🟡 Yellow | Moderate drift — expectancy, win rate, or PF moved outside normal range |
| 🔴 Red | Hard breach confirmed + high severity score + ML anomaly score elevated |

## Typical files

```
08_Monitoring/
├── monitoring_config.json           → Alert thresholds and monitoring parameters
├── alert_thresholds.csv             → Threshold table by metric
├── monitoring_schedule.md           → Cadence and review calendar
├── ml_complement_spec.md            → ML layer specification
├── ml_semaforo_pipeline/            → ML monitoring pipeline package
│   ├── monitoring_ml_pipeline.py
│   ├── monitoring_config.json
│   └── README_PIPELINE_ML_SEMAFORO.md (translated below)
└── trader_medical_card.md           → Quantitative profile snapshot
```
