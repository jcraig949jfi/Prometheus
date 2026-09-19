CRIUS CAMPAIGN 0 REPORT  run=search_c0_seeded_s1  arm=seeded
code_commit=f4dae7a66 dirty=False config_hash=65fd4678cbcdd9c5 world=57065ca240cee53d partitions=ece4bd004beb4710
==============================================================================
SEARCH PROGRESS (fitness = C0_EFFICIENCY, mean over search seeds; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1   2.5012    1.8875         0.9044        48          2
    26   3.1943    3.1910         2.1006        55         17
    51   3.3147    3.3126         2.2939        51         38
    76   3.3175    3.3175         1.7054        34         65
   101   3.3252    3.3252         1.7717        28         91
   126   3.3252    3.3252         1.6977        23        116
   151   3.3442    3.3301         1.6484        21        144
   176   3.6172    3.6076         1.3961        28        170
   201   3.8986    3.8952         2.0454        23        186
   226   4.0526    4.0526         1.1066        25        203
   251   4.2160    4.2081         2.0287        25        222
   276   4.3203    4.2808         2.2605        26        233
   300   4.3403    4.3399         2.0748        24        242
  candidates evaluated: 7208   best_ever 4.3403 (cdc90b7185eeeeed)  wall 242s

BEST PROGRAM cdc90b7185eeeeed (len 24, iteration 299, modification delete@19)
  search seed 101: eff 4.4128 succ 6/50 inter 149 steps 1200 ws_cost 718 blocks 33 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [0.638, 0.3], "B": [0.22, 0.0], "C": [0.746, 0.083], "D": [8.557, 0.1], "E": [8.135, 0.125]}
  search seed 102: eff 4.2679 succ 5/50 inter 148 steps 1198 ws_cost 719 blocks 34 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [0.537, 0.2], "B": [0.22, 0.0], "C": [0.746, 0.083], "D": [8.557, 0.1], "E": [8.135, 0.125]}
  listing:
      0  INPUT          R1, num_ops
      1  BLK_DELETE     R5
      2  CONST          R5, 1
      3  BLK_NEW        R0
      4  BLK_COMPOSE    R3, R3, R6
      5  ADD            R0, R0, R5
      6  EQ             R3, R6, R4
      7  LT             R3, R0, R2
      8  BLK_COMPOSE    R4, R3, R6
      9  MOV            R2, R1
     10  LT             R3, R0, R2
     11  BRZ            R3, 24
     12  ACT            R0
     13  ACT            R1
     14  ADD            R0, R0, R5
     15  BLK_COPY       R4, R7
     16  ACT            R0
     17  BLK_DELETE     R4
     18  ADD            R0, R0, R5
     19  ACT            R0
     20  JMP            10
     21  MOV            R7, R4
     22  BLK_PATCH      R7, R1, R2
     23  BLK_LEN        R2, R5
  ancestry (122 steps, newest first): iteration/fitness/modification
    it  299  4.3403  len 24  delete@19
    it  295  4.3338  len 25  insert@6
    it  291  4.3399  len 24  delete@17
    it  281  4.3333  len 25  delete@16
    it  271  4.3203  len 26  arg@25.0
    it  270  4.3203  len 26  duplicate@10+2->20+insert@23
    it  262  4.2214  len 23  arg@1.0
    it  259  4.2214  len 23  delete@23
    it  258  4.2214  len 24  swap@4,5
    it  256  4.2214  len 24  delete@5
    it  252  4.2089  len 25  delete@23
    it  245  4.2089  len 26  duplicate@1+2->18
    it  244  4.1668  len 24  arg@20.1
    it  239  4.1668  len 24  insert@1
    it  232  4.0526  len 23  delete@23+delete@20
    ... 108 more

