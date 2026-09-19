CRIUS CAMPAIGN 0 REPORT  run=search_c2b_seeded_s1  arm=seeded
code_commit=713b2773f dirty=True config_hash=c9c87cec99eb063f world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  21.9630   21.5182        10.3728        39         11
    26  20.9390   20.9389        11.4280        41        119
    51  25.9541   25.9537        18.8444        41        219
    76  22.9152   22.9142        11.0197        35        313
   101  21.4186   21.4186        15.3466        43        399
   126  23.9369   23.9365        13.2351        57        483
   151  22.3527   21.0265        11.6879        48        579
   176  18.8742   18.8738        12.7348        46        686
   201  25.4592   25.4592        17.2223        54        810
   226  26.9428   26.9428        17.5229        50        942
   251  20.3894   20.3894         9.1980        46       1072
   276  21.4296   18.5783         9.9874        37       1193
   300  24.4119   22.9089        15.1692        38       1310
  candidates evaluated: 7208   best_ever 28.9071 (6fb59e638d4d9944)  wall 1310s

BEST PROGRAM 6fb59e638d4d9944 (len 43, iteration 10, modification const@13)
  search seed 1010100: fit 31.4541 succ 31/50 inter 5350 steps 30008 ws_cost 15 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [203.396, 1.0], "B": [231.868, 1.0], "C": [36.339, 0.5], "D": [47.46, 0.4], "E": [48.365, 0.125]}
  search seed 1010101: fit 26.3601 succ 26/50 inter 16434 steps 77024 ws_cost 15 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [772.632, 1.0], "B": [809.355, 0.9], "C": [38.079, 0.5], "D": [52.29, 0.0], "E": [50.584, 0.125]}
  listing:
      0  INPUT          R1, num_ops
      1  CONST          R5, 1
      2  CONST          R0, -1
      3  MOV            R2, R1
      4  LT             R5, R0, R2
      5  BRZ            R3, 13
      6  ACT            R1
      7  DIV            R4, R0, R1
      8  MOD            R3, R4, R1
      9  ACT            R3
     10  ACT            R0
     11  ADD            R0, R0, R5
     12  JMP            4
     13  CONST          R0, 2
     14  MUL            R2, R1, R1
     15  ADD            R0, R0, R5
     16  BRZ            R3, 26
     17  ACT            R1
     18  MOD            R3, R0, R1
     19  WS_SREAD       R7, R3, R1
     20  ACT            R3
     21  DIV            R4, R0, R1
     22  MOD            R2, R4, R1
     23  ACT            R3
     24  LT             R3, R0, R2
     25  JMP            15
     26  CONST          R3, 0
     27  MUL            R2, R1, R1
     28  MUL            R2, R2, R1
     29  LT             R3, R0, R2
     30  BRZ            R3, 42
     31  ACT            R1
     32  MOD            R3, R0, R1
     33  ACT            R3
     34  DIV            R4, R0, R1
     35  MOD            R3, R4, R1
     36  ACT            R3
     37  DIV            R4, R4, R1
     38  MOD            R3, R4, R1
     39  ACT            R3
     40  ADD            R0, R0, R5
     41  JMP            29
     42  HALT           
  ancestry (7 steps, newest first): iteration/fitness/modification
    it   10  28.9071  len 43  const@13
    it    9  21.9199  len 43  const@2
    it    7  23.4739  len 43  duplicate@31+3->7
    it    6  16.3226  len 40  insert@16+swap@12,21
    it    5  22.4445  len 39  arg@18.0
    it    2  18.9283  len 39  arg@4.0+insert@13+delete@13
    it    0  16.7949  len 39  arg@22.0
    it    0  17.8392  len 39  seed:ENUMERATE_VM

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7315.4    5.3   74.7
  ancestor147_it296_46ac2c6c  21.748  21.748  21.748  21.748  21.3  21.3    10073    10073       7.2    1.0    0.0
  contemp_4570549ba6d355b2    21.748  21.748  21.748  21.748  21.3  21.3    10075    10075       7.2    1.0    0.0
  ancestor74_it147_44d3fc5c1  21.079  21.079  21.079  21.079  20.7  20.7    10299    10299       7.1    1.0    0.0
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.9    3.7    1.7
  bestever_6fb59e638d4d9944   20.413  20.413  20.413  20.413  20.0  20.0    10157    10157       7.2    1.0    0.0
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ancestor1_it0_0875253d162c  19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  top2_5ccd731a114c89d9       19.418  19.418  19.418  19.418  19.0  19.0     9652     9652       7.1    1.0    0.0
  top3_b60ab7843c75e97f       19.418  19.418  19.418  19.418  19.0  19.0     9652     9652       7.1    1.0    0.0
  top1_84557bca5cfc8dc5       19.413  19.413  19.413  19.413  19.0  19.0    10224    10224       7.2    1.0    0.0
  contemp_05d0e418e346e402    19.045  19.044  19.045  19.045  18.7  18.7    14453    14453       5.8    1.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0
  contemp_d16545d9a4649cc9     4.877   4.877   4.877   4.877   4.7   4.7    34220    34220       7.2    1.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.02/ 455.13   14.92/ 539.10   21.12/  47.94   33.22/  48.94   40.08/  50.52
  ancestor147_it296_46ac2c6c  432.45/ 432.58  465.74/ 465.88   48.27/  48.42   51.22/  51.37   51.91/  52.06
  contemp_4570549ba6d355b2    431.45/ 431.58  465.95/ 466.10   49.09/  49.24   51.14/  51.29   51.87/  52.02
  ancestor74_it147_44d3fc5c1  446.34/ 446.47  475.25/ 475.39   48.73/  48.88   50.59/  50.74   51.91/  52.06
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.14/ 443.81  528.13/ 527.79   47.94/  47.89   48.86/  48.88   50.43/  50.46
  bestever_6fb59e638d4d9944   455.75/ 455.88  454.38/ 454.52   50.60/  50.75   51.66/  51.81   52.29/  52.44
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ancestor1_it0_0875253d162c  495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  ENUMERATE_VM_C1             495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  top2_5ccd731a114c89d9       360.43/ 360.55  493.87/ 494.01   48.55/  48.70   50.69/  50.84   51.90/  52.05
  top3_b60ab7843c75e97f       361.58/ 361.71  495.46/ 495.60   48.71/  48.86   50.85/  51.00   52.07/  52.22
  top1_84557bca5cfc8dc5       410.71/ 410.85  501.14/ 501.28   50.29/  50.44   50.39/  50.53   51.91/  52.06
  contemp_05d0e418e346e402    694.51/ 694.63  656.49/ 656.62   48.58/  48.69   51.55/  51.66   51.90/  52.01
  RANDOM_C1                  1662.62/1662.62 1627.07/1627.07   50.50/  50.50   50.50/  50.50   48.56/  48.56
  contemp_d16545d9a4649cc9   1668.55/1668.68 1737.66/1737.80   50.93/  51.08   51.29/  51.44   52.08/  52.23

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  ancestor147_it296_46ac2c6c     6/36    46     1/30    49     0/12    50     0/12    50    28/30   415    29/30   447
  contemp_4570549ba6d355b2       6/36    47     1/30    49     0/12    50     0/12    50    28/30   414    29/30   448
  ancestor74_it147_44d3fc5c1     4/36    47     1/30    49     0/12    50     0/12    50    28/30   429    29/30   456
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  bestever_6fb59e638d4d9944      3/36    48     2/30    49     0/12    50     0/12    50    27/30   435    28/30   434
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ancestor1_it0_0875253d162c     2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  top2_5ccd731a114c89d9          3/36    47     1/30    49     0/12    50     0/12    50    28/30   346    25/30   475
  top3_b60ab7843c75e97f          3/36    47     1/30    49     0/12    50     0/12    50    28/30   346    25/30   475
  top1_84557bca5cfc8dc5          3/36    48     1/30    48     0/12    50     0/12    50    28/30   394    25/30   482
  contemp_05d0e418e346e402       5/36    47     1/30    50     0/12    50     0/12    50    25/30   668    25/30   632
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610
  contemp_d16545d9a4649cc9       2/36    49     1/30    49     0/12    50     0/12    50     6/30  1604     5/30  1670

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.27    49.53    36.27    36.27    49.53    49.53    49.53   5.0
  ancestor147_it296_46ac2c6c    51.52    51.53    51.52    51.52    51.53    51.53    51.53   1.0
  contemp_4570549ba6d355b2      51.47    51.47    51.47    51.47    51.47    51.47    51.47   1.0
  ancestor74_it147_44d3fc5c1    51.18    51.19    51.18    51.18    51.19    51.19    51.19   1.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.56    49.55    49.56    49.56    49.55    49.55    49.55   2.0
  bestever_6fb59e638d4d9944     51.94    51.95    51.94    51.94    51.95    51.95    51.95   1.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ancestor1_it0_0875253d162c    51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  ENUMERATE_VM_C1               51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  top2_5ccd731a114c89d9         51.23    51.24    51.23    51.23    51.24    51.24    51.24   1.0
  top3_b60ab7843c75e97f         51.39    51.40    51.39    51.39    51.40    51.40    51.40   1.0
  top1_84557bca5cfc8dc5         51.06    51.07    51.06    51.06    51.07    51.07    51.07   1.0
  contemp_05d0e418e346e402      51.71    51.71    51.71    51.71    51.71    51.71    51.71   1.0
  RANDOM_C1                     49.64       --    49.64    49.64    49.64    49.64    49.64   0.0
  contemp_d16545d9a4649cc9      51.64    51.65    51.64    51.64    51.65    51.65    51.65   1.0

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
  ancestor147_it296_46ac2c6cf01fa6bc
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 20, 26] vs FRESH [18, 20, 26]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.4] vs 5% of FRESH cost [1561.8, 1537.9, 1433.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.91, 51.91, 50.75] vs CODE_ONLY [51.92, 51.92, 50.76]
    4_scramble_or_reset_damages            0/3  eff ACC [18.386, 20.416, 26.443] SCR [18.386, 20.416, 26.443] RESET [18.386, 20.416, 26.443]
    5_transfers_to_fresh_copy              0/3  FULL [51.91, 51.91, 50.75] vs ACC remainder [51.91, 51.91, 50.75]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.92, 51.92, 50.76] vs ACC remainder [51.91, 51.91, 50.75]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.92, 51.92, 50.76] STORAGE_MATCHED [51.92, 51.92, 50.76] vs ACC remainder [51.91, 51.91, 50.75]
  contemp_4570549ba6d355b2
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 20, 26] vs FRESH [18, 20, 26]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.4] vs 5% of FRESH cost [1560.6, 1535.6, 1463.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.87, 51.87, 50.66] vs CODE_ONLY [51.88, 51.88, 50.67]
    4_scramble_or_reset_damages            0/3  eff ACC [18.386, 20.416, 26.442] SCR [18.386, 20.416, 26.442] RESET [18.386, 20.416, 26.442]
    5_transfers_to_fresh_copy              0/3  FULL [51.87, 51.87, 50.66] vs ACC remainder [51.87, 51.87, 50.66]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.88, 51.88, 50.67] vs ACC remainder [51.87, 51.87, 50.66]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.88, 51.88, 50.67] STORAGE_MATCHED [51.88, 51.88, 50.67] vs ACC remainder [51.87, 51.87, 50.66]
  ancestor74_it147_44d3fc5c15e235c6
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 20, 24] vs FRESH [18, 20, 24]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.3] vs 5% of FRESH cost [1561.8, 1519.2, 1450.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.91, 51.91, 49.72] vs CODE_ONLY [51.92, 51.92, 49.73]
    4_scramble_or_reset_damages            0/3  eff ACC [18.383, 20.415, 24.44] SCR [18.383, 20.415, 24.44] RESET [18.383, 20.415, 24.44]
    5_transfers_to_fresh_copy              0/3  FULL [51.91, 51.91, 49.72] vs ACC remainder [51.91, 51.91, 49.72]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.92, 51.92, 49.73] vs ACC remainder [51.91, 51.91, 49.72]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.92, 51.92, 49.73] STORAGE_MATCHED [51.92, 51.92, 49.73] vs ACC remainder [51.91, 51.91, 49.72]
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
  bestever_6fb59e638d4d9944
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 18, 23] vs FRESH [19, 18, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.4] vs 5% of FRESH cost [1573.1, 1555.4, 1511.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.29, 52.29, 51.24] vs CODE_ONLY [52.3, 52.3, 51.25]
    4_scramble_or_reset_damages            0/3  eff ACC [19.383, 18.413, 23.444] SCR [19.383, 18.413, 23.444] RESET [19.383, 18.413, 23.444]
    5_transfers_to_fresh_copy              0/3  FULL [52.29, 52.29, 51.24] vs ACC remainder [52.29, 52.29, 51.24]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.3, 52.3, 51.25] vs ACC remainder [52.29, 52.29, 51.24]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.3, 52.3, 51.25] STORAGE_MATCHED [52.3, 52.3, 51.25] vs ACC remainder [52.29, 52.29, 51.24]
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
  top2_5ccd731a114c89d9
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [15, 20, 22] vs FRESH [15, 20, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.3] vs 5% of FRESH cost [1561.5, 1528.2, 1437.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.9, 51.9, 49.88] vs CODE_ONLY [51.91, 51.91, 49.89]
    4_scramble_or_reset_damages            0/3  eff ACC [15.361, 20.444, 22.45] SCR [15.361, 20.444, 22.45] RESET [15.361, 20.444, 22.45]
    5_transfers_to_fresh_copy              0/3  FULL [51.9, 51.9, 49.88] vs ACC remainder [51.9, 51.9, 49.88]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.91, 51.91, 49.89] vs ACC remainder [51.9, 51.9, 49.88]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.91, 51.91, 49.89] STORAGE_MATCHED [51.91, 51.91, 49.89] vs ACC remainder [51.9, 51.9, 49.88]
  top3_b60ab7843c75e97f
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [15, 20, 22] vs FRESH [15, 20, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.3] vs 5% of FRESH cost [1566.6, 1533.2, 1442.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.07, 52.07, 50.04] vs CODE_ONLY [52.08, 52.08, 50.05]
    4_scramble_or_reset_damages            0/3  eff ACC [15.36, 20.444, 22.45] SCR [15.36, 20.444, 22.45] RESET [15.36, 20.444, 22.45]
    5_transfers_to_fresh_copy              0/3  FULL [52.07, 52.07, 50.04] vs ACC remainder [52.07, 52.07, 50.04]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.08, 52.08, 50.05] vs ACC remainder [52.07, 52.07, 50.04]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.08, 52.08, 50.05] STORAGE_MATCHED [52.08, 52.08, 50.05] vs ACC remainder [52.07, 52.07, 50.04]
  top1_84557bca5cfc8dc5
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [16, 20, 21] vs FRESH [16, 20, 21]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.4] vs 5% of FRESH cost [1563.8, 1519.2, 1498.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.91, 51.91, 49.37] vs CODE_ONLY [51.92, 51.92, 49.38]
    4_scramble_or_reset_damages            0/3  eff ACC [16.362, 20.446, 21.433] SCR [16.362, 20.446, 21.433] RESET [16.362, 20.446, 21.433]
    5_transfers_to_fresh_copy              0/3  FULL [51.91, 51.91, 49.37] vs ACC remainder [51.91, 51.91, 49.37]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.92, 51.92, 49.38] vs ACC remainder [51.91, 51.91, 49.37]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.92, 51.92, 49.38] STORAGE_MATCHED [51.92, 51.92, 49.38] vs ACC remainder [51.91, 51.91, 49.37]
  contemp_05d0e418e346e402
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 17, 21] vs FRESH [18, 17, 21]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [3.3, 3.3, 3.2] vs 5% of FRESH cost [1547.8, 1520.8, 1482.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.9, 51.9, 51.32] vs CODE_ONLY [51.91, 51.91, 51.33]
    4_scramble_or_reset_damages            0/3  eff ACC [18.397, 17.353, 21.384] SCR [18.397, 17.353, 21.384] RESET [18.397, 17.353, 21.384]
    5_transfers_to_fresh_copy              0/3  FULL [51.9, 51.9, 51.32] vs ACC remainder [51.9, 51.9, 51.32]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.91, 51.91, 51.33] vs ACC remainder [51.9, 51.9, 51.32]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.91, 51.91, 51.33] STORAGE_MATCHED [51.91, 51.91, 51.33] vs ACC remainder [51.9, 51.9, 51.32]
  RANDOM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 6, 9] vs FRESH [6, 6, 9]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1493.8, 1515.0, 1489.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.32, 50.5, 49.1] vs CODE_ONLY [49.32, 50.5, 49.1]
    4_scramble_or_reset_damages            0/3  eff ACC [6.205, 6.235, 9.221] SCR [6.205, 6.235, 9.221] RESET [6.205, 6.235, 9.221]
    5_transfers_to_fresh_copy              0/3  FULL [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.32, 50.5, 49.1]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.32, 50.5, 49.1] STORAGE_MATCHED [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
  contemp_d16545d9a4649cc9
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [9, 3, 2] vs FRESH [9, 3, 2]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.5] vs 5% of FRESH cost [1566.9, 1539.9, 1528.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.08, 52.08, 50.76] vs CODE_ONLY [52.09, 52.09, 50.77]
    4_scramble_or_reset_damages            0/3  eff ACC [9.3, 3.183, 2.149] SCR [9.3, 3.183, 2.149] RESET [9.3, 3.183, 2.149]
    5_transfers_to_fresh_copy              0/3  FULL [52.08, 52.08, 50.76] vs ACC remainder [52.08, 52.08, 50.76]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.09, 52.09, 50.77] vs ACC remainder [52.08, 52.08, 50.76]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.09, 52.09, 50.77] STORAGE_MATCHED [52.09, 52.09, 50.77] vs ACC remainder [52.08, 52.08, 50.76]

MACHINERY OF top1_84557bca5cfc8dc5 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   1    32
    task  9:     0    0    0    0    0 |   1    32
    task 19:     0    0    0    0    0 |   1    32
    task 31:     0    0    0    0    0 |   1    32
    task 41:     0    0    0    0    0 |   1    32
    task 49:     0    0    0    0    0 |   1    32
  artifact events: 1 (create 1, delete 0, patch/append 0); invocations by block: {}; edges: 0
    block 0 origin=calibration len=0 state=[[2, 3, 6, 8, 10, 4, 9, 11, 5, 0, 7, 1], [9, 11, 0, 1, 5, 8, 2, 10, 3, 6, 4, 7], 0] instr=[]
  adaptation curve ACC:   88 1638 91 2073 88 70 101 677 147 178 60 91 2073 2073 11 2073 2073 91 1638 110 52 54 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
  adaptation curve FRESH: 88 1638 91 2074 88 71 101 677 147 178 60 91 2074 2074 11 2074 2074 91 1638 110 52 54 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
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

