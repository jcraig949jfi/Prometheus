CRIUS CAMPAIGN 0 REPORT  run=search_c0x_seeded_s3  arm=seeded
code_commit=f4dae7a66 dirty=True config_hash=a204326d0078673d world=57065ca240cee53d partitions=ece4bd004beb4710
==============================================================================
SEARCH PROGRESS (fitness = C0_EFFICIENCY, mean over search seeds; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1   1.6157    1.0546         0.3916        39          2
    26   1.7567    1.7544         0.9410        50         29
    51   1.7639    1.7583         1.0306        47         51
    76   1.7657    1.7656         0.8874        45         69
   101   1.7906    1.7694         0.9351        48         88
   126   1.7913    1.7910         1.0182        47        104
   151   1.7918    1.7917         1.1044        44        121
   176   1.7930    1.7930         1.0131        45        139
   201   1.7935    1.7935         1.0400        44        155
   226   1.7943    1.7936         1.0054        41        170
   251   1.7943    1.7943         1.0834        38        186
   276   1.9558    1.9429         1.0378        45        200
   300   1.9581    1.9581         0.8517        36        212
  candidates evaluated: 7208   best_ever 1.9581 (6665f2a60e1f9c2b)  wall 212s

BEST PROGRAM 6665f2a60e1f9c2b (len 39, iteration 278, modification delete@31)
  search seed 101: eff 2.0834 succ 50/50 inter 2474 steps 8507 ws_cost 0 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [3.906, 1.0], "B": [2.962, 1.0], "C": [34.982, 1.0], "D": [134.585, 1.0], "E": [90.594, 1.0]}
  search seed 102: eff 1.8328 succ 50/50 inter 2466 steps 8466 ws_cost 0 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [3.064, 1.0], "B": [3.908, 1.0], "C": [34.983, 1.0], "D": [107.048, 1.0], "E": [123.834, 1.0]}
  listing:
      0  ACT            R3
      1  INPUT          R1, num_ops
      2  CONST          R5, 1
      3  CONST          R0, 2
      4  MOV            R2, R1
      5  LT             R3, R0, R2
      6  BRZ            R3, 15
      7  ACT            R2
      8  ACT            R0
      9  ADD            R0, R0, R0
     10  ACT            R2
     11  ACT            R0
     12  ADD            R0, R0, R5
     13  JMP            5
     14  BLK_REC_BEGIN  
     15  MOV            R3, R1
     16  ACT            R1
     17  DIV            R4, R3, R1
     18  MOD            R3, R4, R3
     19  CONST          R0, -19
     20  ACT            R3
     21  ADD            R0, R0, R5
     22  JMP            31
     23  BLK_LEN        R1, R5
     24  ACT            R3
     25  ACT            R1
     26  MOD            R3, R0, R1
     27  ACT            R3
     28  DIV            R4, R0, R1
     29  MOD            R3, R4, R1
     30  ACT            R3
     31  ACT            R4
     32  ADD            R0, R0, R5
     33  JMP            25
     34  MOD            R3, R4, R1
     35  ADD            R0, R0, R0
     36  ACT            R2
     37  ACT            R3
     38  EQ             R0, R0, R6
  ancestry (74 steps, newest first): iteration/fitness/modification
    it  278  1.9581  len 39  delete@31
    it  277  1.9513  len 40  delete@38
    it  273  1.9513  len 41  const@19+insert@24+duplicate@9+2->36
    it  267  1.8812  len 38  arg@19.1
    it  259  1.8402  len 38  arg@23.1
    it  258  1.8402  len 38  delete@30
    it  249  1.7943  len 39  arg@32.0
    it  248  1.7943  len 39  swap@38,37+swap@32,37
    it  247  1.7943  len 39  arg@18.2+delete@38
    it  230  1.7943  len 40  delete@40
    it  219  1.7943  len 41  arg@9.2
    it  216  1.7935  len 41  delete@38
    it  214  1.7935  len 42  delete@14
    it  213  1.7935  len 43  insert@37
    it  211  1.7935  len 42  arg@37.1
    ... 60 more

