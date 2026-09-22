LINEAGE READOUT run=search_c2a_seeded_s2 arm=seeded
ANCESTRY of final-population top ce61878157317f70 (126 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   19.378  19.0  14273      0       0       0          0       0       0   39  seed:ENUMERATE_VM
   24   20.953  20.5   5493    100     100       0          0       0     100   44  arg@14.0
   42   25.452  25.0   5570    100     200       0          0       0       0   47  replace@27
   60   23.472  23.0   3308    100     200       0          0       0       0   49  arg@16.0+delete@31
   84   21.926  21.5   8749      0     100       0          0       0       0   56  duplicate@30+4->26+swap@32,37+delete@34
  113   20.953  20.5   5550      0       0       0          0       0       0   58  replace@33
  133   22.945  22.5   6412    100       0       0          0       0       0   60  insert@0+arg@58.0
  163   22.936  22.5   7530    100       0     100          0       0       0   55  arg@22.0+const@6
  191   22.449  22.0   5997    100       0     100          0       0       0   50  delete@18+replace@16+delete@2
  204   21.926  21.5   8765    100       0       0          0       0       0   46  delete@6
  221   27.441  27.0   6900    100       0       0          0       0       0   37  delete@23
  242   22.947  22.5   6290    100       0       0          0       0       0   31  arg@15.2+arg@23.0
  282   22.472  22.0   3312      0       0       0          0       0       0   25  replace@7
  283   19.371  19.0  15317      0       0       0          0       0       0   24  delete@5+replace@10
  284   22.428  22.0   8523      0       0       0          0       0       0   24  swap@1,7
  289   20.427  20.0   8675      0       0       0          0       0       0   24  replace@6
  290   21.418  21.0   9681      0       0       0          0       0       0   23  delete@1
  292   23.936  23.5   7520      0       0       0          0       0       0   22  delete@10
  299   19.937  19.5   7484      0       0       0          0       0       0   20  delete@4+delete@9
  gradient (mean first half -> second half of the lineage): reads 68 -> 91, writes 162 -> 0, invokes 0.0 -> 35.9, blocks 0.0 -> 0.0, wsBytes 57 -> 0, successes 21.5 -> 22.0
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      0      0         --      9.957   19.378
   25   24     18      0     14.387     17.810   23.971
   50   24      3      0      8.263     17.279   22.951
   75   24      2      0     20.901     15.088   22.944
  100   24      0      0         --     19.443   23.429
  125   24      0      0         --     18.191   24.957
  150   24      1      0     22.930     12.428   22.930
  175   24      0      0         --     15.756   23.435
  200   24      0      0         --     16.264   21.415
  225   24      1      0      1.605     14.896   25.441
  250   24      2      0     11.042     13.445   21.451
  275   24      4      1      8.259      8.977   19.431
  300   24      0      0         --     13.201   21.950
  candidates that invoked a block: 8; of those in their iteration's top 8: 1
TOP MECHANISM ce61878157317f70: fitness 19.937 succ 19.5 inter 7484 reads 0 writes 0 invokes 0 blocks 0 wsBytes 0 invalid 0
  trace: {"ACT": 22706, "INPUT": 100}
      0  INPUT          R1, num_ops
      1  CONST          R5, 19
      2  JMP            9
      3  WS_LINKS       R7, R7
      4  WS_SREAD       R7, R3, R4
      5  MOD            R3, R5, R6
      6  JMP            12
      7  BLK_DELETE     R4
      8  ACT            R0
      9  ADD            R0, R0, R5
     10  MOD            R3, R0, R1
     11  ACT            R3
     12  DIV            R4, R0, R1
     13  MOD            R3, R4, R1
     14  ACT            R3
     15  DIV            R4, R4, R1
     16  MOD            R3, R4, R1
     17  ACT            R3
     18  ACT            R1
     19  JMP            9
