# How to compare removal strategies

Use this guide to measure how much risk a removal action reduces, and to test whether choosing targets beats choosing at random.

## Size one action

An action is a file that lists the objects it changes, with their before and after states. The example is `examples/actions/adr-derelict-upper-stage.yaml`.

```console
$ uv run sdc delta-r examples/actions/adr-derelict-upper-stage.yaml --reference-unit 10
Illustrative research estimate - not an issued SDC
action       example-adr-01 (horizon 25 years)
dR           89  [24.23 - 270]  (risk proxy, kg-equivalent)
units        2 at dR0 = 10 per unit (from the conservative bound)
```

- **`dR`** is the reduction in risk, summed over the objects the action changes. It is a risk proxy in kg-equivalent units, not a physical quantity.
- **`[24.23 - 270]`** is the interval. The units are counted from the **lower bound**, so an uncertain estimate cannot inflate them.
- **`--reference-unit`** sets `dR0`, the risk reduction that one unit represents. Changing it changes the unit count and nothing else.

## Test targeted against random removal

```console
$ uv run sdc catalogue compare --k 10
```

This removes the `k` highest-R derelicts, then compares the total with `--trials` random sets of the same size. Use `--seed` to make the random draws repeatable:

```console
$ uv run sdc catalogue compare --k 10 --trials 10000 --seed 1
```

Read the output this way:

- **`ratio`** is the targeted total divided by the median random total.
- **`beaten`** is the share of random draws that fall below the targeted conservative bound. A high share means the targeting advantage holds even after the uncertainty is taken into account.

Try other sizes with `--k 1`, `--k 50`, and so on, to see how the advantage changes as the set grows.

## Change the pool

```console
$ uv run sdc catalogue compare --pool rocket_body --k 10
```

The pool determines which objects are candidates. The paper uses the derelict pool, so results from other pools are not directly comparable with it.

## Record a removal as a claim

Once a removal is verified, record it in a claim registry. See [verify a claim registry](verify-a-claim-registry.md).
