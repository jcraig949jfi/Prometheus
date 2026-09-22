CRIUS CAMPAIGN 0 REPORT  run=search_c2b_random_s1  arm=random
code_commit=9c5caf812 dirty=True config_hash=c9c87cec99eb063f world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1   0.6627    0.5377         0.2397         8          5
    26   2.6754    1.4716         1.1428        10         70
    51   8.2458    7.2914         4.7516        30        251
    76   4.2069    4.2069         2.8769        38        405
   101   6.2062    5.7691         4.9069        36        545
   126   2.6750    2.6750         2.5700        28        694
   151   1.1591    1.1591         0.8676        23        832
   176   5.7064    5.2037         3.5429        23        965
   201   1.6835    1.6834         1.4310        32       1098
   226   8.2608    5.4082         3.7178        40       1228
   251   4.2051    3.8246         2.5627        58       1366
   276   4.7227    4.5307         3.2978        63       1513
   300   6.7268    5.7725         4.3220        86       1664
  candidates evaluated: 7208   best_ever 12.2965 (2164dcb8770bf1d8)  wall 1664s

BEST PROGRAM 2164dcb8770bf1d8 (len 27, iteration 167, modification replace@21)
  search seed 1011670: fit 6.2234 succ 6/50 inter 33634 steps 38599 ws_cost 5 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [1822.538, 0.1], "B": [1430.217, 0.3], "C": [50.56, 0.0], "D": [48.129, 0.2], "E": [50.56, 0.0]}
  search seed 1011671: fit 10.2557 succ 10/50 inter 29698 steps 35025 ws_cost 5 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [1626.785, 0.2], "B": [1229.51, 0.4], "C": [50.05, 0.167], "D": [49.243, 0.1], "E": [49.04, 0.125]}
  listing:
      0  VLEN           R3, R2
      1  ACT            R6
      2  ACT            R3
      3  ACT            R6
      4  ACT            R1
      5  ACT            R6
      6  ACT            R6
      7  ACT            R3
      8  ACT            R6
      9  ACT            R1
     10  VLEN           R3, R2
     11  ACT            R6
     12  ACT            R3
     13  ACT            R6
     14  ACT            R1
     15  ACT            R6
     16  ACT            R6
     17  ACT            R6
     18  ACT            R6
     19  ACT            R5
     20  JMP            1
     21  PINVOKE        R3, R6
     22  ACT            R6
     23  BLK_PATCH      R3, R4, R6
     24  WS_SLEN        R6, R4
     25  WS_LINK        R1, R6, R0
     26  NOT            R4, R7
  ancestry (92 steps, newest first): iteration/fitness/modification
    it  167  8.2395  len 27  replace@21
    it  166  1.6754  len 27  duplicate@0+6->10
    it  165  0.6670  len 21  replace@13+duplicate@2+5->7
    it  164  4.7071  len 16  swap@4,7
    it  162  4.7080  len 16  delete@10
    it  158  0.1588  len 17  delete@9+delete@15
    it  157  3.2074  len 19  arg@7.0+delete@17
    it  156  0.6590  len 20  arg@14.2+delete@18
    it  153  1.1752  len 21  delete@18+delete@10
    it  149  1.1667  len 23  delete@15+replace@17
    it  146  1.6747  len 24  delete@17
    it  145  4.1918  len 25  delete@18
    it  144  7.7398  len 26  delete@11
    it  142  4.6918  len 27  arg@23.0+replace@25
    it  140  6.2476  len 27  delete@25
    ... 78 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7315.4    5.3   74.7
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.9    3.7    1.7
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0
  top3_1b39964b16d33e75        6.888   6.222   6.888   6.888   6.7   6.0    32632    32554    -133.6   72.0    0.0
  top1_e342bfe763e71302        6.575   3.853   6.575   6.575   6.3   3.7    30368    36927    6745.1   39.3    0.0
  contemp_871cc86fa2aaf1e9     5.208   8.589   5.875   5.208   5.0   8.3    33875    28534   -5816.9   43.0    0.0
  ancestor163_it299_f836d89f   4.189   6.196   4.522   4.189   4.0   6.0    36480    35797    -817.7   49.3    0.0
  contemp_7ba1375a8a9057a4     3.506   8.231   3.506   3.506   3.3   8.0    38274    31501   -7223.7   42.7    0.0
  ancestor82_it145_4881b2042   2.525   2.525   2.525   2.525   2.3   2.3    37493    37493       2.5    1.0    0.0
  bestever_2164dcb8770bf1d8    2.525   2.525   2.525   2.525   2.3   2.3    37520    37520       2.5    1.0    0.0
  top2_8aaa4a415ae18066        1.822   4.868   1.155   1.822   1.7   4.7    40233    34920   -5599.0   35.0    0.0
  contemp_284c2aea5de41c39     1.163   1.162   1.163   1.163   1.0   1.0     1193     1193       2.0   33.0    0.0
  ancestor1_it0_0afc152e64f8   0.163   0.163   0.163   0.163   0.0   0.0       50       50       1.9    1.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.02/ 455.13   14.92/ 539.10   21.12/  47.94   33.22/  48.94   40.08/  50.52
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.14/ 443.81  528.13/ 527.79   47.94/  47.89   48.86/  48.88   50.43/  50.46
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ENUMERATE_VM_C1             495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  RANDOM_C1                  1662.62/1662.62 1627.07/1627.07   50.50/  50.50   50.50/  50.50   48.56/  48.56
  top3_1b39964b16d33e75      1371.53/1551.93 1902.55/1708.81   52.31/  52.30   52.31/  52.30   48.37/  48.36
  top1_e342bfe763e71302      1417.12/1797.51 1608.46/1903.04   52.15/  51.82   52.15/  52.08   52.15/  52.17
  contemp_871cc86fa2aaf1e9   1825.83/1626.90 1603.76/1222.13   52.74/  52.36   52.74/  52.36   51.15/  50.79
  ancestor163_it299_f836d89f 1786.12/1766.23 1884.60/1824.08   52.21/  51.46   52.21/  52.16   48.36/  47.84
  contemp_7ba1375a8a9057a4   1892.73/1565.33 1977.83/1583.10   52.40/  52.32   52.40/  52.32   50.95/  50.88
  ancestor82_it145_4881b2042 1753.61/1753.66 1887.97/1888.02   49.47/  49.52   50.57/  50.62   50.57/  50.62
  bestever_2164dcb8770bf1d8  1754.73/1754.77 1887.72/1887.77   50.59/  50.64   50.56/  50.61   50.56/  50.61
  top2_8aaa4a415ae18066      2032.07/1857.18 2049.94/1664.95   52.47/  52.44   52.47/  52.44   48.52/  48.59
  contemp_284c2aea5de41c39   2000.87/2000.91 2000.87/2000.91   50.87/  50.91   50.87/  50.91   46.74/  46.78
  ancestor1_it0_0afc152e64f8 2000.12/2000.16 2000.12/2000.16   50.12/  50.16   50.12/  50.16   50.12/  50.16

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610
  top3_1b39964b16d33e75          0/36    50     0/30    50     1/12    47     2/12    44    13/30  1308     4/30  1809
  top1_e342bfe763e71302          0/36    50     0/30    50     0/12    50     0/12    50    11/30  1355     8/30  1532
  contemp_871cc86fa2aaf1e9       0/36    50     0/30    50     0/12    50     1/12    47     5/30  1727     9/30  1512
  ancestor163_it299_f836d89f     0/36    50     0/30    50     1/12    47     2/12    44     5/30  1707     4/30  1794
  contemp_7ba1375a8a9057a4       0/36    50     0/30    50     0/12    50     1/12    47     6/30  1802     3/30  1876
  ancestor82_it145_4881b2042     1/36    49     0/30    50     0/12    50     0/12    50     4/30  1734     2/30  1867
  bestever_2164dcb8770bf1d8      1/36    50     0/30    50     0/12    50     0/12    50     4/30  1735     2/30  1867
  top2_8aaa4a415ae18066          0/36    50     0/30    50     1/12    47     2/12    44     1/30  1934     1/30  1943
  contemp_284c2aea5de41c39       0/36    24     0/30    24     1/12    24     2/12    23     0/30    24     0/30    24
  ancestor1_it0_0afc152e64f8     0/36     1     0/30     1     0/12     1     0/12     1     0/30     1     0/30     1

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.27    49.53    36.27    36.27    49.53    49.53    49.53   5.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.56    49.55    49.56    49.56    49.55    49.55    49.55   2.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ENUMERATE_VM_C1               51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  RANDOM_C1                     49.64       --    49.64    49.64    49.64    49.64    49.64   0.0
  top3_1b39964b16d33e75         50.56    50.50    50.54    50.56    50.54    50.54    50.54  32.0
  top1_e342bfe763e71302         52.15    52.09    52.09    52.15    52.10    52.10    52.10  32.0
  contemp_871cc86fa2aaf1e9      52.03    51.83    51.83    52.03    51.89    51.89    51.89  32.0
  ancestor163_it299_f836d89f    50.50    50.44    50.46    50.50    50.46    50.46    50.46  32.0
  contemp_7ba1375a8a9057a4      51.76    51.69    51.70    51.76    51.70    51.70    51.70  32.0
  ancestor82_it145_4881b2042    50.57    50.57    50.57    50.57    50.57    50.57    50.57   1.0
  bestever_2164dcb8770bf1d8     50.56    50.56    50.56    50.56    50.56    50.56    50.56   1.0
  top2_8aaa4a415ae18066         50.72    50.67    50.69    50.72    50.70    50.70    50.70  32.0
  contemp_284c2aea5de41c39      49.04    48.99    49.04    49.04    49.04    49.04    49.04  32.0
  ancestor1_it0_0afc152e64f8    50.12    50.12    50.12    50.12    50.12    50.12    50.12   1.0

