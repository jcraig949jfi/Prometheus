# PREREG DRAFT: X-INDEP-BATCH (founder independence in one batch, with morph logging)

**Status:** DRAFT, written 2026-10-01T02:40Z (`date -u`). It is NOT frozen, NOT dispatched and NOT authorized. It needs authorization, a Fabric lease and a freeze commit.
**Rank:** 3 of 3. This is the lowest decisiveness per CPU-hour (see §9 and DESIGNS.md).
**Inputs:** W2-12, with the method (cloglog, a jointly fitted p1, β) and the verdict "independent tickets, β = 1.13 [0.98, 1.29]". Also W2-25 F18 and §5 Exp 2, and the ledger batch entry at 02:23Z.

## 0. Why, and why k = 8 rather than k = 4
- **The open question.** All k > 1 evidence comes from three dose blocks. One of them (C-CRITICAL-MASS) alone rejects independence (p = 0.014), through a low k = 1 arm. A same-batch, same-seed-scheme test removes batch heterogeneity by construction.
- **Precision of β** (delta method, calc_bands.json `exp2_beta`, p1 = 0.11):

  | n (k = 1 / k = k) | k = 4 | k = 8 |
  |---|---|---|
  | 800/400 | SE(β̂) 0.097 | SE(β̂) 0.061 |

  k = 8 doubles the log-dose lever without saturating: P8 is 0.61–0.67 at β = 1. **k = 8 is chosen.** k = 4 at the same cost cannot reach a clean call: P(independence call | β = 1) ≤ 0.19.

## 1. Hypotheses
Model: −log(1 − P_k) = −log(1 − p0) + k^β · (−log(1 − p1)), where p0 is the background-only floor.

| hypothesis | predicts | source |
|---|---|---|
| **H-IND (F\* with morphs; T7)** | β = 1; family-level outcomes independent within a run; each family's morph-arrival clock has the same distribution at k = 1 and k = 8 | |
| **H-HOME (T4(a), home advantage / kin superadditivity)** | β > 1; positive within-run correlation of family outcomes | |
| **H-KIN-STATIC** | β ≈ 1.02–1.05. Kin pairing abolishes hijack statically, but kin are 1–3% of partners early | W2-12 §4 |
| **H-INTERFERE** | β < 1. Founders compete for slots and partners | |

## 2. Arms
X-TICKET physics: 7ae3 arm-B cell, splice off, tier M, BASE, max_epochs = 300.

| arm | n | construction |
|---|---|---|
| **K1** | 800 | one implanted founder (as X-TICKET) |
| **K8** | 400 | X-DOSE-CURVE construction: the implant plus 7 extra copies replacing the first 7 `_seed_genome()` draws (anc 1–7) |
| **NC-RM (background floor and ruler negative)** | 64 | the manifest's RANDOM_MATCHED implant (H2 arm C), i.e. k = 0 founders of the 7ae3 type. Estimates p0 and shows that the family ruler does not fire on a non-copier |

## 3. Seeds
- **Base: `42_100_000 + s`.**
  - K1: s ∈ [0, 800).
  - K8: s ∈ [0, 400).
  - NC-RM: s ∈ [0, 64).
- **Used ranges checked:** the inventory in PREREG_DRAFT_IMPLANTED_MORPHS §3. That includes all dose blocks (9_993_000, 9_996_000, 9_997_000), X-TICKET and W2-22. `42_1xx_xxx` is unused. Re-check at freeze.
- Replays used only as controls: X-DOSE-CURVE 9_997_000 + two k = 8 seeds with depth ≥ 5 on record, and X-TICKET 9_998_035.

## 4. Readouts (matched across arms)
- **R1 (primary, run level).** Any founder family reaches causal depth ≥ 5 by epoch 300.
  - Family i is the causal-set closure of founder i (anc i), using the X-TICKET subclass generalised to k sets.
  - Its depth is `depth_from(lineage, [f_i])` (W2-14 `ffield.depth_from`).
- **Readout note (lesson: matched readouts).**
  - W2-12's table uses *world* depth ≥ 5 at **2000** epochs. This batch uses *family* depth at **300**.
  - The new batch is therefore **never pooled** with W2-12's table. Only its internal β is decisive.
  - World depth ≥ 5 is reported as R1w (secondary, non-decisive). W2-2: world depth can come from non-founder chains.
- **R2 (family level, secondary but powered).**
  - Each family's success indicator.
  - p_fam(K8) vs p_fam(K1) = p1.
  - The within-run intraclass correlation (ICC) of family success in K8.
  - The number of successful families per K8 run, compared with Binomial(8, p_fam): an overdispersion test.
- **R3 (morph logging).**
  - Every causal birth in every family is logged: epoch, family, parent side, child bytes 37 and 41–52, child sha256, fid.
  - Per family: the epoch of the first side-0 **genotype** birth, using the static byte classifier frozen in X-IMPLANT-MORPH R5, and the epoch of its 27th birth.
  - "Independent clocks" test: a two-sample KS test of first-morph epochs between K8 families and K1 families, with censoring at family extinction handled by log-rank.
- **R4.** Final genomes stored per run, at the end or at the stop.
- **Stop rule.** Epoch 300, or when every founder family is extinct (its causal set has no live member and no anc-i organism is alive). R1 is exact under this stop. R1w is truncated for stopped runs and is flagged as such.

## 5. Decision rules (frozen)
**Fit.** β̂ by maximum likelihood on {K1, K8}, with p0 fixed at the NC-RM rate. If NC-RM is 0/64, p0 = 0, with the sensitivity case p0 = 1/64. The CI is a 95% profile likelihood.

