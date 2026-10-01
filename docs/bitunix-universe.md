# Universo objetivo: Bitunix

## Alcance solicitado

- Diez criptomonedas con mayor capitalización de mercado en el momento de calcular el universo.
- Stock Perps de acciones estadounidenses grandes que estén disponibles para la cuenta/región.
- Oro, plata y petróleo crudo en los productos listados por Bitunix.

El universo debe resolverse dinámicamente en cada actualización, no escribirse como lista fija. La capitalización global requiere un proveedor independiente con timestamp; después el bot debe cruzar esos activos con los contratos actualmente listados y habilitados en Bitunix. Para evitar sesgo de supervivencia, los backtests usarán la composición histórica punto en el tiempo del top 10, no la lista actual aplicada hacia atrás.

## Datos y contratos

La documentación de Bitunix describe interfaces públicas para datos de mercado y canales WebSocket de futuros. Sus canales públicos incluyen velas, precio de mercado/índice/marca y funding, profundidad y operaciones. El canal de velas informa actualizaciones cada 500 ms; eso no significa que cada vela esté cerrada ni que todos los productos TradFi estén expuestos por API. Cada snapshot debe incluir símbolo, canal, timeframe, timestamp, estado de vela y fuente.

Los nombres de productos TradFi que Bitunix publica actualmente incluyen `XAUUSDT` (oro), `XAGUSDT` (plata) y `CLUSDT` (crudo). Verificar en tiempo de ejecución símbolo, especificación, unidades, horario, fees, funding, fuente del precio de referencia y disponibilidad para la cuenta. La guía de Bitunix los describe como productos ligados al precio y cotizados en USDT; no asumir que son contratos tradicionales entregables de CME ni que comparten reglas de vencimiento/roll de futuros listados.

## Acciones tokenizadas / Stock Perps

Bitunix describe Stock Perps como derivados liquidados y marginados en USDT que siguen precios de acciones estadounidenses; no confieren propiedad, voto ni dividendos. Su centro de ayuda indica que, al 19 de agosto de 2026, esos pares no admiten trading por API y que la disponibilidad depende de la región. Por lo tanto:

- Mantenerlos como universo de análisis solo si la cuenta puede verlos y hay un feed de datos legible y permitido.
- Marcarlos `analysis_only` / `api_trading_unavailable`; excluirlos de cualquier universo ejecutable del bot hasta que Bitunix confirme soporte oficial por API.
- No reemplazar la API con automatización de la interfaz web.
- Volver a comprobar disponibilidad, símbolos y reglas antes de cada integración; el estado del producto puede cambiar.

## Reglas para Astra y los agentes

1. Separar familias y backtests por categoría e instrumento: cripto perpetuo, Stock Perp y producto commodity de Bitunix. No transportar un resultado de futuros tradicionales directamente a estos derivados.
2. En cripto, pedir el origen y timestamp del ranking de capitalización, moneda de cotización, valor de market cap y lista de Bitunix elegible.
3. Para cada símbolo, usar especificación real del producto, historial suficiente, fees, spread, slippage, funding, mark/index y liquidez.
4. Las estrategias se validan por instrumento y timeframe; una estrategia puede calificar para BTC y no para un altcoin, un Stock Perp o CLUSDT.
5. Si el proveedor de datos, la cobertura histórica, la elegibilidad API o la frescura faltan, Astra debe marcar el activo no evaluable o abstenerse. No elegir una alternativa arbitraria para completar diez.

## Fuentes oficiales consultadas (30-09-2026)

- [Bitunix Open API](https://www.bitunix.com/api-docs/): sus interfaces públicas permiten consultar configuración y datos de mercado.
- [Bitunix Futures WebSocket: K-line](https://www.bitunix.com/api-docs/futures/websocket/public/kline%20channel.html): snapshots y actualizaciones de velas; el documento indica push cada 500 ms.
- [Bitunix Futures WebSocket: precio](https://www.bitunix.com/api-docs/futures/websocket/public/MarketPrice%20Channel.html): precio mark/index, funding y próximos horarios de liquidación.
- [Bitunix Stock Perps](https://www.bitunix.com/es-es/hub/helpcenter/article/introduction-to-stock-perpetuals?id=211): naturaleza del producto, falta de propiedad sobre acciones, restricciones regionales y estado de trading API.
- [Bitunix productos commodity](https://www.bitunix.com/hub/academy/operation-guide/bitunix-product-guide/bitunix-commodity-futures-guide): pares commodity publicados, incluidos XAUUSDT, XAGUSDT y CLUSDT.
