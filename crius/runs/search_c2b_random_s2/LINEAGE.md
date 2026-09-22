LINEAGE READOUT run=search_c2b_random_s2 arm=random
ANCESTRY of final-population top 58a19cab3af267af (166 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0    0.163   0.0      0      0       0       0          0       0       0   19  random_init
   16    0.163   0.0      0      0       0       0          0       0       0    6  arg@5.0+arg@5.0+delete@1
   62    3.205   3.0  35524      0       0       0          2       0       0    9  duplicate@2+1->3+const@3+duplicate@1+4->
   85    0.662   0.5  40500      0       0       0          2       0       0   11  replace@2+delete@4
  113    2.698   2.5  36532      0       0       0          2       0       0   30  delete@18+arg@23.0
  131    4.715   4.5  34548    100       0       0          2       0       0   41  swap@20,16+const@33+arg@20.0
  152    1.158   1.0  41454      0       0       0          2       0       0   37  delete@0+arg@18.0+delete@18
  172    3.706   3.5  35640      0     100       0          4       0       0   44  arg@30.0
  192    4.214   4.0  34744      0     100       0          2       0       0   43  delete@23+const@5
  218    3.719   3.5    285    200     800       0         64       0     400   42  const@18+replace@21
  240    2.179   2.0    388    200     700       0         66       0     400   50  duplicate@5+3->5+swap@29,9+arg@14.1
  266    3.703   3.5    346    200     400     100          4       2     302   55  insert@49+const@33+delete@42
  286    1.163   1.0    148    100     200       0          4       0     202   52  swap@25,14+arg@8.2
  294    1.152   1.0  40480  20291   20191       0          4       0       0   58  insert@54+swap@27,43+const@49
  295    3.177   3.0  37508  18850   18750       0          4       0       0   59  duplicate@56+1->34
  296    2.152   2.0  40478  20314   20214       0          6       0       0   60  replace@2+insert@27
  298    5.170   5.0  38388  19334   19234       0          6       0       0   61  arg@27.0+insert@27+const@51
  299    5.211   5.0  33584  16937   16837       0          6       0       0   61  swap@19,25
  300   10.297  10.0  23622  12066   11966       0          6       0       0   62  insert@28+const@53
  gradient (mean first half -> second half of the lineage): reads 12 -> 3691, writes 0 -> 5402, invokes 0.0 -> 13.1, blocks 1.5 -> 15.3, wsBytes 0 -> 136, successes 1.7 -> 2.5
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      4      0      0.163      0.122    0.163
   25   24      8      1      0.417      0.385    0.671
   50   24      6      1      0.163      0.191    0.671
   75   24      7      1      1.385      1.388    2.689
  100   24      1      0      0.646      2.194    4.715
  125   24     12      1      4.056      2.599    6.712
  150   24      2      0      2.947      4.313    4.732
  175   24      1      0      4.213      3.487    4.213
  200   24      1      0      2.180      2.153    3.714
  225   24     20      0      0.869      0.708    3.162
  250   24      5      0      0.966      0.876    2.691
  275   24     23     22      2.627      3.185    3.711
  300   24      7      3      2.257      5.074   10.297
  candidates that invoked a block: 518; of those in their iteration's top 8: 179
TOP MECHANISM 58a19cab3af267af: fitness 10.297 succ 10.0 inter 23622 reads 12066 writes 11966 invokes 0 blocks 6 wsBytes 0 invalid 0
  trace: {"ACTI": 48130, "INPUT": 24132, "BLK_DELETE": 12066, "WS_LINK_GET": 12066, "BLK_COMPOSE": 11966}
      0  ADD            R7, R6, R4
      1  MOV            R1, R3
      2  MOD            R1, R2, R3
      3  BRZ            R3, 43
      4  MOD            R5, R0, R0
      5  MOD            R5, R0, R0
      6  WS_REC_NEW     R0
      7  EQ             R6, R3, R5
      8  MOD            R5, R5, R1
      9  WS_WRITE       R5, R6
     10  BRZ            R3, 39
     11  MOD            R5, R1, R0
     12  BRZ            R3, 35
     13  MOD            R5, R0, R0
     14  WS_LINK_GET    R0, R2, R5
     15  EQ             R1, R3, R5
     16  WS_LINK        R4, R6, R3
     17  WS_REC_NEW     R5
     18  PREC_BEGIN     
     19  MOD            R5, R0, R0
     20  VGET           R2, R6, R1
     21  BLK_STATE_SET  R7, R1, R5
     22  ADD            R7, R6, R4
     23  INPUT          R0, interactions_left
     24  VGET           R2, R5, R3
     25  BRZ            R3, 19
     26  VGET           R0, R7, R4
     27  EQ             R4, R7, R5
     28  BLK_DELETE     R4
     29  CONST          R0, 15
     30  BLK_DELETE     R0
     31  ADD            R7, R6, R4
     32  BLK_COMPOSE    R3, R6, R2
     33  BRZ            R6, 43
     34  VGET           R4, R6, R2
     35  ACTI           2
     36  ACTI           8
     37  WS_WRITE       R7, R3
     38  WS_LINKS       R0, R6
     39  BLK_INVOKE     R3
     40  ACTI           12
     41  MOD            R5, R0, R0
     42  ACT            R0
     43  ADD            R7, R6, R4
     44  WS_LINK_GET    R0, R2, R5
     45  VGET           R0, R7, R4
     46  MOD            R7, R5, R0
     47  MOD            R7, R5, R0
     48  BLK_DELETE     R0
     49  INPUT          R0, interactions_left
     50  MOD            R5, R0, R0
     51  INPUT          R5, last_action
     52  ACTI           8
     53  ACTI           8
     54  VLEN           R7, R0
     55  ACTI           9
     56  ACTI           5
     57  BRNZ           R5, 31
     58  BLK_STATE_SET  R1, R5, R7
     59  WS_WRITE       R7, R3
     60  WS_WRITE       R7, R3
     61  WS_REC_NEW     R4
