# Expansión de volatilidad intradía: estudio exploratorio

**5 de octubre de 2026, Madrid.** La [regla](protocolo-expansion-volatilidad-2026-10-05.md) se fijó antes del replay. Se evaluó en los datos públicos de Kraken Derivatives del 1 de agosto al 2 de octubre UTC de BTC, ETH, SOL y XRP, con una semana inicial para umbrales. El periodo ya se había visto para otras investigaciones; los resultados **no son una validación independiente**. No se enviaron órdenes.

## Hipótesis y ejecución simulada

Cada cinco minutos se buscó un retorno absoluto de 15 minutos por encima del percentil 95 de la semana anterior, volumen de 15 minutos por encima del percentil 75, cierre en el cuarto extremo del rango y spread no superior a 5 bps. La posición sigue la dirección de ese impulso. Un control entra en sentido contrario sobre los mismos eventos. Entrada indicativa dos minutos después, stop de precio 1%, salidas de precio 2% o 3,5% y duración máxima 240 minutos. Las políticas de salida se declararon por anticipado y se reportan ambas.

El dimensionamiento estudia pérdidas **previstas** de cuenta de 1%, 2% y 3%, con 0,1% de comisiones taker y 0,1% de reserva adversa añadidas al stop para determinar notional. El PnL usa VWAP público de libro según tamaño, 5 bps de comisión por lado y 2 bps adicionales de incertidumbre de ejecución por lado. Se calculó sensibilidad con 5 bps adicionales por lado. Funding, conversiones y fills reales no están incluidos ([tarifas oficiales](https://support.kraken.com/es/articles/fees-for-derivatives-trading-eea), [órdenes stop](https://support.kraken.com/articles/13944617482900-futures-order-types)).

## Resultado principal: 1% de pérdida prevista de cuenta

Tras los filtros quedaron 513 eventos BTC, 448 ETH, 453 SOL y 398 XRP. Las operaciones son menos numerosas porque se ignoran señales mientras una posición está abierta y se exige cierre dentro del tramo. Cada tramo usa una cuenta independiente de 10.000 USD por activo, reiniciada entre tramos; no son resultados de cartera conjunta.

| Activo | Salida de precio | Tramo temprano: operaciones; media neta por operación sobre cuenta | Tramo reciente: operaciones; media neta por operación sobre cuenta |
|---|---:|---:|---:|
| BTC | 2,0% | 94; **−0,125%** | 50; **−0,071%** |
| BTC | 3,5% | 89; **−0,085%** | 47; **−0,024%** |
| ETH | 2,0% | 105; **−0,041%** | 48; **−0,248%** |
| ETH | 3,5% | 93; **+0,038%** | 47; **−0,236%** |
| SOL | 2,0% | 117; **−0,177%** | 58; **−0,251%** |
| SOL | 3,5% | 98; **−0,143%** | 44; **−0,008%** |
| XRP | 2,0% | 127; **+0,017%** | 40; **−0,186%** |
| XRP | 3,5% | 106; **+0,192%** | 35; **−0,347%** |

La sensibilidad con 5 bps adicionales por lado resta aproximadamente 0,05 puntos porcentuales de cuenta por operación en el escenario de riesgo 1%. Así, el pequeño positivo de ETH temprano con objetivo 3,5% pasa a **−0,012%** y el de XRP temprano con objetivo 2% pasa a **−0,033%**. XRP temprano con objetivo 3,5% permanece positivo (+0,142% medio), pero su tramo reciente cae aún más (−0,397%). Este patrón no permite elegir retrospectivamente ese mercado y objetivo como estrategia.

El control que apuesta por reversión tampoco ofrece una alternativa general: con objetivo 3,5% y riesgo 1% su media es negativa en ambos tramos para BTC, ETH, SOL y XRP. Por ejemplo, XRP control da −0,307% temprano y −0,379% reciente. El mecanismo de continuidad muestra alguna señal relativa frente al control, pero **no una ventaja neta estable**.

## Qué pasó al escalar a 3% de pérdida prevista

El tamaño aumenta de aproximadamente 0,833x a 2,5x de cuenta. Esto no cambia las condiciones de señal; algunas operaciones se alteran ligeramente por el VWAP dependiente del tamaño. Con la salida de precio 3,5%, XRP temprano obtuvo **+0,468% medio por operación y +50,9% acumulado compuesto en su cuenta simulada**, pero tuvo **37,3% de drawdown** y una peor operación de **−4,44% de cuenta**, superior al 3% presupuestado. En el tramo reciente de XRP, la media fue **−1,046% por operación**, el acumulado **−31,6%** y el drawdown **32,9%**. BTC, ETH y SOL tampoco mostraron rentabilidad estable al escalar; por ejemplo, SOL temprano con objetivo de 2% perdió **−0,536% medio por operación** y tuvo **53,2% de drawdown**. Son cuentas separadas y sin límite diario ni de exposición agregada.

Con el objetivo 3,5%, hubo **8 operaciones XRP tempranas** de al menos +8% de cuenta entre 106, y **1 reciente** entre 35. En el tramo temprano, 42 de las 106 operaciones ocurrieron del 19 al 22 de agosto. Sumar sus retornos individuales da +95,2 puntos porcentuales de cuenta frente a +49,7 puntos de las 106 operaciones: otras fechas compensaron parte de esa ganancia. Excluir **a posteriori** esos cuatro días deja una media de **−0,712% de cuenta** en las 64 operaciones restantes. Esta exclusión es un diagnóstico de concentración, no un nuevo backtest ni una regla seleccionable. El periodo inicial favorable depende mucho de un episodio concreto.

El premio hipotético +8% frente a pérdida exacta −3% requiere ganar más del **27,3%** en una secuencia binaria idealizada. Aquí muchas ganancias son menores y algunas pérdidas superan el presupuesto. Alcanzar +8% alguna vez no basta para asegurar expectativa positiva o un drawdown asumible.

## Decisión y validación futura

**Rechazo esta regla como candidata a operar con dinero o a subir a 2–3% de pérdida prevista.** Detecta expansión real y produce señales, pero los resultados netos no son estables entre activos y periodos. El único tramo favorable relevante (XRP, objetivo 3,5%) depende de pocos días y se revierte en el tramo reciente. Mantengo el motor operativo existente sin cambios, al 0,25% configurado y sin órdenes.

El estudio completo se puede reproducir con [`scripts/run_volatility_expansion_study.py`](../scripts/run_volatility_expansion_study.py); las métricas y CSV de cada escenario están en [el directorio de resultados](../data/backtests/volatility_expansion_20261005/summary.json). La nueva regla y el control quedan congelados en el protocolo para [revisión prospectiva](../scripts/run_expansion_prospective_review.py) con días UTC completos **a partir del 5 de octubre de 2026**. La captura pública diaria existente reúne datos de mercado y flujo. Treinta días y cien operaciones de la política principal serían solo un cribado mínimo: aun con esa muestra harán falta financiación, ejecución realista, evaluación conjunta de posiciones y una revisión manual de incertidumbre antes de considerar operar.

La investigación académica encuentra tanto momentum como reversión intradía y sensibilidad a saltos, anuncios y liquidez, pero no demuestra rentabilidad para estos perpetuos, costes y parámetros ([Wen y cols., estudio original](https://www.sciencedirect.com/science/article/abs/pii/S1062940822000833)).
