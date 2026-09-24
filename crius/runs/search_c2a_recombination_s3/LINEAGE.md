LINEAGE READOUT run=search_c2a_recombination_s3 arm=recombination
ANCESTRY of final-population top cf94c8c3142ac028 (152 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   20.422  20.0   9124      0       0       0          0       0       0   39  seed:ENUMERATE_VM
   22   19.876  19.5  14634      0       0       0          0       0       0   73  arg@11.0
   45   20.450  20.0   5803      0       0       0          0       0       0   72  delete@18
   67   20.917  20.5   9724      0     100       0          0       0       0   81  arg@23.1+swap@18,12+delete@59+splice@27<
   86   22.944  22.5   6544      0       0       0          0       0       0   87  delete@69+replace@20+arg@64.1
  106   18.399  18.0  11984      0       0       0          0       0       0   79  delete@44+delete@47
  122   31.468  31.0   3725      0       0       0          0       0       0   73  arg@39.0+swap@38,41
  142   20.388  20.0  13228      0       0       0          0       0       0   65  delete@52+delete@50
  168   24.437  24.0   7403      0       0       0          0       0       0   59  delete@23
  193   17.859  17.5  16685      0       0       0          0       0       0   58  replace@11
  215   24.950  24.5   5895      0       0       0          0       0       0   46  swap@18,10
  245   23.933  23.5   7949      0       0       0          0       0       0   35  delete@15+delete@20
  273   21.959  21.5   4802      0       0       0          0       0       0   31  arg@5.0+const@5
  280   22.463  22.0   4336      0       0       0          0       0       0   29  delete@7
  282   17.905  17.5  11208      0       0       0          0       0       0   29  replace@12+replace@8
  287   23.454  23.0   5432      0       0       0          0       0       0   28  arg@9.1+delete@12+replace@3
  292   22.387  22.0  13360      0       0       0          0       0       0   28  replace@8+replace@4
  293   23.953  23.5   5588      0       0       0          0       0       0   27  delete@10
  299   20.924  20.5   8996      0       0       0          0       0       0   28  insert@13+const@1
  gradient (mean first half -> second half of the lineage): reads 0 -> 3, writes 25 -> 0, invokes 0.0 -> 0.0, blocks 0.0 -> 0.0, wsBytes 0 -> 0, successes 21.2 -> 21.3
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      0      0         --     10.889   21.923
   25   24      1      0      0.163     20.384   27.462
   50   24      0      0         --     12.408   20.923
   75   24      1      0     20.393     16.936   20.395
  100   24      1      0      1.020     12.636   21.963
  125   24      1      0     18.909     11.514   18.909
  150   24      4      0     10.481     16.350   22.892
  175   24      1      0     22.964     14.652   22.964
  200   24      4      0      5.570     16.258   20.905
  225   24      2      0      1.832     14.696   22.945
  250   24      1      0      0.123      9.641   21.935
  275   24     10      0     12.282     15.167   22.458
  300   24      3      0     10.031     14.202   23.961
  candidates that invoked a block: 0; of those in their iteration's top 8: 0
TOP MECHANISM cf94c8c3142ac028: fitness 20.924 succ 20.5 inter 8996 reads 0 writes 0 invokes 0 blocks 0 wsBytes 0 invalid 0
  trace: {"ACT": 26969, "INPUT": 100}
      0  INPUT          R1, num_ops
      1  CONST          R5, -1
      2  JMP            14
      3  MOD            R6, R6, R7
      4  WS_WRITE       R1, R5
      5  BLK_DELETE     R5
      6  MUL            R2, R6, R0
      7  EQ             R4, R6, R3
      8  WS_APPEND      R6, R2
      9  WS_LINKS       R0, R1
     10  JMP            10
     11  WS_REC_NEW     R5
     12  NOT            R0, R4
     13  SUB            R5, R3, R1
     14  CONST          R0, 21
     15  BRZ            R3, 27
     16  BLK_INVOKE     R2
     17  ADD            R0, R0, R5
     18  ACT            R1
     19  MOD            R3, R0, R1
     20  ACT            R3
     21  DIV            R4, R0, R1
     22  MOD            R3, R4, R1
     23  ACT            R3
     24  DIV            R4, R4, R1
     25  MOD            R3, R4, R1
     26  ACT            R3
     27  JMP            17
