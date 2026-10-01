# Selección final de candidatas por Astra

**Priorizaría momentum temporal como primer test**, seguido de carry de materias primas, basis/funding cripto y momentum transversal. Es una selección de investigaciones: ninguna queda validada para operar. No es posible una decisión en vivo porque no están definidos los contratos ni los backtests aplicables.

La evaluación utiliza el informe aportado; no implica una nueva verificación independiente de sus fuentes. Ordeno cuatro candidatas y comparo las otras cuatro sin ampliar la lista priorizada.

**Criterios y pesos cualitativos**

Defino estos criterios antes de valorar las tarjetas:

| Criterio | Peso | Aplicación |
|---|---|---|
| Evidencia aplicable al producto y mecanismo | Muy alto | Favorecer estudios de la exposición pertinente; penalizar extrapolaciones desde acciones o spot. |
| Posibilidad de demostrar una ventaja neta | Muy alto | Costes, financiación, roll e impacto deben poder reconstruirse. La predictibilidad aislada aporta menos. |
| Estabilidad y pérdidas en estrés | Alto | Examinar cambios de régimen, drawdown, colas y liquidez. |
| Calidad del diseño histórico | Alto | Preferir evaluación cronológica fuera de muestra, sensibilidad y control de selección. |
| Datos e implementación reproducible | Alto | Favorecer hipótesis que puedan probarse de forma fiel y auditable. |
| Aporte al programa de investigación | Medio | Cubrir mecanismos y mercados distintos sin presumir diversificación efectiva. |

Las puntuaciones de las tarjetas son juicios iniciales, no mediciones. No las sumo ni utilizo como evidencia de rentabilidad. **Observaciones** son lo documentado en el informe; **evidencia histórica**, los estudios citados; **inferencias**, las prioridades propuestas aquí.

**Cuatro candidatas para backtests comparables**

| Prioridad | Candidata | Alcance de la prueba propuesta | Motivo principal |
|---|---|---|---|
| 1 — primer test | Momentum temporal | Derivados vinculados a renta variable y materias primas que finalmente se definan | Evidencia histórica relativamente próxima al alcance y una referencia sencilla para comparar otras señales. |
| 2 | Carry general, acotado a estructura temporal de materias primas | Contratos y curvas de vencimientos que puedan reconstruirse | Mecanismo económicamente definido y evidencia específica en futuros de materias primas. |
| 3 | Basis/funding en perpetuos cripto | Separar hipótesis de basis y financiación realizada | Evidencia pertinente a cripto, con mayores exigencias de datos y riesgos operativos. |
| 4 | Momentum transversal | Universo homogéneo de derivados definido previamente | Literatura amplia, pero transferencia al universo provisional y riesgo de crash más problemáticos. |

**1. Momentum temporal: primer test**

- **Evidencia y encaje.** Moskowitz, Ooi y Pedersen estudian futuros y forwards, incluidos índices de acciones y materias primas [1]. La reconstrucción histórica de Hurst et al. amplía la cobertura temporal [2]. Es el encaje más directo para una parte importante del alcance provisional; no acredita automáticamente cualquier derivado de renta variable ni cripto.
- **Evidencia en conflicto.** Chordia et al. encuentran poco apoyo en regresiones por activo dentro y fuera de muestra [3]. Esa discrepancia obliga a distinguir la contribución de la señal de la diversificación y de la transformación de exposiciones. La evidencia de Lempérière et al. sobre deterioro de tendencias cortas añade sensibilidad al horizonte, pero utiliza también series spot [4].
- **Bruto/neto.** El informe no permite reconstruir resultados netos uniformes ni drawdowns comparables. La amplitud bibliográfica justifica investigar; no demuestra una ventaja neta actual.
- **Régimen, drawdown y cola.** Los mercados laterales y cambios bruscos de tendencia pueden producir pérdidas repetidas. Deben evaluarse drawdowns prolongados, gaps y liquidez durante reversiones. No debe presuponerse protección en todas las crisis.
- **Implementación y costes.** La construcción de series continuas y el tratamiento del roll pueden alterar tanto la señal como el resultado. Incluir spread, comisiones, impacto, roll y financiación cuando corresponda, evitando contar dos veces componentes ya incorporados al precio.
- **Datos necesarios.** Precios por contrato, vencimientos, horarios, volumen y liquidez, ajustes documentados y costes históricos. En cripto, cualquier extensión necesitaría evidencia y datos propios.

