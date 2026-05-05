========================================================================
Trial 2 Production Pilot — 1000 episodes x 5 seeds
========================================================================

ACCEPTANCE
  [Primary] structural >= 1.5x uniform with Welch p<0.05: PASS (ratio mean=5.58, p=0.0000)
  [Secondary] archive coverage >= 250: PASS (mean=686)
  [Tertiary] trivial rate <=30% per seed: PASS
  [Quaternary] scheduler min-share compliance per seed: PASS

PER-SEED FILL COUNTS
  seed  archive  struct   symb   unif  a-prior  s-null  promotes   triv%
    42      701     320    213     61       50      57         0   3.70%
   100      700     334    212     54       50      50         0   4.90%
  1234      679     311    207     57       52      52         0   3.50%
  31415      652     301    192     54       47      58         0   3.90%
  271828      699     333    205     61       49      51         0   3.10%

STATISTICAL TEST: structural_fills vs uniform_fills
  Welch's t-statistic: 40.109
  Welch's p-value:     0.0000
  Ratio mean ± stdev:  5.58 ± 0.36
  Per-seed ratios:     [5.25, 6.19, 5.46, 5.57, 5.46]

ARCHIVE SIZE STABILITY
  Mean ± stdev:        686 ± 21.2 cells

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
  Won-cell total:         3553

Note: PROMOTE rate at MVP scope uses tightened MVPSubstrateEvaluator stub
(promote_rate=0.0001); calibrated against Techne's Path B empirical
0/30000 PROMOTEs at degree 10 + +-3.