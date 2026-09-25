CRIUS CAMPAIGN 0 REPORT  run=search_c2b_recombination_s1  arm=recombination
code_commit=713b2773f dirty=True config_hash=c9c87cec99eb063f world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  21.9592   20.9509        11.4957        39         20
    26  23.9548   21.7543         8.2883        73        114
    51  26.4495   24.7011        17.5402        70        202
    76  22.9138   21.1661        17.2850        77        302
   101  22.4176   22.4176        16.1716        93        394
   126  24.4329   24.4329        16.8771        89        478
   151  23.3897   21.1531        16.3587        89        571
   176  20.3819   20.3819        12.4345        81        674
   201  25.4503   24.1054        17.7581        76        773
   226  26.9373   26.9373        20.3838        63        889
   251  16.8393   16.8393        12.0602        52       1010
   276  19.9236   19.9236        14.9811        80       1119
   300  23.9185   23.4771        20.1743        80       1214
  candidates evaluated: 7208   best_ever 28.4727 (e93b41bdc39df122)  wall 1214s

BEST PROGRAM e93b41bdc39df122 (len 57, iteration 240, modification const@36+swap@8,12+const@24)
  search seed 1012400: fit 26.4760 succ 26/50 inter 2796 steps 15745 ws_cost 315 blocks 1 invoked 0 ws_bytes 200
    by stage (mean cost, success rate): {"A": [76.672, 1.0], "B": [84.222, 1.0], "C": [45.287, 0.167], "D": [44.473, 0.2], "E": [44.936, 0.25]}
  search seed 1012401: fit 30.4694 succ 30/50 inter 3565 steps 19362 ws_cost 315 blocks 1 invoked 0 ws_bytes 200
    by stage (mean cost, success rate): {"A": [101.55, 1.0], "B": [147.255, 1.0], "C": [35.758, 0.5], "D": [45.603, 0.3], "E": [48.574, 0.125]}
  listing:
      0  INPUT          R1, num_ops
      1  PINVOKE        R6, R3
      2  CONST          R5, -1
      3  BRZ            R3, 7
      4  ADD            R0, R0, R5
      5  WS_LINK_GET    R6, R4, R5
      6  LT             R2, R0, R2
      7  WS_REC_NEW     R0
      8  WS_REC_NEW     R0
      9  JMP            45
     10  HALT           
     11  ACT            R6
     12  ADD            R0, R0, R5
     13  DIV            R1, R7, R7
     14  MOD            R6, R6, R6
     15  ACT            R0
     16  JMP            35
     17  WS_APPEND      R7, R3
     18  BLK_STATE_GET  R7, R1, R2
     19  JMP            3
     20  MOD            R3, R0, R1
     21  CONST          R0, 3
     22  LT             R3, R0, R1
     23  WS_LINK        R5, R2, R0
     24  CONST          R0, -4
     25  MOD            R3, R0, R1
     26  WS_LINK        R7, R6, R4
     27  ADD            R0, R0, R5
     28  JMP            41
     29  HALT           
     30  MOD            R3, R4, R1
     31  MOD            R3, R0, R1
     32  BLK_APPEND     R5, R0
     33  WS_REC_NEW     R0
     34  MOV            R5, R5
     35  ACT            R3
     36  CONST          R0, -16
     37  BRZ            R3, 18
     38  CONST          R2, -16
     39  MOV            R0, R5
     40  VLEN           R2, R7
     41  ACT            R1
     42  NOT            R5, R4
     43  BRZ            R3, 39
     44  WS_WRITE       R7, R1
     45  ACT            R1
     46  MOD            R3, R0, R1
     47  DIV            R4, R0, R1
     48  ACT            R3
     49  MOD            R3, R4, R1
     50  ACT            R3
     51  DIV            R4, R4, R1
     52  MOD            R3, R4, R1
     53  ACT            R3
     54  ADD            R0, R0, R5
     55  JMP            45
     56  ACT            R4
  ancestry (128 steps, newest first): iteration/fitness/modification
    it  240  28.4727  len 57  const@36+swap@8,12+const@24
    it  237  23.9296  len 57  delete@57
    it  236  23.9376  len 58  arg@23.1
    it  235  26.4700  len 58  const@21
    it  234  22.9469  len 58  delete@3
    it  232  22.9493  len 59  delete@38+const@3
    it  230  22.9462  len 60  const@22+delete@27
    it  227  23.4233  len 61  delete@22+delete@44
    it  225  23.4167  len 63  delete@40
    it  223  21.4401  len 64  delete@3+const@39
    it  222  18.3772  len 65  delete@37+const@4+arg@15.2
    it  221  27.4674  len 66  delete@14+const@24
    it  220  20.4089  len 67  const@28
    it  218  19.8649  len 67  delete@21+delete@9
    it  216  19.8792  len 69  delete@20
    ... 114 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7315.4    5.3   74.7
  ancestor81_it158_df214817d  21.412  20.080  20.745  21.412  21.0  19.7    10369    10205    -165.5    1.0    0.0
  bestever_e93b41bdc39df122   20.746  19.057  19.746  20.746  20.3  18.7    10347    12995    2748.7    1.0    0.0
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.9    3.7    1.7
  top2_026d7a5ac69d8180       20.072  19.053  19.405  20.072  19.7  18.7    11189    13491    2392.2    1.0    0.0
  top3_6262fd973769bf42       20.072  19.053  19.405  20.072  19.7  18.7    11189    13491    2392.2    1.0    0.0
  contemp_b2a202adf3cb20e0    20.072  19.053  19.405  20.072  19.7  18.7    11189    13491    2392.2    1.0    0.0
  ancestor161_it298_ac1728af  20.072  19.053  19.405  20.072  19.7  18.7    11189    13491    2392.2    1.0    0.0
  contemp_bb1d31d9e7ad3e30    20.072  19.052  19.405  20.072  19.7  18.7    11189    13491    2392.2    1.0    0.0
  contemp_313d4f8712dbe061    20.070  19.050  19.403  20.070  19.7  18.7    11189    13491    2438.2    1.0    0.0
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ancestor1_it0_0875253d162c  19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  top1_075631c226922b13       19.053  19.053  19.053  19.053  18.7  18.7    13491    13491       7.1    1.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.02/ 455.13   14.92/ 539.10   21.12/  47.94   33.22/  48.94   40.08/  50.52
  ancestor81_it158_df214817d  443.52/ 455.89  487.32/ 454.64   48.30/  50.71   50.85/  50.54   50.72/  52.21
  bestever_e93b41bdc39df122   444.21/ 495.71  485.21/ 706.41   47.36/  48.80   49.84/  51.20   51.51/  50.37
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.14/ 443.81  528.13/ 527.79   47.94/  47.89   48.86/  48.88   50.43/  50.46
  top2_026d7a5ac69d8180       525.57/ 535.72  490.42/ 717.91   48.40/  49.27   49.72/  51.08   51.34/  50.33
  top3_6262fd973769bf42       525.57/ 535.72  490.42/ 717.91   48.40/  49.27   49.72/  51.08   51.34/  50.33
  contemp_b2a202adf3cb20e0    525.57/ 535.72  490.42/ 717.91   48.40/  49.27   49.72/  51.08   51.34/  50.33
  ancestor161_it298_ac1728af  525.58/ 535.73  490.43/ 717.92   48.41/  49.28   49.73/  51.09   51.35/  50.34
  contemp_bb1d31d9e7ad3e30    525.60/ 535.75  490.45/ 717.94   48.43/  49.30   49.75/  51.11   51.37/  50.36
  contemp_313d4f8712dbe061    535.80/ 546.14  499.96/ 731.83   49.36/  50.24   50.70/  52.08   52.35/  51.31
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ancestor1_it0_0875253d162c  495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  ENUMERATE_VM_C1             495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  top1_075631c226922b13       535.49/ 535.61  717.65/ 717.80   49.01/  49.16   50.82/  50.97   50.07/  50.22
  RANDOM_C1                  1662.62/1662.62 1627.07/1627.07   50.50/  50.50   50.50/  50.50   48.56/  48.56

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  ancestor81_it158_df214817d     6/36    46     1/30    49     1/12    47     0/12    50    27/30   426    28/30   468
  bestever_e93b41bdc39df122      5/36    45     2/30    48     1/12    50     1/12    49    27/30   427    25/30   466
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  top2_026d7a5ac69d8180          4/36    46     2/30    48     1/12    49     1/12    49    26/30   505    25/30   471
  top3_6262fd973769bf42          4/36    46     2/30    48     1/12    49     1/12    49    26/30   505    25/30   471
  contemp_b2a202adf3cb20e0       4/36    46     2/30    48     1/12    49     1/12    49    26/30   505    25/30   471
  ancestor161_it298_ac1728af     4/36    46     2/30    48     1/12    49     1/12    49    26/30   505    25/30   471
  contemp_bb1d31d9e7ad3e30       4/36    46     2/30    48     1/12    49     1/12    49    26/30   505    25/30   471
  contemp_313d4f8712dbe061       4/36    46     2/30    48     1/12    49     1/12    49    26/30   505    25/30   471
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ancestor1_it0_0875253d162c     2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  top1_075631c226922b13          4/36    47     2/30    49     0/12    50     1/12    46    26/30   515    23/30   691
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.27    49.53    36.27    36.27    49.53    49.53    49.53   5.0
  ancestor81_it158_df214817d    50.79    50.80    51.14    50.79    51.14    51.14    51.14   1.0
  bestever_e93b41bdc39df122     50.58    50.59    50.74    50.58    50.75    50.75    50.75   1.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.56    49.55    49.56    49.56    49.55    49.55    49.55   2.0
  top2_026d7a5ac69d8180         50.44    50.45    50.71    50.44    50.72    50.72    50.72   1.0
  top3_6262fd973769bf42         50.44    50.45    50.71    50.44    50.72    50.72    50.72   1.0
  contemp_b2a202adf3cb20e0      50.44    50.45    50.71    50.44    50.72    50.72    50.72   1.0
  ancestor161_it298_ac1728af    50.45    50.46    50.72    50.45    50.73    50.73    50.73   1.0
  contemp_bb1d31d9e7ad3e30      50.47    50.48    50.74    50.47    50.75    50.75    50.75   1.0
  contemp_313d4f8712dbe061      51.44    51.44    51.71    51.44    51.72    51.72    51.72   1.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ancestor1_it0_0875253d162c    51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  ENUMERATE_VM_C1               51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  top1_075631c226922b13         50.49    50.49    50.49    50.49    50.49    50.49    50.49   1.0
  RANDOM_C1                     49.64       --    49.64    49.64    49.64    49.64    49.64   0.0

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
  ancestor81_it158_df214817d85f3e58
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 19, 25] vs FRESH [18, 18, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [7.7, 55.4, 50.1] vs 5% of FRESH cost [1566.3, 1551.7, 1476.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.06, 50.27, 50.04] vs CODE_ONLY [52.07, 52.07, 49.3]
    4_scramble_or_reset_damages            0/3  eff ACC [19.382, 19.413, 25.441] SCR [19.382, 19.413, 25.441] RESET [19.382, 19.413, 23.44]
    5_transfers_to_fresh_copy              0/3  FULL [52.06, 50.27, 50.04] vs ACC remainder [52.06, 50.27, 50.04]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.07, 50.28, 50.05] vs ACC remainder [52.06, 50.27, 50.04]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.07, 52.07, 49.3] STORAGE_MATCHED [52.07, 52.07, 49.3] vs ACC remainder [52.06, 50.27, 50.04]
  bestever_e93b41bdc39df122
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [17, 19, 25] vs FRESH [17, 17, 22]
    1_cost_declines_via_accumulation       1/3  reuse_gain C-E per seed [-37.0, -62.2, 164.4] vs 5% of FRESH cost [1510.9, 1466.2, 1524.5] (and 0 held)
    2_reproduces_on_heldout                1/3  same test, qualification suite; seeds passing = 1/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.37, 51.95, 48.43] vs CODE_ONLY [51.96, 50.51, 49.77]
    4_scramble_or_reset_damages            0/3  eff ACC [17.368, 19.434, 25.436] SCR [17.368, 19.434, 25.436] RESET [17.368, 20.434, 21.435]
    5_transfers_to_fresh_copy              0/3  FULL [51.37, 51.95, 48.43] vs ACC remainder [51.37, 51.95, 48.43]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.37, 51.96, 48.44] vs ACC remainder [51.37, 51.95, 48.43]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.96, 50.51, 49.77] STORAGE_MATCHED [51.96, 50.51, 49.77] vs ACC remainder [51.37, 51.95, 48.43]
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
  top2_026d7a5ac69d8180
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [17, 18, 24] vs FRESH [17, 17, 22]
    1_cost_declines_via_accumulation       1/3  reuse_gain C-E per seed [-37.1, -42.5, 127.0] vs 5% of FRESH cost [1507.4, 1485.5, 1521.0] (and 0 held)
    2_reproduces_on_heldout                1/3  same test, qualification suite; seeds passing = 1/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.11, 52.04, 48.17] vs CODE_ONLY [52.05, 50.43, 49.68]
    4_scramble_or_reset_damages            0/3  eff ACC [17.363, 18.416, 24.436] SCR [17.363, 18.416, 24.436] RESET [17.363, 19.417, 21.435]
    5_transfers_to_fresh_copy              0/3  FULL [51.11, 52.04, 48.17] vs ACC remainder [51.11, 52.04, 48.17]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.12, 52.05, 48.18] vs ACC remainder [51.11, 52.04, 48.17]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.05, 50.43, 49.68] STORAGE_MATCHED [52.05, 50.43, 49.68] vs ACC remainder [51.11, 52.04, 48.17]
  top3_6262fd973769bf42
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [17, 18, 24] vs FRESH [17, 17, 22]
    1_cost_declines_via_accumulation       1/3  reuse_gain C-E per seed [-37.1, -42.5, 127.0] vs 5% of FRESH cost [1507.4, 1485.5, 1521.0] (and 0 held)
    2_reproduces_on_heldout                1/3  same test, qualification suite; seeds passing = 1/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.11, 52.04, 48.17] vs CODE_ONLY [52.05, 50.43, 49.68]
    4_scramble_or_reset_damages            0/3  eff ACC [17.363, 18.416, 24.436] SCR [17.363, 18.416, 24.436] RESET [17.363, 19.417, 21.435]
    5_transfers_to_fresh_copy              0/3  FULL [51.11, 52.04, 48.17] vs ACC remainder [51.11, 52.04, 48.17]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.12, 52.05, 48.18] vs ACC remainder [51.11, 52.04, 48.17]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.05, 50.43, 49.68] STORAGE_MATCHED [52.05, 50.43, 49.68] vs ACC remainder [51.11, 52.04, 48.17]
  contemp_b2a202adf3cb20e0
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [17, 18, 24] vs FRESH [17, 17, 22]
    1_cost_declines_via_accumulation       1/3  reuse_gain C-E per seed [-37.1, -42.5, 127.0] vs 5% of FRESH cost [1507.4, 1485.5, 1521.0] (and 0 held)
    2_reproduces_on_heldout                1/3  same test, qualification suite; seeds passing = 1/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.11, 52.04, 48.17] vs CODE_ONLY [52.05, 50.43, 49.68]
    4_scramble_or_reset_damages            0/3  eff ACC [17.363, 18.416, 24.436] SCR [17.363, 18.416, 24.436] RESET [17.363, 19.417, 21.435]
    5_transfers_to_fresh_copy              0/3  FULL [51.11, 52.04, 48.17] vs ACC remainder [51.11, 52.04, 48.17]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.12, 52.05, 48.18] vs ACC remainder [51.11, 52.04, 48.17]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.05, 50.43, 49.68] STORAGE_MATCHED [52.05, 50.43, 49.68] vs ACC remainder [51.11, 52.04, 48.17]
  ancestor161_it298_ac1728af72f92480
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [17, 18, 24] vs FRESH [17, 17, 22]
    1_cost_declines_via_accumulation       1/3  reuse_gain C-E per seed [-37.1, -42.5, 127.0] vs 5% of FRESH cost [1507.7, 1485.8, 1521.3] (and 0 held)
    2_reproduces_on_heldout                1/3  same test, qualification suite; seeds passing = 1/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.12, 52.05, 48.18] vs CODE_ONLY [52.06, 50.44, 49.69]
    4_scramble_or_reset_damages            0/3  eff ACC [17.363, 18.416, 24.436] SCR [17.363, 18.416, 24.436] RESET [17.363, 19.417, 21.435]
    5_transfers_to_fresh_copy              0/3  FULL [51.12, 52.05, 48.18] vs ACC remainder [51.12, 52.05, 48.18]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.13, 52.06, 48.19] vs ACC remainder [51.12, 52.05, 48.18]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.06, 50.44, 49.69] STORAGE_MATCHED [52.06, 50.44, 49.69] vs ACC remainder [51.12, 52.05, 48.18]
  contemp_bb1d31d9e7ad3e30
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [17, 18, 24] vs FRESH [17, 17, 22]
    1_cost_declines_via_accumulation       1/3  reuse_gain C-E per seed [-37.1, -42.5, 127.0] vs 5% of FRESH cost [1508.3, 1486.4, 1521.9] (and 0 held)
    2_reproduces_on_heldout                1/3  same test, qualification suite; seeds passing = 1/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.14, 52.07, 48.2] vs CODE_ONLY [52.08, 50.46, 49.71]
    4_scramble_or_reset_damages            0/3  eff ACC [17.363, 18.416, 24.436] SCR [17.363, 18.416, 24.436] RESET [17.363, 19.417, 21.435]
    5_transfers_to_fresh_copy              0/3  FULL [51.14, 52.07, 48.2] vs ACC remainder [51.14, 52.07, 48.2]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.15, 52.08, 48.21] vs ACC remainder [51.14, 52.07, 48.2]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.08, 50.46, 49.71] STORAGE_MATCHED [52.08, 50.46, 49.71] vs ACC remainder [51.14, 52.07, 48.2]
  contemp_313d4f8712dbe061
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [17, 18, 24] vs FRESH [17, 17, 22]
    1_cost_declines_via_accumulation       1/3  reuse_gain C-E per seed [-37.8, -43.2, 129.2] vs 5% of FRESH cost [1537.0, 1514.8, 1550.9] (and 0 held)
    2_reproduces_on_heldout                1/3  same test, qualification suite; seeds passing = 1/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.12, 53.06, 49.13] vs CODE_ONLY [53.07, 51.42, 50.66]
    4_scramble_or_reset_damages            0/3  eff ACC [17.361, 18.415, 24.435] SCR [17.361, 18.415, 24.435] RESET [17.361, 19.415, 21.434]
    5_transfers_to_fresh_copy              0/3  FULL [52.12, 53.06, 49.13] vs ACC remainder [52.12, 53.06, 49.13]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.13, 53.07, 49.13] vs ACC remainder [52.12, 53.06, 49.13]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [53.07, 51.42, 50.66] STORAGE_MATCHED [53.07, 51.42, 50.66] vs ACC remainder [52.12, 53.06, 49.13]
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
  top1_075631c226922b13
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [17, 17, 22] vs FRESH [17, 17, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.4, 4.4, 4.5] vs 5% of FRESH cost [1504.1, 1482.2, 1517.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.45, 51.06, 50.95] vs CODE_ONLY [49.46, 51.07, 50.96]
    4_scramble_or_reset_damages            0/3  eff ACC [17.355, 17.372, 22.43] SCR [17.355, 17.372, 22.43] RESET [17.355, 17.372, 22.43]
    5_transfers_to_fresh_copy              0/3  FULL [49.45, 51.06, 50.95] vs ACC remainder [49.45, 51.06, 50.95]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [49.46, 51.07, 50.96] vs ACC remainder [49.45, 51.06, 50.95]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.46, 51.07, 50.96] STORAGE_MATCHED [49.46, 51.07, 50.96] vs ACC remainder [49.45, 51.06, 50.95]
  RANDOM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 6, 9] vs FRESH [6, 6, 9]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1493.8, 1515.0, 1489.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.32, 50.5, 49.1] vs CODE_ONLY [49.32, 50.5, 49.1]
    4_scramble_or_reset_damages            0/3  eff ACC [6.205, 6.235, 9.221] SCR [6.205, 6.235, 9.221] RESET [6.205, 6.235, 9.221]
    5_transfers_to_fresh_copy              0/3  FULL [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.32, 50.5, 49.1]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.32, 50.5, 49.1] STORAGE_MATCHED [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]

MACHINERY OF top1_075631c226922b13 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   1    32
    task  9:     0    0    0    0    0 |   1    32
    task 19:     0    0    0    0    0 |   1    32
    task 31:     0    0    0    0    0 |   1    32
    task 41:     0    0    0    0    0 |   1    32
    task 49:     0    0    0    0    0 |   1    32
  artifact events: 1 (create 1, delete 0, patch/append 0); invocations by block: {}; edges: 0
    block 0 origin=calibration len=0 state=[[2, 3, 6, 8, 10, 4, 9, 11, 5, 0, 7, 1], [9, 11, 0, 1, 5, 8, 2, 10, 3, 6, 4, 7], 0] instr=[]
  adaptation curve ACC:   415 1517 41 2073 415 415 153 556 26 57 113 41 2073 2073 415 2073 2073 41 1517 214 52 38 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 7 52 52 52 52 52 52 52
  adaptation curve FRESH: 415 1517 42 2074 415 415 154 556 26 57 113 42 2074 2074 415 2074 2074 42 1517 214 52 39 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 7 52 52 52 52 52 52 52
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

