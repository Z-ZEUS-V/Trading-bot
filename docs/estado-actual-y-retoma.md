# Estado actual y guía para retomar

Última consolidación: 2026-10-01. Este documento resume lo que puede recuperarse de los archivos disponibles y las decisiones de alcance confirmadas en esta conversación. No sustituye una exportación de la conversación original de Codex.

## Objetivo del proyecto

Construir por fases un asistente de investigación y, más adelante, un bot de futuros cripto. El sistema debe usar datos de mercado verificables y pruebas reproducibles para proponer una estrategia candidata o abstenerse. Los agentes de OpenAI analizan los datos que la aplicación les entregue; no son un feed de mercado ni un motor de backtesting.

Alcance actual por decisión del usuario: operar solo cripto mediante Kraken Derivatives por ahora. Renta variable, materias primas y brokers quedan aparcados. DeFi está explorado documentalmente; Hyperliquid es candidato técnico de testnet, pero aún no se ha verificado la operabilidad legal desde España ni se ha aprobado una conexión mainnet. Ver `docs/analisis-defi-kraken-espana.md`.

Decisión de razonamiento: el usuario quiere utilizar como referencia de selección de estrategias el resultado generado por Astra con esfuerzo `high`, por el valor de análisis adicional. Ese ranking prioriza **investigación y backtests**, no autoriza operación ni prueba rentabilidad. No se ha decidido que Astra deba usar `high` en cada futura consulta operativa; el coste y la calidad deben medirse con paquetes reales antes de fijar el enrutamiento de producción. Véanse los informes versionados de selección y costes en `data/research_runs/` y `docs/estimacion-costes-operativos-y-criterios-reasoning.md`.

**Confirmación requerida:** durante la fase de implementación, antes de ejecutar cualquier llamada a un modelo con razonamiento `high`, pedir confirmación explícita al usuario. No disparar esa llamada hasta recibirla. Esta confirmación es independiente de haber elegido el resultado `high` existente como referencia de investigación.

## Recuperado y disponible

- Catálogo local de 10 fichas de estrategia en `data/strategies.json` y `data/astra_research.sqlite3`, incluida una ficha específica para carry de basis/funding en perpetuos cripto.
- Dos informes de investigación guardados en `data/research_runs/` y una síntesis en `strategy-research.md`.
- Arquitectura propuesta, notas históricas específicas de Bitunix, prompts de selección/decisión y scripts para las sesiones de investigación.
- `data/platform_agents.json` contiene cuatro perfiles: investigador, analista de mercado, revisor de riesgo/backtests y coordinador Astra. En una comprobación previa de la API, los cuatro IDs coincidían con los perfiles remotos del proyecto de API seleccionado.
- La copia recuperada no tiene metadatos `.git`; tampoco contiene el historial de chat de Codex ni un registro de las conversaciones del otro ordenador.

La comprobación remota de agentes es un dato de la sesión anterior, no una comprobación de conectividad o permisos realizada al leer esta carpeta. No se guarda aquí ninguna clave API.

El usuario confirma el 2026-10-02 que Kraken Futures está habilitado en su cuenta y que puede crear claves en Futures/Derivatives. La petición anónima desde su PC dio el 401 `api_key_not_found` esperado. Con el par original y con un par nuevo, Check v3 devolvió `request_signature_invalid`; `GET /derivatives/api/v3/accounts` devolvió `authenticationError`. La respuesta privada de cuentas se descartó sin mostrarla ni guardarla. El usuario afirma que copió correctamente las claves; no atribuirlo sin evidencia a un error de copia. La autenticación de Futures sigue sin confirmarse pese a probar un nuevo par y varias formas documentadas de firma. El 2026-10-02 el usuario confirmó que ya envió el mensaje a Kraken Support para verificar el estado/tipo de la clave y el formato de firma esperado, incluyendo endpoints y códigos de error sin adjuntar claves ni firmas. No crear más pares ni repetir la misma prueba mientras se espera la respuesta de Kraken. No se ha recibido ni guardado ninguna credencial en el proyecto. La comprobación de Kraken Pro sigue sin confirmarse: las dos ejecuciones anteriores terminaron localmente por falta de credenciales o formato Base64 antes de llamar al API. Los endpoints públicos de instrumentos, velas y analíticas de Kraken Derivatives sí se consultaron sin credenciales el 2026-10-01; resultado y límites en `docs/plan-pruebas-estrategias-kraken.md`.

