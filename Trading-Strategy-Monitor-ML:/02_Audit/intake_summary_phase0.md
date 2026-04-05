# FASE 0 — Intake Summary — Backtest personal US30

## 1. Archivos detectados
1. **2026-04-02 18-45-49 History - Quantum_us30pepper (US30, m5, True, True, 0, 1, 61.5, 122.5, 9, 15, 7,).csv**
   - Rol detectado: tabla principal
   - Formato: CSV
   - Grano detectado: **1 fila = 1 trade cerrado**
   - Dimensión: **1823 filas x 16 columnas**

2. **log.txt**
   - Rol detectado: archivo secundario de soporte
   - Formato: TXT
   - Contiene tres esquemas embebidos tipo CSV:
     - `OPEN_CSV`
     - `CLOSE_CSV`
     - `DAY_SUMMARY`

## 2. Tabla principal detectada
La tabla principal del caso es el archivo:

`2026-04-02 18-45-49 History - Quantum_us30pepper (US30, m5, True, True, 0, 1, 61.5, 122.5, 9, 15, 7,).csv`

Motivo:
- tiene estructura tabular directa
- cada fila representa una operación cerrada
- contiene precios de entrada y salida, timestamps, resultado monetario, pips, balance e identificador de trade

## 3. Columnas detectadas en la tabla principal
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

## 4. Equivalencias y solapamientos detectados
- **`Quantity` ↔ `Volume`**
  - ambas columnas representan tamaño de posición en texto
  - cambian la etiqueta de unidad (`Lots` vs `Indices`)
  - no deben tratarse como métricas independientes

- **`Net $` ↔ `Gross $`**
  - en este export son equivalentes en todas las filas observadas
  - esto ocurre porque `Broker commission = 0` y `Swaps = 0` en todas las filas
  - siguen siendo columnas conceptualmente distintas

## 5. Campos críticos detectados
- **PnL / resultado:** `Net $`, `Gross $`, `Pips`, `Balance $`
- **Fechas:** `Entry time (UTC+1)`, `Closing time (UTC+1)`
- **Volumen / size:** `Quantity`, `Volume`
- **Instrumento:** `Symbol`
- **Trade ID:** `ID`
- **Trader:** **no existe columna explícita**

## 6. Problemas estructurales detectados
### 6.1 No hay `trader_id` dentro de la tabla
El archivo funciona como dataset de **un solo trader**, pero eso está dado por contexto de archivo/log y no por una columna formal.

### 6.2 Riesgo temporal
Las fechas del CSV parsean correctamente con formato:

`DD/MM/YYYY HH:MM:SS.mmm`

Pero el encabezado usa `UTC+1` fijo, mientras el log además reporta `Madrid` y `NY` con ajuste horario real.  
Conclusión: **no se puede asumir que `UTC+1` = Madrid local**.

### 6.3 Campos monetarios como texto
- `Net $`
- `Gross $`
- `Balance $`

No vienen como numéricos puros.  
`Balance $` además contiene separador de miles con **non-breaking space**.

### 6.4 Log enriquecido sin join validado
El log aporta slippage, latency, `risk$`, `resultR`, `durationMin`, `sessionTag` y resúmenes diarios.  
Pero:
- el CSV usa `ID`
- el log usa `posId`

No hay equivalencia directa validada en esta fase.

## 7. Chequeos estructurales básicos
- filas duplicadas completas: **0**
- `ID` duplicados: **0**
- filas totalmente vacías: **0**
- headers repetidos dentro del CSV: **no detectados**
- parseo de fechas de entrada exitoso: **1823/1823**
- parseo de fechas de cierre exitoso: **1823/1823**
- trades con cierre anterior a apertura: **0**

## 8. Hallazgos de contexto operativo
- símbolo único detectado: **US30**
- etiquetas/estrategias detectadas: **LONDON_1B1S, RRL**
- lados detectados: **Buy, Sell**
- rango temporal detectado:
  - apertura mínima: **2019-08-01 14:50:43.720000**
  - apertura máxima: **2026-04-02 16:35:00.110000**
  - cierre mínimo: **2019-08-01 15:48:40.466000**
  - cierre máximo: **2026-04-02 16:42:48.236000**

## 9. Estado de la fase
**Resultado:** dataset apto para avanzar a **FASE 1 — AUDITORÍA ESTRUCTURAL**, pero con reservas explícitas.

### Reservas activas
1. Falta `trader_id` explícito.
2. Falta política temporal formal para `UTC+1` vs Madrid/NY.
3. Falta regla de join formal entre CSV y log.

### Decisión
**ADVANCE_TO_PHASE_1_WITH_RESERVATIONS**
