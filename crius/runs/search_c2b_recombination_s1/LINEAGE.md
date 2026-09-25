LINEAGE READOUT run=search_c2b_recombination_s1 arm=recombination
ANCESTRY of final-population top 075631c226922b13 (161 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   17.839  17.5  18871      0       0       0          2       0       0   39  seed:ENUMERATE_VM
   22   21.436  21.0   7468      0     100       0          2       0     200   60  arg@7.0+delete@31
   53   19.948  19.5   6117      0     100       0          2       0     200   57  const@2+delete@40
   79   22.433  22.0   7847      0     200       0          2       0     400   86  delete@15
  101   22.418  22.0   9722      0     200       0          2       0     400   93  delete@68+replace@46
  125   20.918  20.5   9714    100     200       0          2       0     400   89  delete@66
  152   25.447  25.0   6179    100     200       0          2       0     400   82  swap@52,38+swap@15,25
  178   19.949  19.5   5954      0     200       0          2       0     400   80  replace@48
  198   19.929  19.5   8426      0     200       0          2       0     400   73  swap@20,23+const@49+delete@42
  221   27.467  27.0   3816      0     100       0          2       0     200   66  delete@14+const@24
  243   22.934  22.5   7776      0     200       0          2       0     400   56  swap@29,15+delete@29
  260   22.435  22.0   7620      0     200       0          2       0     400   50  arg@22.0+duplicate@45+2->10+const@32
  287   25.454  25.0   5368    100     200       0          2       0     400   77  replace@2+delete@6
  290   20.863  20.5  16213    100     200       0          2       0     400   76  delete@17+insert@39+delete@23
  293   18.378  18.0  14430    100     200       0          2       0     400   76  const@54
  294   23.940  23.5   7096    100     200       0          2       0     400   79  delete@14+const@49+duplicate@50+4->25
  298   20.403  20.0  11416    100     200       0          2       0     400   79  const@39+swap@25,28+replace@9
  300   23.918  23.5   9622    100       0       0          2       0       0   80  swap@46,10+replace@52+swap@9,14+splice@5
  gradient (mean first half -> second half of the lineage): reads 20 -> 22, writes 164 -> 178, invokes 0.0 -> 0.0, blocks 2.0 -> 2.0, wsBytes 328 -> 338, successes 20.9 -> 21.3
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      1      0      9.268      7.407   17.839
   25   24     20      0      8.711      5.973   20.912
   50   24     20      0     16.792      5.270   20.921
   75   24     23      0     18.101      0.000   21.927
  100   24     24      0     16.801         --   23.427
  125   24     23      0     15.210      0.163   21.919
  150   24     24      0     16.729         --   22.936
  175   24     23      0     17.735      0.163   23.958
  200   24     24      0     15.446         --   22.386
  225   24     23      0     17.355      0.163   24.930
  250   24     24      0     13.426         --   19.873
  275   24     24      1     16.753         --   21.409
  300   24     23      0     20.011     23.918   23.918
  candidates that invoked a block: 38; of those in their iteration's top 8: 9
TOP MECHANISM 075631c226922b13: fitness 23.918 succ 23.5 inter 9622 reads 100 writes 0 invokes 0 blocks 2 wsBytes 0 invalid 0
  trace: {"ACT": 29076, "INPUT": 300, "PINVOKE": 200, "WS_LINK_GET": 100}
      0  INPUT          R1, num_ops
      1  PINVOKE        R6, R3
      2  INPUT          R2, steps_left
      3  PINVOKE        R6, R3
      4  CONST          R5, -1
      5  INPUT          R3, current_block
      6  WS_LINK_GET    R6, R4, R5
      7  NOT            R2, R6
      8  EQ             R2, R3, R0
      9  JMP            69
     10  BLK_STATE_GET  R7, R1, R2
     11  WS_REC_NEW     R0
     12  WS_REC_NEW     R7
     13  ACT            R3
     14  WS_FREE        R0
     15  ACT            R6
     16  MOD            R6, R6, R6
     17  JMP            57
     18  WS_APPEND      R7, R3
     19  BLK_STATE_GET  R7, R1, R2
     20  MOD            R3, R0, R1
     21  NOT            R5, R4
     22  CONST          R0, -5
     23  BRZ            R3, 24
     24  WS_WRITE       R7, R1
     25  CONST          R0, -15
     26  MOV            R5, R5
     27  WS_FREE        R2
     28  BLK_APPEND     R5, R0
     29  ACT            R1
     30  MOD            R3, R0, R1
     31  DIV            R4, R0, R1
     32  ACT            R3
     33  WS_APPEND      R0, R4
     34  BLK_DELETE     R4
     35  JMP            63
     36  MOD            R3, R4, R1
     37  DIV            R4, R0, R1
     38  ACT            R3
     39  CONST          R7, -18
     40  ACT            R6
     41  WS_SLEN        R3, R3
     42  ADD            R0, R0, R5
     43  MOD            R6, R6, R6
     44  JMP            49
     45  WS_APPEND      R7, R3
     46  ADD            R0, R0, R5
     47  WS_READ        R3, R6
     48  MOD            R3, R0, R1
     49  MOD            R3, R3, R1
     50  WS_APPEND      R3, R3
     51  BLK_DELETE     R4
     52  JMP            60
     53  WS_READ        R5, R6
     54  CONST          R0, -9
     55  BLK_APPEND     R5, R0
     56  MOV            R5, R5
     57  WS_FREE        R2
     58  CONST          R0, -15
     59  BRZ            R3, 19
     60  MOV            R0, R5
     61  VLEN           R2, R7
     62  BLK_NEW        R2
     63  WS_LINK        R5, R2, R0
     64  BRZ            R3, 60
     65  BLK_STATE_SET  R1, R2, R5
     66  LT             R2, R0, R2
     67  WS_REC_NEW     R0
     68  WS_WRITE       R7, R1
     69  ACT            R1
     70  MOD            R3, R0, R1
     71  DIV            R4, R0, R1
     72  ACT            R3
     73  MOD            R3, R4, R1
     74  ACT            R3
     75  DIV            R4, R4, R1
     76  MOD            R3, R4, R1
     77  ACT            R3
     78  ADD            R0, R0, R5
     79  JMP            69
