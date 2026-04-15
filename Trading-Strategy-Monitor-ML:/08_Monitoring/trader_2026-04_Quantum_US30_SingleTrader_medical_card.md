# Quantitative System Profile — 2026-04_Quantum_US30_SingleTrader

## Identification
- **`case_id`**: `2026-04_Quantum_US30_SingleTrader`
- **`system_id`**: `2026-04_Quantum_US30_SingleTrader`
- **Type**: Proprietary backtest — personal account — US30 instrument
- **Operational Status**: `OPERABLE_WITH_RESERVATIONS`
- **Role in Plan**: Primary personal trading system

## Quantitative Baseline
- **Analyzed Trades**: 1823
- **Symbol**: US30
- **Time Range**: 2019-08-01 15:48:40.466 → 2026-04-02 16:42:48.236
- **Total PnL**: 331,233.36
- **Expectancy (E)**: 181.696851
- **E/SD**: 0.110089
- **PL/SD**: 200.692355
- **Approximate SQN**: 4.700429
- **Profit Factor**: 1.564128
- **% Winners**: 45.968184%
- **Avg Win**: 1,095.935203
- **Avg Loss (abs proxy risk)**: 596.101868
- **Approximate Absolute Max Drawdown**: 55,462.99
- **Approximate Max Drawdown %**: 14.467522%
- **Avg Volume**: 9.580088
- **Avg Holding Minutes**: 86.363031
- **Median Holding Minutes**: 50.574217
- **BUY share**: 75.534833%
- **SELL share**: 24.465167%

---

## Operational Diagnosis

### Strengths
* Sustained positive expectancy over 6+ years and 1823 trades.
* Profit Factor > 1 with a significant sample size.
* Defensible approximate SQN, classifying the system as statistically usable.
* Long time range reduces the risk of results being attributed to random chance.

### Fragilities
* **Open structural warning:** `trader_id_surrogate_case_level|timezone_unvalidated_parse_only`.
* **Directional bias:** Dominant toward BUY (75.5%); sensitive to sustained bearish regimes.
* **Concentration:** Single instrument (US30); lack of asset diversification.
* **Drawdown:** Not dampened by diversification across multiple systems.

---

## Operational Continuity Diagnosis
**Provisional Conclusion:** Operable with reservations.

No sufficient quantitative reason is detected to discard the strategy. However, there is a structural reason not to treat the backtest as a confirmed edge without active monitoring of drift.

## Control Plan

### Weekly Review
* Rolling expectancy (20 trades)
* Rolling profit factor (20 trades)
* Rolling win rate (20 trades)
* Holding time behavior
* Deterioration vs. baseline

### Monthly Review
* Monthly drawdown
* BUY/SELL distribution
* Holding time stability
* Size/volume stability
* Data quality confirmation

### Quarterly Review
* Baseline recalibration
* Revalidation of continuity thesis
* **Decision:** Maintain size / reduce / pause / redesign strategy

---

## Operational Continuity Status (Traffic Light)
* 🟢 **Green:** Stable edge, metrics within baseline range.
* 🟡 **Yellow:** Moderate deterioration vs. baseline — maintain but do not scale.
* 🔴 **Red:** Loss of expectancy, PF < 1, or drawdown outside limits — pause operations.

## Compound Interest Model
In a personal account with profit reinvestment:
1.  Position sizing adjusts to available capital in each cycle.
2.  Drawdown acts as an automatic exposure reducer.
3.  Size is not increased to "recover" — hard limits are strictly respected.

## Integrity Note
This profile was built using summary metrics calculated from the backtest history. It will be updated once `clean_data.csv` is available in the next stage and the analysis is performed on fully scrubbed data.
