"""R_i = M_i x L_i x Pc_i for real objects, from the open GCAT catalogue.

This module turns the paper's object-level proxy (Kadri & Shishkina 2026, §6)
into numbers for every intact object in low Earth orbit. Each term is a range:

* **M**, mass: GCAT dry mass (or launch mass), +/-10 %, or +/-20 % when GCAT
  flags the value as an estimate (GCAT documents those as "hopefully good to
  about 20 percent").
* **L**, persistence: the share of the horizon H the object stays in orbit,
  min(1, lifetime / H). Lifetime comes from integrating circular-orbit drag
  decay, da/dt = -rho B sqrt(mu a) with B = Cd A / m, through an NRLMSIS 2.1
  density profile. The point value uses moderate solar activity at the mean
  altitude. The range runs from high solar activity, the largest area and the
  perigee altitude (shortest life) to low solar activity, the smallest area and
  the mean altitude (longest life). ``backtest_lifetimes`` checks this against
  objects that have already reentered.
* **Pc**, collision probability with a tracked object over H, from the kinetic
  theory of gases (Kessler 1978): Pc = 1 - exp(-n v sigma H), where n is the
  spatial density of catalogued objects along the object's altitude range,
  v the mean relative speed and sigma the object's mean cross-section.

Every assumption is a named constant below, so a reviewer can change it and
rerun. Outputs are illustrative research estimates, not issued SDCs.
"""

from __future__ import annotations

import bisect
import csv
import math
import random
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from functools import cached_property
from importlib import resources
from pathlib import Path

import yaml

from .risk import Estimate, RiskTerms

MU_M3_S2 = 3.986004418e14
EARTH_RADIUS_KM = 6378.137
SECONDS_PER_YEAR = 365.25 * 86400
DRAG_COEFFICIENT = 2.2
REENTRY_ALTITUDE_KM = 120.0
"""Below this altitude an object reenters within days; the decay integral stops here."""

RELATIVE_SPEED_KM_S = Estimate(value=10.0, low=7.0, high=13.0)
"""Mean relative speed of LEO encounters. An assumption, stated as a range."""

MASS_UNCERTAINTY = 0.10
MASS_UNCERTAINTY_FLAGGED = 0.20
BULK_DENSITY_KG_M3 = Estimate(value=300.0, low=100.0, high=1000.0)
"""Used only to size objects without dimensions in GCAT, as an equivalent sphere."""

SHELL_KM = 10.0
DEFAULT_HORIZON_YEARS = 25.0


class ObjectKind(StrEnum):
    PAYLOAD = "payload"
    ROCKET_BODY = "rocket_body"
    COMPONENT = "component"
    DEBRIS = "debris"

    @classmethod
    def from_gcat(cls, code: str) -> ObjectKind:
        return {"P": cls.PAYLOAD, "R": cls.ROCKET_BODY, "C": cls.COMPONENT}.get(code[:1], cls.DEBRIS)


@dataclass(frozen=True)
class CatalogueObject:
    """One row of ``data/gcat/leo-objects.tsv``."""

    jcat: str
    satcat: str
    name: str
    kind: ObjectKind
    active: bool
    owner: str
    state: str
    perigee_km: float
    apogee_km: float
    inc_deg: float | None
    mass_kg: float | None
    mass_uncertain: bool
    length_m: float | None
    diameter_m: float | None
    span_m: float | None

    @property
    def intact(self) -> bool:
        return self.kind in (ObjectKind.PAYLOAD, ObjectKind.ROCKET_BODY)

    @property
    def mean_altitude_km(self) -> float:
        return (self.perigee_km + self.apogee_km) / 2

    @property
    def label(self) -> str:
        return f"{self.satcat or self.jcat} {self.name}"


def _num(text: str) -> float | None:
    try:
        value = float(text.strip().rstrip("?"))
    except ValueError:
        return None
    return value if value > 0 else None


def load_objects(path: Path) -> list[CatalogueObject]:
    """Read a GCAT LEO extract written by ``scripts/fetch_gcat.py``."""
    objects = []
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            inc = row["inc_deg"].strip()
            objects.append(
                CatalogueObject(
                    jcat=row["jcat"],
                    satcat=row["satcat"].lstrip("0"),
                    name=row["name"],
                    kind=ObjectKind.from_gcat(row["type"]),
                    active=row["active"] == "yes",
                    owner=row["owner"],
                    state=row["state"],
                    perigee_km=float(row["perigee_km"]),
                    apogee_km=float(row["apogee_km"]),
                    inc_deg=float(inc) if inc not in ("", "-") else None,
                    mass_kg=_num(row["mass_kg"]),
                    mass_uncertain=row["mass_flag"] == "?",
                    length_m=_num(row["length_m"]),
                    diameter_m=_num(row["diameter_m"]),
                    span_m=_num(row["span_m"]),
                )
            )
    return objects


