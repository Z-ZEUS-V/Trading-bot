"""Run the frozen local strategy experiment without networking or agents.

Requires Python 3.11+ standard library only. --output must be a new directory.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from trading_lab.data import digest, load_market_data, timestamp
from trading_lab.simulator import passive_context, simulate


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict], compressed: bool = False) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    opener = gzip.open if compressed else open
    with opener(path, "wt", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def make_report(summaries: list[dict], baselines: list[dict], audit: dict, config: dict, duration: float) -> str:
    lines = ["# Primera simulación local de estrategias", "",
             "Resultados exploratorios con datos históricos, costes actuales e hipótesis de ejecución. No es operación real ni validación de rentabilidad futura.", "",
             "## Alcance", "",
             f"Capital inicial: {config['initial_equity_usd']:.2f} USD por ventana y variante. Una posición total, cruzado USD, riesgo planificado {config['risk_fraction']:.0%}, exposición máxima {config['max_exposure_over_equity']:g}x. Objetivos netos: {', '.join(format(t, '.0%') for t in config['account_profit_targets'])} sobre equity al entrar.",
             "Ventanas: " + "; ".join(f"{w['id']} [{w['from']}, {w['to_exclusive']})" for w in config['windows']) + ". Extremos derechos excluidos; cada ventana empieza de nuevo con el capital inicial.",
             f"Periodo reservado [{config['reserved_not_evaluated']['from']}, {config['reserved_not_evaluated']['to_exclusive']}): no se calcularon señales/resultados de estrategias para él. No se ajustaron parámetros entre desarrollo y validación.", "",
             "## Conciliación de datos", ""]
    for symbol, a in audit["symbols"].items():
        lines.append(f"- {symbol}: {a['overlap_count']} observaciones comunes; {len(a['overlap_mismatches'])} discrepancias; {len(a['funding_recovered_from_analytics'])} horas recuperadas de analytics; {len(a['remaining_missing_hours'])} horas siguen ausentes fuera de las ventanas elegidas. Ticker de la hora actual coincide: {a['current_hour_timing_check']['current_funding_matches']}.")
    lines += ["", "Se excluyó la vela parcial de las 01:00 UTC del 2 de octubre en trade/mark. El funding se contabiliza como tasa absoluta USD por unidad base y hora, con signo negativo para largos cuando la tasa es positiva.",
              "La coincidencia entre fuentes y ticker respalda el mapeo; no se conciliaron movimientos privados de cuenta. Los valores recuperados son observaciones, no interpolaciones ni ceros inventados.", "",
              "## Todas las variantes", "",
              f"Comisión taker: {config['taker_fee']:.3%} por lado. Fricción adicional por fill: {', '.join(str(c['slippage_each_fill'] * 10000) + ' puntos básicos' for c in config['cost_scenarios'])}, más redondeo adverso a tick. Son escenarios hipotéticos de spread/deslizamiento, no mediciones de ejecución.", "",
              "| Ventana | Regla | Objetivo | Fricción/fill | Operaciones | Saldo USD | Retorno neto | DD horario | Acierto | Fees USD | Funding USD |",
              "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for s in summaries:
        win = f"{s['win_rate']:.1%}" if s["win_rate"] is not None else "—"
        lines.append(f"| {s['window']} | {s['strategy']} | {s['target_fraction']:.0%} | {s['slippage_each_fill']*10000:.0f} pb | {s['trades']} | {s['final_equity_usd']:.2f} | {s['return_fraction']:.2%} | {s['max_hourly_mark_drawdown_fraction']:.2%} | {win} | {s['fees_usd']:.3f} | {s['funding_cashflow_usd']:.3f} |")
    validation = [s for s in summaries if s["window"] == "chronological_validation"]
    positive = sum(s["net_pnl_usd"] > 0 for s in validation)
    lines += ["", f"En validación, {positive} de {len(validation)} variantes terminaron con P&L neto positivo. Esto describe únicamente este replay. Ninguna variante queda aprobada para operar.", "",
              "## Riesgo y ambigüedad", "",
              "| Ventana / variante | Stops y TP en misma hora | Operaciones sobre presupuesto de pérdida | Objetivo neto alcanzado | Incertidumbre acumulada funding USD | Estado |",
              "|---|---:|---:|---:|---:|---|"]
    for s in summaries:
        lines.append(f"| {s['window']} / {s['variant']} | {s['same_hour_double_touches']} | {s['loss_budget_exceeded_trades']} | {s['net_target_achieved_trades']} | {s['funding_intrabar_bound_width_usd']:.5f} | {s['status']} |")
    lines += ["", f"El riesgo inicial reserva el {config['funding_reserve_fraction_of_risk']:.0%} del presupuesto de pérdida para funding; esa reserva no garantiza cubrirlo. El stop puede acercarse al precio para respetar el presupuesto restante, nunca alejarse. Gaps o fills peores pueden superarlo.",
              "Cuando hay salida intrahoraria se desconoce su minuto: se aplica débito de funding de una hora completa o crédito cero. El ancho de incertidumbre se registra. Esta prudencia por operación no es una cota matemática de todas las trayectorias alternativas de cartera.",
              "Stop y objetivo tocados dentro de la misma hora: stop primero. No se conoce la secuencia real. Se marca el caso y no se finge precisión de ticks.",
              "Si el mark permite una liquidación antes de resolver la secuencia de salida, el motor detiene e invalida la variante. No modela una liquidación real ni sus penalizaciones.", "",
              "## Contexto del mercado", "",
              f"La referencia pasiva siguiente compra y mantiene aproximadamente 1x. Tiene un riesgo distinto del de las estrategias con stop; no permite afirmar superioridad ajustada al riesgo. Abstenerse conserva {config['initial_equity_usd']:.2f} USD antes de gastos externos.", "",
              "| Ventana | Activo | Fricción/fill | Saldo pasivo USD | Retorno | DD horario |",
              "|---|---|---:|---:|---:|---:|"]
    for b in baselines:
        lines.append(f"| {b['window']} | {b['symbol']} | {b['slippage_each_fill']*10000:.0f} pb | {b['final_equity_usd']:.2f} | {b['return_fraction']:.2%} | {b['max_hourly_mark_drawdown_fraction']:.2%} |")
    lines += ["", "## Límites de interpretación", "",
              "- Las ventanas son cortas, especialmente para la regla diaria. No se han estimado intervalos de confianza ni corregido formalmente la selección entre variantes. No hay walk-forward entrenado: estas reglas están fijas y no tienen una fase de ajuste.",
              "- El drawdown usa equity marcada al cierre horario y después de salidas; puede subestimar excursiones entre observaciones. Las salidas intrahorarias se sitúan dentro de un intervalo, no en un instante conocido.",
              "- Las reglas actuales de lote, tick, margen y tarifa se aplican a precios históricos para evaluar viabilidad presente. No son una reconstrucción de todas las reglas vigentes en cada fecha.",
              "- USD como garantía, sin conversiones ni recortes. No incluye fiscalidad, intereses por saldo USD negativo, infraestructura ni análisis. La cartera propuesta mantiene liquidez USD; no se certifica elegibilidad de la cuenta.",
              "- No se simulan colas, fills parciales, protección de precio, latencia de red ni rechazos del exchange. Los resultados no validan la ejecución real.",
              "- El P&L bruto ya incorpora fricción de fills. La columna de fricción es informativa; no se descuenta una segunda vez.",
              "- BTC tiene prioridad fija cuando ambas señales coinciden. La contribución por activo está en summary.json; resultados concentrados en un activo no prueban generalización.", "",
              "## Coste y monitorización posterior", "",
              f"Esta ejecución tardó {duration:.2f} segundos en este ordenador. El motor usa únicamente la biblioteca estándar de Python: cero llamadas a modelos, cero tokens de API y cero peticiones de red durante el replay.",
              "Para vigilar en directo, el diseño permite un adaptador de precios público, reglas locales al cerrar cada vela y un supervisor de posición independiente. No hace falta consultar a un LLM por tick. El servicio 24/7, reconexiones y alertas todavía no están implementados; electricidad, conexión y disponibilidad del equipo siguen teniendo coste.",
              "Cambiar de exchange exigiría sustituir el adaptador de datos/contratos/costes y repetir la evaluación. Las señales y la contabilidad local no importan SDKs de agentes.", "",
              "## Archivos y reproducción", "",
              "config.json fija parámetros y ventanas; funding_audit.json y funding_normalized.csv.gz documentan conciliación; summary.json/summary.csv contienen métricas; cada variante guarda operaciones y equity horaria; manifest.json registra hashes y duración.",
              "Ejecutar desde la raíz: `python scripts/run_local_strategy_research.py --output data/research_runs/<directorio-nuevo>`.", "",
              "Fuentes: [especificaciones y funding EEE](https://support.kraken.com/es/articles/perpetual-contract-specifications-for-clients-in-the-eea), [márgenes EEE](https://support.kraken.com/articles/derivatives-margin-schedule-and-maximum-leverage-eea), [comisiones EEE](https://support.kraken.com/au/articles/fees-for-derivatives-trading-eea), [histórico de funding](https://docs.kraken.com/api-reference/historical-funding-rates/historical-funding-rates).", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "config/local_strategy_research.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    if config["astra_enabled"] or config["live_trading_enabled"] or config["purpose"] != "offline_research_only":
        raise ValueError("Only offline research is supported")
    if not (0 < config["risk_fraction"] <= 0.05 and 0 <= config["funding_reserve_fraction_of_risk"] < 1
            and 0 < config["max_exposure_over_equity"] <= 2 and 0 < config["initial_equity_usd"]
            and 0 <= config["taker_fee"] < 0.01 and 0 < config["minimum_free_equity_fraction"] < 1):
        raise ValueError("Invalid research risk/cost parameters")
    if any(not 0 <= c["slippage_each_fill"] < 0.01 for c in config["cost_scenarios"]):
        raise ValueError("Invalid friction scenario")
    if any(not 0 < t <= 0.10 for t in config["account_profit_targets"]):
        raise ValueError("Invalid profit target")
    holdout_start = timestamp(config["reserved_not_evaluated"]["from"])
    for w in config["windows"]:
        start, end = timestamp(w["from"]), timestamp(w["to_exclusive"])
        if start % 3600 or end % 3600 or not start < end <= holdout_start:
            raise ValueError("Window invalid or invades reserved period")
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    write_json(out / "config.json", config)
    started = time.perf_counter()
    try:
        data = load_market_data(ROOT, config)
        write_json(out / "funding_audit.json", data.provenance)
        write_csv(out / "funding_normalized.csv.gz", data.funding_rows, compressed=True)
        summaries, baselines = [], []
        for window in config["windows"]:
            start, end = timestamp(window["from"]), timestamp(window["to_exclusive"])
            for cost in config["cost_scenarios"]:
                for strategy in config["strategies"]:
                    for target in config["account_profit_targets"]:
                        name = f"{strategy['id']}_tp{int(target * 100)}_{cost['name']}"
                        result = simulate(data, config, strategy, target, cost["slippage_each_fill"], start, end)
                        summary = result["summary"]
                        summary.update({"window": window["id"], "variant": name})
                        summaries.append(summary)
                        folder = out / window["id"] / name
                        folder.mkdir(parents=True)
                        write_json(folder / "summary.json", summary)
                        write_csv(folder / "trades.csv", result["trades"])
                        write_csv(folder / "hourly_equity.csv.gz", result["hourly_equity"], compressed=True)
                        write_json(folder / "events.json", result["events"])
                for symbol in config["symbols_priority"]:
                    b = passive_context(data, config, symbol, cost["slippage_each_fill"], start, end)
                    b.update({"window": window["id"], "slippage_each_fill": cost["slippage_each_fill"]})
                    baselines.append(b)
        elapsed = time.perf_counter() - started
        write_json(out / "summary.json", {"strategies": summaries, "passive_context": baselines})
        flat = [{k: v for k, v in s.items() if not isinstance(v, (dict, list))} for s in summaries]
        write_csv(out / "summary.csv", flat)
        (out / "informe.md").write_text(make_report(summaries, baselines, data.provenance, config, elapsed), encoding="utf-8")
        code = list((ROOT / "src/trading_lab").glob("*.py")) + [Path(__file__).resolve(), args.config.resolve()]
        outputs = {str(p.relative_to(out)): digest(p) for p in sorted(out.rglob("*")) if p.is_file()}
        write_json(out / "manifest.json", {"created_at_utc": datetime.now(timezone.utc).isoformat(),
                   "elapsed_seconds": elapsed, "python": sys.version, "network_requests": 0, "model_api_calls": 0,
                   "model_api_tokens": 0, "orders_sent": 0, "strategy_window_runs": len(summaries),
                   "reserved_period_evaluated": False,
                   "code_sha256": {str(p.relative_to(ROOT)): digest(p) for p in code}, "output_sha256": outputs})
        print(json.dumps({"output": str(out), "runs": len(summaries), "elapsed_seconds": round(elapsed, 2),
                          "validation": [{"variant": s["variant"], "trades": s["trades"],
                                          "net_pnl_usd": round(s["net_pnl_usd"], 4),
                                          "status": s["status"]} for s in summaries if s["window"] == "chronological_validation"]}))
    except Exception as exc:
        write_json(out / "failure.json", {"type": type(exc).__name__, "detail": str(exc)})
        raise


if __name__ == "__main__":
    main()
