# Selección de estrategias por Astra

{
  "status": "INSUFFICIENT_DATA",
  "market_snapshot_timestamp": null,
  "instrument": null,
  "contract": null,
  "timeframe": null,
  "regime": null,
  "selected_strategy": null,
  "direction": "NO_SIGNAL",
  "evidence_ids": [],
  "rationale": {
    "observations": [
      "Se aportan ocho tarjetas, notas de investigación y una auditoría de cobertura.",
      "No hay snapshot verificable, feed, contratos definidos ni backtests propios comparables validados por un revisor.",
      "La auditoría clasifica investigación; no valida rendimiento."
    ],
    "inferences": [
      "La primera prioridad investigadora es momentum temporal.",
      "La comparación inicial debe incluir momentum temporal, carry de futuros tradicionales, carry de basis/funding cripto y momentum transversal.",
      "Esta prioridad de investigación no constituye una selección operativa ni demuestra ventaja neta."
    ],
    "historical_evidence": [
      "Las referencias aportadas ofrecen respaldo histórico con distinto grado de correspondencia con el alcance provisional.",
      "Los resultados sobre acciones, divisas o futuros con vencimiento no se transfieren automáticamente a derivados de renta variable, materias primas o perpetuos cripto."
    ]
  },
  "key_risks": [
    "Transferencia inválida de evidencia entre instrumentos y horizontes.",
    "Costes, financiación y reglas contractuales todavía desconocidos.",
    "Sesgo de selección, sobreajuste y falta de validación cronológica propia.",
    "Pérdidas de cola, iliquidez y rupturas de régimen."
  ],
  "missing_data": [
    "Instrumentos, contratos y especificaciones aplicables.",
    "Horizontes y reglas de señal fijados antes de evaluar.",
    "Datos históricos verificables, costes y financiación.",
    "Resultados de un motor de backtesting y revisión independiente.",
    "Para una consulta operativa: snapshot con proveedor y timestamp, umbral de frescura y análisis actual de mercado."
  ],
  "next_validation": [
    "Priorizar momentum temporal como referencia inicial.",
    "Definir protocolos comparables para las cuatro candidatas de investigación.",
    "Validar datos y contratos antes de calcular resultados.",
    "Exigir evaluación neta fuera de muestra, pruebas de estrés y revisión independiente."
  ]
}

**Conclusión ejecutiva**

Mi primera prioridad es **momentum temporal / seguimiento de tendencia**: presenta la correspondencia más directa entre la literatura suministrada y futuros de índices y materias primas, además de una implementación investigadora relativamente sencilla. Su aplicación a cripto sigue siendo una hipótesis que necesita evidencia propia.

Selecciono cuatro candidatas para investigación: **momentum temporal, carry de futuros tradicionales, carry de basis/funding cripto y momentum transversal**. Son cuatro diseños de prueba que pertenecen a tres familias; las dos ramas de carry deben evaluarse separadamente.

No mantengo automáticamente la shortlist anterior: **pospongo pares y calendar spreads**, porque la evidencia aportada sobre pares procede principalmente de acciones y todavía no existen contratos definidos que permitan justificar spreads comparables. La pertinencia específica del carry cripto merece una prueba propia, aunque su riesgo y complejidad impiden situarlo primero.

`INSUFFICIENT_DATA` describe la falta de información para una decisión del bot; **no impide decidir qué investigar**. Tampoco corresponde declarar `NO_EDGE`: aún no se ha efectuado una prueba aplicable que permita concluir si existe ventaja.

Las referencias siguientes son las suministradas. Distingo sus resultados descritos en el material de mis inferencias; no he verificado aquí sus textos completos ni trato sus cifras como métricas propias validadas.

**Criterios de ranking**

La prioridad mide **valor de investigación**, no rentabilidad esperada ni seguridad.

