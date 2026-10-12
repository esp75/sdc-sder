# Claim integrity without a blockchain: lifecycle, independence and double-counting controls for outcome-based debris credits

| | |
|---|---|
| **Series** | SDC Institute Working Paper SDC-WP-2026-03 |
| **Version** | 0.1, 12 October 2026 |
| **Author** | Maxime Kadri, SDC Institute (in formation) |
| **Status** | Working paper. Open for outside peer review ([how to review](../ROADMAP.md#outside-peer-review)). |
| **Extends** | Kadri & Shishkina (2026), §4, §7 and §16.2 |
| **Code** | [`src/sdc/models.py`](../../src/sdc/models.py), [`src/sdc/registry.py`](../../src/sdc/registry.py) |
| **Competing interests** | See [DISCLOSURES.md](../../DISCLOSURES.md). This paper also serves as the public technical disclosure of the registry designs from the originator's abandoned 2025 patent application (§6). |
| **Funding** | None |
| **Data availability** | Running `uv run sdc demo registry.jsonl` reproduces the demonstration log. |
| **License** | [CC BY 4.0](../../LICENSES/CC-BY-4.0.txt) |

## Abstract

An outcome-based credit needs a record of who claimed what, who verified it, and whether the same outcome was counted twice. Environmental markets have shown that weak additionality and double counting can make a credit scheme pay for outcomes that would have happened anyway (ICVCM 2024). This paper specifies the integrity layer that Kadri & Shishkina (2026) describe for Space Debris Credits. It has four parts: an explicit claim lifecycle, rules of independence between claimant and verifier, a uniqueness key per physical outcome, and an append-only, hash-chained log that is replayed through the same rules whenever it is read. We argue that this gives the tamper evidence usually sought from a blockchain without its costs or its governance problems, and that it can be audited by anyone holding a copy of the log. We document a working reference implementation, state the threats it does and does not address, and record publicly the alternative designs considered in 2025.

## 1 Requirements

Kadri & Shishkina (2026, §7) name five elements of a minimum viable verification and registry architecture: a public rulebook, independent accredited verification, an auditable registry with unique identifiers, a dispute process, and transparency requirements. The registry has to make the following properties enforceable and checkable:

| # | Property | Source |
|---|---|---|
| P1 | A claim states its unit, its baseline and its evidence before review | Vision & Principles, SDC 1–2; paper §4 |
| P2 | The verifier is not the claimant and has declared any conflicts | SDC 3; paper §16.2 |
| P3 | One physical outcome on one object supports at most one live claim | SDC 4; paper §7 |
| P4 | Retirement happens once and cannot be reversed | Paper §4 |
| P5 | Rejections and revocations carry a public reason, and corrections remain possible after retirement | SDC 4; GOVERNANCE.md |
| P6 | Any edit, deletion or reordering of the record can be detected by any holder of a copy | Paper §7 ("tamper evident registry") |

## 2 Lifecycle

A claim moves through the states below. Only the listed transitions are allowed.

```
claimed ──► under_review ──► verified ──► issued ──► retired
   │              │              │           │          │
   └──► rejected ◄┘              └──► revoked ◄──────────┘
```

- `rejected` and `revoked` are **void** states. A void claim no longer blocks a fresh claim on the same outcome.
- `retired → revoked` is permitted on purpose (P5). If a retired credit later proves invalid, for example because a "reentered" object is re-acquired by tracking, the correction is recorded and reported, not silently dropped.

## 3 Rules enforced at every event

Each event is an `(action, actor, payload)` triple. The registry applies it only if it satisfies these rules:

1. **Submission.** Only the claimant may submit. Unit definition, baseline and at least one evidence reference are mandatory (P1).
2. **Uniqueness.** The outcome key is (object identifier, normalised to upper case; outcome type). A submission is refused if a non-void claim already holds the same key (P3). This guards against double issuance. Double *use*, meaning two parties counting the same retired credit, is prevented because retirement is a single, irreversible state that records the retiring party (P4).
3. **Independence.** A verifier who is the claimant, or for whom the claimant appears in the declared conflicts, cannot be assigned. Only the assigned verifier may verify (P2).
4. **Reasons.** `reject` and `revoke` must carry a non-empty public reason (P5).
5. **Transitions.** Any other transition is refused.

The rules are applied to a copy of the state first, so a refused event leaves no trace.

## 4 The tamper-evident log

Each event is stored as one line of canonical JSON (sorted keys, no whitespace). The line contains the sequence number, timestamp, action, actor, payload, the hash of the previous line (`prev_hash`, all zeros for the first), and its own SHA-256 `hash` computed over everything else. The current state is **never stored**. Opening a log means replaying it from the start. For each line the replay checks the sequence number, `prev_hash` and `hash`, then applies the rules in §3.

So the log is checked twice. A forger who edits a payload and recomputes every subsequent hash still fails, because the forged history must also be *legal*. A double claim inserted into a valid chain is rejected on replay just as it would have been rejected when submitted. `sdc verify` runs both checks on a log and reports the head hash.

**Why not a blockchain?** Both the 2025 designs (§6) and a long line of carbon-registry experiments put credits on a blockchain. The integrity property the scheme needs is P6: *evidence* of tampering, checkable by third parties. Crosby & Wallach (2009) [crosby2009] showed how to provide that efficiently with hash-based logs that can be audited, held by a logger who need not be trusted. Certificate Transparency (RFC 6962) [rfc6962] then deployed append-only Merkle-tree logs at internet scale, with independent monitors. Neither approach needs consensus among anonymous parties, tokens, or fees. A credit scheme already has an accountable administrator and accredited verifiers (paper §15). It needs that administrator's record to be checkable by others. Kadri & Shishkina (2026, §7) say the same: the registry can be implemented "by a regulated administrator, a consortium record system, or other institutional designs".

**What a hash chain does *not* give.** A chain proves internal consistency. It cannot stop an administrator from rewriting the entire history before anyone has copied it. The remedy is to **publish the head hash** at regular intervals somewhere the administrator does not control. Options include independent mirrors, signed releases, or a transparency log maintained by third parties. The v0.1 implementation does not yet do this (§7).

## 5 Threat model

| Threat | Control | Status in v0.1 |
|---|---|---|
| Double issuance for one outcome | Uniqueness key + replay | Implemented, tested |
| Self-verification or conflicted verifier | Independence rules | Implemented, tested |
| Silent edit, deletion or reordering of history | Hash chain + replay | Implemented, tested |
| Illegal history with valid hashes | Rules re-applied on replay | Implemented, tested |
| Whole-log rewrite before first publication | Head anchoring / witnesses | **Not implemented** |
| False evidence submitted in good faith or bad faith | Accredited verification, audit sampling, revocation | Process (Rulebook), not code |
| Same outcome claimed in *another* scheme | Cross-registry identifiers, attribution to the authorising State | **Open**; see WP-01 and paper §7 |
| Collusion between claimant and verifier | Conflict declarations, rotation, re-audit | Partially (declarations only) |
| Identity spoofing of actors | Signed events | **Not implemented**; actors are strings |

## 6 Designs considered in 2025 (public technical disclosure)

The originator's 2025 design work, including a French patent application that has since been abandoned, explored a token-based variant. It is recorded here in neutral form so that its technical features are publicly disclosed and remain free to use:

1. **Multi-source quorum verification.** Several independent data sources (sensor networks, commercial SSA providers, operator telemetry) report on a candidate mitigation event, such as a reentry, deorbit or capture. The event is confirmed when concordant reports reach a predefined quorum or a weighted threshold.
2. **Automatic audit trigger.** If the source reports conflict, or the quorum is not reached, an audit by independent third-party validators starts automatically.
3. **Paired records per verified event.** A fungible credit record is created together with a non-fungible event certificate. The certificate's metadata include the object identifier, the event timestamp, the debris classification and a hash or signature binding the certificate to the verification evidence.
4. **Collateralised verifiers.** Each data source posts a stake or reputation bond. The bond is forfeited, in part or in full, if the source is found to have reported false or collusive data.
5. **Coupling the rating to obligations.** A risk rating computed from weighted parameters (orbital data, compliance history) adjusts an operator's required mitigation quantity in a bonus–malus scheme.
6. **Staged governance.** Control of rule parameters is held first by a multi-signature consortium and later passed to a broader governance body.
7. **Equity allocation.** A fixed share of transaction proceeds goes automatically to a fund for verification capacity and for emerging space actors.

The reference design keeps the ideas in items 1–2 (several sources; automatic audit triggers) and item 7 (equity support), which the Rulebook treats as options. It handles them as institutional procedure, with no smart contracts. It drops tokens and staking. They add cost, legal uncertainty and attack surface without improving P1–P6, and they assume tradability, which the Vision & Principles explicitly leaves undecided (SDC 5). It reconsiders item 5 in WP-02 §5 (compliance history excluded).

## 7 Limitations and next steps

- **Anchoring.** Publish the log head on a schedule and allow independent witnesses to co-sign it.
- **Signed events.** Each actor signs each event, for example with Ed25519, so that authorship can be checked as well as integrity.
- **Merkle structure.** Replace the linear chain with a Merkle tree so that proofs of inclusion and consistency are logarithmic in size (Crosby & Wallach 2009; RFC 6962). The gain appears only at scale.
- **Partial units and transfer.** v0.1 records one claim per outcome. ΔR-proportional unit counts ([`sdc.risk`](../../src/sdc/risk.py)) and any transfer step are not yet linked into the lifecycle.
- **Confidentiality.** Verifier evidence may be sensitive (paper §16.3). Commitments, meaning hashes of evidence, can be published while the evidence itself stays with auditors.

## References

Full entries are in [references.bib](../references.bib): `kadri2026sdc`, `crosby2009`, `rfc6962`, `icvcm2024`.
