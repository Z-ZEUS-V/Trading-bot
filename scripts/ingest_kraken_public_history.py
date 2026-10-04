"""Download, preserve, and normalize public Kraken Futures chart history."""

from __future__ import annotations

import argparse
import csv
from datetime import UTC, datetime
import gzip
import hashlib
import json
from pathlib import Path
import re
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
CSV_FIELDS = (
    "timestamp_ms", "timestamp_utc", "symbol", "series",
    "open", "high", "low", "close", "volume",
    "rate_open", "rate_high", "rate_low", "rate_close",
    "relative_rate_open", "relative_rate_high", "relative_rate_low", "relative_rate_close",
    "basis",
)


def _time_utc(timestamp_ms: int) -> str:
    return datetime.fromtimestamp(timestamp_ms / 1000, UTC).isoformat(timespec="milliseconds")


def _symbol_safe(symbol: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_-]+", symbol):
        raise ValueError("Símbolo inválido.")
    return symbol


def _url(series: str, symbol: str, start: int, end: int) -> str:
    if series.startswith("candles_"):
        tick_type = series.removeprefix("candles_")
        query = urlencode({"from": start, "to": end})
        return f"{BASE_URL}{CHARTS_PATH}/{tick_type}/{symbol}/1h?{query}"
    analytics = {"funding": "funding", "future_basis": "future-basis"}[series]
    query = urlencode({"since": start, "to": end, "interval": RESOLUTION_SECONDS})
    return f"{BASE_URL}{CHARTS_PATH}/analytics/{symbol}/{analytics}?{query}"


def _fetch(url: str) -> tuple[bytes, dict]:
    request = Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
    with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        raw = response.read()
        return raw, {
            "http_status": response.status,
            "content_type": response.headers.get("Content-Type", ""),
        }


def _get_with_retry(url: str) -> tuple[bytes, dict]:
    for attempt in range(4):
        try:
            return _fetch(url)
        except HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == 3:
                raise
            retry_after = exc.headers.get("Retry-After", "")
            try:
                wait = min(max(float(retry_after), 1.0), 30.0) if retry_after else 2.0 ** attempt
            except ValueError:
                wait = 2.0 ** attempt
            time.sleep(wait)
        except (URLError, TimeoutError, OSError):
            if attempt == 3:
                raise
            time.sleep(2.0 ** attempt)
    raise RuntimeError("No se pudo descargar la respuesta.")


def _analytics_rows(payload: dict, symbol: str, series: str) -> tuple[list[dict], bool, list]:
    result = payload.get("result", {})
    timestamps = result.get("timestamp", [])
    data = result.get("data", {})
    points: list[dict] = []
    for index, raw_timestamp in enumerate(timestamps):
        timestamp = int(raw_timestamp)
        timestamp_ms = timestamp if timestamp > 100_000_000_000 else timestamp * 1000
        row = {"timestamp_ms": timestamp_ms, "timestamp_utc": _time_utc(timestamp_ms), "symbol": symbol, "series": series}
        if series == "funding":
            for field, prefix in (("rate", "rate"), ("relativeRate", "relative_rate")):
                values = data.get(field, [])
                values = values[index] if index < len(values) else []
                for suffix, value in zip(("open", "high", "low", "close"), values):
                    row[f"{prefix}_{suffix}"] = value
        else:
            values = data.get("basis", [])
            row["basis"] = values[index] if index < len(values) else None
        points.append(row)
    return points, bool(result.get("more")), payload.get("errors", [])


def _candle_rows(payload: dict, symbol: str, series: str) -> tuple[list[dict], bool, list]:
    points = []
    for candle in payload.get("candles", []):
        timestamp_ms = int(candle["time"])
        points.append(
            {
                "timestamp_ms": timestamp_ms,
                "timestamp_utc": _time_utc(timestamp_ms),
                "symbol": symbol,
                "series": series,
                "open": candle.get("open"),
                "high": candle.get("high"),
                "low": candle.get("low"),
                "close": candle.get("close"),
                "volume": candle.get("volume"),
            }
        )
    return points, bool(payload.get("more_candles")), []


