# Calibration v2 — Corpus-wide F2 sweep

**Date:** 2026-05-30
**Scan budget:** 30,000,000 records
**F2 threshold:** 0.1
**Min group size:** 50

## Coverage

- Records scanned: **30,000,000**
- SHADOW_CATALOG records: **9,121,654** (30.41% of scan)
- REJECTED records: **12,252,566** (40.84% of scan)
- F2-evaluable (relation-bearing, all verdicts): **21,374,220**
- Distinct (cat_a, inv_a, cat_b, inv_b, rel) groups: **41,545**
- Groups with ≥ 50 records (analyzed): **1,068**

## F2 verdict on the analyzed groups

- Groups promoted by F2: **198** of 1,068 (18.54%)
- Records in promoted groups: **11,215,377** of 20,994,294 (53.42%)

## Top 30 highest-contrast groups (CONTENT-BEARING SIGNAL)

```
   contrast sub_hold    null       n  group
      0.651   86.56%  21.50%   2,195  knot/determinant abs_diff_le_1 ec/tamagawa_product
      0.400   59.93%  19.92%   3,229  knot/determinant abs_diff_le_2 ec/tamagawa_product
      0.354   86.21%  50.84%      58  knot/signature abs_diff_le_58 ec/tamagawa_product
      0.334   94.69%  61.28%     113  knot/signature abs_diff_le_46 ec/tamagawa_product
      0.323   92.59%  60.30%      54  knot/determinant abs_diff_le_51 ec/tamagawa_product
      0.316   93.10%  61.52%      58  knot/determinant abs_diff_le_47 ec/tamagawa_product
      0.306   83.33%  52.72%      60  knot/determinant abs_diff_le_49 ec/tamagawa_product
      0.295   89.29%  59.78%      56  knot/determinant abs_diff_le_61 ec/tamagawa_product
      0.290   84.10%  55.08%   1,302  knot/signature abs_diff_le_14 ec/tamagawa_product
      0.281   88.82%  60.76%     152  knot/signature abs_diff_le_42 ec/tamagawa_product
      0.279   82.35%  54.48%      68  knot/signature abs_diff_le_56 ec/tamagawa_product
      0.276   89.30%  61.66%     215  knot/signature abs_diff_le_40 ec/tamagawa_product
      0.268   87.50%  60.72%     112  knot/trace_field_class abs_diff_le_36 ec/tamagawa_product
      0.268   81.07%  54.30%   2,293  knot/signature abs_diff_le_10 ec/tamagawa_product
      0.264   96.46%  70.02%     113  knot/signature abs_diff_le_52 ec/tamagawa_product
      0.263   93.16%  66.88%     117  knot/signature abs_diff_le_54 ec/tamagawa_product
      0.263   79.14%  52.88%   1,611  knot/signature abs_diff_le_12 ec/tamagawa_product
      0.262   79.71%  53.48%     350  knot/signature abs_diff_le_30 ec/tamagawa_product
      0.262   40.17%  66.40%     234  knot/determinant abs_diff_le_40 ec/tamagawa_product
      0.260   83.70%  57.72%   1,037  knot/signature abs_diff_le_16 ec/tamagawa_product
      0.256   84.47%  58.82%     412  knot/signature abs_diff_le_22 ec/tamagawa_product
      0.256  100.00%  74.36%     167  knot/signature abs_diff_le_12 ec/torsion
      0.253   86.62%  61.34%     299  knot/signature abs_diff_le_36 ec/tamagawa_product
      0.247   31.88%   7.14%   1,694  knot/trace_field_class abs_diff_le_0 ec/torsion
      0.241   65.08%  40.96%   2,285  knot/determinant abs_diff_le_5 ec/tamagawa_product
      0.241   74.92%  50.84%     614  knot/signature abs_diff_le_20 ec/tamagawa_product
      0.239   91.28%  67.38%     172  knot/signature abs_diff_le_48 ec/tamagawa_product
      0.236   90.20%  66.58%      51  knot/signature abs_diff_le_62 ec/tamagawa_product
      0.230   53.56%  76.60%     267  knot/determinant abs_diff_le_42 ec/tamagawa_product
      0.227   85.00%  62.32%      60  knot/crossing_number abs_diff_le_48 ec/tamagawa_product
```

## Bottom 30 lowest-contrast groups (CONTENT-FREE — artifacts/trivialities)

