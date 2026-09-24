LINEAGE READOUT run=search_c2d_recombination_s3 arm=recombination
ANCESTRY of final-population top a2f32643a319c980 (91 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   20.422  20.0   9124      0       0       0          2       0       0   39  seed:ENUMERATE_VM
   14   16.848  16.5  17915      0       0       0          2       0       0   52  insert@15+duplicate@12+2->47+replace@11
   23   24.456  24.0   5177      0       0       0          2       0       0   64  arg@11.0
   35   21.908  21.5  10826      0       0       0          2       0       0   60  arg@22.0+delete@33
   49   21.423  21.0   9073      0       0       0          2       0       0   54  replace@8
   66   23.932  23.5   8058      0       0       0          2       0       0   55  arg@29.1
   79   20.917  20.5   9824      0       0       0          2       0       0   50  const@27
   92   21.448  21.0   6148      0       0       0          2       0       0   46  const@24+arg@4.0
  111   23.908  23.5  10832      0       0       0          2       0       0   42  arg@10.0
  125   23.907  23.5  11022      0       0       0          2       0       0   33  delete@7+swap@11,10+const@12
  149   22.430  22.0   8312      0       0       0          2       0       0   28  replace@5
  182   21.930  21.5   8276      0       0       0          2       0       0   23  replace@9
  231   23.960  23.5   4720      0       0       0          2       0       0   19  const@5
  283   21.950  21.5   5862      0       0       0          2       0       0   15  delete@3
  243   21.910  21.5  10650      0       0       0          2       0       0   19  arg@6.0
  250   22.431  22.0   8182      0       0       0          2       0       0   18  delete@6
  259   22.455  22.0   5254      0       0       0          2       0       0   17  delete@5
  260   21.949  21.5   5990      0       0       0          2       0       0   17  const@4
  271   20.959  20.5   4858      0       0       0          2       0       0   16  delete@3
  gradient (mean first half -> second half of the lineage): reads 0 -> 0, writes 0 -> 0, invokes 0.0 -> 0.0, blocks 2.0 -> 2.0, wsBytes 0 -> 0, successes 21.7 -> 22.5
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      0      0         --     10.889   21.923
   25   24      2      0      1.657     23.856   27.967
   50   24      0      0         --     19.942   23.946
   75   24      1      0     18.893     13.927   18.894
  100   24      2      1     12.313     17.224   23.462
  125   24      0      0         --     11.685   23.907
  150   24      2      0      5.204     13.385   23.924
  175   24      1      1     22.956     13.513   22.956
  200   24      0      0         --      8.937   22.398
  225   24      2      1     12.239     10.486   24.455
  250   24      0      0         --      9.735   22.431
  275   24      0      0         --      9.158   20.949
  300   24      1      0      0.000     13.293   23.461
  candidates that invoked a block: 28; of those in their iteration's top 8: 5
TOP MECHANISM a2f32643a319c980: fitness 21.950 succ 21.5 inter 5862 reads 0 writes 0 invokes 0 blocks 2 wsBytes 0 invalid 0
  trace: {"ACT": 18761, "INPUT": 100}
      0  INPUT          R1, num_ops
      1  CONST          R5, -19
      2  BRZ            R3, 3
      3  ADD            R0, R0, R5
      4  ACT            R1
      5  MOD            R3, R0, R1
      6  ACT            R3
      7  DIV            R4, R0, R1
      8  MOD            R3, R4, R1
      9  ACT            R3
     10  DIV            R4, R4, R1
     11  MOD            R3, R4, R1
     12  ACT            R3
     13  ADD            R0, R0, R5
     14  JMP            4
