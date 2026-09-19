CRIUS CAMPAIGN 0 REPORT  run=search_c2a_random_s3  arm=random
code_commit=96d299784 dirty=True config_hash=401915ec4da9443a world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1   1.1788    0.9247         0.4877        12          3
    26   2.6953    2.2507         0.9436         4         32
    51   4.2165    2.7524         1.0146         8         60
    76   2.6992    2.3807         1.5753        13        148
   101   3.2021    2.6245         1.7778        24        232
   126   5.2173    4.7623         4.0180        26        308
   151   8.7817    7.9560         4.2079        48        396
   176   7.2514    4.6370         3.1151        78        488
   201   8.2652    5.9707         4.7997        70        587
   226   7.7444    6.7295         4.8328        94        696
   251   6.7185    3.5649         2.3208        96        787
   276   7.2523    6.1092         5.0885        95        878
   300   5.7157    5.2676         3.7493        96        972
  candidates evaluated: 7208   best_ever 14.3046 (56c0341b3019cad4)  wall 972s

BEST PROGRAM 56c0341b3019cad4 (len 27, iteration 121, modification const@20+replace@26+arg@17.0)
  search seed 3011210: fit 1.1560 succ 1/50 inter 41476 steps 72898 ws_cost 10533 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [2040.05, 0.0], "B": [2040.05, 0.0], "C": [51.05, 0.0], "D": [48.831, 0.1], "E": [51.05, 0.0]}
  search seed 3011211: fit 5.2057 succ 5/50 inter 35477 steps 63202 ws_cost 9147 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [1836.585, 0.1], "B": [1639.648, 0.2], "C": [43.272, 0.167], "D": [51.05, 0.0], "E": [51.05, 0.0]}
  listing:
      0  VLEN           R3, R5
      1  BLK_STATE_SET  R7, R1, R1
      2  BLK_DELETE     R6
      3  WS_FREE        R3
      4  ACTI           6
      5  ACTI           7
      6  BLK_PATCH      R1, R1, R5
      7  ACTI           0
      8  ACTI           7
      9  VSET           R2, R7, R5
     10  BRZ            R0, 4
     11  BLK_PATCH      R5, R1, R3
     12  ACTI           -3
     13  ACTI           8
     14  WS_SREAD       R0, R3, R3
     15  WS_APPEND      R6, R4
     16  MOV            R2, R2
     17  BRZ            R4, 4
     18  BLK_PATCH      R5, R1, R3
     19  ACTI           -3
     20  ACTI           7
     21  WS_APPEND      R6, R4
     22  ACTI           8
     23  WS_APPEND      R6, R4
     24  BLK_DELETE     R0
     25  WS_LINK        R0, R3, R0
     26  ACTI           6
  ancestry (72 steps, newest first): iteration/fitness/modification
    it  121  3.1808  len 27  const@20+replace@26+arg@17.0
    it  120  2.1646  len 27  insert@2+swap@9,24+replace@14
    it  119  2.6964  len 26  const@18+insert@13+delete@21
    it  118  3.6885  len 26  delete@15+delete@5
    it  117  1.6618  len 28  replace@15
    it  116  5.6950  len 28  insert@13+duplicate@12+5->10
    it  115  3.1926  len 22  duplicate@14+3->14
    it  114  2.6844  len 19  insert@20+delete@7+delete@17
    it  113  5.7410  len 20  arg@7.0+insert@12
    it  112  4.7169  len 19  delete@7+replace@16+delete@7
    it  110  3.7012  len 21  swap@17,14+arg@11.0+delete@6
    it  108  4.1935  len 22  insert@16
    it  107  1.6535  len 21  arg@17.0+arg@14.0
    it  106  3.1784  len 21  insert@0+swap@8,3
    it  105  3.1943  len 20  arg@16.0+delete@5
    ... 58 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7316.0    4.3   74.7
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.3    2.7    1.7
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       0.0    0.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0
  ancestor186_it299_b292e46d   3.857   3.857   3.857   3.857   3.7   3.7    35688    35688       0.0    0.0    0.0
  top1_137c1619929b95ec        3.515   3.515   3.515   3.515   3.3   3.3    36670    36670       0.0    0.0    0.0
  contemp_cb9ab5b10c09f06f     3.190   3.190   3.190   3.190   3.0   3.0    35716    35716       0.0    0.0    0.0
  top2_3218f89f522a8bd2        2.833   2.833   2.833   2.833   2.7   2.7    38349    38349       0.0    0.0    0.0
  top3_dcd4068516cd5882        2.833   2.833   2.833   2.833   2.7   2.7    38349    38349       0.0    0.0    0.0
  bestever_56c0341b3019cad4    2.522   2.522   2.522   2.522   2.3   2.3    37533    37533       0.0    0.0    0.0
  contemp_0b12c4e690262b9d     2.495   2.495   2.495   2.495   2.3   2.3    38853    38853       0.0    0.0    0.0
  contemp_9a5784449db2a473     2.160   2.160   2.160   2.160   2.0   2.0    38917    38917       0.0    0.0    0.0
  ancestor94_it154_8d7fcd786   1.158   1.158   1.158   1.158   1.0   1.0    40355    40355       0.0    0.0    0.0
  ancestor1_it0_085e5a21a759   0.163   0.163   0.163   0.163   0.0   0.0        0        0       0.0   32.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.00/ 455.13   14.90/ 539.10   21.11/  47.94   33.21/  48.94   40.07/  50.52
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.13/ 443.81  528.11/ 527.79   47.93/  47.89   48.85/  48.88   50.42/  50.46
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ENUMERATE_VM_C1             495.80/ 495.80  525.01/ 525.01   50.10/  50.10   51.09/  51.09   52.68/  52.68
  RANDOM_C1                  1662.62/1662.62 1627.07/1627.07   50.50/  50.50   50.50/  50.50   48.56/  48.56
  ancestor186_it299_b292e46d 1922.96/1922.96 1728.02/1728.02   52.42/  52.42   52.16/  52.16   53.19/  53.19
  top1_137c1619929b95ec      1803.26/1803.26 1952.94/1952.94   51.08/  51.08   53.19/  53.19   53.19/  53.19
  contemp_cb9ab5b10c09f06f   1862.34/1862.34 1794.56/1794.56   53.42/  53.42   53.42/  53.42   53.42/  53.42
  top2_3218f89f522a8bd2      1937.54/1937.54 2003.60/2003.60   52.27/  52.27   52.62/  52.62   53.41/  53.41
  top3_dcd4068516cd5882      1938.67/1938.67 2004.77/2004.77   52.30/  52.30   52.66/  52.66   53.45/  53.45
  bestever_56c0341b3019cad4  1838.52/1838.52 1838.79/1838.79   51.05/  51.05   51.05/  51.05   49.40/  49.40
  contemp_0b12c4e690262b9d   2074.31/2074.31 1935.77/1935.77   52.64/  52.64   52.62/  52.62   52.19/  52.19
  contemp_9a5784449db2a473   2011.29/2011.29 2015.09/2015.09   52.50/  52.50   52.50/  52.50   53.61/  53.61
  ancestor94_it154_8d7fcd786 2028.81/2028.81 2028.81/2028.81   50.81/  50.81   52.11/  52.11   52.11/  52.11
  ancestor1_it0_085e5a21a759 2000.08/2000.08 2000.08/2000.08   50.08/  50.08   50.08/  50.08   50.08/  50.08

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610
  ancestor186_it299_b292e46d     1/36    49     1/30    49     0/12    50     0/12    50     3/30  1802     6/30  1619
  top1_137c1619929b95ec          2/36    48     0/30    50     0/12    50     0/12    50     5/30  1690     3/30  1830
  contemp_cb9ab5b10c09f06f       0/36    50     0/30    50     0/12    50     0/12    50     4/30  1743     5/30  1679
  top2_3218f89f522a8bd2          2/36    49     1/30    49     0/12    50     0/12    50     3/30  1813     2/30  1875
  top3_dcd4068516cd5882          2/36    49     1/30    49     0/12    50     0/12    50     3/30  1813     2/30  1875
  bestever_56c0341b3019cad4      0/36    50     0/30    50     0/12    50     1/12    47     3/30  1802     3/30  1802
  contemp_0b12c4e690262b9d       1/36    49     1/30    49     1/12    47     0/12    50     1/30  1934     3/30  1805
  contemp_9a5784449db2a473       1/36    49     1/30    49     0/12    50     0/12    50     2/30  1870     2/30  1874
  ancestor94_it154_8d7fcd786     1/36    49     0/30    50     0/12    50     0/12    50     1/30  1944     1/30  1944
  ancestor1_it0_085e5a21a759     0/36     0     0/30     0     0/12     0     0/12     0     0/30     0     0/30     0

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.26    49.53    36.26    36.26    49.53    49.53    49.53   4.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.55    49.55    49.55    49.55    49.55    49.55    49.55   1.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ENUMERATE_VM_C1               51.80       --    51.80    51.80    51.80    51.80    51.80   0.0
  RANDOM_C1                     49.64       --    49.64    49.64    49.64    49.64    49.64   0.0
  ancestor186_it299_b292e46d    52.62       --    52.62    52.62    52.62    52.62    52.62   0.0
  top1_137c1619929b95ec         53.19       --    53.19    53.19    53.19    53.19    53.19   0.0
  contemp_cb9ab5b10c09f06f      53.42       --    53.42    53.42    53.42    53.42    53.42   0.0
  top2_3218f89f522a8bd2         52.97       --    52.97    52.97    52.97    52.97    52.97   0.0
  top3_dcd4068516cd5882         53.01       --    53.01    53.01    53.01    53.01    53.01   0.0
  bestever_56c0341b3019cad4     50.32       --    50.32    50.32    50.32    50.32    50.32   0.0
  contemp_0b12c4e690262b9d      52.43       --    52.43    52.43    52.43    52.43    52.43   0.0
  contemp_9a5784449db2a473      52.99       --    52.99    52.99    52.99    52.99    52.99   0.0
  ancestor94_it154_8d7fcd786    52.11       --    52.11    52.11    52.11    52.11    52.11   0.0
  ancestor1_it0_085e5a21a759    50.08    50.08    50.08    50.08    50.08    50.08    50.08  32.0

