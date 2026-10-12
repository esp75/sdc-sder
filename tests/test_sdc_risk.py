from __future__ import annotations

import json
from itertools import combinations
from typing import Any

import pytest
import yaml
from conftest import EXAMPLES
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from sdc import Action, Estimate, ObjectChange, RiskTerms, delta_r, issuable_units
from sdc.cli import main
from sdc.risk import REMOVED

ACTIONS = EXAMPLES / "actions"

fraction = st.floats(min_value=0, max_value=1, allow_nan=False)
mass = st.floats(min_value=0, max_value=1e4, allow_nan=False)


@st.composite
def estimates(draw: st.DrawFn, base: st.SearchStrategy[float]) -> Estimate:
    a, b, c = sorted(draw(base) for _ in range(3))
    return Estimate(low=a, value=b, high=c)


@st.composite
def terms(draw: st.DrawFn) -> RiskTerms:
    return RiskTerms(
        mass_kg=draw(estimates(mass)),
        persistence=draw(estimates(fraction)),
        collision_probability=draw(estimates(fraction)),
    )


def action(*changes: ObjectChange) -> Action:
    return Action(action_id="a", horizon_years=25, changes=list(changes))


def load(name: str) -> Action:
    return Action.model_validate(yaml.safe_load((ACTIONS / name).read_text()))


# ---- the model --------------------------------------------------------------


def test_risk_is_product_of_terms() -> None:
    t = RiskTerms(mass_kg=Estimate(value=1000), persistence=0.5, collision_probability=0.01)
    assert t.risk.value == pytest.approx(5.0)


@given(terms())
def test_risk_interval_contains_value(t: RiskTerms) -> None:
    r = t.risk
    assert r.low <= r.value <= r.high


@given(terms())
@settings(max_examples=200)
def test_removal_never_increases_risk(before: RiskTerms) -> None:
    """Removing an object (R_after = 0) can only reduce risk, at every bound."""
    result = delta_r(action(ObjectChange(object_id="X", before=before)))
    assert result.low >= 0
    assert result.low <= result.value <= result.high


@given(st.lists(st.tuples(terms(), terms()), min_size=1, max_size=6))
def test_delta_r_is_additive_across_objects(pairs: list[tuple[RiskTerms, RiskTerms]]) -> None:
    changes = [ObjectChange(object_id=f"O{i}", before=b, after=a) for i, (b, a) in enumerate(pairs)]
    whole = delta_r(action(*changes))
    parts = [delta_r(action(c)) for c in changes]
    assert whole.value == pytest.approx(sum(p.value for p in parts), abs=1e-6)
    assert whole.low == pytest.approx(sum(p.low for p in parts), abs=1e-6)


@given(st.lists(terms(), min_size=4, max_size=8), st.integers(min_value=1, max_value=3))
@settings(max_examples=100)
def test_targeting_highest_risk_objects_maximises_delta_r(population: list[RiskTerms], k: int) -> None:
    """Paper §3 and Fig. 3: under the proxy, removing the k highest-R objects
    yields at least the dR of removing any other k objects."""
    objs = [ObjectChange(object_id=f"O{i}", before=t) for i, t in enumerate(population)]
    targeted = sorted(objs, key=lambda o: o.before.risk.value, reverse=True)[:k]
    best = delta_r(action(*targeted)).value
    for other in combinations(objs, k):
        assert delta_r(action(*other)).value <= best + 1e-9


@given(terms(), st.floats(min_value=1e-6, max_value=1e3))
def test_units_come_from_the_conservative_bound(before: RiskTerms, unit: float) -> None:
    result = delta_r(action(ObjectChange(object_id="X", before=before)))
    n = issuable_units(result, unit)
    assert n >= 0
    assert n * unit <= result.low + 1e-9


def test_risk_increase_issues_nothing() -> None:
    worse = RiskTerms(mass_kg=Estimate(value=100), persistence=1, collision_probability=0.1)
    better = RiskTerms(mass_kg=Estimate(value=100), persistence=0.1, collision_probability=0.1)
    result = delta_r(action(ObjectChange(object_id="X", before=better, after=worse)))
    assert result.value < 0
    assert issuable_units(result, 0.001) == 0


# ---- validation -------------------------------------------------------------


@pytest.mark.parametrize(
    "data",
    [
        {"value": 1, "low": 2, "high": 3},
        {"value": -1},
        {"value": 1, "low": 0, "high": 0.5},
    ],
)
def test_estimate_rejects_disordered_or_negative(data: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        Estimate.model_validate(data)


def test_fractions_must_not_exceed_one() -> None:
    with pytest.raises(ValidationError, match="persistence"):
        RiskTerms(
            mass_kg=Estimate(value=1), persistence=Estimate(value=1.5), collision_probability=REMOVED.mass_kg
        )


def test_same_object_twice_in_one_action_is_rejected() -> None:
    c = ObjectChange(object_id="1999-025a", before=REMOVED)
    with pytest.raises(ValidationError, match="double counting"):
        action(c, c.model_copy(update={"object_id": " 1999-025A "}))


def test_reference_unit_must_be_positive() -> None:
    with pytest.raises(ValueError, match="positive"):
        issuable_units(delta_r(load("adr-derelict-upper-stage.yaml")), 0)


# ---- examples and CLI -------------------------------------------------------


def test_upper_stage_removal_dominates_smallsat_deorbit() -> None:
    """The examples reproduce the paper's point: one massive derelict outweighs
    an early smallsat disposal by orders of magnitude."""
    adr = delta_r(load("adr-derelict-upper-stage.yaml"))
    pmd = delta_r(load("early-deorbit-smallsat.yaml"))
    assert adr.value == pytest.approx(89.0)
    assert pmd.value == pytest.approx(0.1788)
    assert adr.low > 100 * pmd.low


def test_cli_delta_r_table_and_json(capsys: pytest.CaptureFixture[str]) -> None:
    path = str(ACTIONS / "adr-derelict-upper-stage.yaml")
    assert main(["delta-r", path, "--reference-unit", "10"]) == 0
    out = capsys.readouterr().out
    assert "not an issued SDC" in out and "units        2" in out
    assert main(["delta-r", path, "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["issuable_units"] is None
    assert data["objects"][0]["object_id"] == "EXAMPLE-RB-1"