**Por qué primero:** permite construir una referencia reproducible y comprobar una controversia empírica relevante antes de introducir modelos más complejos.

**2. Carry general: limitar la investigación inicial a materias primas**

- **Evidencia y encaje.** La tarjeta agrupa mecanismos diferentes. El carry de divisas documentado en [7] queda fuera del alcance provisional y no prueba carry de materias primas. El estudio multiactivo [8] aporta contexto; Fuertes et al. ofrecen evidencia más próxima sobre estructura temporal y momentum en futuros de materias primas [9].
- **Bruto/neto.** Los resultados históricos descritos no permiten reconstruir un coste integral ni pérdidas comparables. La pendiente de una curva no debe contabilizarse automáticamente como beneficio realizable.
- **Régimen, drawdown y cola.** Los cambios de inventarios, escasez, estacionalidad y shocks de oferta pueden transformar la relación entre vencimientos. Examinar pérdidas conjuntas, concentración y deterioro de liquidez en los tramos relevantes.
- **Implementación y costes.** Hay que fijar qué se mide como carry, cómo se separa del movimiento del precio y cómo se representa el cambio de vencimiento. Importan spreads entre contratos, impacto, roll y discontinuidades de datos.
- **Datos necesarios.** Curvas históricas por vencimiento, especificaciones, calendarios, precios sincronizados y liquidez por contrato. Un precio continuo aislado no permite reconstruir toda esta hipótesis.

**Por qué segundo:** ofrece un mecanismo distinto al seguimiento de tendencia y evidencia específica en una clase incluida en el alcance. Su lugar depende de disponer de curvas fiables; no implica asumir contratos disponibles.

**3. Basis/funding cripto: evidencia pertinente, prueba exigente**

- **Evidencia y encaje.** El BIS documenta carry variable y su relación con crashes futuros [14]. Cao et al. estudian retornos y predictores en perpetuos [15]; Chi et al. encuentran relevancia del basis frente a momentum [16]. Estas fuentes respaldan investigar el mecanismo, pero **un factor transversal de basis, el funding cobrado y una cobertura spot–derivado son hipótesis distintas**.
- **Bruto/neto.** Ninguna de esas descripciones acredita el beneficio neto de la variante concreta de la tarjeta. Una relación predictiva de basis tampoco demuestra que el carry pueda capturarse después de todos los costes.
- **Régimen, drawdown y cola.** El carry alto puede coincidir con mayor fragilidad. Deben examinarse inversión del funding, ampliación del basis, desajustes de cobertura y necesidades de garantías durante estrés. Neutralidad al delta no elimina liquidación, custodia, contraparte o iliquidez.
- **Implementación y costes.** Separar funding efectivamente realizado de estimaciones indicativas; incluir costes de ambas patas, financiación, rebalanceos, impacto y reglas de liquidación. Si una variante requiere spot, esa dependencia debe quedar explícita en su definición.
- **Datos necesarios.** Precios sincronizados, índices y precios de referencia pertinentes, historial de funding y sus reglas, costes, garantías, discontinuidades e incidencias. La frecuencia de observación debe permitir detectar episodios adversos que los cierres diarios ocultarían.

**Por qué tercero:** aporta cobertura específica de cripto y evidencia más pertinente que trasladar indiscriminadamente anomalías de acciones. La dificultad de reconstruir el resultado neto y las colas impide situarlo primero.

**4. Momentum transversal: condicionado a un universo adecuado**

