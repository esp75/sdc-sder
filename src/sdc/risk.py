"""Object-level risk proxy and expected risk reduction (Kadri & Shishkina 2026, §6).

For each resident object i, the paper defines a composite risk proxy

    R_i = M_i x L_i x Pc_i

with mass M (kg), persistence L (the expected fraction of the horizon the object
stays in a hazardous regime, 0-1) and collision probability Pc over the same
horizon (0-1). R_i is a proxy for its contribution to catastrophic fragment
generation, not a probability of catastrophe. An action a changes these terms
for one or more objects, and its expected risk reduction is

    dR(a) = sum_i (R_i,before - R_i,after)

Every term here is a range (low, value, high), not a point. All terms are
non-negative, so the bounds of a product are the products of the bounds.
Credits are counted from the *conservative* bound of dR (lowest plausible
reduction), so uncertainty can only reduce what is issued (principle 4).
"""

from __future__ import annotations

import math
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Estimate(BaseModel):
    """A non-negative quantity with an uncertainty range ``low <= value <= high``."""

    model_config = ConfigDict(frozen=True)

    value: float = Field(ge=0)
    low: float = Field(ge=0)
    high: float = Field(ge=0)

    @model_validator(mode="before")
    @classmethod
    def _point(cls, data: object) -> object:
        """Allow a bare number, or omit ``low``/``high`` to mean an exact value."""
        if isinstance(data, int | float):
            return {"value": data, "low": data, "high": data}
        if isinstance(data, dict) and "value" in data:
            return {"low": data["value"], "high": data["value"], **data}
        return data

    @classmethod
    def exact(cls, value: float) -> Estimate:
        return cls(value=value, low=value, high=value)

    @model_validator(mode="after")
    def _ordered(self) -> Self:
        if not self.low <= self.value <= self.high:
            raise ValueError(f"need low <= value <= high, got {self.low}, {self.value}, {self.high}")
        return self


class RiskTerms(BaseModel):
    """The three terms of R_i for one object in one state (before or after an action)."""

    model_config = ConfigDict(frozen=True)

    mass_kg: Estimate
    persistence: Estimate = Field(description="Fraction of the horizon spent in a hazardous regime, 0-1.")
    collision_probability: Estimate = Field(description="Probability of collision over the horizon, 0-1.")

    @model_validator(mode="after")
    def _fractions(self) -> Self:
        for name in ("persistence", "collision_probability"):
            if getattr(self, name).high > 1:
                raise ValueError(f"{name} must lie in [0, 1]")
        return self

    @property
    def risk(self) -> Estimate:
        m, lt, pc = self.mass_kg, self.persistence, self.collision_probability
        return Estimate(
            value=m.value * lt.value * pc.value,
            low=m.low * lt.low * pc.low,
            high=m.high * lt.high * pc.high,
        )


_ZERO = Estimate.exact(0)
REMOVED = RiskTerms(mass_kg=_ZERO, persistence=_ZERO, collision_probability=_ZERO)
"""Terms for an object confirmed to have left the regime (reentered or removed)."""


class ObjectChange(BaseModel):
    """One object affected by an action: its terms before and after."""

    model_config = ConfigDict(frozen=True)

    object_id: str = Field(min_length=1, description="COSPAR or NORAD identifier.")
    before: RiskTerms
    after: RiskTerms = REMOVED


class Action(BaseModel):
    """A mitigation or remediation action and the objects it changes."""

    model_config = ConfigDict(frozen=True)

    action_id: str = Field(min_length=1)
    description: str | None = None
    horizon_years: float = Field(gt=0, description="Horizon H over which L and Pc are defined.")
    changes: list[ObjectChange] = Field(min_length=1)

    @model_validator(mode="after")
    def _unique_objects(self) -> Self:
        ids = [c.object_id.strip().upper() for c in self.changes]
        if len(ids) != len(set(ids)):
            raise ValueError("an object may appear only once per action (no double counting)")
        return self


class ObjectDelta(BaseModel):
    model_config = ConfigDict(frozen=True)

    object_id: str
    risk_before: Estimate
    risk_after: Estimate
    delta: float
    delta_low: float
    delta_high: float


class DeltaR(BaseModel):
    """Expected risk reduction of an action, with its uncertainty range."""

    model_config = ConfigDict(frozen=True)

    label: str = "Illustrative research estimate - not an issued SDC"
    action_id: str
    horizon_years: float
    value: float
    low: float = Field(description="Conservative bound: lowest plausible reduction.")
    high: float
    objects: list[ObjectDelta]


def delta_r(action: Action) -> DeltaR:
    """dR(a) = sum_i (R_i,before - R_i,after), with bounds."""
    objects = []
    for c in action.changes:
        before, after = c.before.risk, c.after.risk
        objects.append(
            ObjectDelta(
                object_id=c.object_id,
                risk_before=before,
                risk_after=after,
                delta=before.value - after.value,
                delta_low=before.low - after.high,
                delta_high=before.high - after.low,
            )
        )
    return DeltaR(
        action_id=action.action_id,
        horizon_years=action.horizon_years,
        value=math.fsum(o.delta for o in objects),
        low=math.fsum(o.delta_low for o in objects),
        high=math.fsum(o.delta_high for o in objects),
        objects=objects,
    )


def issuable_units(result: DeltaR, reference_unit: float) -> int:
    """Whole credit units supported by the conservative bound of dR.

    ``reference_unit`` is dR0, the reduction one unit represents, set by a
    governing body or calibrated from observed dR (paper §6). An action whose
    lowest plausible reduction is not positive supports no units.
    """
    if reference_unit <= 0:
        raise ValueError("reference_unit must be positive")
    return max(0, math.floor(result.low / reference_unit))