| Criterio | Peso cualitativo | Aplicación |
|---|---|---|
| Calidad, replicabilidad y correspondencia de evidencia | Dominante | Priorizar reglas identificables, fuentes primarias y resultados sobre instrumentos próximos al alcance. |
| Robustez fuera de muestra y entre regímenes | Dominante | Una muestra histórica extensa no sustituye una prueba cronológica independiente. |
| Potencial neto y sensibilidad a costes | Alto | Exigir que el mecanismo sobreviva comisiones, spread, deslizamiento, financiación y tratamiento correcto de vencimientos. |
| Drawdown y cola | Alto | Examinar pérdidas concentradas, duración de recuperación, gaps e iliquidez; no equiparar baja volatilidad con bajo riesgo. |
| Encaje en los mercados provisionales | Alto | Valorar respaldo específico para cripto, derivados de renta variable y materias primas, sin extrapolaciones. |
| Datos e implementación | Alto en esta fase | Favorecer experimentos auditables con menos dependencias desconocidas. |

No sumo las puntuaciones de las tarjetas: son valoraciones ordinales sin calibración común. **La confianza indicada abajo se refiere al orden investigador**, no a la probabilidad de obtener beneficios.

**Ranking de las ocho tarjetas**

| Orden | Candidata | Evidencia y límites de aplicación | Confianza | Riesgos clave |
|---:|---|---|---|---|
| **1** | **Momentum temporal** | Moskowitz, Ooi y Pedersen estudian futuros de índices, materias primas y otras clases; Hurst y colaboradores amplían el contexto histórico. Es el respaldo más próximo al alcance tradicional. Estas fuentes no validan cripto. [T1–T2] | Alta | Lateralidad, cambios bruscos de tendencia, gaps, concentración entre mercados y drawdowns prolongados. |
| **2** | **Carry de futuros tradicionales** | *Carry* estudia varias clases, incluidas materias primas y acciones; la referencia de carry de divisas aporta contexto sobre riesgo, no una validación directa de los contratos objetivo. [C1–C2] | Media | Prima como compensación por riesgo, shocks de curva, financiación, colateral y concentración. |
| **3** | **Carry de basis/funding cripto** | Hay fuentes específicas sobre carry cripto y rendimientos de futuros/perpetuos. Su pertinencia es superior a una extrapolación desde divisas, pero predicción o basis elevado no demuestran beneficio neto realizable. [K1–K3] | Media | Reversión del funding, divergencia del basis, desajuste entre patas, liquidación, custodia y costes. |
| **4** | **Momentum transversal** | La referencia principal estudia acciones. Es respaldo para el mecanismo, no para derivados de índices o perpetuos vinculados a acciones. La auditoría describe evidencia cripto dependiente del horizonte y menos sólida que basis en una muestra. [X1, K2] | Media-baja | Crashes en rebotes, concentración, universo retrospectivo y rotación. |
| **5** | Pares / arbitraje estadístico | Las notas atribuyen a Gatev y colaboradores beneficios históricos después de una estimación de costes en acciones estadounidenses. Eso no valida spreads de futuros, cripto ni intradía; la segunda referencia exige revisar método y costes. [P1–P2] | Media | Ruptura de relación, convergencia lenta, selección retrospectiva y fricción de dos patas. |
| **6** | Reversión a la media | La referencia de 1988 no sustenta por sí sola la regla genérica intradía de la tarjeta. La fuente adicional sobre materias primas distingue spot y futuros: no autoriza transferir resultados entre ellos. [R1–R2] | Media | Confundir ruido con reversión, tendencias persistentes, gaps y absorción de la señal por costes. |
| **7** | ML / ensemble | La fuente suministrada respalda precauciones sobre sobreajuste; no acredita una estrategia ML rentable aplicable a estos mercados. [M1] | Alta para posponer | Fuga temporal, ensayos múltiples, cambios de distribución y dependencia de datos. |
| **8** | Market making | La referencia y las notas aportan contexto de microestructura; no se suministra una estrategia reproducida con rendimiento neto validado para contratos objetivo. [Q1] | Alta para posponer | Selección adversa, inventario, prioridad de cola, latencia y coste de infraestructura. |

