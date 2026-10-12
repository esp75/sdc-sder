# SDC and SDER

**Space Debris Credit (SDC)** and **Space Debris Exposure Rating (SDER)** form an open research programme on two questions. How can a space mission's debris exposure be made visible honestly, including what is not known? And how can a verified reduction in long-lived debris risk be recognised without double counting or paying for what would have happened anyway?

[![ci](https://github.com/spacedebriscredit/sdc-sder/actions/workflows/ci.yml/badge.svg)](https://github.com/spacedebriscredit/sdc-sder/actions/workflows/ci.yml)
[![code: Apache-2.0](https://img.shields.io/badge/code-Apache--2.0-blue)](LICENSES/Apache-2.0.txt)
[![texts: CC BY / BY-SA 4.0](https://img.shields.io/badge/texts-CC%20BY%20%2F%20BY--SA%204.0-lightgrey)](LICENSING.md)
[![REUSE](https://img.shields.io/badge/REUSE-compliant-green)](REUSE.toml)

> **Status: v0.1, open for consultation.** No official SDER rating, issued SDC, certification or market exists. The code produces *illustrative research outputs* with uncalibrated placeholder parameters.

A research programme of the **SDC Institute** (in formation) · originated by **Maxime Kadri** · [spacedebriscredit.org](https://spacedebriscredit.org) · [Disclosures](DISCLOSURES.md) · [Origin](ORIGIN.md)

## Publications

| | |
|---|---|
| **Conference paper** | Kadri & Shishkina, [*Space Debris Credits: A Market-Based Framework for Governance and Environmental Stewardship in Orbit*](papers/2026-strauss-sdc-framework/README.md), Strauss Center Space Traffic Conference 2026, UT Austin |
| **SDC-WP-2026-01** | [Legal pathways for debris remediation under existing space law](papers/wp-01-legal-pathways/README.md) |
| **SDC-WP-2026-02** | [SDER and ΔR: reference methodology, implementation and limits](papers/wp-02-sder-methodology/README.md) |
| **SDC-WP-2026-03** | [Claim integrity without a blockchain](papers/wp-03-claim-integrity/README.md) |
| **Principles** | [Vision and Principles v0.1](spec/vision-and-principles-v0.1.md) (CC BY-SA) |
| **Rulebook** | [Consultation draft v0.2](spec/rulebook-v0.2-consultation-draft.md) (CC BY-SA) |
| **For everyone** | Explainers in [English](docs/explainers/en.md) and [French](docs/explainers/fr.md) · [institutional brief](spec/institutional-brief.md) · [consultation template](spec/consultation-template.md) |

The gaps that remain are listed openly in the [research roadmap](papers/ROADMAP.md).

## From paper to code

| Paper (Kadri & Shishkina 2026) | Implementation | What the tests check |
|---|---|---|
| §5 Exposure rating as a weighted sum of normalised factors | [`src/sder`](src/sder/), with a versioned [method file](src/sder/methodology/research-v0.1.yaml) | Weaker evidence widens the interval. Removing any input never lowers the score. Too much missing data withholds the result. |
| §6 $R_i = M_i \times L_i \times Pc_i$, $\Delta R(a) = \sum_i (R_{i,\text{before}} - R_{i,\text{after}})$ | [`src/sdc/risk.py`](src/sdc/risk.py), `sdc delta-r` | Removal never increases risk. ΔR is additive across objects. Removing the highest-R objects maximises ΔR. Units never exceed the conservative bound. |
| §7 Verification, registry, anti-double-counting | [`src/sdc/registry.py`](src/sdc/registry.py) | A self-verifying or conflicted verifier is refused. A double claim is refused. A forged log fails replay even when all its hashes are recomputed. |

Each principle is enforced in code:

| Principle (v0.1) | Enforcement |
|---|---|
| Distinguish evidence types (SDER 2) | Every input carries `verified`, `independently_observed`, `modeled` or `operator_statement`. |
| Report uncertainty (SDER 3) | Every component and every total is an interval, and the output says whether the band is certain. |
| Never fill gaps favourably (SDER 4) | A missing input is scored at worst case and named. Credits count from the conservative bound of ΔR. |
| Versioned decisions (SDER 7) | Every assessment is stamped with the SHA-256 of the method file. |
| Independent verification (SDC 3) | The registry refuses a verifier who is the claimant or who has declared a conflict with the claimant. |
| No double counting (SDC 4) | One live claim per (object, outcome). Corrections stay possible after retirement. |

## Quickstart

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12+.

```console
$ git clone https://github.com/spacedebriscredit/sdc-sder && cd sdc-sder
$ uv sync
$ uv run sder score examples/leo-smallsat-responsible.yaml
Illustrative research score - not an official SDER rating
mission      example-smallsat-550
method       sder-research-v0.1 (76dbc7650b97)
score        27.7  [20.1-45.2]  low (band uncertain)  indicative

component            weight    risk         range  evidence               rationale
disposal              0.250    14.5          0-44  operator_statement     plan 'reentry_within_5y' (residual 10) with 95% success probability
orbital_persistence   0.200    40.6         31-51  independently_observed ~15.5 years natural decay at 550 km if left uncontrolled
environment           0.150    70.0         60-80  independently_observed congestion band 500-650 km
conjunction           0.150     0.2          0-20  modeled                closest approach 12 km (11 km/s)
consequence           0.100    54.4         49-59  verified               150 kg fragmentation mass
passivation           0.075     0.0          0-30  operator_statement     passivation: full
maneuverability       0.075     0.0          0-10  independently_observed maneuverability: propulsive
```

The disposal plan rests only on the operator's word, so its range is wide. That is enough to make the band uncertain.

```console
$ uv run sdc delta-r examples/actions/adr-derelict-upper-stage.yaml --reference-unit 10
Illustrative research estimate - not an issued SDC
action       example-adr-01 (horizon 25 years)
dR           89  [24.23 - 270]  (risk proxy, kg-equivalent)
units        2 at dR0 = 10 per unit (from the conservative bound)

$ uv run sdc delta-r examples/actions/early-deorbit-smallsat.yaml     # dR 0.18: ~500x less
$ uv run sdc demo registry.jsonl     # submit → verify → issue → retire; the double claim is refused
$ uv run sdc verify registry.jsonl
OK: 5 entries, chain head 5d106b632f74…
```

## Development

```console
$ uv run pytest      # unit + Hypothesis property tests, coverage gate 90%
$ uv run mypy        # strict
$ uv run ruff check .
$ uv run python scripts/regenerate.py   # after intentional model/method changes
```

Scientific disagreements about the scores belong in the [methodology file](src/sder/methodology/research-v0.1.yaml). Pull requests that change weights or tables need sources, and they follow the process in [GOVERNANCE.md](GOVERNANCE.md). See also [CONTRIBUTING.md](CONTRIBUTING.md).

## Licensing

| Material | License |
|---|---|
| Code, schemas, methodology data | [Apache-2.0](LICENSES/Apache-2.0.txt) |
| *Vision and Principles*, *Rulebook* | [CC BY-SA 4.0](LICENSES/CC-BY-SA-4.0.txt) |
| Papers, explainers and other documents | [CC BY 4.0](LICENSES/CC-BY-4.0.txt) |

All three licenses allow commercial use. The 2025 patent application on these concepts has been abandoned. The names and any "rated", "verified" or "certified" claims are not licensed (see [TRADEMARKS.md](TRADEMARKS.md)). The license of each path is listed in [LICENSING.md](LICENSING.md).

## Cite

To cite the framework, cite the paper:

> Kadri, M., & Shishkina, A. (2026). *Space Debris Credits: A Market-Based Framework for Governance and Environmental Stewardship in Orbit.* Strauss Center Space Traffic Conference 2026, The University of Texas at Austin.

To cite the code and the programme, use [CITATION.cff](CITATION.cff):

> Kadri, M. *SDC and SDER: research programme and reference implementation*, v0.1.0 (2026). https://github.com/spacedebriscredit/sdc-sder
