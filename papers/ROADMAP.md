# Research and institutional roadmap

This page lists what the programme has done and what it still lacks. Items are roughly in priority order within each group. Each completed item is also recorded in [CHANGELOG.md](../CHANGELOG.md).

## Done in 0.2.0

1. **Real data for the Strauss paper's Figures 2 and 3.** $R_i$ for 18,036 intact LEO objects from the open GCAT catalogue. Among derelicts, the top 50 hold 46 % of $R$, and removing the top 10 gives 80 times the ΔR of the median random ten. See [WP-04](wp-04-catalogue/README.md) §4–5.
2. **Calibrated SDER tables.** Persistence now comes from a drag-decay model through NRLMSIS 2.1, backtested on 404 reentered rocket bodies. Environment now comes from catalogue spatial density. Both are in method v0.2 (WP-04 §3 and §6).
3. **Sensitivity analysis and case studies.** `sder sensitivity` reports variance shares and weight perturbation. There are 20 real-object cases in [`examples/cases/`](../examples/cases/) (WP-04 §7).
4. **Comparison with published lists.** The comparison is class-level, because the 2021 consensus list is not openly available. No public per-mission SSR scores exist yet (WP-04 §8).

## Outside peer review

All working papers are **open for outside peer review**. No paper here has been peer reviewed yet.

To review a paper, open an issue with the "Peer review" template. Name the paper and its version, state any competing interests, and say whether you want your review published under your name, published anonymously, or kept private. Reviews are answered in public, and each change they lead to is recorded in the changelog. Corrections follow [GOVERNANCE.md](../GOVERNANCE.md).

The reviews most wanted:

- **WP-04.** The lifetime model, the $Pc$ assumptions, and the proposal to tie SDER to $R$.
- **WP-02.** The evidence widths and the missing-data rule.
- **WP-03.** The threat model.
- **WP-01.** The consent pathways, from space lawyers.

## Science

5. **Fix the SDER scale problem found in WP-04 §7.** SDER places a 1.3 kg derelict cubesat in the same band as a 9-tonne stage. Tie the consequence term, or the whole score, to $R$ in method v0.3.
6. **Conjunction-based collision probability.** Replace the kinetic-gas $Pc$ with a covariance-based method (Foster or Alfano) where conjunction data can be obtained and shared.
7. **Object-by-object comparison** with the 2021 list of 50 most concerning objects, if its table can be obtained with permission to publish the comparison. A comparison with SSR results, if per-mission data become available.
8. **Review of the debris environment.** A short paper on the current population, using the ESA Space Environment Report and NASA ODPO figures.
9. **Venues.** A preprint (arXiv, physics.soc-ph or astro-ph.EP), a journal submission (*Journal of Space Safety Engineering* or *Acta Astronautica*) and an IAC 2027 abstract.

## Code

10. Anchor the registry log's head hash and sign each event (WP-03 §7).
11. Connect ΔR-proportional units (`sdc.risk`) to the claim lifecycle.
12. Implement the remaining Table 2 inputs: inclination, area-to-mass ratio, mission duration and design-for-demise.
13. Publish a JSON Schema for ΔR action files.
14. Refresh the GCAT snapshot on a fixed schedule, for example every quarter, and publish the change in the top 50.

## Institution (later)

15. **Legal entity.** For example a French *association loi 1901*, a *fonds de dotation*, or fiscal sponsorship. Until then, the institute is described everywhere as "in formation".
16. **People.** An independent review group of 3 to 5 external experts with published conflict declarations, credited contributors, and an ORCID iD for every author.
17. **Policies.** Conflict-of-interest declarations, funding disclosure, corrections and retractions beyond the interim rules, appeals, and a dual-use review for SSA data.
18. **Publication infrastructure.** A Zenodo DOI for each release and paper, a working-paper template, a publications page, and a public log of consultation responses.

The rights to the Strauss paper are settled: both authors release it under CC BY 4.0, and the conference's rights policy allows this.
