"""Command line: ``sder score``, ``sder methodology``, ``sder schema``."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

import yaml

from .engine import assess
from .methodology import load_methodology
from .models import Assessment, Mission


def load_mission(path: Path) -> Mission:
    return Mission.model_validate(yaml.safe_load(path.read_text()))


def render(a: Assessment) -> str:
    lines = [
        a.label,
        f"mission      {a.mission_id}",
        f"method       {a.methodology_id} ({a.methodology_sha256[:12]})",
    ]
    if a.score is None:
        lines.append(f"status       {a.status.value.upper()}: {a.missing_weight:.0%} of weight missing")
    else:
        certain = "" if a.band_is_certain else " (band uncertain)"
        lines.append(
            f"score        {a.score:.1f}  [{a.low:.1f}-{a.high:.1f}]  {a.band}{certain}  {a.status.value}"
        )
    lines.append("")
    lines.append(f"{'component':<20}{'weight':>7}{'risk':>8}{'range':>14}  {'evidence':<23}rationale")
    for c in a.components:
        ev = c.evidence.value if c.evidence else "-"
        rng = f"{c.low:.0f}-{c.high:.0f}"
        lines.append(f"{c.name:<20}{c.weight:>7.3f}{c.risk:>8.1f}{rng:>14}  {ev:<23}{c.rationale}")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sder", description="Illustrative SDER research scoring.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    score = sub.add_parser("score", help="score one or more mission YAML files")
    score.add_argument("files", nargs="+", type=Path)
    score.add_argument("--methodology", type=Path, default=None)
    score.add_argument("--json", action="store_true", help="emit JSON")
    meth = sub.add_parser("methodology", help="print the methodology in use")
    meth.add_argument("--methodology", type=Path, default=None)
    sub.add_parser("schema", help="print JSON Schemas for inputs and assessments")
    args = parser.parse_args(argv)

    if args.cmd == "score":
        m = load_methodology(args.methodology)
        results = [assess(load_mission(f), m) for f in args.files]
        if args.json:
            payload = [r.model_dump(mode="json") for r in results]
            print(json.dumps(payload[0] if len(payload) == 1 else payload, indent=2))
        else:
            print("\n\n".join(render(r) for r in results))
    elif args.cmd == "methodology":
        print(json.dumps(load_methodology(args.methodology).model_dump(mode="json"), indent=2))
    else:
        schemas = {"mission": Mission.model_json_schema(), "assessment": Assessment.model_json_schema()}
        print(json.dumps(schemas, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
