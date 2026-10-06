"""Replay registered 1m/5m hypotheses with measured quotes and explicit cost allowances."""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import statistics
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from trading_lab.data import digest, timestamp, load_market_data
from trading_lab.intraday import load_intraday, intraday_signals, quoted_cost, aggregate
from trading_lab.simulator import simulate
from diagnose_strategy_targets import save_json, save_csv, ledger_stats
from research_risk_margin import uncertainty, quantile


def render(result):
    lines=["# Investigación intradía: datos reales 1m y señales 1m/5m","",
           "Objetivo neto 0,5 %; riesgo presupuestado 0,25 %; margen asignado ≤40 % al entrar. "
           "Nominal/margen hasta 25x autorizado para evaluar, con IM observado EEE 10 % aplicado. "
           "Una posición global, BTC primero. Retraso de entrada de un minuto tras disponer de la señal.","",
           "Las 16 combinaciones estaban registradas antes del primer P&L. "
           "Ruptura confirmada 5m es la principal; las otras tres son comparaciones, sin sustituirla por selección sobre junio–julio.","",
           "## Resultados después de costes de trading", "",
           "| Periodo | Regla | Coste adicional/fill | Ops | Ops/día | Retorno periodo | DD a 1m | Aciertos | PF | Duración media máx. (min) | TP alcanzados | Margen máx. |",
           "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for v in result["variants"]:
        s,st=v["summary"],v["stats"]
        win=f"{s['win_rate']:.1%}" if s["win_rate"] is not None else "n/a"
        pf=f"{s['profit_factor']:.2f}" if s["profit_factor"] is not None else "n/a"
        hold=f"{st['holding_hours_upper']['mean']*60:.1f}" if s["trades"] else "n/a"
        margin=f"{st['initial_margin_fraction_equity']['max']:.2%}" if s["trades"] else "n/a"
        lines.append(f"| {v['window']} | {v['case']} | {v['additional_adverse_fraction']*1e4:.0f} pb | {s['trades']} | {st['trades_per_calendar_day']:.2f} | {s['return_fraction']:.2%} | {s['max_hourly_mark_drawdown_fraction']:.2%} | {win} | {pf} | {hold} | {s['net_target_achieved_trades']} | {margin} |")
    lines += ["","Coste adicional se suma a medio spread histórico rezagado y a la estimación medida de barrido del libro; "
              "comisión taker 0,05 % por lado y redondeo adverso a tick se contabilizan aparte. Funding por minuto. "
              "El margen de la tabla coincide con el asignado en estos contratos de IM 10 %.","",
              "## Calidad, medición y causalidad","",
              "Velas trade/mark reales de 1m desde el 31 de marzo hasta el 31 de julio, con el primer día para calentamiento. "
              "Bid/ask histórico a 5m: solo el último bucket ya completado, edad máxima 600 s. "
              "Las cotizaciones de analytics pueden estar muestreadas o repetidas; no son un libro ejecutable histórico.","",
              "Libro actual: 30 capturas por activo, aproximadamente un minuto. Se calcula VWAP para nominales 25/50/100/200/500 USD. "
              "Se usa el p95 de barrido adicional para 200 USD como componente estático del coste. "
              "No se midieron fills propios ni deslizamiento por latencia. HTTP RTT no es latencia de una orden.","",
              "El modelo usa un minuto completo de retraso de entrada y reservas explícitas de ejecución adversa de 1/5 pb. "
              "Aplicar la profundidad actual al pasado es una hipótesis de viabilidad actual, no una reconstrucción completa de fills históricos. "
              "Un minuto OHLC aún puede contener secuencias stop/TP indeterminadas; se toma stop primero.","",
              "## Filtro registrado","",
              "Se exige a la principal en ambos periodos y costes: ≥100 operaciones, retorno positivo, PF≥1,1, DD≤10 %, "
              "extremo inferior bootstrap positivo y ninguna posible liquidación. "
              f"Supera todos los filtros: **{result['primary_passes_all_screens']}**. Operación real autorizada por estos resultados: **False**.","",
              "Bootstrap: 2.000 remuestreos circulares con bloques de siete días y días sin operaciones. "
              "Sus percentiles son condicionales al modelo y periodo, no probabilidades garantizadas de rentabilidad futura. "
              "Abril–julio ya se observaron con señales de mayor intervalo. Agosto–septiembre sigue reservado.","",
              "Resultados completos, causas de rechazo, componentes del P&L, incertidumbre y distribución por activo/mes están en results.json. "
              "Cada variante conserva su configuración, libro de operaciones, curva de equity a un minuto y eventos.","",
              "Cálculo local: cero llamadas a modelos, cero tokens API, cero peticiones de red durante replay y cero órdenes. "
              "Las descargas públicas previas tienen sus propios manifiestos.",""]
    return "\n".join(lines)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data",type=Path,required=True)
    p.add_argument("--books",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    source=ROOT/"config/intraday_research.json"
    exp=json.loads(source.read_text(encoding="utf-8"))
    basepath=ROOT/exp["base_config"]
    base=json.loads(basepath.read_text(encoding="utf-8"))
    if base["astra_enabled"] or base["live_trading_enabled"]:
        raise ValueError("Offline research only")
    base["catalog"]=exp["catalog"]
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    save_json(out/"registered_experiment.json",exp)
    started=time.perf_counter()
    data,spreads,audit=load_intraday(ROOT,base,args.data.resolve())
    save_json(out/"data_audit.json",audit)
    bm=args.books.resolve()/"manifest.json"
    book_manifest=json.loads(bm.read_text(encoding="utf-8"))
    bookfile=args.books.resolve()/"summary.json"
    if digest(bookfile)!=book_manifest["summary_sha256"]:
        raise ValueError("Book summary checksum mismatch")
    for r in book_manifest["observations"]:
        raw=gzip.decompress((args.books.resolve()/r["file"]).read_bytes())
        if hashlib.sha256(raw).hexdigest()!=r["response_sha256"]:
            raise ValueError("Raw book checksum mismatch")
    books=json.loads(bookfile.read_text(encoding="utf-8"))
    costs={s:books[s]["200"]["p95_walk_beyond_best_fraction"] for s in base["symbols_priority"]}
    quality={"book_measurements":books,"historical_spreads":{}}
    for s,values in spreads.items():
        xs=[x*1e4 for x in values.values()]
        quality["historical_spreads"][s]={"points":len(xs),"median_full_spread_bps":statistics.median(xs),"p95_full_spread_bps":quantile(xs,.95),"max_full_spread_bps":max(xs)}
    save_json(out/"execution_measurements.json",quality)
    # With a measured book walk for 200 USD, prevent any future config from exceeding that envelope.
    if base["initial_equity_usd"]!=50 or any(i.initial_margin<.1 for i in data.instruments.values()):
        raise ValueError("Execution-cost measurement envelope must be revisited")
    variants=[]
    for wi,w in enumerate(exp["windows"]):
        start,end=timestamp(w["from"]),timestamp(w["to_exclusive"])
        if end>timestamp(base["reserved_not_evaluated"]["from"]):
            raise ValueError("Reserved period cannot be evaluated")
        for si,spec in enumerate(exp["cases"]):
            schedule={s:intraday_signals(data.trade[s],spec,end,exp["signal_to_entry_delay_seconds"]) for s in base["symbols_priority"]}
            for ci,cost in enumerate(exp["cost_scenarios"]):
                cfg=deepcopy(base)
                for key in ("risk_fraction","minimum_net_target_to_budgeted_loss","maximum_nominal_per_allocated_margin","maximum_allocated_margin_fraction","minimum_free_equity_fraction","max_exposure_over_equity","bar_step_seconds"):
                    cfg[key]=exp[key]
                def cost_at(symbol,t):
                    return quoted_cost(spreads[symbol],t,cost["additional_adverse_fraction"],costs[symbol],exp["spread_bucket_seconds"],exp["max_spread_age_seconds"])
                r=simulate(data,cfg,spec,exp["target_fraction"],0,start,end,signal_schedule=schedule,cost_at=cost_at)
                summary,trades=r["summary"],r["trades"]
                if summary["status"]!="exploratory_only":
                    raise ValueError("Invalid possible liquidation; inspect path before reporting PnL")
                if abs(summary["ledger_residual_usd"])>1e-8:
                    raise ValueError("Ledger does not balance")
                for t in trades:
                    if t["allocated_margin_fraction_of_equity"]>.4+1e-10:
                        raise ValueError("Margin allocation cap exceeded")
                    if t["planned_stop_price_loss_and_fees_usd"]+t["funding_budget_usd"]>exp["risk_fraction"]*t["equity_at_entry_usd"]+1e-8:
                        raise ValueError("Planned stop risk exceeded")
                stats=ledger_stats(trades,(end-start)/86400)
                counts=Counter(t["entry_utc"][:10] for t in trades)
                stats["max_entries_per_utc_day"]=max(counts.values(),default=0)
                stats["days_with_entries"]=len(counts)
                stats["days_at_least_50_entries"]=sum(n>=50 for n in counts.values())
                stats["sizing_limits"]=dict(Counter(t["sizing_binding_limit"] for t in trades))
                stats["maximum_entry_notional_usd"]=max((t["entry_notional_usd"] for t in trades),default=0)
                if stats["maximum_entry_notional_usd"]>200+1e-8:
                    raise ValueError("Position exceeds measured depth envelope")
                u=uncertainty(r["hourly_equity"],base["initial_equity_usd"],exp["bootstrap"],exp["bootstrap"]["seed"]+wi*100+si*10+ci)
                g=exp["screening"]
                passed={"count":summary["trades"]>=g["minimum_trades_each_window_cost"],"net":summary["return_fraction"]>0,
                        "profit_factor":(summary["profit_factor"] or 0)>=g["minimum_profit_factor"],
                        "drawdown":summary["max_hourly_mark_drawdown_fraction"]<=g["maximum_mark_drawdown"],
                        "uncertainty":u["same_length_return_percentile_2_5"]>0}
                row={"window":w["id"],"case":spec["id"],"cost":cost["name"],"additional_adverse_fraction":cost["additional_adverse_fraction"],
                     "summary":summary,"stats":stats,"uncertainty":u,"failed_screens":[k for k,v in passed.items() if not v]}
                folder=out/w["id"]/(spec["id"]+"_"+cost["name"]);folder.mkdir(parents=True)
                save_json(folder/"summary.json",row);save_json(folder/"effective_config.json",cfg)
                save_json(folder/"events.json",r["events"])
                save_csv(folder/"trades.csv",trades)
                save_csv(folder/"minute_equity.csv.gz",r["hourly_equity"],zipped=True)
                variants.append(row)
                print(json.dumps({"window":w["id"],"case":spec["id"],"cost":cost["name"],"trades":summary["trades"],"return":summary["return_fraction"]}),flush=True)
    # Regression reference: one historical H3 evaluation, same data/config as its stored control.
    oldbase=json.loads(basepath.read_text(encoding="utf-8"))
    olddata=load_market_data(ROOT,oldbase)
    oldbase["risk_fraction"]=.005
    oldspec={"id":"H3_breakout_1h","kind":"breakout","bar_hours":1,"lookback":20,"atr_period":14,"stop_atr":2,"max_hold_bars":48}
    oldrun=simulate(olddata,oldbase,oldspec,.005,.0002,timestamp("2026-02-14T00:00:00+00:00"),timestamp("2026-06-01T00:00:00+00:00"))
    oldpath=ROOT/"data/research_runs/20261005_target_frequency_diagnosis_v2/development/H3_1h_target05_risk05_base_2bps_each_fill/summary.json"
    old=json.loads(oldpath.read_text())
    control={"old_sha256":digest(oldpath),"return_difference":oldrun["summary"]["return_fraction"]-old["return_fraction"],"trade_count_matches":oldrun["summary"]["trades"]==old["trades"]}
    if abs(control["return_difference"])>1e-12 or not control["trade_count_matches"]:
        raise ValueError("Unexpected hourly regression")
    result={"experiment":exp,"variants":variants,"execution_measurements":quality,"hourly_control":control,
            "primary_passes_all_screens":all(not v["failed_screens"] for v in variants if v["case"]==exp["primary_case"]),"live_promotion_allowed":False}
    save_json(out/"results.json",result)
    (out/"informe.md").write_text(render(result),encoding="utf-8")
    files=list((ROOT/"src/trading_lab").glob("*.py"))+[Path(__file__).resolve(),ROOT/"scripts/diagnose_strategy_targets.py",ROOT/"scripts/research_risk_margin.py",source,basepath]
    save_json(out/"manifest.json",{"created_at_utc":datetime.now(timezone.utc).isoformat(),"duration_seconds":time.perf_counter()-started,
              "evaluations":len(variants),"model_calls":0,"model_tokens":0,"network_calls_during_replay":0,"orders":0,"reserved_period_evaluated":False,
              "input_sha256":{**audit["inputs_sha256"],str(bm.relative_to(ROOT)):digest(bm),str(bookfile.relative_to(ROOT)):digest(bookfile)},
              "code_sha256":{str(p.relative_to(ROOT)):digest(p) for p in files},
              "output_sha256":{str(p.relative_to(out)):digest(p) for p in sorted(out.rglob("*")) if p.is_file()}})
    print(json.dumps({"completed":str(out),"primary_passes":result["primary_passes_all_screens"],"control":control}),flush=True)


if __name__=="__main__": main()
