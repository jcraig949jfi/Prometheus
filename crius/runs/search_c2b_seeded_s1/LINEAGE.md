LINEAGE READOUT run=search_c2b_seeded_s1 arm=seeded
ANCESTRY of final-population top 84557bca5cfc8dc5 (147 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   17.839  17.5  18871      0       0       0          2       0       0   39  seed:ENUMERATE_VM
   21   20.930  20.5   8205      0       0       0          2       0       0   41  delete@41
   42   21.896  21.5  12326      0       0       0          2       0       0   43  swap@12,28
   76   22.914  22.5  10145      0       0       0          2       0       0   34  replace@18+arg@17.2
  105   18.899  18.5  11992      0       0       0          2       0       0   53  duplicate@1+2->50
  123   18.867  18.5  15760      0       0       0          2       0       0   55  const@12+swap@52,31
  146   20.415  20.0   9996      0       0       0          2       0       0   48  const@5
  165   18.878  18.5  14408      0       0       0          2       0       0   43  const@10+insert@22+delete@19
  195   22.465  22.0   4096    100     100       0          2       0     100   51  delete@22+insert@3+replace@16
  215   20.870  20.5  15406      0     200       0          2       0       2   52  delete@14+replace@50
  240   27.451  27.0   5701      0     100       0          2       0       2   48  swap@46,1
  262   19.427  19.0   8618      0       0       0          2       0       0   42  arg@7.2+swap@19,24+arg@39.0
  293   18.895  18.5  12392      0       0       0          2       0       0   39  replace@12
  284   13.816  13.5  21823      0       0       0          2       0       0   41  delete@23
  286   20.929  20.5   8423      0       0       0          2       0       0   39  const@24+delete@37+delete@39
  295   26.961  26.5   4626      0       0       0          2       0       0   38  delete@20+swap@11,22+arg@7.0
  296   24.943  24.5   6667      0       0       0          2       0       0   38  arg@21.1
  298   21.901  21.5  11713      0       0       0          2       0       0   38  const@3
  gradient (mean first half -> second half of the lineage): reads 0 -> 16, writes 0 -> 58, invokes 0.0 -> 0.0, blocks 2.0 -> 7.9, wsBytes 0 -> 17, successes 21.4 -> 21.2
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      1      0     17.839     10.092   17.839
   25   24      0      0         --     10.808   19.907
   50   24      0      0         --     11.000   21.423
   75   24      1      0      7.225     12.778   22.452
  100   24      3      0      8.242     14.164   22.932
  125   24      0      0         --     18.432   22.921
  150   24      2      0     11.549     16.706   23.431
  175   24     13      0     13.618     16.717   20.922
  200   24     18      0     14.880     10.068   19.379
  225   24     24      0     10.391         --   23.427
  250   24      2      0      5.201      9.971   22.929
  275   24      2      0      0.162     11.433   19.920
  300   24      3      0     15.666     15.098   24.411
  candidates that invoked a block: 48; of those in their iteration's top 8: 13
TOP MECHANISM 84557bca5cfc8dc5: fitness 21.901 succ 21.5 inter 11713 reads 0 writes 0 invokes 0 blocks 2 wsBytes 0 invalid 0
  trace: {"ACT": 34366, "INPUT": 100}
      0  SUB            R3, R5, R7
      1  DIV            R4, R0, R1
      2  INPUT          R1, num_ops
      3  CONST          R5, -1
      4  VGET           R0, R1, R6
      5  BRZ            R3, 13
      6  BLK_PATCH      R7, R4, R0
      7  MOD            R5, R5, R6
      8  MOD            R3, R0, R1
      9  WS_ALLOC       R3, R2
     10  MUL            R2, R1, R4
     11  ACT            R4
     12  MOV            R3, R0
     13  BRZ            R3, 23
     14  NOT            R7, R7
     15  DIV            R3, R7, R4
     16  PREC_END       R5
     17  ACT            R3
     18  ADD            R0, R7, R5
     19  PREC_END       R4
     20  MOD            R3, R0, R1
     21  WS_WRITE       R2, R4
     22  VSET           R6, R4, R0
     23  CONST          R0, 40
     24  ADD            R0, R0, R5
     25  ACT            R1
     26  MOD            R3, R0, R1
     27  ACT            R3
     28  DIV            R4, R0, R1
     29  MOD            R3, R4, R1
     30  ACT            R3
     31  DIV            R4, R4, R1
     32  MOD            R3, R4, R1
     33  ACT            R3
     34  ADD            R0, R0, R5
     35  JMP            25
     36  BLK_DELETE     R4
     37  WS_WRITE       R6, R1
