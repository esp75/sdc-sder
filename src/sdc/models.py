"""Claim model and lifecycle for a candidate Space Debris Credit (SDC)."""

from __future__ import annotations

import datetime as dt
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class OutcomeType(StrEnum):
    """The physical outcome a claim asserts. The unit must be defined first (SDC principle 1).

    These are the eligible action classes in Kadri & Shishkina (2026), Table 1.
    """

    EARLY_DEORBIT = "early_deorbit"  # post-mission disposal beyond the baseline
    CONTROLLED_REENTRY = "controlled_reentry"
    PASSIVATION = "passivation"
    ACTIVE_REMOVAL = "active_removal"  # of an intact derelict, with consent
    SERVICING_ENABLED_DISPOSAL = "servicing_enabled_disposal"


class ClaimState(StrEnum):
    CLAIMED = "claimed"
    UNDER_REVIEW = "under_review"
    VERIFIED = "verified"
    ISSUED = "issued"
    RETIRED = "retired"
    REJECTED = "rejected"
    REVOKED = "revoked"


# Allowed transitions. A revocation stays possible after retirement, so that
# corrections are always recorded and reported, never silently dropped
# (SDC principle 4).
TRANSITIONS: dict[ClaimState, frozenset[ClaimState]] = {
    ClaimState.CLAIMED: frozenset({ClaimState.UNDER_REVIEW, ClaimState.REJECTED}),
    ClaimState.UNDER_REVIEW: frozenset({ClaimState.VERIFIED, ClaimState.REJECTED}),
    ClaimState.VERIFIED: frozenset({ClaimState.ISSUED, ClaimState.REVOKED}),
    ClaimState.ISSUED: frozenset({ClaimState.RETIRED, ClaimState.REVOKED}),
    ClaimState.RETIRED: frozenset({ClaimState.REVOKED}),
    ClaimState.REJECTED: frozenset(),
    ClaimState.REVOKED: frozenset(),
}

# States that no longer block a fresh claim on the same outcome.
VOID_STATES = frozenset({ClaimState.REJECTED, ClaimState.REVOKED})


class ClaimSubmission(BaseModel):
    """What a claimant submits. Baseline and evidence are mandatory (SDC principles 2-3)."""

    model_config = ConfigDict(frozen=True)

    claim_id: str = Field(min_length=1)
    object_id: str = Field(min_length=1, description="COSPAR or NORAD identifier of the object.")
    outcome_type: OutcomeType
    event_date: dt.date
    claimant: str = Field(min_length=1)
    unit_definition: str = Field(min_length=1, description="What one unit of this claim represents.")
    baseline: str = Field(min_length=1, description="What would likely have happened without the action.")
    evidence: list[str] = Field(min_length=1, description="References to supporting records.")

    @field_validator("object_id", "claimant")
    @classmethod
    def _normalise(cls, v: str) -> str:
        return v.strip()

    @property
    def outcome_key(self) -> tuple[str, OutcomeType]:
        return (self.object_id.upper(), self.outcome_type)


class Claim(BaseModel):
    """Current state of a claim, rebuilt by replaying the registry log."""

    submission: ClaimSubmission
    state: ClaimState = ClaimState.CLAIMED
    verifier: str | None = None
    history: list[tuple[int, ClaimState]] = Field(default_factory=list)
