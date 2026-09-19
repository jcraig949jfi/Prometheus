LINEAGE READOUT run=search_c1_recombination_s3 arm=recombination
ANCESTRY of final-population top 2d06de6fdc0a2a95 (166 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   25.315  25.0  31685      0       0       0          0       0       0   39  seed:ENUMERATE_VM
   27   34.359  34.0  24333      0       0       0          0       0       0   41  delete@7+arg@23.2
   47   30.329  30.0  29027      0    9705       0          0       0       0   61  duplicate@46+6->33
   69   33.345  33.0  26664      0     150       0          0       0       0   63  delete@6+arg@12.2
   88   38.395  38.0  18089      0      50       0          0       0       0   64  swap@32,29+splice:none:42b00ed440fbe822
  107   30.348  30.0  26160      0     200       0          0       0       0   64  insert@12+const@2
  125   28.304  28.0  33812      0     100      50          0       0       0   61  replace@9
  150   25.315  25.0  31896      0       0      50          0       0       0   53  const@3
  173   26.268  26.0  40302      0       0      50          0       0       0   53  arg@26.0+arg@11.2
  199   37.380  37.0  20897      0      50      50          0       0       0   49  replace@7+swap@23,6+const@26
  221   37.376  37.0  21591      0      50      50          0       0       0   44  const@19+splice@4<-donor[30:35]:84f7315d
  244   29.296  29.0  34979    100    8849       0          0       0       0   64  swap@15,45+const@20+duplicate@14+1->0+sp
  278   28.328  28.0  29722     99     100       0          0       0       0   63  replace@40
  288   30.320  30.0  31120     49     100       0          0       0       0   59  const@20+delete@38+delete@34
  293   42.403  42.0  16673     50     100       0          0       0       0   59  arg@35.2
  295   35.353  35.0  25410     50     100       0          0       0       0   63  delete@50+arg@14.0+splice@53<-donor[54:5
  297   25.287  25.0  36792     50     100       0          0       0       0   64  duplicate@24+1->39+arg@38.0+replace@32
  298   33.333  33.0  28979     50     100       0          0       0       0   63  delete@12
  300   28.304  28.0  34159     50     100       0          0       0       0   64  duplicate@12+1->54+const@19
  gradient (mean first half -> second half of the lineage): reads 0 -> 108, writes 1838 -> 1564, invokes 3.6 -> 32.1, blocks 0.0 -> 0.0, wsBytes 0 -> 0, successes 29.2 -> 31.9
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      0      0         --     12.051   26.324
   25   24      1      0     21.281     13.559   24.271
   50   24      0      0         --     19.951   32.343
   75   24      0      0         --     18.732   30.319
  100   24      0      0         --     16.626   30.332
  125   24      0      0         --     16.585   28.304
  150   24      1      0      1.074     14.253   25.315
  175   24      1      0      1.108     19.180   26.328
  200   24      1      0      0.102     19.642   29.323
  225   24      1      0     25.276     16.892   38.346
  250   24      0      0         --     27.476   37.383
  275   24      2      0     10.144     27.380   36.366
  300   24      2      0      3.605     18.967   28.304
  candidates that invoked a block: 18; of those in their iteration's top 8: 2
TOP MECHANISM 2d06de6fdc0a2a95: fitness 28.304 succ 28.0 inter 34159 reads 50 writes 100 invokes 0 blocks 0 wsBytes 0 invalid 250
  trace: {"ACT": 41315, "BLK_COMPOSE": 50, "INPUT": 50, "WS_SREAD": 50, "WS_WRITE": 50}
      0  MOD            R3, R4, R1
      1  INPUT          R1, num_ops
      2  CONST          R5, 5
      3  BLK_COMPOSE    R4, R2, R0
      4  LT             R0, R7, R5
      5  LT             R0, R7, R5
      6  WS_WRITE       R3, R4
      7  ACT            R1
      8  ACT            R3
      9  MOD            R3, R4, R1
     10  ACT            R3
     11  ADD            R0, R0, R5
     12  ACT            R3
     13  WS_SREAD       R3, R1, R1
     14  BRNZ           R3, 62
     15  LT             R0, R2, R6
     16  LT             R7, R7, R5
     17  ADD            R0, R0, R5
     18  BRZ            R3, 46
     19  ACTI           -9
     20  ACT            R3
     21  WS_LINK_GET    R5, R5, R4
     22  MOD            R3, R4, R1
     23  MUL            R2, R1, R1
     24  WS_FREE        R5
     25  LT             R0, R7, R5
     26  MOD            R2, R1, R5
     27  VGET           R5, R1, R7
     28  INPUT          R7, target
     29  INPUT          R7, num_ops
     30  WS_FIND        R4, R7
     31  ADD            R0, R5, R7
     32  ACT            R1
     33  WS_FIND        R4, R0
     34  MOD            R5, R4, R2
     35  MOD            R3, R4, R1
     36  MOD            R3, R4, R1
     37  WS_LINKS       R6, R5
     38  MUL            R2, R1, R1
     39  MOD            R3, R4, R1
     40  WS_FIND        R4, R7
     41  MOD            R3, R4, R1
     42  ACT            R3
     43  ACT            R5
     44  ACT            R1
     45  ACT            R3
     46  MOD            R3, R4, R1
     47  ACT            R3
     48  DIV            R4, R4, R1
     49  MOD            R3, R4, R1
     50  ADD            R0, R0, R5
     51  ACT            R3
     52  MOD            R3, R4, R1
     53  MOD            R3, R4, R1
     54  ACT            R3
     55  MOD            R3, R0, R1
     56  ACT            R3
     57  DIV            R4, R0, R1
     58  JMP            44
     59  MOD            R3, R4, R1
     60  MOD            R3, R0, R1
     61  ACT            R3
     62  DIV            R4, R0, R1
     63  JMP            44
