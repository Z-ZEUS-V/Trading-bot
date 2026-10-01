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


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a research-only Astra comparison against the local strategy catalog; this is not a live bot session.")
    parser.add_argument("--market", help="Optional market, e.g. equities, futures, fx, options, crypto.")
    parser.add_argument("--horizon", help="Optional horizon, e.g. daily, weekly, intraday.")
    parser.add_argument("--research-file", help="Optional compact literature report to include in Astra's comparison.")
    args = parser.parse_args()
    if not os.environ.get("OPENAI_API_KEY"):
        parser.error("Set OPENAI_API_KEY in your own environment; do not paste it into chat or commit it.")
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
                elif event.type == "agent.session.turn.failed":
                    raise RuntimeError(f"Agent turn failed: {event.turn.error.message if event.turn.error else 'unknown error'}")
                elif event.type == "agent.session.turn.cancelled":
                    raise RuntimeError("Agent turn was cancelled.")
                elif event.type == "agent.session.turn.completed" and event.turn.subagent_id is None:
                    completed = True
            if not completed:
                raise RuntimeError("The event stream closed before the main agent turn completed.")
    print()


if __name__ == "__main__":
    main()
