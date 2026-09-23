CRIUS CAMPAIGN 0 REPORT  run=search_c0_seeded_s2  arm=seeded
code_commit=f4dae7a66 dirty=False config_hash=65fd4678cbcdd9c5 world=57065ca240cee53d partitions=ece4bd004beb4710
==============================================================================
SEARCH PROGRESS (fitness = C0_EFFICIENCY, mean over search seeds; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1   1.6157    1.4015         0.5401        39          1
    26   2.5060    2.5050         1.7202        45         11
    51   2.5073    2.5073         1.7353        34         25
    76   2.5075    2.5075         1.8209        24         42
   101   2.5154    2.5154         1.6356        25         59
   126   2.5162    2.5155         1.7232        23         73
   151   2.5162    2.5162         1.6048        20         87
   176   2.5194    2.5194         1.2052        18         99
   201   2.5194    2.5194         0.9693        16        117
   226   2.5194    2.5194         0.9739        15        134
   251   2.5194    2.5194         0.6337        15        148
   276   2.5194    2.5194         1.1549        15        165
   300   2.5194    2.5194         1.1434        15        180
  candidates evaluated: 7208   best_ever 2.5194 (ef85dee5dabd2e35)  wall 180s

BEST PROGRAM ef85dee5dabd2e35 (len 18, iteration 166, modification delete@9)
  search seed 101: eff 2.8795 succ 20/50 inter 240 steps 1154 ws_cost 0 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [3.557, 1.0], "B": [2.727, 1.0], "C": [6.29, 0.0], "D": [6.29, 0.0], "E": [6.29, 0.0]}
  search seed 102: eff 2.1592 succ 20/50 inter 253 steps 1202 ws_cost 0 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [3.451, 1.0], "B": [4.181, 1.0], "C": [6.29, 0.0], "D": [6.29, 0.0], "E": [6.29, 0.0]}
  listing:
      0  INPUT          R1, num_ops
      1  MOV            R2, R1
      2  CONST          R5, 1
      3  LT             R3, R0, R2
      4  BRZ            R3, 18
      5  ACT            R0
      6  ACT            R1
      7  ADD            R0, R0, R5
      8  ACT            R0
      9  ACT            R1
     10  ADD            R0, R0, R5
     11  ACT            R0
     12  ACT            R2
     13  ADD            R0, R0, R5
     14  JMP            3
     15  WS_LINK_GET    R7, R5, R1
     16  VGET           R2, R3, R2
     17  BLK_STATE_SET  R1, R6, R0
  ancestry (87 steps, newest first): iteration/fitness/modification
    it  166  2.5194  len 18  delete@9
    it  163  2.5175  len 19  arg@16.0+insert@17
    it  162  2.5175  len 18  arg@13.0+delete@18
    it  158  2.5169  len 19  swap@4,5
    it  157  2.5162  len 19  delete@19
    it  156  2.5162  len 20  replace@19
    it  147  2.5162  len 20  const@19+delete@19
    it  139  2.5162  len 21  const@20+delete@19
    it  138  2.5162  len 22  delete@20
    it  130  2.5162  len 23  const@21+swap@2,1+replace@20
    it  125  2.5162  len 23  duplicate@5+4->9
    it  122  2.5154  len 19  const@18+delete@16
    it  121  2.5154  len 20  arg@17.1
    it  118  2.5154  len 20  const@18
    it  117  2.5154  len 20  delete@15+arg@19.1
    ... 73 more

