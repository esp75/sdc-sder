"""SDER research scoring engine.

The engine is a pure function: the same inputs and methodology always give the
same assessment. It implements the v0.1 principles as code:

* Each component carries an uncertainty interval that widens as the evidence
  gets weaker (principles 2 and 3).
* Missing inputs are scored at their worst case and reported explicitly. Too
  much missing weight withholds the result (principle 4).
* Every assessment records the methodology id and its SHA-256 (principle 7).
"""

from __future__ import annotations

import itertools
import math
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .methodology import Methodology, load_methodology
from .models import (
    EVIDENCE_STRENGTH,
    Assessment,
    Band,
    ComponentResult,
    EvidenceClass,
    Evidenced,
    Mission,
    MissionInputs,
    Status,
)

WORST_CASE = 100.0


@dataclass(frozen=True)
class _Raw:
    """A component's risk before evidence and missing-data handling."""

    risk: float | None
    used: dict[str, Evidenced[Any]]
    rationale: str


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _missing(used: dict[str, Evidenced[Any]]) -> list[str]:
    return [name for name, field in used.items() if field.value is None]


def _log_interp(x: float, table: list[tuple[float, float]]) -> float:
    """Interpolate y linearly in log10 space; clamp outside the table."""
    if x <= table[0][0]:
        return table[0][1]
    for (x0, y0), (x1, y1) in itertools.pairwise(table):
        if x <= x1:
            t = (x - x0) / (x1 - x0)
            return float(10 ** (math.log10(y0) + t * (math.log10(y1) - math.log10(y0))))
    return table[-1][1]


def natural_lifetime_years(altitude_km: float, m: Methodology) -> float:
    return _log_interp(altitude_km, m.orbital_persistence.lifetime_table)


def _disposal(i: MissionInputs, m: Methodology) -> _Raw:
    used: dict[str, Evidenced[Any]] = {
        "disposal_plan": i.disposal_plan,
        "disposal_reliability": i.disposal_reliability,
    }
    plan, rel = i.disposal_plan.value, i.disposal_reliability.value
    if plan is None or rel is None:
        return _Raw(None, used, "disposal plan or its reliability not provided")
    base = m.disposal.plan_risk[plan]
    risk = rel * base + (1 - rel) * WORST_CASE
    return _Raw(risk, used, f"plan '{plan}' (residual {base:g}) with {rel:.0%} success probability")


def _persistence(i: MissionInputs, m: Methodology) -> _Raw:
    used: dict[str, Evidenced[Any]] = {"mean_altitude_km": i.mean_altitude_km}
    alt = i.mean_altitude_km.value
    if alt is None:
        return _Raw(None, used, "altitude not provided")
    years = natural_lifetime_years(alt, m)
    sat = m.orbital_persistence.saturation_years
    risk = _clamp(100 * math.log10(1 + years) / math.log10(1 + sat))
    return _Raw(risk, used, f"~{years:.3g} years natural decay at {alt:g} km if left uncontrolled")


def _environment(i: MissionInputs, m: Methodology) -> _Raw:
    used: dict[str, Evidenced[Any]] = {"mean_altitude_km": i.mean_altitude_km}
    alt = i.mean_altitude_km.value
    if alt is None:
        return _Raw(None, used, "altitude not provided")
    for low, high, risk in m.environment.bands:
        if low <= alt < high:
            return _Raw(risk, used, f"congestion band {low:g}-{high:g} km")
    return _Raw(m.environment.default, used, "outside tabulated congestion bands")


def _conjunction(i: MissionInputs, m: Methodology) -> _Raw:
    used: dict[str, Evidenced[Any]] = {"min_miss_distance_km": i.min_miss_distance_km}
    miss, speed = i.min_miss_distance_km.value, i.relative_speed_km_s.value
    if miss is None:
        return _Raw(None, used, "no conjunction screening provided")
    p = m.conjunction
    geometry = 100.0 * math.exp(-miss / p.characteristic_km)
    if speed is None:
        # Conservative on both counts: no speed discount, and the weakest evidence
        # class, so a missing input never narrows the interval.
        factor, note = 1.0, "speed unknown: no discount, weakest evidence assumed"
        used["relative_speed_km_s"] = Evidenced(evidence=EvidenceClass.OPERATOR_STATEMENT)
    else:
        used["relative_speed_km_s"] = i.relative_speed_km_s
        factor = _clamp(speed / p.reference_speed_km_s, p.min_speed_factor, 1.0)
        note = f"{speed:g} km/s"
    return _Raw(geometry * factor, used, f"closest approach {miss:g} km ({note})")


