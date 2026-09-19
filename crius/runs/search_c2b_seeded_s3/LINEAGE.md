LINEAGE READOUT run=search_c2b_seeded_s3 arm=seeded
ANCESTRY of final-population top 0668e1ff67c898f7 (54 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   20.422  20.0   9124      0       0       0          2       0       0   39  seed:ENUMERATE_VM
    4   22.950  22.5   5843      0       0       0          2       0       0   36  arg@2.1
    9   19.934  19.5   7718      0       0       0          2       0       0   38  delete@3
   19   20.913  20.5  10190      0       0       0          2       0       0   35  replace@13+arg@15.2
   24   23.921  23.5   9274      0       0       0          2       0       0   34  delete@12
   35   22.410  22.0  10650      0       0       0          2       0       0   31  delete@14
   41   20.940  20.5   7053      0       0       0          2       0       0   30  swap@1,4
   58   21.433  21.0   7892      0       0       0          2       0       0   27  delete@27
   70   21.975  21.5   2934      0       0       0          2       0       0   26  const@0+const@0+arg@12.2
   90   22.931  22.5   8124      0       0       0          2       0       0   23  arg@5.0+arg@3.0
  108   26.952  26.5   5598      0       0       0          2       0       0   20  delete@3
  165   19.916  19.5   9931      0       0       0          2       0       0   16  delete@1+swap@14,6
  198   21.398  21.0  12106      0       0       0          2       0       0   17  replace@3
  253   22.417  22.0   9782      0       0       0          2       0       0   15  const@3
  210   24.944  24.5   6629      0       0       0          2       0       0   16  delete@5
  215   25.440  25.0   7108      0       0       0          2       0       0   15  const@4+delete@3
  239   22.401  22.0  11669      0       0       0          2       0       0   15  arg@3.0
  274   21.455  21.0   5286      0       0       0          2       0       0   15  const@3
  299   21.919  21.5   9574      0       0       0          2       0       0   15  swap@13,4
  gradient (mean first half -> second half of the lineage): reads 0 -> 0, writes 0 -> 0, invokes 0.0 -> 0.0, blocks 2.0 -> 2.0, wsBytes 0 -> 0, successes 21.1 -> 21.9
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      0      0         --     13.968   20.422
   25   24      0      0         --     11.304   27.966
   50   24      1      0     16.853     11.686   26.473
   75   24      2      0      5.211     10.672   20.941
  100   24      7      0     12.755     12.464   22.964
  125   24      0      0         --     10.582   19.916
  150   24      0      0         --     11.078   22.413
  175   24      0      0         --     17.082   23.459
  200   24      1      0      1.146      9.279   21.413
  225   24      1      0      0.663     11.484   23.436
  250   24      2      0     17.640      6.245   22.939
  275   24      0      0         --      9.607   21.938
  300   24      2      0     13.325      9.703   22.934
  candidates that invoked a block: 44; of those in their iteration's top 8: 11
TOP MECHANISM 0668e1ff67c898f7: fitness 21.919 succ 21.5 inter 9574 reads 0 writes 0 invokes 0 blocks 2 wsBytes 0 invalid 0
  trace: {"ACT": 28578, "INPUT": 100}
      0  CONST          R5, -5
      1  INPUT          R1, num_ops
      2  JMP            5
      3  ACTI           9
      4  MOD            R3, R0, R1
      5  ADD            R0, R0, R5
      6  ACT            R3
      7  DIV            R4, R0, R1
      8  MOD            R3, R4, R1
      9  ACT            R3
     10  DIV            R4, R4, R1
     11  MOD            R3, R4, R1
     12  ACT            R3
     13  ACT            R1
     14  JMP            4
