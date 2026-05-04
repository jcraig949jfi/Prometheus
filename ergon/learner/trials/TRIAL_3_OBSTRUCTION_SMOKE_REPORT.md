========================================================================
Trial 3 ObstructionEnv Smoke Test (200 episodes)
========================================================================

ACCEPTANCE
  [Completed without error]:           PASS
  [Found OBSTRUCTION_SIGNATURE]:       FAIL
  [structural > uniform fills]:        PASS

OBSTRUCTION_SIGNATURE target: {'n_steps': 5, 'neg_x': 4, 'pos_x': 1, 'has_diag_neg': True}
  Found at episodes: []
  (0 hits in 200 episodes)

SECONDARY_SIGNATURE hits: 0
HIGH-LIFT EPISODES (lift >= 5.0): 9
  Top 5 by lift:
    ep 120 (structural  ): lift=12.42 predicate={'neg_z': 3, 'pos_x': 4, 'neg_y': 1}
    ep 122 (symbolic    ): lift=12.42 predicate={'neg_z': 3, 'pos_x': 4, 'neg_y': 1}
    ep 164 (symbolic    ): lift=12.42 predicate={'neg_z': 3, 'pos_x': 4, 'neg_y': 1}
    ep 176 (structural  ): lift=12.42 predicate={'neg_z': 3, 'pos_x': 4, 'neg_y': 1}
    ep  89 (structural  ): lift=7.29 predicate={'n_steps': 5}

Archive cells filled: 25
Substrate-PASSED:     38 (lift >= 1.5 with match-group >= 2)
structural / uniform: 3.00x
Elapsed:              0.01s (15383 eps/sec)

FILL COUNTS BY OPERATOR
  structural        :   18
  symbolic          :    1
  uniform           :    6