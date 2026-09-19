CRIUS CAMPAIGN 0 REPORT  run=search_c0x_random_s1  arm=random
code_commit=f4dae7a66 dirty=True config_hash=a204326d0078673d world=57065ca240cee53d partitions=ece4bd004beb4710
==============================================================================
SEARCH PROGRESS (fitness = C0_EFFICIENCY, mean over search seeds; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1   0.1125    0.0705         0.0208        18          3
    26   0.1910    0.1903         0.1685        41         23
    51   0.3314    0.3234         0.2625        38         42
    76   0.4672    0.4555         0.3702        52         48
   101   0.6131    0.6079         0.4784        58         54
   126   0.7234    0.7228         0.5613        62         60
   151   0.7433    0.7317         0.5404        62         64
   176   0.7765    0.7734         0.6171        64         68
   201   0.8033    0.7842         0.6054        64         73
   226   0.8319    0.8318         0.6312        63         79
   251   0.8433    0.8432         0.6805        62         84
   276   0.9564    0.9078         0.7561        62         88
   300   0.9568    0.9568         0.7578        58         93
  candidates evaluated: 7208   best_ever 0.9568 (e530062f2fabd457)  wall 93s

BEST PROGRAM e530062f2fabd457 (len 58, iteration 297, modification delete@42)
  search seed 101: eff 0.9982 succ 38/50 inter 878 steps 2447 ws_cost 608 blocks 0 invoked 0 ws_bytes 50
    by stage (mean cost, success rate): {"A": [6.158, 1.0], "B": [5.347, 1.0], "C": [26.427, 0.667], "D": [30.475, 0.5], "E": [21.453, 0.625]}
  search seed 102: eff 0.9155 succ 38/50 inter 821 steps 2277 ws_cost 582 blocks 0 invoked 0 ws_bytes 50
    by stage (mean cost, success rate): {"A": [4.627, 1.0], "B": [4.919, 1.0], "C": [25.058, 0.75], "D": [25.918, 0.5], "E": [24.282, 0.5]}
  listing:
      0  BLK_COPY       R1, R6
      1  VGET           R0, R6, R0
      2  WS_APPEND      R4, R0
      3  WS_FREE        R1
      4  ACTI           18
      5  ACT            R1
      6  VGET           R5, R6, R0
      7  ACTI           5
      8  ACT            R1
      9  ACT            R7
     10  EQ             R3, R4, R5
     11  BLK_LEN        R6, R0
     12  ACT            R1
     13  EQ             R3, R1, R1
     14  ACTI           -12
     15  DIV            R1, R0, R4
     16  ACT            R3
     17  ACT            R1
     18  ACT            R6
     19  ACTI           -11
     20  ACT            R1
     21  LT             R1, R5, R7
     22  ACT            R1
     23  VGET           R2, R1, R4
     24  ACTI           4
     25  BLK_REC_END    R5
     26  ACTI           -11
     27  BLK_STATE_SET  R4, R7, R3
     28  ACT            R6
     29  ACT            R1
     30  BRZ            R5, 18
     31  LT             R1, R5, R7
     32  ACT            R1
     33  ACT            R1
     34  ACT            R6
     35  EQ             R5, R0, R5
     36  VSET           R7, R7, R7
     37  ACT            R1
     38  MOD            R4, R1, R4
     39  ACT            R1
     40  BLK_COPY       R1, R0
     41  VGET           R0, R6, R0
     42  VGET           R5, R6, R2
     43  WS_SLEN        R6, R6
     44  ACTI           -15
     45  BLK_REC_END    R5
     46  NOT            R0, R2
     47  ACTI           -11
     48  WS_SLEN        R6, R2
     49  BRZ            R2, 16
     50  ACTI           4
     51  ACTI           17
     52  BLK_STATE_SET  R3, R6, R6
     53  EQ             R3, R1, R1
     54  ACT            R1
     55  DIV            R1, R0, R7
     56  ACT            R1
     57  ACT            R6
  ancestry (123 steps, newest first): iteration/fitness/modification
    it  297  0.9568  len 58  delete@42
    it  290  0.9568  len 59  delete@42+swap@33,20
    it  287  0.9567  len 60  delete@1
    it  280  0.9564  len 61  replace@4
    it  279  0.9566  len 61  delete@26+swap@11,37
    it  274  0.9564  len 62  arg@20.0
    it  273  0.8863  len 62  arg@32.0+replace@44
    it  270  0.8863  len 62  delete@30
    it  266  0.8862  len 63  arg@52.1+delete@4
    it  259  0.8861  len 64  duplicate@5+1->40
    it  257  0.8862  len 63  delete@32
    it  256  0.8861  len 64  duplicate@38+2->62+arg@48.2+arg@49.1
    it  254  0.8433  len 62  swap@60,50+const@50+swap@12,42
    it  247  0.8433  len 62  replace@1
    it  246  0.8432  len 62  arg@61.2+delete@54+insert@21
    ... 109 more

QUALIFICATION suite=heldout_v1 seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED)
  player                        effA    effF    effR    effS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  CACHE_REUSE                  2.965   1.575   2.878   1.620  50.0  49.0     1332     6917    5315.7    0.0    0.0
  ADAPTIVE                     1.972   1.561   2.644   1.417  50.0  49.0     1332     6917    4436.4   27.7    8.7
  ENUMERATE                    1.635   1.635   1.635   1.635  49.0  49.0     6917     6917       0.0    0.0    0.0
  HEURISTIC                    1.591   1.591   1.591   1.591  42.0  42.0     1874     1874       0.0    0.0    0.0
  ENUMERATE_VM                 1.506   1.506   1.506   1.506  48.0  48.0     5611     5611       0.0    0.0    0.0
  top1_e530062f2fabd457        0.591   0.584   0.588   0.591  25.0  24.7     1050     1071      20.6    0.0    0.0
  top2_2ca995411089d7f7        0.591   0.584   0.588   0.591  25.0  24.7     1050     1071      20.6    0.0    0.0
  top3_0918961dd4f21619        0.591   0.584   0.588   0.591  25.0  24.7     1050     1071      20.6    0.0    0.0
  ancestor123_it290_d672f085   0.591   0.584   0.588   0.591  25.0  24.7     1050     1071      20.6    0.0    0.0
  ancestor62_it113_1d09ba0f3   0.539   0.539   0.539   0.539  24.0  24.0      834      834       0.0    0.0    0.0
  contemp_ba7c8858aaaee461     0.461   0.442   0.457   0.461  22.3  22.0     1050     1071      20.6    0.0    0.0
  contemp_005c5df3022015c7     0.454   0.447   0.453   0.454  17.7  17.3     1174     1194      19.6    0.0    0.0
  contemp_7ef58aa5dc0682db     0.363   0.365   0.372   0.363  16.3  17.0     1128     1137       8.5    0.0    0.0
  RANDOM                       0.205   0.205   0.205   0.205   3.3   3.3    14823    14823       0.0    0.0    0.0
  ancestor1_it0_071a88bd5e8e   0.050   0.050   0.050   0.050   2.7   2.7       50       50       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  CACHE_REUSE                   9.89/   4.29    8.07/   4.36    2.65/  33.14    6.18/ 259.04  184.78/ 499.06
  ADAPTIVE                     11.56/   4.83    9.37/   4.90    3.24/  33.74   10.51/ 259.64  288.27/ 499.66
  ENUMERATE                     3.48/   3.48    3.54/   3.54   31.87/  31.87  255.22/ 255.22  492.37/ 492.37
  HEURISTIC                     3.48/   3.48    3.54/   3.54   34.80/  34.80   60.61/  60.61   98.65/  98.65
  ENUMERATE_VM                  3.72/   3.72    3.79/   3.79   34.59/  34.59  264.39/ 264.39  342.45/ 342.45
  top1_e530062f2fabd457         4.90/   4.90    7.59/   7.59   29.01/  30.12   33.22/  33.51   35.10/  35.65
  top2_2ca995411089d7f7         4.90/   4.90    7.59/   7.59   29.01/  30.12   33.22/  33.51   35.10/  35.65
  top3_0918961dd4f21619         4.90/   4.90    7.59/   7.59   29.02/  30.13   33.23/  33.52   35.11/  35.66
  ancestor123_it290_d672f085    4.90/   4.90    7.59/   7.59   29.03/  30.13   33.23/  33.53   35.12/  35.67
  ancestor62_it113_1d09ba0f3    6.18/   6.18    9.07/   9.07   22.31/  22.31   25.01/  25.01   26.41/  26.41
  contemp_ba7c8858aaaee461      6.32/   6.32    6.34/   6.34   29.03/  30.13   33.10/  33.39   35.12/  35.67
  contemp_005c5df3022015c7     10.23/  10.23   11.03/  11.03   32.37/  33.40   33.23/  33.53   35.12/  35.67
  contemp_7ef58aa5dc0682db      7.76/   7.76   11.23/  11.23   29.04/  30.15   34.80/  33.51   35.14/  36.16
  RANDOM                       15.89/  15.89   14.75/  14.75  121.20/ 121.20  808.00/ 808.00  641.35/ 641.35
  ancestor1_it0_071a88bd5e8e    1.22/   1.22    1.22/   1.22    1.22/   1.22    1.22/   1.22    1.22/   1.22

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                      absent_op5_d2  absent_op5_d3         depth4   heldout_pair heldout_triple new_combinatio      primitive  reversed_pair
  CACHE_REUSE                   12/12    58     6/6    496     6/6      4    18/18     2    15/15     3    15/15     3    60/60     2    18/18     2
  ADAPTIVE                      12/12    58     6/6    496     6/6      4    18/18     2    15/15     3    15/15     3    60/60     2    18/18     2
  ENUMERATE                     12/12    58     6/6    496     3/6   1350    18/18    38    15/15   257    15/15   251    60/60     3    18/18    25
  HEURISTIC                      9/12    40     0/6    180     3/6    133    13/18    56    13/15    45    10/15    76    60/60     3    18/18    13
  ENUMERATE_VM                  12/12    52     6/6    480     0/6    726    18/18    40    15/15   257    15/15   248    60/60     3    18/18    25
  top1_e530062f2fabd457          1/12    34     0/6     35     0/6     34     0/18    35     2/15    32     3/15    32    60/60     6     9/18    21
  top2_2ca995411089d7f7          1/12    34     0/6     35     0/6     34     0/18    35     2/15    32     3/15    32    60/60     6     9/18    21
  top3_0918961dd4f21619          1/12    34     0/6     35     0/6     34     0/18    35     2/15    32     3/15    32    60/60     6     9/18    21
  ancestor123_it290_d672f085     1/12    34     0/6     35     0/6     34     0/18    35     2/15    32     3/15    32    60/60     6     9/18    21
  ancestor62_it113_1d09ba0f3     0/12    25     0/6     25     0/6     25     0/18    25     2/15    24     3/15    24    60/60     7     7/18    17
  contemp_ba7c8858aaaee461       1/12    34     0/6     35     0/6     34     0/18    35     3/15    32     4/15    32    50/60     6     9/18    21
  contemp_005c5df3022015c7       1/12    34     0/6     35     0/6     34     3/18    30     2/15    32     3/15    32    42/60    10     2/18    33
  contemp_7ef58aa5dc0682db       1/12    34     0/6     35     0/6     34     0/18    35     1/15    33     0/15    35    38/60     9     9/18    21
  RANDOM                         0/12   120     0/6    800     0/6   1500     0/18   120     0/15   800     0/15   800    10/60    15     0/18   120
  ancestor1_it0_071a88bd5e8e     0/12     1     0/6      1     0/6      1     0/18     1     0/15     1     0/15     1     8/60     1     0/18     1

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  CACHE_REUSE                   85.56       --    93.37    85.56    93.37    93.37    93.37   0.0
  ADAPTIVE                     133.96   106.96   142.50   133.96   114.87   114.87   114.87  10.7
  ENUMERATE                    360.62       --   360.62   360.62   360.62   360.62   360.62   0.0
  HEURISTIC                     77.52       --    77.52    77.52    77.52    77.52    77.52   0.0
  ENUMERATE_VM                 299.08       --   299.08   299.08   299.08   299.08   299.08   0.0
  top1_e530062f2fabd457         34.05       --    34.39    34.05    34.39    34.39    34.39   0.0
  top2_2ca995411089d7f7         34.05       --    34.39    34.05    34.39    34.39    34.39   0.0
  top3_0918961dd4f21619         34.06       --    34.40    34.06    34.40    34.40    34.40   0.0
  ancestor123_it290_d672f085    34.07       --    34.41    34.07    34.41    34.41    34.41   0.0
  ancestor62_it113_1d09ba0f3    25.63       --    25.63    25.63    25.63    25.63    25.63   0.0
  contemp_ba7c8858aaaee461      34.00       --    34.33    34.00    34.33    34.33    34.33   0.0
  contemp_005c5df3022015c7      34.07       --    34.41    34.07    34.41    34.41    34.41   0.0
  contemp_7ef58aa5dc0682db      34.95       --    34.87    34.95    34.87    34.87    34.87   0.0
  RANDOM                       733.93       --   733.93   733.93   733.93   733.93   733.93   0.0
  ancestor1_it0_071a88bd5e8e     1.22       --     1.22     1.22     1.22     1.22     1.22   0.0

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
  top1_e530062f2fabd457
    0_competence_kept_ACC_ge_FRESH         2/3  successes ACC [24, 24, 27] vs FRESH [22, 25, 27]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [42.9, 0.7, 18.2] vs 5% of FRESH cost [1040.4, 958.0, 946.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [34.08, 34.41, 33.67] vs CODE_ONLY [34.7, 34.75, 33.73]
    4_scramble_or_reset_damages            0/3  eff ACC [0.555, 0.541, 0.676] SCR [0.555, 0.541, 0.676] RESET [0.549, 0.563, 0.651]
    5_transfers_to_fresh_copy              0/3  FULL [34.08, 34.41, 33.67] vs ACC remainder [34.08, 34.41, 33.67]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [34.08, 34.41, 33.67]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [34.7, 34.75, 33.73] STORAGE_MATCHED [34.7, 34.75, 33.73] vs ACC remainder [34.08, 34.41, 33.67]
  top2_2ca995411089d7f7
    0_competence_kept_ACC_ge_FRESH         2/3  successes ACC [24, 24, 27] vs FRESH [22, 25, 27]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [42.9, 0.7, 18.2] vs 5% of FRESH cost [1040.4, 958.0, 946.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [34.08, 34.41, 33.67] vs CODE_ONLY [34.7, 34.75, 33.73]
    4_scramble_or_reset_damages            0/3  eff ACC [0.555, 0.541, 0.676] SCR [0.555, 0.541, 0.676] RESET [0.549, 0.563, 0.651]
    5_transfers_to_fresh_copy              0/3  FULL [34.08, 34.41, 33.67] vs ACC remainder [34.08, 34.41, 33.67]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [34.08, 34.41, 33.67]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [34.7, 34.75, 33.73] STORAGE_MATCHED [34.7, 34.75, 33.73] vs ACC remainder [34.08, 34.41, 33.67]
  top3_0918961dd4f21619
    0_competence_kept_ACC_ge_FRESH         2/3  successes ACC [24, 24, 27] vs FRESH [22, 25, 27]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [42.9, 0.7, 18.2] vs 5% of FRESH cost [1040.7, 958.2, 946.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [34.09, 34.42, 33.68] vs CODE_ONLY [34.71, 34.76, 33.74]
    4_scramble_or_reset_damages            0/3  eff ACC [0.555, 0.541, 0.676] SCR [0.555, 0.541, 0.676] RESET [0.549, 0.563, 0.651]
    5_transfers_to_fresh_copy              0/3  FULL [34.09, 34.42, 33.68] vs ACC remainder [34.09, 34.42, 33.68]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [34.09, 34.42, 33.68]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [34.71, 34.76, 33.74] STORAGE_MATCHED [34.71, 34.76, 33.74] vs ACC remainder [34.09, 34.42, 33.68]
  ancestor123_it290_d672f085a216c3f5
    0_competence_kept_ACC_ge_FRESH         2/3  successes ACC [24, 24, 27] vs FRESH [22, 25, 27]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [42.9, 0.7, 18.2] vs 5% of FRESH cost [1041.0, 958.5, 947.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [34.09, 34.43, 33.69] vs CODE_ONLY [34.72, 34.77, 33.75]
    4_scramble_or_reset_damages            0/3  eff ACC [0.555, 0.541, 0.676] SCR [0.555, 0.541, 0.676] RESET [0.549, 0.563, 0.651]
    5_transfers_to_fresh_copy              0/3  FULL [34.09, 34.43, 33.69] vs ACC remainder [34.09, 34.43, 33.69]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [34.09, 34.43, 33.69]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [34.72, 34.77, 33.75] STORAGE_MATCHED [34.72, 34.77, 33.75] vs ACC remainder [34.09, 34.43, 33.69]
  ancestor62_it113_1d09ba0f35d5b602
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [23, 23, 26] vs FRESH [23, 23, 26]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [748.0, 729.1, 710.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [25.12, 26.41, 25.36] vs CODE_ONLY [25.12, 26.41, 25.36]
    4_scramble_or_reset_damages            0/3  eff ACC [0.53, 0.478, 0.608] SCR [0.53, 0.478, 0.608] RESET [0.531, 0.479, 0.608]
    5_transfers_to_fresh_copy              0/3  FULL [25.12, 26.41, 25.36] vs ACC remainder [25.12, 26.41, 25.36]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [25.12, 26.41, 25.36]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [25.12, 26.41, 25.36] STORAGE_MATCHED [25.12, 26.41, 25.36] vs ACC remainder [25.12, 26.41, 25.36]
  contemp_ba7c8858aaaee461
    0_competence_kept_ACC_ge_FRESH         2/3  successes ACC [20, 22, 25] vs FRESH [18, 23, 25]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [42.9, 0.7, 18.2] vs 5% of FRESH cost [1041.0, 956.4, 945.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [34.09, 34.32, 33.58] vs CODE_ONLY [34.72, 34.65, 33.63]
    4_scramble_or_reset_damages            0/3  eff ACC [0.424, 0.421, 0.537] SCR [0.424, 0.421, 0.537] RESET [0.418, 0.44, 0.514]
    5_transfers_to_fresh_copy              0/3  FULL [34.09, 34.32, 33.58] vs ACC remainder [34.09, 34.32, 33.58]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [34.09, 34.32, 33.58]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [34.72, 34.65, 33.63] STORAGE_MATCHED [34.72, 34.65, 33.63] vs ACC remainder [34.09, 34.32, 33.58]
  contemp_005c5df3022015c7
    0_competence_kept_ACC_ge_FRESH         2/3  successes ACC [18, 15, 20] vs FRESH [16, 16, 20]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [42.9, 0.7, 15.2] vs 5% of FRESH cost [1038.9, 1018.2, 1006.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [34.09, 34.43, 33.69] vs CODE_ONLY [34.72, 34.77, 33.75]
    4_scramble_or_reset_damages            0/3  eff ACC [0.451, 0.381, 0.53] SCR [0.451, 0.381, 0.53] RESET [0.446, 0.401, 0.512]
    5_transfers_to_fresh_copy              0/3  FULL [34.09, 34.43, 33.69] vs ACC remainder [34.09, 34.43, 33.69]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [34.09, 34.43, 33.69]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [34.72, 34.77, 33.75] STORAGE_MATCHED [34.72, 34.77, 33.75] vs ACC remainder [34.09, 34.43, 33.69]
  contemp_7ef58aa5dc0682db
    0_competence_kept_ACC_ge_FRESH         1/3  successes ACC [14, 18, 17] vs FRESH [14, 19, 18]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [18.2, -0.4, 7.8] vs 5% of FRESH cost [1029.1, 957.0, 972.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [34.8, 34.4, 35.66] vs CODE_ONLY [34.05, 34.73, 35.83]
    4_scramble_or_reset_damages            0/3  eff ACC [0.336, 0.366, 0.386] SCR [0.336, 0.366, 0.386] RESET [0.362, 0.382, 0.371]
    5_transfers_to_fresh_copy              0/3  FULL [34.8, 34.4, 35.66] vs ACC remainder [34.8, 34.4, 35.66]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [34.8, 34.4, 35.66]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [34.05, 34.73, 35.83] STORAGE_MATCHED [34.05, 34.73, 35.83] vs ACC remainder [34.8, 34.4, 35.66]
  RANDOM
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [3, 2, 5] vs FRESH [3, 2, 5]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [14665.2, 14665.2, 14665.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [733.93, 733.93, 733.93] vs CODE_ONLY [733.93, 733.93, 733.93]
    4_scramble_or_reset_damages            0/3  eff ACC [0.174, 0.191, 0.25] SCR [0.174, 0.191, 0.25] RESET [0.174, 0.191, 0.25]
    5_transfers_to_fresh_copy              0/3  FULL [733.93, 733.93, 733.93] vs ACC remainder [733.93, 733.93, 733.93]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [733.93, 733.93, 733.93]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [733.93, 733.93, 733.93] STORAGE_MATCHED [733.93, 733.93, 733.93] vs ACC remainder [733.93, 733.93, 733.93]
  ancestor1_it0_071a88bd5e8eed21
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [4, 1, 3] vs FRESH [4, 1, 3]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [36.6, 36.6, 36.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1.22, 1.22, 1.22] vs CODE_ONLY [1.22, 1.22, 1.22]
    4_scramble_or_reset_damages            0/3  eff ACC [0.058, 0.04, 0.052] SCR [0.058, 0.04, 0.052] RESET [0.058, 0.04, 0.052]
    5_transfers_to_fresh_copy              0/3  FULL [1.22, 1.22, 1.22] vs ACC remainder [1.22, 1.22, 1.22]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1.22, 1.22, 1.22]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1.22, 1.22, 1.22] STORAGE_MATCHED [1.22, 1.22, 1.22] vs ACC remainder [1.22, 1.22, 1.22]

MACHINERY OF top1_e530062f2fabd457 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     1    0    1    0    0 |   0     0
    task  9:    10    0    1    0    0 |   0     0
    task 19:    20    0    1    0    0 |   0     0
    task 31:    32    0    1    0    0 |   0     0
    task 41:    42    0    1    0    0 |   0     0
    task 49:    50    0    1    0    0 |   0     0
  artifact events: 0 (create 0, delete 0, patch/append 0); invocations by block: {}; edges: 0
  adaptation curve ACC:   4 3 15 4 4 7 1 1 2 3 3 4 15 15 2 15 2 3 15 2 36 36 36 36 36 36 33 36 36 21 5 36 36 33 24 36 36 36 36 36 33 36 36 36 36 36 21 33 36 36
  adaptation curve FRESH: 4 3 15 4 4 7 1 1 2 3 3 4 15 15 2 15 2 3 15 2 36 36 36 36 36 36 36 36 36 36 5 36 36 36 24 36 36 36 36 36 36 36 36 36 36 36 36 36 36 36
  reuse_gain per task:    0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3 0 0 15 0 0 0 3 0 0 0 0 0 0 3 0 0 0 0 0 15 3 0 0

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

