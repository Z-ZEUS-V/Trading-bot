# Plan para optimizar costes sin degradar decisiones

**Fecha:** 1 de octubre de 2026  
**Estado:** primera optimización aplicada a los scripts de investigación; aún no hay bot operativo ni integración de mercado.  
**Límite actual:** el venue/contratos se están evaluando por petición del usuario; no fijar tarifas de trading hasta seleccionar contratos y revisar sus precios oficiales.

## Objetivo

Reducir llamadas, tokens, latencia y costes por operación manteniendo la detección de riesgo, la abstención correcta y una calidad analítica medible. No fijar como meta “el mínimo de tokens”: la meta es el **menor coste total que conserva el umbral de calidad y seguridad acordado**.

## 1. Orden de optimización

### A. Filtrar localmente antes de llamar a un modelo

Ejecutar en el programa determinista, sin LLM:

- Validación de timestamp, barras cerradas, huecos, unidades, contrato y proveedor.
- Cálculo de indicadores, reglas de estrategia, costes estimados, límites de exposición/margen y bloqueos.
- Deduplicación de eventos, cooldowns y umbrales: si no cambió información material, no repetir evaluación.
- Abandono seguro: snapshot vencido, incoherente o incompleto implica no solicitar una “opinión” que no puede corregir el dato y no enviar orden.
- Staging de órdenes y cualquier límite duro permanecen en código; el LLM nunca envía ni administra órdenes.

Esto evita pagar por validar con texto condiciones que una función puede comprobar de forma exacta y reproducible.

### B. Llamar por eventos informativos, no por cada tick

Usar cierre de vela, posible señal, cambio de estado o evento de riesgo como disparador. Consolidar streams de precios localmente. Recalcular siempre las comprobaciones de seguridad, pero llamar al LLM solo si el nuevo snapshot puede cambiar el análisis.

Una salida/stop que se ejecuta mediante una regla local y ya aprobada puede cerrar una posición sin pedir una decisión generativa; la salida debe tener reglas de riesgo fijadas y auditables. Si el modelo no se llama al cierre, baja el coste IA, pero no se debe eliminar una verificación de riesgo requerida.

### C. Enviar un paquete pequeño y relevante

- Datos numéricos resumidos con timestamp/proveedor, timeframe, contrato y métricas calculadas localmente.
- Solo la estrategia/finalistas relevantes y las métricas OOS de sus backtests; no reenviar el catálogo entero, historiales crudos ni informes de investigación en cada evento.
- Resúmenes de los dos especialistas con campos compactos (estado, hallazgos, riesgos y faltantes), no razonamientos largos.
- Salida estructurada compacta con status, estrategia, evidence IDs, riesgos críticos y siguiente validación.
- Mantener instrucciones y ejemplos estables al principio del prompt; variar solo los datos al final. Prompt caching puede reducir coste de entrada en prefijos elegibles/reutilizados. La Agents API no publica un contador separado de cache writes, así que el coste estimado por sesión no representa la factura exacta; hay que contrastarlo con la página de uso/facturación y no asumir que cachear siempre ahorra.

### D. Enrutar modelos según dificultad e impacto

Propuesta para validar, no cambio de configuración ya ejecutado:

| Tipo de trabajo | Ruta inicial | Condición de escalado |
|---|---|---|
| Checks de calidad/riesgo deterministas | Código local | Nunca sustituirlos por un modelo. |
| Análisis acotado de mercado y revisión rutinaria | Luna con `low`/`medium`, como especifican perfiles auxiliares | No escalar si datos y reglas son claros y la respuesta pasa validaciones. |
| Síntesis rutinaria de candidato/abstención | Astra `medium` (actual base) **o challenger GPT-6.1 Sol `medium` en pruebas** | Escalar a Astra `high` ante discrepancia, evento extremo, caso nuevo, evidencia débil o si puede cambiar una abstención/decisión material. |
| Investigación con fuentes | Curador con búsqueda web bajo demanda | No formar parte del bucle de apertura/cierre. |

