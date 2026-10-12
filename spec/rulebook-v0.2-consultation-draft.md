# SDC and SDER Rulebook: consultation draft v0.2

**Status:** consultation draft. It is not in force and no one has adopted it. No SDER rating or SDC has been issued under it.
**Version:** v0.2 · 12 October 2026 · SDC Institute (in formation)
**Builds on:** [Vision and Principles v0.1](vision-and-principles-v0.1.md); Kadri & Shishkina (2026), [*Space Debris Credits*](../papers/2026-strauss-sdc-framework/README.md); working papers [WP-01](../papers/wp-01-legal-pathways/README.md), [WP-02](../papers/wp-02-sder-methodology/README.md) and [WP-03](../papers/wp-03-claim-integrity/README.md).
**License:** © 2026 Maxime Kadri. [CC BY-SA 4.0](../LICENSES/CC-BY-SA-4.0.txt). Using this text does not imply endorsement or certification. See [TRADEMARKS.md](../TRADEMARKS.md).

## How to read this draft

Each rule is presented in three parts:

- **Rule:** the proposed text.
- **Why:** the rationale and its source.
- **Open:** choices this draft deliberately leaves to consultation.

Rules marked ⚙︎ are implemented in the reference code. The code's tests act as executable checks of the rule.

This draft replaces earlier internal drafts written in 2025, which were never published (see [ORIGIN.md](../ORIGIN.md)). Those drafts assumed a blockchain token, a marketplace with fees, oracle staking and a decentralised governance body. **This draft assumes none of these.** Whether credits may be traded at all is an open policy question (Part F).

---

## Part A: General provisions

**A1 Purpose and scope.**
- *Rule.* This Rulebook defines how a mission's debris exposure may be described (SDER) and how a verified reduction in long-lived debris risk may be recorded as a claim (SDC). It covers objects in Earth orbit and the operators, servicers and launching States associated with them.
- *Why.* Kadri & Shishkina (2026, §1): a framework that does not link action to measurable outcome will not change behaviour.

**A2 Definitions.**
- **Object:** a catalogued space object identified by its COSPAR or NORAD identifier.
- **Risk proxy $R_i$:** $M_i \times L_i \times Pc_i$, where $M$ is mass, $L$ is persistence over the horizon $H$ and $Pc$ is collision probability over $H$ (paper §6). It is a proxy, not a probability of catastrophe.
- **Action:** an operation that changes one or more terms of $R$ for one or more objects.
- **ΔR:** the expected risk reduction of an action, $\sum_i (R_{i,\text{before}} - R_{i,\text{after}})$.
- **Reference unit $\Delta R_0$:** the reduction represented by one SDC unit.
- **Baseline:** what would likely have happened without the action, including every applicable legal requirement.
- **Claim:** a request to record an outcome as an SDC, with its unit definition, baseline and evidence.
- **Evidence class:** one of `verified`, `independently_observed`, `modeled` or `operator_statement`.

**A3 Roles.**
- **Operator:** the entity responsible for an object.
- **Claimant:** the entity asserting an outcome, who may also be the operator or a servicer.
- **Verifier:** an accredited entity, independent of the claimant.
- **Administrator:** keeps the rules and the registry.
- **Data provider:** supplies tracking or catalogue data.
- **Review group:** independent experts who challenge methods (see Part G).
- **Licensing authority:** the State body that authorises and supervises activities under OST Art. VI.
- *Why.* Paper §15 sets out four functions: rulemaking, verification governance, registry administration, and reporting and review.
- *Open.* Whether the four functions sit in one administrator during a pilot.

**A4 Relationship to law.**
- *Rule.* Nothing in this Rulebook overrides the jurisdiction and control of the State of registry, the liability regime, or national licensing law. The administrator publishes rules, verifies outcomes and keeps the record. It holds no enforcement power.
- *Why.* [WP-01](../papers/wp-01-legal-pathways/README.md) §2 and §6; paper §16.6.

---

## Part B: Space Debris Exposure Rating (SDER)

**B1 Purpose and limits.**
- *Rule.* An SDER assessment describes a mission's exposure across its lifecycle under a published method version. It is not a ranking of operators. No league tables are published until coverage, peer review, correction and appeal processes are working.
- *Why.* Vision & Principles, SDER 1 and 5.

**B2 Inputs.**
- *Rule.* A method version lists its inputs. The minimum set covers:
  - orbital regime and persistence;
  - mass and cross-section;
  - disposal plan and reliability;
  - passivation;
  - maneuverability and coordination;
  - conjunction exposure.
