# Calibration v3c — per-generator audit of non-mutated F2 contrast

**Date:** 2026-06-03
**Scan budget:** 30,000,000 records (non-mutated only)
**Null:** within-generator random re-pairing of that generator's own values.
**Min (generator, group) size:** 50   **F2 threshold:** 0.1

A generator with promote_rate approx 0 and mean_contrast approx 0 is
UNIFORM-LIKE (its pairings are independent, like a1). A generator with
high promote_rate / mean_contrast is BIAS-INJECTING: its emitted pairs
are non-independent (targeting) or its stored raw values are not the
values the relation was evaluated on (operator transform).

## Per-generator summary (sorted by promote_rate)

```
    gen  groups  promoted  prom_rate  mean_ctr  max_ctr      records
     g5      80        78     97.50%     0.639    1.000       21,015
     g4      96        91     94.79%     0.619    1.000    2,888,840
     a3      96        34     35.42%     0.091    0.332    3,196,599
     f4      96         0      0.00%     0.009    0.081       21,627
     f2      96         0      0.00%     0.007    0.041       21,627
     f3      96         0      0.00%     0.005    0.021    3,229,630
     a1      96         0      0.00%     0.004    0.030    4,793,352
```

## Top 25 (generator, group) cells by contrast

```
    gen  contrast     sub    null         n  group
     g4     1.000 100.00%   0.00%    35,139  knot/trace_field_class abs_diff_le_3 ec/conductor
     g4     1.000 100.00%   0.00%    35,067  knot/three_genus abs_diff_le_3 ec/conductor
     g4     1.000 100.00%   0.00%    35,293  knot/three_genus equal ec/conductor
     g4     1.000 100.00%   0.00%    34,919  knot/signature abs_diff_le_3 ec/conductor
     g4     1.000 100.00%   0.00%     5,527  knot/nf_class_number abs_diff_le_3 ec/conductor
     g5     1.000 100.00%   0.00%       248  knot/three_genus equal ec/conductor
     g5     1.000 100.00%   0.00%       242  knot/trace_field_class equal ec/conductor
     g4     1.000 100.00%   0.00%    35,108  knot/crossing_number equal ec/rank
     g5     1.000 100.00%   0.00%       247  knot/signature equal ec/conductor
     g4     1.000 100.00%   0.00%    34,944  knot/signature equal ec/conductor
     g4     1.000 100.00%   0.00%    35,046  knot/crossing_number equal ec/conductor
     g5     1.000 100.00%   0.00%       273  knot/determinant abs_diff_le_3 ec/conductor
     g5     1.000 100.00%   0.00%       239  knot/crossing_number equal ec/rank
     g5     1.000 100.00%   0.00%       224  knot/determinant equal ec/conductor
     g4     1.000 100.00%   0.00%     5,360  knot/nf_class_number equal ec/conductor
     g5     1.000 100.00%   0.00%       253  knot/crossing_number equal ec/conductor
     g5     1.000 100.00%   0.00%       284  knot/signature abs_diff_le_3 ec/conductor
     g5     1.000 100.00%   0.00%       257  knot/trace_field_class abs_diff_le_3 ec/conductor
     g4     1.000 100.00%   0.00%    35,064  knot/trace_field_class equal ec/conductor
     g5     1.000 100.00%   0.00%       244  knot/crossing_number abs_diff_le_3 ec/conductor
     g4     1.000 100.00%   0.00%    34,868  knot/crossing_number abs_diff_le_3 ec/conductor
     g5     1.000 100.00%   0.00%       246  knot/three_genus abs_diff_le_3 ec/conductor
     g4     1.000 100.00%   0.00%    35,089  knot/determinant abs_diff_le_3 ec/conductor
     g4     1.000  99.99%   0.00%    35,180  knot/determinant equal ec/conductor
     g5     0.996 100.00%   0.38%       264  knot/crossing_number divides ec/torsion
```

## Interpretation

Per `feedback_assume_wrong`: the within-generator null re-pairs each
generator's OWN observed values, so a positive contrast means that
generator's (a,b) pairings are not independent draws from its own
marginals — selection or transform. a1 is the calibration floor
(independent by construction). Generators ranking high here are the
ones whose SHADOW verdicts inflated the v2 corpus signal; their records
should not be scored against a raw-value null in the content-aware
corpus without first reconciling the transform / selection mechanism.