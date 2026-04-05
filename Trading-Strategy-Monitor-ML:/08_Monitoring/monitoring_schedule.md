# Monitoring Schedule — Personal US30 System

## Objective
Monitor the continuity of the personal trading edge, detect regime changes, and flag operational deviations from the historical baseline.

## Frequencies

### Weekly
- Suggested window: last 20 trades or last closed week
- Review:
  - Rolling expectancy
  - Rolling profit factor
  - Rolling win rate
  - Holding time behavior
  - Average position size vs baseline
- Output:
  - `weekly_monitor_report.csv`
  - Traffic light: `GREEN / YELLOW / RED`

### Monthly
- Review:
  - Monthly drawdown
  - Net monthly PnL
  - Position size stability in compound capital terms
  - Directional concentration (BUY/SELL)
  - Capital evolution with compound growth
- Output:
  - `monthly_monitor_report.csv`

### Quarterly
- Review:
  - Edge persistence vs historical baseline
  - Threshold recalibration if capital has grown materially
  - Decision: continue / reduce / pause / redesign
  - Compound growth projection update
- Output:
  - `quarterly_monitor_report.csv`

## Compound scaling rule

Position size in a compound growth account must be reviewed each monthly cycle:
1. Calculate current available capital
2. Determine proportional position size based on current capital (using the same risk % as in the backtest)
3. Adjust before the first trade of the new month
4. Do NOT increase size in cycles where the traffic light is yellow or red
