CRIUS CAMPAIGN 0 REPORT  run=search_c2a_recombination_s1  arm=recombination
code_commit=6eb2d2ac7 dirty=True config_hash=401915ec4da9443a world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  21.9592   20.7616        10.9609        39         16
    26  20.4377   20.4377        14.5130        49         89
    51  24.4521   24.4521        21.9821        83        151
    76  22.9153   22.7275        14.9477        73        218
   101  21.9196   20.9195        18.7415        77        283
   126  23.4084   22.9637        19.0494        65        366
   151  21.8599   21.8599        16.0628        63        439
   176  19.3709   18.9332        13.5018        66        518
   201  25.9540   24.2689        20.4587        96        601
   226  26.9361   26.9361        22.2883        95        677
   251  20.3862   20.3862        14.6078        91        751
   276  20.4006   19.9626        14.5633        96        816
   300  21.9143   21.9143        17.0107        96        883
  candidates evaluated: 7208   best_ever 28.4758 (56414cfe8d0763b2)  wall 883s

BEST PROGRAM 56414cfe8d0763b2 (len 91, iteration 235, modification delete@0+arg@54.1)
  search seed 1012350: fit 31.4816 succ 31/50 inter 2112 steps 15126 ws_cost 400 blocks 0 invoked 0 ws_bytes 150
    by stage (mean cost, success rate): {"A": [46.895, 1.0], "B": [52.302, 1.0], "C": [38.349, 0.583], "D": [45.712, 0.2], "E": [44.748, 0.25]}
  search seed 1012351: fit 25.4700 succ 25/50 inter 3488 steps 19427 ws_cost 400 blocks 0 invoked 0 ws_bytes 150
    by stage (mean cost, success rate): {"A": [144.857, 1.0], "B": [84.226, 1.0], "C": [39.844, 0.333], "D": [49.987, 0.1], "E": [52.18, 0.0]}
  listing:
      0  INPUT          R1, num_ops
      1  CONST          R5, 12
      2  BRZ            R6, 66
      3  WS_REC_SET     R2, R3, R5
      4  WS_WRITE       R1, R6
      5  ACT            R0
      6  ACT            R1
      7  BLK_COUNT      R0
      8  ADD            R0, R3, R5
      9  MOD            R2, R0, R1
     10  BLK_DELETE     R4
     11  WS_LINK        R7, R6, R4
     12  BLK_STATE_SET  R6, R2, R6
     13  WS_REC_GET     R5, R3, R1
     14  BLK_DELETE     R2
     15  JMP            20
     16  DIV            R1, R5, R6
     17  ACTI           9
     18  WS_APPEND      R7, R4
     19  DIV            R4, R0, R1
     20  BLK_DELETE     R4
     21  MOD            R2, R7, R1
     22  LT             R4, R5, R5
     23  ADD            R0, R3, R5
     24  MOD            R2, R0, R1
     25  WS_ALLOC       R1, R3
     26  BLK_DELETE     R4
     27  ADD            R0, R0, R5
     28  JMP            25
     29  CONST          R4, -13
     30  WS_FIND        R7, R4
     31  BLK_STATE_SET  R0, R2, R0
     32  ACT            R1
     33  BRNZ           R2, 2
     34  BLK_STATE_SET  R0, R2, R0
     35  VSET           R4, R2, R4
     36  WS_WRITE       R1, R2
     37  MOD            R3, R0, R1
     38  MOD            R3, R4, R2
     39  BLK_LEN        R3, R5
     40  ACT            R4
     41  MOD            R3, R4, R1
     42  MOD            R7, R2, R1
     43  JMP            20
     44  BLK_PATCH      R1, R3, R6
     45  ADD            R4, R0, R5
     46  WS_ALLOC       R6, R1
     47  MOD            R3, R0, R1
     48  ACT            R1
     49  WS_REC_NEW     R0
     50  BRNZ           R3, 12
     51  ADD            R0, R0, R5
     52  BLK_STATE_SET  R6, R6, R5
     53  ACT            R1
     54  DIV            R4, R3, R1
     55  BLK_COUNT      R4
     56  ADD            R4, R0, R5
     57  WS_REC_NEW     R0
     58  BRNZ           R3, 12
     59  ADD            R0, R0, R5
     60  BLK_LEN        R6, R6
     61  ACT            R1
     62  BLK_DELETE     R2
     63  WS_WRITE       R1, R6
     64  ADD            R4, R0, R5
     65  ACT            R1
     66  WS_REC_NEW     R0
     67  WS_LINK_GET    R3, R0, R0
     68  ADD            R0, R0, R5
     69  ADD            R0, R4, R5
     70  WS_SREAD       R6, R4, R5
     71  MOD            R3, R0, R1
     72  WS_LINK        R1, R1, R6
     73  ACTI           10
     74  MOD            R3, R0, R1
     75  BLK_STATE_SET  R6, R2, R6
     76  ADD            R0, R0, R5
     77  ADD            R0, R0, R5
     78  MOD            R3, R0, R1
     79  CONST          R5, 1
     80  ACT            R3
     81  DIV            R4, R0, R1
     82  MOD            R3, R4, R1
     83  ACT            R3
     84  DIV            R4, R4, R1
     85  MOD            R3, R4, R1
     86  ACT            R3
     87  ACT            R1
     88  JMP            77
     89  WS_REC_NEW     R1
     90  ACT            R1
  ancestry (129 steps, newest first): iteration/fitness/modification
    it  235  28.4758  len 91  delete@0+arg@54.1
    it  234  20.9345  len 92  replace@11+const@18+const@74
    it  230  23.4696  len 92  delete@91+delete@12+arg@22.1
    it  229  18.8619  len 94  replace@72
    it  227  23.9145  len 94  arg@76.0+delete@73+const@75
    it  224  20.9179  len 95  replace@69
    it  223  18.3837  len 95  delete@42
    it  222  20.9018  len 96  replace@45
    it  221  26.4349  len 96  replace@64+insert@49+arg@72.1
    it  220  20.4213  len 95  insert@31+arg@1.1+splice@0<-donor[9:10]:6ce158cff51056e0
    it  219  23.9388  len 93  arg@41.0+insert@70
    it  218  20.4228  len 92  swap@59,31+replace@40+replace@45
    it  217  23.9309  len 92  replace@14+delete@75+delete@72
    it  215  20.3687  len 94  insert@3
    it  214  22.4288  len 93  delete@77+delete@63
    ... 115 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7316.0    4.3   74.7
  top1_169cae41f3c64dd2       21.770  21.770  21.770  21.770  21.3  21.3     7436     7436       0.0    0.0    0.0
  top2_09bdfb9f06bfa880       21.770  21.770  21.770  21.770  21.3  21.3     7436     7436       0.0    0.0    0.0
  top3_3732f98e434516b0       21.770  21.770  21.770  21.770  21.3  21.3     7436     7436       0.0    0.0    0.0
  ancestor169_it297_4bf5a14e  21.770  21.770  21.770  21.770  21.3  21.3     7436     7436       0.0    0.0    0.0
  bestever_56414cfe8d0763b2   21.412  21.412  21.412  21.412  21.0  21.0    10303    10303       0.0    0.0    0.0
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.3    2.7    1.7
  contemp_06f2f2ae189ef84a    20.075  20.075  20.075  20.075  19.7  19.7    10734    10734       0.0    0.0    0.0
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ancestor1_it0_0875253d162c  19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       0.0    0.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       0.0    0.0    0.0
  ancestor85_it159_7fd899c8a  17.719  18.387  18.386  17.719  17.3  18.0    13543    13336    -212.8    0.0    0.0
  contemp_bf6fb1952ead0dac    16.026  16.026  16.026  16.026  15.7  15.7    16488    16488       0.0    0.0    0.0
  contemp_f0fe2dc64b0011d3     8.926   8.926   8.926   8.926   8.7   8.7    28346    28346       0.0    0.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.00/ 455.13   14.90/ 539.10   21.11/  47.94   33.21/  48.94   40.07/  50.52
  top1_169cae41f3c64dd2       307.86/ 307.86  320.28/ 320.28   49.89/  49.89   51.25/  51.25   51.86/  51.86
  top2_09bdfb9f06bfa880       307.88/ 307.88  320.30/ 320.30   49.91/  49.91   51.27/  51.27   51.88/  51.88
  top3_3732f98e434516b0       307.88/ 307.88  320.30/ 320.30   49.91/  49.91   51.27/  51.27   51.88/  51.88
  ancestor169_it297_4bf5a14e  307.88/ 307.88  320.30/ 320.30   49.91/  49.91   51.27/  51.27   51.88/  51.88
  bestever_56414cfe8d0763b2   445.91/ 445.91  481.12/ 481.12   47.49/  47.49   50.79/  50.79   52.18/  52.18
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.13/ 443.81  528.11/ 527.79   47.93/  47.89   48.85/  48.88   50.42/  50.46
  contemp_06f2f2ae189ef84a    428.65/ 428.65  547.98/ 547.98   47.54/  47.54   49.12/  49.12   52.33/  52.33
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ancestor1_it0_0875253d162c  495.80/ 495.80  525.01/ 525.01   50.10/  50.10   51.09/  51.09   52.68/  52.68
  ENUMERATE_VM_C1             495.80/ 495.80  525.01/ 525.01   50.10/  50.10   51.09/  51.09   52.68/  52.68
  ancestor85_it159_7fd899c8a  537.30/ 525.86  717.61/ 710.43   50.20/  49.07   51.33/  50.02   51.96/  51.96
  contemp_bf6fb1952ead0dac    763.08/ 763.08  818.87/ 818.87   50.24/  50.24   51.60/  51.60   52.21/  52.21
  contemp_f0fe2dc64b0011d3   1267.64/1267.64 1540.69/1540.69   49.42/  49.42   50.48/  50.48   52.33/  52.33
  RANDOM_C1                  1662.62/1662.62 1627.07/1627.07   50.50/  50.50   50.50/  50.50   48.56/  48.56

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  top1_169cae41f3c64dd2          3/36    48     2/30    49     1/12    49     0/12    50    29/30   293    29/30   305
  top2_09bdfb9f06bfa880          3/36    48     2/30    49     1/12    49     0/12    50    29/30   293    29/30   305
  top3_3732f98e434516b0          3/36    48     2/30    49     1/12    49     0/12    50    29/30   293    29/30   305
  ancestor169_it297_4bf5a14e     3/36    48     2/30    49     1/12    49     0/12    50    29/30   293    29/30   305
  bestever_56414cfe8d0763b2      5/36    45     1/30    49     0/12    50     0/12    50    28/30   427    29/30   461
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  contemp_06f2f2ae189ef84a       5/36    45     2/30    47     0/12    50     0/12    50    27/30   409    25/30   523
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ancestor1_it0_0875253d162c     2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  ancestor85_it159_7fd899c8a     2/36    48     2/30    49     0/12    50     0/12    50    26/30   517    22/30   691
  contemp_bf6fb1952ead0dac       3/36    48     2/30    49     1/12    49     0/12    50    21/30   725    20/30   778
  contemp_f0fe2dc64b0011d3       4/36    47     2/30    48     0/12    50     0/12    50    12/30  1214     8/30  1476
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.26    49.53    36.26    36.26    49.53    49.53    49.53   4.0
  top1_169cae41f3c64dd2         51.52       --    51.52    51.52    51.52    51.52    51.52   0.0
  top2_09bdfb9f06bfa880         51.54       --    51.54    51.54    51.54    51.54    51.54   0.0
  top3_3732f98e434516b0         51.54       --    51.54    51.54    51.54    51.54    51.54   0.0
  ancestor169_it297_4bf5a14e    51.54       --    51.54    51.54    51.54    51.54    51.54   0.0
  bestever_56414cfe8d0763b2     51.41       --    51.41    51.41    51.41    51.41    51.41   0.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.55    49.55    49.55    49.55    49.55    49.55    49.55   1.0
  contemp_06f2f2ae189ef84a      50.55       --    50.55    50.55    50.55    50.55    50.55   0.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ancestor1_it0_0875253d162c    51.80       --    51.80    51.80    51.80    51.80    51.80   0.0
  ENUMERATE_VM_C1               51.80       --    51.80    51.80    51.80    51.80    51.80   0.0
  ancestor85_it159_7fd899c8a    51.61       --    50.55    51.61    50.55    50.55    50.55   0.0
  contemp_bf6fb1952ead0dac      51.87       --    51.87    51.87    51.87    51.87    51.87   0.0
  contemp_f0fe2dc64b0011d3      51.30       --    51.30    51.30    51.30    51.30    51.30   0.0
  RANDOM_C1                     49.64       --    49.64    49.64    49.64    49.64    49.64   0.0

