LINEAGE READOUT run=search_c2c_seeded_s1 arm=seeded
ANCESTRY of final-population top 34a7c4a1bfe1b4da (94 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   17.839  17.5  18871      0       0       0          2       0       0   39  seed:ENUMERATE_VM
   13   24.445  24.0   6482      0     100       0          2       0       0   53  insert@4+insert@5+insert@52
   30   21.430  21.0   8260      0       0       0          2       0       0   49  const@15+delete@30
   46   28.447  28.0   6172      0       0       0          2       0       0   48  delete@6+const@29
   59   22.950  22.5   5820      0       0       0          2       0       0   43  delete@25+const@25
   73   23.973  23.5   3197      0       0       0          2       0       0   40  delete@7+replace@16
   84   19.935  19.5   7678      0       0       0          2       0       0   42  replace@22+replace@28
  104   20.467  20.0   3895      0       0       0          2       0       0   38  replace@15
  121   21.933  21.5   7908      0       0       0          2       0       0   33  delete@5+replace@8+replace@14
  140   19.925  19.5   8820      0       0       0          2       0       0   30  arg@7.2+arg@28.0
  154   17.313  17.0  22064      0       0       0          2       0       0   26  insert@26+const@11+delete@26
  178   22.434  22.0   7774      0       0       0          2       0       0   22  replace@5+delete@22
  236   21.377  21.0  14474      0       0       0          2       0       0   21  insert@6
  279   20.869  20.5  15434      0       0       0          2       0       0   19  const@7
  269   24.926  24.5   8772      0       0       0          2       0       0   20  insert@5+arg@20.0+delete@6
  272   23.466  23.0   3938      0       0       0          2       0       0   19  delete@7
  280   24.464  24.0   4226      0       0       0          2       0       0   20  insert@5
  281   24.401  24.0  11710      0       0       0          2       0       0   20  replace@3
  299   22.434  22.0   7723      0       0       0          2       0       0   21  duplicate@11+1->7+const@9+arg@5.0
  gradient (mean first half -> second half of the lineage): reads 0 -> 0, writes 6 -> 0, invokes 0.0 -> 0.0, blocks 2.0 -> 2.0, wsBytes 0 -> 0, successes 21.8 -> 20.9
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      1      0     17.839     10.189   17.839
   25   24      1      0      4.694     13.795   19.908
   50   24      0      0         --     12.678   21.421
   75   24      1      0     18.908     11.664   21.432
  100   24      0      0         --     11.988   23.429
  125   24      0      0         --     11.484   21.421
  150   24      1      0      0.647     12.153   24.441
  175   24      0      0         --      9.256   21.427
  200   24      0      0         --      8.564   19.380
  225   24      1      1      0.638      6.570   23.927
  250   24      0      0         --     10.398   22.929
  275   24      0      0         --      8.747   19.942
  300   24      1      0      2.040     13.662   23.409
  candidates that invoked a block: 23; of those in their iteration's top 8: 7
TOP MECHANISM 34a7c4a1bfe1b4da: fitness 22.434 succ 22.0 inter 7723 reads 0 writes 0 invokes 0 blocks 2 wsBytes 0 invalid 0
  trace: {"ACT": 24163, "INPUT": 100}
      0  INPUT          R1, num_ops
      1  CONST          R5, 1
      2  BRZ            R3, 9
      3  BLK_INVOKE     R5
      4  BLK_LEN        R1, R1
      5  PREC_END       R6
      6  VSET           R6, R4, R0
      7  ADD            R0, R0, R5
      8  BLK_DELETE     R2
      9  CONST          R0, 28
     10  MOD            R3, R0, R1
     11  ACT            R1
     12  ADD            R0, R0, R5
     13  BRZ            R3, 20
     14  ACT            R3
     15  DIV            R4, R0, R1
     16  MOD            R3, R4, R1
     17  ACT            R3
     18  DIV            R4, R4, R1
     19  ACT            R4
     20  JMP            10
