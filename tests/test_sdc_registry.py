from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from sdc import (
    ClaimState,
    DoubleCountingError,
    IndependenceError,
    Registry,
    RegistryError,
    TransitionError,
    verify_log,
)
from sdc.cli import main
from sdc.registry import GENESIS, canonical, entry_hash


def submission(
    claim_id: str = "C-1", object_id: str = "2003-031B", claimant: str = "remover"
) -> dict[str, Any]:
    return {
        "claim_id": claim_id,
        "object_id": object_id,
        "outcome_type": "active_removal",
        "event_date": "2026-05-14",
        "claimant": claimant,
        "unit_definition": "one intact object removed",
        "baseline": "would have stayed in orbit",
        "evidence": ["ssa:track-1"],
    }


def full_lifecycle(reg: Registry, claim_id: str = "C-1") -> None:
    reg.record("submit", "remover", submission(claim_id))
    reg.record("assign_verifier", "admin", {"claim_id": claim_id, "verifier": "lab"})
    reg.record("verify", "lab", {"claim_id": claim_id})
    reg.record("issue", "admin", {"claim_id": claim_id})
    reg.record("retire", "operator", {"claim_id": claim_id, "reason": "disclosure"})


def test_happy_path_and_chain(tmp_path: Path) -> None:
    log = tmp_path / "r.jsonl"
    reg = Registry(path=log)
    full_lifecycle(reg)
    assert reg.claims["C-1"].state is ClaimState.RETIRED
    assert [s for _, s in reg.claims["C-1"].history][-1] is ClaimState.RETIRED
    assert reg.entries[0]["prev_hash"] == GENESIS
    assert all(e["prev_hash"] == p["hash"] for p, e in zip(reg.entries, reg.entries[1:], strict=False))
    res = verify_log(log)
    assert res.ok and res.entries == 5 and res.head == reg.head
    reopened = Registry.open(log)
    assert reopened.claims["C-1"].state is ClaimState.RETIRED


def test_double_counting_blocked_until_void() -> None:
    reg = Registry()
    reg.record("submit", "remover", submission("C-1"))
    with pytest.raises(DoubleCountingError):
        reg.record(
            "submit", "other", submission("C-2", object_id=" 2003-031b ".strip().lower(), claimant="other")
        )
    reg.record("reject", "admin", {"claim_id": "C-1", "reason": "insufficient evidence"})
    reg.record("submit", "other", submission("C-2", claimant="other"))
    assert reg.claims["C-2"].state is ClaimState.CLAIMED


def test_rejected_event_leaves_no_trace() -> None:
    reg = Registry()
    reg.record("submit", "remover", submission())
    before = (len(reg.entries), reg.head)
    with pytest.raises(TransitionError):
        reg.record("issue", "admin", {"claim_id": "C-1"})
    assert (len(reg.entries), reg.head) == before
    assert reg.claims["C-1"].state is ClaimState.CLAIMED


@pytest.mark.parametrize(
    "verifier,conflicts",
    [("remover", []), ("lab", ["remover"])],
)
def test_verifier_must_be_independent(verifier: str, conflicts: list[str]) -> None:
    reg = Registry()
    reg.record("submit", "remover", submission())
    with pytest.raises(IndependenceError):
        reg.record(
            "assign_verifier",
            "admin",
            {"claim_id": "C-1", "verifier": verifier, "conflicts_disclosed": conflicts},
        )


def test_only_assigned_verifier_may_verify() -> None:
    reg = Registry()
    reg.record("submit", "remover", submission())
    reg.record("assign_verifier", "admin", {"claim_id": "C-1", "verifier": "lab"})
    with pytest.raises(IndependenceError):
        reg.record("verify", "remover", {"claim_id": "C-1"})


@pytest.mark.parametrize(
    "action,actor,payload,match",
    [
        ("submit", "someone", submission(), "only the claimant"),
        ("teleport", "x", {"claim_id": "C-1"}, "unknown action"),
        ("issue", "x", {"claim_id": "nope"}, "unknown claim"),
        ("assign_verifier", "admin", {"claim_id": "C-1", "verifier": " "}, "verifier required"),
        ("reject", "admin", {"claim_id": "C-1", "reason": ""}, "public reason"),
    ],
)
def test_rule_violations(action: str, actor: str, payload: dict[str, Any], match: str) -> None:
    reg = Registry()
    if action != "submit":
        reg.record("submit", "remover", submission())
    with pytest.raises(RegistryError, match=match):
        reg.record(action, actor, payload)


