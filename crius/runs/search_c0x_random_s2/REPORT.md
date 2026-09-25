CRIUS CAMPAIGN 0 REPORT  run=search_c0x_random_s2  arm=random
code_commit=f4dae7a66 dirty=True config_hash=a204326d0078673d world=57065ca240cee53d partitions=ece4bd004beb4710
==============================================================================
SEARCH PROGRESS (fitness = C0_EFFICIENCY, mean over search seeds; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1   0.0700    0.0648         0.0243         9          1
    26   0.3106    0.3076         0.2606        38         10
    51   0.4936    0.4750         0.4076        59         23
    76   0.5538    0.5538         0.4521        60         29
   101   0.5923    0.5923         0.5131        62         33
   126   0.6206    0.6111         0.4540        57         39
   151   0.6777    0.6776         0.5101        55         47
   176   0.7637    0.7453         0.5450        57         56
   201   0.7672    0.7671         0.5802        52         64
   226   0.7676    0.7675         0.5473        49         70
   251   0.7684    0.7683         0.5075        42         76
   276   0.7685    0.7685         0.5302        41         85
   300   0.7686    0.7686         0.5101        40         90
  candidates evaluated: 7208   best_ever 0.7686 (ec58ed730a3ea51b)  wall 90s

BEST PROGRAM ec58ed730a3ea51b (len 40, iteration 297, modification delete@27)
  search seed 101: eff 0.9394 succ 37/50 inter 475 steps 2144 ws_cost 1239 blocks 33 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [8.409, 0.9], "B": [6.894, 1.0], "C": [9.396, 0.833], "D": [14.374, 0.3], "E": [12.414, 0.625]}
  search seed 102: eff 0.5979 succ 31/50 inter 532 steps 2349 ws_cost 1343 blocks 33 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [8.699, 0.8], "B": [7.587, 1.0], "C": [11.331, 0.667], "D": [15.207, 0.2], "E": [14.753, 0.375]}
  listing:
      0  VGET           R4, R7, R1
      1  BLK_NEW        R1
      2  WS_FIND        R3, R0
      3  ACT            R3
      4  VLEN           R2, R2
      5  MUL            R5, R3, R7
      6  VGET           R6, R4, R7
      7  ACT            R7
      8  DIV            R7, R4, R4
      9  ACT            R7
     10  BLK_REC_END    R7
     11  WS_REC_NEW     R3
     12  ACT            R7
     13  CONST          R3, -18
     14  ACT            R3
     15  BLK_NEW        R7
     16  BRNZ           R6, 19
     17  WS_REC_NEW     R3
     18  ACT            R3
     19  BLK_COUNT      R7
     20  ACT            R7
     21  WS_FIND        R3, R0
     22  WS_REC_GET     R4, R1, R0
     23  BRZ            R6, 0
     24  ACT            R2
     25  ACT            R3
     26  WS_ALLOC       R6, R2
     27  BLK_DELETE     R4
     28  DIV            R7, R3, R5
     29  BLK_COPY       R7, R7
     30  VGET           R3, R6, R6
     31  ACT            R2
     32  ACTI           16
     33  ACT            R3
     34  ACTI           13
     35  ACTI           -2
     36  ACT            R7
     37  ACTI           2
     38  INPUT          R2, current_block
     39  ACTI           4
  ancestry (111 steps, newest first): iteration/fitness/modification
    it  297  0.7686  len 40  delete@27
    it  271  0.7685  len 41  arg@6.2
    it  254  0.7685  len 41  delete@19
    it  248  0.7684  len 42  swap@19,20+delete@29
    it  246  0.7683  len 43  delete@11
    it  245  0.7682  len 44  delete@0
    it  244  0.7680  len 45  insert@30+delete@41+delete@31
    it  238  0.7680  len 46  arg@2.0+delete@40
    it  229  0.7679  len 47  delete@25
    it  227  0.7677  len 48  delete@7
    it  223  0.7676  len 49  const@7+delete@14
    it  221  0.7675  len 50  delete@40
    it  214  0.7674  len 51  delete@22
    it  211  0.7673  len 52  swap@35,7
    it  201  0.7672  len 52  arg@34.1
    ... 97 more

