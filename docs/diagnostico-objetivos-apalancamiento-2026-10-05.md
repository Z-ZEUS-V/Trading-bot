# Objetivos flexibles, diagnóstico y tamaño por operación

Diagnóstico iniciado el 5 de octubre y consolidado el 6 de octubre de 2026 (Europe/Madrid). Investigación local con capital simulado de 50 USD. **No hay estrategia aprobada para operar.**

**Actualización de criterio del 6 de octubre:** el usuario permite considerar hasta 25x nominal/margen en cruzado, con máximo 40 % de cuenta como margen, y pide relacionar el riesgo con cualquier objetivo pequeño. El stop presupuestado del 2 % de cuenta no se utilizará como parámetro fijo al estudiar un objetivo de +0,5 %. La decisión vigente está en `docs/criterios-operativos-vigentes-2026-10-06.md`; la investigación posterior ya se ejecutó y está en `docs/investigacion-riesgo-margen-2026-10-06.md`. El 2x de este informe sigue siendo el parámetro histórico de las pruebas ya ejecutadas.

## Decisión actual del usuario

El beneficio del 5–10 % de la cuenta por operación ganadora deja de ser un requisito fijo. Se pueden estudiar beneficios menores y otra frecuencia. El ejemplo de 0,5 % y 50 operaciones diarias expresa flexibilidad; no constituye una cuota de operaciones ni un rendimiento demostrado. Se mantiene la preferencia por margen cruzado y stop loss.

Evaluaremos rentabilidad neta, pérdidas acumuladas, estabilidad entre periodos y viabilidad de ejecución. No aumentamos riesgo ni apalancamiento para compensar una señal que pierde dinero. El riesgo también puede ser inferior al 2 % inicialmente estudiado.

## Qué se hizo

Se creó `config/target_frequency_diagnosis.json` antes de ejecutar las comparaciones nuevas: dos controles, cuatro cambios de objetivo, dos variantes de riesgo reducido y una hipótesis de ruptura horaria. Cada caso se calculó con dos escenarios de fricción: **18 evaluaciones en desarrollo, del 14 de febrero al 31 de mayo de 2026, 107 días**. Los datos de desarrollo ya se habían observado; fijar estas variantes antes de ejecutarlas no convierte sus resultados en una validación independiente.

El programa `scripts/diagnose_strategy_targets.py` conserva configuración, contabilidad por operación, curvas horarias, recorridos anteriores, métricas y hashes en `data/research_runs/20261005_target_frequency_diagnosis_v2/`. La primera ejecución `v1` se conserva; `v2` añade al diagnóstico la detección de objetivos sin precio positivo, sin cambiar el motor, las operaciones ni los resultados. Son 18 combinaciones únicas, no 36 hipótesis distintas. Las cuatro ejecuciones de control reproducen exactamente los retornos y números de operaciones anteriores; el programa comprueba que el saldo concuerda con la suma del P&L.

El cálculo se ejecuta íntegramente con Python local: **0 llamadas a modelos, 0 tokens de API, 0 peticiones de red y 0 órdenes**. Consultar documentación en esta conversación es una actividad distinta del replay. No se atribuye coste cero a electricidad, equipo o suscripción de esta conversación.

## Por qué falló la ruptura de cuatro horas

Con objetivo neto del 5 % y presupuesto de riesgo del 2 %, H1 perdió 7,5914 USD en desarrollo. Sobre las mismas operaciones y cantidades, el movimiento entre precios de referencia produjo −6,8210 USD; la fricción restó 0,2488 USD y las comisiones 0,5874 USD; el funding aportó 0,0657 USD. Por tanto, **las pérdidas de precio ya dominaban antes de costes**. Esta es una descomposición contable, no un nuevo backtest sin costes.

De 25 operaciones, 19 salieron por stop y solo dos alcanzaron el objetivo. Catorce llegaron a mostrar al menos +0,5 % neto en algún cierre horario completo anterior a la salida. Cinco volvieron al rango anterior en el primer cierre de cuatro horas tras entrar. Este último diagnóstico puede observar un cierre posterior a una salida temprana: describe el recorrido del precio, no demuestra que esa vuelta ocurriera con la posición abierta ni valida un filtro.

