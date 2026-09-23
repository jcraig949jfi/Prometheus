LINEAGE READOUT run=search_c2c_random_s2 arm=random
ANCESTRY of final-population top 00550ee99d42d8e0 (31 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0    0.163   0.0      0    200     100       0          0       0       0    8  random_init
    2    0.163   0.0      0    200     100       0          0       0       0    7  swap@3,2
    5    0.163   0.0      0    100     100       0          0       0       0    4  delete@4
    9    0.163   0.0      0      0       0       0          0       0       0    2  replace@1
   14    0.163   0.0      0      0       0       0          0       0       0    1  arg@0.1
   16    0.663   0.5     50      0       0       0          2       0       0    1  duplicate@0+1->1+replace@1+delete@0
   23    0.163   0.0      0      0       0       0          0       0       0    1  arg@0.1+arg@0.2+arg@0.1
   52    0.163   0.0      0      0     100       0          0       0       0    1  replace@0+arg@0.2
   55    0.163   0.0      0      0       0       0          0       0       0    1  replace@0+replace@0
   65    0.163   0.0      0      0       0       0          0       0       0    1  duplicate@0+1->1+arg@1.1+delete@0
  114    0.163   0.0      0      0       0       0          0       0       0    1  arg@0.0+replace@0
  126    0.663   0.5     50      0       0       0          2       0       0    1  const@0+arg@0.0+arg@0.0
  129    0.163   0.0      0      0       0       0          0       0       0    1  arg@0.0
  135    0.163   0.0     50      0       0       0          2       0       0    2  duplicate@0+1->0+arg@0.0+replace@0
  139    0.163   0.0      0      0       0       0          0       0       0    1  replace@0+arg@0.0
  146    0.163   0.0      0      0       0       0          0       0       0    1  arg@0.0+arg@0.2
  137    0.163   0.0      0      0       0       0          0       0       0    1  arg@1.0+delete@1
  141    0.163   0.0      0      0       0       0          0       0       0    1  arg@0.1
  152    0.163   0.0      0      0       0       0          0       0       0    1  replace@0+arg@0.1+replace@0
  gradient (mean first half -> second half of the lineage): reads 56 -> 0, writes 38 -> 0, invokes 0.0 -> 0.0, blocks 0.2 -> 0.4, wsBytes 0 -> 0, successes 0.1 -> 0.1
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      4      1      0.283      0.290    0.671
   25   24      1      0      0.163      0.207    0.671
   50   24      2      0      0.163      0.185    0.664
   75   24      2      0      0.163      0.247    1.171
  100   24      2      0      0.163      0.155    0.163
  125   24      2      0      0.163      0.209    1.179
  150   24      2      0      0.163      0.155    0.163
  175   24      1      0      0.163      0.207    0.671
  200   24      2      0      0.163      0.163    0.163
  225   24      1      0      0.163      0.163    0.163
  250   24      1      0      0.163      0.163    0.163
  275   24      3      0      0.163      0.163    0.163
  300   24      1      0      0.163      0.163    0.163
  candidates that invoked a block: 8; of those in their iteration's top 8: 1
TOP MECHANISM 00550ee99d42d8e0: fitness 0.163 succ 0.0 inter 0 reads 0 writes 0 invokes 0 blocks 0 wsBytes 0 invalid 0
  trace: {}
      0  MUL            R6, R6, R5
