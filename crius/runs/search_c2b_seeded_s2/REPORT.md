CRIUS CAMPAIGN 0 REPORT  run=search_c2b_seeded_s2  arm=seeded
code_commit=713b2773f dirty=True config_hash=c9c87cec99eb063f world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  21.4764   21.4738        10.0223        39          4
    26  21.9297   21.9297         8.4738        33        134
    51  20.4336   20.4336         9.4849        36        279
    76  23.9163   23.9163        12.8838        31        411
   101  19.8205   18.9447         9.9891        30        546
   126  23.9302   23.9302        13.7385        29        650
   151  22.4131   21.9819        12.1391        38        753
   176  22.4316   22.4316        16.2378        34        874
   201  20.9027   20.9027        12.0286        27        988
   226  21.4269   21.0474        12.3151        29       1094
   251  23.9644   23.9644        13.8830        29       1198
   276  23.9626   23.9626        14.4148        22       1302
   300  20.9570   20.9570        11.1612        19       1401
  candidates evaluated: 7208   best_ever 29.4697 (991405fc52056f75)  wall 1401s

BEST PROGRAM 991405fc52056f75 (len 29, iteration 199, modification arg@11.0)
  search seed 2011990: fit 30.4633 succ 30/50 inter 4298 steps 21998 ws_cost 15 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [125.219, 1.0], "B": [204.404, 1.0], "C": [35.346, 0.5], "D": [47.001, 0.1], "E": [40.968, 0.375]}
  search seed 2011991: fit 28.4762 succ 28/50 inter 2771 steps 15997 ws_cost 15 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [73.177, 1.0], "B": [88.817, 1.0], "C": [38.375, 0.417], "D": [45.333, 0.2], "E": [49.669, 0.125]}
  listing:
      0  INPUT          R1, num_ops
      1  CONST          R5, 5
      2  BRZ            R3, 7
      3  CONST          R4, -2
      4  WS_FIND        R5, R5
      5  WS_REC_SET     R7, R6, R3
      6  BRZ            R3, 6
      7  ADD            R0, R1, R5
      8  ADD            R0, R0, R5
      9  BRZ            R4, 12
     10  MOV            R3, R5
     11  WS_SREAD       R5, R2, R1
     12  ADD            R0, R0, R5
     13  MOD            R3, R0, R1
     14  ACT            R3
     15  DIV            R4, R0, R1
     16  MOD            R3, R4, R1
     17  ACT            R3
     18  DIV            R4, R4, R1
     19  MOD            R3, R4, R1
     20  ACT            R3
     21  ACT            R1
     22  JMP            12
     23  JMP            24
     24  MUL            R4, R5, R3
     25  DIV            R4, R0, R1
     26  WS_READ        R6, R6
     27  WS_LINKS       R7, R3
     28  NOT            R6, R2
  ancestry (76 steps, newest first): iteration/fitness/modification
    it  199  29.4697  len 29  arg@11.0
    it  198  22.4488  len 29  delete@28+delete@6+replace@10
    it  193  21.9365  len 31  insert@4+delete@5
    it  192  23.4299  len 31  delete@30
    it  191  22.9519  len 32  arg@24.0
    it  187  22.9527  len 32  swap@32,8+delete@25+delete@8
    it  185  24.4466  len 34  delete@7+delete@27+delete@12
    it  184  24.4533  len 37  delete@6+insert@31+insert@14
    it  183  23.9316  len 36  arg@29.0
    it  178  17.3901  len 36  duplicate@14+1->12+delete@28+insert@15
    it  177  22.9510  len 35  arg@3.1+swap@30,26
    it  173  20.4208  len 35  delete@10
    it  170  21.4023  len 36  delete@8+const@3
    it  169  26.4543  len 37  const@3
    it  165  24.9761  len 37  delete@16
    ... 62 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7315.4    5.3   74.7
  bestever_991405fc52056f75   23.104  23.104  23.104  23.104  22.7  22.7     7372     7372       7.2    1.0    0.0
  ancestor54_it148_91f269f78  22.441  22.441  22.441  22.441  22.0  22.0     6905     6905       7.1    1.0    0.0
  top1_2a149836950d1044       21.762  21.762  21.762  21.762  21.3  21.3     8380     8380       7.2    1.0    0.0
  top2_11b02ec4bfb9e0f9       21.762  21.762  21.762  21.762  21.3  21.3     8380     8380       7.2    1.0    0.0
  top3_13f726732a75004d       21.762  21.762  21.762  21.762  21.3  21.3     8380     8380       7.2    1.0    0.0
  ancestor106_it292_11b02ec4  21.762  21.762  21.762  21.762  21.3  21.3     8380     8380       7.2    1.0    0.0
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.9    3.7    1.7
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ancestor1_it0_0875253d162c  19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  contemp_01d562cbd7914341    10.969  10.969  10.969  10.969  10.7  10.7    23425    23425       7.1    1.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0
  contemp_93a8e85a858bba93     4.857   4.857   4.857   4.857   4.7   4.7    36649    36649       6.7    1.0    0.0
  contemp_a439da21d6fed983     1.160   1.160   1.160   1.160   1.0   1.0    40153    40153       2.9    1.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.02/ 455.13   14.92/ 539.10   21.12/  47.94   33.22/  48.94   40.08/  50.52
  bestever_991405fc52056f75   335.18/ 335.31  284.40/ 284.54   49.25/  49.40   50.15/  50.30   50.23/  50.38
  ancestor54_it148_91f269f78  287.07/ 287.20  287.12/ 287.27   45.50/  45.64   50.28/  50.43   51.91/  52.06
  top1_2a149836950d1044       388.32/ 388.45  332.99/ 333.13   49.86/  50.00   51.39/  51.54   50.93/  51.08
  top2_11b02ec4bfb9e0f9       388.32/ 388.45  332.99/ 333.13   49.86/  50.00   51.39/  51.54   50.93/  51.08
  top3_13f726732a75004d       388.32/ 388.45  332.99/ 333.13   49.86/  50.00   51.39/  51.54   50.93/  51.08
  ancestor106_it292_11b02ec4  388.32/ 388.45  332.99/ 333.13   49.86/  50.00   51.39/  51.54   50.93/  51.08
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.14/ 443.81  528.13/ 527.79   47.94/  47.89   48.86/  48.88   50.43/  50.46
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ancestor1_it0_0875253d162c  495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  ENUMERATE_VM_C1             495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  contemp_01d562cbd7914341   1222.15/1222.28 1055.44/1055.58   50.21/  50.35   51.39/  51.54   51.88/  52.03
  RANDOM_C1                  1662.62/1662.62 1627.07/1627.07   50.50/  50.50   50.50/  50.50   48.56/  48.56
  contemp_93a8e85a858bba93   1770.20/1770.33 1888.01/1888.16   50.78/  50.91   52.08/  52.21   52.08/  52.21
  contemp_a439da21d6fed983   2080.05/2080.10 1941.75/1941.81   52.04/  52.10   50.41/  50.47   52.04/  52.10

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  bestever_991405fc52056f75      3/36    47     2/30    48     2/12    48     1/12    48    30/30   321    30/30   272
  ancestor54_it148_91f269f78     7/36    43     1/30    48     0/12    50     0/12    50    29/30   275    29/30   275
  top1_2a149836950d1044          4/36    48     1/30    49     1/12    48     0/12    50    29/30   373    29/30   319
  top2_11b02ec4bfb9e0f9          4/36    48     1/30    49     1/12    48     0/12    50    29/30   373    29/30   319
  top3_13f726732a75004d          4/36    48     1/30    49     1/12    48     0/12    50    29/30   373    29/30   319
  ancestor106_it292_11b02ec4     4/36    48     1/30    49     1/12    48     0/12    50    29/30   373    29/30   319
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ancestor1_it0_0875253d162c     2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  contemp_01d562cbd7914341       2/36    48     1/30    49     0/12    50     0/12    50    13/30  1178    16/30  1017
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610
  contemp_93a8e85a858bba93       1/36    49     0/30    50     0/12    50     0/12    50     7/30  1702     6/30  1815
  contemp_a439da21d6fed983       0/36    50     1/30    48     0/12    50     0/12    50     0/30  2000     2/30  1867

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.27    49.53    36.27    36.27    49.53    49.53    49.53   5.0
  bestever_991405fc52056f75     50.18    50.19    50.18    50.18    50.19    50.19    50.19   1.0
  ancestor54_it148_91f269f78    51.01    51.01    51.01    51.01    51.01    51.01    51.01   1.0
  top1_2a149836950d1044         51.19    51.19    51.19    51.19    51.19    51.19    51.19   1.0
  top2_11b02ec4bfb9e0f9         51.19    51.19    51.19    51.19    51.19    51.19    51.19   1.0
  top3_13f726732a75004d         51.19    51.19    51.19    51.19    51.19    51.19    51.19   1.0
  ancestor106_it292_11b02ec4    51.19    51.19    51.19    51.19    51.19    51.19    51.19   1.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.56    49.55    49.56    49.56    49.55    49.55    49.55   2.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ancestor1_it0_0875253d162c    51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  ENUMERATE_VM_C1               51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  contemp_01d562cbd7914341      51.61    51.62    51.61    51.61    51.62    51.62    51.62   1.0
  RANDOM_C1                     49.64       --    49.64    49.64    49.64    49.64    49.64   0.0
  contemp_93a8e85a858bba93      52.08    52.09    52.08    52.08    52.09    52.09    52.09   1.0
  contemp_a439da21d6fed983      51.13    51.14    51.13    51.13    51.14    51.14    51.14   1.0

