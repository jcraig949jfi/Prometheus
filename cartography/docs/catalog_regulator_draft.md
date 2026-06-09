# Catalog Entry Draft — P101 EC regulator stratification

**Task:** `catalog_regulator`
**Drafted by:** Harmonia_M2_sessionD, 2026-04-17 (tick 18)
**Reserved P-ID:** `P101` (via `agora.work_queue.reserve_p_id()` at claim-time; note: `P040` was assigned to a non-stratification slot, so this entry is `P101` by the counter).
**Status:** DRAFT — awaiting sessionA/B review before merging into `harmonia/memory/coordinate_system_catalog.md`
**Proposal:** insert under Section 4 (Stratifications) after P039 Galois ℓ-adic image and before Section 5.
**Reference:** `cartography/docs/ec_harvest_triage.md` (sessionD), harvest row "Regulator — 1960s — covolume of Mordell-Weil lattice".

---

## P101 — EC regulator stratification

**Code:** `WHERE regulator BETWEEN lo AND hi` (or coarse bins) on `ec_curvedata.regulator` (float, 3,824,372 rows, zero NULLs). Natural sub-stratifications: log-magnitude bins, per-rank bins (required because rank-0 regulator is a degenerate cell).
**Type:** stratification (magnitude axis on Mordell-Weil lattice; BSD-formula factor)

**What it resolves:**
- **Covolume of the Mordell-Weil lattice.** The regulator is `det(⟨P_i, P_j⟩)` where `⟨·,·⟩` is the canonical Néron-Tate height pairing on a basis of `E(Q)/torsion`. Encodes how "spread out" the rational points are.
- **BSD leading-term factor.** The BSD conjecture predicts
    `L^(r)(E, 1) / r! = (Ω · regulator · ∏_p c_p · |Ш(E/Q)|) / |E(Q)_tors|²`
  where `r = rank = analytic_rank` (F003 anchor). Regulator is the load-bearing Mordell-Weil-lattice factor; the other factors are archimedean period (Ω), Tamagawa product (`c_p`), Sha (via `P038`), and torsion (via `P024`).
- **Rank-dependent Mordell-Weil structure.** Regulator grows with rank in both minimum and mean (empirically): rank-1 mean 7.99, rank-2 mean 9.50, rank-3 mean 20.9, rank-4 mean 32.0 (see summary below). Higher-rank curves have "further-apart" rational points, consistent with heuristic height-growth conjectures.
- **Silverman / Néron height-gap probe.** The minimum non-zero regulator is bounded below by classical inequalities; the observed minima (0.009 at rank 1, 1.50 at rank 4, 14.8 at rank 5) probe the height-gap conjectures.

**What it collapses:**
- **Rank 0 collapses to a single value.** All 1,404,510 rank-0 EC in `ec_curvedata` have `regulator = 1.000000` exactly (convention: empty product for empty lattice). `P101` is degenerate for rank-0 questions; use `P023 rank = 0` as the effective stratifier instead.
- **Isogeny-class fine structure.** Curves in the same isogeny class have regulators differing by a bounded factor (isogeny degrees); pooling across isogeny classes while comparing regulators mixes these factors.
- **Lattice-shape information.** `P101` reports only the determinant; the *shape* of the lattice (orthogonality, short-vector structure) is collapsed. For shape questions, use the full height-pairing matrix.

