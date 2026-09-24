LINEAGE READOUT run=search_c1b_recombination_s1 arm=recombination
ANCESTRY of final-population top a6d81c1c5184b346 (189 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   25.461  25.0   4617      0       0       0          0       0       0   39  seed:ENUMERATE_VM
   43   21.352  21.0  17478     50       0       0          0       0       0   53  arg@40.1+delete@41
   66   26.479  26.0   2448     50       0       0          0       0       0   63  const@2+const@19+const@2
   91   19.374  19.0  14861    100      50       0          0       0       0   60  delete@61+delete@6
  111   25.466  25.0   3990     99      50       0          0       0       0   64  swap@40,62+const@16
  131   21.471  21.0   3446    150     100       0          0       0       0   64  insert@50+const@50
  147   15.347  15.0  17902   1342     100       0          0       0       0   64  duplicate@1+1->2+replace@19+splice:none:
  167   27.457  27.0   5038   1601       0       0          0       0       0   64  replace@40
  187   14.275  14.0  26205   8657       0       0          0       0       0   63  delete@20
  211   19.375  19.0  14570    462    4663       0          0       0      12   60  const@46+delete@11
  237   20.413  20.0  10277      0       0       0          0       0       0   62  arg@10.1+const@44
  260   27.462  27.0   4469     50       0    1508          0       0       0   62  replace@16
  282   21.429  21.0   8311     50       0       0          0       0       0   62  delete@22
  290   20.379  20.0  14143     50       0       0          0       0       0   59  replace@60+delete@9+delete@42
  293   21.461  21.0   4514     50       0       0          0       0       0   59  arg@5.0+const@35
  294   20.403  20.0  11385     50       0       0          0       0       0   59  arg@39.0+const@35
  296   11.328  11.0  20078     50       0       0          0       0       0   60  replace@43+duplicate@54+1->57
  299   20.424  20.0   8840     50       0       0          0       0       0   60  arg@20.0+arg@0.0
  300   17.381  17.0  13903     50       0       0          0       0       0   61  duplicate@30+1->52+const@35
  gradient (mean first half -> second half of the lineage): reads 217 -> 870, writes 47 -> 602, invokes 3.2 -> 446.2, blocks 0.0 -> 0.0, wsBytes 2 -> 3, successes 21.1 -> 20.4
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      0      0         --     15.173   25.461
   25   24      4      0      8.987      9.354   18.387
   50   24      0      0         --     15.165   28.392
   75   24      0      0         --      9.620   20.370
  100   24      0      0         --     10.562   15.368
  125   24      1      0     15.361     14.977   24.387
  150   24      1      0      0.142     14.566   25.391
  175   24      1      0     19.387     13.714   20.435
  200   24     21      0     12.409      1.494   20.459
  225   24      1      0     17.384     19.780   25.434
  250   24      1      0     15.319     13.451   22.452
  275   24      0      0         --     13.482   28.415
  300   24      0      0         --     10.257   17.381
  candidates that invoked a block: 2; of those in their iteration's top 8: 0
TOP MECHANISM a6d81c1c5184b346: fitness 17.381 succ 17.0 inter 13903 reads 50 writes 0 invokes 0 blocks 0 wsBytes 0 invalid 49
  trace: {"ACT": 18568, "INPUT": 5628, "ACTI": 50, "WS_FIND": 50}
      0  BRZ            R3, 34
      1  WS_SLEN        R4, R6
      2  JMP            24
      3  VGET           R5, R6, R1
      4  DIV            R6, R5, R1
      5  WS_FIND        R4, R5
      6  ADD            R0, R0, R0
      7  MUL            R0, R4, R7
      8  MOD            R3, R4, R3
      9  MOD            R3, R4, R3
     10  BLK_REC_END    R5
     11  SUB            R0, R2, R2
     12  HALT           
     13  BLK_COUNT      R2
     14  ACT            R6
     15  WS_SREAD       R0, R4, R1
     16  VGET           R0, R4, R5
     17  DIV            R4, R4, R1
     18  WS_FREE        R1
     19  MOD            R3, R4, R3
     20  BLK_DELETE     R1
     21  ADD            R0, R0, R0
     22  WS_SREAD       R7, R0, R3
     23  ADD            R0, R0, R5
     24  JMP            25
     25  ADD            R0, R0, R4
     26  MOD            R3, R5, R1
     27  JMP            59
     28  JMP            27
     29  JMP            35
     30  INPUT          R5, interactions_left
     31  MUL            R0, R4, R7
     32  JMP            23
     33  WS_LINK_GET    R5, R4, R0
     34  WS_FIND        R3, R2
     35  ACTI           7
     36  INPUT          R1, num_ops
     37  JMP            45
     38  JMP            27
     39  ACT            R5
     40  JMP            57
     41  ADD            R0, R5, R5
     42  WS_SREAD       R0, R4, R1
     43  BRZ            R7, 59
     44  ACT            R3
     45  BRZ            R3, 30
     46  ACT            R1
     47  ACT            R3
     48  DIV            R4, R0, R1
     49  MOD            R3, R4, R3
     50  ACT            R3
     51  DIV            R4, R4, R1
     52  INPUT          R5, interactions_left
     53  VLEN           R7, R6
     54  MOD            R3, R4, R1
     55  ADD            R0, R0, R5
     56  ADD            R0, R0, R5
     57  ACT            R3
     58  ADD            R0, R0, R5
     59  JMP            45
     60  MOV            R1, R1
