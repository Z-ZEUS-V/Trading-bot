# Replanteamiento del bot con capital inicial de 50 USD

**Nota posterior del 6 de octubre de 2026:** el usuario permite considerar hasta 25x de nominal respecto al margen asignado en cruzado, con techo del 40 % de cuenta como margen, sujeto a elegibilidad y a un control de riesgo ligado al beneficio neto esperado. Consultar `docs/criterios-operativos-vigentes-2026-10-06.md`. La viabilidad del lote sigue calculándose desde el presupuesto de pérdida, costes y margen de cada operación; el apalancamiento disponible no obliga a utilizar toda la cuenta.

**Fecha:** 5 de octubre de 2026
**Estado:** nueva base de diseño e investigación; no autoriza operar ni cambia la configuración de Astra.

**Avance posterior:** ya se implementó y ejecutó un primer replay local H1/H2 con funding conciliado públicamente. Ver `docs/simulacion-local-estrategias-2026-10-05.md` para resultados y límites actuales; el texto siguiente conserva el replanteamiento inicial. Todas las llamadas a Astra quedan pausadas por indicación posterior del usuario.

## Contexto confirmado

- El capital inicial previsto para trading es **50 USD**. El usuario puede aumentarlo más adelante según los resultados.
- El presupuesto de operación/infraestructura va aparte del capital inicial de trading.
- Ninguna de las estrategias previamente seleccionadas tiene rentabilidad verificada para este proyecto, este mercado y Kraken. El ranking anterior determina qué investigar, no qué operar.
- Los costes de ejecución empeoran la viabilidad de las hipótesis actuales. El objetivo ya no es “elegir las mejores del ranking”, sino comprobar primero si existe una ventaja neta que pueda ejecutarse con el capital y las restricciones reales.
- Kraken Derivatives sigue siendo el venue previsto para la primera fase cripto. La clave privada aún no está autenticada; no se harán órdenes ni nuevas pruebas privadas mientras se espera a soporte.

## Implicación inicial de costes

