LINEAGE READOUT run=search_c2c_recombination_s1 arm=recombination
ANCESTRY of final-population top 0fcce4e9606f75c4 (136 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   17.839  17.5  18871      0       0       0          2       0       0   39  seed:ENUMERATE_VM
   24   23.938  23.5   7270      0     100       0          2       0     200   50  delete@23
   52   21.411  21.0  10556      0     100       0          2       0     200   43  const@10+delete@9+arg@8.2
   73   21.462  21.0   4436    100     100       0          2       0     200   58  replace@13+arg@32.0
  109   17.376  17.0  14675    100       0       0          2       0       0   74  swap@39,50+duplicate@58+4->6+delete@19
  139   20.931  20.5   8073    300     100       0          2       0       2   80  delete@7+arg@6.0+const@34+splice@73<-don
  163   20.899  20.5  11884    300       0       0          2       0       0   83  const@51
  187   19.338  19.0  19194    200       0       0          2       0       0   75  replace@18+delete@27+arg@39.0
  209   21.942  21.5   6867    100       0       0          2       0       0   72  const@14
  229   22.422  22.0   9178    200     100       0          2       0     200   83  replace@79+arg@5.0+const@50+splice@30<-d
  246   17.888  17.5  13222    100     100     100          2       0     200   83  replace@66+delete@64
  274   24.438  24.0   7344      0       0       0          2       0       0   85  delete@37
  293   19.890  19.5  13030      0       0       0          2       0       0   87  replace@9+arg@61.1+replace@34
  291   20.412  20.0  10444      0       0       0          2       0       0   87  delete@17+insert@39+delete@23
  294   23.948  23.5   6084      0       0       0          2       0       0   87  swap@68,19+arg@56.0+arg@64.0
  295   22.960  22.5   4710      0       0       0          2       0       0   86  replace@62+delete@69
  297   21.966  21.5   3968      0       0       0          2       0       0   85  swap@74,85+delete@62
  299   24.443  24.0   6664      0       0       0          2       0       0   84  delete@67
  gradient (mean first half -> second half of the lineage): reads 121 -> 114, writes 65 -> 25, invokes 0.0 -> 7.2, blocks 2.0 -> 2.0, wsBytes 83 -> 49, successes 20.8 -> 21.3
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      1      0      9.268      7.407   17.839
   25   24     24      0     10.347         --   20.409
   50   24     23      0     12.989     18.892   20.921
   75   24     23      0     12.427     18.888   22.451
  100   24      0      0         --     15.524   23.931
  125   24     12      0     21.427     21.167   23.900
  150   24     23      0     17.856      0.000   23.448
  175   24      1      0     19.943     16.849   21.449
  200   24      2      0      2.593     17.578   21.398
  225   24      7      0     17.413     15.347   25.442
  250   24     24      2     14.779         --   21.915
  275   24      3      1      4.501     17.335   20.930
  300   24      1      0      0.510     16.607   21.939
  candidates that invoked a block: 48; of those in their iteration's top 8: 6
TOP MECHANISM 0fcce4e9606f75c4: fitness 24.443 succ 24.0 inter 6664 reads 0 writes 0 invokes 0 blocks 2 wsBytes 0 invalid 0
  trace: {"ACT": 21171, "INPUT": 100}
      0  MOD            R5, R0, R6
      1  INPUT          R1, num_ops
      2  CONST          R5, 10
      3  ADD            R0, R0, R5
      4  ADD            R0, R0, R5
      5  DIV            R4, R0, R1
      6  MOD            R3, R0, R1
      7  JMP            72
      8  MOD            R3, R4, R3
      9  VGET           R1, R5, R7
     10  WS_WRITE       R1, R0
     11  VSET           R4, R4, R0
     12  LT             R3, R0, R2
     13  BLK_DELETE     R5
     14  MOD            R6, R1, R2
     15  CONST          R0, 4
     16  WS_REC_NEW     R7
     17  WS_LINK_GET    R2, R3, R3
     18  CONST          R0, 3
     19  ADD            R0, R0, R5
     20  MOD            R3, R4, R1
     21  ACT            R2
     22  WS_SLEN        R7, R4
     23  MOD            R2, R4, R1
     24  MUL            R2, R2, R7
     25  LT             R6, R6, R6
     26  EQ             R3, R6, R1
     27  ADD            R0, R0, R5
     28  WS_WRITE       R1, R0
     29  VSET           R4, R4, R0
     30  LT             R3, R0, R2
     31  BRZ            R5, 54
     32  DIV            R4, R1, R1
     33  ACT            R3
     34  BLK_COMPOSE    R7, R2, R5
     35  MOD            R3, R4, R1
     36  BRNZ           R2, 21
     37  CONST          R1, 1
     38  WS_SLEN        R3, R3
     39  BLK_DELETE     R7
     40  CONST          R5, 10
     41  DIV            R1, R2, R1
     42  ADD            R0, R0, R5
     43  WS_WRITE       R1, R6
     44  LT             R3, R0, R2
     45  INPUT          R1, num_ops
     46  ADD            R0, R0, R5
     47  CONST          R1, -1
     48  MOV            R1, R0
     49  BRZ            R7, 71
     50  LT             R3, R0, R4
     51  JMP            47
     52  LT             R7, R0, R2
     53  CONST          R7, 3
     54  ADD            R0, R0, R5
     55  MOV            R4, R5
     56  BLK_INVOKE     R4
     57  BRZ            R5, 57
     58  BLK_DELETE     R5
     59  MOD            R6, R1, R2
     60  INPUT          R1, num_ops
     61  CONST          R5, 19
     62  CONST          R0, 3
     63  ADD            R2, R0, R5
     64  WS_FIND        R4, R5
     65  CONST          R0, 4
     66  WS_LINK        R3, R3, R1
     67  DIV            R4, R0, R1
     68  MOD            R3, R0, R1
     69  ACT            R3
     70  ACT            R1
     71  MOD            R3, R4, R1
     72  ACT            R3
     73  DIV            R4, R4, R1
     74  MOD            R3, R4, R1
     75  ACT            R3
     76  ADD            R0, R0, R5
     77  JMP            67
     78  ADD            R4, R7, R3
     79  WS_LINK_GET    R2, R3, R3
     80  SUB            R4, R0, R3
     81  BLK_COPY       R3, R2
     82  BRZ            R2, 54
     83  ACT            R3
