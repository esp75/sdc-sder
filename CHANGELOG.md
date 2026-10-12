# Changelog

## 0.2.0 (2026-10-12)

- **Working paper SDC-WP-2026-04:** the paper's Figures 2–3 on real data. R = M × L × Pc for 18,036 intact LEO objects from GCAT; targeted against random removal; a lifetime backtest; a class-level comparison with published lists of the most concerning objects.
- **Code:**
  - `sdc.catalogue` and `sdc catalogue rank | compare | backtest`;
  - `sder.sensitivity` and `sder sensitivity`;
  - SDER method v0.2, now the default, with persistence and environment calibrated from open data (v0.1 kept for reproducibility).
- **Data:** a dated GCAT extract (CC BY 4.0) with SHA-256 fingerprints, and scripts that rebuild it and every number in WP-04.
- **Examples:** 20 case studies of real objects in `examples/cases/`.
- **Review:** all working papers are open for outside peer review, with an issue template.
- **Rights:** both authors release the Strauss paper under CC BY 4.0, and the conference's rights policy allows this.
- **Writing:** every document edited for plain, specific language.

## 0.1.0 (2026-10-12)

First public release of the SDC Institute research programme.

- **Papers:**
  - *Space Debris Credits: A Market-Based Framework for Governance and Environmental Stewardship in Orbit* (Kadri & Shishkina, Strauss Center Space Traffic Conference 2026)
  - Working papers SDC-WP-2026-01 to 03: legal pathways, the SDER and ΔR methodology, claim integrity
- **Specification:** *Vision and Principles v0.1*; the *Rulebook consultation draft v0.2*; the institutional brief; the consultation template; EN/FR explainers.
- **Reference code:**
  - `sder`: an illustrative exposure-scoring engine that accounts for evidence quality, driven by a versioned methodology file
  - `sdc.risk`: the paper's object-level risk proxy R = M × L × Pc and the expected risk reduction ΔR
  - `sdc.registry`: the claim lifecycle state machine, with a hash-chained append-only log and a guard against double counting
- **Provenance:** the 2025 working documents are not published. Their SHA-256 fingerprints are in ORIGIN.md. The 2025 patent application has been abandoned.