La tabla publicada por Kraken para clientes del EEE muestra, en el tramo inicial, 0,0200 % maker y 0,0500 % taker sobre el valor nominal de cada ejecución. Un viaje redondo que cruza el libro al entrar y salir costaría por comisión aproximadamente **0,10 % del nominal**; dos fills maker, aproximadamente **0,04 %**, si ambos llegan a ejecutarse. [Comisiones Kraken Derivatives para el EEE](https://support.kraken.com/es/articles/fees-for-derivatives-trading-eea)

| Supuesto de tamaño | Comisión taker al entrar y salir | Porcentaje de 50 USD |
|---|---:|---:|
| 50 USD de nominal | 0,05 USD | 0,10 % |
| 100 USD de nominal | 0,10 USD | 0,20 % |
| 250 USD de nominal | 0,25 USD | 0,50 % |

Si se hiciera un viaje redondo diario de 50 USD nominal durante 30 días, las comisiones taker sumarían alrededor de 1,50 USD (3 % del capital inicial), antes de spread, slippage, funding, conversiones u otros costes. Es un ejemplo mecánico, no una predicción de frecuencia ni de resultados. El coste real depende del nominal, tipo de fill, contrato, volumen aplicable y tarifas vigentes.

Las comisiones se cobran sobre el nominal ejecutado y se debitan del saldo/cartera correspondiente; aunque el usuario reserve un presupuesto operativo aparte, las comisiones y demás fricciones deben aparecer restando del P&L del bot. No se debe aumentar el apalancamiento para compensar una ventaja pequeña: este escala el nominal, las comisiones y el riesgo de pérdida/liquidación.

El tamaño mínimo depende del contrato. Kraken publica para clientes del EEE, por ejemplo, un lote mínimo de 0,0001 BTC para PF_XBTUSD y 0,001 ETH para PF_ETHUSD; hay que actualizar y verificar esos valores antes de cada backtest o ejecución. [Especificaciones de contratos Kraken Derivatives EEE](https://support.kraken.com/es/articles/perpetual-contract-specifications-for-clients-in-the-eea)

Como comprobación puntual, el 5 de octubre de 2026 a las 20:37 UTC el endpoint público devolvió un mark de 85.793,80 USD para PF_XBTUSD y 2.713,84 USD para PF_ETHUSD. Aplicando los lotes mínimos publicados, el nominal mínimo aproximado era 8,58 USD en BTC y 2,71 USD en ETH. Esto indica que el tamaño mínimo por sí solo no impide abrir un nominal menor de 50 USD en esos dos contratos, sujeto a margen, elegibilidad, estado del mercado y demás límites de cuenta. Los precios cambian y no deben tratarse como cotización ejecutable. [Ticker público de Kraken Futures](https://futures.kraken.com/derivatives/api/v3/tickers)

La conclusión inicial es más matizada que “50 USD hacen inviables las comisiones”: con 50 USD de nominal, dos fills taker cuestan unos 0,05 USD (0,10 %); el problema económico debe medirse incluyendo spread, slippage, funding, selección adversa, riesgo por movimiento mínimo de precio y frecuencia. A una operación redonda taker al día durante 30 días, 1,50 USD equivale al 3 % de 50 USD antes de esas otras fricciones. El gate debe decidir por estrategia, contrato y ritmo de trading; no descartar o aprobar todo el proyecto solo por el capital inicial.

## Nuevo enfoque

### 1. Congelar la selección anterior como lista de hipótesis

No tratar la selección Astra `high` ni el encaje conceptual de funding/basis como evidencia de rentabilidad. El estudio posterior `docs/estudio-trading-algoritmico-2026-10-05.md` desarrolla los requisitos de cruzado, stop y objetivos sobre equity, y propone este orden de investigación:

- Ruptura/tendencia como H1 y momentum temporal diario como comparación H2, con reglas iniciales explícitas y sin rentabilidad presumida.
- Señales de funding/basis en una línea posterior separada, sin llamar “carry neutral” a una estrategia que aún no modela la pata spot y todos sus costes.

Cada hipótesis debe tener reglas de entrada, salida, sizing, no-trade y datos requeridos fijados antes de mirar el resultado OOS. Rechazarla si falla las pruebas; no optimizarla hasta que “parezca rentable”.

### 2. Añadir una puerta de viabilidad específica para 50 USD

Antes de desarrollar la ejecución, calcular para cada contrato candidato:

1. Cantidad mínima, nominal mínimo, margen y colchón disponible con equity de 50 USD, usando la especificación vigente de Kraken.
2. Comisión de entrada y salida bajo escenario taker y maker realista, incluidos fills parciales; no asumir que una orden maker va a llenar.
3. Spread, slippage, funding, conversiones e interés aplicables.
4. Riesgo en USD del stop, tamaño mínimo y pérdida de una liquidación/stop adverso.
5. Expectativa neta por operación y coste como fracción de equity, con escenarios pesimistas.

Si el mínimo de lote o las fricciones obligan a exceder el riesgo permitido, el resultado debe ser **NO TRADE para ese instrumento/capital**. La respuesta puede ser seguir investigando en simulación, probar otra estrategia/mercado compatible o esperar a que el capital crezca; el bot no debe “resolver” la incompatibilidad usando más apalancamiento.

### 3. Separar el laboratorio del bot que ejecutaría

- En fase de investigación, procesar velas, señales, coste, sizing y controles de forma determinista en Python.
- Usar Astra solo para tareas periódicas de investigación o revisión de evidencia con un paquete compacto; nunca llamar al LLM por tick y nunca dejarle fijar tamaño, apalancamiento, stops o validar órdenes.
- En producción futura, el programa local decide si las reglas aprobadas producen señal y si los controles permiten continuar. Si falta dato, falla un límite o el coste calculado elimina la ventaja, no enviar orden.
- No usar el API privado para este replanteamiento. La autenticación permanece pendiente del soporte y no se necesitan órdenes reales para construir el laboratorio.

### 4. Exigir evidencia antes de exponer capital

Un candidato solo pasa si mejora un benchmark simple después de comisiones, spread, slippage y funding; conserva resultado fuera de muestra y walk-forward; no depende de un único activo o episodio; tolera costes estresados; y tiene drawdown/colas compatibles con límites que el usuario defina. Guardar todas las variantes para controlar el sesgo por selección múltiple. Si ninguna pasa, el resultado correcto es no operar.

Primero hacer replay histórico y simulación/paper con precios ejecutables y modelo de fills. Solo después de probar el comportamiento y confirmar que una orden mínima cabe en el presupuesto de riesgo tendría sentido discutir operación real. El crecimiento del capital debe depender de resultados netos realizados y límites explícitos; no aumentar automáticamente el riesgo tras una racha positiva.

## Próximas tareas del proyecto

1. Revisar las especificaciones actuales y la comisión EEE del contrato candidato; representar lotes mínimos y nominales mínimos en los datos del backtest.
2. Incorporar la aclaración del usuario: margen cruzado, stop, beneficio objetivo 5–10 % de equity y riesgo planificado 2–4 %, hasta 5 %. Estudiar 2 % como base y escenarios 4/5 % por separado. Los límites diarios y de drawdown total siguen pendientes; un stop no garantiza el máximo realizado.
3. Implementar solo el simulador determinista y el modelo de costes, con `NO_TRADE` como salida válida.
4. Conciliar el nuevo funding de `data/market_data/funding_rates/20261005T204909Z/`: amplía cobertura observada hasta octubre de 2025, pero tiene ocho horas ausentes por activo y semántica pendiente. Evaluar H1/H2 primero y funding/basis después, sin rellenar ausencias ni ocultar operaciones con coste indeterminado.
5. Publicar los resultados negativos o inconclusos con la misma trazabilidad que los positivos. No ejecutar razonamiento `high` en una nueva fase de implementación sin confirmación explícita del usuario.

## Estado y límites

Este replanteamiento es un diseño de investigación, no asesoramiento personalizado ni una promesa de que 50 USD sean suficientes para obtener rentabilidad. Todavía no hay motor de backtest, estrategia validada, simulación de fills ni resultados OOS en el proyecto. La comisión ilustrativa usa la página EEE localizada en español, actualizada por Kraken el 17 de marzo de 2026; verificar de nuevo tarifas, especificaciones y elegibilidad antes de operar.
