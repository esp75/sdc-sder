from __future__ import annotations

import json

import pytest
from conftest import EXAMPLES

from sder import assess
from sder.cli import load_mission, main
from sder.models import Band
from sder.sensitivity import analyse, render, variance_shares


def test_variance_shares_sum_to_one_and_follow_interval_width() -> None:
    a = assess(load_mission(EXAMPLES / "leo-smallsat-responsible.yaml"))
    shares = variance_shares(a)
    assert sum(shares.values()) == pytest.approx(1.0)
    # The disposal plan rests on the operator's word: the widest weighted interval.
    assert max(shares, key=shares.__getitem__) == "disposal"


def test_analysis_is_reproducible_and_bounded() -> None:
    m = load_mission(EXAMPLES / "leo-smallsat-responsible.yaml")
    one, two = analyse(m, samples=500, seed=7), analyse(m, samples=500, seed=7)
    assert one == two
    assert sum(one.band_share_inputs.values()) == pytest.approx(1.0)
    assert 0 <= one.band_kept_weights <= 1
    lo, hi = one.score_range_weights
    assert lo <= hi
    assert one.nominal_band is Band.LOW


def test_lower_concentration_moves_weights_further() -> None:
    m = load_mission(EXAMPLES / "leo-smallsat-responsible.yaml")
    tight, loose = analyse(m, samples=800, concentration=1000), analyse(m, samples=800, concentration=5)
    width = lambda s: s.score_range_weights[1] - s.score_range_weights[0]  # noqa: E731
    assert width(loose) > width(tight)


def test_withheld_mission_still_reports_variance() -> None:
    s = analyse(load_mission(EXAMPLES / "sparse-operator-claims.yaml"), samples=200)
    assert s.nominal_score is None and "withheld" in render(s)


def test_zero_width_intervals_give_zero_shares() -> None:
    a = assess(load_mission(EXAMPLES / "leo-smallsat-responsible.yaml"))
    flat = a.model_copy(
        update={"components": [c.model_copy(update={"low": c.risk, "high": c.risk}) for c in a.components]}
    )
    assert set(variance_shares(flat).values()) == {0.0}


def test_cli_sensitivity(capsys: pytest.CaptureFixture[str]) -> None:
    f = str(EXAMPLES / "leo-smallsat-responsible.yaml")
    assert main(["sensitivity", f, "--samples", "200"]) == 0
    assert "variance" in capsys.readouterr().out
    assert main(["sensitivity", f, "--samples", "200", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)[0]["samples"] == 200
