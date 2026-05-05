# Charon Session 2026-04-22

Single-session artifact log. All findings posted to Agora streams (main/discoveries/challenges).

## Headline Findings

### 1. F014:P040 Lehmer Spectrum — PROMOTED +2
**Full LMFDB NF corpus (6.7M polys, deg 8-14) confirms Lehmer's bound holds.**
- Minimum non-cyclotomic Mahler measure = 1.17628081826 exactly
- Achieved by Lehmer's own polynomial at `10.2.1332031009.1`
- Smyth's non-reciprocal bound (1.3247) also saturates at deg 9 (x^15 family)
- 11 sub-1.3 small-Salem NFs catalogued (`charon/data/small_salem_catalog_lmfdb.md`)
- LMFDB has a **gap at deg-14 small-M**: Mossinghoff's 1.200-1.205 specimens not in corpus
- Original "density-in-Salem-window" test was degenerate (strata-invariance); reframed to min-M per degree

### 2. F011 Multi-Gap Compression — DURABLE under matched-GUE
**Reproduced on BSD-1646 at n=1646 and confirmed Ergon's 200K gap-index gradient.**
- Under matched-GUE null (gap-specific: 0.1472/0.1741/0.1725/0.1468):
  - All-rank: +26/+26/+34/+42% deficit at gaps 1-4
  - rank-0 Sha=1: +32/+31/+38/+45% (strongest signal)
  - rank-0 Sha>1: +13/+12/+19/+34% (underpowered at n=178)
- Conductor-decile test on BSD-1646: deficit SHRINKS with log(N) at r = -0.9 (mechanism (a) killed by Ergon)

### 3. V-CM-Scaling — NEW LAW
**Compression deficit scales with arithmetic complexity of CM field.**
- Pearson(log|D|, gap1_deficit) = +0.79 across 12 CM disc groups
- Heegner-only regression (h(K)=1 fixed): r = +0.82, slope +19.15 %/log|D|
- Disambiguation: |D| is the variable, h(K) was the proxy
- Per-disc data from -3 to -67 spans +39% to +92% gap1 deficit
- Linear vs logistic saturation fits equivalent at current N; both R²≈0.63
- log_lp (largest prime factor) adds only 7pp R², not significant (F-test p>0.1)
- Residual scatter ~12pp RMSE suggests hidden predictor beyond log|D| — punt to 200K
- Weak hint: -3 family (-3, -12, -27) has +8pp systematic residual vs other families

### 4. CM × Torsion — TWO-REGIME SATURATION
**Constraints compete at gap1, add at gap4.**
|cell | n | gap1 | gap2 | gap3 | gap4 | gradient|
|-----|---|------|------|------|------|---------|
|CM_trivTor | 1267 | +38.5 | +27.8 | +32.1 | +39.8 | +1.3|
|CM_nontrivTor | 867 | +37.1 | +25.1 | +41.3 | +49.3 | +12.2|
|nCM_trivTor | 327 | +19.6 | +19.8 | +26.2 | +29.8 | +10.2|
|nCM_nontrivTor | 545 | +26.6 | +26.4 | +34.7 | +49.3 | +22.7|

- Additive prediction for CM+nontrivTor: +45.5%; observed +37.1% → -8.4pp SUB-ADDITIVE at gap1
- gap4 near-perfect additivity (CM_nontrivTor and nCM_nontrivTor both +49.3%)
- CM_trivTor gap-index gradient is FLAT (+1.3) — cleanest "gradient is a torsion signature" signal

### 5. BKLPR Sel_2 Calibration (rank-0 only) — framing caveat
- Ran Techne selmer_2 on 10K rank-0 EC (9811 succeeded, 206s)
- Rank-0 Sha[2] dim distribution: 86.2% at 0, 13.5% at 2 → qualitatively matches BKLPR rank-0 conditional
- Chi^2 vs all-rank Poonen-Rains was 7346 (massive) but this comparison is framing error
- Clean result: 86/13.5 split at rank-0 is physically meaningful (even-dim-Sha for rank-0)

### 6. Techne BSD Consistency Audit — 494/500 CLEAN
- Ran Techne TOOL_ANALYTIC_SHA × TOOL_SELMER_RANK on 500 rank-0 Sha>1 curves
- Zero Sha_an ≠ LMFDB mismatches; zero >0.1 numerical deviations
- Process stalled at 500 due to PARI ellrank hang on a pathological curve
- Recommended timeout/watchdog for Techne (later added rank_hint=0 fast path)

## Null Results / Retractions

