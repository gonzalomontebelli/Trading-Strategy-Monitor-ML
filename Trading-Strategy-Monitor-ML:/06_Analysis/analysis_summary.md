# Phase 5 — Quantitative Analysis — Personal US30 Backtest

## 1. Dataset analyzed
- Case: `2026-04_Quantum_US30_SingleTrader`
- Primary source: `clean_data.csv`
- Support source: `data_quality_log.csv`
- Total rows in `clean_data.csv`: 1,823
- Rows used in analysis (`quality_flag != ERROR`): 1,823
- Rows excluded: 0
- System analyzed: single (personal backtest)
- Symbol: US30
- Close time range: 2019-08-01 15:48:40 to 2026-04-02 16:42:48

## 2. Exclusions
No rows were excluded, because the phase rule specifies using only `quality_flag != ERROR` and the full dataset is flagged as `WARN`.

## 3. Observed data quality
- `quality_flag` observed: `WARN` across all 1,823 rows
- Dominant warning profile: `trader_id_surrogate_case_level | timezone_unvalidated_parse_only`

## 4. Main quantitative results
- Strategy analyzed: `2026-04_Quantum_US30_SingleTrader`
- Trades used: 1,823
- Expectancy (E): 181.70
- E/SD: 0.110
- PL/SD: 200.69
- SQN (approx): 4.700
- Win Rate: 45.97%
- Max Drawdown (approx): 55,462.99 (14.47%)
- Average risk (approx): 596.10

## 5. Required notes on approximations

### SQN (approximate)
Computed as `sqrt(n) * mean(pnl_net) / std(pnl_net)`.
Reason: the dataset does not include R-multiples or initial risk defined per trade.

### Drawdown (approximate)
Computed over the sequence ordered by `close_time`, using `balance_after_trade` and its cumulative maximum.
Reason: the phase specifies approximate drawdown; no independently validated equity curve was available.

### Average risk (approximate)
Computed as the average absolute loss on trades where `pnl_net < 0`.
Reason: no stop-loss initial column, dollar risk, or planned max loss per trade exists in the dataset.

## 6. Structural scope of this phase

This analysis fully characterizes the personal system. There is no cross-system comparison because the universe is by definition singular: one strategy on one instrument. This is not a limitation of the case — it is the correct nature of a personal backtest analysis.
