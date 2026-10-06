# Diagnóstico de objetivos, frecuencia, margen y apalancamiento

Solo investigación local. Todas las comparaciones nuevas utilizan desarrollo: 14 febrero–31 mayo de 2026. Sin Astra ni órdenes reales.

Los objetivos 5–10 % dejan de ser un requisito fijo. Se evalúa también 0,5 % neto por operación ganadora, sin suponer una cuota de operaciones ni una rentabilidad diaria.

## Qué utilizaban realmente las operaciones anteriores

| Ventana / regla / objetivo | Exposición media / equity | Margen inicial medio / equity | Stop medio del precio | Horas medias de posición (cota superior) | Movimiento medio del fill para TP, sin funding futuro |
|---|---:|---:|---:|---:|---:|
| development / H1_breakout_4h / 5% | 0.531x | 5.31% | 3.10% | 74.3 | 10.39% |
| development / H1_breakout_4h / 10% | 0.532x | 5.32% | 3.08% | 79.8 | 20.69% |
| development / H2_momentum_1d / 5% | 0.162x | 1.62% | 9.41% | 351.9 | 35.43% |
| development / H2_momentum_1d / 10% | 0.162x | 1.62% | 9.41% | 351.9 | 70.77% |
| chronological_validation / H1_breakout_4h / 5% | 0.686x | 6.86% | 2.68% | 72.0 | 8.63% |
| chronological_validation / H1_breakout_4h / 10% | 0.701x | 7.01% | 2.61% | 85.2 | 16.14% |
| chronological_validation / H2_momentum_1d / 5% | 0.179x | 1.79% | 7.14% | 278.6 | 32.82% |
| chronological_validation / H2_momentum_1d / 10% | 0.261x | 2.61% | 6.37% | 472.0 | 38.61% |

El 2x era un techo de exposición. El tamaño se redujo por la distancia del stop y los lotes: no se utilizó 2x automáticamente. El porcentaje de margen de la tabla no limita la pérdida de una cartera en cruzado.

## De dónde salieron las pérdidas o ganancias

Descomposición sobre las MISMAS operaciones y cantidades. Quitar los costes no vuelve a simular la trayectoria ni la reinversión; es una atribución contable.

| Ventana / regla / objetivo | P&L a precios de referencia USD | Fricción fills USD | Comisiones USD | Funding USD | Neto USD |
|---|---:|---:|---:|---:|---:|
| development / H1_breakout_4h / 5% | -6.8210 | 0.2488 | 0.5874 | 0.0657 | -7.5914 |
| development / H1_breakout_4h / 10% | -6.6619 | 0.2398 | 0.5665 | 0.0742 | -7.3940 |
| development / H2_momentum_1d / 5% | 0.0649 | 0.0233 | 0.0557 | 0.0178 | 0.0037 |
| development / H2_momentum_1d / 10% | 0.0649 | 0.0233 | 0.0557 | 0.0178 | 0.0037 |
| chronological_validation / H1_breakout_4h / 5% | 1.4959 | 0.1990 | 0.4747 | -0.0677 | 0.7545 |
| chronological_validation / H1_breakout_4h / 10% | 2.4282 | 0.1918 | 0.4552 | -0.0691 | 1.7121 |
| chronological_validation / H2_momentum_1d / 5% | 2.0092 | 0.0186 | 0.0450 | 0.0138 | 1.9593 |
| chronological_validation / H2_momentum_1d / 10% | 1.9448 | 0.0160 | 0.0391 | 0.0598 | 1.9494 |

## Diagnóstico de recorridos anteriores

| Ventana / regla / objetivo | Operaciones | Salidas por stop | Alcanzaron +0,5 % neto en algún cierre horario completo anterior a la salida | Volvieron al rango en el primer cierre de barra tras entrar |
|---|---:|---:|---:|---:|
| development / H1_breakout_4h / 5% | 25 | 19 | 14 | 5/25 |
| development / H1_breakout_4h / 10% | 24 | 18 | 13 | 5/24 |
| development / H2_momentum_1d / 5% | 7 | 2 | 4 | No aplica |
| development / H2_momentum_1d / 10% | 7 | 2 | 4 | No aplica |
| chronological_validation / H1_breakout_4h / 5% | 13 | 9 | 7 | 0/13 |
| chronological_validation / H1_breakout_4h / 10% | 12 | 8 | 7 | 1/12 |
| chronological_validation / H2_momentum_1d / 5% | 5 | 1 | 2 | No aplica |
| chronological_validation / H2_momentum_1d / 10% | 3 | 0 | 3 | No aplica |

