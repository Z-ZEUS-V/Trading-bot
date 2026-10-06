"""Diagnose existing trade ledgers and replay predeclared target/risk variants.

Offline, standard library only. New strategy replays use development data only.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from trading_lab.data import HOUR, digest, load_market_data, timestamp, utc
from trading_lab.simulator import fill, simulate


def save_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def save_csv(path: Path, rows: list[dict], zipped: bool = False) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    opener = gzip.open if zipped else open
    with opener(path, "wt", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def read_trades(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def distribution(values: list[float]) -> dict:
    return {"count": len(values), "mean": statistics.mean(values) if values else None,
            "median": statistics.median(values) if values else None,
            "min": min(values) if values else None, "max": max(values) if values else None}


def ledger_stats(trades: list[dict], days: float) -> dict:
    def values(key: str) -> list[float]:
        return [float(t[key]) for t in trades]
    net = values("net_pnl_usd")
    gross = sum(values("gross_pnl_after_fill_friction_usd"))
    friction = sum(values("fill_friction_usd_already_in_gross"))
    fees = sum(values("fees_usd"))
    funding = sum(values("funding_cashflow_usd"))
    gains = [x for x in net if x > 0]
    losses = [-x for x in net if x < 0]
    return {
        "trades": len(trades), "calendar_days": days, "trades_per_calendar_day": len(trades) / days,
        "gross_at_reference_prices_usd": gross + friction,
        "friction_already_in_gross_usd": friction, "fees_usd": fees, "funding_usd": funding,
        "net_pnl_usd": sum(net), "average_win_usd": statistics.mean(gains) if gains else None,
        "average_loss_usd": statistics.mean(losses) if losses else None,
        "exposure_over_equity": distribution(values("exposure_over_equity_at_entry")),
        "initial_margin_fraction_equity": distribution([float(t["initial_margin_usd"]) / float(t["equity_at_entry_usd"]) for t in trades]),
        "planned_loss_including_funding_budget_fraction": distribution([(float(t["planned_stop_price_loss_and_fees_usd"]) + float(t["funding_budget_usd"])) / float(t["equity_at_entry_usd"]) for t in trades]),
        "initial_stop_price_distance_fraction": distribution([abs(float(t["entry_fill"]) - float(t["initial_stop"])) / float(t["entry_fill"]) for t in trades]),
        "holding_hours_upper": distribution([(timestamp(t["exit_latest_utc"]) - timestamp(t["entry_utc"])) / HOUR for t in trades]),
        "exit_reasons": dict(Counter(t["exit_reason"] for t in trades)),
        "assets": dict(Counter(t["symbol"] for t in trades)),
    }


def old_trade_diagnostics(data, trades: list[dict], summary: dict, strategy: dict, config: dict) -> list[dict]:
    output = []
    width = strategy["bar_hours"] * HOUR
    end = timestamp(summary["to_exclusive"])
    for t in trades:
        symbol = t["symbol"]
        candles = data.trade[symbol]
        direction, quantity = int(t["direction"]), float(t["quantity_base"])
        entry, equity = float(t["entry_fill"]), float(t["equity_at_entry_usd"])
        start, exit_lower = timestamp(t["entry_utc"]), timestamp(t["exit_earliest_utc"])
        fee = config["taker_fee"]
        entry_fee = quantity * entry * fee
        desired_net = equity * summary["target_fraction"]
        required_exit_fill = (desired_net + entry_fee + direction * quantity * entry) / (quantity * (direction - fee))
        future_funding = 0.0
        best_close_net = -entry_fee
        complete_hours = 0
        for hour in range(start, exit_lower, HOUR):
            if hour + HOUR > exit_lower:
                break
            future_funding += -direction * quantity * data.funding[symbol][hour]
            hypothetical_fill = fill(candles[hour].close, -direction, summary["slippage_each_fill"], data.instruments[symbol])
            hypothetical_net = direction * quantity * (hypothetical_fill - entry) - entry_fee - quantity * hypothetical_fill * fee + future_funding
            best_close_net = max(best_close_net, hypothetical_net)
            complete_hours += 1
        returned_inside = None
        if strategy["kind"] == "breakout" and start + width <= end:
            previous = [candles[h] for h in range(start - (strategy["lookback"] + 1) * width, start - width, HOUR)]
            boundary = max(b.high for b in previous) if direction > 0 else min(b.low for b in previous)
            first_bar_close = candles[start + width - HOUR].close
            returned_inside = direction * (first_bar_close - boundary) <= 0
        output.append({
            "trade_number": t["number"], "symbol": symbol, "entry_utc": t["entry_utc"],
            "required_exit_fill_excluding_future_funding": required_exit_fill,
            "target_has_positive_price_excluding_future_funding": required_exit_fill > 0,
            "target_required_favorable_exit_fill_move_excluding_future_funding": direction * (required_exit_fill / entry - 1),
            "complete_hours_observed_before_exit": complete_hours,
            "best_net_return_at_completed_hour_closes": best_close_net / equity,
            "reached_half_percent_at_completed_hour_close": best_close_net >= 0.005 * equity,
            "first_signal_bar_after_entry_returned_inside_old_range": returned_inside,
            "net_pnl_usd": float(t["net_pnl_usd"]), "exit_reason": t["exit_reason"],
        })
    return output


def arithmetic() -> dict:
    table = []
    for leverage in (0.5, 1, 2):
        table.append({"equity_usd": 50, "exposure_over_equity": leverage,
                      "notional_usd": 50 * leverage, "initial_margin_usd_at_10pct": 5 * leverage,
                      "initial_margin_fraction_equity": 0.1 * leverage,
                      "fee_round_trip_usd_approx": 50 * leverage * 0.001,
                      "fee_plus_friction_round_trip_usd_approx": 50 * leverage * 0.0014,
                      "fees_for_50_round_trips_fixed_notional_usd_approx": 50 * 50 * leverage * 0.001,
                      "fees_plus_friction_for_50_round_trips_fixed_notional_usd_approx": 50 * 50 * leverage * 0.0014})
    risk_examples = []
    for risk in (0.005, 0.02):
        for stop in (0.005, 0.01, 0.02):
            risk_dollars = 50 * risk
            reserve = risk_dollars * 0.10
            nominal = min((risk_dollars - reserve) / (stop + 0.0014), 100)
            risk_examples.append({"equity_usd": 50, "risk_fraction": risk, "technical_stop_price_fraction": stop,
                                  "funding_reserve_usd": reserve, "notional_usd_approx_before_lot_rounding": nominal,
                                  "exposure_over_equity_approx": nominal / 50,
                                  "initial_margin_usd_at_10pct_approx": nominal * 0.1})
    return {"assumptions": ["Fixed 50 USD equity and constant entry/exit nominal for illustration only.",
                            "Fees 0.05% each side; hypothetical combined spread/slippage 0.02% each fill.",
                            "Does not estimate funding, actual win probability, achievable frequency or account eligibility.",
                            "Initial margin here is 10% of notional, not a maximum wallet loss in cross margin."],
            "exposure_examples": table, "sizing_examples": risk_examples,
            "binary_win_rate_break_even_for_net_half_percent_gain": [
                {"loss_fraction": r, "gain_fraction": 0.005, "win_rate": r / (r + 0.005)} for r in (0.0025, 0.005, 0.01, 0.02)]}


def report(reference: list[dict], variants: list[dict], config: dict) -> str:
    lines = ["# Diagnóstico de objetivos, frecuencia, margen y apalancamiento", "",
             "Solo investigación local. Todas las comparaciones nuevas utilizan desarrollo: 14 febrero–31 mayo de 2026. Sin Astra ni órdenes reales.", "",
             "Los objetivos 5–10 % dejan de ser un requisito fijo. Se evalúa también 0,5 % neto por operación ganadora, sin suponer una cuota de operaciones ni una rentabilidad diaria.", "",
             "## Qué utilizaban realmente las operaciones anteriores", "",
             "| Ventana / regla / objetivo | Exposición media / equity | Margen inicial medio / equity | Stop medio del precio | Horas medias de posición (cota superior) | Movimiento medio del fill para TP, sin funding futuro | TP sin precio positivo, sin funding futuro |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for row in reference:
        st = row["stats"]
        lines.append(f"| {row['window']} / {row['strategy']} / {row['target']:.0%} | {st['exposure_over_equity']['mean']:.3f}x | {st['initial_margin_fraction_equity']['mean']:.2%} | {st['initial_stop_price_distance_fraction']['mean']:.2%} | {st['holding_hours_upper']['mean']:.1f} | {row['target_price_distance']['mean']:.2%} | {row['nonpositive_target_price_count_excluding_future_funding']} |")
    lines += ["", "El 2x era un techo de exposición. El tamaño se redujo por la distancia del stop y los lotes: no se utilizó 2x automáticamente. El porcentaje de margen de la tabla no limita la pérdida de una cartera en cruzado.", "",
              "La distancia de TP es un cálculo algebraico, no una afirmación de alcanzabilidad. Si el precio requerido es cero o negativo, ese objetivo no tiene un precio de salida positivo sin aportaciones futuras de funding. En la primera operación corta de H2 con TP 10 % en desarrollo, el nominal era 4,093 USD y el objetivo 5 USD: ni una caída a cero bastaba, antes de costes y funding. Se conserva la operación histórica para diagnosticarla; el motor anterior no rechazaba esa incompatibilidad.", "",
              "## De dónde salieron las pérdidas o ganancias", "",
              "Descomposición sobre las MISMAS operaciones y cantidades. Quitar los costes no vuelve a simular la trayectoria ni la reinversión; es una atribución contable.", "",
              "| Ventana / regla / objetivo | P&L a precios de referencia USD | Fricción fills USD | Comisiones USD | Funding USD | Neto USD |",
              "|---|---:|---:|---:|---:|---:|"]
    for row in reference:
        s = row["stats"]
        lines.append(f"| {row['window']} / {row['strategy']} / {row['target']:.0%} | {s['gross_at_reference_prices_usd']:.4f} | {s['friction_already_in_gross_usd']:.4f} | {s['fees_usd']:.4f} | {s['funding_usd']:.4f} | {s['net_pnl_usd']:.4f} |")
    lines += ["", "## Diagnóstico de recorridos anteriores", "",
              "| Ventana / regla / objetivo | Operaciones | Salidas por stop | Alcanzaron +0,5 % neto en algún cierre horario completo anterior a la salida | Volvieron al rango en el primer cierre de barra tras entrar |",
              "|---|---:|---:|---:|---:|"]
    for row in reference:
        reasons = row["stats"]["exit_reasons"]
        stops = sum(n for reason, n in reasons.items() if reason.startswith("stop"))
        range_value = f"{row['returned_inside_count']}/{row['range_observation_count']}" if row["range_observation_count"] else "No aplica"
        lines.append(f"| {row['window']} / {row['strategy']} / {row['target']:.0%} | {row['stats']['trades']} | {stops} | {row['reached_half_percent_at_close_count']} | {range_value} |")
    lines += ["", "Se excluye de los recorridos la hora de salida cuando se desconoce el instante de ejecución. Alcanzar un valor en un cierre anterior no prueba que una cartera con otro TP obtuviera ese resultado: sus futuras entradas y tamaños cambiarían. El primer cierre de barra tras entrar puede ser posterior a una salida temprana; volver al rango es una observación retrospectiva de precio, no una causa demostrada ni un filtro validado.", "",
              "## Comparaciones nuevas predefinidas", "",
              "Se mantienen el techo 2x, ATR, lote, reglas de funding y prioridades del motor original. Dos controles, cuatro cambios de objetivo, dos escenarios de riesgo reducido y una hipótesis horaria. Cada caso se ejecuta con fricción de 2 y 5 puntos básicos por fill. No se han reajustado tras ver resultados.", "",
              "| Caso | Fricción/fill | Riesgo | TP neto | Ops | Ops/día calendario | Retorno periodo | DD horario | Acierto | Rechazos por lote | Exposición media |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for v in variants:
        s, stats = v["summary"], v["stats"]
        win = f"{s['win_rate']:.1%}" if s["win_rate"] is not None else "—"
        exposure = f"{stats['exposure_over_equity']['mean']:.3f}x" if s["trades"] else "—"
        lines.append(f"| {v['case']} | {s['slippage_each_fill']*10000:.0f} pb | {s['risk_fraction']:.1%} | {s['target_fraction']:.1%} | {s['trades']} | {stats['trades_per_calendar_day']:.3f} | {s['return_fraction']:.2%} | {s['max_hourly_mark_drawdown_fraction']:.2%} | {win} | {s['skipped_signals'].get('minimum_quantity_exceeds_budget', 0)} | {exposure} |")
    lines += ["", "Retornos de todo el periodo, no diarios ni por operación. Se incluye el resultado aunque sea negativo. Un resultado positivo aquí seguiría siendo desarrollo observado, sin aprobación de estrategia. Bajar riesgo también puede cambiar el activo elegido o impedir entradas por lote mínimo.", "",
              "## Frecuencia y costes", "",
              "La regla de 4 horas puede evaluar seis instantes de entrada al día, y la diaria uno, en una cartera de una posición. Además debe terminar la posición anterior. La variante horaria tampoco puede demostrar 50 operaciones diarias; los datos OHLC de una hora no resuelven una operativa de pocos minutos.",
              "Cincuenta operaciones con ganancia media neta del 0,5 % sobre una base fija de 50 USD serían 12,50 USD diarios (25 %). Esa ganancia media tendría que incluir perdedoras y costes. Si 0,5 % es solo el TP ganador, falta conocer aciertos y pérdidas. No es una proyección de rendimiento.",
              "Con nominal fijo 100 USD (2x sobre 50), las comisiones taker de ida/vuelta serían aproximadamente 0,10 USD por operación y 5 USD por 50 operaciones. Sumando la fricción hipotética base, serían aproximadamente 7 USD, antes de funding. Ganar 0,5 % neto de la cuenta exige aproximadamente 0,39 USD de P&L bruto por operación ganadora en ese ejemplo.",
              "Con ganancias netas +0,5 % y pérdidas netas -2 %, el acierto binario de equilibrio es 80 %. Con +0,5 %/-0,5 % es 50 %. Las distribuciones reales incluyen salidas temporales y gaps.", "",
              "## Cómo dimensionar", "",
              "Exposición = nominal/equity. Margen inicial = nominal × requisito del contrato. Riesgo planificado = pérdida hasta el stop más costes y reserva de funding. En cruzado, el saldo de la cartera sirve como garantía compartida.",
              "Se propone mantener 2x como techo inicial de simulación, elegir el stop por mercado y calcular cantidad desde el riesgo. Para una futura hipótesis de mayor frecuencia, estudiar 0,25–0,5 % de riesgo por operación, sujeto a lote mínimo y límites diarios/agregados. En esta ronda se calculó 0,5 %, no se configuró una cuenta ni se aprobó operar.",
              "Ejemplo aproximado: 50 USD, riesgo 0,5 % (0,25 USD), reserva funding 0,025 USD, stop del precio 0,5 % y fricción total 0,14 % del nominal ⇒ nominal 35,16 USD antes de redondeo, exposición 0,70x, margen a IM 10 % de unos 3,52 USD (7,03 % de cuenta).",
              "No se impone un porcentaje fijo de saldo por operación. Si el lote mínimo excede riesgo, la salida es no operar. El colchón libre sigue siendo garantía en cruzado y el stop no asegura un máximo absoluto realizado.", "",
              "## Límites y trazabilidad", "",
              "Se conserva el motor OHLC y todas sus limitaciones de fills, latencia, mark y funding intrahorario. No se estudió ejecución de 50 operaciones diarias, ni se reabrió agosto–septiembre. Las observaciones de junio–julio de las tablas iniciales proceden exclusivamente de resultados ya guardados; las variantes nuevas no se ejecutaron allí.",
              "diagnostics.json guarda métricas y límites, reference_trade_paths.csv los recorridos, cada variante conserva libro y equity. manifest.json guarda hashes del código, configuración y entradas. El cálculo es local y no tiene llamadas a agentes.", "",
              "Fuentes consultadas: [márgenes EEE](https://support.kraken.com/articles/derivatives-margin-schedule-and-maximum-leverage-eea), [comisiones EEE](https://support.kraken.com/au/articles/fees-for-derivatives-trading-eea) y [garantía cruzada](https://support.kraken.com/ca/articles/portfolio-management-eea).", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    config_path = ROOT / "config/target_frequency_diagnosis.json"
    experiment = json.loads(config_path.read_text(encoding="utf-8"))
    base_path = ROOT / experiment["base_config"]
    base = json.loads(base_path.read_text(encoding="utf-8"))
    if experiment["astra_enabled"] or base["astra_enabled"] or base["live_trading_enabled"]:
        raise ValueError("Agent and live modes are not supported")
    start, end = timestamp(experiment["window"]["from"]), timestamp(experiment["window"]["to_exclusive"])
    development = next(w for w in base["windows"] if w["id"] == "development")
    if not timestamp(development["from"]) <= start < end <= timestamp(development["to_exclusive"]):
        raise ValueError("Only development is allowed for new experiments")
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    save_json(out / "experiment.json", experiment)
    save_json(out / "base_config.json", base)
    started = time.perf_counter()
    data = load_market_data(ROOT, base)
    definitions = {s["id"]: s for s in base["strategies"] + experiment["additional_strategies"]}
    reference_dir = ROOT / experiment["reference_results"]
    prior_path = reference_dir / "summary.json"
    prior = json.loads(prior_path.read_text(encoding="utf-8"))["strategies"]
    inputs = {**data.provenance["inputs_sha256"], str(prior_path.relative_to(ROOT)): digest(prior_path)}
    references, reference_paths = [], []
    for summary in prior:
        if summary["slippage_each_fill"] != 0.0002:
            continue
        path = reference_dir / summary["window"] / summary["variant"] / "trades.csv"
        inputs[str(path.relative_to(ROOT))] = digest(path)
        trades = read_trades(path)
        details = old_trade_diagnostics(data, trades, summary, definitions[summary["strategy"]], base)
        for r in details:
            r.update({"window": summary["window"], "strategy": summary["strategy"], "target": summary["target_fraction"]})
        reference_paths.extend(details)
        returns = [x["first_signal_bar_after_entry_returned_inside_old_range"] for x in details
                   if x["first_signal_bar_after_entry_returned_inside_old_range"] is not None]
        refs = {"window": summary["window"], "strategy": summary["strategy"], "target": summary["target_fraction"],
                "stats": ledger_stats(trades, (timestamp(summary["to_exclusive"]) - timestamp(summary["from"])) / 86400),
                "target_price_distance": distribution([x["target_required_favorable_exit_fill_move_excluding_future_funding"] for x in details]),
                "nonpositive_target_price_count_excluding_future_funding": sum(not x["target_has_positive_price_excluding_future_funding"] for x in details),
                "range_observation_count": len(returns), "returned_inside_count": sum(returns),
                "reached_half_percent_at_close_count": sum(x["reached_half_percent_at_completed_hour_close"] for x in details)}
        references.append(refs)
    variants = []
    for case in experiment["cases"]:
        for cost in base["cost_scenarios"]:
            config = deepcopy(base)
            config["risk_fraction"] = case["risk"]
            if not 0 < case["risk"] <= 0.02 or not 0 < case["target"] <= 0.05:
                raise ValueError("Invalid diagnostic risk/target")
            result = simulate(data, config, definitions[case["strategy"]], case["target"], cost["slippage_each_fill"], start, end)
            if abs(result["summary"]["ledger_residual_usd"]) > 1e-8:
                raise ValueError("Unbalanced PnL ledger")
            folder = out / "development" / (case["id"] + "_" + cost["name"])
            folder.mkdir(parents=True)
            save_json(folder / "summary.json", result["summary"])
            save_csv(folder / "trades.csv", result["trades"])
            save_csv(folder / "hourly_equity.csv.gz", result["hourly_equity"], zipped=True)
            save_json(folder / "events.json", result["events"])
            variants.append({"case": case["id"], "cost_scenario": cost["name"], "summary": result["summary"],
                             "stats": ledger_stats(result["trades"], (end - start) / 86400)})
    save_json(out / "diagnostics.json", {"reference": references, "development_variants": variants, "arithmetic": arithmetic()})
    save_csv(out / "reference_trade_paths.csv", reference_paths)
    (out / "informe.md").write_text(report(references, variants, base), encoding="utf-8")
    code = list((ROOT / "src/trading_lab").glob("*.py")) + [Path(__file__).resolve(), config_path, base_path]
    outputs = {str(p.relative_to(out)): digest(p) for p in sorted(out.rglob("*")) if p.is_file()}
    save_json(out / "manifest.json", {"created_at_utc": datetime.now(timezone.utc).isoformat(),
              "duration_seconds": time.perf_counter() - started, "python": sys.version,
              "model_api_calls": 0, "model_api_tokens": 0, "network_requests": 0, "orders_sent": 0,
              "new_development_evaluations": len(variants), "new_validation_evaluations": 0, "reserved_period_evaluated": False,
              "inputs_sha256": inputs, "code_sha256": {str(p.relative_to(ROOT)): digest(p) for p in code},
              "output_sha256": outputs})
    print(json.dumps({"output": str(out), "evaluations": len(variants), "base_results": [
        {"case": v["case"], "return": round(v["summary"]["return_fraction"], 6), "trades": v["summary"]["trades"],
         "lot_rejections": v["summary"]["skipped_signals"].get("minimum_quantity_exceeds_budget", 0)}
        for v in variants if v["summary"]["slippage_each_fill"] == 0.0002]}))


if __name__ == "__main__":
    main()