CHARTER s13 CHECKLIST (seeds passing / seeds; thresholds: 5 percent relative; guard 0 added 2026-09-19, see report.py)
  PROCEDURE_REUSE_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [48, 48, 41] vs FRESH [20, 19, 22]
    1_cost_declines_via_accumulation       3/3  reuse_gain C-E per seed [735.9, 716.9, 235.0] vs 5% of FRESH cost [1515.6, 1467.2, 1423.8] (and 0 held)
    2_reproduces_on_heldout                3/3  same test, qualification suite; seeds passing = 3/3
    3_state_causal_FULL_vs_CODE_ONLY       2/3  remainder mean cost FULL [30.58, 30.14, 48.09] vs CODE_ONLY [50.41, 50.41, 47.78]
    4_scramble_or_reset_damages            3/3  eff ACC [48.449, 48.475, 41.476] SCR [20.443, 21.469, 22.474] RESET [20.443, 21.469, 22.475]
    5_transfers_to_fresh_copy              2/3  FULL [30.58, 30.14, 48.09] vs ACC remainder [30.58, 30.14, 48.09]
    6_executable_components_reused         2/3  invocations [82, 81, 61]; ABLATION_ALL cost [50.41, 50.41, 47.78] vs ACC remainder [30.58, 30.14, 48.09]
    7_not_compute_or_storage               2/3  COMPUTE_MATCHED [50.41, 50.41, 47.78] STORAGE_MATCHED [50.41, 50.41, 47.78] vs ACC remainder [30.58, 30.14, 48.09]
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
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.9, -1.9, 0.5] vs 5% of FRESH cost [1513.8, 1465.5, 1422.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.43, 50.43, 47.81] vs CODE_ONLY [50.42, 50.42, 47.8]
    4_scramble_or_reset_damages            0/3  eff ACC [20.37, 19.409, 22.447] SCR [20.37, 19.409, 22.447] RESET [20.37, 19.409, 22.447]
    5_transfers_to_fresh_copy              0/3  FULL [50.43, 50.43, 47.81] vs ACC remainder [50.43, 50.43, 47.81]
    6_executable_components_reused         0/3  invocations [3, 1, 1]; ABLATION_ALL cost [50.42, 50.42, 47.8] vs ACC remainder [50.43, 50.43, 47.81]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.42, 50.42, 47.8] STORAGE_MATCHED [50.42, 50.42, 47.8] vs ACC remainder [50.43, 50.43, 47.81]
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
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.3] vs 5% of FRESH cost [1584.9, 1536.3, 1492.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.68, 52.68, 50.04] vs CODE_ONLY [52.69, 52.69, 50.05]
    4_scramble_or_reset_damages            0/3  eff ACC [18.368, 18.4, 22.445] SCR [18.368, 18.4, 22.445] RESET [18.368, 18.4, 22.445]
    5_transfers_to_fresh_copy              0/3  FULL [52.68, 52.68, 50.04] vs ACC remainder [52.68, 52.68, 50.04]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.69, 52.69, 50.05] vs ACC remainder [52.68, 52.68, 50.04]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.69, 52.69, 50.05] STORAGE_MATCHED [52.69, 52.69, 50.05] vs ACC remainder [52.68, 52.68, 50.04]
  RANDOM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 6, 9] vs FRESH [6, 6, 9]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1493.8, 1515.0, 1489.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.32, 50.5, 49.1] vs CODE_ONLY [49.32, 50.5, 49.1]
    4_scramble_or_reset_damages            0/3  eff ACC [6.205, 6.235, 9.221] SCR [6.205, 6.235, 9.221] RESET [6.205, 6.235, 9.221]
    5_transfers_to_fresh_copy              0/3  FULL [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.32, 50.5, 49.1]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.32, 50.5, 49.1] STORAGE_MATCHED [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
  top3_1b39964b16d33e75
    0_competence_kept_ACC_ge_FRESH         2/3  successes ACC [8, 6, 6] vs FRESH [6, 7, 5]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [-0.3, -0.3, -0.2] vs 5% of FRESH cost [1539.6, 1534.4, 1538.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.67, 50.38, 50.62] vs CODE_ONLY [50.65, 50.36, 50.6]
    4_scramble_or_reset_damages            0/3  eff ACC [8.235, 6.219, 6.21] SCR [8.235, 6.219, 6.21] RESET [8.235, 6.219, 6.21]
    5_transfers_to_fresh_copy              0/3  FULL [50.67, 50.38, 50.62] vs ACC remainder [50.67, 50.38, 50.62]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [50.62, 50.33, 50.56] vs ACC remainder [50.67, 50.38, 50.62]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.65, 50.36, 50.6] STORAGE_MATCHED [50.65, 50.36, 50.6] vs ACC remainder [50.67, 50.38, 50.62]
  top1_e342bfe763e71302
    0_competence_kept_ACC_ge_FRESH         2/3  successes ACC [6, 4, 9] vs FRESH [3, 5, 3]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [-0.1, -2.1, -11.6] vs 5% of FRESH cost [1564.4, 1562.4, 1552.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.15, 52.15, 52.15] vs CODE_ONLY [52.1, 52.1, 52.1]
    4_scramble_or_reset_damages            0/3  eff ACC [6.233, 4.207, 9.284] SCR [6.233, 4.207, 9.284] RESET [6.233, 4.207, 9.284]
    5_transfers_to_fresh_copy              0/3  FULL [52.15, 52.15, 52.15] vs ACC remainder [52.15, 52.15, 52.15]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.09, 52.09, 52.09] vs ACC remainder [52.15, 52.15, 52.15]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.1, 52.1, 52.1] STORAGE_MATCHED [52.1, 52.1, 52.1] vs ACC remainder [52.15, 52.15, 52.15]
  contemp_871cc86fa2aaf1e9
    0_competence_kept_ACC_ge_FRESH         0/3  successes ACC [8, 2, 5] vs FRESH [10, 6, 9]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [-11.0, -11.4, -11.4] vs 5% of FRESH cost [1533.0, 1570.8, 1570.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.62, 52.74, 52.74] vs CODE_ONLY [50.48, 52.59, 52.59]
    4_scramble_or_reset_damages            0/3  eff ACC [8.24, 2.171, 5.214] SCR [8.24, 2.171, 5.214] RESET [9.24, 3.172, 5.214]
    5_transfers_to_fresh_copy              0/3  FULL [50.62, 52.74, 52.74] vs ACC remainder [50.62, 52.74, 52.74]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [50.42, 52.53, 52.53] vs ACC remainder [50.62, 52.74, 52.74]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.48, 52.59, 52.59] STORAGE_MATCHED [50.48, 52.59, 52.59] vs ACC remainder [50.62, 52.74, 52.74]
  ancestor163_it299_f836d89f6cbb0c61
    0_competence_kept_ACC_ge_FRESH         1/3  successes ACC [3, 5, 4] vs FRESH [6, 5, 7]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [-1.7, -13.2, -25.8] vs 5% of FRESH cost [1535.4, 1518.8, 1511.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.58, 50.3, 50.6] vs CODE_ONLY [50.54, 50.25, 50.6]
    4_scramble_or_reset_damages            0/3  eff ACC [3.177, 5.203, 4.187] SCR [3.177, 5.203, 4.187] RESET [4.178, 5.203, 4.187]
    5_transfers_to_fresh_copy              0/3  FULL [50.58, 50.3, 50.6] vs ACC remainder [50.58, 50.3, 50.6]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [50.53, 50.24, 50.54] vs ACC remainder [50.58, 50.3, 50.6]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.54, 50.25, 50.6] STORAGE_MATCHED [50.54, 50.25, 50.6] vs ACC remainder [50.58, 50.3, 50.6]
  contemp_7ba1375a8a9057a4
    0_competence_kept_ACC_ge_FRESH         1/3  successes ACC [1, 4, 5] vs FRESH [8, 11, 5]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [-2.4, -2.3, -2.4] vs 5% of FRESH cost [1569.6, 1534.9, 1569.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.4, 50.47, 52.4] vs CODE_ONLY [52.34, 50.41, 52.34]
    4_scramble_or_reset_damages            0/3  eff ACC [1.15, 4.181, 5.186] SCR [1.15, 4.181, 5.186] RESET [1.15, 4.181, 5.187]
    5_transfers_to_fresh_copy              0/3  FULL [52.4, 50.47, 52.4] vs ACC remainder [52.4, 50.47, 52.4]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.33, 50.4, 52.33] vs ACC remainder [52.4, 50.47, 52.4]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.34, 50.41, 52.34] STORAGE_MATCHED [52.34, 50.41, 52.34] vs ACC remainder [52.4, 50.47, 52.4]
  ancestor82_it145_4881b2042880cbb0
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [4, 2, 1] vs FRESH [4, 2, 1]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [1.5, 1.5, 1.5] vs 5% of FRESH cost [1518.6, 1479.1, 1518.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.57, 50.57, 50.57] vs CODE_ONLY [50.57, 50.57, 50.57]
    4_scramble_or_reset_damages            0/3  eff ACC [4.224, 2.175, 1.175] SCR [4.224, 2.175, 1.175] RESET [4.224, 2.175, 1.175]
    5_transfers_to_fresh_copy              0/3  FULL [50.57, 50.57, 50.57] vs ACC remainder [50.57, 50.57, 50.57]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [50.57, 50.57, 50.57] vs ACC remainder [50.57, 50.57, 50.57]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.57, 50.57, 50.57] STORAGE_MATCHED [50.57, 50.57, 50.57] vs ACC remainder [50.57, 50.57, 50.57]
  bestever_2164dcb8770bf1d8
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [4, 2, 1] vs FRESH [4, 2, 1]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [1.5, 1.5, 1.5] vs 5% of FRESH cost [1518.3, 1519.3, 1518.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.56, 50.56, 50.56] vs CODE_ONLY [50.56, 50.56, 50.56]
    4_scramble_or_reset_damages            0/3  eff ACC [4.224, 2.175, 1.175] SCR [4.224, 2.175, 1.175] RESET [4.224, 2.175, 1.175]
    5_transfers_to_fresh_copy              0/3  FULL [50.56, 50.56, 50.56] vs ACC remainder [50.56, 50.56, 50.56]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [50.56, 50.56, 50.56] vs ACC remainder [50.56, 50.56, 50.56]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.56, 50.56, 50.56] STORAGE_MATCHED [50.56, 50.56, 50.56] vs ACC remainder [50.56, 50.56, 50.56]
  top2_8aaa4a415ae18066
    0_competence_kept_ACC_ge_FRESH         0/3  successes ACC [1, 3, 1] vs FRESH [5, 7, 2]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [-0.9, -0.8, 1.2] vs 5% of FRESH cost [1543.8, 1538.5, 1544.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.83, 50.54, 50.78] vs CODE_ONLY [50.81, 50.52, 50.76]
    4_scramble_or_reset_damages            0/3  eff ACC [1.145, 3.177, 1.145] SCR [1.145, 3.177, 1.145] RESET [0.145, 3.177, 0.145]
    5_transfers_to_fresh_copy              0/3  FULL [50.83, 50.54, 50.78] vs ACC remainder [50.83, 50.54, 50.78]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [50.78, 50.49, 50.73] vs ACC remainder [50.83, 50.54, 50.78]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.81, 50.52, 50.76] STORAGE_MATCHED [50.81, 50.52, 50.76] vs ACC remainder [50.83, 50.54, 50.78]
  contemp_284c2aea5de41c39
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [1, 1, 1] vs FRESH [1, 1, 1]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [1.2, 1.2, 1.2] vs 5% of FRESH cost [1496.3, 1491.3, 1495.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.15, 48.87, 49.09] vs CODE_ONLY [49.15, 48.87, 49.09]
    4_scramble_or_reset_damages            0/3  eff ACC [1.163, 1.163, 1.163] SCR [1.163, 1.163, 1.163] RESET [1.163, 1.163, 1.163]
    5_transfers_to_fresh_copy              0/3  FULL [49.15, 48.87, 49.09] vs ACC remainder [49.15, 48.87, 49.09]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [49.1, 48.82, 49.05] vs ACC remainder [49.15, 48.87, 49.09]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.15, 48.87, 49.09] STORAGE_MATCHED [49.15, 48.87, 49.09] vs ACC remainder [49.15, 48.87, 49.09]
  ancestor1_it0_0afc152e64f839eb
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [1.2, 1.2, 1.2] vs 5% of FRESH cost [1504.8, 1504.8, 1504.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.12, 50.12, 50.12] vs CODE_ONLY [50.12, 50.12, 50.12]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 0.163] SCR [0.163, 0.163, 0.163] RESET [0.163, 0.163, 0.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.12, 50.12, 50.12] vs ACC remainder [50.12, 50.12, 50.12]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [50.12, 50.12, 50.12] vs ACC remainder [50.12, 50.12, 50.12]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.12, 50.12, 50.12] STORAGE_MATCHED [50.12, 50.12, 50.12] vs ACC remainder [50.12, 50.12, 50.12]

