from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from conftest import EXAMPLES, ROOT

from sder import Status, assess, load_methodology
from sder.cli import load_mission, main
from sder.methodology import DEFAULT_METHODOLOGY


def _bundled() -> dict[str, object]:
    path = ROOT / "src" / "sder" / "methodology" / DEFAULT_METHODOLOGY
    data: dict[str, object] = yaml.safe_load(path.read_text())
    return data


def _write(tmp_path: Path, data: dict[str, object]) -> Path:
    p = tmp_path / "m.yaml"
    p.write_text(yaml.safe_dump(data))
    return p


def test_bundled_methodology_is_marked_illustrative() -> None:
    m = load_methodology()
    assert m.status == "illustrative" and m.id == "sder-research-v0.1"


def test_hash_changes_when_method_changes(tmp_path: Path) -> None:
    data = _bundled()
    data["title"] = "changed"
    assert load_methodology(_write(tmp_path, data)).sha256 != load_methodology().sha256


@pytest.mark.parametrize(
    "mutate,match",
    [
        (lambda d: d["weights"].update(disposal=0.9), "sum to 1.0"),
        (lambda d: d["evidence_uncertainty"].pop("verified"), "every evidence class"),
        (lambda d: d["disposal"]["plan_risk"].pop("none"), "every disposal plan"),
        (lambda d: d["orbital_persistence"]["lifetime_table"].reverse(), "increasing"),
    ],
)
def test_invalid_methodologies_rejected(tmp_path: Path, mutate, match: str) -> None:  # type: ignore[no-untyped-def]
    data = _bundled()
    mutate(data)
    with pytest.raises(ValueError, match=match):
        load_methodology(_write(tmp_path, data))


def test_examples_behave_as_documented() -> None:
    good = assess(load_mission(EXAMPLES / "leo-smallsat-responsible.yaml"))
    bad = assess(load_mission(EXAMPLES / "leo-derelict-upper-stage.yaml"))
    sparse = assess(load_mission(EXAMPLES / "sparse-operator-claims.yaml"))
    assert good.score is not None and bad.score is not None
    assert good.band == "low" and bad.band == "high" and bad.band_is_certain
    assert sparse.status is Status.WITHHELD


def test_expected_outputs_are_current() -> None:
    for yml in sorted(EXAMPLES.glob("*.yaml")):
        expected = json.loads((EXAMPLES / "expected" / f"{yml.stem}.json").read_text())
        assert assess(load_mission(yml)).model_dump(mode="json") == expected, yml.name


def test_cli_text_json_methodology_schema(capsys: pytest.CaptureFixture[str]) -> None:
    files = [str(p) for p in sorted(EXAMPLES.glob("*.yaml"))]
    assert main(["score", *files]) == 0
    out = capsys.readouterr().out
    assert "WITHHELD" in out and "not an official SDER rating" in out and "band uncertain" in out
    assert main(["score", "--json", files[0]]) == 0
    assert json.loads(capsys.readouterr().out)["mission_id"]
    assert main(["score", "--json", *files]) == 0
    assert len(json.loads(capsys.readouterr().out)) == len(files)
    assert main(["methodology"]) == 0
    assert json.loads(capsys.readouterr().out)["id"] == "sder-research-v0.1"
    assert main(["schema"]) == 0
    assert set(json.loads(capsys.readouterr().out)) == {"mission", "assessment"}


def test_committed_schemas_match_models() -> None:
    from sder.models import Assessment, Mission

    for name, model in [("sder-mission", Mission), ("sder-assessment", Assessment)]:
        committed = json.loads((ROOT / "schemas" / f"{name}.schema.json").read_text())
        assert committed == model.model_json_schema(), f"regenerate schemas/{name}.schema.json"


def test_examples_validate_against_schema() -> None:
    import jsonschema

    schema = json.loads((ROOT / "schemas" / "sder-mission.schema.json").read_text())
    for yml in EXAMPLES.glob("*.yaml"):
        jsonschema.validate(yaml.safe_load(yml.read_text()), schema)
