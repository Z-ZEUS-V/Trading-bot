# Estudio aplicado de trading algorítmico: cuenta de 50 USD

**Nota posterior del 6 de octubre de 2026:** las preferencias de objetivo, stop y apalancamiento registradas en este estudio fueron revisadas. Los criterios vigentes están en `docs/criterios-operativos-vigentes-2026-10-06.md`; los cálculos y propuestas siguientes se conservan como investigación histórica.

Fecha: 5 de octubre de 2026. Primera revisión documental y ejercicios aplicados. Ninguna estrategia del proyecto tiene todavía rentabilidad verificada.

**Continuación posterior a este estudio:** el siguiente paso solicitado ya produjo conciliación de funding y un primer replay H1/H2. Resultados, límites y tareas pendientes en [primera simulación local](simulacion-local-estrategias-2026-10-05.md). Las secciones siguientes conservan el protocolo y estado de la revisión previa. Astra queda sin llamadas hasta nueva indicación del usuario.

## 1. Requisitos y conclusión inicial

El usuario pide futuros cripto en Kraken, **margen cruzado con stop loss**, objetivos de beneficio de **5–10 % de la cuenta por operación ganadora** y pérdidas planificadas de **2–4 %, hasta 5 %**. El capital inicial es **50 USD**, con gastos operativos presupuestados aparte. Puede aumentar según resultados; no se presupone ese aumento en las pruebas. Estas preferencias guían el diseño; no se ha cambiado la configuración de una cuenta ni autorizado órdenes reales.

Para hacer medible el objetivo, este estudio interpreta «cuenta» como equity de futuros inmediatamente antes de la entrada, en USD: capital más P&L y costes ya contabilizados. Con una sola posición se evitan ambigüedades por ganancias flotantes de otras operaciones. El objetivo se mide después de comisiones de trading, spread/deslizamiento y funding; los gastos de infraestructura y análisis se contabilizan además en la rentabilidad económica total. No confundir este porcentaje con ROE sobre el margen depositado.

Con 50 USD: beneficio objetivo 2,50–5 USD; pérdida planificada 1–2,50 USD. Son barreras para investigar. No cabe exigir que cada operación gane, ni suponer un porcentaje de acierto por elegir esas barreras. Una salida temporal, parcial o de emergencia puede acabar entre ellas; un salto de precio puede exceder el stop.

**Propuesta de investigación:** empezar con riesgo base del 2 %, una posición total y señal de tendencia/ruptura, comparada con una regla de momentum sencilla. Evaluar 4–5 % como escenarios separados. Es una prioridad por simplicidad, datos y posibilidad de refutarla, no un ranking de rentabilidad. El carry queda como línea independiente; la formación no debe obligarnos a defender la selección anterior.

## 2. Qué se ha estudiado realmente

Se revisaron materiales universitarios, investigaciones de sus autores y documentación oficial del mercado. Leer un temario no equivale a completar un curso. La tabla distingue lectura efectuada, aplicación al proyecto y trabajo todavía pendiente.

| Bloque | Material consultado y alcance | Aplicación concreta | Estado |
|---|---|---|---|
| Finanzas cuantitativas | Temario MIT 15.450 y secciones de las clases 8, 9 y 10: errores estándar, inferencia en muestras pequeñas, bootstrap y volatilidad | Distinguir estimación de retorno, incertidumbre y pronóstico de volatilidad | Revisión documental; ejercicios estadísticos con resultados del bot pendientes |
| Construcción algorítmica | Descripción oficial Georgia Tech CS7646: datos, inversión computacional y aprendizaje automático | Organizar el trabajo desde datos y contabilidad hacia modelos | Mapa curricular; no se completó el curso |
| Sobreajuste | Introducción, metodología y limitaciones de Probability of Backtest Overfitting; secciones metodológicas de Deflated Sharpe Ratio | Registrar variantes, fallos y decisiones antes de escoger ganadores | Protocolo incorporado; indicadores no calculados todavía |
| Evidencia de señales | Resumen de los autores de Time Series Momentum; resúmenes NBER de momentum y factores cripto | Separar evidencia histórica de hipótesis nuevas en Kraken | Revisión con límites de transferencia explícitos |
| Carry cripto | Resumen, introducción y secciones de fricciones/margen de Crypto Carry del BIS | Separar señal de funding de cobertura spot-perpetuo | Segunda línea de investigación |
| Microestructura | Secciones de modelo y supuestos de Avellaneda–Stoikov; órdenes y márgenes de Kraken | Identificar inventario, selección adversa, fills y fallos de protección | Requisitos documentados; modelo de fills pendiente |
| Datos | Series locales y endpoint público de funding histórico | Detectar cobertura nueva y ocho horas ausentes por activo | Captura y auditoría estructural terminadas; significado económico pendiente |
| Riesgo y objetivos | Derivación del P&L de un contrato lineal y escenarios sobre equity | 120 combinaciones largo/corto, exposición, costes y objetivos | Ejercicio numérico ejecutado; no es un backtest |

