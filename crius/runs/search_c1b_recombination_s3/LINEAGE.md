LINEAGE READOUT run=search_c1b_recombination_s3 arm=recombination
ANCESTRY of final-population top 05932a87aec14f1b (171 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   23.441  23.0   6922      0       0       0          0       0       0   39  seed:ENUMERATE_VM
   37   15.356  15.0   6373     50       0       0          0       0       0   43  replace@6+const@2+arg@3.1
   59   20.433  20.0   4526      0       0       0          0       0       0   54  replace@24+arg@7.1+insert@38
   81   24.460  24.0   2980      0       0       0          0       0       0   50  const@6
  113   23.436  23.0   7669      0       0       0          0       0       0   56  duplicate@13+1->14+delete@12+const@6
  142   17.408  17.0  11020      0       0       0          0       0       0   63  arg@15.1
  164   15.342  15.0  18622     50      50       0          0       0       0   59  arg@11.0+delete@46+delete@23
  193   27.482  27.0   2103      0       0       0          0       0       0   54  const@38
  216   13.328  13.0  20350      0       0       0          0       0       0   64  delete@11+replace@6+duplicate@42+1->34
  236    8.280   8.0  25986      0       0       0          0       0       0   56  delete@32
  259   11.279  11.0  26159    150     150       0          0       0       0   64  swap@6,28+arg@31.0
  277    6.244   6.0  30279    150     100       0          0       0       0   59  insert@56+insert@28
  295   17.393  17.0  12667     50     150       0          0       0       0   64  delete@43+duplicate@48+1->27+swap@25,28
  292   14.378  14.0  14381     50     100       0          0       0       0   59  arg@10.1
  294   21.427  21.0   8672     50     150       0          0       0       0   64  swap@4,7+duplicate@22+2->11+splice@35<-d
  296   11.293  11.0  24446     50     150       0          0       0       0   63  replace@45+delete@33
  299   17.385  17.0  13630     50     150       0          0       0       0   62  delete@37
  300    7.213   7.0  33969     50     150       0          0       0       0   62  arg@18.2+arg@49.0
  gradient (mean first half -> second half of the lineage): reads 13 -> 61, writes 5 -> 52, invokes 0.0 -> 1.7, blocks 0.0 -> 0.0, wsBytes 0 -> 0, successes 17.3 -> 17.3
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      0      0         --     11.243   24.450
   25   24      0      0         --      6.821   12.327
   50   24      0      0         --      8.223   19.413
   75   24      0      0         --      6.127   10.302
  100   24      0      0         --     16.880   22.470
  125   24      0      0         --      8.914   23.456
  150   24      0      0         --     10.781   15.367
  175   24      0      0         --     12.406   16.411
  200   24      0      0         --     12.407   17.411
  225   24      1      0      1.164      8.885   10.296
  250   24      2      0     11.802     14.947   23.475
  275   24      0      0         --     13.939   21.409
  300   24      1      0      6.249      4.913    7.213
  candidates that invoked a block: 0; of those in their iteration's top 8: 0
TOP MECHANISM 05932a87aec14f1b: fitness 7.213 succ 7.0 inter 33969 reads 50 writes 150 invokes 0 blocks 0 wsBytes 0 invalid 16953
  trace: {"ACT": 50933, "WS_REC_NEW": 150, "BLK_STATE_GET": 50, "INPUT": 50}
      0  CONST          R2, -5
      1  CONST          R5, 1
      2  INPUT          R1, num_ops
      3  ADD            R0, R4, R5
      4  BLK_STATE_GET  R4, R6, R4
      5  BRZ            R0, 31
      6  WS_REC_NEW     R0
      7  MOD            R3, R4, R1
      8  MOD            R3, R4, R1
      9  WS_REC_NEW     R0
     10  BRNZ           R3, 19
     11  ADD            R0, R1, R5
     12  WS_REC_NEW     R0
     13  BRZ            R3, 49
     14  JMP            20
     15  BLK_STATE_GET  R7, R1, R1
     16  BLK_COUNT      R1
     17  ADD            R0, R0, R1
     18  WS_REC_GET     R1, R1, R1
     19  CONST          R2, -13
     20  MOD            R3, R5, R1
     21  WS_REC_NEW     R6
     22  ADD            R0, R1, R5
     23  WS_READ        R6, R3
     24  ADD            R0, R1, R5
     25  ACT            R0
     26  MUL            R6, R1, R3
     27  ACT            R5
     28  WS_REC_NEW     R0
     29  ACT            R7
     30  VGET           R1, R1, R2
     31  BRNZ           R0, 23
     32  BRZ            R3, 19
     33  MOD            R3, R4, R1
     34  BLK_COPY       R0, R5
     35  ACT            R7
     36  VGET           R1, R1, R2
     37  BLK_STATE_GET  R7, R1, R1
     38  CONST          R1, 14
     39  BLK_REC_BEGIN  
     40  ACT            R3
     41  BRZ            R3, 9
     42  MOD            R3, R0, R1
     43  WS_APPEND      R3, R4
     44  WS_LINKS       R0, R7
     45  MOD            R3, R0, R1
     46  VGET           R1, R1, R2
     47  ACT            R5
     48  ADD            R2, R7, R6
     49  ACT            R0
     50  MOD            R3, R0, R1
     51  DIV            R4, R0, R1
     52  ACT            R3
     53  MOD            R3, R4, R1
     54  ADD            R0, R0, R5
     55  ACT            R3
     56  JMP            49
     57  BLK_REC_BEGIN  
     58  JMP            34
     59  WS_WRITE       R0, R3
     60  BLK_LEN        R0, R4
     61  SUB            R0, R2, R3
