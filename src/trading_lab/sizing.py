"""Local position sizing: account risk, allocated margin and nominal are distinct."""

from dataclasses import dataclass
from decimal import Decimal, ROUND_FLOOR
import math

from .data import Instrument


@dataclass(frozen=True)
class SizePlan:
    quantity: float = 0.0
    initial_margin: float = 0.0
    allocated_margin: float = 0.0
    planned_stop_loss_and_fees: float = 0.0
    binding_limit: str = ""
    rejection: str = ""


def plan_size(*, equity: float, entry: float, stop_fill: float, direction: int,
              instrument: Instrument, fee: float, risk: float, target: float,
              funding_reserve_fraction: float, exposure_cap: float,
              minimum_free_fraction: float, maximum_margin_fraction: float = 1.0,
              maximum_nominal_per_allocated_margin: float = 1e6) -> SizePlan:
    inputs = (equity, entry, stop_fill, fee, risk, target, funding_reserve_fraction,
              exposure_cap, minimum_free_fraction, maximum_margin_fraction,
              maximum_nominal_per_allocated_margin)
    if not all(math.isfinite(x) for x in inputs):
        raise ValueError("Nonfinite sizing input")
    if (min(equity, entry, stop_fill, exposure_cap) <= 0 or direction not in (-1, 1)
            or not 0 <= fee < 1 or not 0 < risk < 1 or target <= 0
            or not 0 <= funding_reserve_fraction < 1 or not 0 <= minimum_free_fraction < 1
            or not 0 < maximum_margin_fraction <= 1 or maximum_nominal_per_allocated_margin < 1):
        raise ValueError("Invalid sizing policy")
    im = instrument.initial_margin
    if not 0 < im <= 1 or instrument.lot <= 0 or instrument.minimum <= 0:
        raise ValueError("Invalid instrument sizing rules")
    loss_per_unit = direction * (entry - stop_fill) + fee * (entry + stop_fill)
    if direction * (entry - stop_fill) <= 0 or loss_per_unit <= 0:
        return SizePlan(rejection="invalid_stop_geometry")
    allocation_rate = max(im, 1 / maximum_nominal_per_allocated_margin)
    limits = {
        "stop_risk": equity * risk * (1 - funding_reserve_fraction) / loss_per_unit,
        "account_exposure": equity * exposure_cap / entry,
        "allocated_margin": equity * maximum_margin_fraction / (entry * allocation_rate),
        "free_equity_after_entry_fee": equity * (1 - minimum_free_fraction) / (entry * (allocation_rate + fee)),
    }
    binding = min(limits, key=limits.get)
    units = Decimal(str(limits[binding])) / Decimal(str(instrument.lot))
    quantity = float(units.to_integral_value(rounding=ROUND_FLOOR) * Decimal(str(instrument.lot)))
    if quantity < instrument.minimum:
        return SizePlan(binding_limit=binding, rejection="minimum_quantity_exceeds_budget")
    nominal = quantity * entry
    if nominal >= instrument.tier_ceiling_usd:
        return SizePlan(binding_limit=binding, rejection="unsupported_margin_tier")
    # No assumed future funding income may make an otherwise impossible target feasible.
    required_exit = (equity * target + nominal * fee + direction * nominal) / (quantity * (direction - fee))
    if required_exit <= 0 or direction * (required_exit - entry) <= 0:
        return SizePlan(binding_limit=binding, rejection="target_has_no_positive_exit_price")
    return SizePlan(quantity, nominal * im, nominal * allocation_rate,
                    quantity * loss_per_unit, binding)
