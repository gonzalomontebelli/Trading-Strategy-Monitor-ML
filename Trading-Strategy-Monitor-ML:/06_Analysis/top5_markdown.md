# Quantitative System Summary — Personal US30 Backtest

## Analysis Scope
- **Analyzed System:** 1 (Operator's personal backtest)
- **Eligible Trades:** 1823 of 1823
- **Exclusions due to `quality_flag = ERROR`:** 0

## Result

| System | Trades | E | E/SD | PL/SD | Approx. SQN | % Winners | Approx. Max DD | Approx. Avg Risk |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026-04_Quantum_US30_SingleTrader | 1823 | 181.70 | 0.1101 | 200.6924 | 4.7004 | 45.97% | 14.47% | 596.10 |

## Interpretation Note

This is a single-system analysis: there is no comparison between external strategies. The metrics fully characterize the historical edge of the proprietary system over US30. The analysis is, by definition, unitary and non-degenerate—it is the correct way to evaluate a personal backtest.

## Methodological Warnings

* **SQN** is calculated as a proxy based on `pnl_net` per trade rather than R-multiples, as the dataset does not include ex-ante risk per operation.
* **Drawdown** is approximate and calculated over the chronological sequence by `close_time` using `balance_after_trade`.
* **Average Risk** is approximated as the average absolute loss of losing trades, as there is no field for initial stop or planned risk per trade.