QUALIFICATION suite=heldout_v1 seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED)
  player                        effA    effF    effR    effS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  CACHE_REUSE                  2.965   1.575   2.878   1.620  50.0  49.0     1332     6917    5315.7    0.0    0.0
  ADAPTIVE                     1.972   1.561   2.644   1.417  50.0  49.0     1332     6917    4436.4   27.7    8.7
  ENUMERATE                    1.635   1.635   1.635   1.635  49.0  49.0     6917     6917       0.0    0.0    0.0
  HEURISTIC                    1.591   1.591   1.591   1.591  42.0  42.0     1874     1874       0.0    0.0    0.0
  contemp_90feff219839ef82     1.579   1.579   1.579   1.579  48.0  48.0     5430     5430       0.0    0.0    0.0
  ancestor1_it0_0875253d162c   1.506   1.506   1.506   1.506  48.0  48.0     5611     5611       0.0    0.0    0.0
  ENUMERATE_VM                 1.506   1.506   1.506   1.506  48.0  48.0     5611     5611       0.0    0.0    0.0
  top1_9b118122c3e95da6        1.499   1.499   1.499   1.499  48.0  48.0     5510     5510       0.0    0.0    0.0
  top2_5b75e0d7c5a8d62e        1.499   1.499   1.499   1.499  48.0  48.0     5510     5510       0.0    0.0    0.0
  top3_cc86e67037106642        1.499   1.499   1.499   1.499  48.0  48.0     5510     5510       0.0    0.0    0.0
  ancestor74_it277_8c1f5fcf5   1.491   1.491   1.491   1.491  48.0  48.0     5510     5510       0.0    0.0    0.0
  contemp_32832c79d7c1f279     1.391   1.391   1.391   1.391  48.0  48.0     6240     6240       0.0    0.0    0.0
  ancestor38_it109_80b460460   1.353   1.353   1.353   1.353  48.0  48.0     6547     6547       0.0    0.0    0.0
  contemp_4f5c08e0deab14c1     0.516   0.517   0.517   0.516  22.3  22.3    14115    14115       0.0   32.0    0.0
  RANDOM                       0.205   0.205   0.205   0.205   3.3   3.3    14823    14823       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  CACHE_REUSE                   9.89/   4.29    8.07/   4.36    2.65/  33.14    6.18/ 259.04  184.78/ 499.06
  ADAPTIVE                     11.56/   4.83    9.37/   4.90    3.24/  33.74   10.51/ 259.64  288.27/ 499.66
  ENUMERATE                     3.48/   3.48    3.54/   3.54   31.87/  31.87  255.22/ 255.22  492.37/ 492.37
  HEURISTIC                     3.48/   3.48    3.54/   3.54   34.80/  34.80   60.61/  60.61   98.65/  98.65
  contemp_90feff219839ef82      3.34/   3.34    4.50/   4.50   52.09/  52.09   92.81/  92.81  497.09/ 497.09
  ancestor1_it0_0875253d162c    3.72/   3.72    3.79/   3.79   34.59/  34.59  264.39/ 264.39  342.45/ 342.45
  ENUMERATE_VM                  3.72/   3.72    3.79/   3.79   34.59/  34.59  264.39/ 264.39  342.45/ 342.45
  top1_9b118122c3e95da6         3.34/   3.34    4.50/   4.50   61.74/  61.74   90.76/  90.76  495.56/ 495.56
  top2_5b75e0d7c5a8d62e         3.34/   3.34    4.50/   4.50   61.74/  61.74   90.76/  90.76  495.56/ 495.56
  top3_cc86e67037106642         3.34/   3.34    4.50/   4.50   61.74/  61.74   90.76/  90.76  495.56/ 495.56
  ancestor74_it277_8c1f5fcf5    3.34/   3.34    4.50/   4.50   61.94/  61.94   91.06/  91.06  497.23/ 497.23
  contemp_32832c79d7c1f279      3.34/   3.34    4.50/   4.50   68.27/  68.27  159.66/ 159.66  493.69/ 493.69
  ancestor38_it109_80b460460    3.37/   3.37    4.37/   4.37   66.24/  66.24  186.11/ 186.11  507.98/ 507.98
  contemp_4f5c08e0deab14c1      4.17/   4.17    5.47/   5.47  106.89/ 106.89  824.17/ 824.17  615.65/ 615.65
  RANDOM                       15.89/  15.89   14.75/  14.75  121.20/ 121.20  808.00/ 808.00  641.35/ 641.35

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                      absent_op5_d2  absent_op5_d3         depth4   heldout_pair heldout_triple new_combinatio      primitive  reversed_pair
  CACHE_REUSE                   12/12    58     6/6    496     6/6      4    18/18     2    15/15     3    15/15     3    60/60     2    18/18     2
  ADAPTIVE                      12/12    58     6/6    496     6/6      4    18/18     2    15/15     3    15/15     3    60/60     2    18/18     2
  ENUMERATE                     12/12    58     6/6    496     3/6   1350    18/18    38    15/15   257    15/15   251    60/60     3    18/18    25
  HEURISTIC                      9/12    40     0/6    180     3/6    133    13/18    56    13/15    45    10/15    76    60/60     3    18/18    13
  contemp_90feff219839ef82      12/12    53     6/6    320     0/6   1500    18/18    48    15/15    95    15/15    85    60/60     4    18/18    53
  ancestor1_it0_0875253d162c    12/12    52     6/6    480     0/6    726    18/18    40    15/15   257    15/15   248    60/60     3    18/18    25
  ENUMERATE_VM                  12/12    52     6/6    480     0/6    726    18/18    40    15/15   257    15/15   248    60/60     3    18/18    25
  top1_9b118122c3e95da6         12/12    51     6/6    318     0/6   1500    18/18    68    15/15    93    15/15    83    60/60     4    18/18    51
  top2_5b75e0d7c5a8d62e         12/12    51     6/6    318     0/6   1500    18/18    68    15/15    93    15/15    83    60/60     4    18/18    51
  top3_cc86e67037106642         12/12    51     6/6    318     0/6   1500    18/18    68    15/15    93    15/15    83    60/60     4    18/18    51
  ancestor74_it277_8c1f5fcf5    12/12    51     6/6    318     0/6   1500    18/18    68    15/15    93    15/15    83    60/60     4    18/18    51
  contemp_32832c79d7c1f279      12/12    43     6/6    328     0/6   1500    18/18    60    15/15   131    15/15   178    60/60     4    18/18    72
  ancestor38_it109_80b460460    12/12    53     6/6    352     0/6   1500    18/18    72    15/15   184    15/15   175    60/60     4    18/18    55
  contemp_4f5c08e0deab14c1       1/12   111     1/6    668     0/6   1500     0/18   120     0/15   800     0/15   800    60/60     5     5/18    87
  RANDOM                         0/12   120     0/6    800     0/6   1500     0/18   120     0/15   800     0/15   800    10/60    15     0/18   120

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  CACHE_REUSE                   85.56       --    93.37    85.56    93.37    93.37    93.37   0.0
  ADAPTIVE                     133.96   106.96   142.50   133.96   114.87   114.87   114.87  10.7
  ENUMERATE                    360.62       --   360.62   360.62   360.62   360.62   360.62   0.0
  HEURISTIC                     77.52       --    77.52    77.52    77.52    77.52    77.52   0.0
  contemp_90feff219839ef82     272.49       --   272.49   272.49   272.49   272.49   272.49   0.0
  ancestor1_it0_0875253d162c   299.08       --   299.08   299.08   299.08   299.08   299.08   0.0
  ENUMERATE_VM                 299.08       --   299.08   299.08   299.08   299.08   299.08   0.0
  top1_9b118122c3e95da6        270.67       --   270.67   270.67   270.67   270.67   270.67   0.0
  top2_5b75e0d7c5a8d62e        270.67       --   270.67   270.67   270.67   270.67   270.67   0.0
  top3_cc86e67037106642        270.67       --   270.67   270.67   270.67   270.67   270.67   0.0
  ancestor74_it277_8c1f5fcf5   271.58       --   271.58   271.58   271.58   271.58   271.58   0.0
  contemp_32832c79d7c1f279     308.12       --   308.12   308.12   308.12   308.12   308.12   0.0
  ancestor38_it109_80b460460   329.16       --   329.16   329.16   329.16   329.16   329.16   0.0
  contemp_4f5c08e0deab14c1     731.50   731.50   731.50   731.50   731.50   731.50   731.50  14.3
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
  contemp_90feff219839ef82
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [48, 48, 48] vs FRESH [48, 48, 48]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [5484.6, 5722.9, 5382.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [276.4, 281.38, 259.7] vs CODE_ONLY [276.4, 281.38, 259.7]
    4_scramble_or_reset_damages            0/3  eff ACC [1.712, 1.441, 1.583] SCR [1.712, 1.441, 1.583] RESET [1.712, 1.441, 1.583]
    5_transfers_to_fresh_copy              0/3  FULL [276.4, 281.38, 259.7] vs ACC remainder [276.4, 281.38, 259.7]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [276.4, 281.38, 259.7]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [276.4, 281.38, 259.7] STORAGE_MATCHED [276.4, 281.38, 259.7] vs ACC remainder [276.4, 281.38, 259.7]
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
  top1_9b118122c3e95da6
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [48, 48, 48] vs FRESH [48, 48, 48]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [5637.8, 5770.8, 5430.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [274.58, 279.56, 257.88] vs CODE_ONLY [274.58, 279.56, 257.88]
    4_scramble_or_reset_damages            0/3  eff ACC [1.566, 1.397, 1.533] SCR [1.566, 1.397, 1.533] RESET [1.566, 1.397, 1.533]
    5_transfers_to_fresh_copy              0/3  FULL [274.58, 279.56, 257.88] vs ACC remainder [274.58, 279.56, 257.88]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [274.58, 279.56, 257.88]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [274.58, 279.56, 257.88] STORAGE_MATCHED [274.58, 279.56, 257.88] vs ACC remainder [274.58, 279.56, 257.88]
  top2_5b75e0d7c5a8d62e
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [48, 48, 48] vs FRESH [48, 48, 48]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [5637.8, 5770.8, 5430.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [274.58, 279.56, 257.88] vs CODE_ONLY [274.58, 279.56, 257.88]
    4_scramble_or_reset_damages            0/3  eff ACC [1.566, 1.397, 1.533] SCR [1.566, 1.397, 1.533] RESET [1.566, 1.397, 1.533]
    5_transfers_to_fresh_copy              0/3  FULL [274.58, 279.56, 257.88] vs ACC remainder [274.58, 279.56, 257.88]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [274.58, 279.56, 257.88]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [274.58, 279.56, 257.88] STORAGE_MATCHED [274.58, 279.56, 257.88] vs ACC remainder [274.58, 279.56, 257.88]
  top3_cc86e67037106642
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [48, 48, 48] vs FRESH [48, 48, 48]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [5637.8, 5770.8, 5430.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [274.58, 279.56, 257.88] vs CODE_ONLY [274.58, 279.56, 257.88]
    4_scramble_or_reset_damages            0/3  eff ACC [1.566, 1.397, 1.533] SCR [1.566, 1.397, 1.533] RESET [1.566, 1.397, 1.533]
    5_transfers_to_fresh_copy              0/3  FULL [274.58, 279.56, 257.88] vs ACC remainder [274.58, 279.56, 257.88]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [274.58, 279.56, 257.88]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [274.58, 279.56, 257.88] STORAGE_MATCHED [274.58, 279.56, 257.88] vs ACC remainder [274.58, 279.56, 257.88]
  ancestor74_it277_8c1f5fcf57bac9a7
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [48, 48, 48] vs FRESH [48, 48, 48]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [5656.6, 5790.1, 5448.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [275.5, 280.5, 258.75] vs CODE_ONLY [275.5, 280.5, 258.75]
    4_scramble_or_reset_damages            0/3  eff ACC [1.557, 1.39, 1.525] SCR [1.557, 1.39, 1.525] RESET [1.557, 1.39, 1.525]
    5_transfers_to_fresh_copy              0/3  FULL [275.5, 280.5, 258.75] vs ACC remainder [275.5, 280.5, 258.75]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [275.5, 280.5, 258.75]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [275.5, 280.5, 258.75] STORAGE_MATCHED [275.5, 280.5, 258.75] vs ACC remainder [275.5, 280.5, 258.75]
  contemp_32832c79d7c1f279
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [48, 48, 48] vs FRESH [48, 48, 48]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [6870.2, 5716.0, 6509.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [333.71, 272.27, 318.38] vs CODE_ONLY [333.71, 272.27, 318.38]
    4_scramble_or_reset_damages            0/3  eff ACC [1.357, 1.382, 1.434] SCR [1.357, 1.382, 1.434] RESET [1.357, 1.382, 1.434]
    5_transfers_to_fresh_copy              0/3  FULL [333.71, 272.27, 318.38] vs ACC remainder [333.71, 272.27, 318.38]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [333.71, 272.27, 318.38]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [333.71, 272.27, 318.38] STORAGE_MATCHED [333.71, 272.27, 318.38] vs ACC remainder [333.71, 272.27, 318.38]
  ancestor38_it109_80b460460835c62f
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [48, 48, 48] vs FRESH [48, 48, 48]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [6410.6, 7197.4, 6551.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [314.86, 355.81, 316.82] vs CODE_ONLY [314.86, 355.81, 316.82]
    4_scramble_or_reset_damages            0/3  eff ACC [1.418, 1.247, 1.393] SCR [1.418, 1.247, 1.393] RESET [1.418, 1.247, 1.393]
    5_transfers_to_fresh_copy              0/3  FULL [314.86, 355.81, 316.82] vs ACC remainder [314.86, 355.81, 316.82]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [314.86, 355.81, 316.82]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [314.86, 355.81, 316.82] STORAGE_MATCHED [314.86, 355.81, 316.82] vs ACC remainder [314.86, 355.81, 316.82]
  contemp_4f5c08e0deab14c1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [23, 22, 22] vs FRESH [23, 22, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [13905.1, 14726.1, 14717.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [703.5, 742.35, 748.64] vs CODE_ONLY [703.5, 742.35, 748.64]
    4_scramble_or_reset_damages            0/3  eff ACC [0.523, 0.497, 0.529] SCR [0.523, 0.497, 0.529] RESET [0.524, 0.497, 0.529]
    5_transfers_to_fresh_copy              0/3  FULL [703.5, 742.35, 748.64] vs ACC remainder [703.5, 742.35, 748.64]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [703.5, 742.35, 748.64] vs ACC remainder [703.5, 742.35, 748.64]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [703.5, 742.35, 748.64] STORAGE_MATCHED [703.5, 742.35, 748.64] vs ACC remainder [703.5, 742.35, 748.64]
  RANDOM
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [3, 2, 5] vs FRESH [3, 2, 5]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [14665.2, 14665.2, 14665.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [733.93, 733.93, 733.93] vs CODE_ONLY [733.93, 733.93, 733.93]
    4_scramble_or_reset_damages            0/3  eff ACC [0.174, 0.191, 0.25] SCR [0.174, 0.191, 0.25] RESET [0.174, 0.191, 0.25]
    5_transfers_to_fresh_copy              0/3  FULL [733.93, 733.93, 733.93] vs ACC remainder [733.93, 733.93, 733.93]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [733.93, 733.93, 733.93]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [733.93, 733.93, 733.93] STORAGE_MATCHED [733.93, 733.93, 733.93] vs ACC remainder [733.93, 733.93, 733.93]

MACHINERY OF top1_9b118122c3e95da6 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   0     0
    task  9:     0    0    0    0    0 |   0     0
    task 19:     0    0    0    0    0 |   0     0
    task 31:     0    0    0    0    0 |   0     0
    task 41:     0    0    0    0    0 |   0     0
    task 49:     0    0    0    0    0 |   0     0
  artifact events: 0 (create 0, delete 0, patch/append 0); invocations by block: {}; edges: 0
  adaptation curve ACC:   2 1 6 2 2 5 3 3 4 1 1 2 6 6 4 6 4 1 6 4 13 112 99 68 37 25 13 62 62 13 81 112 69 103 10 82 190 119 57 88 88 60 233 574 90 1547 22 22 1547 40
  adaptation curve FRESH: 2 1 6 2 2 5 3 3 4 1 1 2 6 6 4 6 4 1 6 4 13 112 99 68 37 25 13 62 62 13 81 112 69 103 10 82 190 119 57 88 88 60 233 574 90 1547 22 22 1547 40
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

