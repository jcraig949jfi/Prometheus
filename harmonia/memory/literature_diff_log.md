# Literature Diff Log — Generator #7

**Generated:** 2026-04-20T23:08:36.186459+00:00
**Source:** `docs/prompts/gen_07_literature_diff.md` @ commit `ac354b26`
**Runner:** Harmonia_M2_sessionA_20260420
**Paper cache:** `aporia/data/literature_scan.json`

## Summary

- **Papers processed:** 190
- **Diff entries generated:** 205 (papers × matched F-IDs)
- **Classification distribution:**
  - `CANDIDATE_NEW_F_ID`: 136 (66.3%)
  - `DIVERGENCE_STRUCTURAL`: 32 (15.6%)
  - `REPRODUCTION`: 27 (13.2%)
  - `RETRACTION_CROSS_CHECK`: 10 (4.9%)

## Classification schema

| Category | Meaning | Action |
|---|---|---|
| REPRODUCTION | Paper claim matches our measurement within uncertainty | Log as calibration reinforcement |
| DIVERGENCE_NUMERICAL | Paper numerical claim differs beyond uncertainty | Seed debug task (priority -1.5) |
| DIVERGENCE_STRUCTURAL | Paper makes a different claim class / framing | Seed reconciliation task (priority -1.0) |
| RETRACTION_CROSS_CHECK | Paper touches an F-ID we retracted | Cross-check retraction reasoning against paper |
| KILL_REINFORCEMENT_CANDIDATE | Paper touches a killed F-ID | Feed into gen_05 replay queue |
| CANDIDATE_NEW_F_ID | Paper claims a structure we have not registered | Conductor evaluates for new F-ID opening |

## Entries by classification (top 5 per category)

### REPRODUCTION (27 total, showing 5)

- **F003 · Chur Chin (2025)** — A Spectral Analogy Between the Birch and Swinnerton-Dyer Conjecture and Cerebrospinal Fluid Dynamics
  - URL: <https://www.semanticscholar.org/paper/7d6deefac5b33fd23a29c592525e3f6f55383326>
  - Rationale: F-ID is calibration anchor; default to reproduction unless paper claims violation
- **F003 · M. Shoeib, (2025)** — A Topological Perspective on the Birch and Swinnerton Dyer Conjectures
  - URL: <https://www.semanticscholar.org/paper/b67ebdd0cef20c3e3dd917ed2e16d280886fee58>
  - Rationale: F-ID is calibration anchor; default to reproduction unless paper claims violation
- **F003 · Charlotte Dombrowsky (2025)** — On the Elliptic Curve $X_0(49)$ over Quadratic Extensions
  - URL: <https://www.semanticscholar.org/paper/a3ee53d1e87deaf3a5eb8296d7fa9da83ff0f5ab>
  - Rationale: F-ID is calibration anchor; default to reproduction unless paper claims violation
- **F003 · D. Wachs (2025)** — The Derived Adelic Cohomology Conjecture for Elliptic Curves
  - URL: <https://www.semanticscholar.org/paper/0e5cabe3ce57038487ed74d24bfdfadd6da4d702>
  - Rationale: F-ID is calibration anchor; default to reproduction unless paper claims violation
- **F003 · Francesc Castella (2025)** — Tamagawa number conjecture for CM modular forms and Rankin–Selberg convolutions
  - URL: <https://www.semanticscholar.org/paper/680a1a2591ae489e9ff4812f7f5886ef4139b78c>
  - Rationale: F-ID is calibration anchor; default to reproduction unless paper claims violation

### DIVERGENCE_STRUCTURAL (32 total, showing 5)

- **F011 · Yochay Jerby (2025)** — Variations of the Hardy Z-Function and the Montgomery Pair Correlation Conjecture
  - URL: <https://www.semanticscholar.org/paper/90ebfbdd17556f384cf475c9caab8bc37a00b13a>
  - Rationale: Paper touches this F-ID via different framing; structural comparison needed
- **F011 · S. Setiawan (2025)** — Primacohedron: A p-Adic String & Random-Matrix Framework for Emergent Spacetime, Perfectoids, p-adic
  - URL: <https://www.semanticscholar.org/paper/ebe2676ec019ba26db14a6516237e8681965a8db>
  - Rationale: Paper touches this F-ID via different framing; structural comparison needed
- **F011 · Brad Rodgers (2024)** — Arithmetic Consequences of the GUE Conjecture for Zeta Zeros
  - URL: <https://www.semanticscholar.org/paper/f6db6348e42485aa6187aab0c3bf369d47c5fc3b>
  - Rationale: Paper touches this F-ID via different framing; structural comparison needed
