========================================================================
Trial 3 5K Scaling Pilot — 5000 episodes x 3 seeds
========================================================================

ACCEPTANCE
  [Completed without error]:                       PASS
  [Found OBSTRUCTION or SECONDARY (exact match)]: PASS
  [Found OBSTRUCTION or SECONDARY (discriminator)]: PASS
  [High-lift predicates >= 5]:                     PASS

PER-SEED RESULTS
    seed  archive  struct   symb   unif  a-pri  pass  high-lift  1st-obs  1st-sec
      42       56      43      7      1      3  1462        840     1485      617
     100       59      47      2      2      7  1428        733     1909      504
    1234       57      44      8      2      2  1443        630     1248     None

AGGREGATE STATS
  Seeds hitting OBSTRUCTION (exact):         3 of 3
  Seeds hitting OBSTRUCTION (discriminator): 3 of 3
  Seeds hitting SECONDARY (exact):           2 of 3
  Seeds hitting SECONDARY (discriminator):   2 of 3
  First-obstruction-exact episodes:    [1485, 1909, 1248]
  First-secondary-exact episodes:      [617, 504, None]
  First-obstruction-disc episodes:    [73, 784, 1248]
  First-secondary-disc episodes:      [617, 504, None]
  Sample obstruction discriminator:    {'n_steps': 5, 'neg_x': 4}
  Sample secondary discriminator:      {'has_diag_pos': True, 'n_steps': 7}
  structural / uniform ratio:   26.80x
  High-lift predicates total:   2203
  Archive sizes (mean):         57
  Substrate-PASSED total:       4333

TOP HIGH-LIFT PREDICATES (from seed 42)
  ep   73 (structural    ): lift=28.40, match_size=8, predicate={'n_steps': 5, 'neg_x': 4}
  ep   78 (structural    ): lift=28.40, match_size=8, predicate={'n_steps': 5, 'neg_x': 4}
  ep  149 (structural    ): lift=28.40, match_size=8, predicate={'n_steps': 5, 'neg_x': 4}
  ep  182 (structural    ): lift=28.40, match_size=8, predicate={'n_steps': 5, 'has_diag_neg': True, 'pos_x': 1}
  ep  309 (structural    ): lift=28.40, match_size=8, predicate={'n_steps': 5, 'has_diag_neg': True, 'pos_x': 1}

NOTE: HardenedObstructionEvaluator requires min_match_group_size >= 3
for substrate-PASS, preventing single-record-overlap lift inflation
from Iter 4 finding.