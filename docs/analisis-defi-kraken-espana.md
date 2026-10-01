# Explorar DeFi para futuros cripto desde España

**Revisado:** 1 de octubre de 2026  
**Decisión de producto vigente:** Kraken Derivatives sigue siendo el único venue seleccionado para el bot. DeFi queda en fase de exploración; no se conecta ni se aprueba para operar con fondos.

## Conclusión ejecutiva

Sí existe una ruta técnicamente viable para un prototipo DeFi. El candidato más adecuado para estudiar primero es **Hyperliquid**, por su API REST/WebSocket oficial, órdenes firmadas, cartera API delegada y testnet. Sus tarifas base publicadas son algo menores que las de Kraken, pero el ahorro a tamaños modestos es pequeño. Ese ahorro no basta por sí solo para justificar la exposición adicional a contratos inteligentes, puentes, oráculos, liquidación, custodia propia y disponibilidad legal.

**No está confirmada la operabilidad regulatoria de Hyperliquid desde España para esta cuenta o este uso.** Las fuentes consultadas no permiten afirmar que un perp DeFi sea lícito/adecuado para el usuario minorista español ni que el protocolo/front-end esté autorizado en España. Tampoco permiten concluir que esté prohibido. ESMA dice que los perpetual futures son derivados y deben evaluarse conforme a MiFID II; en 2026 recordó que ciertos perps pueden caer dentro de las medidas nacionales para CFDs. Eso exige una comprobación jurídica específica antes de cualquier uso con dinero real.

Por tanto, recomendación: **investigar Hyperliquid exclusivamente en testnet y en modo paper/simulado mientras Kraken sigue como venue del proyecto**. No integrar órdenes reales en DeFi hasta que estén despejados país/terms/product classification, riesgos técnicos y criterios del backtest.

## Comisiones comparables

Tarifas base publicadas consultadas; el coste real cambia por volumen, maker/taker y contrato. Round trip supone dos ejecuciones con notional aproximadamente igual y excluye tenencia.

| Venue/protocolo | Maker por fill | Taker por fill | Maker/maker, round trip sobre $1.000 | Maker/taker | Taker/taker |
|---|---:|---:|---:|---:|---:|
| Kraken Derivatives, tier inicial | 0,020% | 0,050% | $0,40 | $0,70 | $1,00 |
| Hyperliquid perps, tarifa base | 0,015% | 0,045% | $0,30 | $0,60 | $0,90 |

La diferencia base de Hyperliquid es **$0,10 por cada $1.000 de notional en un round trip taker/taker** y $0,10 maker/taker; maker/maker ahorra también $0,10 en esta escala. A $10.000 de notional, serían $1 en los tres escenarios frente a Kraken. La tabla compara solo tarifa, no el coste total ni la calidad de ejecución.

En Kraken, funding de perpetuos puede sumar un coste o ingreso y conversiones de colateral pueden aplicar. En Hyperliquid, revisar además precio de entrada/salida, funding, puente/depósito/retirada, eventuales comisiones de interfaz/builder y cualquier coste de red para movimientos. No asumir que maker se consigue: una orden post-only puede no ejecutarse o llenarse parcialmente.

GMX ilustra por qué «DeFi» no tiene una tarifa única: sus docs indican 0,04% o 0,06% de tamaño de posición por apertura/cierre, según desequilibrio OI, además de funding/borrowing, impacto de precio y coste de ejecución/keeper. Para $1.000, la comisión de abrir y cerrar sería aproximadamente $0,80–$1,20 antes de los demás componentes. No es necesariamente más barato que Kraken.

## Encaje técnico y legal por candidato

| Candidato | Viabilidad técnica para bot | Tarifas/costes | España: qué se puede afirmar | Valoración inicial |
|---|---|---|---|---|
| **Hyperliquid** | Alta para prototipado: REST/WS oficiales, API wallet/agent para firmar órdenes, testnet disponible. | Base perps maker 0,015%, taker 0,045%; 14-day weighted tiers. Funding; depósito/retirada y bridge deben medirse; revisar fees de builder. | No encontré confirmación oficial clara de autorización/adecuación de perps para minoristas españoles ni una confirmación de acceso regulatorio para este caso. No usar términos o falta de geoblock como prueba de que está aprobado en España. | Mejor candidato técnico para testnet; **no aprobado para mainnet real**. |
| **dYdX** | Alta: protocolo/software de perps, interfaces y cadena/API. | Fee tier y costes de cadena; falta medir bajo contratos y cuenta concretos. | El front-end publica restricciones geográficas para EE. UU., Canadá, Reino Unido y territorios sancionados; España no figura en esa lista concreta. Sus términos trasladan al usuario la responsabilidad de cumplir la legislación local. La omisión de España no equivale a confirmación legal. | Alternativa técnica; compliance España sigue sin confirmar. |
| **GMX** | Media: SDK/API para órdenes, ejecución depende de keepers/oráculos y mercados/pools. | 0,04–0,06% al abrir y al cerrar en la mayoría de mercados, más funding/borrowing, impacto de precio y execution fee de red. | No se halló fuente oficial que confirme autorización española para exposición apalancada vía perps DeFi. | No priorizar para primera integración por costes variables y modelo de ejecución con keepers. |

