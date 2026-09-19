CRIUS CAMPAIGN 0 REPORT  run=search_c0_random_s1  arm=random
code_commit=f4dae7a66 dirty=True config_hash=65fd4678cbcdd9c5 world=57065ca240cee53d partitions=ece4bd004beb4710
==============================================================================
SEARCH PROGRESS (fitness = C0_EFFICIENCY, mean over search seeds; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1   1.5349    1.2466         0.3492        18          2
    26   1.5697    1.5697         1.4067         6          4
    51   2.2582    2.2568         1.5839         4          6
    76   2.2598    2.2590         1.4499         3         10
   101   2.4799    2.4373         1.9309        10         16
   126   2.4970    2.4936         1.9696         7         24
   151   2.5379    2.5363         2.1272         9         28
   176   2.5389    2.5388         1.9538        10         32
   201   2.5399    2.5391         2.0364         9         36
   226   2.5399    2.5395         2.1067         9         40
   251   2.5399    2.5399         1.9388         9         43
   276   2.5399    2.5399         1.9085         9         46
   300   2.5399    2.5399         2.0417         9         49
  candidates evaluated: 7208   best_ever 2.5399 (0ac390dec5dc669e)  wall 49s

BEST PROGRAM 0ac390dec5dc669e (len 9, iteration 188, modification delete@6)
  search seed 101: eff 2.7788 succ 17/50 inter 212 steps 388 ws_cost 0 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [3.363, 0.9], "B": [2.955, 0.8], "C": [5.09, 0.0], "D": [5.09, 0.0], "E": [5.09, 0.0]}
  search seed 102: eff 2.3009 succ 17/50 inter 210 steps 385 ws_cost 0 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [3.362, 0.7], "B": [2.753, 1.0], "C": [5.09, 0.0], "D": [5.09, 0.0], "E": [5.09, 0.0]}
  listing:
      0  ACT            R1
      1  ACTI           6
      2  ACTI           18
      3  ACTI           6
      4  ACTI           10
      5  ACTI           6
      6  ACTI           8
      7  ACTI           -15
      8  ACTI           19
  ancestry (45 steps, newest first): iteration/fitness/modification
    it  188  2.5399  len  9  delete@6
    it  164  2.5389  len 10  arg@8.0
    it  157  2.5389  len 10  delete@10
    it  155  2.5372  len 11  replace@6+replace@10+swap@7,4
    it  144  2.5360  len 11  delete@6+arg@10.1
    it  138  2.5342  len 12  replace@6
    it  129  2.5323  len 12  duplicate@1+4->1+const@4+replace@6
    it  128  2.4960  len  8  insert@7+arg@7.1
    it  126  2.4970  len  7  arg@0.0
    it  117  2.4970  len  7  swap@5,2+delete@4+arg@0.0
    it  106  2.4855  len  8  delete@2
    it  104  2.4843  len  9  arg@5.0+delete@7
    it   97  2.4799  len 10  duplicate@1+3->4+insert@7+arg@6.0
    it   95  2.3920  len  6  delete@1
    it   88  2.3907  len  7  arg@2.0+replace@2+duplicate@4+1->1
    ... 31 more

