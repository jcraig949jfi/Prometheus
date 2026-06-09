# F041a — Rank-2+ leading-term slope-vs-num_bad_primes monotone ladder

**Status:** `live_specimen` (post-2026-04-18 promotion, 5 kill-test survivors)
**Supersedes:** `F041` (rank-dependent Keating–Snaith convergence) — demoted to first-moment drift on 2026-04-18 when sessionC's `keating_snaith_arithmetic_analysis` identified the real resolving axis as the rank-2+ × num_bad_primes interaction.
**Specimen ID (signals.specimens):** `62`
**n_objects:** 222,288 rank-2 joined rows (primary); rank-3 slope reported at n_decades=2 only.
**Drafted-by:** Harmonia_M2_sessionC (W2 block-null survival 2a3f6c37); nomination Harmonia_worker_T2; finalized Harmonia_M2_sessionB 2026-04-21 under task `wsw_F041a_ladder_catalog`.

---

## 1. Claim

At analytic rank ≥ 2, the slope of the first moment `M_1(leading_term)` across conductor decades is **monotone-increasing in `num_bad_primes`**. At ranks 0 and 1 the slope is flat in nbp. The interaction is rank-specific: it does not exist in the parity-symmetry regime (Katz–Sarnak SO_even / SO_odd) that covers rank 0 and rank 1.

Rank-2 slope table (n=222,288 joined):

| nbp | 1 | 2 | 3 | 4 | 5 | 6 |
|---:|---:|---:|---:|---:|---:|---:|
| slope | 1.206 | 1.520 | 1.703 | 1.864 | 1.954 | 2.521 |
| n (rank=2, nbp, all decades) | ~40K | ~38K | ~57K | ~50K | ~22K | ~17K |

Rank-3 slope table (subset with n ≥ 100 per (nbp, decade), 2 decades):

| nbp | 2 | 3 |
|---:|---:|---:|
| slope | 1.889 | 2.245 |
| n_decades | 2 | 2 |

---

## 2. Why this matters

1. **Not predicted by Katz–Sarnak.** The KS symmetry-type axis (SO_even vs SO_odd) partitions rank-0 vs rank-1. Rank-2+ sits outside that dichotomy; no off-the-shelf KS machinery predicts a monotone `nbp` slope ladder there.
2. **Survives cross-`nbp` block-shuffle** (sessionC W2, commit 2a3f6c37; 300 permutations; min_per_triple=100; seed 20260417). At rank-2: amp ratio 27.6× (real slope range 1.316 vs null 0.046), corr(`nbp`, slope) = 0.966. All pass-gate bars met simultaneously.
3. **Not a Galois-image proxy** (sessionC W3, commit 64a35779). At rank-2: `P021 num_bad_primes` slope range 1.316 vs best `P039 nonmax_count` marginal 0.305 (4.3× separation). `corr(nbp, nonmax_count) = 0.340` — weak overlap.
4. **Not additive-reduction-only** (T3, commit 68225787). `P026 semistable vs additive` split at rank-2: the ladder lives in the **semistable** half (slope range 0.570 vs 0.279 additive; ratio 0.489 well below the 0.8 "additive-carries-it" threshold). Counterintuitive — points toward a multiplicative-ramification effect, not Kodaira type.
5. **Not a specific-prime artifact** (T5, commit d9c646d9). Joint `P021 × bad-prime-set` at rank 2: no single Mazur–Kenku prime dominates (max |slope_diff| = 0.56 for has_2, below the 1.0 ladder threshold). Effect is carried by the *count* of bad primes, plus modest lift from having {2, 3} in the set.
6. **Conductor-controlled** (U_A, commit 4a046a81). Joint OLS with narrow 0.1-decade sub-bins at rank-2: `b_nbp z = 3.37` (above the z ≥ 3 threshold). Within-decade conductor drift is real but does not explain the ladder.

---

## 3. Pattern 30 status

**Graded severity Level 1 — WEAK_ALGEBRAIC** (Pattern library entry, 2026-04-19 upgrade).

The CFKRS arithmetic factor `a_E(k)` carries `num_bad_primes` structure. A correlation between `slope(M_1)` and `nbp` therefore has a partial algebraic component from the arithmetic factor's own `nbp`-dependence — not a forced identity (like F043's Level 3 BSD rearrangement) but not definitionally independent either.

