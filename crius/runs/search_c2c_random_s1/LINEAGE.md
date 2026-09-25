LINEAGE READOUT run=search_c2c_random_s1 arm=random
ANCESTRY of final-population top 003a42a1b2c01e67 (59 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0    0.163   0.0     50    200     300     100          6       2       4   19  random_init
    6    0.163   0.0     50    200     200       0          4       0       0   18  delete@4+replace@6
   11    0.163   0.0     50    100     200       0          2       0       0   16  replace@1+arg@12.1
   17    0.163   0.0     50    100     100       0          2       0       0   11  delete@9+arg@2.0
   23    0.163   0.0     50      0       0       0          2       0       0    9  replace@5+const@4
   30    1.179   1.0     50      0       0       0          2       0       0    5  replace@4
   43    1.179   1.0     50      0       0       0          2       0       0    1  arg@0.0
  137    1.687   1.5     50      0       0       0          2       0       0    1  replace@0+arg@0.0
  148    0.163   0.0     50      0       0       0          2       0       0    2  replace@1
  189    0.163   0.0      0      0       0       0          0       0       0    1  arg@0.1
  207    0.163   0.0      0      0       0       0          0       0       0    2  delete@0+arg@0.0+delete@0
  213    0.163   0.0      0      0       0       0          0       0       0    1  arg@0.1
  211    0.163   0.0      0      0       0       0          0       0       0    1  arg@0.0+arg@0.1
  214    0.163   0.0      0      0       0       0          0       0       0    1  replace@0+insert@0+delete@1
  215    0.163   0.0      0      0       0       0          0       0       0    1  arg@0.1+arg@0.2+arg@0.1
  221    0.163   0.0      0      0       0       0          0       0       0    1  replace@0
  242    0.163   0.0      0      0       0       0          0       0       0    1  arg@0.1
  gradient (mean first half -> second half of the lineage): reads 83 -> 0, writes 127 -> 0, invokes 6.7 -> 0.0, blocks 2.7 -> 0.7, wsBytes 0 -> 0, successes 0.5 -> 0.3
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      4      1      0.163      0.163    0.163
   25   24      2      0      0.417      0.578    0.671
   50   24      3      0      0.163      0.139    0.163
   75   24      3      0      0.163      0.163    0.163
  100   24      1      0      0.163      0.184    0.663
  125   24      1      0      0.163      0.163    0.163
  150   24      0      0         --      0.289    1.171
  175   24      1      0      0.163      0.251    2.187
  200   24      3      0      0.163      0.147    0.163
  225   24      2      0      0.163      0.208    0.663
  250   24      1      0      0.163      0.156    0.163
  275   24      5      0      0.163      0.154    0.163
  300   24      1      0      0.163      0.163    0.163
  candidates that invoked a block: 52; of those in their iteration's top 8: 18
TOP MECHANISM 003a42a1b2c01e67: fitness 0.163 succ 0.0 inter 0 reads 0 writes 0 invokes 0 blocks 0 wsBytes 0 invalid 0
  trace: {}
      0  CONST          R0, -12
