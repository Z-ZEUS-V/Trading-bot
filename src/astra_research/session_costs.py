"""Local exact-result reuse and best-effort token accounting for research sessions.

Only use this for static research/strategy-selection prompts. Never use it for
live decisions, orders, or prompts containing changing market snapshots.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RATES = {
    "gpt-6-astra": {"input": 10.0, "cached_input": 1.0, "output": 50.0},
    "gpt-6-luna": {"input": 0.10, "cached_input": 0.01, "output": 0.50},
}


def profile_fingerprint(spec_file: Path, role: str) -> str:
    specs = json.loads(spec_file.read_text(encoding="utf-8"))
    profile = next((item for item in specs if item.get("role") == role), {})
    return hashlib.sha256(json.dumps(profile, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def cache_key(*, role: str, agent_id: str, model: str, profile_hash: str, prompt: str) -> str:
    raw = "\0".join((role, agent_id, model, profile_hash, prompt)).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def find_cached(cache_dir: Path, key: str) -> dict[str, Any] | None:
    for path in sorted(cache_dir.glob("*.json"), reverse=True):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if record.get("cache_key") == key and record.get("status") == "completed":
            return record
    return None


def estimate_cost_usd(model: str, usage: dict[str, Any] | None) -> float | None:
    rates = RATES.get(model)
    if not rates or not usage:
        return None
    inputs = int(usage.get("input_tokens", 0))
    cached = min(inputs, int(usage.get("input_tokens_details", {}).get("cached_tokens", 0)))
    outputs = int(usage.get("output_tokens", 0))
    return ((inputs - cached) * rates["input"] + cached * rates["cached_input"] + outputs * rates["output"]) / 1_000_000


def save_run(cache_dir: Path, *, key: str, role: str, agent_id: str, model: str,
             profile_hash: str, prompt: str, output: str, session_id: str | None,
             usage: dict[str, Any] | None) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    created = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    record = {
        "cache_key": key, "status": "completed", "created_at_utc": created,
        "role": role, "agent_id": agent_id, "model": model,
        "profile_sha256": profile_hash, "session_id": session_id,
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "usage": usage, "estimated_token_cost_usd": estimate_cost_usd(model, usage),
        "cost_note": "Best-effort estimate from Agents API usage; cache-write tokens and separate tool charges are not exposed here.",
        "output": output,
    }
    path = cache_dir / f"{created}-{key[:12]}.json"
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path