CHARTER s13 CHECKLIST (seeds passing / seeds; thresholds: 5 percent relative; guard 0 added 2026-09-19, see report.py)
  PROCEDURE_REUSE_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [48, 48, 41] vs FRESH [20, 19, 22]
    1_cost_declines_via_accumulation       3/3  reuse_gain C-E per seed [735.9, 716.9, 235.0] vs 5% of FRESH cost [1515.6, 1467.2, 1423.8] (and 0 held)
    2_reproduces_on_heldout                3/3  same test, qualification suite; seeds passing = 3/3
    3_state_causal_FULL_vs_CODE_ONLY       2/3  remainder mean cost FULL [30.58, 30.14, 48.09] vs CODE_ONLY [50.41, 50.41, 47.78]
    4_scramble_or_reset_damages            3/3  eff ACC [48.449, 48.475, 41.476] SCR [20.443, 21.469, 22.474] RESET [20.443, 21.469, 22.475]
    5_transfers_to_fresh_copy              2/3  FULL [30.58, 30.14, 48.09] vs ACC remainder [30.58, 30.14, 48.09]
    6_executable_components_reused         2/3  invocations [82, 81, 61]; ABLATION_ALL cost [50.41, 50.41, 47.78] vs ACC remainder [30.58, 30.14, 48.09]
    7_not_compute_or_storage               2/3  COMPUTE_MATCHED [50.41, 50.41, 47.78] STORAGE_MATCHED [50.41, 50.41, 47.78] vs ACC remainder [30.58, 30.14, 48.09]
  bestever_991405fc52056f75
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [22, 22, 24] vs FRESH [22, 22, 24]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.4] vs 5% of FRESH cost [1525.5, 1514.0, 1456.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.91, 51.65, 48.99] vs CODE_ONLY [49.92, 51.65, 49.0]
    4_scramble_or_reset_damages            0/3  eff ACC [22.442, 22.421, 24.449] SCR [22.442, 22.421, 24.449] RESET [22.442, 22.421, 24.449]
    5_transfers_to_fresh_copy              0/3  FULL [49.91, 51.65, 48.99] vs ACC remainder [49.91, 51.65, 48.99]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [49.92, 51.65, 49.0] vs ACC remainder [49.91, 51.65, 48.99]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.92, 51.65, 49.0] STORAGE_MATCHED [49.92, 51.65, 49.0] vs ACC remainder [49.91, 51.65, 48.99]
  ancestor54_it148_91f269f78aaee613
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [21, 19, 26] vs FRESH [21, 19, 26]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.2] vs 5% of FRESH cost [1533.7, 1528.5, 1343.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.91, 51.91, 49.2] vs CODE_ONLY [51.92, 51.92, 49.21]
    4_scramble_or_reset_damages            0/3  eff ACC [21.46, 19.413, 26.451] SCR [21.46, 19.413, 26.451] RESET [21.46, 19.413, 26.451]
    5_transfers_to_fresh_copy              0/3  FULL [51.91, 51.91, 49.2] vs ACC remainder [51.91, 51.91, 49.2]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.92, 51.92, 49.21] vs ACC remainder [51.91, 51.91, 49.2]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.92, 51.92, 49.21] STORAGE_MATCHED [51.92, 51.92, 49.21] vs ACC remainder [51.91, 51.91, 49.2]
  top1_2a149836950d1044
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 22, 22] vs FRESH [20, 22, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.5] vs 5% of FRESH cost [1540.0, 1509.9, 1522.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.61, 51.88, 51.07] vs CODE_ONLY [50.62, 51.89, 51.08]
    4_scramble_or_reset_damages            0/3  eff ACC [20.426, 22.403, 22.458] SCR [20.426, 22.403, 22.458] RESET [20.426, 22.403, 22.458]
    5_transfers_to_fresh_copy              0/3  FULL [50.61, 51.88, 51.07] vs ACC remainder [50.61, 51.88, 51.07]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [50.62, 51.89, 51.08] vs ACC remainder [50.61, 51.88, 51.07]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.62, 51.89, 51.08] STORAGE_MATCHED [50.62, 51.89, 51.08] vs ACC remainder [50.61, 51.88, 51.07]
  top2_11b02ec4bfb9e0f9
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 22, 22] vs FRESH [20, 22, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.5] vs 5% of FRESH cost [1540.0, 1509.9, 1522.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.61, 51.88, 51.07] vs CODE_ONLY [50.62, 51.89, 51.08]
    4_scramble_or_reset_damages            0/3  eff ACC [20.426, 22.403, 22.458] SCR [20.426, 22.403, 22.458] RESET [20.426, 22.403, 22.458]
    5_transfers_to_fresh_copy              0/3  FULL [50.61, 51.88, 51.07] vs ACC remainder [50.61, 51.88, 51.07]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [50.62, 51.89, 51.08] vs ACC remainder [50.61, 51.88, 51.07]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.62, 51.89, 51.08] STORAGE_MATCHED [50.62, 51.89, 51.08] vs ACC remainder [50.61, 51.88, 51.07]
  top3_13f726732a75004d
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 22, 22] vs FRESH [20, 22, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.5] vs 5% of FRESH cost [1540.0, 1509.9, 1522.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.61, 51.88, 51.07] vs CODE_ONLY [50.62, 51.89, 51.08]
    4_scramble_or_reset_damages            0/3  eff ACC [20.426, 22.403, 22.458] SCR [20.426, 22.403, 22.458] RESET [20.426, 22.403, 22.458]
    5_transfers_to_fresh_copy              0/3  FULL [50.61, 51.88, 51.07] vs ACC remainder [50.61, 51.88, 51.07]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [50.62, 51.89, 51.08] vs ACC remainder [50.61, 51.88, 51.07]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.62, 51.89, 51.08] STORAGE_MATCHED [50.62, 51.89, 51.08] vs ACC remainder [50.61, 51.88, 51.07]
  ancestor106_it292_11b02ec4bfb9e0f9
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 22, 22] vs FRESH [20, 22, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.5] vs 5% of FRESH cost [1540.0, 1509.9, 1522.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.61, 51.88, 51.07] vs CODE_ONLY [50.62, 51.89, 51.08]
    4_scramble_or_reset_damages            0/3  eff ACC [20.426, 22.403, 22.458] SCR [20.426, 22.403, 22.458] RESET [20.426, 22.403, 22.458]
    5_transfers_to_fresh_copy              0/3  FULL [50.61, 51.88, 51.07] vs ACC remainder [50.61, 51.88, 51.07]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [50.62, 51.89, 51.08] vs ACC remainder [50.61, 51.88, 51.07]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.62, 51.89, 51.08] STORAGE_MATCHED [50.62, 51.89, 51.08] vs ACC remainder [50.61, 51.88, 51.07]
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
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.9, -1.9, 0.5] vs 5% of FRESH cost [1513.8, 1465.5, 1422.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.43, 50.43, 47.81] vs CODE_ONLY [50.42, 50.42, 47.8]
    4_scramble_or_reset_damages            0/3  eff ACC [20.37, 19.409, 22.447] SCR [20.37, 19.409, 22.447] RESET [20.37, 19.409, 22.447]
    5_transfers_to_fresh_copy              0/3  FULL [50.43, 50.43, 47.81] vs ACC remainder [50.43, 50.43, 47.81]
    6_executable_components_reused         0/3  invocations [3, 1, 1]; ABLATION_ALL cost [50.42, 50.42, 47.8] vs ACC remainder [50.43, 50.43, 47.81]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.42, 50.42, 47.8] STORAGE_MATCHED [50.42, 50.42, 47.8] vs ACC remainder [50.43, 50.43, 47.81]
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
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.3] vs 5% of FRESH cost [1584.9, 1536.3, 1492.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.68, 52.68, 50.04] vs CODE_ONLY [52.69, 52.69, 50.05]
    4_scramble_or_reset_damages            0/3  eff ACC [18.368, 18.4, 22.445] SCR [18.368, 18.4, 22.445] RESET [18.368, 18.4, 22.445]
    5_transfers_to_fresh_copy              0/3  FULL [52.68, 52.68, 50.04] vs ACC remainder [52.68, 52.68, 50.04]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.69, 52.69, 50.05] vs ACC remainder [52.68, 52.68, 50.04]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.69, 52.69, 50.05] STORAGE_MATCHED [52.69, 52.69, 50.05] vs ACC remainder [52.68, 52.68, 50.04]
  ENUMERATE_VM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 18, 22] vs FRESH [18, 18, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.3] vs 5% of FRESH cost [1584.9, 1536.3, 1492.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.68, 52.68, 50.04] vs CODE_ONLY [52.69, 52.69, 50.05]
    4_scramble_or_reset_damages            0/3  eff ACC [18.368, 18.4, 22.445] SCR [18.368, 18.4, 22.445] RESET [18.368, 18.4, 22.445]
    5_transfers_to_fresh_copy              0/3  FULL [52.68, 52.68, 50.04] vs ACC remainder [52.68, 52.68, 50.04]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.69, 52.69, 50.05] vs ACC remainder [52.68, 52.68, 50.04]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.69, 52.69, 50.05] STORAGE_MATCHED [52.69, 52.69, 50.05] vs ACC remainder [52.68, 52.68, 50.04]
  contemp_01d562cbd7914341
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [10, 10, 12] vs FRESH [10, 10, 12]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.5] vs 5% of FRESH cost [1560.9, 1524.5, 1522.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.88, 51.88, 51.07] vs CODE_ONLY [51.89, 51.89, 51.08]
    4_scramble_or_reset_damages            0/3  eff ACC [10.314, 10.295, 12.298] SCR [10.314, 10.295, 12.298] RESET [10.314, 10.295, 12.298]
    5_transfers_to_fresh_copy              0/3  FULL [51.88, 51.88, 51.07] vs ACC remainder [51.88, 51.88, 51.07]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.89, 51.89, 51.08] vs ACC remainder [51.88, 51.88, 51.07]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.89, 51.89, 51.08] STORAGE_MATCHED [51.89, 51.89, 51.08] vs ACC remainder [51.88, 51.88, 51.07]
  RANDOM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 6, 9] vs FRESH [6, 6, 9]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1493.8, 1515.0, 1489.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.32, 50.5, 49.1] vs CODE_ONLY [49.32, 50.5, 49.1]
    4_scramble_or_reset_damages            0/3  eff ACC [6.205, 6.235, 9.221] SCR [6.205, 6.235, 9.221] RESET [6.205, 6.235, 9.221]
    5_transfers_to_fresh_copy              0/3  FULL [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.32, 50.5, 49.1]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.32, 50.5, 49.1] STORAGE_MATCHED [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
  contemp_93a8e85a858bba93
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [3, 7, 4] vs FRESH [3, 7, 4]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [3.9, 3.8, 3.9] vs 5% of FRESH cost [1566.3, 1519.5, 1566.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.08, 52.08, 52.08] vs CODE_ONLY [52.09, 52.09, 52.09]
    4_scramble_or_reset_damages            0/3  eff ACC [3.18, 7.218, 4.172] SCR [3.18, 7.218, 4.172] RESET [3.18, 7.218, 4.172]
    5_transfers_to_fresh_copy              0/3  FULL [52.08, 52.08, 52.08] vs ACC remainder [52.08, 52.08, 52.08]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.09, 52.09, 52.09] vs ACC remainder [52.08, 52.08, 52.08]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.09, 52.09, 52.09] STORAGE_MATCHED [52.09, 52.09, 52.09] vs ACC remainder [52.08, 52.08, 52.08]
  contemp_a439da21d6fed983
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [1, 1, 1] vs FRESH [1, 1, 1]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [1.8, 1.8, 1.8] vs 5% of FRESH cost [1563.0, 1563.0, 1514.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.04, 52.04, 49.32] vs CODE_ONLY [52.04, 52.04, 49.32]
    4_scramble_or_reset_damages            0/3  eff ACC [1.166, 1.166, 1.149] SCR [1.166, 1.166, 1.149] RESET [1.166, 1.166, 1.149]
    5_transfers_to_fresh_copy              0/3  FULL [52.04, 52.04, 49.32] vs ACC remainder [52.04, 52.04, 49.32]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.04, 52.04, 49.32] vs ACC remainder [52.04, 52.04, 49.32]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.04, 52.04, 49.32] STORAGE_MATCHED [52.04, 52.04, 49.32] vs ACC remainder [52.04, 52.04, 49.32]

