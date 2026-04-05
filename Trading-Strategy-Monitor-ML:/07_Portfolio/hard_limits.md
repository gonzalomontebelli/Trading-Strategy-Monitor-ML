# Phase 6 — Risk Rules & Operational Continuity

## Purpose

Define objective rules for managing the personal trading strategy with compound growth:
- Continue operating normally
- Reduce position size
- Pause trading
- Stop the system

## Official system baseline
- `system_id`: `2026-04_Quantum_US30_SingleTrader`
- `expectancy_e`: 181.697
- `profit_factor`: 1.564
- `win_rate`: 45.97%
- `max_drawdown_pct_approx`: 14.47%
- `avg_loss_abs_proxy_risk`: 596.10
- `quality_warning_profile`: `trader_id_surrogate_case_level | timezone_unvalidated_parse_only`

## Decision rules

### CONTINUE OPERATING
Operate at normal size when all of the following are met simultaneously:
- Rolling expectancy over 20 trades > 136.27
- Rolling profit factor ≥ 1.20
- Rolling win rate ≥ 37.97%
- Observed drawdown does not exceed 16.64%
- No new structural data warnings appear
- No evident regime change in trading behavior

### REDUCE POSITION SIZE
Reduce position size if any of the following conditions occurs:
- Rolling expectancy over 20 trades falls below 136.27
- Rolling profit factor falls below 1.20
- Rolling win rate falls below 37.97%
- Observed drawdown exceeds 16.64%
- Operational changes appear that increase concentration, slippage, or unusually long holding time

### PAUSE TRADING
Pause trading if any of the following conditions occurs:
- Rolling expectancy over 20 trades ≤ 0.00
- Rolling profit factor < 1.00
- Rolling win rate < 33.97%
- Observed drawdown exceeds 19.53%
- A sustained statistical regime change is detected

### STOP THE SYSTEM
Stop and review the strategy if any of the following is confirmed:
- Persistent deterioration in 2 consecutive review windows without recovery
- Drawdown outside historical limits with no recovery signal
- Structural behavior change incompatible with the baseline
- BUY/SELL bias reversal without documented market context justification
- Data integrity issue that invalidates the historical baseline

## Compound growth rule

In a compound growth model, position size must be adjusted to available capital. This means:
- Reduction rules apply to both absolute size and percentage of capital
- A capital reduction from drawdown already reduces position size automatically
- Do NOT compensate losses by increasing size to "recover faster"

## Methodological note

These limits are governance rules for personal trading defined from the historical backtest.
They are not observed facts from post-baseline history.
They must be reviewed quarterly to assess whether the baseline remains representative.
