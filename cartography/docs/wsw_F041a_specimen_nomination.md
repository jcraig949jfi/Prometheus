# Specimen Nomination — F041a rank≥2 leading_term slope-vs-`num_bad_primes` monotone ladder

**Specimen ID:** `F041a`
**Label:** `rank2plus_nbp_slope_ladder` — at analytic rank ≥ 2, the conductor-decade slope of `M_1(leading_term)` is monotone-increasing in `num_bad_primes`.
**Tier:** `live_specimen_candidate` — post-block-null, pre-CFKRS-theoretical-match. Promoted from `conjecture_candidate` (previous nomination, 2026-04-18) after W2 block-null survival. Promotion to `live_specimen` pending Pattern-5 theoretical gate.
**Authorship:** Harmonia_M2_sessionC (nomination), Harmonia_workers W1/W2/W3/W4 (follow-up battery).
**Drafted:** 2026-04-18 by Harmonia_worker_T2.
**Supersedes:** `cartography/docs/wsw_F041_specimen_nomination.md` (F041 downgrade doc, 2026-04-18); the "F041a candidate" sub-specimen block of that doc is the seed.
**Status:** DRAFT — awaiting sessionA/B review before merging into landscape tensor / `signals.specimens`.

---

## 1. Observation

From `cartography/docs/keating_snaith_moments_results.json` (Report 4 execution, commit `5a4bdade`) joined with `num_bad_primes` in `cartography/docs/keating_snaith_arithmetic_analysis_results.json` (F1/F4 stratification, commit `2e21872a`):

Slope of `M_1(leading_term)` vs `log(conductor_mid)` across decades [10³, 10⁶), per `(rank, nbp)` stratum:

| rank \\ nbp | 1 | 2 | 3 | 4 | 5 | 6 |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | −0.004 | 0.139 | 0.143 | 0.132 | 0.112 | 0.121 |
| 1 | 0.651 | 0.835 | 0.850 | 0.886 | 0.921 | 0.626 |
| **2** | **1.206** | **1.520** | **1.703** | **1.864** | **1.954** | **2.521** |
| 3 | — | 1.889 | 2.245 | — | — | — |

- **Rank 2:** monotone across all six `nbp` buckets, slope more than doubles (1.21 → 2.52).
- **Rank 3:** monotone across the two adequate buckets (1.89 → 2.25); `nbp=1, 4, 5, 6` below n≥100.
- **Rank 0:** flat (range 0.147, non-monotone, peak at nbp=3).
- **Rank 1:** flat (range 0.294, non-monotone, peak at nbp=5; falls at nbp=6).

The ladder is a **rank-magnitude × bad-prime interaction**, visible only at rank ≥ 2. No equivalent in the rank-0/1 cells where the Katz-Sarnak SO_even/SO_odd dichotomy applies.

---

## 2. Block-null survival (W2)

`cartography/docs/wsw_F041a_block_null_results.json` (commit `24b41571`, 300 permutations, `min_per_triple=100`, seed 20260417). The null shuffles `leading_term` across `nbp` within each `(rank, decade)` block — destroying `E[L | nbp, decade]` while preserving the `(rank, decade)` marginal. **Verdict: `SURVIVES_BLOCK_NULL`.**

Per-rank ladder-discriminator summary (`amp_ratio = real_slope_range / null_slope_mean_range`):

| rank | real slope range | null slope range | amp ratio | corr(nbp, slope) |
|---:|---:|---:|---:|---:|
| 0 | 0.147 | 0.085 | **1.73×** | 0.513 |
| 1 | 0.294 | 0.146 | **2.01×** | 0.074 |
| **2** | **1.316** | **0.046** | **27.6×** | **0.966** |
| 3 | 0.355 | 0.007 | **5.49×** | 1.000 |

Per-`nbp` permutation z-scores at rank 2 (`nbp` with `n_decades≥3`): nbp=2 z=−27.5, nbp=3 z=−30.5, nbp=4 z=−4.56. (nbp=1 and nbp=5,6 2-decade fits are by construction degenerate under the slope-through-two-points null; included in the amp-ratio metric but not in the z-audit.)

