LINEAGE READOUT run=search_c2b_random_s3 arm=random
ANCESTRY of final-population top 192c0d79bfcd40dc (183 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0    0.163   0.0     50    100       0       0          4       0       0   18  random_init
   22    0.163   0.0      0      0       0       0          0       0       0   10  swap@6,8+delete@7
   41    0.163   0.0     50      0       0       0          2       0       0    3  delete@0+delete@3
   94    3.194   3.0  36651  24684   24684       0          2       0    8192   12  replace@2+delete@2+duplicate@0+5->4
  117    2.177   2.0  38670   4268   30348       0          2       0    8192   50  replace@21+replace@44
  136    4.207   4.0  35148   4578   20848       0          2       0    8192   77  const@5+delete@45
  160    3.694   3.5  36720  10214   18743       0          2       0    8192   96  replace@59
  187    4.205   4.0  35318  12485   17122       0          2       0    8192   93  delete@59+swap@91,32
  207    5.222   5.0  33105  17744   20214       0          2       0    8192   96  arg@31.1+replace@49
  231    8.235   8.0  31472  16175   22021       0         64       0    6666   96  swap@74,69+swap@87,62
  254    6.240   6.0  30954  20810   16651       0          2       0    8192   96  const@17
  277    3.703   3.5  35140  22475   25834       0         64       0    8192   95  const@16
  296    5.206   5.0  34880  19200   22557       0          2       0    8192   95  insert@50+delete@32
  294    6.741   6.5  30664  16966   19933       0          2       0    8192   95  insert@92+const@55
  295    3.687   3.5  37100  20346   23901       0          2       0    8192   95  const@18+delete@21+duplicate@3+1->93
  297    5.698   5.5  35775  19712   23151       0          2       0    8192   95  arg@87.1
  299    5.199   5.0  35734  19660   23100       0          2       0    8192   95  const@0
  300    7.240   7.0  30814  17074   20056       0          2       0    8192   96  insert@50+const@19
  gradient (mean first half -> second half of the lineage): reads 4992 -> 16797, writes 12175 -> 19831, invokes 4.3 -> 0.0, blocks 2.0 -> 12.8, wsBytes 4363 -> 8116, successes 2.9 -> 5.5
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      5      1      0.097      0.163    0.163
   25   24      7      7      0.663      0.458    1.679
   50   24      2      0      0.163      0.271    0.671
   75   24      1      0      0.163      0.163    0.163
  100   24     13      0      1.785      1.714    4.193
  125   24     24      0      4.134         --    7.242
  150   24     24      0      4.689         --    7.244
  175   24     24      0      6.666         --    8.774
  200   24     24      0      3.021         --    7.230
  225   24     24      0      4.935         --   13.304
  250   24     24      0      3.316         --    7.238
  275   24     24      1      3.207         --    7.753
  300   24     24      0      2.235         --    7.240
  candidates that invoked a block: 196; of those in their iteration's top 8: 65
TOP MECHANISM 192c0d79bfcd40dc: fitness 7.240 succ 7.0 inter 30814 reads 17074 writes 20056 invokes 0 blocks 2 wsBytes 8192 invalid 11335
  trace: {"ACTI": 68336, "WS_APPEND": 17159, "BLK_LEN": 11370, "PREC_BEGIN": 5727, "ACT": 5668, "BLK_COUNT": 2901, "BLK_REC_BEGIN": 2900, "WS_REC_NEW": 2897, "WS_FREE": 2833, "WS_SLEN": 2803}
      0  ACTI           1
      1  WS_APPEND      R1, R7
      2  ACTI           9
      3  CONST          R6, -23
      4  VGET           R1, R6, R6
      5  BLK_COUNT      R3
      6  BLK_LEN        R2, R5
      7  MUL            R6, R6, R2
      8  VGET           R0, R4, R4
      9  ACTI           0
     10  BLK_REC_BEGIN  
     11  WS_REC_NEW     R2
     12  ADD            R1, R0, R5
     13  ACTI           9
     14  WS_APPEND      R1, R7
     15  ACTI           6
     16  PREC_BEGIN     
     17  ACTI           7
     18  ACTI           -13
     19  ACTI           6
     20  ACTI           3
     21  MOV            R5, R2
     22  ACT            R3
     23  SUB            R6, R0, R1
     24  ACTI           1
     25  ACTI           1
     26  BRNZ           R4, 17
     27  ACTI           2
     28  ACT            R4
     29  BLK_LEN        R7, R2
     30  WS_APPEND      R4, R7
     31  BLK_LEN        R2, R3
     32  ACTI           1
     33  PREC_BEGIN     
     34  ACTI           16
     35  ACTI           8
     36  DIV            R5, R7, R6
     37  BRNZ           R0, 93
     38  ACTI           -5
     39  JMP            53
     40  VGET           R6, R3, R2
     41  WS_LINKS       R5, R0
     42  ACTI           0
     43  ACTI           2
     44  ACTI           11
     45  ACT            R4
     46  WS_LINK        R6, R2, R5
     47  ACTI           3
     48  ACTI           -3
     49  PREC_END       R0
     50  BLK_COUNT      R7
     51  ACTI           9
     52  WS_APPEND      R1, R7
     53  ACTI           9
     54  WS_APPEND      R1, R7
     55  ACTI           -1
     56  ACTI           1
     57  ACTI           5
     58  DIV            R5, R7, R6
     59  WS_APPEND      R1, R7
     60  WS_APPEND      R1, R7
     61  WS_FREE        R6
     62  MOV            R5, R2
     63  WS_APPEND      R3, R7
     64  ACTI           6
     65  ACTI           2
     66  ACTI           3
     67  ACTI           2
     68  WS_SLEN        R6, R1
     69  BLK_LEN        R2, R3
     70  DIV            R5, R7, R6
     71  ACTI           1
     72  JMP            2
     73  ADD            R4, R7, R3
     74  JMP            85
     75  ACTI           -11
     76  BLK_COUNT      R6
     77  ACTI           3
     78  ACTI           4
     79  ACTI           3
     80  ACTI           6
     81  BLK_REC_BEGIN  
     82  WS_APPEND      R1, R0
     83  BLK_APPEND     R0, R5
     84  DIV            R5, R7, R6
     85  WS_LINKS       R7, R7
     86  BLK_DELETE     R0
     87  WS_FIND        R6, R0
     88  WS_ALLOC       R1, R4
     89  BLK_INVOKE     R0
     90  ACTI           -1
     91  SUB            R4, R2, R2
     92  CONST          R0, 16
     93  WS_FIND        R7, R1
     94  CONST          R6, -23
     95  WS_REC_NEW     R1
