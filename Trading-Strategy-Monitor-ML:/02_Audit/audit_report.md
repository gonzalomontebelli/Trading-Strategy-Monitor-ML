# FASE 1 — AUDITORÍA ESTRUCTURAL

## 1. Objetivo
Auditar la calidad estructural del dataset raw antes de diseñar la normalización.

## 2. Inputs auditados
- Dataset principal: `2026-04-02 18-45-49 History - Quantum_us30pepper (US30, m5, True, True, 0, 1, 61.5, 122.5, 9, 15, 7,).csv`
- Contrato de referencia: `config_block_phase0.json`

## 3. Validación del contrato de entrada
- `case_id`: `2026-04_Quantum_US30_SingleTrader`
- grano esperado: `1 row = 1 closed trade`
- columnas esperadas según Fase 0: `16`
- columnas observadas en el CSV: `16`
- coincidencia exacta de nombres y orden: **sí**

## 4. Resultado ejecutivo
**Decisión de Fase 1:** `ADVANCE_WITH_RESERVATIONS`  
**Confiabilidad estructural:** ALTA para avanzar a normalización, con reservas documentadas.

## 5. Chequeos estructurales principales

### 5.1 Integridad básica
- filas observadas: **1823**
- columnas observadas: **16**
- filas duplicadas completas: **0**
- `ID` duplicados: **0**
- filas con strings vacíos en cualquier columna: **0 columnas afectadas**
- columnas con nulos raw (`NaN`): **0 columnas afectadas**

### 5.2 Fechas
- parseo exitoso `Entry time (UTC+1)`: **1823/1823**
- parseo exitoso `Closing time (UTC+1)`: **1823/1823**
- formato validado: **DD/MM/YYYY HH:MM:SS.mmm**
- cierres anteriores a aperturas: **0**
- archivo ordenado por `Entry time (UTC+1)`: **sí**
- archivo ordenado por `Closing time (UTC+1)`: **no**
- timestamps de cierre duplicados: **117**  
  Nota: esto no invalida el dataset; indica cierres simultáneos o muy cercanos, por lo que el balance debe interpretarse por cierre y no por el orden raw.

### 5.3 Campos numéricos y monetarios
- parseo exitoso `Entry price`: **1823/1823**
- parseo exitoso `Closing price`: **1823/1823**
- parseo exitoso `Pips`: **1823/1823**
- parseo exitoso `Net $`: **1823/1823**
- parseo exitoso `Gross $`: **1823/1823**
- parseo exitoso `Balance $` luego de limpieza de texto: **1823/1823**
- `Balance $` contiene separador NBSP: **sí**
- `Broker commission` todo cero: **sí**
- `Swaps` todo cero: **sí**

### 5.4 Coherencia interna entre columnas
- mismatch numérico `Quantity` vs `Volume`: **0**
- mismatch `Net $` vs `Gross $`: **0**
- mismatch signo `Pips` vs `Net $`: **0**
- mismatch precio vs `Pips` en `Buy`: **0**
- mismatch precio vs `Pips` en `Sell`: **0**

## 6. Separación de columnas por tipo

### 6.1 Identificación
- `Label`
- `Symbol`
- `Type`
- `ID`

### 6.2 Ejecución
- `Entry time (UTC+1)`
- `Entry price`
- `Closing price`
- `Closing time (UTC+1)`

### 6.3 Resultado
- `Net $`
- `Pips`
- `Gross $`
- `Balance $`

### 6.4 Riesgo / tamaño / costos
- `Quantity`
- `Volume`
- `Broker commission`
- `Swaps`

## 7. Riesgos y limitaciones detectados

### 7.1 Riesgos no bloqueantes
1. **`trader_id` no existe como columna explícita.**  
   El caso se comporta como single-trader, pero esa identidad no está materializada dentro de la tabla.

2. **Semántica temporal abierta.**  
   El formato de fecha parsea bien, pero la etiqueta `UTC+1` sigue sin equivalencia formal con Madrid/NY.

3. **`Balance $` no viene como numérico puro.**  
   Requiere limpieza de NBSP para casteo confiable.

4. **El orden raw no sirve para reconstrucción secuencial de balance.**  
   El archivo está ordenado por apertura, no por cierre. Si se usa `Balance $`, debe respetarse el orden de cierre.

5. **`Net $` y `Gross $` son equivalentes solo en este export.**  
   No debe asumirse esa equivalencia como regla general del sistema.

### 7.2 Bloqueantes
**No se detectaron bloqueantes estructurales que impidan pasar a Fase 2.**

## 8. Evaluación de confiabilidad
El dataset es **confiable para avanzar a diseño de normalización**, porque:
- no tiene nulos raw en columnas críticas
- no tiene duplicados completos ni `ID` duplicados
- todas las fechas parsean
- no hay cierres anteriores a aperturas
- precios, `Pips`, `Net $` y `Gross $` son coherentes entre sí
- `Quantity` y `Volume` son consistentes a nivel numérico

La confiabilidad baja solo cuando se intenta enriquecer el caso con:
- identidad formal del trader
- semántica exacta de zona horaria
- join del log secundario

## 9. Conclusión de Fase 1
**Resultado:** `ADVANCE_WITH_RESERVATIONS`  
El raw está estructuralmente sano para pasar a Fase 2, pero con reservas documentadas que deben mantenerse abiertas en el contrato del caso.
