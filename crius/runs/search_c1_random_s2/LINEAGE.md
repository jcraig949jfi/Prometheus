LINEAGE READOUT run=search_c1_random_s2 arm=random
ANCESTRY of final-population top d95cba58ac8f3f95 (118 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0    0.112   0.0      0      0      50       0          0       0      49    8  random_init
   36    0.112   0.0      0      0       0       0          0       0       0    1  replace@0+const@0
  162    1.117   1.0  67612      0       0       0          0       0       0   11  duplicate@0+2->9+const@1
  178   13.194  13.0  54044   2163    6447       0          0       0       0   32  delete@25+duplicate@7+4->9+insert@12
  189    9.170   9.0  58150   6501    6441       0          0       0       0   45  const@30
  201    7.161   7.0  59815  10213    4367       0          0       0       0   64  swap@35,33+delete@59+duplicate@59+2->45
  212   11.159  11.0  60073  13658    4103       0          0       0       0   64  duplicate@36+2->55+const@24
  232   14.233  14.0  47046  11220    4484       0          0       0       0   63  duplicate@41+1->7
  243   18.218  18.0  49530  12385    4932       0          0       0       0   64  replace@46+swap@0,6+arg@12.0
  253   10.144  10.0  62460  12798    7935       0          0       0    1606   64  delete@59+duplicate@30+1->49+replace@14
  262   11.148  11.0  61552  17332    7622       0          0       0       0   62  swap@9,31+swap@52,48+arg@59.0
  277   10.167  10.0  58485  18784    2089       0          0       0       0   64  replace@31+arg@23.0+arg@53.0
  288    6.131   6.0  64481  23209    5159       0          0       0    2583   64  duplicate@39+2->24+arg@40.0+swap@41,62
  297    8.145   8.0  62255  23960       0       0          0       0       0   62  replace@25+delete@10
  293   13.191  13.0  53988  16596    4141       0          0       0    2080   64  const@24+arg@35.2
  294    8.150   8.0  61350  20387    2286       0          0       0    2286   64  replace@35+swap@44,36+arg@7.0
  295    5.129   5.0  64901  22492    2500       0          0       0    2500   63  arg@52.0+delete@13
  296   17.196  17.0  53132  18402    2053       0          0       0    2053   63  const@39
  298    6.137   6.0  63550  25422       0       0          0       0       0   61  swap@27,37+delete@1+const@11
  gradient (mean first half -> second half of the lineage): reads 7394 -> 16446, writes 4259 -> 5235, invokes 0.0 -> 0.0, blocks 0.0 -> 0.0, wsBytes 3 -> 799, successes 6.9 -> 10.9
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      6      2      0.112      0.112    0.112
   25   24      3      0      0.112      0.106    0.112
   50   24     10      0      0.112      0.112    0.112
   75   24      1      0      0.112      0.156    1.123
  100   24      3      0      0.112      0.106    0.112
  125   24      2      0      0.112      0.152    1.123
  150   24      1      0      0.112      0.112    0.112
  175   24      4      0      5.650      6.561   14.223
  200   24      5      0      8.170     11.337   22.244
  225   24      1      0      5.134      6.803   14.188
  250   24      3      0      3.120      5.088   12.190
  275   24      2      0      5.651      7.065   10.188
  300   24     17      0      8.459     13.202   17.235
  candidates that invoked a block: 6; of those in their iteration's top 8: 2
TOP MECHANISM d95cba58ac8f3f95: fitness 6.137 succ 6.0 inter 63550 reads 25422 writes 0 invokes 0 blocks 0 wsBytes 0 invalid 2540
  trace: {"ACTI": 38140, "ACT": 27956, "BLK_DELETE": 7622, "WS_SREAD": 7622, "BLK_STATE_GET": 5088, "WS_FIND": 2546, "WS_LINKS": 2542, "WS_READ": 2542, "WS_REC_GET": 2542, "WS_ALLOC": 2540, "WS_SLEN": 2540}
      0  DIV            R5, R1, R5
      1  ACT            R7
      2  BLK_STATE_GET  R5, R5, R6
      3  ACTI           4
      4  VGET           R1, R0, R7
      5  ACTI           3
      6  ACT            R7
      7  WS_FIND        R2, R5
      8  ACTI           3
      9  ACTI           6
     10  ACTI           5
     11  ACTI           0
     12  ADD            R4, R1, R7
     13  ACTI           3
     14  BLK_DELETE     R2
     15  ACTI           8
     16  ACTI           3
     17  WS_SREAD       R4, R6, R7
     18  ACT            R4
     19  WS_REC_GET     R1, R3, R7
     20  ACTI           3
     21  ACTI           1
     22  ACT            R5
     23  WS_READ        R2, R3
     24  WS_LINKS       R6, R3
     25  MUL            R5, R4, R6
     26  BLK_STATE_GET  R7, R0, R5
     27  ACTI           3
     28  ACT            R4
     29  WS_SREAD       R2, R4, R2
     30  ACTI           0
     31  WS_ALLOC       R3, R7
     32  WS_SREAD       R3, R7, R5
     33  WS_SLEN        R1, R6
     34  ACTI           1
     35  ACT            R3
     36  BLK_DELETE     R6
     37  ACTI           22
     38  ACT            R7
     39  ACT            R0
     40  ACT            R7
     41  BLK_DELETE     R5
     42  LT             R6, R2, R4
     43  ACT            R7
     44  ACT            R7
     45  BRZ            R2, 1
     46  ACTI           3
     47  VGET           R6, R5, R7
     48  VSET           R0, R5, R1
     49  ACTI           -3
     50  ACTI           4
     51  VGET           R7, R1, R4
     52  BLK_STATE_SET  R2, R0, R3
     53  BLK_APPEND     R2, R5
     54  ACT            R7
     55  NOT            R1, R7
     56  ACT            R7
     57  WS_REC_GET     R1, R3, R7
     58  WS_READ        R3, R7
     59  ACTI           3
     60  BRZ            R4, 1
