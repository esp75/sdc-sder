"""A tamper-evident, append-only claim registry.

Each log line is a JSON object that carries the SHA-256 of the previous line, so
any edit, deletion or reordering breaks the chain. The current state is never
stored. It is rebuilt by replaying the log through the same rules that accepted
each event, so a log with valid hashes but an illegal history is rejected too.
No blockchain is needed for this.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import TRANSITIONS, VOID_STATES, Claim, ClaimState, ClaimSubmission

GENESIS = "0" * 64


class RegistryError(Exception):
    """An event that the SDC rules do not allow."""


class DoubleCountingError(RegistryError):
    """A second live claim for the same object and outcome."""


class IndependenceError(RegistryError):
    """A verifier who is the claimant or declared a conflict."""


class TransitionError(RegistryError):
    """A lifecycle step that is not allowed from the current state."""


class IntegrityError(RegistryError):
    """The hash chain or sequence is broken."""


def canonical(obj: dict[str, Any]) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def entry_hash(entry: dict[str, Any]) -> str:
    body = {k: v for k, v in entry.items() if k != "hash"}
    return hashlib.sha256(canonical(body).encode()).hexdigest()


# action -> target state
_ACTIONS: dict[str, ClaimState] = {
    "assign_verifier": ClaimState.UNDER_REVIEW,
    "verify": ClaimState.VERIFIED,
    "reject": ClaimState.REJECTED,
    "issue": ClaimState.ISSUED,
    "retire": ClaimState.RETIRED,
    "revoke": ClaimState.REVOKED,
}


class Registry:
    """In-memory registry state with an optional JSONL log on disk."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path
        self.claims: dict[str, Claim] = {}
        self.entries: list[dict[str, Any]] = []

    @property
    def head(self) -> str:
        return self.entries[-1]["hash"] if self.entries else GENESIS

    # ---- rules -------------------------------------------------------------

    def _apply(self, seq: int, action: str, actor: str, payload: dict[str, Any]) -> Claim:
        if action == "submit":
            sub = ClaimSubmission.model_validate(payload)
            if sub.claim_id in self.claims:
                raise RegistryError(f"claim_id {sub.claim_id!r} already exists")
            if actor != sub.claimant:
                raise RegistryError("only the claimant may submit a claim")
            for other in self.claims.values():
                if other.submission.outcome_key == sub.outcome_key and other.state not in VOID_STATES:
                    raise DoubleCountingError(
                        f"{sub.object_id} {sub.outcome_type} already claimed by "
                        f"{other.submission.claim_id} ({other.state})"
                    )
            claim = Claim(submission=sub, history=[(seq, ClaimState.CLAIMED)])
            self.claims[sub.claim_id] = claim
            return claim

        if action not in _ACTIONS:
            raise RegistryError(f"unknown action {action!r}")
        claim_id = payload.get("claim_id")
        if claim_id not in self.claims:
            raise RegistryError(f"unknown claim {claim_id!r}")
        claim = self.claims[claim_id]
        target = _ACTIONS[action]
        if target not in TRANSITIONS[claim.state]:
            raise TransitionError(f"{claim_id}: cannot go {claim.state} -> {target}")

        if action == "assign_verifier":
            verifier = str(payload.get("verifier", "")).strip()
            conflicts = [str(c).strip() for c in payload.get("conflicts_disclosed", [])]
            if not verifier:
                raise RegistryError("verifier required")
            if verifier == claim.submission.claimant or claim.submission.claimant in conflicts:
                raise IndependenceError(f"{verifier} is not independent of {claim.submission.claimant}")
            claim.verifier = verifier
        elif action == "verify" and actor != claim.verifier:
            raise IndependenceError(f"only the assigned verifier {claim.verifier} may verify")
        elif action in {"reject", "revoke"} and not str(payload.get("reason", "")).strip():
            raise RegistryError(f"{action} requires a public reason")

        claim.state = target
        claim.history.append((seq, target))
        return claim

    # ---- log ---------------------------------------------------------------

    def record(
        self, action: str, actor: str, payload: dict[str, Any], timestamp: str | None = None
    ) -> dict[str, Any]:
        """Validate an event, apply it, and append it to the chain (and file)."""
        seq = len(self.entries)
        # Apply to a copy first, so that a rejected event leaves no trace.
        snapshot = {k: v.model_copy(deep=True) for k, v in self.claims.items()}
        try:
            self._apply(seq, action, actor, payload)
        except Exception:
            self.claims = snapshot
            raise
        entry: dict[str, Any] = {
            "seq": seq,
            "timestamp": timestamp or dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
            "action": action,
            "actor": actor,
            "payload": payload,
            "prev_hash": self.head,
        }
        entry["hash"] = entry_hash(entry)
        self.entries.append(entry)
        if self.path is not None:
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(canonical(entry) + "\n")
        return entry

    @classmethod
    def replay(cls, lines: Iterator[str] | list[str], path: Path | None = None) -> Registry:
        """Rebuild state from log lines, checking the chain and every rule."""
        reg = cls(path=None)
        for n, line in enumerate(lines):
            if not line.strip():
                continue
            entry = json.loads(line)
            if entry.get("seq") != len(reg.entries):
                raise IntegrityError(f"line {n + 1}: expected seq {len(reg.entries)}, got {entry.get('seq')}")
            if entry.get("prev_hash") != reg.head:
                raise IntegrityError(f"line {n + 1}: prev_hash does not match previous entry")
            if entry.get("hash") != entry_hash(entry):
                raise IntegrityError(f"line {n + 1}: content does not match its hash")
            try:
                reg._apply(entry["seq"], entry["action"], entry["actor"], entry["payload"])
            except RegistryError as exc:
                raise RegistryError(f"line {n + 1}: {exc}") from exc
            reg.entries.append(entry)
        reg.path = path
        return reg

    @classmethod
    def open(cls, path: Path) -> Registry:
        if not path.exists():
            return cls(path=path)
        with path.open(encoding="utf-8") as fh:
            return cls.replay(list(fh), path=path)


@dataclass(frozen=True)
class VerifyResult:
    ok: bool
    entries: int
    head: str
    error: str | None = None


def verify_log(path: Path) -> VerifyResult:
    try:
        reg = Registry.open(path)
    except (RegistryError, json.JSONDecodeError, KeyError, ValueError) as exc:
        return VerifyResult(ok=False, entries=0, head="", error=str(exc))
    return VerifyResult(ok=True, entries=len(reg.entries), head=reg.head)
