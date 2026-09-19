LINEAGE READOUT run=search_c1_recombination_s1 arm=recombination
ANCESTRY of final-population top de08b338928aca30 (174 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   30.366  30.0  23009      0       0       0          0       0       0   39  seed:ENUMERATE_VM
   22   31.327  31.0  29724     50      50       0          0       0      50   60  insert@12
   49   23.292  23.0  35905     50       0       0          0       0       0   54  delete@47+arg@8.0
   75   25.323  25.0  30682     50       0       0          0       0       0   61  delete@12+arg@6.0
   97   33.364  33.0  23202     50      50       0          0       0      50   64  replace@23+replace@25
  115   32.355  32.0  24787      0       0       0          0       0       0   63  swap@11,43+delete@12+const@10
  136   45.431  45.0  11851      0       0       0          0       0       0   63  arg@27.1+arg@50.0
  168   30.316  30.0  31850      0       0       0          0       0       0   63  const@12+const@32+delete@32+splice@21<-d
  197   41.400  41.0  17345      0       0       0          0       0       0   63  delete@1+duplicate@45+1->4+delete@42
  227   31.345  31.0  26867     50       0       0          0       0       0   64  replace@25+replace@3+swap@62,59+splice:n
  246   34.348  34.0  26215      0       0       0          0       0       0   59  swap@3,53
  264   28.329  28.0  29603     50       0       0          0       0       0   62  delete@6
  290   29.342  29.0  27311    100       0       0          0       0       0   62  delete@37
  292   47.450  47.0   8637    100       0       0          0       0       0   61  delete@6+arg@5.0+swap@32,38
  293   33.353  33.0  25366    100       0       0          0       0       0   62  swap@12,19+insert@42
  294   36.353  36.0  25415    100       0       0          0       0       0   59  delete@15+delete@41+delete@31
  298   36.391  36.0  18751    100       0       0          0       0       0   63  delete@21+splice@31<-donor[13:18]:2516e9
  299   38.368  38.0  22741     99       0       0          0       0       0   63  swap@36,35
  300   22.291  22.0  36135    100       0       0          0       0       0   64  replace@6+duplicate@37+1->32
  gradient (mean first half -> second half of the lineage): reads 32 -> 37, writes 9 -> 1, invokes 0.0 -> 0.0, blocks 0.0 -> 0.0, wsBytes 9 -> 1, successes 28.4 -> 30.1
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      0      0         --     17.735   30.366
   25   24     19      0     12.001      9.773   18.247
   50   24      0      0         --     26.293   38.381
   75   24      0      0         --     21.493   26.328
  100   24     14      0     18.879     16.545   28.296
  125   24      1      0     32.320     21.066   36.337
  150   24      1      0      0.112     24.199   34.349
  175   24      0      0         --     25.322   28.356
  200   24      0      0         --     19.924   26.312
  225   24      1      0      2.020     16.439   30.323
  250   24      4      0     18.219     28.012   34.363
  275   24      0      0         --     30.450   38.387
  300   24      1      0      1.109     16.626   22.291
  candidates that invoked a block: 3; of those in their iteration's top 8: 0
TOP MECHANISM de08b338928aca30: fitness 22.291 succ 22.0 inter 36135 reads 100 writes 0 invokes 0 blocks 0 wsBytes 0 invalid 0
  trace: {"ACT": 48184, "INPUT": 150, "BLK_COUNT": 50, "BLK_LEN": 50}
      0  INPUT          R1, num_ops
      1  BRZ            R3, 10
      2  INPUT          R2, task_index
      3  WS_FREE        R0
      4  LT             R0, R0, R0
      5  BLK_INVOKE     R4
      6  INPUT          R4, task_index
      7  WS_SREAD       R2, R2, R2
      8  BRZ            R3, 10
      9  BLK_COUNT      R3
     10  JMP            25
     11  ADD            R0, R0, R5
     12  MUL            R5, R3, R0
     13  ACT            R3
     14  DIV            R4, R0, R1
     15  ACT            R3
     16  INPUT          R7, current_block
     17  MOV            R2, R4
     18  BLK_COUNT      R6
     19  ACT            R1
     20  MOV            R2, R4
     21  JMP            11
     22  INPUT          R5, interactions_left
     23  VLEN           R5, R6
     24  DIV            R4, R0, R1
     25  ACT            R3
     26  INPUT          R5, interactions_left
     27  ADD            R0, R3, R5
     28  BLK_LEN        R0, R0
     29  ADD            R0, R0, R5
     30  MOV            R2, R6
     31  DIV            R4, R0, R1
     32  ADD            R0, R0, R5
     33  MOD            R3, R4, R1
     34  ACT            R3
     35  INPUT          R7, current_block
     36  ADD            R0, R0, R5
     37  MOV            R2, R4
     38  ADD            R0, R0, R5
     39  ADD            R0, R0, R5
     40  BLK_COUNT      R3
     41  ADD            R0, R0, R5
     42  ADD            R0, R0, R5
     43  BRNZ           R1, 52
     44  ACT            R1
     45  INPUT          R5, current
     46  ACT            R3
     47  MOD            R3, R0, R1
     48  ACT            R3
     49  DIV            R4, R0, R1
     50  MOD            R3, R4, R1
     51  ACT            R3
     52  DIV            R4, R4, R1
     53  MOD            R3, R4, R1
     54  ACT            R1
     55  ADD            R0, R0, R5
     56  JMP            46
     57  WS_REC_NEW     R2
     58  WS_READ        R5, R2
     59  BLK_DELETE     R0
     60  INPUT          R3, current
     61  DIV            R4, R4, R5
     62  VSET           R1, R7, R0
     63  MUL            R2, R1, R2
