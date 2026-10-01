from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "strategies.json"
DB_FILE = Path(os.environ.get("ASTRA_DB_PATH", ROOT / "data" / "astra_research.sqlite3"))


def connect() -> sqlite3.Connection:
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_FILE)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    return db


def initialize() -> int:
    items: list[dict[str, Any]] = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    with connect() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS strategies (
                id TEXT PRIMARY KEY, name TEXT NOT NULL, family TEXT NOT NULL,
                markets_json TEXT NOT NULL, horizons_json TEXT NOT NULL,
                mechanism TEXT NOT NULL, benefit_potential INTEGER NOT NULL,
                market_risk INTEGER NOT NULL, tail_risk INTEGER NOT NULL,
                implementation_risk INTEGER NOT NULL, cost_sensitivity INTEGER NOT NULL,
                evidence_strength INTEGER NOT NULL, capital_and_infrastructure TEXT NOT NULL,
                failure_modes_json TEXT NOT NULL, evidence_summary TEXT NOT NULL,
                sources_json TEXT NOT NULL, review_status TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)
        for item in items:
            fields = list(item)
            values = [json.dumps(item[k], ensure_ascii=False) if isinstance(item[k], list) else item[k] for k in fields]
            columns_by_key = {"markets": "markets_json", "horizons": "horizons_json", "failure_modes": "failure_modes_json", "sources": "sources_json"}
            columns = ",".join(columns_by_key.get(key, key) for key in fields)
            placeholders = ",".join("?" for _ in fields)
            updates = ",".join(f"{columns_by_key.get(key, key)}=excluded.{columns_by_key.get(key, key)}" for key in fields if key != "id")
            db.execute(f"INSERT INTO strategies ({columns}) VALUES ({placeholders}) ON CONFLICT(id) DO UPDATE SET {updates}, updated_at=CURRENT_TIMESTAMP", values)
    return len(items)


def list_strategies(market: str | None = None, max_risk: int = 5, limit: int = 50) -> list[dict[str, Any]]:
    with connect() as db:
        rows = db.execute("SELECT * FROM strategies WHERE market_risk <= ? AND tail_risk <= ? ORDER BY evidence_strength DESC, benefit_potential DESC LIMIT ?", (max_risk, max_risk, limit)).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        for key in ("markets", "horizons", "failure_modes", "sources"):
            item[key] = json.loads(item.pop(f"{key}_json"))
        item.pop("updated_at", None)
        if market and market.lower() not in item["markets"]:
            continue
        result.append(item)
    return result


def candidates(market: str, horizon: str, risk: str, limit: int = 5) -> list[dict[str, Any]]:
    risk_caps = {"low": 2, "moderate": 3, "high": 4, "very_high": 5}
    if risk not in risk_caps:
        raise ValueError(f"risk must be one of: {', '.join(risk_caps)}")
    # Exclude execution-only methods from alpha selection and order by evidence before the qualitative benefit score.
    rows = list_strategies(max_risk=risk_caps[risk], limit=100)
    matches = [x for x in rows if market.lower() in x["markets"] and horizon.lower() in x["horizons"] and x["family"] != "execution"]
    matches.sort(key=lambda x: (x["evidence_strength"], x["benefit_potential"], -x["tail_risk"]), reverse=True)
    return matches[:limit]