Estos datos muestran recorridos favorables insuficientes para el objetivo y muchas pérdidas posteriores. No permiten atribuir todas las pérdidas a falsas rupturas inmediatas, a una causa de microestructura concreta o a un régimen identificado. La regla no mostró una ventaja neta suficiente en este tramo.

La comparación directa resuelve una hipótesis: **bajar únicamente el objetivo no arregla H1**. Con objetivo 0,5 % y riesgo 2 %, aumentó de 25 a 61 operaciones, pero el retorno empeoró de −15,18 % a −21,49 %. Cambiar una salida modifica las entradas futuras, el saldo y los tamaños; no basta con recortar retrospectivamente las operaciones ganadoras.

## Por qué costaba alcanzar los objetivos

El techo de exposición era 2x, pero el tamaño se calculaba desde el stop y se redondeaba al lote permitido. En desarrollo:

| Regla anterior | Exposición media respecto a la cuenta | Stop medio: movimiento del precio | Movimiento favorable medio del precio de ejecución necesario para +5 % neto de cuenta | Para +10 % |
|---|---:|---:|---:|---:|
| Ruptura de 4 h | 0,53x | 3,10 % | 10,39 % | 20,69 % |
| Momentum diario | 0,16x | 9,41 % | 35,43 % | 70,77 % |

Los movimientos requeridos se calculan por operación incluyendo comisiones, desde el precio de entrada ejecutado hasta el precio de salida ejecutado. Excluyen funding futuro y no equivalen a una predicción del mercado. Las columnas de objetivo 5/10 % corresponden a sus respectivas carteras.

**Incompatibilidad adicional detectada:** en la primera operación H2 con objetivo 10 %, un corto de ETH del 14 de febrero tenía solo 4,093 USD de nominal frente a 5 USD de beneficio exigido. Incluso una caída a cero daría menos de 5 USD antes de costes; el objetivo algebraico exigía un precio negativo si no se contaba con ingresos futuros de funding. El motor anterior admitía esa combinación y cerró por tiempo. La media de distancias de la tabla incluye ese valor algebraico; no todas esas distancias eran físicamente alcanzables. El diagnóstico ahora lo marca expresamente. El diseño siguiente deberá rechazar objetivos incompatibles con precios positivos, sin depender de funding futuro para hacerlos viables.

Los stops amplios obligaban a posiciones pequeñas para respetar el riesgo. Especialmente en la regla diaria, se pedía un recorrido muy grande antes de su salida temporal máxima de 20 días. Subir el techo 2x no aumentaría por sí solo cantidades que ya están limitadas por el riesgo. Forzar posiciones mayores con el mismo stop aumentaría la pérdida planificada.

## Resultado de las comparaciones nuevas

Escenario base: comisión taker 0,05 % por lado, fricción hipotética adicional 0,02 % por ejecución, redondeo a tick y funding histórico. Todos los porcentajes de retorno corresponden a **107 días completos**. Los gastos de infraestructura se presupuestan aparte.

| Regla | TP neto de cuenta | Riesgo presupuestado | Operaciones | Retorno del periodo | Caída máxima de equity horario |
|---|---:|---:|---:|---:|---:|
| Ruptura 4 h, control | 5 % | 2 % | 25 | −15,18 % | 19,00 % |
| Ruptura 4 h | 0,5 % | 2 % | 61 | −21,49 % | 22,23 % |
| Ruptura 4 h | 1 % | 2 % | 50 | −16,54 % | 20,07 % |
| Momentum diario, control | 5 % | 2 % | 7 | +0,01 % | 4,54 % |
| Momentum diario | 0,5 % | 2 % | 20 | −2,12 % | 5,27 % |
| Momentum diario | 1 % | 2 % | 13 | −3,91 % | 5,04 % |
| Ruptura 4 h | 0,5 % | 0,5 % | 27 | −1,49 % | 2,66 % |
| Momentum diario | 0,5 % | 0,5 % | 7 | −0,10 % | 1,67 % |
| Ruptura 1 h, H3 | 0,5 % | 0,5 % | 89 | +3,79 % | 3,44 % |

