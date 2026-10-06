# Astra Trading Research and Bot Blueprint

Starter project for the strategy research workflow and four OpenAI API agents.

Current design preferences are recorded in `docs/criterios-operativos-vigentes-2026-10-06.md` and `config/criterios-operativos-vigentes.json`: consider up to 25x nominal/allocated margin, cap allocated margin at 40% of account equity, and relate stop risk to small net profit targets. This corrects the earlier interpretation of 25x as nominal/account equity. The public EEA retail schedule still requires 10% initial margin for BTC/ETH. The 2x account-exposure caps in older replay configs remain the assumptions of those historical experiments.

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
- `src/trading_lab/`: deterministic closed-bar signals, single-position USD ledger, lot/tick/margin constraints, and approximate hourly or minute fills; no agent or network dependency.
- `config/local_strategy_research.json`: frozen research assumptions and chronological windows, with August–September reserved.
- `scripts/run_local_strategy_research.py`: reproduce the 16 evaluations locally with `--output data/research_runs/<new-directory>`. Python standard library only; no package installation or API key required.
- `docs/diagnostico-objetivos-apalancamiento-2026-10-05.md`: updated flexible account targets, breakout diagnosis, actual exposure/margin/risk, and 18 development-only target/risk comparisons. The hourly H3 result is exploratory and not approved for trading.
- `config/target_frequency_diagnosis.json` and `scripts/diagnose_strategy_targets.py`: reproduce the new comparisons with `python scripts/diagnose_strategy_targets.py --output data/research_runs/<new-directory>`. Offline Python; no model calls or orders. Original research configurations/results remain historical records; 5–10% profit per trade is no longer a fixed user requirement.
- `docs/investigacion-riesgo-margen-2026-10-06.md`, `config/risk_margin_research.json` and `scripts/research_risk_margin.py`: twelve risk/reward evaluations, two historical controls, margin limits and conditional block-bootstrap intervals. Run `python scripts/research_risk_margin.py --output data/research_runs/<new-directory>` offline. No strategy passes the predeclared screen.
- `docs/investigacion-intradia-2026-10-06.md`: completed minute research, with four registered 1m/5m breakout/reversion cases and 16 evaluations. Every case loses after modeled costs in both windows. The 1m breakout reaches high frequency but fails economically. Maximum observed allocated margin is 19.38%; no live promotion.
- `config/intraday_research.json`, `src/trading_lab/intraday.py` and `scripts/research_intraday.py`: closed-bar intraday rules, one-minute entry delay, lagged spread estimates and minute funding/ledger. Reproduce offline with `python scripts/research_intraday.py --data data/market_data/intraday/20261006_v1 --books data/market_data/execution_books/20261006_v1 --output data/research_runs/<new-directory>`.
- `scripts/capture_intraday_data.py`: public-only history/book capture with raw responses and hashes. Saved data contains 708,480 minute trade/mark candles, 70,848 historical quote proxies and 60 current book samples. Quoted depth is not evidence of own fills or historical executable depth.
- `scripts/audit_intraday_run.py` and `data/research_runs/20261006_intraday_audit_v1/audit.json`: independent hash/ledger checks and exact minute-to-hour OHLC reconciliation. Research replays do not yet implement daily-loss/drawdown trading halts; reported full-period losses are diagnostic, not an approved operating policy.
- `src/trading_lab/sizing.py`: separate account risk, allocated margin and exposure; reject impossible positive-price targets. Its sizing correction can change historical replays that previously admitted impossible targets; the stored historical reports remain unchanged. Targeted offline checks: `python -m unittest discover -s tests -p test_sizing_policy.py -v`.
- `scripts/check_kraken_futures_key.py`: local, read-only Kraken Derivatives API-key check. Prompts for credentials without echo and never writes or prints them.
- `scripts/check_kraken_pro_key.py`: local, read-only Kraken Pro Spot REST API-key check, separate from Futures. Prompts hide credentials and only reports permission names.
- Current scope: crypto derivatives on Kraken only; brokers, equities, and commodities are parked. DeFi remains research/testnet-only. The user chose Astra `high` strategy selection as the research-prioritization reference; those strategies still require crypto/Kraken-specific validation and backtests.

## Setup

Requires Python 3.11+. Install with `pip install -e .`. Keep `OPENAI_API_KEY` in a local environment variable; never commit secrets.

The project reads public exchange data and now includes an initial offline strategy simulator. It does not place orders or run a live monitor. Execution calibration, broader validation, paper trading, and a bot dispatcher remain pending. The user has paused all Astra calls until further instruction; existing agent profiles are unchanged.
