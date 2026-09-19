CRIUS CAMPAIGN 0 REPORT  run=search_c0x_seeded_s2  arm=seeded
code_commit=f4dae7a66 dirty=True config_hash=a204326d0078673d world=57065ca240cee53d partitions=ece4bd004beb4710
==============================================================================
SEARCH PROGRESS (fitness = C0_EFFICIENCY, mean over search seeds; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1   1.6157    1.3886         0.5098        39          1
    26   1.7352    1.7213         0.7607        41         18
    51   1.8590    1.8521         1.0497        43         39
    76   1.9108    1.8982         1.0408        53         63
   101   1.9131    1.9128         0.8886        48         80
   126   1.9217    1.9211         1.1717        48         95
   151   1.9241    1.9239         0.9962        47        110
   176   1.9263    1.9260         1.0604        42        126
   201   1.9425    1.9422         1.1962        47        148
   226   1.9462    1.9462         1.1893        47        162
   251   1.9462    1.9462         0.9291        42        182
   276   1.9463    1.9463         0.7280        37        206
   300   1.9463    1.9463         0.8757        35        226
  candidates evaluated: 7208   best_ever 1.9463 (e2f253a285470e80)  wall 226s

BEST PROGRAM e2f253a285470e80 (len 41, iteration 259, modification delete@28)
  search seed 101: eff 2.0819 succ 50/50 inter 3070 steps 13516 ws_cost 0 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [3.61, 1.0], "B": [2.747, 1.0], "C": [32.247, 1.0], "D": [215.66, 1.0], "E": [74.754, 1.0]}
  search seed 102: eff 1.8108 succ 50/50 inter 2421 steps 11074 ws_cost 0 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [3.496, 1.0], "B": [4.257, 1.0], "C": [32.247, 1.0], "D": [150.851, 1.0], "E": [69.843, 1.0]}
  listing:
      0  INPUT          R1, num_ops
      1  CONST          R5, 1
      2  ACT            R3
      3  ACTI           -15
      4  ACT            R5
      5  CONST          R0, -4
      6  JMP            18
      7  WS_REC_SET     R1, R6, R3
      8  ADD            R3, R7, R1
      9  WS_FREE        R2
     10  ADD            R4, R7, R6
     11  WS_REC_SET     R1, R6, R3
     12  WS_READ        R6, R7
     13  JMP            18
     14  ADD            R0, R0, R5
     15  ACT            R3
     16  JMP            15
     17  VSET           R3, R6, R5
     18  MUL            R2, R1, R1
     19  LT             R3, R0, R2
     20  BRZ            R3, 28
     21  ACT            R1
     22  MOD            R3, R0, R1
     23  ACT            R3
     24  DIV            R4, R0, R1
     25  ACT            R4
     26  ADD            R0, R0, R5
     27  JMP            19
     28  ACT            R1
     29  MOD            R3, R0, R1
     30  ACT            R3
     31  DIV            R4, R0, R1
     32  ACT            R0
     33  DIV            R4, R4, R1
     34  MOD            R3, R4, R1
     35  ACT            R3
     36  ADD            R0, R0, R5
     37  ADD            R0, R0, R5
     38  JMP            28
     39  BLK_LEN        R7, R1
     40  ACT            R1
  ancestry (82 steps, newest first): iteration/fitness/modification
    it  259  1.9463  len 41  delete@28
    it  258  1.9462  len 42  replace@9
    it  257  1.9462  len 42  delete@11
    it  255  1.9462  len 43  duplicate@11+1->7
    it  249  1.9462  len 42  delete@13
    it  240  1.9462  len 43  delete@14
    it  236  1.9462  len 44  delete@16
    it  234  1.9462  len 45  arg@12.1+arg@20.0
    it  232  1.9462  len 45  delete@8+arg@2.0
    it  231  1.9462  len 46  arg@2.0
    it  229  1.9462  len 46  arg@22.0+arg@19.0
    it  227  1.9462  len 46  delete@20
    it  225  1.9462  len 47  delete@45+arg@14.0
    it  224  1.9462  len 48  delete@19
    it  223  1.9462  len 49  delete@19
    ... 68 more