- **Evidencia y encaje.** Jegadeesh y Titman documentan momentum en acciones individuales [5]. Eso no valida automáticamente un ranking de derivados vinculados a renta variable. Las señales entre futuros de materias primas de [9] aportan evidencia más próxima para ese segmento, aunque requieren su propia definición.
- **Conflicto y transferencia.** Daniel y Moskowitz documentan crashes de momentum [6]. Para cripto, Chi et al. debilitan la tesis de una prima de momentum independiente del basis en su muestra [16]. No puede tratarse como una anomalía universal.
- **Bruto/neto.** El informe no establece una estrategia neta comparable para el universo final. Rotación, concentración y composición histórica pueden cambiar sustancialmente el resultado.
- **Régimen, drawdown y cola.** Deben analizarse reversiones rápidas del liderazgo, concentración sectorial y pérdidas simultáneas. Un universo pequeño puede convertir el ranking en unas pocas exposiciones dominantes.
- **Implementación y costes.** Requiere comparabilidad entre instrumentos y precios observables en momentos compatibles. Incluir roll, financiación y costes específicos del producto; el préstamo de acciones solo corresponde si la implementación realmente lo necesita.
- **Datos necesarios.** Universo point-in-time, instrumentos desaparecidos, cambios de composición, precios y liquidez históricos, exposición subyacente y costes por instrumento.

**Por qué cuarto:** la literatura justifica mantenerlo en la primera ronda, pero su encaje depende más del universo elegido que el de momentum temporal.

**Comparación de las otras cuatro candidatas**

| Candidata | Evaluación independiente | Decisión de investigación |
|---|---|---|
| **Pares / arbitraje estadístico** | Gatev et al. aportan un backtest histórico en acciones con estimaciones de costes [12]. Do y Faff cuestionan la robustez neta frente a costes [13]. La transferencia a derivados exige relación económica, sincronización y estabilidad; no basta seleccionar pares que convergieron retrospectivamente. Las dos patas añaden costes y riesgo de ejecución; la convergencia puede tardar o desaparecer. | **Posponer como alternativa a la cuarta plaza.** Podría sustituir a momentum transversal si se identifica una relación económica verificable y datos sólidos de ambas patas. |
| **Reversión a la media** | Lo y MacKinlay rechazan determinadas hipótesis de paseo aleatorio, pero advierten que eso no demuestra reversión a la media [10]. El preprint cripto del informe encuentra una ventaja bruta inferior a su coste supuesto [11]; además, estudia spot y no está revisado por pares. Tendencias persistentes, gaps y selección adversa son riesgos centrales. | **Posponer.** Primero definir una anomalía, horizonte y referencia concretos. No llevar la familia genérica a una competición de parámetros. |
| **ML / ensemble** | Gu et al. sustentan investigación predictiva en acciones [17], no un ensemble neto validado para estos derivados. Bailey et al. es evidencia metodológica sobre sobreajuste, no evidencia de beneficio de ML [18]. La búsqueda múltiple, filtraciones y cambios de distribución pueden inflar resultados; los costes dependen de las señales resultantes. | **Posponer hasta disponer de referencias simples.** Evaluar entonces su contribución incremental fuera de muestra, registrando todos los ensayos. |
| **Market making** | La fuente de la tarjeta no acredita rentabilidad neta en el universo propuesto [19]. La evidencia sobre formación de precios dependiente del estado [20] no prueba spread capturado. Los límites estudiados para HFT agresivo [21] tampoco son una prueba directa de provisión pasiva. Dominan colas, fills parciales, selección adversa, inventario y liquidez en estrés. | **Excluir de esta primera comparación.** Necesita datos y un simulador de microestructura distintos; un backtest con velas no permitiría compararlo de forma creíble. |

**Cómo hacer comparable la primera ronda**

La comparación debe compartir criterios de evaluación, sin forzar reglas idénticas entre mecanismos:

1. **Definir previamente** universo, contratos, hipótesis, construcción de datos, reglas y costes. Registrar variantes investigadas.
2. **Separar selección y evaluación cronológicamente**, con pruebas fuera de muestra y walk-forward. Evitar ajustar la estrategia después de observar el tramo reservado.
3. **Presentar resultados brutos y netos**, sensibilidad a costes y contribución por instrumento y periodo. Comparar ventanas comunes y mostrar aparte la historia adicional disponible.
4. **Examinar riesgo comparable:** drawdown y duración, pérdidas de cola, concentración, rotación, liquidez y restricciones de garantías. No inferir viabilidad solo de una media favorable.
5. **Exigir revisión independiente del motor y los resultados.** Solo entonces aceptar las métricas como medidas del proyecto; las cifras bibliográficas siguen siendo antecedentes.

