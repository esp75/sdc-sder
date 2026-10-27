# Tutorial 2: Rank real debris by risk

In this tutorial you will rank the intact objects in low Earth orbit by risk, using the committed GCAT snapshot. The ranking uses the product R = M × L × Pc: mass, times the expected lifetime in orbit, times the probability of a collision.

**You will need:** the [setup from Tutorial 1](01-score-a-mission.md#1-install). No download is needed. The snapshot ships with the repository.

## 1. Rank the top three

```console
$ uv run sdc catalogue rank --top 3
Illustrative research estimate - not an issued SDC
18036 intact LEO objects ranked by R = M x L x Pc over 25 years
   #  object                              kind             alt km    M kg     L        Pc        R  range
   1  23343 Zenit-2 No. 1-87 Stage 2      rocket_body     626-634    9000  1.00  1.77e-02      160  10.8-246
   2  25400 Zenit-2 No. 18NI Stage 2      rocket_body     797-812    9000  1.00  1.62e-02      145  27.6-224
   3  27386 Envisat                       payload         760-762    7911  1.00  1.81e-02      143  19.1-541
```

`M`, `L` and `Pc` are the factors of the product, and `R` is their result. `range` is the uncertainty interval for `R`. The [scoring model reference](../reference/scoring-model.md) defines each factor.

## 2. Restrict the ranking to derelicts

Most of the risk sits in objects nobody is controlling. Limit the pool to derelicts:

```console
$ uv run sdc catalogue rank --pool derelict --top 5
```

The derelict pool has 2,845 objects. `--pool` also accepts `rocket_body` and `all`.

## 3. Compare with a random choice

The question that matters for a removal programme is not which objects are risky, but how much better targeting does. Run:

```console
$ uv run sdc catalogue compare --k 10
pool         derelict (2845 objects), k = 10, 10000 random draws
targeted dR  1409  [239.5 - 2495]
random dR    median 17.53, 95th percentile 149.3
ratio        80.4x the median random set
beaten       99.5% of random draws fall below the targeted conservative bound
```

Removing the ten highest-R derelicts gives about 80 times the median risk reduction of removing ten at random. The "beaten" line counts the random draws that fall below the targeted conservative bound, which is the lower end of its range.

## 4. Check the model

```console
$ uv run sdc catalogue backtest
404 reentered rocket bodies; predicted range holds the actual lifetime for 96%
median predicted/actual 1.08; within x2 42%
```

The lifetime model is tested against 404 rocket bodies that have already reentered. The predicted range contains the true lifetime for 96% of them.

## What you have learned

- Risk is a product of mass, lifetime and collision probability, and each factor has an uncertainty range.
- A few objects carry most of the risk, so targeting pays off.
- The model is checked against outcomes it has not seen.

Next, look up the commands in the [CLI reference](../reference/cli.md), or try the how-to on [comparing removal strategies](../how-to/compare-removal-strategies.md).
