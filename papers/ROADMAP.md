# Research and institutional roadmap

This page lists what the programme still lacks before its outputs could be called institute-grade. Items are roughly in priority order within each group. Each completed item is recorded in [CHANGELOG.md](../CHANGELOG.md).

## Science

1. **Real data for the Strauss paper's Figures 2 and 3.** Rank intact LEO objects by $R_i = M_i L_i Pc_i$ using public catalogue data: CelesTrak SATCAT for orbits, and ESA DISCOS for mass, subject to its terms of use. Then compare the ΔR of removing the top 10 objects with the ΔR of removing 10 at random. This is the most valuable next step, because it turns the paper's illustration into a result.
2. **Calibrate the SDER placeholders** ([WP-02](wp-02-sder-methodology/README.md) §6):
   - lifetime from a decay model that accounts for ballistic coefficient and solar flux;
   - congestion from catalogue spatial density;
   - collision probability from an established method where conjunction data exist;
   - consequence from the NASA Standard Breakup Model or from ECOB.
3. **Sensitivity analysis.** Use Monte Carlo or Sobol analysis to measure how weights and bands affect band assignment. Ship it as a `sder sensitivity` command and a notebook.
4. **Reproducible case studies.** Assemble about 20 missions from public licensing filings, for example FCC orbital debris assessment reports, and record the license of each data source. Space-Track data cannot be redistributed.
5. **Comparison with other indices.** Score missions that have published Space Sustainability Rating results, and check where the two agree. Test whether McKnight et al.'s (2021) list of the 50 most concerning objects falls in the top set of $R_i$.
6. **Review of the debris environment.** Write a short review paper on the current debris population, using the ESA Space Environment Report and NASA ODPO figures.
7. **Peer review and venues.**
   - Seek external review of WP-02 and WP-03, and publish the reviewer reports.
   - Post a preprint (arXiv, physics.soc-ph or astro-ph.EP).
   - Submit to a journal, such as *Journal of Space Safety Engineering* or *Acta Astronautica*.
   - Submit an abstract to IAC 2027.

## Code

8. Anchor the registry log's head hash and sign each event (WP-03 §7).
9. Connect ΔR-proportional units (`sdc.risk`) to the claim lifecycle.
10. Implement the remaining Table 2 inputs: inclination, area-to-mass ratio, mission duration and design-for-demise.
11. Publish a JSON Schema for ΔR action files.

## Institution

12. **Legal entity.** Set up the institute, for example as a French *association loi 1901* or a *fonds de dotation*, or under fiscal sponsorship. Until then, it is described everywhere as "in formation".
13. **People.**
    - Form an independent review group of 3 to 5 external experts, and publish its terms of reference and its members' conflict declarations.
    - Credit contributors.
    - Give every author an ORCID iD.
14. **Policies.**
    - Conflict-of-interest declarations for every contributor.
    - A funding disclosure policy.
    - A corrections and retractions policy, beyond the interim rules in GOVERNANCE.md.
    - An appeals procedure.
    - A review of security and dual-use concerns for SSA data.
15. **Rights.** Record written confirmation that both authors release the Strauss paper under CC BY 4.0, and confirm the conference's rights policy.
16. **Publication infrastructure.**
    - A Zenodo DOI for each release and each paper.
    - A template for working papers.
    - A publications page on spacedebriscredit.org.
    - A public log of consultation responses, with a published response document.
17. **Translations.** French versions of the principles and the Rulebook draft.
