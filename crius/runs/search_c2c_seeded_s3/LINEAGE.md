LINEAGE READOUT run=search_c2c_seeded_s3 arm=seeded
ANCESTRY of final-population top bd6d521120b1b606 (104 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   20.422  20.0   9124      0       0       0          2       0       0   39  seed:ENUMERATE_VM
   14   17.349  17.0  17756      0       0       0          2       0       0   39  const@22+const@1
   39   18.381  18.0  14082      0       0       0          2       0       0   46  duplicate@1+2->22
   58   20.891  20.5  12851      0       0       0          2       0       0   46  const@29
   78   24.948  24.5   6082      0     100       0          2       0       0   48  delete@6
   94   23.954  23.5   5460      0       0       0          2       0       0   40  delete@24+delete@10
  121   24.428  24.0   8462      0       0       0          2       0       0   36  delete@7
  148   21.936  21.5   7564      0       0       0          2       0       0   38  replace@10+replace@14+delete@11
  170   22.442  22.0   6825      0       0       0          2       0       0   34  insert@15
  196   26.431  26.0   8150      0       0       0          2       0       0   43  delete@21
  230   23.448  23.0   6096      0       0       0          2       0       0   40  const@0+const@0+arg@16.0
  255   23.951  23.5   5696    200       0       0          4       0       0   53  const@0
  270   24.468  24.0   3775    500     300     100         64      90       0   75  duplicate@2+6->49+insert@26+duplicate@8+
  300   24.433  24.0   7854    500     300     100          2       0       2   70  arg@20.0+insert@50
  284   24.449  24.0   5996    500     300     100         64      90       0   73  delete@7+replace@11
  288   22.938  22.5   7322    500     300     100         64      90       0   72  delete@57
  291   22.933  22.5   7936    500     300     100         64      90       0   71  delete@16
  292   20.409  20.0  10738    500     300     100         64      90       0   70  arg@46.1+delete@32
  299   20.418  20.0   9658    500     200     100          2       0       0   69  delete@50
  gradient (mean first half -> second half of the lineage): reads 0 -> 155, writes 13 -> 72, invokes 0.0 -> 20.8, blocks 2.0 -> 18.8, wsBytes 0 -> 0, successes 21.3 -> 22.8
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      0      0         --     13.968   20.422
   25   24      0      0         --     20.457   27.462
   50   24      1      0     19.908     16.615   23.922
   75   24      0      0         --     12.056   20.400
  100   24      0      0         --     15.929   22.470
  125   24      0      0         --     13.124   21.925
  150   24      3      0     18.880     16.614   22.907
  175   24      4      0      8.397     16.637   24.447
  200   24      2      0     10.787     14.023   22.400
  225   24      1      0      0.163     16.662   24.463
  250   24      1      1     12.809     13.380   23.933
  275   24     20     20     13.227     15.998   22.438
  300   24     19     18     17.826     17.964   24.433
  candidates that invoked a block: 681; of those in their iteration's top 8: 240
TOP MECHANISM bd6d521120b1b606: fitness 24.433 succ 24.0 inter 7854 reads 500 writes 300 invokes 100 blocks 2 wsBytes 2 invalid 200
  trace: {"ACT": 24527, "WS_FIND": 200, "WS_SREAD": 200, "BLK_INVOKE": 100, "BLK_LEN": 100, "BLK_REC_END": 100, "BLK_STATE_SET": 100, "INPUT": 100, "PSIM": 100, "WS_WRITE": 100}
      0  CONST          R5, 5
      1  ADD            R0, R0, R5
      2  ADD            R0, R0, R7
      3  ADD            R0, R0, R5
      4  ADD            R0, R0, R5
      5  VGET           R3, R1, R7
      6  ACT            R0
      7  ADD            R1, R7, R3
      8  BLK_REC_END    R3
      9  MUL            R2, R2, R1
     10  ADD            R1, R7, R3
     11  BLK_LEN        R3, R4
     12  ADD            R0, R0, R5
     13  WS_FIND        R1, R4
     14  ADD            R0, R0, R5
     15  WS_FIND        R1, R4
     16  ADD            R0, R0, R5
     17  BLK_INVOKE     R5
     18  ADD            R0, R0, R5
     19  PSIM           R1, R3, R4
     20  ACT            R7
     21  ADD            R0, R0, R5
     22  WS_SREAD       R7, R2, R0
     23  ADD            R0, R0, R5
     24  SUB            R1, R4, R7
     25  ADD            R0, R0, R5
     26  JMP            43
     27  DIV            R4, R4, R1
     28  BLK_PATCH      R0, R7, R6
     29  HALT           
     30  INPUT          R5, num_ops
     31  DIV            R7, R3, R7
     32  HALT           
     33  INPUT          R5, num_ops
     34  WS_FIND        R2, R4
     35  ADD            R0, R7, R7
     36  VGET           R0, R0, R6
     37  BLK_INVOKE     R7
     38  ADD            R0, R0, R5
     39  BLK_DELETE     R2
     40  ACT            R0
     41  MUL            R2, R2, R1
     42  ADD            R1, R7, R3
     43  ADD            R0, R0, R5
     44  WS_SREAD       R7, R2, R0
     45  ADD            R0, R7, R5
     46  ADD            R0, R0, R5
     47  ADD            R0, R0, R5
     48  INPUT          R1, num_ops
     49  ADD            R0, R0, R5
     50  WS_WRITE       R1, R6
     51  ADD            R0, R0, R5
     52  ADD            R0, R0, R7
     53  ADD            R0, R0, R5
     54  ADD            R0, R0, R5
     55  ACT            R0
     56  ADD            R0, R0, R5
     57  BLK_STATE_SET  R0, R2, R7
     58  ADD            R0, R0, R5
     59  ADD            R0, R0, R5
     60  MOD            R3, R0, R1
     61  ACT            R3
     62  DIV            R4, R0, R1
     63  MOD            R3, R4, R1
     64  ACT            R3
     65  DIV            R4, R4, R1
     66  MOD            R3, R4, R1
     67  ACT            R3
     68  ACT            R1
     69  JMP            59
