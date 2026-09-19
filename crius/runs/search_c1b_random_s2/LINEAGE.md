LINEAGE READOUT run=search_c1b_random_s2 arm=random
ANCESTRY of final-population top 108ed018eab82162 (52 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0    0.163   0.0      0      0      50       0          0       0      49    8  random_init
    4    0.163   0.0      0      0       0       0          0       0       0   12  const@3+swap@1,0
    9    0.163   0.0      0      0       0       0          0       0       0    9  arg@9.1+delete@6
   17    0.163   0.0      0      0       0       0          0       0       0    4  arg@1.1+replace@3+delete@2
   23    0.163   0.0      0      0       0       0          0       0       0    2  insert@2+delete@2+arg@1.0
   36    0.163   0.0      0      0       0       0          0       0       0    1  const@0+const@0
  101    6.244   6.0     94      0       0       0          0       0       0    2  delete@2
  106    2.195   2.0     98     48      48       0          0       0       0    4  const@1
  112    1.179   1.0     99     50       0       0          0       0       0    4  replace@1+arg@2.0
  116    1.179   1.0     50     50      50       0          0       0       0    3  replace@0+const@2
  121    0.163   0.0      0      0       0       0          0       0       0    1  replace@0+arg@0.0
  179    0.163   0.0      0      0       0       0          0       0       0    1  arg@0.2+delete@1
  240    0.163   0.0      0      0       0       0          0       0       0    1  arg@0.1+arg@0.2
  300    2.179   2.0     50      0       0       0          0       0       0    2  replace@0+insert@0
  199    0.163   0.0      0      0       0       0          0       0       0    1  replace@0
  264    0.163   0.0      0      0       0       0          0       0       0    1  replace@0+replace@0
  275    0.163   0.0      0      0       0       0          0       0       0    1  arg@0.1+arg@0.0
  276    0.163   0.0      0      0       0       0          0       0       0    1  arg@0.2
  gradient (mean first half -> second half of the lineage): reads 0 -> 20, writes 4 -> 13, invokes 0.0 -> 0.0, blocks 0.0 -> 0.0, wsBytes 2 -> 0, successes 0.5 -> 1.2
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      6      2      0.162      0.162    0.163
   25   24      1      0      0.163      0.163    0.163
   50   24      6      0      0.163      0.163    0.163
   75   24      2      0      0.163      0.194    1.179
  100   24      1      0      0.163      0.552    2.195
  125   24      1      0      0.163      0.163    0.163
  150   24      2      0      0.163      0.201    1.163
  175   24      3      0      0.840      1.324    2.195
  200   24      3      0      0.163      0.163    0.163
  225   24      1      0      0.163      0.156    0.163
  250   24      1      0      0.163      0.163    0.163
  275   24      4      0      0.163      0.146    0.163
  300   24      2      0      0.163      0.247    2.179
  candidates that invoked a block: 7; of those in their iteration's top 8: 2
TOP MECHANISM 108ed018eab82162: fitness 2.179 succ 2.0 inter 50 reads 0 writes 0 invokes 0 blocks 0 wsBytes 0 invalid 0
  trace: {"ACT": 50}
      0  BRNZ           R3, 0
      1  ACT            R4
