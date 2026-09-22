LINEAGE READOUT run=search_c1b_seeded_s2 arm=seeded
ANCESTRY of final-population top d19ba9831f137eca (195 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   18.413  18.0  10217      0       0       0          0       0       0   39  seed:ENUMERATE_VM
   20   20.380  20.0   5651   1402    1502       0          0       0       1   55  delete@3
   38   25.467  25.0   3904     50    1331       0          0       0       0   59  delete@31
   66   21.429  21.0   3780     50      50       0          0       0       0   52  delete@7
   93   16.368  16.0   4660      0      50       0          0       0       0   55  duplicate@31+6->14+const@29+replace@17
  118   14.376  14.0   4492    100       0       0          0       0       0   61  replace@8+const@23
  141   19.378  19.0   4269     50       0       0          0       0       0   56  delete@8+arg@12.1
  171   13.357  13.0   5000    150       0       0          0       0       0   53  duplicate@33+3->15
  195   17.379  17.0  14298    200      50       0          0       0      50   63  const@22+const@5
  223   20.409  20.0  10740     50       0       0          0       0       0   62  swap@11,32
  243   11.293  11.0  24413    100       0       0          0       0       0   56  arg@38.2
  267   16.392  16.0  12757    100       0       0          0       0       0   50  arg@18.0+delete@42
  297   22.417  22.0   9815      0     100       0          0       0       0   47  const@14
  295   14.356  14.0  17102      0     100       0          0       0       0   47  swap@8,17
  296   25.480  25.0   2391      0     100       0          0       0       0   47  arg@10.0
  298   18.415  18.0  10177      0     100       0          0       0       0   46  delete@41+replace@33
  299   22.469  22.0   3693      0     100       0          0       0       0   46  arg@2.0
  300   23.441  23.0   7064      0     100       0          0       0       0   46  swap@16,5
  gradient (mean first half -> second half of the lineage): reads 360 -> 102, writes 832 -> 18, invokes 0.0 -> 0.0, blocks 0.0 -> 0.0, wsBytes 0 -> 7, successes 17.7 -> 17.4
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      0      0         --     10.555   18.432
   25   24     21      0     10.508      3.822   17.417
   50   24      1      0      0.148      3.994   10.311
   75   24      0      0         --      5.900   10.315
  100   24      0      0         --     14.651   20.452
  125   24      0      0         --     13.050   20.402
  150   24      2      0     12.288      9.432   12.289
  175   24      0      0         --     14.140   21.403
  200   24     22      0     13.706     11.275   20.367
  225   24      1      0      0.000     21.632   26.485
  250   24      0      0         --     11.814   19.425
  275   24      1      0      0.153     11.814   18.380
  300   24      1      0      1.151     17.105   23.441
  candidates that invoked a block: 0; of those in their iteration's top 8: 0
TOP MECHANISM d19ba9831f137eca: fitness 23.441 succ 23.0 inter 7064 reads 0 writes 100 invokes 0 blocks 0 wsBytes 0 invalid 0
  trace: {"ACT": 9451, "INPUT": 100, "BLK_APPEND": 50, "WS_REC_NEW": 50}
      0  INPUT          R1, num_ops
      1  BRZ            R3, 11
      2  WS_WRITE       R7, R7
      3  ACTI           -1
      4  MOD            R0, R4, R5
      5  ADD            R0, R0, R5
      6  WS_LINKS       R3, R3
      7  MUL            R4, R5, R3
      8  BLK_STATE_GET  R2, R3, R4
      9  CONST          R1, 6
     10  BLK_COUNT      R2
     11  CONST          R0, -14
     12  LT             R5, R0, R2
     13  ADD            R6, R1, R3
     14  CONST          R0, -5
     15  WS_REC_NEW     R6
     16  INPUT          R0, interactions_left
     17  BLK_APPEND     R2, R1
     18  BRZ            R3, 37
     19  VSET           R6, R5, R2
     20  WS_LINK_GET    R2, R0, R2
     21  ADD            R0, R0, R5
     22  WS_READ        R5, R2
     23  BRNZ           R2, 3
     24  WS_READ        R3, R2
     25  BLK_LEN        R5, R4
     26  CONST          R3, -7
     27  MOD            R3, R4, R5
     28  WS_ALLOC       R5, R1
     29  BLK_NEW        R2
     30  WS_SREAD       R1, R0, R4
     31  MUL            R3, R0, R7
     32  WS_SREAD       R0, R7, R3
     33  VGET           R3, R4, R3
     34  LT             R6, R5, R7
     35  ADD            R0, R0, R2
     36  DIV            R5, R0, R1
     37  DIV            R4, R0, R1
     38  MOD            R3, R0, R1
     39  ACT            R3
     40  ACT            R1
     41  ACT            R3
     42  MOD            R3, R4, R1
     43  ACT            R3
     44  ADD            R0, R0, R5
     45  JMP            37
