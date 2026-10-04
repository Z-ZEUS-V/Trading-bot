"""Estimate the oldest public hourly history available per active crypto perpetual."""

from __future__ import annotations

from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from probe_kraken_public_coverage import (
    BASE_URL,
    CHARTS_PATH,
    REQUEST_PAUSE_SECONDS,
    TIMEOUT_SECONDS,
    USER_AGENT,
    active_crypto_perpetual_symbols,
)

HOUR = 3600
SERIES = ("candles_trade", "candles_mark", "funding", "future-basis")


def utc_seconds(value: str) -> int:
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())


def request_url(symbol: str, series: str, start: int, end: int) -> str:
    if series.startswith("candles_"):
        tick = series.removeprefix("candles_")
        query = urlencode({"from": start, "to": end})
        return f"{BASE_URL}{CHARTS_PATH}/{tick}/{symbol}/1h?{query}"
    endpoint = "future-basis" if series == "future-basis" else "funding"
    query = urlencode({"since": start, "to": end, "interval": HOUR})
    return f"{BASE_URL}{CHARTS_PATH}/analytics/{symbol}/{endpoint}?{query}"


def get_observation(item: dict, series: str, end: int) -> dict:
    symbol = item["symbol"]
    base = {
        "symbol": symbol,
        "series": series,
        "instrument_opening_date": item.get("openingDate"),
    }
    opening = item.get("openingDate")
    if not opening:
        return {**base, "error": "missing_openingDate"}
    start = utc_seconds(opening)
    url = request_url(symbol, series, start, end)
    req = Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=TIMEOUT_SECONDS) as response:
            raw = response.read()
            status = response.status
    except HTTPError as exc:
        return {**base, "http_status": exc.code, "error": f"HTTP {exc.code}"}
    except (URLError, TimeoutError, OSError) as exc:
        return {**base, "error": f"network:{type(exc).__name__}"}
    try:
        payload = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {**base, "http_status": status, "error": "invalid_json"}

    if series.startswith("candles_"):
        rows = payload.get("candles", [])
        stamps = [int(row["time"]) for row in rows if isinstance(row, dict) and row.get("time") is not None]
        more = payload.get("more_candles")
        errors = []
    else:
        result = payload.get("result", {})
        stamps = [int(ts) for ts in result.get("timestamp", [])]
        more = result.get("more")
        errors = payload.get("errors", [])
    stamps_ms = sorted({stamp if stamp > 100_000_000_000 else stamp * 1000 for stamp in stamps})
    first_ms = stamps_ms[0] if stamps_ms else None
    last_ms = stamps_ms[-1] if stamps_ms else None
    first_dt = datetime.fromtimestamp(first_ms / 1000, UTC) if first_ms is not None else None
    opening_dt = datetime.fromtimestamp(start, UTC)
    return {
        **base,
        "http_status": status,
        "response_sha256": hashlib.sha256(raw).hexdigest(),
        "requested_from_utc": opening_dt.isoformat(timespec="seconds"),
        "requested_to_utc": datetime.fromtimestamp(end, UTC).isoformat(timespec="seconds"),
        "point_count": len(stamps_ms),
        "first_point_utc": first_dt.isoformat(timespec="seconds") if first_dt else None,
        "last_point_utc": datetime.fromtimestamp(last_ms / 1000, UTC).isoformat(timespec="seconds") if last_ms else None,
        "age_from_listing_to_first_point_days": round((first_dt.timestamp() - start) / 86400, 4) if first_dt else None,
        "history_days_from_first_point_to_now": round((end - first_dt.timestamp()) / 86400, 2) if first_dt else 0,
        "more": more,
        "errors": errors,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    catalog = root / "data/market_data/instruments/20261002T001640Z/response.json"
    symbols, universe = active_crypto_perpetual_symbols(catalog)
    instruments = json.loads(catalog.read_text(encoding="utf-8"))["instruments"]
    by_symbol = {item["symbol"]: item for item in instruments}
    end = int(time.time())
    end -= end % HOUR
    observations = []
    total = len(symbols) * len(SERIES)
    for index, (symbol, series) in enumerate(((s, t) for s in symbols for t in SERIES), start=1):
        item = get_observation(by_symbol[symbol], series, end)
        observations.append(item)
        if index % 40 == 0 or index == total:
            print(f"Sondeadas {index}/{total} combinaciones contrato/serie", flush=True)
        time.sleep(REQUEST_PAUSE_SECONDS)

    summaries = []
    for series in SERIES:
        rows = [row for row in observations if row["series"] == series]
        present = [row for row in rows if row.get("point_count", 0) > 0]
        depths = sorted(row["history_days_from_first_point_to_now"] for row in present)
        errors = [row for row in rows if row.get("error") or row.get("errors")]
        summaries.append({
            "series": series,
            "contracts_queried": len(rows),
            "contracts_with_data": len(present),
            "contracts_without_data": len(rows) - len(present) - len(errors),
            "contracts_with_errors": len(errors),
            "oldest_point_overall_utc": min((r["first_point_utc"] for r in present), default=None),
            "newest_point_overall_utc": max((r["last_point_utc"] for r in present), default=None),
            "median_history_days": depths[len(depths) // 2] if depths else None,
            "min_history_days": depths[0] if depths else None,
            "max_history_days": depths[-1] if depths else None,
            "responses_with_more_true": sum(row.get("more") is True for row in rows),
        })

    report = {
        "captured_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "source": f"{BASE_URL}{CHARTS_PATH}",
        "catalog_snapshot": str(catalog.relative_to(root)).replace("\\", "/"),
        "universe_selection": universe,
        "requested_interval_seconds": HOUR,
        "historical_depth_method": "One full-range request from each instrument openingDate to capture time per series. Kraken returns a limited page; the earliest returned point is a depth estimate, not a guarantee of complete continuous history. more=true means the response is truncated.",
        "series_summaries": summaries,
        "observations": observations,
        "notes": [
            "Solo endpoints públicos; no se enviaron credenciales ni órdenes.",
            "Cada hash identifica el cuerpo JSON recibido; no se duplican aquí las series completas.",
            "Un comienzo temprano y more=true no demuestra continuidad hasta el presente. Usar las capturas por ventanas para verificar tramos concretos.",
            "El catálogo refleja el universo activo observado el 2026-10-02; no es el universo histórico ni confirma elegibilidad de la cuenta.",
        ],
    }
    capture_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    output_dir = root / "data/market_data/history_depth" / capture_id
    output_dir.mkdir(parents=True, exist_ok=False)
    output_path = output_dir / "depth.json"
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Informe guardado: {output_path}")
    for summary in summaries:
        print(f"{summary['series']}: datos {summary['contracts_with_data']}/{summary['contracts_queried']}; mediana {summary['median_history_days']} días; max {summary['max_history_days']} días; truncadas more=true: {summary['responses_with_more_true']}; errores {summary['contracts_with_errors']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