def mass_estimate(obj: CatalogueObject) -> Estimate | None:
    if obj.mass_kg is None:
        return None
    u = MASS_UNCERTAINTY_FLAGGED if obj.mass_uncertain else MASS_UNCERTAINTY
    return Estimate(value=obj.mass_kg, low=obj.mass_kg * (1 - u), high=obj.mass_kg * (1 + u))


def area_estimate(obj: CatalogueObject) -> Estimate | None:
    """Mean cross-section in m^2 for a randomly tumbling object.

    With dimensions: the object is treated as a cylinder of length L and
    diameter D. Its mean projected area is S/4 (Cauchy's formula for convex
    bodies), bounded by the end-on area and the broadside area including span.
    Without dimensions: an equivalent sphere at an assumed bulk density.
    """
    d = obj.diameter_m
    length = obj.length_m or d
    if d is not None and length is not None:
        end_on = math.pi * d * d / 4
        broadside = max(length, obj.span_m or 0.0) * d
        mean = (math.pi * d * length + 2 * end_on) / 4
        low, high = min(end_on, mean), max(broadside, mean)
        return Estimate(value=mean, low=low, high=high)
    if obj.mass_kg is None:
        return None

    mass = obj.mass_kg

    def sphere(rho: float) -> float:
        r: float = (3 * mass / (4 * math.pi * rho)) ** (1 / 3)
        return math.pi * r * r

    b = BULK_DENSITY_KG_M3
    return Estimate(value=sphere(b.value), low=sphere(b.high), high=sphere(b.low))


class Atmosphere:
    """Orbit-averaged density profiles and the drag-decay integral."""

    def __init__(self, altitude_km: Sequence[float], density: dict[str, Sequence[float]]) -> None:
        self.altitude_km = list(altitude_km)
        self.density = {k: list(v) for k, v in density.items()}
        self._integral = {k: self._cumulative(k) for k in self.density}

    @classmethod
    def bundled(cls) -> Atmosphere:
        raw = resources.files("sdc").joinpath("data", "atmosphere.yaml").read_text(encoding="utf-8")
        doc = yaml.safe_load(raw)
        return cls(doc["altitude_km"], doc["density_kg_m3"])

    def rho(self, h_km: float, scenario: str) -> float:
        """Density, log-linear between table points, clamped to the table's ends."""
        alts, rho = self.altitude_km, self.density[scenario]
        if h_km <= alts[0]:
            return rho[0]
        if h_km >= alts[-1]:
            return rho[-1]
        i = bisect.bisect_right(alts, h_km)
        t = (h_km - alts[i - 1]) / (alts[i] - alts[i - 1])
        return math.exp(math.log(rho[i - 1]) + t * (math.log(rho[i]) - math.log(rho[i - 1])))

    def _cumulative(self, scenario: str, step_km: float = 1.0) -> list[float]:
        """K(h) = integral from the reentry altitude to h of dh / (rho sqrt(mu r)), in s.kg/m^2."""
        top = self.altitude_km[-1]
        n = round((top - REENTRY_ALTITUDE_KM) / step_km)
        k, total = [0.0], 0.0
        for j in range(n):
            mid = REENTRY_ALTITUDE_KM + (j + 0.5) * step_km
            r_m = (EARTH_RADIUS_KM + mid) * 1e3
            total += step_km * 1e3 / (self.rho(mid, scenario) * math.sqrt(MU_M3_S2 * r_m))
            k.append(total)
        return k

    def lifetime_years(self, h_km: float, ballistic_m2_kg: float, scenario: str) -> float:
        """Natural decay time of a circular orbit at ``h_km`` with B = Cd A / m."""
        if h_km <= REENTRY_ALTITUDE_KM:
            return 0.0
        k = self._integral[scenario]
        x = min(h_km - REENTRY_ALTITUDE_KM, len(k) - 1.0)
        i = min(int(x), len(k) - 2)
        value = k[i] + (x - i) * (k[i + 1] - k[i])
        if h_km > self.altitude_km[-1]:
            value = math.inf
        return value / ballistic_m2_kg / SECONDS_PER_YEAR