La guía de modelos de OpenAI describe Astra como el modelo de mayor capacidad, GPT-6.1 Sol como alternativa de coste menor y cercana a Astra en tareas complejas, y Luna para tareas acotadas/frecuentes. Esto **no prueba** equivalencia para señales de trading: la decisión debe pasar una evaluación del proyecto. [Selección de modelos](https://developers.openai.com/api/docs/guides/model-selection) · [GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol)

## 2. Sensibilidad de coste si probamos GPT-6.1 Sol

Tarifa estándar publicada por millón de tokens, contexto corto: Astra $10 entrada/$50 salida; Sol $2/$10; Luna $0,10/$0,50. Sol cuesta 80% menos por token que Astra con estos precios. [Tarifas actuales](https://developers.openai.com/api/docs/pricing?tab=suite)

Aplicando al escenario central del presupuesto previo (Astra 4.000 tokens de entrada y 400 de salida; dos Luna suman $0,00070 por decisión):

| Ruta por decisión | Coste orientativo |
|---|---:|
| Dos Luna + Astra | **$0,06070** |
| Dos Luna + Sol en vez de Astra | **$0,01270** |
| Ahorro orientativo | **$0,04800 (79%)** |

Con 100 ciclos completos al mes y dos decisiones por ciclo, el escenario central daría alrededor de $12,14/mes con Astra frente a $2,54/mes con Sol como síntesis; el diferencial sería $9,60/mes. Es una extrapolación aritmética con sobres hipotéticos, no una cotización de uso ni una garantía de calidad. Sol solo debería sustituir Astra si la evaluación mantiene la calidad crítica y si `high` en Astra queda disponible para escalado.

La diferencia observada entre `medium` y `high` en una selección fue $0,04455 por llamada (+18%), con el ranking igual. No extrapolar ese delta a decisiones de mercado: sus paquetes tendrán diferente longitud y dificultad. Para cada ruta se debe guardar el `usage` real.

## 3. Cómo demostrar que una optimización conserva calidad

Antes de cambiar modelo, esfuerzo, prompt, número de agentes o frecuencia, construir un conjunto versionado de casos de simulación. Ejecutar las variantes con **entradas idénticas** y comparar a ciegas:

1. **Seguridad:** no recomendar candidato/entrada con datos vencidos, backtest no comparable o control duro fallido; no omitir `NO_TRADE`/`INSUFFICIENT_DATA`.
2. **Riesgos:** detección de funding, spread, slippage, drawdown/colas, datos faltantes y discrepancia de especialistas donde esos factores cambien el resultado.
3. **Fidelidad:** no inventar precios, fills, indicadores ni evidencia; JSON válido y consistente con el esquema.
4. **Calidad económica:** analizar resultados solo en backtests cronológicos OOS y paper trading con fills, fees, funding, slippage e impacto modelados. No seleccionar un modelo por un corto tramo de P&L.
5. **Eficiencia:** coste por respuesta válida, tokens, latencia p50/p95, reintentos y proporción de llamadas escaladas.

Mantener cada cambio solo si no empeora las métricas de seguridad y cumple el mínimo de calidad predefinido, además de reducir coste o latencia. Ejecutar en modo sombra primero; cambiar un elemento cada vez y conservar versión de modelo/prompt/dataset. El umbral inicial del documento previo (mejora material en errores críticos con coste aceptable) es una hipótesis de gobernanza que hay que calibrar en la muestra del proyecto.

## 4. Qué no optimizar a costa de calidad

- No eliminar verificaciones de frescura, integridad, margen, límites, permisos o kill switch.
- No reducir el tamaño del paquete por debajo de los datos que Astra necesita para abstenerse correctamente.
- No usar una salida generativa para tamaño de posición, apalancamiento, validación de orden o stop si eso se puede hacer de forma determinista.
- No cambiar a un modelo barato, proveedor externo o nivel menor sin medir casos difíciles, variabilidad, latencia y privacidad/retención.
- No usar `high` o modelos grandes para cada tick como sustituto de una arquitectura de eventos.
- No forzar órdenes maker para abaratar comisiones si el fill/selección adversa empeora el resultado neto.

## 5. Costes de trading e infraestructura

Los costes de IA son solo una parte. Tras especificar mercado/venue, contrato y tamaño, medir y optimizar por separado:

- Comisiones efectivas maker/taker y cargos por fills parciales/cancelaciones.
- Bid-ask, slippage, impacto y shortfall respecto al precio de señal.
- Funding de perpetuos, roll/financiación de futuros con vencimiento, préstamo y FX cuando apliquen.
- Feed de mercado, históricos y ranking externo de capitalización; decidir la frecuencia mínima de actualización que conserva cobertura del universo.
- Hosting, energía, almacenamiento, backups, alertas, redundancia y recuperación ante fallos.

La estrategia puede reducir costes mediante menor rotación, umbrales de señal y evitar órdenes innecesarias, pero estos cambios se aceptan solo si mantienen o mejoran el P&L neto y riesgo fuera de muestra. Kraken es ahora el venue elegido para la primera fase; aún hay que verificar contratos accesibles y tarifas vigentes aplicables a la cuenta antes de fijar los costes del backtest. Los datos pagados y hosting tampoco están seleccionados.

## 6. Medición obligatoria en el futuro bot

Por cada llamada: fecha UTC, rol, modelo/version, esfuerzo, identificador de prompt, tokens de entrada/salida/razonamiento/cache, coste calculado, latencia y reintentos. Por cada trade: `trade_id`, producto, notional, fills, comisión, referencia de señal, slippage, funding/roll y timestamps. Unir ambos logs para calcular:

- coste IA por decisión/ciclo y por estrategia;
- coste por respuesta válida y por llamada escalada;
- costes de ejecución/funding frente a IA;
- coste mensual bajo el volumen real;
- diferencia de resultado entre señales con ruta base y ruta escalada.

Los precios y aliases de modelos pueden cambiar; guardar el modelo/version explícitos y recalcular el estimador al provisionar o actualizar agentes. Prompt caching debe monitorizar lecturas y escrituras; la guía oficial detalla cómo aprovechar prefijos estables y cómo medir el ahorro. [Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching) · [Checklist de despliegue](https://developers.openai.com/api/docs/guides/deployment-checklist)

### Aplicado ya en los scripts de investigación

- Selector de estrategias: persiste la salida y el `usage` de Agents API, estima el coste de tokens y reutiliza una respuesta solo si el prompt completo, modelo, ID del agente y perfil local coinciden exactamente. `--refresh` fuerza una nueva llamada.
- Investigador web: persiste cada informe y el `usage`, pero siempre vuelve a consultar las fuentes; no reutiliza respuestas de búsqueda antiguas.
- Los registros quedan en `data/research_runs/session_cache/`. La cifra es estimada, no una factura final: la Agents API no expone por separado todos los tokens de escritura de caché ni necesariamente cargos de herramientas.
- Esta caché es solo para investigación estática. No debe usarse en decisiones de mercado en vivo, snapshots cambiantes, gestión de posiciones ni órdenes.

El atajo ahorra el coste completo de una nueva consulta de selección idéntica. No reduce el coste de la primera ejecución ni promete ahorros en el bucle futuro; ese bucle todavía no está implementado.

## 7. Secuencia de implementación sugerida

1. Congelar el presupuesto/escenario central como referencia y definir criterios de aceptación de calidad con ejemplos sintéticos e históricos.
2. En la capa de aplicación, construir validación local, deduplicación y registro de coste antes de integrar órdenes.
3. Con feed y backtest disponibles, capturar tamaños reales de snapshots y `usage` por rol.
4. Ejecutar comparación ciega Astra medium vs Sol medium; comparar coste, errores, latencia y abstenciones.
5. Implementar escalado Astra high solo para disparadores concretos y ensayarlo en modo sombra.
6. Añadir costes de trading de Kraken una vez confirmados venue/contrato y tarifas aplicables; no fijar maker/taker, funding ni proveedor de datos con supuestos.
7. Pasar de paper trading a ejecución real únicamente después de backtests OOS, costes netos y controles operativos aprobados.

### Decisión recomendada ahora

Mantener los perfiles actuales mientras construimos la capa de datos/backtest y el registro de uso. Diseñar una prueba de challenger con GPT-6.1 Sol antes de cambiar Astra. La optimización de mayor retorno esperado es evitar llamadas inútiles y reducir el paquete dinámico; después, si Sol conserva la calidad, usarlo para casos rutinarios y escalar a Astra `high` en situaciones difíciles.

### Decisión posterior del usuario: selección de estrategias con `high`

El usuario ha decidido utilizar el resultado de selección de estrategias generado con Astra `high` como referencia para priorizar la investigación y los backtests. Esto actualiza la recomendación anterior de volver a seleccionar con `medium`. La decisión **no** fija todavía el esfuerzo de razonamiento para cada futura consulta de mercado: primero hay que tener backtests y paquetes reales, y entonces medir coste, latencia y errores críticos por nivel. Tampoco convierte el ranking en autorización para operar. Dado el alcance actual de cripto mediante Kraken, antes de backtest hay que adaptar y filtrar el ranking a estrategias plausibles en futuros perpetuos cripto; las prioridades de materias primas no pasan a la prueba actual.

Durante la fase de implementación, cualquier nueva ejecución de un modelo con razonamiento `high` requiere confirmación explícita del usuario antes de lanzarla. La selección `high` ya almacenada no se considera consentimiento para futuras ejecuciones.