Se excluye de los recorridos la hora de salida cuando se desconoce el instante de ejecución. Alcanzar un valor en un cierre anterior no prueba que una cartera con otro TP obtuviera ese resultado: sus futuras entradas y tamaños cambiarían. Volver al rango es una observación retrospectiva de precio, no una causa demostrada ni un filtro validado.

## Comparaciones nuevas predefinidas

Se mantienen el techo 2x, ATR, lote, reglas de funding y prioridades del motor original. Dos controles, cuatro cambios de objetivo, dos escenarios de riesgo reducido y una hipótesis horaria. Cada caso se ejecuta con fricción de 2 y 5 puntos básicos por fill. No se han reajustado tras ver resultados.

| Caso | Fricción/fill | Riesgo | TP neto | Ops | Ops/día calendario | Retorno periodo | DD horario | Acierto | Rechazos por lote | Exposición media |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| control_H1_target5_risk2 | 2 pb | 2.0% | 5.0% | 25 | 0.234 | -15.18% | 19.00% | 24.0% | 0 | 0.531x |
| control_H1_target5_risk2 | 5 pb | 2.0% | 5.0% | 25 | 0.234 | -15.41% | 19.19% | 24.0% | 0 | 0.529x |
| control_H2_target5_risk2 | 2 pb | 2.0% | 5.0% | 7 | 0.065 | 0.01% | 4.54% | 57.1% | 1 | 0.162x |
| control_H2_target5_risk2 | 5 pb | 2.0% | 5.0% | 7 | 0.065 | -0.05% | 4.56% | 57.1% | 1 | 0.162x |
| H1_target05_risk2 | 2 pb | 2.0% | 0.5% | 61 | 0.570 | -21.49% | 22.23% | 57.4% | 0 | 0.573x |
| H1_target05_risk2 | 5 pb | 2.0% | 0.5% | 61 | 0.570 | -21.85% | 22.57% | 57.4% | 0 | 0.571x |
| H1_target1_risk2 | 2 pb | 2.0% | 1.0% | 50 | 0.467 | -16.54% | 20.07% | 48.0% | 0 | 0.571x |
| H1_target1_risk2 | 5 pb | 2.0% | 1.0% | 47 | 0.439 | -12.08% | 15.81% | 51.1% | 0 | 0.570x |
| H2_target05_risk2 | 2 pb | 2.0% | 0.5% | 20 | 0.187 | -2.12% | 5.27% | 65.0% | 1 | 0.185x |
| H2_target05_risk2 | 5 pb | 2.0% | 0.5% | 19 | 0.178 | -0.40% | 5.28% | 68.4% | 1 | 0.170x |
| H2_target1_risk2 | 2 pb | 2.0% | 1.0% | 13 | 0.121 | -3.91% | 5.04% | 38.5% | 1 | 0.154x |
| H2_target1_risk2 | 5 pb | 2.0% | 1.0% | 13 | 0.121 | -3.96% | 5.07% | 38.5% | 1 | 0.154x |
| H1_target05_risk05 | 2 pb | 0.5% | 0.5% | 27 | 0.252 | -1.49% | 2.66% | 37.0% | 14 | 0.122x |
| H1_target05_risk05 | 5 pb | 0.5% | 0.5% | 27 | 0.252 | -1.54% | 2.41% | 37.0% | 13 | 0.122x |
| H2_target05_risk05 | 2 pb | 0.5% | 0.5% | 7 | 0.065 | -0.10% | 1.67% | 57.1% | 63 | 0.043x |
| H2_target05_risk05 | 5 pb | 0.5% | 0.5% | 7 | 0.065 | -0.11% | 1.67% | 57.1% | 63 | 0.043x |
| H3_1h_target05_risk05 | 2 pb | 0.5% | 0.5% | 89 | 0.832 | 3.79% | 3.44% | 49.4% | 0 | 0.289x |
| H3_1h_target05_risk05 | 5 pb | 0.5% | 0.5% | 88 | 0.822 | 2.99% | 3.43% | 48.9% | 0 | 0.282x |

