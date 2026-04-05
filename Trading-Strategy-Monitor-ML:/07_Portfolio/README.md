# 07_Portfolio — Capital Management Plan

## What happens here

The **final capital management decision** is defined: how to operate the strategy, with what position sizing, and under what conditions.

For a single-strategy context (this project), this phase defines the compound growth model, scaling rules, and hard risk limits.

## Decision framework

| Decision | Meaning |
|---|---|
| `OPERATE` | Strategy enters active trading with defined parameters |
| `WATCH` | Promising but monitor one more period before scaling |
| `DISCARD` | Does not meet minimum quantitative criteria |

## Portfolio considerations

- Is there concentration risk in a single instrument or direction?
- Do historical drawdowns overlap with expected market regimes?
- Does holding time allow execution without severe slippage?
- Is the BUY/SELL bias a structural risk in adverse market conditions?

## Typical files

```
07_Portfolio/
├── portfolio_thesis.md         → Full capital management justification
├── selected_traders.csv        → Selected strategies with key metrics
├── portfolio_weights.csv       → Capital allocation weights
├── hard_limits.md              → Hard risk limits per strategy and total
└── portfolio_backtest_summary.md → Backtest of the capital plan
```
