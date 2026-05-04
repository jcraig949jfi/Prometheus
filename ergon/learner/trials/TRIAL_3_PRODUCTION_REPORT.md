========================================================================
Trial 3 Production Pilot — 1000 episodes x 3 seeds
========================================================================

ACCEPTANCE
  [Completed without error]:                       PASS
  [Found OBSTRUCTION or SECONDARY (exact match)]: PASS
  [Found OBSTRUCTION or SECONDARY (discriminator)]: PASS
  [High-lift predicates >= 5]:                     PASS

PER-SEED RESULTS
    seed  archive  struct   symb   unif  a-pri  pass  high-lift  1st-obs  1st-sec
      42       46      39      3      1      2   285        166     None      617
     100       39      27      3      2      6   260         88     None      504
    1234       42      31      8      1      2   268         65     None     None

AGGREGATE STATS
  Seeds hitting OBSTRUCTION (exact):         0 of 3
  Seeds hitting OBSTRUCTION (discriminator): 2 of 3
  Seeds hitting SECONDARY (exact):           2 of 3
  Seeds hitting SECONDARY (discriminator):   2 of 3
  First-obstruction-exact episodes:    [None, None, None]
  First-secondary-exact episodes:      [617, 504, None]
  First-obstruction-disc episodes:    [73, 784, None]
  First-secondary-disc episodes:      [617, 504, None]
  Sample obstruction discriminator:    {'n_steps': 5, 'neg_x': 4}
  Sample secondary discriminator:      {'has_diag_pos': True, 'n_steps': 7}
  structural / uniform ratio:   24.25x
  High-lift predicates total:   319
  Archive sizes (mean):         42
  Substrate-PASSED total:       813

TOP HIGH-LIFT PREDICATES (from seed 42)
  ep   73 (structural    ): lift=28.40, match_size=8, predicate={'n_steps': 5, 'neg_x': 4}
  ep   78 (structural    ): lift=28.40, match_size=8, predicate={'n_steps': 5, 'neg_x': 4}
  ep  149 (structural    ): lift=28.40, match_size=8, predicate={'n_steps': 5, 'neg_x': 4}
  ep  182 (structural    ): lift=28.40, match_size=8, predicate={'n_steps': 5, 'has_diag_neg': True, 'pos_x': 1}
  ep  309 (structural    ): lift=28.40, match_size=8, predicate={'n_steps': 5, 'has_diag_neg': True, 'pos_x': 1}

NOTE: HardenedObstructionEvaluator requires min_match_group_size >= 3
for substrate-PASS, preventing single-record-overlap lift inflation
from Iter 4 finding.