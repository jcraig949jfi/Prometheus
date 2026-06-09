# Reaudit — 10 stratifier-mismatch cells

**Task:** `reaudit_10_stratifier_mismatch_cells`
**Worker:** Harmonia_M2_sessionD
**Commit at run:** `f2ea773c`
**Started / finished:** 2026-04-21T08:08:26 / 08:26:26 UTC (18 min)
**N:** 2,009,089 EC (LMFDB `ec_curvedata` ⋈ `prometheus_fire.zeros.object_zeros`, n_zeros≥2, rank not null)
**Operator used:** `NULL_BSWCD@v2` (literal) + per-claim-class reformulation (Class 3 → per-stratum deficit bootstrap; Class 2 → joint (rank, cond_decile) shuffle)
**Reference:** `harmonia/memory/symbols/protocols/null_protocol_v1.md`, `cartography/docs/cell_null_classification.json`

---

## TL;DR — conductor summary

| Cell | Prescribed (Class/Stratifier) | Literal z | Reformulated raw verdict | **Final interpretation** | Tensor action |
|---|---|---|---|---|---|
| F011:P021 | 3 / num_bad_primes | 17.08 | MIXED (nbp=1 reverse-sign, nbp=2 at noise) | **Non-uniform deficit across nbp (Class-2 interaction reframe)** | **retain +2 + annotate** |
| F011:P023 | 3 / rank | 275.29 | MIXED (rank-3 z=2.81 at n=5405) | **Durable on n-large strata; rank-3 power-limited** | **retain +2 + annotate** |
| F011:P026 | 3 / semistable | 6.45 | DURABLE (both strata z>100) | **Clean Class-3 uniformity confirmation** | **retain +2** |
| F011:P036 | 3 / root_number | 190.61 | DURABLE (both strata z>90) | **Durable; P30-L1 root-number↔rank-parity note** | **retain +2** |
| F013:P023 | 2 / rank | 92.62 | COLLAPSES (reform z=−0.58, null_std=0) | **DEGENERATE reform; original conductor-null was correct** | **retain +2** (JSON misflag) |
| F013:P028 | 2 / rank | 92.62 | COLLAPSES (reform null_std=0) | **DEGENERATE reform; classification mismatch is false** | **retain +2** |
| F013:P041 | 2 / rank | 92.62 | COLLAPSES (reform null_std=0) | **DEGENERATE reform** | **retain +2** |
| F013:P051 | 2 / rank | 92.62 | COLLAPSES (reform null_std=0) | **DEGENERATE reform** | **retain +2** |
| F013:P104 | 2 / rank | 92.62 | COLLAPSES (reform null_std=0) | **DEGENERATE reform** | **retain +2** |

**Zero tensor invariance-value changes recommended.** The auto-generated per-verdict recommendations (downgrade / demote) are superseded by the interpretation below.

**Scope note:** 3 F044 Class-4 cells (P020, P023, P026) are out of scope — NULL_BSWCD insufficient per `null_protocol_v1.md` §Class 4. See `audit_F044_framebased_resample` @ priority −1.0.

---

## 1. Headline methodology finding

**The literal Class-2/3 prescription is structurally degenerate for these cells.** In Class-2/3, the prescribed shuffle preserves the within-stratum *value distribution* exactly. If the test statistic is a function only of per-stratum *aggregates* (means, variances) of the stratifier variable, the statistic is invariant under the shuffle → null_std ≈ 0 → z uninformative.

- **F011-style cross-group spread** (max − min of per-stratum deficits): per-stratum means are invariant → degenerate under stratifier=V.
- **F013-style slope-of-(per-stratum-variance)-vs-stratifier**: per-stratum variances are invariant → degenerate under stratifier=rank.

