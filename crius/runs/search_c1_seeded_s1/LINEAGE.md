LINEAGE READOUT run=search_c1_seeded_s1 arm=seeded
ANCESTRY of final-population top d467f76689979ce2 (186 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   30.366  30.0  23009      0       0       0          0       0       0   39  seed:ENUMERATE_VM
   33   31.309  31.0  31370      0    8004       0          0       0       0   50  delete@31+const@27
   63   22.305  22.0  33584      0      50       0          0       0       0   53  swap@23,36
   85   33.353  33.0  25387     50      50       0          0       0       0   53  const@32+arg@21.0
  105   40.403  40.0  16784      0     100       0          0       0      50   51  const@10
  131   30.317  30.0  31681      0     100       0          0       0       0   53  const@13+const@13
  158   38.373  38.0  22102      0     100       0          0       0       1   60  duplicate@6+5->7+const@45
  178   42.370  42.0  22564   8984       0       0          0       0       0   64  insert@8
  197   30.354  30.0  25458      0       0       0          0       0       0   61  delete@14
  217   38.358  38.0  24819     50       0       0          0       0       0   61  replace@19+duplicate@7+1->26+swap@31,16
  245   30.319  30.0  31565     50       0       0          0       0       0   59  delete@10+const@17
  271   25.299  25.0  35012      0       0       0          0       0       0   64  arg@14.2
  291   43.416  43.0  14546      0       0       0          0       0       0   60  delete@13
  292   49.433  49.0  11564      0       0       0          0       0       0   59  delete@43
  293   36.373  36.0  21985      0       0       0          0       0       0   58  delete@4
  295   35.347  35.0  26519      0       0       0          0       0       0   57  delete@22
  296   25.270  25.0  39906      0       0       0          0       0       0   56  delete@29
  297   30.314  30.0  32342      0       0       0          0       0       0   55  delete@33
  300   27.315  27.0  32142      0       0       0          0       0       0   56  insert@26+const@45+swap@20,24
  gradient (mean first half -> second half of the lineage): reads 13 -> 634, writes 1070 -> 158, invokes 280.5 -> 0.0, blocks 0.0 -> 0.0, wsBytes 7 -> 0, successes 30.2 -> 30.9
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      0      0         --     23.042   30.366
   25   24      2      0      0.096     13.571   25.306
   50   24      1      0      0.000     19.545   41.397
   75   24      2      0      2.616     18.113   26.305
  100   24     20      0     18.694     14.209   30.329
  125   24      0      0         --     24.191   34.344
  150   24     11      0     26.103     21.951   31.331
  175   24      0      0         --     24.992   36.347
  200   24      0      0         --     17.297   24.294
  225   24     10      0     17.021     25.494   36.320
  250   24      2      0      8.672     23.939   38.350
  275   24      0      0         --     29.856   44.426
  300   24      0      0         --     19.127   27.315
  candidates that invoked a block: 2; of those in their iteration's top 8: 0
TOP MECHANISM d467f76689979ce2: fitness 27.315 succ 27.0 inter 32142 reads 0 writes 0 invokes 0 blocks 0 wsBytes 0 invalid 0
  trace: {"ACT": 40244, "INPUT": 50}
      0  INPUT          R1, num_ops
      1  CONST          R5, 10
      2  JMP            41
      3  ACT            R3
      4  CONST          R5, 11
      5  SUB            R7, R3, R2
      6  ACT            R6
      7  HALT           
      8  BLK_NEW        R7
      9  HALT           
     10  VGET           R2, R1, R1
     11  MOV            R2, R1
     12  VSET           R4, R0, R7
     13  ADD            R0, R1, R5
     14  WS_REC_NEW     R2
     15  WS_READ        R6, R4
     16  ADD            R3, R4, R1
     17  BLK_REC_BEGIN  
     18  NOT            R3, R2
     19  NOT            R2, R6
     20  BLK_NEW        R7
     21  WS_FIND        R7, R1
     22  MOV            R2, R1
     23  CONST          R5, 10
     24  JMP            15
     25  ACT            R3
     26  WS_LINK_GET    R6, R6, R4
     27  INPUT          R1, target
     28  WS_REC_GET     R6, R6, R2
     29  WS_FIND        R4, R1
     30  WS_LINK_GET    R0, R2, R5
     31  BLK_REC_BEGIN  
     32  HALT           
     33  WS_FIND        R7, R3
     34  WS_LINKS       R3, R2
     35  CONST          R0, -2
     36  ACT            R3
     37  MOD            R3, R0, R1
     38  BLK_COUNT      R2
     39  WS_FIND        R7, R4
     40  WS_REC_NEW     R5
     41  ADD            R3, R4, R1
     42  CONST          R0, -8
     43  ACT            R3
     44  MOD            R3, R0, R1
     45  CONST          R5, 17
     46  ACT            R3
     47  DIV            R4, R0, R1
     48  MOD            R3, R4, R1
     49  DIV            R4, R4, R1
     50  ACT            R3
     51  ACT            R2
     52  ADD            R0, R0, R5
     53  MOD            R3, R4, R1
     54  ACT            R1
     55  JMP            43
