from pathlib import Path
import json
import csv

case_id = "2026-04_Quantum_US30_SingleTrader"
# Path relative to project root — adjust as needed
base = Path(".") / "03_Normalization"
base.mkdir(parents=True, exist_ok=True)

# This script generates Phase 2 documentation artifacts.
# It does not clean data or touch the raw files. It only materializes the validated logical design.

normalization_md = f'''# FASE 2 — DISEÑO DE NORMALIZACIÓN

## 1. Objetivo
Definir el diseño lógico para transformar el dataset raw del caso `{case_id}` a un esquema canónico reutilizable, sin ejecutar todavía la limpieza ni modificar el archivo fuente.

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
- Para este caso single-trader, el valor canónico se define como surrogate temporal derivado del caso: `{case_id}`.
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
'''

(base / 'normalization_spec.md').write_text(normalization_md, encoding='utf-8')

canonical_map = {
    "case_id": case_id,
    "phase": "FASE 2 - DISEÑO DE NORMALIZACIÓN",
    "status": "ADVANCE_TO_PHASE_3_WITH_RESERVATIONS",
    "canonical_schema_minimum": [
        "trader_id",
        "symbol",
        "side",
        "open_time",
        "close_time",
        "volume",
        "entry_price",
        "exit_price",
        "pnl_net"
    ],
    "traceability_support_fields": [
        "trade_id",
        "strategy_label",
        "pnl_gross",
        "pips",
        "balance_after_trade",
        "broker_commission",
        "swaps",
        "volume_alt_raw"
    ],
    "field_map": {
        "trader_id": {
            "source_type": "derived_case_constant",
            "source_column": None,
            "value": case_id,
            "target_dtype": "string",
            "required": True,
            "rule": "Usar surrogate case-level solo para este caso single-trader.",
            "quality_impact": "WARN"
        },
        "symbol": {
            "source_type": "raw_column",
            "source_column": "Symbol",
            "target_dtype": "string",
            "required": True,
            "rule": "trim + uppercase",
            "quality_impact": "ERROR_if_empty_or_unparseable"
        },
        "side": {
            "source_type": "raw_column",
            "source_column": "Type",
            "target_dtype": "string",
            "required": True,
            "rule": {"Buy": "BUY", "Sell": "SELL"},
            "quality_impact": "ERROR_if_outside_domain"
        },
        "open_time": {
            "source_type": "raw_column",
            "source_column": "Entry time (UTC+1)",
            "target_dtype": "datetime",
            "required": True,
            "rule": {
                "parse_format": "%d/%m/%Y %H:%M:%S.%f",
                "timezone_strategy": "parse_only_keep_raw_clock",
                "timezone_status": "unvalidated_label"
            },
            "quality_impact": "WARN_until_timezone_semantics_validated"
        },
        "close_time": {
            "source_type": "raw_column",
            "source_column": "Closing time (UTC+1)",
            "target_dtype": "datetime",
            "required": True,
            "rule": {
                "parse_format": "%d/%m/%Y %H:%M:%S.%f",
                "timezone_strategy": "parse_only_keep_raw_clock",
                "timezone_status": "unvalidated_label",
                "validation": "close_time >= open_time"
            },
            "quality_impact": "WARN_until_timezone_semantics_validated"
        },
        "volume": {
            "source_type": "raw_column_with_crosscheck",
            "source_column": "Quantity",
            "crosscheck_column": "Volume",
            "target_dtype": "decimal",
            "required": True,
            "rule": {
                "extract_numeric_payload": True,
                "primary_source": "Quantity",
                "crosscheck": "normalized_numeric(Quantity) == normalized_numeric(Volume)"
            },
            "quality_impact": "ERROR_if_crosscheck_fails"
        },
        "entry_price": {
            "source_type": "raw_column",
            "source_column": "Entry price",
            "target_dtype": "decimal",
            "required": True,
            "rule": "numeric_cast_direct",
            "quality_impact": "ERROR_if_parse_fails"
        },
        "exit_price": {
            "source_type": "raw_column",
            "source_column": "Closing price",
            "target_dtype": "decimal",
            "required": True,
            "rule": "numeric_cast_direct",
            "quality_impact": "ERROR_if_parse_fails"
        },
        "pnl_net": {
            "source_type": "raw_column",
            "source_column": "Net $",
            "target_dtype": "decimal",
            "required": True,
            "rule": "money_text_cleanup_then_numeric_cast",
            "quality_impact": "ERROR_if_parse_fails"
        }
    },
    "support_field_map": {
        "trade_id": "ID",
        "strategy_label": "Label",
        "pnl_gross": "Gross $",
        "pips": "Pips",
        "balance_after_trade": "Balance $",
        "broker_commission": "Broker commission",
        "swaps": "Swaps",
        "volume_alt_raw": "Volume"
    },
    "quality_flag": {
        "OK": [
            "all_minimum_fields_present_and_parseable",
            "side_in_allowed_domain",
            "close_time_gte_open_time",
            "volume_crosscheck_passes",
            "no_open_case_warnings_apply"
        ],
        "WARN": [
            "row_usable_but_depends_on_case_level_surrogate_trader_id",
            "row_usable_but_timezone_semantics_still_unvalidated"
        ],
        "ERROR": [
            "missing_required_column",
            "date_parse_failure",
            "side_outside_domain",
            "close_before_open",
            "volume_crosscheck_failure",
            "numeric_parse_failure",
            "empty_or_unparseable_symbol"
        ]
    },
    "open_blockers": [
        {
            "id": "AMB_001",
            "topic": "trader_id missing at row level",
            "severity": "high",
            "status": "open"
        },
        {
            "id": "AMB_002",
            "topic": "time zone semantics",
            "severity": "high",
            "status": "open"
        },
        {
            "id": "AMB_003",
            "topic": "log join key",
            "severity": "medium",
            "status": "open"
        }
    ]
}
(base / 'canonical_map.json').write_text(json.dumps(canonical_map, indent=2, ensure_ascii=False), encoding='utf-8')