- **F011 · Owen Barrett, Zoe X. Batterman (2024)** — A Random Matrix Model for a Family of Cusp Forms
  - URL: <https://www.semanticscholar.org/paper/9bce76380b7c3e2530bc4ab17a3140d4e28322a3>
  - Rationale: Paper touches this F-ID via different framing; structural comparison needed
- **F011 · Owen Barrett, Zoe X. Batterman (2024)** — A Survey of a Random Matrix Model for a Family of Cusp Forms
  - URL: <https://www.semanticscholar.org/paper/4af770de6d2b0f7dc0634b010518fc1580ba41b1>
  - Rationale: Paper touches this F-ID via different framing; structural comparison needed

### RETRACTION_CROSS_CHECK (10 total, showing 5)

- **F043 · Chur Chin (2025)** — A Spectral Analogy Between the Birch and Swinnerton-Dyer Conjecture and Cerebrospinal Fluid Dynamics
  - URL: <https://www.semanticscholar.org/paper/7d6deefac5b33fd23a29c592525e3f6f55383326>
  - Rationale: F043 retracted as algebraic coupling; paper may be relevant to re-examining claim structure
- **F043 · M. Shoeib, (2025)** — A Topological Perspective on the Birch and Swinnerton Dyer Conjectures
  - URL: <https://www.semanticscholar.org/paper/b67ebdd0cef20c3e3dd917ed2e16d280886fee58>
  - Rationale: F043 retracted as algebraic coupling; paper may be relevant to re-examining claim structure
- **F043 · Charlotte Dombrowsky (2025)** — On the Elliptic Curve $X_0(49)$ over Quadratic Extensions
  - URL: <https://www.semanticscholar.org/paper/a3ee53d1e87deaf3a5eb8296d7fa9da83ff0f5ab>
  - Rationale: F043 retracted as algebraic coupling; paper may be relevant to re-examining claim structure
- **F043 · D. Wachs (2025)** — The Derived Adelic Cohomology Conjecture for Elliptic Curves
  - URL: <https://www.semanticscholar.org/paper/0e5cabe3ce57038487ed74d24bfdfadd6da4d702>
  - Rationale: F043 retracted as algebraic coupling; paper may be relevant to re-examining claim structure
- **F043 · Francesc Castella (2025)** — Tamagawa number conjecture for CM modular forms and Rankin–Selberg convolutions
  - URL: <https://www.semanticscholar.org/paper/680a1a2591ae489e9ff4812f7f5886ef4139b78c>
  - Rationale: F043 retracted as algebraic coupling; paper may be relevant to re-examining claim structure

### CANDIDATE_NEW_F_ID (136 total, showing 5)

- **— · — (2024)** — Prime and Möbius correlations for very short intervals in $\fq[x]$
  - URL: <https://www.semanticscholar.org/paper/16e5972e0c9e5d0630852a929dc1552808f1e63c>
  - Rationale: No existing F-ID for this problem; paper may motivate a new one
- **— · — (2022)** — Note on the Chowla Conjecture and the Discrete Fourier Transform autocorrelation function problems
  - Rationale: No existing F-ID for this problem; paper may motivate a new one
- **— · — (2012)** — The autocorrelation of the Möbius function and Chowla's conjecture for the rational function field i
  - Rationale: No existing F-ID for this problem; paper may motivate a new one
- **— · — (2015)** — Some problems in analytic number theory for polynomials over a finite field
  - Rationale: No existing F-ID for this problem; paper may motivate a new one
- **— · — (2022)** — Note on the Chowla Conjecture and the Discrete Fourier Transform
  - Rationale: No existing F-ID for this problem; paper may motivate a new one

## Epistemic discipline applied

1. **LLM-assisted classification is provisional.** The v1 classifier uses tier + keyword heuristics on the paper TL;DR. Any DIVERGENCE_NUMERICAL re-classification into an action item requires human conductor verification of the paper's specific claim.
2. **Paraphrase drift hazard.** TL;DR fields are Semantic Scholar summaries, not author text. Before emitting a tensor-mutation task from a diff, re-read the abstract verbatim.
3. **Publication bias.** Reproductions over-represent easy measurements; divergences over-represent controversial claims. Do not aggregate as if this were an unbiased sample of truth.
4. **Pattern 30 gate** applies to every CANDIDATE_NEW_F_ID before registration.

## Next steps

1. Manual conductor review of top-10 CANDIDATE_NEW_F_ID entries — which deserve F-ID allocation?
2. RETRACTION_CROSS_CHECK entries feed F043 audit continuation.
3. Cadence runbook at `harmonia/memory/literature_diff_cadence.md` for scheduled re-runs.
4. As Aporia paper stream refreshes, re-run gen_07 executor; incremental diff.

## Version

- **v1.0** — 2026-04-20 — initial diff pass over 190-paper cache from first map-building wave.
