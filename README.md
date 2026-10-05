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
- `scripts/capture_kraken_instruments.py`: save a dated, hashed snapshot of Kraken Derivatives' public instrument catalog without API credentials.
- `scripts/probe_kraken_public_coverage.py`: measure one-hour history windows for candles, funding, and basis without credentials.
- `scripts/probe_kraken_history_depth.py`: estimate earliest available public history for every active crypto perpetual in the saved catalog.

Capture the current public catalog from the repository root with `python scripts/capture_kraken_instruments.py`. The raw response and a manifest are saved under `data/market_data/instruments/`; the snapshot is not an account eligibility check or a historical universe.

Probe historical coverage with `python scripts/probe_kraken_public_coverage.py --days 365 --chunk-days 30`. This stores response hashes, observed timestamp ranges, and gaps under `data/market_data/coverage/`; it does not download or store every market-data point.

Probe the last 30 days for current crypto perpetual candidates from the saved instrument catalog with `python scripts/probe_kraken_public_coverage.py --all-active-crypto-perps --days 30 --chunk-days 30 --compact --summary-only`. Download and normalize a bounded historical sample with `python scripts/ingest_kraken_public_history.py --symbols PF_XBTUSD,PF_ETHUSD --days 365 --chunk-days 30`; each run stores compressed raw responses, normalized gzip CSVs, and a provenance manifest under `data/market_data/datasets/`.

Estimate historical depth per contract/series with `python scripts/probe_kraken_history_depth.py`. The result records response hashes and the API's truncation flag under `data/market_data/history_depth/`. It is an oldest-point estimate; a `more=true` response is capped and does not establish complete continuity. The expanded BTC/ETH sample through the oldest available PF perpetual history is documented in `docs/historico-publico-profundidad-2026-10-02.md`.
- `docs/estado-actual-y-retoma.md`: recovered project status, implemented parts, missing components, and recommended continuation order.
- `docs/estimacion-costes-operativos-y-criterios-reasoning.md`: operating-cost scenarios per futures round trip and criteria for escalating Astra reasoning from medium to high.
- `docs/plan-optimizacion-costes-y-calidad.md`: phased plan for local gating, token reduction, model routing, evaluation and per-trade cost telemetry.
- `docs/recomendacion-venue-espana.md`: provisional venue recommendation for Spain, coverage gaps, cost factors and pre-integration checks.
- `docs/comparativa-comisiones-kraken-broker.md`: Kraken crypto derivatives maker/taker round-trip costs versus a CME micro Bitcoin futures broker reference.
- `docs/analisis-defi-kraken-espana.md`: feasibility, fee comparison, legal-access uncertainties, and security requirements for a possible DeFi perpetuals testnet evaluation.
- `docs/plan-pruebas-estrategias-kraken.md`: adaptation of the `high` strategy selection to Kraken crypto perpetuals, public API checks, data coverage requirements, and the safe next steps.
- `docs/replanteamiento-capital-inicial-50-usd.md`: new research plan with 50 USD initial trading capital, an explicit cost/lot-size viability gate, and no assumption that ranked strategies are profitable.
- `docs/estudio-trading-algoritmico-2026-10-05.md`: applied study, reviewed primary sources, cross-margin/stop design, 5–10% account profit targets and 2–5% planned risk, data corrections, and falsifiable trend experiments. No validated strategy yet.
- `scripts/analyze_account_risk_targets.py`: offline account-target arithmetic, including entry/exit fees, hypothetical friction, break-even win rates and loss streaks. Run with `--output` pointing to a new directory; results in `data/research_runs/20261005_account_risk/` are scenarios, not backtests.
- `data/market_data/funding_rates/20261005T204909Z/`: raw public historical-funding responses for BTC/ETH from October 2025. The subsequent local replay reconciles the public sources and recovers two missing hours per symbol; private account cashflows remain unverified.
- `docs/simulacion-local-estrategias-2026-10-05.md`: first local replay results, funding reconciliation, limitations, and a low-cost monitoring design. No strategy is approved for live trading.
- `src/trading_lab/`: deterministic closed-bar signals, single-position USD ledger, lot/tick/margin constraints, and approximate hourly fills; no agent or network dependency.
- `config/local_strategy_research.json`: frozen research assumptions and chronological windows, with August–September reserved.
- `scripts/run_local_strategy_research.py`: reproduce the 16 evaluations locally with `--output data/research_runs/<new-directory>`. Python standard library only; no package installation or API key required.
- `scripts/check_kraken_futures_key.py`: local, read-only Kraken Derivatives API-key check. Prompts for credentials without echo and never writes or prints them.
- `scripts/check_kraken_pro_key.py`: local, read-only Kraken Pro Spot REST API-key check, separate from Futures. Prompts hide credentials and only reports permission names.
- Current scope: crypto derivatives on Kraken only; brokers, equities, and commodities are parked. DeFi remains research/testnet-only. The user chose Astra `high` strategy selection as the research-prioritization reference; those strategies still require crypto/Kraken-specific validation and backtests.

## Setup

Requires Python 3.11+. Install with `pip install -e .`. Keep `OPENAI_API_KEY` in a local environment variable; never commit secrets.

The project reads public exchange data and now includes an initial offline strategy simulator. It does not place orders or run a live monitor. Execution calibration, broader validation, paper trading, and a bot dispatcher remain pending. The user has paused all Astra calls until further instruction; existing agent profiles are unchanged.
