# Primera simulación local: resultados y decisiones

Fecha: 5 de octubre de 2026. **Investigación, sin órdenes reales y sin llamadas a Astra.**

**Actualización posterior:** el usuario flexibilizó los objetivos por operación. El diagnóstico y las comparaciones de TP menores/riesgo reducido están en `docs/diagnostico-objetivos-apalancamiento-2026-10-05.md`. Los resultados y parámetros de este documento se conservan como primera investigación, no como requisitos operativos vigentes.

El usuario pide avanzar en la estrategia y mantener abierta una revisión posterior del exchange y los agentes. La monitorización continua deberá ser asequible. Hasta que el usuario indique lo contrario, no ejecutar llamadas a Astra de ningún nivel de razonamiento.

## Resultado principal

Ya existe un primer motor local de señales, contabilidad y simulación de ejecución para contratos lineales en USD. Se ejecutaron las cuatro variantes propuestas, cada una con dos escenarios de fricción y dos ventanas temporales: **16 evaluaciones**. Se conservaron todos los resultados.

La ejecución `20261005_local_strategies_v2` reproduce los mismos resultados de `v1` después de adaptar la redacción del generador a los parámetros del archivo de configuración. No se cambiaron señales, costes ni ventanas. Ambas ejecuciones se conservan; son 16 combinaciones únicas, no 32 hipótesis diferentes.

**Ninguna estrategia queda validada para operar.** La ruptura falla en el primer tramo. La regla diaria tiene demasiadas pocas operaciones para concluir rentabilidad y alcanza pocas veces el beneficio solicitado por operación. No se eligió una ganadora usando solo el tramo favorable.

Los parámetros se fijaron en `config/local_strategy_research.json` antes de la primera ejecución: 50 USD por ventana/variante, una posición total, riesgo planificado 2 %, reserva del 10 % de ese presupuesto para funding, exposición máxima 2x y objetivos netos 5/10 %. Son las hipótesis iniciales de investigación. No se cambió la cuenta del exchange.

### Escenario base: comisión y fricción incluidas

Comisión taker 0,05 % por lado. Fricción adicional hipotética de 0,02 % por fill, incluido spread/deslizamiento; redondeo adverso a tick. Funding observado incluido, con tratamiento conservador de salidas intrahorarias. No incluye infraestructura, fiscalidad ni costes de esta conversación.

| Regla y objetivo de cuenta por operación | Desarrollo: 14 febrero–31 mayo | Operaciones | Validación: junio–julio | Operaciones |
|---|---:|---:|---:|---:|
| Ruptura 4h, objetivo 5 % | −15,18 % | 25 | +1,51 % | 13 |
| Ruptura 4h, objetivo 10 % | −14,79 % | 24 | +3,42 % | 12 |
| Momentum diario, objetivo 5 % | +0,01 % | 7 | +3,92 % | 5 |
| Momentum diario, objetivo 10 % | +0,01 % | 7 | +3,90 % | 3 |

**Los rendimientos de la tabla son del periodo completo, no de cada operación.** Las ventanas empiezan con 50 USD de forma independiente; no sumar sus porcentajes como si fueran una cartera continua.

Con fricción de 0,05 % por fill, la ruptura pierde 15,20–15,41 % en desarrollo y gana 1,27–3,07 % en validación. Momentum diario pasa a aproximadamente −0,05 % en desarrollo y +3,71–3,85 % en validación. No se ha optimizado un modelo de deslizamiento contra esos resultados.

### Encaje real con los objetivos del usuario

En el escenario base, sumando el número de operaciones de las dos ventanas, pero sin combinar sus retornos:

| Variante | Operaciones | Veces que alcanzó el objetivo neto |
|---|---:|---:|
| Ruptura, +5 % cuenta | 38 | 5 |
| Ruptura, +10 % cuenta | 36 | 1 |
| Momentum diario, +5 % cuenta | 12 | 1 |
| Momentum diario, +10 % cuenta | 10 | 0 |

El resto salió por stop, tiempo máximo o fin de ventana; algunas salidas temporales ganaron menos que el objetivo. La variante diaria del 10 % no demostró alcanzar ese objetivo. Aumentar apalancamiento o riesgo después de ver la tabla sería otra hipótesis, que habría que registrar y justificar; no se hizo.

El drawdown horario máximo de ruptura fue aproximadamente 19 % en desarrollo y 12 % en validación. El de momentum estuvo entre 1,9 % y 4,6 % según variante/ventana. El beneficio de momentum en validación provino exclusivamente de BTC; ETH no tuvo operaciones por la prioridad fija y la regla de una sola posición. No constituye evidencia independiente en dos activos.

No aparecieron pérdidas mayores del presupuesto planificado en estos escenarios. Esto **no garantiza** el límite ante saltos, problemas de ejecución o caídas del exchange. El drawdown horario tampoco representa el peor recorrido intrahorario.

## Conciliación de funding completada para el replay

Se contrastaron las capturas originales de `historical-funding-rates` con analytics: **5.555 marcas comunes por activo, cero discrepancias**, tanto en tasa absoluta como relativa. Se recuperaron las horas de 13 de febrero de 2026 a las 18:00 UTC y 9 de mayo a las 06:00 UTC usando valores observados en analytics. No se interpoló.

