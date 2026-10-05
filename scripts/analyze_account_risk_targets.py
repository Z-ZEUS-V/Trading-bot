"""Offline arithmetic for account-level profit/loss targets, not a backtest.

Linear USD contracts, continuous sizes, unchanged quantity between entry/exit.
No exchange connection, credentials, account settings, or model calls.
Run from any directory; --output names a NEW directory, never overwrites a run.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path


def exit_ratio(net_return: float, exposure: float, direction: int,
               entry_fee: float, exit_fee: float, extra_cost: float) -> float:
    """Solve R=L*[d*(Pexit/Pentry-1)-fin-fout*Pexit/Pentry-extra]."""
    return (net_return / exposure + direction + entry_fee + extra_cost) / (direction - exit_fee)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--equity", type=float, default=50.0)
    parser.add_argument("--entry-fee", type=float, default=0.0005)
    parser.add_argument("--exit-fee", type=float, default=0.0005)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not math.isfinite(args.equity) or args.equity <= 0:
        parser.error("equity must be finite and positive")
    if any(not math.isfinite(f) or not 0 <= f < 1 for f in (args.entry_fee, args.exit_fee)):
        parser.error("fee rates must be finite fractions in [0, 1)")

    rows = []
    for extra_label, extra in (("fees_only", 0.0), ("illustrative_extra_4bps", 0.0004)):
        for exposure in (1, 2, 3, 5, 10):
            for direction, side in ((1, "long"), (-1, "short")):
                for risk in (0.02, 0.04, 0.05):
                    for gain in (0.05, 0.10):
                        target_x = exit_ratio(gain, exposure, direction, args.entry_fee, args.exit_fee, extra)
                        stop_x = exit_ratio(-risk, exposure, direction, args.entry_fee, args.exit_fee, extra)
                        stop_distance = -direction * (stop_x - 1)
                        # Algebraic feasibility ONLY, not margin, lot, liquidity or account eligibility.
                        feasible = target_x > 0 and stop_x > 0 and stop_distance > 0
                        rows.append({
                            "cost_scenario": extra_label,
                            "exposure_over_equity": exposure,
                            "side": side,
                            "equity_usd": args.equity,
                            "entry_notional_usd": args.equity * exposure,
                            "risk_fraction_equity": risk,
                            "target_fraction_equity": gain,
                            "planned_loss_usd": args.equity * risk,
                            "target_profit_usd": args.equity * gain,
                            "flat_price_cost_usd": args.equity * exposure * (args.entry_fee + args.exit_fee + extra),
                            "target_favorable_move_fraction": direction * (target_x - 1),
                            "stop_adverse_move_fraction": stop_distance,
                            "target_exit_to_entry_price_ratio": target_x,
                            "stop_exit_to_entry_price_ratio": stop_x,
                            "adverse_stop_algebraically_feasible": feasible,
                        })

    binary = []
    streaks = []
    for risk in (0.02, 0.04, 0.05):
        survival = (1 - risk) ** 10
        streaks.append({"loss_fraction": risk, "consecutive_losses": 10,
                        "balance_usd": args.equity * survival,
                        "drawdown_fraction": 1 - survival,
                        "recovery_gain_fraction": 1 / survival - 1})
        for gain in (0.05, 0.10):
            binary.append({"loss_fraction": risk, "gain_fraction": gain,
                           "reward_to_risk": gain / risk,
                           "arithmetic_break_even_win_rate": risk / (gain + risk),
                           "log_growth_break_even_win_rate": -math.log1p(-risk) / (math.log1p(gain) - math.log1p(-risk))})

    result = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "kind": "deterministic_scenario_arithmetic_not_strategy_results",
        "inputs": {"equity_usd": args.equity, "entry_fee_fraction": args.entry_fee,
                   "exit_fee_fraction": args.exit_fee, "funding_modeled": False},
        "assumptions": [
            "Linear USD PnL; constant continuous quantity; no lot/tick rounding.",
            "Exit fee is charged on exit notional, not entry notional.",
            "Four extra basis points are a hypothetical round-trip stress, not measured slippage.",
            "Funding, liquidation, collateral FX/haircuts, tax and infrastructure excluded.",
            "10x is an arithmetic stress only: at 10% initial margin it leaves no initial equity buffer before costs.",
            "Stops are hypothetical fill prices, not guaranteed trigger execution.",
            "Binary break-even assumes all outcomes exactly target or stop, net of modeled costs.",
            "No strategy hit rate, future return, maximum actual loss or trading eligibility is estimated."
        ],
        "sources": [
            "https://support.kraken.com/au/articles/fees-for-derivatives-trading-eea",
            "https://support.kraken.com/articles/derivatives-margin-schedule-and-maximum-leverage-eea"
        ],
        "source_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "scenarios": rows, "binary_break_even": binary, "loss_streaks": streaks,
    }
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    (out / "scenarios.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (out / "scenarios.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    report = [
        "# Objetivos sobre equity: ejercicio numérico",
        "", "Cálculos de escenarios; no son resultados de una estrategia ni un backtest.", "",
        f"Equity: {args.equity:.2f} USD. Entrada: {args.entry_fee:.4%}; salida: {args.exit_fee:.4%} del nominal correspondiente.",
        "La tabla usa largos y un coste adicional HIPOTÉTICO de 0,04 % del nominal inicial por operación completa.",
        "No incluye funding. Los porcentajes de stop son movimientos del precio hasta un fill ideal, no pérdida garantizada.", "",
        "| Exposición/equity | Nominal USD | Coste con precio constante USD | Precio para +5 % cuenta | Precio para +10 % cuenta | Caída para -2 % cuenta | Caída para -5 % cuenta |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for exposure in (1, 2, 3, 5, 10):
        selected = [r for r in rows if r["cost_scenario"] == "illustrative_extra_4bps" and r["side"] == "long" and r["exposure_over_equity"] == exposure]
        a = next(r for r in selected if r["target_fraction_equity"] == 0.05 and r["risk_fraction_equity"] == 0.02)
        b = next(r for r in selected if r["target_fraction_equity"] == 0.10 and r["risk_fraction_equity"] == 0.05)
        report.append(f"| {exposure}x | {a['entry_notional_usd']:.2f} | {a['flat_price_cost_usd']:.2f} | {a['target_favorable_move_fraction']:.3%} | {b['target_favorable_move_fraction']:.3%} | {a['stop_adverse_move_fraction']:.3%} | {b['stop_adverse_move_fraction']:.3%} |")
    report += ["", "10x consume el 100 % de equity como margen inicial si IM=10 %, antes de costes: no es una propuesta operativa.", "",
               "## Acierto de equilibrio bajo dos únicos resultados", "",
               "| Pérdida neta | Ganancia neta | Beneficio/riesgo | Acierto para esperanza aritmética cero | Acierto para crecimiento logarítmico cero |",
               "|---:|---:|---:|---:|---:|"]
    for r in binary:
        report.append(f"| {r['loss_fraction']:.0%} | {r['gain_fraction']:.0%} | {r['reward_to_risk']:.2f} | {r['arithmetic_break_even_win_rate']:.2%} | {r['log_growth_break_even_win_rate']:.2%} |")
    report += ["", "Superar el umbral es necesario en este modelo simplificado; la estrategia aún debe demostrar su distribución real de resultados.", "",
               "## Diez pérdidas consecutivas con riesgo fraccional", "",
               "| Riesgo | Saldo USD | Caída acumulada | Ganancia necesaria para recuperar |", "|---:|---:|---:|---:|"]
    for r in streaks:
        report.append(f"| {r['loss_fraction']:.0%} | {r['balance_usd']:.2f} | {r['drawdown_fraction']:.2%} | {r['recovery_gain_fraction']:.2%} |")
    report += ["", "No se estima la probabilidad de esa racha. Los objetivos no generan por sí mismos una ventaja estadística.", "",
               "## Fórmula", "", "`R = L * [d * (x - 1) - f_entrada - f_salida * x - c]`", "",
               "`x = (R/L + d + f_entrada + c) / (d - f_salida)`", "",
               "R: rendimiento neto sobre equity; L: nominal inicial/equity; d: +1 largo o -1 corto; x: precio salida/entrada; c: coste extra sobre nominal inicial.", "",
               "Referencias consultadas el 2026-10-05: [comisiones EEE](https://support.kraken.com/au/articles/fees-for-derivatives-trading-eea) y [márgenes EEE](https://support.kraken.com/articles/derivatives-margin-schedule-and-maximum-leverage-eea).", ""]
    (out / "informe.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps({"output": str(out), "scenarios": len(rows), "api_calls": 0}))


if __name__ == "__main__":
    main()
