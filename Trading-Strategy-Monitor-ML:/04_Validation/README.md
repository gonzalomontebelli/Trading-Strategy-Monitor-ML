# 04_Validation — Quality Gate

## What happens here

The **Quality Gate** checklist is run before computing any metrics.

**Absolute rule:** Never compute metrics on questionable data.

## Key Quality Gate questions

- Is PnL consistent with entry/exit prices?
- Are there rows with missing critical fields?
- Are dates coherent (close time > open time)?
- Are symbols recognizable and consistent?
- Are there strategies with fewer than N trades (minimum statistical threshold)?

## Verdict

- `GO` → proceed to `05_Clean`
- `NO GO` → list all blockers. Do not compute metrics until resolved.

## Typical files

```
04_Validation/
├── validation_checklist.md  → Full checklist with results per item
├── blockers.txt             → List of issues blocking progress
└── go_no_go_decision.md     → Final documented decision
```
