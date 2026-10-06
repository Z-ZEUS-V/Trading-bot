"""Offline, predeclared risk/reward and margin comparisons; no network or agents."""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import random
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from trading_lab.data import digest, load_market_data, timestamp
from trading_lab.simulator import simulate
from diagnose_strategy_targets import save_json, save_csv, ledger_stats


def quantile(xs, p):
    ys = sorted(xs)
    point = (len(ys) - 1) * p
    low, high = math.floor(point), math.ceil(point)
    return ys[low] + (ys[high] - ys[low]) * (point - low)


def uncertainty(curve, initial, settings, seed):
    # Final marked equity of each UTC calendar day, including zero-trade days.
    days = {}
    for row in curve:
        day = datetime.fromtimestamp(timestamp(row["utc"]) - 1, timezone.utc).date().isoformat()
        days[day] = row["equity_usd"]
    previous = initial
    returns = []
    for equity in days.values():
        returns.append(equity / previous - 1)
        previous = equity
    rng = random.Random(seed)
    n, block = len(returns), settings["block_days"]
    sampled = []
    for _ in range(settings["resamples"]):
        sample = []
        while len(sample) < n:
            at = rng.randrange(n)
            sample.extend(returns[(at + i) % n] for i in range(block))
        sampled.append(math.prod(1 + x for x in sample[:n]) - 1)
    return {"calendar_days": n, "daily_returns": returns,
            "block_days": block, "resamples": settings["resamples"], "seed": seed,
            "same_length_return_percentile_2_5": quantile(sampled, .025),
            "same_length_return_percentile_97_5": quantile(sampled, .975),
            "bootstrap_positive_fraction_not_probability_of_future_profit": sum(x > 0 for x in sampled) / len(sampled)}


def arithmetic():
    rows = []
    for multiplier in (10, 25):
        for margin_fraction in (.01, .02, .05, .10, .20, .40):
            equity = 50
            nominal = equity * margin_fraction * multiplier
            # Fixed same notional at both ends. Hypothetical friction, not calibrated execution.
            costs = nominal * .0014
            for risk in (.001, .0025, .005):
                budget = equity * risk
                reserve = budget * .1
                stop_room = (budget - reserve - costs) / nominal
                rows.append({"nominal_per_margin": multiplier, "hypothetical_25x_not_account_eligible": multiplier == 25,
                             "allocated_margin_fraction": margin_fraction, "allocated_margin_usd": equity * margin_fraction,
                             "notional_usd": nominal, "exposure_over_equity": nominal / equity,
                             "risk_fraction": risk, "target_fraction": .005,
                             "fees_round_trip_usd": nominal * .001,
                             "fees_and_base_friction_round_trip_usd": costs,
                             "funding_reserve_usd": reserve,
                             "approx_price_stop_distance_after_cost_budget": stop_room,
                             "positive_price_stop_budget": stop_room > 0,
                             "approx_price_move_for_net_target": (.25 + costs) / nominal,
                             "fifty_fixed_nominal_round_trips_fees_usd": 50 * nominal * .001,
                             "fifty_fixed_nominal_round_trips_fees_and_friction_usd": 50 * costs})
    return rows