CHARTER s13 CHECKLIST (seeds passing / seeds; thresholds: 5 percent relative; guard 0 added 2026-09-19, see report.py)
  PROCEDURE_REUSE_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [48, 48, 41] vs FRESH [20, 19, 22]
    1_cost_declines_via_accumulation       3/3  reuse_gain C-E per seed [736.2, 717.2, 235.3] vs 5% of FRESH cost [1515.6, 1467.2, 1423.8] (and 0 held)
    2_reproduces_on_heldout                3/3  same test, qualification suite; seeds passing = 3/3
    3_state_causal_FULL_vs_CODE_ONLY       2/3  remainder mean cost FULL [30.57, 30.13, 48.08] vs CODE_ONLY [50.41, 50.41, 47.78]
    4_scramble_or_reset_damages            3/3  eff ACC [48.449, 48.475, 41.476] SCR [20.443, 21.469, 22.474] RESET [20.443, 21.469, 22.475]
    5_transfers_to_fresh_copy              2/3  FULL [30.57, 30.13, 48.08] vs ACC remainder [30.57, 30.13, 48.08]
    6_executable_components_reused         2/3  invocations [82, 81, 61]; ABLATION_ALL cost [50.41, 50.41, 47.78] vs ACC remainder [30.57, 30.13, 48.08]
    7_not_compute_or_storage               2/3  COMPUTE_MATCHED [50.41, 50.41, 47.78] STORAGE_MATCHED [50.41, 50.41, 47.78] vs ACC remainder [30.57, 30.13, 48.08]
  ENUMERATE_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 19, 22] vs FRESH [20, 19, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1509.3, 1461.0, 1417.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.31, 50.31, 47.68] vs CODE_ONLY [50.31, 50.31, 47.68]
    4_scramble_or_reset_damages            0/3  eff ACC [20.373, 19.411, 22.449] SCR [20.373, 19.411, 22.449] RESET [20.373, 19.411, 22.449]
    5_transfers_to_fresh_copy              0/3  FULL [50.31, 50.31, 47.68] vs ACC remainder [50.31, 50.31, 47.68]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.31, 50.31, 47.68]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.31, 50.31, 47.68] STORAGE_MATCHED [50.31, 50.31, 47.68] vs ACC remainder [50.31, 50.31, 47.68]
  TABLE_MEMO_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 19, 22] vs FRESH [20, 19, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [-12.0, -11.4, -12.6] vs 5% of FRESH cost [1509.3, 1461.0, 1417.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.71, 50.69, 48.12] vs CODE_ONLY [50.31, 50.31, 47.7]
    4_scramble_or_reset_damages            0/3  eff ACC [20.372, 19.411, 22.449] SCR [20.372, 19.411, 22.449] RESET [20.373, 19.411, 22.449]
    5_transfers_to_fresh_copy              0/3  FULL [50.71, 50.69, 48.12] vs ACC remainder [50.71, 50.69, 48.12]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.71, 50.69, 48.12]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.31, 50.31, 47.7] STORAGE_MATCHED [50.31, 50.31, 47.7] vs ACC remainder [50.71, 50.69, 48.12]
  PROCEDURE_NOCAL_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 19, 22] vs FRESH [20, 19, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [1.2, -1.6, 0.8] vs 5% of FRESH cost [1513.8, 1465.5, 1422.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.42, 50.42, 47.8] vs CODE_ONLY [50.42, 50.42, 47.8]
    4_scramble_or_reset_damages            0/3  eff ACC [20.37, 19.409, 22.447] SCR [20.37, 19.409, 22.447] RESET [20.37, 19.409, 22.447]
    5_transfers_to_fresh_copy              0/3  FULL [50.42, 50.42, 47.8] vs ACC remainder [50.42, 50.42, 47.8]
    6_executable_components_reused         0/3  invocations [3, 1, 1]; ABLATION_ALL cost [50.42, 50.42, 47.8] vs ACC remainder [50.42, 50.42, 47.8]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.42, 50.42, 47.8] STORAGE_MATCHED [50.42, 50.42, 47.8] vs ACC remainder [50.42, 50.42, 47.8]
  QUIT_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 18, 20] vs FRESH [20, 18, 20]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1500.0, 1500.0, 1500.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.0, 50.0, 50.0] vs CODE_ONLY [50.0, 50.0, 50.0]
    4_scramble_or_reset_damages            0/3  eff ACC [20.373, 18.411, 20.449] SCR [20.373, 18.411, 20.449] RESET [20.373, 18.411, 20.449]
    5_transfers_to_fresh_copy              0/3  FULL [50.0, 50.0, 50.0] vs ACC remainder [50.0, 50.0, 50.0]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.0, 50.0, 50.0]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.0, 50.0, 50.0] STORAGE_MATCHED [50.0, 50.0, 50.0] vs ACC remainder [50.0, 50.0, 50.0]
  ENUMERATE_VM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 18, 22] vs FRESH [18, 18, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1580.4, 1531.9, 1488.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.68, 52.68, 50.04] vs CODE_ONLY [52.68, 52.68, 50.04]
    4_scramble_or_reset_damages            0/3  eff ACC [18.368, 18.4, 22.445] SCR [18.368, 18.4, 22.445] RESET [18.368, 18.4, 22.445]
    5_transfers_to_fresh_copy              0/3  FULL [52.68, 52.68, 50.04] vs ACC remainder [52.68, 52.68, 50.04]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.68, 52.68, 50.04]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.68, 52.68, 50.04] STORAGE_MATCHED [52.68, 52.68, 50.04] vs ACC remainder [52.68, 52.68, 50.04]
  RANDOM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 6, 9] vs FRESH [6, 6, 9]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1493.8, 1515.0, 1489.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.32, 50.5, 49.1] vs CODE_ONLY [49.32, 50.5, 49.1]
    4_scramble_or_reset_damages            0/3  eff ACC [6.205, 6.235, 9.221] SCR [6.205, 6.235, 9.221] RESET [6.205, 6.235, 9.221]
    5_transfers_to_fresh_copy              0/3  FULL [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.32, 50.5, 49.1]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.32, 50.5, 49.1] STORAGE_MATCHED [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
  ancestor186_it299_b292e46d9199ccf8
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 2, 3] vs FRESH [6, 2, 3]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1567.9, 1595.7, 1564.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [53.19, 53.19, 51.47] vs CODE_ONLY [53.19, 53.19, 51.47]
    4_scramble_or_reset_damages            0/3  eff ACC [6.225, 2.171, 3.175] SCR [6.225, 2.171, 3.175] RESET [6.225, 2.171, 3.175]
    5_transfers_to_fresh_copy              0/3  FULL [53.19, 53.19, 51.47] vs ACC remainder [53.19, 53.19, 51.47]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [53.19, 53.19, 51.47]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [53.19, 53.19, 51.47] STORAGE_MATCHED [53.19, 53.19, 51.47] vs ACC remainder [53.19, 53.19, 51.47]
  top1_137c1619929b95ec
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [3, 1, 6] vs FRESH [3, 1, 6]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1554.0, 1595.7, 1561.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [53.19, 53.19, 53.19] vs CODE_ONLY [53.19, 53.19, 53.19]
    4_scramble_or_reset_damages            0/3  eff ACC [3.173, 1.156, 6.216] SCR [3.173, 1.156, 6.216] RESET [3.173, 1.156, 6.216]
    5_transfers_to_fresh_copy              0/3  FULL [53.19, 53.19, 53.19] vs ACC remainder [53.19, 53.19, 53.19]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [53.19, 53.19, 53.19]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [53.19, 53.19, 53.19] STORAGE_MATCHED [53.19, 53.19, 53.19] vs ACC remainder [53.19, 53.19, 53.19]
  contemp_cb9ab5b10c09f06f
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [4, 0, 5] vs FRESH [4, 0, 5]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1602.6, 1602.6, 1602.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [53.42, 53.42, 53.42] vs CODE_ONLY [53.42, 53.42, 53.42]
    4_scramble_or_reset_damages            0/3  eff ACC [4.208, 0.139, 5.222] SCR [4.208, 0.139, 5.222] RESET [4.208, 0.139, 5.222]
    5_transfers_to_fresh_copy              0/3  FULL [53.42, 53.42, 53.42] vs ACC remainder [53.42, 53.42, 53.42]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [53.42, 53.42, 53.42]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [53.42, 53.42, 53.42] STORAGE_MATCHED [53.42, 53.42, 53.42] vs ACC remainder [53.42, 53.42, 53.42]
  top2_3218f89f522a8bd2
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [3, 3, 2] vs FRESH [3, 3, 2]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1602.3, 1601.0, 1538.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [53.41, 53.41, 52.09] vs CODE_ONLY [53.41, 53.41, 52.09]
    4_scramble_or_reset_damages            0/3  eff ACC [3.19, 3.171, 2.14] SCR [3.19, 3.171, 2.14] RESET [3.19, 3.171, 2.14]
    5_transfers_to_fresh_copy              0/3  FULL [53.41, 53.41, 52.09] vs ACC remainder [53.41, 53.41, 52.09]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [53.41, 53.41, 52.09]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [53.41, 53.41, 52.09] STORAGE_MATCHED [53.41, 53.41, 52.09] vs ACC remainder [53.41, 53.41, 52.09]
  top3_dcd4068516cd5882
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [3, 3, 2] vs FRESH [3, 3, 2]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1603.5, 1602.1, 1539.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [53.45, 53.45, 52.13] vs CODE_ONLY [53.45, 53.45, 52.13]
    4_scramble_or_reset_damages            0/3  eff ACC [3.19, 3.17, 2.14] SCR [3.19, 3.17, 2.14] RESET [3.19, 3.17, 2.14]
    5_transfers_to_fresh_copy              0/3  FULL [53.45, 53.45, 52.13] vs ACC remainder [53.45, 53.45, 52.13]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [53.45, 53.45, 52.13]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [53.45, 53.45, 52.13] STORAGE_MATCHED [53.45, 53.45, 52.13] vs ACC remainder [53.45, 53.45, 52.13]
  bestever_56c0341b3019cad4
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 1, 0] vs FRESH [6, 1, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1492.0, 1531.5, 1531.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [48.85, 51.05, 51.05] vs CODE_ONLY [48.85, 51.05, 51.05]
    4_scramble_or_reset_damages            0/3  eff ACC [6.238, 1.172, 0.156] SCR [6.238, 1.172, 0.156] RESET [6.238, 1.172, 0.156]
    5_transfers_to_fresh_copy              0/3  FULL [48.85, 51.05, 51.05] vs ACC remainder [48.85, 51.05, 51.05]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [48.85, 51.05, 51.05]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [48.85, 51.05, 51.05] STORAGE_MATCHED [48.85, 51.05, 51.05] vs ACC remainder [48.85, 51.05, 51.05]
  contemp_0b12c4e690262b9d
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [3, 2, 2] vs FRESH [3, 2, 2]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1544.1, 1573.3, 1608.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.03, 53.63, 53.63] vs CODE_ONLY [50.03, 53.63, 53.63]
    4_scramble_or_reset_damages            0/3  eff ACC [3.156, 2.156, 2.172] SCR [3.156, 2.156, 2.172] RESET [3.156, 2.156, 2.172]
    5_transfers_to_fresh_copy              0/3  FULL [50.03, 53.63, 53.63] vs ACC remainder [50.03, 53.63, 53.63]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.03, 53.63, 53.63]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.03, 53.63, 53.63] STORAGE_MATCHED [50.03, 53.63, 53.63] vs ACC remainder [50.03, 53.63, 53.63]
  contemp_9a5784449db2a473
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [4, 0, 2] vs FRESH [4, 0, 2]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1608.3, 1608.3, 1535.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [53.61, 53.61, 51.75] vs CODE_ONLY [53.61, 53.61, 51.75]
    4_scramble_or_reset_damages            0/3  eff ACC [4.204, 0.137, 2.138] SCR [4.204, 0.137, 2.138] RESET [4.204, 0.137, 2.138]
    5_transfers_to_fresh_copy              0/3  FULL [53.61, 53.61, 51.75] vs ACC remainder [53.61, 53.61, 51.75]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [53.61, 53.61, 51.75]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [53.61, 53.61, 51.75] STORAGE_MATCHED [53.61, 53.61, 51.75] vs ACC remainder [53.61, 53.61, 51.75]
  ancestor94_it154_8d7fcd7863273cf7
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [2, 0, 1] vs FRESH [2, 0, 1]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1563.3, 1563.3, 1516.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.11, 52.11, 52.11] vs CODE_ONLY [52.11, 52.11, 52.11]
    4_scramble_or_reset_damages            0/3  eff ACC [2.177, 0.148, 1.148] SCR [2.177, 0.148, 1.148] RESET [2.177, 0.148, 1.148]
    5_transfers_to_fresh_copy              0/3  FULL [52.11, 52.11, 52.11] vs ACC remainder [52.11, 52.11, 52.11]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.11, 52.11, 52.11]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.11, 52.11, 52.11] STORAGE_MATCHED [52.11, 52.11, 52.11] vs ACC remainder [52.11, 52.11, 52.11]
  ancestor1_it0_085e5a21a759324b
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1502.4, 1502.4, 1502.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.08, 50.08, 50.08] vs CODE_ONLY [50.08, 50.08, 50.08]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 0.163] SCR [0.163, 0.163, 0.163] RESET [0.163, 0.163, 0.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.08, 50.08, 50.08] vs ACC remainder [50.08, 50.08, 50.08]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [50.08, 50.08, 50.08] vs ACC remainder [50.08, 50.08, 50.08]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.08, 50.08, 50.08] STORAGE_MATCHED [50.08, 50.08, 50.08] vs ACC remainder [50.08, 50.08, 50.08]

