"""Command line: ``sdc demo``, ``sdc verify``, ``sdc show``, ``sdc delta-r``."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

import yaml

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
    args = parser.parse_args(argv)

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
