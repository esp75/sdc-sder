from __future__ import annotations

import json
import math
from pathlib import Path

import pytest
from conftest import ROOT
from hypothesis import given, settings
from hypothesis import strategies as st

from sdc.catalogue import (
    Atmosphere,
    Catalogue,
    CatalogueObject,
    Environment,
    ObjectKind,
    area_estimate,
    backtest_lifetimes,
    collision_probability,
    compare_removal,
    concentration,
    lifetime_estimate,
    load_objects,
    mass_estimate,
    removal_delta,
    risk_terms,
)
from sdc.cli import main

DATA = ROOT / "data" / "gcat"
HEADER = (
    "jcat\tsatcat\tname\ttype\tactive\towner\tstate\tperigee_km\tapogee_km\tinc_deg\torbit_epoch\t"
    "mass_kg\tmass_flag\tlength_m\tdiameter_m\tspan_m\n"
)


def obj(
    perigee: float = 800.0,
    apogee: float = 800.0,
    mass: float | None = 1000.0,
    length: float | None = 4.0,
    diameter: float | None = 2.0,
    kind: ObjectKind = ObjectKind.ROCKET_BODY,
    active: bool = False,
    jcat: str = "S1",
) -> CatalogueObject:
    return CatalogueObject(
        jcat=jcat, satcat=jcat[1:], name=f"Test {jcat}", kind=kind, active=active, owner="X", state="XX",
        perigee_km=perigee, apogee_km=apogee, inc_deg=98.0, mass_kg=mass, mass_uncertain=False,
        length_m=length, diameter_m=diameter, span_m=None,
    )  # fmt: skip


@pytest.fixture(scope="module")
def atm() -> Atmosphere:
    return Atmosphere.bundled()


@pytest.fixture(scope="module")
def snapshot() -> Catalogue:
    return Catalogue.load(DATA / "leo-objects.tsv")


def write_fixture(tmp_path: Path) -> Path:
    rows = [
        "S100\t00100\tBig Stage 2\tR2\tno\tA\tSU\t840\t850\t71.0\t2026 Oct 10\t9000\t\t11\t3.9\t11\n",
        "S101\t00101\tOld Sat\tP\tno\tB\tUS\t780\t790\t98.5\t2026 Oct 10\t800\t?\t3\t2\t8\n",
        "S102\t00102\tLive Sat\tP\tyes\tC\tUS\t550\t552\t53.0\t2026 Oct 10\t300\t\t\t\t\n",
        "S103\t00103\tFragment\tD\tno\t\tCN\t800\t900\t98.0\t-\t\t\t\t\t\n",
        "S104\t00104\tNo Mass\tP\tno\tD\tFR\t600\t610\t-\t2026 Oct 10\t-\t\t1\t1\t1\n",
    ]
    path = tmp_path / "leo.tsv"
    path.write_text(HEADER + "".join(rows))
    return path


def test_parser_reads_kinds_flags_and_missing_values(tmp_path: Path) -> None:
    objects = {o.jcat: o for o in load_objects(write_fixture(tmp_path))}
    assert objects["S100"].kind is ObjectKind.ROCKET_BODY and objects["S100"].satcat == "100"
    assert objects["S101"].mass_uncertain and objects["S101"].kind is ObjectKind.PAYLOAD
    assert objects["S102"].active and objects["S102"].length_m is None
    assert objects["S103"].kind is ObjectKind.DEBRIS and not objects["S103"].intact
    assert objects["S104"].mass_kg is None and objects["S104"].inc_deg is None
    assert ObjectKind.from_gcat("C  F") is ObjectKind.COMPONENT


def test_catalogue_ranks_only_intact_objects_with_mass(tmp_path: Path) -> None:
    cat = Catalogue.load(write_fixture(tmp_path))
    ids = [r.obj.jcat for r in cat.ranked]
    assert set(ids) == {"S100", "S101", "S102"}
    assert ids[0] == "S100"  # the 9 t stage at 845 km dominates
    assert cat.unranked_intact() == 1


def test_flagged_mass_has_wider_range() -> None:
    plain, flagged = obj(), obj()
    flagged = CatalogueObject(**{**flagged.__dict__, "mass_uncertain": True})
    p, f = mass_estimate(plain), mass_estimate(flagged)
    assert p is not None and f is not None and (f.high - f.low) > (p.high - p.low)
    assert mass_estimate(obj(mass=None)) is None


def test_area_from_dimensions_and_from_mass() -> None:
    a = area_estimate(obj())
    assert a is not None and a.low <= a.value <= a.high
    assert a.value == pytest.approx((math.pi * 2 * 4 + 2 * math.pi) / 4)
    sphere = area_estimate(obj(length=None, diameter=None))
    assert sphere is not None and sphere.low < sphere.value < sphere.high
    assert area_estimate(obj(mass=None, length=None, diameter=None)) is None


@settings(max_examples=60, deadline=None)
@given(h=st.floats(200, 1900), dh=st.floats(5, 100), b=st.floats(0.001, 0.2))
def test_lifetime_increases_with_altitude(atm: Atmosphere, h: float, dh: float, b: float) -> None:
    for scenario in ("low", "moderate", "high"):
        assert atm.lifetime_years(h + dh, b, scenario) > atm.lifetime_years(h, b, scenario)


@settings(max_examples=60, deadline=None)
@given(h=st.floats(200, 1900), b=st.floats(0.001, 0.1), factor=st.floats(1.1, 10))
def test_lifetime_falls_as_area_to_mass_rises(atm: Atmosphere, h: float, b: float, factor: float) -> None:
    assert atm.lifetime_years(h, b * factor, "moderate") < atm.lifetime_years(h, b, "moderate")


