CRIUS CAMPAIGN 0 REPORT  run=search_c0_random_s3  arm=random
code_commit=f4dae7a66 dirty=True config_hash=65fd4678cbcdd9c5 world=57065ca240cee53d partitions=ece4bd004beb4710
==============================================================================
SEARCH PROGRESS (fitness = C0_EFFICIENCY, mean over search seeds; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1   1.4760    1.3191         0.6475        10          1
    26   2.0424    2.0408         0.9336         1         12
    51   2.0424    2.0419         0.8011         1         19
    76   2.0424    2.0419         0.7233         1         31
   101   2.0424    2.0419         1.2506         1         38
   126   2.0424    2.0419         1.1156         1         50
   151   2.0424    2.0419         0.8039         1         62
   176   2.0424    2.0419         1.0437         1         71
   201   2.0424    2.0419         0.9688         1         77
   226   2.0424    2.0419         1.2281         1         82
   251   2.0424    2.0419         0.9955         1         88
   276   2.0424    2.0419         1.0365         1         98
   300   2.0424    2.0419         1.0649         1        104
  candidates evaluated: 7208   best_ever 2.0424 (44b56fef8e705554)  wall 104s

BEST PROGRAM 44b56fef8e705554 (len 1, iteration 19, modification delete@0+delete@1)
  search seed 101: eff 2.6497 succ 4/50 inter 50 steps 50 ws_cost 0 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [1.01, 0.2], "B": [1.01, 0.2], "C": [1.01, 0.0], "D": [1.01, 0.0], "E": [1.01, 0.0]}
  search seed 102: eff 1.4352 succ 2/50 inter 50 steps 50 ws_cost 0 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [1.01, 0.1], "B": [1.01, 0.1], "C": [1.01, 0.0], "D": [1.01, 0.0], "E": [1.01, 0.0]}
  listing:
      0  ACTI           17
  ancestry (14 steps, newest first): iteration/fitness/modification
    it   19  2.0424  len  1  delete@0+delete@1
    it   17  2.0379  len  3  swap@1,0
    it   15  2.0379  len  3  delete@3
    it   14  2.0335  len  4  delete@2+arg@3.1+replace@1
    it   12  2.0335  len  5  delete@1
    it   11  2.0290  len  6  delete@5
    it    9  2.0246  len  7  swap@2,0+delete@5
    it    8  2.0246  len  8  swap@0,7+delete@4
    it    7  2.0246  len  9  insert@7+swap@3,4+insert@6
    it    6  2.0246  len  7  swap@6,3+delete@1+swap@2,3
    it    4  2.0147  len  8  swap@2,3
    it    3  2.0147  len  8  delete@7
    it    2  2.0103  len  9  const@5+arg@9.1+delete@3
    it    1  1.3026  len 10  delete@7+arg@7.0
    it    0  1.3026  len 11  random_init