```
   contrast sub_hold    null       n  group
      0.000  100.00% 100.00%      50  knot/three_genus abs_diff_le_7919 ec/conductor
      0.000  100.00% 100.00%      81  knot/trace_field_class abs_diff_le_139 ec/tamagawa_product
      0.000  100.00% 100.00%     351  knot/determinant abs_diff_le_45 ec/rank
      0.000  100.00% 100.00%      75  knot/trace_field_class abs_diff_le_9445 ec/conductor
      0.000  100.00% 100.00%      65  knot/trace_field_class abs_diff_le_1795 ec/conductor
      0.000    0.00%   0.00%      59  knot/trace_field_class abs_diff_le_1793 ec/conductor
      0.000  100.00% 100.00%      50  knot/nf_class_number abs_diff_le_64 ec/tamagawa_product
      0.000  100.00% 100.00%      53  knot/trace_field_class abs_diff_le_187 ec/tamagawa_product
      0.000  100.00% 100.00%      51  knot/trace_field_class abs_diff_le_1955 ec/conductor
      0.000  100.00% 100.00%      51  knot/trace_field_class abs_diff_le_2035 ec/conductor
      0.000  100.00% 100.00%      63  knot/three_genus abs_diff_le_7349 ec/conductor
      0.000  100.00% 100.00%     111  knot/trace_field_class abs_diff_le_4795 ec/conductor
      0.000   90.00%  90.00%      80  knot/crossing_number abs_diff_le_9342 ec/conductor
      0.000    0.00%   0.00%      52  knot/trace_field_class abs_diff_le_3119 ec/conductor
      0.000    0.00%   0.00%      71  knot/trace_field_class abs_diff_le_5603 ec/conductor
      0.000    0.00%   0.00%      56  knot/trace_field_class abs_diff_le_5033 ec/conductor
      0.000  100.00% 100.00%      50  knot/trace_field_class abs_diff_le_5299 ec/conductor
      0.000  100.00% 100.00%      53  knot/trace_field_class abs_diff_le_6595 ec/conductor
      0.000    0.00%   0.00%      66  knot/trace_field_class abs_diff_le_2033 ec/conductor
      0.000  100.00% 100.00%      75  knot/trace_field_class abs_diff_le_9345 ec/conductor
      0.000    0.00%   0.00%      98  knot/trace_field_class abs_diff_le_4793 ec/conductor
      0.000    0.00%   0.00%      62  knot/trace_field_class abs_diff_le_6393 ec/conductor
      0.000  100.00% 100.00%      52  knot/trace_field_class abs_diff_le_6045 ec/conductor
      0.000  100.00% 100.00%      77  knot/three_genus abs_diff_le_9349 ec/conductor
      0.000    0.00%   0.00%      61  knot/trace_field_class abs_diff_le_3689 ec/conductor
      0.000    0.00%   0.00%      50  knot/trace_field_class abs_diff_le_6713 ec/conductor
      0.000  100.00% 100.00%      78  knot/trace_field_class abs_diff_le_3595 ec/conductor
      0.000    0.00%   0.00%      64  knot/trace_field_class abs_diff_le_7643 ec/conductor
      0.000  100.00% 100.00%      51  knot/trace_field_class abs_diff_le_8974 ec/conductor
      0.000  100.00% 100.00%      56  knot/trace_field_class abs_diff_le_7645 ec/conductor
```

## Substrate-level interpretation

This sweep takes the substrate's entire SHADOW_CATALOG corpus and
asks: how many (invariant pair × relation) groups produce a
meaningful F2 contrast?

- High-contrast groups encode real coupling between invariants —
  the relation holds at substantially higher rate than chance.
- Low-contrast groups are catalog-volume / codomain-bound /
  parity-shaped trivialities — the relation holds by structure
  of the values, not by mathematical coupling.

**198/1068 (18.5%) of substrate-analyzed
invariant-pair-relation groups have substrate_hold meaningfully
divergent from random-pairing null.**

These groups contain 11,215,377 substrate records.

**Most are mutated-K relations** (C2/C4/D2 mutators turning
`abs_diff_le_3` into `abs_diff_le_47`, etc.). These reflect
PARENT-RECORD SELECTION BIAS, not coupling — mutators take an
existing SHADOW record and modify its K; the value distribution
inherits the parent's selection. Excluding mutated-K groups, the
signal-bearing pool shrinks substantially.

## Doctrinal honesty caveats

Per `feedback_assume_wrong` and `feedback_ai_to_ai_inflation`, this
result is reported as **signal-shaped pattern detection, not
confirmed cross-catalog mathematical structure**. The 12 promoted
groups are ALL cross-catalog (knot × EC), with the strongest being
parity-style correlations between knot-genus / knot-crossing-number
and EC-rank / EC-torsion.

Before treating these as structural findings, falsify against:

1. **Marginal-distribution audit.** Confirm the null rate (computed
   over the source pool's value distribution) is well-estimated and
   not biased by SHADOW-only sampling. A separate sweep over BOTH
   SHADOW and REJECTED records, computing marginal hold rates, would
   give an independent null.

2. **Operator-transformed records.** a3 emits records with
   value_a_raw and value_b_raw that were NOT directly compared —
   the relation was checked on f(value_a_raw), g(value_b_raw). Raw-
   value re-evaluation in this scan underestimates the true hold
   rate for a3-style records. This may explain why observed rates
   are < 100% on SHADOW records.

3. **Selection-bias check.** Generators sample (knot, EC) pairs via
   independent rng.choice. But the BANDIT downweights low-yield
   generators across fires, potentially biasing the corpus toward
   gens that preferentially emit certain object pairs. A re-run on
   the same scan budget restricted to a single generator would
   discriminate.

4. **Catalog marginal explicit-compute.** Independently estimate the
   parity of every EC's rank and every knot's three_genus across
   the full catalog. If those marginals are skewed enough (e.g.,
   most rank-0 ECs are over-represented), the 'observed' rate may
   inherit catalog-volume bias rather than encoding coupling.

The honest claim: **F2 calibrates on synthetic known-true relations**
(v0 Murasugi, v1 EC-torsion-divides). On the substrate's existing
corpus, F2 surfaces ~18% group-level contrast, but a substantial
fraction is mutation-induced selection bias. A small residual set of
non-mutated high-contrast groups (e.g., trace_field_class abs_diff_le_0
torsion at 31.9% vs 7.1% null on 1,694 records) may represent real
catalog coupling worth investigating, but are not by themselves
sufficient evidence of widespread substrate-detected signal.

**Update relative to v2.0:** the cross-catalog parity contrast
(three_genus equal_mod_2 rank at 77.8% vs 50.6%) was an ARTIFACT of
a field-name bug — v2.0 only saw a3 operator-transformed records,
which exhibit parity excess for unrelated reasons. v2.1 with the
bug fixed shows parity relations have substrate_hold ≈ null ≈ 50%
(contrast ~0) — no cross-catalog parity coupling detected.