Per Level-1 discipline: the claim must go beyond the direction the algebra forces. F041a does this. The algebra-induced direction is "some monotone dependence at rank 0 as well"; observation shows rank 0/1 are **flat** in `nbp`, while rank 2+ carries the ladder. That rank-magnitude selectivity is not predicted by the arithmetic factor alone.

**The Pattern 30 gate and the Pattern 5 gate collapse to the same gate here:** if a CFKRS rank-2 SO(even) closed-form predicts the monotone-in-`nbp` pattern quantitatively → F041a demotes to calibration / algebraic consequence. If not → fully frontier. This is open.

**LINEAGE_REGISTRY tag:** `algebraic_lineage` (dispatches to `CouplingCheck`); current verdict `WEAK_ALGEBRAIC` → `WARN` under gen_06 sweep runner.

---

## 4. Invariance profile (tensor row)

Current tensor state (resolved via `agora.tensor.resolve_row('F041a')`):

| Projection | Cell | Role |
|:--|---:|:--|
| P020 conductor decade | **+2** | measurement axis (slope defined across it) |
| P021 num_bad_primes | **+2** | sharpest resolver; specimen's defining axis |
| P023 analytic rank | **+2** | rank-2+ selectivity is the structural filter |
| P026 semistable/additive | **+2** | effect in semistable half, counterintuitive |
| P104 block-shuffle null | **+2** | cross-nbp null survival (amp 27.6×) |
| P025 CM | **−1** | no CM structure resolves the ladder |
| P036 isogeny class | **−1** | isogeny does not carry |
| P039 Galois ℓ-adic image | **−1** | `nonmax_count` does not subsume `nbp` |

Five +2 cells, three kill cells. Density for this row: 8/37 = 21.6% (well above tensor-wide 9.07%).

**Pattern 18 relation:** F041a is visible across all five +2 projections at rank ≥ 2 — a VACUUM-shape fragment of the EXHAUSTION pattern. The resolving axis *within* the rank-2+ regime is `num_bad_primes` (P021); but the *family-class* axis (the thing that picks out "rank ≥ 2" as the regime where the ladder lives) is not named as a P-ID in the current catalog. Candidate promotion: a rank-magnitude family-class axis distinct from the parity SO-even/SO-odd dichotomy.

---

## 5. What F041 → F041a rename documents

- **Tensor (authoritative):** F041 already removed from the FEATURES list; F041a registered with the 8-cell invariance row above. No ID reuse — F041 retired permanently per VERSIONING Rule 5 (semantic stability).
- **Lineage edge:** `{"from": "F041a", "to": "F041", "relation": "supersedes", "note": "F041 (rank-dependent convergence) was first-moment drift; F041a is the residual ladder that survived W2 block-null at rank ≥ 2"}` — held for tensor-diff merge by sessionA when the next tensor rebuild occurs.
- **signals.specimens:** specimen_id `62` carries the F041a claim. No separate F041 specimen was ever registered (it was demoted before reaching registration).

---

## 6. Rank-3 verification status

**From sessionC W2 at n ≥ 100 per (nbp, decade):** only `nbp ∈ {2, 3}` satisfy the coverage bar, giving a 2-point slope of (1.889, 2.245) across 2 decades each. Monotone in the narrow window but fragile.

**bsd_joined / ec_curvedata coverage at rank 3** (verified 2026-04-21 against `lmfdb.ec_curvedata`, n_rank3 = 37,334):

| nbp | count | coverage vs rank-2 pattern |
|---:|---:|:--|
| 1 | 27,959 | dominates — but Pattern 4 hazard: rank-3 nbp=1 = mostly prime-conductor Griffin–Ono construction, not a random sample |
| 2 | 1,509 | thin |
| 3 | 4,031 | adequate |
| 4 | 3,200 | adequate |
| 5 | 612 | thin |
| 6 | 23 | no coverage |

**Conclusion for rank-3 extension:**

1. Rank-3 has sufficient raw-count coverage at `nbp ∈ {3, 4}` for 3–4 decade fits; the `nbp ∈ {2, 5}` regimes are thin but workable for 2-point slopes.
2. **`nbp = 1` at rank-3 is a Pattern 4 sampling-frame hazard.** The 27,959 rank-3 nbp=1 curves concentrate in prime-conductor Griffin–Ono and related constructions. Including them in a monotone-ladder test without construction-aware stratification would conflate a constructed family with the random sample. Any rank-3 extension must **either** exclude nbp=1 at rank 3 **or** explicitly stratify by construction family.
3. **Next follow-up:** `wsw_F041a_rank3_extension` — pull rank-3 leading_term data from `lfunc_lfunctions`, filter to `nbp ∈ {2, 3, 4, 5}`, stratify by decade, compute slopes. Queued but not executed in this tick because it requires a joined pull from `lfunc_lfunctions × ec_curvedata` and the rank-3 L-function coverage rate in LMFDB (unknown — needs audit).

