"""Read-only Kraken snapshot adapter and auditable funding reconciliation."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

HOUR = 3600


def timestamp(value: str) -> int:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("A timezone is required")
    return int(parsed.timestamp())


def utc(value: int) -> str:
    return datetime.fromtimestamp(value, timezone.utc).isoformat()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True)
class Candle:
    start: int
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class Instrument:
    symbol: str
    tick: float
    lot: float
    minimum: float
    initial_margin: float
    maintenance_margin: float
    tier_ceiling_usd: float


@dataclass
class MarketData:
    trade: dict[str, dict[int, Candle]]
    mark: dict[str, dict[int, Candle]]
    funding: dict[str, dict[int, float]]
    instruments: dict[str, Instrument]
    provenance: dict
    funding_rows: list[dict]


def read_csv(path: Path) -> list[dict]:
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_market_data(root: Path, config: dict) -> MarketData:
    dataset = root / config["dataset"]
    funding_dir = root / config["funding_snapshot"]
    manifest = json.loads((dataset / "manifest.json").read_text(encoding="utf-8"))
    funding_manifest = json.loads((funding_dir / "manifest.json").read_text(encoding="utf-8"))
    captured = timestamp(manifest["captured_at_utc"])
    catalog_path = root / config["catalog"]
    catalog = {r["symbol"]: r for r in json.loads(catalog_path.read_text(encoding="utf-8"))["instruments"]}
    inputs = {str(catalog_path.relative_to(root)): digest(catalog_path),
              str((dataset / "manifest.json").relative_to(root)): digest(dataset / "manifest.json"),
              str((funding_dir / "manifest.json").relative_to(root)): digest(funding_dir / "manifest.json")}
    trade, mark, funding, instruments = {}, {}, {}, {}
    audit = {"symbols": {}, "inputs_sha256": inputs, "funding_semantics": {
        "unit": "USD per base unit per hour, linear PF contracts only",
        "cashflow": "-direction * base_quantity * fundingRate * held_seconds/3600",
        "timestamp_interpretation": "start of hourly accrual interval",
        "evidence": "Historical rate equals analytics close at same timestamp; live ticker independently corroborates current-hour rate.",
        "private_account_cashflows_verified": False,
        "sources": ["https://support.kraken.com/es/articles/perpetual-contract-specifications-for-clients-in-the-eea",
                    "https://docs.kraken.com/api-reference/historical-funding-rates/historical-funding-rates"]}}
    funding_rows = []
    for symbol in config["symbols_priority"]:
        spec = catalog[symbol]
        if spec["type"] != "flexible_futures" or spec["contractSize"] != 1 or spec["quote"] != "USD":
            raise ValueError(f"Unsupported linear contract: {symbol}")
        tiers = spec["marginSchedules"][config["margin_region"]][config["margin_category"]]
        instruments[symbol] = Instrument(symbol, float(spec["tickSize"]),
                                        10 ** -int(spec["contractValueTradePrecision"]),
                                        float(config["min_quantity"][symbol]),
                                        float(tiers[0]["initialMargin"]), float(tiers[0]["maintenanceMargin"]),
                                        float(tiers[1]["numNonContractUnits"]) if len(tiers) > 1 else math.inf)
        sa = {"discarded_partial_candles": {}, "funding_recovered_from_analytics": []}
        analytics = {}
        for series, dest in (("candles_trade", trade), ("candles_mark", mark), ("funding", analytics)):
            meta = next(r for r in manifest["datasets"] if r["symbol"] == symbol and r["series"] == series)
            path = dataset / Path(meta["csv_gzip_file"].replace("\\", "/"))
            sha = digest(path)
            if sha != meta["csv_gzip_sha256"]:
                raise ValueError(f"Checksum mismatch: {path}")
            inputs[str(path.relative_to(root))] = sha
            rows = read_csv(path)
            if series == "funding":
                analytics = {int(r["timestamp_ms"]) // 1000: r for r in rows}
                if len(analytics) != len(rows):
                    raise ValueError("Duplicate analytics timestamp")
                continue
            candles = {}
            discarded = []
            for row in rows:
                t = int(row["timestamp_ms"]) // 1000
                if t + HOUR > captured:
                    discarded.append(utc(t))
                    continue
                values = [float(row[k]) for k in ("open", "high", "low", "close", "volume")]
                o, h, l, c, v = values
                if t % HOUR or t in candles or not all(math.isfinite(x) for x in values):
                    raise ValueError(f"Invalid timestamp/value in {path}")
                if min(o, h, l, c) <= 0 or v < 0 or l > min(o, c) or h < max(o, c) or l > h:
                    raise ValueError(f"Invalid OHLC in {path} at {utc(t)}")
                candles[t] = Candle(t, o, h, l, c, v)
            dest[symbol] = candles
            sa["discarded_partial_candles"][series] = discarded

        hm = next(x for x in funding_manifest["observations"] if x["symbol"] == symbol)
        path = funding_dir / hm["raw_file"]
        raw = gzip.decompress(path.read_bytes())
        if hashlib.sha256(raw).hexdigest() != hm["response_sha256"]:
            raise ValueError("Historical funding checksum mismatch")
        inputs[str(path.relative_to(root))] = digest(path)
        payload = json.loads(raw)
        if payload.get("result") != "success":
            raise ValueError("Funding response not successful")
        history = {}
        for r in payload["rates"]:
            t = timestamp(r["timestamp"])
            if t % HOUR or t in history or not all(math.isfinite(float(r[k])) for k in ("fundingRate", "relativeFundingRate")):
                raise ValueError("Invalid historical funding point")
            history[t] = r
        common = sorted(history.keys() & analytics.keys())
        mismatches = []
        for t in common:
            if not (math.isclose(float(history[t]["fundingRate"]), float(analytics[t]["rate_close"]), rel_tol=1e-7, abs_tol=1e-12)
                    and math.isclose(float(history[t]["relativeFundingRate"]), float(analytics[t]["relative_rate_close"]), rel_tol=1e-7, abs_tol=1e-12)):
                mismatches.append(utc(t))
        sa.update({"overlap_count": len(common), "overlap_mismatches": mismatches})
        if len(common) < 100 or mismatches:
            raise ValueError(f"Funding sources not reconciled for {symbol}")
        combined = {}
        for t in range(min(history), max(history) + HOUR, HOUR):
            source = "historical_funding_rates"
            if t in history:
                rate, relative = float(history[t]["fundingRate"]), float(history[t]["relativeFundingRate"])
            elif t in analytics:
                rate, relative = float(analytics[t]["rate_close"]), float(analytics[t]["relative_rate_close"])
                if not math.isfinite(rate) or not math.isfinite(relative):
                    raise ValueError("Nonfinite analytics recovery")
                source = "analytics_observed_close"
                sa["funding_recovered_from_analytics"].append(utc(t))
            else:
                continue
            combined[t] = rate
            funding_rows.append({"symbol": symbol, "period_start_utc": utc(t), "period_end_utc": utc(t + HOUR),
                                 "funding_usd_per_base_unit_hour": rate, "relative_fraction": relative,
                                 "source": source, "interpolated": False})
        sa["remaining_missing_hours"] = [utc(t) for t in range(min(history), max(history) + HOUR, HOUR) if t not in combined]
        funding[symbol] = combined
        audit["symbols"][symbol] = sa

    timing_dir = root / config["funding_timing_snapshot"]
    timing_manifest = json.loads((timing_dir / "manifest.json").read_text(encoding="utf-8"))
    timing_payloads = {}
    inputs[str((timing_dir / "manifest.json").relative_to(root))] = digest(timing_dir / "manifest.json")
    for item in timing_manifest:
        path = timing_dir / (item["name"] + ".json.gz")
        raw = gzip.decompress(path.read_bytes())
        if hashlib.sha256(raw).hexdigest() != item["sha256_raw"]:
            raise ValueError("Timing snapshot checksum mismatch")
        inputs[str(path.relative_to(root))] = digest(path)
        timing_payloads[item["name"]] = json.loads(raw)
    tickers = timing_payloads["tickers"]
    live_hour = timestamp(tickers["serverTime"]) // HOUR * HOUR
    for symbol in config["symbols_priority"]:
        current = next(r for r in tickers["tickers"] if r["symbol"] == symbol)
        historical = next(r for r in timing_payloads[symbol]["rates"] if timestamp(r["timestamp"]) == live_hour)
        matches = math.isclose(float(current["fundingRate"]), float(historical["fundingRate"]), rel_tol=1e-12)
        audit["symbols"][symbol]["current_hour_timing_check"] = {"ticker_server_time": tickers["serverTime"],
            "historical_timestamp": historical["timestamp"], "current_funding_matches": matches,
            "ticker_current_rate": current["fundingRate"], "prediction_not_used": current.get("fundingRatePrediction")}
        if not matches:
            raise ValueError("Current funding timestamp not corroborated")
    return MarketData(trade, mark, funding, instruments, audit, funding_rows)
