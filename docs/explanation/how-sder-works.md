# Explanation: how SDER works

SDER, the Space Debris Exposure Rating, answers one question: how much debris exposure does a mission carry, and how sure are we? This page explains the design choices behind the answer. For exact fields and formulas, see the [scoring model](../reference/scoring-model.md).

## Why a weighted sum, with intervals

A mission's exposure depends on several things at once: how it leaves orbit, how long it would stay if it did not, how crowded its shell is, how likely it is to collide, how much it would break up, whether it can be passivated, and whether it can manoeuvre. SDER scores each of these on a 0–100 risk scale and combines them with fixed weights. The weights are public and versioned.

A single number would hide how much of the answer is known. So every component, and the total, carries an interval, and the output says whether the band is certain. A mission can read `low (band uncertain)`, which means the evidence does not yet settle the band.

## Why evidence labels change the answer

The principles require distinguishing four kinds of evidence: operator statements, independent observations, verified records and model estimates. SDER does not treat them as equal. Each input is labelled with its evidence class, and the class sets how wide its uncertainty is. Weaker evidence gives a wider range, so the score is more cautious where the operator has not been checked.

The sensitivity analysis then shows which input dominates the uncertainty. In the worked example in [Tutorial 1](../tutorials/01-score-a-mission.md), the disposal plan accounts for 75% of the variance because it is only an operator's statement. Improving that one input gives the largest gain in confidence. The model points to the evidence that matters, rather than the number that looks worst.

## Why missing data is not forgiven

Two rules stop a score from improving by omission:

- A **missing input is scored at worst case**, and it is named in the output.
- If missing inputs carry more than 30% of the total weight, the **score is withheld**, not estimated.

Without these rules, an operator could raise a score by leaving inputs out.

## Why the method is versioned and hashed

Every assessment is stamped with the SHA-256 of the method file it used. Compare scores only within one method version, and the hash makes the version visible. Method v0.1 used placeholder tables. Method v0.2 replaces two of them with values calibrated from open data. Both are kept in the repository, so the change can be inspected.

## Where the risk product comes from

The catalogue ranking uses a different, narrower quantity: R = M × L × Pc. It is a risk proxy, not a score, and it is used to find which objects matter most. Its factors are:

- **M**, the mass of the object.
- **L**, the fraction of the horizon the object spends in orbit, capped at 1.
- **Pc**, the collision probability, from kinetic gas theory and the catalogue's own spatial density.

Removing an object's contribution gives a reduction in risk, ΔR. ΔR is additive, so the value of a set of removals is the sum over its members. That additivity is what makes targeting meaningful. Removing the ten highest-R derelicts gives about 80 times the median risk reduction of removing ten at random.

## What the model cannot do

The authors' own paper states the limits, and the code repeats them in its output:

- The weighted sum rates a 1.3 kg cubesat in the same band as a 9-tonne rocket stage. WP-04 reports this as a weakness of the weighted sum.
- Method v0.2 calibrates only two tables. The other parameters are placeholders until an independent review.
- The score is illustrative research output. It is not an official SDER rating.

## Further reading

- [WP-02: SDER and ΔR, reference methodology](../../papers/wp-02-sder-methodology/README.md)
- [WP-04: ranking LEO objects by R](../../papers/wp-04-catalogue/README.md)
- [Vision and Principles v0.1](../../spec/vision-and-principles-v0.1.md)
- [Claim integrity](claim-integrity.md), for how removals are recorded and verified
