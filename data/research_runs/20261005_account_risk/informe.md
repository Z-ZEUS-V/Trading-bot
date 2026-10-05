# Objetivos sobre equity: ejercicio numérico

Cálculos de escenarios; no son resultados de una estrategia ni un backtest.

Equity: 50.00 USD. Entrada: 0.0500%; salida: 0.0500% del nominal correspondiente.
La tabla usa largos y un coste adicional HIPOTÉTICO de 0,04 % del nominal inicial por operación completa.
No incluye funding. Los porcentajes de stop son movimientos del precio hasta un fill ideal, no pérdida garantizada.

| Exposición/equity | Nominal USD | Coste con precio constante USD | Precio para +5 % cuenta | Precio para +10 % cuenta | Caída para -2 % cuenta | Caída para -5 % cuenta |
|---:|---:|---:|---:|---:|---:|---:|
| 1x | 50.00 | 0.07 | 5.143% | 10.145% | 1.861% | 4.862% |
| 2x | 100.00 | 0.14 | 2.641% | 5.143% | 0.860% | 2.361% |
| 3x | 150.00 | 0.21 | 1.808% | 3.475% | 0.527% | 1.527% |
| 5x | 250.00 | 0.35 | 1.141% | 2.141% | 0.260% | 0.860% |
| 10x | 500.00 | 0.70 | 0.640% | 1.141% | 0.060% | 0.360% |

10x consume el 100 % de equity como margen inicial si IM=10 %, antes de costes: no es una propuesta operativa.

## Acierto de equilibrio bajo dos únicos resultados

| Pérdida neta | Ganancia neta | Beneficio/riesgo | Acierto para esperanza aritmética cero | Acierto para crecimiento logarítmico cero |
|---:|---:|---:|---:|---:|
| 2% | 5% | 2.50 | 28.57% | 29.28% |
| 2% | 10% | 5.00 | 16.67% | 17.49% |
| 4% | 5% | 1.25 | 44.44% | 45.55% |
| 4% | 10% | 2.50 | 28.57% | 29.99% |
| 5% | 5% | 1.00 | 50.00% | 51.25% |
| 5% | 10% | 2.00 | 33.33% | 34.99% |

Superar el umbral es necesario en este modelo simplificado; la estrategia aún debe demostrar su distribución real de resultados.

## Diez pérdidas consecutivas con riesgo fraccional

| Riesgo | Saldo USD | Caída acumulada | Ganancia necesaria para recuperar |
|---:|---:|---:|---:|
| 2% | 40.85 | 18.29% | 22.39% |
| 4% | 33.24 | 33.52% | 50.41% |
| 5% | 29.94 | 40.13% | 67.02% |

No se estima la probabilidad de esa racha. Los objetivos no generan por sí mismos una ventaja estadística.

## Fórmula

`R = L * [d * (x - 1) - f_entrada - f_salida * x - c]`

`x = (R/L + d + f_entrada + c) / (d - f_salida)`

R: rendimiento neto sobre equity; L: nominal inicial/equity; d: +1 largo o -1 corto; x: precio salida/entrada; c: coste extra sobre nominal inicial.

Referencias consultadas el 2026-10-05: [comisiones EEE](https://support.kraken.com/au/articles/fees-for-derivatives-trading-eea) y [márgenes EEE](https://support.kraken.com/articles/derivatives-margin-schedule-and-maximum-leverage-eea).
