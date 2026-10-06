"""Public-only minute history and bounded book measurements. No credentials or orders."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from trading_lab.data import timestamp, utc, digest

LOCK = threading.Lock()
NEXT_REQUEST = 0.0


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def fetch(url):
    global NEXT_REQUEST
    for attempt in range(4):
        with LOCK:
            time.sleep(max(0, NEXT_REQUEST - time.monotonic()))
            NEXT_REQUEST = time.monotonic() + .2
        start = time.perf_counter()
        try:
            req = Request(url, headers={"User-Agent": "TradingLabPublicResearch/0.1", "Accept": "application/json"})
            with urlopen(req, timeout=25) as response:
                raw = response.read()
                http = response.status
            return raw, {"http_status": http, "round_trip_ms": (time.perf_counter() - start) * 1000,
                         "captured_at_utc": datetime.now(timezone.utc).isoformat(),
                         "response_sha256": hashlib.sha256(raw).hexdigest()}
        except HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504) or attempt == 3:
                raise
            time.sleep(min(30, max(2 ** attempt, float(e.headers.get("Retry-After", 1)))))
        except (URLError, TimeoutError, OSError):
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError("Fetch exhausted")


def write_csv(path, rows):
    if not rows:
        raise ValueError("Empty dataset")
    with gzip.open(path, "wt", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def capture_history(out, spec, symbols):
    start, end = timestamp(spec["data_from"]), timestamp(spec["data_to_exclusive"])
    def series(symbol, kind):
        step = 300 if kind == "spreads" else 60
        chunk_seconds = 86400 if kind != "spreads" else 5 * 86400
        points, requests, duplicates = {}, [], 0
        rawdir = out / "raw" / symbol / kind
        rawdir.mkdir(parents=True)
        for left in range(start, end, chunk_seconds):
            right = min(left + chunk_seconds, end)
            query = {"since": left, "to": right - 1, "interval": 300} if kind == "spreads" else {"from": left, "to": right - 1}
            route = f"analytics/{symbol}/spreads" if kind == "spreads" else f"{kind}/{symbol}/1m"
            url = "https://futures.kraken.com/api/charts/v1/" + route + "?" + urlencode(query)
            raw, meta = fetch(url)
            payload = json.loads(raw)
            file = rawdir / f"{left}_{right}.json.gz"
            file.write_bytes(gzip.compress(raw, compresslevel=6))
            meta.update({"source": url, "raw_file": str(file.relative_to(out)), "from": utc(left), "to_exclusive": utc(right)})
            requests.append(meta)
            if kind == "spreads":
                r = payload["result"]
                if r.get("more") or payload.get("errors"):
                    raise ValueError(f"Truncated or erroneous analytics: {symbol} {left}")
                times = r["timestamp"]
                bids, asks = r["data"]["bid"]["best_price"], r["data"]["ask"]["best_price"]
                if len(times) != len(bids) or len(times) != len(asks):
                    raise ValueError("Analytics arrays differ in length")
                rows = [{"timestamp": int(t), "bid": b, "ask": a} for t, b, a in zip(times, bids, asks)]
            else:
                if payload.get("more_candles"):
                    raise ValueError(f"Truncated minute candle request: {symbol} {left}")
                rows = [{"timestamp": int(c["time"]) // 1000, **{k: c[k] for k in ("open", "high", "low", "close", "volume")}} for c in payload["candles"]]
            for row in rows:
                t = row["timestamp"]
                if not left <= t < right:
                    continue
                if t % step:
                    raise ValueError("Off-grid timestamp")
                if t in points:
                    duplicates += 1
                    if row != points[t]:
                        raise ValueError("Conflicting duplicate data")
                points[t] = row
        ordered = [points[t] for t in sorted(points)]
        invalid, zero_volume = [], 0
        for row in ordered:
            if kind == "spreads":
                if row["bid"] is None or row["ask"] is None:
                    invalid.append(row["timestamp"])
                    continue
                b, a = float(row["bid"]), float(row["ask"])
                if not all(math.isfinite(x) for x in (b, a)) or b <= 0 or a <= b:
                    invalid.append(row["timestamp"])
            else:
                o, h, l, c, v = [float(row[k]) for k in ("open", "high", "low", "close", "volume")]
                if not all(math.isfinite(x) for x in (o, h, l, c, v)) or min(o,h,l,c) <= 0 or v < 0 or l > min(o,c) or h < max(o,c):
                    invalid.append(row["timestamp"])
                zero_volume += v == 0
        missing = [t for t in range(start, end, step) if t not in points]
        file = out / f"{symbol}_{kind}.csv.gz"
        write_csv(file, ordered)
        meta = {"symbol": symbol, "kind": kind, "step_seconds": step, "points": len(points),
                "expected_points": (end-start)//step, "missing_count": len(missing), "missing_timestamps": missing,
                "invalid_count": len(invalid), "invalid_timestamps": invalid, "duplicates": duplicates,
                "zero_volume_bars": zero_volume, "file": file.name, "sha256": digest(file), "requests": requests}
        save(out / f"{symbol}_{kind}_manifest.json", meta)
        print(json.dumps({k:meta[k] for k in ("symbol","kind","points","missing_count","invalid_count")}), flush=True)
        return meta
    jobs = [(s,k) for s in symbols for k in ("trade","mark","spreads")]
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda job: series(*job), jobs))
    save(out / "manifest.json", {"captured_at_utc": datetime.now(timezone.utc).isoformat(),
          "config_sha256": digest(ROOT / "config/intraday_research.json"), "from": utc(start), "to_exclusive": utc(end),
          "datasets": results, "network_requests": sum(len(x["requests"]) for x in results),
          "orders": 0, "credentials_used": False, "synthetic_gap_filling": False})


def walk(levels, quantity):
    remaining, value = quantity, 0.0
    for price, size in levels:
        used = min(remaining, size)
        value += used * price
        remaining -= used
        if remaining <= 1e-12:
            return value / quantity
    raise ValueError("Insufficient displayed depth")


def capture_books(out, spec, symbols):
    cfg = spec["book_measurement"]
    records, measures = [], []
    (out / "raw").mkdir()
    for i in range(cfg["samples_per_symbol"]):
        began = time.monotonic()
        for symbol in symbols:
            url = "https://futures.kraken.com/derivatives/api/v3/orderbook?" + urlencode({"symbol": symbol})
            raw, meta = fetch(url)
            p = json.loads(raw)
            if p.get("result") != "success":
                raise ValueError("Orderbook failed")
            # REST bids may arrive ascending: sort explicitly before walking.
            bids = sorted([(float(a),float(b)) for a,b in p["orderBook"]["bids"] if float(b)>0], reverse=True)
            asks = sorted([(float(a),float(b)) for a,b in p["orderBook"]["asks"] if float(b)>0])
            if not bids or not asks or bids[0][0] >= asks[0][0]:
                raise ValueError("Invalid/crossed public book")
            if not all(math.isfinite(x) and x>0 for levels in (bids,asks) for pair in levels for x in pair):
                raise ValueError("Invalid public book level")
            mid = (bids[0][0]+asks[0][0])/2
            file = out / "raw" / f"{i:03}_{symbol}.json.gz"
            file.write_bytes(gzip.compress(raw))
            records.append({**meta,"symbol":symbol,"sample":i,"server_time":p["serverTime"],"source":url,"file":str(file.relative_to(out))})
            for nominal in cfg["notionals_usd"]:
                quantity = nominal/mid
                buy, sell = walk(asks,quantity), walk(bids,quantity)
                measures.append({"symbol":symbol,"sample":i,"server_time":p["serverTime"],"notional_usd":nominal,
                    "mid":mid,"full_spread_fraction":(asks[0][0]-bids[0][0])/mid,
                    "buy_total_fraction_from_mid":buy/mid-1,"sell_total_fraction_from_mid":1-sell/mid,
                    "buy_walk_fraction_beyond_best":max(0,(buy-asks[0][0])/mid),
                    "sell_walk_fraction_beyond_best":max(0,(bids[0][0]-sell)/mid),"http_round_trip_ms":meta["round_trip_ms"]})
        if i+1 < cfg["samples_per_symbol"]:
            time.sleep(max(0,cfg["seconds_between_rounds"]-(time.monotonic()-began)))
    def p95(xs):
        return sorted(xs)[math.ceil(.95*len(xs))-1]
    summary = {}
    for s in symbols:
        summary[s] = {}
        for n in cfg["notionals_usd"]:
            rows = [r for r in measures if r["symbol"]==s and r["notional_usd"]==n]
            summary[s][str(n)]={"count":len(rows),"median_spread_bps":statistics.median(r["full_spread_fraction"] for r in rows)*1e4,
                "p95_spread_bps":p95([r["full_spread_fraction"] for r in rows])*1e4,
                "p95_walk_beyond_best_fraction":p95([max(r["buy_walk_fraction_beyond_best"],r["sell_walk_fraction_beyond_best"]) for r in rows]),
                "max_walk_beyond_best_fraction":max(max(r["buy_walk_fraction_beyond_best"],r["sell_walk_fraction_beyond_best"]) for r in rows),
                "median_http_round_trip_ms":statistics.median(r["http_round_trip_ms"] for r in rows)}
    write_csv(out / "measurements.csv.gz",measures)
    save(out / "summary.json",summary)
    save(out / "manifest.json", {"captured_at_utc":datetime.now(timezone.utc).isoformat(),"observations":records,
         "network_requests":len(records),"config_sha256":digest(ROOT / "config/intraday_research.json"),
         "measurements_sha256":digest(out / "measurements.csv.gz"),"summary_sha256":digest(out / "summary.json"),
         "notes":["Displayed liquidity only; no actual fills, cancellation risk or latency slippage measured.",
                  "HTTP round-trip time is not exchange order latency. A minute-long sample is not representative of every market regime.",
                  "Book sizes are base quantity for the selected linear contracts; query sizes are hypothetical."],"orders":0})
    print(json.dumps(summary),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode",choices=("history","books"))
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    spec=json.loads((ROOT / "config/intraday_research.json").read_text(encoding="utf-8"))
    base=json.loads((ROOT/spec["base_config"]).read_text(encoding="utf-8"))
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    save(out / "capture_plan.json",spec)
    (capture_history if args.mode=="history" else capture_books)(out,spec,base["symbols_priority"])


if __name__ == "__main__":
    main()