Fuentes curriculares: [MIT, temario y notas](https://ocw.mit.edu/courses/15-450-analytics-of-finance-fall-2010/pages/lecture-notes/) y [Georgia Tech, CS7646](https://www.omscs.gatech.edu/cs-7646-machine-learning-trading). Esta revisión amplía la base documental; no supone reentrenamiento permanente del modelo ni acredita todavía una estrategia rentable.

### Estadística que cambia nuestras decisiones

La incertidumbre no se resuelve acumulando velas si las observaciones están relacionadas. Hay que examinar autocorrelación, heterocedasticidad y dependencia entre operaciones. La inferencia con errores robustos y la revisión de muestras pequeñas son relevantes antes de interpretar una media positiva. [MIT, clase 8](https://ocw.mit.edu/courses/15-450-analytics-of-finance-fall-2010/b79caa581c25f2c6df2a3c7af099150e_MIT15_450F10_lec08.pdf), [clase 9](https://ocw.mit.edu/courses/15-450-analytics-of-finance-fall-2010/3894e9e72ac0f3d1c98d43323a104fec_MIT15_450F10_lec09.pdf).

En el proyecto estimaremos intervalos de incertidumbre con métodos que conserven dependencia temporal, por ejemplo remuestreo por bloques con sensibilidad a su longitud. Un bootstrap de operaciones barajadas independientemente podría borrar rachas y agrupaciones por régimen. Ningún intervalo resolverá por sí solo el sesgo de haber elegido la mejor estrategia entre muchas.

Predecir volatilidad tampoco demuestra capacidad para predecir dirección. Un estimador de volatilidad puede servir para dimensionar exposición aunque no tenga señal de compra o venta. Empezaremos con medidas simples antes de justificar un modelo GARCH. [MIT, clase 10](https://ocw.mit.edu/courses/15-450-analytics-of-finance-fall-2010/dc9b7ce0d6220d59e32ba4f3eaf690aa_MIT15_450F10_lec10.pdf).

Probar muchas señales, stops y horizontes aumenta la posibilidad de seleccionar una coincidencia histórica. PBO propone una evaluación de esa selección; DSR considera efectos de selección y no normalidad al interpretar Sharpe. Ambos necesitan supuestos y datos adecuados, y no certifican beneficios futuros. [Bailey y colaboradores, PBO](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf), [Bailey y López de Prado, DSR](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf). El trabajo de [Harvey, Liu y Zhu](https://www.nber.org/papers/w20592), consultado en su resumen oficial, también motiva el control de pruebas múltiples; no trasladamos sus umbrales a nuestro bot automáticamente.

## 3. Qué implican los porcentajes solicitados

### Beneficio, riesgo y frecuencia de acierto

Si solo hubiera dos resultados posibles, ganancia neta `G` y pérdida neta `R`, la esperanza aritmética sería `p*G - (1-p)*R`. El acierto de equilibrio sería `R/(G+R)`.

| Objetivo neto de cuenta | Pérdida neta de cuenta | Beneficio/riesgo | Acierto para equilibrio aritmético |
|---:|---:|---:|---:|
| 5 % | 2 % | 2,5 | 28,57 % |
| 10 % | 2 % | 5,0 | 16,67 % |
| 5 % | 4 % | 1,25 | 44,44 % |
| 10 % | 4 % | 2,5 | 28,57 % |
| 5 % | 5 % | 1,0 | 50,00 % |
| 10 % | 5 % | 2,0 | 33,33 % |

No son tasas de acierto estimadas. Alejar el objetivo suele cambiar la probabilidad y duración de alcanzarlo; hay que medir ambas. Además, esperanza aritmética cero no implica crecimiento compuesto cero. El informe numérico incluye el umbral logarítmico y calcula la distribución binaria solo como ejercicio.

Diez pérdidas seguidas, arriesgando cada vez una fracción del saldo restante, dejarían:

| Riesgo por operación | Saldo desde 50 USD | Caída acumulada |
|---:|---:|---:|
| 2 % | 40,85 USD | 18,29 % |
| 4 % | 33,24 USD | 33,52 % |
| 5 % | 29,94 USD | 40,13 % |

No estimamos aquí la probabilidad de esa racha. Estos números explican por qué propongo el 2 % como punto de partida de simulación y no el 5 % habitual. Siguen pendientes límites de pérdida diaria y de drawdown total; no sustituirlos por el límite de una sola operación.

### El apalancamiento cambia el tamaño, no crea una ventaja

Para un contrato lineal, cantidad constante y precios en USD:

`rendimiento_neto_cuenta = L * [d*(x-1) - f_entrada - f_salida*x - c]`

`L` es nominal inicial/equity, `d` vale +1 para largo y -1 para corto, `x` es precio de salida/entrada, y `c` es un coste adicional sobre nominal inicial. Se cobra la comisión de salida sobre su propio nominal. Funding y costes de garantía se añadirían por separado.

Ejemplo puramente numérico de largos: comisión taker 0,05 % por lado y **0,04 % adicional hipotético por operación completa** para explorar fricción. No es una medición del spread ni del deslizamiento. La tarifa inicial publicada para EEE es 0,02 % maker y 0,05 % taker; no asumimos fills maker. [Comisiones Kraken EEE](https://support.kraken.com/au/articles/fees-for-derivatives-trading-eea).

| Nominal/equity | Nominal con 50 USD | Coste si el precio no cambia | Subida para ganar 5 % cuenta | Subida para ganar 10 % cuenta | Caída para perder 2 % cuenta |
|---:|---:|---:|---:|---:|---:|
| 1x | 50 USD | 0,07 USD | 5,143 % | 10,145 % | 1,861 % |
| 2x | 100 USD | 0,14 USD | 2,641 % | 5,143 % | 0,860 % |
| 5x | 250 USD | 0,35 USD | 1,141 % | 2,141 % | 0,260 % |

En 5x, el coste ilustrativo a precio constante ya consume el 35 % del presupuesto de pérdida de 1 USD. El stop compatible con ese presupuesto sería muy próximo al precio inicial; falta medir si una señal puede tolerarlo. Aumentar exposición para acercar el objetivo también aproxima el stop y amplifica fricciones.

El cálculo completo, incluidos cortos, está en [informe numérico](../data/research_runs/20261005_account_risk/informe.md), [CSV](../data/research_runs/20261005_account_risk/scenarios.csv) y [JSON con supuestos](../data/research_runs/20261005_account_risk/scenarios.json). Se genera con `scripts/analyze_account_risk_targets.py`; no consulta APIs.

Para el sizing real, primero se propone un stop por estructura/volatilidad y después se calcula la cantidad compatible con el presupuesto de riesgo, costes, lote y margen. **No se estrecha artificialmente el stop para justificar una exposición deseada.** Si la cantidad mínima ya excede el presupuesto, se omite la operación. Si se reduce el nominal, se recalcula la distancia necesaria al objetivo y se evalúa si el horizonte permite alcanzarlo.

## 4. Margen cruzado y protección de pérdidas

Kraken describe el margen cruzado como garantía compartida dentro de la cartera de trading. Por ello, varios stops individuales no equivalen a un límite de pérdida del conjunto: posiciones relacionadas pueden deteriorarse simultáneamente. [Gestión de cartera EEE](https://support.kraken.com/ca/articles/portfolio-management-eea).

La tabla EEE consultada especifica, para el nivel I aplicable a determinadas clases/tamaños, IM del 10 %, MM del 5 % y máximo 10x. Esto no verifica el permiso ni las condiciones de esta cuenta. Con 50 USD y nominal 500 USD, un IM del 10 % consumiría los 50 USD antes de comisiones; ese escenario del calculador no es una propuesta de operación. [Márgenes EEE](https://support.kraken.com/articles/derivatives-margin-schedule-and-maximum-leverage-eea).

Diseño propuesto:

1. Una posición total en el primer experimento. Más adelante, presupuesto de riesgo agregado y exposición por factor; BTC y ETH no cuentan como riesgos independientes.
2. Stop alojado en el exchange y salida que reduzca la posición. La API documenta `reduceOnly` con valor predeterminado falso: hay que enviarlo explícitamente cuando corresponda. [Send order](https://docs.kraken.com/api-reference/order-management/send-order).
3. Diferenciar precio que dispara el stop, precio de ejecución y mark usado para margen. No asumir que coinciden.
4. Contemplar fills parciales, gap, rechazo, retraso de confirmación y posición abierta mientras se instala protección. Un stop-market no garantiza precio; un stop-limit puede quedar sin ejecutar. Las protecciones de precio del mercado pueden limitar la ejecución. [Tipos de órdenes Derivatives](https://support.kraken.com/es/articles/360031471211-derivatives-order-types).
5. Reservar colchón sobre el margen y controlar el saldo tras comisiones/funding. Comparar la trayectoria intrabar con margen de mantenimiento; no calcular liquidación con una regla universal `1/apalancamiento`.
6. Diseñar la desconexión con cuidado: el dead man's switch documentado cancela órdenes al vencer el temporizador. No cierra posiciones; podría eliminar protección pendiente. No utilizarlo como sustituto de un cierre o sin comprobar su interacción con los stops. [Dead man's switch](https://docs.kraken.com/api-reference/order-management/dead-mans-switch).

Por tanto, el 5 % puede ser un **máximo de pérdida planificada**; no podemos garantizarlo como máximo realizado usando únicamente stop loss y margen cruzado.

## 5. Qué familias merece la pena investigar

El catálogo contiene diez familias. Se conserva su historia; los números de puntuación antiguos no pasan a considerarse evidencia empírica. La prioridad siguiente es una decisión de ingeniería de investigación.

| Familia | Mecanismo que habría que demostrar | Encaje y decisión actual |
|---|---|---|
| Momentum temporal/tendencia | Persistencia direccional suficiente para superar entradas falsas y costes | Primera línea; probar regla sencilla y ruptura, sin prometer que objetivos amplios mejoren la expectativa |
| Momentum transversal | Rendimiento relativo entre activos | Posterior: exige universo histórico con altas/bajas; el catálogo actual induce supervivencia |
| Reversión a la media | Desviaciones transitorias que realmente revierten antes del stop | Segunda ronda; investigar por régimen, sin promediar pérdidas ilimitadamente |
| Pares/arbitraje estadístico | Relación estable y convergencia después de costes de ambas patas | Posponer primera implementación: dos órdenes, financiación y ruptura de relación |
| Carry general | Prima por mantener exposición/financiar otra | Mercados tradicionales fuera del alcance; no trasladar evidencia sin adaptación |
| Funding/basis cripto | Información direccional o ingresos de una cobertura, según variante | Línea separada; funding alto no basta para abrir un corto ni prueba rentabilidad de carry |
| Market making | Spread capturado superior a inventario, selección adversa y ejecución | Depriorizar con datos horarios y esta infraestructura; exigir libro/cola y simulación de fills |
| Prima de volatilidad/opciones | Remuneración por riesgo de volatilidad y colas | Fuera de la primera implementación en perpetuos lineales |
| ML/ensemble | Mejora incremental de predicción/decisión respecto a reglas simples | Evaluar después de disponer de base neta y validación; no usar complejidad como evidencia |
| VWAP/TWAP/POV | Reducción de coste de ejecutar una señal ya existente | Capa de ejecución, sin asumir que genere rentabilidad direccional por sí sola |

La evidencia de **Time Series Momentum** consultada corresponde a una investigación de futuros diversificados y horizontes mucho mayores que una ruptura de 4 horas. La propuesta local es nueva y requiere su propia prueba. [Resumen de los autores, AQR](https://www.aqr.com/Insights/Research/Journal-Article/Time-Series-Momentum). Los resúmenes de [Liu y Tsyvinski](https://www.nber.org/papers/w24877) y [Liu, Tsyvinski y Wu](https://www.nber.org/papers/w25882) ofrecen motivación histórica para estudiar momentum/factores en cripto; no validan nuestras reglas, tarifas o instrumentos. No se revisaron íntegramente esos dos trabajos NBER en esta sesión.

**Crypto Carry** estudia primas y fricciones de financiación y arbitraje; una cobertura puede afrontar restricciones de margen antes de converger. Un rendimiento de carry anualizado tampoco equivale a ganar 5 % por operación. [BIS, documento revisado](https://www.bis.org/publications/working-paper-1087-crypto-carry.pdf).

El modelo de **Avellaneda–Stoikov** permite entender la interacción entre cotizaciones, inventario y llegadas de órdenes bajo supuestos concretos. Sus simulaciones no sustituyen un modelo de cola y ejecución de Kraken. [Artículo de los autores, NYU](https://math.nyu.edu/~avellane/HighFrequencyTrading.pdf).

También se consideraron enfoques no separados en el catálogo: pullbacks son una variante de tendencia; filtros de régimen son hipótesis adicionales; grid y martingala no crean ventaja por repartir órdenes y no encajan si requieren aumentar sin límite el riesgo tras pérdidas. No se descarta toda estrategia que use rejillas, pero cualquier versión necesitaría exposición acotada y evidencia neta propia. No hay justificación para pasar directamente a refuerzo, redes complejas o señales de noticias sin datos adecuados.

## 6. Hallazgo nuevo de datos y corrección del diagnóstico anterior

La cobertura anterior de funding procedía de la API de **analytics**. No probaba que Kraken careciese de toda historia previa a febrero de 2026.

Se consultó el endpoint público [historical funding rates](https://docs.kraken.com/api-reference/historical-funding-rates/historical-funding-rates), mediante `GET /derivatives/api/v3/historical-funding-rates?symbol=...`, para PF_XBTUSD y PF_ETHUSD. La captura sin credenciales está en `data/market_data/funding_rates/20261005T204909Z/`, con respuestas gzip, URLs, fecha, hashes y auditoría.

| Resultado por cada activo | Observado |
|---|---|
| Registros | 8.861 |
| Primera marca | 2025-10-01 08:00 UTC |
| Última marca | 2026-10-05 20:00 UTC |
| Duplicados / tasas no finitas | 0 / 0 |
| Orden de timestamps | Ascendente |
| Intervalos con huecos | 7 |
| Horas ausentes en esos intervalos | 8 |

Los huecos son compartidos por ambas series: 1 y 2 de noviembre, 19 de noviembre y 4 de diciembre de 2025; 4 y 13 de febrero y 9 de mayo de 2026. El archivo `quality.json` identifica las horas exactas. Son ausencias de la respuesta observada; aún no sabemos si corresponden a incidentes, publicación o recopilación.

Pendiente antes del backtest: resolver unidades y signo de `fundingRate` y `relativeFundingRate`, momento de devengo/publicación, y conciliación con analytics y el contrato lineal. No equiparar automáticamente un indicador de funding con el flujo pagado. No rellenar huecos con cero, ni unir series con distinta semántica porque sus timestamps coincidan.

Las velas locales llegan hasta el 2 de octubre. El final común para una primera integración será el menor de las coberturas verificadas. Esta captura amplía datos disponibles; no entrega automáticamente cuatro años completos de P&L después de funding. Preservamos los conjuntos anteriores como evidencia inmutable de sus propias consultas.

## 7. Primeros experimentos propuestos, antes de ver resultados

Los siguientes parámetros son decisiones iniciales de diseño, **no parámetros optimizados ni una estrategia aprobada**. Quedan registrados para evitar cambiarlos silenciosamente después de observar rendimiento. Cualquier cambio crea otra variante en el registro.

### H1: ruptura con tamaño por volatilidad

- Hipótesis: una ruptura de rango puede producir movimientos persistentes que compensen los intentos fallidos, después de costes.
- Datos iniciales: PF_XBTUSD y PF_ETHUSD; barras UTC de 4 horas construidas desde horas completas. Este par es un universo técnico limitado, no una diversificación demostrada.
- Señal: al cierre, largo si cierra por encima del máximo de las **20 barras anteriores**, corto si cierra por debajo del mínimo de esas barras. Excluir la barra de señal del rango.
- Entrada simulada: primera oportunidad posterior al cierre; no ejecutar retrospectivamente al precio que generó la señal.
- Volatilidad: ATR como media simple de 14 true ranges cerrados; `TR=max(high-low, abs(high-close_previo), abs(low-close_previo))`. Esta definición evita ambigüedad con suavizados diferentes.
- Stop inicial: distancia de dos ATR desde el fill de entrada. No alejarlo si la operación pierde. Tamaño redondeado hacia abajo para arriesgar como máximo el 2 % incluyendo costes presupuestados.
- Cap de exposición inicial propuesto: nominal total/equity de 2x. El cap puede reducir el riesgo efectivo por debajo del 2 %. No aumentarlo para forzar una operación.
- Beneficio: variante primaria a +5 % de equity neto; variante secundaria a +10 %. Funding y costes efectivos pueden desplazar el precio necesario. Una incertidumbre excesiva en esos costes invalida la estimación.
- Tiempo máximo: 48 barras de 4 horas desde entrada; salida en la primera oportunidad posterior si no ha ocurrido otra salida. No tiene que ganar 5 % por cumplirse el tiempo.
- Una posición total; si ambos activos señalan simultáneamente, prioridad fija a BTC para esta primera prueba. Sin aumentar posiciones ni invertirlas en la misma oportunidad. Esperar una barra cerrada nueva antes de otra entrada.
- Descartar entrada si faltan datos, la cantidad mínima supera el riesgo, no hay margen/colchón, o no se puede modelar protección.

### H2: momentum diario como comparación

Mismo presupuesto de capital, cartera, costes y reglas de elegibilidad. Usar el signo del retorno de los últimos 20 días cerrados; señal cero implica abstención. ATR simple de 14 días, stop a dos ATR y salida máxima tras 20 días, además del stop/objetivo. Entrar después de la señal y aplicar la misma pausa de una barra tras salir. Comparar por separado objetivos netos del 5 % y 10 %. El horizonte de 20 días es una hipótesis local, no una réplica del artículo de momentum.

Primero se evaluarán cuatro variantes primarias: H1/H2 por objetivo 5/10, con riesgo 2 %. Las comparaciones de riesgo 4/5 %, exposición y costes también se registrarán si se ejecutan. No seleccionar sobre el mismo tramo el mejor horizonte, stop, objetivo, activo y apalancamiento y después presentar ese tramo como validación.

Una prueba puede concluir que el objetivo es demasiado distante para ese horizonte, que el stop se activa demasiado a menudo, que las fricciones consumen la ventaja, o que no hay suficientes observaciones. Esas son conclusiones útiles; no requieren forzar otra configuración rentable en la misma muestra.

## 8. Cómo se aceptará o descartará una hipótesis

### Datos y contabilidad primero

Construir un libro de operaciones con señal, datos disponibles en ese instante, cantidad, nominal, margen, fills, comisiones, funding y P&L realizado/no realizado. Calcular por separado retorno de la cuenta y beneficio económico tras infraestructura/IA. Un gasto pagado fuera de los 50 USD sigue siendo un gasto del proyecto.

Con OHLC horario, si una vela toca stop y objetivo, no sabemos el orden. Usar detalle más fino donde exista y marcar toda ambigüedad; el escenario stop primero sirve como cota conservadora, no como reconstrucción exacta. En gaps, un stop no se rellena mágicamente al precio disparador. Tampoco se asume fill de una orden límite porque el máximo/mínimo haya tocado su precio. Evitar contar dos veces el spread si ya está incorporado a los precios de fill.

Los tramos con funding desconocido deben señalarse. Una operación que atraviese un hueco no desaparece silenciosamente del informe: cuantificarla como indeterminada, intentar recuperar datos o aplicar cotas explícitas de coste. Si se bloquean ventanas para un estudio completo, documentar la pérdida de cobertura y el sesgo que puede introducir esa selección.

### Separación temporal y registro

1. Fijar versiones de datos, reglas y costes; guardar hashes, fechas y decisiones.
2. Usar periodos cronológicos de desarrollo, validación y prueba final. No barajar pasado y futuro.
3. Ajustar solo en desarrollo. Walk-forward evalúa cómo se comportaría un proceso que decide con información pasada. La longitud de ventanas dependerá de cobertura y número efectivo de observaciones; no imponer varios años de funding que no tenemos.
4. Si etiquetas u operaciones se solapan entre particiones, impedir que información futura contamine entrenamiento; ajustar separación y purgado a su horizonte real.
5. Registrar todas las variantes, incluidas las fallidas. Un tramo consultado repetidamente deja de ser una prueba final intacta. Reservar además observación futura/paper después de congelar reglas.

### Informe mínimo de resultados

Mostrar resultados agregados y por activo/periodo: operaciones y tiempo expuesto, expectativa neta e incertidumbre, media/mediana de ganancia y pérdida, porcentaje de acierto, profit factor, costes por concepto, máximo drawdown y duración, peores operaciones, colas, rachas y crecimiento compuesto. Incluir restricciones por lote/margen y operaciones descartadas/indeterminadas. Comparar con abstenerse y con exposición simple al mercado ajustada al riesgo y a los costes.

Exigir que la conclusión no dependa de un único episodio, activo, fill favorable o combinación exacta de parámetros. Evaluar costes mayores y retraso de ejecución, sin inventar que un multiplicador de slippage sea una estimación empírica. Publicar la sensibilidad completa.

Para considerar un candidato se necesita evidencia neta fuera de muestra con incertidumbre suficientemente pequeña, estabilidad razonable, riesgo compatible con los límites y ejecución plausible. Si el intervalo de expectativa sigue incluyendo pérdidas relevantes, clasificarlo como inconcluso. No hay un número universal de operaciones ni un Sharpe que por sí solo prueben rentabilidad. La escasez de datos puede dejar el proyecto en investigación.

La aprobación operativa requerirá además paper con comportamiento de órdenes comprobado y límites finales acordados. El soporte de Kraken sigue pendiente; no se han reintentado claves ni enviado órdenes. La exigencia de confirmación antes de llamadas Astra `high` continúa vigente.

## 9. Entregables de esta sesión y continuación

**Realizado:** revisión de fuentes indicada arriba; traducción de objetivos a dinero y exposición; 120 escenarios aritméticos; nueva captura pública de funding con hashes y auditoría de huecos; mapa de las diez familias; reglas iniciales y protocolo de validación; actualización de la memoria del proyecto.

**No realizado todavía:** backtest de H1/H2, conciliación económica del funding, estimación de tasas de acierto, selección de una estrategia rentable, simulación completa de liquidación o paper trading. No se ejecutaron nuevas llamadas a la API de Astra. El coste de esta conversación no se ha medido aquí.

El siguiente trabajo concreto es resolver la semántica/cobertura del funding y construir el motor determinista de contabilidad y fills para esas reglas. Después se ejecutan los experimentos congelados y se informa tanto si fallan como si resultan prometedores. La formación continúa con ejercicios sobre los datos y errores reales que aparezcan, con trazabilidad de lo aprendido.
