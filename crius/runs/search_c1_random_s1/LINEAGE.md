LINEAGE READOUT run=search_c1_random_s1 arm=random
ANCESTRY of final-population top 019618f846f38b61 (102 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0    0.112   0.0      0     50       0       0          0       0       0   11  random_init
   13    0.112   0.0      0     50       0       0          0       0       0    4  replace@0+swap@1,0
   38    0.112   0.0      0     50       0       0          0       0       0    1  replace@0
   64    1.116   1.0    100      0       0       0          0       0       0    2  swap@0,1
   74    1.116   1.0    250      0     100       0          0       0     100    7  delete@5+const@6
   82    1.118   1.0    199     49      99       0          0       0      99   11  duplicate@3+3->2+replace@7
   93    1.123   1.0     50      0      50       0          0       0      50   10  insert@3+swap@1,9+replace@0
  103    0.112   0.0      0      0       0       0          0       0       0    2  arg@0.1+delete@0+swap@1,0
  158    2.134   2.0     98      0       0       0          0       0       0    3  replace@2
  193    0.112   0.0      0      0      50       0          0       0       0    1  arg@0.0
  232    0.112   0.0      0     50       0       0          0       0       0    2  replace@1
  267    0.112   0.0     50    150       0       0          0       0       0    4  delete@1+replace@0
  277    1.123   1.0     50     50       0       0          0       0       0    3  insert@1+arg@0.0+swap@1,0
  278    2.134   2.0     50      0      50       0          0       0       0    2  delete@0+replace@0
  279    0.112   0.0      0      0      50       0          0       0       0    1  delete@1
  281    0.112   0.0      0      0      50       0          0       0       0    1  arg@0.1+arg@0.2
  286    0.112   0.0      0      0      50       0          0       0       0    1  arg@0.1
  287    0.112   0.0      0      0       0       0          0       0       0    1  replace@0
  293    0.112   0.0      0      0       0       0          0       0       0    1  arg@0.1
  gradient (mean first half -> second half of the lineage): reads 19 -> 25, writes 33 -> 12, invokes 0.0 -> 0.0, blocks 0.0 -> 0.6, wsBytes 31 -> 0, successes 1.0 -> 0.5
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      3      0      0.449      0.045    1.123
   25   24      1      0      0.112      0.151    1.123
   50   24      0      0         --      0.107    0.112
   75   24     11      0      2.592      1.278    4.156
  100   24      1      0      0.112      0.112    0.112
  125   24      1      0      0.112      0.112    0.112
  150   24      2      0      0.112      0.112    0.112
  175   24      3      0      0.112      0.112    0.112
  200   24      2      0      0.112      0.096    0.112
  225   24      3      0      0.112      0.347    1.123
  250   24      4      0      0.112      0.100    0.112
  275   24      2      2      0.112      0.518    1.118
  300   24      0      0         --      0.112    0.112
  candidates that invoked a block: 10; of those in their iteration's top 8: 2
TOP MECHANISM 019618f846f38b61: fitness 0.112 succ 0.0 inter 0 reads 0 writes 0 invokes 0 blocks 0 wsBytes 0 invalid 0
  trace: {}
      0  CONST          R0, -15
