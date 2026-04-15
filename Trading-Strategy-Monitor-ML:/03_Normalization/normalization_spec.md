# PHASE 2 — NORMALIZATION DESIGN

## 1. Objective
Define the logical design to transform the raw dataset of the `2026-04_Quantum_US30_SingleTrader` case into a reusable canonical schema, without executing the cleaning or modifying the source file yet.

## 2. Inputs Used
- `config_block_phase0.json`
- `audit_report.md`
- `detected_columns.csv`
- validated context from Phase 0 and Phase 1

## 3. Design Decision
A **minimum canonical schema** oriented to closed trades analysis is defined, maintaining traceability back to the raw data.

This design **does not assume** unconfirmed semantics. Therefore:
- `trader_id` is defined as a **case-level surrogate** as long as there is no native row-level identifier.
- `open_time` and `close_time` are parsed with the validated format, but **without time zone conversion** as long as the `UTC+1` ambiguity remains open.
- `volume` is built from `Quantity` with cross-validation against `Volume`, because both columns were confirmed as overlapping.
- `pnl_net` is taken from `Net $`; `Gross $` remains as traceability support, not as a primary source.

## 4. Minimum Canonical Schema

| canonical_field | required | logical origin | target type | main rule |
|---|---:|---|---|---|
| trader_id | yes | derived from case | string | case-level temporal surrogate |
| symbol | yes | `Symbol` | string | trim + uppercase |
| side | yes | `Type` | string | `Buy→BUY`, `Sell→SELL` |
| open_time | yes | `Entry time (UTC+1)` | datetime | parse `%d/%m/%Y %H:%M:%S.%f` without TZ conversion |
| close_time | yes | `Closing time (UTC+1)` | datetime | parse `%d/%m/%Y %H:%M:%S.%f` without TZ conversion |
| volume | yes | `Quantity` (+ cross-check `Volume`) | decimal | extract numerical size payload |
| entry_price | yes | `Entry price` | decimal | direct numerical casting |
| exit_price | yes | `Closing price` | decimal | direct numerical casting |
| pnl_net | yes | `Net $` | decimal | monetary cleaning + numerical casting |

## 5. Recommended Support Fields for Traceability
These fields do not replace the minimum canonical schema, but must be preserved in Phase 4 to avoid losing auditability:

| support_field | source_column | reason |
|---|---|---|
| trade_id | `ID` | row-level traceability and future join validation |
| strategy_label | `Label` | segmentation by sub-strategy (`LONDON_1B1S`, `RRL`) |
| pnl_gross | `Gross $` | coherence control and compatibility with other exports |
| pips | `Pips` | operational analysis and coherence checks |
| balance_after_trade | `Balance $` | equity reference by closing, not sequential raw |
| broker_commission | `Broker commission` | future compatibility with exports containing costs |
| swaps | `Swaps` | future compatibility with exports containing costs |
| volume_alt_raw | `Volume` | size cross-validation |

## 6. Normalization Rules

### 6.1 `trader_id`
- No native column exists in the raw data.
- For this single-trader case, the canonical value is defined as a temporal surrogate derived from the case: `2026-04_Quantum_US30_SingleTrader`.
- Status: **structural WARN**, not `ERROR`, because the case was validated as single-trader.
- Restriction: do not reuse this rule in multi-trader datasets without an explicit key.

### 6.2 `symbol`
- Source: `Symbol`.
- Rule: `trim` + `uppercase`.
- In this case, only `US30` was detected.
- If in another case the symbol is empty or unparseable → `ERROR`.

### 6.3 `side`
- Source: `Type`.
- Allowed dictionary:
  - `Buy` → `BUY`
  - `Sell` → `SELL`
- Any value outside this domain → `ERROR`.

