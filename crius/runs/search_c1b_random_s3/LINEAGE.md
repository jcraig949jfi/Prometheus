LINEAGE READOUT run=search_c1b_random_s3 arm=random
ANCESTRY of final-population top 06c9b6f2eb5a9055 (63 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0    1.163   1.0     50    350      50      50          0       0      50   13  random_init
    5    0.163   0.0    100    200      50      50          0       0      50    9  replace@0
   10    0.163   0.0     50    100       0       0          0       0       0    4  delete@2
   80    0.163   0.0      0      0       0       0          0       0       0    1  replace@0
  100    1.179   1.0     50      0       0       0          0       0       0    1  replace@0+arg@0.0
  108    0.163   0.0      0      0       0       0          0       0       0    4  swap@0,1+insert@0
  116    0.163   0.0     50      0       0       0          0       0       0    1  delete@1
  142    4.078   4.0     50      0       0       0          0       0       0    3  replace@0+insert@1+duplicate@1+1->0
  155    0.163   0.0      0      0       0       0          0       0       0    1  arg@0.0+arg@0.1
  248    2.195   2.0     50      0       0       0          0       0       0    3  duplicate@0+1->1+insert@0
  255    1.163   1.0     50     50       0       0          0       0       0    2  arg@0.0
  260    3.211   3.0    100      0       0       0          0       0       0    3  arg@1.0+duplicate@1+1->0
  276    0.163   0.0      0      0       0       0          0       0       0    1  arg@0.0
  268    0.163   0.0      0      0       0       0          0       0       0    1  replace@1+arg@0.0+delete@0
  269    0.163   0.0      0      0       0       0          0       0       0    1  arg@0.0
  282    0.163   0.0      0      0       0       0          0       0       0    1  replace@0
  285    0.163   0.0      0      0       0       0          0       0       0    1  arg@0.0
  299    0.163   0.0      0      0       0       0          0       0       0    1  replace@0+replace@0
  gradient (mean first half -> second half of the lineage): reads 80 -> 6, writes 11 -> 0, invokes 12.5 -> 0.0, blocks 0.0 -> 0.0, wsBytes 11 -> 0, successes 0.6 -> 0.5
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      5      0      0.530      0.163    1.163
   25   24      0      0         --      0.141    0.163
   50   24      1      0      0.163      0.251    1.179
   75   24      3      0      0.163      0.147    0.163
  100   24      1      0      0.163      0.200    1.179
  125   24      4      0      0.163      0.264    2.195
  150   24      2      0      0.163      0.140    0.163
  175   24      1      0      0.163      0.148    0.163
  200   24      2      0      0.163      0.163    0.163
  225   24      2      0      0.163      0.155    0.163
  250   24      4      0      0.925      1.026    1.179
  275   24      1      0      0.163      0.163    0.163
  300   24      0      0         --      0.163    0.163
  candidates that invoked a block: 3; of those in their iteration's top 8: 0
TOP MECHANISM 06c9b6f2eb5a9055: fitness 0.163 succ 0.0 inter 0 reads 0 writes 0 invokes 0 blocks 0 wsBytes 0 invalid 0
  trace: {}
      0  MOD            R1, R6, R0
