LINEAGE READOUT run=search_c2c_recombination_s3 arm=recombination
ANCESTRY of final-population top b0815fab4759654b (140 steps, oldest first; every 1/12th plus the last 6)
  it   fitness  succ  inter  reads  writes invokes blkCreated invoked wsBytes  len  modification
    0   20.422  20.0   9124      0       0       0          2       0       0   39  seed:ENUMERATE_VM
   17   21.924  21.5   8950      0       0       0          2       0       0   47  replace@26
   35   18.879  18.5  14289      0       0       0          2       0       0   53  duplicate@41+2->33+replace@15+const@37
   60   19.439  19.0   7139      0       0       0          2       0       0   47  const@2
   82   21.906  21.5  11146    100       0       0          2       0       0   46  const@27+arg@4.2
  112   22.411  22.0  10460      0       0       0          2       0       0   39  delete@22+delete@39+delete@11
  137   18.409  18.0  10762      0       0       0          2       0       0   39  const@26
  161   20.925  20.5   8895      0       0       0          2       0       0   40  delete@25
  194   19.387  19.0  13360      0       0       0          2       0       0   46  replace@23+swap@19,21+arg@32.0
  215   22.953  22.5   5498      0       0       0          2       0       0   49  const@34+delete@35
  240   25.450  25.0   5838      0       0       0          2       0       0   41  delete@15+swap@18,19
  259   20.932  20.5   8046      0       0       0          2       0       0   46  const@9
  278   20.926  20.5   8706      0       0       0          2       0       0   47  delete@17
  287   21.942  21.5   6808      0       0       0          2       0       0   44  replace@25+replace@17
  290   24.459  24.0   4851      0       0       0          2       0       0   44  const@1+const@32+replace@6
  291   21.422  21.0   9230      0       0       0          2       0       0   45  insert@20
  294   20.908  20.5  10830      0       0       0          2       0       0   45  const@33
  298   21.935  21.5   7661      0       0       0          2       0       0   45  const@13+const@13
  299   20.427  20.0   8616      0       0       0          2       0       0   45  arg@33.1+const@1
  gradient (mean first half -> second half of the lineage): reads 19 -> 0, writes 0 -> 0, invokes 0.0 -> 0.0, blocks 2.0 -> 2.0, wsBytes 0 -> 0, successes 21.2 -> 21.4
CENSUS per iteration (every 25th): n  keptState  invokedBlock  meanFit(kept) meanFit(notKept)  best
    0    8      0      0         --     10.889   21.923
   25   24      2      2      7.978     20.545   27.463
   50   24      1      1      2.678     16.184   23.965
   75   24      1      1      1.674     13.183   19.890
  100   24      2      0      6.216     18.972   22.970
  125   24      1      1      0.150     11.810   19.911
  150   24      0      0         --     15.885   22.399
  175   24      3      1      0.328     19.418   22.965
  200   24      1      1     20.889     10.065   20.889
  225   24      1      1     23.949     16.841   24.449
  250   24      0      0         --     14.665   22.906
  275   24      0      0         --     14.021   20.929
  300   24      1      0      6.195     13.532   22.423
  candidates that invoked a block: 213; of those in their iteration's top 8: 20
TOP MECHANISM b0815fab4759654b: fitness 20.427 succ 20.0 inter 8616 reads 0 writes 0 invokes 0 blocks 2 wsBytes 0 invalid 0
  trace: {"ACT": 25882, "INPUT": 100}
      0  INPUT          R1, num_ops
      1  CONST          R5, -1
      2  BRZ            R7, 33
      3  VGET           R5, R4, R3
      4  WS_LINKS       R4, R3
      5  BLK_COPY       R2, R0
      6  EQ             R3, R1, R7
      7  WS_READ        R6, R0
      8  BLK_PATCH      R6, R0, R0
      9  PREC_BEGIN     
     10  BRNZ           R6, 22
     11  MUL            R7, R4, R6
     12  MUL            R7, R4, R6
     13  CONST          R0, 31
     14  ACT            R1
     15  WS_ALLOC       R6, R7
     16  MUL            R0, R1, R5
     17  WS_SLEN        R6, R1
     18  SUB            R5, R7, R7
     19  SUB            R0, R2, R2
     20  ADD            R4, R4, R1
     21  BRNZ           R6, 17
     22  ACT            R7
     23  WS_FIND        R1, R5
     24  HALT           
     25  HALT           
     26  WS_REC_SET     R3, R4, R0
     27  WS_LINKS       R4, R2
     28  WS_REC_SET     R5, R2, R7
     29  WS_SREAD       R4, R0, R2
     30  BLK_STATE_GET  R4, R0, R2
     31  ACT            R3
     32  BLK_COPY       R2, R0
     33  CONST          R0, 11
     34  ACT            R1
     35  MOD            R3, R0, R1
     36  ACT            R3
     37  DIV            R4, R0, R1
     38  MOD            R3, R4, R1
     39  ACT            R3
     40  DIV            R4, R4, R1
     41  MOD            R3, R4, R1
     42  ACT            R3
     43  ADD            R0, R0, R5
     44  JMP            34
