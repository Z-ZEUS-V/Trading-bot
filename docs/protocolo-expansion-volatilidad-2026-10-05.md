# Protocolo previo al replay: expansión de volatilidad intradía

**5 de octubre de 2026, Madrid.** Hipótesis nueva, motivada por el fallo de la ruptura tras compresión. Investigación de solo lectura en los cuatro perpetuos ya archivados. El periodo 1 de agosto–2 de octubre de 2026 UTC se había inspeccionado previamente: sus resultados serán exploratorios, sin holdout limpio.

## Regla principal: continuidad tras una expansión anómala

En cada cierre de cinco minutos (`t % 5 == 4`), tras al menos siete días de historial:

1. Calcular el retorno de 15 minutos `r15 = close[t] / close[t-15] - 1`. Su magnitud debe superar el percentil 95 de los retornos absolutos de 15 minutos, calculados cada cinco minutos en los siete días que terminan **antes de comenzar** la ventana actual. El signo determina largo o corto.
2. El volumen trade total de los últimos 15 minutos, incluido `t`, debe superar el percentil 75 del volumen de ventanas equivalentes en esos siete días anteriores.
3. El cierre `t` debe quedar en el cuarto superior del rango high/low de esos 15 minutos para largo o en el cuarto inferior para corto. Se abstiene si el rango es cero.
4. Spread top-of-book de `t` <=5 bps. Se abstiene ante datos incompletos o inválidos.

Se asume que la vela, el volumen y la instantánea analítica del minuto `t` están disponibles tras su cierre; la entrada indicativa se retrasa dos minutos (`t+2`). La hipótesis es que el impulso con volumen y cierre extremo continúa, no que un retorno extremo por sí solo prediga ganancias.

Se registra una **variante de control** que opera en sentido contrario con los mismos eventos. Es una prueba de falsación del mecanismo de continuación, no una vía para elegir retrospectivamente el mejor sentido. CVD y profundidad se guardan como diagnóstico; no se usan para filtrar esta regla porque restringieron demasiado la hipótesis anterior. No se ajustarán los percentiles ni el spread tras ver el resultado.

## Salidas, tamaño y costes

Se reutiliza el motor de replay exploratorio congelado para la hipótesis anterior: una posición por activo; stop de precio 1,0%, take profits de 2,0% y 3,5% de precio como políticas declaradas; máximo 240 minutos; high/low de mark para barreras y stop prioritario si ambos se tocan en el mismo minuto; entrada y salida con VWAP público del libro interpolado por tamaño, salida al minuto siguiente tras barrera y nunca mejor que el nivel tocado. Comisiones taker 5 bps por lado, más 2 bps por lado para incertidumbre de ejecución; sensibilidad con 5 bps por lado. Funding y conversiones quedan pendientes. Los VWAP de un minuto no son fills garantizados.

La pérdida **prevista** de cuenta se estudia en 1%, 2% y 3%. Con stop de 1%, 0,1% en comisiones y 0,1% de reserva adversa, `notional/equity = min(riesgo/1,2%, 3x)`. Solo cambia el tamaño, no la señal. El 1% es el escenario principal; 2–3% son sensibilidades, sin modificar el motor operativo configurado al 0,25%.

## Evaluación

Se reportarán señales, operaciones, stop/objetivo/tiempo, ganadores, media neta sobre la cuenta, ganancias y pérdidas extremas, drawdown por cuenta separada, excursiones de mark, resultados en tramo temprano (8 ago–15 sep UTC) y reciente (16 sep–2 oct UTC), sensibilidad a costes y control contrario. Los cuatro activos se examinan por separado. Una media conjunta de operaciones es solo descriptiva y no representa una cartera con riesgo agregado.

Ni un resultado positivo del periodo ya inspeccionado ni una variante de control favorable autorizan órdenes. Para continuar se debe congelar una regla y evaluarla en días futuros completos, con funding, fills y exposición conjunta. Fuentes: [estudio primario sobre momentum y reversión intradía en criptomonedas](https://www.sciencedirect.com/science/article/abs/pii/S1062940822000833), [tarifas de Kraken EEE](https://support.kraken.com/es/articles/fees-for-derivatives-trading-eea) y [stops de Derivatives](https://support.kraken.com/articles/13944617482900-futures-order-types).
