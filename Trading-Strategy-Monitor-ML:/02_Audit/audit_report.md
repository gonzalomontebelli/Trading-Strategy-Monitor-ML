# PHASE 1 — STRUCTURAL AUDIT

## 1. Objective
Audit the structural quality of the raw dataset before designing the normalization.

## 2. Audited Inputs
- Main dataset: `2026-04-02 18-45-49 History - Quantum_us30pepper (US30, m5, True, True, 0, 1, 61.5, 122.5, 9, 15, 7,).csv`
- Reference contract: `config_block_phase0.json`

## 3. Input Contract Validation
- `case_id`: `2026-04_Quantum_US30_SingleTrader`
- expected grain: `1 row = 1 closed trade`
- expected columns according to Phase 0: `16`
- observed columns in the CSV: `16`
- exact match of names and order: **yes**

## 4. Executive Result
**Phase 1 Decision:** `ADVANCE_WITH_RESERVATIONS`  
**Structural reliability:** HIGH to advance to normalization, with documented reservations.

## 5. Main Structural Checks

### 5.1 Basic Integrity
- observed rows: **1823**
- observed columns: **16**
- complete duplicate rows: **0**
- duplicate `ID`s: **0**
- rows with empty strings in any column: **0 affected columns**
- columns with raw nulls (`NaN`): **0 affected columns**

### 5.2 Dates
- successful parsing of `Entry time (UTC+1)`: **1823/1823**
- successful parsing of `Closing time (UTC+1)`: **1823/1823**
- validated format: **DD/MM/YYYY HH:MM:SS.mmm**
- closings prior to openings: **0**
- file sorted by `Entry time (UTC+1)`: **yes**
- file sorted by `Closing time (UTC+1)`: **no**
- duplicate closing timestamps: **117** Note: this does not invalidate the dataset; it indicates simultaneous or very close closings, so the balance must be interpreted by closing and not by the raw order.

### 5.3 Numeric and Monetary Fields
- successful parsing of `Entry price`: **1823/1823**
- successful parsing of `Closing price`: **1823/1823**
- successful parsing of `Pips`: **1823/1823**
- successful parsing of `Net $`: **1823/1823**
- successful parsing of `Gross $`: **1823/1823**
- successful parsing of `Balance $` after text cleaning: **1823/1823**
- `Balance $` contains NBSP separator: **yes**
- `Broker commission` all zero: **yes**
- `Swaps` all zero: **yes**

### 5.4 Internal Coherence Between Columns
- numeric mismatch `Quantity` vs `Volume`: **0**
- mismatch `Net $` vs `Gross $`: **0**
- sign mismatch `Pips` vs `Net $`: **0**
- price vs `Pips` mismatch on `Buy`: **0**
- price vs `Pips` mismatch on `Sell`: **0**

## 6. Column Separation by Type

### 6.1 Identification
- `Label`
- `Symbol`
- `Type`
- `ID`

### 6.2 Execution
- `Entry time (UTC+1)`
- `Entry price`
- `Closing price`
- `Closing time (UTC+1)`

### 6.3 Result
- `Net $`
- `Pips`
- `Gross $`
- `Balance $`

### 6.4 Risk / Size / Costs
- `Quantity`
- `Volume`
- `Broker commission`
- `Swaps`

## 7. Detected Risks and Limitations

### 7.1 Non-Blocking Risks
1. **`trader_id` does not exist as an explicit column.** The case behaves as single-trader, but that identity is not materialized within the table.

2. **Open temporal semantics.** The date format parses well, but the `UTC+1` label still lacks a formal equivalence with Madrid/NY.

3. **`Balance $` does not come as pure numeric.** Requires NBSP cleaning for reliable casting.

4. **Raw order is not useful for sequential balance reconstruction.** The file is sorted by opening, not by closing. If `Balance $` is used, the closing order must be respected.

5. **`Net $` and `Gross $` are equivalent only in this export.** This equivalence should not be assumed as a general rule of the system.

### 7.2 Blocking Risks
**No structural blockers were detected that prevent moving to Phase 2.**

## 8. Reliability Assessment
The dataset is **reliable to advance to normalization design**, because:
- it has no raw nulls in critical columns
- it has no complete duplicates or duplicate `ID`s
- all dates parse
- there are no closings prior to openings
- prices, `Pips`, `Net $`, and `Gross $` are coherent with each other
- `Quantity` and `Volume` are consistent at a numeric level

Reliability drops only when attempting to enrich the case with:
- formal trader identity
- exact time zone semantics
- secondary log join

## 9. Phase 1 Conclusion
**Result:** `ADVANCE_WITH_RESERVATIONS`  
The raw data is structurally sound to move to Phase 2, but with documented reservations that must remain open in the case contract.
