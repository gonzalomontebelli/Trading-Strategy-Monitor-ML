# Phase 3 — Validation Checklist — Personal US30 Backtest

## Case
`2026-04_Quantum_US30_SingleTrader`

## Objective
Determine whether the backtest dataset is ready to enter Phase 4 (`CLEAN DATA`) without violating the contract defined in Phase 0, the structural audit of Phase 1, and the logical design of Phase 2.

## Executive result
**Final classification:** `ERROR`
**Decision:** `NO_GO_TO_PHASE_4`
**Reason:** Critical structural ambiguities remain open. The mapping is consistent, but the case validation cannot be fully closed for production cleaning under strict system criteria.

---

## Validation checklist

| check_id | validation | status | evidence | decision |
|---|---|---|---|---|
| VAL_001 | Case ID is consistent across Phase 0, 1 and 2 | OK | `case_id` consistent: `2026-04_Quantum_US30_SingleTrader` | keep |
| VAL_002 | Contractual grain is still `1 row = 1 closed trade` | OK | Phase 0 contract consistent with audit | keep |
| VAL_003 | Primary table retains 1,823 rows and 16 columns | OK | Phase 0 and Phase 1 match | keep |
| VAL_004 | All minimum required columns for the canonical schema exist in raw | OK | `Symbol`, `Type`, `Entry time (UTC+1)`, `Closing time (UTC+1)`, `Quantity`, `Entry price`, `Closing price`, `Net $` present | keep |
| VAL_005 | `canonical_map.json` mapping matches `field_mapping.csv` | OK | Order, canonical names and sources consistent | keep |
| VAL_006 | `side` domain is closed and validated | OK | `Buy → BUY`, `Sell → SELL` | keep |
| VAL_007 | Date parsing validated and `close_time >= open_time` | OK | 1,823/1,823 parsed; 0 violations | keep |
| VAL_008 | Minimum numeric parsing validated | OK | `Entry price`, `Closing price`, `Net $`, `Gross $`, `Pips`, `Balance $` parse correctly; `Quantity` vs `Volume` mismatch = 0 | keep |
| VAL_009 | No structural duplicates breaking the contract | OK | 0 fully duplicated rows; 0 duplicate `ID` values | keep |
| VAL_010 | `trader_id` is natively resolved at row level | ERROR | No trader column exists; only a case-level surrogate | block GO |
| VAL_011 | Timestamp semantics are closed for cleaning and future traceability | ERROR | The `UTC+1` label remains unvalidated; no confirmed equivalence with UTC/Madrid/NY | block GO |
| VAL_012 | A validated join rule with the secondary log exists | ERROR | `ID` does not match `posId` directly; join rule open | block GO |
| VAL_013 | `Balance $` can be used sequentially in raw row order | WARN | Requires NBSP cleanup and ordering by `close_time`, not raw order | document |
| VAL_014 | `Net $ = Gross $` can be generalized as a system rule | WARN | Valid only in this export where commissions and swaps are zero | document |
| VAL_015 | The case can advance to Phase 4 without reservations | ERROR | Contradicts the Phase 3 rule: stop if structural uncertainty remains | NO GO |

---

## Status interpretation
- `OK` = validated and consistent for the current contract
- `WARN` = usable with documented restriction; does not block alone
- `ERROR` = ambiguity or absence that prevents GO to Phase 4

---

## Approved fallback

Only the following fallback is permitted, subject to explicit approval:

### Fallback F4A — Restricted cleaning
Allow a limited Phase 4 **only if** the following is formally accepted:
1. `trader_id` is kept as a case-level surrogate.
2. `open_time` and `close_time` are parsed **without timezone conversion**.
3. Any strong join with `log.txt` is prohibited.
4. `Balance $` is kept only as a non-sequential support field.
5. The output must be explicitly labeled `clean_data_restricted`.

Without that approval, the gate decision remains `NO_GO_TO_PHASE_4`.

---

## Final validation decision
**Official Phase 3 status:** `ERROR / NO GO`
**Correct reading:** the dataset is good enough to continue the pipeline design, but not for executing standard production cleaning without first accepting the open case restrictions.
