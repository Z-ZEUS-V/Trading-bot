# Estado actual y guía para retomar

Última consolidación: 2026-10-05. Este documento resume lo que puede recuperarse de los archivos disponibles y las decisiones de alcance confirmadas en esta conversación. No sustituye una exportación de la conversación original de Codex.

## Objetivo del proyecto

Construir por fases un asistente de investigación y, más adelante, un bot de futuros cripto. El sistema debe usar datos de mercado verificables y pruebas reproducibles para proponer una estrategia candidata o abstenerse. Los agentes de OpenAI analizan los datos que la aplicación les entregue; no son un feed de mercado ni un motor de backtesting.

Alcance actual por decisión del usuario: operar solo cripto mediante Kraken Derivatives por ahora. Renta variable, materias primas y brokers quedan aparcados. DeFi está explorado documentalmente; Hyperliquid es candidato técnico de testnet, pero aún no se ha verificado la operabilidad legal desde España ni se ha aprobado una conexión mainnet. Ver `docs/analisis-defi-kraken-espana.md`.

Decisión de razonamiento: el usuario quiere utilizar como referencia de selección de estrategias el resultado generado por Astra con esfuerzo `high`, por el valor de análisis adicional. Ese ranking prioriza **investigación y backtests**, no autoriza operación ni prueba rentabilidad. No se ha decidido que Astra deba usar `high` en cada futura consulta operativa; el coste y la calidad deben medirse con paquetes reales antes de fijar el enrutamiento de producción. Véanse los informes versionados de selección y costes en `data/research_runs/` y `docs/estimacion-costes-operativos-y-criterios-reasoning.md`.

**Replanteamiento confirmado el 2026-10-05:** el capital inicial previsto para trading es 50 USD; gastos operativos presupuestados aparte; el capital puede aumentar según resultados. El usuario informa que ninguna estrategia seleccionada tiene rentabilidad verificada para el proyecto y que los costes hacen peor su viabilidad. Por tanto, las estrategias clasificadas son hipótesis para probar, no candidatas aprobadas. La siguiente fase debe comprobar viabilidad de lote/margen y P&L neto para 50 USD antes de avanzar a ejecución. Plan en `docs/replanteamiento-capital-inicial-50-usd.md`.

**Aclaración posterior del usuario, 2026-10-05:** desea margen cruzado con stop loss, beneficio objetivo de 5–10 % de la cuenta de futuros por operación ganadora y pérdida planificada de 2–4 %, hasta 5 %. Pide ampliar sustancialmente el estudio de trading algorítmico y permite propuestas alternativas. El estudio interpreta los porcentajes sobre equity al entrar y netos de costes de trading; no son retornos prometidos ni un límite garantizado por el stop. La propuesta inicial es simular riesgo 2 %, una posición total y exposición máxima 2x, comparando escenarios mayores por separado; estas últimas son propuestas de investigación, no ajustes aprobados para operar. Fuentes, aprendizaje aplicado, cálculos y experimentos propuestos en `docs/estudio-trading-algoritmico-2026-10-05.md`.

**Confirmación requerida:** durante la fase de implementación, antes de ejecutar cualquier llamada a un modelo con razonamiento `high`, pedir confirmación explícita al usuario. No disparar esa llamada hasta recibirla. Esta confirmación es independiente de haber elegido el resultado `high` existente como referencia de investigación.

**Instrucción posterior vigente, 2026-10-05:** no llamar a Astra todavía, en ningún nivel. El usuario pide continuar en la estrategia del exchange y dejar para después la revisión de agentes y posible cambio de exchange. La monitorización futura deberá ser asequible. No ejecutar investigación/selección remota por iniciativa propia.

## Recuperado y disponible

