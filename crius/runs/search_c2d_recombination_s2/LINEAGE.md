LINEAGE READOUT run=search_c2d_recombination_s2 arm=recombination
ANCESTRY of final-population top 66871687158cfab1 (117 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   19.378  19.0  14273      0       0       0          2       0       0   39  seed:ENUMERATE_VM
   18   22.408  22.0  10839      0     100       0          2       0       0   49  replace@30+swap@30,9
   40   20.908  20.5  10815      0     166       0          2       0       0   49  arg@13.0
   65   18.398  18.0  12083      0     412       0          2       0       0   60  const@21+insert@40
   78   27.435  27.0   7684      0     504     168          2       0     168   66  const@23+const@23+delete@53
   94   23.964  23.5   4224      0     190       0          2       0     190   80  duplicate@45+2->13
  109   26.477  26.0   2662      0     190       0          2       0     190   74  delete@30+splice@44<-donor[45:46]:587df7
  132   22.461  22.0   4634      0       0       0          2       0       0   80  delete@39
  162   21.933  21.5   7916      0       0       0          2       0       0   70  delete@22
  189   22.419  22.0   9540      0       0       0          2       0       0   63  delete@13+insert@62+arg@23.1
  214   24.967  24.5   3902      0       0       0          2       0       0   55  replace@34+delete@40+replace@7
  238   21.423  21.0   9132      0       0       0          2       0       0   46  delete@4
  262   24.466  24.0   3969      0       0       0          2       0       0   44  delete@6+swap@26,14+replace@27
  299   21.959  21.5   4830      0       0       0          2       0       0   37  const@1+arg@15.2
  280   23.455  23.0   5235      0       0       0          2       0       0   42  arg@24.0
  282   22.466  22.0   4004      0       0       0          2       0       0   41  delete@23+arg@23.0
  286   24.440  24.0   7088      0       0       0          2       0       0   39  delete@13+delete@6
  289   18.905  18.5  11201      0       0       0          2       0       0   39  replace@9+replace@3
  291   22.459  22.0   4786      0       0       0          2       0       0   37  delete@22+delete@7
  gradient (mean first half -> second half of the lineage): reads 0 -> 0, writes 205 -> 0, invokes 31.3 -> 0.0, blocks 2.0 -> 2.0, wsBytes 70 -> 0, successes 21.6 -> 21.7
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      0      0         --     10.370   19.379
   25   24      0      0         --     13.474   22.970
   50   24      4      1     10.723     15.017   22.950
   75   24     23      2     16.412      1.012   23.950
  100   24     24      1     18.896         --   25.436
  125   24      1      1     19.391     19.133   23.457
  150   24      0      0         --     17.118   21.397
  175   24      0      0         --     16.416   21.439
  200   24      0      0         --     12.808   21.879
  225   24      2      1      0.000     17.399   25.956
  250   24      5      2     11.191     11.228   21.416
  275   24      4      4      5.075     13.556   21.949
  300   24      2      2      9.765     10.575   21.962
  candidates that invoked a block: 415; of those in their iteration's top 8: 41
TOP MECHANISM 66871687158cfab1: fitness 21.959 succ 21.5 inter 4830 reads 0 writes 0 invokes 0 blocks 2 wsBytes 0 invalid 0
  trace: {"ACT": 15918, "INPUT": 100, "WS_ALLOC": 100}
      0  INPUT          R1, num_ops
      1  CONST          R5, 5
      2  BRZ            R3, 18
      3  BLK_LEN        R5, R3
      4  VGET           R7, R5, R2
      5  ACT            R3
      6  MOD            R3, R3, R7
      7  WS_WRITE       R0, R1
      8  WS_APPEND      R5, R4
      9  PREC_BEGIN     
     10  ADD            R4, R3, R3
     11  DIV            R4, R4, R1
     12  MOD            R3, R4, R1
     13  BLK_COPY       R6, R4
     14  BLK_INVOKE     R3
     15  LT             R3, R0, R3
     16  ADD            R0, R0, R5
     17  BRZ            R3, 25
     18  WS_ALLOC       R2, R2
     19  JMP            15
     20  WS_FREE        R7
     21  ACT            R3
     22  SUB            R5, R6, R2
     23  WS_SLEN        R5, R5
     24  ADD            R0, R0, R5
     25  ADD            R0, R0, R5
     26  MOD            R3, R0, R1
     27  ACT            R3
     28  DIV            R4, R0, R1
     29  MOD            R3, R4, R1
     30  ACT            R3
     31  DIV            R4, R4, R1
     32  MOD            R3, R4, R1
     33  ACT            R3
     34  ACT            R1
     35  JMP            25
     36  BLK_REC_END    R5