rows = [
    ["1", "canonical_minimum", "trader_id", "", "derived_case_constant", case_id, "string", "yes", "surrogate temporal a nivel caso; no reutilizable en multi-trader", "WARN", "No existe columna trader en el raw"],
    ["2", "canonical_minimum", "symbol", "Symbol", "raw_column", "trim + uppercase", "string", "yes", "valor no vacío y reconocible", "ERROR", "Único símbolo detectado: US30"],
    ["3", "canonical_minimum", "side", "Type", "raw_column", "Buy→BUY; Sell→SELL", "string", "yes", "dominio cerrado BUY/SELL", "ERROR", "No admitir otros valores"],
    ["4", "canonical_minimum", "open_time", "Entry time (UTC+1)", "raw_column", "%d/%m/%Y %H:%M:%S.%f; parse sin conversión TZ", "datetime", "yes", "parse exitoso requerido", "WARN", "Mantener reloj raw hasta validar timezone"],
    ["5", "canonical_minimum", "close_time", "Closing time (UTC+1)", "raw_column", "%d/%m/%Y %H:%M:%S.%f; parse sin conversión TZ; close>=open", "datetime", "yes", "parse exitoso y close_time>=open_time", "WARN", "Mantener reloj raw hasta validar timezone"],
    ["6", "canonical_minimum", "volume", "Quantity", "raw_column_with_crosscheck", "extraer payload numérico; cross-check con Volume", "decimal", "yes", "Quantity_num debe coincidir con Volume_num", "ERROR", "Quantity queda como fuente primaria"],
    ["7", "canonical_minimum", "entry_price", "Entry price", "raw_column", "numeric_cast_direct", "decimal", "yes", "parse numérico obligatorio", "ERROR", ""],
    ["8", "canonical_minimum", "exit_price", "Closing price", "raw_column", "numeric_cast_direct", "decimal", "yes", "parse numérico obligatorio", "ERROR", ""],
    ["9", "canonical_minimum", "pnl_net", "Net $", "raw_column", "money_text_cleanup_then_numeric_cast", "decimal", "yes", "parse numérico obligatorio", "ERROR", "Gross $ queda solo como soporte"],
    ["10", "traceability_support", "trade_id", "ID", "raw_column", "preservar valor original", "int64|string", "recommended", "unicidad por fila", "ERROR", "Clave útil para trazabilidad y joins futuros"],
    ["11", "traceability_support", "strategy_label", "Label", "raw_column", "trim preservando dominio observado", "string", "recommended", "opcional", "OK", "Valores detectados: LONDON_1B1S, RRL"],
    ["12", "traceability_support", "pnl_gross", "Gross $", "raw_column", "money_text_cleanup_then_numeric_cast", "decimal", "recommended", "opcional", "OK", "No usar como fuente principal de pnl_net"],
    ["13", "traceability_support", "pips", "Pips", "raw_column", "numeric_cast_direct", "decimal", "recommended", "opcional", "OK", "Útil para controles y análisis"],
    ["14", "traceability_support", "balance_after_trade", "Balance $", "raw_column", "money_text_cleanup_then_numeric_cast", "decimal", "recommended", "opcional", "WARN", "No usar secuencialmente en orden raw"],
    ["15", "traceability_support", "broker_commission", "Broker commission", "raw_column", "numeric_cast_direct", "decimal", "recommended", "opcional", "OK", "En este export todo observado es 0"],
    ["16", "traceability_support", "swaps", "Swaps", "raw_column", "numeric_cast_direct", "decimal", "recommended", "opcional", "OK", "En este export todo observado es 0"],
    ["17", "traceability_support", "volume_alt_raw", "Volume", "raw_column", "preservar raw para cross-check", "string", "recommended", "opcional", "WARN", "Solapada con Quantity"],
]

with open(base / 'field_mapping.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([
        'mapping_order','mapping_scope','canonical_field','source_column','source_type',
        'transformation_rule','target_dtype','required_for_phase4','validation_rule','default_quality_impact','notes'
    ])
    writer.writerows(rows)

print(f"Artefactos de Fase 2 generados en: {base}")
