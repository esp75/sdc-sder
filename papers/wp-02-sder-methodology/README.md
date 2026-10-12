# SDER and ΔR: a reference methodology, its implementation and its limits

| | |
|---|---|
| **Series** | SDC Institute Working Paper SDC-WP-2026-02 |
| **Version** | 0.1, 12 October 2026 |
| **Author** | Maxime Kadri, SDC Institute (in formation) |
| **Status** | Working paper. Not peer reviewed. All parameters are uncalibrated placeholders. |
| **Extends** | Kadri & Shishkina (2026), §5, §6 and §13 |
| **Code** | [`src/sder`](../../src/sder/), [`src/sdc/risk.py`](../../src/sdc/risk.py), method file [`research-v0.1.yaml`](../../src/sder/methodology/research-v0.1.yaml) |
| **Competing interests** | See [DISCLOSURES.md](../../DISCLOSURES.md) |
| **Funding** | None |
| **Data availability** | Examples and expected outputs are in [`examples/`](../../examples/). Everything here can be reproduced with `uv run sder score` and `uv run sdc delta-r`. |
| **License** | [CC BY 4.0](../../LICENSES/CC-BY-4.0.txt) |

## Abstract

Kadri & Shishkina (2026) propose two quantitative constructs. One is a mission-level **Space Debris Exposure Rating (SDER)** built as a weighted sum of a few normalised factors. The other is an object-level risk proxy $R_i = M_i \times L_i \times Pc_i$, whose change $\Delta R$ is meant to size outcome-based credits. This paper documents an open, tested reference implementation of both. Its central design choice is that **evidence quality and missing data are part of the output, not hidden inside it**. Each input carries an evidence class. Weaker evidence widens the uncertainty interval. A missing input is scored at its worst case, and a result with too much missing weight is withheld. Credits are counted from the conservative bound of $\Delta R$. We describe the method, state which parts of the paper's Table 2 it covers, position it against existing indices (the Space Sustainability Rating, ECOB, CSI and the "50 most concerning" list), and set out what calibration and validation it still needs. No parameter in v0.1 is calibrated, and every output is labelled as illustrative.

## 1 Two constructs, two scales

The two constructs answer different questions.

- **SDER** asks how much long-lived debris exposure a *mission* creates over its lifecycle, given what is known about it. It works at mission level and looks forward. It is meant to scale obligations.
- **ΔR** asks how much an *action* reduced the risk contributed by specific *objects*. It works at object level, compares before and after, and is meant to size a credit.

They share a data layer (altitude, mass, disposal and conjunction information) but are computed separately. This keeps the uncertainty of one out of the other.

## 2 SDER reference method v0.1

### 2.1 Components

The engine ([`engine.py`](../../src/sder/engine.py)) computes seven component risks on a 0–100 scale, with higher meaning more exposure. It then combines them with the weights in the method file.

| Component | Weight | Inputs | Placeholder formula | Paper Table 2 input |
|---|---|---|---|---|
| Disposal | 0.25 | plan, reliability | residual risk by plan, weighted by reliability; a failed disposal counts as 100 | Predicted time to disposal |
| Orbital persistence | 0.20 | mean altitude | log-scaled natural-decay lifetime from an altitude table | Altitude; orbital regime |
| Environment | 0.15 | mean altitude | congestion score by altitude band | Orbital regime or protected shell |
| Conjunction | 0.15 | closest miss distance, relative speed | $100\,e^{-d/2\,\text{km}}$ times a speed factor | (coordination burden) |
| Consequence | 0.10 | mass | log-scaled mass up to 10,000 kg | (mass and area) |
| Passivation | 0.075 | level | full 0 / partial 50 / none 100 | Passivation status |
| Maneuverability | 0.075 | capability | propulsive 0 / drag device 40 / none 100 | Maneuverability and tracking transparency |

Four inputs in Table 2 are **not yet implemented**: inclination, area-to-mass ratio, mission duration and design-for-demise. A fifth, compliance history, is deliberately left out. Section 5 explains the second choice.