- *Why.* Paper §5 and Table 2.
- *Open.* Whether to include inclination, area-to-mass ratio, mission duration and design-for-demise, which are listed in Table 2 but not yet implemented. Compliance history is excluded until appeals exist ([WP-02](../papers/wp-02-sder-methodology/README.md) §5).

**B3 Evidence classes.** ⚙︎
- *Rule.* Every input carries an evidence class and a source reference. A component takes the class of its weakest input, and a weaker class widens the component's uncertainty interval.
- *Why.* SDER 2–3.

**B4 Missing data.** ⚙︎
- *Rule.* A missing input is never replaced by a favourable value. It is scored at its worst case and named in the output. The result is *indicative* when nothing is missing and *provisional* when the missing weight is at or below a published threshold. Above that threshold the result is *withheld*.
- *Why.* SDER 4.
- *Open.* The threshold. It is 0.30 in research method v0.1.

**B5 Uncertainty and bands.** ⚙︎
- *Rule.* Every result gives a point estimate and an interval. A band (low, medium or high) is reported together with whether the interval lies entirely inside it.
- *Why.* SDER 3. A single score must not look more certain than its inputs.

**B6 Method versions.** ⚙︎
- *Rule.* Weights, tables and thresholds are published as a versioned method file. Each assessment records the method's identifier and its SHA-256. A new version never changes the meaning of a past assessment.
- *Why.* SDER 7; paper §16.1.

**B7 Disclosure, correction and appeal.**
- *Rule.* An assessed operator receives the inputs, the evidence classes and the rationale for each component. The operator may submit corrected evidence, and may appeal to a panel that took no part in the assessment.
- *Why.* SDER 6; paper §16.2.

---

## Part C: Space Debris Credit (SDC)

**C1 Unit.**
- *Rule.* One SDC unit represents a verified reduction of $\Delta R_0$ in the risk proxy over a stated horizon, relative to a stated baseline. The number of units for an action is calculated from the **conservative bound** of ΔR, meaning the lowest reduction consistent with the evidence, rounded down. ⚙︎
- *Why.* SDC 1; paper §6. Uncertainty may only reduce what is issued.
- *Open.* How $\Delta R_0$ is set: fixed by the review group, or a percentile of observed ΔR over a calibration period (paper §6). Also, the horizon $H$ for each regime.

**C2 Eligible action classes.** ⚙︎ (`OutcomeType`)
- *Rule.* Only the following classes are eligible during a pilot:

| Class | Baseline | Minimum evidence |
|---|---|---|
| `early_deorbit`: post-mission disposal beyond the applicable rule | the applicable national rule, otherwise the IADC guideline | independent orbit history; operator maneuver logs; tracking confirmation of decay or disposal orbit |
| `controlled_reentry` | uncontrolled decay | reentry prediction and maneuver telemetry; independent confirmation of decay and disappearance; reentry notice where applicable |
| `passivation` at end of life | no passivation | operator passivation report; telemetry of tank pressures and battery states; audit sampling; monitoring for absence of break-up |
| `active_removal` of an intact derelict | object remains in its shell | independent tracking before and after; rendezvous evidence; change in the catalogue; audit of identity linkage; consent (C6) |
| `servicing_enabled_disposal` | object remains persistent | servicer telemetry and tracking; capability evidence before and after; disposal confirmation |

- *Why.* Paper §4 and Table 1. Each class must change a risk-relevant state variable *and* be verifiable from independent data.
- *Open.* Collision-avoidance maneuvers are excluded. They are routine practice, and the counterfactual cannot be verified.

**C3 Baselines.**
- *Rule.* Baselines are versioned by jurisdiction and by date. Doing what the law requires earns no units. Only performance beyond the applicable requirement is credited.
- *Why.* SDC 2; [WP-01](../papers/wp-01-legal-pathways/README.md) §4. For example, the FCC five-year disposal rule makes a 25-year baseline too lenient for systems it covers.

**C4 Moral-hazard safeguards.**
- *Rule.* Disposal credits apply only to performance beyond the baseline. Legacy-removal credits are restricted to objects launched before the scheme, or to removals by an entity other than the original operator acting under explicit consent. Newly launched objects become eligible for disposal credits only after a waiting period.
- *Why.* Paper §8: "Paying for cleaning your own room can create moral hazard if it rewards the creation of risk."
- *Open.* The length of the waiting period.

