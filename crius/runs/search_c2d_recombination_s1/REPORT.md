CRIUS CAMPAIGN 0 REPORT  run=search_c2d_recombination_s1  arm=recombination
code_commit=52c58d0d4 dirty=True config_hash=7ab056c39e1821fd world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  21.9592   20.9509        10.8649        39         20
    26  20.9388   20.5008        14.0729        44        122
    51  25.9527   25.9527        22.2954        50        218
    76  22.4135   22.2257        18.4141        54        322
   101  20.4171   20.4171        11.9451        57        423
   126  25.4376   25.1253        17.8873        55        520
   151  21.3333   21.3329        15.9119        67        602
   176  18.8730   18.4979        12.5075        57        689
   201  25.4580   25.4576        17.1973        51        790
   226  26.9417   26.9417        18.7084        69        877
   251  20.3894   20.3882        14.2963        66        977
   276  20.9286   17.3751        11.1658        62       1082
   300  21.4075   21.4075        13.0749        57       1188
  candidates evaluated: 7208   best_ever 28.4071 (c1c82b4c7a9799c7)  wall 1188s

BEST PROGRAM c1c82b4c7a9799c7 (len 46, iteration 10, modification swap@25,13)
  search seed 1010100: fit 30.4538 succ 30/50 inter 5404 steps 28122 ws_cost 15 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [205.85, 1.0], "B": [234.23, 1.0], "C": [37.763, 0.5], "D": [44.279, 0.3], "E": [48.579, 0.125]}
  search seed 1010101: fit 26.3604 succ 26/50 inter 16457 steps 71524 ws_cost 15 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [767.55, 1.0], "B": [809.561, 0.9], "C": [39.497, 0.5], "D": [52.1, 0.0], "E": [50.79, 0.125]}
  listing:
      0  INPUT          R1, num_ops
      1  CONST          R5, 1
      2  CONST          R0, 0
      3  LT             R3, R0, R2
      4  BRZ            R3, 11
      5  ADD            R0, R0, R5
      6  JMP            11
      7  ACT            R1
      8  ACT            R0
      9  ADD            R0, R0, R5
     10  MOD            R3, R4, R1
     11  BRZ            R3, 28
     12  BLK_STATE_GET  R3, R0, R1
     13  ACT            R3
     14  LT             R3, R0, R2
     15  MOD            R3, R0, R1
     16  ACT            R3
     17  DIV            R4, R0, R1
     18  MOD            R3, R4, R1
     19  CONST          R0, 0
     20  ACT            R1
     21  MOD            R3, R0, R1
     22  ACT            R3
     23  DIV            R4, R0, R1
     24  JMP            3
     25  MUL            R2, R1, R1
     26  ADD            R0, R0, R5
     27  JMP            14
     28  CONST          R0, 2
     29  MUL            R2, R2, R1
     30  LT             R3, R0, R2
     31  MUL            R2, R1, R1
     32  MUL            R2, R2, R1
     33  LT             R3, R0, R2
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
     44  JMP            33
     45  HALT           
  ancestry (6 steps, newest first): iteration/fitness/modification
    it   10  28.4071  len 46  swap@25,13
    it    9  21.9207  len 46  swap@24,10+const@28+swap@19,11
    it    8  20.8783  len 46  insert@12
    it    6  16.3227  len 45  delete@33
    it    2  20.9443  len 46  delete@3+duplicate@23+2->5
    it    1  21.4565  len 45  duplicate@24+2->23+splice@13<-donor[27:31]:5cd41b9c6d1da0a9
    it    0  17.8392  len 39  seed:ENUMERATE_VM

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7315.4    5.3   74.7
  top1_6f29e1bb9d20323a       21.748  21.748  21.748  21.748  21.3  21.3    10033    10033       7.2    1.0    0.0
  top2_c477f327ebeb3d4b       21.748  21.748  21.748  21.748  21.3  21.3    10033    10033       7.2    1.0    0.0
  top3_ed5de93aa267b52f       21.748  21.748  21.748  21.748  21.3  21.3    10033    10033       7.2    1.0    0.0
  contemp_c5a93ef0c4ece9e7    21.748  21.748  21.748  21.748  21.3  21.3    10033    10033       7.2    1.0    0.0
  ancestor128_it299_ed5de93a  21.748  21.748  21.748  21.748  21.3  21.3    10033    10033       7.2    1.0    0.0
  contemp_b8e731c6b9584466    21.748  21.748  21.748  21.748  21.3  21.3    10033    10033       7.2    1.0    0.0
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.9    3.7    1.7
  ancestor64_it142_10eace10e  20.411  20.411  20.411  20.411  20.0  20.0    10556    10556       7.1    1.0    0.0
  bestever_c1c82b4c7a9799c7   20.080  20.080  20.080  20.080  19.7  19.7    10205    10205       7.2    1.0    0.0
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ancestor1_it0_0875253d162c  19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  contemp_f6143601abe6b82d    13.614  13.614  13.614  13.614  13.3  13.3    25468    25468       7.2    1.0 12936.7
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.02/ 455.13   14.92/ 539.10   21.12/  47.94   33.22/  48.94   40.08/  50.52
  top1_6f29e1bb9d20323a       429.52/ 429.65  463.95/ 464.10   48.76/  48.91   51.08/  51.23   51.88/  52.03
  top2_c477f327ebeb3d4b       429.52/ 429.65  463.95/ 464.10   48.76/  48.91   51.08/  51.23   51.88/  52.03
  top3_ed5de93aa267b52f       429.52/ 429.65  463.95/ 464.10   48.76/  48.91   51.08/  51.23   51.88/  52.03
  contemp_c5a93ef0c4ece9e7    429.52/ 429.65  463.95/ 464.10   48.76/  48.91   51.08/  51.23   51.88/  52.03
  ancestor128_it299_ed5de93a  429.52/ 429.65  463.95/ 464.10   48.76/  48.91   51.08/  51.23   51.88/  52.03
  contemp_b8e731c6b9584466    429.53/ 429.66  463.96/ 464.11   48.77/  48.92   51.09/  51.24   51.89/  52.04
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.14/ 443.81  528.13/ 527.79   47.94/  47.89   48.86/  48.88   50.43/  50.46
  ancestor64_it142_10eace10e  450.11/ 450.24  498.79/ 498.93   49.02/  49.17   50.88/  51.02   49.89/  50.04
  bestever_c1c82b4c7a9799c7   457.09/ 457.22  455.82/ 455.96   50.59/  50.74   50.43/  50.58   52.10/  52.25
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ancestor1_it0_0875253d162c  495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  ENUMERATE_VM_C1             495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  contemp_f6143601abe6b82d   1370.92/1371.04 1175.86/1176.00   51.33/  51.47   51.94/  52.09   53.03/  53.18
  RANDOM_C1                  1662.62/1662.62 1627.07/1627.07   50.50/  50.50   50.50/  50.50   48.56/  48.56

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  top1_6f29e1bb9d20323a          6/36    47     1/30    49     0/12    50     0/12    50    28/30   412    29/30   446
  top2_c477f327ebeb3d4b          6/36    47     1/30    49     0/12    50     0/12    50    28/30   412    29/30   446
  top3_ed5de93aa267b52f          6/36    47     1/30    49     0/12    50     0/12    50    28/30   412    29/30   446
  contemp_c5a93ef0c4ece9e7       6/36    47     1/30    49     0/12    50     0/12    50    28/30   412    29/30   446
  ancestor128_it299_ed5de93a     6/36    47     1/30    49     0/12    50     0/12    50    28/30   412    29/30   446
  contemp_b8e731c6b9584466       6/36    47     1/30    49     0/12    50     0/12    50    28/30   412    29/30   446
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  ancestor64_it142_10eace10e     3/36    47     1/30    49     1/12    46     0/12    50    27/30   432    28/30   479
  bestever_c1c82b4c7a9799c7      2/36    48     2/30    48     0/12    50     0/12    50    27/30   438    28/30   436
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ancestor1_it0_0875253d162c     2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  contemp_f6143601abe6b82d       2/36    48     1/30    49     0/12    50     0/12    50    19/30  1292    18/30  1108
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.27    49.53    36.27    36.27    49.53    49.53    49.53   5.0
  top1_6f29e1bb9d20323a         51.44    51.45    51.44    51.44    51.45    51.45    51.45   1.0
  top2_c477f327ebeb3d4b         51.44    51.45    51.44    51.44    51.45    51.45    51.45   1.0
  top3_ed5de93aa267b52f         51.44    51.45    51.44    51.44    51.45    51.45    51.45   1.0
  contemp_c5a93ef0c4ece9e7      51.44    51.45    51.44    51.44    51.45    51.45    51.45   1.0
  ancestor128_it299_ed5de93a    51.44    51.45    51.44    51.44    51.45    51.45    51.45   1.0
  contemp_b8e731c6b9584466      51.45    51.46    51.45    51.45    51.46    51.46    51.46   1.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.56    49.55    49.56    49.56    49.55    49.55    49.55   2.0
  ancestor64_it142_10eace10e    50.44    50.45    50.44    50.44    50.45    50.45    50.45   1.0
  bestever_c1c82b4c7a9799c7     51.17    51.18    51.17    51.17    51.18    51.18    51.18   1.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ancestor1_it0_0875253d162c    51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  ENUMERATE_VM_C1               51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  contemp_f6143601abe6b82d      52.42    52.43    52.42    52.42    52.43    52.43    52.43   1.0
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
  top1_6f29e1bb9d20323a
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 20, 26] vs FRESH [18, 20, 26]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.4] vs 5% of FRESH cost [1560.9, 1533.9, 1451.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.88, 51.88, 50.55] vs CODE_ONLY [51.89, 51.89, 50.56]
    4_scramble_or_reset_damages            0/3  eff ACC [18.386, 20.416, 26.443] SCR [18.386, 20.416, 26.443] RESET [18.386, 20.416, 26.443]
    5_transfers_to_fresh_copy              0/3  FULL [51.88, 51.88, 50.55] vs ACC remainder [51.88, 51.88, 50.55]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.89, 51.89, 50.56] vs ACC remainder [51.88, 51.88, 50.55]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.89, 51.89, 50.56] STORAGE_MATCHED [51.89, 51.89, 50.56] vs ACC remainder [51.88, 51.88, 50.55]
  top2_c477f327ebeb3d4b
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 20, 26] vs FRESH [18, 20, 26]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.4] vs 5% of FRESH cost [1560.9, 1533.9, 1451.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.88, 51.88, 50.55] vs CODE_ONLY [51.89, 51.89, 50.56]
    4_scramble_or_reset_damages            0/3  eff ACC [18.386, 20.416, 26.443] SCR [18.386, 20.416, 26.443] RESET [18.386, 20.416, 26.443]
    5_transfers_to_fresh_copy              0/3  FULL [51.88, 51.88, 50.55] vs ACC remainder [51.88, 51.88, 50.55]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.89, 51.89, 50.56] vs ACC remainder [51.88, 51.88, 50.55]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.89, 51.89, 50.56] STORAGE_MATCHED [51.89, 51.89, 50.56] vs ACC remainder [51.88, 51.88, 50.55]
  top3_ed5de93aa267b52f
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 20, 26] vs FRESH [18, 20, 26]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.4] vs 5% of FRESH cost [1560.9, 1533.9, 1451.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.88, 51.88, 50.55] vs CODE_ONLY [51.89, 51.89, 50.56]
    4_scramble_or_reset_damages            0/3  eff ACC [18.386, 20.416, 26.443] SCR [18.386, 20.416, 26.443] RESET [18.386, 20.416, 26.443]
    5_transfers_to_fresh_copy              0/3  FULL [51.88, 51.88, 50.55] vs ACC remainder [51.88, 51.88, 50.55]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.89, 51.89, 50.56] vs ACC remainder [51.88, 51.88, 50.55]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.89, 51.89, 50.56] STORAGE_MATCHED [51.89, 51.89, 50.56] vs ACC remainder [51.88, 51.88, 50.55]
  contemp_c5a93ef0c4ece9e7
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 20, 26] vs FRESH [18, 20, 26]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.4] vs 5% of FRESH cost [1560.9, 1533.9, 1451.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.88, 51.88, 50.55] vs CODE_ONLY [51.89, 51.89, 50.56]
    4_scramble_or_reset_damages            0/3  eff ACC [18.386, 20.416, 26.443] SCR [18.386, 20.416, 26.443] RESET [18.386, 20.416, 26.443]
    5_transfers_to_fresh_copy              0/3  FULL [51.88, 51.88, 50.55] vs ACC remainder [51.88, 51.88, 50.55]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.89, 51.89, 50.56] vs ACC remainder [51.88, 51.88, 50.55]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.89, 51.89, 50.56] STORAGE_MATCHED [51.89, 51.89, 50.56] vs ACC remainder [51.88, 51.88, 50.55]
  ancestor128_it299_ed5de93aa267b52f
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 20, 26] vs FRESH [18, 20, 26]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.4] vs 5% of FRESH cost [1560.9, 1533.9, 1451.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.88, 51.88, 50.55] vs CODE_ONLY [51.89, 51.89, 50.56]
    4_scramble_or_reset_damages            0/3  eff ACC [18.386, 20.416, 26.443] SCR [18.386, 20.416, 26.443] RESET [18.386, 20.416, 26.443]
    5_transfers_to_fresh_copy              0/3  FULL [51.88, 51.88, 50.55] vs ACC remainder [51.88, 51.88, 50.55]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.89, 51.89, 50.56] vs ACC remainder [51.88, 51.88, 50.55]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.89, 51.89, 50.56] STORAGE_MATCHED [51.89, 51.89, 50.56] vs ACC remainder [51.88, 51.88, 50.55]
  contemp_b8e731c6b9584466
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 20, 26] vs FRESH [18, 20, 26]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.4] vs 5% of FRESH cost [1561.2, 1534.2, 1451.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.89, 51.89, 50.56] vs CODE_ONLY [51.9, 51.9, 50.57]
    4_scramble_or_reset_damages            0/3  eff ACC [18.386, 20.416, 26.443] SCR [18.386, 20.416, 26.443] RESET [18.386, 20.416, 26.443]
    5_transfers_to_fresh_copy              0/3  FULL [51.89, 51.89, 50.56] vs ACC remainder [51.89, 51.89, 50.56]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.9, 51.9, 50.57] vs ACC remainder [51.89, 51.89, 50.56]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.9, 51.9, 50.57] STORAGE_MATCHED [51.9, 51.9, 50.57] vs ACC remainder [51.89, 51.89, 50.56]
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
  ancestor64_it142_10eace10eb344175
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 19, 22] vs FRESH [19, 19, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.4, 4.3, 4.4] vs 5% of FRESH cost [1522.4, 1469.3, 1509.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.88, 49.23, 50.21] vs CODE_ONLY [51.89, 49.23, 50.21]
    4_scramble_or_reset_damages            0/3  eff ACC [19.379, 19.413, 22.44] SCR [19.379, 19.413, 22.44] RESET [19.379, 19.413, 22.44]
    5_transfers_to_fresh_copy              0/3  FULL [51.88, 49.23, 50.21] vs ACC remainder [51.88, 49.23, 50.21]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.89, 49.23, 50.21] vs ACC remainder [51.88, 49.23, 50.21]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.89, 49.23, 50.21] STORAGE_MATCHED [51.89, 49.23, 50.21] vs ACC remainder [51.88, 49.23, 50.21]
  bestever_c1c82b4c7a9799c7
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 18, 23] vs FRESH [18, 18, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.3] vs 5% of FRESH cost [1567.5, 1552.9, 1477.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.1, 52.1, 49.32] vs CODE_ONLY [52.11, 52.11, 49.33]
    4_scramble_or_reset_damages            0/3  eff ACC [18.383, 18.413, 23.444] SCR [18.383, 18.413, 23.444] RESET [18.383, 18.413, 23.444]
    5_transfers_to_fresh_copy              0/3  FULL [52.1, 52.1, 49.32] vs ACC remainder [52.1, 52.1, 49.32]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.11, 52.11, 49.33] vs ACC remainder [52.1, 52.1, 49.32]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.11, 52.11, 49.33] STORAGE_MATCHED [52.11, 52.11, 49.33] vs ACC remainder [52.1, 52.1, 49.32]
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
  contemp_f6143601abe6b82d
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [12, 12, 16] vs FRESH [12, 12, 16]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.5] vs 5% of FRESH cost [1595.4, 1560.4, 1536.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [53.03, 53.03, 51.21] vs CODE_ONLY [53.04, 53.04, 51.22]
    4_scramble_or_reset_damages            0/3  eff ACC [12.317, 12.25, 16.274] SCR [12.317, 12.25, 16.274] RESET [12.317, 12.25, 16.274]
    5_transfers_to_fresh_copy              0/3  FULL [53.03, 53.03, 51.21] vs ACC remainder [53.03, 53.03, 51.21]
    6_executable_components_reused         0/3  invocations [10767, 14673, 13370]; ABLATION_ALL cost [53.04, 53.04, 51.22] vs ACC remainder [53.03, 53.03, 51.21]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [53.04, 53.04, 51.22] STORAGE_MATCHED [53.04, 53.04, 51.22] vs ACC remainder [53.03, 53.03, 51.21]
  RANDOM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 6, 9] vs FRESH [6, 6, 9]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1493.8, 1515.0, 1489.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.32, 50.5, 49.1] vs CODE_ONLY [49.32, 50.5, 49.1]
    4_scramble_or_reset_damages            0/3  eff ACC [6.205, 6.235, 9.221] SCR [6.205, 6.235, 9.221] RESET [6.205, 6.235, 9.221]
    5_transfers_to_fresh_copy              0/3  FULL [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.32, 50.5, 49.1]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.32, 50.5, 49.1] STORAGE_MATCHED [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]

MACHINERY OF top1_6f29e1bb9d20323a (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   1    32
    task  9:     0    0    0    0    0 |   1    32
    task 19:     0    0    0    0    0 |   1    32
    task 31:     0    0    0    0    0 |   1    32
    task 41:     0    0    0    0    0 |   1    32
    task 49:     0    0    0    0    0 |   1    32
  artifact events: 1 (create 1, delete 0, patch/append 0); invocations by block: {}; edges: 0
    block 0 origin=calibration len=0 state=[[2, 3, 6, 8, 10, 4, 9, 11, 5, 0, 7, 1], [9, 11, 0, 1, 5, 8, 2, 10, 3, 6, 4, 7], 0] instr=[]
  adaptation curve ACC:   139 2073 58 895 27 102 49 1625 94 150 212 284 895 895 24 1392 1392 21 2073 60 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
  adaptation curve FRESH: 139 2074 58 895 27 102 49 1626 94 150 213 284 895 895 24 1392 1392 21 2074 60 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
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