QUALIFICATION suite=heldout_v1 seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED)
  player                        effA    effF    effR    effS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  CACHE_REUSE                  2.965   1.575   2.878   1.620  50.0  49.0     1332     6917    5315.7    0.0    0.0
  ADAPTIVE                     1.972   1.561   2.644   1.417  50.0  49.0     1332     6917    4436.4   27.7    8.7
  ENUMERATE                    1.635   1.635   1.635   1.635  49.0  49.0     6917     6917       0.0    0.0    0.0
  HEURISTIC                    1.591   1.591   1.591   1.591  42.0  42.0     1874     1874       0.0    0.0    0.0
  ENUMERATE_VM                 1.506   1.506   1.506   1.506  48.0  48.0     5611     5611       0.0    0.0    0.0
  top1_ec58ed730a3ea51b        0.506   0.504   0.481   0.506  22.7  21.7      623      612     -11.9   33.0    0.0
  top2_e7c6ee2b07b16a29        0.506   0.504   0.481   0.506  22.7  21.7      623      612     -12.0   33.0    0.0
  top3_143e35b6db20cab1        0.506   0.504   0.481   0.506  22.7  21.7      623      612     -12.0   33.0    0.0
  ancestor111_it271_faac591e   0.506   0.504   0.480   0.506  22.7  21.7      623      612     -12.0   33.0    0.0
  contemp_3aeff08696eb13c2     0.468   0.412   0.450   0.468  20.7  17.3      612      664      53.4   42.7    0.0
  ancestor56_it98_28318ce70f   0.376   0.346   0.379   0.376  18.0  18.7      706      732      24.6   32.0   96.3
  contemp_c58e73e24573d65c     0.364   0.335   0.358   0.364  19.3  18.3      629      619     -12.0   33.0    0.0
  contemp_870f8f2e8abaf32e     0.317   0.515   0.336   0.317  15.0  25.3    12713    11270   -1545.3   32.0    0.0
  RANDOM                       0.205   0.205   0.205   0.205   3.3   3.3    14823    14823       0.0    0.0    0.0
  ancestor1_it0_7d015143dbaa   0.050   0.050   0.050   0.050   2.7   2.7       50       50       0.0   32.0   98.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  CACHE_REUSE                   9.89/   4.29    8.07/   4.36    2.65/  33.14    6.18/ 259.04  184.78/ 499.06
  ADAPTIVE                     11.56/   4.83    9.37/   4.90    3.24/  33.74   10.51/ 259.64  288.27/ 499.66
  ENUMERATE                     3.48/   3.48    3.54/   3.54   31.87/  31.87  255.22/ 255.22  492.37/ 492.37
  HEURISTIC                     3.48/   3.48    3.54/   3.54   34.80/  34.80   60.61/  60.61   98.65/  98.65
  ENUMERATE_VM                  3.72/   3.72    3.79/   3.79   34.59/  34.59  264.39/ 264.39  342.45/ 342.45
  top1_ec58ed730a3ea51b         8.86/   8.25    9.94/   9.47   15.51/  15.14   15.66/  15.75   16.67/  16.96
  top2_e7c6ee2b07b16a29         8.86/   8.25    9.95/   9.48   15.53/  15.15   15.67/  15.76   16.68/  16.97
  top3_143e35b6db20cab1         8.86/   8.25    9.95/   9.48   15.53/  15.15   15.67/  15.76   16.68/  16.97
  ancestor111_it271_faac591e    8.87/   8.25    9.95/   9.49   15.53/  15.16   15.67/  15.77   16.69/  16.98
  contemp_3aeff08696eb13c2      8.87/  10.54    9.72/  11.40   15.06/  15.63   15.77/  16.64   16.48/  17.02
  ancestor56_it98_28318ce70f   10.93/  10.28   12.32/  12.26   18.15/  18.22   16.59/  18.47   18.97/  20.47
  contemp_c58e73e24573d65c      9.22/   8.61   10.30/   9.84   15.55/  15.18   15.69/  15.79   16.71/  17.00
  contemp_870f8f2e8abaf32e     10.46/   8.75   13.10/  11.03  110.26/  88.10  665.64/ 544.48  683.34/ 679.58
  RANDOM                       15.89/  15.89   14.75/  14.75  121.20/ 121.20  808.00/ 808.00  641.35/ 641.35
  ancestor1_it0_7d015143dbaa    1.35/   1.35    1.35/   1.35    1.35/   1.35    1.35/   1.35    1.35/   1.35

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                      absent_op5_d2  absent_op5_d3         depth4   heldout_pair heldout_triple new_combinatio      primitive  reversed_pair
  CACHE_REUSE                   12/12    58     6/6    496     6/6      4    18/18     2    15/15     3    15/15     3    60/60     2    18/18     2
  ADAPTIVE                      12/12    58     6/6    496     6/6      4    18/18     2    15/15     3    15/15     3    60/60     2    18/18     2
  ENUMERATE                     12/12    58     6/6    496     3/6   1350    18/18    38    15/15   257    15/15   251    60/60     3    18/18    25
  HEURISTIC                      9/12    40     0/6    180     3/6    133    13/18    56    13/15    45    10/15    76    60/60     3    18/18    13
  ENUMERATE_VM                  12/12    52     6/6    480     0/6    726    18/18    40    15/15   257    15/15   248    60/60     3    18/18    25
  top1_ec58ed730a3ea51b          0/12    16     0/6     16     0/6     16     0/18    16     2/15    15     3/15    14    55/60     9     8/18    13
  top2_e7c6ee2b07b16a29          0/12    16     0/6     16     0/6     16     0/18    16     2/15    15     3/15    14    55/60     9     8/18    13
  top3_143e35b6db20cab1          0/12    16     0/6     16     0/6     16     0/18    16     2/15    15     3/15    14    55/60     9     8/18    13
  ancestor111_it271_faac591e     0/12    16     0/6     16     0/6     16     0/18    16     2/15    15     3/15    14    55/60     9     8/18    13
  contemp_3aeff08696eb13c2       0/12    15     0/6     16     0/6     16     0/18    15     3/15    14     1/15    15    50/60     9     8/18    13
  ancestor56_it98_28318ce70f     0/12    18     0/6     18     0/6     17     0/18    17     4/15    15     3/15    16    39/60    11     8/18    16
  contemp_c58e73e24573d65c       0/12    16     0/6     16     0/6     16     0/18    16     2/15    15     3/15    14    45/60     9     8/18    13
  contemp_870f8f2e8abaf32e       0/12   120     0/6    800     0/6   1500     0/18   120     2/15   695     5/15   542    32/60    11     6/18    85
  RANDOM                         0/12   120     0/6    800     0/6   1500     0/18   120     0/15   800     0/15   800    10/60    15     0/18   120
  ancestor1_it0_7d015143dbaa     0/12     1     0/6      1     0/6      1     0/18     1     0/15     1     0/15     1     8/60     1     0/18     1

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  CACHE_REUSE                   85.56       --    93.37    85.56    93.37    93.37    93.37   0.0
  ADAPTIVE                     133.96   106.96   142.50   133.96   114.87   114.87   114.87  10.7
  ENUMERATE                    360.62       --   360.62   360.62   360.62   360.62   360.62   0.0
  HEURISTIC                     77.52       --    77.52    77.52    77.52    77.52    77.52   0.0
  ENUMERATE_VM                 299.08       --   299.08   299.08   299.08   299.08   299.08   0.0
  top1_ec58ed730a3ea51b         16.11    16.33    16.16    16.11    16.46    16.46    16.46  32.0
  top2_e7c6ee2b07b16a29         16.12    16.34    16.17    16.12    16.47    16.47    16.47  32.0
  top3_143e35b6db20cab1         16.12    16.34    16.17    16.12    16.47    16.47    16.47  32.0
  ancestor111_it271_faac591e    16.12    16.34    16.18    16.12    16.48    16.48    16.48  32.0
  contemp_3aeff08696eb13c2      16.08    16.01    15.96    16.08    16.35    16.35    16.35  32.0
  ancestor56_it98_28318ce70f    17.65    17.88    18.21    17.65    18.82    18.82    18.82  32.0
  contemp_c58e73e24573d65c      16.14    16.36    16.20    16.14    16.50    16.50    16.50  32.0
  contemp_870f8f2e8abaf32e     673.50   672.93   672.75   673.50   659.22   659.22   659.22  32.0
  RANDOM                       733.93       --   733.93   733.93   733.93   733.93   733.93   0.0
  ancestor1_it0_7d015143dbaa     1.35     1.35     1.35     1.35     1.35     1.35     1.35  32.0

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
  ENUMERATE_VM
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [48, 48, 48] vs FRESH [48, 48, 48]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [4920.9, 6275.5, 6199.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [248.65, 325.66, 322.94] vs CODE_ONLY [248.65, 325.66, 322.94]
    4_scramble_or_reset_damages            0/3  eff ACC [1.622, 1.428, 1.467] SCR [1.622, 1.428, 1.467] RESET [1.622, 1.428, 1.467]
    5_transfers_to_fresh_copy              0/3  FULL [248.65, 325.66, 322.94] vs ACC remainder [248.65, 325.66, 322.94]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [248.65, 325.66, 322.94]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [248.65, 325.66, 322.94] STORAGE_MATCHED [248.65, 325.66, 322.94] vs ACC remainder [248.65, 325.66, 322.94]
  top1_ec58ed730a3ea51b
    0_competence_kept_ACC_ge_FRESH         2/3  successes ACC [20, 24, 24] vs FRESH [20, 20, 25]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [2.7, 6.8, -13.1] vs 5% of FRESH cost [493.2, 480.7, 450.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       1/3  remainder mean cost FULL [16.39, 16.57, 15.36] vs CODE_ONLY [16.23, 16.57, 16.57]
    4_scramble_or_reset_damages            0/3  eff ACC [0.441, 0.507, 0.57] SCR [0.441, 0.507, 0.57] RESET [0.453, 0.482, 0.507]
    5_transfers_to_fresh_copy              1/3  FULL [16.39, 16.57, 15.36] vs ACC remainder [16.39, 16.57, 15.36]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [16.52, 16.4, 16.06] vs ACC remainder [16.39, 16.57, 15.36]
    7_not_compute_or_storage               1/3  COMPUTE_MATCHED [16.23, 16.57, 16.57] STORAGE_MATCHED [16.23, 16.57, 16.57] vs ACC remainder [16.39, 16.57, 15.36]
  top2_e7c6ee2b07b16a29
    0_competence_kept_ACC_ge_FRESH         2/3  successes ACC [20, 24, 24] vs FRESH [20, 20, 25]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [2.7, 6.7, -13.2] vs 5% of FRESH cost [493.5, 481.0, 450.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       1/3  remainder mean cost FULL [16.4, 16.58, 15.37] vs CODE_ONLY [16.24, 16.58, 16.58]
    4_scramble_or_reset_damages            0/3  eff ACC [0.441, 0.507, 0.57] SCR [0.441, 0.507, 0.57] RESET [0.453, 0.482, 0.507]
    5_transfers_to_fresh_copy              1/3  FULL [16.4, 16.58, 15.37] vs ACC remainder [16.4, 16.58, 15.37]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [16.53, 16.41, 16.07] vs ACC remainder [16.4, 16.58, 15.37]
    7_not_compute_or_storage               1/3  COMPUTE_MATCHED [16.24, 16.58, 16.58] STORAGE_MATCHED [16.24, 16.58, 16.58] vs ACC remainder [16.4, 16.58, 15.37]
  top3_143e35b6db20cab1
    0_competence_kept_ACC_ge_FRESH         2/3  successes ACC [20, 24, 24] vs FRESH [20, 20, 25]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [2.7, 6.7, -13.2] vs 5% of FRESH cost [493.5, 481.0, 450.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       1/3  remainder mean cost FULL [16.4, 16.58, 15.36] vs CODE_ONLY [16.24, 16.58, 16.58]
    4_scramble_or_reset_damages            0/3  eff ACC [0.441, 0.507, 0.57] SCR [0.441, 0.507, 0.57] RESET [0.453, 0.482, 0.507]
    5_transfers_to_fresh_copy              1/3  FULL [16.4, 16.58, 15.36] vs ACC remainder [16.4, 16.58, 15.36]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [16.53, 16.41, 16.07] vs ACC remainder [16.4, 16.58, 15.36]
    7_not_compute_or_storage               1/3  COMPUTE_MATCHED [16.24, 16.58, 16.58] STORAGE_MATCHED [16.24, 16.58, 16.58] vs ACC remainder [16.4, 16.58, 15.36]
  ancestor111_it271_faac591e03ecd896
    0_competence_kept_ACC_ge_FRESH         2/3  successes ACC [20, 24, 24] vs FRESH [20, 20, 25]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [2.7, 6.7, -13.2] vs 5% of FRESH cost [493.8, 481.3, 451.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       1/3  remainder mean cost FULL [16.41, 16.59, 15.37] vs CODE_ONLY [16.25, 16.59, 16.59]
    4_scramble_or_reset_damages            0/3  eff ACC [0.441, 0.507, 0.57] SCR [0.441, 0.507, 0.57] RESET [0.453, 0.482, 0.507]
    5_transfers_to_fresh_copy              1/3  FULL [16.41, 16.59, 15.37] vs ACC remainder [16.41, 16.59, 15.37]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [16.54, 16.42, 16.08] vs ACC remainder [16.41, 16.59, 15.37]
    7_not_compute_or_storage               1/3  COMPUTE_MATCHED [16.25, 16.59, 16.59] STORAGE_MATCHED [16.25, 16.59, 16.59] vs ACC remainder [16.41, 16.59, 15.37]
  contemp_3aeff08696eb13c2
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 18, 24] vs FRESH [19, 16, 17]
    1_cost_declines_via_accumulation       2/3  reuse_gain C-E per seed [28.6, 4.5, 26.6] vs 5% of FRESH cost [499.3, 479.8, 491.2] (and 0 held)
    2_reproduces_on_heldout                2/3  same test, qualification suite; seeds passing = 2/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [16.12, 16.12, 16.01] vs CODE_ONLY [16.35, 16.35, 16.35]
    4_scramble_or_reset_damages            0/3  eff ACC [0.441, 0.402, 0.562] SCR [0.441, 0.402, 0.562] RESET [0.419, 0.408, 0.524]
    5_transfers_to_fresh_copy              0/3  FULL [16.12, 16.12, 16.01] vs ACC remainder [16.12, 16.12, 16.01]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [15.95, 16.24, 15.84] vs ACC remainder [16.12, 16.12, 16.01]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [16.35, 16.35, 16.35] STORAGE_MATCHED [16.35, 16.35, 16.35] vs ACC remainder [16.12, 16.12, 16.01]
  ancestor56_it98_28318ce70f12b001
    0_competence_kept_ACC_ge_FRESH         1/3  successes ACC [16, 17, 21] vs FRESH [17, 17, 22]
    1_cost_declines_via_accumulation       1/3  reuse_gain C-E per seed [54.0, 31.5, 9.6] vs 5% of FRESH cost [578.1, 579.4, 543.8] (and 0 held)
    2_reproduces_on_heldout                1/3  same test, qualification suite; seeds passing = 1/3
    3_state_causal_FULL_vs_CODE_ONLY       1/3  remainder mean cost FULL [16.64, 18.91, 17.38] vs CODE_ONLY [19.19, 19.19, 18.08]
    4_scramble_or_reset_damages            0/3  eff ACC [0.324, 0.331, 0.475] SCR [0.324, 0.331, 0.475] RESET [0.326, 0.36, 0.45]
    5_transfers_to_fresh_copy              1/3  FULL [16.64, 18.91, 17.38] vs ACC remainder [16.64, 18.91, 17.38]
    6_executable_components_reused         0/3  invocations [97, 96, 96]; ABLATION_ALL cost [16.94, 18.68, 18.03] vs ACC remainder [16.64, 18.91, 17.38]
    7_not_compute_or_storage               1/3  COMPUTE_MATCHED [19.19, 19.19, 18.08] STORAGE_MATCHED [19.19, 19.19, 18.08] vs ACC remainder [16.64, 18.91, 17.38]
  contemp_c58e73e24573d65c
    0_competence_kept_ACC_ge_FRESH         2/3  successes ACC [16, 21, 21] vs FRESH [16, 17, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [2.7, 6.7, -13.2] vs 5% of FRESH cost [494.4, 481.9, 451.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       1/3  remainder mean cost FULL [16.43, 16.61, 15.39] vs CODE_ONLY [16.27, 16.61, 16.61]
    4_scramble_or_reset_damages            0/3  eff ACC [0.307, 0.382, 0.403] SCR [0.307, 0.382, 0.403] RESET [0.32, 0.38, 0.373]
    5_transfers_to_fresh_copy              1/3  FULL [16.43, 16.61, 15.39] vs ACC remainder [16.43, 16.61, 15.39]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [16.56, 16.44, 16.1] vs ACC remainder [16.43, 16.61, 15.39]
    7_not_compute_or_storage               1/3  COMPUTE_MATCHED [16.27, 16.61, 16.61] STORAGE_MATCHED [16.27, 16.61, 16.61] vs ACC remainder [16.43, 16.61, 15.39]
  contemp_870f8f2e8abaf32e
    0_competence_kept_ACC_ge_FRESH         0/3  successes ACC [15, 15, 15] vs FRESH [24, 25, 27]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [-1777.9, -1017.5, -1727.3] vs 5% of FRESH cost [12670.0, 12695.7, 10450.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [735.89, 688.14, 596.49] vs CODE_ONLY [736.21, 688.46, 552.99]
    4_scramble_or_reset_damages            0/3  eff ACC [0.281, 0.299, 0.372] SCR [0.281, 0.299, 0.372] RESET [0.28, 0.305, 0.422]
    5_transfers_to_fresh_copy              0/3  FULL [735.89, 688.14, 596.49] vs ACC remainder [735.89, 688.14, 596.49]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [735.61, 687.86, 595.31] vs ACC remainder [735.89, 688.14, 596.49]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [736.21, 688.46, 552.99] STORAGE_MATCHED [736.21, 688.46, 552.99] vs ACC remainder [735.89, 688.14, 596.49]
  RANDOM
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [3, 2, 5] vs FRESH [3, 2, 5]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [14665.2, 14665.2, 14665.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [733.93, 733.93, 733.93] vs CODE_ONLY [733.93, 733.93, 733.93]
    4_scramble_or_reset_damages            0/3  eff ACC [0.174, 0.191, 0.25] SCR [0.174, 0.191, 0.25] RESET [0.174, 0.191, 0.25]
    5_transfers_to_fresh_copy              0/3  FULL [733.93, 733.93, 733.93] vs ACC remainder [733.93, 733.93, 733.93]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [733.93, 733.93, 733.93]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [733.93, 733.93, 733.93] STORAGE_MATCHED [733.93, 733.93, 733.93] vs ACC remainder [733.93, 733.93, 733.93]
  ancestor1_it0_7d015143dbaaf77d
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [4, 1, 3] vs FRESH [4, 1, 3]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [40.5, 40.5, 40.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1.35, 1.35, 1.35] vs CODE_ONLY [1.35, 1.35, 1.35]
    4_scramble_or_reset_damages            0/3  eff ACC [0.058, 0.04, 0.052] SCR [0.058, 0.04, 0.052] RESET [0.058, 0.04, 0.052]
    5_transfers_to_fresh_copy              0/3  FULL [1.35, 1.35, 1.35] vs ACC remainder [1.35, 1.35, 1.35]
    6_executable_components_reused         0/3  invocations [98, 98, 98]; ABLATION_ALL cost [1.35, 1.35, 1.35] vs ACC remainder [1.35, 1.35, 1.35]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1.35, 1.35, 1.35] STORAGE_MATCHED [1.35, 1.35, 1.35] vs ACC remainder [1.35, 1.35, 1.35]

MACHINERY OF top1_ec58ed730a3ea51b (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    2    0 |   3    24
    task  9:     0    0    0   21    0 |  28   224
    task 19:     0    0    0   45    0 |  32   256
    task 31:     0    0    0   81    0 |  32   256
    task 41:     0    0    0  111    0 |  32   256
    task 49:     0    0    0  135    0 |  32   256
  artifact events: 34 (create 33, delete 1, patch/append 0); invocations by block: {}; edges: 0
    block 1 origin=new len=0 state=[0, 0, 0] instr=[]
    block 2 origin=new len=0 state=[0, 0, 0] instr=[]
    block 3 origin=new len=0 state=[0, 0, 0] instr=[]
    block 4 origin=new len=0 state=[0, 0, 0] instr=[]
    block 5 origin=new len=0 state=[0, 0, 0] instr=[]
  adaptation curve ACC:   7 1 6 4 16 3 16 17 14 1 1 16 12 12 15 11 15 1 12 15 17 16 17 16 17 17 17 17 16 17 12 17 17 17 11 17 16 16 17 17 17 17 17 16 16 17 17 17 17 17
  adaptation curve FRESH: 7 1 12 7 7 3 17 17 15 1 1 7 12 12 15 12 15 1 12 15 17 17 17 17 17 17 17 17 17 17 8 17 17 17 11 17 17 17 17 17 17 17 17 17 17 17 17 17 17 17
  reuse_gain per task:    0 0 6 2 -9 0 1 0 1 0 0 -9 0 0 0 1 0 0 0 0 0 1 0 1 0 0 0 0 1 0 -4 0 0 0 0 0 1 1 0 0 0 0 0 1 1 0 0 0 0 0

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

