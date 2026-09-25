LINEAGE READOUT run=search_c2d_random_s3 arm=random
ANCESTRY of final-population top 5b47569ca88afb66 (128 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0    0.163   0.0      0    100     100     100          0       0       0   21  random_init
   13    0.163   0.0      0      0       0       0          0       0       0   13  delete@1+replace@4
   24    0.163   0.0      0      0       0       0          0       0       0    4  replace@2
   92    1.179   1.0     50      0       0       0          2       0       0    2  insert@1
  121    0.671   0.5     50      0       0       0          2       0       0    1  arg@0.0
  150    0.163   0.0      0      0       0       0          0       0       0    1  arg@0.1+arg@0.0+arg@0.1
  184    1.675   1.5  39518      0       0       0          2       0       0    9  delete@8+const@2
  201    3.695   3.5  36627  21122       0       0          2       0       0   16  duplicate@2+6->4+arg@8.0+const@2
  219    2.682   2.5  37620  37780    9431       0         64       0       0   26  swap@11,23
  236    5.714   5.5  33829  37200   12344       0         64       0       0   34  insert@29+delete@2
  254    4.716   4.5  33722  39696   16963       0          2       0       2   33  delete@21
  268    4.206   4.0  34678  18968   31621       0          2       0       2   35  swap@15,14+swap@13,28+replace@10
  285    7.726   7.5  31913  32296   38661       0          2       0       0   40  swap@1,22+delete@15+swap@16,9
  291    5.695   5.5  35662  28761   43048       0          2       0       0   39  delete@14+insert@20+swap@19,29
  292    5.702   5.5  34815  28089   42037       0          2       0       0   39  swap@16,0
  295    5.186   5.0  36766  37068   36995       0          2       0       0   45  duplicate@15+6->1
  296    3.182   3.0  37206  37380   37331       0          2       0       0   46  insert@3+arg@7.1
  297    7.237   7.0  30888  31286   26032       0          2       0       0   44  delete@41+delete@28+swap@32,15
  298    3.188   3.0  36736  36928   30718       0          2       0       0   42  const@40+delete@33+delete@31
  gradient (mean first half -> second half of the lineage): reads 305 -> 32632, writes 3 -> 20560, invokes 3.1 -> 0.0, blocks 0.8 -> 23.0, wsBytes 0 -> 1, successes 0.6 -> 4.3
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      4      1      0.122      0.122    0.163
   25   24      3      0      0.163      0.163    0.163
   50   24      1      0      0.163      0.148    0.163
   75   24      2      0      0.163      0.163    0.163
  100   24      3      0      0.163      0.155    0.163
  125   24      3      0      0.163      0.210    0.663
  150   24      3      0      0.163      0.155    0.163
  175   24      2      0      0.163      0.854    5.244
  200   24      2      0      0.912      1.115    3.702
  225   24      2      1      4.724      4.139    5.709
  250   24     11      0      4.323      2.482    6.238
  275   24     16      1      1.374      2.412    6.212
  300   24      0      0         --      4.063    7.229
  candidates that invoked a block: 61; of those in their iteration's top 8: 15
TOP MECHANISM 5b47569ca88afb66: fitness 3.188 succ 3.0 inter 36736 reads 36928 writes 30718 invokes 0 blocks 2 wsBytes 0 invalid 18524
  trace: {"ACTI": 73857, "BLK_LEN": 24618, "ACT": 18488, "PMATCH": 12369, "BLK_PATCH": 12331, "WS_FIND": 12310, "PREC_END": 12309, "WS_REC_SET": 12272, "BLK_REC_BEGIN": 12270, "WS_ALLOC": 6116, "BLK_APPEND": 6115}
      0  BLK_PATCH      R5, R6, R6
      1  ACTI           15
      2  ACT            R1
      3  PMATCH         R4, R5, R2
      4  ACTI           9
      5  WS_FIND        R2, R0
      6  BLK_LEN        R7, R5
      7  EQ             R3, R6, R4
      8  WS_REC_SET     R0, R1, R7
      9  VGET           R6, R5, R5
     10  ACTI           7
     11  PREC_END       R3
     12  ACTI           13
     13  NOT            R2, R5
     14  PREC_END       R3
     15  ACTI           2
     16  PMATCH         R5, R7, R3
     17  BLK_REC_BEGIN  
     18  BLK_LEN        R7, R5
     19  ACTI           11
     20  BLK_LEN        R7, R5
     21  MOV            R4, R3
     22  ACTI           15
     23  ACT            R1
     24  ACTI           9
     25  WS_FIND        R2, R0
     26  BLK_LEN        R7, R5
     27  EQ             R3, R4, R4
     28  ACTI           6
     29  ACT            R3
     30  BLK_REC_BEGIN  
     31  EQ             R4, R5, R7
     32  WS_REC_SET     R4, R5, R3
     33  ACTI           1
     34  BLK_PATCH      R5, R6, R6
     35  ACTI           9
     36  WS_ALLOC       R0, R7
     37  VLEN           R6, R2
     38  ACTI           8
     39  BLK_APPEND     R4, R3
     40  BRZ            R5, 0
     41  JMP            18
