# Riesgo, margen y apalancamiento: comparación registrada

Cálculo local. Tres riesgos para TP neto 0,5 %, dos costes y dos periodos. Una posición total. 40 % de margen asignado como máximo; la comisión de entrada también debe dejar 60 % libre al entrar. El multiplicador 25x es nominal/margen; nominal/equity es otra magnitud.

La captura pública de BTC/ETH para europa/retail exige IM 10 % (nominal/margen 10x). 25x solo aparece como aritmética hipotética, sin simular margen regulatorio ficticio. El saldo libre sigue respaldando pérdidas en cruzado.

| Ventana | Caso | Fricción/fill | Ops | Ops/día | Retorno periodo | DD horario | Aciertos | PF | Margen medio/máx. | IC bootstrap del retorno |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| development | primary_rr2 | 2 pb | 73 | 0.68 | -0.43% | 2.71% | 35.6% | 0.95 | 1.41%/4.02% | [-5.11%, 4.36%] |
| development | primary_rr2 | 5 pb | 77 | 0.72 | -1.63% | 3.84% | 31.2% | 0.83 | 1.36%/4.02% | [-6.07%, 3.26%] |
| development | sensitivity_rr1 | 2 pb | 89 | 0.83 | 3.79% | 3.44% | 49.4% | 1.22 | 2.89%/7.68% | [-3.80%, 11.88%] |
| development | sensitivity_rr1 | 5 pb | 88 | 0.82 | 2.99% | 3.43% | 48.9% | 1.18 | 2.82%/7.73% | [-3.90%, 10.63%] |
| development | sensitivity_rr5 | 2 pb | 48 | 0.45 | -0.16% | 1.14% | 27.1% | 0.93 | 0.52%/1.33% | [-1.80%, 1.73%] |
| development | sensitivity_rr5 | 5 pb | 48 | 0.45 | -0.20% | 1.25% | 25.0% | 0.92 | 0.51%/1.33% | [-1.86%, 1.78%] |
| chronological_check | primary_rr2 | 2 pb | 44 | 0.72 | -0.70% | 2.84% | 29.5% | 0.85 | 1.25%/3.91% | [-3.75%, 2.83%] |
| chronological_check | primary_rr2 | 5 pb | 44 | 0.72 | -0.66% | 2.76% | 29.5% | 0.86 | 1.21%/3.90% | [-3.66%, 3.03%] |
| chronological_check | sensitivity_rr1 | 2 pb | 53 | 0.87 | 0.81% | 3.79% | 45.3% | 1.08 | 2.65%/7.75% | [-5.69%, 7.19%] |
| chronological_check | sensitivity_rr1 | 5 pb | 54 | 0.89 | -1.61% | 4.88% | 38.9% | 0.86 | 2.67%/7.87% | [-7.28%, 4.59%] |
| chronological_check | sensitivity_rr5 | 2 pb | 33 | 0.54 | -0.26% | 1.22% | 27.3% | 0.83 | 0.43%/1.30% | [-1.56%, 1.30%] |
| chronological_check | sensitivity_rr5 | 5 pb | 32 | 0.52 | -0.16% | 1.11% | 31.2% | 0.89 | 0.43%/1.29% | [-1.39%, 1.41%] |

El caso principal fija riesgo 0,25 % (R/B 1:2); las sensibilidades usan 0,5 % (1:1) y 0,1 % (1:5). Ninguna usa un presupuesto de pérdida del 2 %. Los porcentajes de retorno son del periodo completo. Las pérdidas reales pueden superar un stop presupuestado.

## Criterios registrados antes de ejecutar

Para continuar como candidata, la principal debe tener al menos 50 operaciones, retorno positivo, PF ≥1,1, DD horario ≤10 % y extremo inferior bootstrap >0 en cada periodo y coste. Este filtro permite seguir validando; nunca autoriza operar. Los criterios concretos son decisiones de investigación, no umbrales universales de rentabilidad.

Caso principal supera todos los filtros: **False**.

- development / base_2bps_each_fill: fallos = positive_net_return, profit_factor, positive_bootstrap_lower_bound.
- development / stress_5bps_each_fill: fallos = positive_net_return, profit_factor, positive_bootstrap_lower_bound.
- chronological_check / base_2bps_each_fill: fallos = enough_trades, positive_net_return, profit_factor, positive_bootstrap_lower_bound.
- chronological_check / stress_5bps_each_fill: fallos = enough_trades, positive_net_return, profit_factor, positive_bootstrap_lower_bound.

## Alcance de la evidencia

Junio–julio es nuevo para H3, pero ya se observaron esos meses al analizar H1/H2. No es una reserva completamente intacta del proyecto. Agosto–septiembre no se ejecutó. Los intervalos son percentiles de remuestreo circular en bloques de siete días (2.000 muestras), con los días sin operaciones incluidos. Son condicionales a la regla y datos elegidos, no pronósticos ni correcciones de la selección previa de H3. La dependencia y el régimen de mercado pueden durar más de siete días.

Se conservan fills OHLC horarios, funding intrahorario acotado y costes hipotéticos. No se supone ejecución maker ni se valida una frecuencia de 50 operaciones/día. Los límites de margen se comprueban al entrar; la ratio puede subir si cae la equity mientras sigue abierta la posición.

arithmetic.csv compara nominal, margen, coste y presupuesto restante para stop en los casos 10x y 25x. No permite convertir el 40 % de margen en una pérdida máxima de cuenta.

El cálculo tuvo cero llamadas a modelos, cero tokens, cero peticiones de red y cero órdenes. La captura pública del catálogo se realizó antes y su manifiesto se conserva por separado.
