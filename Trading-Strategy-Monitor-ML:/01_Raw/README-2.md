# Case: 2026-04_Quantum_US30_SingleTrader

## Case context

Full quantitative pipeline on a **single-strategy trade history** dataset (US30) — 1,823 closed trades from Aug 2019 to Apr 2026.

## Current status
- Phase completed: **Phase 0 — Schema Detective**
- Next pending step: **Phase 1 — Structural Audit**

## Official source files
- `01_Raw/2026-04-02 18-45-49 History - Quantum_us30pepper (US30, m5, ...).csv`
- `01_Raw/log.txt`
- `02_Audit/config_block_phase0.json`
- `02_Audit/intake_summary_phase0.md`

## Open warnings
- No explicit `trader_id` column exists at the row level (surrogate used).
- The CSV timestamp label (`UTC+1`) must not be equated with the Madrid local time in the log.
- The log contains enriched trade data but the join with the CSV has not been formally validated yet.