**Pass gate:** rank 2 meets all three bars simultaneously — all |z|≥3.0 on 3-decade fits, amp ratio 27.6 × ≫ 5, corr(nbp, real_slope) = 0.966 ≥ 0.9. Rank 0/1 fail the amp and correlation bars; rank 3 passes by correlation but only 2 `nbp` points. **The rank-2 ladder is not a `(rank, decade)`-marginal artifact.**

Sanity null (within-cell shuffle) gives degenerate z-scores as expected (max |z| < 2.01, reported in `z_scores_cell_within_null_SANITY`). Pipeline integrity confirmed.

---

## 3. What F041a is NOT

### 3a. NOT a Galois-image proxy (W3)

`cartography/docs/rank2_P039_vs_P021_stratification_results.json` (commit `64a35779`, n=222,288 rank-2 rows, conductor [10³, 10⁶)). Parallel stratification at rank 2:

| stratification | slope range | n_strata |
|:--|---:|---:|
| `P021` `num_bad_primes` | **1.316** | 6 |
| `P039` `nonmax_count` (Galois image) | 0.305 | 3 |
| `P039` `has_3` marginal | 0.152 | 2 |
| `P039` `has_2` marginal | 0.014 | 2 |
| joint `P021 × P039` | 1.240 | 13 |

- `corr(nbp, nonmax_count) = 0.340` at rank 2 — weak overlap.
- P021's slope range is **4.3× larger** than the best P039 marginal. Joint stratification does NOT lift it — P021 carries the resolving power on its own.
- **Verdict (W3): `P021_SHARPER`.** `num_bad_primes` is NOT a Galois-image effect dressed up as a bad-prime count. The ladder is an `nbp` phenomenon per se, not a projection of `nonmax_primes`.

### 3b. NOT a pure Euler-product artifact (W4, partial)

`cartography/docs/euler_product_deflation_results.json` (commit `1c08e40e`, rank-0 sample n=5000, N_PRIMES=25, sub-decades [10⁵, 3·10⁵) and [3·10⁵, 10⁶)):

- Per-curve truncated Euler product `a_E(1) = ∏_{p≤97} L_p(1,E)` correlates with `leading_term` at Pearson 0.874 / Spearman 0.949 → truncation captures most of the rank-0 multiplicative content.
- After deflation `L / a_E(1)`, rank-0 `M_k / RMT` ratios at k=1..4 drop from (2.89, 13.3, 87.6, 774) to (2.22, 5.74, 16.8, 55.0) — deflation flattens slopes at k=3,4 (reduction ≈2×) but worsens at k=2. Residual multiplicative tail remains.
- W4 is **rank 0 only**. The F041a ladder lives at rank ≥ 2, and rank-0 is the regime the Euler-product removal actually reaches. That under-deflation at rank 0 means we cannot bound the fraction of the rank≥2 slope that would survive full Euler removal. The conservative read: if the full Euler product were divided out per curve, some of the nbp-dependence is expected to cancel (each bad prime contributes a local factor ≠1 at `s=1`), but the slope amplification in `log X` and the cross-rank concentration at rank ≥ 2 are NOT obvious first-order consequences of the product's additive log.

**Conclusion:** W4 cannot rule out a partial arithmetic-factor contribution to the ladder, but it cannot explain away the rank-concentration (only rank ≥ 2) or the amp ratio (27.6× at rank 2 vs. 1.73× at rank 0). F041a is not simply "the Euler product reappearing."

---

## 4. Invariance profile

Projections applied in the F041a nomination battery and their effect on the specimen:

| Projection | Role | Effect on F041a |
|:--|:--|:--|
| **P023** rank | primary axis | ladder exists only at rank ≥ 2 (rank 0/1 flat); feature is rank-conditional, not rank-invariant. |
| **P020** conductor decade | primary axis | slope is *defined* along this axis; decade-binning is the measurement, not a resolver. |
| **P021** `num_bad_primes` | primary axis | sharpest resolver on the rank-2 slice (range 1.32); the specimen lives on this axis. |
| **P028** Katz-Sarnak family | rank-parity proxy | rank-2/3 sit outside the SO_even/SO_odd dichotomy of rank-0/1 → classical Katz-Sarnak does not predict the ladder. |
| **P039** Galois ℓ-adic image | near-axis test | `nonmax_count` slope range 0.305 vs P021 1.316; joint 1.24. P039 does NOT subsume P021. Pattern-13-adjacent. |
| **Euler deflation** (no P-ID yet) | arithmetic-factor removal | W4 rank-0 partial deflation (Pearson 0.87) flattens k=3,4 slopes ~2×; rank≥2 deflation not yet executed. |
| **Cross-nbp block null** (within-(rank, decade)) | null-discriminator | rank 2 amp 27.6×, corr 0.966; **survives.** |
| **Within-cell shuffle** (sanity null) | pipeline check | degenerate z as expected; pipeline clean. |

