LINEAGE READOUT run=search_c1b_recombination_s2 arm=recombination
ANCESTRY of final-population top f31ebd4d500ce6d6 (189 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   18.413  18.0  10217      0       0       0          0       0       0   39  seed:ENUMERATE_VM
   32   20.430  20.0   8202      0       0       0          0       0       0   57  const@35+replace@14+delete@21
   55   15.249  15.0  29228      0       0       0          0       0       0   64  insert@43
   77   21.423  21.0   9043      0       0       0          0       0       0   63  duplicate@33+2->20
   99   23.461  23.0   4574     50       0       0          0       0       0   62  swap@28,6
  121   25.437  25.0   7457     50       0       0          0       0       0   61  swap@18,37+arg@49.0+const@5
  139   21.377  21.0  14500    100       0       0          0       0       0   63  delete@15+const@0
  160   29.467  29.0   3897     50       0       0          0       0       0   61  const@0+delete@37
  186   19.403  19.0  11454      0       0       0          0       0       0   59  delete@11+delete@14
  214   18.388  18.0  13189      0       0       0          0       0       0   61  delete@30+delete@16+arg@23.0
  239   16.344  16.0  18374      0      50       0          0       0       0   64  replace@6+splice:none:954e50cfa85e8e2a
  265   18.369  18.0  15397      0     200       0          0       0      51   64  replace@4+splice@35<-donor[18:19]:80571c
  283   20.398  20.0  12014      0     150       0          0       0       1   63  const@1+replace@6
  293   23.469  23.0   3685     50     150       0          0       0       0   62  replace@0
  294   20.474  20.0   3024     50     150       0          0       0       0   62  const@4+arg@1.1
  296   28.474  28.0   3011    100     150       0          0       0       0   62  arg@37.0+delete@61+insert@1
  297   18.426  18.0   8654    100     150       0          0       0       0   61  delete@4
  298   21.448  21.0   6133    100     150       0          0       0       0   61  arg@41.0+const@60
  300   25.442  25.0   6866    100     150       0          0       0       0   60  const@4+swap@43,24+delete@2
  gradient (mean first half -> second half of the lineage): reads 32 -> 16, writes 1 -> 60, invokes 0.0 -> 0.0, blocks 0.0 -> 0.0, wsBytes 0 -> 8, successes 20.6 -> 21.5
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      0      0         --     11.040   18.413
   25   24      5      0     10.491      7.358   15.367
   50   24      2      0      1.156     14.022   17.344
   75   24      0      0         --     14.101   21.401
  100   24      0      0         --     14.185   22.446
  125   24      0      0         --     14.327   22.416
  150   24      0      0         --     15.739   24.406
  175   24      0      0         --     17.896   25.456
  200   24      0      0         --     20.171   23.408
  225   24      1      0     25.482     24.097   28.484
  250   24     24      0     16.742         --   25.457
  275   24     24      0     16.552         --   23.439
  300   24      1      0      0.000     16.077   25.442
  candidates that invoked a block: 0; of those in their iteration's top 8: 0
TOP MECHANISM f31ebd4d500ce6d6: fitness 25.442 succ 25.0 inter 6866 reads 100 writes 150 invokes 0 blocks 0 wsBytes 0 invalid 100
  trace: {"ACT": 9287, "INPUT": 2321, "BLK_COPY": 50, "BLK_STATE_SET": 50, "WS_FREE": 50, "WS_LINKS": 50, "WS_REC_SET": 50, "WS_SLEN": 50}
      0  WS_LINKS       R5, R4
      1  WS_SLEN        R3, R7
      2  WS_REC_SET     R3, R7, R0
      3  CONST          R1, -13
      4  MOD            R3, R4, R1
      5  BLK_STATE_SET  R7, R5, R4
      6  MOD            R7, R7, R0
      7  WS_FREE        R3
      8  BLK_COPY       R1, R3
      9  SUB            R4, R7, R7
     10  JMP            47
     11  BRNZ           R3, 32
     12  ADD            R7, R3, R1
     13  ACT            R0
     14  WS_READ        R1, R2
     15  ACT            R2
     16  BLK_COUNT      R3
     17  JMP            35
     18  DIV            R7, R4, R1
     19  INPUT          R1, current_block
     20  ADD            R1, R4, R7
     21  BRZ            R7, 3
     22  DIV            R4, R4, R1
     23  HALT           
     24  DIV            R2, R3, R7
     25  BRZ            R3, 35
     26  BLK_DELETE     R1
     27  DIV            R6, R3, R7
     28  JMP            42
     29  ACT            R2
     30  BLK_STATE_SET  R0, R0, R1
     31  CONST          R2, 11
     32  WS_SLEN        R5, R4
     33  HALT           
     34  ACT            R1
     35  BLK_APPEND     R5, R2
     36  BRZ            R7, 3
     37  WS_LINK        R0, R5, R1
     38  WS_WRITE       R1, R0
     39  WS_FREE        R3
     40  BLK_COPY       R3, R3
     41  BLK_STATE_SET  R2, R4, R3
     42  DIV            R4, R4, R1
     43  ACT            R3
     44  WS_APPEND      R3, R7
     45  DIV            R4, R0, R1
     46  ACT            R1
     47  MOD            R3, R0, R1
     48  ACT            R3
     49  VLEN           R5, R6
     50  MOD            R3, R4, R1
     51  INPUT          R1, num_ops
     52  ACT            R3
     53  DIV            R4, R4, R1
     54  MOD            R3, R4, R1
     55  ADD            R0, R0, R5
     56  ACT            R3
     57  JMP            45
     58  DIV            R4, R6, R1
     59  CONST          R1, -24
