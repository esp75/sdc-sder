# How to verify a claim registry

Use this guide to check that a claim log has not been changed since it was written. The registry is a hash chain: every entry records the hash of the entry before it, so editing any line breaks every later link.

## Verify a log

```console
$ uv run sdc verify registry.jsonl
OK: 5 entries, chain head 5d106b632f74fd4a39f361f0bc75dd918aaf61370386751ff211be766066291f
```

The **chain head** is the hash of the last entry. Publish it somewhere separate from the log, such as a repository release note or a signed message. Anyone can then confirm that the log still ends at the same point.

## Detect a change

Here is what happens when one character of an entry is altered:

```console
$ uv run sdc verify registry.jsonl
INVALID: line 1: content does not match its hash
```

The check reports the first line where the content no longer matches its own hash. Restore the log from a copy, or record a correction as a new entry. Do not edit old lines.

## Try it on a demo log

```console
$ uv run sdc demo registry.jsonl
$ uv run sdc verify registry.jsonl
$ uv run sdc show registry.jsonl
```

`sdc demo` writes a short log that runs a claim through its lifecycle: submission, verification, issue and retirement. It also attempts a double claim, which the registry refuses. `sdc show` lists the claims and their states.

## Understand what verification does and does not prove

- It proves the log is **internally consistent** and has not been altered since the chain head was recorded.
- It does not prove that the claimed removal happened. That needs the independent verifier named in the claim.
- A log rewritten from scratch, with every hash recomputed, verifies on its own. Only comparing its chain head with one you published earlier reveals the rewrite. This is why the head must be published separately.

See [claim integrity](../explanation/claim-integrity.md) for why the registry works this way.
