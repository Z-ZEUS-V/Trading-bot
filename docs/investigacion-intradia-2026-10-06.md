# Investigación intradía: oportunidades frecuentes con una cuenta de 50 USD

Fecha: 6 de octubre de 2026. Investigación local terminada; sin llamadas a Astra, sin claves privadas y sin órdenes. Este informe continúa la investigación horaria de riesgo/margen, cuya duración media principal rondaba 22,5 horas. No se trasladó esa señal a minutos por simple cambio de etiqueta: se definieron nuevas reglas para ese horizonte.

**Resultado: las cuatro variantes de uno y cinco minutos pierden después de costes en ambos periodos y ambos escenarios de ejecución. La ruptura de un minuto alcanza una frecuencia cercana a 50 operaciones diarias, pero destruye capital en esta simulación. La reversión de cinco minutos pierde mucho menos porque opera muy poco; no demuestra rentabilidad.**

## 1. Qué se ha investigado

Protocolo fijado antes del primer resultado de estas señales: `config/intraday_research.json`. Caso principal: ruptura confirmada de cinco minutos. Comparaciones: la misma lógica a un minuto y reversión explícita a uno/cinco minutos. Cuatro reglas × dos periodos × dos costes = **16 evaluaciones**. No se ajustaron sus parámetros después de ver las pérdidas.

Cada evaluación empieza con 50 USD de garantía en USD, margen cruzado, una única posición para toda la cuenta y prioridad BTC sobre ETH cuando coinciden señales. Abril–mayo son desarrollo; junio–julio, comprobación cronológica. Cada tramo contiene 61 días. Los saldos se reinician entre tramos: sus retornos no se deben sumar como si fueran una única cuenta. Estos meses ya se observaron con estrategias horarias; no constituyen una muestra intacta para el conjunto del proyecto. Agosto–septiembre sigue reservado.

El objetivo de cada operación es **+0,5 % neto de la cuenta al entrar**, con pérdida presupuestada de **0,25 %**, incluidos costes y reserva de funding. Sobre los primeros 50 USD son 0,25 USD frente a 0,125 USD. El 10 % del presupuesto de pérdida se reserva para funding; el tamaño se redondea hacia abajo al lote permitido. Esta relación 2:1 es de objetivos, no la relación entre ganancias y pérdidas finalmente obtenidas: también hay salidas por tiempo y saltos de precio.

## 2. Datos y comprobaciones

- BTC `PF_XBTUSD` y ETH `PF_ETHUSD`, del 31 de marzo al 31 de julio de 2026. El primer día se usa para calentamiento.
- **708.480 velas reales de un minuto**: 177.120 por activo y tipo de precio, trade/mark. Cero huecos y cero OHLC inválidos. Hay minutos sin volumen; no se eliminan de la cronología. Las señales requieren volumen positivo en sus dos últimas barras.
- **70.848 observaciones históricas bid/ask de cinco minutos**: 35.424 por activo, sin huecos ni cotizaciones inválidas en la captura.
- 542 respuestas públicas de historia conservadas comprimidas, junto con CSV normalizados y SHA-256.
- Al agregar las nuevas velas a una hora, los cuatro precios OHLC coinciden exactamente con las capturas horarias previas en **2.952 horas por cada una de las cuatro series**: 11.808 comparaciones sin diferencias.
- 60 capturas públicas del libro actual, 30 por activo durante aproximadamente un minuto, para estimar el precio medio de cruzar nominales de 25/50/100/200/500 USD.

Archivos: `data/market_data/intraday/20261006_v1/` y `data/market_data/execution_books/20261006_v1/`. La auditoría independiente verificó 120 hashes de entradas/código/salidas y las 542 respuestas históricas; también concilió cada operación desde sus precios de referencia. Evidencia: `data/research_runs/20261006_intraday_audit_v1/audit.json`.

