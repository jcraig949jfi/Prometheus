CRIUS CAMPAIGN 0 REPORT  run=search_c0x_random_s3  arm=random
code_commit=f4dae7a66 dirty=True config_hash=a204326d0078673d world=57065ca240cee53d partitions=ece4bd004beb4710
==============================================================================
SEARCH PROGRESS (fitness = C0_EFFICIENCY, mean over search seeds; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1   0.1124    0.0701         0.0277        19          1
    26   0.2366    0.2326         0.2050        34          6
    51   0.3370    0.3361         0.3129        48         12
    76   0.4291    0.4291         0.3903        52         18
   101   0.5745    0.5744         0.4742        59         24
   126   0.5866    0.5865         0.4517        57         29
   151   0.6703    0.6383         0.5223        64         34
   176   0.7485    0.7477         0.5985        64         38
   201   0.8318    0.8317         0.6497        62         42
   226   0.8530    0.8528         0.6310        60         52
   251   0.9077    0.8760         0.6148        59         61
   276   0.9375    0.9157         0.6934        64         73
   300   0.9601    0.9600         0.7047        63         80
  candidates evaluated: 7208   best_ever 0.9601 (72ebab0c37a15132)  wall 80s

BEST PROGRAM 72ebab0c37a15132 (len 63, iteration 294, modification delete@35)
  search seed 101: eff 1.0057 succ 37/50 inter 720 steps 2766 ws_cost 836 blocks 35 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [4.649, 1.0], "B": [4.218, 1.0], "C": [18.34, 0.75], "D": [23.328, 0.3], "E": [26.749, 0.625]}
  search seed 102: eff 0.9145 succ 38/50 inter 757 steps 2887 ws_cost 872 blocks 35 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [4.342, 1.0], "B": [4.87, 1.0], "C": [18.26, 0.75], "D": [26.315, 0.4], "E": [27.525, 0.625]}
  listing:
      0  INPUT          R4, current
      1  CONST          R5, 7
      2  BLK_STATE_GET  R5, R2, R5
      3  BLK_DELETE     R6
      4  ACT            R3
      5  SUB            R6, R4, R6
      6  NOT            R2, R1
      7  MOV            R1, R5
      8  WS_SLEN        R7, R5
      9  BLK_LEN        R3, R6
     10  ACT            R3
     11  BLK_LEN        R6, R5
     12  NOT            R0, R2
     13  BLK_DELETE     R6
     14  ACT            R3
     15  NOT            R2, R2
     16  ACTI           12
     17  ACT            R3
     18  BLK_COPY       R5, R0
     19  LT             R4, R3, R1
     20  NOT            R2, R2
     21  ACT            R2
     22  BLK_REC_END    R3
     23  NOT            R2, R2
     24  ACT            R6
     25  SUB            R6, R4, R3
     26  ACTI           -5
     27  ACT            R5
     28  ACTI           -10
     29  BLK_REC_END    R3
     30  ACTI           -4
     31  BRNZ           R1, 2
     32  NOT            R2, R2
     33  ACT            R2
     34  ACT            R3
     35  NOT            R2, R2
     36  NOT            R2, R2
     37  NOT            R2, R2
     38  ACT            R6
     39  BLK_LEN        R3, R1
     40  BLK_REC_BEGIN  
     41  ACTI           -3
     42  BLK_NEW        R7
     43  ACT            R2
     44  NOT            R0, R2
     45  BLK_DELETE     R6
     46  ACT            R3
     47  ACTI           10
     48  ACT            R2
     49  ACT            R5
     50  ACT            R2
     51  WS_SLEN        R7, R5
     52  BRNZ           R0, 15
     53  BRNZ           R1, 5
     54  SUB            R6, R0, R7
     55  BLK_PATCH      R2, R0, R1
     56  BRNZ           R7, 33
     57  WS_REC_GET     R0, R2, R0
     58  VSET           R0, R2, R7
     59  CONST          R5, 11
     60  BLK_DELETE     R2
     61  VSET           R0, R5, R7
     62  ACT            R2
  ancestry (147 steps, newest first): iteration/fitness/modification
    it  294  0.9601  len 63  delete@35
    it  291  0.9599  len 64  arg@56.0
    it  290  0.9599  len 64  swap@52,35+replace@57
    it  286  0.9599  len 64  arg@52.2
    it  285  0.9599  len 64  swap@26,63+arg@23.0
    it  282  0.9376  len 64  replace@7+arg@19.2
    it  278  0.9376  len 64  insert@56+arg@35.0
    it  277  0.9376  len 63  delete@4
    it  275  0.9375  len 64  duplicate@27+2->50
    it  273  0.9124  len 62  replace@2+delete@30
    it  261  0.9080  len 63  duplicate@17+1->15
    it  259  0.9048  len 62  insert@9+replace@51
    it  254  0.9051  len 61  const@60
    it  251  0.8944  len 61  arg@55.0+duplicate@43+2->12+swap@29,40
    it  250  0.8666  len 59  arg@55.1
    ... 133 more

