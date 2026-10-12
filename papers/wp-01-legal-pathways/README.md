# Legal pathways for debris remediation and outcome-based incentives under existing space law

| | |
|---|---|
| **Series** | SDC Institute Working Paper SDC-WP-2026-01 |
| **Version** | 0.1, 12 October 2026 |
| **Author** | Maxime Kadri, SDC Institute (in formation) |
| **Status** | Working paper. Not peer reviewed. Comments are invited through the [consultation template](../../spec/consultation-template.md). |
| **Extends** | Kadri & Shishkina (2026), §9 |
| **Competing interests** | See [DISCLOSURES.md](../../DISCLOSURES.md) |
| **Funding** | None |
| **Data availability** | No data. All sources are public and listed below. |
| **License** | [CC BY 4.0](../../LICENSES/CC-BY-4.0.txt) |

## Abstract

An incentive for debris mitigation and remediation of the kind proposed in Kadri & Shishkina (2026), whether a credit, an exposure rating, a bond or a fee, has to fit the law as it stands. It cannot assume a new treaty. This paper maps the binding treaty provisions and the main non-binding instruments onto three questions such a scheme must answer. Who may act on an object? Who bears the risk of the action? Which public record can confirm that the outcome occurred? We find that three provisions set the constraints. Article VIII of the Outer Space Treaty requires consent from the State of registry. The fault-based liability of the Liability Convention applies to damage in space. The registration regime is the basis for attributing an outcome to an object. We identify three pathways that need no new treaty: objects under domestic jurisdiction, bilateral permissions, and a standing-consent registry. Recent national and regional rules, such as the FCC five-year disposal rule and the proposed EU Space Act, define the *baseline* that any outcome-based incentive must exceed. We close with five design requirements for the [Rulebook](../../spec/rulebook-v0.2-consultation-draft.md).

## 1 Why the legal frame comes first

An outcome-based credit pays for a change of physical state: an object that reenters, is passivated, or is removed from a congested shell. Each step raises a legal question. Remediation may involve another State's object. Any operation near another object carries a risk of damage. The outcome has to be attributed to a registered object and to an accountable party, or it could be counted twice. A scheme that leaves these questions open will either be unlawful in some cases or unable to verify outcomes. Kadri & Shishkina (2026, §9) set out the constraints. This paper documents them against the primary texts.

## 2 Binding treaty provisions

**Responsibility and supervision.** Under Article VI of the Outer Space Treaty (OST), States bear international responsibility for national activities in outer space, including activities by non-governmental entities. Those activities require "authorization and continuing supervision" by the appropriate State [ost1967]. For an incentive scheme, this means every participating operator is already inside some national licensing regime. That regime is the natural point at which obligations, disclosures and recognised outcomes can attach.

**Jurisdiction, control and ownership.** Article VIII provides that a State of registry "shall retain jurisdiction and control" over an object launched into outer space, and that ownership is "not affected by" its presence in space or its return to Earth [ost1967]. No provision of space law resembles maritime salvage, and an object does not lose its owner by being abandoned. A third party therefore cannot lawfully remove, capture or move another State's object without that State's consent. This is the strongest constraint on remediation credits. It is the reason Kadri & Shishkina restrict eligibility for legacy objects to removals made under explicit consent.

**Liability.** The Liability Convention makes a launching State absolutely liable for damage its space object causes on the surface of the Earth or to aircraft in flight (Art. II). Damage caused elsewhere, including to another space object, gives rise to liability only if the damage is due to the fault of the launching State or of persons for whom it is responsible (Art. III) [liab1972]. Where several States jointly launch an object, they are jointly and severally liable (Art. V). Two consequences follow for remediation. The servicer and the State of registry of the target must allocate the risk of a collision during proximity operations by contract and through licensing, because the Convention does not settle it. And under the fault standard in Art. III, it is uncertain whether leaving a derelict in orbit counts as fault. The convention therefore gives a weak deterrent against leaving debris in orbit. This gap is the economic opening for an incentive instrument.

**Registration.** The Registration Convention requires a launching State to keep a national registry and to furnish the UN Secretary-General with basic orbital parameters and the general function of each registered object (Arts. II and IV) [reg1975]. For a credit scheme, the registry and the public catalogues together form the identity layer. An outcome can be credited only if it can be tied to a uniquely identified, registered object. The double-counting key in the reference registry implementation (COSPAR or NORAD identifier plus outcome type) depends on this layer.

**Due regard.** Article IX of the OST requires States to conduct their activities "with due regard to the corresponding interests of all other States Parties". It also provides for international consultations before any activity that could cause potentially harmful interference [ost1967]. This principle does not prescribe any particular debris practice. It does give a treaty basis to the argument that leaving a high-consequence object in a congested shell is a matter of shared concern.

## 3 Non-binding instruments and standards

There is no binding treaty dedicated to space debris. The practical norms come from a layered set of non-binding guidelines and from standards. Each layer can become binding when a State incorporates it into its licensing.

