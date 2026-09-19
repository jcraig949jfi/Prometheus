LINEAGE READOUT run=search_c2b_recombination_s2 arm=recombination
ANCESTRY of final-population top b655bc7181e19770 (141 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   19.378  19.0  14273      0       0       0          2       0       0   39  seed:ENUMERATE_VM
   19   21.956  21.5   5131      0       0       0          2       0       0   55  replace@30+swap@30,9
   36   20.961  20.5   4614      0       0       0          2       0       0   59  arg@34.0+delete@44+insert@57
   55   20.437  20.0   7408      0       0       0          2       0       0   50  const@15+replace@12
   88   23.456  23.0   5222      0       0       0          2       0       0   46  swap@30,18
  107   22.433  22.0   7938      0       0       0          2       0       0   64  const@19
  128   16.856  16.5  17104      0       0       0          2       0       0   55  arg@31.1+arg@4.2
  147   22.929  22.5   8395      0       0       0          2       0       0   58  insert@42+swap@50,35
  175   20.937  20.5   7400      0       0       0          2       0       0   52  arg@51.0
  198   20.435  20.0   7707      0       0       0          2       0       0   63  delete@49+arg@24.0+insert@30
  222   20.933  20.5   7884      0       0       0          2       0       0   53  replace@10+delete@37
  250   19.909  19.5  10794      0     100       0          2       0       0   54  delete@33+delete@31
  282   23.449  23.0   5954    200     800       0         64       0     200   82  delete@33+duplicate@56+3->14
  287   23.433  23.0   7934    300     800       0         64       0     200   96  delete@95+swap@5,26+splice@78<-donor[3:4
  293   18.370  18.0  15307    300     800       0         64       0     200   96  arg@62.0+replace@39
  294   21.948  21.5   6052    300     800       0         64       0     200   96  arg@28.2
  296   21.903  21.5  11442    300     800       0         64       0     200   95  arg@26.0+delete@16
  297   22.357  22.0  16947    300     800       0         64       0     200   95  swap@25,15
  300   21.960  21.5   4648    300     700       0         64       0     100   95  delete@49+splice@94<-donor[10:11]:e199bd
  gradient (mean first half -> second half of the lineage): reads 0 -> 56, writes 0 -> 186, invokes 0.0 -> 0.0, blocks 2.0 -> 17.7, wsBytes 0 -> 38, successes 21.4 -> 20.7
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      0      0         --     10.370   19.379
   25   24      2      0     12.315     19.693   22.970
   50   24      0      0         --     16.979   23.451
   75   24      2      1     11.029     12.508   21.946
  100   24      4      1     11.290     15.185   22.427
  125   24     12      0     16.953      9.799   24.453
  150   24      4      2      2.857     15.818   18.370
  175   24      0      0         --     15.651   22.940
  200   24      2      0      5.969     13.358   16.896
  225   24      0      0         --     17.863   24.435
  250   24      2      0     17.380     17.123   19.909
  275   24     24      0     15.299         --   19.413
  300   24     23      0     16.545      0.150   21.960
  candidates that invoked a block: 222; of those in their iteration's top 8: 31
TOP MECHANISM b655bc7181e19770: fitness 21.960 succ 21.5 inter 4648 reads 300 writes 700 invokes 0 blocks 64 wsBytes 100 invalid 600
  trace: {"ACT": 16127, "BLK_REC_END": 400, "BLK_NEW": 200, "WS_LINKS": 200, "BLK_COUNT": 100, "INPUT": 100, "WS_LINK": 100}
      0  EQ             R7, R1, R6
      1  INPUT          R1, num_ops
      2  CONST          R5, 1
      3  ADD            R0, R0, R5
      4  JMP            44
      5  ACT            R0
      6  PINVOKE        R0, R3
      7  DIV            R4, R4, R1
      8  VGET           R3, R4, R0
      9  DIV            R2, R4, R7
     10  DIV            R4, R4, R1
     11  MOD            R3, R4, R0
     12  ACT            R3
     13  ADD            R0, R0, R5
     14  ACT            R3
     15  WS_LINKS       R1, R0
     16  BLK_REC_END    R3
     17  ACT            R1
     18  ADD            R0, R0, R5
     19  SUB            R7, R0, R1
     20  MOD            R2, R1, R1
     21  MOD            R3, R4, R1
     22  MOD            R7, R4, R0
     23  BRZ            R3, 81
     24  ACT            R0
     25  DIV            R4, R4, R1
     26  VGET           R5, R3, R7
     27  MUL            R5, R1, R4
     28  WS_REC_NEW     R0
     29  ACT            R0
     30  ACT            R0
     31  VGET           R5, R3, R7
     32  MUL            R5, R1, R7
     33  SUB            R0, R3, R7
     34  MOD            R3, R4, R0
     35  BLK_REC_END    R3
     36  MOD            R3, R7, R5
     37  ACT            R3
     38  BLK_COPY       R2, R3
     39  VGET           R3, R4, R0
     40  WS_SLEN        R3, R7
     41  DIV            R2, R4, R5
     42  BLK_NEW        R6
     43  ACT            R3
     44  MOD            R3, R4, R0
     45  BLK_REC_END    R3
     46  ADD            R0, R0, R5
     47  ACT            R3
     48  BLK_NEW        R6
     49  MOD            R3, R4, R0
     50  BLK_REC_END    R3
     51  BLK_COUNT      R2
     52  ADD            R0, R0, R5
     53  ACT            R3
     54  ADD            R0, R0, R5
     55  ACT            R3
     56  BLK_NEW        R6
     57  WS_LINK        R6, R6, R6
     58  DIV            R4, R0, R1
     59  ACT            R3
     60  WS_LINKS       R2, R2
     61  ACT            R3
     62  WS_LINKS       R3, R2
     63  DIV            R4, R0, R1
     64  MOD            R3, R4, R1
     65  VLEN           R2, R4
     66  MOD            R3, R4, R0
     67  ADD            R0, R0, R5
     68  DIV            R4, R4, R1
     69  BLK_REC_END    R3
     70  ADD            R0, R0, R5
     71  SUB            R7, R0, R1
     72  MOD            R2, R1, R1
     73  MOD            R3, R4, R1
     74  MOD            R3, R4, R0
     75  BLK_REC_END    R3
     76  ADD            R0, R0, R5
     77  ADD            R0, R0, R5
     78  ACT            R3
     79  ADD            R0, R0, R5
     80  ADD            R0, R0, R5
     81  ACT            R1
     82  MOD            R3, R0, R1
     83  ACT            R3
     84  DIV            R4, R0, R1
     85  MOD            R3, R4, R1
     86  ACT            R3
     87  DIV            R4, R4, R1
     88  MOD            R3, R4, R0
     89  ACT            R3
     90  ADD            R0, R0, R5
     91  JMP            81
     92  MOD            R3, R4, R0
     93  VSET           R1, R5, R3
     94  DIV            R4, R4, R1