MACHINERY OF top1_e342bfe763e71302 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:   542    0    1    0  360 |  32   342
    task  9:  3981    0   10    0 2646 |  32   342
    task 19:  4096    0   11    0 2722 |  32   331
    task 31:  4096    0   11    0 2722 |  32   342
    task 41:  4096    0   11    0 2722 |  32   342
    task 49:  4096    0   11    0 2722 |  32   342
  artifact events: 46 (create 39, delete 7, patch/append 0); invocations by block: {}; edges: 76
    block 0 origin=calibration len=0 state=[[2, 3, -1, -1, 10, 4, -1, -1, -1, -1, -1, -1], [9, 11, 0, 1, 5, 8, 2, 10, 3, 6, 4, 7], 0] instr=[]
    block 1 origin=compose len=0 state=[0, 0, 0] instr=[]
    block 2 origin=compose len=0 state=[0, 0, 10] instr=[]
    block 3 origin=compose len=0 state=[0, 0, 0] instr=[]
    block 5 origin=compose len=0 state=[0, 0, 0] instr=[]
  adaptation curve ACC:   2086 2091 2091 299 292 535 639 2091 2091 2091 2091 2091 2101 2101 177 2101 2101 2101 2101 32 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
  adaptation curve FRESH: 2086 2085 2085 2085 2085 2085 2085 2085 2085 497 354 2085 2093 2093 2093 2093 2093 2093 2093 2093 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 54 52 52 52 52 52
  reuse_gain per task:    0 -6 -6 1786 1792 1550 1446 -6 -6 -1594 -1737 -6 -8 -8 1916 -8 -8 -8 -8 2061 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 2 -0 -0 -0 -0 -0