**Tautology profile:**
- **P101 ↔ P023 rank (trivial tautology at rank 0).** `rank = 0 ⇒ regulator = 1`. Pooling across ranks without reporting the rank distribution treats the rank-0 spike at `regulator = 1` as if it were a signal. Always stratify by rank first, then analyze regulator within each rank ≥ 1 cell.
- **P101 ↔ leading_term (BSD identity, Pattern 1 formula lineage).** `leading_term = Ω · regulator · ∏c_p · |Ш| / |tors|²`. Any correlation claim between regulator and leading_term is reporting the BSD identity, not structural information. The only non-tautological correlation is `regulator × (Ω · ∏c_p · |Ш| / |tors|²)` vs `leading_term` — with the constraint that the ratio is 1 by BSD.
- **P101 ↔ P038 Sha (BSD-formula joint factor).** Joint `regulator × Sha` enters BSD multiplicatively; at fixed rank, `regulator · |Ш|` is determined by `leading_term` up to the other factors. Independent-axis use double-counts the BSD identity.
- **P101 ↔ conductor (heuristic scaling, not strict tautology).** Heuristic height-conjecture bounds (e.g., Lang's conjecture, Silverman) predict `regulator ≲ log(conductor)^{f(rank)}` for explicit functions `f`. Within each rank bin this is a predicted scaling, and any observation aligning with it is calibration of the heuristic, not discovery. Use `P020 × P023 × P101` joint stratification for clean effects.

**Stratum-count summary (live `ec_curvedata` queries, 2026-04-17):**

| Rank | n | min regulator | max regulator | mean |
|---|---|---|---|---|
| 0 | 1,404,510 | 1.000000 | 1.0000e+00 | 1.0000e+00 |
| 1 | 1,887,132 | 0.008914 | 1.0471e+04 | 7.9850e+00 |
| 2 | 493,291 | 0.015169 | 4.4695e+03 | 9.5015e+00 |
| 3 | 37,334 | 0.118694 | 1.3171e+03 | 2.0934e+01 |
| 4 | 2,086 | 1.504345 | 1.7003e+02 | 3.1977e+01 |
| 5 | 19 | 14.790528 | 4.6846e+01 | 3.1115e+01 |

Total: 3,824,372 rows; zero NULLs.

**Small-n strata discipline:**
- At rank ≤ 3, all strata are above `n = 100` by wide margins. No small-n concern.
- **Rank 4: n = 2,086.** Adequate at the marginal level, but joint stratifications (`rank=4 × P020 conductor × P101 log-bin`) rapidly fall below 100 per cell. Pattern 9 (delinquent frontier) applies jointly with F030/F033.
- **Rank 5: n = 19.** Below adequacy threshold. Any rank-5 claim about regulator structure is a point-estimate on 19 observations and should be reported with explicit coverage caveat (Pattern 9).
- **Log-magnitude bins at rank 1**: regulator ranges 0.009 to 10,471, spanning ~6 decades. Log-bins of width 1 (decade) cover the distribution; expect n per decade-bin to range from single-digit (extreme tails) to >500K (central bulk).

**Calibration anchors:**
- **Rank-0 regulator = 1 convention.** All 1,404,510 rank-0 EC have exactly `regulator = 1.0`. Any deviation = data-quality violation (Pattern 7 anchor).
- **BSD identity** for proved cases (rank 0-1, Kolyvagin / Gross-Zagier): `L^{(r)}(1)/r! = Ω · regulator · ∏c_p · |Ш| / |tors|²` holds exactly on verified curves. LMFDB's `leading_term` column should match the RHS on a per-row basis.
- **Regulator positivity.** For rank ≥ 1, `regulator > 0` (Néron-Tate height pairing is positive-definite). Any non-positive regulator = data-quality violation.
- **Silverman height-difference bound** (1990): |h_canonical - h_naive| ≤ c(E) for explicit c(E). Candidate calibration for any computation derived from naive heights.

**Known failure modes:**
- **Pooling across ranks without rank stratification.** The 1.4M rank-0 `regulator = 1` spike will dominate any pooled magnitude analysis.
- **Reporting `regulator × sha` correlation as a finding.** Pattern 1 — they appear multiplicatively in BSD, so the correlation is an identity not a signal.
- **High-rank (≥ 4) extrapolation.** 2,086 rank-4 and 19 rank-5 curves are the delinquent frontier (F030/F033). Any regulator scaling "observed at all ranks" is effectively a rank ≤ 3 observation.
- **Log-regulator vs conductor confound.** Both regulator and conductor scale with "how arithmetically complex the curve is" in rank-dependent ways. Pre-control for conductor (`P020`) before claiming a regulator trend.

**When to use:**
- **BSD-formula consistency checks.** Per-row verification of `leading_term = Ω · regulator · ∏c_p · |Ш| / |tors|²` is the cleanest instrument-health check available for rank ≥ 1.
- **Mordell-Weil height-distribution analyses** — any question about the distribution of heights of rational points factors through regulator (plus higher-order lattice-shape info).
- **Height-gap conjecture tests** — stratify by rank, look at minimum regulator within each rank-bin, compare to Silverman-type lower bounds.
- **Joint `P101 × P020 × P023`** for cleanest rank-specific conductor-regulator scaling analyses.

**When NOT to use:**
- **At rank 0** (degenerate — trivially 1).
- **Jointly with `leading_term` as independent axes** (BSD formula lineage).
- **Jointly with `P038` Sha at fixed rank + conductor** (BSD identity collapses the joint axis).
- **For cross-family comparisons** (regulator is EC-specific; the MF-side analog requires different normalization).

**Related projections:**
- **P023 rank** — tautology at rank 0 (degenerate) and joint-factor in BSD for rank ≥ 1.
- **P020 conductor conditioning** — required pre-control for height-scaling heuristics.
- **P038 Sha** — joint BSD-formula factor (sessionC merged this tick, before this draft).
- **P024 torsion** — BSD denominator term; treat jointly not independently.
- **P036 Root number** — rank-parity-aliased via F003.

**Follow-ups this entry motivates:**
1. `audit_bsd_identity_per_row` — for each EC row with rank ≤ 1, verify `leading_term ≈ Ω · regulator · ∏c_p · |Ш| / |tors|²` within numerical precision. Candidate calibration anchor (F010 or next free, not to be confused with the F010 *feature* which is the NF backbone specimen — use F-series for anchors and feature-ID-series for specimens; name collision is unfortunate).
2. `wsw_regulator_vs_conductor_per_rank` — within each rank ∈ {1, 2, 3}, test the predicted `regulator ≲ (log N)^{f(r)}` heuristic scaling. Expect calibration-level agreement for small f; any deviation is a Lang-conjecture-adjacent frontier.
3. `catalog_leading_term_as_derived_projection` — document `leading_term` as an *output* of the BSD factor product, not an independent axis. Add to Section 8 tautology pairs.
4. `probe_rank_5_regulator_cliff` — the 19 rank-5 curves are Category-3 specimens per Pattern 16. A dedicated walk (once higher-rank lfunc data is materialized, per F033 coverage cliff) is warranted.

*End of draft.*
