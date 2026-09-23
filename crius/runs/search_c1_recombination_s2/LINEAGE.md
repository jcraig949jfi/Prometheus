LINEAGE READOUT run=search_c1_recombination_s2 arm=recombination
ANCESTRY of final-population top db9a25ed1f5fd813 (180 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   20.287  20.0  36485      0       0       0          0       0       0   39  seed:ENUMERATE_VM
   24   24.271  24.0  39531      0       0       0          0       0       0   55  arg@21.0+insert@3+duplicate@27+2->17+spl
   47   26.322  26.0  30824      0       0       0          0       0       0   63  swap@33,43+delete@41
   74   38.392  38.0  18637     50     100       0          0       0      51   64  delete@11+arg@19.0+splice@39<-donor[2:3]
   95   22.322  22.0  30681      0       0       0          0       0       0   60  delete@0+arg@21.0+delete@47
  123   32.356  32.0  24817      0       0       0          0       0       0   63  arg@4.1+swap@7,6
  148   38.350  38.0  25941      0     100       0          0       0      51   64  replace@43
  176   31.309  31.0  33228      0      50       0          0       0       1   60  delete@8
  204   33.355  33.0  25015      0       0       0          0       0       0   61  insert@62+delete@12+delete@11
  232   43.411  43.0  15441      0     177       0          0       0       0   64  duplicate@51+1->39+splice:none:5b9f457c1
  254   37.389  37.0  19263    211     311       0         32       0       0   64  swap@36,25+splice:none:0e9f15fd2dddfe99
  274   38.388  38.0  19343      0      50       0          0       0       0   61  arg@14.0+replace@5
  300   35.366  35.0  23092   5825       0      50          0       0       0   58  arg@18.1+replace@3+arg@16.0
  288   26.296  26.0  35170   8873      50       0          0       0       0   62  delete@13+arg@13.0+swap@35,30
  289   35.360  35.0  24067   6074      50       0          0       0       0   61  delete@20+swap@34,33+const@40
  291   43.427  43.0  12631   3184      50       0          0       0       0   60  delete@27
  292   32.336  32.0  28305   7140      50       0          0       0       0   60  arg@56.1
  298   22.296  22.0  35083   8841      50       0          0       0       0   58  delete@31+delete@24+arg@52.1
  gradient (mean first half -> second half of the lineage): reads 11 -> 1021, writes 34 -> 124, invokes 5.0 -> 0.5, blocks 0.0 -> 4.6, wsBytes 9 -> 5, successes 28.3 -> 32.4
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      0      0         --     12.323   20.288
   25   24      1      0     17.268      7.240   17.268
   50   24      5      0      9.766     15.160   22.258
   75   24     24      0     16.136         --   25.307
  100   24      7      0      0.661     20.099   25.320
  125   24      5      0     23.273     20.830   31.347
  150   24     24      0     19.317         --   29.303
  175   24     24      0     28.223         --   34.320
  200   24     10      0     28.300     33.389   43.407
  225   24      1      0     28.328     26.905   44.430
  250   24      6      6     10.490     21.147   31.341
  275   24      1      0     29.342     22.278   29.347
  300   24      3      1     14.198     26.723   35.366
  candidates that invoked a block: 51; of those in their iteration's top 8: 2
TOP MECHANISM db9a25ed1f5fd813: fitness 35.366 succ 35.0 inter 23092 reads 5825 writes 0 invokes 50 blocks 0 wsBytes 0 invalid 0
  trace: {"ACT": 29022, "WS_SREAD": 5825, "INPUT": 292, "BLK_INVOKE": 50}
      0  INPUT          R1, num_ops
      1  ACT            R1
      2  CONST          R5, 19
      3  BLK_INVOKE     R0
      4  BRZ            R3, 38
      5  WS_WRITE       R7, R0
      6  BLK_APPEND     R3, R2
      7  VLEN           R3, R7
      8  ACT            R1
      9  BRZ            R3, 38
     10  EQ             R6, R3, R7
     11  CONST          R1, 3
     12  ACT            R4
     13  ACT            R0
     14  JMP            22
     15  EQ             R7, R5, R5
     16  DIV            R5, R1, R6
     17  CONST          R0, -4
     18  ADD            R3, R2, R7
     19  ACT            R1
     20  BLK_PATCH      R0, R7, R7
     21  CONST          R5, 12
     22  ADD            R0, R0, R5
     23  INPUT          R4, target
     24  BRZ            R3, 40
     25  MOV            R5, R1
     26  ACT            R2
     27  BLK_COMPOSE    R4, R5, R5
     28  BLK_APPEND     R3, R4
     29  ADD            R0, R6, R5
     30  EQ             R6, R1, R7
     31  BLK_DELETE     R7
     32  MOD            R3, R0, R1
     33  ADD            R0, R0, R5
     34  ACT            R4
     35  BLK_INVOKE     R6
     36  CONST          R7, -10
     37  ACTI           -6
     38  ADD            R0, R6, R5
     39  CONST          R7, 8
     40  ADD            R0, R0, R5
     41  EQ             R3, R1, R7
     42  ADD            R0, R0, R5
     43  ACT            R1
     44  MOD            R3, R0, R1
     45  ACT            R3
     46  DIV            R4, R0, R1
     47  MOD            R3, R4, R1
     48  ACT            R3
     49  DIV            R4, R4, R1
     50  MOD            R3, R4, R1
     51  ACT            R3
     52  WS_SREAD       R4, R2, R0
     53  BRZ            R3, 14
     54  MOD            R3, R2, R1
     55  ACT            R3
     56  ADD            R0, R0, R5
     57  JMP            43
