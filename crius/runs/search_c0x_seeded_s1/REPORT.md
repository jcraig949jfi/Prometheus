CRIUS CAMPAIGN 0 REPORT  run=search_c0x_seeded_s1  arm=seeded
code_commit=f4dae7a66 dirty=True config_hash=a204326d0078673d world=57065ca240cee53d partitions=ece4bd004beb4710
==============================================================================
SEARCH PROGRESS (fitness = C0_EFFICIENCY, mean over search seeds; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1   1.7198    1.4944         0.6356        39          2
    26   1.9213    1.9164         1.0551        46         27
    51   1.9259    1.9253         0.8803        51         45
    76   1.9301    1.9300         0.9072        64         60
   101   1.9341    1.9340         1.1812        61         72
   126   1.9353    1.9351         1.2798        59         88
   151   1.9791    1.9756         1.0578        64        108
   176   1.9828    1.9827         1.0232        58        124
   201   2.0396    2.0396         1.4616        54        142
   226   2.0396    2.0396         0.9728        52        158
   251   2.0407    2.0406         1.0784        50        177
   276   2.0699    2.0627         0.9382        50        194
   300   2.0758    2.0758         0.8133        48        214
  candidates evaluated: 7208   best_ever 2.0758 (1bec543c80abe8aa)  wall 214s

BEST PROGRAM 1bec543c80abe8aa (len 48, iteration 295, modification const@11+delete@28)
  search seed 101: eff 2.1855 succ 50/50 inter 2609 steps 12680 ws_cost 0 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [4.061, 1.0], "B": [2.964, 1.0], "C": [32.913, 1.0], "D": [184.696, 1.0], "E": [52.955, 1.0]}
  search seed 102: eff 1.9662 succ 50/50 inter 1972 steps 10143 ws_cost 0 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [3.169, 1.0], "B": [4.04, 1.0], "C": [32.913, 1.0], "D": [122.296, 1.0], "E": [47.929, 1.0]}
  listing:
      0  INPUT          R1, num_ops
      1  CONST          R5, 1
      2  MOV            R2, R1
      3  BRZ            R6, 8
      4  LT             R3, R0, R2
      5  BRZ            R3, 11
      6  ACT            R1
      7  ADD            R0, R0, R5
      8  ACT            R0
      9  ADD            R0, R0, R5
     10  JMP            4
     11  CONST          R0, -4
     12  MUL            R2, R1, R1
     13  LT             R3, R0, R2
     14  BRZ            R3, 31
     15  ACT            R1
     16  ADD            R0, R0, R5
     17  MOD            R3, R0, R1
     18  ACT            R3
     19  DIV            R4, R0, R1
     20  ACT            R4
     21  ADD            R0, R0, R5
     22  JMP            13
     23  BRNZ           R0, 38
     24  BLK_PATCH      R6, R1, R5
     25  MUL            R3, R1, R3
     26  BLK_APPEND     R6, R4
     27  MOD            R3, R4, R1
     28  HALT           
     29  ADD            R0, R0, R4
     30  JMP            4
     31  JMP            35
     32  WS_APPEND      R7, R7
     33  CONST          R5, -11
     34  DIV            R4, R3, R1
     35  ACT            R1
     36  MOD            R3, R0, R1
     37  ACT            R3
     38  DIV            R4, R0, R1
     39  MOD            R3, R4, R1
     40  ACT            R3
     41  DIV            R4, R4, R1
     42  MOD            R3, R4, R1
     43  ACT            R3
     44  ADD            R0, R0, R5
     45  ADD            R0, R0, R5
     46  JMP            35
     47  MOD            R3, R0, R1
  ancestry (88 steps, newest first): iteration/fitness/modification
    it  295  2.0758  len 48  const@11+delete@28
    it  294  2.0699  len 49  delete@23
    it  288  2.0699  len 50  delete@31+insert@25
    it  274  2.0699  len 50  const@11
    it  272  2.0595  len 50  swap@49,24
    it  270  2.0595  len 50  const@35
    it  269  2.0595  len 50  swap@15,6+replace@29
    it  261  2.0595  len 50  arg@35.1+duplicate@45+1->7
    it  260  2.0407  len 49  const@34
    it  255  2.0407  len 49  arg@28.0+swap@23,32+delete@24
    it  251  2.0407  len 50  delete@27
    it  250  2.0407  len 51  delete@38
    it  239  2.0405  len 52  delete@29
    it  234  2.0405  len 53  insert@3
    it  229  2.0396  len 52  const@36
    ... 74 more

