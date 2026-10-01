# Reevaluación de estrategias por Astra (reasoning medium)

**Conclusión**

Priorizaría **momentum temporal**, **carry de curva en materias primas**, **basis/funding cripto** y **momentum transversal**, en ese orden. La primera candidata sería `time-series-momentum`, inicialmente en futuros tradicionales cuya disponibilidad se confirme: combina evidencia histórica próxima al alcance del proyecto con una implementación relativamente sencilla de auditar.

Este orden asigna recursos de **investigación y backtest**; no acredita rentabilidad ni autoriza operativa. El paquete no aporta resultados en vivo ni métricas netas homogéneas que permitan comparar directamente las ocho candidatas.

**Criterios**

- **Calidad y correspondencia:** evidencia sobre el mismo producto, mecanismo y horizonte; una prueba de predictibilidad no equivale a una estrategia ejecutable.
- **Robustez:** resultados fuera de muestra, entre periodos y regímenes, sensibilidad a parámetros y control de selección retrospectiva.
- **Resultado neto:** comisiones, spread, impacto, financiación y costes de mantenimiento o renovación de contratos. No tratar el retorno bruto como ventaja disponible.
- **Colas y liquidez:** pérdidas extremas, duración del drawdown, gaps, cambios de financiación y capacidad de mantener o cerrar las exposiciones.
- **Datos e implementación:** históricos reproducibles, universo disponible en cada fecha, contratos identificados y ejecución simulable.

Las puntuaciones del catálogo son orientativas; no sustituyen estos criterios. La confianza indicada abajo se refiere al **respaldo para investigar**, no a rentabilidad futura.

**Ranking completo**

