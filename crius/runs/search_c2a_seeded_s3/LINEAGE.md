LINEAGE READOUT run=search_c2a_seeded_s3 arm=seeded
ANCESTRY of final-population top 0f33f6bb4fa2d99d (132 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   20.422  20.0   9124      0       0       0          0       0       0   39  seed:ENUMERATE_VM
   27   22.961  22.5   4542    100       0       0          0       0       0   39  arg@17.0
   53   22.907  22.5  10907    100       0       0          0       0       0   34  delete@19
   83   19.915  19.5  10060    100       0       0          0       0       0   31  arg@7.1+replace@7+const@1
  100   22.959  22.5   4802    100       0       0          0       0       0   40  arg@39.0
  131   16.882  16.5  13967    100       0       0          0       0       0   41  delete@7+arg@23.0
  157   21.925  21.5   8858      0     300       0          0       0     100   42  insert@38+duplicate@7+3->2+swap@6,20
  180   20.413  20.0  10304    100     300       0          0       0     100   51  const@1+delete@11+swap@41,31
  199   22.940  22.5   7043    100     100       0          0       0     100   42  delete@12
  224   19.432  19.0   8051    100       0       0          0       0       0   36  const@0+arg@36.0+delete@4
  243   22.928  22.5   8497    100       0       0          0       0       0   30  arg@26.1+delete@29
  269   19.418  19.0   9639      0     100       0          0       0       0   36  insert@29+duplicate@10+6->11
  300   22.928  22.5   8517      0     100       0          0       0       0   40  duplicate@8+5->12
  284   23.923  23.5   9051      0     100       0          0       0       0   32  swap@15,0
  294   23.435  23.0   7708      0     100       0          0       0       0   35  duplicate@10+3->31
  295   21.364  21.0  16034      0     100       0          0       0       0   34  delete@13+arg@8.0+const@14
  296   19.909  19.5  10792      0     100       0          0       0       0   36  duplicate@15+2->28
  298   21.423  21.0   9055      0     100       0          0       0       0   35  delete@12
  gradient (mean first half -> second half of the lineage): reads 188 -> 79, writes 27 -> 100, invokes 0.0 -> 0.0, blocks 0.0 -> 0.0, wsBytes 5 -> 34, successes 21.3 -> 22.4
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      0      0         --     13.968   20.422
   25   24      0      0         --     14.325   26.961
   50   24      1      0     22.916     15.323   25.971
   75   24      0      0         --      7.503   17.881
  100   24      0      0         --     14.519   22.962
  125   24      0      0         --     14.845   22.887
  150   24      1      0     20.906     14.319   22.925
  175   24     21      0     15.320     21.462   23.459
  200   24     22      0     12.631     10.291   21.399
  225   24      0      0         --     20.625   25.445
  250   24      4      0     10.913     12.391   20.941
  275   24      1      0      4.695     15.597   21.957
  300   24      0      0         --     15.127   22.928
  candidates that invoked a block: 4; of those in their iteration's top 8: 0
TOP MECHANISM 0f33f6bb4fa2d99d: fitness 22.928 succ 22.5 inter 8517 reads 0 writes 100 invokes 0 blocks 0 wsBytes 0 invalid 0
  trace: {"ACT": 25970, "INPUT": 400, "WS_ALLOC": 200, "BLK_STATE_SET": 100}
      0  INPUT          R1, num_ops
      1  ACT            R4
      2  ADD            R0, R0, R5
      3  BLK_STATE_SET  R1, R0, R2
      4  VLEN           R0, R0
      5  VGET           R5, R3, R5
      6  INPUT          R5, interactions_left
      7  ADD            R0, R0, R5
      8  ADD            R7, R1, R1
      9  WS_ALLOC       R6, R4
     10  ADD            R0, R0, R5
     11  INPUT          R1, num_ops
     12  ADD            R7, R1, R1
     13  WS_ALLOC       R6, R4
     14  ADD            R0, R0, R5
     15  INPUT          R1, num_ops
     16  ADD            R0, R0, R5
     17  ADD            R0, R0, R5
     18  CONST          R6, -6
     19  ACT            R1
     20  MOD            R3, R0, R1
     21  ACT            R3
     22  DIV            R4, R0, R1
     23  MOD            R3, R4, R1
     24  ACT            R3
     25  DIV            R4, R4, R1
     26  MOD            R3, R4, R1
     27  ACT            R3
     28  ADD            R0, R0, R5
     29  JMP            19
     30  BLK_REC_END    R6
     31  BLK_STATE_SET  R5, R7, R3
     32  ACT            R1
     33  MOD            R3, R0, R1
     34  BLK_LEN        R0, R3
     35  JMP            6
     36  ADD            R0, R0, R5
     37  INPUT          R1, num_ops
     38  MOD            R3, R0, R1
     39  VSET           R4, R0, R7
