# Investigación intradía: datos reales 1m y señales 1m/5m

Objetivo neto 0,5 %; riesgo presupuestado 0,25 %; margen asignado ≤40 % al entrar. Nominal/margen hasta 25x autorizado para evaluar, con IM observado EEE 10 % aplicado. Una posición global, BTC primero. Retraso de entrada de un minuto tras disponer de la señal.

Las 16 combinaciones estaban registradas antes del primer P&L. Ruptura confirmada 5m es la principal; las otras tres son comparaciones, sin sustituirla por selección sobre junio–julio.

## Resultados después de costes de trading

| Periodo | Regla | Coste adicional/fill | Ops | Ops/día | Retorno periodo | DD a 1m | Aciertos | PF | Duración media máx. (min) | TP alcanzados | Margen máx. |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| development | confirmed_breakout_5m | 1 pb | 575 | 9.43 | -34.14% | 34.87% | 24.7% | 0.42 | 36.9 | 36 | 17.86% |
| development | confirmed_breakout_5m | 5 pb | 566 | 9.28 | -41.15% | 41.64% | 20.3% | 0.26 | 37.7 | 20 | 10.53% |
| development | confirmed_breakout_1m | 1 pb | 2723 | 44.64 | -97.05% | 97.05% | 10.6% | 0.11 | 6.4 | 35 | 19.38% |
| development | confirmed_breakout_1m | 5 pb | 2210 | 36.23 | -96.19% | 96.19% | 5.7% | 0.05 | 6.0 | 12 | 12.92% |
| development | reversion_5m | 1 pb | 13 | 0.21 | -1.75% | 1.96% | 23.1% | 0.19 | 22.5 | 0 | 17.42% |
| development | reversion_5m | 5 pb | 3 | 0.05 | -0.63% | 0.73% | 0.0% | 0.00 | 19.3 | 0 | 10.99% |
| development | reversion_1m | 1 pb | 15 | 0.25 | -0.98% | 1.34% | 26.7% | 0.60 | 4.1 | 1 | 18.04% |
| development | reversion_1m | 5 pb | 3 | 0.05 | -0.34% | 0.36% | 33.3% | 0.39 | 4.0 | 0 | 13.85% |
| chronological_check | confirmed_breakout_5m | 1 pb | 609 | 9.98 | -32.83% | 33.11% | 27.4% | 0.51 | 35.8 | 50 | 18.35% |
| chronological_check | confirmed_breakout_5m | 5 pb | 600 | 9.84 | -39.79% | 39.79% | 23.3% | 0.37 | 36.3 | 35 | 10.69% |
| chronological_check | confirmed_breakout_1m | 1 pb | 2946 | 48.30 | -96.55% | 96.55% | 14.1% | 0.21 | 6.5 | 68 | 19.11% |
| chronological_check | confirmed_breakout_1m | 5 pb | 2524 | 41.38 | -96.48% | 96.48% | 8.8% | 0.13 | 6.2 | 34 | 13.39% |
| chronological_check | reversion_5m | 1 pb | 13 | 0.21 | -0.14% | 1.32% | 30.8% | 0.93 | 17.5 | 3 | 13.86% |
| chronological_check | reversion_5m | 5 pb | 6 | 0.10 | -0.20% | 0.74% | 33.3% | 0.78 | 16.0 | 1 | 11.36% |
| chronological_check | reversion_1m | 1 pb | 57 | 0.93 | -9.76% | 9.83% | 8.8% | 0.12 | 2.9 | 2 | 18.85% |
| chronological_check | reversion_1m | 5 pb | 16 | 0.26 | -2.94% | 3.21% | 6.2% | 0.15 | 2.6 | 1 | 14.03% |

Coste adicional se suma a medio spread histórico rezagado y a la estimación medida de barrido del libro; comisión taker 0,05 % por lado y redondeo adverso a tick se contabilizan aparte. Funding por minuto. El margen de la tabla coincide con el asignado en estos contratos de IM 10 %.

## Calidad, medición y causalidad

Velas trade/mark reales de 1m desde el 31 de marzo hasta el 31 de julio, con el primer día para calentamiento. Bid/ask histórico a 5m: solo el último bucket ya completado, edad máxima 600 s. Las cotizaciones de analytics pueden estar muestreadas o repetidas; no son un libro ejecutable histórico.

Libro actual: 30 capturas por activo, aproximadamente un minuto. Se calcula VWAP para nominales 25/50/100/200/500 USD. Se usa el p95 de barrido adicional para 200 USD como componente estático del coste. No se midieron fills propios ni deslizamiento por latencia. HTTP RTT no es latencia de una orden.

El modelo usa un minuto completo de retraso de entrada y reservas explícitas de ejecución adversa de 1/5 pb. Aplicar la profundidad actual al pasado es una hipótesis de viabilidad actual, no una reconstrucción completa de fills históricos. Un minuto OHLC aún puede contener secuencias stop/TP indeterminadas; se toma stop primero.

## Filtro registrado

Se exige a la principal en ambos periodos y costes: ≥100 operaciones, retorno positivo, PF≥1,1, DD≤10 %, extremo inferior bootstrap positivo y ninguna posible liquidación. Supera todos los filtros: **False**. Operación real autorizada por estos resultados: **False**.

Bootstrap: 2.000 remuestreos circulares con bloques de siete días y días sin operaciones. Sus percentiles son condicionales al modelo y periodo, no probabilidades garantizadas de rentabilidad futura. Abril–julio ya se observaron con señales de mayor intervalo. Agosto–septiembre sigue reservado.

Resultados completos, causas de rechazo, componentes del P&L, incertidumbre y distribución por activo/mes están en results.json. Cada variante conserva su configuración, libro de operaciones, curva de equity a un minuto y eventos.

Cálculo local: cero llamadas a modelos, cero tokens API, cero peticiones de red durante replay y cero órdenes. Las descargas públicas previas tienen sus propios manifiestos.
