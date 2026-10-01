# Estimación de costes operativos y criterio de razonamiento

**Fecha:** 1 de octubre de 2026  
**Alcance:** estimación de diseño, no presupuesto contractual ni coste histórico del bot en producción.

## 1. Conclusiones ejecutivas

- El repositorio todavía está en fase de investigación. Hay catálogo, agentes y diseño; **no hay adaptador de mercado, motor de backtest, despachador de órdenes ni bot operativo**. Por tanto, no existe todavía un coste observado por apertura/cierre real. (Véanse `README.md`, `docs/architecture.md` y `docs/estado-actual-y-retoma.md`.)
- Para una decisión de mercado se propone un flujo de **dos análisis GPT-6 Luna y una síntesis GPT-6 Astra**, no llamadas por tick. El agente investigador con web no debe ejecutarse en el ciclo rutinario.
- Con sobres de tokens ilustrativos para un paquete compacto, la IA costaría aproximadamente **$0,038–$0,122 por decisión**. Si el bot pide una evaluación para abrir y otra para cerrar, serían **$0,076–$0,243 por ciclo completo**; escenario central: **$0,121 por ciclo**.
- Comisiones, spread/slippage y financiación pueden superar ampliamente el coste de IA. Sin venue, contrato, tamaño, tipo de orden y duración no hay una cifra real de trading. El reporte ofrece fórmulas y escenarios transparentes, no atribuye estas tasas a un exchange.
- Recomendación de configuración: mantener **medium** como base para Astra; usar **high** de forma escalonada si una evaluación de calidad muestra que reduce errores importantes o incertidumbre material por encima del coste adicional. Reservar `xhigh`/`max` para casos excepcionales con beneficio medido.

## 2. Qué significa subir el razonamiento y cómo decidirlo

