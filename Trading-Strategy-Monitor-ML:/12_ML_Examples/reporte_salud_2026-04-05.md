# Reporte de Salud de la Estrategia
## Sistema: Quantum_us30pepper — US30
### Período: 24 marzo – 2 abril 2026
### Generado: 2026-04-05

---

## 1. Resumen de Rendimiento

| Métrica | Período | Baseline histórico |
|---|---|---|
| Trades ejecutados | 8 | — |
| Días operados | 5 | — |
| Wins | 2 (25.0%) | 45.97% |
| Losses | 6 | — |
| PnL neto | **−$77.82** | — |
| Profit Factor | 0.662 | 1.564 |
| Avg Win | $76.26 | ~$1,095.94 |
| Avg Loss | −$38.39 | — |
| R/trade promedio | −0.238 | +0.375 |
| Balance inicio período | $3,947.12 | — |
| Balance cierre período | $3,869.30 | — |
| DD del período | −1.97% | — |
| DD desde inicio cuenta ($4,000) | −3.27% | 14.47% máx histórico |

**Breakdown por sub-estrategia:**

| Estrategia | Trades | Wins | WR período | WR baseline | PnL |
|---|---|---|---|---|---|
| RRL | 7 | 1 | 14.3% | 47.2% | −$156.18 |
| LONDON_1B1S | 1 | 1 | 100.0% | 43.5% | +$78.36 |

---

## 2. Análisis de Desviación — Esperado vs. Real

### 2.1 Win Rate

| | Valor |
|---|---|
| WR esperado (baseline) | 45.97% |
| WR observado (período) | 25.0% |
| Desviación absoluta | −20.97 pp |
| Test binomial p-valor (unilateral) | 0.204 |
| ¿Significativo estadísticamente? | **No** |

Con n=8 operaciones, observar 2 o menos wins tiene probabilidad del 20.4% incluso si el sistema opera con su WR histórico normal. La muestra es demasiado pequeña para distinguir entre ruido estadístico y deterioro estructural.

**Interpretación:** desviación dentro del rango de varianza esperada para muestras de 8 trades.

### 2.2 Sub-estrategia RRL

| | Valor |
|---|---|
| WR esperado RRL (baseline) | 47.2% |
| WR observado RRL | 14.3% (1/7) |
| Test binomial p-valor (unilateral) | 0.083 |
| ¿Significativo estadísticamente? | **Borderline** (umbral convencional: 0.05) |

RRL acumula 7 de los 8 trades del período con solo 1 win. El p-valor de 0.083 es el dato más relevante del período: está por encima del umbral convencional de significancia (α=0.05), pero es lo suficientemente bajo como para no ignorarlo. No confirma deterioro, pero lo señaliza.

### 2.3 R por trade

| | Valor |
|---|---|
| R esperado por trade | +0.3754 |
| R observado por trade | −0.2380 |
| Diferencia | −0.6134 R |
| Error estándar (n=8) | 0.528 |
| Z-score | −1.16 |
| p-valor (unilateral) | 0.122 |
| ¿Significativo estadísticamente? | **No** |

La desviación de R/trade tampoco alcanza significancia estadística con esta muestra. El sistema no ha entrado en pérdida estructural confirmada.

### 2.4 Ejecución y calidad operativa

| Métrica | Período | Límite operativo |
|---|---|---|
| Avg spread | 2.02 pips | máx 3.5 pips |
| Slippage apertura (signed) | −2.11 pips (favorable) | — |
| Slippage cierre (signed) | −0.30 pips (favorable) | — |
| Latencia promedio | 381 ms | — |
| Evento latencia alta | 857 ms (24/03, único) | — |

La ejecución es técnicamente sana. El slippage promedio resultó favorable (el broker ejecutó levemente mejor que el precio de referencia en apertura). El spread promedio de 2.02 pips está dentro del límite configurado de 3.5 pips. No se detectan problemas de infraestructura.

El evento de latencia aislado (857 ms, 24/03) no afectó el resultado de ese trade (SL hit, −0.50R). No requiere acción.

---

## 3. Diagnóstico de Mercado

### 3.1 Evento crítico: Liberation Day — 2 de abril de 2026

El 2 de abril de 2026, la administración Trump anunció aranceles recíprocos globales ("Liberation Day"), generando el mayor shock de volatilidad en US30 desde la pandemia de 2020. El índice sufrió una caída abrupta de aproximadamente 1,500 puntos en la sesión.

**Este evento es relevante para la evaluación del período por tres razones:**

1. **El sistema opera con sesgo BUY dominante (75.5% histórico).** Un evento de caída pronunciada en el índice crea condiciones estructuralmente adversas para la estrategia tal como está calibrada.