### 2.2 Evidence classes and uncertainty

Each input is an `Evidenced[T]` value made of a value, an evidence class and a source reference. From strongest to weakest, the classes are `verified`, `independently_observed`, `modeled` and `operator_statement`. A component takes the evidence class of its *weakest* input. That class sets the half-width of the component's interval: ±5, ±10, ±20 or ±30 points respectively. The total interval is the weighted sum of the component intervals. The output reports the band (low below 34, medium below 67, high otherwise) and states whether it is *certain*, meaning the whole interval falls inside one band.

These widths encode a policy choice, not an empirical error model. Their purpose is to make "we only have the operator's word" visible in the result. Replacing them with error distributions estimated per data source is a calibration task (§6).

### 2.3 Missing data

A missing input never takes a favourable default. The affected component scores 100, with an interval of [0, 100], and the input is named in the output. The result is *indicative* when nothing is missing. It is *provisional* when the missing weight is 0.30 or less, and *withheld* above that. A Hypothesis property test checks that removing any single input never lowers the score ([`tests/test_sder_engine.py`](../../tests/test_sder_engine.py)). During development, that test found a real defect: a missing relative speed had narrowed the interval instead of widening it.

### 2.4 Versioning

Weights and tables live in a YAML method file, not in code. Every assessment records the method's identifier and the SHA-256 of the file, so a later change cannot silently alter the meaning of an earlier result. This implements principle 7 of the [Vision and Principles](../../spec/vision-and-principles-v0.1.md) and §16.1 of the paper.

### 2.5 Worked examples

| Example | Score [interval] | Band | Status |
|---|---|---|---|
| [Responsible LEO smallsat](../../examples/leo-smallsat-responsible.yaml), 550 km, propulsive, disposal plan stated only by the operator | 27.7 [20.1–45.2] | low (uncertain) | indicative |
| [Derelict upper stage](../../examples/leo-derelict-upper-stage.yaml), 850 km, 1,400 kg, no disposal, no passivation | 91.9 | high (certain) | indicative |
| [Sparse operator claims](../../examples/sparse-operator-claims.yaml) | — | — | withheld |

The first row shows the intended behaviour. The smallsat's point score is low, but because its disposal plan rests only on the operator's word, its interval crosses into the medium band, and the output says so.

## 3 ΔR reference implementation

[`src/sdc/risk.py`](../../src/sdc/risk.py) implements §6 of the paper directly. For each affected object, an action supplies the terms before and after: mass $M$ (kg), persistence $L$ (the fraction of the horizon $H$ spent in a hazardous regime) and collision probability $Pc$ over $H$. An object that has been removed or has reentered has $R_{\text{after}} = 0$.

- **Intervals.** Every term is a range (low, value, high). All terms are non-negative, so $R^{\text{low}} = M^{\text{low}} L^{\text{low}} Pc^{\text{low}}$, and likewise for the high bound.
- **Conservative bound.** $\Delta R^{\text{low}} = \sum_i (R^{\text{low}}_{i,\text{before}} - R^{\text{high}}_{i,\text{after}})$. This is the smallest reduction consistent with the inputs.
- **Issuance.** The number of units is $\lfloor \max(0, \Delta R^{\text{low}}) / \Delta R_0 \rfloor$. Uncertainty can therefore only reduce what is issued, never increase it.
- **No double counting inside an action.** An action may list an object only once.

Property tests check four things. Removal never increases risk, at any bound. $\Delta R$ is additive across objects. Units never exceed the conservative bound. And under the proxy, removing the $k$ objects with the highest $R$ gives at least the $\Delta R$ of any other $k$-subset, which is the formal content of the paper's Figure 3 claim. With the illustrative inputs in [`examples/actions/`](../../examples/actions/), removing one ~8.9 t upper stage gives $\Delta R \approx 89$ (conservative bound 24). An early deorbit of a 150 kg smallsat gives $\Delta R \approx 0.18$ (conservative bound 0.024). The difference is about 500×, which illustrates the targeting argument of Liou et al. (2010) and Kadri & Shishkina (2026, §3).

