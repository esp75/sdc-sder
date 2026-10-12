# Space Debris Credits: A Market-Based Framework for Governance and Environmental Stewardship in Orbit

Maxime Kadri and Anna Shishkina · Strauss Center Space Traffic Conference 2026, The University of Texas at Austin

- [PDF as presented](kadri-shishkina-2026-space-debris-credits.pdf), 11 pages. SHA-256 `fa0bc210e9eec1a6b82f1573b331ab7874be7f1166d19ce1b5d14a10a02d598a`
- [Markdown edition](paper.md)

## Contribution in brief

1. **Construct 1, the Space Debris Credit.** An outcome-linked unit representing a *verified reduction in long-term debris risk relative to a stated baseline*. Only a small set of action classes are eligible, each with high verification confidence: post-mission disposal, controlled reentry, passivation, active debris removal, and servicing that enables disposal.
2. **Construct 2, the Space Debris Exposure Rating.** A minimum viable proxy that scales obligations in proportion to a mission's predicted contribution to long-lived risk.
3. **Action → outcome model.** For each object *i*, the risk proxy is $R_i = M_i \times L_i \times Pc_i$, where *M* is mass, *L* is persistence over a horizon and *Pc* is the probability of collision. The expected risk reduction of an action is $\Delta R(a) = \sum_i (R_{i,\text{before}} - R_{i,\text{after}})$. Credits are issued relative to a reference unit $\Delta R_0$.
4. **Integrity.** A public rulebook, independent accredited verification, a registry with unique identifiers, disputes and transparency. None of these depends on a particular technology.
5. **Legal feasibility.** Consent pathways under OST Article VIII and the Liability Convention, starting with objects under domestic jurisdiction.
6. **Evidence plan.** A falsifiable pilot design and a checklist.

## Where it lives in this repository

| Paper | Implementation or extension |
|---|---|
| §5, Table 2 (SDER inputs) | [`src/sder`](../../src/sder/): engine that accounts for evidence quality, with a [methodology file](../../src/sder/methodology/research-v0.1.yaml); [WP-02](../wp-02-sder-methodology/README.md) |
| §6 (R = M × L × Pc, ΔR) | [`src/sdc/risk.py`](../../src/sdc/risk.py), `sdc delta-r`; [WP-02](../wp-02-sder-methodology/README.md) |
| §4, §7 (lifecycle, verification, double counting) | [`src/sdc/registry.py`](../../src/sdc/registry.py); [WP-03](../wp-03-claim-integrity/README.md) |
| §9 (legal pathways) | [WP-01](../wp-01-legal-pathways/README.md) |
| §7, §14–16 (rulebook, pilot, governance) | [Rulebook consultation draft v0.2](../../spec/rulebook-v0.2-consultation-draft.md) |

## Known limitations, as stated in the paper

- Figures 2–3 use synthetic illustrative values. Producing the same figures from catalogue data is the first item on the [research roadmap](../ROADMAP.md).
- The mass estimate *M*, the probability of collision *Pc* and the persistence *L* are proxies that carry uncertainty from the data sources and from solar activity.
- The framework does not address debris smaller than 10 cm directly.

## Cite

> Kadri, M., & Shishkina, A. (2026). *Space Debris Credits: A Market-Based Framework for Governance and Environmental Stewardship in Orbit.* Strauss Center Space Traffic Conference 2026, The University of Texas at Austin.

© 2026 Maxime Kadri and Anna Shishkina. Licensed under CC BY 4.0.
