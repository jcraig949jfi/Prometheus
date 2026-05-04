========================================================================
Trial 3 Iter-18 Canonical Production Pipeline
========================================================================
  evaluator: ObstructionBindEvalEvaluator (BindEvalKernelV2)
  exploration_rate: 0.15
  episodes: 5000 x 3 seeds = 15,000 total kernel EVALs

ACCEPTANCE
  [Completed without error]:           PASS
  [Ledger >= 1500 records]:            PASS (4149)
  [3/3 seeds OBS exact OR 3/3 SEC]:    PASS (obs_exact=2/3, sec_exact=3/3)
  [Run < 60 seconds total]:            PASS (19.2s)

DISCOVERY ACROSS SEEDS
  OBSTRUCTION exact:         2/3 seeds
  OBSTRUCTION discriminator: 3/3 seeds
  SECONDARY exact:           3/3 seeds
  SECONDARY discriminator:   3/3 seeds
  First-OBS-exact eps:       [None, 2118, 1099]
  First-SEC-exact eps:       [1687, 241, 299]

LEDGER CLASSIFICATION
                         obstruction_exact:    57
                           secondary_exact:    49
            obstruction_discriminator_only:   149
              secondary_discriminator_only:     1
                non_planted_substrate_pass:  3893

  Total substrate-PASS records: 4149
  Unique predicates: 1583
  Kernel error rate: 0/15000

PER-SEED
    seed  archive   pass  obs_ex  obs_dc  sec_ex  sec_dc  time(s)
      42       51   1391       0      26       7       7     6.4
     100       54   1356      18      95      17      18     6.3
    1234       58   1402      39      85      25      25     6.5