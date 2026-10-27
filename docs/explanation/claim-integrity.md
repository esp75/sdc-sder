# Explanation: claim integrity

An outcome-based credit is only worth something if three things are true. Someone is accountable for the claim, someone other than the claimant checks it, and the same physical outcome cannot be counted twice. This page explains how the registry enforces those rules, and why it does not need a blockchain to do so. The full specification is [WP-03](../../papers/wp-03-claim-integrity/README.md).

## The problem: double counting

Environmental markets have shown that weak additionality and double counting let a credit scheme pay for outcomes that would have happened anyway. A debris removal can be claimed by an operator, by a launch provider and by a government programme. Without a rule, all three could sell the same kilogram of risk reduction.

## The five properties

WP-03 turns the principles into five checkable properties:

| # | Property | What it prevents |
|---|---|---|
| P1 | A claim states its unit, baseline and evidence before review | Claims that change their terms after the fact |
| P2 | The verifier is not the claimant and has declared any conflicts | Marking your own homework |
| P3 | One physical outcome on one object supports at most one live claim | Double counting |
| P4 | Retirement happens once and cannot be reversed | Selling the same credit twice |
| P5 | Rejections and revocations carry a public reason, and corrections stay possible | Silent edits |

Each property is enforced in code, not only described in policy. `sdc demo` shows the refusals: a double claim on the same object and outcome is rejected with the reason `already claimed`.

## The mechanism: an append-only, hash-chained log

Every entry in the registry records the hash of the entry before it. Changing any line changes its hash, which no longer matches the next entry's record. `sdc verify` replays the whole chain and reports the first line that does not match.

This makes the log tamper-evident, not tamper-proof. Someone who rewrites the whole log and recomputes every hash produces a log that verifies on its own. The protection comes from publishing the **chain head**, the hash of the last entry, somewhere the log's author cannot quietly change. Anyone who holds an earlier head can detect a rewrite. The [verification guide](../how-to/verify-a-claim-registry.md) shows the steps.

## Why not a blockchain

A blockchain would add a distributed ledger, consensus and a token. None of those supplies the properties above. A blockchain can record who submitted a claim, but it cannot tell whether the claim is true, whether the verifier was independent, or whether the physical outcome was already counted off-chain. Those are institutional questions, and the registry answers them with the rules in P1 to P5. The hash chain only makes the record hard to rewrite.

Independence and accreditation stay with people and institutions. The registry checks the rules it can check, and leaves the rest to the verifier.

## Why this paper discloses the design

The registry designs described in WP-03 are the same ones the originator described in a 2025 patent application that has since been abandoned. WP-03 serves as their public technical disclosure, so the designs are documented in the open. The [disclosures](../../DISCLOSURES.md) file records the originator's competing interests.

## Further reading

- [WP-03: claim integrity without a blockchain](../../papers/wp-03-claim-integrity/README.md)
- [How to verify a claim registry](../how-to/verify-a-claim-registry.md)
- [CLI reference](../reference/cli.md)