Quedan seis horas sin datos por activo entre noviembre de 2025 y el 4 de febrero de 2026. Las ventanas elegidas comienzan después y contienen todos los datos requeridos. El motor aborta si falta una hora necesaria, en lugar de sustituir funding por cero o eliminar una operación.

La documentación de Kraken describe el devengo horario y la tasa absoluta para contratos lineales. Se usa `cashflow = -dirección × cantidad_base × tasa_absoluta × horas`. Una captura pública adicional a las 21:09 UTC confirmó que la tasa histórica de las 21:00 coincidía con la tasa vigente del ticker y se diferenciaba de su predicción. Esto respalda tratar la marca como inicio del periodo. No se han contrastado movimientos privados de cuenta. [Especificaciones de funding EEE](https://support.kraken.com/es/articles/perpetual-contract-specifications-for-clients-in-the-eea), [histórico](https://docs.kraken.com/api-reference/historical-funding-rates/historical-funding-rates).

También se excluyó la última vela trade/mark del conjunto original, iniciada el 2 de octubre a las 01:00 UTC: la captura se hizo a las 01:06 y la vela aún no estaba cerrada.

## Qué hace el motor y qué falta

- Señales con datos de barras cerradas; entrada en la oportunidad siguiente. Ruptura excluye la barra de señal de su rango histórico.
- ATR definido explícitamente; tamaño por riesgo, lote mínimo, pasos de cantidad, tick y colchón de margen. El adaptador lee el margen EEE del catálogo, no el máximo global.
- Una cartera en USD y una posición total; stops que pueden estrecharse por presupuesto de riesgo, nunca ampliarse para soportar pérdidas.
- Comisiones sobre el nominal de cada fill; funding con signo; costes de fill ya incluidos en P&L y sin doble descuento.
- Stop primero si una vela toca stop y objetivo. Si un mark extremo permite liquidación y no sabemos el orden real, se detiene e invalida esa ejecución.
- Operaciones, curva horaria, exclusiones, contribución por activo, riesgo y costes guardados. La diferencia contable entre suma de P&L y cambio de saldo quedó por debajo de 0,000000001 USD en las 16 ejecuciones.

Sigue siendo un simulador OHLC. Faltan fills parciales, cola, latencia/rechazos, protección de precio y liquidación exacta. Las especificaciones actuales se aplican retrospectivamente como estudio de viabilidad presente. No se estimaron intervalos de confianza, corrección formal por múltiples variantes ni una referencia equivalente en riesgo. La referencia pasiva del informe sirve únicamente de contexto.

**Agosto y septiembre siguen reservados.** El programa impide evaluar ventanas que invadan ese periodo. Se ha auditado la calidad de sus datos, pero no calculado el rendimiento de las estrategias allí.

## Base para monitorización de coste bajo

Las 16 evaluaciones tardaron **3,52 segundos** en la ejecución final local (3,63 segundos en la primera). El motor usa solo Python estándar y no importa agentes ni SDKs de exchange. Durante el replay hizo **0 peticiones de red, 0 llamadas a modelos y 0 tokens de API**. Fuera del replay se realizaron tres lecturas públicas de Kraken para contrastar el momento del funding.

La futura arquitectura puede mantener un feed público, guardar datos localmente y evaluar H1 seis veces al día por activo y H2 una vez al día. La supervisión de posiciones debe seguir siendo continua e independiente de ese ritmo de señales. Los stops alojados en el exchange, reconciliación de órdenes y reconexión requieren desarrollo específico.

Kraken documenta feeds WebSocket y mantenimiento de conexión mediante ping. Un feed ligero puede vigilar precios; para reconstruir velas exactas y estimar costes hacen falta los mensajes/datos apropiados, sin tratar muestras de ticker como todos los trades. [Suscripciones oficiales](https://support.kraken.com/articles/360022635632-subscriptions-websockets-api-derivatives).

Esto permite eliminar consultas continuas a IA del cálculo de señales. No demuestra coste total cero: el equipo debe permanecer disponible, con electricidad, conexión, almacenamiento y recuperación ante fallos. Todavía no se ha desplegado un monitor 24/7 ni contratado un servidor.

Cambiar el exchange requeriría reemplazar el adaptador de datos y especificaciones, recalibrar costes y repetir la evaluación. Los agentes y el exchange pueden reconsiderarse después; este paso no modifica sus perfiles.

## Archivos y siguiente decisión

- [Informe completo generado, con las 16 evaluaciones](../data/research_runs/20261005_local_strategies_v2/informe.md).
- [Parámetros fijados](../config/local_strategy_research.json).
- [Auditoría de funding](../data/research_runs/20261005_local_strategies_v2/funding_audit.json).
- [Resumen numérico](../data/research_runs/20261005_local_strategies_v2/summary.json).
- Reproducción: `python scripts/run_local_strategy_research.py --output data/research_runs/<directorio-nuevo>`.

La siguiente prioridad de estrategia es explicar el fallo de las rupturas y el bajo número de objetivos alcanzados, usando el tramo de desarrollo y registrando cualquier hipótesis nueva. No reajustar sobre junio–julio ni consumir la reserva final para buscar una curva positiva. Para una conclusión sólida harán falta más periodos completos, incertidumbre estadística y costes de ejecución observados. El resultado actual permite continuar investigando; no autoriza pasar a capital real.
