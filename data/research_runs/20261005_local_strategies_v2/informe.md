# Primera simulación local de estrategias

Resultados exploratorios con datos históricos, costes actuales e hipótesis de ejecución. No es operación real ni validación de rentabilidad futura.

## Alcance

Capital inicial: 50.00 USD por ventana y variante. Una posición total, cruzado USD, riesgo planificado 2%, exposición máxima 2x. Objetivos netos: 5%, 10% sobre equity al entrar.
Ventanas: development [2026-02-14T00:00:00+00:00, 2026-06-01T00:00:00+00:00); chronological_validation [2026-06-01T00:00:00+00:00, 2026-08-01T00:00:00+00:00). Extremos derechos excluidos; cada ventana empieza de nuevo con el capital inicial.
Periodo reservado [2026-08-01T00:00:00+00:00, 2026-10-02T01:00:00+00:00): no se calcularon señales/resultados de estrategias para él. No se ajustaron parámetros entre desarrollo y validación.

## Conciliación de datos

- PF_XBTUSD: 5555 observaciones comunes; 0 discrepancias; 2 horas recuperadas de analytics; 6 horas siguen ausentes fuera de las ventanas elegidas. Ticker de la hora actual coincide: True.
- PF_ETHUSD: 5555 observaciones comunes; 0 discrepancias; 2 horas recuperadas de analytics; 6 horas siguen ausentes fuera de las ventanas elegidas. Ticker de la hora actual coincide: True.

Se excluyó la vela parcial de las 01:00 UTC del 2 de octubre en trade/mark. El funding se contabiliza como tasa absoluta USD por unidad base y hora, con signo negativo para largos cuando la tasa es positiva.
La coincidencia entre fuentes y ticker respalda el mapeo; no se conciliaron movimientos privados de cuenta. Los valores recuperados son observaciones, no interpolaciones ni ceros inventados.

## Todas las variantes

Comisión taker: 0.050% por lado. Fricción adicional por fill: 2.0 puntos básicos, 5.0 puntos básicos, más redondeo adverso a tick. Son escenarios hipotéticos de spread/deslizamiento, no mediciones de ejecución.

| Ventana | Regla | Objetivo | Fricción/fill | Operaciones | Saldo USD | Retorno neto | DD horario | Acierto | Fees USD | Funding USD |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| development | H1_breakout_4h | 5% | 2 pb | 25 | 42.41 | -15.18% | 19.00% | 24.0% | 0.587 | 0.066 |
| development | H1_breakout_4h | 10% | 2 pb | 24 | 42.61 | -14.79% | 18.52% | 25.0% | 0.567 | 0.074 |
| development | H2_momentum_1d | 5% | 2 pb | 7 | 50.00 | 0.01% | 4.54% | 57.1% | 0.056 | 0.018 |
| development | H2_momentum_1d | 10% | 2 pb | 7 | 50.00 | 0.01% | 4.54% | 57.1% | 0.056 | 0.018 |
| development | H1_breakout_4h | 5% | 5 pb | 25 | 42.29 | -15.41% | 19.19% | 24.0% | 0.585 | 0.066 |
| development | H1_breakout_4h | 10% | 5 pb | 24 | 42.40 | -15.20% | 18.86% | 25.0% | 0.567 | 0.074 |
| development | H2_momentum_1d | 5% | 5 pb | 7 | 49.97 | -0.05% | 4.56% | 57.1% | 0.056 | 0.018 |
| development | H2_momentum_1d | 10% | 5 pb | 7 | 49.97 | -0.05% | 4.56% | 57.1% | 0.056 | 0.018 |
| chronological_validation | H1_breakout_4h | 5% | 2 pb | 13 | 50.75 | 1.51% | 11.92% | 30.8% | 0.475 | -0.068 |
| chronological_validation | H1_breakout_4h | 10% | 2 pb | 12 | 51.71 | 3.42% | 11.85% | 33.3% | 0.455 | -0.069 |
| chronological_validation | H2_momentum_1d | 5% | 2 pb | 5 | 51.96 | 3.92% | 1.92% | 40.0% | 0.045 | 0.014 |
| chronological_validation | H2_momentum_1d | 10% | 2 pb | 3 | 51.95 | 3.90% | 3.26% | 66.7% | 0.039 | 0.060 |
| chronological_validation | H1_breakout_4h | 5% | 5 pb | 13 | 50.64 | 1.27% | 12.09% | 30.8% | 0.475 | -0.067 |
| chronological_validation | H1_breakout_4h | 10% | 5 pb | 12 | 51.54 | 3.07% | 11.91% | 33.3% | 0.450 | -0.068 |
| chronological_validation | H2_momentum_1d | 5% | 5 pb | 5 | 51.85 | 3.71% | 1.74% | 40.0% | 0.045 | 0.010 |
| chronological_validation | H2_momentum_1d | 10% | 5 pb | 3 | 51.93 | 3.85% | 3.28% | 66.7% | 0.039 | 0.060 |

