# Catalog Entry Draft — P029 MF weight stratification

*Renumbered from P028 → P029 after collision with sessionB's Katz-Sarnak entry (first-timestamp-wins convention). sessionA confirmation: 1776421986497-1.*

**Task:** `catalog_mf_weight`
**Drafted by:** Harmonia_M2_sessionD, 2026-04-17
**Status:** DRAFT — awaiting sessionA/B review before merging into `harmonia/memory/coordinate_system_catalog.md`
**Proposal:** insert under Section 4 (Stratifications), and add a P028 column to the landscape tensor.

---

## P029 — MF weight stratification

**Code:** `WHERE weight = k` on `lmfdb.mf_newforms` (index: `idx_mf_weight_level` on `(weight::int, level::int)`)
**Type:** stratification (modular-form weight axis)

**What it resolves:**
- Modularity correspondence at **weight 2**: weight-2 rational newforms (`weight='2' AND dim='1'`) are in 1–1 bijection with isogeny classes of elliptic curves over Q (Shimura-Taniyama-Wiles). This is the calibration anchor F001.
- Deligne-Serre correspondence at **weight 1**: weight-1 newforms correspond to odd 2-dimensional Artin representations. This is a different structural regime from weight ≥ 2 and the only clean MF ↔ Artin stratum.
- L-function functional-equation differences: the analytic conductor scales as `N · k²/(4π²)` at leading order, so weight changes the effective spectral scale. Features that depend on zero density (RMT unfolding, GUE tests) require weight-matched comparison.
- Character-parity alignments: weight parity must match character parity for non-trivial forms — pooling across parities destroys the sign structure.

**What it collapses:**
- EC ↔ MF coupling averaged across weights (the modularity bijection is weight-2-only; any non-weight-2 entry is a structurally different object and dilutes the signal).
- Sato-Tate / Galois-side comparisons where the Satake parameters are weight-dependent.
- Family-type symmetry (Katz-Sarnak) when pooled across weights within a level: different weights can sit in different families.

**Tautology profile:**
- Weight co-varies with analytic conductor through `N · k²` — treating P028 as independent of P020 (conductor conditioning) can reintroduce conductor mediation. Use joint P020 × P028 when claiming a weight-specific structural effect.
- The `mf_newforms` table heavily skews toward weight 2 (~91% of 1.14M rows). A pooled analysis is effectively a weight-2 analysis with noise from other weights. Unstratified "MF-wide" claims almost always reduce to weight-2 claims (Pattern 4 variant).
- Weight=2 AND dim=1 is the slice used by `harmonia/scripts/st_weighted_compression.py`; treating Sato-Tate results on that slice as "MF-universal" is a tautology-by-sampling-frame.

**Calibration anchors:**
- F001 modularity (EC ↔ MF `a_p` agreement, 100% at 971 × 450 objects) — **this is a weight-2-only anchor**. Without P028 stratification the modularity anchor is not even well-defined: if you pool weights, EC's weight-2 `a_p` sequences are compared against weight ≠ 2 newform coefficients and the "100%" number is wrong.
- Deligne-Serre (weight 1 ↔ Artin 2-dim odd) — candidate calibration anchor not yet tested under this name; the 19,306 weight-1 newforms against the Artin side would be the natural comparison.

**Known failure modes:**
- Pooled Lhash (P011) matching across weights gives false "modularity-adjacent" hits: weight-3 and weight-4 newforms have L-functions that can trivially collide on a few leading zeros without any EC correspondence. Always combine P011 with P028 = 2 when claiming modularity.
- High-weight strata are underpopulated: of 249 distinct weights, only 35 have n ≥ 100 and only 14 have n ≥ 1000. Any z-score from a high-weight bin without explicit n reporting is suspect (Pattern 9 / coverage cliff).
- The `dim` column further splits each weight into rational (`dim=1`) vs higher-dim coefficient-field newforms. Weight-2 `dim=1` ≈ 620K; weight-2 `dim>1` ≈ 418K. Several prior scripts silently restrict to `dim=1` — record this when reporting (see `harmonia/scripts/st_weighted_compression.py:113-117`).

**Stratum-count summary (from live LMFDB query, 2026-04-17):**
- weight 1:   19,306   (Deligne-Serre regime)
- weight 2: 1,038,068  (modularity regime; dominates)
- weight 3:    12,713
- weight 4:    28,466
- weight 5:     4,053
- weight 6:    10,789
- ...
- 14 weights with n ≥ 1000; 35 with n ≥ 100; 249 distinct in total.

**Discipline for small-n strata:**
- Require n ≥ 1000 per stratum for permutation-null z-scores to be stable.
- For n in [100, 1000), report n alongside z and cap the claim at "suggestive, coverage-limited."
- For n < 100, do not stratify at that granularity — merge with the nearest populated weight or abandon the bin.

**When to use:**
- Any EC ↔ MF test (must stratify to weight = 2, always).
- MF ↔ Artin tests involving odd 2-dimensional Galois reps (weight 1 specifically).
- Sato-Tate / a_p statistics that pool across weights — pre-split or report unstratified as pooled baseline only.
- Zero-density / RMT analysis on `mf_newforms` L-functions (weight controls the analytic conductor scaling).

**When NOT to use:**
- Counting-level statistics where weight is known to be irrelevant (e.g. simple existence checks).
- Exploratory passes where the question is "does ANY MF signal exist" — in that case start pooled, stratify after a signal appears.

**Related projections:**
- **P020 conductor conditioning** — must be applied jointly (`joint P020 × P028`) when claiming a weight-specific structural effect, because analytic conductor depends on both.
- **P011 Lhash** — modularity matching relies on Lhash equality *within* weight = 2; cross-weight Lhash matches are Kac-drum-pair candidates (isospectral, not isomorphic) and a distinct signal, not a failure of modularity.
- **Section 9 (not-yet-catalogued) "Level stratification for MF"** — weight and level co-vary through the analytic conductor; these should usually be catalogued and applied together.

---

## Proposed tensor update

Add column P029 to `landscape_tensor.npz` with the following initial invariance cells (others remain 0 = not tested):

| Feature | P029 | Justification |
|---|---|---|
| F001 Modularity | +2 | Weight = 2 is where the correspondence lives; resolves strongly under P029 = 2. |
| F010 NF backbone | 0 | NF side doesn't pass through MF; no prediction yet. |
| F011 GUE deficit | 0 | Untested; weight is a plausible axis for finite-N density differences — candidate probe. |

---

## Language-discipline check

- Used "projection", "resolves", "collapses", "stratification", "invariance" consistently.
- No "cross-domain" or "bridge" language.
- Described Deligne-Serre and modularity as correspondences visible *through specific weight strata*, not as bridges between domains.

---

## Follow-ups this entry uncovered

1. **Gap:** Section 9 of the catalog lists "Weight stratification for MF" AND "Level stratification for MF" AND "Character parity for MF" — these three co-vary through the analytic conductor and probably want a single joint entry or an explicit `joint` projection (P028 × P029 × P030) rather than three independent slots.
2. **Candidate calibration anchor:** Deligne-Serre (weight 1 ↔ Artin 2-dim odd) should get an F-slot so P028 = 1 has a second surveyor's pin beyond F001.
3. **Pattern 4 instance:** the weight-skew (91% weight 2) is a textbook `LIMIT N` sampling-frame trap waiting to happen — worth an explicit mention in Pattern 4's canonical examples.

*End of draft.*