CHARTER s13 CHECKLIST (seeds passing / seeds; thresholds: 5 percent relative; guard 0 added 2026-09-19, see report.py)
  PROCEDURE_REUSE_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [48, 48, 41] vs FRESH [20, 19, 22]
    1_cost_declines_via_accumulation       3/3  reuse_gain C-E per seed [736.2, 717.2, 235.3] vs 5% of FRESH cost [1515.6, 1467.2, 1423.8] (and 0 held)
    2_reproduces_on_heldout                3/3  same test, qualification suite; seeds passing = 3/3
    3_state_causal_FULL_vs_CODE_ONLY       2/3  remainder mean cost FULL [30.57, 30.13, 48.08] vs CODE_ONLY [50.41, 50.41, 47.78]
    4_scramble_or_reset_damages            3/3  eff ACC [48.449, 48.475, 41.476] SCR [20.443, 21.469, 22.474] RESET [20.443, 21.469, 22.475]
    5_transfers_to_fresh_copy              2/3  FULL [30.57, 30.13, 48.08] vs ACC remainder [30.57, 30.13, 48.08]
    6_executable_components_reused         2/3  invocations [82, 81, 61]; ABLATION_ALL cost [50.41, 50.41, 47.78] vs ACC remainder [30.57, 30.13, 48.08]
    7_not_compute_or_storage               2/3  COMPUTE_MATCHED [50.41, 50.41, 47.78] STORAGE_MATCHED [50.41, 50.41, 47.78] vs ACC remainder [30.57, 30.13, 48.08]
  top1_169cae41f3c64dd2
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 22, 23] vs FRESH [19, 22, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1549.1, 1531.3, 1497.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.3, 51.72, 50.55] vs CODE_ONLY [52.3, 51.72, 50.55]
    4_scramble_or_reset_damages            0/3  eff ACC [19.401, 22.459, 23.45] SCR [19.401, 22.459, 23.45] RESET [19.401, 22.459, 23.45]
    5_transfers_to_fresh_copy              0/3  FULL [52.3, 51.72, 50.55] vs ACC remainder [52.3, 51.72, 50.55]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.3, 51.72, 50.55]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.3, 51.72, 50.55] STORAGE_MATCHED [52.3, 51.72, 50.55] vs ACC remainder [52.3, 51.72, 50.55]
  top2_09bdfb9f06bfa880
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 22, 23] vs FRESH [19, 22, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1549.7, 1531.9, 1498.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.32, 51.74, 50.57] vs CODE_ONLY [52.32, 51.74, 50.57]
    4_scramble_or_reset_damages            0/3  eff ACC [19.401, 22.459, 23.45] SCR [19.401, 22.459, 23.45] RESET [19.401, 22.459, 23.45]
    5_transfers_to_fresh_copy              0/3  FULL [52.32, 51.74, 50.57] vs ACC remainder [52.32, 51.74, 50.57]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.32, 51.74, 50.57]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.32, 51.74, 50.57] STORAGE_MATCHED [52.32, 51.74, 50.57] vs ACC remainder [52.32, 51.74, 50.57]
  top3_3732f98e434516b0
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 22, 23] vs FRESH [19, 22, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1549.7, 1531.9, 1498.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.32, 51.74, 50.57] vs CODE_ONLY [52.32, 51.74, 50.57]
    4_scramble_or_reset_damages            0/3  eff ACC [19.401, 22.459, 23.45] SCR [19.401, 22.459, 23.45] RESET [19.401, 22.459, 23.45]
    5_transfers_to_fresh_copy              0/3  FULL [52.32, 51.74, 50.57] vs ACC remainder [52.32, 51.74, 50.57]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.32, 51.74, 50.57]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.32, 51.74, 50.57] STORAGE_MATCHED [52.32, 51.74, 50.57] vs ACC remainder [52.32, 51.74, 50.57]
  ancestor169_it297_4bf5a14e6520bb19
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 22, 23] vs FRESH [19, 22, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1549.7, 1531.9, 1498.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.32, 51.74, 50.57] vs CODE_ONLY [52.32, 51.74, 50.57]
    4_scramble_or_reset_damages            0/3  eff ACC [19.401, 22.459, 23.45] SCR [19.401, 22.459, 23.45] RESET [19.401, 22.459, 23.45]
    5_transfers_to_fresh_copy              0/3  FULL [52.32, 51.74, 50.57] vs ACC remainder [52.32, 51.74, 50.57]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.32, 51.74, 50.57]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.32, 51.74, 50.57] STORAGE_MATCHED [52.32, 51.74, 50.57] vs ACC remainder [52.32, 51.74, 50.57]
  bestever_56414cfe8d0763b2
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 20, 24] vs FRESH [19, 20, 24]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1519.5, 1520.6, 1445.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.18, 52.18, 49.86] vs CODE_ONLY [52.18, 52.18, 49.86]
    4_scramble_or_reset_damages            0/3  eff ACC [19.383, 20.414, 24.44] SCR [19.383, 20.414, 24.44] RESET [19.383, 20.414, 24.44]
    5_transfers_to_fresh_copy              0/3  FULL [52.18, 52.18, 49.86] vs ACC remainder [52.18, 52.18, 49.86]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.18, 52.18, 49.86]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.18, 52.18, 49.86] STORAGE_MATCHED [52.18, 52.18, 49.86] vs ACC remainder [52.18, 52.18, 49.86]
  ENUMERATE_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 19, 22] vs FRESH [20, 19, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1509.3, 1461.0, 1417.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.31, 50.31, 47.68] vs CODE_ONLY [50.31, 50.31, 47.68]
    4_scramble_or_reset_damages            0/3  eff ACC [20.373, 19.411, 22.449] SCR [20.373, 19.411, 22.449] RESET [20.373, 19.411, 22.449]
    5_transfers_to_fresh_copy              0/3  FULL [50.31, 50.31, 47.68] vs ACC remainder [50.31, 50.31, 47.68]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.31, 50.31, 47.68]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.31, 50.31, 47.68] STORAGE_MATCHED [50.31, 50.31, 47.68] vs ACC remainder [50.31, 50.31, 47.68]
  TABLE_MEMO_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 19, 22] vs FRESH [20, 19, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [-12.0, -11.4, -12.6] vs 5% of FRESH cost [1509.3, 1461.0, 1417.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.71, 50.69, 48.12] vs CODE_ONLY [50.31, 50.31, 47.7]
    4_scramble_or_reset_damages            0/3  eff ACC [20.372, 19.411, 22.449] SCR [20.372, 19.411, 22.449] RESET [20.373, 19.411, 22.449]
    5_transfers_to_fresh_copy              0/3  FULL [50.71, 50.69, 48.12] vs ACC remainder [50.71, 50.69, 48.12]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.71, 50.69, 48.12]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.31, 50.31, 47.7] STORAGE_MATCHED [50.31, 50.31, 47.7] vs ACC remainder [50.71, 50.69, 48.12]
  PROCEDURE_NOCAL_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 19, 22] vs FRESH [20, 19, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [1.2, -1.6, 0.8] vs 5% of FRESH cost [1513.8, 1465.5, 1422.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.42, 50.42, 47.8] vs CODE_ONLY [50.42, 50.42, 47.8]
    4_scramble_or_reset_damages            0/3  eff ACC [20.37, 19.409, 22.447] SCR [20.37, 19.409, 22.447] RESET [20.37, 19.409, 22.447]
    5_transfers_to_fresh_copy              0/3  FULL [50.42, 50.42, 47.8] vs ACC remainder [50.42, 50.42, 47.8]
    6_executable_components_reused         0/3  invocations [3, 1, 1]; ABLATION_ALL cost [50.42, 50.42, 47.8] vs ACC remainder [50.42, 50.42, 47.8]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.42, 50.42, 47.8] STORAGE_MATCHED [50.42, 50.42, 47.8] vs ACC remainder [50.42, 50.42, 47.8]
  contemp_06f2f2ae189ef84a
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [16, 21, 22] vs FRESH [16, 21, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1524.9, 1428.7, 1487.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.33, 49.72, 49.6] vs CODE_ONLY [52.33, 49.72, 49.6]
    4_scramble_or_reset_damages            0/3  eff ACC [16.376, 21.413, 22.437] SCR [16.376, 21.413, 22.437] RESET [16.376, 21.413, 22.437]
    5_transfers_to_fresh_copy              0/3  FULL [52.33, 49.72, 49.6] vs ACC remainder [52.33, 49.72, 49.6]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.33, 49.72, 49.6]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.33, 49.72, 49.6] STORAGE_MATCHED [52.33, 49.72, 49.6] vs ACC remainder [52.33, 49.72, 49.6]
  QUIT_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 18, 20] vs FRESH [20, 18, 20]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1500.0, 1500.0, 1500.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.0, 50.0, 50.0] vs CODE_ONLY [50.0, 50.0, 50.0]
    4_scramble_or_reset_damages            0/3  eff ACC [20.373, 18.411, 20.449] SCR [20.373, 18.411, 20.449] RESET [20.373, 18.411, 20.449]
    5_transfers_to_fresh_copy              0/3  FULL [50.0, 50.0, 50.0] vs ACC remainder [50.0, 50.0, 50.0]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.0, 50.0, 50.0]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.0, 50.0, 50.0] STORAGE_MATCHED [50.0, 50.0, 50.0] vs ACC remainder [50.0, 50.0, 50.0]
  ancestor1_it0_0875253d162cdf0f
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 18, 22] vs FRESH [18, 18, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1580.4, 1531.9, 1488.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.68, 52.68, 50.04] vs CODE_ONLY [52.68, 52.68, 50.04]
    4_scramble_or_reset_damages            0/3  eff ACC [18.368, 18.4, 22.445] SCR [18.368, 18.4, 22.445] RESET [18.368, 18.4, 22.445]
    5_transfers_to_fresh_copy              0/3  FULL [52.68, 52.68, 50.04] vs ACC remainder [52.68, 52.68, 50.04]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.68, 52.68, 50.04]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.68, 52.68, 50.04] STORAGE_MATCHED [52.68, 52.68, 50.04] vs ACC remainder [52.68, 52.68, 50.04]
  ENUMERATE_VM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 18, 22] vs FRESH [18, 18, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1580.4, 1531.9, 1488.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.68, 52.68, 50.04] vs CODE_ONLY [52.68, 52.68, 50.04]
    4_scramble_or_reset_damages            0/3  eff ACC [18.368, 18.4, 22.445] SCR [18.368, 18.4, 22.445] RESET [18.368, 18.4, 22.445]
    5_transfers_to_fresh_copy              0/3  FULL [52.68, 52.68, 50.04] vs ACC remainder [52.68, 52.68, 50.04]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.68, 52.68, 50.04]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.68, 52.68, 50.04] STORAGE_MATCHED [52.68, 52.68, 50.04] vs ACC remainder [52.68, 52.68, 50.04]
  ancestor85_it159_7fd899c8a27aba60
    0_competence_kept_ACC_ge_FRESH         1/3  successes ACC [15, 15, 22] vs FRESH [16, 16, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [-26.0, -30.1, -23.8] vs 5% of FRESH cost [1532.8, 1492.3, 1489.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.96, 51.96, 50.92] vs CODE_ONLY [50.55, 51.47, 49.63]
    4_scramble_or_reset_damages            0/3  eff ACC [15.359, 15.37, 22.427] SCR [15.359, 15.37, 22.427] RESET [16.359, 17.371, 21.427]
    5_transfers_to_fresh_copy              0/3  FULL [51.96, 51.96, 50.92] vs ACC remainder [51.96, 51.96, 50.92]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.96, 51.96, 50.92]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.55, 51.47, 49.63] STORAGE_MATCHED [50.55, 51.47, 49.63] vs ACC remainder [51.96, 51.96, 50.92]
  contemp_bf6fb1952ead0dac
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [13, 13, 21] vs FRESH [13, 13, 21]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1559.5, 1541.8, 1508.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.64, 52.07, 50.91] vs CODE_ONLY [52.64, 52.07, 50.91]
    4_scramble_or_reset_damages            0/3  eff ACC [13.337, 13.308, 21.432] SCR [13.337, 13.308, 21.432] RESET [13.337, 13.308, 21.432]
    5_transfers_to_fresh_copy              0/3  FULL [52.64, 52.07, 50.91] vs ACC remainder [52.64, 52.07, 50.91]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.64, 52.07, 50.91]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.64, 52.07, 50.91] STORAGE_MATCHED [52.64, 52.07, 50.91] vs ACC remainder [52.64, 52.07, 50.91]
  contemp_f0fe2dc64b0011d3
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [11, 10, 5] vs FRESH [11, 10, 5]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1562.5, 1533.2, 1453.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.33, 50.93, 50.64] vs CODE_ONLY [52.33, 50.93, 50.64]
    4_scramble_or_reset_damages            0/3  eff ACC [11.313, 10.282, 5.183] SCR [11.313, 10.282, 5.183] RESET [11.313, 10.282, 5.183]
    5_transfers_to_fresh_copy              0/3  FULL [52.33, 50.93, 50.64] vs ACC remainder [52.33, 50.93, 50.64]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.33, 50.93, 50.64]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.33, 50.93, 50.64] STORAGE_MATCHED [52.33, 50.93, 50.64] vs ACC remainder [52.33, 50.93, 50.64]
  RANDOM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 6, 9] vs FRESH [6, 6, 9]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1493.8, 1515.0, 1489.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.32, 50.5, 49.1] vs CODE_ONLY [49.32, 50.5, 49.1]
    4_scramble_or_reset_damages            0/3  eff ACC [6.205, 6.235, 9.221] SCR [6.205, 6.235, 9.221] RESET [6.205, 6.235, 9.221]
    5_transfers_to_fresh_copy              0/3  FULL [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.32, 50.5, 49.1]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.32, 50.5, 49.1] STORAGE_MATCHED [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]

