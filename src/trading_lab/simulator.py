"""Single-position, USD-linear research ledger. No order submission capability.

OHLC fills and intrabar funding are explicitly approximate. A possible margin
breach invalidates and halts a run instead of fabricating exact liquidation.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR
from statistics import mean

from .data import HOUR, Instrument, MarketData, timestamp, utc
from .strategies import signals
from .sizing import plan_size


def grid(value: float, increment: float, up: bool) -> float:
    units = Decimal(str(value)) / Decimal(str(increment))
    return float(units.to_integral_value(rounding=ROUND_CEILING if up else ROUND_FLOOR) * Decimal(str(increment)))


def fill(reference: float, side: int, slip: float, instrument: Instrument) -> float:
    """Buy side +1: higher price. Sell side -1: lower price."""
    return grid(reference * (1 + side * slip), instrument.tick, up=side > 0)


@dataclass
class Position:
    symbol: str
    direction: int
    quantity: float
    entry: float
    entry_reference: float
    entry_time: int
    expiry: int
    equity_at_entry: float
    entry_fee: float
    stop: float
    initial_stop: float
    planned_price_loss_plus_fees: float
    initial_margin: float
    allocated_margin: float
    sizing_limit: str
    funding: float = 0.0
    funding_uncertainty: float = 0.0


def trigger_for_equity(position: Position, cash: float, wanted_equity: float,
                       fee: float, slip: float, instrument: Instrument) -> float:
    d, q, entry = position.direction, position.quantity, position.entry
    required_fill = (wanted_equity - cash + d * q * entry) / (q * (d - fee))
    # Round in the favorable direction to preserve the requested net boundary.
    required_fill = grid(required_fill, instrument.tick, up=d > 0)
    raw_trigger = required_fill / (1 - d * slip)
    return grid(raw_trigger, instrument.tick, up=d > 0)


def simulate(data: MarketData, config: dict, strategy: dict, target: float,
             slip: float, start: int, end: int, *, signal_schedule: dict | None = None,
             cost_at=None) -> dict:
    symbols = config["symbols_priority"]
    step = config.get("bar_step_seconds", HOUR)
    if step not in (60, 300, HOUR) or start % step or end % step:
        raise ValueError("Invalid simulation step or boundary")
    signal_width = strategy.get("bar_seconds", strategy.get("bar_hours", 1) * HOUR)
    for s in symbols:
        for t in range(start, end, step):
            if t not in data.trade[s] or t not in data.mark[s] or t // HOUR * HOUR not in data.funding[s]:
                raise ValueError(f"Incomplete evaluation window: {s} {utc(t)}")
    schedule = signal_schedule if signal_schedule is not None else {s: signals(data.trade[s], strategy, end) for s in symbols}
    cash = initial = float(config["initial_equity_usd"])
    fee = config["taker_fee"]
    risk = config["risk_fraction"]
    if target / risk < config.get("minimum_net_target_to_budgeted_loss", 0):
        raise ValueError("Net target does not meet the configured reward/risk floor")
    reserve_fraction = config["funding_reserve_fraction_of_risk"]
    position = None
    last_exit_upper = -1
    trades, curve, events = [], [], []
    skipped = Counter()
    peak, max_dd = initial, 0.0
    status = "exploratory_only"
    active_slip = slip

    def apply_funding(value: float, uncertainty: float = 0) -> None:
        nonlocal cash
        cash += value
        position.funding += value
        position.funding_uncertainty += uncertainty

    def close(reference: float, lower: int, upper: int, reason: str,
              double_touch: bool = False) -> None:
        nonlocal cash, position, last_exit_upper
        p = position
        spec = data.instruments[p.symbol]
        price = fill(reference, -p.direction, active_slip, spec)
        gross = p.direction * p.quantity * (price - p.entry)
        exit_fee = p.quantity * price * fee
        cash += gross - exit_fee
        net = gross - p.entry_fee - exit_fee + p.funding
        trades.append({
            "number": len(trades) + 1, "symbol": p.symbol,
            "direction": p.direction, "quantity_base": p.quantity,
            "entry_utc": utc(p.entry_time), "exit_earliest_utc": utc(lower), "exit_latest_utc": utc(upper),
            "entry_reference": p.entry_reference, "entry_fill": p.entry,
            "exit_reference": reference, "exit_fill": price,
            "entry_notional_usd": p.quantity * p.entry,
            "exposure_over_equity_at_entry": p.quantity * p.entry / p.equity_at_entry,
            "equity_at_entry_usd": p.equity_at_entry, "equity_after_usd": cash,
            "initial_margin_usd": p.initial_margin,
            "allocated_margin_usd": p.allocated_margin,
            "allocated_margin_fraction_of_equity": p.allocated_margin / p.equity_at_entry,
            "nominal_over_allocated_margin": p.quantity * p.entry / p.allocated_margin,
            "sizing_binding_limit": p.sizing_limit,
            "initial_stop": p.initial_stop, "last_stop": p.stop,
            "planned_stop_price_loss_and_fees_usd": p.planned_price_loss_plus_fees,
            "funding_budget_usd": p.equity_at_entry * risk * reserve_fraction,
            "gross_pnl_after_fill_friction_usd": gross,
            "fees_usd": p.entry_fee + exit_fee, "funding_cashflow_usd": p.funding,
            "funding_intrabar_bound_width_usd": p.funding_uncertainty,
            "fill_friction_usd_already_in_gross": p.quantity * (abs(p.entry - p.entry_reference) + abs(price - reference)),
            "net_pnl_usd": net, "net_return_on_entry_equity": net / p.equity_at_entry,
            "exit_reason": reason, "same_hour_stop_and_target": double_touch,
            "actual_loss_exceeds_planned_budget": net < -p.equity_at_entry * risk - 1e-8,
            "target_net_achieved": net >= p.equity_at_entry * target - 1e-8,
        })
        last_exit_upper = upper
        position = None

    def record(t: int) -> None:
        nonlocal peak, max_dd
        unrealized = 0.0
        nominal = 0.0
        if position:
            price = data.mark[position.symbol][t].close
            unrealized = position.direction * position.quantity * (price - position.entry)
            nominal = position.quantity * price
        equity = cash + unrealized
        peak = max(peak, equity)
        dd = max(0.0, (peak - equity) / peak)
        max_dd = max(max_dd, dd)
        curve.append({"utc": utc(t + step), "cash_usd": cash, "unrealized_mark_pnl_usd": unrealized,
                      "equity_usd": equity, "drawdown_fraction": dd, "nominal_usd": nominal})

    last_processed = start - step
    for t in range(start, end, step):
        last_processed = t
        if position is None and cash > 0:
            for symbol in symbols:
                sig = schedule[symbol].get(t)
                if sig is None:
                    continue
                if sig.available_at > t:
                    raise ValueError("Signal scheduled before its inputs are available")
                if t <= last_exit_upper:
                    skipped["wait_for_new_closed_signal_bar"] += 1
                    continue
                spec = data.instruments[symbol]
                active_slip = cost_at(symbol, t) if cost_at else slip
                if active_slip is None:
                    skipped["missing_completed_spread_bucket"] += 1
                    continue
                reference = data.trade[symbol][t].open
                entry = fill(reference, sig.direction, active_slip, spec)
                raw_stop = sig.stop_reference if sig.stop_reference is not None else entry - sig.direction * strategy["stop_atr"] * sig.atr
                stop = grid(raw_stop, spec.tick, up=sig.direction > 0)
                stop_fill = fill(stop, -sig.direction, active_slip, spec)
                price_loss_and_fees = sig.direction * (entry - stop_fill) + fee * (entry + stop_fill)
                if stop <= 0 or price_loss_and_fees <= 0 or sig.direction * (entry - stop) <= 0:
                    skipped["invalid_stop_geometry"] += 1
                    continue
                size = plan_size(equity=cash, entry=entry, stop_fill=stop_fill,
                                 direction=sig.direction, instrument=spec, fee=fee, risk=risk,
                                 target=target, funding_reserve_fraction=reserve_fraction,
                                 exposure_cap=config["max_exposure_over_equity"],
                                 minimum_free_fraction=config["minimum_free_equity_fraction"],
                                 maximum_margin_fraction=config.get("maximum_allocated_margin_fraction", 1.0),
                                 maximum_nominal_per_allocated_margin=config.get("maximum_nominal_per_allocated_margin", 1e6))
                if size.rejection:
                    skipped[size.rejection] += 1
                    continue
                quantity = size.quantity
                nominal = quantity * entry
                margin = size.initial_margin
                entry_fee = nominal * fee
                if sig.profit_anchor is not None:
                    anchor_fill = fill(sig.profit_anchor, -sig.direction, active_slip, spec)
                    anchor_net = sig.direction * quantity * (anchor_fill - entry) - entry_fee - quantity * anchor_fill * fee - cash * risk * reserve_fraction
                    if anchor_net < cash * target:
                        skipped["reversion_mean_cannot_cover_net_target"] += 1
                        continue
                if cash - size.allocated_margin - entry_fee < cash * config["minimum_free_equity_fraction"] - 1e-10:
                    skipped["insufficient_margin_buffer"] += 1
                    continue
                position = Position(symbol, sig.direction, quantity, entry, reference, t,
                                    t + strategy["max_hold_bars"] * signal_width,
                                    cash, entry_fee, stop, stop, size.planned_stop_loss_and_fees, margin,
                                    size.allocated_margin, size.binding_limit)
                cash -= entry_fee
                break

        if position:
            p = position
            spec = data.instruments[p.symbol]
            active_slip = cost_at(p.symbol, t) if cost_at else slip
            if active_slip is None:
                raise ValueError(f"Missing lagged execution-cost data while position open: {p.symbol} {utc(t)}")
            bar, mark = data.trade[p.symbol][t], data.mark[p.symbol][t]
            full_hour_funding = -p.direction * p.quantity * data.funding[p.symbol][t // HOUR * HOUR] * step / HOUR
            # For an intrabar exit the exact holding fraction is unknown.
            debit_bound = min(full_hour_funding, 0.0)
            guarded_cash = cash + debit_bound
            risk_stop = trigger_for_equity(p, guarded_cash, p.equity_at_entry * (1 - risk), fee, active_slip, spec)
            p.stop = max(p.stop, risk_stop) if p.direction > 0 else min(p.stop, risk_stop)
            tp = trigger_for_equity(p, guarded_cash, p.equity_at_entry * (1 + target), fee, active_slip, spec)
            adverse_mark = mark.low if p.direction > 0 else mark.high
            open_margin_equity = cash + p.direction * p.quantity * (mark.open - p.entry)
            open_breach = open_margin_equity <= p.quantity * mark.open * spec.maintenance_margin
            if open_breach:
                events.append({"utc": utc(t), "type": "possible_margin_breach_at_open", "symbol": p.symbol})
                close(bar.open, t, t, "margin_path_indeterminate")
                status = "invalid_possible_liquidation"
            elif p.direction * (bar.open - p.stop) <= 0:
                close(bar.open, t, t, "stop_at_open")
            elif p.direction * (bar.open - tp) >= 0:
                close(bar.open, t, t, "target_at_open")
            elif t >= p.expiry:
                close(bar.open, t, t, "time_exit")
            else:
                worst_equity = guarded_cash + p.direction * p.quantity * (adverse_mark - p.entry)
                if worst_equity <= p.quantity * adverse_mark * spec.maintenance_margin:
                    events.append({"utc": utc(t), "type": "possible_intrabar_margin_breach", "symbol": p.symbol})
                    apply_funding(debit_bound, abs(full_hour_funding))
                    close(bar.low if p.direction > 0 else bar.high, t, t + step, "margin_path_indeterminate")
                    status = "invalid_possible_liquidation"
                else:
                    stop_hit = bar.low <= p.stop if p.direction > 0 else bar.high >= p.stop
                    target_hit = bar.high >= tp if p.direction > 0 else bar.low <= tp
                    if stop_hit or target_hit:
                        apply_funding(debit_bound, abs(full_hour_funding))
                        close(p.stop if stop_hit else tp, t, t + step,
                              "stop_intrabar" if stop_hit else "target_intrabar", stop_hit and target_hit)
                    else:
                        apply_funding(full_hour_funding)
        # Enforce a flat boundary between independently funded evaluation windows.
        if t + step == end and position:
            close(data.trade[position.symbol][t].close, end, end, "window_end")
        record(t)
        if status != "exploratory_only":
            break

    net_values = [r["net_pnl_usd"] for r in trades]
    wins = sum(x > 0 for x in net_values)
    total_gains = sum(x for x in net_values if x > 0)
    total_losses = -sum(x for x in net_values if x < 0)
    by_symbol = {}
    for symbol in symbols:
        subset = [r for r in trades if r["symbol"] == symbol]
        by_symbol[symbol] = {"trades": len(subset), "net_pnl_usd": sum(r["net_pnl_usd"] for r in subset)}
    monthly = {}
    last_equity = initial
    for point in curve:
        # Label the hour by its start, not by the next month at midnight.
        month = utc(timestamp(point["utc"]) - step)[:7]
        monthly[month] = monthly.get(month, 0.0) + point["equity_usd"] - last_equity
        last_equity = point["equity_usd"]
    final_equity = curve[-1]["equity_usd"] if curve else initial
    return {"summary": {
        "status": status, "strategy": strategy["id"], "target_fraction": target,
        "risk_fraction": risk, "slippage_each_fill": slip,
        "from": utc(start), "to_exclusive": utc(last_processed + step),
        "mark_observation_seconds": step,
        "execution_cost_model": "causal_callback" if cost_at else "constant_fraction",
        "initial_equity_usd": initial, "final_equity_usd": final_equity,
        "net_pnl_usd": final_equity - initial, "return_fraction": final_equity / initial - 1,
        "trades": len(trades), "win_rate": wins / len(trades) if trades else None,
        "profit_factor": total_gains / total_losses if total_losses else None,
        "mean_trade_net_usd": mean(net_values) if net_values else None,
        "worst_trade_net_usd": min(net_values) if net_values else None,
        "mean_entry_exposure": mean(r["exposure_over_equity_at_entry"] for r in trades) if trades else None,
        "max_hourly_mark_drawdown_fraction": max_dd,
        "fees_usd": sum(r["fees_usd"] for r in trades),
        "funding_cashflow_usd": sum(r["funding_cashflow_usd"] for r in trades),
        "funding_intrabar_bound_width_usd": sum(r["funding_intrabar_bound_width_usd"] for r in trades),
        "fill_friction_usd_already_in_gross": sum(r["fill_friction_usd_already_in_gross"] for r in trades),
        "same_hour_double_touches": sum(r["same_hour_stop_and_target"] for r in trades),
        "loss_budget_exceeded_trades": sum(r["actual_loss_exceeds_planned_budget"] for r in trades),
        "net_target_achieved_trades": sum(r["target_net_achieved"] for r in trades),
        "by_symbol": by_symbol, "monthly_mark_pnl_usd": monthly,
        "skipped_signals": dict(skipped), "promotion_allowed": False,
        "ledger_residual_usd": final_equity - initial - sum(net_values),
    }, "trades": trades, "hourly_equity": curve, "events": events}


def passive_context(data: MarketData, config: dict, symbol: str, slip: float, start: int, end: int) -> dict:
    """1x buy-and-hold context, explicitly NOT risk-matched to a stopped strategy."""
    initial = config["initial_equity_usd"]
    fee, spec = config["taker_fee"], data.instruments[symbol]
    entry = fill(data.trade[symbol][start].open, 1, slip, spec)
    quantity = grid(initial / entry, spec.lot, up=False)
    cash = initial - quantity * entry * fee
    funding = 0.0
    peak, dd = initial, 0.0
    for t in range(start, end, HOUR):
        flow = -quantity * data.funding[symbol][t]
        funding += flow
        cash += flow
        equity = cash + quantity * (data.mark[symbol][t].close - entry)
        peak = max(peak, equity)
        dd = max(dd, (peak - equity) / peak)
    exit_price = fill(data.trade[symbol][end - HOUR].close, -1, slip, spec)
    cash += quantity * (exit_price - entry) - quantity * exit_price * fee
    dd = max(dd, (peak - cash) / peak)
    return {"symbol": symbol, "kind": "passive_1x_context_not_risk_matched", "quantity": quantity,
            "final_equity_usd": cash, "return_fraction": cash / initial - 1,
            "max_hourly_mark_drawdown_fraction": dd,
            "fees_usd": quantity * (entry + exit_price) * fee, "funding_cashflow_usd": funding}
