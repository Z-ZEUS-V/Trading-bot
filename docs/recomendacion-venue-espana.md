# Recomendación provisional de venue para operar desde España

**Fecha de revisión:** 1 de octubre de 2026  
**Estado:** sustituida por la decisión posterior del usuario de operar solo cripto en Kraken durante la fase actual. Se conserva como antecedente de por qué no se recomendó un venue único para el universo original multi-mercado. No hay integración ni órdenes habilitadas.

## Decisión

No he encontrado evidencia oficial de un único venue que cubra simultáneamente los requisitos recuperados: top 10 dinámico de criptoactivos mediante futuros/perpetuos, exposición a acciones estadounidenses vía Stock Perps ejecutables por API, y oro, plata y crudo, con disponibilidad confirmada para un residente español.

La recomendación provisional anterior era **separar la operativa regulada en dos venues**:

1. **Interactive Brokers Ireland (IBKR) como venue principal para futuros tradicionales** de índices de renta variable y materias primas (metales/energía). La CNMV lo registra como empresa de servicios de inversión del EEE en libre prestación en España; la TWS API admite contratos de futuros y órdenes. Esto no convierte Stock Perps en el producto equivalente: la alternativa que sí queda respaldada aquí es exposición mediante futuros listados, especialmente índices.
2. **Kraken Derivatives para la pata de futuros cripto del EEE**, sujeto a habilitación de cuenta, cuestionario de idoneidad e información fiscal. Sus materiales describen la oferta de derivados EEE bajo MiFID II y proporciona API de derivados. Antes de desarrollar, hay que comprobar por API la cobertura real del top 10 deseado, instrumentos, tamaños mínimos, comisiones y permisos de la cuenta española.

Esto es una arquitectura candidata, no una afirmación de que ya satisface el universo entero. La restricción que sigue abierta es operar exactamente las diez mayores criptomonedas como universo dinámico y conseguir cotizaciones/histórico/contratos disponibles para cada una. Si esas condiciones no se cumplen en Kraken, se excluye el activo de la cesta ejecutable y se deja documentado; no se sustituye por un producto no verificable. Los Stock Perps no se incorporan a ejecución hasta que haya soporte oficial de API para España; en la propuesta actual se reemplazan por futuros listados de índices.

## Por qué no elegir un solo venue

- **IBKR:** amplitud global de futuros de índices y materias primas, API oficial y registro CNMV. Los futuros de criptomonedas que anuncia no acreditan cobertura de un top 10 dinámico completo ni equivalencia con cripto-perpetuos.
- **Kraken EEE:** su documentación acredita derivados cripto para clientes del EEE, pero no un catálogo de futuros de acciones e índices y materias primas para este proyecto.
- **Bybit EU:** la documentación disponible de la Unified Trading Account no confirma futuros para el modo aislado y describe spot como producto soportado en ese modo. No se toma como candidata a ejecución de derivados hasta verificar oficialmente productos y elegibilidad de una cuenta española.
- **Bitunix:** las notas heredadas del proyecto dicen que Stock Perps no admitían trading por API en la revisión del 19-08-2026. No se adopta como venue ejecutable sin confirmar país, alcance regulatorio aplicable, producto y API vigente.

La decisión vigente del usuario simplifica este plan: empezar solo con **Kraken Derivatives y cripto**. Ver la tarifa por operación contra broker en `comparativa-comisiones-kraken-broker.md`. El universo, los contratos y los permisos de API aún deben verificarse para la cuenta concreta antes de construir el adaptador.

## Costes: qué podemos optimizar y qué falta cotizar

- El coste IA baja al evitar consultas repetidas de selección estática; los scripts ahora guardan outputs y uso, y reutilizan únicamente una consulta de selección cuyo prompt completo y perfiles locales coinciden. Astra continúa en `medium`; no se alteró modelo ni esfuerzo.
- La investigación web guarda uso pero vuelve a buscar, porque el mismo tema puede tener fuentes y datos recientes distintos.
- No fijo tarifas de exchange, spread, datos ni comisiones sin elegir contratos y volumen. En IBKR esas cifras dependen del mercado, contrato, plan de comisiones, permisos y datos; en Kraken, del producto y nivel de tarifas. Se medirán por contrato antes del backtest para no fabricar una comparación.
- El registro IA es una estimación basada en el uso comunicado por Agents API y tarifas estándar cortas actuales; no es la factura final y excluye cargos de herramienta no expuestos. La guía oficial de OpenAI advierte que el uso es best-effort y que Agents API no expone por separado los tokens de escritura de caché.

## Siguiente paso de ingeniería

Antes de escribir adaptadores, mantener esta decisión como propuesta provisional y generar una matriz de instrumentos reales mediante los endpoints oficiales: símbolo/contrato, disponibilidad España, API de datos y órdenes, histórico, granularidad, tick/contract size, horarios, comisiones, spread, funding o roll, y permisos. Si la cobertura de Kraken no satisface el universo cripto, decidir explícitamente si se reduce el universo, se amplía el número de venues o se aparca esa pata. Ningún API key ni permiso de trading se solicita aquí.

## Fuentes oficiales

- [Registro CNMV de Interactive Brokers Ireland (n.º 5023)](https://www.cnmv.es/Portal/consultas/esi/esisextranjeraslp?lang=es&numero=5023&tipo=CLP&vista=17)
- [Documentación TWS API de IBKR](https://www.interactivebrokers.eu/campus/ibkr-api-page/trader-workstation-api/)
- [Mercados y productos de futuros IBKR](https://www.interactivebrokers.eu/de/trading/pdfhighlights/PDF-FutureOptions.php?ib_entity=de)
- [Derivados de Kraken para clientes del EEE](https://support.kraken.com/es/articles/overview-of-changes-for-eea-clients)
- [Documentación API oficial Kraken Derivatives](https://support.kraken.com/articles/8832693094036-derivatives-api-documentation)
- [Bybit EU Unified Trading Account: productos admitidos](https://www.bybit.eu/en-EU/help-center/article/Introduction-to-Bybit-Unified-Trading-Account)
- [Bitunix: introducción a Stock Perps](https://www.bitunix.com/es-es/hub/helpcenter/article/introduction-to-stock-perpetuals?id=211)
- [OpenAI: uso, precios y límites de observabilidad en Agents API](https://developers.openai.com/api/docs/guides/agents-api/observability)
- [OpenAI: precios API](https://developers.openai.com/api/docs/pricing?tab=suite)