- Catálogo local de 10 fichas de estrategia en `data/strategies.json` y `data/astra_research.sqlite3`, incluida una ficha específica para carry de basis/funding en perpetuos cripto.
- Dos informes de investigación guardados en `data/research_runs/` y una síntesis en `strategy-research.md`.
- Arquitectura propuesta, notas históricas específicas de Bitunix, prompts de selección/decisión y scripts para las sesiones de investigación.
- `data/platform_agents.json` contiene cuatro perfiles: investigador, analista de mercado, revisor de riesgo/backtests y coordinador Astra. En una comprobación previa de la API, los cuatro IDs coincidían con los perfiles remotos del proyecto de API seleccionado.
- La copia recuperada inicialmente no tenía metadatos `.git` ni el historial de chat del otro ordenador. El directorio de trabajo actual sí es un repositorio Git; eso no recupera automáticamente aquellas conversaciones.

La comprobación remota de agentes es un dato de la sesión anterior, no una comprobación de conectividad o permisos realizada al leer esta carpeta. No se guarda aquí ninguna clave API.

El usuario confirma el 2026-10-02 que Kraken Futures está habilitado en su cuenta y que puede crear claves en Futures/Derivatives. La petición anónima desde su PC dio el 401 `api_key_not_found` esperado. Con el par original y con un par nuevo, Check v3 devolvió `request_signature_invalid`; `GET /derivatives/api/v3/accounts` devolvió `authenticationError`. La respuesta privada de cuentas se descartó sin mostrarla ni guardarla. El usuario afirma que copió correctamente las claves; no atribuirlo sin evidencia a un error de copia. La autenticación de Futures sigue sin confirmarse pese a probar un nuevo par y varias formas documentadas de firma. El 2026-10-02 el usuario confirmó que ya envió el mensaje a Kraken Support para verificar el estado/tipo de la clave y el formato de firma esperado, incluyendo endpoints y códigos de error sin adjuntar claves ni firmas. No crear más pares ni repetir la misma prueba mientras se espera la respuesta de Kraken. No se ha recibido ni guardado ninguna credencial en el proyecto. La comprobación de Kraken Pro sigue sin confirmarse: las dos ejecuciones anteriores terminaron localmente por falta de credenciales o formato Base64 antes de llamar al API. Los endpoints públicos de instrumentos, velas y analíticas de Kraken Derivatives sí se consultaron sin credenciales el 2026-10-01; resultado y límites en `docs/plan-pruebas-estrategias-kraken.md`.

El 2026-10-02 se guardó además una instantánea completa del endpoint público de instrumentos: 226 registros, hora del servidor `2026-10-02T00:16:39.988Z`, con respuesta original y manifiesto SHA-256 en `data/market_data/instruments/20261002T001640Z/`. No se aplicaron filtros: el catálogo incluye distintas clases de contratos y no demuestra elegibilidad de la cuenta.

También se sondeó un año de historia pública horaria para `PF_XBTUSD` y `PF_ETHUSD`: trade, mark y future-basis devuelven 8.761 puntos cada uno desde 2025-10-02; funding devuelve 5.556 puntos desde 2026-02-12 13:00 UTC. No se observaron huecos horarios dentro de los tramos devueltos; funding anterior a esa fecha no estuvo disponible en estas consultas. Informe y hashes en `data/market_data/coverage/20261002T001950Z/coverage.json`. Este es un sondeo por ventanas, no un backtest ni prueba de rentabilidad.

El 2026-10-02 también se descargó y normalizó esa muestra BTC/ETH en `data/market_data/datasets/20261002T003224Z/`, con respuestas originales gzip, CSV gzip y manifiestos por serie. Una comprobación de los últimos 30 días cubrió 172 contratos cripto PF_/PI_ según categorías del catálogo: los cuatro tipos de serie devolvieron 721 puntos por contrato, sin errores ni saltos horarios, en `data/market_data/coverage/20261002T004152Z/coverage.json`. El sondeo previo `20261002T003731Z` usó solo prefijos PF_/PI_ e incluía productos no cripto; está marcado como preliminar y supersedido.

