# How to read a score and its uncertainty

Use this guide when you have a mission score and need to know how far to trust it.

## Read the three parts of the result

1. **Point score**: the centre of the estimate.
2. **Interval**: the range the true value is expected to fall in. Each component and the total both have one.
3. **Band**: `low`, `medium` or `high`. The label `(band uncertain)` appears when the interval crosses a band boundary. Treat the band as provisional in that case.

## Find out which input drives the interval

```console
$ uv run sder sensitivity path/to/mission.yaml
```

Read the `variance` line. It gives each input's share of the total uncertainty. Improve the input with the largest share first. Usually that means replacing an `operator_statement` with `independently_observed` or `verified` evidence.

The `weights` line checks whether the band survives changes to the component weights. If the nominal band is kept in most draws, the band does not depend on the weights.

## Check which evidence label each input carries

```console
$ uv run sder score path/to/mission.yaml
```

Each component row shows its `evidence` type. The types, from most to least trusted, are `verified`, `independently_observed`, `modeled` and `operator_statement`. Each type sets the width of the uncertainty for that input.

## Get machine-readable output

```console
$ uv run sder score path/to/mission.yaml --json
```

Use this for pipelines. The `--json` output carries the same intervals and evidence labels.

## Check which method version produced the score

The header line shows the method and a short hash, for example `sder-research-v0.2 (d352186bed98)`. Two scores are comparable only when their method hashes match. To print the full method file, run:

```console
$ uv run sder methodology
```

See the [scoring model reference](../reference/scoring-model.md) for the fields and their meanings.
