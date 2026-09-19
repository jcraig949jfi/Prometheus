CRIUS CAMPAIGN 0 REPORT  run=search_c0_seeded_s3  arm=seeded
code_commit=f4dae7a66 dirty=False config_hash=65fd4678cbcdd9c5 world=57065ca240cee53d partitions=ece4bd004beb4710
==============================================================================
SEARCH PROGRESS (fitness = C0_EFFICIENCY, mean over search seeds; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1   1.8951    1.2654         0.4978        37          1
    26   2.5157    2.5157         1.3568        32         23
    51   2.5189    2.5183         1.5224        32         45
    76   2.5231    2.5225         1.4730        23         68
   101   2.5231    2.5231         1.4799        17         87
   126   2.5231    2.5231         1.6338        15        103
   151   2.5231    2.5231         1.4307        14        121
   176   2.5238    2.5235         1.3143        14        147
   201   2.5238    2.5238         1.1499        14        172
   226   2.5312    2.5309         1.1850        18        191
   251   2.5312    2.5312         1.3913        17        207
   276   2.5312    2.5312         1.2931        17        224
   300   2.5312    2.5312         1.1095        16        242
  candidates evaluated: 7208   best_ever 2.5312 (b9f83c3dfe5a8bae)  wall 242s

BEST PROGRAM b9f83c3dfe5a8bae (len 19, iteration 219, modification duplicate@5+5->8)
  search seed 101: eff 2.8524 succ 21/50 inter 300 steps 1385 ws_cost 0 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [3.569, 1.0], "B": [2.736, 1.0], "C": [8.36, 0.083], "D": [8.36, 0.0], "E": [8.36, 0.0]}
  search seed 102: eff 2.2101 succ 21/50 inter 313 steps 1448 ws_cost 0 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [3.469, 1.0], "B": [4.199, 1.0], "C": [8.36, 0.083], "D": [8.36, 0.0], "E": [8.36, 0.0]}
  listing:
      0  INPUT          R1, num_ops
      1  CONST          R5, 1
      2  MOV            R2, R1
      3  LT             R3, R0, R2
      4  BRZ            R3, 15
      5  ACT            R0
      6  ACT            R1
      7  ADD            R0, R0, R5
      8  ACT            R0
      9  ACT            R1
     10  ADD            R0, R0, R5
     11  JMP            3
     12  WS_LINKS       R6, R1
     13  JMP            3
     14  WS_LINKS       R6, R1
     15  CONST          R0, 14
     16  MOD            R3, R0, R2
     17  ACT            R3
     18  ACT            R6
  ancestry (59 steps, newest first): iteration/fitness/modification
    it  219  2.5312  len 19  duplicate@5+5->8
    it  176  2.5238  len 14  arg@11.2
    it  173  2.5238  len 14  replace@9
    it  165  2.5238  len 14  arg@9.1
    it  152  2.5238  len 14  delete@13
    it  148  2.5231  len 15  arg@9.0
    it  123  2.5231  len 15  delete@10
    it  120  2.5231  len 16  arg@15.0
    it  117  2.5231  len 16  delete@11
    it  103  2.5231  len 17  delete@10
    it   96  2.5231  len 18  delete@11
    it   94  2.5231  len 19  delete@13
    it   93  2.5231  len 20  delete@9+insert@11
    it   90  2.5231  len 20  delete@12
    it   85  2.5231  len 21  delete@15
    ... 45 more