Los puestos 2–4 son sensibles a la disponibilidad de datos. Un histórico fiable de funding puede elevar la prioridad práctica de carry cripto; curvas incompletas pueden retrasar carry tradicional. Eso modificaría la **viabilidad del experimento**, no demostraría mayor rendimiento.

**Las cuatro pruebas seleccionadas**

**1. Momentum temporal — primera prioridad**

- **Mecanismo:** investigar si la dirección de retornos pasados contiene persistencia posterior. Las reglas de ventanas, actualización y tratamiento de volatilidad deben quedar fijadas antes de evaluar.
- **Mercados y horizontes posibles:** futuros de índices y materias primas con evaluación diaria y señales de horizonte más lento; cripto como estudio separado. La evidencia tradicional procede de [T1–T2]; su traslado a cripto sería una inferencia.
- **Mercado y cola:** cambios repetidos de dirección pueden acumular pérdidas. Los gaps y las reversiones rápidas pueden producir pérdidas antes de que cambie la señal. La asociación histórica con algunos periodos extremos **no convierte la estrategia en cobertura garantizada**.
- **Ejecución y costes:** señales calculadas al cierre requieren precios posteriores utilizables en la simulación. Deben incluirse spread, deslizamiento, comisiones y transiciones de contratos. Menor frecuencia puede reducir fricción, pero es una expectativa de diseño, no un resultado.
- **Datos faltantes:** contratos individuales, calendario, vencimientos, liquidez histórica y metodología de series continuas. En cripto, también financiación y especificaciones del derivado.
- **Punto crítico:** separar resultados por clase; una cartera tradicional favorable no valida la rama cripto.

**2. Carry de futuros tradicionales**

- **Mecanismo:** investigar si el carry implícito contiene información sobre retornos posteriores. No confundir pendiente de curva con beneficio asegurado ni con una previsión infalible del precio.
- **Mercados y horizontes posibles:** materias primas y, condicionalmente, derivados de renta variable cuyo carry pueda definirse y observarse correctamente; señales semanales o mensuales con valoración diaria. [C2] ofrece contexto multiactivo, pero exige identificar la construcción aplicable a cada caso.
- **Mercado y cola:** en materias primas, almacenamiento, escasez, estacionalidad y entrega pueden alterar la curva. En renta variable, tipos y dividendos introducen determinantes distintos. Las exposiciones no deben tratarse como equivalentes.
- **Ejecución y costes:** vencimientos y liquidez pueden cambiar sustancialmente la fricción. El simulador debe distinguir rendimiento contractual, financiación, colateral y costes de transición, evitando contabilizar dos veces un supuesto “roll yield”.
- **Datos faltantes:** curvas históricas sincronizadas, contratos y calendarios, reglas de liquidación, referencias de financiación y, cuando corresponda, dividendos.
- **Punto crítico:** no utilizar la evidencia de carry de divisas [C1] como prueba suficiente para materias primas o renta variable.

**3. Carry de basis/funding cripto**

- **Mecanismo:** evaluar por separado la capacidad predictiva del basis y el resultado de una hipótesis cubierta que incorpore funding efectivamente realizado. **Basis y funding son variables relacionadas, pero no intercambiables.**
- **Mercados y horizontes posibles:** cripto, condicionado a que existan instrumentos compatibles y datos suficientes; valoración alineada con cada evento de financiación y análisis diario/semanal. No presupongo disponibilidad de productos.
- **Evidencia:** el BIS documenta carry variable y su relación con riesgo de caídas; los trabajos sobre factores y perpetuos aportan evidencia específica de esos mercados. Ninguno valida automáticamente la construcción concreta propuesta. [K1–K3]
- **Mercado y cola:** funding futuro incierto, ampliación del basis, divergencia entre referencias y pérdidas transitorias capaces de comprometer la continuidad de la hipótesis cubierta. Una exposición direccional reducida no elimina riesgo de liquidación o contraparte.
- **Ejecución y costes:** dos patas, sincronización, comisiones, spread, financiación del componente spot y rebalanceos. El funding anunciado o actual no puede sustituir al histórico efectivamente liquidado.
- **Datos faltantes:** precios de ambas patas, índices y precios de referencia, eventos de funding, reglas históricas de margen y liquidación, colateral e interrupciones.
- **Punto crítico:** si solo se dispone de velas y una tasa de funding actual, el experimento no es válido.