El 2026-10-02 se consultó además la profundidad por contrato/serie de los 172 instrumentos seleccionados: 688 consultas públicas, sin errores ni contratos sin puntos. El resultado y hashes están en `data/market_data/history_depth/20261002T010323Z/depth.json`; las llamadas de intervalo completo alcanzaron el límite de respuesta (`more=true`) en 169–170 contratos por serie, por lo que su primer timestamp sirve como estimación del comienzo, no como serie completa. Los puntos más antiguos observados fueron: trade 2020-02-26, mark y future-basis 2021-07-07, funding 2026-02-12. Ningún instrumento de la instantánea ofrece 365 días comunes en las cuatro series; 169 ofrecen al menos 90 días estimados. Estos umbrales no validan continuidad ni el universo histórico.

Para convertir esa medición en un conjunto concreto de backtest se descargó el histórico disponible de `PF_XBTUSD` y `PF_ETHUSD` por ventanas de 30 días en `data/market_data/datasets/20261002T010411Z/`: 39.688 puntos trade por activo desde 2022-03-23, 39.709 puntos mark y basis desde 2022-03-22, y 5.557 puntos de funding desde 2026-02-12. Las ocho series cubren hasta 2026-10-02, sin huecos horarios detectados ni errores de consulta; ningún chunk quedó truncado. No se rellenó el periodo previo a los datos de funding. La descarga se guardó correctamente; el comando original encontró luego un problema de codificación al imprimir una flecha Unicode en Windows, ya corregido en `scripts/ingest_kraken_public_history.py`.

**Corrección de alcance del funding, 2026-10-05:** los límites anteriores describen las consultas de analytics, no toda la historia pública de Kraken. El endpoint distinto `historical-funding-rates` devolvió 8.861 observaciones por BTC/ETH, desde 2025-10-01 08:00 hasta 2026-10-05 20:00 UTC. Respuestas, SHA-256 y auditoría en `data/market_data/funding_rates/20261005T204909Z/`. Se detectaron 7 intervalos con 8 horas ausentes por activo; cero duplicados y cero tasas no finitas. No está conciliado aún el significado de tasas, signo, devengo y publicación con las otras series. No rellenar con cero ni modificar los conjuntos anteriores. Esta captura no constituye todavía un dataset completo de P&L.

Se ejecutó también un ejercicio local de 120 escenarios de objetivos/riesgo, largos y cortos, con costes explícitos: `data/research_runs/20261005_account_risk/`. Es aritmética de contratos lineales, no resultados de estrategias. No incluye funding, liquidación ni redondeo a lotes.

**Siguiente paso completado, 2026-10-05:** conciliación local de funding y primera simulación de estrategias. Las 5.555 observaciones comunes por activo coinciden; se recuperan dos horas ausentes del histórico usando analytics observado, y quedan seis huecos anteriores al comienzo de las evaluaciones. Una captura ticker/histórico a las 21:09 UTC respalda que la tasa marcada a las 21:00 aplica a esa hora. Evidencia en `data/market_data/funding_timing/20261005T210921Z/` y `data/research_runs/20261005_local_strategies_v1/funding_audit.json`. No se conciliaron extractos privados. La vela parcial de las 01:00 UTC del 2 de octubre queda excluida del adaptador.

El motor local `src/trading_lab/` y `scripts/run_local_strategy_research.py` ejecutaron 16 evaluaciones (H1/H2, objetivos 5/10 %, dos costes, dos ventanas). Desarrollo febrero–mayo: H1 aproximadamente −15 %; H2 cerca de cero. Validación junio–julio: H1 +1,27–3,42 % y H2 +3,71–3,92 %, con solo 3–5 operaciones H2. Estos son retornos del periodo, no por operación. Agosto–septiembre queda reservado sin resultados de estrategias. Informe y limitaciones en `docs/simulacion-local-estrategias-2026-10-05.md`; no hay estrategia aprobada ni llamadas a Astra.

## Estado de implementación

Está implementada la base de investigación: catálogo, almacenamiento SQLite, aprovisionador de perfiles y scripts que ejecutan investigación web y selección de estrategias mediante la Agents API.

