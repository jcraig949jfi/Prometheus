LINEAGE READOUT run=search_c2a_random_s2 arm=random
ANCESTRY of final-population top f51ccd5faa432f7f (150 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0    0.163   0.0     50    200     300     100          0       0     300   19  random_init
   17    2.181   2.0  38485      0     100       0          0       0     200   19  swap@11,16+const@3
   31    2.665   2.5  40406      0       0       0          0       0       0   12  delete@1+delete@1
   52    1.167   1.0  40480      0       0       0          0       0       0   13  duplicate@5+1->5
   65    0.163   0.0      0      0       0       0          0       0       0    6  replace@3+swap@3,4+delete@1
   83    0.163   0.0      0      0       0       0          0       0       0    1  arg@0.1
  179    1.171   1.0     99      0       0       0          0       0       0    3  insert@1+replace@1+duplicate@1+1->0
  197    1.174   1.0  39550    100       0       0          0       0       0   10  replace@4+delete@6
  212    4.711   4.5  35034      0    4220    4120          0       0       0   29  replace@4
  242    4.219   4.0  34014   3000    6020       0          0       0    2960   44  insert@13+replace@31
  260    6.716   6.5  34342   8147    3022       0         66       0       0   60  swap@6,11
  275    9.758   9.5  29254   3900    2453       0         66       0     102   80  const@67+duplicate@47+5->71+const@48
  290    7.729   7.5  32680   7977    2151    1570        109       0     102   96  duplicate@19+1->84+replace@83+replace@68
  291   11.785  11.5  25890   6638    1885    1302        109       0     102   96  arg@88.0+const@19
  294    9.253   9.0  29792   7496    2054    1473        108       0     102   96  arg@4.0
  295   10.756  10.5  29413   7459    2048    1464        111       0     102   96  const@49+swap@51,16
  296    7.710   7.5  34991   8680    2291    1715        110       0     102   95  delete@86
  299    9.753   9.5  29786   7505    2057    1479        107       0     102   95  const@66+const@82
  300    8.744   8.5  30870   7745    2106    1523        107       0     102   94  delete@66+const@17
  gradient (mean first half -> second half of the lineage): reads 12 -> 3176, writes 5354 -> 3421, invokes 2142.2 -> 716.5, blocks 0.9 -> 43.6, wsBytes 41 -> 1037, successes 0.7 -> 6.0
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      7      2      0.162      0.162    0.163
   25   24      3      0      1.174      2.012    2.189
   50   24      0      0         --      0.607    0.666
   75   24      0      0         --      0.149    0.163
  100   24      3      0      0.163      0.163    0.163
  125   24      1      0      1.179      0.737    1.179
  150   24      2      0      0.163      0.148    0.163
  175   24      1      0      0.163      0.163    0.163
  200   24      1      0      4.224      2.140    4.731
  225   24      9      0      4.932      3.959   10.733
  250   24     13      0      3.855      3.788    7.219
  275   24     20      0      4.838      4.338    9.758
  300   24     23      0      4.946      3.191    8.744
  candidates that invoked a block: 28; of those in their iteration's top 8: 4
TOP MECHANISM f51ccd5faa432f7f: fitness 8.744 succ 8.5 inter 30870 reads 7745 writes 2106 invokes 1523 blocks 107 wsBytes 102 invalid 11097
  trace: {"ACTI": 61809, "ACT": 13626, "BLK_DELETE": 4734, "WS_SLEN": 3008, "INPUT": 1625, "WS_READ": 1606, "WS_SREAD": 1525, "BLK_INVOKE": 1523, "BLK_COUNT": 1506, "BLK_NEW": 1506, "BLK_PATCH": 200, "BLK_STATE_SET": 200, "WS_APPEND": 100, "WS_LINK_GET": 100, "WS_WRITE": 100}
      0  ADD            R7, R2, R2
      1  BLK_DELETE     R7
      2  BLK_PATCH      R5, R5, R3
      3  ACTI           12
      4  ACTI           -18
      5  SUB            R3, R3, R5
      6  BRNZ           R7, 22
      7  ACTI           5
      8  BLK_STATE_SET  R3, R4, R7
      9  BRNZ           R7, 40
     10  BLK_STATE_SET  R3, R4, R7
     11  VSET           R2, R0, R1
     12  ACTI           4
     13  ACTI           7
     14  ACTI           8
     15  WS_APPEND      R6, R4
     16  ACTI           8
     17  ACTI           -18
     18  WS_READ        R6, R1
     19  ACTI           5
     20  BLK_DELETE     R7
     21  WS_LINK_GET    R6, R6, R0
     22  INPUT          R0, current
     23  WS_WRITE       R7, R7
     24  LT             R3, R1, R1
     25  BLK_PATCH      R5, R5, R3
     26  ACTI           12
     27  ACTI           1
     28  ACTI           12
     29  BRNZ           R7, 22
     30  EQ             R6, R2, R7
     31  ACTI           7
     32  ACT            R0
     33  ACTI           6
     34  ACTI           -20
     35  ACTI           5
     36  BLK_DELETE     R7
     37  ACTI           7
     38  WS_SREAD       R3, R0, R0
     39  ACT            R7
     40  ACTI           7
     41  INPUT          R0, current
     42  ACTI           7
     43  ACTI           8
     44  ACTI           -20
     45  ACTI           5
     46  ACTI           5
     47  BLK_INVOKE     R3
     48  ACTI           7
     49  ACTI           6
     50  ACTI           7
     51  ACT            R0
     52  ACT            R0
     53  ACTI           8
     54  ACTI           -20
     55  ACTI           5
     56  ACTI           8
     57  ACTI           -20
     58  ACT            R0
     59  ACTI           7
     60  ACTI           20
     61  ACTI           7
     62  BLK_DELETE     R7
     63  ACTI           7
     64  ACT            R0
     65  ACTI           8
     66  ACTI           5
     67  BLK_COUNT      R2
     68  ACTI           7
     69  ACTI           8
     70  ACT            R0
     71  WS_READ        R1, R2
     72  MOV            R7, R5
     73  BLK_NEW        R3
     74  ACTI           6
     75  ACTI           7
     76  ACTI           5
     77  ACTI           7
     78  ACTI           8
     79  WS_SLEN        R5, R7
     80  ACT            R0
     81  ACTI           6
     82  WS_SLEN        R0, R6
     83  ACTI           7
     84  ACTI           6
     85  ACT            R0
     86  ACTI           -1
     87  ACTI           -20
     88  ACTI           5
     89  BLK_DELETE     R7
     90  ACTI           1
     91  ACTI           2
     92  JMP            31
     93  ACTI           5