QUALIFICATION suite=heldout_v1 seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED)
  player                        effA    effF    effR    effS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  top1_3f43de330f2d3edd        3.021   3.021   3.021   3.021  20.0  20.0      249      249       0.0    0.0    0.0
  top2_6d21889901c3bedf        3.021   3.021   3.021   3.021  20.0  20.0      249      249       0.0    0.0    0.0
  top3_72ccc6b274f4ad99        3.021   3.021   3.021   3.021  20.0  20.0      249      249       0.0    0.0    0.0
  ancestor87_it163_ae0f7e014   3.019   3.019   3.019   3.019  20.0  20.0      249      249       0.0    0.0    0.0
  ancestor44_it61_9a9993b101   3.007   3.007   3.007   3.007  20.0  20.0      249      249       0.0    0.0    0.0
  CACHE_REUSE                  2.965   1.575   2.878   1.620  50.0  49.0     1332     6917    5315.7    0.0    0.0
  HEURISTIC                    2.245   2.245   2.245   2.245  42.0  42.0     1874     1874       0.0    0.0    0.0
  contemp_9e567c9b0bfd351b     2.002   2.002   2.002   2.002   6.7   6.7       97       97       0.0    0.0    0.0
  ADAPTIVE                     1.972   1.561   2.644   1.417  50.0  49.0     1332     6917    4436.4   27.7    8.7
  ENUMERATE                    1.635   1.635   1.635   1.635  49.0  49.0     6917     6917       0.0    0.0    0.0
  ancestor1_it0_0875253d162c   1.601   1.601   1.601   1.601  48.0  48.0     5611     5611       0.0    0.0    0.0
  ENUMERATE_VM                 1.601   1.601   1.601   1.601  48.0  48.0     5611     5611       0.0    0.0    0.0
  RANDOM                       0.205   0.205   0.205   0.205   3.3   3.3    14823    14823       0.0    0.0    0.0
  contemp_4e01fa2ef0239519     0.047   0.047   0.047   0.047   2.7   2.7    14835    14835       0.0    0.0    0.0
  contemp_e3f2bc3f78d34494     0.000   0.000   0.000   0.000   0.0   0.0        0        0       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  top1_3f43de330f2d3edd         3.59/   3.59    3.66/   3.66    6.29/   6.29    6.29/   6.29    6.29/   6.29
  top2_6d21889901c3bedf         3.59/   3.59    3.66/   3.66    6.29/   6.29    6.29/   6.29    6.29/   6.29
  top3_72ccc6b274f4ad99         3.59/   3.59    3.66/   3.66    6.29/   6.29    6.29/   6.29    6.29/   6.29
  ancestor87_it163_ae0f7e014    3.60/   3.60    3.67/   3.67    6.31/   6.31    6.31/   6.31    6.31/   6.31
  ancestor44_it61_9a9993b101    3.64/   3.64    3.71/   3.71    6.44/   6.44    6.44/   6.44    6.44/   6.44
  CACHE_REUSE                   9.89/   4.29    8.07/   4.36    2.65/  33.14    6.18/ 259.04  184.78/ 499.06
  HEURISTIC                     3.48/   3.48    3.54/   3.54   34.80/  34.80   60.61/  60.61   98.65/  98.65
  contemp_9e567c9b0bfd351b      1.94/   1.94    2.08/   2.08    2.17/   2.17    2.17/   2.17    2.17/   2.17
  ADAPTIVE                     11.56/   4.83    9.37/   4.90    3.24/  33.74   10.51/ 259.64  288.27/ 499.66
  ENUMERATE                     3.48/   3.48    3.54/   3.54   31.87/  31.87  255.22/ 255.22  492.37/ 492.37
  ancestor1_it0_0875253d162c    3.72/   3.72    3.79/   3.79   34.59/  34.59  264.39/ 264.39  342.45/ 342.45
  ENUMERATE_VM                  3.72/   3.72    3.79/   3.79   34.59/  34.59  264.39/ 264.39  342.45/ 342.45
  RANDOM                       15.89/  15.89   14.75/  14.75  121.20/ 121.20  808.00/ 808.00  641.35/ 641.35
  contemp_4e01fa2ef0239519     15.19/  15.19   17.54/  17.54  124.80/ 124.80  832.01/ 832.01  660.40/ 660.40
  contemp_e3f2bc3f78d34494      0.06/   0.06    0.06/   0.06    0.06/   0.06    0.06/   0.06    0.06/   0.06

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                      absent_op5_d2  absent_op5_d3         depth4   heldout_pair heldout_triple new_combinatio      primitive  reversed_pair
  top1_3f43de330f2d3edd          0/12     6     0/6      6     0/6      6     0/18     6     0/15     6     0/15     6    60/60     3     0/18     6
  top2_6d21889901c3bedf          0/12     6     0/6      6     0/6      6     0/18     6     0/15     6     0/15     6    60/60     3     0/18     6
  top3_72ccc6b274f4ad99          0/12     6     0/6      6     0/6      6     0/18     6     0/15     6     0/15     6    60/60     3     0/18     6
  ancestor87_it163_ae0f7e014     0/12     6     0/6      6     0/6      6     0/18     6     0/15     6     0/15     6    60/60     3     0/18     6
  ancestor44_it61_9a9993b101     0/12     6     0/6      6     0/6      6     0/18     6     0/15     6     0/15     6    60/60     3     0/18     6
  CACHE_REUSE                   12/12    58     6/6    496     6/6      4    18/18     2    15/15     3    15/15     3    60/60     2    18/18     2
  HEURISTIC                      9/12    40     0/6    180     3/6    133    13/18    56    13/15    45    10/15    76    60/60     3    18/18    13
  contemp_9e567c9b0bfd351b       0/12     2     0/6      2     0/6      2     0/18     2     0/15     2     0/15     2    20/60     2     0/18     2
  ADAPTIVE                      12/12    58     6/6    496     6/6      4    18/18     2    15/15     3    15/15     3    60/60     2    18/18     2
  ENUMERATE                     12/12    58     6/6    496     3/6   1350    18/18    38    15/15   257    15/15   251    60/60     3    18/18    25
  ancestor1_it0_0875253d162c    12/12    52     6/6    480     0/6    726    18/18    40    15/15   257    15/15   248    60/60     3    18/18    25
  ENUMERATE_VM                  12/12    52     6/6    480     0/6    726    18/18    40    15/15   257    15/15   248    60/60     3    18/18    25
  RANDOM                         0/12   120     0/6    800     0/6   1500     0/18   120     0/15   800     0/15   800    10/60    15     0/18   120
  contemp_4e01fa2ef0239519       0/12   120     0/6    800     0/6   1500     0/18   120     0/15   800     0/15   800     8/60    16     0/18   120
  contemp_e3f2bc3f78d34494       0/12     0     0/6      0     0/6      0     0/18     0     0/15     0     0/15     0     0/60     0     0/18     0

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  top1_3f43de330f2d3edd          6.29       --     6.29     6.29     6.29     6.29     6.29   0.0
  top2_6d21889901c3bedf          6.29       --     6.29     6.29     6.29     6.29     6.29   0.0
  top3_72ccc6b274f4ad99          6.29       --     6.29     6.29     6.29     6.29     6.29   0.0
  ancestor87_it163_ae0f7e014     6.31       --     6.31     6.31     6.31     6.31     6.31   0.0
  ancestor44_it61_9a9993b101     6.44       --     6.44     6.44     6.44     6.44     6.44   0.0
  CACHE_REUSE                   85.56       --    93.37    85.56    93.37    93.37    93.37   0.0
  HEURISTIC                     77.52       --    77.52    77.52    77.52    77.52    77.52   0.0
  contemp_9e567c9b0bfd351b       2.17       --     2.17     2.17     2.17     2.17     2.17   0.0
  ADAPTIVE                     133.96   106.96   142.50   133.96   114.87   114.87   114.87  10.7
  ENUMERATE                    360.62       --   360.62   360.62   360.62   360.62   360.62   0.0
  ancestor1_it0_0875253d162c   299.08       --   299.08   299.08   299.08   299.08   299.08   0.0
  ENUMERATE_VM                 299.08       --   299.08   299.08   299.08   299.08   299.08   0.0
  RANDOM                       733.93       --   733.93   733.93   733.93   733.93   733.93   0.0
  contemp_4e01fa2ef0239519     755.74       --   755.74   755.74   755.74   755.74   755.74   0.0
  contemp_e3f2bc3f78d34494       0.06       --     0.06     0.06     0.06     0.06     0.06   0.0

