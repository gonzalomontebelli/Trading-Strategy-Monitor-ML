# 06_Analysis — Quantitative Metrics & Ranking

## What happens here

All quantitative metrics are computed from the clean dataset and a full ranking is generated.

## Metrics computed (in priority order)

1. **Expectancy** — primary metric. Average profit/loss per trade.
2. **Max Drawdown** — worst historical scenario (absolute and percentage)
3. **Profit Factor** — gross profit / gross loss ratio
4. **SQN (approx)** — System Quality Number, measures statistical robustness
5. **Win Rate** — percentage of profitable trades
6. **Average Holding Time** — trade duration profile
7. **Outlier Dependency** — how much performance depends on extreme trades
8. **BUY/SELL Bias** — directional imbalance flag

## Typical files

```
06_Analysis/
├── trader_metrics.csv       → Full metrics per strategy
├── ranking_cuantitativo.csv → Quantitative ranking
├── analysis_summary.md      → Summary with interpretations
└── top5_markdown.md         → Top candidates narrative
```