The Class-2/3 prescriptions work for statistics that pair `value` with a **non-stratifier covariate** within each stratum (e.g., F041a's per-rank slope of moment-vs-log_conductor). They **do not** work for F011/F013's current statistic shapes.

Consequence: **the original conductor-stratified nulls were the structurally correct match for F011 and F013's statistic shapes.** The classification JSON's "Class 2 mismatch" flag on F013's five cells, and the re-labeling of F011 cells as Class 3, are both false flags against the existing statistics.

**Symbol-promotion candidate (Tier 2):** `PATTERN_STRATIFIER_INVARIANCE@v0` (DRAFT) — when a statistic depends only on per-stratum aggregates of the stratifier, `NULL_BSWCD@v2[stratifier=V]` is degenerate. Required diagnostic before any such audit: verify non-invariance under proposed stratifier. Reformulation options: (i) statistic paired with non-V covariate; (ii) bootstrap per-stratum durability; (iii) switch stratifier to documented nuisance. Anchor cases: F011 cross-group spread, F013 slope-of-variance-vs-rank. Generalizes `null_protocol_v1.md` §Class 2/3 into a precondition on statistic shape.

---

## 2. F011 Class-3 cells — per-stratum durability

Reformulated test: for each stratum *v* with n ≥ 500, compute `deficit_v = GUE_MEAN − mean(gap1_unfolded | V=v)` and bootstrap SE over 300 resamples. `z_v = deficit_v / bootstrap_SE`.

### F011:P021 — num_bad_primes

| nbp | n | deficit | SE | z | |
|---:|---:|---:|---:|---:|---|
| 1 | 3,915 | **−0.0272** | 0.0070 | **−3.88** | reverse sign |
| 2 | 74,596 | 0.0027 | 0.0014 | +1.92 | at noise |
| 3 | 464,308 | 0.0303 | 0.00052 | +58.64 | durable |
| 4 | 922,339 | 0.0560 | 0.00036 | +155.39 | durable |
| 5 | 492,493 | 0.0827 | 0.00044 | +190.06 | durable |
| 6 | 51,438 | 0.1050 | 0.00124 | +84.43 | durable |

**Interpretation:** deficit grows monotonically with nbp from 3→6, is at noise at nbp=2, **reverses sign at nbp=1** (one-bad-prime curves have first-gap variance *above* GUE). This is consistent with F011's live description: *"deficit varies with arithmetic complexity — NOT uniform, rules out generic unfolding error."* The claim "deficit uniform across nbp" fails (that was never F011's actual claim); the claim "nbp is an axis that reveals structure" (Class-2 interaction) is strongly supported. **Retain +2** with an annotation recording the nbp=1 reverse-sign observation.

### F011:P023 — rank

| rank | n | deficit | SE | z |
|---:|---:|---:|---:|---:|
| 0 | 773,232 | 0.1017 | 0.00034 | +298.20 |
| 1 | 1,008,146 | 0.0301 | 0.00033 | +91.98 |
| 2 | 222,305 | 0.0126 | 0.00077 | +16.44 |
| 3 | 5,405 | 0.0131 | 0.00467 | **+2.81** |

**Interpretation:** same-sign deficit across all four ranks, decaying monotonically from rank 0 (DHKMS excised-ensemble layer). Rank 3 falls just below |z|≥3 at n=5,405 — a sample-size limit, not a claim failure. Dropping strata with n<10K (standard small-n discipline) leaves all remaining strata DURABLE. **Retain +2** with annotation "rank-3 power-limited (n=5,405)".

### F011:P026 — semistable_flag

| semistable | n | deficit | SE | z |
|---:|---:|---:|---:|---:|
| 0 (additive) | 1,489,960 | 0.0563 | 0.00028 | +204.36 |
| 1 (multiplicative) | 519,129 | 0.0539 | 0.00048 | +112.15 |

**Interpretation:** clean Class-3 uniformity confirmation. Deficit durable in both strata at z > 100 with near-identical magnitudes (spread = 0.0024). **Retain +2.**

### F011:P036 — root_number (≡ rank parity on EC)

| root_number | n | deficit | SE | z |
|---:|---:|---:|---:|---:|
| 0 (even rank) | 995,538 | 0.0818 | 0.00032 | +256.43 |
| 1 (odd rank) | 1,013,551 | 0.0300 | 0.00032 | +92.44 |

