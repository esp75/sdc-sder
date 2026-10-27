# Reference: command line

The package installs two commands, `sder` and `sdc`. Run them with `uv run` from the repository root, or activate the environment with `uv sync` and call them directly.

For any command, `--help` prints the full option list.

## `sder`: score missions

Illustrative SDER research scoring. Reads mission files and prints their scores.

| Command | Purpose |
|---|---|
| `sder score FILES... [--methodology PATH] [--json]` | Score one or more mission files. `--json` emits machine-readable output with the score, interval, band, `band_is_certain`, `missing_weight` and per-component values. |
| `sder sensitivity FILES... [--samples N] [--concentration X] [--seed N] [--json]` | Variance shares by input, and how stable the band is under weight perturbation. The default sample count is 5,000. |
| `sder methodology` | Print the method in use as JSON, including its SHA-256. |
| `sder schema` | Print the JSON Schemas for mission and assessment files. |

Example:

```console
$ uv run sder score examples/leo-smallsat-responsible.yaml --json
```

## `sdc`: claims, removal value and catalogue

Candidate SDC claim registry (research prototype).

| Command | Purpose |
|---|---|
| `sdc demo LOG` | Write a demo log: submit, verify, issue, retire. Also attempts a double claim, which is refused. |
| `sdc verify LOG` | Check every entry's hash and the chain. Reports `OK` with the chain head, or `INVALID` with the first failing line. |
| `sdc show LOG` | List the claims in a log and their states. |
| `sdc delta-r ACTION [--reference-unit X] [--json]` | Reduction in risk (ΔR) of an action file, and its unit count. `--reference-unit` sets `dR0`, the ΔR per unit. |
| `sdc catalogue rank` | Rank objects by R = M × L × Pc. |
| `sdc catalogue compare` | Targeted top-k removal against random k-subsets. Reproduces Figure 3 of the paper. |
| `sdc catalogue backtest` | Check the lifetime model against objects that have reentered. |

### `sdc catalogue` options

| Option | Applies to | Meaning |
|---|---|---|
| `--data DIR` | all | Directory with the GCAT extracts. Defaults to the committed snapshot in `data/gcat/`. |
| `--horizon YEARS` | all | Horizon H in years. Default 25. |
| `--pool {derelict,rocket_body,all}` | `rank`, `compare`, `backtest` | Which objects are candidates. Default `derelict`. |
| `--top N` | `rank` | Number of objects to show. Default 20. |
| `--json` | `rank` | Machine-readable output. |
| `--k K` | `compare` | Size of the removed set. Default 10. |
| `--trials N` | `compare` | Number of random draws. Default 10,000. |
| `--seed N` | `compare` | Random seed. Default 2026. The same seed gives the same output. |

Examples:

```console
$ uv run sdc catalogue rank --pool derelict --top 10
$ uv run sdc catalogue compare --k 10 --trials 10000 --seed 1
$ uv run sdc delta-r examples/actions/adr-derelict-upper-stage.yaml --reference-unit 10
```

## Exit codes

`sdc verify` exits with status 0 when the log is intact and 1 when it is not. It prints `OK` or `INVALID` and names the failing line.

## Related

- [How to read a score](../how-to/read-a-score.md)
- [How to verify a claim registry](../how-to/verify-a-claim-registry.md)
- [Scoring model](scoring-model.md)
