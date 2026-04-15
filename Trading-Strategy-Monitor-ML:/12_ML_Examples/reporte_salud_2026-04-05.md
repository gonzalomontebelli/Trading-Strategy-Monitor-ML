# Strategy Health Report
## System: Quantum_us30pepper — US30
### Period: March 24 – April 2, 2026
### Generated: 2026-04-05

---

## 1. Performance Summary

| Metric | Period | Historical Baseline |
|---|---|---|
| Trades executed | 8 | — |
| Days traded | 5 | — |
| Wins | 2 (25.0%) | 45.97% |
| Losses | 6 | — |
| Net PnL | **−$77.82** | — |
| Profit Factor | 0.662 | 1.564 |
| Avg Win | $76.26 | ~$1,095.94 |
| Avg Loss | −$38.39 | — |
| Avg R/trade | −0.238 | +0.375 |
| Start Period Balance | $3,947.12 | — |
| End Period Balance | $3,869.30 | — |
| Period DD | −1.97% | — |
| DD from Start ($4,000) | −3.27% | 14.47% historical max |

**Sub-strategy Breakdown:**

| Strategy | Trades | Wins | Period WR | Baseline WR | PnL |
|---|---|---|---|---|---|
| RRL | 7 | 1 | 14.3% | 47.2% | −$156.18 |
| LONDON_1B1S | 1 | 1 | 100.0% | 43.5% | +$78.36 |

---

## 2. Deviation Analysis — Expected vs. Actual

### 2.1 Win Rate

| | Value |
|---|---|
| Expected WR (baseline) | 45.97% |
| Observed WR (period) | 25.0% |
| Absolute Deviation | −20.97 pp |
| Binomial test p-value (one-tailed) | 0.204 |
| Statistically Significant? | **No** |

With n=8 trades, observing 2 or fewer wins has a 20.4% probability even if the system is operating at its normal historical WR. The sample size is too small to distinguish between statistical noise and structural deterioration.

**Interpretation:** Deviation is within the expected variance range for a sample of 8 trades.

### 2.2 RRL Sub-strategy

| | Value |
|---|---|
| Expected RRL WR (baseline) | 47.2% |
| Observed RRL WR | 14.3% (1/7) |
| Binomial test p-value (one-tailed) | 0.083 |
| Statistically Significant? | **Borderline** (conventional threshold: 0.05) |

RRL accounts for 7 of the 8 trades in the period with only 1 win. The p-value of 0.083 is the most relevant data point: while above the conventional significance threshold (α=0.05), it is low enough not to be ignored. It does not confirm deterioration but signals it.

### 2.3 R per Trade

| | Value |
|---|---|
| Expected R per trade | +0.3754 |
| Observed R per trade | −0.2380 |
| Difference | −0.6134 R |
| Standard Error (n=8) | 0.528 |
| Z-score | −1.16 |
| p-value (one-tailed) | 0.122 |
| Statistically Significant? | **No** |

The R/trade deviation also fails to reach statistical significance with this sample. The system has not entered confirmed structural loss.

### 2.4 Execution and Operational Quality

| Metric | Period | Operational Limit |
|---|---|---|
| Avg spread | 2.02 pips | max 3.5 pips |
| Entry slippage (signed) | −2.11 pips (favorable) | — |
| Exit slippage (signed) | −0.30 pips (favorable) | — |
| Avg latency | 381 ms | — |
| High latency event | 857 ms (24/03, single) | — |

Execution is technically sound. Average slippage was favorable (the broker executed slightly better than the reference price at entry). The average spread of 2.02 pips is well within the 3.5 pip limit. No infrastructure issues were detected.

The isolated latency event (857 ms, 24/03) did not affect the outcome of that trade (SL hit, −0.50R). No action required.

---

## 3. Market Diagnosis

### 3.1 Critical Event: Liberation Day — April 2, 2026

On April 2, 2026, the Trump administration announced global reciprocal tariffs ("Liberation Day"), generating the largest volatility shock in the US30 since the 2020 pandemic. The index suffered an abrupt drop of approximately 1,500 points during the session.

