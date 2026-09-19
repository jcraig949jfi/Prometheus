LINEAGE READOUT run=search_c2a_recombination_s1 arm=recombination
ANCESTRY of final-population top 169cae41f3c64dd2 (169 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   17.839  17.5  18871      0       0       0          0       0       0   39  seed:ENUMERATE_VM
   28   18.356  18.0  17078      0       0       0          0       0       0   58  delete@41+const@19+splice@9<-donor[27:32
   49   23.904  23.5  11292      0     100       0          0       0     200   84  arg@5.0+arg@58.1
   76   22.915  22.5  10004      0     100       0          0       0     200   74  swap@73,69
  102   25.976  25.5   2852      0     100       0          0       0     200   66  const@29
  127   21.413  21.0  10292      0     200       0          0       0     200   64  const@32
  159   18.877  18.5  14560      0     200       0          0       0     200   59  replace@4+delete@8+const@11
  189   21.949  21.5   6022      0     500       0          0       0     300   90  arg@37.2+swap@8,59+splice@37<-donor[45:5
  210   20.943  20.5   6746      0     500       0          0       0     300   96  arg@13.0+replace@42
  229   18.862  18.5  16282    200     300       0          0       0     300   94  replace@72
  259   23.941  23.5   6834    200     300       0          0       0     300   96  replace@66+duplicate@56+1->35+replace@72
  277   21.938  21.5   7230      0     400       0          0       0     100   96  delete@43+insert@66+const@2
  297   22.969  22.5   3612    100     200       0          0       0     100   96  arg@26.2
  292   23.951  23.5   5714    100     300       0          0       0     100   95  duplicate@31+3->92+delete@5+swap@69,76
  293   20.390  20.0  12932    100     300       0          0       0     100   95  insert@21+delete@0
  295   24.444  24.0   6550    100     300       0          0       0     100   96  duplicate@30+1->24+delete@11+splice@51<-
  296   24.452  24.0   5655    100     200       0          0       0     100   96  swap@69,28
  299   23.449  23.0   5962    100     100       0          0       0     100   96  replace@60+delete@76+insert@4+splice:non
  gradient (mean first half -> second half of the lineage): reads 0 -> 66, writes 94 -> 381, invokes 0.0 -> 0.0, blocks 0.0 -> 0.0, wsBytes 139 -> 255, successes 21.4 -> 21.7
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      1      0      9.268      7.407   17.839
   25   24      1      0      0.163     10.296   19.406
   50   24     23      0     14.941      0.142   21.921
   75   24     24      0     19.968         --   22.452
  100   24     23      0     15.487     23.415   23.415
  125   24     23      0     16.779      0.000   24.439
  150   24     23      0     18.701     20.911   22.917
  175   24     24      0     13.855         --   21.920
  200   24     24      0     17.223         --   21.378
  225   24     24      0     19.571         --   24.927
  250   24     24      0     15.003         --   22.922
  275   24     24      0     16.771         --   20.430
  300   24     23      0     16.841     20.912   21.914
  candidates that invoked a block: 0; of those in their iteration's top 8: 0
TOP MECHANISM 169cae41f3c64dd2: fitness 23.449 succ 23.0 inter 5962 reads 100 writes 100 invokes 0 blocks 0 wsBytes 100 invalid 0
  trace: {"ACT": 18760, "INPUT": 100, "WS_FIND": 100, "WS_LINK": 100}
      0  INPUT          R1, num_ops
      1  CONST          R5, 16
      2  BRZ            R6, 70
      3  WS_REC_SET     R2, R3, R5
      4  LT             R1, R5, R4
      5  ACT            R0
      6  BLK_PATCH      R1, R3, R6
      7  ADD            R6, R3, R5
      8  MOD            R2, R0, R1
      9  BLK_DELETE     R4
     10  WS_WRITE       R1, R2
     11  WS_LINK        R7, R6, R4
     12  WS_REC_GET     R5, R3, R1
     13  BLK_DELETE     R2
     14  MOD            R3, R0, R1
     15  BRNZ           R3, 12
     16  ADD            R0, R0, R5
     17  WS_LINK_GET    R2, R7, R5
     18  ACT            R1
     19  JMP            28
     20  BLK_STATE_GET  R0, R2, R2
     21  JMP            33
     22  WS_APPEND      R5, R4
     23  DIV            R1, R5, R6
     24  BRZ            R3, 83
     25  ADD            R0, R0, R5
     26  ACTI           2
     27  DIV            R4, R0, R4
     28  BLK_DELETE     R4
     29  BLK_COPY       R3, R3
     30  LT             R4, R5, R5
     31  BRZ            R3, 84
     32  MOD            R2, R0, R1
     33  ACT            R2
     34  WS_ALLOC       R0, R1
     35  ACTI           -15
     36  LT             R3, R2, R3
     37  ADD            R0, R0, R5
     38  CONST          R4, -11
     39  WS_FIND        R7, R4
     40  BLK_STATE_SET  R0, R2, R0
     41  BRNZ           R2, 2
     42  BLK_STATE_SET  R0, R2, R6
     43  VSET           R4, R2, R4
     44  WS_WRITE       R1, R2
     45  WS_REC_NEW     R7
     46  BLK_LEN        R3, R5
     47  WS_ALLOC       R1, R3
     48  BRNZ           R3, 12
     49  ADD            R4, R0, R5
     50  WS_LINK_GET    R7, R6, R2
     51  ACTI           9
     52  MOD            R3, R0, R1
     53  MOD            R3, R0, R1
     54  ADD            R0, R5, R5
     55  BLK_STATE_SET  R6, R6, R5
     56  LT             R3, R2, R3
     57  DIV            R4, R0, R1
     58  INPUT          R7, last_primitive
     59  ADD            R4, R2, R5
     60  WS_REC_NEW     R0
     61  WS_REC_GET     R1, R0, R0
     62  ADD            R0, R0, R5
     63  BLK_PATCH      R6, R5, R7
     64  ACT            R1
     65  MOD            R3, R0, R3
     66  BLK_DELETE     R2
     67  BRZ            R1, 39
     68  ADD            R4, R0, R5
     69  ACT            R1
     70  MOD            R2, R7, R1
     71  ADD            R7, R5, R5
     72  WS_FIND        R2, R0
     73  ADD            R0, R4, R5
     74  MOD            R3, R0, R1
     75  WS_LINK        R1, R1, R6
     76  ACT            R1
     77  ADD            R3, R7, R3
     78  ADD            R0, R0, R5
     79  MOD            R3, R0, R1
     80  CONST          R5, -1
     81  ACT            R3
     82  ADD            R0, R0, R4
     83  DIV            R4, R0, R1
     84  MOD            R3, R4, R1
     85  ACT            R3
     86  DIV            R4, R4, R1
     87  MOD            R3, R4, R1
     88  ACT            R3
     89  ACT            R1
     90  JMP            78
     91  WS_REC_NEW     R1
     92  BRZ            R3, 84
     93  MOD            R2, R0, R1
     94  ACT            R2
     95  WS_REC_SET     R2, R2, R7