En validación, 8 de 8 variantes terminaron con P&L neto positivo. Esto describe únicamente este replay. Ninguna variante queda aprobada para operar.

## Riesgo y ambigüedad

| Ventana / variante | Stops y TP en misma hora | Operaciones sobre presupuesto de pérdida | Objetivo neto alcanzado | Incertidumbre acumulada funding USD | Estado |
|---|---:|---:|---:|---:|---|
| development / H1_breakout_4h_tp5_base_2bps_each_fill | 0 | 0 | 2 | 0.00223 | exploratory_only |
| development / H1_breakout_4h_tp10_base_2bps_each_fill | 0 | 0 | 0 | 0.00193 | exploratory_only |
| development / H2_momentum_1d_tp5_base_2bps_each_fill | 0 | 0 | 0 | 0.00002 | exploratory_only |
| development / H2_momentum_1d_tp10_base_2bps_each_fill | 0 | 0 | 0 | 0.00002 | exploratory_only |
| development / H1_breakout_4h_tp5_stress_5bps_each_fill | 0 | 0 | 2 | 0.00221 | exploratory_only |
| development / H1_breakout_4h_tp10_stress_5bps_each_fill | 0 | 0 | 0 | 0.00193 | exploratory_only |
| development / H2_momentum_1d_tp5_stress_5bps_each_fill | 0 | 0 | 0 | 0.00002 | exploratory_only |
| development / H2_momentum_1d_tp10_stress_5bps_each_fill | 0 | 0 | 0 | 0.00002 | exploratory_only |
| chronological_validation / H1_breakout_4h_tp5_base_2bps_each_fill | 0 | 0 | 3 | 0.00331 | exploratory_only |
| chronological_validation / H1_breakout_4h_tp10_base_2bps_each_fill | 0 | 0 | 1 | 0.00234 | exploratory_only |
| chronological_validation / H2_momentum_1d_tp5_base_2bps_each_fill | 0 | 0 | 1 | 0.00034 | exploratory_only |
| chronological_validation / H2_momentum_1d_tp10_base_2bps_each_fill | 0 | 0 | 0 | 0.00000 | exploratory_only |
| chronological_validation / H1_breakout_4h_tp5_stress_5bps_each_fill | 0 | 0 | 3 | 0.00325 | exploratory_only |
| chronological_validation / H1_breakout_4h_tp10_stress_5bps_each_fill | 0 | 0 | 1 | 0.00227 | exploratory_only |
| chronological_validation / H2_momentum_1d_tp5_stress_5bps_each_fill | 0 | 0 | 1 | 0.00013 | exploratory_only |
| chronological_validation / H2_momentum_1d_tp10_stress_5bps_each_fill | 0 | 0 | 0 | 0.00000 | exploratory_only |

El riesgo inicial reserva el 10% del presupuesto de pérdida para funding; esa reserva no garantiza cubrirlo. El stop puede acercarse al precio para respetar el presupuesto restante, nunca alejarse. Gaps o fills peores pueden superarlo.
Cuando hay salida intrahoraria se desconoce su minuto: se aplica débito de funding de una hora completa o crédito cero. El ancho de incertidumbre se registra. Esta prudencia por operación no es una cota matemática de todas las trayectorias alternativas de cartera.
Stop y objetivo tocados dentro de la misma hora: stop primero. No se conoce la secuencia real. Se marca el caso y no se finge precisión de ticks.
Si el mark permite una liquidación antes de resolver la secuencia de salida, el motor detiene e invalida la variante. No modela una liquidación real ni sus penalizaciones.