**Pattern-20 hygiene:** every slope reported per-(rank, nbp, decade) cell with n≥100 gate; sparse cells flagged and excluded from slope fits per `wsw_F041a_block_null_results._meta.pattern_20_notes`.

**Pattern alignment:**
- **Pattern 18** (family-dependent observable, axis-class orphan) — the "family" here is a rank-parity-**extended** Katz-Sarnak grouping (rank ≥ 2 = non-parity family). F041a's visibility is conditional on the rank-2+ family class.
- **Pattern 20** (stratification reveals pooled artifact) — inverse direction: the ladder is **hidden** by the pooled (rank, decade)-only view and only surfaces after P021 stratification. Canonical Pattern-20 exhibit: pooled rank-2 slope ≈1.93; stratified range 1.21..2.52.
- **Pattern 13-adjacent** (two-axis-kills-within-class collapse) — P039 and P021 disagree on resolving power; P021 does not project to any P039 marginal. The ladder is NOT a P039 class artifact.

---

## 5. What to test next (Pattern 5 gate)

Pattern 5 is the promotion gate from `live_specimen_candidate` to `live_specimen`. Theoretical comparison queue, in priority order:

1. **CFKRS moment prediction for L''(1,E)/2! at rank 2.** Conrey-Farmer-Keating-Rubinstein-Snaith moment conjectures are developed primarily for rank 0 (central value) and in less detail for the derivative; the second-derivative / rank-2 regime is sparsely covered in the published canon. Concrete question: **does the rank-2 CFKRS arithmetic factor `a_{r=2}(k)` carry an explicit `num_bad_primes` dependence that matches the ladder?** If yes → F041a becomes calibration (demotes to `live_specimen-calibration-alignment` anchor). If CFKRS at rank 2 is genuinely under-developed → F041a is frontier.
2. **Joint `P021 × P026` (semistable vs additive) at rank 2.** See sibling worker T5 output when available. Hypothesis: the ladder is driven by additive-reduction primes (larger local factors) rather than `nbp` cardinality per se.
3. **Joint `P021 × bad-prime-set` at rank 2.** See sibling worker T3 output. Hypothesis: specific prime *identity* (small primes 2, 3, 5 carry larger Euler-factor contributions) explains more than cardinality. If yes, refines F041a to a prime-set specimen; if slope still tracks cardinality, cardinality is the real resolver.
4. **Full Euler deflation at rank 2.** Extend W4 from rank-0 to rank-2 (needs rank-2 sample with complete `lfunc_lfunctions.euler_factors` coverage) and check whether the ladder survives division by per-curve `a_E(1)` at rank 2. Direct falsifier for "ladder is the Euler product."
5. **Extend to rank 4+** once F030/F033 lfunc coverage cliff is unblocked. If the monotone-in-nbp slope continues past rank 3, specimen generalizes to a rank-magnitude scaling law; if not, the specimen is specifically a rank-2/3 regime.

---

## 6. Proposed tensor entry

Add row `F041a` to `FEATURES` in `harmonia/memory/build_landscape_tensor.py` (held for sessionA tensor-diff merge):

```diff
+    {"id": "F041a", "label": "rank≥2 leading_term slope-vs-num_bad_primes monotone ladder",
+     "tier": "live_specimen_candidate", "n_objects": 222288,
+     "description": "At analytic_rank ≥ 2, slope of M_1(leading_term) vs log(conductor) is "
+                    "monotone-increasing in num_bad_primes across nbp∈{1..6} (rank 2: 1.21 → 2.52). "
+                    "Survives cross-nbp block-null within (rank, decade) at amp 27.6× / corr 0.97 (W2). "
+                    "P021 range 1.316 vs best P039 marginal 0.305 → NOT a Galois-image proxy (W3). "
+                    "Rank-0 W4 partial Euler deflation does not kill (rank-2 deflation not yet run). "
+                    "Pattern 5 gate: rank-2+ CFKRS moment comparison outstanding."},
```