## 4 Related work

| Index | Unit | What it measures | Relation to SDER and ΔR |
|---|---|---|---|
| **Space Sustainability Rating** (SSR) [ssr2021] | Mission and operator | A composite of six modules: mission index; collision avoidance; data sharing; detectability, identification and tracking; standards compliance; on-orbit servicing. Awarded in tiers. Operated by an independent Swiss association since its launch in 2022. | The closest existing analogue to SDER. SDER differs in two ways. Its evidence class and missing-data rules are part of the output, and its method file and code are open source. A comparison on the same missions is a priority (§6). |
| **ECOB** (Letizia et al. 2016) [letizia2016] | Object | How much a breakup would increase the collision probability of operational satellites, from an analytical model of fragment density. | A physically grounded candidate to replace the consequence and environment placeholders, and an alternative to $M \times Pc$ for ranking objects. |
| **Criticality of Spacecraft Index** (Rossi et al. 2015) [rossi2015csi] | Object | An analytic ranking of abandoned LEO objects by their physical characteristics, orbit and environment. | A cross-check for $R_i$ rankings. |
| **"50 statistically-most-concerning" objects** (McKnight et al. 2021) [mcknight2021] | Object | A consensus ranking of derelicts by statistical collision risk, built from several methods. | An external benchmark: a calibrated $R_i$ should place most of these objects in its top set. |
| **Mass × Pc target selection** (Liou et al. 2010) [liou2010] | Object | LEGEND simulations showing that ADR targets selected by mass times collision probability stabilise the LEO population at about five removals per year. | The empirical basis for the form $R = M \times L \times Pc$. |

## 5 Design decisions open to challenge

1. **A weighted sum versus physical aggregation.** The paper chose a parsimonious weighted sum because it is easy to read (§5). The cost is that weights are value judgements. Each weight in v0.1 is a placeholder. Any change needs a source and a sensitivity analysis.
2. **Compliance history is excluded.** Using past compliance as a rating input can lock in incumbents and penalise new entrants for reasons unrelated to the mission's physics. We leave it out until a procedure for appeals and corrections exists, in line with principle 5 (comparability with limits).
3. **Evidence widths are policy choices.** See §2.2.
4. **Persistence $L$ as a fraction of the horizon.** This keeps $R$ bounded and readable. It is less faithful to the physics than a lifetime integral weighted by flux.

## 6 Calibration and validation programme

These items are tracked in the [roadmap](../ROADMAP.md).

1. **Lifetime.** Replace the altitude table with a decay model that accounts for ballistic coefficient and solar-flux scenarios.
2. **Environment and Pc.** Replace the band scores and the single-miss-distance proxy with spatial density from public catalogues, and use a proper collision-probability method where conjunction data allow it.
3. **Consequence.** Replace log-mass with a fragment-generation estimate from the NASA Standard Breakup Model (Johnson et al. 2001) [johnson2001sbm], or with ECOB.
4. **Sensitivity.** Run Monte Carlo or Sobol analysis of the weights and bands, and publish how often a mission's band changes.
5. **Real data for the paper's Figures 2–3.** Rank intact LEO objects by $R_i$ from catalogue data, then compare the ΔR of targeted and random removal sets.
6. **External comparison.** Score missions that have published SSR results. Check whether objects on McKnight et al.'s list fall in the top set of $R_i$.

## 7 Limitations

All weights, tables and widths are uncalibrated. The method does not model debris smaller than 10 cm, in line with the paper's §11. Conjunction is represented by a single screening proxy. Outputs are **illustrative research scores**. They are not ratings and must not be presented as "SDER rated" (see [TRADEMARKS.md](../../TRADEMARKS.md)).

## References

Full entries are in [references.bib](../references.bib): `kadri2026sdc`, `liou2010`, `johnson2001sbm`, `letizia2016`, `rossi2015csi`, `mcknight2021`, `ssr2021`.
