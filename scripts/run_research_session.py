from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run an on-demand strategy literature search through a saved Agents API researcher.")
    parser.add_argument("--question", required=True, help="Specific market/family/question; include timeframe and constraints when known.")
    args = parser.parse_args()
    if not os.environ.get("OPENAI_API_KEY"):
        parser.error("Set OPENAI_API_KEY in your own environment; do not paste it into chat or commit it.")
    id_file = ROOT / "data" / "platform_agents.json"
    if not id_file.exists():
        parser.error("Provision the saved API agents first: python scripts/provision_platform_agents.py")
    agent_id = json.loads(id_file.read_text(encoding="utf-8"))["research_curator"]["id"]
    prompt = (
        args.question
        + "\nSearch for primary academic and official sources. Cite URLs next to claims. Separate historical gross/net results, "
          "risk, costs, sample period, and limitations. If performance comparisons are not comparable, say so. Keep the report concise."
    )

    output = []
    with OpenAI() as client:
        with client.beta.agents.sessions.create(
            agent_id=agent_id,
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
                    raise RuntimeError(f"Research session failed: {event.turn.error.message if event.turn.error else 'unknown error'}")
                elif event.type == "agent.session.turn.cancelled":
                    raise RuntimeError("Research session was cancelled.")
                elif event.type == "agent.session.turn.completed" and event.turn.subagent_id is None:
                    completed = True
            if not completed:
                raise RuntimeError("The event stream closed before the research turn completed.")
    print()
    reports_dir = ROOT / "data" / "research_runs"
    reports_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = reports_dir / f"strategy-research-{timestamp}.md"
    report_path.write_text(f"# Research run\n\nQuestion: {args.question}\n\n" + "".join(output) + "\n", encoding="utf-8")
    print(f"Saved research report to {report_path}")


if __name__ == "__main__":
    main()