QUALIFICATION suite=heldout_v1 seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED)
  player                        effA    effF    effR    effS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  CACHE_REUSE                  2.965   1.575   2.878   1.620  50.0  49.0     1332     6917    5315.7    0.0    0.0
  HEURISTIC                    2.245   2.245   2.245   2.245  42.0  42.0     1874     1874       0.0    0.0    0.0
  top1_011f847af76d3980        2.025   2.025   2.025   2.025   4.0   4.0       50       50       0.0    0.0    0.0
  top2_44b56fef8e705554        2.025   2.025   2.025   2.025   4.0   4.0       50       50       0.0    0.0    0.0
  top3_5a043a8968ae7e07        2.025   2.025   2.025   2.025   4.0   4.0       50       50       0.0    0.0    0.0
  contemp_265ee84f006cb0a6     2.021   2.021   2.021   2.021   4.0   4.0       50       50       0.0    0.0    0.0
  ancestor14_it17_7f04253345   2.021   2.021   2.021   2.021   4.0   4.0       50       50       0.0    0.0    0.0
  ancestor8_it8_d1aa9be58edd   2.007   2.007   2.007   2.007   4.0   4.0       50       50       0.0    0.0    0.0
  ADAPTIVE                     1.972   1.561   2.644   1.417  50.0  49.0     1332     6917    4436.4   27.7    8.7
  ENUMERATE                    1.635   1.635   1.635   1.635  49.0  49.0     6917     6917       0.0    0.0    0.0
  ENUMERATE_VM                 1.601   1.601   1.601   1.601  48.0  48.0     5611     5611       0.0    0.0    0.0
  ancestor1_it0_32295e8a6876   1.484   1.488   1.487   1.484   3.7   3.7       50       50       0.0    0.0    0.0
  contemp_17658d0f517c5ea6     0.699   0.699   0.699   0.699   2.3   2.3       50       50       0.0    0.0    0.0
  RANDOM                       0.205   0.205   0.205   0.205   3.3   3.3    14823    14823       0.0    0.0    0.0
  contemp_1423375d8734c5a9     0.000   0.000   0.000   0.000   0.0   0.0        0        0       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  CACHE_REUSE                   9.89/   4.29    8.07/   4.36    2.65/  33.14    6.18/ 259.04  184.78/ 499.06
  HEURISTIC                     3.48/   3.48    3.54/   3.54   34.80/  34.80   60.61/  60.61   98.65/  98.65
  top1_011f847af76d3980         1.01/   1.01    1.01/   1.01    1.01/   1.01    1.01/   1.01    1.01/   1.01
  top2_44b56fef8e705554         1.01/   1.01    1.01/   1.01    1.01/   1.01    1.01/   1.01    1.01/   1.01
  top3_5a043a8968ae7e07         1.01/   1.01    1.01/   1.01    1.01/   1.01    1.01/   1.01    1.01/   1.01
  contemp_265ee84f006cb0a6      1.03/   1.03    1.03/   1.03    1.03/   1.03    1.03/   1.03    1.03/   1.03
  ancestor14_it17_7f04253345    1.03/   1.03    1.03/   1.03    1.03/   1.03    1.03/   1.03    1.03/   1.03
  ancestor8_it8_d1aa9be58edd    1.09/   1.09    1.09/   1.09    1.09/   1.09    1.09/   1.09    1.09/   1.09
  ADAPTIVE                     11.56/   4.83    9.37/   4.90    3.24/  33.74   10.51/ 259.64  288.27/ 499.66
  ENUMERATE                     3.48/   3.48    3.54/   3.54   31.87/  31.87  255.22/ 255.22  492.37/ 492.37
  ENUMERATE_VM                  3.72/   3.72    3.79/   3.79   34.59/  34.59  264.39/ 264.39  342.45/ 342.45
  ancestor1_it0_32295e8a6876    1.14/   1.14    1.14/   1.14    1.14/   1.14    1.14/   1.14    1.14/   1.14
  contemp_17658d0f517c5ea6      1.02/   1.02    1.02/   1.02    1.02/   1.02    1.02/   1.02    1.02/   1.02
  RANDOM                       15.89/  15.89   14.75/  14.75  121.20/ 121.20  808.00/ 808.00  641.35/ 641.35
  contemp_1423375d8734c5a9      0.01/   0.01    0.01/   0.01    0.01/   0.01    0.01/   0.01    0.01/   0.01

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                      absent_op5_d2  absent_op5_d3         depth4   heldout_pair heldout_triple new_combinatio      primitive  reversed_pair
  CACHE_REUSE                   12/12    58     6/6    496     6/6      4    18/18     2    15/15     3    15/15     3    60/60     2    18/18     2
  HEURISTIC                      9/12    40     0/6    180     3/6    133    13/18    56    13/15    45    10/15    76    60/60     3    18/18    13
  top1_011f847af76d3980          0/12     1     0/6      1     0/6      1     0/18     1     0/15     1     0/15     1    12/60     1     0/18     1
  top2_44b56fef8e705554          0/12     1     0/6      1     0/6      1     0/18     1     0/15     1     0/15     1    12/60     1     0/18     1
  top3_5a043a8968ae7e07          0/12     1     0/6      1     0/6      1     0/18     1     0/15     1     0/15     1    12/60     1     0/18     1
  contemp_265ee84f006cb0a6       0/12     1     0/6      1     0/6      1     0/18     1     0/15     1     0/15     1    12/60     1     0/18     1
  ancestor14_it17_7f04253345     0/12     1     0/6      1     0/6      1     0/18     1     0/15     1     0/15     1    12/60     1     0/18     1
  ancestor8_it8_d1aa9be58edd     0/12     1     0/6      1     0/6      1     0/18     1     0/15     1     0/15     1    12/60     1     0/18     1
  ADAPTIVE                      12/12    58     6/6    496     6/6      4    18/18     2    15/15     3    15/15     3    60/60     2    18/18     2
  ENUMERATE                     12/12    58     6/6    496     3/6   1350    18/18    38    15/15   257    15/15   251    60/60     3    18/18    25
  ENUMERATE_VM                  12/12    52     6/6    480     0/6    726    18/18    40    15/15   257    15/15   248    60/60     3    18/18    25
  ancestor1_it0_32295e8a6876     0/12     1     0/6      1     0/6      1     0/18     1     0/15     1     0/15     1    11/60     1     0/18     1
  contemp_17658d0f517c5ea6       0/12     1     0/6      1     0/6      1     0/18     1     0/15     1     0/15     1     7/60     1     0/18     1
  RANDOM                         0/12   120     0/6    800     0/6   1500     0/18   120     0/15   800     0/15   800    10/60    15     0/18   120
  contemp_1423375d8734c5a9       0/12     0     0/6      0     0/6      0     0/18     0     0/15     0     0/15     0     0/60     0     0/18     0

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  CACHE_REUSE                   85.56       --    93.37    85.56    93.37    93.37    93.37   0.0
  HEURISTIC                     77.52       --    77.52    77.52    77.52    77.52    77.52   0.0
  top1_011f847af76d3980          1.01       --     1.01     1.01     1.01     1.01     1.01   0.0
  top2_44b56fef8e705554          1.01       --     1.01     1.01     1.01     1.01     1.01   0.0
  top3_5a043a8968ae7e07          1.01       --     1.01     1.01     1.01     1.01     1.01   0.0
  contemp_265ee84f006cb0a6       1.03       --     1.03     1.03     1.03     1.03     1.03   0.0
  ancestor14_it17_7f04253345     1.03       --     1.03     1.03     1.03     1.03     1.03   0.0
  ancestor8_it8_d1aa9be58edd     1.09       --     1.09     1.09     1.09     1.09     1.09   0.0
  ADAPTIVE                     133.96   106.96   142.50   133.96   114.87   114.87   114.87  10.7
  ENUMERATE                    360.62       --   360.62   360.62   360.62   360.62   360.62   0.0
  ENUMERATE_VM                 299.08       --   299.08   299.08   299.08   299.08   299.08   0.0
  ancestor1_it0_32295e8a6876     1.14       --     1.14     1.14     1.14     1.14     1.14   0.0
  contemp_17658d0f517c5ea6       1.02       --     1.02     1.02     1.02     1.02     1.02   0.0
  RANDOM                       733.93       --   733.93   733.93   733.93   733.93   733.93   0.0
  contemp_1423375d8734c5a9       0.01       --     0.01     0.01     0.01     0.01     0.01   0.0

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
  HEURISTIC
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [44, 42, 40] vs FRESH [44, 42, 40]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1854.6, 1657.6, 1926.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [83.65, 66.96, 81.94] vs CODE_ONLY [83.65, 66.96, 81.94]
    4_scramble_or_reset_damages            0/3  eff ACC [2.597, 2.205, 1.932] SCR [2.597, 2.205, 1.932] RESET [2.597, 2.205, 1.932]
    5_transfers_to_fresh_copy              0/3  FULL [83.65, 66.96, 81.94] vs ACC remainder [83.65, 66.96, 81.94]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [83.65, 66.96, 81.94]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [83.65, 66.96, 81.94] STORAGE_MATCHED [83.65, 66.96, 81.94] vs ACC remainder [83.65, 66.96, 81.94]
  top1_011f847af76d3980
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [1, 6, 5] vs FRESH [1, 6, 5]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [30.3, 30.3, 30.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1.01, 1.01, 1.01] vs CODE_ONLY [1.01, 1.01, 1.01]
    4_scramble_or_reset_damages            0/3  eff ACC [1.326, 1.988, 2.761] SCR [1.326, 1.988, 2.761] RESET [1.326, 1.988, 2.761]
    5_transfers_to_fresh_copy              0/3  FULL [1.01, 1.01, 1.01] vs ACC remainder [1.01, 1.01, 1.01]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1.01, 1.01, 1.01]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1.01, 1.01, 1.01] STORAGE_MATCHED [1.01, 1.01, 1.01] vs ACC remainder [1.01, 1.01, 1.01]
  top2_44b56fef8e705554
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [1, 6, 5] vs FRESH [1, 6, 5]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [30.3, 30.3, 30.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1.01, 1.01, 1.01] vs CODE_ONLY [1.01, 1.01, 1.01]
    4_scramble_or_reset_damages            0/3  eff ACC [1.326, 1.988, 2.761] SCR [1.326, 1.988, 2.761] RESET [1.326, 1.988, 2.761]
    5_transfers_to_fresh_copy              0/3  FULL [1.01, 1.01, 1.01] vs ACC remainder [1.01, 1.01, 1.01]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1.01, 1.01, 1.01]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1.01, 1.01, 1.01] STORAGE_MATCHED [1.01, 1.01, 1.01] vs ACC remainder [1.01, 1.01, 1.01]
  top3_5a043a8968ae7e07
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [1, 6, 5] vs FRESH [1, 6, 5]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [30.3, 30.3, 30.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1.01, 1.01, 1.01] vs CODE_ONLY [1.01, 1.01, 1.01]
    4_scramble_or_reset_damages            0/3  eff ACC [1.326, 1.988, 2.761] SCR [1.326, 1.988, 2.761] RESET [1.326, 1.988, 2.761]
    5_transfers_to_fresh_copy              0/3  FULL [1.01, 1.01, 1.01] vs ACC remainder [1.01, 1.01, 1.01]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1.01, 1.01, 1.01]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1.01, 1.01, 1.01] STORAGE_MATCHED [1.01, 1.01, 1.01] vs ACC remainder [1.01, 1.01, 1.01]
  contemp_265ee84f006cb0a6
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [1, 6, 5] vs FRESH [1, 6, 5]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [30.9, 30.9, 30.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1.03, 1.03, 1.03] vs CODE_ONLY [1.03, 1.03, 1.03]
    4_scramble_or_reset_damages            0/3  eff ACC [1.323, 1.984, 2.755] SCR [1.323, 1.984, 2.755] RESET [1.323, 1.984, 2.755]
    5_transfers_to_fresh_copy              0/3  FULL [1.03, 1.03, 1.03] vs ACC remainder [1.03, 1.03, 1.03]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1.03, 1.03, 1.03]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1.03, 1.03, 1.03] STORAGE_MATCHED [1.03, 1.03, 1.03] vs ACC remainder [1.03, 1.03, 1.03]
  ancestor14_it17_7f04253345c58ac4
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [1, 6, 5] vs FRESH [1, 6, 5]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [30.9, 30.9, 30.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1.03, 1.03, 1.03] vs CODE_ONLY [1.03, 1.03, 1.03]
    4_scramble_or_reset_damages            0/3  eff ACC [1.323, 1.984, 2.755] SCR [1.323, 1.984, 2.755] RESET [1.323, 1.984, 2.755]
    5_transfers_to_fresh_copy              0/3  FULL [1.03, 1.03, 1.03] vs ACC remainder [1.03, 1.03, 1.03]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1.03, 1.03, 1.03]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1.03, 1.03, 1.03] STORAGE_MATCHED [1.03, 1.03, 1.03] vs ACC remainder [1.03, 1.03, 1.03]
  ancestor8_it8_d1aa9be58edd431b
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [1, 6, 5] vs FRESH [1, 6, 5]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [32.7, 32.7, 32.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1.09, 1.09, 1.09] vs CODE_ONLY [1.09, 1.09, 1.09]
    4_scramble_or_reset_damages            0/3  eff ACC [1.314, 1.971, 2.737] SCR [1.314, 1.971, 2.737] RESET [1.314, 1.971, 2.737]
    5_transfers_to_fresh_copy              0/3  FULL [1.09, 1.09, 1.09] vs ACC remainder [1.09, 1.09, 1.09]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1.09, 1.09, 1.09]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1.09, 1.09, 1.09] STORAGE_MATCHED [1.09, 1.09, 1.09] vs ACC remainder [1.09, 1.09, 1.09]
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
  ENUMERATE_VM
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [48, 48, 48] vs FRESH [48, 48, 48]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [4920.9, 6275.5, 6199.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [248.65, 325.66, 322.94] vs CODE_ONLY [248.65, 325.66, 322.94]
    4_scramble_or_reset_damages            0/3  eff ACC [1.733, 1.515, 1.555] SCR [1.733, 1.515, 1.555] RESET [1.733, 1.515, 1.555]
    5_transfers_to_fresh_copy              0/3  FULL [248.65, 325.66, 322.94] vs ACC remainder [248.65, 325.66, 322.94]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [248.65, 325.66, 322.94]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [248.65, 325.66, 322.94] STORAGE_MATCHED [248.65, 325.66, 322.94] vs ACC remainder [248.65, 325.66, 322.94]
  ancestor1_it0_32295e8a6876cfdb
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [4, 4, 3] vs FRESH [4, 4, 3]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [34.2, 34.2, 34.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1.14, 1.14, 1.14] vs CODE_ONLY [1.14, 1.14, 1.14]
    4_scramble_or_reset_damages            0/3  eff ACC [1.412, 1.738, 1.303] SCR [1.412, 1.738, 1.303] RESET [1.415, 1.741, 1.306]
    5_transfers_to_fresh_copy              0/3  FULL [1.14, 1.14, 1.14] vs ACC remainder [1.14, 1.14, 1.14]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1.14, 1.14, 1.14]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1.14, 1.14, 1.14] STORAGE_MATCHED [1.14, 1.14, 1.14] vs ACC remainder [1.14, 1.14, 1.14]
  contemp_17658d0f517c5ea6
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [2, 3, 2] vs FRESH [2, 3, 2]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [30.6, 30.6, 30.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1.02, 1.02, 1.02] vs CODE_ONLY [1.02, 1.02, 1.02]
    4_scramble_or_reset_damages            0/3  eff ACC [0.662, 0.772, 0.662] SCR [0.662, 0.772, 0.662] RESET [0.662, 0.772, 0.662]
    5_transfers_to_fresh_copy              0/3  FULL [1.02, 1.02, 1.02] vs ACC remainder [1.02, 1.02, 1.02]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1.02, 1.02, 1.02]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1.02, 1.02, 1.02] STORAGE_MATCHED [1.02, 1.02, 1.02] vs ACC remainder [1.02, 1.02, 1.02]
  RANDOM
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [3, 2, 5] vs FRESH [3, 2, 5]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [14665.2, 14665.2, 14665.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [733.93, 733.93, 733.93] vs CODE_ONLY [733.93, 733.93, 733.93]
    4_scramble_or_reset_damages            0/3  eff ACC [0.174, 0.191, 0.25] SCR [0.174, 0.191, 0.25] RESET [0.174, 0.191, 0.25]
    5_transfers_to_fresh_copy              0/3  FULL [733.93, 733.93, 733.93] vs ACC remainder [733.93, 733.93, 733.93]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [733.93, 733.93, 733.93]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [733.93, 733.93, 733.93] STORAGE_MATCHED [733.93, 733.93, 733.93] vs ACC remainder [733.93, 733.93, 733.93]
  contemp_1423375d8734c5a9
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [0.3, 0.3, 0.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [0.01, 0.01, 0.01] vs CODE_ONLY [0.01, 0.01, 0.01]
    4_scramble_or_reset_damages            0/3  eff ACC [0.0, 0.0, 0.0] SCR [0.0, 0.0, 0.0] RESET [0.0, 0.0, 0.0]
    5_transfers_to_fresh_copy              0/3  FULL [0.01, 0.01, 0.01] vs ACC remainder [0.01, 0.01, 0.01]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [0.01, 0.01, 0.01]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [0.01, 0.01, 0.01] STORAGE_MATCHED [0.01, 0.01, 0.01] vs ACC remainder [0.01, 0.01, 0.01]

MACHINERY OF top1_011f847af76d3980 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   0     0
    task  9:     0    0    0    0    0 |   0     0
    task 19:     0    0    0    0    0 |   0     0
    task 31:     0    0    0    0    0 |   0     0
    task 41:     0    0    0    0    0 |   0     0
    task 49:     0    0    0    0    0 |   0     0
  artifact events: 0 (create 0, delete 0, patch/append 0); invocations by block: {}; edges: 0
  adaptation curve ACC:   1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
  adaptation curve FRESH: 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
  reuse_gain per task:    0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0

BASELINES ON SEARCH SUITE (crius/runs/baselines_c0): effA effF effR effS  succA  interA interF  reuse_gain  blocks
  ADAPTIVE_seed101          5.078  1.839  4.494  1.866   50     114   4139     3906.2   27
  ADAPTIVE_seed102          4.837  1.544  4.212  1.386   50     110   3795     3602.8   26
  CACHE_REUSE_seed101       5.784  1.859  4.700  2.080   50     114   4139     3987.9    0
  CACHE_REUSE_seed102       5.507  1.561  4.435  1.744   50     110   3795     3673.8    0
  ENUMERATE_VM_seed101      1.773  1.773  1.773  1.773   50    4424   4424        0.0    0
  ENUMERATE_VM_seed102      1.458  1.458  1.458  1.458   50    4335   4335        0.0    0
  ENUMERATE_seed101         1.926  1.926  1.926  1.926   50    4139   4139        0.0    0
  ENUMERATE_seed102         1.612  1.612  1.612  1.612   50    3795   3795        0.0    0
  HEURISTIC_seed101         2.844  2.844  2.844  2.844   47    1482   1482        0.0    0
  HEURISTIC_seed102         2.127  2.127  2.127  2.127   48    1410   1410        0.0    0
  RANDOM_seed101            0.193  0.193  0.193  0.193    4   13311  13311        0.0    0
  RANDOM_seed102            0.159  0.159  0.159  0.159    7   13058  13058        0.0    0

