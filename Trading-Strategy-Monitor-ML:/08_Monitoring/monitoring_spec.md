# Monitoring Specification

## Case
- case_id: `2026-04_Quantum_US30_SingleTrader`
- portfolio_type: `single_manager_pilot_portfolio`
- current_decision: `OPERATE_WITH_RESERVATIONS`
- 1 strategy selected at 100% portfolio weight
- Quality warning carried forward: `trader_id_surrogate_case_level | timezone_unvalidated_parse_only`

## Phase 7 objective

Build the professional monitoring system:
1. Quantitative strategy profile (baseline snapshot)
2. Weekly, monthly, and quarterly tracking
3. Explicit alert system
4. Portfolio backtest
5. ML-based drift and anomaly detection

## Scope resolved in this phase

- `clean_data.csv` used as the official quantitative data source
- `selected_traders.csv` used as the official selection source
- `portfolio_weights.csv` used as the official weighting source
- `hard_limits.md` was NOT integrated in this phase; monitoring thresholds defined here do not substitute the scaling/pause policy approved in Phase 6

## Quantitative baseline profile

### Operational identity
- trader_id: `2026-04_Quantum_US30_SingleTrader`
- symbol: `US30`
- period analyzed: 2019-08-01 → 2026-04-02
- closed trades: 1,823
- active trading days: 925

### Consistency and expectancy
- win_rate baseline: 0.4597
- expectancy baseline: 181.70
- trade_std baseline: 1,650.45
- E/SD baseline: 0.1101
- SQN baseline: 4.7004
- profit_factor baseline: 1.5641

### Risk and drawdown
- max_drawdown_abs_closed_pnl: -55,462.99
- max_single_loss: -6,450.00
- avg_loss_abs: 596.10
- max_single_win: 12,147.30
- avg_win: 1,095.94

### Frequency and trading style
- holding_min_mean: 86.36
- holding_min_median: 50.57
- holding_min_p95: 260.00
- volume_mean: 9.5801
- volume_median: 2.6000
- volume_p95: 50.1300
- buy_share: 0.7553
- sell_share: 0.2447

### Concentration
- top5_wins_share_of_total_profit: 0.0562
- top10_wins_share_of_total_profit: 0.1002

## Monitoring periods

### 1. Weekly monitor
- Window: operational week aggregated by close date
- Use: early deterioration detection
- Decision: traffic light signal and size adjustment

### 2. Monthly monitor
- Window: calendar month
- Use: validate edge continuity and operational stability
- Decision: maintain, reduce, or pause based on drift persistence

### 3. Quarterly monitor
- Window: calendar quarter
- Use: review regime change and structural robustness
- Decision: strategic continuity of the strategy

## Minimum variables reviewed per period
- `pnl_net` (aggregated)
- `trades`
- `win_rate`
- `expectancy`
- `pnl_std`
- `e_sd`
- `hold_min_median`
- `buy_share`
- `volume_mean`

## Alert system

### GREEN state
- No critical threshold breached
- At most 1 warning threshold triggered
- No consecutive negative persistence
- No significant ML drift

### YELLOW state
- 2 or more warning breaches in the same period
- Or mild negative persistence
- Or ML warning-level drift
- Action: maintain with surveillance or reduce per hard limits

### RED state
- 3 or more critical breaches in the same period
- Or strong negative persistence
- Or critical ML drift
- Action: pause trading per hard limits

## Quantitative activation rules

Exact values are in `monitoring_thresholds.json`. Logic:

### Weekly
- Warning if 2+ metrics fall below / exceed the weekly warning range
- Red if 3+ metrics cross the weekly critical range
- Additional warning if 2 consecutive weeks with `pnl_net <= 0`
- Additional red if 3 consecutive weeks with `pnl_net <= 0`

### Monthly
- Warning if 2+ metrics cross the monthly warning range
- Red if 3+ metrics cross the monthly critical range
- Additional warning if 2 non-positive months within a 3-month window
- Additional red if 2 consecutive months with `pnl_net <= 0`

### Quarterly
- Warning if 2+ metrics cross the quarterly warning range
- Red if 3+ metrics cross the quarterly critical range
- Additional warning if the quarter closes with `pnl_net <= 0`
- Additional red if the quarter closes with `pnl_net < 0` AND ML drift is critical

## ML layer (lightweight unsupervised)

Implemented with `pandas` + `numpy` only:

1. **Weekly feature vector**: expectancy, win_rate, pnl_std, trades, hold_min_median, buy_share, volume_mean
2. **Robust drift score**: center = historical median, scale = historical MAD, score = mean absolute robust z-scores
3. **Regularized Mahalanobis**: measures how far the recent week is from the multivariate baseline
4. **PSI**: measures distribution drift between recent window and baseline
5. **ML final rule**:
   - Warning if robust_score ≥ p90 historical, or Mahalanobis ≥ p90, or PSI ≥ 0.20
   - Critical if robust_score ≥ p95 historical, or Mahalanobis ≥ p95, or PSI ≥ 0.35

## Portfolio backtest

Current portfolio is a single-manager pilot. Therefore:
- 1 strategy selected at 100% weight
- Portfolio equity curve = strategy equity curve
- No correlation matrix applicable in this version

The engine is prepared for multi-strategy use:
- Weight normalization
- Trade-level combination
- Daily aggregation
- Portfolio equity curve
- Trade-level and daily drawdown
- Correlation matrix for 2+ strategies

## Observed backtest metrics
- portfolio_total_pnl: 331,233.36
- portfolio_max_dd_trade_level: -55,462.99
- portfolio_max_dd_daily_level: -51,952.99

## Recommended monitoring cadence
- **Weekly**: run every Monday covering the closed week
- **Monthly**: run on the first business day of each month
- **Quarterly**: run on the first business day of each quarter
- **Incident**: trigger an ad-hoc run if a red week or critical ML anomaly appears

## Open limitations
1. `hard_limits.md` was not integrated in this phase.
2. No live execution log was loaded; no slippage or real execution control available.
3. The timezone warning remains open; dates were parsed and used as-is.
4. The `trader_id` remains case-level (not a persistent external identifier).

## Operational conclusion

The monitoring system is designed and parameterized on the real strategy baseline. It is executable and reusable for future cases with the same canonical schema. Final scaling/pause decision integration must be reconciled with `hard_limits.md`.
