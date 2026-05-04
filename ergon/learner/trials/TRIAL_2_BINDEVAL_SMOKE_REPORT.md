========================================================================
BindEvalKernelV2 Smoke Test (200 episodes)
========================================================================

ACCEPTANCE
  [Completed without error]: PASS
  [structural > uniform]:    PASS
  [p50 latency < 50ms]:      PASS

TIMING
  Init:                16.0 ms
  Total elapsed:       0.28 s
  Per-episode avg:     1.38 ms
  Per-episode p50:     1.00 ms
  Per-episode p95:     2.00 ms

RESULTS
  Archive cells filled:    177
  Substrate-PASSED:        0
  Won-cell (archive elite): 192
  Trivial rejects:         9
  structural / uniform:    7.00x

FILL COUNTS
  anti_prior        :   10
  structural        :   91
  structured_null   :   15
  symbolic          :   48
  uniform           :   13

BindEvalEvaluator cache size: 197 entries