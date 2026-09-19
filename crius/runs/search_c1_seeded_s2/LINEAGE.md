LINEAGE READOUT run=search_c1_seeded_s2 arm=seeded
ANCESTRY of final-population top 004f85fcb612a651 (181 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   20.287  20.0  36485      0       0       0          0       0       0   39  seed:ENUMERATE_VM
   20   36.351  36.0  25560      0       0       0          0       0       0   43  arg@20.2
   43   27.284  27.0  37154      0       0       0          0       0       0   46  duplicate@3+4->20+delete@38+duplicate@10
   74   39.395  39.0  18173      0       0       0          0       0       0   42  swap@28,12+const@22+const@22
   97   20.257  20.0  42431      0       0       0          0       0       0   43  duplicate@35+1->41+delete@13+replace@19
  119   33.359  33.0  23868      0    7933       0          0       0       0   46  swap@26,3
  146   22.291  22.0  35996      0       0       0          0       0       0   37  replace@16+delete@24+delete@14
  176   30.316  30.0  31091  10372       0       0          0       0       0   39  replace@13+insert@7
  204   30.316  30.0  31150  10524       0       0          0       0       0   46  replace@10
  227   38.386  38.0  19404   6463       0       0          0       0       0   41  delete@33
  252   27.284  27.0  36469  24377       0       0          0       0       0   54  replace@6+swap@3,1+delete@0
  273   41.383  41.0  20123   5148       0       0          0       0       0   61  delete@39+replace@11
  298   27.329  27.0  29697   6050       0       0          0       0       0   58  insert@5
  293   36.364  36.0  23675   4854       0       0          0       0       0   57  swap@5,27
  294   31.351  31.0  25955   5304       0       0          0       0       0   56  delete@22+replace@22
  296   40.400  40.0  17438   3611       0       0          0       0       0   56  arg@26.0
  297   33.349  33.0  26212   5356       0       0          0       0       0   57  const@43+insert@16
  299   29.347  29.0  26616   5436       0       0          0       0       0   58  const@45
  gradient (mean first half -> second half of the lineage): reads 0 -> 9737, writes 1097 -> 0, invokes 0.0 -> 0.0, blocks 0.0 -> 0.0, wsBytes 0 -> 0, successes 27.7 -> 29.8
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      0      0         --     11.834   20.300
   25   24      1      0     17.268     11.374   18.276
   50   24      0      0         --     16.331   25.269
   75   24      1      0     19.240     10.427   20.260
  100   24      1      0      0.000     20.359   26.326
  125   24      1      0      0.000     19.413   29.315
  150   24      2      0     15.651     18.573   30.298
  175   24      1      0      2.027     25.332   34.358
  200   24      5      0     21.831     29.097   38.376
  225   24      1      0      2.084     26.731   41.420
  250   24      3      0      5.780     19.307   25.323
  275   24      1      0     28.316     22.490   28.320
  300   24      3      0     12.162     24.852   36.371
  candidates that invoked a block: 1; of those in their iteration's top 8: 0
TOP MECHANISM 004f85fcb612a651: fitness 29.347 succ 29.0 inter 26616 reads 5436 writes 0 invokes 0 blocks 0 wsBytes 0 invalid 50
  trace: {"ACT": 26665, "INPUT": 5336, "WS_FIND": 5336, "ACTI": 5316, "BLK_LEN": 50, "WS_LINK_GET": 50}
      0  BRZ            R3, 34
      1  ACT            R7
      2  INPUT          R1, num_ops
      3  ACT            R3
      4  NOT            R2, R6
      5  WS_SREAD       R1, R1, R4
      6  DIV            R4, R4, R1
      7  MOD            R3, R0, R3
      8  NOT            R7, R2
      9  NOT            R1, R0
     10  INPUT          R5, task_index
     11  BLK_COPY       R6, R5
     12  JMP            31
     13  VSET           R3, R6, R1
     14  WS_FREE        R1
     15  LT             R3, R3, R5
     16  WS_FIND        R5, R5
     17  BLK_COUNT      R6
     18  WS_REC_SET     R4, R3, R1
     19  BLK_LEN        R1, R1
     20  WS_FREE        R7
     21  WS_REC_GET     R2, R3, R0
     22  INPUT          R5, steps_left
     23  BLK_REC_BEGIN  
     24  WS_REC_SET     R5, R2, R3
     25  WS_WRITE       R3, R0
     26  WS_REC_SET     R3, R6, R2
     27  ACT            R3
     28  WS_WRITE       R6, R1
     29  DIV            R4, R0, R1
     30  WS_REC_GET     R3, R2, R5
     31  BRZ            R7, 29
     32  EQ             R2, R1, R6
     33  BLK_DELETE     R3
     34  BLK_LEN        R1, R1
     35  WS_LINK_GET    R0, R7, R3
     36  ACT            R1
     37  INPUT          R1, num_ops
     38  ACT            R3
     39  WS_FIND        R5, R5
     40  MOD            R3, R4, R1
     41  ACT            R3
     42  DIV            R4, R4, R1
     43  MOD            R3, R4, R1
     44  ACT            R3
     45  ACTI           6
     46  DIV            R4, R0, R1
     47  MOD            R3, R0, R3
     48  ADD            R0, R0, R5
     49  ACT            R3
     50  JMP            36
     51  WS_WRITE       R2, R1
     52  WS_FREE        R7
     53  DIV            R3, R0, R1
     54  HALT           
     55  ADD            R0, R0, R5
     56  WS_WRITE       R2, R1
     57  ADD            R1, R0, R1
