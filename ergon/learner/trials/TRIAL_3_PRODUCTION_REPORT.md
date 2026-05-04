========================================================================
Trial 3 Production Pilot — 1000 episodes x 3 seeds
========================================================================

ACCEPTANCE
  [Completed without error]:                  PASS
  [Found OBSTRUCTION or SECONDARY signature]: FAIL
  [High-lift predicates >= 5]:                PASS

PER-SEED RESULTS
    seed  archive  struct   symb   unif  a-pri  pass  high-lift  1st-obs  1st-sec
      42       46      39      1      2      2   227        104     None     None
     100       38      28      0      2      4   297        168     None     None
    1234       41      35      0      2      1   296        114     None     None

AGGREGATE STATS
  Seeds hitting OBSTRUCTION:    0 of 3
  Seeds hitting SECONDARY:      0 of 3
  First-obstruction episodes:   [None, None, None]
  First-secondary episodes:     [None, None, None]
  structural / uniform ratio:   17.00x
  High-lift predicates total:   386
  Archive sizes (mean):         42
  Substrate-PASSED total:       820

TOP HIGH-LIFT PREDICATES (from seed 100)
  ep  181 (structural    ): lift=22.40, match_size=10, predicate={'pos_x': 1, 'has_diag_neg': True, 'neg_x': 4}
  ep  207 (symbolic      ): lift=22.40, match_size=10, predicate={'pos_x': 1, 'has_diag_neg': True, 'neg_x': 4}
  ep  208 (structural    ): lift=22.40, match_size=10, predicate={'pos_x': 1, 'has_diag_neg': True, 'neg_x': 4}
  ep  430 (structural    ): lift=22.40, match_size=10, predicate={'pos_x': 1, 'has_diag_neg': True, 'neg_x': 4}
  ep  570 (symbolic      ): lift=22.40, match_size=10, predicate={'pos_x': 1, 'has_diag_neg': True, 'neg_x': 4}

NOTE: HardenedObstructionEvaluator requires min_match_group_size >= 3
for substrate-PASS, preventing single-record-overlap lift inflation
from Iter 4 finding.