**Interpretation:** deficit durable in both strata. Asymmetry mirrors F011:P023 rank pattern (even-rank pool dominated by rank 0's 0.1017 deficit; odd-rank pool dominated by rank 1's 0.0301). **Retain +2**; annotate Pattern 30 Level 1 inherited from F013 (root_number = rank%2 on EC is algebraically tied to rank parity via BSD).

---

## 3. F013 Class-2 cells — degenerate under reformulated test

All five F013 cells share the same underlying slope-diff statistic (F013's tier description defines it globally; per-projection variants decorate with unfolding / variance-decomposition / self-audit). Tests were therefore run once.

**Observed F013 slope-diff statistic** (pair-slope diff of var-vs-rank between SO_even and SO_odd ks_classes, min stratum n=500):

- SO_even slope (rank 0 → rank 2): +0.01459
- SO_odd slope (rank 1 → rank 3): −0.00040
- slope-diff: **0.01500**

**Literal test** (NULL_BSWCD@v2, stratifier="rank"): null_mean = 0.00465, null_std = 0.000112, observed = 0.015 → z = 92.62, nominal DURABLE. The small non-zero null_std is an artifact of `pd.qcut(rank, q=10, duplicates='drop')` producing quantile-buckets that can span multiple discrete ranks, admitting tiny between-rank leakage. That leakage is binning behavior, not a clean test.

**Reformulated test** (per-rank slope of var vs log_conductor, joint (rank, cond_decile) shuffle): observed `std(slope_r) = 0.012463`, **null_std = 0.000000**, z = −0.58. **DEGENERATE.** Per-(rank, cond_decile) variances are exactly preserved under within-cell shuffle; the per-rank slope is a function of those variances; therefore the statistic is invariant.

### The classification flag is a false alarm

`cell_null_classification.json` flagged F013's cells for re-audit on the grounds that conductor-stratified null *"doesn't match the Class 2 rank-slope-interaction claim."* Two facts emerge here:

1. **F013's statistic is invariant under the prescribed Class-2 stratifier.** Any test built around it will be degenerate. The re-audit literally cannot run as specified.

2. **The ORIGINAL conductor-stratified null was the structurally correct null.** It preserves conductor marginal (the documented nuisance) and shuffles rank labels within conductor deciles, which **destroys the rank-to-variance pairing** — exactly what a Class-2 null should do. The confusion arose because `stratifier=conductor` is convention-named "Class 1", but for a statistic whose shape is "slope of variance-vs-rank per ks_class", conductor-shuffle IS the claim-destroying null.

**All five F013 cells: retain +2. Their original z_block values** (P023:22.39, P028:15.31, P041:8211.96, P051:8.05, P104:15.31) **remain the authoritative measurements.** No tensor mutation.

---

## 4. Proposed edits to `cell_null_classification.json`

Surfaced corrections:

- **F011:P021** — `claim_class`: 3 → **2**; rationale: *"deficit varies monotonically with nbp (interaction)"*; `correct_null_stratifier`: **conductor_decile** (prior z=38.58 under this stratifier remains authoritative); `flag_for_reaudit`: **false**.
- **F011:P023** — `claim_class`: 3 → **2**; rationale: *"deficit decreases monotonically with rank (interaction)"*; `correct_null_stratifier`: **conductor_decile**; `flag_for_reaudit`: **false**.
- **F011:P026** — keep Class 3 (genuine uniformity); `correct_null_stratifier`: **conductor_decile** (per-stratum bootstrap is the Class-3 diagnostic, not within-stratum shuffle); `flag_for_reaudit`: **false**.
- **F011:P036** — keep current Class 3 status; annotate Pattern 30 Level 1 (root_number ↔ rank_parity); `correct_null_stratifier`: **conductor_decile**; `flag_for_reaudit`: **false**.
- **F013:{P023,P028,P041,P051,P104}** — `correct_null_stratifier`: **conductor_decile** (the original null was correct); `flag_for_reaudit`: **false**; add note per §3 about statistic invariance under rank shuffle.

**Net effect:** `total_flagged_for_reaudit: 10 → 0` for NULL_BSWCD-appropriate cells. The 3 F044 Class-4 cells remain flagged for Class-4-appropriate audit (frame-based resample).

---

## 5. Tensor mutations

**None.** All nine NULL_BSWCD-appropriate cells retain their current +2 value. Annotations are text-only updates to cell descriptions; the tensor mutation protocol (`agora.tensor.push_tensor`) is not invoked.

---

## 6. Provenance & artifacts

- Full result JSON: `cartography/docs/reaudit_10_stratifier_mismatch_results.json`
- Per-cell SIGNATURE@v1 JSONs: `cartography/docs/signatures/SIG_F{011,013}_P{021,023,026,028,036,041,051,104}_v2.json` (9 files)
- Runner: `harmonia/reaudit_10_stratifier_mismatch.py`
- Operator: `NULL_BSWCD@v2` reference at `harmonia/nulls/block_shuffle.py::bswcd_null`
- Data: `lmfdb.public.ec_curvedata ⋈ prometheus_fire.zeros.object_zeros` (n_zeros≥2, rank not null), n=2,009,089
- Seed: 20260417; N_perms: 300; N_bins: 10; MIN_STRATUM_N: 500
- Literal-stratifier binning caveat: `pd.qcut(stratifier, q=10, duplicates='drop')` with discrete stratifiers produces quantile-buckets that can span multiple discrete values — interpret `n_strata_used < unique_values(V)` as binning-induced leakage, not a clean per-V shuffle.

---

## 7. Open follow-ups (for conductor)

1. **Classification JSON correction** — authoritative edit to `cell_null_classification.json` per §4 (conductor-owned action).
2. **`null_protocol_v1.md` §Class 2/3 amendment** — add precondition: *"the statistic must not be invariant under within-stratum shuffle of value"*. Pointer to PATTERN_STRATIFIER_INVARIANCE.
3. **Symbol promotion** — draft `PATTERN_STRATIFIER_INVARIANCE@v0` to `harmonia/memory/symbols/CANDIDATES.md` Tier 2.
4. **F044 cells** — audit_F044_framebased_resample @ −1.0 remains the correct task; out of scope here.

---

## 8. Per-cell mechanical detail (auto-generated)

Below tables record the raw reformulated-test output. Interpretation layer is in §2–§3 above; interpretation supersedes the literal verdict labels where noted.

### F011:P021 per-stratum table (reformulated, N_boot=300)

| stratum | n | deficit | SE | z | durable |
|---|---|---|---|---|---|
| 1 | 3,915 | −0.027208 | 7.007e-03 | −3.88 | ✓ |
| 2 | 74,596 | +0.002678 | 1.395e-03 | +1.92 | ✗ |
| 3 | 464,308 | +0.030301 | 5.167e-04 | +58.64 | ✓ |
| 4 | 922,339 | +0.055956 | 3.601e-04 | +155.39 | ✓ |
| 5 | 492,493 | +0.082696 | 4.351e-04 | +190.06 | ✓ |
| 6 | 51,438 | +0.104978 | 1.243e-03 | +84.43 | ✓ |

### F011:P023 per-stratum table

| stratum | n | deficit | SE | z | durable |
|---|---|---|---|---|---|
| 0 | 773,232 | +0.101704 | 3.411e-04 | +298.20 | ✓ |
| 1 | 1,008,146 | +0.030133 | 3.276e-04 | +91.98 | ✓ |
| 2 | 222,305 | +0.012639 | 7.687e-04 | +16.44 | ✓ |
| 3 | 5,405 | +0.013121 | 4.664e-03 | +2.81 | ✗ |

### F011:P026 per-stratum table

| stratum | n | deficit | SE | z | durable |
|---|---|---|---|---|---|
| 0 | 1,489,960 | +0.056314 | 2.756e-04 | +204.36 | ✓ |
| 1 | 519,129 | +0.053927 | 4.809e-04 | +112.15 | ✓ |

### F011:P036 per-stratum table

| stratum | n | deficit | SE | z | durable |
|---|---|---|---|---|---|
| 0 | 995,538 | +0.081815 | 3.191e-04 | +256.43 | ✓ |
| 1 | 1,013,551 | +0.030043 | 3.250e-04 | +92.44 | ✓ |

### F013 reformulated joint-shuffle test (applies to all 5 F013 cells)

- observed `std(slope_r)` = 0.012463
- null_mean = 0.012463
- null_std = **0.000000** (degenerate under joint (rank, cond_decile) shuffle)
- null_p99 = 0.012463
- z = −0.58 (round-to-2-places artifact; real z is undefined)
- **verdict: DEGENERATE, not COLLAPSES.** The auto-label "COLLAPSES" was from a naive |z|<3 mapping and is superseded.

---

## 9. Addendum — individual-curve slope-diff tests for F013 (2026-04-21)

**Motivation.** §3 showed F013's decile-variance slope-diff statistic is invariant under the prescribed Class-2 shuffle. An orthogonal question is whether a *non-aggregated* Class-2 statistic — per-rank OLS slope of individual-curve `gap1_unfolded` vs `log_cond`, differenced across rank cohorts — survives a within-rank-cohort shuffle. This statistic is NOT invariant under within-rank shuffle (pairings between `value` and `log_cond` within a rank are destroyed), so it gives a non-degenerate test of a different-but-related Class-2 claim.

**Addendum script:** `harmonia/tmp/reaudit_10_f013_addendum.py` → `cartography/docs/reaudit_10_stratifier_mismatch_f013_addendum.json`.

| Statistic | Stratifier | Observed | null_mean | null_std | z | Verdict |
|---|---|---:|---:|---:|---:|---|
| `slope(rank=0) − slope(rank≥1)` of individual value vs log_cond | `rank_bin` (qcut→2 effective strata, P26 warning: 88.7% dominant) | −0.01580 | −0.00324 | 1.09e-03 | **−11.53** | DURABLE |
| `slope(SO_even) − slope(SO_odd)` of individual value vs log_cond | `rank_parity` (qcut degenerate, P26 warning: 100% dominant) | −0.000817 | −0.000109 | 1.10e-03 | −0.64 | COLLAPSES |

**Findings.**

1. **Rank=0 vs rank≥1 individual-curve slope-diff is DURABLE at z=−11.53** under within-rank-cohort shuffle. Rank-0 curves have a *lower* slope of gap vs log_cond than rank≥1 curves. This is a genuine Class-2 rank interaction at individual-curve resolution.

2. **Sign is OPPOSITE to the original F013 claim** (published as "SO_even +0.01284 > SO_odd −0.00216"). The original was measured on decile-aggregated variances; the addendum measures individual-curve mean-slopes. These are different physical quantities — not a contradiction, but a caveat against conflating them.

3. **Rank-parity split (SO_even vs SO_odd) at individual-curve resolution COLLAPSES.** Under a binary stratifier that bswcd_null's qcut couldn't split (100% dominant), the observed parity slope-diff (−0.000817) is within null noise (std 1.10e-03). There is no individual-curve parity-based slope interaction.

**Interpretation.**
- F013's decile-variance statistic and F013's individual-curve statistic are *different measurements* answering *different questions*. Both are legitimately-computable, but they probe different layers (dispersion-of-dispersion vs mean-slope). Interpreting the two as the same claim was a latent conflation.
- The existing tensor +2 on F013 cells rests on the decile-variance claim, which §3 confirms is correct under the original conductor-stratified null. No tensor mutation triggered by this addendum.
- Compression-candidate refresh: `PATTERN_STRATIFIER_INVARIANCE@v0` (draft in §1) now has a second anchor — the existence of a *related but non-aggregated* statistic that IS non-invariant under the same shuffle. A complete Pattern-31 would note that statistic *shape* (aggregated vs individual) interacts with stratifier *choice* to determine degeneracy.

**Open question for conductor:** does F013's finding description need to be split into two claims (decile-variance slope-diff vs individual-curve slope-diff) to disambiguate downstream consumers? The two currently read as one.
