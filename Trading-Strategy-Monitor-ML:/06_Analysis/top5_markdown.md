# Resumen cuantitativo del sistema — Backtest personal US30

## Alcance del análisis
- Sistema analizado: 1 (backtest personal del operador)
- Trades elegibles: 1823 de 1823
- Exclusiones por `quality_flag = ERROR`: 0

## Resultado

| Sistema | Trades | E | E/SD | PL/SD | SQN aprox. | % winners | DD máx aprox. | Riesgo medio aprox. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026-04_Quantum_US30_SingleTrader | 1823 | 181.70 | 0.1101 | 200.6924 | 4.7004 | 45.97% | 14.47% | 596.10 |

## Nota de interpretación

Se trata de un sistema único: no hay comparación entre estrategias externas. Las métricas caracterizan completamente el edge histórico del sistema propio sobre US30. El análisis es por definición unitario y no degenerado — es la forma correcta de evaluar un backtest personal.

## Advertencias metodológicas

- `SQN` se calcula como proxy sobre `pnl_net` por trade, no sobre R-multiples, porque el dataset no incluye riesgo ex-ante por operación.
- `drawdown` es aproximado y se calcula sobre la secuencia cronológica por `close_time` usando `balance_after_trade`.
- `riesgo medio` se aproxima como promedio de pérdida absoluta en trades perdedores, porque no existe campo de stop inicial ni riesgo planificado por trade.