QUALIFICATION suite=heldout_v1 seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED)
  player                        effA    effF    effR    effS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  contemp_4d45fc483d73e715     4.259   2.257   0.984   4.259   1.7  11.3       96      224     141.5   34.3    0.0
  top1_cdc90b7185eeeeed        3.881   2.019   0.934   3.881   2.0  16.0      154      329     186.5   34.3    0.0
  top2_4e17d0fff66a93db        3.880   2.018   0.935   3.880   2.0  16.0      154      329     187.1   34.3    0.0
  top3_80aa5f6e15f492c5        3.880   2.018   0.935   3.880   2.0  16.0      154      329     187.1   34.3    0.0
  ancestor122_it295_8ec53c1e   3.875   2.018   0.934   3.875   2.0  16.0      154      329     187.1   34.3    0.0
  contemp_56fb00956890118e     3.855   2.014   0.934   3.855   2.0  16.0      154      329     189.0   34.3    0.0
  ancestor62_it102_b8edce073   3.667   3.049   2.096   3.667   5.3  17.3      200      213      12.1   32.0    0.0
  CACHE_REUSE                  2.965   1.575   2.878   1.620  50.0  49.0     1332     6917    5315.7    0.0    0.0
  HEURISTIC                    2.245   2.245   2.245   2.245  42.0  42.0     1874     1874       0.0    0.0    0.0
  contemp_1d10daaeebe9997f     2.011   2.018   2.018   2.011  16.0  16.0      329      329       2.2   34.3    0.0
  ADAPTIVE                     1.972   1.561   2.644   1.417  50.0  49.0     1332     6917    4436.4   27.7    8.7
  ENUMERATE                    1.635   1.635   1.635   1.635  49.0  49.0     6917     6917       0.0    0.0    0.0
  ancestor1_it0_0875253d162c   1.601   1.601   1.601   1.601  48.0  48.0     5611     5611       0.0    0.0    0.0
  ENUMERATE_VM                 1.601   1.601   1.601   1.601  48.0  48.0     5611     5611       0.0    0.0    0.0
  RANDOM                       0.205   0.205   0.205   0.205   3.3   3.3    14823    14823       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  contemp_4d45fc483d73e715      0.48/   4.41    0.22/   4.92    0.58/   5.17    5.67/   5.72    5.67/   5.62
  top1_cdc90b7185eeeeed         0.68/   6.07    0.22/   5.32    0.78/   7.83    8.63/   8.43    8.67/   8.54
  top2_4e17d0fff66a93db         0.68/   6.08    0.21/   5.32    0.77/   7.85    8.65/   8.45    8.69/   8.56
  top3_80aa5f6e15f492c5         0.68/   6.08    0.21/   5.32    0.77/   7.85    8.65/   8.45    8.69/   8.56
  ancestor122_it295_8ec53c1e    0.69/   6.09    0.22/   5.33    0.78/   7.86    8.66/   8.46    8.70/   8.57
  contemp_56fb00956890118e      0.68/   6.14    0.21/   5.38    0.78/   7.93    8.74/   8.54    8.78/   8.65
  ancestor62_it102_b8edce073    0.83/   3.76    1.63/   3.12    6.52/   5.45    6.52/   5.45    6.52/   5.45
  CACHE_REUSE                   9.89/   4.29    8.07/   4.36    2.65/  33.14    6.18/ 259.04  184.78/ 499.06
  HEURISTIC                     3.48/   3.48    3.54/   3.54   34.80/  34.80   60.61/  60.61   98.65/  98.65
  contemp_1d10daaeebe9997f      6.04/   6.08    5.29/   5.32    7.80/   7.85    8.40/   8.45    8.51/   8.56
  ADAPTIVE                     11.56/   4.83    9.37/   4.90    3.24/  33.74   10.51/ 259.64  288.27/ 499.66
  ENUMERATE                     3.48/   3.48    3.54/   3.54   31.87/  31.87  255.22/ 255.22  492.37/ 492.37
  ancestor1_it0_0875253d162c    3.72/   3.72    3.79/   3.79   34.59/  34.59  264.39/ 264.39  342.45/ 342.45
  ENUMERATE_VM                  3.72/   3.72    3.79/   3.79   34.59/  34.59  264.39/ 264.39  342.45/ 342.45
  RANDOM                       15.89/  15.89   14.75/  14.75  121.20/ 121.20  808.00/ 808.00  641.35/ 641.35

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                      absent_op5_d2  absent_op5_d3         depth4   heldout_pair heldout_triple new_combinatio      primitive  reversed_pair
  contemp_4d45fc483d73e715       0/12     5     0/6      5     0/6      5     0/18     1     0/15     5     0/15     5     4/60     0     1/18     0
  top1_cdc90b7185eeeeed          0/12     8     0/6      8     0/6      8     0/18     1     0/15     8     1/15     8     4/60     0     1/18     0
  top2_4e17d0fff66a93db          0/12     8     0/6      8     0/6      8     0/18     1     0/15     8     1/15     8     4/60     0     1/18     0
  top3_80aa5f6e15f492c5          0/12     8     0/6      8     0/6      8     0/18     1     0/15     8     1/15     8     4/60     0     1/18     0
  ancestor122_it295_8ec53c1e     0/12     8     0/6      8     0/6      8     0/18     1     0/15     8     1/15     8     4/60     0     1/18     0
  contemp_56fb00956890118e       0/12     8     0/6      8     0/6      8     0/18     1     0/15     8     1/15     8     4/60     0     1/18     0
  ancestor62_it102_b8edce073     0/12     6     0/6      6     0/6      6     0/18     6     0/15     6     0/15     6    16/60     1     0/18     6
  CACHE_REUSE                   12/12    58     6/6    496     6/6      4    18/18     2    15/15     3    15/15     3    60/60     2    18/18     2
  HEURISTIC                      9/12    40     0/6    180     3/6    133    13/18    56    13/15    45    10/15    76    60/60     3    18/18    13
  contemp_1d10daaeebe9997f       2/12     8     0/6      8     0/6      8     0/18     8     0/15     8     2/15     7    38/60     5     6/18     6
  ADAPTIVE                      12/12    58     6/6    496     6/6      4    18/18     2    15/15     3    15/15     3    60/60     2    18/18     2
  ENUMERATE                     12/12    58     6/6    496     3/6   1350    18/18    38    15/15   257    15/15   251    60/60     3    18/18    25
  ancestor1_it0_0875253d162c    12/12    52     6/6    480     0/6    726    18/18    40    15/15   257    15/15   248    60/60     3    18/18    25
  ENUMERATE_VM                  12/12    52     6/6    480     0/6    726    18/18    40    15/15   257    15/15   248    60/60     3    18/18    25
  RANDOM                         0/12   120     0/6    800     0/6   1500     0/18   120     0/15   800     0/15   800    10/60    15     0/18   120

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  contemp_4d45fc483d73e715       5.67     0.22     5.67     5.67     0.53     0.53     0.53  32.0
  top1_cdc90b7185eeeeed          8.65     0.22     8.65     8.65     0.69     0.69     0.69  32.0
  top2_4e17d0fff66a93db          8.67     0.21     8.67     8.67     0.68     0.68     0.68  32.0
  top3_80aa5f6e15f492c5          8.67     0.21     8.67     8.67     0.68     0.68     0.68  32.0
  ancestor122_it295_8ec53c1e     8.68     0.22     8.68     8.68     0.69     0.69     0.69  32.0
  contemp_56fb00956890118e       8.76     0.21     8.76     8.76     0.69     0.69     0.69  32.0
  ancestor62_it102_b8edce073     6.52     0.15     6.52     6.52     1.40     1.40     1.40  32.0
  CACHE_REUSE                   85.56       --    93.37    85.56    93.37    93.37    93.37   0.0
  HEURISTIC                     77.52       --    77.52    77.52    77.52    77.52    77.52   0.0
  contemp_1d10daaeebe9997f       8.45     8.45     8.45     8.45     8.45     8.45     8.45  32.0
  ADAPTIVE                     133.96   106.96   142.50   133.96   114.87   114.87   114.87  10.7
  ENUMERATE                    360.62       --   360.62   360.62   360.62   360.62   360.62   0.0
  ancestor1_it0_0875253d162c   299.08       --   299.08   299.08   299.08   299.08   299.08   0.0
  ENUMERATE_VM                 299.08       --   299.08   299.08   299.08   299.08   299.08   0.0
  RANDOM                       733.93       --   733.93   733.93   733.93   733.93   733.93   0.0

