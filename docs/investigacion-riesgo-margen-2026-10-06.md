# Investigación de riesgo, margen parcial y apalancamiento

Fecha: 6 de octubre de 2026, Europe/Madrid. Capital de cada simulación: 50 USD. Investigación local, sin estrategia aprobada para operar.

## Corrección de la interpretación y reglas utilizadas

La aclaración del usuario distingue utilizar 25x respecto al margen y comprometer una parte limitada de la cuenta. La anotación anterior de «25x de exposición efectiva sobre la cuenta» interpretaba mal ese planteamiento y se ha corregido.

- Multiplicador sobre margen = nominal / margen asignado.
- Exposición efectiva sobre cuenta = nominal / patrimonio de la cuenta.
- Porcentaje usado como margen = margen asignado / patrimonio de la cuenta.
- Por tanto: exposición efectiva = multiplicador sobre margen × fracción de cuenta asignada.

Ejemplo hipotético: 50 USD en cuenta, 10 USD de margen (20 %) y multiplicador 25x implican 250 USD de nominal y exposición efectiva 5x. El máximo indicado por el usuario de 40 % de margen a 25x implica 500 USD de nominal, es decir 10x de cuenta, antes de considerar comisiones, límites del contrato y el presupuesto de pérdida.

Aplicamos el 40 % como techo de margen para todos los casos nuevos. Se exige además que, tras asignar margen y pagar la comisión de entrada, quede al menos 60 % libre. Son condiciones al admitir una posición: las proporciones pueden cambiar con el precio. En cruzado, el saldo libre continúa como garantía compartida. [Gestión de cartera de Kraken EEE](https://support.kraken.com/ca/articles/portfolio-management-eea).

## Lo confirmado sobre Kraken

El cuadro específico de márgenes EEE establece IM 10 % y MM 5 % en su primer nivel, equivalente a 10x nominal/margen. La página general de cartera contiene una frase inconsistente que relaciona 2 % con 10x; no utilizamos ese 2 % para dimensionar. [Tabla específica de márgenes EEE](https://support.kraken.com/articles/derivatives-margin-schedule-and-maximum-leverage-eea).

La consulta pública a `/derivatives/api/v3/instruments` del 6 de octubre a las 01:51:56 UTC confirma para `PF_XBTUSD` y `PF_ETHUSD`, en `marginSchedules.europa.retail`, IM 0,10 y MM 0,05. Respuesta original y SHA-256: `data/market_data/instruments/20261006T015156Z/`. Es información de producto; no verifica la clasificación o permisos privados de la cuenta.

Las simulaciones aplican ese requisito observado del 10 %. El 25x se conserva como escenario aritmético hipotético autorizado para investigar. No se sustituyó el margen real por 4 % para obtener resultados artificiales. Con IM 10 % y techo de margen 40 %, el nominal máximo teórico es 4 veces el saldo; la condición de saldo libre tras comisiones lo reduce ligeramente.

## Cómo se relacionan objetivo y riesgo

Fijamos antes de ejecutar tres variantes de la misma ruptura horaria H3, todas con beneficio objetivo **neto del 0,5 % de cuenta**:

| Caso | Riesgo presupuestado de cuenta | USD sobre 50 | Beneficio objetivo / riesgo presupuestado |
|---|---:|---:|---:|
| Principal | 0,25 % | 0,125 USD | 2:1 |
| Sensibilidad | 0,5 % | 0,25 USD | 1:1 |
| Sensibilidad | 0,1 % | 0,05 USD | 5:1 |

La relación es entre beneficio neto solicitado y pérdida presupuestada, no entre distancias brutas de precio. El presupuesto incluye pérdida al stop, comisiones, ejecución adversa modelada y reserva para funding. El 10 % de cada presupuesto se reserva para funding. No se utilizó el anterior riesgo fijo del 2 %.

El stop inicial continúa en 2 ATR de la señal horaria para aislar el efecto de cambiar riesgo y objetivo; no se ajustó después de observar resultados. Reducir la pérdida de cuenta se consigue reduciendo cantidad. Esto también puede hacer que el beneficio exigido necesite un recorrido mayor o que el lote mínimo impida la entrada.

El nuevo dimensionador toma la cantidad mínima permitida por el presupuesto de stop, el techo de exposición, el máximo de margen y el saldo libre después de la comisión. Redondea hacia abajo al lote. El margen asignado por unidad es el mayor entre el exigido por el contrato y el que exige el límite de multiplicador del usuario. Rechaza los objetivos que necesitarían un precio de salida cero o negativo sin ingresos futuros de funding.

Estos cambios están en `src/trading_lab/sizing.py` e integrados en el simulador. Corrigen el caso histórico del corto de 4,093 USD que pretendía ganar 5 USD. Los informes antiguos conservan sus resultados y hashes; el código corregido puede cambiar una repetición de casos afectados por aquel fallo.

## Diseño de la comparación

Protocolo previo: `config/risk_margin_research.json`. Misma señal H3: ruptura al cierre de los extremos de las 20 velas horarias anteriores, ATR 14, stop 2 ATR y permanencia máxima 48 horas. Una posición total, BTC antes de ETH. Se evalúan tres riesgos, dos costes y dos periodos: **12 evaluaciones y dos controles históricos adicionales**.

Desarrollo: 14 de febrero–31 de mayo, 107 días. Comprobación cronológica: 1 de junio–31 de julio, 61 días. Junio–julio es nuevo para H3, pero ya se observó con H1/H2, por lo que no es una reserva completamente intacta del estudio. Agosto–septiembre continúa reservado y no se ejecutó.

Comisión taker: 0,05 % por lado, sobre el nominal ejecutado. Se añade fricción hipotética de 0,02 % por ejecución en base y 0,05 % en estrés, además de redondeo a tick y funding histórico. No se presupone ejecución maker. [Tarifas EEE de Kraken](https://support.kraken.com/au/articles/fees-for-derivatives-trading-eea).

## Resultados completos por riesgo

Los retornos son de cada periodo completo e incluyen costes de trading modelados; no son retornos diarios ni por operación. Cada ventana empieza con 50 USD y sus porcentajes no se suman como si fueran una cuenta continua.

| Riesgo por operación | Febrero–mayo base | Febrero–mayo estrés | Junio–julio base | Junio–julio estrés | Operaciones base: desarrollo / comprobación |
|---|---:|---:|---:|---:|---:|
| 0,25 %: caso principal | −0,43 % | −1,63 % | −0,70 % | −0,66 % | 73 / 44 |
| 0,5 % | +3,79 % | +2,99 % | +0,81 % | −1,61 % | 89 / 53 |
| 0,1 % | −0,16 % | −0,20 % | −0,26 % | −0,16 % | 48 / 33 |

La variante principal no muestra beneficio neto. En desarrollo ganó el 35,6 % de sus operaciones: la ganancia media ganadora fue 0,1570 USD y la pérdida media perdedora 0,09146 USD. Con esas medias observadas habría necesitado 36,8 % para empatar. No todas las ganadoras alcanzan el TP: algunas salen por tiempo, por lo que una relación objetivo 2:1 no garantiza una relación media realizada 2:1. En junio–julio acertó 29,5 %, frente a un equilibrio de 32,9 % calculado con sus medias observadas.

La sensibilidad de riesgo 0,5 % sigue positiva con costes base, pero su rentabilidad no resiste el escenario de mayor fricción en junio–julio. El beneficio base de ese tramo son **0,407 USD**, solo 0,00769 USD netos por operación en promedio. Esa holgura no justifica aumentar exposición.

El cambio de coste puede modificar lotes, momentos de salida y entradas siguientes; por eso alguna variante de estrés pierde menos. No es una demostración de que ejecutar peor sea favorable.

## Cuánto margen utilizaron realmente

| Riesgo | Margen medio de cuenta, desarrollo / comprobación | Máximo de margen, ambos periodos base | Límite que determinó todas las cantidades ejecutadas |
|---|---:|---:|---|
| 0,25 % | 1,41 % / 1,25 % | 4,02 % | Pérdida presupuestada al stop |
| 0,5 % | 2,89 % / 2,65 % | 7,75 % | Pérdida presupuestada al stop |
| 0,1 % | 0,52 % / 0,43 % | 1,33 % | Pérdida presupuestada al stop |

En el peor escenario de fricción, el máximo observado entre todas las variantes fue 7,87 %, también inferior al techo 40 %. No hay obligación de llenar ese techo. Los dos controles H3 reproducen exactamente el número de operaciones y retorno de la simulación anterior; ampliar el margen disponible no modifica cantidades que ya están limitadas por el presupuesto de stop.

Con multiplicador hipotético 25x, mantener el mismo nominal de estas operaciones requeriría menos margen asignado que con 10x. Su P&L y comisión por ese mismo nominal serían iguales. No se ha afirmado elegibilidad privada para 25x.

## Aritmética específica del caso 25x

Sobre 50 USD, con costes aproximados de ida/vuelta del 0,14 % del nominal: 0,10 % de comisiones taker y 0,04 % de fricción hipotética. Sin variación de nominal entre los dos fills, sin ticks/lotes y antes de funding efectivo:

| Margen de cuenta a 25x | Margen USD | Nominal USD | Comisión ida/vuelta USD | Comisión + fricción USD | ¿Cabe dentro de riesgo 0,25 % = 0,125 USD, dejando 0,0125 USD para funding? |
|---|---:|---:|---:|---:|---|
| 2 % | 1,00 | 25 | 0,025 | 0,035 | Sí; quedan 0,0775 USD para movimiento adverso |
| 5 % | 2,50 | 62,50 | 0,0625 | 0,0875 | Sí; quedan 0,025 USD para movimiento adverso |
| 10 % | 5,00 | 125 | 0,125 | 0,175 | No |
| 20 % | 10,00 | 250 | 0,250 | 0,350 | No |
| 40 % | 20,00 | 500 | 0,500 | 0,700 | No |

El 40 % es un límite de margen; la combinación de riesgo pequeño y costes puede exigir un porcentaje mucho menor. En el ejemplo del 2 %, un nominal de 25 USD permite aproximadamente 0,31 % de movimiento adverso y exige 1,14 % de movimiento favorable para obtener 0,25 USD netos, antes de funding y redondeo. Es una condición aritmética, no una estrategia ni una probabilidad de alcanzarlo. Con margen 5 %, el stop disponible cae a aproximadamente 0,04 % de precio, que exigiría datos y modelado de ejecución mucho más precisos.

Con riesgo 0,25 %, el límite aritmético de nominal antes de que los costes agoten todo el presupuesto disponible para stop es aproximadamente 80,36 USD: margen 3,21 USD (6,43 % de cuenta) a 25x. En ese extremo ya no quedaría recorrido adverso permitido, así que un stop positivo requiere menor nominal. Esto explica por qué usar todo el margen permitido no es el objetivo del dimensionador.

El archivo `arithmetic.csv` incluye 36 escenarios, con márgenes 1/2/5/10/20/40 %, multiplicadores 10/25 y los tres riesgos. Cincuenta operaciones completas de nominal constante 500 USD costarían aproximadamente 25 USD en comisiones y 35 USD con la fricción base, antes de funding; con nominal 25 USD serían 1,25 USD y 1,75 USD, respectivamente. Son escenarios de costes con nominal fijo, no previsiones de actividad o beneficios.

## Incertidumbre, controles y decisión

Antes de ejecutar se fijó como filtro de investigación: al menos 50 operaciones por periodo y coste, retorno positivo, factor de beneficio al menos 1,1, caída máxima horaria no superior al 10 % y extremo inferior del intervalo bootstrap positivo. La variante principal debía cumplir todos los criterios; las sensibilidades no pueden reemplazarla por selección posterior sobre junio–julio.

Se realizó un remuestreo circular de retornos diarios marcados, incluidos días sin operaciones, en bloques de siete días y 2.000 muestras, con semillas guardadas. Para el caso principal base, el intervalo percentil 95 % del retorno de un periodo de igual longitud fue **[−5,11 %, +4,36 %]** en desarrollo y **[−3,75 %, +2,83 %]** en junio–julio. La sensibilidad 0,5 % tampoco excluye pérdidas: **[−5,69 %, +7,19 %]** en la segunda ventana base. Son intervalos condicionales al modelo y a la muestra, no pronósticos ni una corrección del sesgo por haber elegido H3 después de observar desarrollo.

**Ningún caso ofrece evidencia suficiente para operar.** El principal pierde en ambas ventanas; el 0,5 % es sensible a costes y el 0,1 % tiene muchas exclusiones por lote y pocos objetivos alcanzados. Una relación riesgo/beneficio mejor definida evita decisiones incoherentes, pero no crea una ventaja de mercado por sí misma.

Se ejecutaron cinco pruebas de límites: coste y reserva dentro del riesgo; asignación parcial con techo 25x; prioridad del margen real del contrato; rechazo de TP imposible en un corto; y rechazo del lote que excede presupuesto. Pasaron. Cada replay comprueba además margen máximo y riesgo planificado en sus operaciones, y la conciliación contable. No se observaron pérdidas ejecutadas por encima del presupuesto. Hubo un doble toque de stop y objetivo dentro de una misma vela en el conjunto de variantes; se resolvió con stop primero según la regla conservadora del motor. Estos resultados no garantizan límites de pérdida en vivo ni resuelven la secuencia intrahoraria real.

La frecuencia observada permanece por debajo de una operación diaria de media; máximo dos entradas por día UTC en base. La duración media de la principal ronda 22,5 horas. Esta señal horaria no constituye un diseño de 50 operaciones diarias. Para estudiar oportunidades frecuentes con stops menores, la siguiente investigación necesita datos de 1–5 minutos, costes de ejecución medidos y una señal definida previamente en ese horizonte, por ejemplo una ruptura que exija confirmación o una reversión explícita; ninguna de esas alternativas queda validada aquí.

Se conserva el protocolo y no se reajusta sobre las pérdidas recién observadas. La reserva agosto–septiembre sigue intacta. Los fills horarios, funding intrahorario y costes hipotéticos continúan siendo límites materiales. El cálculo local registró **0 llamadas a modelos, 0 tokens, 0 solicitudes de red y 0 órdenes**. Fuera del replay hubo una solicitud al catálogo público y consultas a la documentación oficial. Infraestructura y coste de la conversación no están incluidos en el P&L.

Resultados completos: `data/research_runs/20261006_risk_margin_v1/results.json`, `informe.md`, libros por operación, curvas horarias, `arithmetic.csv` y manifiesto SHA-256. Para repetir: `python scripts/research_risk_margin.py --output data/research_runs/<directorio-nuevo>`.
