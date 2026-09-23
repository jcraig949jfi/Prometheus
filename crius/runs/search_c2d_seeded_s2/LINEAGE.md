LINEAGE READOUT run=search_c2d_seeded_s2 arm=seeded
ANCESTRY of final-population top ccccac14c9e9c953 (124 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   19.378  19.0  14273      0       0       0          2       0       0   39  seed:ENUMERATE_VM
   27   25.901  25.5  11714      0       0       0          2       0       0   35  delete@20
   52   21.436  21.0   7578      0     100       0          4       0       0   36  const@18+delete@7+duplicate@32+1->1
   71   21.435  21.0   7634      0       0       0          4       0       0   49  replace@47
   90   21.921  21.5   9382      0       0       0          4       0       0   43  delete@17
  107   22.931  22.5   8145      0       0       0          4       0       0   47  swap@37,41
  127   23.458  23.0   4992      0       0       0          2       0       0   52  delete@49+arg@36.0
  152   20.427  20.0   8626      0       0       0          2       0       0   44  delete@9
  183   23.907  23.5  11038      0       0       0          2       0       0   40  replace@4
  204   21.397  21.0  12124      0       0       0          2       0       0   36  const@33
  236   20.945  20.5   6467      0       0       0          2       0       0   28  delete@5
  258   25.427  25.0   8584      0       0       0          2       0       0   24  duplicate@23+1->5+delete@23
  282   22.976  22.5   2826      0       0       0          2       0       0   25  const@11
  280   21.435  21.0   7658      0       0       0          2       0       0   25  insert@10+const@9
  285   20.925  20.5   8881      0       0       0          2       0       0   24  delete@8
  287   23.956  23.5   5167      0       0       0          2       0       0   24  replace@6
  290   20.931  20.5   8176      0       0       0          2       0       0   22  delete@9+delete@8+arg@21.2
  300   20.962  20.5   4492      0       0       0          2       0       0   23  arg@9.0+insert@13
  gradient (mean first half -> second half of the lineage): reads 8 -> 0, writes 23 -> 0, invokes 0.0 -> 0.0, blocks 3.3 -> 2.0, wsBytes 0 -> 0, successes 21.4 -> 22.0
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      0      0         --      9.957   19.378
   25   24      1      0      0.656     17.121   23.470
   50   24      0      0         --     14.024   23.452
   75   24      0      0         --     17.620   22.446
  100   24      1      0      1.163     16.979   23.428
  125   24      4      0      4.090     15.917   19.922
  150   24      3      0      4.365     15.546   23.915
  175   24      1      1      0.510     14.366   22.945
  200   24      1      0      6.715      9.193   22.419
  225   24      0      0         --     15.305   25.957
  250   24      1      0      2.184     10.677   21.431
  275   24      1      0      6.733     10.790   21.455
  300   24      4      0      5.273     10.066   21.933
  candidates that invoked a block: 33; of those in their iteration's top 8: 6
TOP MECHANISM ccccac14c9e9c953: fitness 20.962 succ 20.5 inter 4492 reads 0 writes 0 invokes 0 blocks 2 wsBytes 0 invalid 0
  trace: {"ACT": 14820, "INPUT": 100}
      0  CONST          R0, 18
      1  CONST          R5, -7
      2  MOD            R3, R0, R1
      3  INPUT          R1, num_ops
      4  ACT            R1
      5  BRZ            R3, 8
      6  PSIM           R3, R0, R4
      7  WS_ALLOC       R2, R7
      8  CONST          R0, 18
      9  ACT            R1
     10  MOD            R3, R0, R1
     11  ACT            R3
     12  DIV            R4, R0, R1
     13  SUB            R4, R6, R4
     14  MOD            R3, R4, R1
     15  ACT            R3
     16  DIV            R4, R4, R1
     17  MOD            R3, R4, R1
     18  ACT            R3
     19  ADD            R0, R0, R5
     20  JMP            9
     21  WS_LINK_GET    R0, R6, R6
     22  ADD            R7, R6, R3