MACHINERY OF top1_169cae41f3c64dd2 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     1    0    0    0    1 |   0     0
    task  9:    10    0    0    0   10 |   0     0
    task 19:    20    0    0    0   20 |   0     0
    task 31:    32    0    0    0   32 |   0     0
    task 41:    42    0    0    0   42 |   0     0
    task 49:    50    0    0    0   50 |   0     0
  artifact events: 0 (create 0, delete 0, patch/append 0); invocations by block: {}; edges: 0
  adaptation curve ACC:   67 2087 70 963 67 49 79 562 231 352 39 70 963 963 55 910 910 70 2087 89 52 32 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
  adaptation curve FRESH: 67 2087 70 963 67 49 79 562 231 352 39 70 963 963 55 910 910 70 2087 89 52 32 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
  reuse_gain per task:    0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0

BASELINES ON SEARCH SUITE (crius/runs/baselines_c2a): effA effF effR effS  succA  interA interF  reuse_gain  blocks
  ENUMERATE_C1_seed301     21.473 21.473 21.473 21.473   21    3358   3358        0.0    0
  ENUMERATE_C1_seed302     19.412 19.412 19.412 19.412   19   10771  10771        0.0    0
  ENUMERATE_C1_seed303     22.479 22.479 22.479 22.479   22    2548   2548        0.0    0
  ENUMERATE_VM_C1_seed301  21.471 21.471 21.471 21.471   21    3358   3358        0.0    0
  ENUMERATE_VM_C1_seed302  19.397 19.397 19.397 19.397   19   12109  12109        0.0    0
  ENUMERATE_VM_C1_seed303  22.470 22.470 22.470 22.470   22    3428   3428        0.0    0
  PROCEDURE_NOCAL_C1_seed301 21.471 21.471 21.471 21.471   21    3538   3538      -49.9    3
  PROCEDURE_NOCAL_C1_seed302 19.410 19.411 19.411 19.410   19   10917  10915      -45.5    3
  PROCEDURE_NOCAL_C1_seed303 22.477 22.478 22.478 22.477   22    2732   2728      -59.1    5
  PROCEDURE_REUSE_C1_seed301 50.488 21.470 21.481 21.481   50    1338   3718     2288.5    4
  PROCEDURE_REUSE_C1_seed302 49.459 18.410 21.453 21.453   49    4787  11057     6085.5    6
  PROCEDURE_REUSE_C1_seed303 50.492 22.476 22.484 22.483   50     948   2908     1895.0    5
  QUIT_C1_seed301          20.472 20.472 20.472 20.472   20    1907   1907        0.0    0
  QUIT_C1_seed302          17.412 17.412 17.412 17.412   17    9331   9331        0.0    0
  QUIT_C1_seed303          20.479 20.479 20.479 20.479   20    1135   1135        0.0    0
  RANDOM_C1_seed301         7.237  7.237  7.237  7.237    7   32013  32013        0.0    0
  RANDOM_C1_seed302         9.240  9.240  9.240  9.240    9   31692  31692        0.0    0
  RANDOM_C1_seed303        12.282 12.282 12.282 12.282   12   26477  26477        0.0    0
  TABLE_MEMO_C1_seed301    21.472 21.473 21.473 21.472   21    3358   3358      -15.9    0
  TABLE_MEMO_C1_seed302    19.412 19.412 19.412 19.412   19   10771  10771      -13.8    0
  TABLE_MEMO_C1_seed303    22.479 22.479 22.479 22.479   22    2548   2548      -16.7    0