Primera optimización aplicada: resultados de selección estática se guardan con huella del prompt/perfil, usage y coste estimado; una coincidencia exacta puede reutilizarse localmente y `--refresh` fuerza una llamada. El investigador web guarda usage pero siempre repite búsquedas para evitar servir investigación obsoleta. Los perfiles/modelos operativos existentes siguen sin cambios; la selección `high` se usa ahora como referencia del ranking de investigación, no como configuración ya aprobada para cada consulta en vivo.

Además de la biblioteca de investigación, están implementados un adaptador de snapshots Kraken con hashes y conciliación de funding, señales H1/H2 deterministas y un primer replay de cartera lineal USD con lotes, costes y fills OHLC aproximados. No importa modelos/SDKs ni envía peticiones durante el cálculo.

Todavía faltan:

1. Feed continuo, reconexión, persistencia y supervisor 24/7; un universo transversal requeriría además composición histórica.
2. Calibración con spreads/fills observados y contraste de flujos privados de funding cuando vuelva la autenticación. La conciliación pública ya permite el replay documentado, no una certificación de cuenta.
3. Validación estadística más amplia, nuevos periodos completos, incertidumbre, modelado de latencia/fills parciales/liquidación y evaluación final reservada. El replay inicial ya guarda resultados versionados.
4. Aplicación que coordine el feed, los cálculos locales, los agentes y la salida analítica.
5. Paper trading. No existe integración de envío de órdenes.

Hay resultados exploratorios de dos reglas; aún no hay estrategia con rentabilidad robusta verificada ni bot operativo.

## Siguiente secuencia de trabajo documentada

1. Esperar la respuesta del ticket ya enviado a Kraken Support. Cuando contesten, revisar sus indicaciones antes de cualquier nueva prueba; no adjuntar ni enviar claves, secrets o firmas.
2. Aplicar primero la puerta de viabilidad para 50 USD del documento `docs/replanteamiento-capital-inicial-50-usd.md`, incluida especificación y coste vigentes del lote mínimo; si un contrato no cabe dentro de límites de riesgo, usar `NO_TRADE`.
3. Revisar el fallo H1 y la escasez de objetivos alcanzados H2 usando desarrollo; registrar hipótesis nuevas antes de ejecutarlas. Mantener datos ausentes explícitos y no completar con cero las seis horas antiguas todavía no recuperadas.
4. Mejorar la precisión de ejecución y ampliar periodos completos antes de afirmar rentabilidad. Conservar agosto–septiembre reservado; no ajustar sobre la validación ya observada. Funding/basis sigue como línea separada.
5. Añadir evaluación de incertidumbre y más periodos cronológicos; monitor local continuo solo cuando su alcance se implemente. Mantener 0 llamadas a Astra hasta nueva indicación del usuario.
6. Solo después de evidencia robusta, límites de riesgo aprobados y simulación/paper satisfactoria, estudiar una prueba real con supervisión humana. El bot debe poder no operar indefinidamente.

## Inconsistencia conocida en la documentación

`guia-conexion-agents-api.md` conserva instrucciones antiguas: habla de tres agentes y dice que `OPENAI_API_KEY` no estaba disponible. El proyecto actual especifica cuatro perfiles y el historial de esta sesión registró una comprobación anterior de los cuatro IDs contra la API. Para el estado técnico y el diseño actual, consultar `architecture.md`, `data/platform_agent_specs.json` y `data/platform_agents.json`; no seguir literalmente las frases antiguas de esa guía sobre cantidad de agentes o disponibilidad de la clave.

## Límites de esta recuperación

La exportación disponible permite retomar el plan técnico, pero no recuperar decisiones conversacionales que no se escribieron en archivos. Para reconstruirlas haría falta el chat del otro Codex o una exportación adicional de su conversación. La carpeta contiene un ZIP y una copia extraída del mismo contenido; no se identificaron otros archivos en `outputs` o `work`.
