CRIUS CAMPAIGN 0 REPORT  run=search_c2d_recombination_s3  arm=recombination
code_commit=52c58d0d4 dirty=True config_hash=7ab056c39e1821fd world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  20.9038   19.9571         8.5032        40         17
    26  23.4329   23.4329        19.4114        62        113
    51  21.9225   20.8210        12.4932        62        193
    76  21.9354   21.9354        13.6619        49        273
   101  19.8982   19.8979        13.2723        46        352
   126  24.9194   24.9194        18.4710        33        443
   151  23.4508   22.5649        18.9186        34        535
   176  25.4667   25.4667        11.5624        24        647
   201  22.9628   22.9628        14.5964        21        754
   226  20.4348   20.4348        10.3956        19        854
   251  22.9683   22.5072        12.0344        18        961
   276  22.9313   22.9313        11.8190        16       1062
   300  22.4369   22.4369        12.7393        15       1181
  candidates evaluated: 7208   best_ever 28.9769 (258cf8756ba56722)  wall 1181s

BEST PROGRAM 258cf8756ba56722 (len 35, iteration 122, modification delete@8+delete@8)
  search seed 3011220: fit 22.4661 succ 22/50 inter 3974 steps 19108 ws_cost 15 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [136.187, 1.0], "B": [130.368, 1.0], "C": [47.183, 0.167], "D": [51.86, 0.0], "E": [51.86, 0.0]}
  search seed 3011221: fit 35.4878 succ 35/50 inter 1383 steps 12219 ws_cost 15 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [25.267, 1.0], "B": [22.247, 1.0], "C": [36.886, 0.417], "D": [40.739, 0.4], "E": [22.522, 0.75]}
  listing:
      0  INPUT          R1, num_ops
      1  CONST          R5, -17
      2  BRZ            R3, 20
      3  LT             R3, R0, R2
      4  ACT            R0
      5  LT             R3, R0, R2
      6  HALT           
      7  LT             R3, R0, R2
      8  LT             R3, R0, R2
      9  WS_LINK        R3, R1, R4
     10  MOD            R0, R4, R3
     11  DIV            R4, R4, R1
     12  ACTI           1
     13  DIV            R4, R0, R1
     14  BRZ            R3, 6
     15  CONST          R3, -18
     16  BRZ            R3, 28
     17  BRZ            R0, 11
     18  BRZ            R3, 6
     19  JMP            19
     20  ADD            R0, R0, R5
     21  ACT            R1
     22  MOD            R3, R0, R1
     23  ACT            R3
     24  DIV            R4, R0, R1
     25  MOD            R3, R4, R1
     26  ACT            R3
     27  DIV            R4, R4, R1
     28  MOD            R3, R4, R1
     29  ACT            R3
     30  ADD            R0, R0, R5
     31  JMP            21
     32  BLK_COPY       R4, R5
     33  ACT            R3
     34  ACT            R1
  ancestry (61 steps, newest first): iteration/fitness/modification
    it  122  28.9769  len 35  delete@8+delete@8
    it  116  22.4530  len 37  replace@34
    it  114  20.4162  len 37  delete@6+swap@5,12+delete@19
    it  113  25.4598  len 39  delete@22+delete@23
    it  112  26.4444  len 41  delete@3+const@18
    it  111  23.9083  len 42  arg@10.0
    it  105  20.3947  len 42  delete@15+replace@16
    it  102  21.9372  len 43  delete@19
    it  101  19.8979  len 44  delete@20+splice@42<-donor[36:37]:714a18c85e89eec6
    it   98  21.9178  len 44  swap@20,4
    it   94  21.9672  len 44  arg@30.0+swap@11,43+delete@29
    it   93  23.9324  len 45  delete@44
    it   92  21.4478  len 46  const@24+arg@4.0
    it   90  24.9303  len 46  const@24
    it   89  22.9343  len 46  replace@44+arg@41.0+delete@11
    ... 47 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7315.4    5.3   74.7
  top1_a2f32643a319c980       22.097  22.097  22.097  22.097  21.7  21.7     8252     8252       7.1    1.0    0.0
  top2_20ab751c3d0dd7b3       22.097  22.097  22.097  22.097  21.7  21.7     8252     8252       7.1    1.0    0.0
  top3_45c83b353370df5e       22.097  22.097  22.097  22.097  21.7  21.7     8252     8252       7.1    1.0    0.0
  contemp_39104483a82b37c6    22.097  22.097  22.097  22.097  21.7  21.7     8252     8252       7.1    1.0    0.0
  ancestor91_it271_ba21bb27b  22.097  22.097  22.097  22.097  21.7  21.7     8252     8252       7.1    1.0    0.0
  bestever_258cf8756ba56722   22.084  22.084  22.084  22.084  21.7  21.7     9745     9745       7.1    1.0    0.0
  ancestor46_it85_108f4c7441  22.084  22.084  22.084  22.084  21.7  21.7     9745     9745       7.1    1.0    0.0
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.9    3.7    1.7
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ancestor1_it0_0875253d162c  19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  contemp_7a9653d1023b7ba7    13.662  13.662  13.662  13.662  13.3  13.3    20450    20450       6.7    1.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0
  contemp_ed8dbe6ab031c1eb     3.187   3.187   3.187   3.187   3.0   3.0    36850    36850       7.2    1.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.02/ 455.13   14.92/ 539.10   21.12/  47.94   33.22/  48.94   40.08/  50.52
  top1_a2f32643a319c980       347.67/ 347.80  362.06/ 362.20   49.41/  49.55   51.17/  51.32   49.65/  49.80
  top2_20ab751c3d0dd7b3       347.67/ 347.80  362.06/ 362.20   49.41/  49.55   51.17/  51.32   49.65/  49.80
  top3_45c83b353370df5e       347.67/ 347.80  362.06/ 362.20   49.41/  49.55   51.17/  51.32   49.65/  49.80
  contemp_39104483a82b37c6    347.68/ 347.81  362.07/ 362.21   49.42/  49.56   51.18/  51.33   49.66/  49.81
  ancestor91_it271_ba21bb27b  347.67/ 347.80  362.06/ 362.20   49.41/  49.55   51.17/  51.32   49.65/  49.80
  bestever_258cf8756ba56722   366.50/ 366.62  499.80/ 499.95   48.34/  48.48   48.88/  49.03   51.94/  52.09
  ancestor46_it85_108f4c7441  366.50/ 366.62  499.80/ 499.95   48.34/  48.48   48.88/  49.03   51.94/  52.09
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.14/ 443.81  528.13/ 527.79   47.94/  47.89   48.86/  48.88   50.43/  50.46
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ancestor1_it0_0875253d162c  495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  ENUMERATE_VM_C1             495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  contemp_7a9653d1023b7ba7    897.37/ 897.50 1060.75/1060.89   51.26/  51.39   51.61/  51.74   51.61/  51.74
  RANDOM_C1                  1662.62/1662.62 1627.07/1627.07   50.50/  50.50   50.50/  50.50   48.56/  48.56
  contemp_ed8dbe6ab031c1eb   1880.78/1880.92 1810.52/1810.66   50.16/  50.30   52.18/  52.33   52.18/  52.33

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  top1_a2f32643a319c980          3/36    47     1/30    49     2/12    45     0/12    50    29/30   333    30/30   347
  top2_20ab751c3d0dd7b3          3/36    47     1/30    49     2/12    45     0/12    50    29/30   333    30/30   347
  top3_45c83b353370df5e          3/36    47     1/30    49     2/12    45     0/12    50    29/30   333    30/30   347
  contemp_39104483a82b37c6       3/36    47     1/30    49     2/12    45     0/12    50    29/30   333    30/30   347
  ancestor91_it271_ba21bb27b     3/36    47     1/30    49     2/12    45     0/12    50    29/30   333    30/30   347
  bestever_258cf8756ba56722      4/36    46     2/30    47     0/12    50     1/12    50    30/30   352    28/30   480
  ancestor46_it85_108f4c7441     4/36    46     2/30    47     0/12    50     1/12    50    30/30   352    28/30   480
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ancestor1_it0_0875253d162c     2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  contemp_7a9653d1023b7ba7       1/36    50     0/30    50     0/12    50     0/12    50    21/30   868    18/30  1027
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610
  contemp_ed8dbe6ab031c1eb       2/36    48     0/30    50     0/12    50     0/12    50     3/30  1802     4/30  1735

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.27    49.53    36.27    36.27    49.53    49.53    49.53   5.0
  top1_a2f32643a319c980         50.49    50.50    50.49    50.49    50.50    50.50    50.50   1.0
  top2_20ab751c3d0dd7b3         50.49    50.50    50.49    50.49    50.50    50.50    50.50   1.0
  top3_45c83b353370df5e         50.49    50.50    50.49    50.49    50.50    50.50    50.50   1.0
  contemp_39104483a82b37c6      50.50    50.51    50.50    50.50    50.51    50.51    50.51   1.0
  ancestor91_it271_ba21bb27b    50.49    50.50    50.49    50.49    50.50    50.50    50.50   1.0
  bestever_258cf8756ba56722     50.24    50.25    50.24    50.24    50.25    50.25    50.25   1.0
  ancestor46_it85_108f4c7441    50.24    50.25    50.24    50.24    50.25    50.25    50.25   1.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.56    49.55    49.56    49.56    49.55    49.55    49.55   2.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ancestor1_it0_0875253d162c    51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  ENUMERATE_VM_C1               51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  contemp_7a9653d1023b7ba7      51.61    51.62    51.61    51.61    51.62    51.62    51.62   1.0
  RANDOM_C1                     49.64       --    49.64    49.64    49.64    49.64    49.64   0.0
  contemp_ed8dbe6ab031c1eb      52.18    52.19    52.18    52.18    52.19    52.19    52.19   1.0

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
  top1_a2f32643a319c980
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [21, 21, 23] vs FRESH [21, 21, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.4] vs 5% of FRESH cost [1544.7, 1486.4, 1487.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.99, 49.78, 50.7] vs CODE_ONLY [51.0, 49.79, 50.71]
    4_scramble_or_reset_damages            0/3  eff ACC [21.419, 21.419, 23.452] SCR [21.419, 21.419, 23.452] RESET [21.419, 21.419, 23.452]
    5_transfers_to_fresh_copy              0/3  FULL [50.99, 49.78, 50.7] vs ACC remainder [50.99, 49.78, 50.7]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.0, 49.79, 50.71] vs ACC remainder [50.99, 49.78, 50.7]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.0, 49.79, 50.71] STORAGE_MATCHED [51.0, 49.79, 50.71] vs ACC remainder [50.99, 49.78, 50.7]
  top2_20ab751c3d0dd7b3
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [21, 21, 23] vs FRESH [21, 21, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.4] vs 5% of FRESH cost [1544.7, 1486.4, 1487.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.99, 49.78, 50.7] vs CODE_ONLY [51.0, 49.79, 50.71]
    4_scramble_or_reset_damages            0/3  eff ACC [21.419, 21.419, 23.452] SCR [21.419, 21.419, 23.452] RESET [21.419, 21.419, 23.452]
    5_transfers_to_fresh_copy              0/3  FULL [50.99, 49.78, 50.7] vs ACC remainder [50.99, 49.78, 50.7]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.0, 49.79, 50.71] vs ACC remainder [50.99, 49.78, 50.7]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.0, 49.79, 50.71] STORAGE_MATCHED [51.0, 49.79, 50.71] vs ACC remainder [50.99, 49.78, 50.7]
  top3_45c83b353370df5e
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [21, 21, 23] vs FRESH [21, 21, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.4] vs 5% of FRESH cost [1544.7, 1486.4, 1487.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.99, 49.78, 50.7] vs CODE_ONLY [51.0, 49.79, 50.71]
    4_scramble_or_reset_damages            0/3  eff ACC [21.419, 21.419, 23.452] SCR [21.419, 21.419, 23.452] RESET [21.419, 21.419, 23.452]
    5_transfers_to_fresh_copy              0/3  FULL [50.99, 49.78, 50.7] vs ACC remainder [50.99, 49.78, 50.7]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.0, 49.79, 50.71] vs ACC remainder [50.99, 49.78, 50.7]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.0, 49.79, 50.71] STORAGE_MATCHED [51.0, 49.79, 50.71] vs ACC remainder [50.99, 49.78, 50.7]
  contemp_39104483a82b37c6
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [21, 21, 23] vs FRESH [21, 21, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.4] vs 5% of FRESH cost [1545.0, 1486.7, 1487.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.0, 49.79, 50.71] vs CODE_ONLY [51.01, 49.8, 50.72]
    4_scramble_or_reset_damages            0/3  eff ACC [21.419, 21.419, 23.452] SCR [21.419, 21.419, 23.452] RESET [21.419, 21.419, 23.452]
    5_transfers_to_fresh_copy              0/3  FULL [51.0, 49.79, 50.71] vs ACC remainder [51.0, 49.79, 50.71]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.01, 49.8, 50.72] vs ACC remainder [51.0, 49.79, 50.71]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.01, 49.8, 50.72] STORAGE_MATCHED [51.01, 49.8, 50.72] vs ACC remainder [51.0, 49.79, 50.71]
  ancestor91_it271_ba21bb27bc48657c
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [21, 21, 23] vs FRESH [21, 21, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.4] vs 5% of FRESH cost [1544.7, 1486.4, 1487.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.99, 49.78, 50.7] vs CODE_ONLY [51.0, 49.79, 50.71]
    4_scramble_or_reset_damages            0/3  eff ACC [21.419, 21.419, 23.452] SCR [21.419, 21.419, 23.452] RESET [21.419, 21.419, 23.452]
    5_transfers_to_fresh_copy              0/3  FULL [50.99, 49.78, 50.7] vs ACC remainder [50.99, 49.78, 50.7]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.0, 49.79, 50.71] vs ACC remainder [50.99, 49.78, 50.7]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.0, 49.79, 50.71] STORAGE_MATCHED [51.0, 49.79, 50.71] vs ACC remainder [50.99, 49.78, 50.7]
  bestever_258cf8756ba56722
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [23, 19, 23] vs FRESH [23, 19, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.4, 4.5, 4.4] vs 5% of FRESH cost [1478.0, 1530.1, 1458.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.55, 51.86, 49.32] vs CODE_ONLY [49.56, 51.87, 49.33]
    4_scramble_or_reset_damages            0/3  eff ACC [23.443, 19.364, 23.445] SCR [23.443, 19.364, 23.445] RESET [23.443, 19.364, 23.445]
    5_transfers_to_fresh_copy              0/3  FULL [49.55, 51.86, 49.32] vs ACC remainder [49.55, 51.86, 49.32]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [49.56, 51.87, 49.33] vs ACC remainder [49.55, 51.86, 49.32]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.56, 51.87, 49.33] STORAGE_MATCHED [49.56, 51.87, 49.33] vs ACC remainder [49.55, 51.86, 49.32]
  ancestor46_it85_108f4c744160d86b
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [23, 19, 23] vs FRESH [23, 19, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.4, 4.5, 4.4] vs 5% of FRESH cost [1478.0, 1530.1, 1458.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.55, 51.86, 49.32] vs CODE_ONLY [49.56, 51.87, 49.33]
    4_scramble_or_reset_damages            0/3  eff ACC [23.443, 19.364, 23.445] SCR [23.443, 19.364, 23.445] RESET [23.443, 19.364, 23.445]
    5_transfers_to_fresh_copy              0/3  FULL [49.55, 51.86, 49.32] vs ACC remainder [49.55, 51.86, 49.32]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [49.56, 51.87, 49.33] vs ACC remainder [49.55, 51.86, 49.32]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.56, 51.87, 49.33] STORAGE_MATCHED [49.56, 51.87, 49.33] vs ACC remainder [49.55, 51.86, 49.32]
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
  contemp_7a9653d1023b7ba7
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [12, 14, 14] vs FRESH [12, 14, 14]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [3.9, 3.9, 3.9] vs 5% of FRESH cost [1552.2, 1539.7, 1552.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.61, 51.61, 51.61] vs CODE_ONLY [51.62, 51.62, 51.62]
    4_scramble_or_reset_damages            0/3  eff ACC [12.331, 14.318, 14.335] SCR [12.331, 14.318, 14.335] RESET [12.331, 14.318, 14.335]
    5_transfers_to_fresh_copy              0/3  FULL [51.61, 51.61, 51.61] vs ACC remainder [51.61, 51.61, 51.61]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.62, 51.62, 51.62] vs ACC remainder [51.61, 51.61, 51.61]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.62, 51.62, 51.62] STORAGE_MATCHED [51.62, 51.62, 51.62] vs ACC remainder [51.61, 51.61, 51.61]
  RANDOM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 6, 9] vs FRESH [6, 6, 9]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1493.8, 1515.0, 1489.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.32, 50.5, 49.1] vs CODE_ONLY [49.32, 50.5, 49.1]
    4_scramble_or_reset_damages            0/3  eff ACC [6.205, 6.235, 9.221] SCR [6.205, 6.235, 9.221] RESET [6.205, 6.235, 9.221]
    5_transfers_to_fresh_copy              0/3  FULL [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.32, 50.5, 49.1]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.32, 50.5, 49.1] STORAGE_MATCHED [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
  contemp_ed8dbe6ab031c1eb
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [2, 5, 2] vs FRESH [2, 5, 2]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.4] vs 5% of FRESH cost [1569.9, 1546.0, 1520.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.18, 52.18, 52.18] vs CODE_ONLY [52.19, 52.19, 52.19]
    4_scramble_or_reset_damages            0/3  eff ACC [2.182, 5.215, 2.165] SCR [2.182, 5.215, 2.165] RESET [2.182, 5.215, 2.165]
    5_transfers_to_fresh_copy              0/3  FULL [52.18, 52.18, 52.18] vs ACC remainder [52.18, 52.18, 52.18]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.19, 52.19, 52.19] vs ACC remainder [52.18, 52.18, 52.18]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.19, 52.19, 52.19] STORAGE_MATCHED [52.19, 52.19, 52.19] vs ACC remainder [52.18, 52.18, 52.18]

MACHINERY OF top1_a2f32643a319c980 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   1    32
    task  9:     0    0    0    0    0 |   1    32
    task 19:     0    0    0    0    0 |   1    32
    task 31:     0    0    0    0    0 |   1    32
    task 41:     0    0    0    0    0 |   1    32
    task 49:     0    0    0    0    0 |   1    32
  artifact events: 1 (create 1, delete 0, patch/append 0); invocations by block: {}; edges: 0
    block 0 origin=calibration len=0 state=[[2, 3, 6, 8, 10, 4, 9, 11, 5, 0, 7, 1], [9, 11, 0, 1, 5, 8, 2, 10, 3, 6, 4, 7], 0] instr=[]
  adaptation curve ACC:   166 108 18 795 166 166 150 1467 60 36 54 23 795 795 166 1619 1619 18 108 38 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 36 52 52 52 52
  adaptation curve FRESH: 166 108 18 795 166 166 150 1467 60 36 54 23 795 795 166 1619 1619 18 108 38 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 36 52 52 52 52
  reuse_gain per task:    0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0

BASELINES ON SEARCH SUITE (crius/runs/baselines_c2d): effA effF effR effS  succA  interA interF  reuse_gain  blocks
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

