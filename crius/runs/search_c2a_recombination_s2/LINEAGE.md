LINEAGE READOUT run=search_c2a_recombination_s2 arm=recombination
ANCESTRY of final-population top 1e77e4c386f01d87 (171 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   19.378  19.0  14273      0       0       0          0       0       0   39  seed:ENUMERATE_VM
   25   23.472  23.0   3284      0     200       0          0       0       0   76  delete@6+const@46
   48   25.465  25.0   4157      0       0     100          0       0       0   87  const@70+swap@28,26
   72   21.404  21.0  11376      0     100     100          0       0       0   85  delete@36+swap@63,49+swap@60,61
   91   20.930  20.5   8224      0     100       0          0       0       0   96  replace@26+splice:none:76061e4e198f6aba
  110   23.957  23.5   5055      0       0       0          0       0       0   89  swap@50,66
  139   21.953  21.5   5511      0       0       0          0       0       0   87  arg@73.2+delete@88+delete@23
  167   18.913  18.5  10321      0       0       0          0       0       0   89  delete@24+delete@6+replace@18
  196   19.861  19.5  16552      0       0       0          0       0       0   93  delete@61+insert@38
  216   22.411  22.0  10558      0       0       0          0       0       0   87  delete@44+arg@57.0+const@12
  241   21.403  21.0  11509      0       0       0          0       0       0   80  const@58+delete@70+replace@56
  269   20.906  20.5  11134      0       0       0          0       0       0   70  delete@15+const@56
  296   21.910  21.5  10655      0       0       0          0       0       0   74  arg@15.0+swap@34,48+arg@60.2
  293   18.874  18.5  14946      0       0       0          0       0       0   75  delete@37+const@51+replace@39
  294   26.448  26.0   6138      0       0       0          0       0       0   74  delete@35+swap@31,36
  297   21.871  21.5  15340      0       0       0          0       0       0   74  replace@37+const@57
  298   22.442  22.0   6840      0       0       0          0       0       0   79  insert@29+splice@48<-donor[63:67]:eb9bab
  300   21.963  21.5   4340      0       0       0          0       0       0   84  swap@47,56+delete@65+insert@17+splice@39
  gradient (mean first half -> second half of the lineage): reads 0 -> 0, writes 60 -> 0, invokes 29.1 -> 0.0, blocks 0.0 -> 0.0, wsBytes 0 -> 0, successes 20.9 -> 21.4
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      0      0         --     10.370   19.379
   25   24      1      0     23.471     16.295   23.472
   50   24      0      0         --     18.341   23.451
   75   24      0      0         --     18.865   22.946
  100   24      1      0     21.926     17.554   22.427
  125   24      0      0         --     18.605   21.918
  150   24      0      0         --     11.788   18.370
  175   24      0      0         --     17.840   22.940
  200   24      0      0         --     12.436   16.886
  225   24      0      0         --     19.360   24.941
  250   24      1      0      0.162     15.201   21.914
  275   24      0      0         --     17.396   20.411
  300   24      8      0     14.297     16.707   21.963
  candidates that invoked a block: 14; of those in their iteration's top 8: 0
TOP MECHANISM 1e77e4c386f01d87: fitness 21.963 succ 21.5 inter 4340 reads 0 writes 0 invokes 0 blocks 0 wsBytes 0 invalid 0
  trace: {"ACT": 15006, "INPUT": 100}
      0  INPUT          R1, num_ops
      1  CONST          R5, 1
      2  BRZ            R2, 68
      3  ACTI           -17
      4  NOT            R1, R5
      5  CONST          R0, 1
      6  CONST          R4, 21
      7  BLK_COMPOSE    R2, R7, R5
      8  MOV            R4, R1
      9  ACT            R6
     10  BLK_LEN        R0, R1
     11  MUL            R0, R2, R3
     12  VSET           R6, R6, R5
     13  BLK_PATCH      R7, R6, R6
     14  BLK_APPEND     R6, R6
     15  ADD            R4, R0, R5
     16  BLK_INVOKE     R5
     17  WS_ALLOC       R2, R3
     18  ACT            R3
     19  DIV            R1, R6, R3
     20  BRNZ           R7, 26
     21  BLK_COPY       R1, R3
     22  BLK_COPY       R0, R0
     23  ADD            R2, R2, R4
     24  MOD            R3, R0, R1
     25  BLK_PATCH      R6, R7, R1
     26  ACT            R3
     27  MOV            R4, R1
     28  ACT            R6
     29  WS_FREE        R0
     30  VGET           R3, R2, R3
     31  LT             R3, R7, R2
     32  BLK_DELETE     R7
     33  DIV            R4, R0, R1
     34  INPUT          R0, current_block
     35  BRNZ           R1, 60
     36  CONST          R0, -6
     37  WS_FIND        R1, R2
     38  BLK_LEN        R6, R1
     39  ADD            R4, R0, R5
     40  BLK_INVOKE     R5
     41  ACT            R3
     42  DIV            R1, R6, R3
     43  BRNZ           R7, 25
     44  WS_LINKS       R5, R0
     45  WS_REC_NEW     R2
     46  WS_LINK        R4, R4, R7
     47  MUL            R1, R1, R1
     48  BRNZ           R3, 5
     49  WS_FIND        R3, R0
     50  ACT            R6
     51  ACT            R1
     52  ADD            R0, R0, R5
     53  JMP            66
     54  ACT            R3
     55  DIV            R4, R0, R1
     56  MOD            R3, R4, R1
     57  ACT            R3
     58  ACT            R0
     59  MUL            R2, R1, R1
     60  ACTI           -12
     61  ACTI           -23
     62  CONST          R0, -3
     63  JMP            68
     64  HALT           
     65  BLK_NEW        R3
     66  ACT            R1
     67  ADD            R0, R0, R5
     68  CONST          R0, 24
     69  ADD            R0, R0, R5
     70  ADD            R0, R0, R5
     71  ACT            R1
     72  MOD            R3, R0, R1
     73  ACT            R3
     74  DIV            R4, R0, R1
     75  MOD            R3, R4, R1
     76  ACT            R3
     77  DIV            R4, R4, R1
     78  ACT            R4
     79  ADD            R0, R0, R5
     80  JMP            71
     81  WS_FIND        R3, R0
     82  ACT            R6
     83  ADD            R0, R0, R5
