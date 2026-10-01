# Auditoría de cobertura de estrategias

Fecha: 2026-10-01. Revisión de `data/strategies.json`, `docs/strategy-research.md` y los dos informes de `data/research_runs/`. El alcance es el universo provisional ya conversado: cripto, productos vinculados a acciones y materias primas. El exchange y los contratos concretos quedan para más adelante.

## Conclusión

Las familias de la shortlist previa sí tienen análisis en los informes: momentum temporal, momentum transversal, carry/estructura temporal y spreads. Sin embargo, la cobertura del catálogo era incompleta para cripto: el carry de basis/funding de perpetuos no estaba separado ni etiquetado como candidato cripto. Lo incorporé a `data/strategies.json` y a SQLite.

Tras este ajuste, no queda sin clasificar ninguna familia que aparezca en los informes revisados: queda dentro del catálogo, como variante de otra familia, como componente de ejecución, como candidato pospuesto o como fuera del universo elegido. Esta es una auditoría del material y de las familias encontradas en esa búsqueda; no prueba que exista una taxonomía exhaustiva de todas las estrategias publicadas.

## Matriz de cobertura

| Familia/idea | ¿Analizada en los informes? | Situación en la selección y catálogo | Observación de cobertura |
|---|---|---|---|
| Momentum temporal / trend following | Sí | En la shortlist; está en el catálogo | Evidencia histórica principalmente de futuros tradicionales. Requiere una comprobación propia para cripto y para cada instrumento final. |
| Momentum transversal | Sí | En la shortlist; está en el catálogo | En futuros de cripto la evidencia directa es dependiente del horizonte y no equivale a la evidencia general de equities/futuros tradicionales. Un estudio encuentra basis más robusto que momentum y que varios premios pierden fuerza al alargar la tenencia. |
| Breakout / canales | Sí | No tiene ficha separada; queda como implementación de tendencia | El informe lo estudia como regla concreta de trend following, no como una familia alfa independiente. Conviene fijar ventanas y fills como variante de backtest. |
| Reversión a la media | Sí | Está en el catálogo; no quedó en la shortlist inicial | La evidencia depende mucho de mercado y horizonte. No extrapolar reversión en spot de commodities a sus futuros ni a perpetuos cripto. |
| Pares / arbitraje estadístico | Sí | Está en el catálogo; el informe evalúa spreads relacionados | Requiere justificar relación, cubrir las dos patas, y medir costes y riesgo de divergencia. |
| Carry y estructura temporal | Sí | En la shortlist; hay ficha genérica de carry | La ficha genérica no cubría explícitamente basis/funding de perpetuos cripto; añadí una ficha especializada para ese caso. |
| Carry de basis/funding de perpetuos cripto | La familia genérica estaba; este caso específico no | Añadido al catálogo, con prioridad de investigación, no aprobado | Literatura específica documenta basis/carry variable y compensación por riesgo. Deben separarse funding cobrado/pagado, financiación de spot, costes, margen y liquidación. |
| Calendar spreads | Sí | En la shortlist como alternativa; sin ficha propia | Solo es candidato si el producto final tiene vencimientos comparables y curva de precios. Un perpetuo aislado no ofrece por sí solo un calendar spread entre vencimientos. |
| Estacionalidad / event-driven | Sí | Analizada, no seleccionada; sin ficha de catálogo | El informe cubre evidencia en futuros de energía. No se convierte en señal hasta validar un calendario, instrumento y periodo sin sesgo retrospectivo. |
| Market making / microestructura | Sí | Analizada y pospuesta por necesidad de datos/infraestructura; market making sí está en el catálogo | Son hipótesis diferentes de VWAP/TWAP: requieren libro, trades, modelo de fill/cola y análisis de selección adversa. La evidencia predictiva no demuestra rentabilidad neta. |
| ML / combinaciones de señales | Sí | Está en el catálogo; pospuesta | No se considera fuente automática de ventaja. Controlar leakage, búsqueda múltiple, cambios de distribución y comparación con reglas simples. |
| VWAP / TWAP / POV | Sí | Está en el catálogo como ejecución, no como estrategia alfa seleccionada | Puede reducir coste de implementación; no se debe contar como señal direccional independiente. |
| Venta de volatilidad/opciones | Sí en el mapa inicial | En el catálogo, pero fuera del universo provisional conversado | No incluir mientras no se decida operar opciones. Requeriría ampliar el alcance y evaluar pérdidas de cola y margen. |

## Matiz específico para cripto

La literatura revisada sobre futuros perpetuos identifica basis y variables de precio/volumen como predictores, pero no autoriza a trasladar una regla de futuros tradicionales. Un estudio de factores en futuros cripto encuentra que el basis resulta más robusto que momentum en su muestra; los resultados cambian con horizonte y costes. El BIS describe el carry cripto como muy variable y relaciona niveles altos con riesgo de caídas y liquidaciones. Por eso el carry de perpetuos cripto queda como hipótesis que merece probarse, no como selección final ni como arbitraje garantizado.

La investigación tampoco convierte la evidencia general de acciones en evidencia para Stock Perps. Cuando se conozca el instrumento concreto habrá que verificar qué datos, costes y reglas permiten evaluarlo. La clasificación actual es de familias, no una validación por activo.

## Orden de candidatas que queda registrado

La shortlist previa sigue siendo una lista de hipótesis para comparar, no una decisión de operar:

1. Momentum temporal / trend following.
2. Momentum transversal.
3. Carry / estructura temporal; con una rama explícita de basis/funding para perpetuos cripto.
4. Calendar spreads o reversión de spreads, solo donde haya dos instrumentos/contratos comparables.

Reversión simple, estacionalidad, market making/microestructura y ML quedan documentados para evaluación posterior o bajo condiciones de datos. La venta de opciones queda fuera del alcance provisional. No se han corrido backtests propios en esta auditoría.

## Fuentes primarias añadidas o verificadas

- Schmeling, Schrimpf y Todorov, BIS Working Paper 1087, *Crypto carry* (2023): [BIS](https://www.bis.org/publications/working-paper-1087-crypto-carry).
- Chi et al., *An empirical investigation on risk factors in cryptocurrency futures*, *Journal of Futures Markets* (2023): [DOI](https://doi.org/10.1002/fut.22425).
- Cao, Zhai y Luo, *Anatomy of cryptocurrency perpetual futures returns*, *Journal of Futures Markets* (2024): [Universidad de Edimburgo](https://www.research.ed.ac.uk/en/publications/anatomy-of-cryptocurrency-perpetual-futures-returns/).
- Ewald et al., *Trading time seasonality in commodity futures* (2022): [repositorio de la Universidad de Glasgow](https://eprints.gla.ac.uk/281581/).
- Chaves y Viswanathan, *Momentum and mean-reversion in commodity spot and futures markets* (2016): [DOI](https://doi.org/10.1016/j.jcomm.2016.08.001).

