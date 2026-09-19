LINEAGE READOUT run=search_c1b_seeded_s3 arm=seeded
ANCESTRY of final-population top eed569b9f71c3338 (182 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   23.441  23.0   6922      0       0       0          0       0       0   39  seed:ENUMERATE_VM
   24   17.427  17.0   3630      0       3       0          0       0       0   43  delete@40+arg@30.0+delete@32
   53   22.411  22.0   3819      0       4       0          0       0       0   38  arg@2.1+insert@36
   87   11.330  11.0   5196      9       9       0          0       0       0   32  swap@19,2+const@2
  114   18.397  18.0   3885      5       5       0          0       0       0   30  delete@3
  133   16.401  16.0   3385     20      35       0          0       0       2   39  arg@33.0+duplicate@12+5->16+swap@26,16
  154   10.301  10.0   5051      0       0       0          0       0       0   54  arg@35.2+replace@53
  175   16.415  16.0  10084      0       0       0          0       0       0   58  duplicate@48+4->31+const@2+arg@28.1
  194   20.471  20.0   3457     50       0       0          0       0       0   54  arg@28.2
  214   19.394  19.0  12514      0       0       0          0       0       0   42  delete@14
  234   12.344  12.0  18394      0       0       0          0       0       0   33  delete@22
  259   11.280  11.0  26005      0       0       0          0       0       0   21  arg@13.1+delete@12
  291   16.392  16.0  12762     50       0       0          0       0       0   19  delete@18
  287   12.279  12.0  26113     50       0       0          0       0       0   21  duplicate@5+1->2+insert@17+insert@1
  288   17.380  17.0  14141     50       0       0          0       0       0   20  delete@17
  290   24.476  24.0   2865     50       0       0          0       0       0   20  swap@2,0+swap@16,19
  292   14.380  14.0  14233     50       0       0          0       0       0   18  delete@16+swap@0,1
  298   10.267  10.0  27537    100      50       0          0       0       0   22  duplicate@13+4->2+const@1+arg@2.1
  gradient (mean first half -> second half of the lineage): reads 6 -> 14, writes 14 -> 3, invokes 0.0 -> 0.0, blocks 0.0 -> 0.0, wsBytes 0 -> 0, successes 16.4 -> 16.5
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      0      0         --     16.485   23.441
   25   24      0      0         --      7.091   12.334
   50   24      0      0         --     11.693   18.413
   75   24      0      0         --      5.556   12.292
  100   24      1      0      0.163     11.231   19.444
  125   24      1      0     10.284      6.269   11.283
  150   24     12      0     13.857      7.679   15.379
  175   24     19      0     15.558      9.910   16.415
  200   24      0      0         --     12.746   17.411
  225   24      1      0     11.286      7.284   11.292
  250   24      1      0     13.333     11.818   23.475
  275   24      1      0      3.147      5.790   20.407
  300   24      0      0         --      2.888    6.249
  candidates that invoked a block: 2; of those in their iteration's top 8: 0
TOP MECHANISM eed569b9f71c3338: fitness 10.267 succ 10.0 inter 27537 reads 100 writes 50 invokes 0 blocks 0 wsBytes 0 invalid 0
  trace: {"ACT": 41314, "BLK_COMPOSE": 50, "BLK_DELETE": 50, "INPUT": 50, "WS_LINKS": 50, "WS_LINK_GET": 50}
      0  WS_LINK_GET    R4, R3, R0
      1  CONST          R5, 1
      2  BLK_COMPOSE    R2, R2, R1
      3  BRNZ           R0, 2
      4  WS_LINKS       R4, R6
      5  BLK_DELETE     R0
      6  INPUT          R1, num_ops
      7  ACT            R3
      8  ADD            R0, R4, R5
      9  ACT            R1
     10  MOD            R3, R0, R1
     11  ACT            R3
     12  DIV            R4, R0, R1
     13  MOD            R3, R4, R1
     14  ACT            R3
     15  ADD            R0, R0, R5
     16  JMP            9
     17  BLK_COMPOSE    R2, R1, R1
     18  BRNZ           R0, 6
     19  WS_LINKS       R4, R6
     20  BLK_DELETE     R0
     21  BLK_PATCH      R7, R2, R4
