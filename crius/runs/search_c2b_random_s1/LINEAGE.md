LINEAGE READOUT run=search_c2b_random_s1 arm=random
ANCESTRY of final-population top e342bfe763e71302 (163 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0    0.163   0.0     50    200     100       0          2       0       0    8  random_init
   26    1.154   1.0  41460  41561       0       0          2       0       0   10  swap@6,7
   48    3.197   3.0  36614  16555       0       0          2       0       0   27  delete@3
   73    4.707   4.5  35520    200       0       0          2       0       0   39  arg@11.0
   97    3.707   3.5  35482    100       0       0          2       0       0   36  delete@27+arg@2.1
  117    3.716   3.5  34520      0       0       0          2       0       0   32  duplicate@25+3->8
  140    6.248   6.0  30685      0       0       0          2       0       0   27  delete@25
  169    3.708   3.5  35508      0       0       0          2       0       0   21  insert@19+delete@6
  195    2.191   2.0  37532      0       0       0          2       0       0   28  delete@16+const@26
  227    2.674   2.5  39594   3202    6404       0          2       0    6404   45  duplicate@11+5->13+delete@17
  251    3.694   3.5  36728   6228   21776    3099          4       0    8192   54  replace@27
  274    6.704   6.5  35205   6842   27556       0          4       0    8192   65  insert@62+duplicate@48+1->60
  292    6.717   6.5  33188  14570   43843       0        136       0    8192   83  arg@42.0+replace@72
  294    6.719   6.5  32910  13637   47754       0         87       0    8192   86  delete@24+insert@16+duplicate@30+3->56
  295    9.750   9.5  29236  11839   41436       0         83       0    8192   87  insert@8+const@86+arg@22.0
  296    4.197   4.0  35512  14294   50005       0         89       0    8192   88  const@38+insert@87+swap@52,85
  298    4.209   4.0  34066  13755   48101       0         88       0    8192   87  delete@48
  299    2.668   2.5  38950  15644   50806       0        100       0    8192   86  arg@25.0+delete@28
  300    6.727   6.5  32061  13041   39032       0         91       0    8192   86  const@10+insert@36+delete@4
  gradient (mean first half -> second half of the lineage): reads 7481 -> 5037, writes 3487 -> 15847, invokes 0.0 -> 378.2, blocks 3.5 -> 15.3, wsBytes 0 -> 4647, successes 3.1 -> 4.4
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      4      1      0.163      0.122    0.163
   25   24      1      0      2.675      1.661    2.679
   50   24      0      0         --      1.969    3.705
   75   24      0      0         --      3.259    4.712
  100   24      2      1      2.673      2.583    3.189
  125   24      0      0         --      4.178    5.708
  150   24      2      0      1.931      3.260    4.199
  175   24      5      0      1.864      1.877    3.175
  200   24      3      0      3.176      3.128    3.180
  225   24     24      0      3.212         --    7.243
  250   24     24      0      2.496         --    4.198
  275   24     24      1      3.789         --    6.242
  300   24     24      0      4.322         --    6.727
  candidates that invoked a block: 148; of those in their iteration's top 8: 33
TOP MECHANISM e342bfe763e71302: fitness 6.727 succ 6.5 inter 32061 reads 13041 writes 39032 invokes 0 blocks 91 wsBytes 8192 invalid 9995
  trace: {"ACT": 72327, "WS_LINK": 12934, "BLK_DELETE": 9829, "WS_REC_SET": 9684, "WS_APPEND": 6578, "WS_FREE": 6569, "WS_SLEN": 6471, "INPUT": 6458, "BLK_COUNT": 3324, "BLK_STATE_SET": 3324, "BLK_COMPOSE": 3266, "ACTI": 3246, "BLK_PATCH": 3246, "BLK_STATE_GET": 3246}
      0  ACT            R6
      1  ACT            R2
      2  ACT            R6
      3  CONST          R7, 5
      4  WS_APPEND      R3, R2
      5  ACT            R6
      6  ACT            R6
      7  WS_FREE        R1
      8  ACT            R0
      9  CONST          R7, 4
     10  ACT            R6
     11  BLK_COUNT      R5
     12  ACT            R6
     13  ACT            R1
     14  ADD            R5, R7, R2
     15  ACT            R6
     16  BLK_STATE_SET  R2, R4, R1
     17  BLK_DELETE     R5
     18  ACT            R6
     19  BLK_COMPOSE    R0, R0, R0
     20  ACT            R6
     21  ACT            R7
     22  NOT            R0, R1
     23  ADD            R5, R7, R2
     24  BLK_DELETE     R5
     25  ACT            R1
     26  CONST          R7, 5
     27  WS_APPEND      R3, R2
     28  ACT            R6
     29  ACT            R6
     30  NOT            R0, R1
     31  WS_LINK        R1, R5, R0
     32  BLK_DELETE     R5
     33  ACT            R5
     34  ACT            R3
     35  CONST          R3, -10
     36  BLK_STATE_GET  R1, R5, R0
     37  ACTI           5
     38  BLK_PATCH      R0, R3, R0
     39  ACT            R6
     40  ACT            R6
     41  WS_SLEN        R2, R2
     42  WS_FREE        R6
     43  ACT            R4
     44  WS_REC_SET     R3, R2, R6
     45  WS_REC_SET     R3, R2, R6
     46  NOT            R0, R1
     47  LT             R6, R4, R5
     48  INPUT          R1, task_index
     49  WS_LINK        R4, R3, R1
     50  DIV            R4, R7, R2
     51  ADD            R5, R7, R2
     52  ACT            R6
     53  INPUT          R1, task_index
     54  WS_LINK        R4, R3, R1
     55  ACT            R6
     56  NOT            R0, R1
     57  WS_LINK        R1, R5, R0
     58  WS_SLEN        R3, R0
     59  WS_REC_SET     R3, R1, R1
     60  JMP            1
     61  BLK_PATCH      R3, R4, R6
     62  DIV            R7, R4, R2
     63  BLK_INVOKE     R5
     64  JMP            75
     65  ACT            R1
     66  ACTI           9
     67  WS_LINK_GET    R2, R5, R3
     68  ACT            R6
     69  WS_READ        R7, R1
     70  WS_REC_SET     R3, R1, R1
     71  INPUT          R1, task_index
     72  BRNZ           R7, 65
     73  DIV            R6, R2, R3
     74  ACT            R4
     75  WS_LINK        R1, R6, R0
     76  BLK_DELETE     R5
     77  ACT            R7
     78  ACT            R5
     79  BLK_STATE_GET  R6, R4, R2
     80  ACT            R3
     81  BLK_STATE_GET  R1, R5, R0
     82  ACTI           5
     83  NOT            R0, R1
     84  ACTI           4
     85  WS_REC_SET     R5, R4, R6
