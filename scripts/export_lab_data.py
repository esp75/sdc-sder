"""Export data and parity fixtures for the interactive lab on maximekadri.org.

    uv run python scripts/export_lab_data.py ../maximekadri.org

Writes into the site repository:
* ``public/lab/sdc/objects.json``: every ranked intact LEO object, columnar;
* ``public/lab/sdc/model.json``: atmosphere table, shell densities, constants
  and the SDER method in use, so the browser can recompute R and SDER;
* ``src/lab/sdc/parity.json``: golden outputs from this Python code, which the
  site's ``node --test`` suite compares with its TypeScript port.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from sdc.catalogue import (
    BULK_DENSITY_KG_M3,
    DEFAULT_HORIZON_YEARS,
    DRAG_COEFFICIENT,
    MASS_UNCERTAINTY,
    MASS_UNCERTAINTY_FLAGGED,
    REENTRY_ALTITUDE_KM,
    RELATIVE_SPEED_KM_S,
    Catalogue,
    CatalogueObject,
    ObjectKind,
    risk_terms,
)
from sder.engine import assess
from sder.methodology import load_methodology
from sder.models import DisposalPlan, EvidenceClass, Maneuverability, Mission, Passivation

ROOT = Path(__file__).resolve().parent.parent


def sig(x: float, n: int = 4) -> float:
    return float(f"{x:.{n}g}")


def objects_payload(cat: Catalogue, snapshot: dict[str, object]) -> dict[str, object]:
    cols = [
        "satcat",
        "name",
        "kind",
        "active",
        "owner",
        "perigee",
        "apogee",
        "mass",
        "L",
        "Pc",
        "R",
        "Rlo",
        "Rhi",
    ]
    rows = []
    for r in cat.ranked:
        o, t = r.obj, r.terms
        rows.append(
            [
                o.satcat, o.name, "r" if o.kind is ObjectKind.ROCKET_BODY else "p", int(o.active), o.owner,
                o.perigee_km, o.apogee_km, t.mass_kg.value, sig(t.persistence.value, 3),
                sig(t.collision_probability.value, 3), sig(r.risk.value), sig(r.risk.low), sig(r.risk.high),
            ]
        )  # fmt: skip
    return {
        "source": "GCAT, Jonathan C. McDowell (CC BY 4.0), https://planet4589.org/space/gcat/",
        "snapshot": snapshot["currentcat_updated"],
        "horizon_years": cat.horizon_years,
        "columns": cols,
        "rows": rows,
    }


def model_payload(cat: Catalogue) -> dict[str, object]:
    atm, env = cat.atmosphere, cat.environment
    return {
        "constants": {
            "drag_coefficient": DRAG_COEFFICIENT,
            "reentry_altitude_km": REENTRY_ALTITUDE_KM,
            "relative_speed_km_s": RELATIVE_SPEED_KM_S.model_dump(),
            "mass_uncertainty": MASS_UNCERTAINTY,
            "mass_uncertainty_flagged": MASS_UNCERTAINTY_FLAGGED,
            "bulk_density_kg_m3": BULK_DENSITY_KG_M3.model_dump(),
            "horizon_years": DEFAULT_HORIZON_YEARS,
        },
        "atmosphere": {"altitude_km": atm.altitude_km, "density_kg_m3": atm.density},
        "environment": {"shell_km": env.shell_km, "density_per_km3": env.density},
        "method": load_methodology().model_dump(mode="json"),
    }


def random_object(rng: random.Random, i: int) -> CatalogueObject:
    perigee = rng.uniform(250, 1500)
    has_dims = rng.random() < 0.7
    apogee = min(1999.0, perigee + rng.choice([0, 0, rng.uniform(0, 400)]))
    return CatalogueObject(
        jcat=f"T{i}", satcat=str(i), name=f"test {i}", kind=ObjectKind.ROCKET_BODY, active=False,
        owner="", state="", perigee_km=round(perigee, 1), apogee_km=round(apogee, 1),
        inc_deg=None, mass_kg=round(rng.uniform(1, 9000), 1), mass_uncertain=rng.random() < 0.3,
        length_m=round(rng.uniform(0.1, 12), 2) if has_dims else None,
        diameter_m=round(rng.uniform(0.1, 4), 2) if has_dims else None,
        span_m=round(rng.uniform(0.1, 20), 2) if has_dims and rng.random() < 0.5 else None,
    )  # fmt: skip


def random_mission(rng: random.Random, i: int) -> Mission:
    classes = list(EvidenceClass)

    def field(value: object) -> dict[str, object]:
        if rng.random() < 0.15:
            return {"evidence": rng.choice(classes)}
        return {"value": value, "evidence": rng.choice(classes)}

    inputs = {
        "mean_altitude_km": field(round(rng.uniform(200, 2500), 1)),
        "mass_kg": field(round(10 ** rng.uniform(0, 4.2), 1)),
        "disposal_plan": field(rng.choice(list(DisposalPlan)).value),
        "disposal_reliability": field(round(rng.random(), 3)),
        "passivation": field(rng.choice(list(Passivation)).value),
        "maneuverability": field(rng.choice(list(Maneuverability)).value),
        "min_miss_distance_km": field(round(rng.uniform(0, 20), 3)),
        "relative_speed_km_s": field(round(rng.uniform(0, 15), 2)),
    }
    return Mission.model_validate({"mission": {"id": f"random-{i}"}, "inputs": inputs})


def parity_payload(cat: Catalogue) -> dict[str, object]:
    rng = random.Random(2026)
    missions = [Mission.model_validate_json(json.dumps(_load_yaml(p))) for p in _mission_files()]
    missions += [random_mission(rng, i) for i in range(200)]
    sder = []
    for m in missions:
        a = assess(m)
        sder.append(
            {
                "inputs": m.inputs.model_dump(mode="json"),
                "score": a.score,
                "low": a.low,
                "high": a.high,
                "band": a.band,
                "band_is_certain": a.band_is_certain,
                "status": a.status.value,
                "missing_weight": a.missing_weight,
                "components": {c.name: [c.risk, c.low, c.high] for c in a.components},
            }
        )
    objs = [random_object(rng, i) for i in range(200)] + [
        r.obj for r in cat.ranked[:: max(1, len(cat.ranked) // 50)]
    ]
    risk = []
    for o in objs:
        r = risk_terms(o, cat.atmosphere, cat.environment)
        if r is None:
            continue
        risk.append(
            {
                "object": {
                    "perigee_km": o.perigee_km, "apogee_km": o.apogee_km, "mass_kg": o.mass_kg,
                    "mass_uncertain": o.mass_uncertain, "length_m": o.length_m, "diameter_m": o.diameter_m,
                    "span_m": o.span_m,
                },
                "lifetime": r.lifetime_years.model_dump(),
                "L": r.terms.persistence.model_dump(),
                "Pc": r.terms.collision_probability.model_dump(),
                "R": r.risk.model_dump(),
            }
        )  # fmt: skip
    return {"sder": sder, "risk": risk}


def _mission_files() -> list[Path]:
    return sorted((ROOT / "examples").glob("*.yaml")) + sorted((ROOT / "examples" / "cases").glob("*.yaml"))


def _load_yaml(path: Path) -> object:
    import yaml

    return yaml.safe_load(path.read_text())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("site", type=Path, help="path to the maximekadri.org repository")
    args = parser.parse_args()
    cat = Catalogue.load(ROOT / "data" / "gcat" / "leo-objects.tsv")
    snapshot = json.loads((ROOT / "data" / "gcat" / "SNAPSHOT.json").read_text())
    public = args.site / "public" / "lab" / "sdc"
    fixtures = args.site / "src" / "lab" / "sdc"
    public.mkdir(parents=True, exist_ok=True)
    fixtures.mkdir(parents=True, exist_ok=True)
    for path, data in [
        (public / "objects.json", objects_payload(cat, snapshot)),
        (public / "model.json", model_payload(cat)),
        (fixtures / "parity.json", parity_payload(cat)),
    ]:
        path.write_text(json.dumps(data, separators=(",", ":"), ensure_ascii=False))
        print(f"wrote {path} ({path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