CHARTER s13 CHECKLIST (seeds passing / seeds; thresholds: 5 percent relative; guard 0 added 2026-09-19, see report.py)
  top1_3f43de330f2d3edd
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 20, 20] vs FRESH [20, 20, 20]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [188.7, 188.7, 188.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [6.29, 6.29, 6.29] vs CODE_ONLY [6.29, 6.29, 6.29]
    4_scramble_or_reset_damages            0/3  eff ACC [3.084, 2.71, 3.269] SCR [3.084, 2.71, 3.269] RESET [3.084, 2.71, 3.269]
    5_transfers_to_fresh_copy              0/3  FULL [6.29, 6.29, 6.29] vs ACC remainder [6.29, 6.29, 6.29]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [6.29, 6.29, 6.29]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [6.29, 6.29, 6.29] STORAGE_MATCHED [6.29, 6.29, 6.29] vs ACC remainder [6.29, 6.29, 6.29]
  top2_6d21889901c3bedf
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 20, 20] vs FRESH [20, 20, 20]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [188.7, 188.7, 188.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [6.29, 6.29, 6.29] vs CODE_ONLY [6.29, 6.29, 6.29]
    4_scramble_or_reset_damages            0/3  eff ACC [3.084, 2.71, 3.269] SCR [3.084, 2.71, 3.269] RESET [3.084, 2.71, 3.269]
    5_transfers_to_fresh_copy              0/3  FULL [6.29, 6.29, 6.29] vs ACC remainder [6.29, 6.29, 6.29]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [6.29, 6.29, 6.29]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [6.29, 6.29, 6.29] STORAGE_MATCHED [6.29, 6.29, 6.29] vs ACC remainder [6.29, 6.29, 6.29]
  top3_72ccc6b274f4ad99
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 20, 20] vs FRESH [20, 20, 20]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [188.7, 188.7, 188.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [6.29, 6.29, 6.29] vs CODE_ONLY [6.29, 6.29, 6.29]
    4_scramble_or_reset_damages            0/3  eff ACC [3.084, 2.71, 3.269] SCR [3.084, 2.71, 3.269] RESET [3.084, 2.71, 3.269]
    5_transfers_to_fresh_copy              0/3  FULL [6.29, 6.29, 6.29] vs ACC remainder [6.29, 6.29, 6.29]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [6.29, 6.29, 6.29]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [6.29, 6.29, 6.29] STORAGE_MATCHED [6.29, 6.29, 6.29] vs ACC remainder [6.29, 6.29, 6.29]
  ancestor87_it163_ae0f7e01403255a4
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 20, 20] vs FRESH [20, 20, 20]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [189.3, 189.3, 189.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [6.31, 6.31, 6.31] vs CODE_ONLY [6.31, 6.31, 6.31]
    4_scramble_or_reset_damages            0/3  eff ACC [3.082, 2.708, 3.267] SCR [3.082, 2.708, 3.267] RESET [3.082, 2.708, 3.267]
    5_transfers_to_fresh_copy              0/3  FULL [6.31, 6.31, 6.31] vs ACC remainder [6.31, 6.31, 6.31]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [6.31, 6.31, 6.31]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [6.31, 6.31, 6.31] STORAGE_MATCHED [6.31, 6.31, 6.31] vs ACC remainder [6.31, 6.31, 6.31]
  ancestor44_it61_9a9993b1014ce36e
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 20, 20] vs FRESH [20, 20, 20]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [193.2, 193.2, 193.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [6.44, 6.44, 6.44] vs CODE_ONLY [6.44, 6.44, 6.44]
    4_scramble_or_reset_damages            0/3  eff ACC [3.069, 2.698, 3.254] SCR [3.069, 2.698, 3.254] RESET [3.069, 2.698, 3.254]
    5_transfers_to_fresh_copy              0/3  FULL [6.44, 6.44, 6.44] vs ACC remainder [6.44, 6.44, 6.44]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [6.44, 6.44, 6.44]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [6.44, 6.44, 6.44] STORAGE_MATCHED [6.44, 6.44, 6.44] vs ACC remainder [6.44, 6.44, 6.44]
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
  contemp_9e567c9b0bfd351b
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [5, 7, 8] vs FRESH [5, 7, 8]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [65.1, 65.1, 65.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [2.17, 2.17, 2.17] vs CODE_ONLY [2.17, 2.17, 2.17]
    4_scramble_or_reset_damages            0/3  eff ACC [1.647, 1.854, 2.504] SCR [1.647, 1.854, 2.504] RESET [1.647, 1.854, 2.504]
    5_transfers_to_fresh_copy              0/3  FULL [2.17, 2.17, 2.17] vs ACC remainder [2.17, 2.17, 2.17]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [2.17, 2.17, 2.17]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [2.17, 2.17, 2.17] STORAGE_MATCHED [2.17, 2.17, 2.17] vs ACC remainder [2.17, 2.17, 2.17]
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
  RANDOM
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [3, 2, 5] vs FRESH [3, 2, 5]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [14665.2, 14665.2, 14665.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [733.93, 733.93, 733.93] vs CODE_ONLY [733.93, 733.93, 733.93]
    4_scramble_or_reset_damages            0/3  eff ACC [0.174, 0.191, 0.25] SCR [0.174, 0.191, 0.25] RESET [0.174, 0.191, 0.25]
    5_transfers_to_fresh_copy              0/3  FULL [733.93, 733.93, 733.93] vs ACC remainder [733.93, 733.93, 733.93]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [733.93, 733.93, 733.93]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [733.93, 733.93, 733.93] STORAGE_MATCHED [733.93, 733.93, 733.93] vs ACC remainder [733.93, 733.93, 733.93]
  contemp_4e01fa2ef0239519
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [4, 1, 3] vs FRESH [4, 1, 3]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [15100.9, 15100.9, 15100.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [755.74, 755.74, 755.74] vs CODE_ONLY [755.74, 755.74, 755.74]
    4_scramble_or_reset_damages            0/3  eff ACC [0.055, 0.038, 0.049] SCR [0.055, 0.038, 0.049] RESET [0.055, 0.038, 0.049]
    5_transfers_to_fresh_copy              0/3  FULL [755.74, 755.74, 755.74] vs ACC remainder [755.74, 755.74, 755.74]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [755.74, 755.74, 755.74]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [755.74, 755.74, 755.74] STORAGE_MATCHED [755.74, 755.74, 755.74] vs ACC remainder [755.74, 755.74, 755.74]
  contemp_e3f2bc3f78d34494
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1.8, 1.8, 1.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [0.06, 0.06, 0.06] vs CODE_ONLY [0.06, 0.06, 0.06]
    4_scramble_or_reset_damages            0/3  eff ACC [0.0, 0.0, 0.0] SCR [0.0, 0.0, 0.0] RESET [0.0, 0.0, 0.0]
    5_transfers_to_fresh_copy              0/3  FULL [0.06, 0.06, 0.06] vs ACC remainder [0.06, 0.06, 0.06]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [0.06, 0.06, 0.06]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [0.06, 0.06, 0.06] STORAGE_MATCHED [0.06, 0.06, 0.06] vs ACC remainder [0.06, 0.06, 0.06]

MACHINERY OF top1_3f43de330f2d3edd (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   0     0
    task  9:     0    0    0    0    0 |   0     0
    task 19:     0    0    0    0    0 |   0     0
    task 31:     0    0    0    0    0 |   0     0
    task 41:     0    0    0    0    0 |   0     0
    task 49:     0    0    0    0    0 |   0     0
  artifact events: 0 (create 0, delete 0, patch/append 0); invocations by block: {}; edges: 0
  adaptation curve ACC:   3 1 2 3 3 4 5 5 6 1 1 3 2 2 6 2 6 1 2 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6
  adaptation curve FRESH: 3 1 2 3 3 4 5 5 6 1 1 3 2 2 6 2 6 1 2 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6
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

