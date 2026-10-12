"""Loading and validating a versioned SDER methodology file."""

from __future__ import annotations

import hashlib
import math
from importlib import resources
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, model_validator

from .models import DisposalPlan, EvidenceClass, Maneuverability, Passivation

DEFAULT_METHODOLOGY = "research-v0.2.yaml"


class Bands(BaseModel):
    model_config = ConfigDict(frozen=True)

    low_below: float
    medium_below: float


class DisposalParams(BaseModel):
    model_config = ConfigDict(frozen=True)

    plan_risk: dict[DisposalPlan, float]


class PersistenceParams(BaseModel):
    model_config = ConfigDict(frozen=True)

    lifetime_table: list[tuple[float, float]]
    saturation_years: float

    @model_validator(mode="after")
    def _sorted(self) -> PersistenceParams:
        alts = [a for a, _ in self.lifetime_table]
        years = [y for _, y in self.lifetime_table]
        if alts != sorted(alts) or years != sorted(years) or min(years) <= 0:
            raise ValueError("lifetime_table must be increasing in altitude and lifetime (> 0)")
        return self


class EnvironmentParams(BaseModel):
    model_config = ConfigDict(frozen=True)

    bands: list[tuple[float, float, float]]
    default: float


class ConjunctionParams(BaseModel):
    model_config = ConfigDict(frozen=True)

    characteristic_km: float
    reference_speed_km_s: float
    min_speed_factor: float


class ConsequenceParams(BaseModel):
    model_config = ConfigDict(frozen=True)

    saturation_mass_kg: float


class PassivationParams(BaseModel):
    model_config = ConfigDict(frozen=True)

    levels: dict[Passivation, float]


class ManeuverabilityParams(BaseModel):
    model_config = ConfigDict(frozen=True)

    levels: dict[Maneuverability, float]


class Methodology(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    status: str
    title: str
    weights: dict[str, float]
    evidence_uncertainty: dict[EvidenceClass, float]
    withhold_if_missing_weight_above: float
    bands: Bands
    disposal: DisposalParams
    orbital_persistence: PersistenceParams
    environment: EnvironmentParams
    conjunction: ConjunctionParams
    consequence: ConsequenceParams
    passivation: PassivationParams
    maneuverability: ManeuverabilityParams
    sha256: str = ""

    @model_validator(mode="after")
    def _check(self) -> Methodology:
        if not math.isclose(sum(self.weights.values()), 1.0, abs_tol=1e-9):
            raise ValueError(f"weights must sum to 1.0, got {sum(self.weights.values())}")
        if set(self.evidence_uncertainty) != set(EvidenceClass):
            raise ValueError("evidence_uncertainty must cover every evidence class")
        if set(self.disposal.plan_risk) != set(DisposalPlan):
            raise ValueError("disposal.plan_risk must cover every disposal plan")
        return self


def _parse(raw: bytes) -> Methodology:
    data: dict[str, Any] = yaml.safe_load(raw)
    data["sha256"] = hashlib.sha256(raw).hexdigest()
    return Methodology.model_validate(data)


def load_methodology(path: str | Path | None = None) -> Methodology:
    """Load a methodology file, or the bundled default when ``path`` is None."""
    if path is None:
        raw = resources.files("sder").joinpath("methodology", DEFAULT_METHODOLOGY).read_bytes()
    else:
        raw = Path(path).read_bytes()
    return _parse(raw)