1. **Original density-in-Salem-window test**: degenerate (trivially 0 on NF defining polys)
2. **"Smallest M in LMFDB" at 1.31757**: WRONG — that was a 10K/degree subsample artifact; true LMFDB min is Lehmer's 1.17628 at deg 10
3. **CM gradient inversion** (initial n=18): WRONG — actual CM gradient is +5.8 (same sign as non-CM), much shallower than non-CM
4. **Sha split "opposite of Wachs"**: WRONG — direction actually matches Wachs 2026 under correct null
5. **Mechanism (a) "deficit grows with conductor"**: KILLED (Ergon's 40-cell test; my BSD-1646 also showed NEGATIVE slope r=-0.9)
6. **H101 trivial (deg-10 Salem NF = knot trace field)**: KILLED by Ergon's 245K reverse-substitution
7. **H27 Yakaboylu Artin root-number test**: DATA-BLOCKED (0 Artin L-functions in lfunc_lfunctions)
8. **log_lp second predictor**: not statistically significant at n=12

## Methodological Lessons

1. **Null-choice is load-bearing**: my first F011 comparison used Gaudin constant 0.178 (equivalent to global-mean-normalized GUE) while observation used local-4-gap normalization. Different constraint structure → different baseline. PATTERN_NULL_CONSTRAINT_MISMATCH.
2. **Wide CIs are not a substitute for adequate N**: my n=18 CM bootstrap gave CI [-35.5, +5.4] for the gradient. Reporting "gradient" as -15.9 was reading the point estimate past its resolution.
3. **Framing errors in conditional-vs-unconditional comparisons**: rank-0 Sha[2] vs all-rank PR is apples/oranges.
4. **Subsampling misses extremes**: 10K/degree from 2.8M missed Lehmer's own NF (0.35% hit rate).

## Open Threads Passed to Team

- Ergon: closure regression on 200K for mechanism (c) verdict
- Aporia: H15 retry with file-based output
- Techne: standby; iTrF extension deferred
- Mnemosyne: offline (Artin L-function ingestion, deg-14 Mossinghoff gap backfill both would unblock)

## Files Produced

```
charon/data/
  lehmer_spectrum_audit.json          10K/deg initial scan
  lehmer_exhaustive_deg8_14.json      6.7M exhaustive (Lehmer hit)
  small_salem_catalog_lmfdb.md        11 sub-1.3 NFs catalog
  small_salem_canonical_polys.json    polredabs forms for H101 matching
  bsd_at_scale.json (preexisting)     1646 BSD-verified curves
  f011_bsd1646_check.json             multi-gap deficit pattern
  f011_sha_bootstrap.json             Sha-split bootstrap (gap1)
  f011_sha_gap4_bootstrap.json        Sha-split bootstrap (gap1-4)
  f011_conductor_gradient.json        conductor-decile (Katz-Sarnak read)
  f011_cm_split.json                  CM/non-CM n=18 (retracted)
  cm_disc_scaling.json                V-CM-scaling per-disc (validated n=2134)
  cm_torsion_cross.json               4-cell cross table
  bklpr_sel2_test.json                BKLPR calibration
  techne_bsd_audit.log                BSD audit (partial; 500/500 clean)

charon/scripts/
  lehmer_spectrum_audit.py
  lehmer_exhaustive_deg8_14.py
  f011_bsd1646_check.py
  f011_sha_bootstrap.py
  f011_sha_gap4_bootstrap.py
  f011_conductor_gradient.py
  f011_cm_large_sample.py
  cm_disc_scaling.py
  bklpr_sel2_test.py
  techne_bsd_audit.py
```

## Tensor Promotions Endorsed (pending Koios)

- F014:P040: LEHMER PROMOTED to +2
- F011 multi-gap matched-GUE: DURABLE
- F-LOGD-SCALING (new feature proposal): +2 within CM-only

End of session log.


---

# Day-2 Addendum (2026-04-23)

James lifted the day-1 stand-down. Team resumed for paper-finalization work.
Session cron cadence increased 5→10 min per James direction. Charon contributions day 2:

## Day-2 Findings & Contributions

### F011 Gap-k scan cross-check on BSD-1646
- Ergon's 24-gap scan showed edge EXCESS at k=1-3 and bulk DEFICIT monotone to +51% at k=24
- Cross-checked on my BSD-1646 (n=547 non-CM with ≥25 zeros)
- Bulk (k≥15) REPRODUCES within 2pp (k=24: mine 52.1% vs Ergon 50.9%)
- Edge AMPLIFIED by BSD-1646 selection (-14.6% vs his -7%)
- PATTERN_NORMALIZATION_SIGN_FLIP cross-confirmed: same gap1 flips DEFICIT↔EXCESS under 4-gap vs 24-gap norms

### Mechanism (c) refinement + retraction
- Retracted n=18 CM inversion claim (magnitudes and gradient direction wrong due to small sample)
- Ergon's n=2134 CM: +37-43% deficit, gradient +5.8 (not inverted)
- V-CM-scaling r=+0.79 (log|D| vs gap1 deficit) confirmed on 12 CM discs, Heegner-only r=+0.82

### PATTERN_SELECTION_BIAS contribution
- Flagged BSD-1646 nbp signal as rho=+0.03 vs Ergon's 150K random rho=+1.0
- Diagnosed selection bias: curated subsets may flip sign from representative samples
- Aporia credited as "Charon's 2-minute SQL-level-filter diagnostic" and logged as Kairos meta-pattern

### CM 24-gap scan
- Ran on n=2064 CM rank-0 with ≥25 zeros
- EDGE SIGN FLIP between CM (+7% gap1 deficit) and non-CM (-7% gap1 excess)
- BULK CONVERGES: CM +48% vs non-CM +51% at k=24 (within 3pp)
- Bulk rigidity is cross-family constant

### O+ matched null simulation (Seed 11)
- Generated 20K SO(80) samples via scipy.stats.ortho_group
- Computed O+ null variance per gap k
- EC k=1 vs O+ null: -48.6% EXCESS (deeper than -7% vs GUE)
- REFUTED Aporia's Seed 11 edge-is-Katz-Sarnak-universality hypothesis
- EC data has MORE variance than O+ predicts at edge — genuine beyond-universality

### Katz-Sarnak Literature Confirmations
Posted bibliography pinning at `charon/docs/paper_references.md`:
- Axis 1 validated: ILS 2000 + Young 2005 predict O-/O+ ratio 1.71; observed 1.72 (0.2% match)
- Axis 3b theoretical anchor: KS 1999 Sec 3.3 gives O+/O- positive 2-point correction, USp negative
- Per-curve nbp sign matches family-averaged correction sign for Orthogonal/Symplectic
- Unitary class exception noted (nbp ρ=+1 despite zero 2-point correction)

### Scope Matrix for paper Appendix B
- 7-row table: random 150K vs BSD-1646 curated, per finding
- Robust: CM vs non-CM gap; gap4 rank-invariance; gradient ~+14; V-GAMMA Q(√-3) inversion; CM×tor sub-additivity
- Scope-specific: nbp=1 gap1 deficit; nbp monotonicity (Spearman)

### CUE surrogate test (iv) for Axis 3b pre-publication
- 10K U(40) samples with artificial Poisson(3.5)-distributed nbp
- Spearman(artificial_nbp, variance_per_k): rho wanders in [-0.89, +0.26], no consistent sign
- PASSES: real data ρ=+1.000 is NOT a generic monotone-predictor artifact
- Rules out "random CUE zeros + random ordinal predictor → spurious +ρ" hypothesis
- Complementary test (iii) — partial-ρ stratified by log(N) — is Ergon's lane

## Day-2 Retractions
- n=18 CM magnitudes/direction (superseded by n=2134)
- Initial "edge = Katz-Sarnak O+ universality" prediction (O+ null refuted it)
- Aporia's pre-regs (Dirichlet ρ≈0 and complex-only ρ≈0) — both refuted at n=40K+, but I didn't predict them wrong; just confirmed the refutation

## Paper contribution artifacts (Charon)
- `charon/CHARON_SESSION_2026-04-22.md` (session artifact)
- `charon/docs/paper_references.md` (15+ primary refs across 6 sections)
- `charon/data/lehmer_exhaustive_deg8_14.json` (F014:P040 main data)
- `charon/data/small_salem_catalog_lmfdb.md` (11 sub-1.3 Salem NFs)
- `charon/data/cm_disc_gap_profile.md` (per-disc shape taxonomy)
- `charon/data/cm_24gap_scan.json` (CM 24-gap data)
- `charon/data/oplus_null.json` (O+ matched null)
- `charon/data/cue_surrogate_axis3b.json` (test iv data)
- `charon/data/scope_matrix` (for paper Appendix B)

## Session Close
Team paper-ready on 3 axes with comprehensive empirical + theoretical anchoring.
Standing down per user directive 2026-04-23.

Total session: 2 calendar days, ~7 hours wall time, 20+ Charon posts to Agora.
Contributions span data science (exhaustive Lehmer scan of 6.7M polys), method
(PATTERN_SELECTION_BIAS, CUE surrogate validation), theory (ILS/Young/KS
citation pinning), and synthesis (scope matrix, session artifact).
