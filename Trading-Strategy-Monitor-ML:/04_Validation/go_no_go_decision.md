# Phase 3 — Go / No-Go Decision — Personal US30 Backtest

## Case
`2026-04_Quantum_US30_SingleTrader`

## Final decision
**NO GO** (with approved fallback F4A)

## Classification
`ERROR`

## Executive justification

The normalization logical design is consistent and usable, but the validation cannot be closed as a full `GO` because structural ambiguities remain open regarding:
- Formalized row identity (`strategy_id` or native `trader_id`)
- Operational semantics of the timestamp timezone (`UTC+1` without validated equivalence)
- Join rule with the secondary log

Under the Phase 3 system rule, if structural uncertainty persists, standard production cleaning is not enabled.
Fallback F4A was approved as a restricted cleaning variant — the correct path for this single-strategy personal backtest case.

## What was validated

- Consistent case contract
- Consistent grain: `1 row = 1 closed trade`
- 1,823 rows and 16 columns
- All minimum required columns present
- Logical mapping consistent between `canonical_map.json` and `field_mapping.csv`
- Dates parseable and `close_time >= open_time`
- Minimum numeric consistency validated
- `Quantity` vs `Volume` consistent
- `Net $` vs `Gross $` consistent in this export

## What blocks the GO

1. `trader_id` does not exist natively at the row level.
2. `UTC+1` remains an unvalidated label for timezone conversion.
3. `ID` vs `posId` still lacks a formally validated join rule.
4. The system requires stopping if those ambiguities remain open.

## Recommended operational decision

Do not execute the standard `clean_data.csv` pipeline. Use the restricted variant.

## Approved variant

`PHASE 4A — RESTRICTED CLEAN DATA`

Scope of that variant:
- Parse-only for dates
- Zero timezone conversion
- Zero join with log
- Case-level surrogate `trader_id` (identifies the own system within the case)
- Full traceability of restrictions in the quality log

**Context note:** in a personal backtest with a single system, the surrogate `trader_id` is not a major conceptual problem — an identity column simply does not exist in the export because there is only one operator. The restriction is documented for methodological rigor.

## Case status
`FALLBACK_F4A_APPROVED`
