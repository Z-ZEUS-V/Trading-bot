# Comparativa de comisiones: Kraken Derivatives frente a broker

**Fecha de consulta:** 1 de octubre de 2026  
**Comparación de broker:** Interactive Brokers Ireland (IBKR), futuro CME Micro Bitcoin (MBT), cuenta directa y tramo inicial publicado.  
**Alcance:** comisión de apertura y cierre (round trip); no es una comparación de rentabilidad ni de coste total de mantener una posición.

## Tarifas base consultadas

| Producto | Fee por cada ejecución | Apertura + cierre | Base |
|---|---:|---:|---|
| Kraken Derivatives, maker | 0,0200% | Según notional de cada lado | Tier inicial, volumen de futuros a 30 días desde $0 y menor de $5 M |
| Kraken Derivatives, taker | 0,0500% | Según notional de cada lado | Tier inicial, volumen de futuros a 30 días desde $0 y menor de $5 M |
| IBKR CME Micro Bitcoin (MBT) | $0,85 comisión + $1,15 cargo de recuperación CME = **$2,00 por contrato y lado** | **$4,00 por contrato** | Tramo inicial publicado, hasta 1.000 contratos/mes; antes de otros cargos que pudieran aplicar |

Kraken cobra el porcentaje sobre el valor nocional de cada operación ejecutada; los niveles bajan a medida que aumenta el volumen rolling de 30 días. Una orden que cruza y ejecuta de inmediato es taker; una orden que espera en el libro antes de ejecutarse es maker. La tarifa de IBKR está expresada por contrato, por lo que el coste porcentual implícito varía con el valor nocional del contrato. MBT representa 0,10 BTC.

## Kraken: coste por abrir y cerrar una posición del mismo notional

Sea `N` el notional de la posición en USD. Se supone que la apertura y el cierre tienen aproximadamente el mismo notional; el coste real usa el precio/valor de cada fill.

| Notional `N` | Maker al abrir + maker al cerrar (0,04% de N) | Maker + taker (0,07% de N) | Taker al abrir + taker al cerrar (0,10% de N) |
|---:|---:|---:|---:|
| $1.000 | $0,40 | $0,70 | $1,00 |
| $5.000 | $2,00 | $3,50 | $5,00 |
| $10.000 | $4,00 | $7,00 | $10,00 |

Son únicamente comisiones de trading. No incluyen funding de perpetuos, spread, deslizamiento, conversiones de colateral ni liquidaciones.

## Comparación práctica con IBKR

IBKR publica $0,85 de comisión para cada ejecución de MBT y un cargo de recuperación de tarifas CME de $1,15 por ejecución. Con un contrato para abrir y el mismo para cerrar, la suma indicada es **$4 por round trip**. Cada contrato equivale a 0,1 BTC, así que su notional es `0,1 × precio BTC` y no permite ajustar libremente el tamaño como un perp fraccionable.

| Ruta en Kraken para el mismo notional `N` | Comisión round trip | Frente al coste de referencia de IBKR ($4 por MBT round trip) |
|---|---:|---|
| Maker + maker | `0,0004 × N` | Kraken cuesta menos si N < $10.000; igual en $10.000 |
| Maker + taker | `0,0007 × N` | Kraken cuesta menos si N < aprox. $5.714 |
| Taker + taker | `0,0010 × N` | Kraken cuesta menos si N < $4.000 |

Así que no hay un ganador universal: en Kraken una ejecución pasiva en ambos lados puede ser más barata para un notional moderado; si se entra y sale tomando liquidez, su comisión porcentual puede superar los $4 de referencia de IBKR cuando el notional excede $4.000. En un solo contrato MBT, el notional depende del precio vigente y no es directamente fraccionable.

## Qué cambia en el coste total

- **Kraken perp:** funding se calcula continuamente en posiciones perpetuas y puede sumar un cargo o un ingreso según la tasa y el lado; Kraken indica que no es una comisión de trading cobrada por el exchange. En Multi-M, se pueden añadir conversiones/cargos si el colateral o saldo de liquidación no está en USD/USDC/USDG/USDT.
- **Futuro CME vía broker:** no tiene funding de perp; tiene vencimiento/settlement y puede requerir rollover, con su propia comisión y riesgo de base. IBKR publica además tarifas aplicables a posiciones overnight para ciertos contratos; confirmar con la cuenta y el preview de orden antes de cotizar una cifra “all-in”.
- En ambos casos hay que medir spread y slippage por separado. Una orden límite maker puede no ejecutarse o hacerlo parcialmente; no se debe perseguir maker a costa del fill o del precio.
- Para el proyecto, el usuario ha elegido **solo cripto en Kraken por ahora**. IBKR queda como referencia comparativa, no como venue seleccionado ni objetivo de integración.

## Fuentes oficiales

- [Kraken Derivatives: tarifas, tramos, cálculo sobre notional y funding](https://support.kraken.com/articles/360048917612-fee-schedule)
- [IBKR Ireland: comisiones de futuros, incluido CME MBT](https://www.interactivebrokers.ie/en/pricing/commissions-futures.php)
- [IBKR Ireland: cargo de recuperación CME para Bitcoin Micro Futures ($1,15)](https://www.interactivebrokers.ie/en/accounts/fees/CME.php)
- [CME: especificación del contrato Micro Bitcoin (0,10 BTC)](https://www.cmegroup.com/markets/cryptocurrencies/bitcoin/micro-bitcoin.contractSpecs.html)