Kraken describe analytics como datos agrupados por intervalo, y el libro REST como una captura de órdenes disponibles. Esta distinción condiciona el modelo: [Market Analytics](https://docs.kraken.com/api/docs/futures-api/charts/market-analytics) y [Get orderbook](https://docs.kraken.com/api-reference/market-data/get-orderbook).

## 3. Señales definidas antes de medir su P&L

**Ruptura confirmada:** se calcula el máximo/mínimo de 20 barras anteriores a la ruptura. Una barra debe cerrar fuera del rango; la siguiente debe seguir fuera y cerrar al menos tan lejos en la dirección de la ruptura. Stop a 1,5 ATR de 14 barras desde el cierre de confirmación. Máximo 12 barras en posición: 12 minutos en la variante 1m, 60 minutos en 5m.

**Reversión tras extensión:** media y desviación típica poblacional de 20 cierres previos a la extensión. Una barra cierra fuera de dos desviaciones; la siguiente vuelve dentro de esa banda fija, sin cruzar aún la media. Se entra hacia la media, con stop a 1 ATR y el mismo máximo de 12 barras. Solo se admite si el beneficio estimado al llegar a esa media cubre el objetivo neto, las comisiones, la fricción y la reserva de funding. La media es un filtro de viabilidad; el objetivo ejecutado sigue siendo el +0,5 % de cuenta.

Ambas esperan **un minuto completo adicional** desde que el cierre confirma la señal. Es una demora supuesta, no una latencia medida del bot. No se entra retrospectivamente en el cierre que produjo la señal. Si la entrada ya queda al otro lado del stop, se rechaza. No se fuerza una cuota de operaciones.

## 4. Costes: qué se observó y qué sigue siendo una hipótesis

La tarifa inicial EEE empleada es **0,05 % taker por lado**, sobre el nominal ejecutado: aproximadamente 0,10 % por ida/vuelta. La cuenta real y su nivel de tarifas no se verificaron. Se presupone garantía USD; otras garantías pueden añadir conversiones o intereses que este replay no representa. [Tarifas oficiales EEE](https://support.kraken.com/au/articles/fees-for-derivatives-trading-eea).

| Medición | BTC | ETH |
|---|---:|---:|
| Spread histórico completo, mediana | 0,1523 pb | 0,5732 pb |
| Spread histórico completo, percentil 95 | 0,4795 pb | 1,6374 pb |
| Spread histórico completo, máximo | 9,3998 pb | 17,7109 pb |
| Spread completo del libro actual, mediana | 0,1170 pb | 0,3700 pb |
| Barrido adicional al mejor precio, p95 para 200 USD | 0,0000 pb | 0,4501 pb |

Un punto básico (pb) equivale al 0,01 %. El cero de barrido BTC es el percentil de esta muestra pequeña; su máximo fue 0,0220 pb. No significa coste de ejecución cero.

Cada fill simulado suma medio spread histórico del último intervalo **ya cerrado**, el barrido p95 medido para 200 USD y una reserva adicional adversa. El escenario base añade 1 pb por fill; el de estrés, 5 pb. Comisiones, redondeo adverso a tick y funding se contabilizan aparte. La mayor posición admitida fue 93,306 USD, por debajo del nominal de 200 USD utilizado para esa medición.

**Lo medido son cotizaciones y profundidad, no ejecuciones propias.** Analytics puede repetir precios y no reconstruye la cola de órdenes; usar profundidad actual para operaciones pasadas es una hipótesis de viabilidad actual. El tiempo HTTP mediano fue unos 85–87 ms, pero no mide latencia de órdenes. Faltan observaciones prolongadas, fills parciales y deslizamiento efectivo. Tampoco se atribuyen fills maker ni su menor comisión sin un modelo de cola.

Se rechazan cotizaciones ausentes o demasiado antiguas; no se rellenan con cero. El funding horario conciliado se prorratea por minuto. Cuando el instante de salida intraminuto es desconocido, se imputa el débito del minuto completo o cero crédito, y se registra la incertidumbre. Si stop y TP se tocan en la misma vela, se toma el stop primero. Hubo un caso así en ruptura 1m base de desarrollo.

## 5. Resultados completos por periodo

Retornos de cada tramo de 61 días, netos de los costes de trading modelados. Las columnas de frecuencia y duración corresponden al escenario base. La duración usa el extremo superior del intervalo de salida, con precisión de un minuto.

| Regla | Periodo | Operaciones base | Media/día | Duración media | Retorno base | Retorno estrés |
|---|---|---:|---:|---:|---:|---:|
| Ruptura 5m, principal | Abril–mayo | 575 | 9,43 | 36,9 min | −34,14 % | −41,15 % |
| Ruptura 5m, principal | Junio–julio | 609 | 9,98 | 35,8 min | −32,83 % | −39,79 % |
| Ruptura 1m | Abril–mayo | 2.723 | 44,64 | 6,4 min | −97,05 % | −96,19 % |
| Ruptura 1m | Junio–julio | 2.946 | 48,30 | 6,5 min | −96,55 % | −96,48 % |
| Reversión 5m | Abril–mayo | 13 | 0,21 | 22,5 min | −1,75 % | −0,63 % |
| Reversión 5m | Junio–julio | 13 | 0,21 | 17,5 min | −0,14 % | −0,20 % |
| Reversión 1m | Abril–mayo | 15 | 0,25 | 4,1 min | −0,98 % | −0,34 % |
| Reversión 1m | Junio–julio | 57 | 0,93 | 2,9 min | −9,76 % | −2,94 % |

Un resultado menos negativo con mayor fricción no es una mejora: el dimensionador reduce nominal, rechaza más entradas y el lote mínimo acaba impidiendo operaciones. Son trayectorias distintas, no una comparación de las mismas cantidades/fills con una factura añadida.

La ruptura 1m base alcanza un máximo de **62 y 63 entradas en un día**, y al menos 50 entradas en **27 y 33 días**, respectivamente. Por tanto, sí se observó frecuencia suficiente algunos días. El objetivo neto solo se alcanzó en 35/2.723 y 68/2.946 operaciones: aproximadamente 1,29 % y 2,31 % de ellas.

En ruptura 5m base el máximo fue 16/15 entradas diarias. Solo 36/575 y 50/609 operaciones alcanzaron el objetivo. En junio–julio hubo 348 stops, 210 salidas por tiempo, 50 objetivos y una salida al terminar la ventana. El acierto neto fue 27,4 % y el profit factor 0,51: por cada dólar perdido se recuperaron aproximadamente 0,51 USD en operaciones ganadoras.

Los replays continuaron hasta el final para diagnosticar las reglas: **no incluyen un interruptor operativo que detenga la cuenta por drawdown**. El umbral del 10 % fue un filtro de descarte. La ruptura 1m base ya lo atravesó el 2 de abril a las 14:26 UTC y el 2 de junio a las 07:08 UTC. Sus pérdidas cercanas al 97 % son resultados de investigación; no representan una política aceptable para desplegar el bot.

## 6. Qué explica las pérdidas

Descomposición de junio–julio base sobre las operaciones y tamaños realmente elegidos por el simulador:

| Concepto, USD | Ruptura 5m | Ruptura 1m |
|---|---:|---:|
| P&L a precios de referencia, antes de fricción/comisiones/funding | +3,3840 | +0,8728 |
| Fricción de fills, incluido tick | −4,4414 | −11,6513 |
| Comisiones | −15,3500 | −37,4963 |
| Funding neto | −0,0077 | +0,0001 |
| P&L neto | **−16,4151** | **−48,2746** |

El P&L de referencia es una atribución contable de esas mismas operaciones; **no es un backtest separado sin costes**, porque las decisiones y los tamaños ya dependieron de ellos. Incluso antes de restar comisiones, la fricción supera la ganancia de referencia de ambas rupturas. En ruptura 1m, la pérdida de desarrollo ya era −0,9911 USD a precios de referencia.

En junio–julio, ruptura 1m paga por operación una media de 0,0882 % de la equity de entrada en comisiones y 0,0295 % en fricción. Es un gasto medio cercano al 0,118 % de cuenta por ida/vuelta frente al presupuesto total de pérdida de 0,25 %. Aumentar la frecuencia multiplica esa factura. Como ejemplo aritmético, 50 vueltas diarias con nominal constante igual a una cuenta de 50 USD cuestan unos 2,50 USD/día solo en comisiones taker, antes de spread y demás componentes.

La reversión 5m base rechazó **1.569/1.515 señales** por recorrido hasta la media insuficiente para cubrir el objetivo neto bajo el presupuesto de riesgo. Solo entró 13 veces por tramo. En 1m rechazó 7.012/7.100 por esa razón. Hay señales visuales de reversión, pero la mayoría no ofrece espacio económico suficiente para esta combinación de objetivo, stop y costes.

## 7. Apalancamiento y porcentaje de cuenta utilizado

Se conserva la autorización de considerar hasta 25x **nominal/margen asignado**, el techo de margen del 40 % y un mínimo del 60 % libre después de la comisión de entrada. Para BTC/ETH se aplicó el requisito público EEE de margen inicial del 10 %, equivalente a 10x nominal/margen; 25x sigue sujeto a comprobar disponibilidad real. [Cuadro específico de márgenes EEE](https://support.kraken.com/articles/derivatives-margin-schedule-and-maximum-leverage-eea).

**Ninguna operación agotó el techo de margen. Todas quedaron limitadas primero por el presupuesto de pérdida del stop y los costes.** El mayor margen usado en las 16 evaluaciones fue 19,38 % de la cuenta; la mayor exposición, 1,938 veces su equity. En junio–julio base:

| Regla | Exposición media nominal/cuenta | Margen medio de cuenta | Margen máximo |
|---|---:|---:|---:|
| Ruptura 5m | 0,610x | 6,10 % | 18,35 % |
| Ruptura 1m | 0,882x | 8,82 % | 19,11 % |
| Reversión 5m | 0,713x | 7,13 % | 13,86 % |
| Reversión 1m | 1,241x | 12,41 % | 18,85 % |

Si el contrato admitiese 25x, esas mismas posiciones necesitarían un 40 % del margen usado con 10x, pero sus ganancias, pérdidas y comisiones serían iguales. Aumentar el nominal para aprovechar margen sobrante aumentaría el riesgo de cuenta; la investigación no encuentra una razón rentable para hacerlo con estas señales.

Ejemplo aproximado independiente de los resultados: cuenta 50 USD, presupuesto de pérdida 0,125 USD, reserva funding 0,0125 USD, stop de precio a 0,20 % y coste de ida/vuelta estimado 0,122 %. El nominal máximo por riesgo sería `(0,125 − 0,0125)/(0,002 + 0,00122) ≈ 34,94 USD`, antes del redondeo a lote/tick. Exigiría unos 3,49 USD de margen a 10x (6,99 % de cuenta), o 1,40 USD a un hipotético 25x (2,80 %). Ganar 0,25 USD netos requeriría un movimiento favorable cercano a 0,84 % del precio antes del funding efectivo. Así se relacionan margen, objetivo y stop sin comprometer toda la cuenta.

El presupuesto no es una garantía de pérdida máxima: hubo 33 excesos sobre 0,25 % al contar todas las simulaciones, que comparten datos y no son operaciones independientes. El peor resultado individual fue aproximadamente −0,2986 % de la equity de entrada. La principal 5m no tuvo excesos. En cruzado, el saldo libre sigue respaldando la posición.

## 8. Criterio de aceptación y aprendizaje para el siguiente diseño

Se exigía a la principal en cada periodo/coste: al menos 100 operaciones, retorno positivo, profit factor ≥1,1, drawdown ≤10 %, extremo inferior del intervalo bootstrap positivo y ninguna posible liquidación. **No pasa. Tampoco pasan las comparaciones.**

Para ruptura 5m base, los intervalos percentiles 2,5–97,5 del retorno remuestreado son aproximadamente [−38,98 %, −28,86 %] en desarrollo y [−38,14 %, −27,17 %] en comprobación. Son 2.000 remuestreos circulares de bloques de siete días, incluidos días sin operaciones. Condicionan sobre este periodo/modelo; no representan probabilidades garantizadas del futuro. La reversión 5m tiene muestras demasiado pequeñas para presentarla como alternativa validada.

Decisión: descartar estas cuatro parametrizaciones para operar. Esto no descarta toda ruptura o reversión posible, ni demuestra que cualquier bot intradía sea inviable. La evidencia sí obliga a que la siguiente señal tenga una ventaja bastante mayor por operación o una ejecución verificablemente más barata.

La siguiente investigación debe registrar primero una nueva hipótesis económica —por ejemplo, continuación tras retroceso que mejore el precio de entrada y el recorrido disponible— y medir excursión favorable/adversa neta de costes antes de recorrer objetivos o apalancamientos. Cualquier filtro nuevo deberá fijarse con desarrollo y necesitará periodos adicionales; junio–julio ya no puede reutilizarse como validación intacta. Mantener agosto–septiembre reservado para una candidata que sobreviva a ese proceso. Si se estudia ejecución maker, modelar probabilidad de fill, cola, selección adversa y salidas taker; tocar un precio límite no equivale a ejecutar.

Para la futura operativa hacen falta, además, límites agregados por día y por drawdown y medidas de ejecución continuas. Esta investigación no los ha optimizado ni configura una cuenta real. El cálculo local reduce el coste de inteligencia artificial, pero no elimina comisiones, infraestructura, electricidad o conexión.

## 9. Reproducción y archivos

Ejecutar desde la raíz del proyecto, usando un directorio de salida nuevo:

```powershell
& 'C:\Python312\python.exe' scripts/research_intraday.py --data data/market_data/intraday/20261006_v1 --books data/market_data/execution_books/20261006_v1 --output data/research_runs/<directorio-nuevo>
& 'C:\Python312\python.exe' scripts/audit_intraday_run.py --run data/research_runs/<directorio-nuevo> --data data/market_data/intraday/20261006_v1 --output data/research_runs/<auditoria-nueva>
```

Resultados originales: `data/research_runs/20261006_intraday_v1/`. Incluyen protocolo, configuración efectiva, resumen, operaciones, equity a minuto, eventos y manifiesto. Motor: `src/trading_lab/intraday.py`, `simulator.py` y `sizing.py`. Captura pública reproducible: `scripts/capture_intraday_data.py`.

Las 12 pruebas locales existentes de causalidad, funding a minuto, doble toque, reversión y dimensionamiento pasaron. El control horario anterior reprodujo exactamente retorno y número de operaciones. Son comprobaciones del cálculo, no validación de rentabilidad real. **Replay: cero llamadas a modelos, cero tokens API, cero red y cero órdenes.** Las descargas públicas previas y la muestra de libros están registradas por separado; no se ha medido un coste monetario de electricidad/conexión ni se atribuye un coste de API a esta conversación de Codex.
