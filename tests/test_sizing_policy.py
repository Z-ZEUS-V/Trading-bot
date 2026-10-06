"""Boundary checks for money-at-risk and the user's margin cap; offline fixtures."""
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from trading_lab.data import Instrument
from trading_lab.sizing import plan_size


class SizingPolicyTests(unittest.TestCase):
    def size(self, **changes):
        args = dict(equity=50, entry=100, stop_fill=99.5, direction=1,
                    instrument=Instrument("fixture", .001, .0001, .0001, .1, .05, math.inf),
                    fee=.0005, risk=.0025, target=.005, funding_reserve_fraction=.1,
                    exposure_cap=10, minimum_free_fraction=.6, maximum_margin_fraction=.4,
                    maximum_nominal_per_allocated_margin=25)
        args.update(changes)
        return plan_size(**args)

    def test_stop_costs_and_funding_reserve_fit_account_budget(self):
        p = self.size()
        self.assertFalse(p.rejection)
        self.assertLessEqual(p.planned_stop_loss_and_fees + .0125, .125 + 1e-12)

    def test_25x_uses_partial_margin_and_reserves_entry_fee(self):
        p = self.size(risk=.05, target=.05, stop_fill=99.9,
                      instrument=Instrument("hypothetical", .001, .0001, .0001, .02, .01, math.inf))
        self.assertFalse(p.rejection)
        self.assertLessEqual(p.allocated_margin, 20)
        self.assertAlmostEqual(p.quantity * 100 / p.allocated_margin, 25)
        self.assertLessEqual(p.quantity * 100 / 50, 10)
        self.assertGreaterEqual(50 - p.allocated_margin - p.quantity * 100 * .0005, 30)

    def test_venue_10_percent_margin_cannot_be_overridden_by_25x(self):
        p = self.size(risk=.05, target=.05, stop_fill=99.9)
        self.assertAlmostEqual(p.quantity * 100 / p.allocated_margin, 10)
        self.assertLessEqual(p.quantity * 100, 200)

    def test_small_short_cannot_earn_more_than_its_notional_from_price(self):
        p = self.size(entry=2046.5, stop_fill=2484.1, direction=-1, risk=.02, target=.1,
                      instrument=Instrument("ETH_fixture", .1, .001, .001, .1, .05, math.inf))
        self.assertEqual(p.rejection, "target_has_no_positive_exit_price")

    def test_minimum_lot_does_not_force_risk_up(self):
        p = self.size(instrument=Instrument("large_lot", .1, 1, 1, .1, .05, math.inf))
        self.assertEqual(p.rejection, "minimum_quantity_exceeds_budget")


if __name__ == "__main__":
    unittest.main()