QUALIFICATION suite=heldout_v1 seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED)
  player                        effA    effF    effR    effS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  CACHE_REUSE                  2.965   1.575   2.878   1.620  50.0  49.0     1332     6917    5315.7    0.0    0.0
  ADAPTIVE                     1.972   1.561   2.644   1.417  50.0  49.0     1332     6917    4436.4   27.7    8.7
  ENUMERATE                    1.635   1.635   1.635   1.635  49.0  49.0     6917     6917       0.0    0.0    0.0
  HEURISTIC                    1.591   1.591   1.591   1.591  42.0  42.0     1874     1874       0.0    0.0    0.0
  ancestor1_it0_0875253d162c   1.506   1.506   1.506   1.506  48.0  48.0     5611     5611       0.0    0.0    0.0
  ENUMERATE_VM                 1.506   1.506   1.506   1.506  48.0  48.0     5611     5611       0.0    0.0    0.0
  ancestor42_it133_553a211cc   1.397   1.397   1.397   1.397  45.0  45.0     7528     7528       0.0    0.0    0.0
  top1_4bc201b44e35e9a6        1.389   1.389   1.389   1.389  45.0  45.0     7653     7653       0.0    0.0    0.0
  top2_5daf8049f5d19573        1.389   1.389   1.389   1.389  45.0  45.0     7653     7653       0.0    0.0    0.0
  top3_6b59180fc43563a3        1.389   1.389   1.389   1.389  45.0  45.0     7653     7653       0.0    0.0    0.0
  ancestor82_it258_c9c1117b0   1.389   1.389   1.389   1.389  45.0  45.0     7653     7653       0.0    0.0    0.0
  contemp_0c8bf897cbf3ffad     0.808   0.814   0.811   0.808  36.0  36.0    13271    13271       0.0    0.0    0.0
  contemp_1ee366902b59c02f     0.566   0.566   0.566   0.566  25.3  25.3    13886    13886       0.0    0.0    0.0
  RANDOM                       0.205   0.205   0.205   0.205   3.3   3.3    14823    14823       0.0    0.0    0.0
  contemp_2803a48e34b50caa     0.100   0.100   0.100   0.100   3.0   3.0    14569    14569       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  CACHE_REUSE                   9.89/   4.29    8.07/   4.36    2.65/  33.14    6.18/ 259.04  184.78/ 499.06
  ADAPTIVE                     11.56/   4.83    9.37/   4.90    3.24/  33.74   10.51/ 259.64  288.27/ 499.66
  ENUMERATE                     3.48/   3.48    3.54/   3.54   31.87/  31.87  255.22/ 255.22  492.37/ 492.37
  HEURISTIC                     3.48/   3.48    3.54/   3.54   34.80/  34.80   60.61/  60.61   98.65/  98.65
  ancestor1_it0_0875253d162c    3.72/   3.72    3.79/   3.79   34.59/  34.59  264.39/ 264.39  342.45/ 342.45
  ENUMERATE_VM                  3.72/   3.72    3.79/   3.79   34.59/  34.59  264.39/ 264.39  342.45/ 342.45
  ancestor42_it133_553a211cc    3.75/   3.75    3.81/   3.81   34.58/  34.58  251.45/ 251.45  605.71/ 605.71
  top1_4bc201b44e35e9a6         3.64/   3.64    3.71/   3.71   34.45/  34.45  264.12/ 264.12  604.67/ 604.67
  top2_5daf8049f5d19573         3.64/   3.64    3.71/   3.71   34.45/  34.45  264.12/ 264.12  604.67/ 604.67
  top3_6b59180fc43563a3         3.64/   3.64    3.71/   3.71   34.45/  34.45  264.12/ 264.12  604.67/ 604.67
  ancestor82_it258_c9c1117b0    3.64/   3.64    3.71/   3.71   34.45/  34.45  264.13/ 264.13  604.67/ 604.67
  contemp_0c8bf897cbf3ffad      3.64/   3.64    3.71/   3.71   34.45/  34.45  854.17/ 854.17  641.61/ 641.61
  contemp_1ee366902b59c02f      4.57/   4.57    4.65/   4.65   92.02/  92.02  803.47/ 803.47  644.08/ 644.08
  RANDOM                       15.89/  15.89   14.75/  14.75  121.20/ 121.20  808.00/ 808.00  641.35/ 641.35
  contemp_2803a48e34b50caa     15.15/  15.15   17.50/  17.50  124.41/ 124.41  801.81/ 801.81  658.29/ 658.29

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                      absent_op5_d2  absent_op5_d3         depth4   heldout_pair heldout_triple new_combinatio      primitive  reversed_pair
  CACHE_REUSE                   12/12    58     6/6    496     6/6      4    18/18     2    15/15     3    15/15     3    60/60     2    18/18     2
  ADAPTIVE                      12/12    58     6/6    496     6/6      4    18/18     2    15/15     3    15/15     3    60/60     2    18/18     2
  ENUMERATE                     12/12    58     6/6    496     3/6   1350    18/18    38    15/15   257    15/15   251    60/60     3    18/18    25
  HEURISTIC                      9/12    40     0/6    180     3/6    133    13/18    56    13/15    45    10/15    76    60/60     3    18/18    13
  ancestor1_it0_0875253d162c    12/12    52     6/6    480     0/6    726    18/18    40    15/15   257    15/15   248    60/60     3    18/18    25
  ENUMERATE_VM                  12/12    52     6/6    480     0/6    726    18/18    40    15/15   257    15/15   248    60/60     3    18/18    25
  ancestor42_it133_553a211cc    12/12    52     1/6    723     0/6   1500    18/18    40    13/15   238    13/15   244    60/60     3    18/18    25
  top1_4bc201b44e35e9a6         12/12    52     1/6    723     0/6   1500    18/18    40    13/15   238    13/15   269    60/60     3    18/18    25
  top2_5daf8049f5d19573         12/12    52     1/6    723     0/6   1500    18/18    40    13/15   238    13/15   269    60/60     3    18/18    25
  top3_6b59180fc43563a3         12/12    52     1/6    723     0/6   1500    18/18    40    13/15   238    13/15   269    60/60     3    18/18    25
  ancestor82_it258_c9c1117b0    12/12    52     1/6    723     0/6   1500    18/18    40    13/15   238    13/15   269    60/60     3    18/18    25
  contemp_0c8bf897cbf3ffad      12/12    52     0/6    800     0/6   1500    18/18    40     0/15   800     0/15   800    60/60     3    18/18    25
  contemp_1ee366902b59c02f       5/12    94     0/6    800     0/6   1500     5/18    89     1/15   752     0/15   800    60/60     4     5/18    88
  RANDOM                         0/12   120     0/6    800     0/6   1500     0/18   120     0/15   800     0/15   800    10/60    15     0/18   120
  contemp_2803a48e34b50caa       0/12   120     0/6    800     0/6   1500     0/18   120     0/15   800     1/15   747     8/60    16     0/18   120

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  CACHE_REUSE                   85.56       --    93.37    85.56    93.37    93.37    93.37   0.0
  ADAPTIVE                     133.96   106.96   142.50   133.96   114.87   114.87   114.87  10.7
  ENUMERATE                    360.62       --   360.62   360.62   360.62   360.62   360.62   0.0
  HEURISTIC                     77.52       --    77.52    77.52    77.52    77.52    77.52   0.0
  ancestor1_it0_0875253d162c   299.08       --   299.08   299.08   299.08   299.08   299.08   0.0
  ENUMERATE_VM                 299.08       --   299.08   299.08   299.08   299.08   299.08   0.0
  ancestor42_it133_553a211cc   408.90       --   408.90   408.90   408.90   408.90   408.90   0.0
  top1_4bc201b44e35e9a6        415.47       --   415.47   415.47   415.47   415.47   415.47   0.0
  top2_5daf8049f5d19573        415.47       --   415.47   415.47   415.47   415.47   415.47   0.0
  top3_6b59180fc43563a3        415.47       --   415.47   415.47   415.47   415.47   415.47   0.0
  ancestor82_it258_c9c1117b0   415.48       --   415.48   415.48   415.48   415.48   415.48   0.0
  contemp_0c8bf897cbf3ffad     759.70       --   759.70   759.70   759.70   759.70   759.70   0.0
  contemp_1ee366902b59c02f     732.63       --   732.63   732.63   732.63   732.63   732.63   0.0
  RANDOM                       733.93       --   733.93   733.93   733.93   733.93   733.93   0.0
  contemp_2803a48e34b50caa     738.03       --   738.03   738.03   738.03   738.03   738.03   0.0