def _gap_summary(timestamps: list[int]) -> tuple[int, int, list[dict]]:
    ordered = sorted(set(timestamps))
    gaps = []
    missing = 0
    step = RESOLUTION_SECONDS * 1000
    for left, right in zip(ordered, ordered[1:]):
        delta = right - left
        if delta > step:
            absent = max(0, delta // step - 1)
            missing += absent
            gaps.append({"after_utc": _time_utc(left), "before_utc": _time_utc(right), "missing_hour_buckets": absent})
    return len(gaps), missing, gaps


def ingest(symbols: list[str], days: int, chunk_days: int, output_root: Path, catalog_path: Path | None) -> Path:
    now = int(time.time())
    end = now - (now % RESOLUTION_SECONDS)
    start = end - days * 86400
    chunk_seconds = chunk_days * 86400
    capture_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    run_dir = output_root / "datasets" / capture_id
    (run_dir / "raw").mkdir(parents=True, exist_ok=False)
    catalog_rows = {}
    if catalog_path:
        catalog_payload = json.loads(catalog_path.read_text(encoding="utf-8"))
        catalog_rows = {item.get("symbol"): item for item in catalog_payload.get("instruments", []) if isinstance(item, dict)}

    datasets = []
    for symbol_input in symbols:
        symbol = _symbol_safe(symbol_input)
        for series in ("candles_trade", "candles_mark", "funding", "future_basis"):
            rows_by_timestamp: dict[int, dict] = {}
            chunk_manifest = []
            cursor = start
            while cursor < end:
                chunk_end = min(cursor + chunk_seconds, end)
                request_url = _url(series, symbol, cursor, chunk_end)
                chunk_meta = {
                    "requested_from_utc": datetime.fromtimestamp(cursor, UTC).isoformat(timespec="seconds"),
                    "requested_to_utc": datetime.fromtimestamp(chunk_end, UTC).isoformat(timespec="seconds"),
                    "source": request_url,
                }
                try:
                    raw, http = _get_with_retry(request_url)
                    payload = json.loads(raw)
                    parser = _candle_rows if series.startswith("candles_") else _analytics_rows
                    points, more, errors = parser(payload, symbol, series)
                    chunk_meta.update(http)
                    chunk_meta.update(
                        {
                            "response_sha256": hashlib.sha256(raw).hexdigest(),
                            "point_count": len(points),
                            "first_point_utc": points[0]["timestamp_utc"] if points else None,
                            "last_point_utc": points[-1]["timestamp_utc"] if points else None,
                            "more": more,
                            "errors": errors,
                        }
                    )
                    raw_name = f"{symbol}_{series}_{cursor}_{chunk_end}.json.gz"
                    raw_dir = run_dir / "raw" / symbol
                    raw_dir.mkdir(parents=True, exist_ok=True)
                    with gzip.open(raw_dir / raw_name, "wb", compresslevel=6) as raw_file:
                        raw_file.write(raw)
                    chunk_meta["raw_response_file"] = str(Path("raw") / symbol / raw_name)
                    for point in points:
                        rows_by_timestamp[point["timestamp_ms"]] = point
                except HTTPError as exc:
                    chunk_meta.update({"http_status": exc.code, "error": f"HTTP {exc.code}"})
                except (URLError, TimeoutError, OSError) as exc:
                    chunk_meta["error"] = f"network:{type(exc).__name__}"
                except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
                    chunk_meta["error"] = f"invalid_response:{type(exc).__name__}"
                chunk_manifest.append(chunk_meta)
                cursor = chunk_end
                time.sleep(REQUEST_PAUSE_SECONDS)

            rows = [rows_by_timestamp[ts] for ts in sorted(rows_by_timestamp)]
            gaps, missing, gap_list = _gap_summary([row["timestamp_ms"] for row in rows])
            dataset_dir = run_dir / "normalized"
            dataset_dir.mkdir(exist_ok=True)
            dataset_path = dataset_dir / f"{symbol}_{series}.csv.gz"
            with gzip.open(dataset_path, "wt", encoding="utf-8", newline="", compresslevel=6) as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(rows)
            csv_sha256 = hashlib.sha256(dataset_path.read_bytes()).hexdigest()
            instrument = catalog_rows.get(symbol, {})
            datasets.append(
                {
                    "symbol": symbol,
                    "series": series,
                    "requested_from_utc": datetime.fromtimestamp(start, UTC).isoformat(timespec="seconds"),
                    "requested_to_utc": datetime.fromtimestamp(end, UTC).isoformat(timespec="seconds"),
                    "resolution_seconds": RESOLUTION_SECONDS,
                    "point_count": len(rows),
                    "first_point_utc": rows[0]["timestamp_utc"] if rows else None,
                    "last_point_utc": rows[-1]["timestamp_utc"] if rows else None,
                    "gap_count": gaps,
                    "missing_hour_buckets_between_points": missing,
                    "gaps": gap_list,
                    "csv_gzip_file": str(dataset_path.relative_to(run_dir)),
                    "csv_gzip_sha256": csv_sha256,
                    "contract_metadata": {key: instrument.get(key) for key in ("type", "base", "quote", "pair", "openingDate", "expiry", "isExpired", "tradfi", "contractSize", "tickSize")},
                    "chunks": chunk_manifest,
                }
            )

    manifest = {
        "captured_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "source": f"{BASE_URL}{CHARTS_PATH}",
        "symbols": symbols,
        "requested_days": days,
        "chunk_days": chunk_days,
        "resolution_seconds": RESOLUTION_SECONDS,
        "normalization": "One timestamp per hourly point; analytics series expanded into scalar CSV columns; duplicate boundary timestamps keep the last observation. No filling or interpolation.",
        "credentials_used": False,
        "orders_sent": False,
        "catalog_source": str(catalog_path) if catalog_path else None,
        "datasets": datasets,
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return run_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Descarga y normaliza series públicas horarias de Kraken Derivatives.")
    parser.add_argument("--symbols", default="PF_XBTUSD,PF_ETHUSD", help="Símbolos separados por coma.")
    parser.add_argument("--days", type=int, default=365)
    parser.add_argument("--chunk-days", type=int, default=30)
    parser.add_argument("--output-dir", type=Path, default=Path("data/market_data"))
    parser.add_argument("--catalog", type=Path, default=Path("data/market_data/instruments/20261002T001640Z/response.json"))
    args = parser.parse_args()
    symbols = [item.strip() for item in args.symbols.split(",") if item.strip()]
    if not symbols or args.days < 1 or args.chunk_days < 1:
        parser.error("Indica al menos un símbolo y valores positivos para --days y --chunk-days.")
    try:
        run_dir = ingest(symbols, args.days, args.chunk_days, args.output_dir, args.catalog if args.catalog.exists() else None)
        manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"Error al preparar la ingesta pública ({type(exc).__name__}).", file=sys.stderr)
        return 1
    print(f"Ingesta guardada: {run_dir}")
    for item in manifest["datasets"]:
        failed = sum("error" in chunk for chunk in item["chunks"])
        print(
            f"{item['symbol']} {item['series']}: {item['point_count']} puntos; "
            f"{item['gap_count']} huecos; errores de consulta={failed}; "
            f"{item['first_point_utc']} to {item['last_point_utc']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
