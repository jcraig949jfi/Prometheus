# Calibration v3 — non-mutated falsification of the v2 corpus sweep

**Date:** 2026-06-03
**Scan budget:** 30,000,000 records (matched to v2's window: sorted-file, oldest-N)
**F2 threshold:** 0.1   **Min non-mutated group size:** 50
**Filter:** records with a `parent_record_id` (mutation-derived) EXCLUDED; only independently-sampled records scored.

## Coverage

- Records scanned: **30,000,000**
- Evaluable (relation-bearing, SHADOW+REJECTED): **21,374,220**
- Of which mutation-derived (had parent_record_id): **7,200,918** (33.7% of evaluable)
- Independently-sampled (non-mutated, scored): **14,173,302**
- Distinct groups: **41,545**  |  with >= 50 non-mutated: **96**

## F2 verdict on NON-MUTATED groups

- Groups promoted by F2 (non-mutated): **61** of 96 (63.54%)
- Non-mutated records in promoted groups: **9,673,437** of 14,173,302 (68.25%)

Compare to v2 (all records): 198/1068 groups (18.54%) promoted. The delta
between this non-mutated rate and v2's all-record rate is the share of v2's
'signal' that was parent-inheritance selection bias.

## Watch group — strongest non-mutated candidate v2 named

`knot/trace_field_class abs_diff_le_0 ec/torsion` (v2 reported: 31.9% vs 7.1% null on 1,694 records)

- **COLLAPSES below eligibility.** all-record n=1,694 but only 0 non-mutated records (< 50). The v2 signal in this group was 100.0% mutation-derived.

## Top 30 non-mutated groups by contrast

```
   contrast sub_hold    null    n_nm   mut%  group
      0.274   30.60%   3.18% 168,640  30.6%  knot/crossing_number abs_diff_le_3 ec/rank
      0.255   35.94%  10.44% 169,434  30.2%  knot/trace_field_class abs_diff_le_3 ec/rank
      0.255   25.47%   0.00% 169,139  29.5%  knot/three_genus abs_diff_le_3 ec/conductor
      0.249   24.87%   0.00% 169,176  29.7%  knot/signature abs_diff_le_3 ec/conductor
      0.249   25.46%   0.60% 169,169  29.4%  knot/crossing_number divides ec/torsion
      0.243   29.14%   4.88% 168,916  30.3%  knot/determinant divides ec/tamagawa_product
      0.242   26.49%   2.30% 168,930  29.8%  knot/determinant divides ec/torsion
      0.235   23.46%   0.00% 168,898  30.0%  knot/crossing_number abs_diff_le_3 ec/conductor
      0.234   31.50%   8.08% 169,296  30.4%  knot/crossing_number abs_diff_le_3 ec/torsion
      0.234   26.19%   2.84% 169,194  29.4%  knot/trace_field_class divides ec/torsion
      0.232   23.16%   0.00% 169,624  29.1%  knot/trace_field_class abs_diff_le_3 ec/conductor
      0.229   22.94%   0.00% 169,409  28.9%  knot/determinant abs_diff_le_3 ec/conductor
      0.225   32.52%  10.02% 169,376  30.0%  knot/determinant abs_diff_le_3 ec/rank
      0.223   22.26%   0.00% 169,363  30.2%  knot/crossing_number equal ec/rank
      0.222   22.21%   0.00% 169,122  29.4%  knot/signature equal ec/conductor
      0.221   22.77%   0.68% 169,057  29.8%  knot/determinant equal ec/rank
      0.220   25.98%   4.02% 169,411  29.7%  knot/trace_field_class equal ec/rank
      0.218   21.84%   0.00% 168,898  29.6%  knot/trace_field_class equal ec/conductor
      0.217   22.11%   0.38% 169,202  29.5%  knot/crossing_number equal ec/torsion
      0.216   21.63%   0.00% 169,589  29.7%  knot/three_genus equal ec/conductor
      0.215   37.16%  15.62% 169,012  30.0%  knot/determinant equal_mod_2 ec/tamagawa_product
      0.214   21.40%   0.00% 168,621  30.1%  knot/crossing_number equal ec/conductor
      0.213   21.90%   0.56% 169,616  29.3%  knot/determinant equal ec/tamagawa_product
      0.213   21.34%   0.00% 169,378  30.0%  knot/determinant equal ec/conductor
      0.211   22.42%   1.32% 169,420  29.7%  knot/determinant equal ec/torsion
      0.208   23.05%   2.24% 169,536  29.5%  knot/trace_field_class equal ec/torsion
      0.208   32.78%  11.98% 169,207  29.6%  knot/determinant abs_diff_le_3 ec/torsion
      0.206   40.42%  19.86% 168,812  29.3%  knot/determinant divides ec/conductor
      0.204   21.69%   1.30% 169,669  30.4%  knot/signature equal ec/tamagawa_product
      0.198   38.18%  18.34% 169,140  29.6%  knot/trace_field_class divides ec/tamagawa_product
```

## Interpretation

Per `feedback_assume_wrong` + `feedback_ai_to_ai_inflation`, reported as
signal-shaped pattern detection, NOT confirmed cross-catalog structure.

- If the non-mutated promote rate is far below v2's 18.5% and the watch
  group collapses, v2's corpus 'signal' was substantially mutation-selection
  bias — a substrate self-finding, not catalog coupling.
- Surviving non-mutated high-contrast groups are the genuine residual worth
  a marginal-explicit-compute pass (v2 caveat #4) before any further claim.

**Sampling-window note** (`feedback_sampling_strategy_is_analysis`): this scans
the OLDEST N records (sorted batch filenames), matched to v2 for comparability.
It is NOT a uniform sample of the 658M-record lifetime corpus. A mtime-stratified
re-run is the natural follow-up if the residual survives.