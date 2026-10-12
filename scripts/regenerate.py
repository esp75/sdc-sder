"""Regenerate committed JSON Schemas and expected example outputs.

Run after any intentional change to the models or the methodology:
    uv run python scripts/regenerate.py
The tests fail if these files drift from the code.
"""

from __future__ import annotations

import json
from pathlib import Path

from sder import assess
from sder.cli import load_mission
from sder.models import Assessment, Mission

ROOT = Path(__file__).resolve().parent.parent


def dump(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print("wrote", path.relative_to(ROOT))


def main() -> None:
    dump(ROOT / "schemas" / "sder-mission.schema.json", Mission.model_json_schema())
    dump(ROOT / "schemas" / "sder-assessment.schema.json", Assessment.model_json_schema())
    for folder in (ROOT / "examples", ROOT / "examples" / "cases"):
        for yml in sorted(folder.glob("*.yaml")):
            dump(folder / "expected" / f"{yml.stem}.json", assess(load_mission(yml)).model_dump(mode="json"))


if __name__ == "__main__":
    main()