Los 18 resultados completos, incluidos escenarios desfavorables, están en el `informe.md` de la ejecución. Al cambiar la fricción pueden cambiar la cantidad redondeada, los activos elegibles y los momentos de salida; algún resultado de estrés puede mejorar por ese cambio de trayectoria. Eso no convierte una fricción mayor en una ventaja.

H3 usa cierres horarios que rompen el máximo/mínimo de las 20 velas anteriores, ATR de 14 velas, stop inicial de 2 ATR y permanencia máxima de 48 horas. Mantiene una sola posición total y prioridad BTC antes de ETH. Cambia simultáneamente el horizonte de la señal y el de permanencia: no aísla cuál de ellos explica su resultado.

H3 terminó con **51,90 USD**, frente a 50 iniciales; con fricción de 0,05 % por ejecución terminó con **51,49 USD** (+2,99 %). En el escenario base hubo 39 objetivos alcanzados, 43 stops y siete salidas temporales. El 49,4 % de operaciones ganó dinero; la ganancia media ganadora fue 0,2386 USD y la pérdida media perdedora 0,1912 USD. El promedio neto de todas las operaciones fue **0,0213 USD**, no 0,25 USD.

Su beneficio tiene poca holgura: las comisiones sumaron 1,3338 USD y la fricción 0,5614 USD. Por meses, el P&L marcado fue febrero +0,4826 USD, marzo +2,1973, abril +0,0838 y mayo −0,8670. Marzo explica más que todo el beneficio final. La caída máxima se mide en cierres horarios y puede subestimar una caída intrahoraria.

La frecuencia observada fue **0,83 operaciones/día calendario**, con un máximo de dos entradas por día UTC y unas 16 horas de permanencia media como cota superior. El resultado justifica examinar esta hipótesis con más precisión y periodos independientes; **no demuestra todavía rentabilidad robusta ni ejecución de alta frecuencia**.

## Cómo utilizaremos el apalancamiento y la cuenta

Hay tres cantidades diferentes:

