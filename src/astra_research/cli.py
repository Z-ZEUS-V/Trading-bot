from __future__ import annotations

import argparse
import json

from .catalog import candidates, initialize, list_strategies


def main() -> None:
    parser = argparse.ArgumentParser(prog="astra-research")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help="Create/update the local SQLite catalog from the versioned JSON")
    listing = sub.add_parser("list", help="List catalog entries without an API call")
    listing.add_argument("--market")
    listing.add_argument("--max-risk", type=int, default=5)
    rec = sub.add_parser("shortlist", help="Filter candidates locally without an API call")
    rec.add_argument("--market", required=True)
    rec.add_argument("--horizon", required=True)
    rec.add_argument("--risk", choices=["low", "moderate", "high", "very_high"], required=True)
    args = parser.parse_args()

    if args.command == "init":
        print(f"Loaded {initialize()} strategy records into the local catalog.")
    elif args.command == "list":
        initialize()
        print(json.dumps(list_strategies(args.market, args.max_risk), ensure_ascii=False, indent=2))
    elif args.command == "shortlist":
        initialize()
        shortlist = candidates(args.market, args.horizon, args.risk)
        print(json.dumps(shortlist, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