El 2026-10-02 se guardó además una instantánea completa del endpoint público de instrumentos: 226 registros, hora del servidor `2026-10-02T00:16:39.988Z`, con respuesta original y manifiesto SHA-256 en `data/market_data/instruments/20261002T001640Z/`. No se aplicaron filtros: el catálogo incluye distintas clases de contratos y no demuestra elegibilidad de la cuenta.

También se sondeó un año de historia pública horaria para `PF_XBTUSD` y `PF_ETHUSD`: trade, mark y future-basis devuelven 8.761 puntos cada uno desde 2025-10-02; funding devuelve 5.556 puntos desde 2026-02-12 13:00 UTC. No se observaron huecos horarios dentro de los tramos devueltos; funding anterior a esa fecha no estuvo disponible en estas consultas. Informe y hashes en `data/market_data/coverage/20261002T001950Z/coverage.json`. Este es un sondeo por ventanas, no un backtest ni prueba de rentabilidad.

## Estado de implementación

Está implementada la base de investigación: catálogo, almacenamiento SQLite, aprovisionador de perfiles y scripts que ejecutan investigación web y selección de estrategias mediante la Agents API.

Primera optimización aplicada: resultados de selección estática se guardan con huella del prompt/perfil, usage y coste estimado; una coincidencia exacta puede reutilizarse localmente y `--refresh` fuerza una llamada. El investigador web guarda usage pero siempre repite búsquedas para evitar servir investigación obsoleta. Los perfiles/modelos operativos existentes siguen sin cambios; la selección `high` se usa ahora como referencia del ranking de investigación, no como configuración ya aprobada para cada consulta en vivo.

Todavía no están implementados:

1. Adaptador de datos de Kraken Derivatives y, si se mantiene un universo por capitalización, proveedor externo con ranking histórico.
2. Normalización de velas, especificaciones de contrato, frescura y calidad de datos.
3. Motor determinista de backtesting con costes, funding, slippage, validación walk-forward y resultados versionados.
4. Aplicación que coordine el feed, los cálculos locales, los agentes y la salida analítica.
5. Paper trading. No existe integración de envío de órdenes.

Por tanto, aún no hay una estrategia propia probada ni evidencia de rentabilidad del bot.

## Siguiente secuencia de trabajo documentada

1. Esperar la respuesta del ticket ya enviado a Kraken Support. Cuando contesten, revisar sus indicaciones antes de cualquier nueva prueba; no adjuntar ni enviar claves, secrets o firmas.
2. Usar la adaptación de la selección `high` recogida en `docs/plan-pruebas-estrategias-kraken.md`: basis/funding como hipótesis específica y momentum temporal como benchmark; posponer momentum transversal hasta reconstruir el universo histórico.
3. Ampliar la medición de antigüedad máxima y límites de consulta por contrato. El primer sondeo de velas `trade`/`mark`, funding y basis para BTC y ETH está guardado en `data/market_data/coverage/`; su tramo de funding comienza el 2026-02-12.
4. Implementar y versionar la ingestión/normalización de datos históricos y de mercado, con frescura, huecos, contratos y funding auditables.
5. Construir un motor determinista de backtesting y probar primero una estrategia de referencia por vez, incluyendo comisión maker/taker, spread, slippage, funding y liquidación/margen cuando corresponda.
6. Evaluar cronológicamente fuera de muestra y walk-forward, con costes estresados, drawdown/colas, sensibilidad y registro de todas las variantes; la revisión de Astra audita la evidencia, pero no reemplaza los cálculos ni los controles locales.
7. Solo después de resultados robustos, pasar a paper trading. La ejecución con dinero real queda para una fase posterior, con permisos mínimos, límites duros y supervisión humana.

## Inconsistencia conocida en la documentación

`guia-conexion-agents-api.md` conserva instrucciones antiguas: habla de tres agentes y dice que `OPENAI_API_KEY` no estaba disponible. El proyecto actual especifica cuatro perfiles y el historial de esta sesión registró una comprobación anterior de los cuatro IDs contra la API. Para el estado técnico y el diseño actual, consultar `architecture.md`, `data/platform_agent_specs.json` y `data/platform_agents.json`; no seguir literalmente las frases antiguas de esa guía sobre cantidad de agentes o disponibilidad de la clave.

## Límites de esta recuperación

La exportación disponible permite retomar el plan técnico, pero no recuperar decisiones conversacionales que no se escribieron en archivos. Para reconstruirlas haría falta el chat del otro Codex o una exportación adicional de su conversación. La carpeta contiene un ZIP y una copia extraída del mismo contenido; no se identificaron otros archivos en `outputs` o `work`.
