# Documentation

This documentation follows the [Diátaxis](https://diataxis.fr/) framework. It has four kinds of page. Each one does a single job, so you can find what you need by asking what you are trying to do.

|  | Learning | Working |
|---|---|---|
| **Practical** | [**Tutorials**](tutorials/): learn by doing, step by step | [**How-to guides**](how-to/): solve one specific problem |
| **Theoretical** | [**Explanation**](explanation/): understand why it works this way | [**Reference**](reference/): look up exact commands, fields and formulas |

## Start here

1. [Score your first mission](tutorials/01-score-a-mission.md). About ten minutes, no data download.
2. [Rank real debris by risk](tutorials/02-rank-real-debris.md). Uses the committed GCAT snapshot.

## Where things are

| You want to... | Go to |
|---|---|
| Score a mission or check how sure the score is | [How-to: read a score and its uncertainty](how-to/read-a-score.md) |
| Measure how much a removal reduces risk | [How-to: compare targeted and random removal](how-to/compare-removal-strategies.md) |
| Check that a claim log has not been altered | [How-to: verify a claim registry](how-to/verify-a-claim-registry.md) |
| Refresh the catalogue or add a case study | [How-to: refresh the GCAT data](how-to/refresh-gcat-data.md) |
| Look up a command or flag | [Reference: CLI](reference/cli.md) |
| Look up the scoring formula and the input fields | [Reference: scoring model](reference/scoring-model.md) |
| Understand the design choices | [Explanation: how SDER works](explanation/how-sder-works.md) |
| Understand why claims are verified this way | [Explanation: claim integrity](explanation/claim-integrity.md) |
| Read the papers | [Working papers](../papers/README.md) |

Plain-language explainers in [English](explainers/en.md) and [French](explainers/fr.md) are written for a general audience.

## Status

Everything here is **research code**. Scores are illustrative, not official SDER ratings, and no SDC has been issued. The code reports its own limits: where a method table is still a placeholder, the output says so.
