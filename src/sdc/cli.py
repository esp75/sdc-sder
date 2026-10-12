"""Command line: ``sdc demo``, ``sdc verify``, ``sdc show``, ``sdc delta-r``, ``sdc catalogue``."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

import yaml

from .catalogue import Catalogue, RankedObject, backtest_lifetimes, compare_removal
from .registry import Registry, RegistryError, verify_log
from .risk import Action, delta_r, issuable_units

DEMO_EVENTS: list[tuple[str, str, dict[str, object]]] = [
    (
        "submit",
        "orbit-cleanup-co",
        {
            "claim_id": "C-0001",
            "object_id": "2003-031B",
            "outcome_type": "active_removal",
            "event_date": "2026-05-14",
            "claimant": "orbit-cleanup-co",
            "unit_definition": "one intact derelict upper stage removed from LEO",
            "baseline": "object would have remained in orbit for >100 years with no disposal plan",
            "evidence": ["ssa:radar-track-2026-05-14", "mission-report:OC-7"],
        },
    ),
    (
        "assign_verifier",
        "registry-admin",
        {"claim_id": "C-0001", "verifier": "independent-ssa-lab", "conflicts_disclosed": []},
    ),
    ("verify", "independent-ssa-lab", {"claim_id": "C-0001", "finding": "reentry confirmed by two sensors"}),
    ("issue", "registry-admin", {"claim_id": "C-0001"}),
    ("retire", "satellite-operator-x", {"claim_id": "C-0001", "reason": "voluntary disclosure FY2026"}),
]


def _demo(path: Path) -> int:
    if path.exists():
        print(f"{path} already exists; refusing to overwrite", file=sys.stderr)
        return 1
    reg = Registry(path=path)
    for i, (action, actor, payload) in enumerate(DEMO_EVENTS):
        reg.record(action, actor, dict(payload), timestamp=f"2026-06-0{i + 1}T12:00:00+00:00")
    try:  # the guard against double counting, demonstrated
        reg.record(
            "submit", "someone-else", {**DEMO_EVENTS[0][2], "claim_id": "C-0002", "claimant": "someone-else"}
        )
    except RegistryError as exc:
        print(f"rejected as expected: {exc}")
    print(f"wrote {len(reg.entries)} entries to {path}; head {reg.head[:16]}")
    return 0


def _delta_r(path: Path, reference_unit: float | None, as_json: bool) -> int:
    result = delta_r(Action.model_validate(yaml.safe_load(path.read_text(encoding="utf-8"))))
    units = None if reference_unit is None else issuable_units(result, reference_unit)
    if as_json:
        print(json.dumps({**result.model_dump(mode="json"), "issuable_units": units}, indent=2))
        return 0
    print(result.label)
    print(f"action       {result.action_id} (horizon {result.horizon_years:g} years)")
    rng = f"[{result.low:.4g} - {result.high:.4g}]"
    print(f"dR           {result.value:.4g}  {rng}  (risk proxy, kg-equivalent)")
    if units is not None:
        print(f"units        {units} at dR0 = {reference_unit:g} per unit (from the conservative bound)")
    print(f"\n{'object':<16}{'R before':>12}{'R after':>12}{'dR':>12}{'range':>22}")
    for o in result.objects:
        rng = f"{o.delta_low:.4g} - {o.delta_high:.4g}"
        print(
            f"{o.object_id:<16}{o.risk_before.value:>12.4g}{o.risk_after.value:>12.4g}{o.delta:>12.4g}{rng:>22}"
        )
    return 0


DEFAULT_DATA = Path("data/gcat")
POOLS = ("derelict", "rocket_body", "all")


def pool(cat: Catalogue, name: str) -> list[RankedObject]:
    """Removal candidates: derelict intact objects, derelict rocket bodies, or every ranked object."""
    if name == "all":
        return cat.ranked
    derelict = [r for r in cat.ranked if not r.obj.active]
    if name == "rocket_body":
        return [r for r in derelict if r.obj.kind.value == "rocket_body"]
    return derelict


def _catalogue(args: argparse.Namespace) -> int:
    if args.catalogue_cmd == "backtest":
        b = backtest_lifetimes(args.data / "decayed-sample.tsv")
        print(
            f"{b.n} reentered rocket bodies; predicted range holds the actual lifetime for {b.coverage:.0%}"
        )
        print(f"median predicted/actual {10**b.median_log10_ratio:.2f}; within x2 {b.within_factor_2:.0%}")
        return 0
    cat = Catalogue.load(args.data / "leo-objects.tsv", horizon_years=args.horizon)
    label = "Illustrative research estimate - not an issued SDC"
    if args.catalogue_cmd == "rank":
        rows = pool(cat, args.pool)[: args.top]
        if args.json:
            print(json.dumps([_ranked_json(r) for r in rows], indent=2))
            return 0
        print(label)
        print(f"{len(cat.ranked)} intact LEO objects ranked by R = M x L x Pc over {args.horizon:g} years")
        print(
            f"{'#':>4}  {'object':<36}{'kind':<12}{'alt km':>11}{'M kg':>8}{'L':>6}{'Pc':>10}{'R':>9}  range"
        )
        for i, r in enumerate(rows, 1):
            o, t = r.obj, r.terms
            alt = f"{o.perigee_km:.0f}-{o.apogee_km:.0f}"
            print(
                f"{i:>4}  {o.label[:35]:<36}{o.kind.value:<12}{alt:>11}{t.mass_kg.value:>8.0f}"
                f"{t.persistence.value:>6.2f}{t.collision_probability.value:>10.2e}{r.risk.value:>9.3g}"
                f"  {r.risk.low:.3g}-{r.risk.high:.3g}"
            )
        return 0
    c = compare_removal(pool(cat, args.pool), args.k, args.trials, seed=args.seed, name=args.pool)
    dr = c.targeted
    print(label)
    print(f"pool         {c.pool} ({c.pool_size} objects), k = {c.k}, {c.trials} random draws")
    print(f"targeted dR  {dr.value:.4g}  [{dr.low:.4g} - {dr.high:.4g}]")
    print(f"random dR    median {c.quantile(0.5):.4g}, 95th percentile {c.quantile(0.95):.4g}")
    print(f"ratio        {dr.value / c.quantile(0.5):.3g}x the median random set")
    print(f"beaten       {c.share_beaten:.1%} of random draws fall below the targeted conservative bound")
    return 0


def _ranked_json(r: RankedObject) -> dict[str, object]:
    o = r.obj
    return {
        "satcat": o.satcat,
        "jcat": o.jcat,
        "name": o.name,
        "kind": o.kind.value,
        "active": o.active,
        "owner": o.owner,
        "perigee_km": o.perigee_km,
        "apogee_km": o.apogee_km,
        "lifetime_years": r.lifetime_years.model_dump(),
        **r.terms.model_dump(mode="json"),
        "risk": r.risk.model_dump(),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sdc", description="Candidate SDC claim registry (research prototype)."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name, text in [("demo", "write a demo log"), ("verify", "check a log"), ("show", "list claims")]:
        sub.add_parser(name, help=text).add_argument("log", type=Path)
    dr = sub.add_parser("delta-r", help="expected risk reduction of an action (R = M x L x Pc)")
    dr.add_argument("action", type=Path)
    dr.add_argument("--reference-unit", type=float, default=None, help="dR0 per credit unit")
    dr.add_argument("--json", action="store_true")
    cat = sub.add_parser("catalogue", help="R = M x L x Pc for real LEO objects (GCAT snapshot)")
    cat_sub = cat.add_subparsers(dest="catalogue_cmd", required=True)
    for name, text in [
        ("rank", "rank objects by R"),
        ("compare", "targeted top-k removal against random k-subsets (paper Figure 3)"),
        ("backtest", "check the lifetime model against objects that have reentered"),
    ]:
        p = cat_sub.add_parser(name, help=text)
        p.add_argument("--data", type=Path, default=DEFAULT_DATA, help="directory with the GCAT extracts")
        p.add_argument("--horizon", type=float, default=25.0, help="horizon H in years")
        p.add_argument("--pool", choices=POOLS, default="derelict")
    cat_sub.choices["rank"].add_argument("--top", type=int, default=20)
    cat_sub.choices["rank"].add_argument("--json", action="store_true")
    cat_sub.choices["compare"].add_argument("--k", type=int, default=10)
    cat_sub.choices["compare"].add_argument("--trials", type=int, default=10000)
    cat_sub.choices["compare"].add_argument("--seed", type=int, default=2026)
    args = parser.parse_args(argv)

    if args.cmd == "catalogue":
        return _catalogue(args)
    if args.cmd == "delta-r":
        return _delta_r(args.action, args.reference_unit, args.json)

    if args.cmd == "demo":
        return _demo(args.log)
    if args.cmd == "verify":
        res = verify_log(args.log)
        if res.ok:
            print(f"OK: {res.entries} entries, chain head {res.head}")
            return 0
        print(f"INVALID: {res.error}")
        return 1
    reg = Registry.open(args.log)
    print(f"{'claim':<10}{'object':<14}{'outcome':<20}{'state':<14}{'verifier'}")
    for c in reg.claims.values():
        s = c.submission
        row = f"{s.claim_id:<10}{s.object_id:<14}{s.outcome_type.value:<20}{c.state.value:<14}"
        print(row + (c.verifier or "-"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
