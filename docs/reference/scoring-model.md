# Reference: scoring model

This page lists the fields, enums, weights and formulas used by the code. The authoritative values live in the method file, `src/sder/methodology/research-v0.2.yaml`. Its SHA-256 is stamped on every assessment. Print it with `uv run sder methodology`.

> **Status:** method v0.2 calibrates the persistence and environment tables from open data. The other values are placeholders for consultation and are not a standard.

## Score

A score is a weighted sum of seven component risks. Each component risk runs from 0 (best) to 100 (worst).

$$\text{score} = \sum_{c} w_c \cdot \text{risk}_c$$

Each component carries a range, and the total carries one too. Bands are read from the total:

| Band | Score |
|---|---|
| `low` | below 34 |
| `medium` | 34 to below 67 |
| `high` | 67 and above |

`band_is_certain` is `false` when the interval crosses a band boundary.

**Withholding.** If inputs with more than 30% of the total weight are missing, the score is withheld rather than estimated (`withhold_if_missing_weight_above: 0.3`). Missing inputs that are below that threshold are scored at worst case and named in the output.

## Components

| Component | Weight | Inputs | Table in method v0.2 |
|---|---|---|---|
| `disposal` | 0.250 | `disposal_plan`, `disposal_reliability` | Plan risk: `controlled_reentry` 0, `reentry_within_5y` 10, `reentry_within_25y` 40, `graveyard_orbit` 30, `none` 100 |
| `orbital_persistence` | 0.200 | `mean_altitude_km`, `mass_kg` | Natural-decay lifetime by altitude, from 200 km (0.003 years) to 2,000 km (45,800 years). Saturates at 1,000 years. |
| `environment` | 0.150 | `mean_altitude_km` | Relative spatial density per 50 km shell, log-scaled (100 = densest shell) |
| `conjunction` | 0.150 | `min_miss_distance_km`, `relative_speed_km_s` | Characteristic distance 2.0 km, reference speed 10 km/s, minimum speed factor 0.3 |
| `consequence` | 0.100 | `mass_kg` | Saturates at 10,000 kg |
| `passivation` | 0.075 | `passivation` | `full` 0, `partial` 50, `none` 100 |
| `maneuverability` | 0.075 | `maneuverability` | `propulsive` 0, `drag_device` 40, `none` 100 |

The weights sum to 1.0.

## Inputs

Every input is an object with three parts:

```yaml
mass_kg: {value: 150, evidence: verified, source: "launch manifest"}
```

| Field | Type | Meaning |
|---|---|---|
| `value` | number or enum, or absent | The value. Absent means missing. |
| `evidence` | enum | How the value is known. See below. |
| `source` | string, optional | A reference to the supporting record. |

### Evidence classes

From strongest to weakest:

| Class | Meaning | Uncertainty |
|---|---|---|
| `verified` | Backed by a verified record | Narrowest |
| `independently_observed` | Measured by a third party, such as a public catalogue | |
| `modeled` | Computed from a model and stated inputs | |
| `operator_statement` | Claimed by the operator, without independent check | Widest |

The uncertainty width for each class is set under `evidence_uncertainty` in the method file. Weaker evidence always gives a wider range.

### Enums

- `disposal_plan`: `controlled_reentry`, `reentry_within_5y`, `reentry_within_25y`, `graveyard_orbit`, `none`
- `passivation`: `full`, `partial`, `none`
- `maneuverability`: `propulsive`, `drag_device`, `none`

Run `uv run sder schema` for the JSON Schema of the mission and assessment files.

## Risk product

For each object, the risk proxy is

$$R = M \times L \times Pc$$

where $M$ is mass in kilograms, $L = \min(1, T/H)$ is the fraction of the horizon $H$ that the object spends in orbit, with $T$ its lifetime, and $Pc$ is the collision probability over $H$. $L$ is bounded at 1, so an object that outlives the horizon contributes its full mass. $Pc$ comes from kinetic gas theory, using the catalogue's own spatial density (see [WP-04](../../papers/wp-04-catalogue/README.md)).

The reduction from an action, summed over the objects it changes, is

$$\Delta R(a) = \sum_i \left(R_{i,\text{before}} - R_{i,\text{after}}\right)$$

ΔR is additive across objects. Units are counted from the conservative (lower) bound of ΔR, so an uncertain estimate never inflates them. The reference value `dR0` sets how much ΔR one unit represents, and it is set with `--reference-unit`.

## Limits

These are stated in the output, not hidden:

- The score is **illustrative research output**, not an official SDER rating.
- Parameters marked as placeholders in the method file have not been calibrated.
- ΔR is a risk proxy in kg-equivalent units, not a physical quantity.

See [how SDER works](../explanation/how-sder-works.md) for the reasoning behind these choices.
