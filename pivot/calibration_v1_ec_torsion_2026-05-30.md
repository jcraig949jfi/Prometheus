# Calibration v1 — EC torsion divides #E(F_p)

**Date:** 2026-05-30
**Pre-registered thresholds:** F1 promote ≥ 0.6, F2 contrast ≥ 0.1
**N per source:** 500    **F2 null samples:** 5000    **Seed:** 20260530
**Restriction:** ECs with torsion >= 2 (n=577 of 1000)

## F1 — existing training_weight

```
  source                   n  n_promoted    rate   mean_w
  TRUE_EC_TORSION        500           0   0.00%    0.319
  DECOY_PARITY           500           0   0.00%    0.254
  DECOY_CODOMAIN         500           0   0.00%    0.319
  STRATIFIED_PERM        500           0   0.00%    0.319
  RANDOM_MARGINAL        500           0   0.00%    0.319
```

## F2 — content-aware (observed vs random-pairing null)

```
  source                observed    null  contrast  promotes
  TRUE_EC_TORSION         99.80%  88.14%     0.117      True
  DECOY_PARITY           100.00% 100.00%     0.000     False
  DECOY_CODOMAIN         100.00% 100.00%     0.000     False
  STRATIFIED_PERM         89.60%  88.64%     0.010     False
  RANDOM_MARGINAL         91.60%  89.40%     0.022     False
```

## Verdict

**CALIBRATED — F2 generalizes from Murasugi to EC torsion without re-tuning**

F2 promoted TRUE_EC_TORSION (contrast 0.117) and rejected all 4 non-TRUE sources. The contrast metric and threshold (0.10) work for a second, structurally different relation without modification. The substrate's claim ecology supports content-aware filtering on at least two distinct mathematical structures.
