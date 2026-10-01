# Mapa inicial de estrategias algorítmicas

Fecha de consulta: 30-09-2026. Este mapa sintetiza literatura y mecanismos conocidos; no es una clasificación de rentabilidad futura. Sin mercado, universo, frecuencia, capital, jurisdicción y costes concretos, no existe un ranking universal válido. Las puntuaciones de la biblioteca son ordinales (1 bajo–5 alto) y describen riesgos/operativa, no el retorno esperado.

## Lectura rápida

| Familia | Beneficio potencial bruto | Riesgo | Coste/infraestructura | Observación |
|---|---:|---:|---:|---|
| Momentum temporal / seguimiento de tendencia | Medio–alto, muy dependiente del régimen | Medio–alto | Bajo–medio | Diversificación de futuros históricamente importante; whipsaw y drawdowns prolongados |
| Momentum transversal | Medio–alto | Alto | Medio | Evidencia extensa en acciones; rotación, crowding y caídas bruscas |
| Reversión a la media | Bajo–medio | Medio–alto | Bajo–medio | Puede capturar rebotes pequeños; una ruptura estructural crea pérdidas grandes |
| Pares / arbitraje estadístico | Bajo–medio neto | Medio–alto | Medio | Relación puede romperse; costes consumen el margen |
| Carry (FX/futuros) | Medio | Alto | Medio | Prima históricamente observada, compensación por riesgo de cola y financiación |
| Market making | Bajo–medio por operación | Muy alto | Muy alto | Spread no es beneficio gratis: adverse selection, inventario, cola, latencia y tarifas |
| Prima de volatilidad / venta de opciones | Medio aparente | Muy alto | Alto | Ingresos frecuentes pequeños frente a pérdidas de cola; margen y gaps |
| Señales ML / ensemble | Desconocido; puede ser alto si existe señal real | Muy alto | Alto | Riesgo máximo de sobreajuste, fuga temporal y múltiples pruebas |
| Ejecución (VWAP/TWAP/POV) | No genera alpha direccional | Bajo–medio | Medio | Busca reducir coste de implementación; debe evaluarse contra benchmark |

## Estrategias y evidencia

### 1. Momentum temporal y seguimiento de tendencia
Regla típica: signo/ranking de retornos pasados por activo, con volatilidad objetivo y diversificación por clases. El estudio de Moskowitz, Ooi y Pedersen documenta momentum temporal en 58 futuros líquidos de índices, divisas, materias primas y bonos; el resultado de cartera diversificada se asocia a periodos extremos. Hurst, Ooi y Pedersen extienden la evidencia histórica de seguimiento de tendencia a múltiples mercados desde 1880. No implica que los parámetros publicados sigan funcionando tras costes actuales.

**Beneficio:** diversificación y potencial protección relativa en algunas crisis/tendencias. **Riesgos:** whipsaw en lateralidad, gaps, financiación/roll de futuros, retraso de señal, apalancamiento y drawdowns largos. Costes suelen ser moderados en horizontes diarios y activos líquidos.

### 2. Momentum transversal
Compra activos con mejor rendimiento relativo y vende/infra pondera los peores. La evidencia académica de momentum accionario es amplia; la implementación depende de universo, neutralización sectorial, turnover y préstamo de títulos. Puede sufrir crashes de momentum tras rebotes de mercado y crowding.

**Beneficio:** fuente potencial de retorno diversificada. **Riesgos:** cola negativa, cortos difíciles/caros, sesgo de supervivencia y rotación. Riesgo alto; exigir costes de borrow y disponibilidad histórica del universo.

### 3. Reversión a la media / reversión intradía
Compra caídas y vende subidas relativas a una referencia, spread o valor estimado. Puede funcionar en activos líquidos y horizontes cortos, pero la señal bruta suele ser pequeña y sensible a spread, latencia y selección adversa. Una tendencia nueva o noticia puede convertir el “barato” en una caída persistente.

**Beneficio:** frecuencia alta de aciertos no equivale a expectativa positiva. **Riesgos:** cola izquierda, stops/gaps, cambios estructurales y costes de ejecución. No optimizar umbrales con todo el histórico.

### 4. Pares y arbitraje estadístico
Opera el spread de dos activos relacionados (distancia, cointegración, copulas u otros modelos), apostando por convergencia. Gatev, Goetzmann y Rouwenhorst estudiaron pares en acciones estadounidenses de 1962–1997 y hallaron beneficios históricos reducidos pero positivos tras una estimación conservadora de costes. Estudios posteriores encuentran fuerte sensibilidad a costes y método de selección; los resultados no se transfieren automáticamente a cripto, intradía o activos actuales.

**Beneficio:** exposición direccional potencialmente menor. **Riesgos:** relación rota, hedge imperfecto, borrow, coste de dos piernas, selección retrospectiva y convergencia lenta. Riesgo medio–alto; exigir stops por ruptura de cointegración y límite de exposición.

