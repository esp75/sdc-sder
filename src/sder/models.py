"""Data models for SDER inputs, methodology and assessments."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EvidenceClass(StrEnum):
    """How an input is known, from strongest to weakest (principle 2)."""

    VERIFIED = "verified"
    INDEPENDENTLY_OBSERVED = "independently_observed"
    MODELED = "modeled"
    OPERATOR_STATEMENT = "operator_statement"


EVIDENCE_STRENGTH: dict[EvidenceClass, int] = {
    EvidenceClass.VERIFIED: 3,
    EvidenceClass.INDEPENDENTLY_OBSERVED: 2,
    EvidenceClass.MODELED: 1,
    EvidenceClass.OPERATOR_STATEMENT: 0,
}


class DisposalPlan(StrEnum):
    CONTROLLED_REENTRY = "controlled_reentry"
    REENTRY_WITHIN_5Y = "reentry_within_5y"
    REENTRY_WITHIN_25Y = "reentry_within_25y"
    GRAVEYARD_ORBIT = "graveyard_orbit"
    NONE = "none"


class Passivation(StrEnum):
    FULL = "full"
    PARTIAL = "partial"
    NONE = "none"


class Maneuverability(StrEnum):
    PROPULSIVE = "propulsive"
    DRAG_DEVICE = "drag_device"
    NONE = "none"


class Evidenced[T](BaseModel):
    """A value together with how it is known. ``value=None`` means missing."""

    model_config = ConfigDict(frozen=True)

    value: T | None = None
    evidence: EvidenceClass = EvidenceClass.OPERATOR_STATEMENT
    source: str | None = Field(default=None, description="Reference to the supporting record.")


class MissionRef(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    name: str | None = None
    operator: str | None = None


class MissionInputs(BaseModel):
    """Everything the method may use. Any field may be missing."""

    model_config = ConfigDict(frozen=True)

    mean_altitude_km: Evidenced[float] = Evidenced()
    mass_kg: Evidenced[float] = Evidenced()
    disposal_plan: Evidenced[DisposalPlan] = Evidenced()
    disposal_reliability: Evidenced[float] = Evidenced()
    passivation: Evidenced[Passivation] = Evidenced()
    maneuverability: Evidenced[Maneuverability] = Evidenced()
    min_miss_distance_km: Evidenced[float] = Evidenced()
    relative_speed_km_s: Evidenced[float] = Evidenced()

    @model_validator(mode="after")
    def _check_ranges(self) -> MissionInputs:
        checks: list[tuple[str, float | None, float, float]] = [
            ("mean_altitude_km", self.mean_altitude_km.value, 0.0, 1e6),
            ("mass_kg", self.mass_kg.value, 0.0, 1e7),
            ("disposal_reliability", self.disposal_reliability.value, 0.0, 1.0),
            ("min_miss_distance_km", self.min_miss_distance_km.value, 0.0, 1e6),
            ("relative_speed_km_s", self.relative_speed_km_s.value, 0.0, 30.0),
        ]
        for name, value, low, high in checks:
            if value is not None and not low <= value <= high:
                raise ValueError(f"{name}={value} outside [{low}, {high}]")
        return self


class Mission(BaseModel):
    """An SDER input document (see examples/*.yaml)."""

    model_config = ConfigDict(frozen=True)

    mission: MissionRef
    inputs: MissionInputs = MissionInputs()


class Status(StrEnum):
    """Result status per principle 4: say what is missing, never hide it."""

    INDICATIVE = "indicative"
    PROVISIONAL = "provisional"
    WITHHELD = "withheld"


class Band(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ComponentResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    weight: float
    risk: float = Field(description="Component risk 0-100 (worst case if missing).")
    low: float
    high: float
    contribution: float = Field(description="weight * risk")
    evidence: EvidenceClass | None = Field(description="Weakest evidence among inputs; None if missing.")
    missing_inputs: list[str]
    rationale: str


class Assessment(BaseModel):
    """An illustrative SDER research assessment, not an official rating."""

    model_config = ConfigDict(frozen=True)

    label: str = "Illustrative research score - not an official SDER rating"
    mission_id: str
    methodology_id: str
    methodology_sha256: str
    status: Status
    score: float | None = Field(description="Conservative point estimate 0-100; None when withheld.")
    low: float
    high: float
    band: Band | None
    band_is_certain: bool = Field(description="True if the whole interval falls within one band.")
    missing_weight: float
    components: list[ComponentResult]
