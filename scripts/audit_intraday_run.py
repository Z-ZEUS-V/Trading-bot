"""Offline provenance, candle reconciliation and ledger diagnosis; never tunes signals."""
from __future__ import annotations
import argparse
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from trading_lab.data import digest, load_market_data, timestamp, utc
from trading_lab.intraday import load_intraday, aggregate


def read_rows(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", type=Path, required=True)
    p.add_argument("--data", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    run, folder, out = args.run.resolve(), args.data.resolve(), args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    result = json.loads((run / "results.json").read_text(encoding="utf-8"))
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    checked = 0
    for category, base in (("input_sha256", ROOT), ("code_sha256", ROOT), ("output_sha256", run)):
        for path, sha in manifest[category].items():
            if digest(base / path) != sha:
                raise ValueError(f"Hash mismatch: {category} {path}")
            checked += 1
    raw_manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    raw_count = 0
    for dataset in raw_manifest["datasets"]:
        for request in dataset["requests"]:
            raw = gzip.decompress((folder / request["raw_file"]).read_bytes())
            if hashlib.sha256(raw).hexdigest() != request["response_sha256"]:
                raise ValueError("Raw history checksum mismatch")
            raw_count += 1
    base = json.loads((ROOT / result["experiment"]["base_config"]).read_text(encoding="utf-8"))
    base["catalog"] = result["experiment"]["catalog"]
    hourly = load_market_data(ROOT, base)
    minute, _, _ = load_intraday(ROOT, base, folder)
    end = timestamp(raw_manifest["to_exclusive"])
    reconciled = []
    for symbol in base["symbols_priority"]:
        for kind in ("trade", "mark"):
            bars = aggregate(getattr(minute, kind)[symbol], 3600, end)
            differences, examples = [], []
            for bar in bars:
                old = getattr(hourly, kind)[symbol][bar.start]
                differences.append(max(abs(getattr(bar, key) - getattr(old, key)) for key in ("open", "high", "low", "close")))
                if differences[-1] > 1e-7 and len(examples) < 5:
                    examples.append({"utc": utc(bar.start), "max_price_difference": differences[-1]})
            reconciled.append({"symbol": symbol, "kind": kind, "hours": len(bars),
                               "ohlc_differences_over_1e_7": sum(x > 1e-7 for x in differences),
                               "max_price_difference": max(differences), "examples": examples})
    variants = []
    for row in result["variants"]:
        path = run / row["window"] / (row["case"] + "_" + row["cost"])
        trades = read_rows(path / "trades.csv")
        curve = read_rows(path / "minute_equity.csv.gz")
        first_dd = next((r["utc"] for r in curve if float(r["drawdown_fraction"]) > .1), None)
        for trade in trades:
            gross = int(trade["direction"]) * float(trade["quantity_base"]) * (float(trade["exit_reference"]) - float(trade["entry_reference"]))
            net = gross - float(trade["fill_friction_usd_already_in_gross"]) - float(trade["fees_usd"]) + float(trade["funding_cashflow_usd"])
            if not math.isclose(net, float(trade["net_pnl_usd"]), abs_tol=1e-9):
                raise ValueError("Independent reference-price ledger reconciliation failed")
        variants.append({"window": row["window"], "case": row["case"], "cost": row["cost"],
                         "first_mark_drawdown_over_ten_percent": first_dd,
                         "minimum_realized_net_return_on_entry_equity": min((float(t["net_return_on_entry_equity"]) for t in trades), default=None),
                         "mean_fee_fraction_entry_equity": sum(float(t["fees_usd"]) / float(t["equity_at_entry_usd"]) for t in trades) / len(trades) if trades else None,
                         "mean_friction_fraction_entry_equity": sum(float(t["fill_friction_usd_already_in_gross"]) / float(t["equity_at_entry_usd"]) for t in trades) / len(trades) if trades else None,
                         "maximum_nominal_to_allocated_margin": max((float(t["nominal_over_allocated_margin"]) for t in trades), default=None)})
    payload = {"run": str(run.relative_to(ROOT)), "run_manifest_sha256": digest(run / "manifest.json"),
               "script_sha256": digest(Path(__file__)), "verified_manifest_hashes": checked,
               "verified_raw_history_responses": raw_count,
               "hourly_ohlc_reconciliation": reconciled, "ledger_diagnostics": variants,
               "interpretation": "Diagnostics of fixed recorded paths, not new strategy trials. A 10% drawdown is a screening threshold, not an active kill switch in these replays."}
    (out / "audit.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=True))


if __name__ == "__main__":
    main()