MACHINERY OF top1_2a149836950d1044 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   1    32
    task  9:     0    0    0    0    0 |   1    32
    task 19:     0    0    0    0    0 |   1    32
    task 31:     0    0    0    0    0 |   1    32
    task 41:     0    0    0    0    0 |   1    32
    task 49:     0    0    0    0    0 |   1    32
  artifact events: 1 (create 1, delete 0, patch/append 0); invocations by block: {}; edges: 0
    block 0 origin=calibration len=0 state=[[2, 3, 6, 8, 10, 4, 9, 11, 5, 0, 7, 1], [9, 11, 0, 1, 5, 8, 2, 10, 3, 6, 4, 7], 0] instr=[]
  adaptation curve ACC:   256 2073 181 214 18 256 21 251 346 290 4 181 214 214 61 232 232 181 2073 253 52 54 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 29 52 52 52 52
  adaptation curve FRESH: 256 2074 182 214 18 256 21 251 346 290 4 182 214 214 61 232 232 182 2074 253 52 54 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 29 52 52 52 52
  reuse_gain per task:    0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0

BASELINES ON SEARCH SUITE (crius/runs/baselines_c2b): effA effF effR effS  succA  interA interF  reuse_gain  blocks
  ENUMERATE_C1_seed301     21.473 21.473 21.473 21.473   21    3358   3358        0.0    0
  ENUMERATE_C1_seed302     19.412 19.412 19.412 19.412   19   10771  10771        0.0    0
  ENUMERATE_C1_seed303     22.479 22.479 22.479 22.479   22    2548   2548        0.0    0
  ENUMERATE_VM_C1_seed301  21.471 21.471 21.471 21.471   21    3358   3358        6.8    1
  ENUMERATE_VM_C1_seed302  19.397 19.397 19.397 19.397   19   12109  12109        7.0    1
  ENUMERATE_VM_C1_seed303  22.470 22.470 22.470 22.470   22    3428   3428        6.9    1
  PROCEDURE_NOCAL_C1_seed301 21.471 21.471 21.471 21.471   21    3538   3538      -50.2    4
  PROCEDURE_NOCAL_C1_seed302 19.410 19.411 19.411 19.410   19   10917  10915      -46.0    4
  PROCEDURE_NOCAL_C1_seed303 22.477 22.478 22.478 22.477   22    2732   2728      -59.6    6
  PROCEDURE_REUSE_C1_seed301 50.488 21.470 21.481 21.481   50    1338   3718     2287.9    5
  PROCEDURE_REUSE_C1_seed302 49.459 18.410 21.453 21.453   49    4787  11057     6084.9    7
  PROCEDURE_REUSE_C1_seed303 50.492 22.476 22.484 22.483   50     948   2908     1894.4    6
  QUIT_C1_seed301          20.472 20.472 20.472 20.472   20    1907   1907        0.0    0
  QUIT_C1_seed302          17.412 17.412 17.412 17.412   17    9331   9331        0.0    0
  QUIT_C1_seed303          20.479 20.479 20.479 20.479   20    1135   1135        0.0    0
  RANDOM_C1_seed301         7.237  7.237  7.237  7.237    7   32013  32013        0.0    0
  RANDOM_C1_seed302         9.240  9.240  9.240  9.240    9   31692  31692        0.0    0
  RANDOM_C1_seed303        12.282 12.282 12.282 12.282   12   26477  26477        0.0    0
  TABLE_MEMO_C1_seed301    21.472 21.473 21.473 21.472   21    3358   3358      -15.9    0
  TABLE_MEMO_C1_seed302    19.412 19.412 19.412 19.412   19   10771  10771      -13.8    0
  TABLE_MEMO_C1_seed303    22.479 22.479 22.479 22.479   22    2548   2548      -16.7    0

