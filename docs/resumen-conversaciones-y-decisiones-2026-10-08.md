# Resumen de conversaciones y decisiones del proyecto

**Actualizado el 8 de octubre de 2026.** Este documento recoge las decisiones de trabajo acordadas en las conversaciones sobre el bot. Es un resumen, no una transcripción. No contiene claves de API, contraseñas ni códigos de autenticación.

## Objetivo y límites

- Investigar un bot algorítmico para futuros de Kraken, inicialmente con 40–50 € de capital y unos 25 € reservados para posibles costes de API. La reserva no equivale a gasto realizado.
- Evaluar operaciones intradía de hasta cuatro horas. Se plantearon objetivos de 0,5–1,5 % neto por operación sobre toda la cuenta y escenarios de pérdida de 1–3 %; son hipótesis de investigación, no resultados conseguidos ni límites garantizados por un stop.
- Incluir comisiones, deslizamiento, financiación, tamaño mínimo, calidad de ejecución y costes de IA antes de juzgar la rentabilidad. El apalancamiento y un objetivo de beneficio mayor no crean por sí solos una ventaja estadística.
- Usar RSI y MACD como filtros candidatos, comparando su aportación con una regla base de flujo. Mantener congeladas las reglas A (flujo) y B (flujo con RSI/MACD) durante la evaluación prospectiva.
- La [preferencia vigente](criterios-operativos-vigentes-2026-10-06.md) es estudiar margen cruzado sin comprometer toda la cuenta: máximo 40 % como margen en el escenario hipotético de 25x respecto a ese margen. Hay que respetar el límite real del contrato y la cuenta; el catálogo público EEE usado en la investigación indicaba 10x para BTC/ETH. El ejemplo de objetivo neto de 0,5 % de cuenta se comparó con riesgo presupuestado de 0,25 %; no es una configuración operativa aprobada.
- La credencial de Kraken verificada para investigación tiene permiso de **solo lectura**. No se autorizó operar con dinero real. No usar claves en los estudios públicos ni enviar órdenes.

## Decisiones de arquitectura y costes

- Consultar datos de mercado públicos con un proceso local frecuente. Reservar las llamadas a modelos para eventos filtrados, revisiones o excepciones; no usar Astra en cada observación del mercado.
- Priorizar filtros deterministas locales, reutilización de datos, métricas compactas, límites de consumo y medición del uso real de tokens. Comparar esas opciones con las tarifas y el tamaño de la cuenta.
- El [análisis de opciones de ahorro](opciones-reducir-costes-y-viabilidad-2026-10-05.md) concluye que aún no existe una regla con ventaja neta estable demostrada. Por tanto, los costes actuales son presupuesto de investigación, no una inversión con retorno esperado probado.
- Mantener fuera de producción cualquier estrategia hasta verificarla con suficientes días prospectivos, operaciones, costes completos y ejecuciones reales o una simulación más fiel. No aumentar capital de forma automática por un resultado aislado.

## Evidencia y estado del seguimiento

- El [estudio exploratorio de expansión de volatilidad](resultados-expansion-volatilidad-2026-10-05.md) no validó una ventaja robusta reciente para BTC, ETH, SOL o XRP. Las reglas y el periodo se describen en su [protocolo](protocolo-expansion-volatilidad-2026-10-05.md).
- Las [investigaciones de riesgo y margen](investigacion-riesgo-margen-2026-10-06.md) y [señales intradía](investigacion-intradia-2026-10-06.md) tampoco dieron evidencia suficiente para operar; las 16 evaluaciones intradía del segundo estudio perdieron tras costes.
- Desde el 5 de octubre UTC se comparan A y B con días públicos completos de Kraken. Al cierre del 7 de octubre UTC hay **3 días prospectivos**, **15 operaciones simuladas** en A y **5** en B. La muestra está por debajo del mínimo de 30 días y 100 operaciones por variante definido por el seguimiento; no permite elegir estrategia.
- Al revisar esos tres días, B registró en ETH una operación simulada el 7 de octubre UTC con pérdida de **30,43 USD** sobre una cuenta de simulación de 10.000 USD, frente a un riesgo previsto de **25 USD**. El indicador `risk_budget_breaches` marcó 1. Fue una salida por stop; las comisiones contribuyeron a superar el presupuesto previsto. No hubo órdenes reales.
- Los manifiestos diarios del 3 al 7 de octubre UTC están completos, y las capturas del 4 al 7 revisadas no mostraron huecos en las series. El informe prospectivo `through_2026-10-07.json` permanece en la carpeta de investigación local y no forma parte de esta copia de GitHub; aún faltan financiación y fills reales.

## Próxima decisión

Continuar la observación sin cambiar umbrales. Analizar por qué la pérdida simulada de ETH superó el riesgo previsto y exigir que el dimensionamiento contemple comisiones y ejecución adversa antes de considerar una operación real. La comparación A/B sigue abierta.