## Marco regulatorio: límite de esta revisión

- ESMA clasifica los perpetual futures como contratos derivados para evaluar bajo las categorías pertinentes de MiFID II. En febrero de 2026 recordó que algunos perps, aunque se comercialicen con otro nombre, pueden ser CFDs y estar sujetos a medidas nacionales de intervención de producto.
- MiCA no sustituye automáticamente MiFID II para un producto que sea instrumento financiero. La clasificación depende de las características del producto y servicio, y del papel que desempeñe cada interfaz, equipo, operador o proveedor.
- La CNMV informa que desde el 1 de julio de 2026 los proveedores de servicios de criptoactivos cubiertos por MiCA que operan en España deben estar autorizados/notificados según corresponda. La aplicación de esa regla a cada protocolo/facilitador DeFi concreto requiere analizar quién presta qué servicio; esta nota no hace esa determinación.
- Antes de una cuenta real, pedir una comprobación escrita a asesor especializado o a CNMV sobre el producto y el operador concreto. No eludir restricciones geográficas ni términos de uso.

## Seguridad y arquitectura si se continúa

1. Empezar con testnet; el adaptador se diseña detrás de una interfaz común con Kraken, sin mover estrategia/modelo.
2. Para órdenes, crear wallet API/agent separada y de privilegio mínimo si el protocolo lo permite. No guardar frase semilla ni clave de la cartera maestra en el bot, `.env` compartido o repositorio. La aprobación inicial y revocación deben ser manuales y trazables.
3. Separar fondos operativos de tesorería; usar balance pequeño limitado y límites de retirada. No conceder permisos de transferencia a la clave de órdenes si la plataforma permite una clave de firma limitada.
4. Añadir límites duros locales, `reduce-only`, expiración/idempotencia de órdenes, reconciliación de posiciones y un interruptor que cancele y cierre/abstenga según reglas preaprobadas.
5. Medir comisiones realizadas, funding, conversiones, bridge, gas/keeper, spread, impacto y slippage por fill. Comparar P&L neto OOS con Kraken en instrumentos/timeframes equivalentes.
6. Tratar fallos de RPC, API, puente, oráculo, liquidación y despegue de stablecoin como escenarios de riesgo y bloquear apertura cuando los datos o el estado de cadena estén incompletos.

## Fuentes primarias

- [ESMA: informe final sobre clasificación de criptoactivos como instrumentos financieros](https://www.esma.europa.eu/sites/default/files/2024-12/ESMA75453128700-1323_Final_Report_Guidelines_on_the_conditions_and_criteria_for_the_qualification_of_CAs_as_FIs.pdf)
- [ESMA: recordatorio sobre perpetual futures y medidas de intervención CFD (24-02-2026)](https://www.esma.europa.eu/press-news/esma-news/esma-reminds-firms-their-obligations-under-cfd-product-intervention-measures)
- [CNMV: regulación MiCA en España y fin del periodo transitorio el 01-07-2026](https://www.cnmv.es/Portal/mica/regulacion-criptoactivos?lang=es)
- [Hyperliquid API oficial: endpoints, REST/WebSocket y testnet](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api)
- [Hyperliquid: comisiones de perps y tramos](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees)
- [Hyperliquid: firmar órdenes, endpoint de exchange](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint)
- [Hyperliquid: API wallets, nonces y separación por proceso](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/nonces-and-api-wallets)
- [Hyperliquid: términos oficiales de uso](https://app.hyperliquid.xyz/terms)
- [Kraken: fees de derivados, funding y conversiones](https://support.kraken.com/articles/360048917612-fee-schedule)
- [dYdX: restricciones geográficas de la interfaz (23-04-2026)](https://help.dydx.trade/en/articles/166970-geo-restrictions-site-access)
- [dYdX: términos del software](https://dydx.exchange/v4-terms)
- [GMX: tarifas de trading, funding, borrowing, impacto y network fees](https://docs.gmx.io/docs/trading/fees/)
- [GMX: SDK y ejemplos de órdenes](https://docs.gmx.io/docs/sdk/v2/examples/)
