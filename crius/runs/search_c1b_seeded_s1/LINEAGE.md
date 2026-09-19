LINEAGE READOUT run=search_c1b_seeded_s1 arm=seeded
ANCESTRY of final-population top 83472f066ff4a2a5 (186 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   25.461  25.0   4617      0       0       0          0       0       0   39  seed:ENUMERATE_VM
   25   20.397  20.0  12132      0       0       0          0       0       0   51  const@1+const@23
   48   27.472  27.0   3257      0       0       0          0       0       0   50  replace@16+const@26
   71   21.444  21.0   6652      0       0       0          0       0       0   64  replace@32
   96   21.414  21.0  10168      0       0       0          0       0       0   63  arg@4.0
  115   22.464  22.0   4215      0       0       0          0       0       0   53  delete@26+swap@13,6
  146   20.418  20.0   9700      0       0       0          0       0       0   49  delete@8+arg@6.0+insert@15
  169   20.439  20.0   7283      0       0       0          0       0       0   35  delete@23
  200   20.456  20.0   5218      0       0       0          0       0       0   28  delete@12
  233   20.399  20.0  11970      0      50       0          0       0      50   26  insert@19+replace@9+delete@12
  254   19.390  19.0  13075      0      50       0          0       0      50   35  duplicate@15+5->13+const@1+arg@12.1
  273   25.467  25.0   3944      0      50      50          0       0      50   53  const@1
  292   30.486  30.0   1665      0      50      50          0       0      50   63  duplicate@21+1->9+delete@62+const@1
  293   25.454  25.0   5521      0      50      50          0       0      50   63  duplicate@12+1->61+const@1+delete@39
  294   20.455  20.0   5343      0      50      50          0       0      50   63  swap@38,60
  296   18.393  18.0  12690      0      50      50          0       0      50   63  arg@18.0
  297   18.339  18.0  19192      0      50      50          0       0      50   63  replace@15+delete@6+insert@38
  298   26.461  26.0   4669      0      50      50          0       0      50   62  replace@25+delete@3
  299   23.379  23.0  14413      0      50      50          0       0      50   61  replace@35+delete@47
  gradient (mean first half -> second half of the lineage): reads 0 -> 67, writes 0 -> 33, invokes 0.0 -> 13.3, blocks 0.0 -> 0.0, wsBytes 0 -> 29, successes 21.8 -> 21.9
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      0      0         --     19.495   25.461
   25   24      0      0         --      9.362   20.397
   50   24      1      0     24.463     15.747   26.471
   75   24      0      0         --     16.599   19.380
  100   24      0      0         --     16.631   22.452
  125   24      0      0         --     16.913   27.436
  150   24      0      0         --     12.366   23.430
  175   24      0      0         --     16.573   21.446
  200   24      0      0         --     15.001   20.456
  225   24      0      0         --     10.365   18.392
  250   24     21      0     14.774      9.626   26.446
  275   24     21      1     21.670     23.427   28.448
  300   24     24      2     12.737         --   22.427
  candidates that invoked a block: 31; of those in their iteration's top 8: 5
TOP MECHANISM 83472f066ff4a2a5: fitness 23.379 succ 23.0 inter 14413 reads 0 writes 50 invokes 50 blocks 0 wsBytes 50 invalid 0
  trace: {"ACT": 19251, "INPUT": 100, "BLK_INVOKE": 50, "WS_LINK": 50}
      0  ADD            R0, R0, R5
      1  CONST          R5, -18
      2  DIV            R0, R5, R6
      3  DIV            R4, R0, R1
      4  INPUT          R2, num_ops
      5  ACT            R3
      6  JMP            42
      7  BLK_INVOKE     R1
      8  MOD            R3, R0, R1
      9  ADD            R5, R4, R5
     10  ACT            R3
     11  ACT            R3
     12  NOT            R5, R6
     13  WS_READ        R0, R7
     14  DIV            R0, R5, R6
     15  BLK_APPEND     R4, R5
     16  BLK_COUNT      R1
     17  DIV            R4, R0, R1
     18  ADD            R0, R0, R5
     19  WS_FIND        R3, R6
     20  BLK_INVOKE     R1
     21  BLK_NEW        R4
     22  ADD            R0, R0, R5
     23  WS_REC_NEW     R5
     24  BLK_COPY       R2, R0
     25  ADD            R0, R0, R5
     26  LT             R2, R0, R2
     27  ADD            R4, R5, R1
     28  JMP            44
     29  WS_WRITE       R5, R3
     30  WS_LINK_GET    R2, R2, R3
     31  JMP            47
     32  NOT            R5, R6
     33  BLK_REC_BEGIN  
     34  ACT            R3
     35  DIV            R0, R0, R1
     36  ACT            R3
     37  EQ             R0, R0, R2
     38  ACT            R3
     39  ACT            R1
     40  INPUT          R4, current
     41  BRZ            R1, 52
     42  ADD            R0, R0, R5
     43  WS_LINK        R6, R3, R2
     44  INPUT          R1, num_ops
     45  BLK_INVOKE     R1
     46  DIV            R4, R0, R1
     47  ACT            R1
     48  ACT            R3
     49  DIV            R4, R0, R1
     50  MOD            R3, R0, R1
     51  ADD            R5, R4, R5
     52  ACT            R3
     53  MOD            R3, R4, R1
     54  ACT            R3
     55  ADD            R0, R0, R5
     56  JMP            47
     57  WS_LINK_GET    R2, R2, R3
     58  WS_FIND        R5, R4
     59  JMP            47
     60  BLK_REC_BEGIN  
