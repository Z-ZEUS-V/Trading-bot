# Astra Trading Research and Bot Blueprint

Proyecto de investigación de estrategias algorítmicas con agentes OpenAI. Revisa el README local y la carpeta docs para conocer los prompts, el flujo de agentes y la biblioteca de estrategias.

Incluye informes de investigación, catálogo JSON, base SQLite, scripts y prompts. Configura OPENAI_API_KEY localmente; nunca la subas al repositorio. El bot aún no se conecta a un exchange ni envía órdenes.

## Instalación

Requiere Python 3.11 o posterior. Instala el proyecto con `pip install -e .`.

## Seguridad

Mantén las claves API en variables de entorno y usa permisos mínimos. Valida backtests con costes y paper trading antes de cualquier despliegue.