CHARTER s13 CHECKLIST (seeds passing / seeds; thresholds: 5 percent relative; guard 0 added 2026-09-19, see report.py)
  CACHE_REUSE
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [50, 50, 50] vs FRESH [49, 49, 49]
    1_cost_declines_via_accumulation       3/3  reuse_gain C-E per seed [5178.1, 5454.4, 5593.9] vs 5% of FRESH cost [6646.6, 7007.8, 7287.4] (and 0 held)
    2_reproduces_on_heldout                3/3  same test, qualification suite; seeds passing = 3/3
    3_state_causal_FULL_vs_CODE_ONLY       2/3  remainder mean cost FULL [79.84, 84.51, 92.32] vs CODE_ONLY [85.9, 88.8, 105.39]
    4_scramble_or_reset_damages            3/3  eff ACC [2.861, 2.921, 3.114] SCR [1.614, 1.556, 1.689] RESET [2.78, 2.849, 3.005]
    5_transfers_to_fresh_copy              2/3  FULL [79.84, 84.51, 92.32] vs ACC remainder [79.84, 84.51, 92.32]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [79.84, 84.51, 92.32]
    7_not_compute_or_storage               3/3  COMPUTE_MATCHED [85.9, 88.8, 105.39] STORAGE_MATCHED [85.9, 88.8, 105.39] vs ACC remainder [79.84, 84.51, 92.32]
  ADAPTIVE
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [50, 50, 50] vs FRESH [49, 49, 49]
    1_cost_declines_via_accumulation       3/3  reuse_gain C-E per seed [4390.1, 4446.1, 4808.9] vs 5% of FRESH cost [6664.5, 7025.7, 7305.3] (and 0 held)
    2_reproduces_on_heldout                3/3  same test, qualification suite; seeds passing = 3/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [124.2, 141.21, 136.47] vs CODE_ONLY [104.78, 115.05, 124.77]
    4_scramble_or_reset_damages            0/3  eff ACC [1.956, 1.841, 2.118] SCR [1.498, 1.316, 1.437] RESET [2.526, 2.624, 2.783]
    5_transfers_to_fresh_copy              0/3  FULL [124.2, 141.21, 136.47] vs ACC remainder [124.2, 141.21, 136.47]
    6_executable_components_reused         0/3  invocations [9, 9, 8]; ABLATION_ALL cost [98.34, 110.86, 111.7] vs ACC remainder [124.2, 141.21, 136.47]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [104.78, 115.05, 124.77] STORAGE_MATCHED [104.78, 115.05, 124.77] vs ACC remainder [124.2, 141.21, 136.47]
  ENUMERATE
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [49, 49, 49] vs FRESH [49, 49, 49]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [6543.4, 6900.1, 7176.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [343.29, 360.87, 377.7] vs CODE_ONLY [343.29, 360.87, 377.7]
    4_scramble_or_reset_damages            0/3  eff ACC [1.769, 1.505, 1.632] SCR [1.769, 1.505, 1.632] RESET [1.769, 1.505, 1.632]
    5_transfers_to_fresh_copy              0/3  FULL [343.29, 360.87, 377.7] vs ACC remainder [343.29, 360.87, 377.7]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [343.29, 360.87, 377.7]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [343.29, 360.87, 377.7] STORAGE_MATCHED [343.29, 360.87, 377.7] vs ACC remainder [343.29, 360.87, 377.7]
  HEURISTIC
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [44, 42, 40] vs FRESH [44, 42, 40]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1854.6, 1657.6, 1926.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [83.65, 66.96, 81.94] vs CODE_ONLY [83.65, 66.96, 81.94]
    4_scramble_or_reset_damages            0/3  eff ACC [1.842, 1.479, 1.453] SCR [1.842, 1.479, 1.453] RESET [1.842, 1.479, 1.453]
    5_transfers_to_fresh_copy              0/3  FULL [83.65, 66.96, 81.94] vs ACC remainder [83.65, 66.96, 81.94]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [83.65, 66.96, 81.94]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [83.65, 66.96, 81.94] STORAGE_MATCHED [83.65, 66.96, 81.94] vs ACC remainder [83.65, 66.96, 81.94]
  ancestor1_it0_0875253d162cdf0f
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [48, 48, 48] vs FRESH [48, 48, 48]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [4920.9, 6275.5, 6199.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [248.65, 325.66, 322.94] vs CODE_ONLY [248.65, 325.66, 322.94]
    4_scramble_or_reset_damages            0/3  eff ACC [1.622, 1.428, 1.467] SCR [1.622, 1.428, 1.467] RESET [1.622, 1.428, 1.467]
    5_transfers_to_fresh_copy              0/3  FULL [248.65, 325.66, 322.94] vs ACC remainder [248.65, 325.66, 322.94]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [248.65, 325.66, 322.94]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [248.65, 325.66, 322.94] STORAGE_MATCHED [248.65, 325.66, 322.94] vs ACC remainder [248.65, 325.66, 322.94]
  ENUMERATE_VM
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [48, 48, 48] vs FRESH [48, 48, 48]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [4920.9, 6275.5, 6199.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [248.65, 325.66, 322.94] vs CODE_ONLY [248.65, 325.66, 322.94]
    4_scramble_or_reset_damages            0/3  eff ACC [1.622, 1.428, 1.467] SCR [1.622, 1.428, 1.467] RESET [1.622, 1.428, 1.467]
    5_transfers_to_fresh_copy              0/3  FULL [248.65, 325.66, 322.94] vs ACC remainder [248.65, 325.66, 322.94]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [248.65, 325.66, 322.94]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [248.65, 325.66, 322.94] STORAGE_MATCHED [248.65, 325.66, 322.94] vs ACC remainder [248.65, 325.66, 322.94]
  ancestor42_it133_553a211ccea2eeec
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [45, 46, 44] vs FRESH [45, 46, 44]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [7802.0, 6982.0, 8541.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [408.72, 364.91, 453.06] vs CODE_ONLY [408.72, 364.91, 453.06]
    4_scramble_or_reset_damages            0/3  eff ACC [1.4, 1.468, 1.322] SCR [1.4, 1.468, 1.322] RESET [1.4, 1.469, 1.322]
    5_transfers_to_fresh_copy              0/3  FULL [408.72, 364.91, 453.06] vs ACC remainder [408.72, 364.91, 453.06]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [408.72, 364.91, 453.06]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [408.72, 364.91, 453.06] STORAGE_MATCHED [408.72, 364.91, 453.06] vs ACC remainder [408.72, 364.91, 453.06]
  top1_4bc201b44e35e9a6
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [45, 46, 44] vs FRESH [45, 46, 44]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [8190.9, 7007.3, 8477.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [430.42, 366.41, 449.6] vs CODE_ONLY [430.42, 366.41, 449.6]
    4_scramble_or_reset_damages            0/3  eff ACC [1.364, 1.471, 1.332] SCR [1.364, 1.471, 1.332] RESET [1.364, 1.471, 1.332]
    5_transfers_to_fresh_copy              0/3  FULL [430.42, 366.41, 449.6] vs ACC remainder [430.42, 366.41, 449.6]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [430.42, 366.41, 449.6]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [430.42, 366.41, 449.6] STORAGE_MATCHED [430.42, 366.41, 449.6] vs ACC remainder [430.42, 366.41, 449.6]
  top2_5daf8049f5d19573
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [45, 46, 44] vs FRESH [45, 46, 44]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [8190.9, 7007.3, 8477.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [430.42, 366.41, 449.6] vs CODE_ONLY [430.42, 366.41, 449.6]
    4_scramble_or_reset_damages            0/3  eff ACC [1.364, 1.471, 1.332] SCR [1.364, 1.471, 1.332] RESET [1.364, 1.471, 1.332]
    5_transfers_to_fresh_copy              0/3  FULL [430.42, 366.41, 449.6] vs ACC remainder [430.42, 366.41, 449.6]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [430.42, 366.41, 449.6]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [430.42, 366.41, 449.6] STORAGE_MATCHED [430.42, 366.41, 449.6] vs ACC remainder [430.42, 366.41, 449.6]
  top3_6b59180fc43563a3
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [45, 46, 44] vs FRESH [45, 46, 44]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [8190.9, 7007.3, 8477.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [430.42, 366.41, 449.6] vs CODE_ONLY [430.42, 366.41, 449.6]
    4_scramble_or_reset_damages            0/3  eff ACC [1.364, 1.471, 1.332] SCR [1.364, 1.471, 1.332] RESET [1.364, 1.471, 1.332]
    5_transfers_to_fresh_copy              0/3  FULL [430.42, 366.41, 449.6] vs ACC remainder [430.42, 366.41, 449.6]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [430.42, 366.41, 449.6]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [430.42, 366.41, 449.6] STORAGE_MATCHED [430.42, 366.41, 449.6] vs ACC remainder [430.42, 366.41, 449.6]
  ancestor82_it258_c9c1117b06365255
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [45, 46, 44] vs FRESH [45, 46, 44]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [8191.0, 7007.5, 8477.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [430.43, 366.41, 449.61] vs CODE_ONLY [430.43, 366.41, 449.61]
    4_scramble_or_reset_damages            0/3  eff ACC [1.364, 1.471, 1.332] SCR [1.364, 1.471, 1.332] RESET [1.364, 1.471, 1.332]
    5_transfers_to_fresh_copy              0/3  FULL [430.43, 366.41, 449.61] vs ACC remainder [430.43, 366.41, 449.61]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [430.43, 366.41, 449.61]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [430.43, 366.41, 449.61] STORAGE_MATCHED [430.43, 366.41, 449.61] vs ACC remainder [430.43, 366.41, 449.61]
  contemp_0c8bf897cbf3ffad
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [36, 36, 36] vs FRESH [36, 36, 36]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [14113.8, 14007.2, 14143.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [759.47, 755.29, 764.34] vs CODE_ONLY [759.47, 755.29, 764.34]
    4_scramble_or_reset_damages            0/3  eff ACC [0.807, 0.787, 0.829] SCR [0.807, 0.787, 0.829] RESET [0.81, 0.79, 0.833]
    5_transfers_to_fresh_copy              0/3  FULL [759.47, 755.29, 764.34] vs ACC remainder [759.47, 755.29, 764.34]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [759.47, 755.29, 764.34]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [759.47, 755.29, 764.34] STORAGE_MATCHED [759.47, 755.29, 764.34] vs ACC remainder [759.47, 755.29, 764.34]
  contemp_1ee366902b59c02f
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [23, 26, 27] vs FRESH [23, 26, 27]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [14682.8, 13718.6, 14473.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [752.28, 698.49, 747.12] vs CODE_ONLY [752.28, 698.49, 747.12]
    4_scramble_or_reset_damages            0/3  eff ACC [0.519, 0.564, 0.615] SCR [0.519, 0.564, 0.615] RESET [0.519, 0.564, 0.615]
    5_transfers_to_fresh_copy              0/3  FULL [752.28, 698.49, 747.12] vs ACC remainder [752.28, 698.49, 747.12]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [752.28, 698.49, 747.12]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [752.28, 698.49, 747.12] STORAGE_MATCHED [752.28, 698.49, 747.12] vs ACC remainder [752.28, 698.49, 747.12]
  RANDOM
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [3, 2, 5] vs FRESH [3, 2, 5]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [14665.2, 14665.2, 14665.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [733.93, 733.93, 733.93] vs CODE_ONLY [733.93, 733.93, 733.93]
    4_scramble_or_reset_damages            0/3  eff ACC [0.174, 0.191, 0.25] SCR [0.174, 0.191, 0.25] RESET [0.174, 0.191, 0.25]
    5_transfers_to_fresh_copy              0/3  FULL [733.93, 733.93, 733.93] vs ACC remainder [733.93, 733.93, 733.93]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [733.93, 733.93, 733.93]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [733.93, 733.93, 733.93] STORAGE_MATCHED [733.93, 733.93, 733.93] vs ACC remainder [733.93, 733.93, 733.93]
  contemp_2803a48e34b50caa
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [5, 1, 3] vs FRESH [5, 1, 3]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [14226.6, 15052.8, 15052.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [707.43, 753.33, 753.33] vs CODE_ONLY [707.43, 753.33, 753.33]
    4_scramble_or_reset_damages            0/3  eff ACC [0.102, 0.095, 0.103] SCR [0.102, 0.095, 0.103] RESET [0.102, 0.095, 0.103]
    5_transfers_to_fresh_copy              0/3  FULL [707.43, 753.33, 753.33] vs ACC remainder [707.43, 753.33, 753.33]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [707.43, 753.33, 753.33]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [707.43, 753.33, 753.33] STORAGE_MATCHED [707.43, 753.33, 753.33] vs ACC remainder [707.43, 753.33, 753.33]

MACHINERY OF top1_4bc201b44e35e9a6 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   0     0
    task  9:     0    0    0    0    0 |   0     0
    task 19:     0    0    0    0    0 |   0     0
    task 31:     0    0    0    0    0 |   0     0
    task 41:     0    0    0    0    0 |   0     0
    task 49:     0    0    0    0    0 |   0     0
  artifact events: 0 (create 0, delete 0, patch/append 0); invocations by block: {}; edges: 0
  adaptation curve ACC:   3 1 2 3 3 4 5 5 6 1 1 3 2 2 6 2 6 1 2 6 40 46 38 17 67 59 40 13 13 40 25 46 281 150 109 106 831 213 717 126 126 94 831 831 32 1558 57 57 1558 69
  adaptation curve FRESH: 3 1 2 3 3 4 5 5 6 1 1 3 2 2 6 2 6 1 2 6 40 46 38 17 67 59 40 13 13 40 25 46 281 150 109 106 831 213 717 126 126 94 831 831 32 1558 57 57 1558 69
  reuse_gain per task:    0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0

BASELINES ON SEARCH SUITE (crius/runs/baselines_c0x): effA effF effR effS  succA  interA interF  reuse_gain  blocks
  ADAPTIVE_seed101          5.078  1.839  4.494  1.866   50     114   4139     3906.2   27
  ADAPTIVE_seed102          4.837  1.544  4.212  1.386   50     110   3795     3602.8   26
  CACHE_REUSE_seed101       5.784  1.859  4.700  2.080   50     114   4139     3987.9    0
  CACHE_REUSE_seed102       5.507  1.561  4.435  1.744   50     110   3795     3673.8    0
  ENUMERATE_VM_seed101      1.773  1.773  1.773  1.773   50    4424   4424        0.0    0
  ENUMERATE_VM_seed102      1.458  1.458  1.458  1.458   50    4335   4335        0.0    0
  ENUMERATE_seed101         1.926  1.926  1.926  1.926   50    4139   4139        0.0    0
  ENUMERATE_seed102         1.612  1.612  1.612  1.612   50    3795   3795        0.0    0
  HEURISTIC_seed101         2.215  2.215  2.215  2.215   47    1482   1482        0.0    0
  HEURISTIC_seed102         1.949  1.949  1.949  1.949   48    1410   1410        0.0    0
  RANDOM_seed101            0.193  0.193  0.193  0.193    4   13311  13311        0.0    0
  RANDOM_seed102            0.159  0.159  0.159  0.159    7   13058  13058        0.0    0