| verdict | condition | kills |
|---|---|---|
| **INDEPENDENT** | CI ⊂ [0.80, 1.20] | T4(a) as a material effect (> 20% per-founder superadditivity, the size the C-CRITICAL-MASS excess needed). C-CRITICAL-MASS's 41/80 is filed as a k = 1-arm fluke. F\* passes this test |
| **SUPERADDITIVE** | CI lower bound > 1.05, i.e. above the static kin-route ceiling | F\*'s "no kinship term" (F\* kill criterion 3 in spirit) and W2-12's verdict. T4(a) is revived |
| **SUBADDITIVE** | CI upper bound < 0.95 | both "independent tickets" and T4(a). F\* survives only if the founder-free-bank model reproduces the interference; that is not pre-specified, so it is flagged |
| **UNRESOLVED** | otherwise | nothing. Report the CI |

**Family-level co-readouts** (decisive only for mechanism, not for the β verdict):
- r = p_fam(K8) / p1:
  - CI ⊂ [0.80, 1.25] together with ICC CI ∋ 0 → "independent tickets at the family level";
  - CI lower bound of r > 1.10 → kin help.
- Morph clocks:
  - KS/log-rank p > 0.05 → independent clocks;
  - a K8 morph-arrival time shifted earlier (p < 0.01) → morphs spread between families, which is a kin or heredity term.

**Power** (Monte Carlo, 4,000 replicate batches; p1 at 300 epochs assumed 0.08–0.13):

| true β | n = 800/400 | n = 1000/500 |
|---|---|---|
| 1.00 | P(INDEPENDENT) **0.63–0.89** | 0.80–0.95 |
| 1.15 | P(SUPERADDITIVE) 0.28–0.42 (mostly UNRESOLVED) | 0.35–0.52 |
| 1.30 | P(SUPERADDITIVE) **0.97–1.00** | ≈ 1.00 |

- Family level: SE(log r) ≈ 0.13 at p_fam ≈ 0.08. This detects r ≥ 1.3 at about 2σ.

## 6. Eligibility count (pre-run)
- **K1:** 800 × (0.08–0.13) ≈ **64–104** successes.
- **K8:** 400 × (0.49–0.67) ≈ **195–270** successes, and 3,200 family outcomes.
- **Morph-clock test:** needs ≥ 20 families with a side-0 genotype birth in each arm.
  - Under W2-25 F5's event rate (3.5% per birth), most families of more than 30 births qualify. Under N17d's genotype rate (7.5e-4) almost none do.
  - **This sub-test may be INELIGIBLE.** That outcome is itself informative for the F5 switch-rate contradiction, and is pre-registered as such.
- **NC-RM:** p0 is expected to be about 0. If NC-RM ≥ 3/64, p0 is a real term and is reported.

## 7. Planted controls with demonstrated reachability
- **PC1 (harness equivalence and positive reachability).**
  - Replay two X-DOSE-CURVE k = 8 seeds that have world depth ≥ 5 on record, at the full 2,000 epochs (about 211 s each).
  - Required: world depth and p11_events equal to `x_dose_curve/results` exactly. This verifies the k-founder construction.
  - Also replay X-TICKET s35 for 300 epochs. Required: the traj equals the record, and family depth ≥ 5 is reached. This shows the family ruler can fire.
- **NC1.** NC-RM arm (above): the family depth ruler should give ≤ 1/64 successes. More than that is an instrument flag.
- **NC2 (static).**
  - On synthetic lineage graphs with known family depths, `depth_from` per family must give exact values.
  - That includes families that absorb each other's victims (cross-family births are attributed to the parent's family).
- **Classifier.** The same static classifier controls as X-IMPLANT-MORPH NC2/PC3.

## 8. CPU estimate
| item | runs × cost | core-h |
|---|---|---|
| K1 | 800 × ~20 s (about 55% of runs reach 300 epochs at about 32 s; the rest stop early) | 4.4 |
| K8 | 400 × ~70 s (8 families; saturating runs about 85–100 s) | 7.8 |
| NC-RM | 64 × 20 s | 0.35 |
| PC1 | 2 × 211 s + 1 × 90 s | 0.15 |
| **Total** | | **≈ 12.7** |

- Hard cap 15.5.
- **Pre-registered checkpoint.** After 10% of runs, project the total.
  - If the projection exceeds 15.5, fall back to K1 = 640 and K8 = 320. Power then drops: P(INDEPENDENT | β = 1) ≈ 0.5–0.8.
  - The fallback is decided by cost only, never by data.

## 9. Envelope check (MWO-0004 R2)
- 12.7 core-h is under 16 per item, but leaves little margin.
- Together with X-IMPLANT-MORPH (10) and X-HARV-INWORLD (6.5), the total is about 29 core-h, against the seat cap of 48 per rolling 24 h. Check the trailing Wave-2 usage first.
- Fabric lease required.
- New preregistration, so authorization is required.

## 10. Failure modes
1. **The stakes are already low.** T4(a) is "unsupported, not excluded" (W2-12). The likeliest outcome (β ≈ 1.0–1.15) gives INDEPENDENT or UNRESOLVED and moves no headline. This is why the experiment ranks last.
2. **The horizon shift (300 vs 2000) changes p1.** It is handled by the in-batch fit and the ban on pooling. The absolute p1 is not comparable to W2-12's 0.13.
3. **Family attribution under interaction.** A family-i member overwriting a family-j member makes a family-i child. The analysis therefore uses *success* per family, not size. Family "absorption" is logged.
4. **K8 replaces 7 background genomes.** That slightly changes background composition and shifts RNG consumption, so there are no common random numbers across arms. This is accepted, as in X-DOSE-CURVE.
5. **The morph-clock sub-test may be ineligible** (§6).
6. **The splice-on heterogeneity** (W2-12 §5, p = 0.006) is out of scope: splice off only.
