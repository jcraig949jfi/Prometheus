LINEAGE READOUT run=search_c2b_seeded_s2 arm=seeded
ANCESTRY of final-population top 2a149836950d1044 (106 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   19.378  19.0  14273      0       0       0          2       0       0   39  seed:ENUMERATE_VM
   15   17.367  17.0  15596      0       0       0          2       0       0   35  swap@8,18+delete@15+const@2
   44   21.938  21.5   7218      0       0       0          2       0       0   37  arg@17.2+swap@33,24+insert@12
   67   22.408  22.0  10834      0       0       0          2       0       0   31  const@3
   91   20.434  20.0   7775      0       0       0          2       0       0   29  delete@18
  113   22.459  22.0   4868      0       0       0          2       0       0   26  arg@1.1
  141   22.918  22.5   9687      0       0       0          2       0       0   27  insert@26
  152   21.939  21.5   7246      0       0       0          2       0       0   37  replace@17+replace@12+delete@30
  170   21.402  21.0  11544      0       0       0          2       0       0   36  delete@8+const@3
  191   22.952  22.5   5666      0       0       0          2       0       0   32  arg@24.0
  205   23.943  23.5   6696      0       0       0          2       0       0   27  const@9
  242   22.900  22.5  11707    398       0       0          2       0       0   28  insert@0+insert@14+duplicate@3+1->22
  261   21.417  21.0   9733      0       0       0          2       0       0   26  swap@26,5+delete@10
  288   23.926  23.5   8736      0       0       0          2       0       0   20  swap@17,14+const@8
  278   20.434  20.0   7744      0       0       0          2       0       0   21  delete@4
  279   20.372  20.0  15123      0       0       0          2       0       0   20  delete@0
  286   24.440  24.0   7092      0       0       0          2       0       0   20  replace@4+const@4
  292   21.918  21.5   9706      0       0       0          2       0       0   20  swap@8,6
  297   22.897  22.5  12156      0       0       0          2       0       0   19  arg@6.1+delete@3
  gradient (mean first half -> second half of the lineage): reads 71 -> 44, writes 4 -> 0, invokes 0.0 -> 0.0, blocks 4.3 -> 2.0, wsBytes 0 -> 0, successes 21.7 -> 22.0
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      0      0         --      9.957   19.378
   25   24      0      0         --     11.348   23.468
   50   24      1      0     23.951     12.223   23.952
   75   24      2      0     21.431     11.414   22.944
  100   24      0      0         --     15.688   22.927
  125   24      1      0      0.000     14.607   23.457
  150   24      1      0      2.692     16.830   22.413
  175   24      1      0     18.395      9.834   20.437
  200   24      0      0         --      9.267   21.423
  225   24      0      0         --     15.637   25.963
  250   24      0      0         --     10.184   20.913
  275   24      1      0     21.948     14.966   21.948
  300   24      1      0     14.354     11.022   20.958
  candidates that invoked a block: 45; of those in their iteration's top 8: 6
TOP MECHANISM 2a149836950d1044: fitness 22.897 succ 22.5 inter 12156 reads 0 writes 0 invokes 0 blocks 2 wsBytes 0 invalid 0
  trace: {"ACT": 35610, "INPUT": 100}
      0  INPUT          R1, num_ops
      1  CONST          R5, 7
      2  BRZ            R3, 5
      3  CONST          R4, -2
      4  DIV            R7, R4, R6
      5  CONST          R4, -10
      6  ADD            R0, R0, R5
      7  ADD            R0, R0, R5
      8  ADD            R0, R0, R5
      9  MOD            R3, R0, R1
     10  ACT            R3
     11  DIV            R4, R0, R1
     12  MOD            R3, R4, R1
     13  ACT            R3
     14  DIV            R4, R4, R1
     15  MOD            R3, R4, R1
     16  ACT            R3
     17  ACT            R1
     18  JMP            8
