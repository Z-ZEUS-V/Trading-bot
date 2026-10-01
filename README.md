# Astra Trading Research and Bot Blueprint

Starter project for the strategy research workflow and four OpenAI API agents.

## Contents

- `data/strategies.json`: strategy catalog.
- `data/astra_research.sqlite3`: searchable local library.
- `data/research_runs/`: sourced research reports.
- `data/platform_agent_specs.json`: agent instructions; `data/platform_agents.json`: saved agent IDs.
- `docs/`: prompts, architecture, API setup guide, and exchange universe notes.
- `scripts/`: create agent profiles and run research/selection sessions.
- `src/astra_research/`: catalog and CLI package.

## Setup

Requires Python 3.11+. Install with `pip install -e .`. Keep `OPENAI_API_KEY` in a local environment variable; never commit secrets.

The project does not yet connect to an exchange or place orders. It defines the agent workflow and research library; the market data adapter, backtesting engine, and bot dispatcher remain to be built. Validate strategies with realistic costs, out-of-sample tests, and paper trading before deployment.
