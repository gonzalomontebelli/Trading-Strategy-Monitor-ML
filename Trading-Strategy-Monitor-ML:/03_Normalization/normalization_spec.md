# FASE 2 — DISEÑO DE NORMALIZACIÓN

## 1. Objetivo
Definir el diseño lógico para transformar el dataset raw del caso `2026-04_Quantum_US30_SingleTrader` a un esquema canónico reutilizable, sin ejecutar todavía la limpieza ni modificar el archivo fuente.

## 2. Inputs utilizados
- `config_block_phase0.json`
- `audit_report.md`
- `detected_columns.csv`
- contexto validado de Fase 0 y Fase 1

## 3. Decisión de diseño
Se define un **esquema canónico mínimo** orientado a análisis de trades cerrados, manteniendo trazabilidad hacia el raw.

Este diseño **no asume** semánticas no confirmadas. Por eso:
- `trader_id` se define como **surrogate case-level** mientras no exista identificador nativo por fila.
- `open_time` y `close_time` se parsean con el formato validado, pero **sin conversión de zona horaria** mientras siga abierta la ambigüedad de `UTC+1`.
- `volume` se construye desde `Quantity` con validación cruzada contra `Volume`, porque ambas columnas fueron confirmadas como solapadas.
- `pnl_net` se toma desde `Net $`; `Gross $` queda como soporte de trazabilidad, no como fuente principal.

## 4. Esquema canónico mínimo

| canonical_field | requerido | origen lógico | tipo objetivo | regla principal |
|---|---:|---|---|---|
| trader_id | sí | derivado del caso | string | surrogate temporal a nivel caso |
| symbol | sí | `Symbol` | string | trim + uppercase |
| side | sí | `Type` | string | `Buy→BUY`, `Sell→SELL` |
| open_time | sí | `Entry time (UTC+1)` | datetime | parse `%d/%m/%Y %H:%M:%S.%f` sin conversión TZ |
| close_time | sí | `Closing time (UTC+1)` | datetime | parse `%d/%m/%Y %H:%M:%S.%f` sin conversión TZ |
| volume | sí | `Quantity` (+ cross-check `Volume`) | decimal | extraer payload numérico de tamaño |
| entry_price | sí | `Entry price` | decimal | casteo numérico directo |
| exit_price | sí | `Closing price` | decimal | casteo numérico directo |
| pnl_net | sí | `Net $` | decimal | limpieza monetaria + casteo numérico |

## 5. Campos de soporte recomendados para trazabilidad
Estos campos no reemplazan al mínimo canónico, pero deben preservarse en Fase 4 para no perder auditabilidad:

| support_field | source_column | motivo |
|---|---|---|
| trade_id | `ID` | trazabilidad por fila y futura validación de joins |
| strategy_label | `Label` | segmentación por subestrategia (`LONDON_1B1S`, `RRL`) |
| pnl_gross | `Gross $` | control de coherencia y compatibilidad con otros exports |
| pips | `Pips` | análisis operativo y chequeos de coherencia |
| balance_after_trade | `Balance $` | referencia de equity por cierre, no secuencial raw |
| broker_commission | `Broker commission` | compatibilidad futura con exports con costos |
| swaps | `Swaps` | compatibilidad futura con exports con costos |
| volume_alt_raw | `Volume` | validación cruzada de tamaño |

## 6. Reglas de normalización

### 6.1 `trader_id`
- No existe columna nativa en el raw.
- Para este caso single-trader, el valor canónico se define como surrogate temporal derivado del caso: `2026-04_Quantum_US30_SingleTrader`.
- Estado: **WARN estructural**, no `ERROR`, porque el caso fue validado como single-trader.
- Restricción: no reutilizar esta regla en datasets multi-trader sin una clave explícita.

### 6.2 `symbol`
- Fuente: `Symbol`.
- Regla: `trim` + `uppercase`.
- En este caso se detectó solo `US30`.
- Si en otro caso el símbolo queda vacío o no parseable → `ERROR`.

### 6.3 `side`
- Fuente: `Type`.
- Diccionario permitido:
  - `Buy` → `BUY`
  - `Sell` → `SELL`
- Cualquier valor fuera de ese dominio → `ERROR`.

### 6.4 `open_time` y `close_time`
- Fuentes: `Entry time (UTC+1)` y `Closing time (UTC+1)`.
- Formato validado: `%d/%m/%Y %H:%M:%S.%f`.
- Regla: parsear a datetime preservando el reloj observado en el raw.
- Regla explícita: **no convertir a UTC, Madrid o New York** en Fase 4 mientras siga abierta la ambigüedad de la etiqueta `UTC+1`.
- Validación mínima:
  - parse exitoso obligatorio
  - `close_time >= open_time`