BASELINES ON SEARCH SUITE (crius/runs/baselines_c2b): effA effF effR effS  succA  interA interF  reuse_gain  blocks
  ENUMERATE_C1_seed301     21.473 21.473 21.473 21.473   21    3358   3358        0.0    0
  ENUMERATE_C1_seed302     19.412 19.412 19.412 19.412   19   10771  10771        0.0    0
  ENUMERATE_C1_seed303     22.479 22.479 22.479 22.479   22    2548   2548        0.0    0
  ENUMERATE_VM_C1_seed301  21.471 21.471 21.471 21.471   21    3358   3358        6.8    1
  ENUMERATE_VM_C1_seed302  19.397 19.397 19.397 19.397   19   12109  12109        7.0    1
  ENUMERATE_VM_C1_seed303  22.470 22.470 22.470 22.470   22    3428   3428        6.9    1
  PROCEDURE_NOCAL_C1_seed301 21.471 21.471 21.471 21.471   21    3538   3538      -50.2    4
  PROCEDURE_NOCAL_C1_seed302 19.410 19.411 19.411 19.410   19   10917  10915      -46.0    4
  PROCEDURE_NOCAL_C1_seed303 22.477 22.478 22.478 22.477   22    2732   2728      -59.6    6
  PROCEDURE_REUSE_C1_seed301 50.488 21.470 21.481 21.481   50    1338   3718     2287.9    5
  PROCEDURE_REUSE_C1_seed302 49.459 18.410 21.453 21.453   49    4787  11057     6084.9    7
  PROCEDURE_REUSE_C1_seed303 50.492 22.476 22.484 22.483   50     948   2908     1894.4    6
  QUIT_C1_seed301          20.472 20.472 20.472 20.472   20    1907   1907        0.0    0
  QUIT_C1_seed302          17.412 17.412 17.412 17.412   17    9331   9331        0.0    0
  QUIT_C1_seed303          20.479 20.479 20.479 20.479   20    1135   1135        0.0    0
  RANDOM_C1_seed301         7.237  7.237  7.237  7.237    7   32013  32013        0.0    0
  RANDOM_C1_seed302         9.240  9.240  9.240  9.240    9   31692  31692        0.0    0
  RANDOM_C1_seed303        12.282 12.282 12.282 12.282   12   26477  26477        0.0    0
  TABLE_MEMO_C1_seed301    21.472 21.473 21.473 21.472   21    3358   3358      -15.9    0
  TABLE_MEMO_C1_seed302    19.412 19.412 19.412 19.412   19   10771  10771      -13.8    0
  TABLE_MEMO_C1_seed303    22.479 22.479 22.479 22.479   22    2548   2548      -16.7    0

