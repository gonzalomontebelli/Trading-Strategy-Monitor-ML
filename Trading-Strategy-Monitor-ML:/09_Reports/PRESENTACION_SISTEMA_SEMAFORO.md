# System Presentation — Quantitative ML Monitoring with Traffic Light

## 1. Problem this solves

In personal trading, knowing whether a week was profitable or not is not enough.
What matters is detecting **when the system stops behaving like the validated historical pattern**.

The system is designed to answer one question:

> Is my strategy still operating within its own healthy historical pattern — or has it entered deterioration?

---

## 2. Core idea

The system learns the historical behavior of the strategy (from the validated backtest) and then compares each week and month against that baseline.

It does not try to predict the market.
It detects **deviation of the system from its own history**.

---

## 3. What the system monitors

Each trade feeds into aggregated metrics:

- PnL (cumulative and rolling)
- Rolling expectancy
- Rolling win rate
- Rolling profit factor
- PnL volatility
- Average position size
- Trade frequency
- Loss streaks
- BUY/SELL directional bias
- Average risk per trade
- Holding time
- Slippage (when available)

---

## 4. How it learns

The model uses two layers:

### Layer A — Robust statistical rules
Compares each period against the historical baseline using robust deviation thresholds.
If a metric falls outside the defined tolerance range, an alert is triggered.

### Layer B — Machine Learning
Trains an `IsolationForest` to detect "unusual" weeks or months relative to the system's own history.

---

## 5. Traffic light — operational continuity signal

### Green
The system is operating within its normal historical behavior zone.

**Action:**
- Continue trading at normal size
- Adjust position size to current capital (compound growth)

### Yellow
Moderate deterioration or mixed signals detected relative to baseline.

**Action:**
- Hold current size, do not scale up
- Review the next period before making any new decisions

### Red
Strong deterioration or statistical regime change detected.

**Action:**
- Pause trading
- Review the quantitative profile
- Do not reactivate until the deterioration is confirmed as transient — or redesign the strategy

---

## 6. How it avoids serious errors

The system is designed to **not overreact to normal statistical noise**.

Red is not triggered by a single isolated bad week.
It combines:

- Hard limit violations
- Severity score
- ML anomaly score
- Weekly and monthly confirmation

This reduces false positives and prevents exiting a strategy due to expected variance.

---

## 7. What it delivers

The system provides clear outputs for personal management:

- Weekly scorecards with rolling metrics
- Monthly scorecards with compound capital evolution
- Traffic light continuity signal
- Signal color rationale
- Executive decision message
- Updated quantitative profile snapshot

---

## 8. Sample alert messages

### Green
`System US30 is green. Expectancy and PF within historical range. No significant drift signals. Adjust size to current capital.`

### Yellow
`System US30 is yellow. Win rate dropped and weekly PnL volatility increased. Hold current size and review next week before scaling.`

### Red
`System US30 is red. Negative expectancy, PF < 0.90 and high anomaly score. Pause trading and assess whether the deterioration is transient or structural.`

---

## 9. How it integrates with the capital plan

This module operates after the clean baseline and quantitative profile are established.

### Full flow
1. Trade history (backtest or live)
2. Cleaned canonical dataset
3. System metrics (baseline)
4. Compound capital plan
5. Weekly / monthly monitoring with traffic light
6. Quantitative profile update and compound projection update

---

## 10. Final note

This system does not replace trader judgment.

What it does is **organize the evidence**, detect deviations from the system's own behavior before capital damage becomes severe, and help decide when to continue, when to watch, and when to stop.

That is the correct logic for managing a personal strategy with compound growth:
- Do not react too late to real deterioration
- Do not overreact to normal statistical noise
- Do not confuse a losing streak with permanent loss of edge