**4. Momentum transversal**

- **Mecanismo:** ordenar un universo contemporáneamente conocido por rendimiento pasado y evaluar persistencia relativa. Es distinto de momentum temporal: un “ganador” relativo puede estar cayendo.
- **Mercados y horizontes posibles:** universos separados de derivados de renta variable, materias primas o cripto; clasificación mensual y contraste de horizontes más largos. Son propuestas de investigación, no horizontes ya validados.
- **Evidencia:** [X1] respalda momentum en acciones, **no su traslado a derivados de índices ni a otros instrumentos vinculados a acciones**. [K2], según la auditoría, obliga a examinar dependencia del horizonte en cripto.
- **Mercado y cola:** rebotes abruptos, concentración sectorial o temática y cambios de correlación pueden deteriorar simultáneamente varias exposiciones relativas.
- **Ejecución y costes:** rotación, financiación y vencimientos dependen del instrumento. El préstamo de acciones citado en la tarjeta no debe imputarse automáticamente a un derivado.
- **Datos faltantes:** universo histórico con altas y bajas, contratos desaparecidos, liquidez conocida en cada fecha y reglas de clasificación.
- **Punto crítico:** un universo pequeño o reconstruido con supervivientes actuales puede hacer que la prueba resulte poco informativa.

**Familias y variantes pospuestas o excluidas**

| Familia o variante adicional | Decisión y motivo |
|---|---|
| Pares / reversión de spreads | Posponer hasta justificar la relación económica y contar con dos series compatibles. La evidencia de acciones [P1] no valida futuros ni cripto. |
| Calendar spreads | Condicional, sin prueba independiente inicial. Requiere vencimientos comparables y curvas; un perpetuo aislado no basta. No todos los calendar spreads son estrategias de carry. |
| Reversión simple | Posponer: faltan referencia, horizonte y mecanismo concretos. La amplitud de la tarjeta dificulta falsarla sin introducir muchas decisiones retrospectivas. |
| Breakout / canales | Considerar como variante posterior de tendencia, no como otra familia independiente. Cada variante contará como ensayo adicional. |
| Estacionalidad / eventos | Posponer. La fuente de futuros de materias primas merece revisión específica, pero no respalda cripto ni derivados de renta variable. Faltan calendario y regla definidos de antemano. [S1] |
| ML / ensemble | Posponer hasta disponer de baselines y datos auditados. Solo tendría prioridad si aporta mejora neta independiente que compense su complejidad. |
| Market making / microestructura | Posponer hasta disponer de libro, operaciones y un modelo verificable de cola y fills. Las velas no permiten una simulación suficiente. |
| Prima de volatilidad / opciones | Fuera de esta selección: el material la excluye del alcance provisional. No se incorpora por el mero hecho de que se hayan mencionado derivados. |
| VWAP / TWAP / POV | Excluir del ranking alfa. Es investigación de implementación, no evidencia de señal direccional. |

**Comprobaciones mínimas y condiciones de descarte o cambio**

1. **Reproducibilidad documental.** Identificar qué regla, muestra, instrumentos y tratamiento de costes sostiene cada referencia. Si una fuente es metodológica o estudia otro mercado, limitar su función a ese contexto.

2. **Datos y contratos.** Auditar timestamps, huecos, revisiones, vencimientos, financiación y universo histórico. Si no puede reconstruirse lo que era conocido en cada fecha, suspender la prueba afectada.

