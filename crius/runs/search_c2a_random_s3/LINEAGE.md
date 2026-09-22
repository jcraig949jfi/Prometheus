LINEAGE READOUT run=search_c2a_random_s3 arm=random
ANCESTRY of final-population top 137c1619929b95ec (186 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0    0.163   0.0      0      0     100       0         64       0       0    8  random_init
   34    1.179   1.0    149      0       0       0          0       0       0    3  duplicate@1+1->2
   54    4.187   4.0  36446  36548       0       0          0       0       0   10  swap@2,5
   77    4.223   4.0  33596      0     100       0          0       0       0   16  insert@15+const@2
  107    1.654   1.5  41438      0   13927       0          0       0       0   21  arg@17.0+arg@14.0
  128    6.217   6.0  33562   8501   50932       0          0       0    8192   32  const@13+const@10
  149    6.740   6.5  30860   9689   43410       0          0       0    8192   49  arg@39.1+insert@48
  175    4.705   4.5  34578  19373   65635       0          0       0    8192   66  delete@15+insert@46
  203    7.220   7.0  32636  24311   59175       0          0       0    7068   76  swap@25,11+insert@48+duplicate@20+4->64
  224    4.207   4.0  34153  22863   55724       0          0       0    3343   96  arg@24.0+arg@0.0+const@35
  250    3.177   3.0  37900  25334   47468       0          0       0    3156   96  arg@36.1+const@7+swap@72,91
  272    7.743   7.5  30180  17476   40948       0          0       0    5873   96  const@82+arg@92.0+const@58
  294    6.231   6.0  30845  31049   58323    3873          0       0    8192   95  insert@67+insert@82
  295    5.195   5.0  34892  35050   65820    4378          0       0    8192   96  const@65+insert@21
  296    4.686   4.5  35962  36091   67784    4510          0       0    8192   96  const@87+const@19+const@64
  297    3.187   3.0  35854  35922   67466    4489          0       0    8192   96  arg@55.2
  298    5.719   5.5  32225  32394   56747    4049          0       0    8192   95  delete@12
  299    2.682   2.5  36598  34553   60298    4236          0       0    8192   96  insert@79+const@18+arg@49.0
  300    5.716   5.5  32765  31073   54213    3803          0       0    8192   96  swap@39,29+swap@18,29
  gradient (mean first half -> second half of the lineage): reads 5318 -> 23481, writes 15156 -> 54864, invokes 1545.3 -> 704.6, blocks 1.4 -> 0.0, wsBytes 1764 -> 5670, successes 2.6 -> 4.8
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      5      0      0.130      0.163    0.163
   25   24      1      0      0.663      1.034    4.212
   50   24      0      0         --      2.322    7.245
   75   24      1      0      1.672      0.884    1.675
  100   24      3      1      3.522      3.470    7.728
  125   24      5      0      1.838      0.602    7.229
  150   24     24      0      3.907         --    9.270
  175   24     24      0      4.070         --    9.770
  200   24     24      0      2.808         --    5.712
  225   24     24      0      6.100         --    9.259
  250   24      3      0      2.506      2.362    5.705
  275   24     24      0      2.787         --    5.705
  300   24     23      1      3.885      0.640    5.716
  candidates that invoked a block: 22; of those in their iteration's top 8: 1
TOP MECHANISM 137c1619929b95ec: fitness 5.716 succ 5.5 inter 32765 reads 31073 writes 54213 invokes 3803 blocks 0 wsBytes 8192 invalid 38775
  trace: {"ACTI": 89206, "WS_FREE": 31013, "BLK_PATCH": 27069, "ACT": 15602, "WS_SREAD": 11603, "INPUT": 11532, "BLK_STATE_SET": 7770, "BLK_COMPOSE": 7769, "WS_APPEND": 7702, "WS_FIND": 3901, "BLK_COUNT": 3900, "WS_LINKS": 3900, "WS_LINK_GET": 3900, "WS_SLEN": 3869, "BLK_INVOKE": 3803, "WS_REC_NEW": 3803, "BLK_REC_BEGIN": 3801, "BLK_REC_END": 100}
      0  ACTI           -12
      1  DIV            R3, R2, R7
      2  BRZ            R0, 7
      3  INPUT          R1, status
      4  VLEN           R3, R5
      5  ACT            R1
      6  BLK_STATE_SET  R7, R1, R1
      7  ACTI           -6
      8  BLK_REC_END    R2
      9  WS_FREE        R3
     10  ACTI           8
     11  WS_FREE        R7
     12  ACT            R1
     13  WS_SREAD       R4, R2, R2
     14  SUB            R6, R7, R6
     15  SUB            R6, R7, R6
     16  ACT            R1
     17  ACTI           4
     18  ACTI           7
     19  WS_FIND        R7, R6
     20  WS_FREE        R2
     21  BLK_STATE_SET  R5, R2, R4
     22  DIV            R6, R4, R1
     23  ACTI           5
     24  WS_FREE        R7
     25  BLK_PATCH      R5, R1, R3
     26  BLK_COMPOSE    R4, R4, R2
     27  WS_LINK_GET    R2, R7, R4
     28  VSET           R5, R3, R5
     29  ACTI           4
     30  BLK_PATCH      R1, R1, R5
     31  VSET           R2, R7, R5
     32  DIV            R4, R2, R7
     33  ACT            R7
     34  BLK_PATCH      R1, R1, R5
     35  BRNZ           R0, 88
     36  ACT            R4
     37  CONST          R3, -18
     38  ACTI           -1
     39  ACTI           -10
     40  BLK_PATCH      R5, R1, R3
     41  WS_LINKS       R5, R4
     42  WS_SREAD       R0, R2, R3
     43  WS_APPEND      R6, R4
     44  ACTI           1
     45  ACTI           3
     46  BLK_COUNT      R0
     47  ACTI           -4
     48  ACTI           13
     49  ACTI           9
     50  BLK_COMPOSE    R2, R4, R1
     51  WS_FREE        R3
     52  INPUT          R1, status
     53  WS_FREE        R7
     54  BLK_STATE_SET  R6, R0, R1
     55  ACTI           7
     56  ACTI           10
     57  WS_SLEN        R4, R1
     58  ACTI           -18
     59  WS_FREE        R7
     60  BLK_PATCH      R5, R1, R3
     61  ACTI           11
     62  SUB            R6, R7, R6
     63  ACTI           8
     64  INPUT          R2, last_primitive
     65  ACTI           2
     66  BLK_INVOKE     R1
     67  WS_REC_NEW     R5
     68  INPUT          R4, last_primitive
     69  ACTI           13
     70  WS_SREAD       R6, R4, R6
     71  SUB            R6, R7, R6
     72  ACTI           -3
     73  WS_APPEND      R6, R4
     74  BLK_PATCH      R5, R1, R3
     75  ACTI           6
     76  WS_FREE        R7
     77  BLK_PATCH      R1, R1, R5
     78  WS_FREE        R7
     79  BLK_REC_BEGIN  
     80  DIV            R4, R2, R7
     81  ACTI           19
     82  ACTI           18
     83  VLEN           R6, R0
     84  BRZ            R0, 10
     85  SUB            R4, R7, R6
     86  BLK_PATCH      R1, R1, R5
     87  ACTI           -3
     88  WS_FREE        R3
     89  ACTI           -2
     90  WS_APPEND      R6, R5
     91  WS_FREE        R7
     92  WS_APPEND      R7, R4
     93  WS_READ        R7, R3
     94  SUB            R7, R7, R1
     95  BLK_REC_END    R1
