# Calibration v0 — Murasugi-form smoke test

**Date:** 2026-05-30
**Pre-registered thresholds:** F1 promote ≥ 0.6, F2 contrast ≥ 0.1
**N per source:** 500    **F2 null samples:** 5000    **Seed:** 20260530

## F1 — existing training_weight

```
  source                       n  n_promoted    rate   mean_w
  TRUE_MURASUGI_eq           500           0   0.00%    0.033
  TRUE_MURASUGI_le1          500           0   0.00%    0.429
  TRUE_MURASUGI_le3          500           0   0.00%    0.429
  DECOY_PARITY               500           0   0.00%    0.254
  DECOY_CODOMAIN             500           0   0.00%    0.078
  STRATIFIED_PERM_eq         500           0   0.00%    0.033
  STRATIFIED_PERM_le1        500           0   0.00%    0.429
  STRATIFIED_PERM_le3        500           0   0.00%    0.429
  RANDOM_MARGINAL_eq         500           0   0.00%    0.033
  RANDOM_MARGINAL_le1        500           0   0.00%    0.429
  RANDOM_MARGINAL_le3        500           0   0.00%    0.429
  EXISTING_F1_PROMOTED         0           0   0.00%    0.000
```

## F2 — content-aware (hold vs random-pairing null)

```
  source                    observed    null  contrast  promotes
  TRUE_MURASUGI_eq            35.40%  20.08%     0.153      True
  TRUE_MURASUGI_le1           78.80%  57.36%     0.214      True
  TRUE_MURASUGI_le3          100.00%  96.80%     0.032     False
  DECOY_PARITY               100.00% 100.00%     0.000     False
  DECOY_CODOMAIN             100.00% 100.00%     0.000     False
  STRATIFIED_PERM_eq          22.40%  20.32%     0.021     False
  STRATIFIED_PERM_le1         61.40%  59.00%     0.024     False
  STRATIFIED_PERM_le3         96.80%  96.94%     0.001     False
  RANDOM_MARGINAL_eq          19.00%  19.08%     0.001     False
  RANDOM_MARGINAL_le1         56.80%  56.74%     0.001     False
  RANDOM_MARGINAL_le3         97.40%  97.32%     0.001     False
  EXISTING_F1_PROMOTED     per-record evaluation: 0/0 pass contrast threshold (0.00%)
      relations seen: {}
```

## Pre-registered outcome interpretation

- TRUE_MURASUGI_le1 should be the strongest signal (tight relation + true math).
  If F1 promotes it AND DECOYs at same rate → F1 PATHOLOGICAL (shape-driven).
  If F2 contrasts it high AND DECOYs low → F2 CALIBRATED.

- DECOY_PARITY and DECOY_CODOMAIN are the artifact-rejection probes.
  F2 should give them ~0 contrast (observed ≈ null).

- STRATIFIED_PERM_le1 measures coupling-vs-distributional-shape.
  If TRUE_MURASUGI_le1 contrast > STRATIFIED_PERM_le1 contrast by >0.10,
  F2 distinguishes real coupling from shape-matched permutation.

- EXISTING_F1_PROMOTED rate under F2 is the key honest accounting:
  this is what fraction of the 2,351 lifetime promoted records would
  pass a content-aware filter. Low rate = current corpus is mostly
  shape-promoted artifacts.

## Verdict (computed from above)

### F1 (existing training_weight)

**Verdict: OVER-REJECTING — F1 promotes 0% of all sources, including TRUE Murasugi**

F1 mean_weight is 0.43 for bridge_extension+abs_diff_le_K (capped by relation-table downweight) and 0.03 for equal (relation-table floor). F1's promote threshold of 0.6 is never reached for records bearing a 'relation' field in claim_payload. The 2,351 lifetime promoted records must come from a metadata path that lacks the relation field (triggering the kind-fallback at 0.55 × 1.3 = 0.715).

### F2 (content-aware contrast)

**Verdict: CALIBRATED**

F2 promoted 2/3 TRUE sources (signal recovery) and 0/8 non-TRUE sources (clean artifact rejection). Murasugi inequality is recoverable from the catalog at tight relation specificities (equal, abs_diff_le_1) but codomain-trivial at loose ones (abs_diff_le_3).

## Substrate-level conclusion

**The decisive substrate question is answered in the positive for this slice of the claim ecology.** Murasugi's inequality is recoverable by a content-aware filter using only the substrate's existing invariant menu (three_genus, signature). The existing F1 filter cannot recover it because F1 evaluates only metadata shape. The path forward is to expand F2 to 4 more known relations (Hasse bound, EC torsion divides, knot determinant parity, modular degree growth) and verify F2 generalizes without re-tuning.
