========================================================================
Trial 2 Dry-Run Report (seed=42, n=200)
========================================================================
Elapsed: 0.02s
Episodes/sec: 9523.7

ACCEPTANCE
  [Primary] structural >= 1.5x uniform fills: PASS (structural=11, uniform=2, ratio=5.50)
  [Secondary] archive coverage >= 10: PASS (actual=19)
  [Tertiary] trivial rate in [0, 30%]: PASS (actual=0.000)
  [Quaternary] scheduler min-share compliant: PASS

OPERATOR FILL COUNTS
  anti_prior        :    3 cells (efficiency: 0.250)
  structural        :   11 cells (efficiency: 0.108)
  structured_null   :    1 cells (efficiency: 0.062)
  symbolic          :    2 cells (efficiency: 0.036)
  uniform           :    2 cells (efficiency: 0.133)

SCHEDULER CUMULATIVE SHARES
  anti_prior        : 0.060
  structural        : 0.510
  structured_null   : 0.080
  symbolic          : 0.275
  uniform           : 0.075

COVERAGE DIVERGENCES (Jaccard distance between operator-cell-sets)
  anti_prior_vs_structured_null      : 1.000
  anti_prior_vs_uniform              : 1.000
  structural_vs_anti_prior           : 1.000
  structural_vs_uniform              : 1.000
  symbolic_vs_uniform                : 1.000

PROMOTED: 21
TRIVIAL REJECTS: 0

Note: PROMOTE rate at MVP scope uses MVPSubstrateEvaluator stub
calibrated against Path B's empirical 0/30000 finding; near-zero
promotes is expected, not failure.