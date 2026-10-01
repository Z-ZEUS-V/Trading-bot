# Arquitectura para Astra y el bot de futuros

## Objetivo

En cada consulta operativa del bot, analizar el mercado con datos recientes, contrastar el contexto con backtests verificables y producir una decisión analítica de estrategia. Astra coordina el resultado. El sistema debe abstenerse si los datos están ausentes, vencidos o no respaldan una ventaja.

Los perfiles en OpenAI son agentes de análisis, no una fuente de precios ni un motor de backtesting. Antes de usar el flujo en vivo, el bot debe conectar un proveedor de datos de mercado y un motor determinista de backtests.

El venue definido es **Bitunix**. El universo solicitado es top 10 cripto por capitalización (ranking externo y dinámico), Stock Perps grandes, y oro, plata y crudo. Consultar [universo y limitaciones de Bitunix](bitunix-universe.md) antes de integrar. Bitunix actualmente indica que Stock Perps no admite trading por API; esos símbolos quedan solo para análisis hasta que el soporte oficial cambie.

## Perfiles de agentes

1. **Astra Real-Time Futures Decision Analyst (`gpt-6-astra`):** recibe todos los insumos, escoge la estrategia candidata mejor sustentada para el contexto actual o se abstiene. Devuelve estado, dirección analítica (LONG/SHORT/NO_SIGNAL), evidencia, riesgos y datos faltantes; no emite órdenes.
2. **Astra Live Market Analyst (`gpt-6-luna`):** analiza snapshot, régimen e indicadores calculados por el bot. Comprueba timestamp, contrato, timeframe, huecos y consistencia; no inventa cotizaciones.
3. **Astra Backtest and Risk Reviewer (`gpt-6-luna`):** audita las métricas y metodología entregadas por el motor de backtesting, costes netos, validación fuera de muestra, drawdown y riesgos de cola.
4. **Astra Strategy Research Curator (`gpt-6-luna`):** actualiza la biblioteca con búsqueda web bajo demanda y fuentes primarias. No se activa en cada consulta del bot.

## Flujo por consulta del bot

```text
Evento de decisión (por intervalo/condición, no cada tick por defecto)
                         ↓
Proveedor de datos → snapshot con timestamp + contrato + velas/volumen/OI
                         ↓
Motor local calcula indicadores y consulta backtests versionados
                         ↓
              ┌──────────┴──────────┐
              ↓                     ↓
       Market Analyst       Backtest/Risk Reviewer
              └──────────┬──────────┘
                         ↓
        Astra integra snapshot + informes + catálogo
                         ↓
 JSON: candidato o abstención + evidencia + límites
```

Los dos análisis especialistas pueden correr en paralelo. El bot adjunta después sus resultados a la sesión de Astra. El investigador solo corre cuando falta cobertura de evidencia o cuando se solicite una actualización. El bot debe consumir los canales públicos de Bitunix apropiados para velas, precio, profundidad y operaciones; marcar cada barra como abierta/cerrada. El top 10 por market cap requiere un proveedor externo. El conector es función de la aplicación/bot; no está incluido en los perfiles API y aún no hay código conectado a Bitunix.

## Contrato mínimo de datos

- Símbolo y contrato exactos, mercado, zona horaria y proveedor.
- Timestamp UTC del snapshot y máximo de antigüedad permitido para ese timeframe.
- Velas OHLCV completas y su frecuencia; open interest si está disponible.
- Especificaciones: multiplicador, tick, horario, vencimiento y regla de rollover.
- Indicadores con fórmula, periodo y valor, calculados fuera del LLM.
- Ficha de backtest vinculada a versión de estrategia, instrumento, datos y fecha.
- Comisiones, spread, slippage, funding/rollover y benchmark usados.
- Métricas OOS/walk-forward: retorno neto, volatilidad, Sharpe/Sortino si se calcularon, máximo drawdown, CVaR/pérdidas de cola, rotación, tamaño de muestra y desglose por régimen.

Si faltan elementos necesarios, Astra reporta `INSUFFICIENT_DATA` o `STALE_DATA`; si las pruebas no son robustas, `NO_EDGE`. La salida direccional es informativa para el bot y no contiene tamaño, apalancamiento ni orden de broker.

## Almacenamiento

- `data/strategies.json` y `data/astra_research.sqlite3`: catálogo de familias, evidencia y fuentes.
- `data/research_runs/`: informes del investigador para revisión y curación.
- `data/platform_agent_specs.json`: instrucciones versionadas para los perfiles API.
- `data/platform_agents.json`: IDs de perfiles creados en el proyecto API.
- Resultados futuros de backtesting deben almacenarse versionados por estrategia y dataset, fuera del chat del modelo.

No guardar claves API en estos archivos ni en Git. La biblioteca no es entrenamiento ni memoria automática: el bot adjunta a cada sesión el contexto relevante.

## Control de coste y latencia

- Ejecutar análisis cuando el bot necesite tomar una decisión (por intervalo o condición), no por cada tick de precio.
- Dos sesiones breves de Luna en paralelo y una síntesis de Astra; enviar solo snapshot resumido, finalistas pertinentes y métricas de backtest relevantes.
- No enviar imágenes de gráficos de forma rutinaria: las barras numéricas y los indicadores reproducibles ocupan menos y permiten auditoría. Usar imagen opcional para una lectura visual complementaria.
- La investigación web queda bajo demanda; sus búsquedas y tokens son coste adicional.
- Registrar uso por rol y limitar contexto/salida; no asumir que el coste queda fijo.

## Fases

1. Crear y guardar los cuatro perfiles API con estas instrucciones.
2. Integrar un proveedor de datos compatible con los mercados elegidos y el motor local de backtests.
3. Construir la aplicación del bot que llama a los dos especialistas en paralelo y pasa sus informes a Astra.
4. Validar con datos históricos, pruebas walk-forward y paper trading.
5. Una integración de ejecución con broker, si se construye más adelante, debe ser una fase aparte con límites duros y supervisión humana.

## Referencias de OpenAI

- [Agents API: configuración reutilizable](https://developers.openai.com/api/docs/guides/agents-api/configuration)
- [Agents API: crear un agente](https://developers.openai.com/api/reference/python/resources/beta/subresources/agents/methods/create)
- [Agents API: búsqueda web](https://developers.openai.com/api/docs/guides/agents-api/tools/web-search)
- [OpenAI API: herramientas y funciones](https://developers.openai.com/api/docs/guides/tools)