Initial invariance row (cells pending full audit; encoded per battery-v3 convention: +2 = sharp resolver, +1 = partial, 0 = untested / not-applicable, −1 = collapses feature):

| Feature | P020 | P021 | P023 | P026 | P028 | P039 |
|---|---:|---:|---:|---:|---:|---:|
| F041a | +1 | **+2** | **+2** | 0 | +1 | 0 |

Justifications:
- `P020 = +1` — decade is the measurement axis (slope is defined over it), not a resolver.
- `P021 = +2` — sharpest resolver on the rank-2 slice; the specimen's defining axis (W2 + W3).
- `P023 = +2` — feature exists only at rank ≥ 2; the rank-class enumeration is structural, not noise.
- `P026 = 0` — semistable/additive joint untested; sibling worker T5.
- `P028 = +1` — Katz-Sarnak rank-parity family does NOT predict the ladder at rank ≥ 2, but the rank-0/1 flatness is consistent with SO_even/SO_odd.
- `P039 = 0` — P021 is sharper than any P039 marginal tested; P039 does not subsume (W3), but joint orthogonality not yet audited.

Feature edge candidate:

```diff
+    {"from": "F041a", "to": "F041", "relation": "survives_as_sub_specimen",
+     "note": "F041 (convergence rate vs rank) downgraded to Katz-Sarnak-calibration "
+            "after F1 first-moment deflation. F041a is the residual sub-specimen "
+            "that survived W2 block-null at rank ≥ 2."},
```

---

## 7. Next-step followups (queue for sessionA seeding)

1. **`wsw_F041a_cfkrs_rank2_rank3_comparison`** — compute CFKRS second-moment / rank-2 L''-ratio arithmetic factors where available; audit whether any existing CFKRS form predicts monotone `a(k)` in `num_bad_primes` at rank ≥ 2. Pattern-5 gate; this is the promotion blocker.
2. **`wsw_F041a_P026_joint_rank2`** — joint `P021 × P026` (semistable vs additive) slope table at rank 2 over decades [10³, 10⁶). Falsifier for "it's additive reduction primes, not cardinality."
3. **`wsw_F041a_bad_prime_set_rank2`** — joint `P021 × bad-prime-set` at rank 2, small-p subset (primes 2, 3, 5, 7 membership as explicit markers). Falsifier for "cardinality is a proxy for prime-identity."
4. **`wsw_F041a_euler_deflation_rank2`** — extend W4 to rank-2 sample with full `euler_factors` coverage; recompute slope-vs-nbp post-deflation. Direct falsifier for "ladder is the Euler product."
5. **`wsw_F041a_rank_extension`** — re-execute slope-vs-nbp at ranks 4 and 5 once F030/F033 coverage cliff is addressed. Tests whether F041a generalizes to a rank-scaling law or is specifically rank-2/3.
6. **`audit_F041a_decade_10^6_cliff`** — the nbp=6 slope at rank 2 (2.52) rests on n=17,928 in decade [10⁵, 10⁶) and a thin n=1,317 at [10⁴, 10⁵); verify behaviour when decade [10⁶, 10⁷) coverage is added (currently gated by F030 cliff).

---

## 8. Language-discipline check

- "Ladder", "slope-vs-nbp", "monotone", "stratification", "block-null survival", "Pattern-5 gate" used consistently.
- No "cross-domain" or "bridge" language.
- Pattern-18 family-class extension (rank ≥ 2 as non-SO-even/odd family) described as an *observable*, not a new RMT group.
- Ratios and ranges reported with explicit numerators (no "roughly" where the number is computed).
- `live_specimen_candidate` tier chosen deliberately: specimen survives block-null (W2), resolves against Galois-image (W3), is not trivially explained by arithmetic factor (W4 partial), but the theoretical comparison (Pattern 5) has not yet closed.

---

*End of nomination. Drafted by Harmonia_worker_T2 per sessionA task `wsw_F041a_specimen_nomination`. Supersedes the F041a candidate block in `wsw_F041_specimen_nomination.md`. Catalog entry NOT yet created; tensor row NOT yet merged — held for sessionA/B review.*
