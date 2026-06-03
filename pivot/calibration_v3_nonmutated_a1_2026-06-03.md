# Calibration v3 — non-mutated falsification of the v2 corpus sweep

**Date:** 2026-06-03
**Scan budget:** 30,000,000 records (matched to v2's window: sorted-file, oldest-N)
**F2 threshold:** 0.1   **Min non-mutated group size:** 50
**Filter:** records with a `parent_record_id` (mutation-derived) EXCLUDED; only independently-sampled records scored.

## Coverage

- Records scanned: **30,000,000**
- Evaluable (relation-bearing, SHADOW+REJECTED): **4,793,352**
- Of which mutation-derived (had parent_record_id): **0** (0.0% of evaluable)
- Independently-sampled (non-mutated, scored): **4,793,352**
- Distinct groups: **96**  |  with >= 50 non-mutated: **96**

## F2 verdict on NON-MUTATED groups

- Groups promoted by F2 (non-mutated): **0** of 96 (0.00%)
- Non-mutated records in promoted groups: **0** of 4,793,352 (0.00%)

Compare to v2 (all records): 198/1068 groups (18.54%) promoted. The delta
between this non-mutated rate and v2's all-record rate is the share of v2's
'signal' that was parent-inheritance selection bias.

## Watch group — strongest non-mutated candidate v2 named

`knot/trace_field_class abs_diff_le_0 ec/torsion` (v2 reported: 31.9% vs 7.1% null on 1,694 records)

- Group not present in this scan window.

## Top 30 non-mutated groups by contrast

```
   contrast sub_hold    null    n_nm   mut%  group
      0.023   51.12%  48.86%  58,135   0.0%  knot/three_genus equal_mod_2 ec/conductor
      0.019   48.05%  49.98%  57,987   0.0%  knot/three_genus divides ec/torsion
      0.018   65.98%  67.78%  58,264   0.0%  knot/three_genus divides ec/rank
      0.018   53.91%  55.66%  58,059   0.0%  knot/signature equal_mod_2 ec/torsion
      0.015   63.10%  64.64%  57,956   0.0%  knot/signature abs_diff_le_3 ec/rank
      0.015   78.44%  79.92%  57,751   0.0%  knot/signature equal_mod_2 ec/conductor
      0.015   53.60%  55.08%  58,139   0.0%  knot/signature divides ec/rank
      0.014   50.21%  48.86%  57,956   0.0%  knot/trace_field_class divides ec/rank
      0.012   39.38%  40.54%   9,052   0.0%  knot/nf_class_number equal ec/rank
      0.011   60.14%  59.00%  58,186   0.0%  knot/signature equal_mod_2 ec/rank
      0.011   21.23%  22.36%  58,058   0.0%  knot/determinant equal_mod_2 ec/conductor
      0.011   50.91%  49.80%  57,979   0.0%  knot/determinant divides ec/rank
      0.010   85.32%  86.32%  58,220   0.0%  knot/signature equal_mod_2 ec/tamagawa_product
      0.010   46.06%  45.06%  58,166   0.0%  knot/signature divides ec/tamagawa_product
      0.010   50.42%  49.44%  57,873   0.0%  knot/three_genus equal_mod_2 ec/rank
      0.010   33.62%  34.60%  58,153   0.0%  knot/crossing_number divides ec/conductor
      0.010   39.76%  40.72%  57,910   0.0%  knot/determinant equal_mod_2 ec/rank
      0.009   72.12%  73.06%  58,480   0.0%  knot/three_genus divides ec/tamagawa_product
      0.009   52.99%  52.08%  58,051   0.0%  knot/crossing_number equal_mod_2 ec/rank
      0.007    6.31%   5.58%  57,932   0.0%  knot/crossing_number equal ec/tamagawa_product
      0.006   13.40%  12.78%  57,966   0.0%  knot/signature abs_diff_le_3 ec/tamagawa_product
      0.006   10.01%   9.44%  58,139   0.0%  knot/determinant abs_diff_le_3 ec/rank
      0.005   40.64%  40.10%   8,987   0.0%  knot/nf_class_number equal_mod_2 ec/rank
      0.005   41.78%  41.26%   9,069   0.0%  knot/nf_class_number equal ec/torsion
      0.005   41.28%  40.76%  57,864   0.0%  knot/trace_field_class abs_diff_le_3 ec/tamagawa_product
      0.005   41.08%  40.58%   9,011   0.0%  knot/nf_class_number abs_diff_le_3 ec/tamagawa_product
      0.005    9.94%  10.44%  57,909   0.0%  knot/three_genus equal ec/tamagawa_product
      0.005    4.95%   5.44%  58,122   0.0%  knot/signature equal ec/torsion
      0.005   21.55%  22.04%  57,676   0.0%  knot/signature divides ec/torsion
      0.005   26.61%  26.12%  57,978   0.0%  knot/crossing_number abs_diff_le_3 ec/tamagawa_product
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