CHARTER s13 CHECKLIST (seeds passing / seeds; thresholds: 5 percent relative; guard 0 added 2026-09-19, see report.py)
  contemp_4d45fc483d73e715
    0_competence_kept_ACC_ge_FRESH         0/3  successes ACC [2, 1, 2] vs FRESH [13, 10, 11]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [51.5, 54.8, 59.1] vs 5% of FRESH cost [161.7, 165.0, 166.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [5.67, 5.67, 5.67] vs CODE_ONLY [0.53, 0.53, 0.53]
    4_scramble_or_reset_damages            0/3  eff ACC [4.046, 2.968, 5.763] SCR [4.046, 2.968, 5.763] RESET [1.221, 0.561, 1.17]
    5_transfers_to_fresh_copy              0/3  FULL [5.67, 5.67, 5.67] vs ACC remainder [5.67, 5.67, 5.67]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [0.22, 0.22, 0.22] vs ACC remainder [5.67, 5.67, 5.67]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [0.53, 0.53, 0.53] STORAGE_MATCHED [0.53, 0.53, 0.53] vs ACC remainder [5.67, 5.67, 5.67]
  top1_cdc90b7185eeeeed
    0_competence_kept_ACC_ge_FRESH         0/3  successes ACC [2, 2, 2] vs FRESH [19, 14, 15]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [74.2, 80.7, 90.1] vs 5% of FRESH cost [241.4, 246.7, 252.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [8.67, 8.61, 8.67] vs CODE_ONLY [0.69, 0.69, 0.69]
    4_scramble_or_reset_damages            0/3  eff ACC [3.552, 3.053, 5.037] SCR [3.552, 3.053, 5.037] RESET [1.1, 0.666, 1.037]
    5_transfers_to_fresh_copy              0/3  FULL [8.67, 8.61, 8.67] vs ACC remainder [8.67, 8.61, 8.67]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [0.22, 0.22, 0.22] vs ACC remainder [8.67, 8.61, 8.67]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [0.69, 0.69, 0.69] STORAGE_MATCHED [0.69, 0.69, 0.69] vs ACC remainder [8.67, 8.61, 8.67]
  top2_4e17d0fff66a93db
    0_competence_kept_ACC_ge_FRESH         0/3  successes ACC [2, 2, 2] vs FRESH [19, 14, 15]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [74.5, 80.9, 90.4] vs 5% of FRESH cost [241.9, 247.2, 252.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [8.69, 8.63, 8.69] vs CODE_ONLY [0.68, 0.68, 0.68]
    4_scramble_or_reset_damages            0/3  eff ACC [3.551, 3.052, 5.036] SCR [3.551, 3.052, 5.036] RESET [1.101, 0.667, 1.038]
    5_transfers_to_fresh_copy              0/3  FULL [8.69, 8.63, 8.69] vs ACC remainder [8.69, 8.63, 8.69]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [0.21, 0.21, 0.21] vs ACC remainder [8.69, 8.63, 8.69]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [0.68, 0.68, 0.68] STORAGE_MATCHED [0.68, 0.68, 0.68] vs ACC remainder [8.69, 8.63, 8.69]
  top3_80aa5f6e15f492c5
    0_competence_kept_ACC_ge_FRESH         0/3  successes ACC [2, 2, 2] vs FRESH [19, 14, 15]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [74.5, 80.9, 90.4] vs 5% of FRESH cost [241.9, 247.2, 252.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [8.69, 8.63, 8.69] vs CODE_ONLY [0.68, 0.68, 0.68]
    4_scramble_or_reset_damages            0/3  eff ACC [3.551, 3.052, 5.036] SCR [3.551, 3.052, 5.036] RESET [1.101, 0.667, 1.038]
    5_transfers_to_fresh_copy              0/3  FULL [8.69, 8.63, 8.69] vs ACC remainder [8.69, 8.63, 8.69]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [0.21, 0.21, 0.21] vs ACC remainder [8.69, 8.63, 8.69]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [0.68, 0.68, 0.68] STORAGE_MATCHED [0.68, 0.68, 0.68] vs ACC remainder [8.69, 8.63, 8.69]
  ancestor122_it295_8ec53c1e4dcb575f
    0_competence_kept_ACC_ge_FRESH         0/3  successes ACC [2, 2, 2] vs FRESH [19, 14, 15]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [74.5, 80.9, 90.4] vs 5% of FRESH cost [242.2, 247.5, 252.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [8.7, 8.64, 8.7] vs CODE_ONLY [0.69, 0.69, 0.69]
    4_scramble_or_reset_damages            0/3  eff ACC [3.546, 3.048, 5.029] SCR [3.546, 3.048, 5.029] RESET [1.099, 0.665, 1.037]
    5_transfers_to_fresh_copy              0/3  FULL [8.7, 8.64, 8.7] vs ACC remainder [8.7, 8.64, 8.7]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [0.22, 0.22, 0.22] vs ACC remainder [8.7, 8.64, 8.7]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [0.69, 0.69, 0.69] STORAGE_MATCHED [0.69, 0.69, 0.69] vs ACC remainder [8.7, 8.64, 8.7]
  contemp_56fb00956890118e
    0_competence_kept_ACC_ge_FRESH         0/3  successes ACC [2, 2, 2] vs FRESH [19, 14, 15]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [75.2, 81.8, 91.4] vs 5% of FRESH cost [244.3, 249.7, 255.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [8.78, 8.71, 8.78] vs CODE_ONLY [0.69, 0.69, 0.69]
    4_scramble_or_reset_damages            0/3  eff ACC [3.528, 3.033, 5.004] SCR [3.528, 3.033, 5.004] RESET [1.1, 0.666, 1.037]
    5_transfers_to_fresh_copy              0/3  FULL [8.78, 8.71, 8.78] vs ACC remainder [8.78, 8.71, 8.78]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [0.21, 0.21, 0.21] vs ACC remainder [8.78, 8.71, 8.78]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [0.69, 0.69, 0.69] STORAGE_MATCHED [0.69, 0.69, 0.69] vs ACC remainder [8.78, 8.71, 8.78]
  ancestor62_it102_b8edce073289a72f
    0_competence_kept_ACC_ge_FRESH         0/3  successes ACC [5, 5, 6] vs FRESH [16, 19, 17]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [-32.1, -32.1, -32.1] vs 5% of FRESH cost [163.5, 163.5, 163.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [6.52, 6.52, 6.52] vs CODE_ONLY [1.4, 1.4, 1.4]
    4_scramble_or_reset_damages            0/3  eff ACC [3.653, 3.177, 4.171] SCR [3.653, 3.177, 4.171] RESET [2.233, 1.941, 2.114]
    5_transfers_to_fresh_copy              0/3  FULL [6.52, 6.52, 6.52] vs ACC remainder [6.52, 6.52, 6.52]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [0.15, 0.15, 0.15] vs ACC remainder [6.52, 6.52, 6.52]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1.4, 1.4, 1.4] STORAGE_MATCHED [1.4, 1.4, 1.4] vs ACC remainder [6.52, 6.52, 6.52]
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
  contemp_1d10daaeebe9997f
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 14, 15] vs FRESH [19, 14, 15]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [1.4, 1.4, 1.5] vs 5% of FRESH cost [241.9, 247.2, 252.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [8.45, 8.45, 8.45] vs CODE_ONLY [8.45, 8.45, 8.45]
    4_scramble_or_reset_damages            0/3  eff ACC [2.19, 1.861, 1.983] SCR [2.19, 1.861, 1.983] RESET [2.197, 1.867, 1.99]
    5_transfers_to_fresh_copy              0/3  FULL [8.45, 8.45, 8.45] vs ACC remainder [8.45, 8.45, 8.45]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [8.45, 8.45, 8.45] vs ACC remainder [8.45, 8.45, 8.45]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [8.45, 8.45, 8.45] STORAGE_MATCHED [8.45, 8.45, 8.45] vs ACC remainder [8.45, 8.45, 8.45]
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

MACHINERY OF top1_cdc90b7185eeeeed (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   3    24
    task  9:     0    0    0    0    0 |  11    88
    task 19:     0    0    0    0    0 |  21   168
    task 31:     0    0    0    0    0 |  32   256
    task 41:     0    0    0    0    0 |  32   256
    task 49:     0    0    0    0    0 |  32   256
  artifact events: 36 (create 34, delete 2, patch/append 0); invocations by block: {}; edges: 5
    block 1 origin=compose len=0 state=[0, 0, 0] instr=[]
    block 2 origin=compose len=0 state=[0, 0, 0] instr=[]
    block 4 origin=new len=0 state=[0, 0, 0] instr=[]
    block 5 origin=new len=0 state=[0, 0, 0] instr=[]
    block 6 origin=new len=0 state=[0, 0, 0] instr=[]
  adaptation curve ACC:   2 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 9 9 9 9 9 9 9 9 9 9 9 9 9 9 9 9 9 9 9
  adaptation curve FRESH: 2 9 1 2 2 9 6 6 9 9 9 2 1 1 9 1 9 9 1 9 3 9 9 9 9 9 3 9 9 3 9 9 9 9 9 9 9 4 9 9 9 9 9 9 9 9 9 9 9 9
  reuse_gain per task:    0 6 1 2 2 8 5 5 8 8 8 2 1 1 8 1 8 8 1 8 3 8 8 8 8 8 3 8 8 3 8 0 0 0 0 0 0 -4 0 0 0 0 0 0 0 0 0 0 0 0

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