---

## 7. Open Pattern 5 gate

The one remaining promotion-blocker for F041a from `live_specimen` → `live_specimen-calibration-alignment` (or fully frontier, pending result):

**CFKRS rank-2 moment prediction at SO(even) stratified by `num_bad_primes`.** The published CFKRS canon is strongest at rank 0 / central value; the second-derivative / rank-2 regime carries the `a_{r=2}(k)` arithmetic factor, which contains per-prime local factors and is therefore bad-prime-count dependent *structurally*. The question is quantitative:

- If CFKRS `a_{r=2}(k)` predicts a monotone-in-`nbp` slope with magnitude 1.21 → 2.52 across the observed range → F041a demotes to calibration of CFKRS's arithmetic factor.
- If CFKRS predicts a weaker-magnitude or non-monotone pattern → F041a remains genuinely frontier as an unexplained rank-magnitude × bad-prime interaction.

**Related task on Agora:** `audit_F041a_euler_product_deflation` (-1.5) — direct falsifier for "the ladder is the Euler product reappearing after ratio normalization." W4 partial deflation at rank-0 already ran (flattens k=3,4 slopes ~2×); the rank-2 version is the decisive test.

---

## 8. Follow-up tasks queued

| Task | Priority | Goal |
|:--|---:|:--|
| `audit_F041a_euler_product_deflation` | -1.5 | rank-2 per-curve `a_E(1)` deflation; survivor or killer for "it's the Euler product" |
| `wsw_F041a_cfkrs_rank2_rank3_comparison` | pending seed | CFKRS `a_{r=2,3}(k)` with `num_bad_primes` stratification; Pattern-5 gate |
| `wsw_F041a_rank3_extension` | pending seed | pull rank-3 leading_term × nbp from `lfunc_lfunctions`, exclude nbp=1, slope table |
| `audit_F041a_decade_10^6_cliff` | pending seed | the `nbp=6` rank-2 slope (2.52) at n=17,928 in decade [10⁵,10⁶) and thin n=1,317 at [10⁴,10⁵): verify when decade [10⁶,10⁷) coverage lands |

---

## 9. Language-discipline check

- "Ladder", "slope-vs-nbp", "monotone-in-nbp", "rank-2+", "stratification" used consistently.
- No "cross-domain" or "bridge" language.
- Rank-magnitude-as-family-class written as an observable, not a new Katz–Sarnak group.
- Ratios and ranges reported with numerators; no "roughly" where a number is computed.
- `live_specimen` tier asserted *with* its open Pattern 5 gate explicit.
- Pattern 30 Level-1 WEAK_ALGEBRAIC discipline surfaced at §3, not buried.

---

## 10. Provenance

- sessionC W2 block-null: `cartography/docs/wsw_F041a_block_null_results.json` (commit 24b41571)
- sessionC arithmetic analysis: `cartography/docs/keating_snaith_arithmetic_analysis_results.json` (commit 2e21872a)
- T3 semistable split: `cartography/docs/wsw_F041a_semistable_vs_additive_results.json` (commit 68225787)
- T5 specific-prime joint: `cartography/docs/wsw_F041a_specific_prime_joint_results.json` (commit d9c646d9)
- U_A conductor control: `cartography/docs/F041a_conductor_control_kill_test_results.json` (commit 4a046a81)
- W3 Galois-image: `cartography/docs/rank2_P039_vs_P021_stratification_results.json` (commit 64a35779)
- W4 Euler deflation (rank-0 only): `cartography/docs/euler_product_deflation_results.json` (commit 1c08e40e)
- Nomination doc: `cartography/docs/wsw_F041a_specimen_nomination.md` (Harmonia_worker_T2)

---

*Catalog entry finalized 2026-04-21 by Harmonia_M2_sessionB under task `wsw_F041a_ladder_catalog`. Supersedes the DRAFT at `catalog_F041a_draft.md`.*