def report(result):
    lines = ["# Riesgo, margen y apalancamiento: comparación registrada", "",
             "Cálculo local. Tres riesgos para TP neto 0,5 %, dos costes y dos periodos. Una posición total. "
             "40 % de margen asignado como máximo; la comisión de entrada también debe dejar 60 % libre al entrar. "
             "El multiplicador 25x es nominal/margen; nominal/equity es otra magnitud.", "",
             "La captura pública de BTC/ETH para europa/retail exige IM 10 % (nominal/margen 10x). "
             "25x solo aparece como aritmética hipotética, sin simular margen regulatorio ficticio. "
             "El saldo libre sigue respaldando pérdidas en cruzado.", "",
             "| Ventana | Caso | Fricción/fill | Ops | Ops/día | Retorno periodo | DD horario | Aciertos | PF | Margen medio/máx. | IC bootstrap del retorno |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for v in result["variants"]:
        s, st, u = v["summary"], v["stats"], v["uncertainty"]
        margin = st["initial_margin_fraction_equity"]
        win = f"{s['win_rate']:.1%}" if s["win_rate"] is not None else "n/a"
        pf = f"{s['profit_factor']:.2f}" if s["profit_factor"] is not None else "n/a"
        m = f"{margin['mean']:.2%}/{margin['max']:.2%}" if s["trades"] else "n/a"
        lines.append(f"| {v['window']} | {v['case']} | {s['slippage_each_fill']*1e4:.0f} pb | {s['trades']} | {st['trades_per_calendar_day']:.2f} | {s['return_fraction']:.2%} | {s['max_hourly_mark_drawdown_fraction']:.2%} | {win} | {pf} | {m} | [{u['same_length_return_percentile_2_5']:.2%}, {u['same_length_return_percentile_97_5']:.2%}] |")
    lines += ["", "El caso principal fija riesgo 0,25 % (R/B 1:2); las sensibilidades usan 0,5 % (1:1) y 0,1 % (1:5). "
              "Ninguna usa un presupuesto de pérdida del 2 %. Los porcentajes de retorno son del periodo completo. "
              "Las pérdidas reales pueden superar un stop presupuestado.", "",
              "## Criterios registrados antes de ejecutar", "",
              "Para continuar como candidata, la principal debe tener al menos 50 operaciones, retorno positivo, PF ≥1,1, "
              "DD horario ≤10 % y extremo inferior bootstrap >0 en cada periodo y coste. "
              "Este filtro permite seguir validando; nunca autoriza operar. "
              "Los criterios concretos son decisiones de investigación, no umbrales universales de rentabilidad.", "",
              f"Caso principal supera todos los filtros: **{result['primary_passes_all_screens']}**.", ""]
    for v in result["variants"]:
        if v["case"] == "primary_rr2":
            lines.append(f"- {v['window']} / {v['cost']}: fallos = {', '.join(v['failed_screens']) or 'ninguno'}.")
    lines += ["", "## Alcance de la evidencia", "",
              "Junio–julio es nuevo para H3, pero ya se observaron esos meses al analizar H1/H2. "
              "No es una reserva completamente intacta del proyecto. Agosto–septiembre no se ejecutó. "
              "Los intervalos son percentiles de remuestreo circular en bloques de siete días (2.000 muestras), "
              "con los días sin operaciones incluidos. Son condicionales a la regla y datos elegidos, no pronósticos "
              "ni correcciones de la selección previa de H3. La dependencia y el régimen de mercado pueden durar más de siete días.", "",
              "Se conservan fills OHLC horarios, funding intrahorario acotado y costes hipotéticos. "
              "No se supone ejecución maker ni se valida una frecuencia de 50 operaciones/día. "
              "Los límites de margen se comprueban al entrar; la ratio puede subir si cae la equity mientras sigue abierta la posición.", "",
              "arithmetic.csv compara nominal, margen, coste y presupuesto restante para stop en los casos 10x y 25x. "
              "No permite convertir el 40 % de margen en una pérdida máxima de cuenta.", "",
              "El cálculo tuvo cero llamadas a modelos, cero tokens, cero peticiones de red y cero órdenes. "
              "La captura pública del catálogo se realizó antes y su manifiesto se conserva por separado.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    source = ROOT / "config/risk_margin_research.json"
    exp = json.loads(source.read_text(encoding="utf-8"))
    base_path = ROOT / exp["base_config"]
    base = json.loads(base_path.read_text(encoding="utf-8"))
    if base["astra_enabled"] or base["live_trading_enabled"]:
        raise ValueError("Only offline research supported")
    base["catalog"] = exp["catalog"]
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    save_json(out / "registered_experiment.json", exp)
    save_json(out / "base_config_with_current_catalog.json", base)
    before = time.perf_counter()
    data = load_market_data(ROOT, base)
    save_json(out / "funding_audit.json", data.provenance)
    variants, controls = [], []
    for wi, window in enumerate(exp["windows"]):
        start, end = timestamp(window["from"]), timestamp(window["to_exclusive"])
        if end > timestamp(base["reserved_not_evaluated"]["from"]):
            raise ValueError("Reserved period must remain untouched")
        for ci, case in enumerate(exp["risk_cases"]):
            for ki, cost in enumerate(base["cost_scenarios"]):
                cfg = deepcopy(base)
                cfg.update({"risk_fraction": case["risk_fraction"],
                            "max_exposure_over_equity": exp["theoretical_max_exposure_over_equity_before_venue_and_risk_limits"],
                            "maximum_nominal_per_allocated_margin": exp["maximum_nominal_per_allocated_margin"],
                            "maximum_allocated_margin_fraction": exp["maximum_allocated_margin_fraction"],
                            "minimum_free_equity_fraction": exp["minimum_free_equity_fraction_after_entry_fee"],
                            "minimum_net_target_to_budgeted_loss": exp["minimum_net_target_to_budgeted_loss"]})
                run = simulate(data, cfg, exp["strategy"], exp["target_fraction"], cost["slippage_each_fill"], start, end)
                s, trades = run["summary"], run["trades"]
                if abs(s["ledger_residual_usd"]) > 1e-8:
                    raise ValueError("Ledger does not balance")
                for t in trades:
                    eq = t["equity_at_entry_usd"]
                    if t["allocated_margin_usd"] > .4 * eq + 1e-8:
                        raise ValueError("Allocated margin cap exceeded")
                    if t["planned_stop_price_loss_and_fees_usd"] + t["funding_budget_usd"] > eq * case["risk_fraction"] + 1e-8:
                        raise ValueError("Planned risk exceeds budget")
                uncertainty_result = uncertainty(run["hourly_equity"], cfg["initial_equity_usd"], exp["bootstrap"], exp["bootstrap"]["seed"] + wi * 100 + ci * 10 + ki)
                gates = exp["screening_gates_for_further_validation"]
                screens = {"enough_trades": s["trades"] >= gates["minimum_trades_each_window_and_cost"],
                           "positive_net_return": s["return_fraction"] > 0,
                           "profit_factor": (s["profit_factor"] or 0) >= gates["minimum_profit_factor_each_window_and_cost"],
                           "drawdown": s["max_hourly_mark_drawdown_fraction"] <= gates["maximum_hourly_mark_drawdown_fraction"],
                           "positive_bootstrap_lower_bound": uncertainty_result["same_length_return_percentile_2_5"] > 0,
                           "valid_run": s["status"] == "exploratory_only"}
                stats = ledger_stats(trades, (end - start) / 86400)
                stats["sizing_binding_limits"] = dict(Counter(t["sizing_binding_limit"] for t in trades))
                counts = Counter(t["entry_utc"][:10] for t in trades)
                stats["max_entries_per_utc_day"] = max(counts.values(), default=0)
                item = {"window": window["id"], "case": case["id"], "cost": cost["name"],
                        "summary": s, "stats": stats, "uncertainty": uncertainty_result,
                        "failed_screens": [k for k, passed in screens.items() if not passed]}
                folder = out / window["id"] / (case["id"] + "_" + cost["name"])
                folder.mkdir(parents=True)
                save_json(folder / "summary.json", item)
                save_json(folder / "effective_config.json", cfg)
                save_csv(folder / "trades.csv", trades)
                save_csv(folder / "hourly_equity.csv.gz", run["hourly_equity"], zipped=True)
                save_json(folder / "events.json", run["events"])
                variants.append(item)
        if window["id"] == "development":
            for cost in base["cost_scenarios"]:
                cfg = deepcopy(base)
                cfg["risk_fraction"] = .005
                c = simulate(data, cfg, exp["strategy"], .005, cost["slippage_each_fill"], start, end)
                oldfile = ROOT / "data/research_runs/20261005_target_frequency_diagnosis_v2/development" / ("H3_1h_target05_risk05_" + cost["name"]) / "summary.json"
                old = json.loads(oldfile.read_text(encoding="utf-8"))
                controls.append({"cost": cost["name"], "old_summary_sha256": digest(oldfile),
                                 "trade_count_matches": old["trades"] == c["summary"]["trades"],
                                 "return_difference": c["summary"]["return_fraction"] - old["return_fraction"]})
    result = {"experiment": exp, "variants": variants, "historical_h3_controls": controls,
              "primary_passes_all_screens": all(not v["failed_screens"] for v in variants if v["case"] == "primary_rr2"),
              "live_promotion_allowed": False}
    save_json(out / "results.json", result)
    save_csv(out / "arithmetic.csv", arithmetic())
    (out / "informe.md").write_text(report(result), encoding="utf-8")
    paths = list((ROOT / "src/trading_lab").glob("*.py")) + [Path(__file__).resolve(), ROOT / "scripts/diagnose_strategy_targets.py", source, base_path]
    save_json(out / "manifest.json", {"created_at_utc": datetime.now(timezone.utc).isoformat(),
              "duration_seconds": time.perf_counter() - before, "model_calls": 0, "model_tokens": 0,
              "network_calls_during_computation": 0, "orders": 0, "reserved_period_evaluated": False,
              "variant_evaluations": len(variants), "historical_control_evaluations": len(controls),
              "input_sha256": data.provenance["inputs_sha256"],
              "code_sha256": {str(p.relative_to(ROOT)): digest(p) for p in paths},
              "output_sha256": {str(p.relative_to(out)): digest(p) for p in sorted(out.rglob("*")) if p.is_file()}})
    print(json.dumps({"output": str(out), "primary_passes": result["primary_passes_all_screens"], "controls": controls,
                      "results": [{"window": v["window"], "case": v["case"], "cost": v["cost"], "return": v["summary"]["return_fraction"], "trades": v["summary"]["trades"]} for v in variants]}))


if __name__ == "__main__":
    main()
