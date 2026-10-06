"""Causality, real time units and adverse path checks for minute replay."""
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from trading_lab.data import Candle, Instrument, MarketData
from trading_lab.strategies import Signal
from trading_lab.intraday import aggregate, intraday_signals, quoted_cost
from trading_lab.simulator import simulate


class IntradayChecks(unittest.TestCase):
    def test_aggregation_excludes_incomplete_or_future_bars(self):
        minutes={t:Candle(t,100,101,99,100,1) for t in range(0,600,60)}
        self.assertEqual(len(aggregate(minutes,300,599)),1)
        del minutes[120]
        self.assertEqual(len(aggregate(minutes,300,600)),1)
        self.assertEqual(aggregate(minutes,300,600)[0].start,300)

    def test_breakout_needs_confirmation_and_one_minute_delay(self):
        bars={t:Candle(t,100,101,99,100,1) for t in range(0,1200,60)}
        bars[1200]=Candle(1200,100,103,99,102,1)
        bars[1260]=Candle(1260,102,104,101,102.5,1)
        spec={"kind":"confirmed_breakout","bar_seconds":60,"lookback":20,"atr_period":14,"stop_atr":1.5}
        self.assertEqual(intraday_signals(bars,spec,1260,60),{})
        result=intraday_signals(bars,spec,1320,60)
        self.assertEqual(list(result),[1380])
        self.assertEqual(result[1380].available_at,1320)
        self.assertEqual(result[1380].direction,1)
        bars[1320]=Candle(1320,102.5,1000,1,999,100)
        self.assertEqual(result,intraday_signals(bars,spec,1320,60))

    def test_reversion_uses_band_from_before_excursion(self):
        bars={i*60:Candle(i*60,100,101,99,99 if i%2 else 101,1) for i in range(20)}
        bars[1200]=Candle(1200,100,100,96,97,1)
        bars[1260]=Candle(1260,97,99,97,98.5,1)
        spec={"kind":"band_reentry","bar_seconds":60,"lookback":20,"atr_period":14,"stop_atr":1,"band_standard_deviations":2}
        s=intraday_signals(bars,spec,1320,60)[1380]
        self.assertEqual(s.direction,1)
        self.assertEqual(s.profit_anchor,100)

    def test_cost_never_uses_current_unclosed_quote_bucket(self):
        quotes={0:.0002,300:.0004,600:.1}
        self.assertAlmostEqual(quoted_cost(quotes,601,.0001,0),.0003)
        quotes[600]=.9
        self.assertAlmostEqual(quoted_cost(quotes,601,.0001,0),.0003)
        self.assertIsNone(quoted_cost({0:.1},601,.0001,0))

    def fixture(self, double_touch=False):
        trade={t:Candle(t,100,100.01,99.99,100,1) for t in range(0,7200,60)}
        if double_touch: trade[0]=Candle(0,100,102,98,100,1)
        data=MarketData({"X":trade},{"X":dict(trade)},{"X":{0:.01,3600:.02}},
            {"X":Instrument("X",.001,.001,.001,.1,.05,math.inf)},{},[])
        cfg={"symbols_priority":["X"],"initial_equity_usd":50,"taker_fee":0,"risk_fraction":.01,
            "funding_reserve_fraction_of_risk":.1,"max_exposure_over_equity":10,
            "minimum_free_equity_fraction":.6,"maximum_allocated_margin_fraction":.4,
            "maximum_nominal_per_allocated_margin":25,"bar_step_seconds":60}
        strategy={"id":"fixture","bar_seconds":60,"stop_atr":1,"max_hold_bars":60}
        return data,cfg,strategy

    def test_hourly_funding_is_prorated_and_not_charged_after_exact_time_exit(self):
        data,cfg,strategy=self.fixture()
        r=simulate(data,cfg,strategy,.05,0,0,7200,signal_schedule={"X":{0:Signal(0,1,1,99)}})
        self.assertEqual(len(r["trades"]),1)
        t=r["trades"][0]
        self.assertEqual(t["exit_reason"],"time_exit")
        self.assertAlmostEqual(t["funding_cashflow_usd"],-t["quantity_base"]*.01)
        self.assertAlmostEqual(r["summary"]["ledger_residual_usd"],0,places=10)

    def test_minute_double_touch_uses_stop_first(self):
        data,cfg,strategy=self.fixture(True)
        r=simulate(data,cfg,strategy,.005,0,0,7200,signal_schedule={"X":{0:Signal(0,1,1,99)}})
        t=r["trades"][0]
        self.assertTrue(t["same_hour_stop_and_target"])
        self.assertEqual(t["exit_reason"],"stop_intrabar")
        self.assertLess(t["net_pnl_usd"],0)

    def test_reversion_target_must_fit_observed_mean_after_costs(self):
        data,cfg,strategy=self.fixture()
        r=simulate(data,cfg,strategy,.005,0,0,7200,signal_schedule={"X":{0:Signal(0,1,1,99,100.01)}})
        self.assertEqual(r["summary"]["trades"],0)
        self.assertEqual(r["summary"]["skipped_signals"]["reversion_mean_cannot_cover_net_target"],1)


if __name__ == "__main__": unittest.main()
