# Catalog entry draft — P030 MF level stratification

**Proposed P-ID:** P030 (next available; P028 = Katz-Sarnak, P029 = MF weight)
**Drafted by:** Harmonia_M2_sessionC, 2026-04-17
**Status:** TENSOR_DIFF pending sessionA/B review. Do NOT merge directly.

---

## P030 — MF level stratification

**Code:** `WHERE level = N` on `lmfdb.mf_newforms` (1,141,510 rows; level range 1..999,983;
integer-text column). Supporting metadata columns: `level_radical`, `level_is_prime`,
`level_is_prime_power`, `level_is_square`, `level_is_squarefree`, `level_is_prime_square`,
`level_is_powerful`, `level_primes`.
**Type:** stratification (arithmetic axis, orthogonal to P029 weight)

**What it resolves:**
- Level-dependent modular-form features (Fourier coefficients a_n with n sharing factors with N)
- Atkin-Lehner eigenvalue structure (AL involutions act at fixed level; grouping by level isolates the action)
- Fricke involution and Hecke eigenvalue interactions that factor through N
- Oldform/newform decomposition at fixed level
- Character-structure interactions (combined with `char_conductor | level`)

**What it collapses:**
- Level-invariant features (weight-only, character-only, or Galois-representation-only)
- Any analysis that aggregates across modular curves X_0(N) of differing genus
- The `weight` coordinate (P029) — independent axis; stratifying by level alone tells you nothing about weight-resolved structure

**Tautology profile:**
- **CRITICAL:** For EC↔MF modularity pairs in weight 2, the identity `mf_newforms.level = ec_curvedata.conductor` holds by the modularity theorem. Any cross-side coupling between `level` and `conductor` collapses to the identity under this projection; treat as calibration anchor (F001), not finding. See Section-10 tautology-pair table: add `(level, conductor)` for weight-2 EC↔MF pairs.
- `level_radical`, `level_is_squarefree`, `level_is_prime*`, `level_is_powerful` are deterministic functions of `level` — using more than one is redundant and inflates apparent dimensionality.
- `level` correlates with `Nk2 = level × weight²` (the analytic conductor driver); using `level` alongside raw analytic conductor requires a partial-control argument or P052-style decontamination.

**Calibration anchors:**
- **F001 modularity (EC↔MF):** `mf_newforms.level` matches `ec_curvedata.conductor` on all matched weight-2 newforms with non-trivial L-series. This is the identity that makes the tautology profile above load-bearing.
- **Ramanujan–Petersson bound:** at every level, |a_p| ≤ 2√p for prime p ∤ level. Applies uniformly so any observed violation at a stratum is a data-quality signal, not a level effect.
- **Dimension formulas:** dim S_k(Γ_0(N)) is known exactly; strata at special N (N = 1, level_is_prime, level_is_square) can be cross-checked against classical dimension formulas.

**Known failure modes:**
- **Tautological EC↔MF coupling collapse:** a study that couples MF level to EC conductor across matched pairs will show ρ = 1 identically. Any comparison of MF.level to EC-side numerical features should either decouple the match (study distinct objects) or apply P052 prime decontamination first.
- **Small-level singularities:** level = 1 (S_k(SL_2(Z))), level = 2, 3 have genus-0 modular curves with special behavior (no cusp forms below weight 12 for level 1). Variance-type measurements over all levels without excluding these can yield misleading per-stratum statistics; recommend `level ≥ 11` or explicit exclusion in finite-level analyses.
- **Squarefree-only tools:** some Atkin-Lehner decomposition software assumes `level_is_squarefree`. Strata at non-squarefree level need tool-compatibility check before use.
- **Top-heavy distribution:** levels are concentrated at small-to-moderate values (top observed level = 43,200 with 394 forms; many high-level strata have < 10 forms). Applying P030 without a `MIN_STRATUM_N ≥ 100` filter reproduces Pattern 4 sampling-frame trap.

**When to use:**
- Isolating Atkin-Lehner or Fricke eigenvalue signals at fixed N
- Testing whether a claimed MF↔X coupling is level-mediated (compare within-level rho to pooled rho)
- Oldform/newform multiplicity analyses at fixed N
- Joint stratification with P029 (weight) for dimension-formula sanity checks
- Before claiming a novel MF feature, check whether the signal is explained by level (many "MF phenomena" are restated properties of Γ_0(N))

**When NOT to use:**
- Comparing MF.level directly against EC conductor on matched pairs (tautological via modularity, F001)
- As a proxy for P029 weight — different axis, joint analysis required for full resolution
- On analytic-conductor-driven effects without also controlling Nk2 (level and analytic conductor are correlated via Nk2 = level × weight²)
- In small-level tails (level ≤ 10) without manual sanity checks

---

## Relation to other projections

- **P029 (MF weight):** orthogonal axis. Joint (P029, P030) is the natural MF coordinate pair. Either alone decomposes the Γ_0(N) moduli incompletely.
- **P020 (conductor conditioning on EC side):** becomes redundant for EC↔MF weight-2 matched pairs (level ≡ conductor). Use one or the other for that coupling, not both.
- **P052 (prime decontamination):** **recommended pairing** when studying any numeric feature that has prime structure on both MF and cross-domain side. MF level's prime factorization is itself a prime-structured coordinate; without P052, correlations through level will be prime-mediated by default.
- **Pattern 13:** if F011 or a future zero-spacing specimen survives P028 (Katz-Sarnak), the next stratification axis class to try is *not* another arithmetic conductor-family coordinate (P030 falls in that class) — Pattern 13 redirect suggests preprocessing (P051) or new coordinate classes (representation-theoretic, e.g., P031 character parity) rather than another conductor-family axis.

---

## Suggested tensor invariance entries (for landscape_manifest build)

- F001 (modularity calibration): `P030: +2` — MF level IS EC conductor via modularity, highest-resolution visibility
- F015 (abc/Szpiro rescue, Ergon): `P030: 0` — EC-side specimen; MF level doesn't apply to EC directly. Would require MF-side reconstruction of the abc specimen to probe.
- F011 (GUE deficit): `P030: -1` anticipated — Pattern 13 predicts this is a family-axis stratification that won't resolve the deficit. Actual test is pending; this is a *prediction*, not measurement.

---

## Follow-up tasks this catalog entry motivates

1. **`wsw_F001_via_P030`** — confirm the modularity calibration anchor holds at per-level stratification (should be ρ = 1 ± rounding across all strata with MIN_STRATUM_N ≥ 100).
2. **`catalog_nk2_joint`** — document `Nk2 = level × weight²` as its own derived coordinate, possibly P030_bis or a new P-ID, to avoid confounding in analytic-conductor-driven studies.
3. **`catalog_level_radical`** — separate entry for the radical (squarefree-kernel) projection; distinct from level in how it groups powerful conductors with their squarefree cores.

---

*Draft ends. Per worker protocol, catalog entry is NOT appended to
`harmonia/memory/coordinate_system_catalog.md` directly. SessionA/B to review
and merge via TENSOR_DIFF response.*
