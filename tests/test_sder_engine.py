from __future__ import annotations

import math
from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from sder import EvidenceClass, Mission, Status, assess
from sder.engine import COMPONENTS, natural_lifetime_years
from sder.methodology import Methodology
from sder.models import DisposalPlan, Maneuverability, MissionInputs, Passivation

EVIDENCE = st.sampled_from(list(EvidenceClass))


def ev(value: Any, evidence: EvidenceClass = EvidenceClass.VERIFIED) -> dict[str, Any]:
    return {"value": value, "evidence": evidence}


def full_inputs(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "mean_altitude_km": ev(550.0),
        "mass_kg": ev(150.0),
        "disposal_plan": ev("reentry_within_5y"),
        "disposal_reliability": ev(0.9),
        "passivation": ev("full"),
        "maneuverability": ev("propulsive"),
        "min_miss_distance_km": ev(10.0),
        "relative_speed_km_s": ev(10.0),
    }
    base.update(overrides)
    return base


def mission(**overrides: Any) -> Mission:
    return Mission.model_validate({"mission": {"id": "t"}, "inputs": full_inputs(**overrides)})


inputs_strategy = st.fixed_dictionaries(
    {
        "mean_altitude_km": st.builds(ev, st.floats(150, 40000), EVIDENCE),
        "mass_kg": st.builds(ev, st.floats(1, 20000), EVIDENCE),
        "disposal_plan": st.builds(ev, st.sampled_from(list(DisposalPlan)), EVIDENCE),
        "disposal_reliability": st.builds(ev, st.floats(0, 1), EVIDENCE),
        "passivation": st.builds(ev, st.sampled_from(list(Passivation)), EVIDENCE),
        "maneuverability": st.builds(ev, st.sampled_from(list(Maneuverability)), EVIDENCE),
        "min_miss_distance_km": st.builds(ev, st.floats(0, 500), EVIDENCE),
        "relative_speed_km_s": st.builds(ev, st.floats(0, 20), EVIDENCE),
    }
)


def test_complete_inputs_are_indicative(methodology: Methodology) -> None:
    a = assess(mission(), methodology)
    assert a.status is Status.INDICATIVE
    assert a.score is not None and 0 <= a.low <= a.score <= a.high <= 100
    assert a.methodology_sha256 == methodology.sha256 and len(a.methodology_sha256) == 64
    assert {c.name for c in a.components} == set(COMPONENTS)
    assert "not an official" in a.label


@settings(max_examples=300, deadline=None)
@given(inputs_strategy)
def test_score_bounded_and_interval_contains_point(raw: dict[str, Any]) -> None:
    a = assess(Mission.model_validate({"mission": {"id": "h"}, "inputs": raw}))
    assert a.score is not None
    assert 0 <= a.low <= a.score + 1e-6 and a.score <= a.high + 1e-6 and a.high <= 100


@settings(max_examples=200, deadline=None)
@given(inputs_strategy, st.sampled_from(sorted(MissionInputs.model_fields)))
def test_missing_data_never_lowers_the_score(raw: dict[str, Any], field: str) -> None:
    """Principle 4: absent evidence is never replaced by a favourable assumption."""
    complete = assess(Mission.model_validate({"mission": {"id": "h"}, "inputs": raw}))
    raw = {**raw, field: {"value": None}}
    gap = assess(Mission.model_validate({"mission": {"id": "h"}, "inputs": raw}))
    worst = gap.score if gap.score is not None else 100 * (1 - gap.missing_weight) + 100 * gap.missing_weight
    assert complete.score is not None and worst >= complete.score - 1e-6
    assert gap.high >= complete.high - 1e-6


@settings(max_examples=200, deadline=None)
@given(st.floats(0, 200), st.floats(0, 200))
def test_closer_approach_never_lowers_risk(a_km: float, b_km: float) -> None:
    near, far = sorted([a_km, b_km])
    s_near = assess(mission(min_miss_distance_km=ev(near))).score
    s_far = assess(mission(min_miss_distance_km=ev(far))).score
    assert s_near is not None and s_far is not None and s_near >= s_far - 1e-9


@settings(max_examples=100, deadline=None)
@given(st.floats(150, 2000), st.floats(150, 2000))
def test_lifetime_increases_with_altitude(
    a: float,
    b: float,
) -> None:
    from sder.methodology import load_methodology

    m = load_methodology()
    low, high = sorted([a, b])
    assert natural_lifetime_years(low, m) <= natural_lifetime_years(high, m) + 1e-12


def test_weaker_evidence_widens_interval() -> None:
    strong = assess(mission())
    weak_inputs = {k: {**v, "evidence": "operator_statement"} for k, v in full_inputs().items()}
    weak = assess(Mission.model_validate({"mission": {"id": "w"}, "inputs": weak_inputs}))
    assert strong.score == weak.score
    assert (weak.high - weak.low) > (strong.high - strong.low)


def test_component_evidence_is_the_weakest_input() -> None:
    a = assess(mission(disposal_reliability=ev(0.9, EvidenceClass.OPERATOR_STATEMENT)))
    disposal = next(c for c in a.components if c.name == "disposal")
    assert disposal.evidence is EvidenceClass.OPERATOR_STATEMENT


def test_small_gap_is_provisional_large_gap_is_withheld() -> None:
    provisional = assess(mission(min_miss_distance_km={"value": None}))
    assert provisional.status is Status.PROVISIONAL and provisional.score is not None
    assert math.isclose(provisional.missing_weight, 0.15)

    withheld = assess(mission(mean_altitude_km={"value": None}))  # persistence + environment = 0.35
    assert withheld.status is Status.WITHHELD
    assert withheld.score is None and withheld.band is None and not withheld.band_is_certain
    missing = {c.name for c in withheld.components if c.evidence is None}
    assert missing == {"orbital_persistence", "environment"}


def test_unknown_speed_is_conservative() -> None:
    known = assess(mission(relative_speed_km_s=ev(3.0))).score
    unknown = assess(mission(relative_speed_km_s={"value": None})).score
    assert unknown is not None and known is not None and unknown >= known


def test_disposal_failure_probability_is_penalised() -> None:
    reliable = assess(mission(disposal_reliability=ev(1.0))).score
    shaky = assess(mission(disposal_reliability=ev(0.5))).score
    assert reliable is not None and shaky is not None and shaky > reliable


def test_altitude_outside_bands_uses_default() -> None:
    a = assess(mission(mean_altitude_km=ev(100000.0)))
    env = next(c for c in a.components if c.name == "environment")
    assert "outside" in env.rationale


@pytest.mark.parametrize("field,value", [("disposal_reliability", 1.5), ("relative_speed_km_s", -1.0)])
def test_out_of_range_inputs_rejected(field: str, value: float) -> None:
    with pytest.raises(ValueError, match=field):
        mission(**{field: ev(value)})


def test_methodology_mismatch_rejected(methodology: Methodology) -> None:
    bad = methodology.model_copy(update={"weights": {"disposal": 1.0}})
    with pytest.raises(ValueError, match="components"):
        assess(mission(), bad)