QUALIFICATION suite=heldout_v1 seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED)
  player                        effA    effF    effR    effS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  CACHE_REUSE                  2.965   1.575   2.878   1.620  50.0  49.0     1332     6917    5315.7    0.0    0.0
  top1_0ac390dec5dc669e        2.839   2.839   2.839   2.839  16.3  16.3      220      220       0.0    0.0    0.0
  top2_16aeb380a6943a47        2.839   2.839   2.839   2.839  16.3  16.3      220      220       0.0    0.0    0.0
  top3_1d5a642ce7b2395a        2.839   2.839   2.839   2.839  16.3  16.3      220      220       0.0    0.0    0.0
  ancestor45_it164_752c9b0b2   2.837   2.837   2.837   2.837  16.3  16.3      220      220       0.0    0.0    0.0
  contemp_8916b34baf936f01     2.769   2.769   2.769   2.769  11.0  11.0      180      180       0.0    0.0    0.0
  contemp_ac108a65d998e655     2.591   2.591   2.591   2.591  13.3  13.3      182      182       0.0    0.0    0.0
  contemp_10237d3de53658b7     2.352   2.352   2.352   2.352  13.0  13.0      257      257       0.0    0.0    0.0
  HEURISTIC                    2.245   2.245   2.245   2.245  42.0  42.0     1874     1874       0.0    0.0    0.0
  ADAPTIVE                     1.972   1.561   2.644   1.417  50.0  49.0     1332     6917    4436.4   27.7    8.7
  ENUMERATE                    1.635   1.635   1.635   1.635  49.0  49.0     6917     6917       0.0    0.0    0.0
  ancestor23_it41_eee015f78a   1.610   1.610   1.610   1.610   6.7   6.7      145      145       0.0    0.0    0.0
  ENUMERATE_VM                 1.601   1.601   1.601   1.601  48.0  48.0     5611     5611       0.0    0.0    0.0
  ancestor1_it0_071a88bd5e8e   1.043   1.043   1.043   1.043   2.7   2.7       50       50       0.0    0.0    0.0
  RANDOM                       0.205   0.205   0.205   0.205   3.3   3.3    14823    14823       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  CACHE_REUSE                   9.89/   4.29    8.07/   4.36    2.65/  33.14    6.18/ 259.04  184.78/ 499.06
  top1_0ac390dec5dc669e         3.43/   3.43    3.74/   3.74    5.09/   5.09    5.09/   5.09    5.09/   5.09
  top2_16aeb380a6943a47         3.43/   3.43    3.74/   3.74    5.09/   5.09    5.09/   5.09    5.09/   5.09
  top3_1d5a642ce7b2395a         3.43/   3.43    3.74/   3.74    5.09/   5.09    5.09/   5.09    5.09/   5.09
  ancestor45_it164_752c9b0b2    3.44/   3.44    3.74/   3.74    5.10/   5.10    5.10/   5.10    5.10/   5.10
  contemp_8916b34baf936f01      3.03/   3.03    3.10/   3.10    4.08/   4.08    4.08/   4.08    4.08/   4.08
  contemp_ac108a65d998e655      3.13/   3.13    3.23/   3.23    4.12/   4.12    4.12/   4.12    4.12/   4.12
  contemp_10237d3de53658b7      3.83/   3.83    4.04/   4.04    6.09/   6.09    6.09/   6.09    6.09/   6.09
  HEURISTIC                     3.48/   3.48    3.54/   3.54   34.80/  34.80   60.61/  60.61   98.65/  98.65
  ADAPTIVE                     11.56/   4.83    9.37/   4.90    3.24/  33.74   10.51/ 259.64  288.27/ 499.66
  ENUMERATE                     3.48/   3.48    3.54/   3.54   31.87/  31.87  255.22/ 255.22  492.37/ 492.37
  ancestor23_it41_eee015f78a    2.67/   2.67    2.94/   2.94    3.08/   3.08    3.08/   3.08    3.08/   3.08
  ENUMERATE_VM                  3.72/   3.72    3.79/   3.79   34.59/  34.59  264.39/ 264.39  342.45/ 342.45
  ancestor1_it0_071a88bd5e8e    1.22/   1.22    1.22/   1.22    1.22/   1.22    1.22/   1.22    1.22/   1.22
  RANDOM                       15.89/  15.89   14.75/  14.75  121.20/ 121.20  808.00/ 808.00  641.35/ 641.35

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                      absent_op5_d2  absent_op5_d3         depth4   heldout_pair heldout_triple new_combinatio      primitive  reversed_pair
  CACHE_REUSE                   12/12    58     6/6    496     6/6      4    18/18     2    15/15     3    15/15     3    60/60     2    18/18     2
  top1_0ac390dec5dc669e          0/12     5     0/6      5     0/6      5     0/18     5     0/15     5     0/15     5    49/60     4     0/18     5
  top2_16aeb380a6943a47          0/12     5     0/6      5     0/6      5     0/18     5     0/15     5     0/15     5    49/60     4     0/18     5
  top3_1d5a642ce7b2395a          0/12     5     0/6      5     0/6      5     0/18     5     0/15     5     0/15     5    49/60     4     0/18     5
  ancestor45_it164_752c9b0b2     0/12     5     0/6      5     0/6      5     0/18     5     0/15     5     0/15     5    49/60     4     0/18     5
  contemp_8916b34baf936f01       1/12     4     0/6      4     0/6      4     0/18     4     0/15     4     0/15     4    32/60     3     0/18     4
  contemp_ac108a65d998e655       0/12     4     0/6      4     0/6      4     0/18     4     0/15     4     0/15     4    40/60     3     0/18     4
  contemp_10237d3de53658b7       0/12     6     0/6      6     0/6      6     0/18     6     0/15     6     0/15     6    39/60     4     0/18     6
  HEURISTIC                      9/12    40     0/6    180     3/6    133    13/18    56    13/15    45    10/15    76    60/60     3    18/18    13
  ADAPTIVE                      12/12    58     6/6    496     6/6      4    18/18     2    15/15     3    15/15     3    60/60     2    18/18     2
  ENUMERATE                     12/12    58     6/6    496     3/6   1350    18/18    38    15/15   257    15/15   251    60/60     3    18/18    25
  ancestor23_it41_eee015f78a     0/12     3     0/6      3     0/6      3     0/18     3     0/15     3     0/15     3    20/60     3     0/18     3
  ENUMERATE_VM                  12/12    52     6/6    480     0/6    726    18/18    40    15/15   257    15/15   248    60/60     3    18/18    25
  ancestor1_it0_071a88bd5e8e     0/12     1     0/6      1     0/6      1     0/18     1     0/15     1     0/15     1     8/60     1     0/18     1
  RANDOM                         0/12   120     0/6    800     0/6   1500     0/18   120     0/15   800     0/15   800    10/60    15     0/18   120

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  CACHE_REUSE                   85.56       --    93.37    85.56    93.37    93.37    93.37   0.0
  top1_0ac390dec5dc669e          5.09       --     5.09     5.09     5.09     5.09     5.09   0.0
  top2_16aeb380a6943a47          5.09       --     5.09     5.09     5.09     5.09     5.09   0.0
  top3_1d5a642ce7b2395a          5.09       --     5.09     5.09     5.09     5.09     5.09   0.0
  ancestor45_it164_752c9b0b2     5.10       --     5.10     5.10     5.10     5.10     5.10   0.0
  contemp_8916b34baf936f01       4.08       --     4.08     4.08     4.08     4.08     4.08   0.0
  contemp_ac108a65d998e655       4.12       --     4.12     4.12     4.12     4.12     4.12   0.0
  contemp_10237d3de53658b7       6.09       --     6.09     6.09     6.09     6.09     6.09   0.0
  HEURISTIC                     77.52       --    77.52    77.52    77.52    77.52    77.52   0.0
  ADAPTIVE                     133.96   106.96   142.50   133.96   114.87   114.87   114.87  10.7
  ENUMERATE                    360.62       --   360.62   360.62   360.62   360.62   360.62   0.0
  ancestor23_it41_eee015f78a     3.08       --     3.08     3.08     3.08     3.08     3.08   0.0
  ENUMERATE_VM                 299.08       --   299.08   299.08   299.08   299.08   299.08   0.0
  ancestor1_it0_071a88bd5e8e     1.22       --     1.22     1.22     1.22     1.22     1.22   0.0
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
  top1_0ac390dec5dc669e
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [16, 16, 17] vs FRESH [16, 16, 17]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [152.7, 152.7, 152.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [5.09, 5.09, 5.09] vs CODE_ONLY [5.09, 5.09, 5.09]
    4_scramble_or_reset_damages            0/3  eff ACC [2.713, 2.557, 3.246] SCR [2.713, 2.557, 3.246] RESET [2.713, 2.557, 3.246]
    5_transfers_to_fresh_copy              0/3  FULL [5.09, 5.09, 5.09] vs ACC remainder [5.09, 5.09, 5.09]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [5.09, 5.09, 5.09]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [5.09, 5.09, 5.09] STORAGE_MATCHED [5.09, 5.09, 5.09] vs ACC remainder [5.09, 5.09, 5.09]
  top2_16aeb380a6943a47
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [16, 16, 17] vs FRESH [16, 16, 17]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [152.7, 152.7, 152.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [5.09, 5.09, 5.09] vs CODE_ONLY [5.09, 5.09, 5.09]
    4_scramble_or_reset_damages            0/3  eff ACC [2.713, 2.557, 3.246] SCR [2.713, 2.557, 3.246] RESET [2.713, 2.557, 3.246]
    5_transfers_to_fresh_copy              0/3  FULL [5.09, 5.09, 5.09] vs ACC remainder [5.09, 5.09, 5.09]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [5.09, 5.09, 5.09]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [5.09, 5.09, 5.09] STORAGE_MATCHED [5.09, 5.09, 5.09] vs ACC remainder [5.09, 5.09, 5.09]
  top3_1d5a642ce7b2395a
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [16, 16, 17] vs FRESH [16, 16, 17]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [152.7, 152.7, 152.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [5.09, 5.09, 5.09] vs CODE_ONLY [5.09, 5.09, 5.09]
    4_scramble_or_reset_damages            0/3  eff ACC [2.713, 2.557, 3.246] SCR [2.713, 2.557, 3.246] RESET [2.713, 2.557, 3.246]
    5_transfers_to_fresh_copy              0/3  FULL [5.09, 5.09, 5.09] vs ACC remainder [5.09, 5.09, 5.09]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [5.09, 5.09, 5.09]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [5.09, 5.09, 5.09] STORAGE_MATCHED [5.09, 5.09, 5.09] vs ACC remainder [5.09, 5.09, 5.09]
  ancestor45_it164_752c9b0b2ab266ed
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [16, 16, 17] vs FRESH [16, 16, 17]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [153.0, 153.0, 153.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [5.1, 5.1, 5.1] vs CODE_ONLY [5.1, 5.1, 5.1]
    4_scramble_or_reset_damages            0/3  eff ACC [2.712, 2.556, 3.244] SCR [2.712, 2.556, 3.244] RESET [2.712, 2.556, 3.244]
    5_transfers_to_fresh_copy              0/3  FULL [5.1, 5.1, 5.1] vs ACC remainder [5.1, 5.1, 5.1]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [5.1, 5.1, 5.1]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [5.1, 5.1, 5.1] STORAGE_MATCHED [5.1, 5.1, 5.1] vs ACC remainder [5.1, 5.1, 5.1]
  contemp_8916b34baf936f01
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [10, 10, 13] vs FRESH [10, 10, 13]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [122.4, 122.4, 122.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [4.08, 4.08, 4.08] vs CODE_ONLY [4.08, 4.08, 4.08]
    4_scramble_or_reset_damages            0/3  eff ACC [2.497, 2.519, 3.292] SCR [2.497, 2.519, 3.292] RESET [2.497, 2.519, 3.292]
    5_transfers_to_fresh_copy              0/3  FULL [4.08, 4.08, 4.08] vs ACC remainder [4.08, 4.08, 4.08]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [4.08, 4.08, 4.08]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [4.08, 4.08, 4.08] STORAGE_MATCHED [4.08, 4.08, 4.08] vs ACC remainder [4.08, 4.08, 4.08]
  contemp_ac108a65d998e655
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [15, 13, 12] vs FRESH [15, 13, 12]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [123.6, 123.6, 123.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [4.12, 4.12, 4.12] vs CODE_ONLY [4.12, 4.12, 4.12]
    4_scramble_or_reset_damages            0/3  eff ACC [2.891, 2.47, 2.412] SCR [2.891, 2.47, 2.412] RESET [2.891, 2.47, 2.412]
    5_transfers_to_fresh_copy              0/3  FULL [4.12, 4.12, 4.12] vs ACC remainder [4.12, 4.12, 4.12]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [4.12, 4.12, 4.12]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [4.12, 4.12, 4.12] STORAGE_MATCHED [4.12, 4.12, 4.12] vs ACC remainder [4.12, 4.12, 4.12]
  contemp_10237d3de53658b7
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [12, 13, 14] vs FRESH [12, 13, 14]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [182.7, 182.7, 182.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [6.09, 6.09, 6.09] vs CODE_ONLY [6.09, 6.09, 6.09]
    4_scramble_or_reset_damages            0/3  eff ACC [2.18, 2.18, 2.695] SCR [2.18, 2.18, 2.695] RESET [2.18, 2.18, 2.695]
    5_transfers_to_fresh_copy              0/3  FULL [6.09, 6.09, 6.09] vs ACC remainder [6.09, 6.09, 6.09]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [6.09, 6.09, 6.09]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [6.09, 6.09, 6.09] STORAGE_MATCHED [6.09, 6.09, 6.09] vs ACC remainder [6.09, 6.09, 6.09]
  HEURISTIC
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [44, 42, 40] vs FRESH [44, 42, 40]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1854.6, 1657.6, 1926.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [83.65, 66.96, 81.94] vs CODE_ONLY [83.65, 66.96, 81.94]
    4_scramble_or_reset_damages            0/3  eff ACC [2.597, 2.205, 1.932] SCR [2.597, 2.205, 1.932] RESET [2.597, 2.205, 1.932]
    5_transfers_to_fresh_copy              0/3  FULL [83.65, 66.96, 81.94] vs ACC remainder [83.65, 66.96, 81.94]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [83.65, 66.96, 81.94]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [83.65, 66.96, 81.94] STORAGE_MATCHED [83.65, 66.96, 81.94] vs ACC remainder [83.65, 66.96, 81.94]
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
  ancestor23_it41_eee015f78a9bd52c
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [5, 7, 8] vs FRESH [5, 7, 8]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [92.4, 92.4, 92.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [3.08, 3.08, 3.08] vs CODE_ONLY [3.08, 3.08, 3.08]
    4_scramble_or_reset_damages            0/3  eff ACC [1.435, 1.492, 1.902] SCR [1.435, 1.492, 1.902] RESET [1.435, 1.492, 1.902]
    5_transfers_to_fresh_copy              0/3  FULL [3.08, 3.08, 3.08] vs ACC remainder [3.08, 3.08, 3.08]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [3.08, 3.08, 3.08]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [3.08, 3.08, 3.08] STORAGE_MATCHED [3.08, 3.08, 3.08] vs ACC remainder [3.08, 3.08, 3.08]
  ENUMERATE_VM
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [48, 48, 48] vs FRESH [48, 48, 48]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [4920.9, 6275.5, 6199.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [248.65, 325.66, 322.94] vs CODE_ONLY [248.65, 325.66, 322.94]
    4_scramble_or_reset_damages            0/3  eff ACC [1.733, 1.515, 1.555] SCR [1.733, 1.515, 1.555] RESET [1.733, 1.515, 1.555]
    5_transfers_to_fresh_copy              0/3  FULL [248.65, 325.66, 322.94] vs ACC remainder [248.65, 325.66, 322.94]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [248.65, 325.66, 322.94]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [248.65, 325.66, 322.94] STORAGE_MATCHED [248.65, 325.66, 322.94] vs ACC remainder [248.65, 325.66, 322.94]
  ancestor1_it0_071a88bd5e8eed21
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [4, 1, 3] vs FRESH [4, 1, 3]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [36.6, 36.6, 36.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1.22, 1.22, 1.22] vs CODE_ONLY [1.22, 1.22, 1.22]
    4_scramble_or_reset_damages            0/3  eff ACC [1.187, 0.863, 1.079] SCR [1.187, 0.863, 1.079] RESET [1.187, 0.863, 1.079]
    5_transfers_to_fresh_copy              0/3  FULL [1.22, 1.22, 1.22] vs ACC remainder [1.22, 1.22, 1.22]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1.22, 1.22, 1.22]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1.22, 1.22, 1.22] STORAGE_MATCHED [1.22, 1.22, 1.22] vs ACC remainder [1.22, 1.22, 1.22]
  RANDOM
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [3, 2, 5] vs FRESH [3, 2, 5]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [14665.2, 14665.2, 14665.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [733.93, 733.93, 733.93] vs CODE_ONLY [733.93, 733.93, 733.93]
    4_scramble_or_reset_damages            0/3  eff ACC [0.174, 0.191, 0.25] SCR [0.174, 0.191, 0.25] RESET [0.174, 0.191, 0.25]
    5_transfers_to_fresh_copy              0/3  FULL [733.93, 733.93, 733.93] vs ACC remainder [733.93, 733.93, 733.93]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [733.93, 733.93, 733.93]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [733.93, 733.93, 733.93] STORAGE_MATCHED [733.93, 733.93, 733.93] vs ACC remainder [733.93, 733.93, 733.93]

MACHINERY OF top1_0ac390dec5dc669e (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   0     0
    task  9:     0    0    0    0    0 |   0     0
    task 19:     0    0    0    0    0 |   0     0
    task 31:     0    0    0    0    0 |   0     0
    task 41:     0    0    0    0    0 |   0     0
    task 49:     0    0    0    0    0 |   0     0
  artifact events: 0 (create 0, delete 0, patch/append 0); invocations by block: {}; edges: 0
  adaptation curve ACC:   5 1 4 5 5 3 2 2 5 1 1 5 4 4 5 4 5 1 4 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5
  adaptation curve FRESH: 5 1 4 5 5 3 2 2 5 1 1 5 4 4 5 4 5 1 4 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5
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

