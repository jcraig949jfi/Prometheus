LINEAGE READOUT run=search_c2d_recombination_s1 arm=recombination
ANCESTRY of final-population top 6f29e1bb9d20323a (128 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   17.839  17.5  18871      0       0       0          2       0       0   39  seed:ENUMERATE_VM
   25   19.907  19.5  10950      0       0       0          2       0       0   44  const@2+delete@3+const@26
   47   21.913  21.5  10284      0       0       0          2       0       0   53  swap@18,7+swap@2,29+delete@40
   67   17.864  17.5  16128      0       0       0          2       0       0   49  replace@18+duplicate@13+2->8+arg@28.0
   93   22.432  22.0   8028      0       0       0          2       0       0   61  duplicate@16+4->29
  119   21.874  21.5  14898      0       0       0          2       0       0   56  replace@29+delete@39
  134   19.438  19.0   7269      0       0       0          2       0       0   62  arg@31.0
  168   21.437  21.0   7470      0       0       0          2       0       0   57  delete@34
  193   21.438  21.0   7294      0       0       0          2       0       0   55  arg@40.0
  218   20.424  20.0   8964      0       0       0          2       0       0   67  const@29+arg@42.0
  250   22.929  22.5   8426      0       0       0          2       0       0   65  arg@11.0+swap@3,45
  269   24.421  24.0   9280      0       0       0          2       0       0   62  const@23+const@31+insert@30
  284   13.816  13.5  21823      0       0       0          2       0       0   61  replace@6
  291   19.398  19.0  12106      0       0       0          2       0       0   57  delete@29+const@22
  293   18.895  18.5  12392      0       0       0          2       0       0   57  const@31
  294   25.431  25.0   8141      0       0       0          2       0       0   58  swap@30,19+insert@10
  296   24.944  24.5   6594      0       0       0          2       0       0   57  const@32+delete@35
  299   21.932  21.5   8035      0       0       0          2       0       0   57  replace@15+arg@12.1+const@23
  300   21.407  21.0  10936      0       0       0          2       0       0   57  replace@6
  gradient (mean first half -> second half of the lineage): reads 2 -> 0, writes 0 -> 0, invokes 0.0 -> 0.0, blocks 2.0 -> 2.0, wsBytes 0 -> 0, successes 21.1 -> 21.2
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      1      0      9.268      7.407   17.839
   25   24      1      0      0.661     12.550   19.907
   50   24      2      0     10.785     14.548   21.422
   75   24      3      0      7.520     16.505   21.930
  100   24      8      0      9.445     14.940   22.927
  125   24      5      0     13.807     16.249   24.936
  150   24      0      0         --     19.902   24.437
  175   24      1      0      0.149     17.462   20.921
  200   24      2      0      2.166     15.253   19.378
  225   24      4      0     10.766     18.716   23.426
  250   24      3      0     11.611     15.543   23.429
  275   24      4      2      7.448     14.158   19.920
  300   24      7      4      6.090     15.951   21.407
  candidates that invoked a block: 83; of those in their iteration's top 8: 10
TOP MECHANISM 6f29e1bb9d20323a: fitness 21.407 succ 21.0 inter 10936 reads 0 writes 0 invokes 0 blocks 2 wsBytes 0 invalid 0
  trace: {"ACT": 32222, "INPUT": 100}
      0  INPUT          R1, num_ops
      1  CONST          R5, 1
      2  JMP            19
      3  WS_REC_NEW     R3
      4  WS_FREE        R7
      5  WS_SREAD       R0, R7, R7
      6  BLK_REC_BEGIN  
      7  INPUT          R5, last_action
      8  INPUT          R2, num_ops
      9  WS_LINK_GET    R3, R1, R6
     10  MOV            R0, R7
     11  ACT            R3
     12  BLK_STATE_GET  R0, R2, R7
     13  ACT            R1
     14  BLK_INVOKE     R6
     15  BRZ            R0, 0
     16  WS_REC_SET     R6, R7, R6
     17  ACT            R1
     18  WS_WRITE       R0, R2
     19  BRZ            R3, 32
     20  WS_WRITE       R7, R7
     21  VSET           R1, R7, R3
     22  WS_REC_NEW     R1
     23  CONST          R4, -4
     24  BLK_STATE_GET  R0, R0, R6
     25  ADD            R0, R0, R5
     26  JMP            46
     27  WS_FREE        R5
     28  BLK_STATE_GET  R0, R6, R7
     29  DIV            R3, R0, R1
     30  BLK_INVOKE     R3
     31  ACT            R1
     32  CONST          R0, 42
     33  BRZ            R3, 46
     34  ACT            R1
     35  MUL            R2, R2, R3
     36  JMP            41
     37  BLK_COMPOSE    R6, R0, R6
     38  ACT            R6
     39  BRZ            R3, 32
     40  DIV            R7, R0, R1
     41  ACT            R1
     42  BLK_INVOKE     R6
     43  WS_FREE        R5
     44  MUL            R2, R1, R5
     45  MUL            R2, R2, R1
     46  ACT            R1
     47  MOD            R3, R0, R1
     48  ACT            R3
     49  DIV            R4, R0, R1
     50  MOD            R3, R4, R1
     51  ACT            R3
     52  DIV            R4, R4, R1
     53  MOD            R3, R4, R1
     54  ACT            R3
     55  ADD            R0, R0, R5
     56  JMP            46
