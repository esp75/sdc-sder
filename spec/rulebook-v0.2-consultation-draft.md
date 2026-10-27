# SDC and SDER Rulebook: consultation draft v0.2

**Status:** consultation draft. It is not in force and no one has adopted it. No SDER rating or SDC has been issued under it.
**Version:** v0.2 · 12 October 2026 · SDC Institute (in formation)
**Builds on:** [Vision and Principles v0.1](vision-and-principles-v0.1.md); Kadri & Shishkina (2026), [*Space Debris Credits*](../papers/2026-strauss-sdc-framework/README.md); working papers [WP-01](../papers/wp-01-legal-pathways/README.md), [WP-02](../papers/wp-02-sder-methodology/README.md), [WP-03](../papers/wp-03-claim-integrity/README.md) and [WP-04](../papers/wp-04-catalogue/README.md).
**License:** © 2026 Maxime Kadri. [CC BY-SA 4.0](../LICENSES/CC-BY-SA-4.0.txt). Using this text does not imply endorsement or certification. See [TRADEMARKS.md](../TRADEMARKS.md).
**Also available as:** [PDF](rulebook-v0.2-consultation-draft.pdf) and an [interactive version](https://maximekadri.org/research/space-debris-credits/rulebook).

## How to read this draft

Each rule is presented in three parts:

- **Rule:** the proposed text.
- **Why:** the rationale and its source.
- **Open:** choices this draft deliberately leaves to consultation.

Rules marked ⚙︎ are implemented in the reference code. The code's tests act as executable checks of the rule. "Option" in a rule's title means the rule applies only if a jurisdiction or the scheme chooses that instrument.

The draft has ten Parts:

| Part | Covers |
|---|---|
| A | Purpose, definitions, roles, and the scheme's place in space law |
| B | The Space Debris Exposure Rating (SDER) |
| C | The Space Debris Credit (SDC): unit, eligibility, lifecycle |
| D | Verification, audit, compliance review and disputes |
| E | Registry and public reporting |
| F | Policy instruments that may use SDER and SDC |
| G | Governance and rule changes |
| H | The Equitable Space Access Fund (ESAF) |
| I | Phased implementation, national integration and international pathways |
| J | Outcome indicators and review |

**Relationship to the 2025 drafts.** This draft replaces internal drafts written in 2025, which were never published. Their policy content is carried over here: the definitions, the legal framework, the rating, verification and audit, governance, the Equitable Space Access Fund, and phased adoption. Their technical premises are not: a blockchain token, non-fungible disposal certificates, oracles that stake collateral, smart-contract enforcement, a decentralised governance body, and market-size projections. Where a 2025 parameter is kept as a starting point for consultation (for example the ESAF funding shares), it is labelled as such under *Open*.

---

## Part A: General provisions

**A1 Purpose and scope.**
- *Rule.* This Rulebook defines how a mission's debris exposure may be described (SDER) and how a verified reduction in long-lived debris risk may be recorded as a claim (SDC). Its purpose is to make the cost of leaving long-lived risk in orbit visible, and to give States, insurers and other buyers a common unit for paying for its reduction. It covers objects in Earth orbit and the operators, servicers and launching States associated with them. The activities in scope are launches, operations, end-of-life disposal, passivation and active removal.
- *Why.* Kadri & Shishkina (2026, §1): a framework that does not link action to measurable outcome will not change behaviour.
- *Open.* Whether lunar and cislunar orbits should later be covered by an annex.

**A2 Definitions.**

*Objects and risk*
- **Object:** a catalogued space object identified by its COSPAR or NORAD identifier.
- **Legacy object:** an object launched before the scheme's start date, or whose original operator no longer exists or no longer controls it.
- **Risk proxy $R_i$:** $M_i \times L_i \times Pc_i$, where $M$ is mass, $L$ is persistence over the horizon $H$ and $Pc$ is collision probability over $H$ (paper §6). It is a proxy, not a probability of catastrophe.
- **Horizon $H$:** the period over which persistence and collision probability are assessed. The research default is 25 years.
- **Action:** an operation that changes one or more terms of $R$ for one or more objects.
- **ΔR:** the expected risk reduction of an action, $\sum_i (R_{i,\text{before}} - R_{i,\text{after}})$.
- **Reference unit $\Delta R_0$:** the reduction represented by one SDC unit.

*Claims and evidence*
- **Baseline:** what would likely have happened without the action, including every applicable legal requirement.
- **Claim:** a request to record an outcome as an SDC, with its unit definition, baseline and evidence.
- **Evidence class:** one of `verified`, `independently_observed`, `modeled` or `operator_statement`.
- **Retirement:** the one-way use of an SDC unit to support an obligation or a public claim, after which it cannot be used again.

*Ratings and obligations*
- **SDER assessment:** a mission-level description of debris exposure under a published method version (Part B).
- **Obligation:** a requirement, set by a licensing authority or accepted voluntarily, to disclose an SDER assessment or to retire SDC units (Part F).
- **Quota:** an obligation expressed as a number of units to retire per period or per object launched (F3, an option).
- **Bonus–malus adjustment:** a change to an obligation according to an SDER band (F4, an option).

*Institutions and people*
- **Equitable Space Access Fund (ESAF):** the fund in Part H, which supports participation by emerging space actors and shared infrastructure.
- **Emerging space actor:** a State without an established national space agency or launch capability, or an organisation in such a State, or a first-time operator (H6 defines eligibility).
- **Verifier:** an accredited entity, independent of the claimant, that confirms outcomes (Part D).
- **Data provider:** a source of tracking, catalogue or telemetry data used as evidence, for example a national surveillance network or a commercial tracking provider.

**A3 Roles.**
- **Operator:** the entity responsible for an object.
- **Claimant:** the entity asserting an outcome, who may also be the operator or a servicer.
- **Verifier:** see A2.
- **Administrator:** keeps the rules and the registry (G4).
- **Data provider:** see A2.
- **Review group:** independent experts who challenge methods (G2).
- **ESAF board:** governs the fund (H3).
- **Licensing authority:** the State body that authorises and supervises activities under OST Art. VI.
- *Why.* Paper §15 sets out four functions: rulemaking, verification governance, registry administration, and reporting and review.
- *Open.* Whether the four functions sit in one administrator during a pilot.

**A4 Relationship to law.**
- *Rule.* Nothing in this Rulebook overrides the jurisdiction and control of the State of registry, the liability regime, or national licensing law. The administrator publishes rules, verifies outcomes and keeps the record. It holds no enforcement power.
- *Why.* [WP-01](../papers/wp-01-legal-pathways/README.md) §2 and §6; paper §16.6.

**A5 Legal and regulatory framework.** The scheme is designed to sit inside existing law. Each instrument below shapes one or more rules.

| Instrument | What it requires | How this Rulebook relates |
|---|---|---|
| Outer Space Treaty (1967), Art. VI | States bear international responsibility for national activities and must authorise and continually supervise non-governmental ones | Licensing authorities are the natural place to attach obligations (F1, I2). SDER disclosure and registry records can document supervision |
| OST Art. VII; Liability Convention (1972), Arts. II, III, V | Absolute liability for damage on Earth; fault-based liability in space; joint and several liability for joint launches | Claims involving proximity operations must allocate liability first (C6). Registry records may serve as evidence of due care, but the scheme does not change the liability regime |
| OST Art. VIII | The State of registry keeps jurisdiction and control; ownership is unaffected by being in space | Removal of another State's object needs that State's consent (C6). No abandonment or salvage is assumed |
| OST Art. IX | Due regard for the interests of other States; consultation before potentially harmful interference | Gives a treaty basis for treating long-lived objects in congested shells as a shared concern |
| Registration Convention (1975), Arts. II, IV | National registries and basic orbital data furnished to the UN | Identity layer for claims (C8). Registries may note disposal plans and recorded outcomes (E1) |
| IADC Space Debris Mitigation Guidelines, Rev. 4 (2025); COPUOS Space Debris Mitigation Guidelines (2007) | Limit released debris, prevent break-ups, dispose after mission, avoid collisions | Define the practices a baseline reflects (C3) and the factors SDER assesses (B2) |
| COPUOS LTS Guidelines (2019) | 21 voluntary guidelines, including information sharing and conjunction assessment | Support the data-sharing and transparency rules (D2, E3) |
| ISO 24113:2023 | Auditable debris mitigation requirements | Reference for evidence requirements (C2, D1) |
| FCC Second Report and Order 22-74 (2022) | Five-year post-mission disposal for LEO space stations licensed in, or seeking access to, the US; effective 9 September 2024 | Sets the baseline for systems it covers (C3) |
| France, Space Operations Act (2008) | Authorisation and technical regulations including end-of-life obligations | A national baseline (C3) |
| Proposed EU Space Act, COM(2025) 335 | Debris mitigation plans at authorisation, collision-avoidance capability for constellations, an EU legal representative for non-EU operators; full application proposed from 1 January 2030. Still in the legislative procedure | A future baseline. The proposal contains no removal obligation and no tradable credits; the scheme would complement it, not implement it |

- *Why.* [WP-01](../papers/wp-01-legal-pathways/README.md) §2–4, which documents each provision against the primary texts [ost1967; liab1972; reg1975; iadc2025; copuos2007sdmg; lts2019; iso24113; fcc2022; eu2025spaceact].
- *Open.* Whether the scheme should seek recognition under the LTS Guidelines' reporting practice.

**A6 Compliance and enforcement.**
- *Rule.* Participation is voluntary unless a licensing authority makes it a condition. Only States and their authorities may impose sanctions, such as fines, licence conditions, suspension or refusal of a licence. The administrator may refuse to record a claim, revoke a recorded unit (C10), suspend a verifier's accreditation (D1), and publish these decisions. It reports suspected non-compliance to the relevant licensing authority.
- *Why.* Paper §16.6; WP-01 §6, requirement 5. A private administrator that claimed enforcement powers would lack legitimacy and legal basis.
- *Open.* Whether participants should accept, by contract, a binding first-instance dispute procedure (D4).

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
- *Open.*
  - Whether to include inclination, area-to-mass ratio and mission duration, which are listed in the paper's Table 2 but not yet implemented.
  - Whether to include design features: low-fragmentation design, avoiding release of mission-related objects, passive deorbit devices such as drag sails, design-for-demise, and aids that make later capture or tracking easier.
  - Whether to include compliance with standards (IADC, ISO 24113, national rules) as a separate factor, or only through the baseline.
  - Whether to include the operator's track record: disposal success rate, past break-ups, collision-avoidance practice. This stays excluded until correction and appeal processes exist ([WP-02](../papers/wp-02-sder-methodology/README.md) §5), because an error in a track record harms an operator across every future assessment.

**B3 Evidence classes.** ⚙︎
- *Rule.* Every input carries an evidence class and a source reference. A component takes the class of its weakest input, and a weaker class widens the component's uncertainty interval.
- *Why.* SDER 2–3.

**B4 Missing data.** ⚙︎
- *Rule.* A missing input is never replaced by a favourable value. It is scored at its worst case and named in the output. The result is *indicative* when nothing is missing and *provisional* when the missing weight is at or below a published threshold. Above that threshold the result is *withheld*.
- *Why.* SDER 4.
- *Open.* The threshold. It is 0.30 in research methods v0.1 and v0.2.

**B5 Uncertainty and bands.** ⚙︎
- *Rule.* Every result gives a point estimate and an interval. A band (low, medium or high) is reported together with whether the interval lies entirely inside it.
- *Why.* SDER 3. A single score must not look more certain than its inputs.

**B6 Method versions.** ⚙︎
- *Rule.* Weights, tables and thresholds are published as a versioned method file. Each assessment records the method's identifier and its SHA-256. A new version never changes the meaning of a past assessment.
- *Why.* SDER 7; paper §16.1.
- *Open.* The 2025 drafts proposed illustrative weights of 40% orbit, 20% design, 15% track record, 15% local density and 10% standards compliance. Research method v0.2 uses different, calibrated tables; see WP-02 and WP-04. Which weighting a pilot adopts is for the review group.

**B7 Disclosure, correction and appeal.**
- *Rule.* An assessed operator receives the inputs, the evidence classes and the rationale for each component. The operator may submit corrected evidence, and may appeal to a panel that took no part in the assessment.
- *Why.* SDER 6; paper §16.2.

**B8 Operator-level summaries (option).**
- *Rule.* If a scheme reports an operator-level figure, it is computed from the operator's mission assessments under one method version, with the number of missions and the share withheld shown next to it. It is published only once B1's conditions are met.
- *Why.* The 2025 drafts rated operators rather than missions. Mission-level assessment is more accurate and easier to correct, but insurers and regulators often reason about operators.
- *Open.* Whether operator-level figures should exist at all, given the risk that they become league tables.

**B9 Uses of an assessment.**
- *Rule.* An SDER assessment may be used for disclosure, to adjust an obligation (F4), to inform an orbital-use fee (F1), or as an insurance or procurement criterion (F1). Each use names the method version and the band certainty (B5). A *withheld* result cannot be used to reduce an obligation.
- *Why.* SDER 1; paper §5 and §12.

---

## Part C: Space Debris Credit (SDC)

**C1 Unit.**
- *Rule.* One SDC unit represents a verified reduction of $\Delta R_0$ in the risk proxy over a stated horizon, relative to a stated baseline. The number of units for an action is calculated from the conservative bound of ΔR, meaning the lowest reduction consistent with the evidence, rounded down. ⚙︎
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
- *Open.* Collision-avoidance maneuvers are excluded. They are routine practice, and the counterfactual cannot be verified. Natural decay of a derelict is also excluded, because no one acted.

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
- *Open.* Whether a reversible `suspended` state is needed while a dispute is open (D4). The 2025 drafts froze disputed credits; the reference code has no such state yet.

**C8 Uniqueness.** ⚙︎
- *Rule.* Only one non-void claim may exist for a given (object identifier, outcome type). Within one action, an object may appear only once. Credits go to a single accountable entity, typically the operator under the authorising State. A service provider may receive the economic value by contract, but the registry still records only one issuance for the physical event.
- *Why.* SDC 4; paper §7.
- *Open.* How to prevent the same outcome being claimed in another scheme. Cross-registry identifiers are one route.

**C9 Retirement.** ⚙︎
- *Rule.* Retirement is one-way and records who retired the unit and for what purpose (an obligation, named; or a voluntary claim).
- *Why.* Paper §4.

**C10 Reversal and false claims.** ⚙︎ (reversal)
- *Rule.* `reject` and `revoke` require a public reason. If a recorded outcome proves false, for example because an object reported as reentered is re-acquired by tracking, the claim is revoked and the revocation is published. A claimant found to have made a knowingly false claim is barred from submitting claims for a published period, and the administrator informs its licensing authority. A verifier that confirmed it without due care loses accreditation (D1).
- *Why.* SDC 4; [GOVERNANCE.md](../GOVERNANCE.md). The 2025 drafts set the same consequences.
- *Open.* Who bears the loss when a retired unit is revoked: the claimant must replace it, or the obligation it supported is reopened.

**C11 Trackability.**
- *Rule.* An action is eligible only if the objects it concerns can be reliably tracked before and after, by at least one data provider independent of the claimant. The administrator publishes the size threshold for each orbital regime and widens the scope as tracking improves (D6).
- *Why.* Verification depends on independent tracking. Objects larger than about 10 cm are tracked routinely in LEO [nasa_odpo_faq]; the threshold is higher in geostationary orbit.
- *Open.* The thresholds. The 2025 drafts proposed about 10 cm in LEO and about 1 m in GEO. Whether removal of many small fragments, once trackable, should earn units in proportion to ΔR.

**C12 No credit for unsafe actions.**
- *Rule.* No unit is issued for an action that itself creates undue risk, such as deliberate fragmentation, or an action carried out in breach of flight-safety rules or without the coordination a licensing authority requires. If an action produces debris, that debris is counted against ΔR.
- *Why.* The point of the unit is net risk reduction. Carried over from the 2025 drafts.

**C13 Advance notification.**
- *Rule.* A claimant files a plan for any action it intends to claim, before the action, with its baseline, method version and evidence plan. Actions not notified in advance may be claimed only if the evidence required by C2 is still complete, and they are marked as such.
- *Why.* Advance filing makes the baseline harder to adjust after the event, and lets verifiers prepare independent observation. Carried over from the 2025 drafts, which encouraged advance plans.

**C14 Why the unit is based on ΔR.**
- *Rule.* Units are counted in ΔR, not per object or per kilogram removed.
- *Why.* One unit per object would treat a 1 kg fragment like a 9 t rocket stage. One unit per kilogram ignores persistence and congestion. WP-04 shows that, on real catalogue data, removing the ten highest-R derelicts reduces R by about 80 times as much as removing ten at random. A per-object unit would hide that difference.
- *Open.* Whether a simpler per-object unit should be allowed in Phase 0 (I1) for administrative reasons, with a conversion published later.

---

## Part D: Verification, audit and disputes

**D1 Accreditation and independence.** ⚙︎ (partly)
- *Rule.* Verifiers are accredited against published criteria: technical competence, independence and data handling. A verifier must not be the claimant and must declare conflicts. The registry refuses a conflicted assignment. Only the assigned verifier may record verification. The administrator publishes the list of accredited verifiers and data providers, and may add, suspend or remove them.
- *Why.* SDC 3; paper §16.2.

**D2 Several sources and audit triggers.**
- *Rule.* Wherever possible, an outcome is confirmed by at least two independent data sources, for example two tracking networks, or tracking plus operator telemetry. If the sources disagree, or the confirmation threshold is not met, a third-party audit starts automatically and no unit is issued until it ends.
- *Why.* [WP-03](../papers/wp-03-claim-integrity/README.md) §6, items 1–2.
- *Open.* The confirmation threshold for each action class.

**D3 Quality control.**
- *Rule.* The administrator rotates verifiers, peer-reviews a sample of verifications and re-audits a random sample. Part of the verification fees may fund this work.
- *Why.* Paper §16.2. Auditors paid by participants need structural checks.

**D4 Disputes and appeals.**
- *Rule.* Disputes go through three tiers:
  1. **Informal resolution**, facilitated by the administrator: sharing data, correcting inputs, recalculating.
  2. **A dispute panel** combining technical and legal expertise, under published procedures and timelines. Every party affected has the right to be heard, and decisions rest on the evidence and give reasons.
  3. **External recourse.** Nothing in this Rulebook prevents a party from going to national courts or diplomatic channels. A court decision that bears on a recorded outcome is applied in the registry.

  When disputes show that a rule is systematically ambiguous, the rule is clarified in the next method cycle.
- *Why.* Paper §16.2. The PCA Optional Rules for Arbitration of Disputes Relating to Outer Space Activities (2011) are a ready template for tier 2 [pca2011].
- *Open.* Whether tier 2 should be binding by contract on participants.

**D5 System audits.**
- *Rule.* An independent auditor, not the administrator, audits the scheme each year and publishes the results:
  - **data audit:** a sample of issuances checked against raw tracking data and mission logs, and a sample of SDER inputs checked against their sources;
  - **financial audit:** all fees, penalties received and ESAF flows (H7);
  - **procedural audit:** that rule and method changes were made as decided (G1), and that every manual intervention was logged with a reason.
- *Why.* The 2025 drafts set out the same three audits. Published audits are how a registry earns trust without claiming authority (A4).

**D6 Technical standards updates.**
- *Rule.* The administrator reviews the evidence requirements (C2), trackability thresholds (C11) and method versions (B6) at least once a year, through the change process in G1.
- *Why.* Tracking and servicing technology change faster than rules; a fixed standard would either exclude new capability or lag behind it.

**D7 Compliance review.**
- *Rule.* Where an obligation exists (Part F), the administrator compares each participant's retirements with its obligation once per period and publishes the result. A shortfall is handled in steps: notice, then a published grace period, then a report to the licensing authority, which decides any sanction (A6).
- *Why.* The 2025 drafts proposed the same graduated response. It keeps enforcement with States.

---

## Part E: Registry and transparency

**E1 Records.** ⚙︎
- *Rule.* The registry records every event: submission, verifier assignment, verification, rejection, issuance, retirement and revocation. Each record carries a sequence number, a timestamp, the actor and the payload.
- *Why.* Paper §7.
- *Open.* Whether national registries under the Registration Convention should cross-reference recorded outcomes.

**E2 Tamper evidence.** ⚙︎ (partly)
- *Rule.* The registry is an append-only log in which each entry carries the hash of the previous one. When the log is opened, it is replayed and re-checked against these rules. The head hash is published on a schedule in at least one location the administrator does not control.
- *Why.* [WP-03](../papers/wp-03-claim-integrity/README.md) §4. A hash chain gives the tamper evidence the 2025 drafts sought from a blockchain, without a token or a consensus network. Anchoring the head hash is not yet implemented.

**E3 Public reporting.**
- *Rule.* The administrator publishes aggregate outcomes, including total ΔR retired. It also publishes methods, anonymised verification statistics (time, cost, dispute rate) and uncertainty ranges for key parameters. Sensitive operational details are not published.
- *Why.* Paper §13 and §16.3.

**E4 Annual report.**
- *Rule.* Each year the administrator publishes an orbital sustainability report covering: ΔR recorded and retired by action class and regime; claims rejected and revoked, with reasons; audit findings (D5); compliance review results (D7); ESAF accounts and grants (H7); and progress on the indicators in Part J.
- *Why.* The 2025 drafts proposed an annual report of this kind. One document makes the scheme checkable by people outside it.

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
| Public procurement of removal | An agency pays for removal of chosen objects and records the outcome | Finite budgets; no lasting price signal |

- *Why.* Vision & Principles SDC 5; paper §12.
- *Open.* Whether units may ever be transferred. If they may, transfer rules, holder disclosure and measures against manipulation are needed before any transfer is allowed.

**F2 Shared infrastructure and equity.**
- *Rule.* Whatever instrument is chosen, a published share of the scheme's revenue goes to the Equitable Space Access Fund (Part H).
- *Why.* Paper §11 and §16.4.

**F3 Obligations and quotas (option).**
- *Rule.* A jurisdiction that sets an obligation publishes: who is covered; the unit per object launched or per unit of SDER exposure; the period; how initial allocations, if any, are made; and an aggregate ceiling. The ceiling is set so that, across covered operators, long-lived risk does not grow. A stricter ambition, in which each new object is matched by a recorded reduction ("one-up, one-down"), is one possible end point.
- *Why.* The 2025 drafts proposed a global cap. A cap can only be set by authorities with jurisdiction, so this draft frames it as a published design for each jurisdiction.
- *Open.* How allocations are made (free, by auction, or by a mix), and how legacy debris is brought into obligations over time (I1).

**F4 Bonus–malus (option).**
- *Rule.* An obligation may be adjusted by SDER band. Missions in the low band with an interval wholly inside it may have their obligation reduced. Missions in the high band may have it increased, for example to two units where one would otherwise apply. Missions in the middle band, or whose interval crosses a band boundary, keep the nominal obligation. The adjustment schedule is published with the method version.
- *Why.* The 2025 drafts proposed bonus credits for the best tier and extra obligations for the worst. Tying the adjustment to band certainty (B5) stops an uncertain rating from earning a reduction.
- *Open.* Whether a reduction should take the form of fewer units owed or of units granted from a reserve. Granting units creates supply without a physical outcome, so this draft prefers fewer units owed.

**F5 Penalties and their use.**
- *Rule.* Where a licensing authority imposes a financial penalty for a shortfall, it is invited to direct a published share of it to the ESAF (H2). The administrator itself imposes no financial penalties (A6).
- *Why.* Carried over from the 2025 drafts, which sent penalties to the fund.

---

## Part G: Governance and change

**G1 Rule changes.**
- *Rule.* Changes follow [GOVERNANCE.md](../GOVERNANCE.md):
  - a proposal with rationale and sources;
  - at least 30 days of comment for substantive changes;
  - a published decision with reasons;
  - versioned effect, so a change never applies retroactively.
- The cadence is annual, with an emergency route for safety-critical corrections. Every emergency change is logged with its reason and reviewed at the next annual cycle.
- *Why.* Paper §16.1, where rule drift is named as a central failure mode.

**G2 Review group.**
- *Rule.* An independent expert group is drawn from operators, insurers, regulators and independent researchers, with conflicts declared. It proposes method updates. Voting rules prevent any one class of participant from dominating.
- *Why.* Paper §16.1; Vision & Principles, "Governance proposed for the Institute".

**G3 Originator.**
- *Rule.* The originator and any affiliated organisation may implement the method. They may not assess or certify their own missions or claims, chair the review group permanently, hold a seat on the ESAF board, or veto a method.
- *Why.* Vision & Principles SDER 6; [DISCLOSURES.md](../DISCLOSURES.md). The 2025 drafts gave the originating company veto rights over technical parameters and a seat on the fund's board. This draft removes both.

**G4 Administrator functions.**
- *Rule.* The administrator:
  - keeps this Rulebook and its annexes (G1);
  - accredits verifiers and data providers (D1);
  - keeps the registry (Part E);
  - runs compliance reviews where obligations exist (D7);
  - runs tier 1 of dispute resolution and convenes tier 2 (D4);
  - publishes the annual report (E4).

  It does not set obligations or quotas; licensing authorities do (F3).
- *Why.* Paper §15 and §16.

**G5 International home.**
- *Rule.* The administrator reports annually to the States that recognise the scheme, and offers its reports to COPUOS through a participating State or observer organisation.
- *Why.* The 2025 drafts placed the scheme under the auspices of UNOOSA and COPUOS. Neither body can be committed by this Rulebook, so the rule describes what the administrator itself can do.
- *Open.* Whether a dedicated intergovernmental body should take over the administrator's functions if the scheme reaches Phase 3 (I1).

**G6 Evolution of governance.**
- *Rule.* Governance widens as participation grows. When published milestones are met, seats in the review group and decision rights pass from founding participants to broader constituencies. The milestones concern the number of participating States and operators, the share of participants that are emerging space actors, and years of operation.
- *Why.* The 2025 drafts set similar milestones for handing control from a founding consortium to the wider community.
- *Open.* The milestones; whether decisions on method changes need agreement of two chambers (one for States, one for operators and other participants); whether some decisions should be one entity, one vote.

**G7 Entrenched provisions.**
- *Rule.* The following can be changed only by a supermajority set out in GOVERNANCE.md, after at least 90 days of comment: A4 (relationship to law), C3 (baselines), C6 (consent), G3 (originator), and the existence of the ESAF and its beneficiary floor (H2, H6).
- *Why.* The 2025 drafts proposed "constitutional" protection for OST compliance and the fund's share, so that a narrow future majority could not remove them.

---

## Part H: Equitable Space Access Fund (ESAF)

**H1 Purpose and principles.**
- *Rule.* The ESAF exists so that debris rules do not become a barrier to entry for States and organisations with fewer resources, and so that they can take part in tracking, verification and remediation. It follows three principles:
  - Outer space is "the province of all mankind" and is free for exploration and use by all States (OST Art. I).
  - Responsibility is proportional: those who place more long-lived risk in orbit contribute more.
  - Compliance should build capacity, not only cost money.
- *Why.* [ost1967] Art. I; paper §11 ("Equity is not peripheral") and §16.4.

**H2 Funding.**
- *Rule.* The ESAF receives a published share of each revenue stream the scheme or a recognising jurisdiction creates:
  - proceeds of any initial allocation or auction of obligations (F3);
  - verification and registry fees;
  - penalties directed to it (F5) and forfeited bonds (F1);
  - fees on transfers, if transfer is ever permitted (F1).

  It may also receive voluntary contributions from States, operators and foundations, and co-financing from development banks. No contribution buys influence over grant decisions.
- *Why.* Paper §4, §8 and §16.4 propose that a share of auction revenue or fees supports shared infrastructure. A share-of-proceeds levy has precedent: the Adaptation Fund was first financed by 2% of the credits issued under the Kyoto Protocol's Clean Development Mechanism, and the Paris Agreement's Article 6.4 mechanism sends 5% of issued units to it [unfccc_af].
- *Open.* The shares. The 2025 drafts proposed 40% of initial allocation proceeds and 10% of ongoing fees and penalties. This draft keeps those figures as the starting point for consultation.

**H3 Governance.**
- *Rule.* An ESAF board governs the fund, separately from issuance decisions. It has equal numbers of seats for:
  - emerging space actors (A2), with regional balance;
  - contributors.

  It also has non-voting seats for independent experts, for example from UN development or space bodies. The chair rotates between the two groups each year. Decisions are by consensus where possible; otherwise by a two-thirds majority that includes a majority of each group. The originator holds no seat (G3).
- *Why.* Paper §16.4: governance of the fund "should be separated from credit issuance decisions to avoid conflicts". The structure follows two working precedents. The Executive Committee of the Montreal Protocol's Multilateral Fund has seven members from developing and seven from developed countries, rotates its chair, and decides by a two-thirds majority that includes a majority of each group [mlf_excom]. The Green Climate Fund's board has 24 members split equally between developing and developed countries [gcf_gi].
- *Open.* The number of seats; how emerging-actor seats are filled; whether operators and States share the contributor seats.

**H4 Eligibility and selection.**
- *Rule.* The board publishes calls for proposals and its selection criteria. The criteria cover: the expected effect on orbital safety or on the applicant's ability to take part; the applicant's capacity to deliver; value for money; and regional balance. Every decision is published with reasons. Applicants may ask for a review once.
- *Why.* Paper §16.4 asks for "published objectives … annual budgets, grant decisions, and impact metrics".
- *Open.* How often calls are held; the maximum grant size.

**H5 Programmes.** The ESAF funds four kinds of work:
1. **Capacity building.**
   - Access to tracking data, or a share in tracking stations, for States that rely entirely on others for orbital data.
   - Training and scholarships in orbital mechanics, debris mitigation engineering and space law.
   - Deorbit devices such as drag sails or small propulsion modules for first national satellites and university satellites, so they meet disposal rules.
2. **Support with compliance costs.**
   - Covering verification fees for small operators (paper §16.4).
   - Covering all or part of an obligation (F3) for a State's first satellites.
   - Co-funding an unplanned disposal or removal service for a small operator.

   Support is conditional on the recipient following the disposal and passivation practices in its plan.
3. **Technology and open tools.**
   - Removal and servicing demonstrations carried out with or for emerging space agencies.
   - Open-source tools for SDER assessment, compliance tracking and mission planning.
   - Observation campaigns that involve universities in several regions.
   - Open research that improves the risk proxy and the rating method (paper §16.4).
4. **Participation.**
   - Translation of this Rulebook and its methods.
   - Workshops.
   - Travel grants so that participants from low-income countries can attend standard-setting meetings.

- *Why.* Paper §11 and §16.4. UNOOSA's Access to Space for All initiative, launched in 2018, shows the demand for programmes of this kind [unoosa_a2s4a].

**H6 Beneficiary floor.**
- *Rule.* At least 50% of disbursements each year go to projects led by, or directly benefiting, emerging space actors.
- *Why.* Carried over from the 2025 drafts. A floor keeps the fund from drifting towards the best-resourced applicants.
- *Open.* The share; the exact definition of emerging space actor, for example by reference to UN country groupings or to the absence of national launch capability.

**H7 Transparency and audit.**
- *Rule.* The ESAF publishes annual accounts, every grant with its amount and purpose, and an impact report against stated objectives. An independent audit of its finances is carried out each year (D5) and published.
- *Why.* Paper §16.4.

**H8 Annual forum.**
- *Rule.* The board holds an annual open forum, where possible alongside a COPUOS session or the International Astronautical Congress. Funded projects report there and contributors announce pledges.
- *Why.* Carried over from the 2025 drafts. A public forum keeps recipients' voices in the fund's decisions.

**H9 Coordination with rule changes.**
- *Rule.* When a proposed rule change (G1) would raise obligations, the board is consulted on its effect on emerging space actors and may propose transitional support. The board itself cannot change H2's shares or H6's floor; those follow G1 and G7.
- *Why.* The 2025 drafts linked the fund's board to the main governance body for this reason.

---

## Part I: Implementation and adoption

**I1 Phases.**
- *Rule.* The scheme is introduced in four phases. A phase begins only when the evidence gates of the previous phase are met and published. The phases are not tied to dates.

| Phase | What happens | Gates to move on |
|---|---|---|
| 0. Pilot | A pilot administrator publishes this Rulebook, accredits verifiers and runs the registry with public aggregate reporting. Eligible classes (C2) and baselines (C3) are limited to actions with high verification confidence, such as controlled reentry and early disposal confirmed by independent tracking. One or two shells are chosen where persistence and density justify the focus. One compliance cycle runs with a fixed retirement date | Verification cost and time measured and published; dispute rate below a published level; at least one outcome of each pilot class verified; a documented consent pathway for objects outside domestic jurisdiction; method update cadence in place |
| 1. Insurers and procurement | Insurers and customers reward low SDER bands and retired units through pricing or contract preference. No legal obligation yet. This tests whether demand appears without regulation | Measured change in operator behaviour, for example disposal success rate or the share of missions rated *indicative* rather than *provisional*; at least one insurer or buyer using the scheme |
| 2. National licensing | One or more licensing authorities require SDER disclosure, and retirement in proportion to the rating for missions in defined shells (I2), starting with a partial obligation. Early jurisdictions set up mutual recognition (I3). More States adopt compatible rules, including emerging space actors supported by the ESAF. Obligations may rise and may start to require a share of units from removal of legacy objects | No unresolved double counting between jurisdictions; indicators in Part J show slower growth of long-lived risk in target shells; ESAF disbursements meet the beneficiary floor |
| 3. Harmonisation | Eligible actions, evidence requirements and reporting templates are aligned across jurisdictions and with existing guidance. Most launches are covered by compatible national rules or an international instrument (I4). The ambition becomes no net growth of long-lived risk, or a net reduction | Reviewed every five years against Part J (J2) |

- *Why.* Paper §10 sets out these four phases (pilot; insurers and procurement; national licensing; harmonisation) and §14 gives the pilot checklist. The 2025 drafts also had four phases, tied to years and to market-size forecasts. This draft ties them to evidence instead, because no forecast of that kind can yet be sourced.
- *Open.* The thresholds for each gate. Whether Phases 1 and 2 can run in parallel in different jurisdictions.

**I2 National integration.** A State can integrate the scheme in several ways, which can be combined:
- **Launch and payload licensing:** a licence condition that the operator disclose an SDER assessment and, where an obligation exists, show retirement of the required units before launch.
- **Operator licensing and continuing supervision:** ongoing compliance (D7) as a condition of keeping an operator licence, as OST Art. VI allows.
- **Spectrum and market access:** authorities that grant spectrum or market access may consider SDER disclosure. Any role for ITU procedures would need agreement among administrations and is speculative today.
- **Liability and insurance:** a State may set financial-responsibility requirements according to SDER band. Insurers may use ratings and retired units in underwriting.
- **Fiscal instruments:** tax relief for removal services or for retirement, or a launch levy that is reduced when units are retired.
- *Why.* WP-01 §4–5; paper §12. Carried over from the 2025 drafts.
- *Open.* Which combination a first adopting jurisdiction should use.

**I3 Mutual recognition.**
- *Rule.* Jurisdictions that implement this Rulebook recognise units issued under each other's implementation, provided both use the same unit definition (C1), publish their baselines (C3) and share one registry or linked registries that enforce uniqueness (C8). Each jurisdiction publishes a conformance statement.
- *Why.* Paper §16.5 calls for interoperability through "a canonical definition of the credit unit and the rating method".

**I4 International pathways.** In order of increasing formality:
1. **Recognition as a reference standard.** States note the Rulebook in COPUOS reporting, as they do for other standards.
2. **A UN General Assembly resolution** encouraging States to adopt measures consistent with it. Not binding, but politically significant.
3. **An interpretive understanding or protocol** on what due regard (OST Art. IX) and continuing supervision (Art. VI) mean for long-lived objects, without reopening the Treaty.
4. **A new agreement on orbital sustainability**, with the unit and rating method in a technical annex.
- *Why.* WP-01 §5 shows that much can be done without a new treaty. The 2025 drafts listed the same four pathways.
- *Open.* Whether to pursue any pathway beyond 1 before Phase 2.

**I5 Adaptive management.**
- *Rule.* If removal capacity lags behind obligations, authorities may phase obligations in more slowly, and the ESAF may co-fund removal missions. If recorded units greatly exceed obligations, authorities may tighten obligations sooner. If transfer is permitted, any price-stabilisation measure (for example a reserve) is published in advance with its trigger.
- *Why.* Lessons from emissions trading, carried over from the 2025 drafts.

**I6 Sunset and maintenance.**
- *Rule.* If the Part J indicators show that long-lived risk is falling and disposal is routine, the review group may propose moving the scheme to a maintenance mode with lighter reporting. This change follows G1.
- *Why.* A scheme should not outlive its purpose. Carried over from the 2025 drafts.

---

## Part J: Outcome indicators and review

**J1 Indicators.**
- *Rule.* The administrator tracks and publishes, each year:
  - total ΔR recorded and retired, by action class and regime;
  - total R in each target shell, from an open catalogue, and its trend;
  - verification cost, time and dispute rate (E3);
  - the share of missions with *indicative*, *provisional* and *withheld* ratings;
  - the number of participating States and operators, and the share that are emerging space actors;
  - ESAF income, disbursements, and the beneficiary share (H6).
- *Why.* Paper §13. Indicators replace the forecasts in the 2025 drafts. They can be checked; forecasts could not.

**J2 Five-year review.**
- *Rule.* Every five years, an independent review asks whether the scheme has reduced long-lived risk relative to what would likely have happened without it, and whether its costs fall fairly. The review is published with the data it used.
- *Why.* Paper §14: if verification is not affordable or behaviour does not change, the evidence should show what to simplify or redesign.

---

## Annex A: rule-to-code map

| Rule | Code | Test |
|---|---|---|
| B3–B6 | [`src/sder/engine.py`](../src/sder/engine.py), [`research-v0.2.yaml`](../src/sder/methodology/research-v0.2.yaml) | [`tests/test_sder_engine.py`](../tests/test_sder_engine.py) |
| C1 | [`src/sdc/risk.py`](../src/sdc/risk.py) (`issuable_units`) | [`tests/test_sdc_risk.py`](../tests/test_sdc_risk.py) |
| C2, C7 | [`src/sdc/models.py`](../src/sdc/models.py) (`OutcomeType`, `TRANSITIONS`) | [`tests/test_sdc_registry.py`](../tests/test_sdc_registry.py) |
| C8–C10, D1, E1–E2 | [`src/sdc/registry.py`](../src/sdc/registry.py) | [`tests/test_sdc_registry.py`](../tests/test_sdc_registry.py) |
| C14, J1 (R by shell) | [`src/sdc/catalogue.py`](../src/sdc/catalogue.py) | [`tests/test_sdc_catalogue.py`](../tests/test_sdc_catalogue.py) |

## Annex B: glossary of abbreviations

| Term | Meaning |
|---|---|
| ADR | Active debris removal: rendezvous with a defunct object and removal from its orbit |
| COPUOS | United Nations Committee on the Peaceful Uses of Outer Space |
| COSPAR ID | International designator of a launched object |
| ESAF | Equitable Space Access Fund (Part H) |
| GEO | Geostationary orbit, about 35,786 km altitude |
| IADC | Inter-Agency Space Debris Coordination Committee |
| LEO | Low Earth orbit, up to 2,000 km altitude |
| LTS Guidelines | COPUOS Guidelines for the Long-term Sustainability of Outer Space Activities (2019) |
| NORAD ID | Satellite catalogue number assigned by the US Space Force |
| OST | Outer Space Treaty (1967) |
| PCA | Permanent Court of Arbitration |
| SDC | Space Debris Credit (Part C) |
| SDER | Space Debris Exposure Rating (Part B) |
| UNOOSA | United Nations Office for Outer Space Affairs |

## Consultation questions

1. Is $R = M \times L \times Pc$ a sufficient proxy for a pilot, or should the consequence term be replaced at once by a fragment-based metric such as ECOB?
2. How should $\Delta R_0$ be set so that units stay comparable across regimes?
3. Which evidence can be public without compromising operator confidentiality or security?
4. What waiting period (C4) prevents missions from being designed to earn credits?
5. Should transfer of units ever be permitted (F1)?
6. Are the 2025 funding shares for the ESAF (40% of allocation proceeds, 10% of fees and penalties) the right starting point (H2)? Is a 50% beneficiary floor right (H6)?
7. How should emerging space actors be defined, and how should their seats on the ESAF board be filled (H3, H6)?
8. Which evidence gates should open each phase (I1), and at what thresholds?
9. What trackability thresholds should apply in each regime (C11)?
10. Should operator-level summaries exist at all (B8)?

Please respond using the [consultation template](consultation-template.md).