### 5. Carry
Mantiene activos con carry/rendimiento implícito mayor, financiados por activos de menor carry. La evidencia en FX identifica primas medias, pero también asimetría negativa y crashes cuando se deshacen posiciones apalancadas. Trasladar el concepto a futuros requiere modelar curva, roll y colateral.

**Beneficio:** prima persistente en ciertos universos/regímenes. **Riesgos:** crash, liquidez, financiación, contraparte, cambios de tipos y concentración. Riesgo alto aunque la volatilidad histórica parezca contenida.

### 6. Market making / provisión de liquidez
Coloca órdenes límite para capturar spread y gestiona inventario. Trabajos de microestructura muestran que fills informados y prioridad de cola pueden dominar el spread capturado; investigación reciente evalúa controles de adverse selection. Requiere libro de órdenes, modelado de cola, cancelaciones y buena conectividad.

**Beneficio:** spread y rebates posibles. **Riesgos:** inventario, toxic flow, latencia, outages, tasas y capital. Alto coste de datos/infraestructura; no recomendación inicial para un bot retail.

### 7. Prima de volatilidad / estrategias de opciones
Vende volatilidad implícita frente a realizada o estructura exposición a volatilidad. El premio medio observado puede ser compensación por riesgo de crash, no arbitraje. Short puts/straddles pueden mostrar alta tasa de acierto y pérdidas catastróficas en gaps; margen, smile, asignación y griegas son centrales.

**Beneficio:** carry/premio potencial. **Riesgos:** cola extrema, convexidad negativa, volatilidad de volatilidad, liquidez y margen. Riesgo muy alto; modelar escenarios de gap, no solo VaR gaussiano.

### 8. ML y combinaciones de señales
Árboles, boosting, redes y modelos de régimen combinan características para clasificar o predecir. ML es una herramienta, no una fuente de alpha por sí sola. Bailey y López de Prado formalizan la probabilidad de sobreajuste del backtest; muchas configuraciones probadas inflan Sharpe y selección final.

**Beneficio:** puede modelar interacciones si hay señal estable. **Riesgos:** fuga temporal, cambios de distribución, selección múltiple, fragilidad y coste de datos/cómputo. Nivel de riesgo muy alto; comparar con baseline simple y contabilizar todos los ensayos.

### 9. Ejecución algorítmica (VWAP/TWAP/POV)
Divide una orden para reducir impacto o desviación frente a benchmark. No debe clasificarse como estrategia alfa: optimiza implementación y coste de transacción. Requiere benchmark correcto, liquidez y control de participación.

## Método de validación mínimo antes de llamar algo “rentable”

1. Hipótesis y universo fijados antes de mirar el test; incluir delistings y datos point-in-time.
2. Separación cronológica train/validation/test; walk-forward y, si hay etiquetas solapadas, purga/embargo.
3. Comisiones, spread, slippage, impacto, funding, borrow, roll, rebates, latencia y fills parciales modelados por régimen.
4. Benchmark buy-and-hold / cash / factor apropiado; métricas netas, Sharpe/Sortino, max drawdown, Calmar, turnover, skew, pérdida de cola, exposición y estabilidad por subperiodo.
5. Registrar toda prueba y parámetros; corregir múltiples ensayos o estimar Probability of Backtest Overfitting / Deflated Sharpe.
6. Paper trading y límites de pérdida/posición antes de cualquier despliegue; supervisión humana continua.

## Fuentes seleccionadas

- Moskowitz, Ooi & Pedersen (2012), “Time series momentum”, *Journal of Financial Economics*. [Artículo](https://doi.org/10.1016/j.jfineco.2011.11.003)
- Hurst, Ooi & Pedersen (2017), “A Century of Evidence on Trend-Following Investing”. [CBS Research Portal](https://research.cbs.dk/en/publications/a-century-of-evidence-on-trend-following-investing/)
- Gatev, Goetzmann & Rouwenhorst, “Pairs Trading: Performance of a Relative-Value Arbitrage Rule”. [NBER Working Paper 7032](https://www.nber.org/papers/w7032)
- Do & Faff (2012), “Are Pairs Trading Profits Robust to Trading Costs?”. [Journal of Financial Research](https://doi.org/10.1111/j.1475-6803.2012.01317.x)
- Brunnermeier, Nagel & Pedersen (2009), “Carry Trades and Currency Crashes”. [Journal of Finance / DOI](https://doi.org/10.1111/j.1540-6261.2008.01458.x)
- Bailey et al. (2017), “The Probability of Backtest Overfitting”. [UC eScholarship](https://escholarship.org/uc/item/4w1110bb)
- Cartea, Jaimungal & Ricci (2022), adverse selection control in algorithmic market making. [ACM DOI](https://doi.org/10.1145/3490354.3494398)
- Carr & Wu (2009), “Variance Risk Premiums”. [Review of Financial Studies / DOI](https://doi.org/10.1093/rfs/hhn038)
- OpenAI Agents SDK and cost controls: [Agents SDK](https://developers.openai.com/api/docs/guides/agents/sdk), [Batch API](https://developers.openai.com/api/docs/guides/batch), [Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching).