Retornos de todo el periodo, no diarios ni por operación. Se incluye el resultado aunque sea negativo. Un resultado positivo aquí seguiría siendo desarrollo observado, sin aprobación de estrategia. Bajar riesgo también puede cambiar el activo elegido o impedir entradas por lote mínimo.

## Frecuencia y costes

La regla de 4 horas puede evaluar seis instantes de entrada al día, y la diaria uno, en una cartera de una posición. Además debe terminar la posición anterior. La variante horaria tampoco puede demostrar 50 operaciones diarias; los datos OHLC de una hora no resuelven una operativa de pocos minutos.
Cincuenta operaciones con ganancia media neta del 0,5 % sobre una base fija de 50 USD serían 12,50 USD diarios (25 %). Esa ganancia media tendría que incluir perdedoras y costes. Si 0,5 % es solo el TP ganador, falta conocer aciertos y pérdidas. No es una proyección de rendimiento.
Con nominal fijo 100 USD (2x sobre 50), las comisiones taker de ida/vuelta serían aproximadamente 0,10 USD por operación y 5 USD por 50 operaciones. Sumando la fricción hipotética base, serían aproximadamente 7 USD, antes de funding. Ganar 0,5 % neto de la cuenta exige aproximadamente 0,39 USD de P&L bruto por operación ganadora en ese ejemplo.
Con ganancias netas +0,5 % y pérdidas netas -2 %, el acierto binario de equilibrio es 80 %. Con +0,5 %/-0,5 % es 50 %. Las distribuciones reales incluyen salidas temporales y gaps.

## Cómo dimensionar

Exposición = nominal/equity. Margen inicial = nominal × requisito del contrato. Riesgo planificado = pérdida hasta el stop más costes y reserva de funding. En cruzado, el saldo de la cartera sirve como garantía compartida.
Se propone mantener 2x como techo inicial de simulación, elegir el stop por mercado y calcular cantidad desde el riesgo. Para una futura hipótesis de mayor frecuencia, estudiar 0,25–0,5 % de riesgo por operación, sujeto a lote mínimo y límites diarios/agregados. En esta ronda se calculó 0,5 %, no se configuró una cuenta ni se aprobó operar.
Ejemplo aproximado: 50 USD, riesgo 0,5 % (0,25 USD), reserva funding 0,025 USD, stop del precio 0,5 % y fricción total 0,14 % del nominal ⇒ nominal 35,16 USD antes de redondeo, exposición 0,70x, margen a IM 10 % de unos 3,52 USD (7,03 % de cuenta).
No se impone un porcentaje fijo de saldo por operación. Si el lote mínimo excede riesgo, la salida es no operar. El colchón libre sigue siendo garantía en cruzado y el stop no asegura un máximo absoluto realizado.

## Límites y trazabilidad

Se conserva el motor OHLC y todas sus limitaciones de fills, latencia, mark y funding intrahorario. No se estudió ejecución de 50 operaciones diarias, ni se reabrió agosto–septiembre. Las observaciones de junio–julio de las tablas iniciales proceden exclusivamente de resultados ya guardados; las variantes nuevas no se ejecutaron allí.
diagnostics.json guarda métricas y límites, reference_trade_paths.csv los recorridos, cada variante conserva libro y equity. manifest.json guarda hashes del código, configuración y entradas. El cálculo es local y no tiene llamadas a agentes.

Fuentes consultadas: [márgenes EEE](https://support.kraken.com/articles/derivatives-margin-schedule-and-maximum-leverage-eea), [comisiones EEE](https://support.kraken.com/au/articles/fees-for-derivatives-trading-eea) y [garantía cruzada](https://support.kraken.com/ca/articles/portfolio-management-eea).