2. **El RRL (Range Reversal Logic)** fue el sub-sistema más expuesto: 7 de sus 8 operaciones del período se ejecutaron en condiciones de mercado potencialmente perturbadas por el build-up de tensión previo al anuncio y la caída posterior.

3. **NewsGuard Lite no cubre este evento.** El filtro del bot bloquea NFP, CPI, Powell, Jackson Hole y Michigan Sentiment, pero no tiene regla para eventos de política comercial de esta magnitud. La estrategia operó con exposición total durante y post-anuncio.

### 3.2 Implicación para la interpretación del período

El under-performance del período tiene una explicación de régimen identificable. Esto no invalida el edge histórico, pero sí implica que la estrategia entró en un entorno de mercado que difiere materialmente de su base de entrenamiento (backtest 2019–2026, que incluye pero no overrepresenta episodios de shock unidireccional violento en el índice).

**La hipótesis de trabajo es:** el resultado negativo del período responde principalmente al cambio de régimen inducido por Liberation Day, no a un deterioro interno del edge.

Esta hipótesis no puede confirmarse con 8 trades. Solo puede monitorearse en las semanas siguientes.

---

## 4. Semáforo de Continuidad Operativa

### 🟡 AMARILLO

**Motivo del color:**

El sistema presenta under-performance en el período analizado, pero las pruebas estadísticas no alcanzan significancia con n=8. El deterioro no está confirmado como estructural. Sin embargo, la combinación de tres factores impide el verde:

- RRL con WR 14.3% en 7 trades y p-valor borderline (0.083) — señal de atención, no de alarma
- Evento de régimen documentado (Liberation Day, 2/04) que modifica el contexto operativo del sistema
- Sistema sin filtro para shocks de política comercial: riesgo operativo no cubierto por NewsGuard Lite

**Lo que NO activa el rojo:**
- DD del período: −1.97% (dentro del rango de varianza normal; hard limit es −10% mensual)
- DD desde inicio de cuenta: −3.27% (límite de pausa es −20%)
- Ejecución técnica sana (spread, slippage, latencia)
- WR global p-valor = 0.204 (no significativo)
- Z-score R/trade = −1.16 (no significativo)
- Muestra de 8 trades: insuficiente para confirmar cambio estructural

---

## 5. Decisión Operativa

**MANTENER tamaño actual. NO escalar. Revisar en siguiente ciclo semanal.**

Acciones concretas:

1. **No aumentar el tamaño de posición** en el próximo ciclo. La regla del plan compuesto establece que no se escala mientras el semáforo esté en amarillo.

2. **Monitorear RRL específicamente** en las próximas 2 semanas. Si RRL mantiene WR < 30% sobre las próximas 10–15 operaciones acumuladas, el p-valor acumulado cruzará el umbral de significancia y corresponderá evaluar una pausa o ajuste de parámetros.

3. **Evaluar ampliar NewsGuard Lite** para cubrir eventos de política comercial (anuncios USTR, escaladas arancelarias). Esto requiere una modificación en el código fuente del bot.

4. **Próxima revisión:** semana del 6–11 de abril de 2026. Si el contexto de régimen se normaliza (recuperación parcial del índice, reducción de volatilidad VIX-equivalent) y RRL muestra recuperación, corresponde volver a verde.

---

## 6. Alertas Abiertas

| Tipo | Descripción | Urgencia |
|---|---|---|
| Monitoreo RRL | WR 14.3% en 7 trades, p=0.083 | Alta |
| Régimen de mercado | Liberation Day — volatilidad elevada post-anuncio | Alta |
| NewsGuard gap | Sin cobertura para shocks de política comercial | Media |
| Data quality (heredado) | Warning de timezone y trader_id_surrogate (abierto desde fase de backtest) | Baja |

---

## 7. Contexto Acumulado del Plan

| | Valor |
|---|---|
| Capital inicial plan ($) | $4,000.00 |
| Balance actual | $3,869.30 |
| DD acumulado desde inicio | −3.27% |
| Hard limit de pausa (DD) | −20% desde inicio o −10% mensual |
| Estado plan compuesto | **No escalar en siguiente ciclo** |
| Semáforo acumulado | 🟡 AMARILLO |

El plan de interés compuesto sigue activo. El drawdown acumulado de −3.27% es manejable y no compromete la lógica de escalado. La primera revisión de escalado estaba proyectada al cierre del primer mes de operativa; esa decisión se pospone hasta que el semáforo vuelva a verde.

---

*Reporte generado automáticamente sobre datos reales de broker (cT_1329775_2026-04-05_09-50.csv) y log operativo (2026-04-05_09-43 - Quantum_us30pepper, Instance 926220.log). Baseline: 2026-04_Quantum_US30_SingleTrader (1823 trades, agosto 2019 – abril 2026).*