def test_lifetime_edges_and_solar_activity(atm: Atmosphere) -> None:
    assert atm.lifetime_years(100, 0.02, "moderate") == 0.0
    assert math.isinf(atm.lifetime_years(2500, 0.02, "moderate"))
    assert atm.lifetime_years(500, 0.02, "low") > atm.lifetime_years(500, 0.02, "high")
    assert atm.rho(50, "low") == atm.density["low"][0]
    assert atm.rho(5000, "low") == atm.density["low"][-1]


@settings(max_examples=60, deadline=None)
@given(
    perigee=st.floats(250, 1500),
    extra=st.floats(0, 400),
    mass=st.floats(1, 10000),
    length=st.floats(0.1, 15),
    diameter=st.floats(0.1, 5),
)
def test_terms_are_ordered_ranges(
    atm: Atmosphere,
    snapshot: Catalogue,
    perigee: float,
    extra: float,
    mass: float,
    length: float,
    diameter: float,
) -> None:
    o = obj(perigee=perigee, apogee=min(perigee + extra, 1999), mass=mass, length=length, diameter=diameter)
    life = lifetime_estimate(o, atm)
    assert life is not None and life.low <= life.value <= life.high
    r = risk_terms(o, atm, snapshot.environment)
    assert r is not None
    assert r.risk.low <= r.risk.value <= r.risk.high
    assert 0 <= r.terms.collision_probability.low <= r.terms.collision_probability.high <= 1
    assert 0 <= r.terms.persistence.high <= 1


def test_pc_rises_with_density_and_horizon(snapshot: Catalogue) -> None:
    sparse = Environment([obj(jcat="S1")])
    dense = Environment([obj(jcat=f"S{i}") for i in range(50)])
    o = obj()
    lo, hi = collision_probability(o, sparse, 25), collision_probability(o, dense, 25)
    assert lo is not None and hi is not None and hi.value > lo.value
    longer = collision_probability(o, dense, 50)
    assert longer is not None and longer.value > hi.value
    assert collision_probability(obj(mass=None, length=None, diameter=None), dense, 25) is None


def test_missing_mass_gives_no_terms(atm: Atmosphere, snapshot: Catalogue) -> None:
    assert risk_terms(obj(mass=None), atm, snapshot.environment) is None
    assert lifetime_estimate(obj(mass=None), atm) is None


def test_targeted_removal_beats_every_random_draw_on_the_point_value(snapshot: Catalogue) -> None:
    pool = [r for r in snapshot.ranked if not r.obj.active]
    c = compare_removal(pool, k=10, trials=500, seed=1)
    assert all(v <= c.targeted.value + 1e-9 for v in c.random_values)
    assert c.targeted == removal_delta(pool[:10])
    assert 0 <= c.share_beaten <= 1 and c.quantile(0.5) <= c.quantile(0.95)
    with pytest.raises(ValueError):
        compare_removal(pool, k=0, trials=1)


def test_concentration_is_monotone(snapshot: Catalogue) -> None:
    shares = concentration(snapshot.ranked, [10, 100, 1000])
    assert 0 < shares[10] < shares[100] < shares[1000] <= 1


def test_backtest_on_committed_snapshot() -> None:
    b = backtest_lifetimes(DATA / "decayed-sample.tsv")
    assert b.n > 300 and b.coverage > 0.9
    assert abs(b.median_log10_ratio) < 0.2
    with pytest.raises(ValueError):
        backtest_lifetimes(DATA / "decayed-sample.tsv", kinds=frozenset())


def test_snapshot_hashes_match_committed_extracts() -> None:
    import hashlib

    snap = json.loads((DATA / "SNAPSHOT.json").read_text())
    assert snap["license"] == "CC-BY-4.0"
    for name, digest in snap["extract_sha256"].items():
        assert hashlib.sha256((DATA / name).read_bytes()).hexdigest() == digest, name


def test_working_paper_numbers_match_the_code(snapshot: Catalogue) -> None:
    """results.json is what WP-04 quotes; it must match a fresh computation."""
    results = json.loads((ROOT / "papers" / "wp-04-catalogue" / "results.json").read_text())
    assert results["counts"]["intact_ranked"] == len(snapshot.ranked)
    derelict = [r for r in snapshot.ranked if not r.obj.active]
    assert results["counts"]["derelict_intact_ranked"] == len(derelict)
    c = compare_removal(derelict, k=10, trials=10_000)
    published = results["comparisons"][0]
    assert published["targeted"] == round(c.targeted.value, 2)
    assert published["random_median"] == round(c.quantile(0.5), 2)
    assert published["share_below_targeted_low"] == round(c.share_beaten, 4)
    top = results["top_derelict"][0]
    assert top["satcat"] == derelict[0].obj.satcat
    b = backtest_lifetimes(DATA / "decayed-sample.tsv")
    assert results["backtest"]["coverage"] == round(b.coverage, 4)


def test_cli_catalogue_commands(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["catalogue", "rank", "--top", "3"]) == 0
    out = capsys.readouterr().out
    assert "not an issued SDC" in out and "Zenit-2" in out
    assert main(["catalogue", "rank", "--top", "2", "--json", "--pool", "rocket_body"]) == 0
    rows = json.loads(capsys.readouterr().out)
    assert len(rows) == 2 and all(r["kind"] == "rocket_body" for r in rows)
    assert main(["catalogue", "rank", "--top", "1", "--pool", "all"]) == 0
    capsys.readouterr()
    assert main(["catalogue", "compare", "--k", "5", "--trials", "200"]) == 0
    assert "targeted dR" in capsys.readouterr().out
    assert main(["catalogue", "backtest"]) == 0
    assert "reentered rocket bodies" in capsys.readouterr().out
