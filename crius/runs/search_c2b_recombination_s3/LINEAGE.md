LINEAGE READOUT run=search_c2b_recombination_s3 arm=recombination
ANCESTRY of final-population top fb5a6561255806ec (125 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   20.422  20.0   9124      0       0       0          2       0       0   39  seed:ENUMERATE_VM
   23   26.464  26.0   4154      0       0       0          2       0       0   41  const@25
   43   20.362  20.0  16222      0       0       0          2       0       0   43  replace@4+replace@19+delete@4
   57   21.962  21.5   4442      0       0       0          2       0       0   42  const@21
   76   17.352  17.0  17475      0       0       0          2       0       0   32  delete@10
  102   20.374  20.0  14948      0       0       0          2       0       0   27  duplicate@25+1->14
  152   21.924  21.5   8950    100     100       0          2       0       0   38  delete@8+delete@7+duplicate@4+6->9
  173   26.974  26.5   2980      0     100       0          2       0       0   59  delete@45
  195   19.893  19.5  12609      0       0       0          2       0       0   62  const@2
  218   26.950  26.5   5922    100       0       0          2       0       0   62  delete@6
  240   25.952  25.5   5614      0       0       0          2       0       0   70  delete@47
  263   19.920  19.5   9468      0       0       0          2       0       0   71  replace@40
  283   22.430  22.0   8233      0       0       0          2       0       0   58  arg@10.0+delete@4
  288   19.916  19.5   9934      0       0       0          2       0       0   58  replace@23
  290   23.945  23.5   6448      0       0       0          2       0       0   58  arg@35.2
  291   22.932  22.5   7994      0       0       0          2       0       0   57  delete@10
  295   17.843  17.5  18531      0       0       0          2       0       0   56  delete@5
  300   24.440  24.0   7114    200       0       0          2       0       0   63  arg@4.0+insert@38+duplicate@25+6->2
  gradient (mean first half -> second half of the lineage): reads 11 -> 11, writes 17 -> 24, invokes 0.0 -> 0.0, blocks 2.0 -> 2.0, wsBytes 0 -> 0, successes 21.3 -> 22.3
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      0      0         --     10.889   21.923
   25   24      3      1     26.799     14.846   27.462
   50   24      1      0     19.908     12.553   19.908
   75   24      1      0     19.888      6.927   19.890
  100   24      3      0      7.926      7.521   22.969
  125   24      7      0      7.586      9.383   21.910
  150   24     14      0     13.112      6.973   22.890
  175   24      4      0     13.537     17.970   24.957
  200   24      0      0         --     12.841   19.388
  225   24      3      0     20.397     18.736   24.960
  250   24      1      0      0.139     15.022   24.428
  275   24      4      1     11.521     16.475   22.459
  300   24      1      0      0.671     15.355   24.440
  candidates that invoked a block: 29; of those in their iteration's top 8: 3
TOP MECHANISM fb5a6561255806ec: fitness 24.440 succ 24.0 inter 7114 reads 200 writes 0 invokes 0 blocks 2 wsBytes 0 invalid 100
  trace: {"ACT": 22557, "BLK_COUNT": 100, "INPUT": 100, "WS_LINKS": 100}
      0  LT             R7, R0, R2
      1  INPUT          R1, num_ops
      2  WS_LINKS       R2, R3
      3  MUL            R2, R1, R1
      4  LT             R7, R0, R2
      5  CONST          R5, 1
      6  BLK_COUNT      R3
      7  MOD            R3, R0, R1
      8  CONST          R5, -1
      9  CONST          R0, -18
     10  BRNZ           R0, 20
     11  MOD            R3, R0, R1
     12  BLK_REC_BEGIN  
     13  MOD            R3, R0, R1
     14  ACT            R6
     15  JMP            23
     16  MOD            R3, R0, R1
     17  ACT            R3
     18  WS_READ        R3, R3
     19  WS_LINK_GET    R6, R6, R5
     20  MUL            R0, R1, R1
     21  VGET           R3, R2, R3
     22  ADD            R0, R0, R5
     23  BRZ            R6, 55
     24  WS_REC_SET     R3, R3, R1
     25  MUL            R2, R1, R4
     26  VGET           R3, R2, R3
     27  BLK_COPY       R3, R7
     28  WS_WRITE       R1, R6
     29  LT             R7, R0, R2
     30  BRNZ           R0, 20
     31  WS_LINKS       R2, R3
     32  MUL            R2, R1, R1
     33  LT             R7, R0, R2
     34  CONST          R5, 1
     35  BLK_COUNT      R3
     36  MOD            R3, R0, R1
     37  DIV            R4, R0, R1
     38  LT             R7, R0, R2
     39  VSET           R1, R0, R2
     40  ADD            R2, R5, R0
     41  BLK_NEW        R3
     42  MUL            R2, R1, R1
     43  WS_WRITE       R5, R7
     44  WS_LINKS       R6, R5
     45  WS_SLEN        R1, R3
     46  JMP            47
     47  ACT            R1
     48  MOD            R3, R0, R1
     49  ACT            R3
     50  DIV            R4, R0, R1
     51  MOD            R3, R4, R1
     52  ACT            R3
     53  DIV            R4, R4, R1
     54  MOD            R3, R4, R3
     55  ACT            R3
     56  ADD            R0, R0, R5
     57  JMP            47
     58  VGET           R3, R2, R3
     59  ACT            R1
     60  MOD            R3, R0, R1
     61  DIV            R4, R0, R1
     62  BLK_REC_END    R7
