# Ficha cuantitativa del sistema — 2026-04_Quantum_US30_SingleTrader

## Identificación
- `case_id`: `2026-04_Quantum_US30_SingleTrader`
- `system_id`: `2026-04_Quantum_US30_SingleTrader`
- Tipo: backtest propio — cuenta personal — instrumento US30
- Estado operativo: `OPERABLE_CON_RESERVAS`
- Rol en el plan: sistema único de trading personal

## Baseline cuantitativo
- Trades analizados: 1823
- Símbolo: US30
- Rango temporal: 2019-08-01 15:48:40.466 → 2026-04-02 16:42:48.236
- PnL total: 331.233,36
- Expectancy (E): 181.696851
- E/SD: 0.110089
- PL/SD: 200.692355
- SQN aproximado: 4.700429
- Profit Factor: 1.564128
- % Winners: 45.968184%
- Avg Win: 1.095,935203
- Avg Loss abs proxy risk: 596.101868
- Max Drawdown abs aproximado: 55.462,99
- Max Drawdown % aproximado: 14.467522%
- Avg Volume: 9.580088
- Avg Holding Minutes: 86.363031
- Median Holding Minutes: 50.574217
- BUY share: 75.534833%
- SELL share: 24.465167%

## Diagnóstico operativo
### Fortalezas
- expectativa positiva sostenida sobre 6+ años y 1823 trades
- profit factor > 1 con muestra amplia
- SQN aproximado defensible para clasificar el sistema como estadísticamente usable
- rango temporal largo reduce el riesgo de resultados atribuibles al azar

### Fragilidades
- warning estructural abierto: `trader_id_surrogate_case_level|timezone_unvalidated_parse_only`
- sesgo direccional dominante hacia BUY (75.5%): sensible a regímenes bajistas sostenidos
- concentración en un único instrumento (US30): sin diversificación de activo
- drawdown no amortiguado por diversificación entre sistemas

## Diagnóstico de continuidad operativa
**Conclusión provisional:** operable con reservas.

No se detecta razón cuantitativa suficiente para descartar la estrategia.
Sí existe razón estructural para no tratar el backtest como edge confirmado sin seguimiento activo del drift.

## Plan de control
### Revisión semanal
- rolling expectancy 20 trades
- rolling profit factor 20 trades
- rolling win rate 20 trades
- comportamiento del holding time
- deterioro vs baseline

### Revisión mensual
- drawdown del mes
- distribución BUY/SELL
- estabilidad de holding time
- estabilidad de tamaño/volumen
- confirmación de calidad de datos

### Revisión trimestral
- recalibración de baseline
- revalidación de tesis de continuidad
- decisión: mantener tamaño / reducir / pausar / rediseñar estrategia

## Semáforo de continuidad operativa
- 🟢 Verde: edge estable, métricas dentro de rango baseline
- 🟡 Amarillo: deterioro moderado vs baseline — mantener pero no escalar
- 🔴 Rojo: pérdida de expectancy, PF < 1 o drawdown fuera de límites — pausar

## Modelo de interés compuesto
En cuenta personal con reinversión de ganancias:
- el tamaño de posición se ajusta al capital disponible en cada ciclo
- el drawdown actúa como reductor automático de exposición
- no se aumenta el tamaño para "recuperar" — se respetan los límites duros

## Nota de integridad
Esta ficha se construyó con métricas de resumen calculadas sobre el historial de backtest.
Se actualizará cuando `clean_data.csv` esté disponible en la siguiente etapa y el análisis se ejecute sobre datos depurados completos.
