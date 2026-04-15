# PHASE 0 — Intake Summary — Personal Backtest US30

## 1. Detected Files
1. **2026-04-02 18-45-49 History - Quantum_us30pepper (US30, m5, True, True, 0, 1, 61.5, 122.5, 9, 15, 7,).csv**
   - Detected role: main table
   - Format: CSV
   - Detected grain: **1 row = 1 closed trade**
   - Dimension: **1823 rows x 16 columns**

2. **log.txt**
   - Detected role: secondary support file
   - Format: TXT
   - Contains three embedded CSV-type schemas:
     - `OPEN_CSV`
     - `CLOSE_CSV`
     - `DAY_SUMMARY`

## 2. Detected Main Table
The main table of the case is the file:

`2026-04-02 18-45-49 History - Quantum_us30pepper (US30, m5, True, True, 0, 1, 61.5, 122.5, 9, 15, 7,).csv`

Reason:
- has a direct tabular structure
- each row represents a closed trade
- contains entry and exit prices, timestamps, monetary result, pips, balance, and trade identifier

## 3. Detected Columns in the Main Table
1. `Label`
2. `Entry time (UTC+1)`
3. `Symbol`
4. `Quantity`
5. `Volume`
6. `Type`
7. `Entry price`
8. `Broker commission`
9. `Swaps`
10. `Closing price`
11. `Closing time (UTC+1)`
12. `Net $`
13. `Pips`
14. `Gross $`
15. `Balance $`
16. `ID`

## 4. Detected Equivalences and Overlaps
- **`Quantity` ↔ `Volume`**
  - both columns represent position size in text
  - they change the unit label (`Lots` vs `Indices`)
  - should not be treated as independent metrics

- **`Net $` ↔ `Gross $`**
  - in this export they are equivalent in all observed rows
  - this occurs because `Broker commission = 0` and `Swaps = 0` in all rows
  - they remain conceptually distinct columns

## 5. Detected Critical Fields
- **PnL / result:** `Net $`, `Gross $`, `Pips`, `Balance $`
- **Dates:** `Entry time (UTC+1)`, `Closing time (UTC+1)`
- **Volume / size:** `Quantity`, `Volume`
- **Instrument:** `Symbol`
- **Trade ID:** `ID`
- **Trader:** **no explicit column exists**

## 6. Detected Structural Problems
### 6.1 No `trader_id` within the table
The file functions as a **single-trader** dataset, but that is given by the file/log context and not by a formal column.

### 6.2 Temporal Risk
The CSV dates parse correctly with format:

`DD/MM/YYYY HH:MM:SS.mmm`

But the header uses a fixed `UTC+1`, while the log also reports `Madrid` and `NY` with a real time adjustment.  
Conclusion: **it cannot be assumed that `UTC+1` = local Madrid**.

### 6.3 Monetary Fields as Text
- `Net $`
- `Gross $`
- `Balance $`

They do not come as pure numerics.  
`Balance $` also contains a thousands separator with a **non-breaking space**.

### 6.4 Enriched log without validated join
The log provides slippage, latency, `risk$`, `resultR`, `durationMin`, `sessionTag`, and daily summaries.  
But:
- the CSV uses `ID`
- the log uses `posId`

There is no direct validated equivalence in this phase.

## 7. Basic Structural Checks
- complete duplicate rows: **0**
- duplicate `ID`s: **0**
- completely empty rows: **0**
- repeated headers within the CSV: **not detected**
- successful parsing of entry dates: **1823/1823**
- successful parsing of closing dates: **1823/1823**
- trades with closing prior to opening: **0**

## 8. Operational Context Findings
- unique symbol detected: **US30**
- detected labels/strategies: **LONDON_1B1S, RRL**
- detected sides: **Buy, Sell**
- detected time range:
  - minimum opening: **2019-08-01 14:50:43.720000**
  - maximum opening: **2026-04-02 16:35:00.110000**
  - minimum closing: **2019-08-01 15:48:40.466000**
  - maximum closing: **2026-04-02 16:42:48.236000**

## 9. Phase Status
**Result:** dataset suitable to advance to **PHASE 1 — STRUCTURAL AUDIT**, but with explicit reservations.

### Active Reservations
1. Missing explicit `trader_id`.
2. Missing formal temporal policy for `UTC+1` vs Madrid/NY.
3. Missing formal join rule between CSV and log.

### Decision
**ADVANCE_TO_PHASE_1_WITH_RESERVATIONS**