3. **Comparación justa.** Usar periodos comunes donde sea posible, reglas de riesgo comparables y una contabilidad uniforme. Mantener los costes y eventos específicos de cada contrato. Comparar primero dentro de cada clase, sin ocultar diferencias mediante agregación.

4. **Validación cronológica.** Separar desarrollo, validación y prueba final; realizar walk-forward sin reutilizar el tramo final para elegir parámetros. Registrar todas las variantes ensayadas, incluidos canales, ventanas y filtros.

5. **Resultados netos revisados.** El motor deberá entregar rendimiento bruto y neto separados, drawdown y duración, pérdidas extremas, rotación, exposición, costes y descomposición por mercado y régimen. **Solo aceptaré esas métricas tras la validación del revisor.**

6. **Estrés pertinente.** Examinar gaps, menor liquidez, mayores costes, retrasos y financiación adversa. Para carry cripto, añadir divergencia de referencias y eventos de margen; para curvas, dislocaciones entre vencimientos.

7. **Descarte o degradación de prioridad.** Retirar de la primera ronda cualquier hipótesis cuyo resultado dependa de costes omitidos, información futura, pocos episodios dominantes o parámetros muy estrechos. Si no supera una referencia sencilla fuera de muestra, no atribuirle una ventaja incremental.

8. **Cambio de ranking.** Elevar una candidata pospuesta únicamente con evidencia aplicable, datos reproducibles y mejora neta revisada. Fijar los umbrales de aceptación antes de observar la prueba final; todavía faltan objetivos y restricciones para concretarlos.

La ausencia de un snapshot no bloquea estas investigaciones históricas. Sí bloquea inferir el régimen actual, elegir una candidata operativa o emitir dirección.

**Fuentes suministradas**

- **[T1]** Moskowitz, Ooi y Pedersen, *Time Series Momentum*: [DOI](https://doi.org/10.1016/j.jfineco.2011.11.003).
- **[T2]** Hurst, Ooi y Pedersen, *A Century of Evidence on Trend-Following Investing*: [CBS](https://research.cbs.dk/en/publications/a-century-of-evidence-on-trend-following-investing/).
- **[C1]** Referencia de carry de divisas: [DOI](https://doi.org/10.1086/593088). **[C2]** *Carry*: [NBER](https://www.nber.org/papers/w19623).
- **[K1]** Schmeling, Schrimpf y Todorov, *Crypto carry*: [BIS](https://www.bis.org/publications/working-paper-1087-crypto-carry).
- **[K2]** Chi et al., *An empirical investigation on risk factors in cryptocurrency futures*: [DOI](https://doi.org/10.1002/fut.22425).
- **[K3]** Cao, Zhai y Luo, *Anatomy of cryptocurrency perpetual futures returns*: [Edimburgo](https://www.research.ed.ac.uk/en/publications/anatomy-of-cryptocurrency-perpetual-futures-returns/).
- **[X1]** Jegadeesh y Titman, momentum accionario: [DOI](https://doi.org/10.1111/j.1540-6261.1993.tb04702.x).
- **[P1]** Gatev, Goetzmann y Rouwenhorst, pares: [NBER](https://www.nber.org/papers/w7032). **[P2]** Referencia complementaria de pares: [DOI](https://doi.org/10.1111/j.1475-6803.2012.01317.x).
- **[R1]** Referencia de reversión de la tarjeta: [DOI](https://doi.org/10.1016/0304-405X(88)90021-9). **[R2]** Chaves y Viswanathan, momentum y reversión en materias primas: [DOI](https://doi.org/10.1016/j.jcomm.2016.08.001).
- **[M1]** Referencia metodológica sobre sobreajuste: [eScholarship](https://escholarship.org/uc/item/4w1110bb).
- **[Q1]** Referencia de market making: [DOI](https://doi.org/10.1145/3490354.3494398).
- **[S1]** Ewald et al., *Trading time seasonality in commodity futures*: [Glasgow](https://eprints.gla.ac.uk/281581/).
