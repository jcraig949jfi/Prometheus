LINEAGE READOUT run=search_c2a_seeded_s1 arm=seeded
ANCESTRY of final-population top 8250b21b407b14dd (151 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   17.839  17.5  18871      0       0       0          0       0       0   39  seed:ENUMERATE_VM
   18   24.973  24.5   3148      0       0       0          0       0       0   46  arg@26.2+const@18+delete@46
   39   20.417  20.0   9779      0       0       0          0       0       0   56  duplicate@8+5->33+insert@5+const@23
   59   23.460  23.0   4648      0       0       0          0       0       0   54  swap@12,37+duplicate@51+1->32+swap@22,38
   88   24.415  24.0   9955      0       0       0          0       0       0   52  swap@3,36+const@1
  108   24.978  24.5   2574      0       0       0          0       0       0   46  const@1+delete@1
  131   20.400  20.0  11820      0       0       0          0       0       0   43  arg@26.0
  160   20.443  20.0   6752      0       0       0          0       0       0   40  const@28+delete@7+delete@18
  180   21.442  21.0   6776      0       0       0          0       0       0   48  delete@30
  205   19.412  19.0  10344      0       0       0          0       0       0   47  const@34+delete@25
  229   19.866  19.5  15860      0       0       0          0       0       0   42  arg@4.0
  251   20.401  20.0  11636      0       0       0          0       0       0   40  delete@12+insert@22
  281   24.404  24.0  11354      0       0       0          0       0       0   36  swap@9,3
  283   22.929  22.5   8312      0       0       0          0       0       0   35  const@21
  285   23.924  23.5   8994      0       0       0          0       0       0   35  arg@10.0
  287   21.929  21.5   8374      0       0       0          0       0       0   35  replace@2
  290   21.912  21.5  10360      0       0       0          0       0       0   34  const@21+delete@11
  297   23.971  23.5   3358      0       0       0          0       0       0   33  delete@10
  300   23.419  23.0   9504      0       0       0          0       0       0   33  const@19
  gradient (mean first half -> second half of the lineage): reads 0 -> 681, writes 0 -> 0, invokes 0.0 -> 0.0, blocks 0.0 -> 0.0, wsBytes 0 -> 0, successes 21.5 -> 21.5
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      1      0     17.839     10.092   17.839
   25   24      1      0     19.907     12.508   20.425
   50   24      1      0     21.422     12.916   21.423
   75   24      1      0     12.282     13.981   22.454
  100   24      3      0     10.880     16.950   22.928
  125   24      0      0         --     12.920   21.920
  150   24      1      0     16.814     18.105   23.939
  175   24      2      0     19.919     13.686   21.425
  200   24      0      0         --     13.950   20.875
  225   24      1      0     22.926     14.772   22.939
  250   24      2      0      1.139     14.688   22.936
  275   24      2      0     10.790     15.237   20.425
  300   24      5      0      9.125     17.143   23.419
  candidates that invoked a block: 0; of those in their iteration's top 8: 0
TOP MECHANISM 8250b21b407b14dd: fitness 23.419 succ 23.0 inter 9504 reads 0 writes 0 invokes 0 blocks 0 wsBytes 0 invalid 0
  trace: {"ACT": 28294, "INPUT": 100}
      0  INPUT          R1, num_ops
      1  BRZ            R7, 19
      2  BLK_APPEND     R1, R5
      3  LT             R5, R0, R2
      4  WS_SLEN        R6, R3
      5  WS_APPEND      R5, R4
      6  JMP            10
      7  DIV            R4, R0, R0
      8  BLK_COPY       R3, R1
      9  DIV            R4, R7, R2
     10  WS_REC_NEW     R6
     11  MOD            R4, R0, R5
     12  ADD            R0, R0, R4
     13  ADD            R0, R0, R4
     14  ADD            R0, R0, R5
     15  BRZ            R3, 20
     16  WS_REC_GET     R6, R4, R0
     17  VGET           R4, R6, R6
     18  BLK_REC_END    R6
     19  CONST          R0, 46
     20  VLEN           R5, R7
     21  ADD            R0, R0, R5
     22  MOD            R3, R0, R1
     23  ACT            R3
     24  DIV            R4, R0, R1
     25  MOD            R3, R4, R1
     26  BRZ            R3, 13
     27  ACT            R3
     28  DIV            R4, R4, R1
     29  MOD            R3, R4, R1
     30  ACT            R3
     31  ACT            R1
     32  JMP            21
