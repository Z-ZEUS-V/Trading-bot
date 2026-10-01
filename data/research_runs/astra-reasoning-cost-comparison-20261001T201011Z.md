# Comparación de coste: Astra medium frente a high

**Fecha UTC:** 20261001T201011Z
**Modelo:** GPT-6 Astra (`agent_0c6cf59a3e95405b8c5cf839a3ab36720b7fdf0c528748e6ba`)
**Agente persistente:** permanece en `medium`; `high` se aplicó solo a esta sesión.
**Método:** mismo prompt, ocho fichas y mismo informe de evidencia; sin búsqueda web durante las ejecuciones. Se hizo primero medium y después high.
## Resumen de uso y coste

| Métrica | Medium | High | Diferencia high − medium |
|---|---:|---:|---:|
| Tokens de entrada | 13,848 | 13,848 | +0 |
| Entrada en caché | 0 | 0 | +0 |
| Tokens de salida (incluye razonamiento) | 2,185 | 3,076 | +891 |
| De salida: razonamiento | 105 | 1,034 | +929 |
| Total de tokens | 16,033 | 16,924 | +891 |
| **Coste estimado USD** | **$0.247730** | **$0.292280** | **$+0.044550 (+18.0%)** |

### Cálculo

`((entrada total − entrada cacheada) × $10 + entrada cacheada × $1 + salida × $50) / 1.000.000`. La salida incluye los tokens de razonamiento. Tarifas estándar publicadas para Astra: entrada $10/M, entrada cacheada $1/M y salida $50/M. No hay recargo separado por seleccionar `high`; el coste varía según tokens facturados. Ver [precios oficiales de GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra).

## Comparación analítica

### Medium — extracto del ranking

prioriza **correspondencia de evidencia, viabilidad de validación y riesgos económicos**, no una rentabilidad esperada cuantificada. El paquete no permite comparar ventajas netas ni drawdowns bajo condiciones homogéneas. Las puntuaciones de las fichas son orientativas: no sustituyen evidencia. Ninguna candidata queda aprobada para operar.

### Ranking de las ocho candidatas

