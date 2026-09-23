LINEAGE READOUT run=search_c2c_recombination_s2 arm=recombination
ANCESTRY of final-population top 790a654baede04ee (160 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   19.378  19.0  14273      0       0       0          2       0       0   39  seed:ENUMERATE_VM
   31   27.976  27.5   2730      0     100       0         64       0       0   61  swap@33,38+splice@14<-donor[29:32]:a3eff
   61   21.423  21.0   9008      0     100       0          2       0       0   61  delete@15
   84   17.918  17.5   9642      0     400     100          2       0     100   83  const@41
  105   25.470  25.0   3514      0     100       0          2       0       0   89  const@41+splice@55<-donor[33:41]:76d4d84
  129   21.958  21.5   4872      0     100       0          4       0       0   91  delete@20+delete@18+delete@13
  156   20.926  20.5   8680      0     200       0          4       0       0   96  duplicate@39+6->52+swap@71,26
  183   24.429  24.0   8319      0     100       0          2       0       0   95  duplicate@71+1->84+arg@93.0
  207   22.960  22.5   4666      0     100       0          2       0       0   93  replace@26+duplicate@79+3->36+delete@24+
  230   21.958  21.5   4970      0     100     100          2      98       0   87  arg@13.0+replace@32
  249   27.473  27.0   3140      0     100     100          2      98       0   93  swap@25,24+duplicate@67+2->9
  271   24.466  24.0   4032      0       0     100          2      98       0   91  duplicate@49+1->12+arg@39.0+swap@63,31
  290   22.917  22.5   9827      0       0     200          2      98       0   93  swap@59,48+const@64+const@43
  289   21.930  21.5   8204      0       0     200          2      98       0   93  const@59
  296   21.933  21.5   7902      0       0     200          2      98       0   95  swap@38,70+const@4+splice@43<-donor[75:7
  297   22.922  22.5   9200      0       0     200          2      98       0   96  delete@51+swap@7,53+delete@5+splice@75<-
  298   20.945  20.5   6518      0     100     100         64      98       0   96  replace@79+splice:none:f863e1e6ce026c5a
  299   21.455  21.0   5254      0     200     100         64      98       0   96  swap@66,32+replace@39+swap@75,13+splice:
  gradient (mean first half -> second half of the lineage): reads 5 -> 0, writes 129 -> 72, invokes 11.2 -> 79.0, blocks 10.2 -> 3.8, wsBytes 22 -> 0, successes 21.8 -> 22.0
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      0      0         --     10.370   19.379
   25   24      3      0      8.549      9.871   22.970
   50   24      0      0         --     15.617   23.451
   75   24     24      5     16.560         --   23.962
  100   24     22      1     17.264     23.681   24.946
  125   24      1      1      1.168     17.637   24.951
  150   24      1      0     20.412     19.168   24.431
  175   24      1      0     20.951     17.837   21.453
  200   24      2      1      0.162     15.836   19.902
  225   24     23     23     20.067      0.000   25.444
  250   24     23     23     19.743      2.692   22.949
  275   24     23     23     13.179      0.000   20.914
  300   24     23     23     17.688      0.671   21.962
  candidates that invoked a block: 2142; of those in their iteration's top 8: 715
TOP MECHANISM 790a654baede04ee: fitness 21.455 succ 21.0 inter 5254 reads 0 writes 200 invokes 100 blocks 64 wsBytes 0 invalid 0
  trace: {"ACT": 17044, "BLK_APPEND": 100, "BLK_INVOKE": 100, "BLK_NEW": 100, "INPUT": 100}
      0  INPUT          R1, num_ops
      1  JMP            60
      2  MOV            R7, R6
      3  INPUT          R1, steps_left
      4  CONST          R5, -5
      5  BLK_REC_END    R2
      6  WS_REC_SET     R4, R6, R1
      7  BLK_REC_BEGIN  
      8  MUL            R4, R4, R4
      9  ACTI           10
     10  PREC_BEGIN     
     11  WS_FIND        R2, R3
     12  ADD            R6, R0, R5
     13  CONST          R5, -17
     14  BLK_REC_BEGIN  
     15  WS_FIND        R7, R3
     16  CONST          R0, 21
     17  CONST          R0, -21
     18  BLK_REC_BEGIN  
     19  MOV            R7, R6
     20  MOV            R7, R6
     21  BLK_REC_BEGIN  
     22  WS_FIND        R7, R3
     23  CONST          R0, -3
     24  CONST          R5, 0
     25  DIV            R4, R0, R1
     26  WS_FIND        R2, R3
     27  CONST          R0, -2
     28  CONST          R5, -4
     29  ADD            R0, R0, R5
     30  HALT           
     31  CONST          R5, -1
     32  BLK_REC_BEGIN  
     33  CONST          R0, -3
     34  ADD            R0, R0, R0
     35  MUL            R2, R1, R1
     36  MOD            R6, R4, R3
     37  ACT            R3
     38  MUL            R3, R1, R1
     39  BLK_STATE_SET  R4, R4, R7
     40  ACT            R3
     41  ACT            R3
     42  EQ             R0, R2, R3
     43  MUL            R0, R4, R3
     44  CONST          R1, 17
     45  WS_REC_SET     R4, R6, R1
     46  MOV            R3, R4
     47  MUL            R2, R1, R0
     48  BLK_COMPOSE    R7, R0, R4
     49  CONST          R0, 7
     50  WS_SREAD       R4, R0, R4
     51  CONST          R0, 11
     52  ADD            R0, R0, R5
     53  BRNZ           R5, 32
     54  ADD            R0, R0, R5
     55  MUL            R2, R3, R1
     56  BLK_COMPOSE    R7, R0, R4
     57  ACT            R3
     58  ADD            R0, R5, R5
     59  MOD            R3, R4, R1
     60  VGET           R7, R0, R4
     61  MUL            R2, R1, R1
     62  ADD            R4, R0, R2
     63  BLK_INVOKE     R5
     64  CONST          R5, -18
     65  ADD            R0, R0, R5
     66  BLK_APPEND     R3, R3
     67  ACT            R3
     68  ADD            R0, R0, R5
     69  DIV            R4, R0, R1
     70  ADD            R0, R0, R5
     71  ADD            R0, R0, R5
     72  ADD            R0, R0, R5
     73  EQ             R0, R2, R3
     74  ADD            R0, R0, R5
     75  MOV            R7, R6
     76  ADD            R0, R0, R5
     77  ADD            R0, R0, R5
     78  CONST          R4, -2
     79  BLK_NEW        R5
     80  CONST          R5, -17
     81  ADD            R0, R0, R5
     82  ADD            R0, R0, R5
     83  BRNZ           R1, 84
     84  ACT            R1
     85  ADD            R0, R0, R5
     86  MOD            R3, R0, R1
     87  ACT            R3
     88  DIV            R4, R0, R1
     89  MOD            R3, R4, R1
     90  ACT            R3
     91  DIV            R4, R4, R1
     92  MOD            R3, R4, R1
     93  ACT            R3
     94  JMP            84
     95  WS_SREAD       R7, R5, R4
