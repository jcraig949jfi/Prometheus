LINEAGE READOUT run=search_c1_random_s3 arm=random
ANCESTRY of final-population top 0075e6ffbef86f40 (54 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0    0.112   0.0      0      0      50       0         32       0       0    8  random_init
    5    0.112   0.0     50     50       0       0          0       0       0    5  delete@3+delete@0+duplicate@3+1->1
   10    1.116   1.0     50     50       0       0          0       0       0    3  const@1+delete@2
   16    0.112   0.0     50      0       0       0          0       0       0    2  swap@0,2+delete@2
   22    0.112   0.0      0      0       0       0          0       0       0    1  arg@0.0
   29    1.116   1.0     50      0     100       0          0       0       0    4  insert@1+delete@1+replace@0
   35    0.112   0.0      0      0       0       0          0       0       0    1  replace@0+arg@0.0+arg@0.0
   72    3.145   3.0     50     50       0       0          0       0       0    2  arg@0.0
   76    0.112   0.0      0      0       0       0          0       0       0    1  arg@0.0
   82    0.112   0.0      0      0       0       0          0       0       0    1  delete@1+replace@0+arg@0.0
  176    1.116   1.0     50      0       0       0          0       0       0    2  insert@1+duplicate@1+1->0+delete@0
  206    0.112   0.0      0      0      50       0          0       0       0    1  insert@0+delete@1
  237    1.116   1.0     50      0       0       0          0       0       0    2  delete@0+insert@0+swap@1,0
  246    0.112   0.0      0      0       0       0          0       0       0    1  arg@0.0
  241    0.112   0.0      0      0       0       0          0       0       0    1  arg@1.1+delete@0
  242    0.112   0.0      0      0       0       0          0       0       0    1  arg@0.0
  243    0.112   0.0      0      0       0       0          0       0       0    1  arg@0.1+arg@0.0+arg@0.1
  250    0.112   0.0      0      0       0       0          0       0       0    1  arg@0.0+duplicate@0+1->1+delete@1
  259    0.112   0.0      0     50       0       0          0       0       0    1  arg@0.0+replace@0
  gradient (mean first half -> second half of the lineage): reads 20 -> 9, writes 19 -> 7, invokes 0.0 -> 0.0, blocks 1.2 -> 0.0, wsBytes 0 -> 0, successes 0.6 -> 0.5
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      5      0      0.491      0.112    1.116
   25   24      1      0      0.112      0.195    2.134
   50   24      4      0      0.112      0.162    1.123
   75   24      0      0         --      0.107    0.112
  100   24      3      0      0.112      0.106    0.112
  125   24      1      0      0.112      0.112    0.112
  150   24      4      0      0.112      0.162    1.123
  175   24      4      0      0.112      0.162    1.123
  200   24      0      0         --      0.107    0.112
  225   24      2      0      0.112      0.101    0.112
  250   24      1      0      0.112      0.102    0.112
  275   24      4      0      0.112      0.112    0.112
  300   24      1      0      0.112      0.112    0.112
  candidates that invoked a block: 3; of those in their iteration's top 8: 0
TOP MECHANISM 0075e6ffbef86f40: fitness 0.112 succ 0.0 inter 0 reads 50 writes 0 invokes 0 blocks 0 wsBytes 0 invalid 0
  trace: {"WS_SREAD": 50}
      0  WS_SREAD       R2, R1, R4
