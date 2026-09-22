LINEAGE READOUT run=search_c1b_random_s1 arm=random
ANCESTRY of final-population top 0002e3d11ea9e426 (28 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0    0.163   0.0      0     50       0       0          0       0       0   11  random_init
    3    0.163   0.0      0     50       0       0          0       0       0   10  swap@8,7
    5    0.163   0.0      0      0       0       0          0       0       0   11  arg@2.2
    7    0.163   0.0      0      0       0       0          0       0       0    9  delete@5+swap@8,7+arg@8.1
   11    0.163   0.0      0      0       0       0          0       0       0    7  delete@4
   16    0.163   0.0      0      0       0       0          0       0       0    4  delete@4+arg@1.0
   20    0.163   0.0      0      0       0       0          0       0       0    1  swap@0,2+delete@1+delete@1
   23    0.163   0.0      0      0       0       0          0       0       0    1  replace@0+delete@1+replace@0
   27    0.163   0.0      0      0       0       0          0       0       0    1  replace@0
   29    0.163   0.0      0      0       0       0          0       0       0    1  arg@0.0+replace@0
   59    1.163   1.0     50      0       0       0          0       0       0    2  replace@0+const@0+insert@0
   62    1.163   1.0     99      0       0       0          0       0       0    2  duplicate@1+1->0+arg@1.0+delete@1
   64    0.163   0.0      0      0       0       0          0       0       0    1  arg@0.0
   74    0.163   0.0      0      0       0       0          0       0       0    1  const@0
  125    0.163   0.0      0      0       0       0          0       0       0    1  replace@0
   63    0.163   0.0     50      0       0       0          0       0       0    1  delete@1+arg@0.0
   65    0.163   0.0      0      0       0       0          0       0       0    1  const@0
  120    0.163   0.0      0      0       0       0          0       0       0    1  arg@0.0
  gradient (mean first half -> second half of the lineage): reads 11 -> 0, writes 0 -> 0, invokes 0.0 -> 0.0, blocks 0.0 -> 0.0, wsBytes 0 -> 0, successes 0.0 -> 0.2
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      3      0      0.501      0.065    1.179
   25   24      0      0         --      0.163    0.163
   50   24      1      0      0.163      0.163    0.163
   75   24      0      0         --      0.163    0.163
  100   24      0      0         --      0.163    0.163
  125   24      2      0      0.163      0.163    0.163
  150   24      1      0      0.163      0.148    0.163
  175   24      3      0      0.163      0.163    0.163
  200   24      1      0      0.163      0.156    0.163
  225   24      1      0      0.163      0.200    1.179
  250   24      1      0      0.163      0.163    0.163
  275   24      1      0      0.163      0.163    0.163
  300   24      1      0      0.163      0.163    0.163
  candidates that invoked a block: 2; of those in their iteration's top 8: 0
TOP MECHANISM 0002e3d11ea9e426: fitness 0.163 succ 0.0 inter 0 reads 0 writes 0 invokes 0 blocks 0 wsBytes 0 invalid 0
  trace: {}
      0  DIV            R1, R5, R3
