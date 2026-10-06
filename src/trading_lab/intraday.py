"""Minute data validation, closed-bar signals and lagged quoted-cost estimates."""
from __future__ import annotations

import csv
import gzip
import json
import math
from pathlib import Path
import statistics

from .data import Candle, MarketData, digest, load_market_data, timestamp
from .strategies import Signal


def aggregate(minutes: dict[int, Candle], width: int, cutoff: int) -> list[Candle]:
    groups = {}
    for t, c in sorted(minutes.items()):
        if t + 60 <= cutoff:
            groups.setdefault(t // width * width, []).append(c)
    result = []
    for t, rows in sorted(groups.items()):
        if [r.start for r in rows] != list(range(t, t + width, 60)):
            continue
        result.append(Candle(t, rows[0].open, max(r.high for r in rows), min(r.low for r in rows),
                             rows[-1].close, sum(r.volume for r in rows)))
    return result


def intraday_signals(minutes: dict[int, Candle], spec: dict, cutoff: int, delay: int) -> dict[int, Signal]:
    width = spec["bar_seconds"]
    bars = aggregate(minutes, width, cutoff)
    output, tr = {}, []
    needed = max(spec["lookback"] + 1, spec["atr_period"])
    for i, bar in enumerate(bars):
        previous_close = bars[i-1].close if i else bar.open
        tr.append(max(bar.high-bar.low, abs(bar.high-previous_close), abs(bar.low-previous_close)))
        if i < needed or bar.start-bars[i-needed].start != needed*width or bar.volume <= 0 or bars[i-1].volume <= 0:
            continue
        atr = statistics.mean(tr[i-spec["atr_period"]+1:i+1])
        if atr <= 0:
            continue
        past = bars[i-spec["lookback"]-1:i-1]
        excursion = bars[i-1]
        direction, anchor = 0, None
        if spec["kind"] == "confirmed_breakout":
            hi, lo = max(c.high for c in past), min(c.low for c in past)
            if excursion.close > hi and bar.close > hi and bar.close >= excursion.close:
                direction = 1
            elif excursion.close < lo and bar.close < lo and bar.close <= excursion.close:
                direction = -1
        elif spec["kind"] == "band_reentry":
            closes = [c.close for c in past]
            anchor, sd = statistics.mean(closes), statistics.pstdev(closes)
            if sd <= 0:
                continue
            lo, hi = anchor-spec["band_standard_deviations"]*sd, anchor+spec["band_standard_deviations"]*sd
            if excursion.close < lo and lo <= bar.close < anchor:
                direction = 1
            elif excursion.close > hi and anchor < bar.close <= hi:
                direction = -1
        else:
            raise ValueError("Unknown intraday rule")
        if direction:
            available = bar.start + width
            output[available+delay] = Signal(available, direction, atr,
                                             bar.close-direction*spec["stop_atr"]*atr, anchor)
    return output


def load_intraday(root: Path, base: dict, folder: Path) -> tuple[MarketData, dict, dict]:
    # Reuse only the reconciled funding and instrument rules; prices are replaced by real 1m candles.
    prior = load_market_data(root, base)
    manifest_path = folder / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    start, end = timestamp(manifest["from"]), timestamp(manifest["to_exclusive"])
    trade, mark, spreads, audit = {}, {}, {}, {"series": [], "inputs_sha256": dict(prior.provenance["inputs_sha256"])}
    audit["inputs_sha256"][str(manifest_path.relative_to(root))] = digest(manifest_path)
    for meta in manifest["datasets"]:
        symbol, kind = meta["symbol"], meta["kind"]
        if symbol not in base["symbols_priority"]:
            continue
        path = folder / meta["file"]
        if digest(path) != meta["sha256"]:
            raise ValueError("Minute dataset checksum mismatch")
        audit["inputs_sha256"][str(path.relative_to(root))] = digest(path)
        with gzip.open(path, "rt", encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        values = {}
        invalid = []
        for r in rows:
            t = int(r["timestamp"])
            if t in values or not start <= t < end or t % meta["step_seconds"]:
                raise ValueError("Invalid minute timestamp")
            if kind == "spreads":
                if not r["bid"] or not r["ask"]:
                    invalid.append(t); continue
                bid, ask = float(r["bid"]), float(r["ask"])
                if not all(math.isfinite(x) for x in (bid,ask)) or bid <= 0 or ask <= bid:
                    invalid.append(t); continue
                values[t] = (ask-bid)/((ask+bid)/2)
            else:
                o,h,l,c,v = [float(r[k]) for k in ("open","high","low","close","volume")]
                if not all(math.isfinite(x) for x in (o,h,l,c,v)) or min(o,h,l,c) <= 0 or l>min(o,c) or h<max(o,c) or v<0:
                    raise ValueError("Invalid minute OHLC")
                values[t] = Candle(t,o,h,l,c,v)
        missing = [t for t in range(start,end,meta["step_seconds"]) if t not in values]
        if kind != "spreads" and missing:
            raise ValueError(f"Missing real minute candles: {symbol} {kind} {len(missing)}")
        audit["series"].append({"symbol":symbol,"kind":kind,"points":len(values),"missing_or_invalid":len(missing),
                               "first_missing":missing[:10]})
        {"trade":trade,"mark":mark,"spreads":spreads}[kind][symbol] = values
    for s in base["symbols_priority"]:
        if any(s not in part for part in (trade,mark,spreads)):
            raise ValueError("Missing required intraday series")
    return MarketData(trade,mark,prior.funding,prior.instruments,audit,prior.funding_rows), spreads, audit


def quoted_cost(spreads: dict[int,float], t: int, additional: float, measured_walk: float,
                bucket: int = 300, max_age: int = 600) -> float | None:
    # Buckets may include observations throughout the bucket. Use one fully completed bucket.
    latest = t // bucket * bucket - bucket
    for at in range(latest, t-max_age-1, -bucket):
        if at in spreads and t-at <= max_age:
            return spreads[at]/2 + measured_walk + additional
    return None
