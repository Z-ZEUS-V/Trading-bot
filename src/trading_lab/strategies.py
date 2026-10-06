"""Signals from closed candles only; independent of Kraken and of any LLM."""

from dataclasses import dataclass

from .data import Candle, HOUR


@dataclass(frozen=True)
class Signal:
    available_at: int
    direction: int
    atr: float
    stop_reference: float | None = None
    profit_anchor: float | None = None


def signals(hourly: dict[int, Candle], spec: dict, cutoff: int) -> dict[int, Signal]:
    width = spec["bar_hours"] * HOUR
    groups: dict[int, list[Candle]] = {}
    for t, candle in sorted(hourly.items()):
        if t + HOUR <= cutoff:
            groups.setdefault(t // width * width, []).append(candle)
    bars = []
    for start, rows in sorted(groups.items()):
        if [r.start for r in rows] != list(range(start, start + width, HOUR)):
            continue
        bars.append(Candle(start, rows[0].open, max(r.high for r in rows), min(r.low for r in rows),
                           rows[-1].close, sum(r.volume for r in rows)))
    output = {}
    tr = []
    for i, bar in enumerate(bars):
        previous_close = bars[i - 1].close if i else bar.open
        tr.append(max(bar.high - bar.low, abs(bar.high - previous_close), abs(bar.low - previous_close)))
        needed = max(spec["lookback"], spec["atr_period"])
        if i < needed or bars[i].start - bars[i - needed].start != needed * width:
            continue
        atr = sum(tr[i - spec["atr_period"] + 1:i + 1]) / spec["atr_period"]
        if atr <= 0:
            continue
        if spec["kind"] == "breakout":
            past = bars[i - spec["lookback"]:i]
            direction = 1 if bar.close > max(b.high for b in past) else (-1 if bar.close < min(b.low for b in past) else 0)
        elif spec["kind"] == "momentum":
            change = bar.close - bars[i - spec["lookback"]].close
            direction = (change > 0) - (change < 0)
        else:
            raise ValueError("Unknown strategy")
        if direction:
            output[bar.start + width] = Signal(bar.start + width, direction, atr)
    return output
