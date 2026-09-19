CRIUS CAMPAIGN 0 REPORT  run=search_c0_random_s2  arm=random
code_commit=f4dae7a66 dirty=True config_hash=65fd4678cbcdd9c5 world=57065ca240cee53d partitions=ece4bd004beb4710
==============================================================================
SEARCH PROGRESS (fitness = C0_EFFICIENCY, mean over search seeds; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1   1.5384    1.3289         0.6455        20          0
    26   2.0424    2.0410         1.1279         1          5
    51   2.0424    2.0416         0.9750         1         17
    76   2.0424    2.0419         0.8144         1         24
   101   2.0424    2.0419         1.1065         1         33
   126   2.0424    2.0419         1.1564         1         42
   151   2.2598    2.2588         1.4565         3         50
   176   2.2598    2.2598         1.3211         3         54
   201   2.2598    2.2598         1.2805         3         63
   226   2.2598    2.2598         1.4365         3         67
   251   2.2598    2.2598         1.1668         3         71
   276   2.2598    2.2598         1.2101         3         77
   300   2.2598    2.2598         1.2360         3         84
  candidates evaluated: 7208   best_ever 2.2598 (0e878fc4545f1392)  wall 84s

BEST PROGRAM 0e878fc4545f1392 (len 3, iteration 143, modification delete@1)
  search seed 101: eff 2.7363 succ 10/50 inter 94 steps 144 ws_cost 0 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [1.828, 0.4], "B": [1.626, 0.6], "C": [2.03, 0.0], "D": [2.03, 0.0], "E": [2.03, 0.0]}
  search seed 102: eff 1.7833 succ 5/50 inter 97 steps 147 ws_cost 0 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [1.828, 0.3], "B": [1.929, 0.2], "C": [2.03, 0.0], "D": [2.03, 0.0], "E": [2.03, 0.0]}
  listing:
      0  ACT            R7
      1  ACTI           6
      2  ACTI           -18
  ancestry (17 steps, newest first): iteration/fitness/modification
    it  143  2.2598  len  3  delete@1
    it  139  2.2563  len  4  swap@3,0
    it  137  2.1960  len  4  insert@1
    it  136  2.1993  len  3  insert@2
    it  109  2.0402  len  2  insert@1+replace@1
    it   27  2.0424  len  1  arg@0.0
    it   13  2.0424  len  1  delete@1+arg@0.0
    it   12  2.0402  len  2  replace@0+replace@0+swap@1,0
    it   11  2.0402  len  2  delete@0+replace@0
    it   10  2.0357  len  3  delete@1
    it    9  2.0335  len  4  arg@1.0+const@2+swap@1,2
    it    8  2.0335  len  4  delete@4+replace@0
    it    7  2.0312  len  5  swap@4,5+delete@1
    it    4  2.0290  len  6  insert@2
    it    3  2.0312  len  5  arg@5.0+delete@3+replace@3
    ... 3 more