MACHINERY OF top1_137c1619929b95ec (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:   469    0    2  117    0 |   0     0
    task  9:  3832    0    2  956    0 |   0     0
    task 19:  4096    0    2 1022    0 |   0     0
    task 31:  4096    0    2 1022    0 |   0     0
    task 41:  4096    0    2 1022    0 |   0     0
    task 49:  4096    0    2 1022    0 |   0     0
  artifact events: 0 (create 0, delete 0, patch/append 0); invocations by block: {}; edges: 0
  adaptation curve ACC:   2134 2134 2134 2134 2134 2134 5 2134 280 2134 2134 2134 2134 2134 2134 2134 2134 2134 2134 2134 53 53 12 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53
  adaptation curve FRESH: 2134 2134 2134 2134 2134 2134 5 2134 280 2134 2134 2134 2134 2134 2134 2134 2134 2134 2134 2134 53 53 12 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53
  reuse_gain per task:    0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0

BASELINES ON SEARCH SUITE (crius/runs/baselines_c2a): effA effF effR effS  succA  interA interF  reuse_gain  blocks
  ENUMERATE_C1_seed301     21.473 21.473 21.473 21.473   21    3358   3358        0.0    0
  ENUMERATE_C1_seed302     19.412 19.412 19.412 19.412   19   10771  10771        0.0    0
  ENUMERATE_C1_seed303     22.479 22.479 22.479 22.479   22    2548   2548        0.0    0
  ENUMERATE_VM_C1_seed301  21.471 21.471 21.471 21.471   21    3358   3358        0.0    0
  ENUMERATE_VM_C1_seed302  19.397 19.397 19.397 19.397   19   12109  12109        0.0    0
  ENUMERATE_VM_C1_seed303  22.470 22.470 22.470 22.470   22    3428   3428        0.0    0
  PROCEDURE_NOCAL_C1_seed301 21.471 21.471 21.471 21.471   21    3538   3538      -49.9    3
  PROCEDURE_NOCAL_C1_seed302 19.410 19.411 19.411 19.410   19   10917  10915      -45.5    3
  PROCEDURE_NOCAL_C1_seed303 22.477 22.478 22.478 22.477   22    2732   2728      -59.1    5
  PROCEDURE_REUSE_C1_seed301 50.488 21.470 21.481 21.481   50    1338   3718     2288.5    4
  PROCEDURE_REUSE_C1_seed302 49.459 18.410 21.453 21.453   49    4787  11057     6085.5    6
  PROCEDURE_REUSE_C1_seed303 50.492 22.476 22.484 22.483   50     948   2908     1895.0    5
  QUIT_C1_seed301          20.472 20.472 20.472 20.472   20    1907   1907        0.0    0
  QUIT_C1_seed302          17.412 17.412 17.412 17.412   17    9331   9331        0.0    0
  QUIT_C1_seed303          20.479 20.479 20.479 20.479   20    1135   1135        0.0    0
  RANDOM_C1_seed301         7.237  7.237  7.237  7.237    7   32013  32013        0.0    0
  RANDOM_C1_seed302         9.240  9.240  9.240  9.240    9   31692  31692        0.0    0
  RANDOM_C1_seed303        12.282 12.282 12.282 12.282   12   26477  26477        0.0    0
  TABLE_MEMO_C1_seed301    21.472 21.473 21.473 21.472   21    3358   3358      -15.9    0
  TABLE_MEMO_C1_seed302    19.412 19.412 19.412 19.412   19   10771  10771      -13.8    0
  TABLE_MEMO_C1_seed303    22.479 22.479 22.479 22.479   22    2548   2548      -16.7    0