**C5 Evidence.**
- *Rule.* A claim lists references to its evidence. Evidence covered by confidentiality may be held by the verifier, but the registry publishes a commitment to it (a hash) and the verifier's finding.
- *Why.* Paper §16.3.

**C6 Consent and liability.**
- *Rule.* An action on an object outside the claimant's domestic jurisdiction is eligible only with documented consent from the State of registry. Before recognition, the claimant shows how liability is allocated between servicer, State of registry and licensing State.
- *Why.* OST Art. VIII; Liability Convention Art. III; [WP-01](../papers/wp-01-legal-pathways/README.md) §5–6.

**C7 Lifecycle.** ⚙︎ (`ClaimState`, `TRANSITIONS`)
- *Rule.* A claim moves only along these transitions:
  - `claimed` → `under_review` or `rejected`
  - `under_review` → `verified` or `rejected`
  - `verified` → `issued` or `revoked`
  - `issued` → `retired` or `revoked`
  - `retired` → `revoked`
  - `rejected` and `revoked` are final.
- *Why.* [WP-03](../papers/wp-03-claim-integrity/README.md) §2. A correction must remain possible even after retirement.

**C8 Uniqueness.** ⚙︎
- *Rule.* Only one non-void claim may exist for a given (object identifier, outcome type). Within one action, an object may appear only once. Credits go to a single accountable entity, typically the operator under the authorising State. A service provider may receive the economic value by contract, but the registry still records only one issuance for the physical event.
- *Why.* SDC 4; paper §7.
- *Open.* How to prevent the same outcome being claimed in another scheme. Cross-registry identifiers are one route.

**C9 Retirement.** ⚙︎
- *Rule.* Retirement is one-way and records who retired the unit.
- *Why.* Paper §4.

**C10 Reversal.** ⚙︎
- *Rule.* `reject` and `revoke` require a public reason. If a recorded outcome proves false, for example because an object reported as reentered is re-acquired by tracking, the claim is revoked and the revocation is published.
- *Why.* SDC 4; [GOVERNANCE.md](../GOVERNANCE.md).

---

## Part D: Verification

**D1 Accreditation and independence.** ⚙︎ (partly)
- *Rule.* Verifiers are accredited against published criteria: technical competence, independence and data handling. A verifier must not be the claimant and must declare conflicts. The registry refuses a conflicted assignment. Only the assigned verifier may record verification.
- *Why.* SDC 3; paper §16.2.

**D2 Several sources and audit triggers.**
- *Rule.* Wherever possible, an outcome is confirmed by at least two independent data sources, for example two tracking networks, or tracking plus operator telemetry. If the sources disagree, or the confirmation threshold is not met, a third-party audit starts automatically.
- *Why.* [WP-03](../papers/wp-03-claim-integrity/README.md) §6, items 1–2.
- *Open.* The confirmation threshold for each action class.

**D3 Quality control.**
- *Rule.* The administrator rotates verifiers, peer-reviews a sample of verifications and re-audits a random sample. Part of the verification fees may fund this work.
- *Why.* Paper §16.2. Auditors paid by participants need structural checks.

**D4 Disputes and appeals.**
- *Rule.* A dispute panel combining technical and legal expertise operates under published procedures and timelines. When disputes show that a rule is systematically ambiguous, the rule is clarified in the next method cycle.
- *Why.* Paper §16.2.

---

## Part E: Registry and transparency

**E1 Records.** ⚙︎
- *Rule.* The registry records every event: submission, verifier assignment, verification, rejection, issuance, retirement and revocation. Each record carries a sequence number, a timestamp, the actor and the payload.
- *Why.* Paper §7.

**E2 Tamper evidence.** ⚙︎ (partly)
- *Rule.* The registry is an append-only log in which each entry carries the hash of the previous one. When the log is opened, it is replayed and re-checked against these rules. The head hash is published on a schedule in at least one location the administrator does not control.
- *Why.* [WP-03](../papers/wp-03-claim-integrity/README.md) §4. Anchoring the head hash is not yet implemented.

**E3 Public reporting.**
- *Rule.* The administrator publishes aggregate outcomes, including total ΔR retired. It also publishes methods, anonymised verification statistics (time, cost, dispute rate) and uncertainty ranges for key parameters. Sensitive operational details are not published.
- *Why.* Paper §13 and §16.3.

---

## Part F: Policy instruments (options, not premises)

**F1 Instrument choice.**
- *Rule.* This Rulebook does not presuppose a market. Recorded outcomes may serve any of the following:

| Instrument | How a recorded SDC or SDER is used | Main risk |
|---|---|---|
| Voluntary retirement | Operators or purchasers retire units to support claims of stewardship | Weak demand; greenwashing if claims are loose |
| Licensing obligation | Authorities require exposure disclosure and retirement in proportion to the rating in defined shells | Needs a legal basis in each jurisdiction |
| Deposit or bond | A bond is refunded on verified disposal, and a forfeited bond funds remediation | Calibration; legacy objects are not covered |
| Orbital-use fee | The rating informs a fee on congestion (Rao et al. 2020) | Harmonisation; operators move to permissive jurisdictions |
| Procurement or insurance criterion | Buyers and insurers reward low exposure and retired units | Uneven coverage |

- *Why.* Vision & Principles SDC 5; paper §12.
- *Open.* Whether units may ever be transferred. If they may, transfer rules, holder disclosure and measures against manipulation are needed before any transfer is allowed.

**F2 Shared infrastructure and equity (option).**
- *Rule.* If the scheme is funded, a published share may support verification for smaller operators, capacity building for emerging space actors, and open research on methods. This support is governed separately from issuance decisions, and its budgets and grants are published.
- *Why.* Paper §11 and §16.4.

---

## Part G: Governance and change

**G1 Rule changes.**
- *Rule.* Changes follow [GOVERNANCE.md](../GOVERNANCE.md):
  - a proposal with rationale and sources;
  - at least 30 days of comment for substantive changes;
  - a published decision with reasons;
  - versioned effect, so a change never applies retroactively.
- The cadence is annual, with an emergency route for safety-critical corrections.
- *Why.* Paper §16.1, where rule drift is named as a central failure mode.

**G2 Review group.**
- *Rule.* An independent expert group is drawn from operators, insurers, regulators and independent researchers, with conflicts declared. It proposes method updates. Voting rules prevent any one class of participant from dominating.
- *Why.* Paper §16.1; Vision & Principles, "Governance proposed for the Institute".

**G3 Originator.**
- *Rule.* The originator and any affiliated organisation may implement the method. They may not assess or certify their own missions or claims, chair the review group permanently, or veto a method.
- *Why.* Vision & Principles SDER 6; [DISCLOSURES.md](../DISCLOSURES.md).

---

## Part H: Pilot design

A first pilot should:

1. Publish this Rulebook with a small set of eligible classes (C2) and clear baselines (C3).
2. Select one or two shells where persistence and density justify the focus, and publish the shell definitions.
3. Accredit a small number of verifiers and publish their criteria.
4. Run the registry (Part E) with public aggregate reporting.
5. Run one compliance cycle with a fixed retirement date, and publish total ΔR retired.
6. Measure the cost, time, dispute rate and sufficiency of verification.
7. Require a documented consent pathway for any object outside domestic jurisdiction.
8. Publish the method update cadence and the review process.

If verification turns out to be affordable and operators change their behaviour, the constructs pass an initial credibility threshold. If not, the evidence will show what to simplify or redesign (paper §14).

---

## Annex: rule-to-code map

| Rule | Code | Test |
|---|---|---|
| B3–B6 | [`src/sder/engine.py`](../src/sder/engine.py), [`research-v0.1.yaml`](../src/sder/methodology/research-v0.1.yaml) | [`tests/test_sder_engine.py`](../tests/test_sder_engine.py) |
| C1 | [`src/sdc/risk.py`](../src/sdc/risk.py) (`issuable_units`) | [`tests/test_sdc_risk.py`](../tests/test_sdc_risk.py) |
| C2, C7 | [`src/sdc/models.py`](../src/sdc/models.py) (`OutcomeType`, `TRANSITIONS`) | [`tests/test_sdc_registry.py`](../tests/test_sdc_registry.py) |
| C8–C10, D1, E1–E2 | [`src/sdc/registry.py`](../src/sdc/registry.py) | [`tests/test_sdc_registry.py`](../tests/test_sdc_registry.py) |

## Consultation questions

1. Is $R = M \times L \times Pc$ a sufficient proxy for a pilot, or should the consequence term be replaced at once by a fragment-based metric such as ECOB?
2. How should $\Delta R_0$ be set so that units stay comparable across regimes?
3. Which evidence can be public without compromising operator confidentiality or security?
4. What waiting period (C4) prevents missions from being designed to earn credits?
5. Should transfer of units ever be permitted (F1)?

Please respond using the [consultation template](consultation-template.md).
