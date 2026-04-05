# ML Complement Specification — Personal US30 System

## Status
Logical design only.
**Not trained in this phase** — `clean_data.csv` and rolling trade/week-level features required.

## Objective
Use lightweight ML as a complement to the main quantitative analysis of the personal system — never as a replacement for operational judgment.

## Recommended approach

### Model 1 — Drift detection
- Type: rolling comparison vs baseline
- Suggested algorithm: multivariate z-score or control chart
- Features:
  - Rolling expectancy
  - Rolling profit factor
  - Rolling win rate
  - Rolling average holding time
  - Rolling average volume
  - Rolling drawdown

### Model 2 — Anomaly detection
- Type: unsupervised
- Suggested algorithm: Isolation Forest
- Features:
  - Sharp volume change
  - Sharp holding time change
  - BUY/SELL directional bias shift
  - Consistency loss
  - Profit factor drop

## Governance rule
- ML can raise an alert about possible system drift
- ML alone cannot invalidate the operational continuity thesis
- The final decision remains governed by:
  - Rolling quantitative metrics
  - Continuity rules (hard limits)
  - Direct observation of personal trading behavior

## Expected output when implemented
- `ml_drift_report.csv`
- `ml_anomaly_flags.csv`
- Complementary alert score