El coste no aumenta por una tasa fija de “modo high”: se factura el uso de tokens según el modelo. Los tokens de razonamiento cuentan como tokens de salida facturables; un esfuerzo superior tiende a consumir más y a añadir latencia, aunque el efecto depende de la petición. La guía oficial recomienda comparar `medium` y `high` en tareas complejas, y reservar `xhigh` para casos donde una evaluación demuestre una mejora que justifica el coste y la latencia. [Guía de razonamiento](https://developers.openai.com/api/docs/guides/reasoning)

### Criterios de escalado

El sistema debe empezar con `medium` y elevar a `high` cuando coincidan una consecuencia potencialmente importante y una señal de dificultad. Señales que pueden activar la revisión `high`:

1. Los dos analistas discrepan de forma material o la salida de Astra no coincide con sus evidencias.
2. La entrada está cerca de umbrales de frescura, integridad o riesgo; hay datos faltantes, contratos/rollover ambiguos o señales contradictorias.
3. Cambia el régimen, ocurre un movimiento extremo, aparece un producto no evaluado o la evidencia/backtest relevante es escasa o inestable.
4. Una decisión podría cambiar el estado de la estrategia de elegible a abstención (o viceversa) después de costes, margen o riesgo de cola.

La prioridad siempre es corregir/recargar datos o abstenerse cuando falten datos críticos. Más razonamiento no repara datos corruptos, un feed atrasado, un backtest inválido ni una especificación contractual desconocida.

### Evaluación que autorizaría pasar a high

Comparar `medium` y `high` en un conjunto congelado de casos representativos, sin seleccionar casos después de ver sus respuestas. Incluir rutina, discrepancias, datos incompletos, estrés, cambios de régimen y casos con respuesta esperada `NO_TRADE`/`INSUFFICIENT_DATA`.

Puntuar cada respuesta en una rúbrica objetiva:

- estado correcto y abstención correcta ante datos insuficientes;
- riesgos críticos y faltantes detectados;
- uso fiel de métricas/evidence IDs, sin inventar cifras ni supuestos;
- formato JSON válido y acuerdo con reglas deterministas;
- tokens, coste y latencia.

**Regla inicial propuesta:** dejar `high` activado para los casos difíciles solo si, en un lote de validación separado, reduce errores críticos/omisiones al menos **20% en términos relativos** o al menos **2 puntos porcentuales en términos absolutos**, sin elevar errores dañinos, y su coste marginal queda bajo un presupuesto aprobado. Estos umbrales son una política inicial de ingeniería, no una garantía estadística; deberán ajustarse al tamaño del conjunto y al riesgo de cada mercado. No usar rentabilidad de corto plazo como única prueba del razonamiento: el P&L es ruidoso y no identifica causalmente la calidad de la llamada.

La comparación reciente de selección de estrategias mantuvo el mismo ranking con ambos niveles. Allí el coste pasó de $0,24773 en la repetición `medium` a $0,29228 en `high` (+$0,04455, +18%). Es una observación de **una tarea de investigación de ~13.848 tokens de entrada**, no una medición de decisión de mercado rutinaria. `high` empleó 1.034 tokens de razonamiento frente a 105 con `medium`; más tokens por sí solos no demuestran una decisión mejor. Referencia: `data/research_runs/astra-reasoning-cost-comparison-20261001T201130Z.md`.

## 3. Arquitectura de llamada que se ha estimado

Según la arquitectura guardada, una decisión puede usar:

1. **GPT-6 Luna – analista de mercado:** resumen de snapshot, régimen y calidad de datos.
2. **GPT-6 Luna – revisor de backtest/riesgo:** aptitud del backtest, costes y límites.
3. **GPT-6 Astra – coordinador:** integra los dos informes y propone candidato analítico o abstención.

Las dos llamadas Luna podrían correr en paralelo. El curador investigador (Luna con búsqueda web) se reserva para actualizar evidencia; **no se incluye en cada entrada/salida**. Los cálculos de indicadores, validaciones de datos, límites, órdenes, stops y registro deben ser deterministas en el software. El LLM no debe colocar ni gestionar órdenes.

**Unidad de cuenta:** una *decisión* significa una síntesis de mercado con las llamadas de agentes previstas; un *ciclo completo* es una entrada y su posterior salida. Para ser conservadores, el cálculo supone una decisión antes de abrir y otra antes de cerrar: 2 decisiones/ciclo. Un stop ejecutado por regla local sin nueva llamada reduce el coste IA del ciclo aproximadamente a la mitad del escenario central.

## 4. Coste estimado de IA por decisión

Tarifas estándar publicadas por millón de tokens (contexto menor de 272K): GPT-6 Astra: **$10 entrada, $1 entrada cacheada, $50 salida**; GPT-6 Luna: **$0,10 entrada, $0,01 entrada cacheada, $0,50 salida**. Los tokens de razonamiento se cobran como salida. [Precios oficiales de GPT-6 Astra y Luna](https://developers.openai.com/api/docs/pricing?tab=suite) y [guía de razonamiento](https://developers.openai.com/api/docs/guides/reasoning).

El coste se estima así, con todos los tokens de salida incluidos:

`coste = input_no_cache × tarifa_entrada + input_cache × tarifa_entrada_cache + output × tarifa_salida`.

Sobres hipotéticos por decisión, que incluyen instrucciones del agente, datos y respuestas resumidas; deben reemplazarse por el `usage` medido cuando exista el flujo:

| Escenario | Cada Luna (entrada/salida) | Astra (entrada/salida) | Coste IA por decisión | Por apertura+cierre (2 decisiones) |
|---|---:|---:|---:|---:|
| Compacto | 1.000 / 150 tokens | 2.500 / 250 tokens | **$0,03785** | **$0,07570** |
| Centralde que 0** |
| Alto | 5.000 / 600 tokens | 8.000 / 800 tokens | **$0,12160** | **$0,24320** |

Son escenarios de presupuesto, no llamadas ya observadas. Se supone una respuesta de cada Luna y Astra por decisión, tarifas estándar, sin caché, sin herramienta de búsqueda y sin repetición por error. Los precios bajos de Luna dejan su coste marginal pequeño; Astra domina el total.

### Proyección mensual por volumen

| Ciclos completos cerrados/mes | Decisiones IA (2/ciclo) | IA compacto | IA central | IA alto |
|---:|---:|---:|---:|---:|
| 20 | 40 | $1,51 | **$2,43** | $4,86 |
| 100 | 200 | $7,57 | **$12,14** | $24,32 |
| 1.000 | 2.000 | $75,70 | **$121,40** | $243,20 |

Si una evaluación llama al modelo en cada vela de 15 minutos, hay hasta 2.880 evaluaciones al mes (30×24×4), aun sin abrir una sola operación; en el escenario central eso rondaría **$174,82/mes**. Esto ilustra por qué la política debe ser por evento/condición con filtros locales, no por cada tick o cada barra sin cambio útil.

Cuando el flujo real permita medir `high` en decisiones de mercado, calcular el presupuesto escalonado con `coste_mes ≈ 0,06070 × decisiones_totales + ΔC_high × decisiones_escaladas`. `ΔC_high` debe salir de pares de llamadas con el mismo snapshot; no reutilizar automáticamente el +$0,04455 de la tarea de selección, porque aquel prompt de investigación y el prompt operativo tienen longitudes y dificultad diferentes.

La investigación extensa costará más que una decisión rutinaria. Por ejemplo, la selección comparativa medida usó ~14K tokens de entrada y costó unos $0,25–$0,29 por una ejecución. Consultas de investigación con web pueden añadir coste de herramienta además de tokens; quedan fuera de las tablas operativas.

## 5. Costes del futuro que no son tokens

### 5.1 Comisiones de abrir y cerrar

Las comisiones suelen depender del valor nominal ejecutado (notional), del contrato y del tipo de ejecución. No deben calcularse sobre el margen aportado sin comprobar la tarifa: el apalancamiento reduce el margen, pero **no reduce el notional que se negocia**.

`comisión total = notional_entrada × tasa_entrada + notional_salida × tasa_salida`.

Si entrada y salida tienen notional `N` y tasa igual `f` bps por lado:

`comisión round trip = 2 × N × f / 10.000`.

Para ilustrar magnitudes (tasas inventadas de escenario, no tarifas de una plataforma):

| Notional ejecutado | 2 bps por lado | 5 bps por lado | 10 bps por lado |
|---:|---:|---:|---:|
| $1.000 | $0,40 | $1,00 | $2,00 |
| $10.000 | $4,00 | $10,00 | $20,00 |

### 5.2 Spread, slippage e impacto

No son necesariamente una comisión visible, pero sí reducen el resultado económico. Estimar entrada y salida por separado:

`coste ejecución ≈ N_entrada × (spread+slippage+impacto)_entrada_bps/10.000 + N_salida × (...)_salida_bps/10.000`.

En $10.000 de notional, un supuesto adverso de 1, 3 o 5 bps **en cada lado** equivale a $2, $6 o $10 round trip. Debe medirse por contrato, tamaño, sesión y tipo de orden; un backtest que ejecuta al precio de señal sin esta penalización subestima el coste.

### 5.3 Funding, rollover e interés

- **Perpetuos:** `funding neto = Σ (notional al settlement × funding_rate_signed)`. Depende de dirección, tasa, calendario y duración; puede ser crédito o coste. Escenario aritmético: 1 bp adverso cada 8 horas durante 24h sobre $10.000 = **$3**. Es solo una sensibilidad ilustrativa, no una previsión de funding ni una periodicidad universal.
- **Futuros con vencimiento:** considerar comisiones de cambio/roll, diferencial entre vencimientos y efecto de la curva. No contar el “roll yield” dos veces si ya está reflejado en el P&L de los contratos.
- **Margen/financiación de efectivo, préstamo y conversión de divisa:** incluir solo cuando apliquen al instrumento y cuenta. Su existencia y tarifa dependen del producto/plataforma.

### 5.4 Otros costes y riesgos operativos

| Partida | Tratamiento en esta estimación | Datos necesarios para precio real |
|---|---|---|
| Datos de mercado en vivo e históricos | No presupuestado: podrían ser gratuitos, limitados o de pago. | Proveedor, profundidad, mercados, uso histórico, derechos de redistribución. |
| Hosting/PC, electricidad, almacenamiento y copias | No presupuestado. Con un PC ya encendido, medir consumo incremental; con VPS/servidor, cotización del proveedor. | Disponibilidad requerida, región, redundancia, carga, plazo de retención. |
| API/exchange, tarifas de cuenta y órdenes | No presupuestado hasta elegir plataforma. El envío de orden no consume tokens si lo hace el código, pero puede tener costes/reglas propios. | Venue, contrato, niveles de volumen, maker/taker, niveles/API, descuentos. |
| Herramientas de búsqueda de Astra, alertas, logs y monitorización | Excluido del bucle estimado; investigador web solo bajo demanda. | Herramientas activadas, llamadas mensuales y retención. |
| Reintentos, cancelaciones, fills parciales, desconexiones | No es una cifra fija: modelar como tasas de error y órdenes residuales. | Historial paper/live de latencia, fills y reconexión. |
| Liquidación, penalizaciones y pérdidas de cola | Riesgo contingente, no “coste medio por trade”. Puede exceder ampliamente las comisiones y el coste de IA. | Reglas de margen/mantenimiento, mecanismo de liquidación y stress test por contrato. |

No se incluyen impuestos, costes de retirada/depósito ni conversión de divisa; su aplicación depende de residencia fiscal, plataforma y ruta de fondos. Estos conceptos no son necesarios en todos los ciclos, pero deben añadirse al presupuesto total cuando correspondan.

Para presupuestar electricidad local, medir vatios medios y usar `kWh/mes = W_promedio × 0,72` para 30 días continuos; por ejemplo, 50 W medios equivalen a 36 kWh/mes. Multiplicar por el precio real del recibo en €/kWh. No se toma una tarifa eléctrica ni una cuota VPS supuesta como precio del proyecto.

## 6. Ejemplo integrado, $10.000 de notional, 24h

Ejemplo puramente aritmético con 2 decisiones IA en escenario central, comisión hipotética de 5 bps por lado, ejecución adversa de 3 bps por lado y funding adverso supuesto de 1 bp cada 8h:

| Componente | Coste estimado |
|---|---:|
| Comisiones ($10.000 × 5 bps × 2 lados) | $10,00 |
| Spread/slippage/impacto ($10.000 × 3 bps × 2 lados) | $6,00 |
| Funding (3 × $10.000 × 1 bp) | $3,00 |
| IA (2 decisiones central × $0,06070) | $0,1214 |
| **Total modelado de este ejemplo** | **$19,12** |

El total no es una cotización ni un pronóstico: cada tasa no relacionada con IA fue supuesta para mostrar cómo se suma. No incluye hosting, dato de pago, roll, impuestos, fees de liquidación ni el riesgo de precio entre entrada y salida. La pérdida o ganancia de mercado del futuro **no** está incluida en la tabla de costes.

## 7. Fórmula de coste total por ciclo

`coste_ciclo = comisiones_entrada/salida + spread/slippage/impacto_entrada/salida + funding/financiación + roll/borrow/FX + coste_IA_de_decisiones + infraestructura_asignada + datos_asignados + cargos_eventuales`.

Y resultado realizado estimado:

`P&L_net = P&L_bruto_contratos − coste_ciclo`.

El P&L bruto debe calcularse con multiplicador/tick y precios de fill reales o simulados. El apalancamiento afecta a margen y riesgo de liquidación, no convierte el notional en menor ni vuelve gratis la financiación.

## 8. Cómo medir costes reales cuando se implemente

Cada decisión API debe guardar modelo/version, esfuerzo, tokens de entrada/salida/razonamiento, tokens cacheados, coste estimado, latencia, status y tipo de decisión. Cada orden/fill debe registrar instrumento, contrato, notional, lado, maker/taker, comisión/currency, precio de referencia, fill, spread/slippage, funding/roll, IDs de orden y timestamps. No registrar claves secretas.

Luego construir un ledger por `trade_id` que una la decisión de apertura, fills, funding y salida. Reportar mensualmente por estrategia: coste AI/trade, comisiones, ejecución, financiación y P&L neto. Separar hechos de estimaciones, y verificar el total API contra el dashboard/factura del proveedor.

## 9. Lo que falta para pasar de rangos a presupuesto

1. Exchange/venue y producto/contrato concreto (perpetuo o vencimiento, multiplicador y reglas de margen).
2. Notional o tamaño por operación; maker/taker esperado; apalancamiento solo para cálculo de margen.
3. Estrategia y frecuencia objetivo: decisiones/día, operaciones completadas/mes, duración y si el cierre es otra consulta IA o regla determinista.
4. Feed de datos (solo velas vs. profundidad/trades), proveedor del universo cripto, históricos/licencias.
5. Alojamiento (PC/VPS), uptime, latencia aceptable, redundancia y región.
6. Snapshot compacto de prueba para medir tokens de cada rol con el `usage` real y la latencia.

Hasta elegir esas variables, el presupuesto responsable es: **IA central ≈ $0,12 por ciclo entrada+cierre**, más costes variables del futuro según tarifa real y fills, más datos y alojamiento aún por cotizar. Esta cifra solo sirve para orientar; el coste de trading no se valida con una estimación genérica.