### 6.4 `open_time` and `close_time`
- Sources: `Entry time (UTC+1)` and `Closing time (UTC+1)`.
- Validated format: `%d/%m/%Y %H:%M:%S.%f`.
- Rule: parse to datetime preserving the clock observed in the raw data.
- Explicit rule: **do not convert to UTC, Madrid, or New York** in Phase 4 as long as the ambiguity of the `UTC+1` label remains open.
- Minimum validation:
  - successful parse is mandatory
  - `close_time >= open_time`
- Case status: **temporal metadata WARN** until semantic validation against the log.

### 6.5 `volume`
- Primary source: `Quantity`.
- Secondary control source: `Volume`.
- Rule: extract the numerical component from the text and store it as a canonical size decimal.
- Quality condition:
  - if `Quantity_num == Volume_num` → continue
  - if they do not match → `ERROR`
- Reason for priority over `Volume`: maintain a single primary source and use the overlapping column for quality control.
- Note: this phase **does not infer** contract, lot size, or monetary multiplier.

### 6.6 `entry_price` and `exit_price`
- Sources: `Entry price` and `Closing price`.
- Rule: direct numerical casting to decimal.
- If it does not parse → `ERROR`.

### 6.7 `pnl_net`
- Primary source: `Net $`.
- Rule: clean non-standard separators/spaces and convert to signed decimal.
- `Gross $` is preserved as support, but does not replace `Net $` as the primary source.
- Scope note: in this export `Net $ = Gross $` because `Broker commission = 0` and `Swaps = 0`; this equivalence **is not generalized** to the system.

### 6.8 `Balance $`
- Does not enter the minimum canonical schema.
- Is preserved as support `balance_after_trade`.
- Requires NBSP cleaning before casting.
- Cannot be interpreted sequentially in raw order; any analytical use must respect closing order (`close_time`).

## 7. Quality Flag Definition

### 7.1 `OK`
Assign `OK` when:
- all minimum canonical columns exist
- `side` belongs to the allowed domain
- `open_time` and `close_time` parse
- `close_time >= open_time`
- `volume` parses and passes `Quantity` vs `Volume` cross-check
- `entry_price`, `exit_price`, and `pnl_net` parse
- there are no mapping contradictions in the row
- it does not depend on open structural warnings

### 7.2 `WARN`
Assign `WARN` when the row is usable but affected by open case warnings. For this case, the two main sources of `WARN` are:
- `trader_id` derived from the case and not native per row
- parsed timestamps but with unvalidated time zone semantics

### 7.3 `ERROR`
Assign `ERROR` when any of these conditions occur:
- a required minimum column is missing
- parsing of date, price, volume, or `pnl_net` fails
- `side` does not belong to the allowed domain
- `close_time < open_time`
- `Quantity` and `Volume` do not match after numerical normalization
- `Symbol` is empty or uninterpretable

## 8. Active Blockers and Ambiguities

### 8.1 Open Critical Blockers
1. **Missing native `trader_id`**
   - Mapping exists, but depends on a case-level surrogate.
   - Impact: the design is valid for single-trader; it is not portable to multi-trader without adjustment.

2. **Unclosed temporal semantics**
   - The format is known, but the operational equivalence of `UTC+1` with respect to UTC/Madrid/NY is not closed.
   - Impact: must not be converted or joined against the log with a strong temporal base until validation.

### 8.2 Non-Blocking Risks
1. `ID` vs `posId` still lacks a validated join rule.
2. `Net $` and `Gross $` are equivalent only in this export.
3. `Balance $` requires text cleaning and order by closing for sequential analysis.

## 9. Phase 2 Decision
**Result:** `ADVANCE_TO_PHASE_3_WITH_RESERVATIONS`

The phase is closed as a **valid logical design**, but not as an ambiguity-free design. The minimum mapping is defined and usable for Phase 3, provided that the following warnings remain active:
- surrogate `trader_id`
- temporal semantics
- join with log

## 10. Explicit Scope of This Phase
- It does define canonical contract and transformation rules.
- It does define `quality_flag`.
- It does not execute cleaning.
- It does not resolve joins with the log.
- It does not validate timezone at the operational level.