def lifetime_estimate(obj: CatalogueObject, atm: Atmosphere) -> Estimate | None:
    """Range of natural-decay lifetimes in years (see the module docstring)."""
    m, a = mass_estimate(obj), area_estimate(obj)
    if m is None or a is None:
        return None
    b_mid = DRAG_COEFFICIENT * a.value / m.value
    b_short = DRAG_COEFFICIENT * a.high / m.low
    b_long = DRAG_COEFFICIENT * a.low / m.high
    short = atm.lifetime_years(obj.perigee_km, b_short, "high")
    long = atm.lifetime_years(obj.mean_altitude_km, b_long, "low")
    point = atm.lifetime_years(obj.mean_altitude_km, b_mid, "moderate")
    low, high = min(short, long), max(short, long)  # guards rows with apogee < perigee
    return Estimate(value=min(max(point, low), high), low=low, high=high)


class Environment:
    """Spatial density of catalogued objects by altitude shell (objects per km^3)."""

    def __init__(
        self, objects: Iterable[CatalogueObject], shell_km: float = SHELL_KM, top_km: float = 2000
    ) -> None:
        self.shell_km = shell_km
        self.n_shells = int(top_km // shell_km)
        counts = [0.0] * self.n_shells
        for o in objects:
            lo, hi = self._index(o.perigee_km), self._index(o.apogee_km)
            share = 1.0 / (hi - lo + 1)  # time spread evenly over the altitude range: an approximation
            for i in range(lo, hi + 1):
                counts[i] += share
        self.counts = counts
        self.density = [c / self._volume(i) for i, c in enumerate(counts)]

    def _index(self, h_km: float) -> int:
        return max(0, min(self.n_shells - 1, int(h_km // self.shell_km)))

    def _volume(self, i: int) -> float:
        r0 = EARTH_RADIUS_KM + i * self.shell_km
        r1 = r0 + self.shell_km
        return 4 / 3 * math.pi * (r1**3 - r0**3)

    def mean_density(self, perigee_km: float, apogee_km: float) -> float:
        lo, hi = self._index(perigee_km), self._index(apogee_km)
        return math.fsum(self.density[lo : hi + 1]) / (hi - lo + 1)


def collision_probability(obj: CatalogueObject, env: Environment, horizon_years: float) -> Estimate | None:
    """Pc over the horizon, assuming the object stays at its current altitude range."""
    a = area_estimate(obj)
    if a is None:
        return None
    n = env.mean_density(obj.perigee_km, obj.apogee_km)
    seconds = horizon_years * SECONDS_PER_YEAR
    v = RELATIVE_SPEED_KM_S

    def pc(speed: float, area_m2: float) -> float:
        return -math.expm1(-n * speed * area_m2 * 1e-6 * seconds)

    return Estimate(value=pc(v.value, a.value), low=pc(v.low, a.low), high=pc(v.high, a.high))


@dataclass(frozen=True)
class RankedObject:
    obj: CatalogueObject
    lifetime_years: Estimate
    terms: RiskTerms

    @property
    def risk(self) -> Estimate:
        return self.terms.risk


def _fraction(lifetime: Estimate, horizon_years: float) -> Estimate:
    def f(years: float) -> float:
        return min(1.0, years / horizon_years)

    return Estimate(value=f(lifetime.value), low=f(lifetime.low), high=f(lifetime.high))


def risk_terms(
    obj: CatalogueObject, atm: Atmosphere, env: Environment, horizon_years: float = DEFAULT_HORIZON_YEARS
) -> RankedObject | None:
    """R_i terms for one object, or None when GCAT lacks its mass."""
    m, life = mass_estimate(obj), lifetime_estimate(obj, atm)
    pc = collision_probability(obj, env, horizon_years)
    if m is None or life is None or pc is None:
        return None
    terms = RiskTerms(mass_kg=m, persistence=_fraction(life, horizon_years), collision_probability=pc)
    return RankedObject(obj=obj, lifetime_years=life, terms=terms)


@dataclass
class Catalogue:
    """All LEO objects from one snapshot, with R_i for the intact ones that have a mass."""

    objects: list[CatalogueObject]
    horizon_years: float = DEFAULT_HORIZON_YEARS

    @classmethod
    def load(cls, path: Path, horizon_years: float = DEFAULT_HORIZON_YEARS) -> Catalogue:
        return cls(load_objects(path), horizon_years)

    @cached_property
    def atmosphere(self) -> Atmosphere:
        return Atmosphere.bundled()

    @cached_property
    def environment(self) -> Environment:
        return Environment(self.objects)

    @cached_property
    def ranked(self) -> list[RankedObject]:
        """Intact objects with a mass, by R_i (point value), highest first."""
        out = []
        for o in self.objects:
            if not o.intact:
                continue
            r = risk_terms(o, self.atmosphere, self.environment, self.horizon_years)
            if r is not None:
                out.append(r)
        return sorted(out, key=lambda r: (-r.risk.value, r.obj.jcat))

    def unranked_intact(self) -> int:
        return sum(1 for o in self.objects if o.intact) - len(self.ranked)


def removal_delta(selection: Sequence[RankedObject]) -> Estimate:
    """dR of removing every object in ``selection``: R_after = 0, so dR = sum R_before."""
    return Estimate(
        value=math.fsum(r.risk.value for r in selection),
        low=math.fsum(r.risk.low for r in selection),
        high=math.fsum(r.risk.high for r in selection),
    )


@dataclass(frozen=True)
class RemovalComparison:
    """Paper Figure 3 on real data: targeted top-k removal against random k-subsets."""

    pool: str
    pool_size: int
    k: int
    trials: int
    targeted: Estimate
    random_values: list[float]

    def quantile(self, q: float) -> float:
        xs = sorted(self.random_values)
        return xs[min(len(xs) - 1, int(q * len(xs)))]

    @property
    def share_beaten(self) -> float:
        """Share of random draws whose dR (point) is below the targeted set's conservative bound."""
        return sum(1 for x in self.random_values if x < self.targeted.low) / len(self.random_values)


def compare_removal(
    pool: Sequence[RankedObject], k: int, trials: int, seed: int = 2026, name: str = "pool"
) -> RemovalComparison:
    if not 0 < k <= len(pool):
        raise ValueError(f"k must be in 1..{len(pool)}")
    ordered = sorted(pool, key=lambda r: (-r.risk.value, r.obj.jcat))
    rng = random.Random(seed)
    values = [removal_delta(rng.sample(ordered, k)).value for _ in range(trials)]
    return RemovalComparison(
        pool=name,
        pool_size=len(pool),
        k=k,
        trials=trials,
        targeted=removal_delta(ordered[:k]),
        random_values=values,
    )


@dataclass(frozen=True)
class Backtest:
    """How well the lifetime model predicts the reentry of objects that have already decayed."""

    n: int
    coverage: float
    """Share of objects whose actual lifetime falls inside the predicted range."""
    median_log10_ratio: float
    """Median of log10(predicted point / actual); 0 means no bias."""
    within_factor_2: float
    within_factor_3: float


def backtest_lifetimes(
    path: Path, kinds: frozenset[ObjectKind] = frozenset({ObjectKind.ROCKET_BODY})
) -> Backtest:
    """Compare predicted and actual lifetimes in ``data/gcat/decayed-sample.tsv``.

    Rocket bodies are used by default: payloads often lower their orbits on
    purpose, which a natural-decay model should not be asked to predict.
    Objects that reentered within 30 days of their orbit epoch are skipped.
    """
    atm = Atmosphere.bundled()
    ratios, inside = [], 0
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            kind = ObjectKind.from_gcat(row["type"])
            if kind not in kinds:
                continue
            obj = CatalogueObject(
                jcat=row["jcat"], satcat=row["satcat"], name=row["name"], kind=kind, active=False,
                owner="", state="", perigee_km=float(row["perigee_km"]), apogee_km=float(row["apogee_km"]),
                inc_deg=None, mass_kg=_num(row["mass_kg"]), mass_uncertain=row["mass_flag"] == "?",
                length_m=_num(row["length_m"]), diameter_m=_num(row["diameter_m"]),
                span_m=_num(row["span_m"]),
            )  # fmt: skip
            life = lifetime_estimate(obj, atm)
            days = (date.fromisoformat(row["decay_date"]) - date.fromisoformat(row["orbit_epoch"])).days
            if life is None or days < 30:
                continue
            actual = days / 365.25
            inside += life.low <= actual <= life.high
            ratios.append(math.log10(max(life.value, 1e-6) / actual))
    if not ratios:
        raise ValueError("no usable objects in the decayed sample")
    ratios.sort()
    n = len(ratios)
    return Backtest(
        n=n,
        coverage=inside / n,
        median_log10_ratio=ratios[n // 2],
        within_factor_2=sum(abs(x) < math.log10(2) for x in ratios) / n,
        within_factor_3=sum(abs(x) < math.log10(3) for x in ratios) / n,
    )


def concentration(ranked: Sequence[RankedObject], top: Iterable[int]) -> dict[int, float]:
    """Share of total R (point) held by the top-n objects, for each n."""
    total = math.fsum(r.risk.value for r in ranked)
    return {n: math.fsum(r.risk.value for r in ranked[:n]) / total for n in top}