| Orden | Candidata | Motivo | Evidencia / confianza | Riesgo principal |
|---|---|---|---|---|
| **1** | `time-series-momentum` | Correspondencia histórica con futuros de índices y materias primas; permite comenzar con reglas lentas y auditables. | Media-alta: [Moskowitz et al.](https://doi.org/10.1016/j.jfineco.2011.11.003), con contradicción material de [Chordia et al.](https://doi.org/10.1016/j.jfineco.2019.08.004). | Whipsaw y drawdowns prolongados; confundir diversificación o ajuste por volatilidad con efecto de la señal. |
| **2** | `carry` | Prioritaria únicamente como estructura temporal de futuros de materias primas, con definición concreta. | Media: evidencia histórica próxima en [Fuertes et al.](https://doi.org/10.1016/j.jbankfin.2010.04.009); costes integrales pendientes. | Shocks de curva y liquidez; señal contaminada por roll o estacionalidad. |
| **3** | `crypto-perp-basis-funding-carry` | Mayor correspondencia con cripto que extrapolar estudios de acciones; mecanismo medible por componentes. | Media: [BIS](https://www.bis.org/publications/working-paper-1087-crypto-carry) y [Cao et al.](https://www.research.ed.ac.uk/en/publications/anatomy-of-cryptocurrency-perpetual-futures-returns/), sin validación neta ejecutable. | Reversión del funding, ampliación del basis y liquidación pese a cobertura direccional. |
| **4** | `cross-sectional-momentum` | Evidencia histórica amplia; prioridad condicionada a disponer de un universo suficiente de derivados comparables. | Media, con correspondencia limitada: [Jegadeesh–Titman](https://doi.org/10.1111/j.1540-6261.1993.tb04702.x) estudia acciones individuales. | Crashes de momentum, sesgo de supervivencia y costes de rotación. |
| **5** | `pairs-stat-arb` | Hipótesis concreta y contrastable, pero necesita relaciones económicas estables y dos patas ejecutables. | Media-baja para este alcance: [Gatev et al.](https://www.nber.org/papers/w7032), con [contrapeso de costes](https://doi.org/10.1111/j.1475-6803.2012.01317.x). | Ruptura de la relación y convergencia lenta; ejecución incompleta. |
| **6** | `mean-reversion` | La ficha agrupa mecanismos demasiado distintos y carece de respaldo neto comparable. | Baja: [Lo–MacKinlay](https://web.mit.edu/Alo/www/Papers/lo-mackinlay-88.html) no demuestra una regla rentable de reversión. | Tendencias persistentes y costes superiores al efecto bruto. |
| **7** | `ml-signal-ensemble` | Conviene contar antes con datos auditados y referencias simples que superar. | Baja para el producto final: [Gu et al.](https://doi.org/10.1093/rfs/hhaa009) aporta evidencia en acciones, no validación general de derivados. | Sobreajuste, filtración de información y selección entre muchos ensayos. |
| **8** | `market-making` | La viabilidad depende especialmente de infraestructura y microestructura todavía desconocidas. | Baja: la [fuente del catálogo](https://doi.org/10.1145/3490354.3494398) no establece rentabilidad neta transferible. | Selección adversa, posición en cola e inventario durante estrés. |

**Cuatro prioridades para backtest**

**1. Momentum temporal — primera candidata.** Empezaría con pocas especificaciones de horizonte medio/largo, fijadas antes de evaluar. La [reconstrucción histórica de Hurst et al.](https://research.cbs.dk/en/publications/a-century-of-evidence-on-trend-following-investing/) amplía la cobertura temporal, pero no elimina el desacuerdo de Chordia et al.: evidencia de cartera y regresiones por activo no responden exactamente a la misma pregunta. El backtest debe distinguir la contribución de la señal, la diversificación y el ajuste por volatilidad.

Se necesitan precios por contrato, vencimientos, reglas de roll, horarios y cotizaciones para estimar costes. Una serie continua puede servir para construir señales, pero el beneficio debe reconstruirse con contratos negociables. Evaluaría gaps, periodos laterales y duración de drawdowns; la menor rotación esperada no garantiza costes bajos. La extensión a cripto requiere validación separada.

**2. Carry de materias primas.** Acotaría `carry` a una señal de curva definida por vencimientos comparables. La evidencia de [carry en divisas](https://doi.org/10.1086/593088) no valida este mecanismo, y los resultados históricos de Fuertes et al. no resuelven los costes actuales.

Faltan curvas históricas completas, liquidez por vencimiento, especificaciones de liquidación, calendario de entrega y tratamiento de estacionalidad. Deben evitarse vencimientos cuya ejecución no sea reproducible y la doble contabilización del carry: la señal derivada de la curva no constituye un ingreso adicional al resultado contractual. Importan spread, impacto y roll, junto con movimientos abruptos de curva y concentración sectorial. Probaría primero carry y tendencia por separado antes de estudiar su combinación.

**3. Basis/funding cripto.** Separaría dos hipótesis: rendimiento de una cobertura spot–perpetuo y predicción transversal mediante basis. Los resultados de factores no demuestran automáticamente rentabilidad de la primera. Tampoco el funding observado fija el ingreso futuro.

Se requieren precios sincronizados de ambas patas, funding efectivamente pagado y sus reglas, precio de referencia para margen, especificaciones contractuales, costes de custodia y financiación, y ejecuciones parciales. El resultado debe descomponerse en funding, variación del basis y todos los costes. Simularía financiación adversa, ampliación del basis, fallos de cobertura y exigencias de margen. El BIS encuentra que carry elevado anticipa crashes en su muestra: no cabe interpretarlo simplemente como mayor atractivo. La neutralidad direccional no elimina estos riesgos.

**4. Momentum transversal.** Mantendría esta prioridad condicionada al producto final. Un conjunto reducido de derivados sobre índices no reproduce una cartera de acciones ganadoras y perdedoras. Deben definirse universo, formación, mantenimiento y tratamiento de instrumentos desaparecidos antes de seleccionar parámetros.

Faltan disponibilidad histórica de contratos, retornos comparables y costes de cada exposición. El préstamo solo procede cuando la estructura concreta lo requiera; en otros derivados importarán financiación, dividendos implícitos o roll. Evaluaría especialmente recuperaciones bruscas tras caídas, por los [crashes documentados por Daniel–Moskowitz](https://www.sciencedirect.com/science/article/pii/S0304405X16301490). En cripto, [Chi et al.](https://www.repository.cam.ac.uk/items/3a556482-574b-42cd-af07-fe5c9f9db91c) debilita la prioridad de momentum frente a basis; no demuestra su fracaso universal.

Para comparar las cuatro usaría reglas de evaluación comunes: selección y prueba temporal separadas, registro de variantes ensayadas, costes base y estresados, drawdown y recuperación, pérdidas de cola y estabilidad por régimen. La comparación directa debe limitarse a periodos y productos compatibles, mostrando aparte la cobertura restante. La aplicación calculará estas métricas.

**Por qué posponer las demás**

- **Pares:** su evidencia histórica favorable neta depende de estimaciones de costes discutidas posteriormente. Sin pares económicamente justificables y datos sincronizados, la búsqueda retrospectiva puede dominar el resultado.
- **Reversión:** rechazar un paseo aleatorio no prueba reversión negociable. El [preprint cripto citado](https://arxiv.org/abs/2608.21888) encuentra un efecto bruto inferior al coste utilizado; además, estudia spot y no tiene revisión por pares.
- **ML:** es una metodología, todavía no una hipótesis económica delimitada. Exigiría superar referencias simples tras costes y corregir la búsqueda múltiple, como advierte [Bailey et al.](https://escholarship.org/uc/item/4w1110bb).
- **Market making:** barras y spreads cotizados no bastan para estimar ejecuciones. Sin eventos del libro, reglas de cola, latencia y costes efectivos, el backtest puede atribuir ingresos que no serían capturables.

**Qué evidencia cambiaría el orden**

- Momentum temporal bajaría si su resultado neto desaparece fuera de muestra o depende de una especificación estrecha.
- Carry de materias primas bajaría sin curvas y vencimientos líquidos utilizables; cripto subiría con resultados netos reproducibles que incluyan estrés de financiación y margen.
- Momentum transversal bajaría si el universo final carece de amplitud; pares podría sustituirlo con relaciones económicas estables y evidencia neta propia en ambos contratos.
- Reversión, ML o market making subirían con evidencia específica del producto, evaluación temporal independiente y costes de ejecución demostrables. Resultados en vivo auditables reforzarían esa evidencia, sin garantizar persistencia.