def _consequence(i: MissionInputs, m: Methodology) -> _Raw:
    used: dict[str, Evidenced[Any]] = {"mass_kg": i.mass_kg}
    mass = i.mass_kg.value
    if mass is None:
        return _Raw(None, used, "mass not provided")
    risk = _clamp(100 * math.log10(max(mass, 1.0)) / math.log10(m.consequence.saturation_mass_kg))
    return _Raw(risk, used, f"{mass:g} kg fragmentation mass")


def _passivation(i: MissionInputs, m: Methodology) -> _Raw:
    used: dict[str, Evidenced[Any]] = {"passivation": i.passivation}
    level = i.passivation.value
    if level is None:
        return _Raw(None, used, "passivation plan not provided")
    return _Raw(m.passivation.levels[level], used, f"passivation: {level}")


def _maneuverability(i: MissionInputs, m: Methodology) -> _Raw:
    used: dict[str, Evidenced[Any]] = {"maneuverability": i.maneuverability}
    level = i.maneuverability.value
    if level is None:
        return _Raw(None, used, "maneuverability not provided")
    return _Raw(m.maneuverability.levels[level], used, f"maneuverability: {level}")


COMPONENTS: dict[str, Callable[[MissionInputs, Methodology], _Raw]] = {
    "disposal": _disposal,
    "orbital_persistence": _persistence,
    "environment": _environment,
    "conjunction": _conjunction,
    "consequence": _consequence,
    "passivation": _passivation,
    "maneuverability": _maneuverability,
}


def _weakest(used: dict[str, Evidenced[Any]]) -> EvidenceClass:
    return min((f.evidence for f in used.values()), key=EVIDENCE_STRENGTH.__getitem__)


def _component(name: str, inputs: MissionInputs, m: Methodology) -> ComponentResult:
    weight = m.weights[name]
    raw = COMPONENTS[name](inputs, m)
    if raw.risk is None:
        return ComponentResult(
            name=name,
            weight=weight,
            risk=WORST_CASE,
            low=0.0,
            high=WORST_CASE,
            contribution=round(weight * WORST_CASE, 4),
            evidence=None,
            missing_inputs=_missing(raw.used),
            rationale=f"MISSING: {raw.rationale}; scored at worst case",
        )
    evidence = _weakest(raw.used)
    half = m.evidence_uncertainty[evidence]
    risk = _clamp(raw.risk)
    return ComponentResult(
        name=name,
        weight=weight,
        risk=round(risk, 4),
        low=round(_clamp(risk - half), 4),
        high=round(_clamp(risk + half), 4),
        contribution=round(weight * risk, 4),
        evidence=evidence,
        missing_inputs=[],
        rationale=raw.rationale,
    )


def band_for(score: float, m: Methodology) -> Band:
    if score < m.bands.low_below:
        return Band.LOW
    if score < m.bands.medium_below:
        return Band.MEDIUM
    return Band.HIGH


def assess(mission: Mission, methodology: Methodology | None = None) -> Assessment:
    """Score a mission under a methodology (default: bundled research v0.1)."""
    m = methodology or load_methodology()
    if set(m.weights) != set(COMPONENTS):
        raise ValueError(f"methodology weights {sorted(m.weights)} != components {sorted(COMPONENTS)}")
    comps = [_component(name, mission.inputs, m) for name in COMPONENTS]

    point = sum(c.weight * c.risk for c in comps)
    low = sum(c.weight * c.low for c in comps)
    high = sum(c.weight * c.high for c in comps)
    missing_weight = sum(c.weight for c in comps if c.evidence is None)

    if missing_weight == 0:
        status = Status.INDICATIVE
    elif missing_weight <= m.withhold_if_missing_weight_above:
        status = Status.PROVISIONAL
    else:
        status = Status.WITHHELD

    withheld = status is Status.WITHHELD
    return Assessment(
        mission_id=mission.mission.id,
        methodology_id=m.id,
        methodology_sha256=m.sha256,
        status=status,
        score=None if withheld else round(point, 2),
        low=round(low, 2),
        high=round(high, 2),
        band=None if withheld else band_for(point, m),
        band_is_certain=not withheld and band_for(low, m) == band_for(high, m),
        missing_weight=round(missing_weight, 4),
        components=comps,
    )
