from __future__ import annotations

import json
import os
from pathlib import Path

from openai import OpenAI


ROOT = Path(__file__).resolve().parents[1]
SPECS = ROOT / "data" / "platform_agent_specs.json"
ID_FILE = ROOT / "data" / "platform_agents.json"
MODEL_BY_ROLE = {
    "research_curator": os.environ.get("OPENAI_RESEARCH_MODEL", "gpt-6-luna"),
    "market_analyst": os.environ.get("OPENAI_MARKET_MODEL", "gpt-6-luna"),
    "backtest_risk_reviewer": os.environ.get("OPENAI_REVIEW_MODEL", "gpt-6-luna"),
    "astra_coordinator": os.environ.get("OPENAI_SELECTOR_MODEL", "gpt-6-astra"),
}
PROJECT_TAG = "astra_trading_realtime_bot"


def main() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not set. Set it in your local environment; do not paste it into chat or commit it.")

    client = OpenAI()
    specs = json.loads(SPECS.read_text(encoding="utf-8"))
    existing = list(client.beta.agents.list(limit=100))
    by_role = {
        agent.metadata.get("astra_role"): agent
        for agent in existing
        if agent.metadata.get("astra_project") == PROJECT_TAG
    }

    saved = {}
    for spec in specs:
        role = spec["role"]
        instructions = spec.get("instructions")
        if spec.get("instructions_file"):
            instructions = (ROOT / spec["instructions_file"]).read_text(encoding="utf-8")
        if not instructions:
            raise ValueError(f"No instructions configured for agent role: {role}")
        metadata = {"astra_project": PROJECT_TAG, "astra_role": role}
        config = {
            "name": spec["name"],
            "model": MODEL_BY_ROLE[role],
            "instructions": instructions,
            "metadata": metadata,
            "reasoning": {"effort": spec.get("reasoning_effort", "low")},
            "text": {"verbosity": "low"},
            "tools": spec.get("tools", []),
        }
        if role in by_role:
            agent = client.beta.agents.update(by_role[role].id, **config)
            action = "updated"
        else:
            agent = client.beta.agents.create(**config)
            action = "created"
        saved[role] = {"id": agent.id, "name": agent.name, "model": agent.model}
        print(f"{action}: {agent.name} ({agent.id})")

    ID_FILE.write_text(json.dumps(saved, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved agent IDs to {ID_FILE}")


if __name__ == "__main__":
    main()