| Puesto | Candidata | Evidencia y correspondencia | Riesgos decisivos y viabilidad |
|---|---|---|---|
| **1** | **Momentum temporal — seleccionada** | Evidencia histórica directamente relacionada con futuros tradicionales, incluidos índices y materias primas: [Moskowitz et al.](https://doi.org/10.1016/j.jfineco.2011.11.003) y [Hurst et al.](https://research.cbs.dk/en/publications/a-century-of-evidence-on-trend-following-investing/). La amplitud temporal favorece investigarla, pero no equivale a validación prospectiva. [Chordia et al.](https://doi.org/10.1016/j.jfineco.2019.08.004) cuestiona la señal por activo dentro y fuera de muestra. | Whipsaw, drawdowns prolongados, gaps y roll. Requiere contratos históricos, tratamiento reproducible de vencimientos y ejecución sobre precios negociables. Los horizontes más lentos ofrecen, como **inferencia**, menor presión de rotación. No trasladar beneficios de una cartera diversificada a un solo instrumento ni a perpetuos cripto. |
| **2** | **Carry — seleccionada, acotada a materias primas** | [Fuertes et al.](https://doi.org/10.1016/j.jbankfin.2010.04.009) aporta evidencia específica sobre estructura temporal en futuros de materias primas. [Koijen et al.](https://www.nber.org/papers/w19623) respalda investigar carry entre activos, pero no una regla universal. La evidencia de crashes en FX no valida ni caracteriza por completo esta variante. | Exposición a shocks económicos y de liquidez; roll e impacto pueden absorber el resultado. Exige curvas históricas, vencimientos comparables y liquidez por contrato. Las alfas históricas citadas no permiten reconstruir rendimiento neto o drawdown uniforme. No se presupone disponibilidad de varios vencimientos. |
| **3** | **Basis/funding en perpetuos cripto — seleccionada** | Es la evidencia más próxima a la parte cripto del universo: [BIS, *Crypto carry*](https://www.bis.org/publications/working-paper-1087-crypto-carry), [Cao et al.](https://www.research.ed.ac.uk/en/publications/anatomy-of-cryptocurrency-perpetual-futures-returns/) y [Chi et al.](https://www.repository.cam.ac.uk/items/3a556482-574b-42cd-af07-fe5c9f9db91c). **La evidencia sobre factores de basis no demuestra por sí misma rentabilidad neta de una cobertura spot–perpetuo.** | Funding reversible, ampliación del basis, margen, liquidación, desajustes entre patas y custodia. Necesita funding realizado, precios sincronizados, costes de ambas patas y reglas de margen. La liquidez debe existir simultáneamente en ambas. BIS vincula carry alto con crashes: delta neutral no elimina las colas. |
| **4** | **Momentum transversal — seleccionada condicionalmente** | [Jegadeesh–Titman](https://doi.org/10.1111/j.1540-6261.1993.tb04702.x) ofrece evidencia histórica clara en acciones individuales. Su correspondencia con derivados aún desconocidos es limitada. En perpetuos, Chi et al. debilita la justificación de momentum independiente de basis. | [Crashes documentados](https://www.sciencedirect.com/science/article/pii/S0304405X16301490), rotación y concentración de exposiciones. Necesita universo *point-in-time*, activos desaparecidos y cortos viables, con préstamo o financiación según el producto. Los perdedores pueden ser precisamente los instrumentos menos líquidos. |
| **5** | **Pares / arbitraje estadístico** | [Gatev et al.](https://www.nber.org/papers/w7032) reporta beneficios históricos superiores a estimaciones de costes en acciones; [Do–Faff](https://doi.org/10.1111/j.1475-6803.2012.01317.x) muestra sensibilidad del neto a costes. Es evidencia más concreta de estrategia que la reversión genérica, pero no valida pares de derivados. | Ruptura de relación, selección retrospectiva, convergencia lenta y ejecución de dos patas. Neutralidad aparente puede ocultar riesgo económico. Queda detrás del cuarto puesto por la combinación de transferencia incierta, costes y complejidad de ejecución. |
| **6** | **Reversión a la media** | La referencia principal, [Lo–MacKinlay](https://web.mit.edu/Alo/www/Papers/lo-mackinlay-88.html), **no demuestra reversión a la media negociable**. El [preprint cripto de 2026](https://arxiv.org/abs/2608.21888) reporta una ventaja bruta inferior al coste round-trip utilizado en su protocolo; no valida derivados. | Falta definir referencia, horizonte y mecanismo. Tendencias persistentes, gaps y selección adversa pueden dominar. Implementación relativamente accesible, pero las variantes rápidas necesitan datos y ejecución mucho más exigentes. |
| **7** | **ML / ensemble** | [Gu–Kelly–Xiu](https://doi.org/10.1093/rfs/hhaa009) aporta evidencia predictiva fuera de muestra en acciones. ML es una metodología, todavía no una hipótesis económica concreta para estos productos. [Bailey et al.](https://escholarship.org/uc/item/4w1110bb) fundamenta el riesgo de selección entre ensayos. | Leakage, sobreajuste, cambios de distribución y costes inducidos por rotación. Requiere datos versionados y registro de todos los experimentos. Su complejidad solo se justifica si mejora el resultado neto fuera de muestra frente a reglas simples. |
| **8** | **Market making** | La [referencia de la ficha](https://doi.org/10.1145/3490354.3494398) no acredita una estrategia neta transferible. Estudios de microestructura o HFT agresivo no validan captura pasiva de spread. | Máxima dependencia de libro, prioridad de cola, latencia, fees y fills. Selección adversa, inventario y retirada de liquidez dominan en estrés. Sin datos de eventos y simulación de ejecución creíble, un backtest con barras no resolvería la hipótesis. |

### Diseño de la primera ronda

Las cuatro seleccionadas deben convertirse en reglas concretas cuando se definan productos y datos:

1. **Momentum temporal:** probar una especificación parsimoniosa de horizonte medio/largo; separar el efecto de la señal del escalado por volatilidad y la diversificación.
2. **Carry de materias primas:** definir la medida de curva y el roll; evaluar inicialmente carry por separado de momentum para identificar su aportación.
3. **Carry cripto:** separar señal de basis, flujos de funding realizado y resultado de la cobertura. No asumir que el funding observado persistirá ni que un perpetuo convergerá como un futuro con vencimiento.
4. **Momentum transversal:** definir un universo elegible conocido en cada fecha y comprobar exposición residual a mercado, sectores o basis, según corresponda. Sin una sección transversal viable, esta candidata no pasa a implementación.

**Comparables significa compartir protocolo, no imponer idénticos instrumentos u horizontes.** Usaría selección temporal separada de evaluación, ventanas fuera de muestra, parámetros fijados antes del test y registro de variantes ensayadas. Compararía periodos coincidentes cuando existan y mostraría aparte el historial adicional.

La evaluación debe presentar resultado **bruto y neto**, rotación, sensibilidad a costes e impacto, drawdown y duración de recuperación, pérdidas de cola y liquidez en estrés. Fees, spread, financiación, préstamo, funding y roll se contabilizan donde correspondan, evitando duplicidades. La robustez exige estabilidad entre ventanas y regímenes definidos previamente; un buen agregado histórico no basta.

### Qué cambiaría el ranking

- **Momentum temporal bajaría** si la señal no aporta fuera de muestra frente a controles de exposición y escalado, o si el neto depende de pocos episodios o elecciones de parámetros.
- **Carry tradicional o cripto subirían** con evidencia reproducible neta en los contratos elegidos, estable entre regímenes y resistente a costes, iliquidez y tensiones de margen. Caerían si el rendimiento medio oculta pérdidas extremas o financiación inviable.
- **Momentum transversal perdería su plaza frente a pares** si falta un universo adecuado y, en cambio, aparecen pares con fundamento económico, relación estable fuera de muestra y convergencia rentable tras ambas ejecuciones.
- **Reversión, ML o market making subirían** únicamente con evidencia que resuelva su carencia específica: reversión neta negociable; mejora incremental de ML con control de múltiples ensayos; o fills y selección adversa reproducidos con datos de libro.

Esta es una selección de investigación basada en las referencias suministradas. **No hay validación propia ni resultados en vivo acreditados para el producto final.**

### High — extracto del ranking

prioriza correspondencia de evidencia, posibilidad de validación y riesgos de implementación. **No ordena rentabilidades netas demostradas:** el paquete no permite comparar rendimiento, drawdown o pérdidas de cola con una metodología común. Las puntuaciones de las fichas son orientativas, no estimaciones cuantitativas de ventaja.

| Puesto | Candidata | Evidencia y correspondencia | Riesgos decisivos, costes y viabilidad |
|---|---|---|---|
| **1** | **Momentum temporal** | [Moskowitz et al.](https://doi.org/10.1016/j.jfineco.2011.11.003) aporta evidencia histórica directamente pertinente para futuros tradicionales. La reconstrucción de largo plazo amplía cobertura de regímenes, pero no equivale a validación independiente fuera de muestra. [Chordia et al.](https://doi.org/10.1016/j.jfineco.2019.08.004) cuestiona el efecto, incluso fuera de muestra, bajo otra especificación. | Primera opción por correspondencia y relativa sencillez. Preferiría investigar inicialmente horizontes medios/largos; es una elección de investigación, no una superioridad neta demostrada. Whipsaw, drawdowns prolongados, gaps y roll siguen siendo materiales. Requiere precios negociables, tratamiento correcto de vencimientos y costes; la evidencia no se transfiere automáticamente a cripto. |
| **2** | **Carry general, acotado a curva de futuros de materias primas** | [Fuertes et al.](https://doi.org/10.1016/j.jbankfin.2010.04.009) estudia estructura temporal y momentum en futuros de materias primas. Es correspondencia más directa con el universo provisional que extrapolar carry de FX. Los resultados históricos citados no permiten reconstruir rendimiento neto y drawdown comparables. | Investigar una definición concreta de curva, evitando agrupar funding, tipos y dividendos como una misma señal. Riesgos de cambios de curva, shocks de liquidez y pérdidas en estrés. Necesita varios vencimientos, precios sincronizados y costes de roll; la liquidez del contrato cercano no garantiza la de los restantes. |
| **3** | **Basis/funding en perpetuos cripto** | El [working paper del BIS](https://www.bis.org/publications/working-paper-1087-crypto-carry) y [Cao et al.](https://www.research.ed.ac.uk/en/publications/anatomy-of-cryptocurrency-perpetual-futures-returns/) ofrecen correspondencia específica con cripto y perpetuos. Sin embargo, evidencia sobre factores de retornos o carry no demuestra rentabilidad neta de una cobertura spot/perpetuo concreta. | Su correspondencia justifica investigarlo, pero costes y colas limitan su posición. Funding variable, ampliación de basis, rebalanceos, margen, liquidación y custodia pueden dominar el resultado. El crash del subyacente no equivale automáticamente a pérdida de la cobertura; deben modelarse sus flujos y desajustes. Exige históricos de ambas patas y funding efectivamente liquidado. |
| **4** | **Momentum transversal** | [Jegadeesh y Titman](https://doi.org/10.1111/j.1540-6261.1993.tb04702.x) respalda la familia en acciones individuales. Esa evidencia no valida cualquier derivado sobre renta variable. [Daniel y Moskowitz](https://www.sciencedirect.com/science/article/pii/S0304405X16301490) documenta crashes; Chi et al., según el informe, debilita la extrapolación del momentum a cripto al controlar por basis. | Merece una prueba por su evidencia histórica, condicionada a disponer de un universo pertinente. Rotación, liquidez de perdedores, préstamo cuando corresponda y rebotes violentos pueden deteriorar el resultado neto. Requiere universo *point-in-time*, bajas de activos y costes de exposición corta específicos del producto. |
| **5** | **Pares / arbitraje estadístico** | [Gatev et al.](https://www.nber.org/papers/w7032) aporta backtests en acciones con beneficios superiores a costes estimados; [Do y Faff](https://doi.org/10.1111/j.1475-6803.2012.01317.x) cuestiona su robustez tras costes. Es evidencia neta bajo supuestos particulares, no un neto transferible al producto final. | Queda cerca del cuarto puesto, pero la selección de pares, estabilidad de la relación y ejecución de dos patas añaden incertidumbre. Convergencia lenta y ruptura estructural pueden generar pérdidas persistentes. La liquidez debe existir simultáneamente en ambas patas; una relación estadística retrospectiva no basta. |
| **6** | **Reversión a la media** | [Lo y MacKinlay](https://web.mit.edu/Alo/www/Papers/lo-mackinlay-88.html) no valida una estrategia de reversión: rechazar paseo aleatorio no demuestra ese mecanismo. El preprint cripto citado encuentra una ventaja **bruta inferior al coste** de su protocolo; no valida derivados. | Puede servir como hipótesis sencilla y falsable, pero falta respaldo neto para una regla concreta. Spread, selección adversa y slippage pesan especialmente en señales rápidas. Tendencias persistentes, gaps y cambios de régimen cuestionan la referencia de equilibrio. Deben definirse horizonte, referencia y salida antes de probarla. |
| **7** | **ML / ensemble** | [Gu et al.](https://doi.org/10.1093/rfs/hhaa009) aporta evidencia predictiva y evaluación fuera de muestra en acciones estadounidenses; no valida esta familia en los derivados previstos. [Bailey et al.](https://escholarship.org/uc/item/4w1110bb) aporta metodología sobre sobreajuste, no evidencia de rentabilidad. | Lo pospondría hasta disponer de baselines reproducibles. Alto coste de datos, búsqueda y mantenimiento; riesgo de leakage, múltiples ensayos y cambio de distribución. Una mejora predictiva puede concentrarse en activos ilíquidos o desaparecer con rotación y costes. Las colas dependen de las exposiciones aprendidas y aún no están caracterizadas. |
| **8** | **Market making** | Las referencias aportadas estudian microestructura y límites de ejecución; no acreditan beneficio neto de una implementación pasiva comparable. Los resultados de HFT agresivo tampoco validan provisión de liquidez. | Máxima dependencia del mercado y de infraestructura aún desconocidos. Requiere libro de órdenes, prioridad de cola, latencia, fills parciales y tarifas. Selección adversa e inventario durante retiradas de liquidez pueden superar el spread obtenido. Un backtest con barras no resuelve estas incertidumbres. |

**Las cuatro hipótesis seleccionadas deben concretarse así:**

1. **`time-series-momentum`:** comprobar si una regla temporal parsimoniosa conserva ventaja neta fuera de muestra. Separar la aportación de la señal de la diversificación y del escalado por volatilidad.
2. **`carry`:** comprobar una señal explícita de estructura temporal en materias primas, condicionada a disponer de vencimientos comparables. Evaluarla por separado antes de combinarla con momentum.
3. **`crypto-perp-basis-funding-carry`:** reconstruir el resultado de la cobertura completa: variación de ambas patas, funding, financiación, comisiones y rebalanceos. El funding futuro no puede introducirse como información conocida al decidir.
4. **`cross-sectional-momentum`:** probar una regla de ranking predefinida sobre un universo disponible en cada fecha, contabilizando desapariciones, rotación y viabilidad de exposición corta.

Para hacerlos **comparables**, usaría separación temporal entre desarrollo y evaluación final, registro de todos los ensayos y reglas congeladas antes del test. Compararía periodos y presupuestos de riesgo de investigación homogéneos cuando los datos lo permitan, sin forzar instrumentos u horizontes incompatibles.

El informe de cada backtest debe separar **bruto y neto**, desglosar costes y presentar drawdown máximo y duración, pérdidas de cola, rotación, sensibilidad a liquidez y resultados por régimen. Incluiría costes y financiación adversos, discontinuidades y restricciones de ejecución. Ninguna fuente del paquete demuestra rendimiento en vivo del producto final.

**La evidencia que cambiaría el orden sería:**

- **Producto y datos disponibles:** futuros tradicionales líquidos favorecen las dos primeras; un universo exclusivamente cripto podría elevar basis/funding. Derivados sobre acciones no bastan, por sí solos, para sostener momentum transversal o pares.
- **Validación neta reciente:** momentum temporal perdería prioridad si su aportación desaparece frente a baselines comparables o fuera de muestra. Pares podría desplazar a momentum transversal con una relación económicamente defendible, selección prospectiva y costes verificables de ambas patas.
- **Colas y ejecución:** carry descendería si margen, financiación o pérdidas de estrés anulan su ventaja. Reversión, ML o market making subirían únicamente con evidencia específica reproducible: reversión neta de costes, mejora incremental de ML tras controlar ensayos, o ejecución de market making validada con colas y selección adversa.

Los puestos **2–5 son especialmente sensibles al producto final**. La selección actual autoriza priorizar investigación; no establece que ninguna candidata tenga ya una ventaja neta validada.

## Límites de esta medición

- El uso que reporta Agents API es best-effort; los costes son estimaciones calculadas sobre ese uso y las tarifas estándar publicadas, antes de ajustes de cuenta, impuestos o créditos. No se aplicaron descuentos de caché de escritura ni tarifas de servicio especial porque el registro de usage no desglosó esos componentes.
- El caché puede hacer que el coste de entrada cambie entre ejecuciones aunque el prompt sea idéntico; se reflejan los tokens cacheados medidos.
- La comparación contiene una ejecución por nivel; no mide variabilidad entre repeticiones ni prueba que cualquier diferencia del ranking venga solo del esfuerzo.
- La primera reevaluación de las 19:53 UTC no guardó usage. Para esta comparación recuperamos el usage y la respuesta de la sesión medium repetida durante este turno (sesión `sess_0915b8b209873f86006abebcf1d4f481999a7587de488af06c`) y la comparamos con high usando exactamente el mismo prompt y paquete.
- Los informes completos se guardan junto a este archivo como `...-medium.md` y `...-high.md`; los contadores brutos están en `astra-reasoning-cost-comparison-20261001T201011Z.json`.