1. **Exposición o nominal:** valor de la posición. Dividirlo por el patrimonio de la cuenta da el apalancamiento efectivo. Con 50 USD, una posición de 100 USD representa 2x.
2. **Margen inicial:** garantía requerida por el contrato. Para los tramos iniciales BTC/ETH del supuesto EEE minorista utilizado, se aplica 10 % del nominal. Una exposición 2x consume aproximadamente el 20 % de la cuenta como margen inicial, antes de costes. La especificación y elegibilidad de la cuenta deberán confirmarse al conectar. [Tabla de márgenes EEE de Kraken](https://support.kraken.com/articles/derivatives-margin-schedule-and-maximum-leverage-eea).
3. **Pérdida presupuestada:** movimiento hasta el stop más comisiones, ejecución adversa y reserva de funding. Es lo que determina la cantidad; no es un máximo de pérdida garantizado.

Para las pruebas documentadas aquí se propuso riesgo del **0,5 % por operación** (0,25 USD sobre 50), una sola posición total y techo de exposición 2x. Un 0,25 % de riesgo podría estudiarse después si el lote mínimo lo permite; esta ronda solo probó 0,5 % y 2 %. La actualización vigente del 6 de octubre permite considerar un techo mayor y deja la elección concreta de riesgo y apalancamiento para la siguiente investigación. No se ha cambiado ninguna configuración de una cuenta real.

Procedimiento: primero determinar el stop por la señal/volatilidad; luego calcular el nominal que cabe en el presupuesto; redondear hacia abajo al lote y comprobar margen. Si el mínimo excede el presupuesto, no operar. No estrechar artificialmente el stop para conseguir más apalancamiento.

Ejemplos aproximados con 50 USD, presupuesto de pérdida 0,25 USD, reserva de funding 0,025 USD y coste de ida/vuelta 0,14 % del nominal:

`nominal = mínimo(100 USD, (0,25 − 0,025) / (distancia_stop + 0,0014))`

| Distancia del stop en precio | Nominal antes de redondear | Exposición / cuenta | Margen inicial, al 10 % | Margen / cuenta |
|---|---:|---:|---:|---:|
| 0,5 % | 35,16 USD | 0,70x | 3,52 USD | 7,03 % |
| 1 % | 19,74 USD | 0,39x | 1,97 USD | 3,95 % |
| 2 % | 10,51 USD | 0,21x | 1,05 USD | 2,10 % |

Es una aproximación; el motor usa cantidades y precios de entrada/salida distintos, ticks y lotes. En H3, el margen inicial medio real simulado fue **2,89 % de la cuenta**, exposición media 0,289x y riesgo presupuestado medio incluido funding 0,420 %. El redondeo a lotes y la reserva hacen que no se agote siempre el 0,5 % permitido.

**En cruzado, el resto del saldo también respalda la posición.** No podemos afirmar que usar 3,52 USD de margen limite a esa cifra la pérdida. Un salto de precio, retraso o fallo de ejecución puede superar la pérdida planificada por el stop. [Funcionamiento de la cartera y garantía cruzada en Kraken EEE](https://support.kraken.com/ca/articles/portfolio-management-eea).

## Qué significaría hacer 50 operaciones diarias

Con nominal constante de 100 USD, abrir y cerrar como taker cuesta aproximadamente **0,10 USD** en comisiones: 50 operaciones completas cuestan **5 USD**, un 10 % de una cuenta de 50 USD. La tarifa de referencia es 0,05 % por lado y se cobra sobre el nominal ejecutado. [Comisiones de Derivatives para EEE](https://support.kraken.com/au/articles/fees-for-derivatives-trading-eea).

Añadiendo la fricción base hipotética, el coste sería unos **7 USD diarios antes de funding**. Una ganadora de +0,5 % neto de cuenta necesita 0,25 USD netos y aproximadamente 0,39 USD de P&L bruto en ese ejemplo. Con otros nominales los costes cambian proporcionalmente; no es una estimación de la frecuencia o liquidez alcanzables.

Si +0,5 % es solo la ganancia por acierto y una perdedora pierde −2 %, se necesita un **80 % de aciertos para empatar**, suponiendo resultados binarios ya netos. Con +0,5 %/−0,5 % se necesita 50 %. En la práctica hay otras salidas y pérdidas variables.

Si +0,5 % fuera el promedio neto de TODAS las operaciones, incluyendo las perdedoras, 50 operaciones implicarían 25 % diario sobre capital fijo, antes de reinversión. No tenemos evidencia para proyectar ese rendimiento. Se buscarán oportunidades con expectativa positiva, sin forzar un número diario.

## Próximo paso y límites

El diagnóstico inicial está completado. H3 queda como hipótesis de investigación: comprobar la compatibilidad entre cantidad y objetivo antes de admitir señales, registrar criterios antes de evaluar otros periodos, contrastar fills con datos de menor intervalo y medir incertidumbre y concentración temporal. Para una operativa de pocos minutos harían falta datos y ejecución de esa resolución; los OHLC horarios actuales no la validan. Este diagnóstico no elevó riesgo ni apalancamiento; el criterio posterior permite investigar una exposición mayor con el control de riesgo que se definirá después.

Las variantes nuevas no se ejecutaron en junio–julio y agosto–septiembre sigue reservado. El resumen inicial de junio–julio procede de libros ya guardados. No se añaden filtros basados en esos resultados. Continúan las limitaciones de reglas actuales aplicadas al pasado, funding intrahorario aproximado, ausencia de fills reales y de validación privada de cuenta. Antes de una eventual ejecución harán falta también límites agregados y diarios, reconciliación y paper trading.

Se conserva la separación entre lógica de estrategia y adaptador Kraken. Todas las llamadas a Astra siguen suspendidas por instrucción del usuario.
