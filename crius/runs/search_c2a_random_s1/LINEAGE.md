LINEAGE READOUT run=search_c2a_random_s1 arm=random
ANCESTRY of final-population top 933ec6955715f0cc (180 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0    0.163   0.0     50    200     300       0          0       0       4   12  random_init
   22    0.163   0.0    100      0       0       0          0       0       0    4  delete@1
   57    1.179   1.0     99      0       0       0          0       0       0    3  delete@0+const@0+duplicate@0+1->1
   82    2.688   2.5  37559  10905       0       0          0       0       0   18  const@11+delete@10
  105    3.204   3.0  35638    100   10262       0          0       0       0   26  swap@7,10+swap@5,7
  128    4.693   4.5  36438      0   24619   24519          0       0     100   30  duplicate@16+3->0+arg@0.1+swap@26,6
  154    2.666   2.5  39490      0   35284   17654          0       0    8192   47  replace@22
  183    8.246   8.0  30542      0   13357    3853         64    3815    3857   50  const@15+const@33+replace@20
  203   10.244  10.0  31076      0    3721    1907         64    1868    1909   66  arg@45.2+replace@45
  228   11.753  11.5  30030    448    1465    1481         64    1441     548   75  arg@63.1+const@55
  250    3.702   3.5  36238    587    1929    1960         64    1892     687   78  swap@45,42
  276    8.233   8.0  32466    569     476    1606         64    1540       0   92  const@86
  299   13.287  13.0  25850    714    1336    1331         64    1296       0   94  const@68
  292    6.206   6.0  35682    646     552    1838         64    1772       0   90  arg@43.0
  293   10.259  10.0  29204    528     436    1479         64    1413       0   92  duplicate@71+1->49+insert@56
  294    6.719   6.5  34045    851     818    1603         64    1569       0   91  delete@34
  296   14.809  14.5  23174    658     649    1223         64    1189       0   91  arg@70.0
  297   13.782  13.5  26376    727    1358    1361         64    1327       0   94  swap@16,31+duplicate@24+2->54+insert@46
  gradient (mean first half -> second half of the lineage): reads 4541 -> 343, writes 7369 -> 9241, invokes 4299.8 -> 4128.0, blocks 0.0 -> 57.7, wsBytes 188 -> 1967, successes 2.2 -> 8.0
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      4      0      0.122      0.081    0.163
   25   24      2      0      0.671      0.555    0.671
   50   24      2      0      0.163      0.208    0.671
   75   24      1      0      1.150      2.391    4.703
  100   24      1      0      4.194      1.341    4.194
  125   24      0      0         --      3.316    4.213
  150   24     22      5      1.361      0.411    4.216
  175   24     24     20      2.405         --    3.669
  200   24     24     19      3.042         --    5.213
  225   24     23     21      7.336      2.637   12.273
  250   24     24     20      4.196         --    9.244
  275   24     24     23      6.276         --   12.256
  300   24     23     21      6.921      4.702   12.779
  candidates that invoked a block: 2800; of those in their iteration's top 8: 1026
TOP MECHANISM 933ec6955715f0cc: fitness 13.287 succ 13.0 inter 25850 reads 714 writes 1336 invokes 1331 blocks 64 wsBytes 0 invalid 1242
  trace: {"ACTI": 55530, "BLK_REC_BEGIN": 1406, "BLK_INVOKE": 1331, "ACT": 1255, "BLK_REC_END": 707, "WS_REC_SET": 629, "WS_LINK_GET": 614, "WS_SREAD": 100}
      0  WS_SREAD       R4, R2, R6
      1  BRZ            R2, 33
      2  CONST          R7, -2
      3  WS_SREAD       R4, R7, R6
      4  DIV            R5, R4, R7
      5  BLK_STATE_SET  R3, R5, R1
      6  WS_LINK        R7, R6, R4
      7  ACTI           15
      8  WS_FIND        R5, R0
      9  VGET           R4, R0, R5
     10  WS_REC_NEW     R2
     11  BLK_INVOKE     R4
     12  INPUT          R0, current_block
     13  BRZ            R2, 20
     14  WS_REC_SET     R3, R6, R2
     15  WS_WRITE       R0, R0
     16  INPUT          R1, current_block
     17  MUL            R6, R3, R6
     18  MUL            R6, R3, R6
     19  ACTI           -9
     20  WS_REC_NEW     R2
     21  BLK_INVOKE     R4
     22  INPUT          R0, current_block
     23  BRZ            R2, 25
     24  WS_REC_SET     R3, R6, R2
     25  MOV            R6, R0
     26  BLK_INVOKE     R4
     27  BRZ            R2, 25
     28  WS_REC_SET     R3, R6, R2
     29  DIV            R5, R4, R7
     30  BLK_STATE_SET  R3, R5, R1
     31  MOV            R7, R7
     32  BLK_INVOKE     R4
     33  CONST          R5, 14
     34  BLK_INVOKE     R5
     35  ACTI           1
     36  MUL            R6, R3, R6
     37  MOD            R1, R6, R3
     38  CONST          R7, -1
     39  BLK_REC_END    R7
     40  ACTI           7
     41  CONST          R7, -5
     42  VSET           R4, R2, R7
     43  ACTI           7
     44  MOV            R5, R0
     45  EQ             R5, R0, R4
     46  BLK_REC_BEGIN  
     47  BLK_REC_BEGIN  
     48  ACTI           8
     49  ACTI           7
     50  ACTI           5
     51  VGET           R4, R5, R1
     52  SUB            R5, R4, R2
     53  MOV            R7, R7
     54  ACTI           2
     55  WS_REC_SET     R3, R6, R2
     56  MOV            R6, R0
     57  ACTI           5
     58  ACT            R7
     59  ACTI           9
     60  ACTI           7
     61  CONST          R7, -5
     62  VSET           R0, R2, R7
     63  MOV            R5, R0
     64  ACTI           6
     65  ACTI           9
     66  ACTI           7
     67  ACT            R5
     68  ACTI           9
     69  ACTI           8
     70  VSET           R3, R1, R5
     71  NOT            R3, R1
     72  BLK_INVOKE     R4
     73  ACTI           -7
     74  BRNZ           R1, 83
     75  ACTI           7
     76  CONST          R7, -2
     77  WS_LINK_GET    R1, R0, R3
     78  BRZ            R2, 33
     79  WS_READ        R2, R4
     80  ACTI           -2
     81  WS_FIND        R0, R6
     82  BLK_STATE_SET  R3, R5, R1
     83  INPUT          R3, num_ops
     84  WS_APPEND      R5, R2
     85  BLK_INVOKE     R5
     86  BLK_INVOKE     R5
     87  ACTI           1
     88  ACTI           9
     89  WS_REC_SET     R7, R3, R2
     90  WS_FREE        R7
     91  ACTI           6
     92  EQ             R5, R4, R0
     93  ACTI           5
