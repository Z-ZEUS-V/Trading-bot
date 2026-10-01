from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from astra_research.catalog import list_strategies, initialize  # noqa: E402
from astra_research.session_costs import (  # noqa: E402
    cache_key, estimate_cost_usd, find_cached, profile_fingerprint, save_run,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a research-only Astra comparison against the local strategy catalog; this is not a live bot session.")
    parser.add_argument("--market", help="Optional market, e.g. equities, futures, fx, options, crypto.")
    parser.add_argument("--horizon", help="Optional horizon, e.g. daily, weekly, intraday.")
    parser.add_argument("--research-file", help="Optional compact literature report to include in Astra's comparison.")
    parser.add_argument("--refresh", action="store_true", help="Ignore an exact local cache and make a fresh API call.")
    args = parser.parse_args()
    if not (ROOT / "data" / "platform_agents.json").exists():
        parser.error("Provision the saved API agents first: python scripts/provision_platform_agents.py")

    initialize()
    shortlist = list_strategies(limit=100)
    shortlist = [item for item in shortlist if item["family"] != "execution"]
    if args.market:
        shortlist = [item for item in shortlist if args.market.lower() in item["markets"]]
    if args.horizon:
        shortlist = [item for item in shortlist if args.horizon.lower() in item["horizons"]]
    if not shortlist:
        print("No catalog candidates match those optional constraints; no model call made.")
        return
    ids = json.loads((ROOT / "data" / "platform_agents.json").read_text(encoding="utf-8"))
    selector_id = ids["astra_coordinator"]["id"]
    packet = [{key: item[key] for key in ("id", "name", "mechanism", "benefit_potential", "market_risk", "tail_risk", "implementation_risk", "cost_sensitivity", "evidence_strength", "capital_and_infrastructure", "failure_modes", "evidence_summary", "sources")} for item in shortlist]
    research = ""
    if args.research_file:
        research_path = Path(args.research_file)
        if not research_path.is_absolute():
            research_path = ROOT / research_path
        research = research_path.read_text(encoding="utf-8")[:16000]
    prompt = (
        f"MODE: RESEARCH_SELECTION. Compare strategy families from the catalog as a planning step toward building an algorithmic trading bot. "
        f"Market={args.market or 'unspecified'}; horizon={args.horizon or 'unspecified'}; risk preference=unspecified. "
        "Compare every candidate supplied. Use the research notes if present, state conservative assumptions, rank the best-fit "
        "up to four strategy candidates (fewer if evidence does not support more), explain why each qualifies and what could "
        "change the ranking. This session has no live market snapshot, so do not claim a current market decision. Finish with "
        "comparison criteria and a validation plan. Do not give order instructions.\n"
        "Candidate cards:\n" + json.dumps(packet, ensure_ascii=False)
        + ("\nRecent research report:\n" + research if research else "")
    )

    model = ids["astra_coordinator"].get("model", "gpt-6-astra")
    profile_hash = profile_fingerprint(ROOT / "data" / "platform_agent_specs.json", "astra_coordinator")
    key = cache_key(role="astra_coordinator", agent_id=selector_id, model=model, profile_hash=profile_hash, prompt=prompt)
    cache_dir = ROOT / "data" / "research_runs" / "session_cache"
    cached = None if args.refresh else find_cached(cache_dir, key)
    if cached:
        print(cached["output"])
        print(f"\nResultado reutilizado; no se hizo llamada API. Sesión original: {cached.get('session_id') or 'no registrada'}")
        if cached.get("estimated_token_cost_usd") is not None:
            print(f"Coste estimado original: ${cached['estimated_token_cost_usd']:.6f}")
        return

    if not os.environ.get("OPENAI_API_KEY"):
        parser.error("Set OPENAI_API_KEY in your own environment; do not paste it into chat or commit it.")

    output = []
    session_id = None
    with OpenAI() as client:
        with client.beta.agents.sessions.create(
            agent_id=selector_id,
            environment={"type": "none"},
            input=prompt,
            stream=True,
        ) as events:
            completed = False
            for event in events:
                if event.type == "agent.session.turn.output_text.delta":
                    print(event.delta, end="", flush=True)
                    output.append(event.delta)
                elif event.type == "agent.session.turn.failed":
                    raise RuntimeError(f"Agent turn failed: {event.turn.error.message if event.turn.error else 'unknown error'}")
                elif event.type == "agent.session.turn.cancelled":
                    raise RuntimeError("Agent turn was cancelled.")
                elif event.type == "agent.session.turn.completed" and event.turn.subagent_id is None:
                    completed = True
                    session_id = event.session_id
            if not completed:
                raise RuntimeError("The event stream closed before the main agent turn completed.")
        usage = None
        if session_id:
            try:
                recorded = client.beta.agents.sessions.retrieve(session_id).usage
                usage = recorded.model_dump() if recorded else None
            except Exception as exc:
                print(f"\nAviso: no se pudo recuperar usage: {exc}", file=sys.stderr)
    print()
    record_path = save_run(cache_dir, key=key, role="astra_coordinator", agent_id=selector_id, model=model,
                           profile_hash=profile_hash, prompt=prompt, output="".join(output),
                           session_id=session_id, usage=usage)
    print(f"Resultado y uso guardados localmente en {record_path}")
    estimate = estimate_cost_usd(model, usage)
    if estimate is not None:
        print(f"Coste de tokens estimado, no factura final: ${estimate:.6f}")


if __name__ == "__main__":
    main()