QUALIFICATION suite=heldout_v1 seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED)
  player                        effA    effF    effR    effS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  CACHE_REUSE                  2.965   1.575   2.878   1.620  50.0  49.0     1332     6917    5315.7    0.0    0.0
  top1_4a2ff6f68b3b713e        2.949   2.949   2.949   2.949  21.7  21.7      309      309       0.0    0.0    0.0
  top2_6614bbf9c59455dd        2.949   2.949   2.949   2.949  21.7  21.7      309      309       0.0    0.0    0.0
  top3_6b1b07e0c0969179        2.949   2.949   2.949   2.949  21.7  21.7      309      309       0.0    0.0    0.0
  ancestor59_it176_2c4a2b5f5   2.940   2.940   2.940   2.940  21.7  21.7      309      309       0.0    0.0    0.0
  ancestor30_it52_abd2ea2486   2.936   2.936   2.936   2.936  21.7  21.7      309      309       0.0    0.0    0.0
  HEURISTIC                    2.245   2.245   2.245   2.245  42.0  42.0     1874     1874       0.0    0.0    0.0
  ADAPTIVE                     1.972   1.561   2.644   1.417  50.0  49.0     1332     6917    4436.4   27.7    8.7
  ENUMERATE                    1.635   1.635   1.635   1.635  49.0  49.0     6917     6917       0.0    0.0    0.0
  ancestor1_it0_0875253d162c   1.601   1.601   1.601   1.601  48.0  48.0     5611     5611       0.0    0.0    0.0
  ENUMERATE_VM                 1.601   1.601   1.601   1.601  48.0  48.0     5611     5611       0.0    0.0    0.0
  contemp_6d14843e1da590b8     1.391   1.391   1.391   1.391  22.0  22.0      724      724       0.0    0.0    0.0
  contemp_6d6924bb948bb899     0.499   0.499   0.499   0.499   3.3   3.3      518      518       0.0    0.0    0.0
  contemp_337453efa8c8a337     0.390   0.390   0.390   0.390  20.0  20.0    14601    14601       0.0    0.0    0.0
  RANDOM                       0.205   0.205   0.205   0.205   3.3   3.3    14823    14823       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  CACHE_REUSE                   9.89/   4.29    8.07/   4.36    2.65/  33.14    6.18/ 259.04  184.78/ 499.06
  top1_4a2ff6f68b3b713e         3.61/   3.61    3.67/   3.67    8.36/   8.36    8.36/   8.36    8.36/   8.36
  top2_6614bbf9c59455dd         3.61/   3.61    3.67/   3.67    8.36/   8.36    8.36/   8.36    8.36/   8.36
  top3_6b1b07e0c0969179         3.61/   3.61    3.67/   3.67    8.36/   8.36    8.36/   8.36    8.36/   8.36
  ancestor59_it176_2c4a2b5f5    3.65/   3.65    3.72/   3.72    8.45/   8.45    8.45/   8.45    8.45/   8.45
  ancestor30_it52_abd2ea2486    3.65/   3.65    3.72/   3.72    8.50/   8.50    8.50/   8.50    8.50/   8.50
  HEURISTIC                     3.48/   3.48    3.54/   3.54   34.80/  34.80   60.61/  60.61   98.65/  98.65
  ADAPTIVE                     11.56/   4.83    9.37/   4.90    3.24/  33.74   10.51/ 259.64  288.27/ 499.66
  ENUMERATE                     3.48/   3.48    3.54/   3.54   31.87/  31.87  255.22/ 255.22  492.37/ 492.37
  ancestor1_it0_0875253d162c    3.72/   3.72    3.79/   3.79   34.59/  34.59  264.39/ 264.39  342.45/ 342.45
  ENUMERATE_VM                  3.72/   3.72    3.79/   3.79   34.59/  34.59  264.39/ 264.39  342.45/ 342.45
  contemp_6d14843e1da590b8      8.59/   8.59    8.79/   8.79   18.42/  18.42   19.63/  19.63   19.63/  19.63
  contemp_6d6924bb948bb899      9.31/   9.31   10.68/  10.68   11.36/  11.36   10.81/  10.81   11.36/  11.36
  contemp_337453efa8c8a337      4.78/   4.78    4.39/   4.39  135.37/ 135.37  902.71/ 902.71  716.48/ 716.48
  RANDOM                       15.89/  15.89   14.75/  14.75  121.20/ 121.20  808.00/ 808.00  641.35/ 641.35

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                      absent_op5_d2  absent_op5_d3         depth4   heldout_pair heldout_triple new_combinatio      primitive  reversed_pair
  CACHE_REUSE                   12/12    58     6/6    496     6/6      4    18/18     2    15/15     3    15/15     3    60/60     2    18/18     2
  top1_4a2ff6f68b3b713e          0/12     8     0/6      8     0/6      8     0/18     8     0/15     8     0/15     8    60/60     3     5/18     8
  top2_6614bbf9c59455dd          0/12     8     0/6      8     0/6      8     0/18     8     0/15     8     0/15     8    60/60     3     5/18     8
  top3_6b1b07e0c0969179          0/12     8     0/6      8     0/6      8     0/18     8     0/15     8     0/15     8    60/60     3     5/18     8
  ancestor59_it176_2c4a2b5f5     0/12     8     0/6      8     0/6      8     0/18     8     0/15     8     0/15     8    60/60     3     5/18     8
  ancestor30_it52_abd2ea2486     0/12     8     0/6      8     0/6      8     0/18     8     0/15     8     0/15     8    60/60     3     5/18     8
  HEURISTIC                      9/12    40     0/6    180     3/6    133    13/18    56    13/15    45    10/15    76    60/60     3    18/18    13
  ADAPTIVE                      12/12    58     6/6    496     6/6      4    18/18     2    15/15     3    15/15     3    60/60     2    18/18     2
  ENUMERATE                     12/12    58     6/6    496     3/6   1350    18/18    38    15/15   257    15/15   251    60/60     3    18/18    25
  ancestor1_it0_0875253d162c    12/12    52     6/6    480     0/6    726    18/18    40    15/15   257    15/15   248    60/60     3    18/18    25
  ENUMERATE_VM                  12/12    52     6/6    480     0/6    726    18/18    40    15/15   257    15/15   248    60/60     3    18/18    25
  contemp_6d14843e1da590b8       0/12    19     0/6     19     0/6     19     6/18    17     0/15    19     0/15    19    60/60     8     0/18    19
  contemp_6d6924bb948bb899       0/12    11     0/6     11     0/6     11     0/18    11     1/15    10     1/15    10     8/60    10     0/18    11
  contemp_337453efa8c8a337       0/12   120     0/6    800     0/6   1500     0/18   120     0/15   800     0/15   800    60/60     4     0/18   120
  RANDOM                         0/12   120     0/6    800     0/6   1500     0/18   120     0/15   800     0/15   800    10/60    15     0/18   120

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  CACHE_REUSE                   85.56       --    93.37    85.56    93.37    93.37    93.37   0.0
  top1_4a2ff6f68b3b713e          8.36       --     8.36     8.36     8.36     8.36     8.36   0.0
  top2_6614bbf9c59455dd          8.36       --     8.36     8.36     8.36     8.36     8.36   0.0
  top3_6b1b07e0c0969179          8.36       --     8.36     8.36     8.36     8.36     8.36   0.0
  ancestor59_it176_2c4a2b5f5     8.45       --     8.45     8.45     8.45     8.45     8.45   0.0
  ancestor30_it52_abd2ea2486     8.50       --     8.50     8.50     8.50     8.50     8.50   0.0
  HEURISTIC                     77.52       --    77.52    77.52    77.52    77.52    77.52   0.0
  ADAPTIVE                     133.96   106.96   142.50   133.96   114.87   114.87   114.87  10.7
  ENUMERATE                    360.62       --   360.62   360.62   360.62   360.62   360.62   0.0
  ancestor1_it0_0875253d162c   299.08       --   299.08   299.08   299.08   299.08   299.08   0.0
  ENUMERATE_VM                 299.08       --   299.08   299.08   299.08   299.08   299.08   0.0
  contemp_6d14843e1da590b8      19.63       --    19.63    19.63    19.63    19.63    19.63   0.0
  contemp_6d6924bb948bb899      11.06       --    11.06    11.06    11.06    11.06    11.06   0.0
  contemp_337453efa8c8a337     819.94       --   819.94   819.94   819.94   819.94   819.94   0.0
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
  top1_4a2ff6f68b3b713e
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [22, 21, 22] vs FRESH [22, 21, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [250.8, 250.8, 250.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [8.36, 8.36, 8.36] vs CODE_ONLY [8.36, 8.36, 8.36]
    4_scramble_or_reset_damages            0/3  eff ACC [3.005, 2.657, 3.184] SCR [3.005, 2.657, 3.184] RESET [3.005, 2.657, 3.184]
    5_transfers_to_fresh_copy              0/3  FULL [8.36, 8.36, 8.36] vs ACC remainder [8.36, 8.36, 8.36]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [8.36, 8.36, 8.36]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [8.36, 8.36, 8.36] STORAGE_MATCHED [8.36, 8.36, 8.36] vs ACC remainder [8.36, 8.36, 8.36]
  top2_6614bbf9c59455dd
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [22, 21, 22] vs FRESH [22, 21, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [250.8, 250.8, 250.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [8.36, 8.36, 8.36] vs CODE_ONLY [8.36, 8.36, 8.36]
    4_scramble_or_reset_damages            0/3  eff ACC [3.005, 2.657, 3.184] SCR [3.005, 2.657, 3.184] RESET [3.005, 2.657, 3.184]
    5_transfers_to_fresh_copy              0/3  FULL [8.36, 8.36, 8.36] vs ACC remainder [8.36, 8.36, 8.36]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [8.36, 8.36, 8.36]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [8.36, 8.36, 8.36] STORAGE_MATCHED [8.36, 8.36, 8.36] vs ACC remainder [8.36, 8.36, 8.36]
  top3_6b1b07e0c0969179
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [22, 21, 22] vs FRESH [22, 21, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [250.8, 250.8, 250.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [8.36, 8.36, 8.36] vs CODE_ONLY [8.36, 8.36, 8.36]
    4_scramble_or_reset_damages            0/3  eff ACC [3.005, 2.657, 3.184] SCR [3.005, 2.657, 3.184] RESET [3.005, 2.657, 3.184]
    5_transfers_to_fresh_copy              0/3  FULL [8.36, 8.36, 8.36] vs ACC remainder [8.36, 8.36, 8.36]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [8.36, 8.36, 8.36]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [8.36, 8.36, 8.36] STORAGE_MATCHED [8.36, 8.36, 8.36] vs ACC remainder [8.36, 8.36, 8.36]
  ancestor59_it176_2c4a2b5f54ce4ba0
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [22, 21, 22] vs FRESH [22, 21, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [253.5, 253.5, 253.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [8.45, 8.45, 8.45] vs CODE_ONLY [8.45, 8.45, 8.45]
    4_scramble_or_reset_damages            0/3  eff ACC [2.996, 2.649, 3.174] SCR [2.996, 2.649, 3.174] RESET [2.996, 2.649, 3.174]
    5_transfers_to_fresh_copy              0/3  FULL [8.45, 8.45, 8.45] vs ACC remainder [8.45, 8.45, 8.45]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [8.45, 8.45, 8.45]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [8.45, 8.45, 8.45] STORAGE_MATCHED [8.45, 8.45, 8.45] vs ACC remainder [8.45, 8.45, 8.45]
  ancestor30_it52_abd2ea2486d95039
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [22, 21, 22] vs FRESH [22, 21, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [255.0, 255.0, 255.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [8.5, 8.5, 8.5] vs CODE_ONLY [8.5, 8.5, 8.5]
    4_scramble_or_reset_damages            0/3  eff ACC [2.992, 2.646, 3.171] SCR [2.992, 2.646, 3.171] RESET [2.992, 2.646, 3.171]
    5_transfers_to_fresh_copy              0/3  FULL [8.5, 8.5, 8.5] vs ACC remainder [8.5, 8.5, 8.5]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [8.5, 8.5, 8.5]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [8.5, 8.5, 8.5] STORAGE_MATCHED [8.5, 8.5, 8.5] vs ACC remainder [8.5, 8.5, 8.5]
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
  ancestor1_it0_0875253d162cdf0f
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [48, 48, 48] vs FRESH [48, 48, 48]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [4920.9, 6275.5, 6199.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [248.65, 325.66, 322.94] vs CODE_ONLY [248.65, 325.66, 322.94]
    4_scramble_or_reset_damages            0/3  eff ACC [1.733, 1.515, 1.555] SCR [1.733, 1.515, 1.555] RESET [1.733, 1.515, 1.555]
    5_transfers_to_fresh_copy              0/3  FULL [248.65, 325.66, 322.94] vs ACC remainder [248.65, 325.66, 322.94]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [248.65, 325.66, 322.94]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [248.65, 325.66, 322.94] STORAGE_MATCHED [248.65, 325.66, 322.94] vs ACC remainder [248.65, 325.66, 322.94]
  ENUMERATE_VM
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [48, 48, 48] vs FRESH [48, 48, 48]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [4920.9, 6275.5, 6199.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [248.65, 325.66, 322.94] vs CODE_ONLY [248.65, 325.66, 322.94]
    4_scramble_or_reset_damages            0/3  eff ACC [1.733, 1.515, 1.555] SCR [1.733, 1.515, 1.555] RESET [1.733, 1.515, 1.555]
    5_transfers_to_fresh_copy              0/3  FULL [248.65, 325.66, 322.94] vs ACC remainder [248.65, 325.66, 322.94]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [248.65, 325.66, 322.94]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [248.65, 325.66, 322.94] STORAGE_MATCHED [248.65, 325.66, 322.94] vs ACC remainder [248.65, 325.66, 322.94]
  contemp_6d14843e1da590b8
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [22, 22, 22] vs FRESH [22, 22, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [574.4, 574.4, 574.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [19.63, 19.63, 19.63] vs CODE_ONLY [19.63, 19.63, 19.63]
    4_scramble_or_reset_damages            0/3  eff ACC [1.465, 1.224, 1.486] SCR [1.465, 1.224, 1.486] RESET [1.465, 1.224, 1.486]
    5_transfers_to_fresh_copy              0/3  FULL [19.63, 19.63, 19.63] vs ACC remainder [19.63, 19.63, 19.63]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [19.63, 19.63, 19.63]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [19.63, 19.63, 19.63] STORAGE_MATCHED [19.63, 19.63, 19.63] vs ACC remainder [19.63, 19.63, 19.63]
  contemp_6d6924bb948bb899
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [5, 2, 3] vs FRESH [5, 2, 3]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [332.6, 332.6, 340.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [10.9, 10.9, 11.36] vs CODE_ONLY [10.9, 10.9, 11.36]
    4_scramble_or_reset_damages            0/3  eff ACC [0.57, 0.382, 0.546] SCR [0.57, 0.382, 0.546] RESET [0.57, 0.382, 0.546]
    5_transfers_to_fresh_copy              0/3  FULL [10.9, 10.9, 11.36] vs ACC remainder [10.9, 10.9, 11.36]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [10.9, 10.9, 11.36]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [10.9, 10.9, 11.36] STORAGE_MATCHED [10.9, 10.9, 11.36] vs ACC remainder [10.9, 10.9, 11.36]
  contemp_337453efa8c8a337
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 20, 20] vs FRESH [20, 20, 20]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [16383.4, 16383.4, 16383.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [819.94, 819.94, 819.94] vs CODE_ONLY [819.94, 819.94, 819.94]
    4_scramble_or_reset_damages            0/3  eff ACC [0.382, 0.369, 0.418] SCR [0.382, 0.369, 0.418] RESET [0.382, 0.369, 0.418]
    5_transfers_to_fresh_copy              0/3  FULL [819.94, 819.94, 819.94] vs ACC remainder [819.94, 819.94, 819.94]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [819.94, 819.94, 819.94]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [819.94, 819.94, 819.94] STORAGE_MATCHED [819.94, 819.94, 819.94] vs ACC remainder [819.94, 819.94, 819.94]
  RANDOM
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [3, 2, 5] vs FRESH [3, 2, 5]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [14665.2, 14665.2, 14665.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [733.93, 733.93, 733.93] vs CODE_ONLY [733.93, 733.93, 733.93]
    4_scramble_or_reset_damages            0/3  eff ACC [0.174, 0.191, 0.25] SCR [0.174, 0.191, 0.25] RESET [0.174, 0.191, 0.25]
    5_transfers_to_fresh_copy              0/3  FULL [733.93, 733.93, 733.93] vs ACC remainder [733.93, 733.93, 733.93]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [733.93, 733.93, 733.93]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [733.93, 733.93, 733.93] STORAGE_MATCHED [733.93, 733.93, 733.93] vs ACC remainder [733.93, 733.93, 733.93]

MACHINERY OF top1_4a2ff6f68b3b713e (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   0     0
    task  9:     0    0    0    0    0 |   0     0
    task 19:     0    0    0    0    0 |   0     0
    task 31:     0    0    0    0    0 |   0     0
    task 41:     0    0    0    0    0 |   0     0
    task 49:     0    0    0    0    0 |   0     0
  artifact events: 0 (create 0, delete 0, patch/append 0); invocations by block: {}; edges: 0
  adaptation curve ACC:   3 1 2 3 3 4 5 5 6 1 1 3 2 2 6 2 6 1 2 6 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8
  adaptation curve FRESH: 3 1 2 3 3 4 5 5 6 1 1 3 2 2 6 2 6 1 2 6 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8
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