**Qué podría cambiar el orden**

- Curvas históricas incompletas harían descender carry de materias primas.
- Datos cripto completos de financiación, costes y estrés podrían elevar basis/funding; una ventaja que desaparezca neta lo relegaría.
- Un universo amplio y coherente de derivados podría fortalecer momentum transversal; uno reducido favorecería investigar pares concretos.
- Si momentum temporal pierde su ventaja después de costes o depende de pocas exposiciones, perdería el primer puesto.
- Pares desplazaría a la cuarta candidata si demuestra mejor transferencia y robustez neta. ML requeriría mejora incremental auditada; market making, una infraestructura de evaluación específica.

**Fuentes numeradas del informe**

[1] Moskowitz, Ooi y Pedersen, *Time Series Momentum*: https://doi.org/10.1016/j.jfineco.2011.11.003  
[2] Hurst, Ooi y Pedersen, *A Century of Evidence on Trend-Following Investing*: https://research.cbs.dk/en/publications/a-century-of-evidence-on-trend-following-investing/  
[3] Chordia, Goyal y Saretto, *Time series momentum: Is it there?*: https://doi.org/10.1016/j.jfineco.2019.08.004  
[4] Lempérière et al., evidencia histórica de tendencias: https://doi.org/10.48550/arXiv.1404.3274  
[5] Jegadeesh y Titman, *Returns to Buying Winners and Selling Losers*: https://doi.org/10.1111/j.1540-6261.1993.tb04702.x  
[6] Daniel y Moskowitz, *Momentum Crashes*: https://www.sciencedirect.com/science/article/pii/S0304405X16301490  
[7] *Carry Trades and Currency Crashes*: https://doi.org/10.1086/593088  
[8] Koijen et al., investigación sobre carry multiactivo: https://www.nber.org/papers/w19623  
[9] Fuertes, Miffre y Rallis, *Tactical allocation in commodity futures markets*: https://doi.org/10.1016/j.jbankfin.2010.04.009  
[10] Lo y MacKinlay, *Stock Market Prices Do Not Follow Random Walks*: https://web.mit.edu/Alo/www/Papers/lo-mackinlay-88.html  
[11] Preprint sobre reversión cripto citado en el informe: https://arxiv.org/abs/2608.21888  
[12] Gatev, Goetzmann y Rouwenhorst, investigación sobre pares: https://www.nber.org/papers/w7032  
[13] Do y Faff, *Are pairs trading profits robust to trading costs?*: https://doi.org/10.1111/j.1475-6803.2012.01317.x  
[14] Schmeling, Schrimpf y Todorov, *Crypto carry*: https://www.bis.org/publications/working-paper-1087-crypto-carry  
[15] Cao, Zhai y Luo, *Anatomy of Cryptocurrency Perpetual Futures Returns*: https://www.research.ed.ac.uk/en/publications/anatomy-of-cryptocurrency-perpetual-futures-returns/  
[16] Chi et al., *An empirical investigation on risk factors in cryptocurrency futures*: https://www.repository.cam.ac.uk/items/3a556482-574b-42cd-af07-fe5c9f9db91c  
[17] Gu, Kelly y Xiu, *Empirical Asset Pricing via Machine Learning*: https://doi.org/10.1093/rfs/hhaa009  
[18] Bailey et al., *The Probability of Backtest Overfitting*: https://escholarship.org/uc/item/4w1110bb  
[19] Fuente de la tarjeta de market making: https://doi.org/10.1145/3490354.3494398  
[20] *Order flow, dealer profitability, and price formation*: https://doi.org/10.1016/j.jfineco.2006.05.010  
[21] Kearns, Kulesza y Nevmyvaka, límites de HFT agresivo: https://www.cis.upenn.edu/~mkearns/papers/hft_arxiv.pdf
