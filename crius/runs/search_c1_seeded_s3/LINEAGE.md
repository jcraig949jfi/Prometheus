LINEAGE READOUT run=search_c1_seeded_s3 arm=seeded
ANCESTRY of final-population top 001cc78e9ce9aee1 (195 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   25.315  25.0  31685      0       0       0          0       0       0   39  seed:ENUMERATE_VM
   25   19.242  19.0  44167     50      50       0          0       0       1   62  const@36+const@36+insert@24
   52   20.230  20.0  46319     50     100       0          0       0      51   64  insert@16
   71   28.340  28.0  27579      0     100       0          0       0       1   62  arg@41.0+arg@38.0+replace@34
   94   33.368  33.0  22826      0       0       0          0       0       0   61  swap@18,3
  119   27.308  27.0  32951      0       0       0          0       0       0   59  swap@42,53
  150   23.312  23.0  32435    150       0       0          0       0       0   56  const@12
  176   22.268  22.0  39912    150       0       0          0       0       0   52  swap@48,22+delete@34
  206   21.274  21.0  38881    200     100       0          0       0       0   60  arg@28.0+replace@32+const@55
  227   37.389  37.0  19237    200     150       0         32       0       1   63  arg@12.0+delete@12+const@53
  252   17.248  17.0  43849    200     100       0          0       0       1   62  const@57+delete@10
  275   38.364  38.0  23559    150      50       0          0       0       1   59  const@45+replace@17+insert@45
  296   26.281  26.0  38306    100      50       0          0       0       1   53  replace@19+const@27+insert@23
  294   38.374  38.0  22008    100      50       0          0       0       1   51  swap@12,14
  295   34.363  34.0  23976    100      50       0          0       0       1   52  duplicate@20+1->7+const@40
  297   29.309  29.0  33415    100      50       0          0       0       1   51  delete@28+replace@25+delete@13
  299   38.385  38.0  20142    100      50       0          0       0       1   50  delete@24+const@23
  300   26.284  26.0  37674    100      50       0          0       0       1   51  arg@26.1+insert@47
  gradient (mean first half -> second half of the lineage): reads 33 -> 166, writes 45 -> 53, invokes 0.0 -> 0.0, blocks 0.0 -> 3.3, wsBytes 10 -> 1, successes 28.6 -> 30.3
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      0      0         --     17.631   26.301
   25   24     21      0     10.308      0.785   19.242
   50   24     24      0     22.087         --   30.317
   75   24     18      0     18.625     19.074   30.333
  100   24      5      0      9.762     17.391   29.339
  125   24      0      0         --     20.443   30.315
  150   24      0      0         --     19.239   23.312
  175   24      1      0      1.013     17.080   25.326
  200   24      0      0         --     21.133   30.330
  225   24      7      0     23.405     24.802   31.298
  250   24     24      0     28.739         --   38.390
  275   24     24      0     29.105         --   38.364
  300   24     23      0     18.396      0.112   26.284
  candidates that invoked a block: 4; of those in their iteration's top 8: 0
TOP MECHANISM 001cc78e9ce9aee1: fitness 26.284 succ 26.0 inter 37674 reads 100 writes 50 invokes 0 blocks 0 wsBytes 1 invalid 0
  trace: {"ACT": 37722, "ACTI": 7524, "INPUT": 100, "BLK_REC_BEGIN": 50, "BLK_STATE_GET": 50, "WS_LINKS": 50, "WS_WRITE": 50}
      0  BLK_REC_BEGIN  
      1  INPUT          R5, current
      2  INPUT          R1, num_ops
      3  BLK_STATE_GET  R5, R0, R4
      4  WS_LINKS       R4, R6
      5  WS_WRITE       R6, R5
      6  BRZ            R7, 24
      7  EQ             R2, R7, R2
      8  ADD            R0, R0, R0
      9  WS_APPEND      R3, R0
     10  HALT           
     11  VLEN           R3, R5
     12  WS_LINK        R0, R3, R7
     13  INPUT          R1, current
     14  ADD            R0, R0, R6
     15  HALT           
     16  DIV            R4, R6, R2
     17  HALT           
     18  WS_READ        R7, R1
     19  ACT            R2
     20  EQ             R2, R7, R2
     21  WS_LINK_GET    R4, R3, R5
     22  WS_LINK_GET    R1, R0, R4
     23  CONST          R5, 0
     24  MOD            R3, R0, R1
     25  ACT            R1
     26  CONST          R5, -7
     27  MOD            R3, R0, R1
     28  MOD            R3, R0, R1
     29  ACT            R3
     30  DIV            R4, R0, R1
     31  MOD            R3, R4, R1
     32  ACT            R3
     33  DIV            R4, R4, R3
     34  MOD            R3, R4, R1
     35  ADD            R0, R0, R5
     36  ACT            R3
     37  ACT            R6
     38  ACTI           1
     39  ACT            R1
     40  JMP            28
     41  HALT           
     42  BLK_NEW        R5
     43  DIV            R5, R3, R6
     44  MOD            R3, R0, R3
     45  MUL            R6, R3, R3
     46  BLK_INVOKE     R2
     47  WS_REC_GET     R1, R3, R5
     48  BLK_COMPOSE    R5, R5, R7
     49  ACT            R3
     50  CONST          R5, 1