- Estado del caso: **WARN de metadata temporal** hasta validar semántica contra log.

### 6.5 `volume`
- Fuente primaria: `Quantity`.
- Fuente secundaria de control: `Volume`.
- Regla: extraer el componente numérico del texto y almacenarlo como decimal canónico de tamaño.
- Condición de calidad:
  - si `Quantity_num == Volume_num` → continuar
  - si no coinciden → `ERROR`
- Motivo de prioridad sobre `Volume`: mantener una sola fuente primaria y usar la columna solapada como control de calidad.
- Nota: esta fase **no infiere** contrato, lot size ni multiplicador monetario.

### 6.6 `entry_price` y `exit_price`
- Fuentes: `Entry price` y `Closing price`.
- Regla: casteo numérico directo a decimal.
- Si no parsea → `ERROR`.

### 6.7 `pnl_net`
- Fuente primaria: `Net $`.
- Regla: limpiar separadores/espacios no estándar y convertir a decimal firmado.
- `Gross $` se preserva como soporte, pero no reemplaza a `Net $` como fuente principal.
- Nota de alcance: en este export `Net $ = Gross $` porque `Broker commission = 0` y `Swaps = 0`; esta equivalencia **no se generaliza** al sistema.

### 6.8 `Balance $`
- No entra al mínimo canónico.
- Se preserva como `balance_after_trade` de soporte.
- Requiere limpieza de NBSP antes de casteo.
- No puede interpretarse secuencialmente en el orden raw; cualquier uso analítico deberá respetar orden por `close_time`.

## 7. Definición de `quality_flag`

### 7.1 `OK`
Asignar `OK` cuando:
- todas las columnas canónicas mínimas existen
- `side` pertenece al dominio permitido
- `open_time` y `close_time` parsean
- `close_time >= open_time`
- `volume` parsea y pasa cross-check `Quantity` vs `Volume`
- `entry_price`, `exit_price` y `pnl_net` parsean
- no hay contradicciones de mapping en la fila
- no depende de warnings estructurales abiertos

### 7.2 `WARN`
Asignar `WARN` cuando la fila es usable pero queda afectada por advertencias abiertas del caso. Para este caso, las dos fuentes principales de `WARN` son:
- `trader_id` derivado del caso y no nativo por fila
- timestamps parseados pero con semántica de zona horaria todavía no validada

### 7.3 `ERROR`
Asignar `ERROR` cuando ocurra cualquiera de estas condiciones:
- falta una columna mínima requerida
- falla el parseo de fecha, precio, volumen o `pnl_net`
- `side` no pertenece al dominio permitido
- `close_time < open_time`
- `Quantity` y `Volume` no coinciden tras normalización numérica
- `Symbol` queda vacío o no interpretable

## 8. Bloqueantes y ambigüedades activas

### 8.1 Bloqueantes críticos abiertos
1. **`trader_id` nativo ausente**
   - El mapping existe, pero depende de surrogate case-level.
   - Impacto: el diseño es válido para single-trader; no es portable a multi-trader sin ajuste.

2. **Semántica temporal no cerrada**
   - Se conoce el formato, pero no está cerrada la equivalencia operativa de `UTC+1` respecto de UTC/Madrid/NY.
   - Impacto: no se debe convertir ni unir contra log con base temporal fuerte hasta validación.

### 8.2 Riesgos no bloqueantes
1. `ID` vs `posId` sigue sin regla de join validada.
2. `Net $` y `Gross $` equivalen solo en este export.
3. `Balance $` requiere limpieza de texto y orden por cierre para análisis secuencial.

## 9. Decisión de Fase 2
**Resultado:** `ADVANCE_TO_PHASE_3_WITH_RESERVATIONS`

La fase queda cerrada como **diseño lógico válido**, pero no como diseño libre de ambigüedades. El mapping mínimo está definido y es utilizable para Fase 3, siempre que se mantengan activas las advertencias de:
- `trader_id` surrogate
- semántica temporal
- join con log

## 10. Alcance explícito de esta fase
- Sí define contrato canónico y reglas de transformación.
- Sí define `quality_flag`.
- No ejecuta limpieza.
- No resuelve joins con el log.
- No valida timezone a nivel operacional.