QUALIFICATION suite=heldout_v1 seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED)
  player                        effA    effF    effR    effS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  CACHE_REUSE                  2.965   1.575   2.878   1.620  50.0  49.0     1332     6917    5315.7    0.0    0.0
  HEURISTIC                    2.245   2.245   2.245   2.245  42.0  42.0     1874     1874       0.0    0.0    0.0
  top1_03ae23db3a570ae4        2.021   2.021   2.021   2.021   6.7   6.7       97       97       0.0    0.0    0.0
  top2_0cea8d651f28c18e        2.021   2.021   2.021   2.021   6.7   6.7       97       97       0.0    0.0    0.0
  top3_0d9e0ba3757f42c6        2.021   2.021   2.021   2.021   6.7   6.7       97       97       0.0    0.0    0.0
  ancestor9_it10_85b83fe006f   2.018   2.018   2.018   2.018   4.0   4.0       50       50       0.0    0.0    0.0
  ancestor17_it139_db24a44ff   2.018   2.018   2.018   2.018   6.7   6.7       97       97       0.0    0.0    0.0
  ADAPTIVE                     1.972   1.561   2.644   1.417  50.0  49.0     1332     6917    4436.4   27.7    8.7
  ENUMERATE                    1.635   1.635   1.635   1.635  49.0  49.0     6917     6917       0.0    0.0    0.0
  ENUMERATE_VM                 1.601   1.601   1.601   1.601  48.0  48.0     5611     5611       0.0    0.0    0.0
  ancestor1_it0_917933876bd5   1.486   1.490   1.489   1.486   3.7   3.7       50       50       0.0    0.0    0.0
  contemp_e0ab64e2260a436e     1.202   1.202   1.202   1.202   4.0   4.0      142      142       0.0    0.0    0.0
  contemp_878b9dcd0db2b2a7     0.939   0.939   0.939   0.939   4.0   4.0       97       97       0.0    0.0    0.0
  contemp_90436432c94b0030     0.247   0.247   0.247   0.247  10.0  10.0    13854    13854       0.0    0.0    0.0
  RANDOM                       0.205   0.205   0.205   0.205   3.3   3.3    14823    14823       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  CACHE_REUSE                   9.89/   4.29    8.07/   4.36    2.65/  33.14    6.18/ 259.04  184.78/ 499.06
  HEURISTIC                     3.48/   3.48    3.54/   3.54   34.80/  34.80   60.61/  60.61   98.65/  98.65
  top1_03ae23db3a570ae4         1.83/   1.83    1.96/   1.96    2.03/   2.03    2.03/   2.03    2.03/   2.03
  top2_0cea8d651f28c18e         1.83/   1.83    1.96/   1.96    2.03/   2.03    2.03/   2.03    2.03/   2.03
  top3_0d9e0ba3757f42c6         1.83/   1.83    1.96/   1.96    2.03/   2.03    2.03/   2.03    2.03/   2.03
  ancestor9_it10_85b83fe006f    1.04/   1.04    1.04/   1.04    1.04/   1.04    1.04/   1.04    1.04/   1.04
  ancestor17_it139_db24a44ff    1.85/   1.85    1.98/   1.98    2.05/   2.05    2.05/   2.05    2.05/   2.05
  ADAPTIVE                     11.56/   4.83    9.37/   4.90    3.24/  33.74   10.51/ 259.64  288.27/ 499.66
  ENUMERATE                     3.48/   3.48    3.54/   3.54   31.87/  31.87  255.22/ 255.22  492.37/ 492.37
  ENUMERATE_VM                  3.72/   3.72    3.79/   3.79   34.59/  34.59  264.39/ 264.39  342.45/ 342.45
  ancestor1_it0_917933876bd5    1.13/   1.13    1.13/   1.13    1.13/   1.13    1.13/   1.13    1.13/   1.13
  contemp_e0ab64e2260a436e      2.70/   2.70    2.57/   2.57    3.04/   3.04    3.04/   3.04    3.04/   3.04
  contemp_878b9dcd0db2b2a7      1.83/   1.83    1.96/   1.96    2.03/   2.03    2.03/   2.03    2.03/   2.03
  contemp_90436432c94b0030     11.28/  11.28   12.51/  12.51  112.96/ 112.96  735.62/ 735.62  647.69/ 647.69
  RANDOM                       15.89/  15.89   14.75/  14.75  121.20/ 121.20  808.00/ 808.00  641.35/ 641.35

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                      absent_op5_d2  absent_op5_d3         depth4   heldout_pair heldout_triple new_combinatio      primitive  reversed_pair
  CACHE_REUSE                   12/12    58     6/6    496     6/6      4    18/18     2    15/15     3    15/15     3    60/60     2    18/18     2
  HEURISTIC                      9/12    40     0/6    180     3/6    133    13/18    56    13/15    45    10/15    76    60/60     3    18/18    13
  top1_03ae23db3a570ae4          0/12     2     0/6      2     0/6      2     0/18     2     0/15     2     0/15     2    20/60     2     0/18     2
  top2_0cea8d651f28c18e          0/12     2     0/6      2     0/6      2     0/18     2     0/15     2     0/15     2    20/60     2     0/18     2
  top3_0d9e0ba3757f42c6          0/12     2     0/6      2     0/6      2     0/18     2     0/15     2     0/15     2    20/60     2     0/18     2
  ancestor9_it10_85b83fe006f     0/12     1     0/6      1     0/6      1     0/18     1     0/15     1     0/15     1    12/60     1     0/18     1
  ancestor17_it139_db24a44ff     0/12     2     0/6      2     0/6      2     0/18     2     0/15     2     0/15     2    20/60     2     0/18     2
  ADAPTIVE                      12/12    58     6/6    496     6/6      4    18/18     2    15/15     3    15/15     3    60/60     2    18/18     2
  ENUMERATE                     12/12    58     6/6    496     3/6   1350    18/18    38    15/15   257    15/15   251    60/60     3    18/18    25
  ENUMERATE_VM                  12/12    52     6/6    480     0/6    726    18/18    40    15/15   257    15/15   248    60/60     3    18/18    25
  ancestor1_it0_917933876bd5     0/12     1     0/6      1     0/6      1     0/18     1     0/15     1     0/15     1    11/60     1     0/18     1
  contemp_e0ab64e2260a436e       0/12     3     0/6      3     0/6      3     0/18     3     0/15     3     0/15     3    12/60     3     0/18     3
  contemp_878b9dcd0db2b2a7       0/12     2     0/6      2     0/6      2     4/18     2     0/15     2     0/15     2     8/60     2     0/18     2
  contemp_90436432c94b0030       0/12   120     0/6    800     0/6   1500     3/18   102     2/15   695     1/15   747    24/60    12     0/18   120
  RANDOM                         0/12   120     0/6    800     0/6   1500     0/18   120     0/15   800     0/15   800    10/60    15     0/18   120

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  CACHE_REUSE                   85.56       --    93.37    85.56    93.37    93.37    93.37   0.0
  HEURISTIC                     77.52       --    77.52    77.52    77.52    77.52    77.52   0.0
  top1_03ae23db3a570ae4          2.03       --     2.03     2.03     2.03     2.03     2.03   0.0
  top2_0cea8d651f28c18e          2.03       --     2.03     2.03     2.03     2.03     2.03   0.0
  top3_0d9e0ba3757f42c6          2.03       --     2.03     2.03     2.03     2.03     2.03   0.0
  ancestor9_it10_85b83fe006f     1.04       --     1.04     1.04     1.04     1.04     1.04   0.0
  ancestor17_it139_db24a44ff     2.05       --     2.05     2.05     2.05     2.05     2.05   0.0
  ADAPTIVE                     133.96   106.96   142.50   133.96   114.87   114.87   114.87  10.7
  ENUMERATE                    360.62       --   360.62   360.62   360.62   360.62   360.62   0.0
  ENUMERATE_VM                 299.08       --   299.08   299.08   299.08   299.08   299.08   0.0
  ancestor1_it0_917933876bd5     1.13       --     1.13     1.13     1.13     1.13     1.13   0.0
  contemp_e0ab64e2260a436e       3.04       --     3.04     3.04     3.04     3.04     3.04   0.0
  contemp_878b9dcd0db2b2a7       2.03       --     2.03     2.03     2.03     2.03     2.03   0.0
  contemp_90436432c94b0030     696.54       --   696.54   696.54   696.54   696.54   696.54   0.0
  RANDOM                       733.93       --   733.93   733.93   733.93   733.93   733.93   0.0

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
  top1_03ae23db3a570ae4
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [5, 7, 8] vs FRESH [5, 7, 8]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [60.9, 60.9, 60.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [2.03, 2.03, 2.03] vs CODE_ONLY [2.03, 2.03, 2.03]
    4_scramble_or_reset_damages            0/3  eff ACC [1.663, 1.871, 2.528] SCR [1.663, 1.871, 2.528] RESET [1.663, 1.871, 2.528]
    5_transfers_to_fresh_copy              0/3  FULL [2.03, 2.03, 2.03] vs ACC remainder [2.03, 2.03, 2.03]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [2.03, 2.03, 2.03]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [2.03, 2.03, 2.03] STORAGE_MATCHED [2.03, 2.03, 2.03] vs ACC remainder [2.03, 2.03, 2.03]
  top2_0cea8d651f28c18e
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [5, 7, 8] vs FRESH [5, 7, 8]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [60.9, 60.9, 60.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [2.03, 2.03, 2.03] vs CODE_ONLY [2.03, 2.03, 2.03]
    4_scramble_or_reset_damages            0/3  eff ACC [1.663, 1.871, 2.528] SCR [1.663, 1.871, 2.528] RESET [1.663, 1.871, 2.528]
    5_transfers_to_fresh_copy              0/3  FULL [2.03, 2.03, 2.03] vs ACC remainder [2.03, 2.03, 2.03]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [2.03, 2.03, 2.03]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [2.03, 2.03, 2.03] STORAGE_MATCHED [2.03, 2.03, 2.03] vs ACC remainder [2.03, 2.03, 2.03]
  top3_0d9e0ba3757f42c6
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [5, 7, 8] vs FRESH [5, 7, 8]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [60.9, 60.9, 60.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [2.03, 2.03, 2.03] vs CODE_ONLY [2.03, 2.03, 2.03]
    4_scramble_or_reset_damages            0/3  eff ACC [1.663, 1.871, 2.528] SCR [1.663, 1.871, 2.528] RESET [1.663, 1.871, 2.528]
    5_transfers_to_fresh_copy              0/3  FULL [2.03, 2.03, 2.03] vs ACC remainder [2.03, 2.03, 2.03]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [2.03, 2.03, 2.03]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [2.03, 2.03, 2.03] STORAGE_MATCHED [2.03, 2.03, 2.03] vs ACC remainder [2.03, 2.03, 2.03]
  ancestor9_it10_85b83fe006f49a4b
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [1, 6, 5] vs FRESH [1, 6, 5]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [31.2, 31.2, 31.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1.04, 1.04, 1.04] vs CODE_ONLY [1.04, 1.04, 1.04]
    4_scramble_or_reset_damages            0/3  eff ACC [1.321, 1.982, 2.752] SCR [1.321, 1.982, 2.752] RESET [1.321, 1.982, 2.752]
    5_transfers_to_fresh_copy              0/3  FULL [1.04, 1.04, 1.04] vs ACC remainder [1.04, 1.04, 1.04]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1.04, 1.04, 1.04]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1.04, 1.04, 1.04] STORAGE_MATCHED [1.04, 1.04, 1.04] vs ACC remainder [1.04, 1.04, 1.04]
  ancestor17_it139_db24a44ff952be23
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [5, 7, 8] vs FRESH [5, 7, 8]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [61.5, 61.5, 61.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [2.05, 2.05, 2.05] vs CODE_ONLY [2.05, 2.05, 2.05]
    4_scramble_or_reset_damages            0/3  eff ACC [1.661, 1.869, 2.524] SCR [1.661, 1.869, 2.524] RESET [1.661, 1.869, 2.524]
    5_transfers_to_fresh_copy              0/3  FULL [2.05, 2.05, 2.05] vs ACC remainder [2.05, 2.05, 2.05]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [2.05, 2.05, 2.05]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [2.05, 2.05, 2.05] STORAGE_MATCHED [2.05, 2.05, 2.05] vs ACC remainder [2.05, 2.05, 2.05]
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
  ancestor1_it0_917933876bd532c2
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [4, 4, 3] vs FRESH [4, 4, 3]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [33.9, 33.9, 33.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1.13, 1.13, 1.13] vs CODE_ONLY [1.13, 1.13, 1.13]
    4_scramble_or_reset_damages            0/3  eff ACC [1.413, 1.74, 1.305] SCR [1.413, 1.74, 1.305] RESET [1.416, 1.743, 1.307]
    5_transfers_to_fresh_copy              0/3  FULL [1.13, 1.13, 1.13] vs ACC remainder [1.13, 1.13, 1.13]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1.13, 1.13, 1.13]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1.13, 1.13, 1.13] STORAGE_MATCHED [1.13, 1.13, 1.13] vs ACC remainder [1.13, 1.13, 1.13]
  contemp_e0ab64e2260a436e
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [1, 6, 5] vs FRESH [1, 6, 5]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [91.2, 91.2, 91.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [3.04, 3.04, 3.04] vs CODE_ONLY [3.04, 3.04, 3.04]
    4_scramble_or_reset_damages            0/3  eff ACC [0.801, 1.212, 1.593] SCR [0.801, 1.212, 1.593] RESET [0.801, 1.212, 1.593]
    5_transfers_to_fresh_copy              0/3  FULL [3.04, 3.04, 3.04] vs ACC remainder [3.04, 3.04, 3.04]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [3.04, 3.04, 3.04]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [3.04, 3.04, 3.04] STORAGE_MATCHED [3.04, 3.04, 3.04] vs ACC remainder [3.04, 3.04, 3.04]
  contemp_878b9dcd0db2b2a7
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 2, 4] vs FRESH [6, 2, 4]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [60.9, 60.9, 60.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [2.03, 2.03, 2.03] vs CODE_ONLY [2.03, 2.03, 2.03]
    4_scramble_or_reset_damages            0/3  eff ACC [1.134, 0.792, 0.892] SCR [1.134, 0.792, 0.892] RESET [1.134, 0.792, 0.892]
    5_transfers_to_fresh_copy              0/3  FULL [2.03, 2.03, 2.03] vs ACC remainder [2.03, 2.03, 2.03]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [2.03, 2.03, 2.03]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [2.03, 2.03, 2.03] STORAGE_MATCHED [2.03, 2.03, 2.03] vs ACC remainder [2.03, 2.03, 2.03]
  contemp_90436432c94b0030
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [7, 13, 10] vs FRESH [7, 13, 10]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [14696.9, 13088.4, 13894.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [741.19, 651.83, 696.59] vs CODE_ONLY [741.19, 651.83, 696.59]
    4_scramble_or_reset_damages            0/3  eff ACC [0.211, 0.262, 0.266] SCR [0.211, 0.262, 0.266] RESET [0.211, 0.262, 0.266]
    5_transfers_to_fresh_copy              0/3  FULL [741.19, 651.83, 696.59] vs ACC remainder [741.19, 651.83, 696.59]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [741.19, 651.83, 696.59]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [741.19, 651.83, 696.59] STORAGE_MATCHED [741.19, 651.83, 696.59] vs ACC remainder [741.19, 651.83, 696.59]
  RANDOM
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [3, 2, 5] vs FRESH [3, 2, 5]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [14665.2, 14665.2, 14665.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [733.93, 733.93, 733.93] vs CODE_ONLY [733.93, 733.93, 733.93]
    4_scramble_or_reset_damages            0/3  eff ACC [0.174, 0.191, 0.25] SCR [0.174, 0.191, 0.25] RESET [0.174, 0.191, 0.25]
    5_transfers_to_fresh_copy              0/3  FULL [733.93, 733.93, 733.93] vs ACC remainder [733.93, 733.93, 733.93]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [733.93, 733.93, 733.93]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [733.93, 733.93, 733.93] STORAGE_MATCHED [733.93, 733.93, 733.93] vs ACC remainder [733.93, 733.93, 733.93]

MACHINERY OF top1_03ae23db3a570ae4 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   0     0
    task  9:     0    0    0    0    0 |   0     0
    task 19:     0    0    0    0    0 |   0     0
    task 31:     0    0    0    0    0 |   0     0
    task 41:     0    0    0    0    0 |   0     0
    task 49:     0    0    0    0    0 |   0     0
  artifact events: 0 (create 0, delete 0, patch/append 0); invocations by block: {}; edges: 0
  adaptation curve ACC:   2 1 2 2 2 2 2 2 2 1 1 2 2 2 2 2 2 1 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2
  adaptation curve FRESH: 2 1 2 2 2 2 2 2 2 1 1 2 2 2 2 2 2 1 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2
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