## Contexto del mercado

La referencia pasiva siguiente compra y mantiene aproximadamente 1x. Tiene un riesgo distinto del de las estrategias con stop; no permite afirmar superioridad ajustada al riesgo. Abstenerse conserva 50.00 USD antes de gastos externos.

| Ventana | Activo | Fricción/fill | Saldo pasivo USD | Retorno | DD horario |
|---|---|---:|---:|---:|---:|
| development | PF_XBTUSD | 2 pb | 53.46 | 6.91% | 12.88% |
| development | PF_ETHUSD | 2 pb | 48.79 | -2.43% | 19.40% |
| development | PF_XBTUSD | 5 pb | 53.43 | 6.85% | 12.88% |
| development | PF_ETHUSD | 5 pb | 48.76 | -2.48% | 19.41% |
| chronological_validation | PF_XBTUSD | 2 pb | 43.30 | -13.41% | 18.79% |
| chronological_validation | PF_ETHUSD | 2 pb | 46.20 | -7.60% | 23.65% |
| chronological_validation | PF_XBTUSD | 5 pb | 43.27 | -13.46% | 18.79% |
| chronological_validation | PF_ETHUSD | 5 pb | 46.17 | -7.66% | 23.66% |

## Límites de interpretación

- Las ventanas son cortas, especialmente para la regla diaria. No se han estimado intervalos de confianza ni corregido formalmente la selección entre variantes. No hay walk-forward entrenado: estas reglas están fijas y no tienen una fase de ajuste.
- El drawdown usa equity marcada al cierre horario y después de salidas; puede subestimar excursiones entre observaciones. Las salidas intrahorarias se sitúan dentro de un intervalo, no en un instante conocido.
- Las reglas actuales de lote, tick, margen y tarifa se aplican a precios históricos para evaluar viabilidad presente. No son una reconstrucción de todas las reglas vigentes en cada fecha.
- USD como garantía, sin conversiones ni recortes. No incluye fiscalidad, intereses por saldo USD negativo, infraestructura ni análisis. La cartera propuesta mantiene liquidez USD; no se certifica elegibilidad de la cuenta.
- No se simulan colas, fills parciales, protección de precio, latencia de red ni rechazos del exchange. Los resultados no validan la ejecución real.
- El P&L bruto ya incorpora fricción de fills. La columna de fricción es informativa; no se descuenta una segunda vez.
- BTC tiene prioridad fija cuando ambas señales coinciden. La contribución por activo está en summary.json; resultados concentrados en un activo no prueban generalización.

## Coste y monitorización posterior

Esta ejecución tardó 3.52 segundos en este ordenador. El motor usa únicamente la biblioteca estándar de Python: cero llamadas a modelos, cero tokens de API y cero peticiones de red durante el replay.
Para vigilar en directo, el diseño permite un adaptador de precios público, reglas locales al cerrar cada vela y un supervisor de posición independiente. No hace falta consultar a un LLM por tick. El servicio 24/7, reconexiones y alertas todavía no están implementados; electricidad, conexión y disponibilidad del equipo siguen teniendo coste.
Cambiar de exchange exigiría sustituir el adaptador de datos/contratos/costes y repetir la evaluación. Las señales y la contabilidad local no importan SDKs de agentes.

## Archivos y reproducción

config.json fija parámetros y ventanas; funding_audit.json y funding_normalized.csv.gz documentan conciliación; summary.json/summary.csv contienen métricas; cada variante guarda operaciones y equity horaria; manifest.json registra hashes y duración.
Ejecutar desde la raíz: `python scripts/run_local_strategy_research.py --output data/research_runs/<directorio-nuevo>`.

Fuentes: [especificaciones y funding EEE](https://support.kraken.com/es/articles/perpetual-contract-specifications-for-clients-in-the-eea), [márgenes EEE](https://support.kraken.com/articles/derivatives-margin-schedule-and-maximum-leverage-eea), [comisiones EEE](https://support.kraken.com/au/articles/fees-for-derivatives-trading-eea), [histórico de funding](https://docs.kraken.com/api-reference/historical-funding-rates/historical-funding-rates).
