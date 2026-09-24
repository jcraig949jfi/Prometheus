CRIUS CAMPAIGN 0 REPORT  run=search_c2c_seeded_s3  arm=seeded
code_commit=cabe092b4 dirty=True config_hash=416bbe8b9be34706 world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  19.8944   17.3730         8.5991        39          4
    26  24.4247   24.4245        15.7040        39         99
    51  20.9548   18.7197        12.0061        50        194
    76  19.8756   19.8756        11.5242        49        288
   101  22.4104   21.9734        14.2212        40        380
   126  24.9044   23.1761        19.3635        36        489
   151  23.9510   23.9510        15.2115        37        583
   176  24.4700   24.4696        17.5686        36        686
   201  23.4635   23.0278        12.7103        43        783
   226  21.4198   21.4198        15.0048        40        885
   251  23.4383   22.9546        16.2878        51        986
   276  24.4378   22.2487        13.3153        75       1090
   300  24.4332   23.7451        17.8546        70       1196
  candidates evaluated: 7208   best_ever 29.4636 (54f34ab64556d46f)  wall 1196s

BEST PROGRAM 54f34ab64556d46f (len 35, iteration 122, modification delete@18)
  search seed 3011220: fit 25.4477 succ 25/50 inter 6149 steps 27977 ws_cost 15 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [236.803, 1.0], "B": [267.058, 1.0], "C": [42.139, 0.25], "D": [51.92, 0.0], "E": [45.68, 0.25]}
  search seed 3011221: fit 33.4794 succ 33/50 inter 2372 steps 15744 ws_cost 15 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [68.348, 1.0], "B": [59.938, 1.0], "C": [42.913, 0.333], "D": [40.383, 0.4], "E": [40.993, 0.625]}
  listing:
      0  CONST          R5, 5
      1  INPUT          R1, num_ops
      2  ADD            R0, R0, R5
      3  INPUT          R1, num_ops
      4  ADD            R0, R0, R5
      5  JMP            20
      6  ACT            R1
      7  ACT            R3
      8  LT             R3, R0, R2
      9  MOV            R6, R0
     10  INPUT          R3, num_ops
     11  ACT            R6
     12  HALT           
     13  ACT            R3
     14  MUL            R2, R1, R1
     15  ACT            R3
     16  MOD            R3, R4, R1
     17  MUL            R2, R2, R1
     18  ADD            R1, R7, R3
     19  ACT            R1
     20  ADD            R0, R0, R5
     21  ADD            R0, R0, R5
     22  INPUT          R1, num_ops
     23  ADD            R0, R0, R5
     24  ACT            R1
     25  MOD            R3, R0, R1
     26  ACT            R3
     27  DIV            R4, R0, R1
     28  MOD            R3, R4, R1
     29  ACT            R3
     30  DIV            R4, R4, R1
     31  MOD            R3, R4, R1
     32  ACT            R3
     33  ADD            R0, R0, R5
     34  JMP            24
  ancestry (49 steps, newest first): iteration/fitness/modification
    it  122  29.4636  len 35  delete@18
    it  121  24.4283  len 36  delete@7
    it  118  25.4618  len 37  swap@15,23
    it  113  28.9509  len 37  replace@7
    it  111  24.4125  len 37  duplicate@1+2->1
    it  100  22.4695  len 35  delete@20+delete@35+swap@16,22
    it   99  21.9478  len 37  swap@6,20+delete@8
    it   98  21.9160  len 38  delete@13
    it   97  20.4294  len 39  delete@4
    it   94  23.9536  len 40  delete@24+delete@10
    it   93  21.8948  len 42  delete@13
    it   91  25.4682  len 43  delete@5+delete@14+delete@27
    it   89  20.9516  len 46  delete@6+insert@17
    it   83  22.4395  len 46  replace@24+arg@27.0+swap@18,33
    it   81  24.4570  len 46  arg@11.1+delete@27+swap@9,12
    ... 35 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7315.4    5.3   74.7
  top2_462cc1db507c0fa0       22.117  22.117  22.117  22.117  21.7  21.7     5823     5823       7.0   32.0    0.0
  bestever_54f34ab64556d46f   21.782  21.782  21.782  21.782  21.3  21.3     6014     6014       7.1    1.0    0.0
  ancestor52_it129_139bcef45  21.782  21.782  21.782  21.782  21.3  21.3     6042     6042       7.2    1.0    0.0
  top3_becf693d7c047560       21.763  21.763  21.763  21.763  21.3  21.3     8235     8246      17.1   32.0   43.0
  top1_bd6d521120b1b606       21.451  21.451  21.451  21.451  21.0  21.0     5791     5791       7.1    1.0    0.0
  ancestor104_it299_4138c43c  21.449  21.449  21.449  21.449  21.0  21.0     5979     5979       7.2    1.0    0.0
  contemp_162fb3947982f488    21.449  21.449  21.449  21.449  21.0  21.0     5979     5979       7.2   32.0    0.0
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.9    3.7    1.7
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ancestor1_it0_0875253d162c  19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  contemp_e8833170fc8e80e8    10.960  10.960  10.960  10.960  10.7  10.7    23219    23264      12.7   32.0   49.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0
  contemp_4226acae4566b97b     0.150   0.150   0.150   0.150   0.0   0.0    41500    41500       2.0   32.0   45.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.02/ 455.13   14.92/ 539.10   21.12/  47.94   33.22/  48.94   40.08/  50.52
  top2_462cc1db507c0fa0       219.46/ 219.58  238.28/ 238.42   49.71/  49.86   51.23/  51.38   52.34/  52.49
  bestever_54f34ab64556d46f   222.91/ 223.03  254.37/ 254.52   48.80/  48.95   50.81/  50.96   51.92/  52.07
  ancestor52_it129_139bcef45  226.81/ 226.94  252.54/ 252.69   49.58/  49.73   50.71/  50.86   51.92/  52.07
  top3_becf693d7c047560       378.38/ 378.52  331.02/ 332.04   49.29/  49.52   50.33/  50.52   52.41/  52.53
  top1_bd6d521120b1b606       217.94/ 218.06  234.58/ 234.72   50.49/  50.64   51.96/  52.11   52.31/  52.46
  ancestor104_it299_4138c43c  228.34/ 228.47  244.98/ 245.13   50.43/  50.58   50.68/  50.83   52.31/  52.46
  contemp_162fb3947982f488    228.36/ 228.49  245.00/ 245.15   50.45/  50.60   50.70/  50.85   52.33/  52.48
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.14/ 443.81  528.13/ 527.79   47.94/  47.89   48.86/  48.88   50.43/  50.46
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ancestor1_it0_0875253d162c  495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  ENUMERATE_VM_C1             495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  contemp_e8833170fc8e80e8   1263.87/1266.39 1121.51/1124.46   53.77/  52.04   52.99/  51.36   54.96/  54.33
  RANDOM_C1                  1662.62/1662.62 1627.07/1627.07   50.50/  50.50   50.50/  50.50   48.56/  48.56
  contemp_4226acae4566b97b   2073.80/2073.84 2073.80/2073.84   52.30/  52.34   52.30/  52.34   52.30/  52.34

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  top2_462cc1db507c0fa0          4/36    47     1/30    49     0/12    50     0/12    50    30/30   209    30/30   227
  bestever_54f34ab64556d46f      3/36    47     1/30    49     0/12    50     0/12    50    30/30   213    30/30   243
  ancestor52_it129_139bcef45     3/36    48     1/30    49     0/12    50     0/12    50    30/30   217    30/30   242
  top3_becf693d7c047560          4/36    47     2/30    48     0/12    50     0/12    50    29/30   363    29/30   317
  top1_bd6d521120b1b606          2/36    48     1/30    50     0/12    50     0/12    50    30/30   208    30/30   224
  ancestor104_it299_4138c43c     2/36    48     1/30    48     0/12    50     0/12    50    30/30   218    30/30   234
  contemp_162fb3947982f488       2/36    48     1/30    48     0/12    50     0/12    50    30/30   218    30/30   234
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ancestor1_it0_0875253d162c     2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  contemp_e8833170fc8e80e8       1/36    49     2/30    48     1/12    50     0/12    50    13/30  1153    15/30  1023
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610
  contemp_4226acae4566b97b       0/36    50     0/30    50     0/12    50     0/12    50     0/30  2000     0/30  2000

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.27    49.53    36.27    36.27    49.53    49.53    49.53   5.0
  top2_462cc1db507c0fa0         51.72    51.73    51.72    51.72    51.73    51.73    51.73  32.0
  bestever_54f34ab64556d46f     51.30    51.31    51.30    51.30    51.31    51.31    51.31   1.0
  ancestor52_it129_139bcef45    51.25    51.26    51.25    51.25    51.26    51.26    51.26   1.0
  top3_becf693d7c047560         51.26    51.26    51.26    51.26    51.28    51.28    51.28  32.0
  top1_bd6d521120b1b606         52.12    52.12    52.12    52.12    52.12    52.12    52.12   1.0
  ancestor104_it299_4138c43c    51.41    51.41    51.41    51.41    51.41    51.41    51.41   1.0
  contemp_162fb3947982f488      51.43    51.43    51.43    51.43    51.43    51.43    51.43  32.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.56    49.55    49.56    49.56    49.55    49.55    49.55   2.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ancestor1_it0_0875253d162c    51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  ENUMERATE_VM_C1               51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  contemp_e8833170fc8e80e8      53.86    53.87    53.86    53.86    53.82    53.82    53.82  32.0
  RANDOM_C1                     49.64       --    49.64    49.64    49.64    49.64    49.64   0.0
  contemp_4226acae4566b97b      52.30    52.28    52.30    52.30    52.30    52.30    52.30  32.0

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
  top2_462cc1db507c0fa0
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [21, 21, 23] vs FRESH [21, 21, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.5] vs 5% of FRESH cost [1568.4, 1525.8, 1501.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.34, 52.34, 50.49] vs CODE_ONLY [52.35, 52.35, 50.5]
    4_scramble_or_reset_damages            0/3  eff ACC [21.445, 21.445, 23.462] SCR [21.445, 21.445, 23.462] RESET [21.445, 21.445, 23.462]
    5_transfers_to_fresh_copy              0/3  FULL [52.34, 52.34, 50.49] vs ACC remainder [52.34, 52.34, 50.49]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.35, 52.35, 50.5] vs ACC remainder [52.34, 52.34, 50.49]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.35, 52.35, 50.5] STORAGE_MATCHED [52.35, 52.35, 50.5] vs ACC remainder [52.34, 52.34, 50.49]
  bestever_54f34ab64556d46f
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 21, 23] vs FRESH [20, 21, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.4] vs 5% of FRESH cost [1562.1, 1513.2, 1465.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.92, 51.92, 50.07] vs CODE_ONLY [51.93, 51.93, 50.08]
    4_scramble_or_reset_damages            0/3  eff ACC [20.442, 21.44, 23.465] SCR [20.442, 21.44, 23.465] RESET [20.442, 21.44, 23.465]
    5_transfers_to_fresh_copy              0/3  FULL [51.92, 51.92, 50.07] vs ACC remainder [51.92, 51.92, 50.07]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.93, 51.93, 50.08] vs ACC remainder [51.92, 51.92, 50.07]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.93, 51.93, 50.08] STORAGE_MATCHED [51.93, 51.93, 50.08] vs ACC remainder [51.92, 51.92, 50.07]
  ancestor52_it129_139bcef45bc4ffc1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 21, 23] vs FRESH [20, 21, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.4] vs 5% of FRESH cost [1562.1, 1547.5, 1456.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.92, 51.92, 49.9] vs CODE_ONLY [51.93, 51.93, 49.91]
    4_scramble_or_reset_damages            0/3  eff ACC [20.443, 21.44, 23.464] SCR [20.443, 21.44, 23.464] RESET [20.443, 21.44, 23.464]
    5_transfers_to_fresh_copy              0/3  FULL [51.92, 51.92, 49.9] vs ACC remainder [51.92, 51.92, 49.9]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.93, 51.93, 49.91] vs ACC remainder [51.92, 51.92, 49.9]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.93, 51.93, 49.91] STORAGE_MATCHED [51.93, 51.93, 49.91] vs ACC remainder [51.92, 51.92, 49.9]
  top3_becf693d7c047560
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 22, 23] vs FRESH [19, 22, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.6, 5.6, 6.6] vs 5% of FRESH cost [1547.8, 1512.4, 1498.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.41, 52.41, 48.95] vs CODE_ONLY [52.4, 52.4, 49.05]
    4_scramble_or_reset_damages            0/3  eff ACC [19.423, 22.404, 23.463] SCR [19.423, 22.404, 23.463] RESET [19.423, 22.404, 23.463]
    5_transfers_to_fresh_copy              0/3  FULL [52.41, 52.41, 48.95] vs ACC remainder [52.41, 52.41, 48.95]
    6_executable_components_reused         0/3  invocations [43, 43, 43]; ABLATION_ALL cost [52.42, 52.42, 48.95] vs ACC remainder [52.41, 52.41, 48.95]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.4, 52.4, 49.05] STORAGE_MATCHED [52.4, 52.4, 49.05] vs ACC remainder [52.41, 52.41, 48.95]
  top1_bd6d521120b1b606
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 21, 22] vs FRESH [20, 21, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.4] vs 5% of FRESH cost [1573.8, 1547.8, 1523.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.31, 52.31, 51.73] vs CODE_ONLY [52.32, 52.32, 51.74]
    4_scramble_or_reset_damages            0/3  eff ACC [20.444, 21.441, 22.466] SCR [20.444, 21.441, 22.466] RESET [20.444, 21.441, 22.466]
    5_transfers_to_fresh_copy              0/3  FULL [52.31, 52.31, 51.73] vs ACC remainder [52.31, 52.31, 51.73]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.32, 52.32, 51.74] vs ACC remainder [52.31, 52.31, 51.73]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.32, 52.32, 51.74] STORAGE_MATCHED [52.32, 52.32, 51.74] vs ACC remainder [52.31, 52.31, 51.73]
  ancestor104_it299_4138c43caac7fd8b
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 21, 22] vs FRESH [20, 21, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.3] vs 5% of FRESH cost [1573.8, 1546.8, 1484.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.31, 52.31, 49.6] vs CODE_ONLY [52.32, 52.32, 49.61]
    4_scramble_or_reset_damages            0/3  eff ACC [20.444, 21.441, 22.461] SCR [20.444, 21.441, 22.461] RESET [20.444, 21.441, 22.461]
    5_transfers_to_fresh_copy              0/3  FULL [52.31, 52.31, 49.6] vs ACC remainder [52.31, 52.31, 49.6]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.32, 52.32, 49.61] vs ACC remainder [52.31, 52.31, 49.6]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.32, 52.32, 49.61] STORAGE_MATCHED [52.32, 52.32, 49.61] vs ACC remainder [52.31, 52.31, 49.6]
  contemp_162fb3947982f488
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 21, 22] vs FRESH [20, 21, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.3] vs 5% of FRESH cost [1574.4, 1547.4, 1484.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.33, 52.33, 49.62] vs CODE_ONLY [52.34, 52.34, 49.63]
    4_scramble_or_reset_damages            0/3  eff ACC [20.444, 21.441, 22.461] SCR [20.444, 21.441, 22.461] RESET [20.444, 21.441, 22.461]
    5_transfers_to_fresh_copy              0/3  FULL [52.33, 52.33, 49.62] vs ACC remainder [52.33, 52.33, 49.62]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.34, 52.34, 49.63] vs ACC remainder [52.33, 52.33, 49.62]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.34, 52.34, 49.63] STORAGE_MATCHED [52.34, 52.34, 49.63] vs ACC remainder [52.33, 52.33, 49.62]
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
  contemp_e8833170fc8e80e8
    0_competence_kept_ACC_ge_FRESH         2/3  successes ACC [8, 8, 16] vs FRESH [7, 8, 17]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [-19.8, -24.0, -82.4] vs 5% of FRESH cost [1629.9, 1629.9, 1458.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [54.9, 55.13, 51.56] vs CODE_ONLY [54.85, 55.09, 51.52]
    4_scramble_or_reset_damages            0/3  eff ACC [8.252, 8.268, 16.359] SCR [8.252, 8.268, 16.359] RESET [8.252, 8.268, 16.359]
    5_transfers_to_fresh_copy              0/3  FULL [54.9, 55.13, 51.56] vs ACC remainder [54.9, 55.13, 51.56]
    6_executable_components_reused         0/3  invocations [49, 49, 49]; ABLATION_ALL cost [54.91, 55.14, 51.57] vs ACC remainder [54.9, 55.13, 51.56]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [54.85, 55.09, 51.52] STORAGE_MATCHED [54.85, 55.09, 51.52] vs ACC remainder [54.9, 55.13, 51.56]
  RANDOM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 6, 9] vs FRESH [6, 6, 9]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1493.8, 1515.0, 1489.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.32, 50.5, 49.1] vs CODE_ONLY [49.32, 50.5, 49.1]
    4_scramble_or_reset_damages            0/3  eff ACC [6.205, 6.235, 9.221] SCR [6.205, 6.235, 9.221] RESET [6.205, 6.235, 9.221]
    5_transfers_to_fresh_copy              0/3  FULL [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.32, 50.5, 49.1]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.32, 50.5, 49.1] STORAGE_MATCHED [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
  contemp_4226acae4566b97b
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [1.2, 1.2, 1.2] vs 5% of FRESH cost [1570.2, 1570.2, 1570.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.3, 52.3, 52.3] vs CODE_ONLY [52.3, 52.3, 52.3]
    4_scramble_or_reset_damages            0/3  eff ACC [0.15, 0.15, 0.15] SCR [0.15, 0.15, 0.15] RESET [0.15, 0.15, 0.15]
    5_transfers_to_fresh_copy              0/3  FULL [52.3, 52.3, 52.3] vs ACC remainder [52.3, 52.3, 52.3]
    6_executable_components_reused         0/3  invocations [45, 45, 45]; ABLATION_ALL cost [52.28, 52.28, 52.28] vs ACC remainder [52.3, 52.3, 52.3]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.3, 52.3, 52.3] STORAGE_MATCHED [52.3, 52.3, 52.3] vs ACC remainder [52.3, 52.3, 52.3]

MACHINERY OF top1_bd6d521120b1b606 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     1    1    0    0    0 |   1    32
    task  9:     1    1    0    0    0 |   1    32
    task 19:     1    1    0    0    0 |   1    32
    task 31:     1    1    0    0    0 |   1    32
    task 41:     1    1    0    0    0 |   1    32
    task 49:     1    1    0    0    0 |   1    32
  artifact events: 1 (create 1, delete 0, patch/append 0); invocations by block: {}; edges: 0
    block 0 origin=calibration len=0 state=[[2, 3, 6, 8, 10, 4, 9, 11, 5, 0, 7, 1], [9, 11, 0, 1, 5, 8, 2, 10, 3, 6, 4, 7], 0] instr=[]
  adaptation curve ACC:   29 532 71 262 65 28 38 1885 108 233 77 71 262 262 65 361 361 35 532 12 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
  adaptation curve FRESH: 29 532 71 262 65 29 38 1885 108 233 77 71 262 262 65 361 361 35 532 12 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
  reuse_gain per task:    0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0

BASELINES ON SEARCH SUITE (crius/runs/baselines_c2c): effA effF effR effS  succA  interA interF  reuse_gain  blocks
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

