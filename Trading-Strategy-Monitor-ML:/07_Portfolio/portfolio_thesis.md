# Phase 6 — Personal Capital Management Plan with Compound Growth

## Case context
- `case_id`: `2026-04_Quantum_US30_SingleTrader`
- System analyzed: personal backtest on US30
- Account type: personal (not prop firm, not funded account)
- Growth model: compound interest (reinvestment of gains)
- Official sources used: `analysis_summary.md`, `trader_metrics.csv`

## Plan type

Capital management plan for a **single operator** running their own US30 strategy in a personal account with compound reinvestment.

There is no selection among external strategies. The objective of this phase is to define how to operate capital sustainably — when to scale up and when to reduce exposure — based on the observed historical edge.

## System profile
- `system_id`: `2026-04_Quantum_US30_SingleTrader`
- Continuity status: `OPERABLE_WITH_RESERVATIONS`
- Role: sole active system

## Justification for operational continuity

1. The historical backtest covers 6+ years of real operation on US30 (2019–2026).
2. The quantitative base is statistically usable for defining an initial thesis:
   - `n_trades`: 1,823
   - `expectancy_e`: 181.70 per trade
   - `profit_factor`: 1.564
   - `sqn_approx_pnl`: 4.700
   - `win_rate`: 45.97%
3. Total result is positive and consistency is defensible within the approximations documented in Phase 5.
4. The quality warning does not invalidate the system, but prevents treating it as a confirmed edge without continuous monitoring.

## Compound growth model

The plan operates with gain reinvestment. This means:
- Available capital grows with each profitable cycle
- Position size is adjusted proportionally to current capital
- Losses also reduce position size, acting as automatic protection

### Base parameters for compounding
- Approximate historical max drawdown: **14.47%**
- Average risk per trade (proxy from losses): **596.10**
- Average expectancy per trade: **181.70**
- Historical win rate: **45.97%**

### Scaling principle

Scaling is not linear. A staged approach is recommended:
- **Stage 1:** Operate at the base size validated in backtest
- **Stage 2:** Increase size after 3 consecutive months of performance consistent with the baseline
- **Stage 3:** Automatic size reduction if observed drawdown exceeds 75% of the historical maximum drawdown

## Operational risk factors

### 1. Drawdown risk
- `max_drawdown_abs_approx`: 55,462.99
- `max_drawdown_pct_approx`: 14.47%

Implication: in a personal account with compound growth, drawdown directly reduces the compounding capital base. The most effective protection is respecting hard limits before drawdown reaches historical maximum values.

### 2. Concentration risk
- Symbol: 100% US30
- Directional bias:
  - BUY: 75.53%
  - SELL: 24.47%

Implication: the strategy has a structural bullish bias on US30. In a sustained bearish trend, the system may experience systematic deterioration. Monitoring the BUY/SELL bias is an early signal of regime change.

### 3. Edge degradation risk

The observed edge is historical. Future degradation is possible due to:
- Market regime change
- Changes in execution conditions
- Undetected overfitting in the backtest

The weekly / monthly / quarterly monitoring system is designed to detect degradation before capital damage becomes irreversible.

## Thesis conclusion

The strategy is **formally operable in a personal account**, with a positive and statistically defensible quantitative edge across 1,823 trades and 6+ years.

The correct plan is not to maximize leverage from day one, but to operate in a controlled manner with compound growth, active edge monitoring, and automatic size reduction upon deterioration signals.

## Complementary files for this phase
- `hard_limits.md`
- `monitoring_schedule.md` (in `08_Monitoring/`)
- `portfolio_backtest_summary.md`
