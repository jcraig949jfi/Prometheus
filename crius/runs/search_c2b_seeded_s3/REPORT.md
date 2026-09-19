CRIUS CAMPAIGN 0 REPORT  run=search_c2b_seeded_s3  arm=seeded
code_commit=713b2773f dirty=True config_hash=c9c87cec99eb063f world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  20.4007   17.8781         8.7259        40          3
    26  22.4398   22.0088        12.0034        35        114
    51  20.4575   18.2890        10.6742        34        231
    76  19.9211   19.9211        14.8485        24        357
   101  22.4119   20.9054        10.7188        22        490
   126  23.9269   23.0380        11.5104        24        638
   151  23.4544   23.4544        10.4903        17        766
   176  24.4720   24.4720        12.1242        16        897
   201  24.4667   24.4665        14.6961        22       1026
   226  20.9511   20.9511        11.3412        15       1161
   251  26.4676   24.2601        10.6400        17       1303
   276  21.4561   21.4561         8.2269        15       1421
   300  21.9385   21.9385        10.0044        15       1542
  candidates evaluated: 7208   best_ever 28.9760 (4a58e53df142cc51)  wall 1542s

BEST PROGRAM 4a58e53df142cc51 (len 19, iteration 121, modification delete@7)
  search seed 3011210: fit 21.4355 succ 21/50 inter 7604 steps 32260 ws_cost 15 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [263.289, 1.0], "B": [375.234, 1.0], "C": [50.655, 0.083], "D": [51.87, 0.0], "E": [51.87, 0.0]}
  search seed 3011211: fit 24.4314 succ 24/50 inter 8093 steps 34655 ws_cost 15 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [190.929, 1.0], "B": [515.097, 0.8], "C": [43.466, 0.333], "D": [44.289, 0.2], "E": [51.87, 0.0]}
  listing:
      0  CONST          R5, -5
      1  ADD            R0, R0, R5
      2  BRZ            R3, 4
      3  ACT            R0
      4  INPUT          R1, num_ops
      5  BRZ            R2, 8
      6  VLEN           R0, R0
      7  DIV            R4, R0, R1
      8  ACT            R1
      9  MOD            R3, R0, R1
     10  ACT            R3
     11  DIV            R4, R0, R1
     12  MOD            R3, R4, R1
     13  ACT            R3
     14  DIV            R4, R4, R1
     15  MOD            R3, R4, R1
     16  ACT            R3
     17  ADD            R0, R0, R5
     18  JMP            8
  ancestry (41 steps, newest first): iteration/fitness/modification
    it  121  22.9335  len 19  delete@7
    it  108  26.9524  len 20  delete@3
    it  107  23.3721  len 21  replace@7+swap@18,15
    it   92  20.4262  len 21  delete@10
    it   91  25.4743  len 22  delete@3
    it   90  22.9311  len 23  arg@5.0+arg@3.0
    it   87  21.4225  len 23  delete@12
    it   81  23.4390  len 24  delete@13
    it   76  19.9211  len 25  delete@11
    it   70  21.9749  len 26  const@0+const@0+arg@12.2
    it   64  24.9706  len 26  delete@10+arg@17.0
    it   63  21.4291  len 27  replace@10
    it   60  21.4499  len 27  swap@3,5
    it   58  21.4331  len 27  delete@27
    it   55  20.9184  len 28  replace@14
    ... 27 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7315.4    5.3   74.7
  top1_0668e1ff67c898f7       22.755  22.755  22.755  22.755  22.3  22.3     9247     9247       7.1    1.0    0.0
  top2_0a0c1f93c3dfc54d       22.755  22.755  22.755  22.755  22.3  22.3     9247     9247       7.1    1.0    0.0
  top3_18071fc63c53e949       22.755  22.755  22.755  22.755  22.3  22.3     9247     9247       7.1    1.0    0.0
  ancestor54_it274_32eb6a688  22.755  22.755  22.755  22.755  22.3  22.3     9247     9247       7.1    1.0    0.0
  bestever_4a58e53df142cc51   22.749  22.748  22.749  22.749  22.3  22.3    10013    10013       7.1    1.0    0.0
  ancestor28_it55_41b0b01531  22.749  22.748  22.749  22.749  22.3  22.3    10013    10013       7.1    1.0    0.0
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.9    3.7    1.7
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ancestor1_it0_0875253d162c  19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  contemp_b1b14fc3e556d1f5    19.736  19.736  19.736  19.736  19.3  19.3    11435    11435       7.1    1.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0
  contemp_13ac9e76d5c9b0f1     1.179   1.179   1.179   1.179   1.0   1.0      149      149       2.5    1.0    0.0
  contemp_5043285005acbad9     0.149   0.149   0.149   0.149   0.0   0.0    41500    41500       2.0    1.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.02/ 455.13   14.92/ 539.10   21.12/  47.94   33.22/  48.94   40.08/  50.52
  top1_0668e1ff67c898f7       336.66/ 336.78  477.04/ 477.18   48.98/  49.13   50.00/  50.15   50.76/  50.91
  top2_0a0c1f93c3dfc54d       336.66/ 336.78  477.04/ 477.18   48.98/  49.13   50.00/  50.15   50.76/  50.91
  top3_18071fc63c53e949       336.66/ 336.78  477.04/ 477.18   48.98/  49.13   50.00/  50.15   50.76/  50.91
  ancestor54_it274_32eb6a688  336.66/ 336.78  477.04/ 477.18   48.98/  49.13   50.00/  50.15   50.76/  50.91
  bestever_4a58e53df142cc51   403.65/ 403.79  490.79/ 490.93   48.67/  48.81   48.37/  48.52   51.87/  52.02
  ancestor28_it55_41b0b01531  403.66/ 403.80  490.80/ 490.94   48.68/  48.82   48.38/  48.53   51.88/  52.03
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.14/ 443.81  528.13/ 527.79   47.94/  47.89   48.86/  48.88   50.43/  50.46
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ancestor1_it0_0875253d162c  495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  ENUMERATE_VM_C1             495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  contemp_b1b14fc3e556d1f5    406.74/ 406.87  635.46/ 635.61   49.98/  50.13   50.65/  50.80   50.45/  50.59
  RANDOM_C1                  1662.62/1662.62 1627.07/1627.07   50.50/  50.50   50.50/  50.50   48.56/  48.56
  contemp_13ac9e76d5c9b0f1   1933.55/1933.59 1866.94/1866.99   50.14/  50.19   50.14/  50.19   50.14/  50.19
  contemp_5043285005acbad9   2080.00/2080.04 2080.00/2080.04   52.00/  52.04   52.00/  52.04   52.00/  52.04

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  top1_0668e1ff67c898f7          4/36    47     2/30    48     1/12    48     0/12    50    30/30   323    30/30   458
  top2_0a0c1f93c3dfc54d          4/36    47     2/30    48     1/12    48     0/12    50    30/30   323    30/30   458
  top3_18071fc63c53e949          4/36    47     2/30    48     1/12    48     0/12    50    30/30   323    30/30   458
  ancestor54_it274_32eb6a688     4/36    47     2/30    48     1/12    48     0/12    50    30/30   323    30/30   458
  bestever_4a58e53df142cc51      4/36    47     3/30    46     0/12    50     0/12    50    30/30   387    30/30   471
  ancestor28_it55_41b0b01531     4/36    47     3/30    46     0/12    50     0/12    50    30/30   387    30/30   471
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ancestor1_it0_0875253d162c     2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  contemp_b1b14fc3e556d1f5       4/36    48     2/30    49     0/12    50     1/12    47    27/30   389    24/30   609
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610
  contemp_13ac9e76d5c9b0f1       0/36     3     0/30     3     0/12     3     0/12     3     1/30     3     2/30     3
  contemp_5043285005acbad9       0/36    50     0/30    50     0/12    50     0/12    50     0/30  2000     0/30  2000

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.27    49.53    36.27    36.27    49.53    49.53    49.53   5.0
  top1_0668e1ff67c898f7         50.34    50.35    50.34    50.34    50.35    50.35    50.35   1.0
  top2_0a0c1f93c3dfc54d         50.34    50.35    50.34    50.34    50.35    50.35    50.35   1.0
  top3_18071fc63c53e949         50.34    50.35    50.34    50.34    50.35    50.35    50.35   1.0
  ancestor54_it274_32eb6a688    50.34    50.35    50.34    50.34    50.35    50.35    50.35   1.0
  bestever_4a58e53df142cc51     49.93    49.94    49.93    49.93    49.94    49.94    49.94   1.0
  ancestor28_it55_41b0b01531    49.94    49.95    49.94    49.94    49.95    49.95    49.95   1.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.56    49.55    49.56    49.56    49.55    49.55    49.55   2.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ancestor1_it0_0875253d162c    51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  ENUMERATE_VM_C1               51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  contemp_b1b14fc3e556d1f5      50.56    50.57    50.56    50.56    50.57    50.57    50.57   1.0
  RANDOM_C1                     49.64       --    49.64    49.64    49.64    49.64    49.64   0.0
  contemp_13ac9e76d5c9b0f1      50.14    50.14    50.14    50.14    50.14    50.14    50.14   1.0
  contemp_5043285005acbad9      52.00    52.00    52.00    52.00    52.00    52.00    52.00   1.0

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
  top1_0668e1ff67c898f7
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 23, 24] vs FRESH [20, 23, 24]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.4] vs 5% of FRESH cost [1559.7, 1474.4, 1460.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.84, 50.4, 48.78] vs CODE_ONLY [51.85, 50.4, 48.79]
    4_scramble_or_reset_damages            0/3  eff ACC [20.403, 23.414, 24.449] SCR [20.403, 23.414, 24.449] RESET [20.403, 23.414, 24.449]
    5_transfers_to_fresh_copy              0/3  FULL [51.84, 50.4, 48.78] vs ACC remainder [51.84, 50.4, 48.78]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.85, 50.4, 48.79] vs ACC remainder [51.84, 50.4, 48.78]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.85, 50.4, 48.79] STORAGE_MATCHED [51.85, 50.4, 48.79] vs ACC remainder [51.84, 50.4, 48.78]
  top2_0a0c1f93c3dfc54d
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 23, 24] vs FRESH [20, 23, 24]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.4] vs 5% of FRESH cost [1559.7, 1474.4, 1460.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.84, 50.4, 48.78] vs CODE_ONLY [51.85, 50.4, 48.79]
    4_scramble_or_reset_damages            0/3  eff ACC [20.403, 23.414, 24.449] SCR [20.403, 23.414, 24.449] RESET [20.403, 23.414, 24.449]
    5_transfers_to_fresh_copy              0/3  FULL [51.84, 50.4, 48.78] vs ACC remainder [51.84, 50.4, 48.78]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.85, 50.4, 48.79] vs ACC remainder [51.84, 50.4, 48.78]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.85, 50.4, 48.79] STORAGE_MATCHED [51.85, 50.4, 48.79] vs ACC remainder [51.84, 50.4, 48.78]
  top3_18071fc63c53e949
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 23, 24] vs FRESH [20, 23, 24]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.4] vs 5% of FRESH cost [1559.7, 1474.4, 1460.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.84, 50.4, 48.78] vs CODE_ONLY [51.85, 50.4, 48.79]
    4_scramble_or_reset_damages            0/3  eff ACC [20.403, 23.414, 24.449] SCR [20.403, 23.414, 24.449] RESET [20.403, 23.414, 24.449]
    5_transfers_to_fresh_copy              0/3  FULL [51.84, 50.4, 48.78] vs ACC remainder [51.84, 50.4, 48.78]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.85, 50.4, 48.79] vs ACC remainder [51.84, 50.4, 48.78]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.85, 50.4, 48.79] STORAGE_MATCHED [51.85, 50.4, 48.79] vs ACC remainder [51.84, 50.4, 48.78]
  ancestor54_it274_32eb6a6884c250fb
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 23, 24] vs FRESH [20, 23, 24]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.4] vs 5% of FRESH cost [1559.7, 1474.4, 1460.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.84, 50.4, 48.78] vs CODE_ONLY [51.85, 50.4, 48.79]
    4_scramble_or_reset_damages            0/3  eff ACC [20.403, 23.414, 24.449] SCR [20.403, 23.414, 24.449] RESET [20.403, 23.414, 24.449]
    5_transfers_to_fresh_copy              0/3  FULL [51.84, 50.4, 48.78] vs ACC remainder [51.84, 50.4, 48.78]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.85, 50.4, 48.79] vs ACC remainder [51.84, 50.4, 48.78]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.85, 50.4, 48.79] STORAGE_MATCHED [51.85, 50.4, 48.79] vs ACC remainder [51.84, 50.4, 48.78]
  bestever_4a58e53df142cc51
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 23, 24] vs FRESH [20, 23, 24]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.3, 4.3] vs 5% of FRESH cost [1560.6, 1451.3, 1449.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.87, 49.45, 48.46] vs CODE_ONLY [51.88, 49.45, 48.47]
    4_scramble_or_reset_damages            0/3  eff ACC [20.407, 23.408, 24.43] SCR [20.407, 23.408, 24.43] RESET [20.407, 23.408, 24.43]
    5_transfers_to_fresh_copy              0/3  FULL [51.87, 49.45, 48.46] vs ACC remainder [51.87, 49.45, 48.46]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.88, 49.45, 48.47] vs ACC remainder [51.87, 49.45, 48.46]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.88, 49.45, 48.47] STORAGE_MATCHED [51.88, 49.45, 48.47] vs ACC remainder [51.87, 49.45, 48.46]
  ancestor28_it55_41b0b0153123aef6
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 23, 24] vs FRESH [20, 23, 24]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.3, 4.3] vs 5% of FRESH cost [1560.9, 1451.6, 1449.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.88, 49.46, 48.47] vs CODE_ONLY [51.89, 49.47, 48.48]
    4_scramble_or_reset_damages            0/3  eff ACC [20.407, 23.408, 24.43] SCR [20.407, 23.408, 24.43] RESET [20.407, 23.408, 24.43]
    5_transfers_to_fresh_copy              0/3  FULL [51.88, 49.46, 48.47] vs ACC remainder [51.88, 49.46, 48.47]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.89, 49.47, 48.48] vs ACC remainder [51.88, 49.46, 48.47]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.89, 49.47, 48.48] STORAGE_MATCHED [51.89, 49.47, 48.48] vs ACC remainder [51.88, 49.46, 48.47]
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
  contemp_b1b14fc3e556d1f5
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [15, 19, 24] vs FRESH [15, 19, 24]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.4, 4.4, 4.4] vs 5% of FRESH cost [1527.2, 1517.8, 1497.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.93, 52.01, 49.75] vs CODE_ONLY [49.93, 52.02, 49.76]
    4_scramble_or_reset_damages            0/3  eff ACC [15.365, 19.413, 24.431] SCR [15.365, 19.413, 24.431] RESET [15.365, 19.413, 24.431]
    5_transfers_to_fresh_copy              0/3  FULL [49.93, 52.01, 49.75] vs ACC remainder [49.93, 52.01, 49.75]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [49.93, 52.02, 49.76] vs ACC remainder [49.93, 52.01, 49.75]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.93, 52.02, 49.76] STORAGE_MATCHED [49.93, 52.02, 49.76] vs ACC remainder [49.93, 52.01, 49.75]
  RANDOM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 6, 9] vs FRESH [6, 6, 9]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1493.8, 1515.0, 1489.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.32, 50.5, 49.1] vs CODE_ONLY [49.32, 50.5, 49.1]
    4_scramble_or_reset_damages            0/3  eff ACC [6.205, 6.235, 9.221] SCR [6.205, 6.235, 9.221] RESET [6.205, 6.235, 9.221]
    5_transfers_to_fresh_copy              0/3  FULL [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.32, 50.5, 49.1]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.32, 50.5, 49.1] STORAGE_MATCHED [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
  contemp_13ac9e76d5c9b0f1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [3, 0, 0] vs FRESH [3, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [1.5, 1.5, 1.5] vs 5% of FRESH cost [1505.7, 1505.7, 1505.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.14, 50.14, 50.14] vs CODE_ONLY [50.14, 50.14, 50.14]
    4_scramble_or_reset_damages            0/3  eff ACC [3.211, 0.163, 0.163] SCR [3.211, 0.163, 0.163] RESET [3.211, 0.163, 0.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.14, 50.14, 50.14] vs ACC remainder [50.14, 50.14, 50.14]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [50.14, 50.14, 50.14] vs ACC remainder [50.14, 50.14, 50.14]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.14, 50.14, 50.14] STORAGE_MATCHED [50.14, 50.14, 50.14] vs ACC remainder [50.14, 50.14, 50.14]
  contemp_5043285005acbad9
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [1.2, 1.2, 1.2] vs 5% of FRESH cost [1561.2, 1561.2, 1561.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.0, 52.0, 52.0] vs CODE_ONLY [52.0, 52.0, 52.0]
    4_scramble_or_reset_damages            0/3  eff ACC [0.149, 0.149, 0.149] SCR [0.149, 0.149, 0.149] RESET [0.149, 0.149, 0.149]
    5_transfers_to_fresh_copy              0/3  FULL [52.0, 52.0, 52.0] vs ACC remainder [52.0, 52.0, 52.0]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.0, 52.0, 52.0] vs ACC remainder [52.0, 52.0, 52.0]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.0, 52.0, 52.0] STORAGE_MATCHED [52.0, 52.0, 52.0] vs ACC remainder [52.0, 52.0, 52.0]

MACHINERY OF top1_0668e1ff67c898f7 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   1    32
    task  9:     0    0    0    0    0 |   1    32
    task 19:     0    0    0    0    0 |   1    32
    task 31:     0    0    0    0    0 |   1    32
    task 41:     0    0    0    0    0 |   1    32
    task 49:     0    0    0    0    0 |   1    32
  artifact events: 1 (create 1, delete 0, patch/append 0); invocations by block: {}; edges: 0
    block 0 origin=calibration len=0 state=[[2, 3, 6, 8, 10, 4, 9, 11, 5, 0, 7, 1], [9, 11, 0, 1, 5, 8, 2, 10, 3, 6, 4, 7], 0] instr=[]
  adaptation curve ACC:   79 1389 4 1712 79 79 116 108 188 38 287 4 1712 1712 79 593 593 4 1389 228 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
  adaptation curve FRESH: 79 1389 4 1713 79 79 116 108 188 38 287 4 1713 1713 79 593 593 4 1389 228 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
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

