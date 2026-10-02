# Primera ronda de hipótesis cripto para Kraken Derivatives

**Fecha de revisión:** 1 de octubre de 2026  
**Base de priorización:** selección de Astra ejecutada con razonamiento `high`.  
**Alcance:** investigación y backtesting; ninguna hipótesis queda autorizada para operar.

## Resultado de la adaptación del ranking

El ranking de investigación original cubría varios mercados. Para el alcance actual (cripto en Kraken Derivatives) queda filtrado así:

| Familia de la selección `high` | Decisión para Kraken cripto | Hipótesis a evaluar | Requisitos y reservas |
|---|---|---|---|
| Basis/funding en perpetuos cripto | **Primera candidata de investigación por encaje de producto**, no por rentabilidad demostrada. Separar pruebas que no son equivalentes. | (A) comprobar si funding/basis pasado contiene información sobre el rendimiento posterior del perpetuo; (B) estudiar por separado una cobertura spot-perpetuo que intente capturar funding. | Guardar series de funding/basis con timestamp y reglas vigentes en cada periodo. La variante cubierta necesita datos y costes de spot además de perp; no asumir neutralidad ni sumar funding como beneficio sin reconstruir fills, financiación y margen. |
| Momentum temporal | **Mantener como benchmark simple**, adaptado a instrumentos cripto de Kraken. | Señal de tendencia basada solo en datos pasados y barras cerradas; definir antes del tramo de evaluación la fórmula, horizontes, cambios de posición y controles de riesgo. | Evaluar cada producto por separado. Incluir fees, spread, slippage, funding, liquidación/margen y pausas por falta de datos. Evidencia de futuros tradicionales no valida su resultado en cripto. |
| Momentum transversal | **Posponer** hasta acreditar un universo histórico adecuado. | Ranking relativo de retornos pasados entre varios perpetuos, con regla de selección/rotación fijada antes de evaluar. | Se necesita composición histórica punto-en-tiempo, incluidos activos desaparecidos, antigüedad de los contratos y costes comparables. La lista de instrumentos actual no evita sesgo de supervivencia. |
| Carry de materias primas | **Fuera del alcance actual.** | Ninguna para esta ronda. | Broker y mercados no cripto están aparcados. |
| Pares, reversión, ML/ensemble y market-making | **No entran en la primera ronda.** | Reconsiderar solo si aparece evidencia y datos específicos que justifiquen abrir otra línea. | Requieren más supuestos, pruebas o datos de microestructura que todavía no están disponibles. |

El orden para construir el primer backtest será: comprobar y definir la hipótesis de funding/basis en datos, y en paralelo mantener momentum temporal como benchmark sencillo. Esto solo asigna el orden de investigación. No dice que haya que elegir una de estas para operar. Para aislar la contribución, no combinar señales ni ajustar muchos parámetros en la primera prueba.

## Comprobación pública de Kraken realizada

Se consultaron endpoints públicos sin API key ni acciones de cuenta:

- `GET https://futures.kraken.com/derivatives/api/v3/instruments`: devolvió instrumentos y metadatos de contratos. El listado contiene más clases de producto que cripto; `tradeable: true` en la respuesta pública no demuestra que el instrumento esté habilitado en la cuenta o entidad regulatoria del usuario. Debe filtrarse el universo por tipo, activo, estado, `platformsPermitted`, vencimiento y confirmación de elegibilidad.
- `GET https://futures.kraken.com/api/charts/v1/trade/PF_XBTUSD/1h?count=3`: devolvió 3 velas en esta comprobación.
- `GET https://futures.kraken.com/api/charts/v1/analytics/PF_XBTUSD/funding?...&interval=3600`: devolvió 24 marcas horarias de funding para la ventana solicitada en esta comprobación.

Las respuestas prueban que estos endpoints públicos son accesibles desde este entorno en este momento. **No prueban** que el API key recién creado sea válido, que pertenezca a Kraken Derivatives, que tenga permisos adecuados, que la cuenta pueda operar ese contrato, ni que exista un historial suficientemente largo/completo para backtest. La clave y el secreto no se han recibido ni guardado en el proyecto.

Documentación oficial consultada:

- [Kraken Derivatives: velas históricas](https://docs.kraken.com/api/docs/futures-api/charts/candles) — tick types `spot`, `mark`, `trade`; resoluciones desde 1 minuto hasta 1 semana; paginación/ventana a verificar al descargar.
- [Kraken Derivatives: analíticas de mercado](https://docs.kraken.com/api/docs/futures-api/charts/market-analytics) — incluye tipos `funding`, `future-basis`, `open-interest`, spreads, liquidez y slippage.
- [Kraken Derivatives: WebSocket público de libro](https://docs.kraken.com/api/docs/futures-api/websocket/book/) — suscripción de mercado a `book` en `wss://futures.kraken.com/ws/v1`.
- [Elegibilidad de derivados para clientes del EEE](https://support.kraken.com/es/articles/derivatives-eligibility-requirements-eea) — verificación, cuestionario y NIF según los requisitos que Kraken aplique a la cuenta.

## Próximos pasos técnicos

1. El usuario confirma que Futures está habilitado y puede crear claves desde Futures/Derivatives. El usuario probó un par nuevo localmente; Check v3 devolvió `request_signature_invalid` con las variantes de ruta probadas y `GET /derivatives/api/v3/accounts` respondió `authenticationError`. La respuesta de cuenta se descartó, no se mostró ni guardó. La prueba pública anónima desde el PC sí devolvió el 401 esperado `api_key_not_found`; el bloqueo inicial de Cloudflare con User-Agent Python ya se había aislado y corregido. La autenticación del par nuevo tampoco se confirmó. El usuario afirma que copió correctamente las claves; no atribuirlo sin evidencia a un error de transcripción. El usuario ya envió a Kraken Support una consulta para que revisen el estado/tipo de la clave y el requisito exacto de firma para Check v3, indicando los errores sin incluir credenciales. No generar más claves ni repetir la misma comprobación hasta recibir respuesta o una instrucción concreta de soporte.
2. La petición anónima de conectividad desde el PC del usuario sí llegó a Cloudflare/Kraken y devolvió `401` JSON `api_key_not_found`, que es el resultado esperado sin credenciales. Antes, desde el entorno de desarrollo, el User-Agent predeterminado de Python había provocado un 403/Cloudflare 1010; el comprobador actualizado usa un User-Agent estándar. El 403 queda aislado como problema anterior de User-Agent, no como explicación del rechazo de firma actual.
3. **Completado el 2026-10-02:** se implementó `scripts/capture_kraken_instruments.py` y se capturó la respuesta pública completa con fecha, URL, estado HTTP, hora del servidor, SHA-256 y lista de símbolos en `data/market_data/instruments/`. No se aplicaron filtros ni se interpretó el snapshot como universo histórico o elegibilidad de cuenta.
4. **Sondeo inicial completado el 2026-10-02:** `scripts/probe_kraken_public_coverage.py --days 365 --chunk-days 30` consultó en ventanas de 30 días el historial horario público de `PF_XBTUSD` y `PF_ETHUSD`. Cada contrato devolvió 8.761 puntos de velas `trade`, 8.761 de velas `mark` y 8.761 de `future-basis`, desde 2025-10-02 hasta 2026-10-02, sin saltos horarios en la muestra. `funding` devolvió 5.556 puntos, desde 2026-02-12 13:00 UTC hasta 2026-10-02; las ventanas anteriores no devolvieron puntos. El informe con intervalos consultados, hashes de respuesta, errores y huecos está en `data/market_data/coverage/20261002T001950Z/coverage.json`. Esto describe solo la muestra y no prueba disponibilidad anterior ni futura.
5. Continuar midiendo la antigüedad máxima y los límites de consulta por producto/contrato. En los backtests, tratar la ausencia de funding anterior al 2026-02-12 como dato faltante, nunca como funding cero; contrastar también la semántica de las marcas de `future-basis` antes de convertirlas en señal.
6. Elegir un conjunto pequeño y estable para validar el pipeline, empezando por contratos perp cripto de larga trayectoria que pasen todos los filtros; BTC y ETH son ejemplos candidatos, pendientes de verificar cuenta, cobertura y especificaciones, no una decisión final de universo.
7. Especificar reglas completas de momentum temporal y de basis/funding antes de evaluar resultados; mantenerlas como experimentos separados.
8. Construir el motor determinista y el registro de costes/datasets. Comparar con benchmark pasivo y no operar.
9. Usar la revisión de riesgo de Astra sobre resultados calculados localmente. **Cualquier nueva llamada de implementación a un modelo con razonamiento `high` requiere confirmación explícita del usuario antes de ejecutarse.**

## Qué no se ha hecho

La clave y el secreto no se han recibido ni guardado en este entorno; el usuario ejecutó las comprobaciones localmente, también con un par nuevo. El endpoint Check v3 devolvió `request_signature_invalid` y el de cuentas `authenticationError`; por tanto, no se ha confirmado la autenticación. La petición anónima sí llegó a Kraken y obtuvo el 401 esperado. La respuesta privada del endpoint de cuentas se descartó sin mostrarse ni guardarse. No se han creado órdenes, ejecutado backtests ni llamado a Astra en esta fase.

El usuario preguntó si su clave está habilitada para Kraken Pro. Kraken mantiene claves Spot/Pro separadas de Futures. El script `scripts/check_kraken_pro_key.py` llama exclusivamente a `POST /0/private/GetApiKeyInfo` (documentado sin permisos API requeridos), oculta credenciales, no guarda datos, y solo imprime los nombres de permisos. El 2026-10-02 el usuario ejecutó dos veces: una con campos vacíos y otra con secret rechazado localmente como Base64; ambas terminaron antes de enviar la petición, así que la activación Pro sigue sin verificarse. El comprobador ahora tolera whitespace y padding Base64 omitido. Un éxito demuestra que la key autentica contra Pro REST, no que Futures esté habilitado ni que la key tenga permisos para consultar datos privados concretos.