QUALIFICATION suite=heldout_v1 seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED)
  player                        effA    effF    effR    effS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  CACHE_REUSE                  2.965   1.575   2.878   1.620  50.0  49.0     1332     6917    5315.7    0.0    0.0
  ADAPTIVE                     1.972   1.561   2.644   1.417  50.0  49.0     1332     6917    4436.4   27.7    8.7
  ENUMERATE                    1.635   1.635   1.635   1.635  49.0  49.0     6917     6917       0.0    0.0    0.0
  HEURISTIC                    1.591   1.591   1.591   1.591  42.0  42.0     1874     1874       0.0    0.0    0.0
  ancestor1_it0_0875253d162c   1.506   1.506   1.506   1.506  48.0  48.0     5611     5611       0.0    0.0    0.0
  ENUMERATE_VM                 1.506   1.506   1.506   1.506  48.0  48.0     5611     5611       0.0    0.0    0.0
  ancestor44_it146_15270da96   1.350   1.350   1.350   1.350  45.0  45.0     7439     7439       0.0    0.0    0.0
  top1_1bec543c80abe8aa        1.347   1.347   1.347   1.347  45.0  45.0     7312     7312       0.0    0.0    0.0
  top2_5bddc24d0cf39ece        1.347   1.347   1.347   1.347  45.0  45.0     7312     7312       0.0    0.0    0.0
  top3_b1f7245b0d597f16        1.347   1.347   1.347   1.347  45.0  45.0     7312     7312       0.0    0.0    0.0
  ancestor88_it294_4ae1d09df   1.340   1.340   1.340   1.340  45.0  45.0     7291     7291       0.0    0.0    0.0
  contemp_9c78e3d0a419ad02     0.533   0.533   0.533   0.533  23.3  23.3    12074    12074       0.0    0.0    0.0
  RANDOM                       0.205   0.205   0.205   0.205   3.3   3.3    14823    14823       0.0    0.0    0.0
  contemp_3b019fa98dbba9db     0.157   0.157   0.157   0.157   3.3   3.3    14305    14305       0.0    0.0    0.0
  contemp_5abceed3f4d28f57     0.088   0.088   0.088   0.088   6.7   6.7    14771    14771       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  CACHE_REUSE                   9.89/   4.29    8.07/   4.36    2.65/  33.14    6.18/ 259.04  184.78/ 499.06
  ADAPTIVE                     11.56/   4.83    9.37/   4.90    3.24/  33.74   10.51/ 259.64  288.27/ 499.66
  ENUMERATE                     3.48/   3.48    3.54/   3.54   31.87/  31.87  255.22/ 255.22  492.37/ 492.37
  HEURISTIC                     3.48/   3.48    3.54/   3.54   34.80/  34.80   60.61/  60.61   98.65/  98.65
  ancestor1_it0_0875253d162c    3.72/   3.72    3.79/   3.79   34.59/  34.59  264.39/ 264.39  342.45/ 342.45
  ENUMERATE_VM                  3.72/   3.72    3.79/   3.79   34.59/  34.59  264.39/ 264.39  342.45/ 342.45
  ancestor44_it146_15270da96    3.71/   3.71    3.78/   3.78   49.12/  49.12  233.22/ 233.22  596.29/ 596.29
  top1_1bec543c80abe8aa         3.47/   3.47    4.61/   4.61   49.69/  49.69  218.07/ 218.07  596.30/ 596.30
  top2_5bddc24d0cf39ece         3.47/   3.47    4.61/   4.61   49.69/  49.69  218.07/ 218.07  596.30/ 596.30
  top3_b1f7245b0d597f16         3.47/   3.47    4.61/   4.61   49.69/  49.69  218.07/ 218.07  596.30/ 596.30
  ancestor88_it294_4ae1d09df    3.71/   3.71    4.84/   4.84   48.59/  48.59  217.12/ 217.12  595.68/ 595.68
  contemp_9c78e3d0a419ad02      3.95/   3.95    5.70/   5.70  124.70/ 124.70  566.83/ 566.83  658.58/ 658.58
  RANDOM                       15.89/  15.89   14.75/  14.75  121.20/ 121.20  808.00/ 808.00  641.35/ 641.35
  contemp_3b019fa98dbba9db     15.25/  15.25   17.60/  17.60  124.34/ 124.34  773.35/ 773.35  657.37/ 657.37
  contemp_5abceed3f4d28f57     14.17/  14.17   13.16/  13.16  130.78/ 130.78  871.98/ 871.98  692.13/ 692.13

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                      absent_op5_d2  absent_op5_d3         depth4   heldout_pair heldout_triple new_combinatio      primitive  reversed_pair
  CACHE_REUSE                   12/12    58     6/6    496     6/6      4    18/18     2    15/15     3    15/15     3    60/60     2    18/18     2
  ADAPTIVE                      12/12    58     6/6    496     6/6      4    18/18     2    15/15     3    15/15     3    60/60     2    18/18     2
  ENUMERATE                     12/12    58     6/6    496     3/6   1350    18/18    38    15/15   257    15/15   251    60/60     3    18/18    25
  HEURISTIC                      9/12    40     0/6    180     3/6    133    13/18    56    13/15    45    10/15    76    60/60     3    18/18    13
  ancestor1_it0_0875253d162c    12/12    52     6/6    480     0/6    726    18/18    40    15/15   257    15/15   248    60/60     3    18/18    25
  ENUMERATE_VM                  12/12    52     6/6    480     0/6    726    18/18    40    15/15   257    15/15   248    60/60     3    18/18    25
  ancestor44_it146_15270da96    12/12    37     1/6    716     0/6   1500    18/18    62    13/15   220    13/15   226    60/60     3    18/18    31
  top1_1bec543c80abe8aa         12/12    37     1/6    717     0/6   1500    18/18    67    13/15   206    13/15   212    60/60     4    18/18    27
  top2_5bddc24d0cf39ece         12/12    37     1/6    717     0/6   1500    18/18    67    13/15   206    13/15   212    60/60     4    18/18    27
  top3_b1f7245b0d597f16         12/12    37     1/6    717     0/6   1500    18/18    67    13/15   206    13/15   212    60/60     4    18/18    27
  ancestor88_it294_4ae1d09df    12/12    36     1/6    717     0/6   1500    18/18    66    13/15   205    13/15   211    60/60     4    18/18    26
  contemp_9c78e3d0a419ad02       0/12   120     0/6    800     0/6   1500     0/18   120     5/15   547     5/15   546    60/60     4     0/18   120
  RANDOM                         0/12   120     0/6    800     0/6   1500     0/18   120     0/15   800     0/15   800    10/60    15     0/18   120
  contemp_3b019fa98dbba9db       0/12   120     0/6    800     0/6   1500     0/18   120     1/15   747     1/15   747     8/60    16     0/18   120
  contemp_5abceed3f4d28f57       0/12   120     0/6    800     0/6   1500     0/18   120     0/15   800     0/15   800    20/60    13     0/18   120

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  CACHE_REUSE                   85.56       --    93.37    85.56    93.37    93.37    93.37   0.0
  ADAPTIVE                     133.96   106.96   142.50   133.96   114.87   114.87   114.87  10.7
  ENUMERATE                    360.62       --   360.62   360.62   360.62   360.62   360.62   0.0
  HEURISTIC                     77.52       --    77.52    77.52    77.52    77.52    77.52   0.0
  ancestor1_it0_0875253d162c   299.08       --   299.08   299.08   299.08   299.08   299.08   0.0
  ENUMERATE_VM                 299.08       --   299.08   299.08   299.08   299.08   299.08   0.0
  ancestor44_it146_15270da96   394.59       --   394.59   394.59   394.59   394.59   394.59   0.0
  top1_1bec543c80abe8aa        386.17       --   386.17   386.17   386.17   386.17   386.17   0.0
  top2_5bddc24d0cf39ece        386.17       --   386.17   386.17   386.17   386.17   386.17   0.0
  top3_b1f7245b0d597f16        386.17       --   386.17   386.17   386.17   386.17   386.17   0.0
  ancestor88_it294_4ae1d09df   385.37       --   385.37   385.37   385.37   385.37   385.37   0.0
  contemp_9c78e3d0a419ad02     607.61       --   607.61   607.61   607.61   607.61   607.61   0.0
  RANDOM                       733.93       --   733.93   733.93   733.93   733.93   733.93   0.0
  contemp_3b019fa98dbba9db     721.80       --   721.80   721.80   721.80   721.80   721.80   0.0
  contemp_5abceed3f4d28f57     792.05       --   792.05   792.05   792.05   792.05   792.05   0.0

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
  ancestor44_it146_15270da96c268463
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [45, 46, 44] vs FRESH [45, 46, 44]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [7783.6, 6926.4, 8365.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [398.05, 353.87, 431.85] vs CODE_ONLY [398.05, 353.87, 431.85]
    4_scramble_or_reset_damages            0/3  eff ACC [1.361, 1.426, 1.264] SCR [1.361, 1.426, 1.264] RESET [1.361, 1.426, 1.264]
    5_transfers_to_fresh_copy              0/3  FULL [398.05, 353.87, 431.85] vs ACC remainder [398.05, 353.87, 431.85]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [398.05, 353.87, 431.85]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [398.05, 353.87, 431.85] STORAGE_MATCHED [398.05, 353.87, 431.85] vs ACC remainder [398.05, 353.87, 431.85]
  top1_1bec543c80abe8aa
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [45, 46, 44] vs FRESH [45, 46, 44]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [7535.0, 6693.1, 8414.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [384.03, 340.16, 434.32] vs CODE_ONLY [384.03, 340.16, 434.32]
    4_scramble_or_reset_damages            0/3  eff ACC [1.354, 1.453, 1.235] SCR [1.354, 1.453, 1.235] RESET [1.354, 1.453, 1.235]
    5_transfers_to_fresh_copy              0/3  FULL [384.03, 340.16, 434.32] vs ACC remainder [384.03, 340.16, 434.32]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [384.03, 340.16, 434.32]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [384.03, 340.16, 434.32] STORAGE_MATCHED [384.03, 340.16, 434.32] vs ACC remainder [384.03, 340.16, 434.32]
  top2_5bddc24d0cf39ece
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [45, 46, 44] vs FRESH [45, 46, 44]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [7535.0, 6693.1, 8414.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [384.03, 340.16, 434.32] vs CODE_ONLY [384.03, 340.16, 434.32]
    4_scramble_or_reset_damages            0/3  eff ACC [1.354, 1.453, 1.235] SCR [1.354, 1.453, 1.235] RESET [1.354, 1.453, 1.235]
    5_transfers_to_fresh_copy              0/3  FULL [384.03, 340.16, 434.32] vs ACC remainder [384.03, 340.16, 434.32]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [384.03, 340.16, 434.32]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [384.03, 340.16, 434.32] STORAGE_MATCHED [384.03, 340.16, 434.32] vs ACC remainder [384.03, 340.16, 434.32]
  top3_b1f7245b0d597f16
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [45, 46, 44] vs FRESH [45, 46, 44]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [7535.0, 6693.1, 8414.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [384.03, 340.16, 434.32] vs CODE_ONLY [384.03, 340.16, 434.32]
    4_scramble_or_reset_damages            0/3  eff ACC [1.354, 1.453, 1.235] SCR [1.354, 1.453, 1.235] RESET [1.354, 1.453, 1.235]
    5_transfers_to_fresh_copy              0/3  FULL [384.03, 340.16, 434.32] vs ACC remainder [384.03, 340.16, 434.32]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [384.03, 340.16, 434.32]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [384.03, 340.16, 434.32] STORAGE_MATCHED [384.03, 340.16, 434.32] vs ACC remainder [384.03, 340.16, 434.32]
  ancestor88_it294_4ae1d09dfde05245
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [45, 46, 44] vs FRESH [45, 46, 44]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [7507.3, 6664.3, 8387.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [383.23, 339.3, 433.57] vs CODE_ONLY [383.23, 339.3, 433.57]
    4_scramble_or_reset_damages            0/3  eff ACC [1.391, 1.411, 1.218] SCR [1.391, 1.411, 1.218] RESET [1.391, 1.411, 1.218]
    5_transfers_to_fresh_copy              0/3  FULL [383.23, 339.3, 433.57] vs ACC remainder [383.23, 339.3, 433.57]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [383.23, 339.3, 433.57]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [383.23, 339.3, 433.57] STORAGE_MATCHED [383.23, 339.3, 433.57] vs ACC remainder [383.23, 339.3, 433.57]
  contemp_9c78e3d0a419ad02
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [24, 23, 23] vs FRESH [24, 23, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [11923.3, 12713.2, 12663.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [579.27, 623.15, 620.39] vs CODE_ONLY [579.27, 623.15, 620.39]
    4_scramble_or_reset_damages            0/3  eff ACC [0.544, 0.502, 0.551] SCR [0.544, 0.502, 0.551] RESET [0.544, 0.502, 0.551]
    5_transfers_to_fresh_copy              0/3  FULL [579.27, 623.15, 620.39] vs ACC remainder [579.27, 623.15, 620.39]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [579.27, 623.15, 620.39]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [579.27, 623.15, 620.39] STORAGE_MATCHED [579.27, 623.15, 620.39] vs ACC remainder [579.27, 623.15, 620.39]
  RANDOM
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [3, 2, 5] vs FRESH [3, 2, 5]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [14665.2, 14665.2, 14665.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [733.93, 733.93, 733.93] vs CODE_ONLY [733.93, 733.93, 733.93]
    4_scramble_or_reset_damages            0/3  eff ACC [0.174, 0.191, 0.25] SCR [0.174, 0.191, 0.25] RESET [0.174, 0.191, 0.25]
    5_transfers_to_fresh_copy              0/3  FULL [733.93, 733.93, 733.93] vs ACC remainder [733.93, 733.93, 733.93]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [733.93, 733.93, 733.93]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [733.93, 733.93, 733.93] STORAGE_MATCHED [733.93, 733.93, 733.93] vs ACC remainder [733.93, 733.93, 733.93]
  contemp_3b019fa98dbba9db
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [5, 2, 3] vs FRESH [5, 2, 3]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [14213.8, 14207.5, 15032.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [706.76, 706.41, 752.24] vs CODE_ONLY [706.76, 706.41, 752.24]
    4_scramble_or_reset_damages            0/3  eff ACC [0.159, 0.155, 0.157] SCR [0.159, 0.155, 0.157] RESET [0.159, 0.155, 0.157]
    5_transfers_to_fresh_copy              0/3  FULL [706.76, 706.41, 752.24] vs ACC remainder [706.76, 706.41, 752.24]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [706.76, 706.41, 752.24]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [706.76, 706.41, 752.24] STORAGE_MATCHED [706.76, 706.41, 752.24] vs ACC remainder [706.76, 706.41, 752.24]
  contemp_5abceed3f4d28f57
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [9, 4, 7] vs FRESH [9, 4, 7]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [15826.2, 15826.2, 15826.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [792.05, 792.05, 792.05] vs CODE_ONLY [792.05, 792.05, 792.05]
    4_scramble_or_reset_damages            0/3  eff ACC [0.101, 0.069, 0.093] SCR [0.101, 0.069, 0.093] RESET [0.101, 0.069, 0.093]
    5_transfers_to_fresh_copy              0/3  FULL [792.05, 792.05, 792.05] vs ACC remainder [792.05, 792.05, 792.05]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [792.05, 792.05, 792.05]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [792.05, 792.05, 792.05] STORAGE_MATCHED [792.05, 792.05, 792.05] vs ACC remainder [792.05, 792.05, 792.05]

MACHINERY OF top1_1bec543c80abe8aa (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   0     0
    task  9:     0    0    0    0    0 |   0     0
    task 19:     0    0    0    0    0 |   0     0
    task 31:     0    0    0    0    0 |   0     0
    task 41:     0    0    0    0    0 |   0     0
    task 49:     0    0    0    0    0 |   0     0
  artifact events: 0 (create 0, delete 0, patch/append 0); invocations by block: {}; edges: 0
  adaptation curve ACC:   2 1 7 2 2 4 3 3 6 1 1 2 7 7 6 7 6 1 7 6 22 74 67 52 89 83 22 49 49 22 20 74 215 134 81 59 833 190 327 62 62 46 833 833 18 1561 31 31 1561 37
  adaptation curve FRESH: 2 1 7 2 2 4 3 3 6 1 1 2 7 7 6 7 6 1 7 6 22 74 67 52 89 83 22 49 49 22 20 74 215 134 81 59 833 190 327 62 62 46 833 833 18 1561 31 31 1561 37
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

