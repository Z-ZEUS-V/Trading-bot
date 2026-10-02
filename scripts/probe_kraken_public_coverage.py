"""Measure public candles, funding, and basis coverage in bounded windows."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


BASE_URL = "https://futures.kraken.com"
CHARTS_PATH = "/api/charts/v1"
RESOLUTION_SECONDS = 3600
USER_AGENT = "AstraTradingResearch/0.1 (public market-data research)"
TIMEOUT_SECONDS = 30
REQUEST_PAUSE_SECONDS = 0.15
CRYPTO_CATEGORIES = {
    "AI", "Community", "DeFi", "DEX", "DePIN", "Gaming", "Infrastructure",
    "Layer 1", "Layer 2", "Meme", "Privacy", "Real-world assets", "Stablecoin",
    "Utility", "Web3",
}
INVERSE_CRYPTO_BASES = {"BTC", "ETH", "LTC", "XRP"}


def _get_json(url: str) -> tuple[bytes, dict]:
    request = Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
    with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}")
        return response.read(), {"http_status": response.status, "content_type": response.headers.get("Content-Type", "")}


def _time_utc(timestamp: int | None) -> str | None:
    if timestamp is None:
        return None
    seconds = timestamp / 1000 if timestamp > 100_000_000_000 else timestamp
    return datetime.fromtimestamp(seconds, UTC).isoformat(timespec="seconds")


def _probe_one(url: str, series: str, symbol: str, start: int, end: int) -> dict:
    base = {
        "series": series,
        "symbol": symbol,
        "requested_from_utc": _time_utc(start),
        "requested_to_utc": _time_utc(end),
        "requested_interval_seconds": RESOLUTION_SECONDS,
    }
    try:
        raw, http = _get_json(url)
        payload = json.loads(raw)
    except HTTPError as exc:
        return {**base, "http_status": exc.code, "error": f"HTTP {exc.code}"}
    except (URLError, TimeoutError, OSError) as exc:
        return {**base, "error": f"network: {type(exc).__name__}"}
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {**base, "error": "invalid_json"}
    except RuntimeError as exc:
        return {**base, "error": str(exc)}

    if series.startswith("candles_"):
        points = payload.get("candles", [])
        timestamps = [int(row["time"]) for row in points if isinstance(row, dict) and row.get("time") is not None]
        more = payload.get("more_candles")
        errors = []
    else:
        result = payload.get("result", {})
        timestamps = [int(ts) for ts in result.get("timestamp", [])]
        more = result.get("more")
        errors = payload.get("errors", [])

    timestamps_ms = sorted({ts if ts > 100_000_000_000 else ts * 1000 for ts in timestamps})
    return {
        **base,
        **http,
        "response_sha256": hashlib.sha256(raw).hexdigest(),
        "point_count": len(timestamps_ms),
        "first_point_utc": _time_utc(timestamps_ms[0]) if timestamps_ms else None,
        "last_point_utc": _time_utc(timestamps_ms[-1]) if timestamps_ms else None,
        "more": more,
        "errors": errors,
        "timestamps_ms": timestamps_ms,
    }


def _requests(symbol: str, start: int, end: int) -> list[tuple[str, str]]:
    requests: list[tuple[str, str]] = []
    for tick_type in ("trade", "mark"):
        query = urlencode({"from": start, "to": end})
        url = f"{BASE_URL}{CHARTS_PATH}/{tick_type}/{symbol}/1h?{query}"
        requests.append((f"candles_{tick_type}", url))
    for analytics_type in ("funding", "future-basis"):
        query = urlencode({"since": start, "to": end, "interval": RESOLUTION_SECONDS})
        url = f"{BASE_URL}{CHARTS_PATH}/analytics/{symbol}/{analytics_type}?{query}"
        requests.append((analytics_type, url))
    return requests


def probe(symbols: list[str], days: int, chunk_days: int) -> dict:
    now = int(time.time())
    end = now - (now % RESOLUTION_SECONDS)
    start = end - days * 86400
    chunk_seconds = chunk_days * 86400
    observations: list[dict] = []
    for symbol in symbols:
        window_start = start
        while window_start < end:
            window_end = min(window_start + chunk_seconds, end)
            for series, url in _requests(symbol, window_start, window_end):
                observations.append(_probe_one(url, series, symbol, window_start, window_end))
                time.sleep(REQUEST_PAUSE_SECONDS)
            window_start = window_end

    summaries = []
    groups: dict[tuple[str, str], list[dict]] = {}
    for observation in observations:
        groups.setdefault((observation["symbol"], observation["series"]), []).append(observation)
    for (symbol, series), chunks in sorted(groups.items()):
        all_points = sorted({ts for chunk in chunks for ts in chunk.get("timestamps_ms", [])})
        gaps = []
        missing = 0
        for left, right in zip(all_points, all_points[1:]):
            delta = right - left
            if delta > RESOLUTION_SECONDS * 1000:
                missing_here = max(0, delta // (RESOLUTION_SECONDS * 1000) - 1)
                gaps.append({"after_utc": _time_utc(left), "before_utc": _time_utc(right), "missing_hour_buckets": missing_here})
                missing += missing_here
        summaries.append(
            {
                "symbol": symbol,
                "series": series,
                "requested_days": days,
                "point_count": len(all_points),
                "first_point_utc": _time_utc(all_points[0]) if all_points else None,
                "last_point_utc": _time_utc(all_points[-1]) if all_points else None,
                "missing_hour_buckets_between_points": missing,
                "gap_count": len(gaps),
                "gaps": gaps,
                "chunk_count": len(chunks),
                "chunks_with_more": sum(chunk.get("more") is True for chunk in chunks),
                "chunk_errors": [chunk for chunk in chunks if chunk.get("error") or chunk.get("errors")],
            }
        )
    return {
        "captured_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "source": f"{BASE_URL}{CHARTS_PATH}",
        "symbols": symbols,
        "requested_days": days,
        "chunk_days": chunk_days,
        "resolution_seconds": RESOLUTION_SECONDS,
        "series": ["candles_trade", "candles_mark", "funding", "future-basis"],
        "observations": observations,
        "summaries": summaries,
        "notes": [
            "Solo endpoints públicos; no se envió API key ni se consultó una cuenta.",
            "Los hashes identifican cada respuesta; no se guardan aquí todos los datos de mercado.",
            "Los huecos cuentan saltos mayores de una hora entre puntos y deben revisarse contra ventanas de mercado y semántica del endpoint.",
        ],
    }


def active_crypto_perpetual_symbols(catalog_path: Path) -> tuple[list[str], dict]:
    payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    accepted_types = {"flexible_futures", "futures_inverse"}
    selected = []
    for item in payload.get("instruments", []):
        symbol = item.get("symbol", "")
        if (
            isinstance(symbol, str)
            and symbol.startswith(("PF_", "PI_"))
            and item.get("type") in accepted_types
            and item.get("tradeable") is True
            and item.get("isExpired") is not True
            and item.get("tradfi") is not True
            and item.get("expiry") in (None, "")
            and (
                item.get("category") in CRYPTO_CATEGORIES
                or (
                    item.get("category") in (None, "")
                    and symbol.startswith("PI_")
                    and item.get("base") in INVERSE_CRYPTO_BASES
                )
            )
        ):
            selected.append(item)
    selected.sort(key=lambda item: item["symbol"])
    symbols = [item["symbol"] for item in selected]
    criteria = {
        "catalog": str(catalog_path),
        "filters": [
            "symbol starts with PF_ or PI_",
            "type is flexible_futures or futures_inverse",
            "tradeable is true",
            "isExpired is not true",
            "tradfi is not true",
            "expiry is empty",
            f"category is in crypto categories: {sorted(CRYPTO_CATEGORIES)}",
            "blank category accepted only for inverse BTC/ETH/LTC/XRP contracts",
        ],
        "candidate_count": len(symbols),
        "symbols": symbols,
        "note": "Public catalog proxy for currently listed crypto perpetuals; not account eligibility or historical universe membership.",
    }
    return symbols, criteria


def main() -> int:
    parser = argparse.ArgumentParser(description="Sondea cobertura pública de velas, funding y basis de Kraken Derivatives.")
    parser.add_argument("--symbols", default="PF_XBTUSD,PF_ETHUSD", help="Símbolos separados por coma.")
    parser.add_argument("--days", type=int, default=365, help="Días que se investigan (por defecto: 365).")
    parser.add_argument("--chunk-days", type=int, default=30, help="Tamaño acotado de cada consulta (por defecto: 30).")
    parser.add_argument("--output-dir", type=Path, default=Path("data/market_data"))
    parser.add_argument("--all-active-crypto-perps", action="store_true", help="Deriva símbolos PF_/PI_ activos del snapshot completo del catálogo.")
    parser.add_argument("--catalog", type=Path, default=Path("data/market_data/instruments/20261002T001640Z/response.json"))
    parser.add_argument("--compact", action="store_true", help="Guarda resúmenes y hashes sin arrays horarios extensos.")
    parser.add_argument("--summary-only", action="store_true", help="Imprime un resumen agregado, sin una línea por contrato.")
    args = parser.parse_args()
    universe = None
    if args.all_active_crypto_perps:
        if not args.catalog.exists():
            parser.error(f"No se encuentra el snapshot de catálogo: {args.catalog}")
        symbols, universe = active_crypto_perpetual_symbols(args.catalog)
    else:
        symbols = [item.strip() for item in args.symbols.split(",") if item.strip()]
    if not symbols or args.days < 1 or args.chunk_days < 1:
        parser.error("Indica al menos un símbolo y valores positivos para --days y --chunk-days.")
    try:
        report = probe(symbols, args.days, args.chunk_days)
    except Exception as exc:  # Report a sanitized failure; never echo request URLs with any user data.
        print(f"No se pudo completar el sondeo público ({type(exc).__name__}).", file=sys.stderr)
        return 1
    if universe:
        report["universe_selection"] = universe
    if args.compact:
        for observation in report["observations"]:
            observation.pop("timestamps_ms", None)
    capture_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    output_dir = args.output_dir / "coverage" / capture_id
    output_dir.mkdir(parents=True, exist_ok=False)
    output_path = output_dir / "coverage.json"
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Informe guardado: {output_path}")
    if args.summary_only:
        for series in report["series"]:
            items = [item for item in report["summaries"] if item["series"] == series]
            available = sum(item["point_count"] > 0 for item in items)
            failed = sum(bool(item["chunk_errors"]) for item in items)
            gaps = sum(item["gap_count"] for item in items)
            counts = sorted(item["point_count"] for item in items)
            median = counts[len(counts) // 2] if counts else 0
            print(f"{series}: datos en {available}/{len(items)} contratos; mediana={median} puntos; contratos con errores={failed}; huecos horarios={gaps}")
    else:
        for item in report["summaries"]:
            print(
                f"{item['symbol']} {item['series']}: {item['point_count']} puntos; "
                f"{item['gap_count']} huecos; desde {item['first_point_utc']} hasta {item['last_point_utc']}; "
                f"chunks con more=true: {item['chunks_with_more']}"
            )
            if item["chunk_errors"]:
                print(f"  Respuestas con error documentadas: {len(item['chunk_errors'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
