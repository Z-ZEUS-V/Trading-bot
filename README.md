# Astra Trading Research and Bot Blueprint

Starter project for the strategy research workflow and four OpenAI API agents.

## Contents

- `data/strategies.json`: strategy catalog.
- `data/astra_research.sqlite3`: searchable local library.
- `data/research_runs/`: sourced research reports.
- `data/platform_agent_specs.json`: agent instructions; `data/platform_agents.json`: saved agent IDs.
- `docs/prompt-astra-analista-mercado.md`: canonical, exchange-neutral Astra prompt; coordinator defaults to medium reasoning and low text verbosity.
- `docs/`: prompts, architecture, API setup guide, and exchange universe notes.
- `docs/auditoria-cobertura-estrategias.md`: audit of researched, shortlisted, deferred, and out-of-scope strategy families.
- `scripts/`: create agent profiles and run research/selection sessions.
- `src/astra_research/`: catalog and CLI package.
- `docs/estado-actual-y-retoma.md`: recovered project status, implemented parts, missing components, and recommended continuation order.
- `docs/estimacion-costes-operativos-y-criterios-reasoning.md`: operating-cost scenarios per futures round trip and criteria for escalating Astra reasoning from medium to high.
- `docs/plan-optimizacion-costes-y-calidad.md`: phased plan for local gating, token reduction, model routing, evaluation and per-trade cost telemetry.
- `docs/recomendacion-venue-espana.md`: provisional venue recommendation for Spain, coverage gaps, cost factors and pre-integration checks.
- `docs/comparativa-comisiones-kraken-broker.md`: Kraken crypto derivatives maker/taker round-trip costs versus a CME micro Bitcoin futures broker reference.
- `docs/analisis-defi-kraken-espana.md`: feasibility, fee comparison, legal-access uncertainties, and security requirements for a possible DeFi perpetuals testnet evaluation.
- `docs/plan-pruebas-estrategias-kraken.md`: adaptation of the `high` strategy selection to Kraken crypto perpetuals, public API checks, data coverage requirements, and the safe next steps.
- `scripts/check_kraken_futures_key.py`: local, read-only Kraken Derivatives API-key check. Prompts for credentials without echo and never writes or prints them.
- `scripts/check_kraken_pro_key.py`: local, read-only Kraken Pro Spot REST API-key check, separate from Futures. Prompts hide credentials and only reports permission names.
- Current scope: crypto derivatives on Kraken only; brokers, equities, and commodities are parked. DeFi remains research/testnet-only. The user chose Astra `high` strategy selection as the research-prioritization reference; those strategies still require crypto/Kraken-specific validation and backtests.

## Setup

Requires Python 3.11+. Install with `pip install -e .`. Keep `OPENAI_API_KEY` in a local environment variable; never commit secrets.

The project does not yet connect to an exchange or place orders. It defines the agent workflow and research library; the market data adapter, backtesting engine, and bot dispatcher remain to be built. Validate strategies with realistic costs, out-of-sample tests, and paper trading before deployment.