def test_duplicate_claim_id_and_missing_baseline() -> None:
    reg = Registry()
    reg.record("submit", "remover", submission())
    with pytest.raises(RegistryError, match="already exists"):
        reg.record("submit", "remover", submission(object_id="other"))
    with pytest.raises(ValueError):
        reg.record("submit", "remover", {**submission("C-9", object_id="x"), "baseline": ""})


def test_revocation_after_retirement_is_recorded() -> None:
    reg = Registry()
    full_lifecycle(reg)
    reg.record("revoke", "admin", {"claim_id": "C-1", "reason": "sensor data later invalidated"})
    assert reg.claims["C-1"].state is ClaimState.REVOKED
    with pytest.raises(TransitionError):
        reg.record("issue", "admin", {"claim_id": "C-1"})


def _lines(tmp_path: Path) -> tuple[Path, list[str]]:
    log = tmp_path / "r.jsonl"
    full_lifecycle(Registry(path=log))
    return log, log.read_text().splitlines()


@settings(max_examples=50, deadline=None)
@given(idx=st.integers(0, 4), new_actor=st.text(min_size=1, max_size=8))
def test_any_edit_is_detected(tmp_path_factory: pytest.TempPathFactory, idx: int, new_actor: str) -> None:
    log, lines = _lines(tmp_path_factory.mktemp("t"))
    entry = json.loads(lines[idx])
    if entry["actor"] == new_actor:
        return
    entry["actor"] = new_actor
    lines[idx] = canonical(entry)
    log.write_text("\n".join(lines) + "\n")
    res = verify_log(log)
    assert not res.ok and "hash" in (res.error or "")


def test_deletion_and_reordering_detected(tmp_path: Path) -> None:
    log, lines = _lines(tmp_path)
    log.write_text("\n".join(lines[:2] + lines[3:]) + "\n")
    assert not verify_log(log).ok
    log.write_text("\n".join([lines[1], lines[0], *lines[2:]]) + "\n")
    assert not verify_log(log).ok


def test_rehashed_forgery_with_illegal_history_rejected(tmp_path: Path) -> None:
    """A forger who recomputes every hash still cannot skip verification."""
    log, lines = _lines(tmp_path)
    entries = [json.loads(line) for line in lines]
    forged = [entries[0], entries[3]]  # submit, then issue straight away
    prev = GENESIS
    for seq, e in enumerate(forged):
        e.update(seq=seq, prev_hash=prev)
        e["hash"] = entry_hash(e)
        prev = e["hash"]
    log.write_text("\n".join(canonical(e) for e in forged) + "\n")
    res = verify_log(log)
    assert not res.ok and "cannot go" in (res.error or "")


def test_garbage_log(tmp_path: Path) -> None:
    log = tmp_path / "bad.jsonl"
    log.write_text("{not json\n")
    assert not verify_log(log).ok
    log.write_text(json.dumps({"seq": 0, "prev_hash": GENESIS}) + "\n")
    assert not verify_log(log).ok


def test_open_missing_file_is_empty(tmp_path: Path) -> None:
    reg = Registry.open(tmp_path / "new.jsonl")
    assert reg.head == GENESIS and not reg.claims


def test_cli(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    log = tmp_path / "demo.jsonl"
    assert main(["demo", str(log)]) == 0
    assert "rejected as expected" in capsys.readouterr().out
    assert main(["demo", str(log)]) == 1
    assert main(["verify", str(log)]) == 0
    assert "OK: 5 entries" in capsys.readouterr().out
    assert main(["show", str(log)]) == 0
    assert "retired" in capsys.readouterr().out
    log.write_text(log.read_text().replace("independent-ssa-lab", "orbit-cleanup-co", 1))
    assert main(["verify", str(log)]) == 1
    assert "INVALID" in capsys.readouterr().out
