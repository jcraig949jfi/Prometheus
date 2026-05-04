========================================================================
Trial 2 Production Pilot — 1000 episodes x 5 seeds
========================================================================

ACCEPTANCE
  [Primary] structural >= 1.5x uniform with Welch p<0.05: PASS (ratio mean=5.91, p=0.0000)
  [Secondary] archive coverage >= 250: PASS (mean=684)
  [Tertiary] trivial rate <=30% per seed: PASS
  [Quaternary] scheduler min-share compliance per seed: PASS

PER-SEED FILL COUNTS
  seed  archive  struct   symb   unif  a-prior  s-null  promotes   triv%
    42      688     306    221     65       48      48         0   4.40%
   100      672     307    228     47       45      45         0   3.80%
  1234      680     307    211     50       56      56         0   4.40%
  31415      672     331    201     45       45      50         0   3.70%
  271828      707     324    211     67       51      54         0   4.70%

STATISTICAL TEST: structural_fills vs uniform_fills
  Welch's t-statistic: 37.194
  Welch's p-value:     0.0000
  Ratio mean ± stdev:  5.91 ± 1.13
  Per-seed ratios:     [4.71, 6.53, 6.14, 7.36, 4.84]

ARCHIVE SIZE STABILITY
  Mean ± stdev:        684 ± 14.6 cells

COVERAGE DIVERGENCE STABILITY (Jaccard distance, mean ± stdev across seeds)
  anti_prior_vs_structured_null      : 1.000 ± 0.000
  anti_prior_vs_uniform              : 1.000 ± 0.000
  structural_vs_anti_prior           : 1.000 ± 0.000
  structural_vs_uniform              : 1.000 ± 0.000
  symbolic_vs_uniform                : 1.000 ± 0.000

SUBSTRATE-PASS RATE (the load-bearing PROMOTE metric)
  Substrate-PASSED total: 0
  Per episode (avg):      0.000000

ARCHIVE CELL CLAIMS (cell-fill, not substrate-PROMOTE)
  Won-cell total:         3570

Note: PROMOTE rate at MVP scope uses tightened MVPSubstrateEvaluator stub
(promote_rate=0.0001); calibrated against Techne's Path B empirical
0/30000 PROMOTEs at degree 10 + +-3.