**This event is relevant for the period evaluation for three reasons:**

1.  **Dominant BUY bias (75.5% historical):** A sharp index drop creates structurally adverse conditions for the strategy as currently calibrated.
2.  **RRL Exposure:** 7 of its 8 trades were executed in market conditions potentially disrupted by the pre-announcement tension and the subsequent crash.
3.  **NewsGuard Lite Gap:** The bot filter blocks NFP, CPI, Powell, Jackson Hole, and Michigan Sentiment, but has no rule for trade policy events of this magnitude. The strategy operated with full exposure during and post-announcement.

### 3.2 Implication for Period Interpretation

The period's underperformance has an identifiable regime-based explanation. This does not invalidate the historical edge, but it implies the strategy entered a market environment that differs materially from its training base (backtest 2019–2026).

**Working Hypothesis:** The negative result for the period primarily responds to the regime shift induced by Liberation Day, not an internal deterioration of the edge. This hypothesis requires monitoring in the coming weeks to be confirmed.

---

## 4. Operational Continuity Status

### 🟡 YELLOW

**Reason for Status:**

The system underperformed during the analyzed period, but statistical tests do not reach significance with n=8. Deterioration is not confirmed as structural. However, three factors prevent a Green status:

* RRL with a 14.3% WR and a borderline p-value (0.083) — a signal for attention, not yet alarm.
* Documented regime event (Liberation Day, 2/04) modifying the operational context.
* System lacks a filter for trade policy shocks: operational risk not covered by NewsGuard Lite.

**What is NOT triggering Red:**
* Period DD: −1.97% (within normal variance; hard limit is −10% monthly).
* DD since account start: −3.27% (pause limit is −20%).
* Technically sound execution (spread, slippage, latency).
* Global WR p-value = 0.204 (not significant).
* R/trade Z-score = −1.16 (not significant).

---

## 5. Operational Decision

**MAINTAIN current size. DO NOT scale. Review in the next weekly cycle.**

Specific Actions:

1.  **Freeze position sizing:** Do not increase size in the next cycle. Per the compound plan rules, scaling is paused while the status is Yellow.
2.  **Specific RRL Monitoring:** Over the next 2 weeks. If RRL maintains WR < 30% over the next 10–15 accumulated trades, the p-value will cross the significance threshold, requiring a pause or parameter adjustment.
3.  **Evaluate NewsGuard Lite Expansion:** To cover trade policy events (USTR announcements, tariff escalations). This requires a source code modification.
4.  **Next Review:** Week of April 6–11, 2026. If the regime context normalizes and RRL shows recovery, return to Green.

---

## 6. Open Alerts

| Type | Description | Urgency |
|---|---|---|
| RRL Monitoring | WR 14.3% in 7 trades, p=0.083 | High |
| Market Regime | Liberation Day — high volatility post-announcement | High |
| NewsGuard gap | No coverage for trade policy shocks | Medium |
| Data quality (legacy) | Timezone and trader_id_surrogate warnings (open since backtest) | Low |

---

## 7. Accumulated Plan Context

| | Value |
|---|---|
| Initial Plan Capital ($) | $4,000.00 |
| Current Balance | $3,869.30 |
| Accumulated DD from start | −3.27% |
| Hard Pause Limit (DD) | −20% total or −10% monthly |
| Compound Plan Status | **Do not scale in next cycle** |
| Accumulated Status | 🟡 YELLOW |

The compound interest plan remains active. The accumulated drawdown of −3.27% is manageable and does not compromise the scaling logic. The first scaling review projected for month-end is postponed until the status returns to Green.

---

*Report automatically generated based on actual broker data (cT_1329775_2026-04-05_09-50.csv) and operational log (2026-04-05_09-43 - Quantum_us30pepper, Instance 926220.log). Baseline: 2026-04_Quantum_US30_SingleTrader (1823 trades, Aug 2019 – April 2026).*
