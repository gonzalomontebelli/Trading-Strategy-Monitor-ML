# Portfolio Backtest Specification

## Objective

Define the historical portfolio backtest using `clean_data.csv`, `selected_traders.csv`, and `portfolio_weights.csv`.

## Current case status
- Active portfolio: single-manager pilot portfolio
- Selected strategies: 1
- Total weight: 100.0%
- In this case, the portfolio replicates exactly the single strategy's curve
- The logic is ready for multi-strategy use without changing the data contract

## Inputs
- `clean_data.csv`
- `selected_traders.csv`
- `portfolio_weights.csv`

## Combination rules
1. Filter only strategies present in `selected_traders.csv`
2. Map `target_weight_pct / 100` to each trade
3. Compute `weighted_pnl = pnl_net * weight`
4. Sort by `close_time`
5. Build trade-level and daily-level equity curves
6. Compute trade-level and daily-level drawdown
7. If 2 or more strategies:
   - Build correlation matrix by daily PnL
   - Measure risk concentration by weight
   - Detect inter-manager dependence

## Recommended outputs
- `portfolio_trade_curve.csv`
- `portfolio_daily_curve.csv`
- `portfolio_summary.json`
- `portfolio_correlation.csv` (only if 2+ strategies)

## Minimum metrics
- `total_pnl`
- `max_drawdown_trade_level`
- `max_drawdown_daily_level`
- `number_of_trades`
- `number_of_days`
- `selected_traders_count`
- `effective_weight_sum`

## Decision logic
- If portfolio backtest materially worsens vs individual baseline due to negative interaction → review weights
- If a multi-strategy portfolio reduces drawdown without destroying expectancy → valid improvement
- If correlation between strategies exceeds internal defined limit → restrict concentration

## Phase note

Since the current case has a single strategy at 100% weight, the inter-strategy interaction section is marked N/A — no non-existent metric should be forced.