QUALIFICATION suite=heldout_v1 seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED)
  player                        effA    effF    effR    effS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  CACHE_REUSE                  2.965   1.575   2.878   1.620  50.0  49.0     1332     6917    5315.7    0.0    0.0
  ADAPTIVE                     1.972   1.561   2.644   1.417  50.0  49.0     1332     6917    4436.4   27.7    8.7
  ENUMERATE                    1.635   1.635   1.635   1.635  49.0  49.0     6917     6917       0.0    0.0    0.0
  HEURISTIC                    1.591   1.591   1.591   1.591  42.0  42.0     1874     1874       0.0    0.0    0.0
  ENUMERATE_VM                 1.506   1.506   1.506   1.506  48.0  48.0     5611     5611       0.0    0.0    0.0
  top1_001270f44949b659        0.558   0.615   0.562   0.565  23.3  24.7      925      868     -57.1   35.0    0.0
  top2_72ebab0c37a15132        0.558   0.615   0.562   0.565  23.3  24.7      925      868     -57.1   35.0    0.0
  top3_a505f68a42f0d912        0.558   0.615   0.562   0.565  23.3  24.7      925      868     -57.1   35.0    0.0
  contemp_b3ee69958ceefe01     0.558   0.615   0.562   0.565  23.3  24.7      925      868     -57.1   35.0    0.0
  ancestor147_it291_25a03c23   0.557   0.615   0.562   0.565  23.3  24.7      925      868     -57.1   35.0    0.0
  ancestor74_it106_ea707bc8e   0.518   0.518   0.518   0.518  23.3  23.3      634      634       0.0    0.0    0.0
  contemp_8794a25070781bfc     0.320   0.320   0.320   0.320  12.3  12.3    14479    14479       0.0    0.0    0.0
  RANDOM                       0.205   0.205   0.205   0.205   3.3   3.3    14823    14823       0.0    0.0    0.0
  contemp_2ed27ecbecb125eb     0.202   0.203   0.203   0.202   8.3   8.3      358      358       0.0   34.0    0.0
  ancestor1_it0_575a54f23bb2   0.050   0.050   0.050   0.050   2.7   2.7       50       50       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  CACHE_REUSE                   9.89/   4.29    8.07/   4.36    2.65/  33.14    6.18/ 259.04  184.78/ 499.06
  ADAPTIVE                     11.56/   4.83    9.37/   4.90    3.24/  33.74   10.51/ 259.64  288.27/ 499.66
  ENUMERATE                     3.48/   3.48    3.54/   3.54   31.87/  31.87  255.22/ 255.22  492.37/ 492.37
  HEURISTIC                     3.48/   3.48    3.54/   3.54   34.80/  34.80   60.61/  60.61   98.65/  98.65
  ENUMERATE_VM                  3.72/   3.72    3.79/   3.79   34.59/  34.59  264.39/ 264.39  342.45/ 342.45
  top1_001270f44949b659         4.62/   4.62    6.31/   5.29   28.83/  27.06   27.69/  26.39   29.68/  28.09
  top2_72ebab0c37a15132         4.62/   4.62    6.31/   5.29   28.83/  27.06   27.69/  26.39   29.68/  28.09
  top3_a505f68a42f0d912         4.62/   4.62    6.31/   5.29   28.83/  27.06   27.69/  26.39   29.68/  28.09
  contemp_b3ee69958ceefe01      4.62/   4.62    6.32/   5.29   28.85/  27.08   27.71/  26.41   29.70/  28.11
  ancestor147_it291_25a03c23    4.62/   4.62    6.32/   5.29   28.87/  27.10   27.72/  26.43   29.72/  28.13
  ancestor74_it106_ea707bc8e    7.56/   7.56    7.71/   7.71   16.82/  16.82   18.33/  18.33   18.33/  18.33
  contemp_8794a25070781bfc      9.93/   9.93   13.87/  13.87  128.96/ 128.96  832.06/ 832.06  683.10/ 683.10
  RANDOM                       15.89/  15.89   14.75/  14.75  121.20/ 121.20  808.00/ 808.00  641.35/ 641.35
  contemp_2ed27ecbecb125eb      6.23/   6.23    6.92/   6.92    7.86/   7.86    8.24/   8.24    8.38/   8.38
  ancestor1_it0_575a54f23bb2    1.31/   1.31    1.31/   1.31    1.31/   1.31    1.31/   1.31    1.31/   1.31

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                      absent_op5_d2  absent_op5_d3         depth4   heldout_pair heldout_triple new_combinatio      primitive  reversed_pair
  CACHE_REUSE                   12/12    58     6/6    496     6/6      4    18/18     2    15/15     3    15/15     3    60/60     2    18/18     2
  ADAPTIVE                      12/12    58     6/6    496     6/6      4    18/18     2    15/15     3    15/15     3    60/60     2    18/18     2
  ENUMERATE                     12/12    58     6/6    496     3/6   1350    18/18    38    15/15   257    15/15   251    60/60     3    18/18    25
  HEURISTIC                      9/12    40     0/6    180     3/6    133    13/18    56    13/15    45    10/15    76    60/60     3    18/18    13
  ENUMERATE_VM                  12/12    52     6/6    480     0/6    726    18/18    40    15/15   257    15/15   248    60/60     3    18/18    25
  top1_001270f44949b659          2/12    27     0/6     30     0/6     30     2/18    27     2/15    27     3/15    26    59/60     5     2/18    28
  top2_72ebab0c37a15132          2/12    27     0/6     30     0/6     30     2/18    27     2/15    27     3/15    26    59/60     5     2/18    28
  top3_a505f68a42f0d912          2/12    27     0/6     30     0/6     30     2/18    27     2/15    27     3/15    26    59/60     5     2/18    28
  contemp_b3ee69958ceefe01       2/12    27     0/6     30     0/6     30     2/18    27     2/15    27     3/15    26    59/60     5     2/18    28
  ancestor147_it291_25a03c23     2/12    27     0/6     30     0/6     30     2/18    27     2/15    27     3/15    26    59/60     5     2/18    28
  ancestor74_it106_ea707bc8e     0/12    17     0/6     17     0/6     17     5/18    16     0/15    17     0/15    17    60/60     7     5/18    15
  contemp_8794a25070781bfc       0/12   120     0/6    800     0/6   1500     0/18   120     0/15   800     1/15   747    36/60    11     0/18   120
  RANDOM                         0/12   120     0/6    800     0/6   1500     0/18   120     0/15   800     0/15   800    10/60    15     0/18   120
  contemp_2ed27ecbecb125eb       0/12     8     0/6      8     0/6      8     3/18     7     0/15     8     2/15     8    20/60     6     0/18     8
  ancestor1_it0_575a54f23bb2     0/12     1     0/6      1     0/6      1     0/18     1     0/15     1     0/15     1     8/60     1     0/18     1

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  CACHE_REUSE                   85.56       --    93.37    85.56    93.37    93.37    93.37   0.0
  ADAPTIVE                     133.96   106.96   142.50   133.96   114.87   114.87   114.87  10.7
  ENUMERATE                    360.62       --   360.62   360.62   360.62   360.62   360.62   0.0
  HEURISTIC                     77.52       --    77.52    77.52    77.52    77.52    77.52   0.0
  ENUMERATE_VM                 299.08       --   299.08   299.08   299.08   299.08   299.08   0.0
  top1_001270f44949b659         28.57    26.01    28.57    28.57    27.83    27.83    27.83  31.7
  top2_72ebab0c37a15132         28.57    26.01    28.57    28.57    27.83    27.83    27.83  31.7
  top3_a505f68a42f0d912         28.57    26.01    28.57    28.57    27.83    27.83    27.83  31.7
  contemp_b3ee69958ceefe01      28.59    26.03    28.59    28.59    27.85    27.85    27.85  31.7
  ancestor147_it291_25a03c23    28.61    26.05    28.61    28.61    27.87    27.87    27.87  31.7
  ancestor74_it106_ea707bc8e    18.33       --    18.33    18.33    18.33    18.33    18.33   0.0
  contemp_8794a25070781bfc     765.86       --   765.86   765.86   765.86   765.86   765.86   0.0
  RANDOM                       733.93       --   733.93   733.93   733.93   733.93   733.93   0.0
  contemp_2ed27ecbecb125eb       8.30     8.30     8.30     8.30     8.30     8.30     8.30  27.3
  ancestor1_it0_575a54f23bb2     1.31       --     1.31     1.31     1.31     1.31     1.31   0.0

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
  top1_001270f44949b659
    0_competence_kept_ACC_ge_FRESH         1/3  successes ACC [25, 22, 23] vs FRESH [26, 22, 26]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [-30.6, -43.3, -66.7] vs 5% of FRESH cost [797.1, 860.6, 782.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [28.14, 29.91, 27.66] vs CODE_ONLY [27.14, 29.64, 26.71]
    4_scramble_or_reset_damages            0/3  eff ACC [0.628, 0.493, 0.552] SCR [0.649, 0.493, 0.552] RESET [0.609, 0.474, 0.604]
    5_transfers_to_fresh_copy              0/3  FULL [28.14, 29.91, 27.66] vs ACC remainder [28.14, 29.91, 27.66]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [25.3, 28.25, 24.48] vs ACC remainder [28.14, 29.91, 27.66]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [27.14, 29.64, 26.71] STORAGE_MATCHED [27.14, 29.64, 26.71] vs ACC remainder [28.14, 29.91, 27.66]
  top2_72ebab0c37a15132
    0_competence_kept_ACC_ge_FRESH         1/3  successes ACC [25, 22, 23] vs FRESH [26, 22, 26]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [-30.6, -43.3, -66.7] vs 5% of FRESH cost [797.1, 860.6, 782.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [28.14, 29.91, 27.66] vs CODE_ONLY [27.14, 29.64, 26.71]
    4_scramble_or_reset_damages            0/3  eff ACC [0.628, 0.493, 0.552] SCR [0.649, 0.493, 0.552] RESET [0.609, 0.474, 0.604]
    5_transfers_to_fresh_copy              0/3  FULL [28.14, 29.91, 27.66] vs ACC remainder [28.14, 29.91, 27.66]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [25.3, 28.25, 24.48] vs ACC remainder [28.14, 29.91, 27.66]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [27.14, 29.64, 26.71] STORAGE_MATCHED [27.14, 29.64, 26.71] vs ACC remainder [28.14, 29.91, 27.66]
  top3_a505f68a42f0d912
    0_competence_kept_ACC_ge_FRESH         1/3  successes ACC [25, 22, 23] vs FRESH [26, 22, 26]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [-30.6, -43.3, -66.7] vs 5% of FRESH cost [797.1, 860.6, 782.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [28.14, 29.91, 27.66] vs CODE_ONLY [27.14, 29.64, 26.71]
    4_scramble_or_reset_damages            0/3  eff ACC [0.628, 0.493, 0.552] SCR [0.649, 0.493, 0.552] RESET [0.609, 0.474, 0.604]
    5_transfers_to_fresh_copy              0/3  FULL [28.14, 29.91, 27.66] vs ACC remainder [28.14, 29.91, 27.66]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [25.3, 28.25, 24.48] vs ACC remainder [28.14, 29.91, 27.66]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [27.14, 29.64, 26.71] STORAGE_MATCHED [27.14, 29.64, 26.71] vs ACC remainder [28.14, 29.91, 27.66]
  contemp_b3ee69958ceefe01
    0_competence_kept_ACC_ge_FRESH         1/3  successes ACC [25, 22, 23] vs FRESH [26, 22, 26]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [-30.6, -43.3, -66.7] vs 5% of FRESH cost [797.6, 861.2, 783.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [28.16, 29.93, 27.68] vs CODE_ONLY [27.16, 29.66, 26.73]
    4_scramble_or_reset_damages            0/3  eff ACC [0.628, 0.493, 0.552] SCR [0.649, 0.493, 0.552] RESET [0.609, 0.474, 0.603]
    5_transfers_to_fresh_copy              0/3  FULL [28.16, 29.93, 27.68] vs ACC remainder [28.16, 29.93, 27.68]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [25.31, 28.27, 24.5] vs ACC remainder [28.16, 29.93, 27.68]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [27.16, 29.66, 26.73] STORAGE_MATCHED [27.16, 29.66, 26.73] vs ACC remainder [28.16, 29.93, 27.68]
  ancestor147_it291_25a03c23efa7b928
    0_competence_kept_ACC_ge_FRESH         1/3  successes ACC [25, 22, 23] vs FRESH [26, 22, 26]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [-30.6, -43.3, -66.7] vs 5% of FRESH cost [798.2, 861.8, 783.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [28.18, 29.95, 27.7] vs CODE_ONLY [27.18, 29.68, 26.74]
    4_scramble_or_reset_damages            0/3  eff ACC [0.628, 0.493, 0.552] SCR [0.649, 0.493, 0.552] RESET [0.609, 0.474, 0.603]
    5_transfers_to_fresh_copy              0/3  FULL [28.18, 29.95, 27.7] vs ACC remainder [28.18, 29.95, 27.7]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [25.33, 28.29, 24.52] vs ACC remainder [28.18, 29.95, 27.7]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [27.18, 29.68, 26.74] STORAGE_MATCHED [27.18, 29.68, 26.74] vs ACC remainder [28.18, 29.95, 27.7]
  ancestor74_it106_ea707bc8ec9c7a87
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [23, 23, 24] vs FRESH [23, 23, 24]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [532.6, 534.6, 528.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [18.33, 18.33, 18.33] vs CODE_ONLY [18.33, 18.33, 18.33]
    4_scramble_or_reset_damages            0/3  eff ACC [0.501, 0.479, 0.574] SCR [0.501, 0.479, 0.574] RESET [0.501, 0.48, 0.574]
    5_transfers_to_fresh_copy              0/3  FULL [18.33, 18.33, 18.33] vs ACC remainder [18.33, 18.33, 18.33]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [18.33, 18.33, 18.33]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [18.33, 18.33, 18.33] STORAGE_MATCHED [18.33, 18.33, 18.33] vs ACC remainder [18.33, 18.33, 18.33]
  contemp_8794a25070781bfc
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [15, 11, 11] vs FRESH [15, 11, 11]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [14761.3, 15618.7, 15618.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [734.1, 781.73, 781.73] vs CODE_ONLY [734.1, 781.73, 781.73]
    4_scramble_or_reset_damages            0/3  eff ACC [0.341, 0.289, 0.329] SCR [0.341, 0.289, 0.329] RESET [0.341, 0.289, 0.329]
    5_transfers_to_fresh_copy              0/3  FULL [734.1, 781.73, 781.73] vs ACC remainder [734.1, 781.73, 781.73]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [734.1, 781.73, 781.73]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [734.1, 781.73, 781.73] STORAGE_MATCHED [734.1, 781.73, 781.73] vs ACC remainder [734.1, 781.73, 781.73]
  RANDOM
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [3, 2, 5] vs FRESH [3, 2, 5]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [14665.2, 14665.2, 14665.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [733.93, 733.93, 733.93] vs CODE_ONLY [733.93, 733.93, 733.93]
    4_scramble_or_reset_damages            0/3  eff ACC [0.174, 0.191, 0.25] SCR [0.174, 0.191, 0.25] RESET [0.174, 0.191, 0.25]
    5_transfers_to_fresh_copy              0/3  FULL [733.93, 733.93, 733.93] vs ACC remainder [733.93, 733.93, 733.93]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [733.93, 733.93, 733.93]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [733.93, 733.93, 733.93] STORAGE_MATCHED [733.93, 733.93, 733.93] vs ACC remainder [733.93, 733.93, 733.93]
  contemp_2ed27ecbecb125eb
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [7, 8, 10] vs FRESH [7, 8, 10]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [243.0, 245.2, 243.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [8.26, 8.38, 8.26] vs CODE_ONLY [8.26, 8.38, 8.26]
    4_scramble_or_reset_damages            0/3  eff ACC [0.174, 0.174, 0.259] SCR [0.174, 0.174, 0.259] RESET [0.174, 0.174, 0.259]
    5_transfers_to_fresh_copy              0/3  FULL [8.26, 8.38, 8.26] vs ACC remainder [8.26, 8.38, 8.26]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [8.26, 8.38, 8.26] vs ACC remainder [8.26, 8.38, 8.26]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [8.26, 8.38, 8.26] STORAGE_MATCHED [8.26, 8.38, 8.26] vs ACC remainder [8.26, 8.38, 8.26]
  ancestor1_it0_575a54f23bb29d9d
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [4, 1, 3] vs FRESH [4, 1, 3]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [39.3, 39.3, 39.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1.31, 1.31, 1.31] vs CODE_ONLY [1.31, 1.31, 1.31]
    4_scramble_or_reset_damages            0/3  eff ACC [0.058, 0.04, 0.052] SCR [0.058, 0.04, 0.052] RESET [0.058, 0.04, 0.052]
    5_transfers_to_fresh_copy              0/3  FULL [1.31, 1.31, 1.31] vs ACC remainder [1.31, 1.31, 1.31]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1.31, 1.31, 1.31]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1.31, 1.31, 1.31] STORAGE_MATCHED [1.31, 1.31, 1.31] vs ACC remainder [1.31, 1.31, 1.31]

MACHINERY OF top1_001270f44949b659 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   0     0
    task  9:     0    0    0    0    0 |   0     0
    task 19:     0    0    0    0    0 |   0     0
    task 31:     0    0    0    0    0 |  31   688
    task 41:     0    0    0    0    0 |  32   696
    task 49:     0    0    0    0    0 |  32   696
  artifact events: 38 (create 35, delete 3, patch/append 0); invocations by block: {}; edges: 1
    block 3 origin=record len=10 state=[0, 0, 0] instr=[[19, 4, 0, 0], [19, 0, 0, 0], [19, 6, 0, 0], [19, 3, 0, 0], [19, 0, 0, 0], [19, 6, 0, 0]]
    block 4 origin=new len=0 state=[0, 0, 0] instr=[]
    block 5 origin=new len=0 state=[0, 0, 0] instr=[]
    block 6 origin=record len=10 state=[0, 0, 0] instr=[[19, 4, 0, 0], [19, 0, 0, 0], [19, 6, 0, 0], [19, 3, 0, 0], [19, 0, 0, 0], [19, 6, 0, 0]]
    block 7 origin=new len=0 state=[0, 0, 0] instr=[]
  adaptation curve ACC:   4 1 3 4 4 12 5 5 2 1 1 4 3 3 2 3 2 1 3 2 30 28 30 28 31 31 31 17 31 28 31 2 31 31 10 31 31 28 31 31 28 31 31 31 31 31 15 18 31 31
  adaptation curve FRESH: 4 1 3 4 4 12 5 5 2 1 1 4 3 3 2 3 2 1 3 2 29 29 29 29 29 23 29 17 17 29 29 29 29 29 7 29 29 29 29 29 29 29 29 29 29 29 15 15 29 29
  reuse_gain per task:    0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 -1 1 -1 1 -2 -8 -2 0 -14 1 -2 27 -2 -2 -3 -2 -2 1 -2 -2 1 -2 -2 -2 -2 -2 0 -3 -2 -2

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

