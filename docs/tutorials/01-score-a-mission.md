# Tutorial 1: Score your first mission

In this tutorial you will score a small satellite, read the result, and see how its uncertainty changes when one input is only an operator's claim. It takes about ten minutes and needs no data download.

**You will need:** [uv](https://docs.astral.sh/uv/) and Python 3.12 or later.

## 1. Install

```console
$ git clone https://github.com/esp75/sdc-sder
$ cd sdc-sder
$ uv sync
```

## 2. Look at the input

Open the example mission:

```console
$ cat examples/leo-smallsat-responsible.yaml
```

Each input has a value, an evidence type and a source. The evidence type matters most. `verified` and `independently_observed` values are trusted more than `operator_statement`. The disposal plan here is only an operator's statement, so it is the input to watch.

## 3. Score it

```console
$ uv run sder score examples/leo-smallsat-responsible.yaml
Illustrative research score - not an official SDER rating
mission      example-smallsat-550
method       sder-research-v0.2 (d352186bed98)
score        24.9  [17.2-42.4]  low (band uncertain)  indicative

component            weight    risk         range  evidence               rationale
disposal              0.250    14.5          0-44  operator_statement     plan 'reentry_within_5y' (residual 10) with 95% success probability
orbital_persistence   0.200    25.7         16-36  independently_observed ~4.9 years natural decay at 550 km if left uncontrolled
...
```

Read the first line of the result, not just the number:

- **`24.9`** is the point score.
- **`[17.2-42.4]`** is the interval. The true value is expected to lie inside it.
- **`low (band uncertain)`** says the interval crosses a band boundary. The score is low, but it could be medium.

## 4. See what drives the uncertainty

```console
$ uv run sder sensitivity examples/leo-smallsat-responsible.yaml
mission      example-smallsat-550  [sder-research-v0.2]
score        24.9 (low)
inputs       band shares: low 86%, medium 14%, high 0%
weights      nominal band kept in 100% of 5000 draws (concentration 100); score 5-95%: 21.0-28.9
variance     disposal 75%, orbital_persistence 10%, conjunction 6%, environment 5%, passivation 3%, consequence 1%
```

Disposal accounts for 75% of the variance. That is the input to improve first, and the way to do it is to replace the operator's statement with independent evidence.

## 5. Try it yourself

Change `disposal_plan` in a copy of the file to a value you think is better supported, then score it again. Notice that the component's evidence label changes the interval even when the value stays the same.

## What you have learned

- A score is always an interval, and the output says when the interval crosses a band.
- Weaker evidence widens the interval. The tests check this for every input.
- Sensitivity analysis shows which input to improve first.

Next: [Tutorial 2, rank real debris by risk](02-rank-real-debris.md).