| Instrument | Status | Relevance to an incentive scheme |
|---|---|---|
| IADC Space Debris Mitigation Guidelines, IADC-02-01 Rev. 4 (Jan 2025) [iadc2025] | Technical consensus of space agencies. Rev. 4 adds a section on large constellations. | Defines the mitigation practices (limiting released debris, preventing break-ups, post-mission disposal, collision avoidance) that a baseline must reflect. |
| COPUOS Space Debris Mitigation Guidelines (2007), endorsed by UNGA resolution 62/217 [copuos2007sdmg] | Political, voluntary | Gives the IADC practices intergovernmental legitimacy. |
| COPUOS Guidelines for the Long-term Sustainability of Outer Space Activities (2019), A/74/20 annex II [lts2019] | Political, voluntary; 21 guidelines | Covers information sharing, conjunction assessment, registration practice and regulatory frameworks. Supports the transparency and data-sharing indicators in SDER. |
| ISO 24113:2023, 4th edition [iso24113] | International standard | Puts the mitigation requirements into an auditable form. A natural reference for evidence requirements. |
| ESA Zero Debris Charter (2024) [esa2024zerodebris] | Non-binding, multi-stakeholder | Sets debris-neutrality ambitions for 2030. These are voluntary commitments that credits could help evidence. |

## 4 National and regional rules as the baseline

Outcome-based credits must reward performance *beyond* what is already required. Otherwise they subsidise compliance (Kadri & Shishkina 2026, §3 and §8). Requirements therefore depend on the jurisdiction and change over time:

- **United States.** The FCC's Second Report and Order (FCC 22-74, adopted 29 September 2022) shortened the post-mission disposal benchmark for space stations in low Earth orbit from 25 years to five. It applies to US-licensed systems and to non-US systems seeking US market access, and took effect on 9 September 2024 [fcc2022].
- **France.** The 2008 Space Operations Act (*loi* n° 2008-518) makes space operations subject to authorisation and to technical regulations that include end-of-life obligations.
- **European Union.** The Commission proposed an EU Space Act on 25 June 2025 (COM(2025) 335), with safety, resilience and sustainability as its pillars. If adopted, it would apply to EU operators and to non-EU operators whose activities have a link to the EU, from 1 January 2030 [eu2025spaceact]. At the time of writing it is still in the legislative procedure.

An international scheme therefore needs a baseline per jurisdiction, with a dated version. A single global "25-year rule" baseline would already over-credit missions licensed under the FCC five-year rule.

## 5 Three pathways that need no new treaty

Building on Kadri & Shishkina (2026, §9):

1. **Domestic jurisdiction.** A State, or operators it licenses, remediates objects on its own registry. Consent and jurisdiction coincide, so no cross-border consent is needed. The first remediation demonstrations follow this pattern. In JAXA's Commercial Removal of Debris Demonstration, the ADRAS-J inspection spacecraft approached a Japanese H-IIA upper stage in 2024 [jaxa_crd2]. ESA's ClearSpace-1 mission was redirected to an ESA-owned satellite, PROBA-1 [esa2024clearspace].
2. **Bilateral permission.** The State of registry gives consent for specific objects or classes of objects. The agreement allocates liability, safety constraints and data access. Each permission takes time to negotiate, but it fits Article VIII.
3. **Standing-consent registry.** States and operators record in advance their consent for defined interventions on defined objects or classes. Each entry gives the object identifiers, the permitted action types, the safety constraints and a point of contact. This lowers transaction costs and keeps jurisdiction and control with the State of registry. It is the only one of the three pathways that requires new institutional infrastructure, though not a treaty.

## 6 Design requirements for the Rulebook

The analysis implies five requirements. They are implemented in the [Rulebook consultation draft v0.2](../../spec/rulebook-v0.2-consultation-draft.md):

1. **Consent evidence.** No outcome involving an object outside the claimant's domestic jurisdiction is eligible without documented consent from the State of registry.
2. **Baselines by jurisdiction.** Baselines are versioned by jurisdiction and date. Meeting a legal requirement earns nothing, and only performance beyond it is credited.
3. **Identity.** Every claim names a registered object by its COSPAR or NORAD identifier. One outcome on one object yields one claim (see [WP-03](../wp-03-claim-integrity/README.md)).
4. **Liability allocation.** Before a remediation outcome is recognised, the claimant must show how liability is allocated between servicer, State of registry and licensing State.
5. **The scheme's role.** The administrator publishes rules, verifies outcomes and keeps the record. Enforcement is left to licensing authorities, insurers and contracts (Kadri & Shishkina 2026, §16.6). The scheme claims no public authority it does not have.

## 7 Limitations

This is a desk review of primary texts. It is not legal advice and it does not survey national laws. National law is covered only through the US, French and EU examples. Two questions are still open: whether fault under Art. III of the Liability Convention could include a failure to dispose of an object, and how the EU Space Act will look once adopted. Comments from space-law scholars are particularly welcome.

## References

Full entries are in [references.bib](../references.bib): `kadri2026sdc`, `ost1967`, `liab1972`, `reg1975`, `iadc2025`, `copuos2007sdmg`, `lts2019`, `iso24113`, `esa2024zerodebris`, `fcc2022`, `eu2025spaceact`, `jaxa_crd2`, `esa2024clearspace`. France: *Loi n° 2008-518 du 3 juin 2008 relative aux opérations spatiales*.
