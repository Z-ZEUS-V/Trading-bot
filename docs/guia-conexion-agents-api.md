# Guía sencilla: crear los agentes en tu proyecto de OpenAI

## La diferencia importante

- **Proyecto de API:** el espacio de OpenAI Platform que agrupa uso, permisos, facturación y claves. La clave que ya tienes pertenece a un proyecto concreto.
- **Agente guardado:** instrucciones, modelo y herramientas reutilizables dentro de ese proyecto. El agente no es un GPT personalizado de ChatGPT ni aparece automáticamente en la lista de chats de ChatGPT.
- **Sesión:** una ejecución del agente. Aquí se consumen tokens y, si se activa, búsquedas web.

```text
Tu proyecto API → tres agentes guardados → sesión de investigación (cuando la pidas)
                                      └→ sesión de Astra para elegir la estrategia
```

## Qué agentes hemos preparado

1. **Astra Research Curator:** investiga estrategias en la web y devuelve hallazgos con fuentes. Solo se ejecuta si le pides investigación.
2. **Astra Risk Reviewer:** revisa riesgos y pruebas pendientes. Se usa de forma opcional.
3. **Astra Strategy Selector:** usa GPT-6 Astra para comparar el catálogo y devolver una lista ordenada de 3–4 estrategias finalistas, con sus riesgos y motivos.

El prompt persistente actual de Astra está en [`prompt-astra-analista-mercado.md`](prompt-astra-analista-mercado.md). La guía restante describe el aprovisionamiento inicial y puede contener pasos históricos que ya no aplican.

La investigación y el filtro local no gastan tokens. La elección final abre una sesión de Astra. No hay conexión con broker ni envío de órdenes.

## Lo que hace falta en tu cuenta

1. Entra en [OpenAI Platform](https://platform.openai.com/) y selecciona el proyecto al que pertenece tu clave actual. Si ya tienes clave, no hace falta crear otro proyecto.
2. Comprueba que es una **clave de proyecto** y que permite `api.agents.read`, `api.agents.write` y `api.responses.write`. Las dos primeras permiten crear/listar agentes; la última permite ejecutar sesiones de modelo.
3. Activa la facturación de API y configura un límite o alerta de gasto antes de ejecutar búsquedas. La API se factura aparte de ChatGPT.

La clave es una contraseña de la API. No la pegues en este chat, ni en código, ni en un archivo del repositorio.

Si no tienes claro a qué proyecto pertenece, entra en OpenAI Platform y selecciona el proyecto de la clave. Cada organización incluye un proyecto predeterminado; crear otro es opcional y, en una organización, puede requerir ser propietario. La clave y los agentes deben pertenecer al mismo proyecto.

## Dos formas de continuar

### Opción A: quieres que Codex los cree

La variable `OPENAI_API_KEY` debe estar disponible para los comandos que ejecuta Codex. Ahora mismo no lo está. En Windows:

1. Abre Inicio y busca **“Editar las variables de entorno de tu cuenta”**.
2. En **Variables de usuario**, elige **Nueva**. Nombre: `OPENAI_API_KEY`. Valor: tu clave secreta.
3. Guarda los cambios y reinicia Codex para que herede la variable.
4. Vuelve a este chat y dime **“ya está configurada”**. Comprobaré solo que la variable existe (sin mostrarla) y ejecutaré el aprovisionador.

No pegues el valor de la variable en este chat. Codex necesita que su proceso local pueda leerla. El aprovisionador no la escribe en el proyecto.

Si prefieres no guardar la clave como variable de usuario, usa la opción B: la ejecutas tú en una PowerShell local donde la variable esté cargada. Yo no podré invocar la API desde aquí hasta que la clave esté disponible en el entorno de Codex.

### Opción B: prefieres hacerlo en tu ordenador

Desde la carpeta del proyecto, instala el paquete y ejecuta `scripts/provision_platform_agents.py` en una PowerShell donde `OPENAI_API_KEY` ya esté configurada. Al terminar, se guardan los IDs en `data/platform_agents.json`. Luego dime **“ya está”** y continúo desde esos IDs.

## Orden de trabajo una vez creados

1. Ejecutar una búsqueda enfocada con **Astra Research Curator**. El informe se guarda en `data/research_runs/`.
2. Pasar ese informe y el catálogo al **Astra Strategy Selector**. Astra entrega 3–4 finalistas, explica los supuestos y compara sus riesgos y evidencia.
3. Someter las finalistas a backtests comparables con costes y pruebas fuera de muestra; entonces decidir cuál prototipar.
4. Si quieres, pedir al **Risk Reviewer** una revisión separada. Esta sesión gasta tokens adicionales, así que no se activa siempre.
5. Solo después empezamos a implementar y probar el bot en paper trading.

## Archivos y comandos del proyecto

- Aprovisionar los perfiles: `python scripts/provision_platform_agents.py`
- Buscar literatura: `python scripts/run_research_session.py --question "..."`
- Pedir a Astra que elija: `python scripts/run_selector_session.py`
- Revisar la investigación inicial: `docs/strategy-research.md`

Algunos detalles de la API cambian con el tiempo. Consulta [la guía oficial de Agents API](https://developers.openai.com/api/docs/guides/agents-api/quickstart), [agentes reutilizables y sesiones](https://developers.openai.com/api/docs/guides/agents-api/configuration) y [permisos/seguridad](https://developers.openai.com/api/docs/guides/agents-api/environments/security).
