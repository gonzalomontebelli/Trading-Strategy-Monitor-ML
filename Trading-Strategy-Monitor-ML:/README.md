# Trading Strategy Monitor — Quantitative ML Pipeline

> End-to-end quantitative analysis and monitoring system for a personal US30 (Dow Jones) trading strategy, with ML-based anomaly detection and a traffic-light continuity signal.

---

## Overview

This project implements a full quantitative pipeline to audit, normalize, analyze, and monitor a personal trading strategy on US30. The system processes raw trade history exports (CSV), computes key quantitative metrics, builds a capital management plan with compound growth, and monitors live/ongoing performance using statistical rules and unsupervised Machine Learning.

The goal is not to predict the market. The goal is to detect when the strategy **deviates from its own validated historical pattern** — early enough to act, without overreacting to normal statistical noise.

---

## Key Metrics (Baseline — Aug 2019 to Apr 2026)

| Metric | Value |
|---|---|
| Trades analyzed | 1,823 |
| Time range | Aug 2019 — Apr 2026 |
| Total historical PnL | 331,233.36 |
| Expectancy (E) | 181.70 per trade |
| SQN (approx) | 4.70 |
| Profit Factor | 1.56 |
| Win Rate | 45.97% |
| Max Drawdown (approx) | 14.47% |

---

## Architecture

```
Raw trade history (CSV)
        │
        ▼
Phase 0 — Schema Detective         Detect structure, columns, schemas
        │
        ▼
Phase 1 — Structural Audit         Validate integrity, duplicates, nulls
        │
        ▼
Phase 2 — Normalization            Canonical field mapping, type casting
        │
        ▼
Phase 3 — Validation               Go / No-go decision with documented blockers
        │
        ▼
Phase 4 — Data Cleaning            Apply rules, flag quality (OK / WARN / REJECT)
        │
        ▼
Phase 5 — Quantitative Analysis    Expectancy, SQN, Profit Factor, Drawdown, etc.
        │
        ▼
Phase 6 — Portfolio / Capital Plan Compound growth model, scaling rules, hard limits
        │
        ▼
Phase 7 — Monitoring               Weekly/Monthly ML drift detection + traffic light
```

---

## Monitoring System — Traffic Light

The monitoring layer learns the strategy's historical behavior and flags deviations across two layers:

**Layer A — Robust statistical rules**
Compares each week and month against the historical baseline using:
- Rolling expectancy, win rate, profit factor
- PnL volatility, trade frequency, position size stability
- Loss streaks, BUY/SELL bias, holding time

**Layer B — Unsupervised ML (IsolationForest)**
Trains one model per horizon (weekly / monthly) to detect anomalous periods relative to the strategy's own history.

### Signal States

| State | Meaning | Action |
|---|---|---|
| 🟢 Green | Within normal historical range | Operate normally, adjust size to current capital |
| 🟡 Yellow | Moderate drift or mixed signals | Hold size, do not scale, review next period |
| 🔴 Red | Strong drift or regime change detected | Pause trading, review quantitative profile |

The system is designed to **avoid overreacting to normal noise**: red requires a combination of hard limit breach + severity score + ML anomaly score, not a single bad week.

---

## Project Structure

```
.
├── README.md
├── requirements.txt
├── .gitignore
│
├── 01_Raw/                  Raw input files (unmodified)
├── 02_Audit/                Schema detection outputs, integrity reports
├── 03_Normalization/        Canonical field mapping, normalization spec
├── 04_Validation/           Go/no-go checklist, blockers, decision log
├── 05_Clean/                Cleaned canonical dataset, rejection log
├── 06_Analysis/             Quantitative metrics, rankings, summaries
├── 07_Portfolio/            Capital plan, compound growth model, hard limits
├── 08_Monitoring/           Monitoring config, ML pipeline, alert thresholds
├── 09_Reports/              Executive summaries, system presentations
├── 10_Deliverables/         Final outputs and artifacts
├── 11_Code/                 Python source code (pipeline + monitoring)
└── 12_ML_Examples/          Sample outputs from ML monitoring runs
```

---

## Source Code

All pipeline logic lives in `11_Code/`:

| Script | Purpose |
|---|---|
| `phase0_schema_detective.py` | Auto-detect CSV structure, column types, time spans |
| `phase1_structural_audit.py` | Validate row integrity, duplicates, nulls |
| `phase2_generate_normalization_artifacts.py` | Build canonical field mapping |
| `phase3_validation_check.py` | Go / No-go decision with documented blockers |
| `phase4a_clean_data.py` | Apply cleaning rules, produce canonical dataset |
| `phase5_quant_analysis.py` | Full quantitative metrics computation |
| `phase6_portfolio_builder.py` | Compound capital plan, scaling framework |
| `pipeline_clean.py` | Standalone clean pipeline (production-ready) |
| `metrics_engine.py` | Trade-level, weekly, monthly, quarterly metrics |
| `portfolio_engine.py` | Portfolio backtesting with weights and hard limits |
| `monitoring_engine.py` | ML drift detection, traffic light alerts |
| `monitoring_ml_pipeline.py` | End-to-end monitoring pipeline entry point |

---

## Installation

```bash
git clone https://github.com/your-username/trading-strategy-monitor.git
cd trading-strategy-monitor
pip install -r requirements.txt
```

---

## Usage

Run the pipeline in sequence:

```bash
python 11_Code/phase0_schema_detective.py
python 11_Code/phase1_structural_audit.py
python 11_Code/phase2_generate_normalization_artifacts.py
python 11_Code/phase3_validation_check.py
python 11_Code/phase4a_clean_data.py
python 11_Code/phase5_quant_analysis.py
python 11_Code/phase6_portfolio_builder.py
```

Run the monitoring engine:

```bash
python 11_Code/monitoring_engine.py --config 11_Code/config_case.json
```

---

## Requirements

- Python 3.10+
- pandas
- numpy
- scikit-learn (IsolationForest)

---

## Input Format

The pipeline expects a CSV export of closed trades with the following minimum columns:

| Column | Description |
|---|---|
| `Entry time` | Trade open timestamp |
| `Closing time` | Trade close timestamp |
| `Symbol` | Instrument (e.g., US30) |
| `Net $` | Net PnL per trade |
| `Gross $` | Gross PnL per trade |
| `Quantity` / `Volume` | Position size |
| `ID` | Trade identifier |

After normalization, the canonical schema uses: `trader_id`, `open_time`, `close_time`, `pnl_net`, `volume`, `side`, `quality_flag`.

---

## Capital Management Philosophy

The system operates on a **compound growth model**:
- Position size is adjusted proportionally to current capital each cycle
- Losses automatically reduce position size (built-in protection)
- Scale-up only after 3 consecutive months of performance consistent with the baseline
- Mandatory drawdown protection: reduce size when observed drawdown exceeds 75% of historical maximum

---

## Changelog

| Date | Phase | Event |
|---|---|---|
| 2026-04 | Phase 0 | Dataset accepted with reservations. No native trader_id; timezone not fully validated. |
| 2026-04 | Phase 1 | ADVANCE\_WITH\_RESERVATIONS — structurally sound; no duplicates or nulls. |
| 2026-04 | Phase 3 | Fallback F4A approved — proceed without TZ conversion or log join. |
| 2026-04 | Phase 5 | 1,823 trades analyzed. Positive expectancy. SQN ≈ 4.70. Max DD ≈ 14.47%. |
| 2026-04 | Phase 6 | Compound capital plan defined. Quantitative edge validated as operationally usable. |

---

## License

MIT License — see [LICENSE](LICENSE) for details.
