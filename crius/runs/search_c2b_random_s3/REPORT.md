CRIUS CAMPAIGN 0 REPORT  run=search_c2b_random_s3  arm=random
code_commit=9c5caf812 dirty=True config_hash=c9c87cec99eb063f world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1   1.1788    1.1788         0.4961        18          4
    26   0.6707    0.6707         0.6004        10          6
    51   0.1626    0.1626         0.1490         1         12
    76   0.1626    0.1626         0.1558         1         43
   101   7.2540    3.9542         1.6323         7        114
   126   3.7077    3.3240         2.6468        59        277
   151   9.2680    8.2646         7.2270        92        426
   176   6.2369    3.7027         2.3081        94        579
   201   5.2247    4.2619         2.8450        94        738
   226   7.2326    6.0338         4.0947        96        906
   251   6.7371    6.0983         4.8933        96       1068
   276   7.7476    5.5175         4.2769        95       1223
   300   7.2402    4.3807         2.2347        96       1375
  candidates evaluated: 7208   best_ever 13.3036 (2310e316b3217861)  wall 1375s

BEST PROGRAM 2310e316b3217861 (len 95, iteration 225, modification insert@8+delete@62)
  search seed 3012250: fit 4.2144 succ 4/50 inter 33949 steps 84998 ws_cost 33256 blocks 1 invoked 0 ws_bytes 4096
    by stage (mean cost, success rate): {"A": [1701.952, 0.2], "B": [1655.892, 0.2], "C": [51.77, 0.0], "D": [51.77, 0.0], "E": [51.77, 0.0]}
  search seed 3012251: fit 22.3929 succ 22/50 inter 12668 steps 35910 ws_cost 14227 blocks 1 invoked 0 ws_bytes 4096
    by stage (mean cost, success rate): {"A": [487.485, 0.8], "B": [682.809, 0.7], "C": [51.216, 0.167], "D": [43.768, 0.5], "E": [51.77, 0.0]}
  listing:
      0  ACTI           3
      1  WS_APPEND      R1, R7
      2  ACTI           3
      3  ACTI           6
      4  CONST          R6, -20
      5  DIV            R5, R7, R6
      6  BLK_COUNT      R3
      7  BLK_LEN        R2, R5
      8  EQ             R1, R0, R0
      9  WS_FREE        R6
     10  VGET           R0, R4, R4
     11  ACTI           2
     12  MUL            R6, R6, R2
     13  ACTI           3
     14  WS_APPEND      R1, R7
     15  WS_APPEND      R5, R7
     16  ACTI           5
     17  WS_APPEND      R1, R0
     18  WS_REC_NEW     R2
     19  MOV            R5, R2
     20  WS_APPEND      R1, R7
     21  ACTI           11
     22  ACTI           1
     23  VSET           R7, R5, R1
     24  BRNZ           R4, 15
     25  ACTI           2
     26  ACT            R3
     27  LT             R5, R2, R0
     28  WS_APPEND      R1, R7
     29  WS_REC_GET     R3, R3, R6
     30  WS_APPEND      R1, R0
     31  MOV            R5, R2
     32  BLK_LEN        R2, R3
     33  PREC_BEGIN     
     34  ACTI           8
     35  MOV            R5, R2
     36  ACTI           -5
     37  ACTI           4
     38  ACTI           3
     39  WS_LINKS       R5, R4
     40  ACTI           6
     41  DIV            R5, R7, R6
     42  ACTI           2
     43  ACTI           1
     44  ACTI           -2
     45  DIV            R5, R7, R6
     46  ACTI           6
     47  ACTI           4
     48  ACTI           7
     49  ACTI           4
     50  WS_REC_SET     R7, R4, R2
     51  ACTI           5
     52  ACTI           2
     53  ACTI           1
     54  ACTI           4
     55  MOV            R5, R2
     56  ACTI           3
     57  WS_APPEND      R1, R7
     58  ACTI           -3
     59  MUL            R6, R6, R2
     60  ACTI           1
     61  VGET           R1, R6, R6
     62  ACTI           7
     63  ACTI           3
     64  ACTI           2
     65  PREC_BEGIN     
     66  MOV            R5, R2
     67  WS_SREAD       R5, R7, R5
     68  DIV            R5, R7, R6
     69  BLK_PATCH      R5, R2, R5
     70  ACTI           6
     71  ACTI           3
     72  BLK_LEN        R2, R5
     73  LT             R6, R6, R1
     74  JMP            3
     75  ADD            R4, R7, R3
     76  WS_FIND        R6, R0
     77  ACTI           -13
     78  ACTI           5
     79  BLK_LEN        R7, R2
     80  WS_READ        R7, R4
     81  ACTI           3
     82  ACTI           4
     83  WS_APPEND      R1, R7
     84  BLK_APPEND     R0, R5
     85  BLK_COPY       R7, R0
     86  ACTI           4
     87  WS_LINKS       R7, R7
     88  WS_REC_NEW     R1
     89  JMP            86
     90  WS_APPEND      R3, R7
     91  WS_APPEND      R1, R7
     92  WS_FIND        R5, R1
     93  WS_APPEND      R1, R7
     94  BLK_DELETE     R0
  ancestry (129 steps, newest first): iteration/fitness/modification
    it  225  13.3036  len 95  insert@8+delete@62
    it  223  2.6775  len 95  swap@17,78+delete@19+insert@22
    it  222  4.6966  len 95  const@50+const@37+const@22
    it  218  5.2198  len 95  duplicate@48+1->53+arg@49.2
    it  216  9.7654  len 94  const@69+swap@76,7+replace@91
    it  215  4.6987  len 94  swap@93,77+delete@94
    it  214  3.7011  len 95  const@15
    it  212  3.6903  len 95  delete@50+replace@77+swap@63,76
    it  211  3.6952  len 96  swap@4,41+const@39+swap@61,95
    it  207  5.2219  len 96  arg@31.1+replace@49
    it  206  4.7135  len 96  const@52+duplicate@31+2->64
    it  205  5.7184  len 94  arg@68.0
    it  204  4.6954  len 94  const@10+delete@93+arg@57.0
    it  203  4.2084  len 95  const@62+delete@83
    it  202  5.7234  len 96  const@67+insert@19+arg@7.0
    ... 115 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7315.4    5.3   74.7
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.9    3.7    1.7
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0
  contemp_b2010f220490371c     6.216   6.900   6.216   6.216   6.0   6.7    33653    31667   -2057.2    1.0    0.0
  bestever_2310e316b3217861    5.875   5.875   5.875   5.875   5.7   5.7    34666    34666       5.9    1.0    0.0
  ancestor92_it162_037f4aca8   5.210   5.210   5.210   5.210   5.0   5.0    34783    34783       5.3    1.0    0.0
  contemp_ca115b1f56eb74ed     4.207   4.207   4.207   4.207   4.0   4.0    34538    34538       6.3    1.0    0.0
  top3_1d4b70b33ec77d7a        3.862   3.862   3.862   3.862   3.7   3.7    36089    36089       6.3    1.0    0.0
  ancestor183_it299_24583292   3.862   3.862   3.862   3.862   3.7   3.7    36089    36089       6.3    1.0    0.0
  top2_940c553ff051848b        2.850   2.850   2.850   2.850   2.7   2.7    37636    37636       6.3    1.0    0.0
  contemp_1ab23ae10d3baa1e     2.848   2.848   2.848   2.848   2.7   2.7    37768    37768       6.3    1.0    0.0
  top1_192c0d79bfcd40dc        2.514   2.514   2.514   2.514   2.3   2.3    37853    37853       5.8    1.0    0.0
  ancestor1_it0_d02a3abcf6f4   0.163   0.163   0.163   0.163   0.0   0.0       50       50       1.9    2.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.02/ 455.13   14.92/ 539.10   21.12/  47.94   33.22/  48.94   40.08/  50.52
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.14/ 443.81  528.13/ 527.79   47.94/  47.89   48.86/  48.88   50.43/  50.46
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ENUMERATE_VM_C1             495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  RANDOM_C1                  1662.62/1662.62 1627.07/1627.07   50.50/  50.50   50.50/  50.50   48.56/  48.56
  contemp_b2010f220490371c   1571.86/1610.36 1763.38/1517.72   51.23/  50.55   50.80/  51.96   50.60/  51.96
  bestever_2310e316b3217861  1852.48/1852.59 1580.82/1580.94   51.06/  51.18   51.83/  51.95   51.77/  51.89
  ancestor92_it162_037f4aca8 1775.70/1775.80 1642.41/1642.52   48.90/  49.01   51.26/  51.37   50.60/  50.71
  contemp_ca115b1f56eb74ed   1757.02/1757.14 1689.38/1689.50   52.04/  52.17   52.04/  52.17   50.77/  50.90
  top3_1d4b70b33ec77d7a      1826.02/1826.14 1762.19/1762.32   50.53/  50.66   51.87/  52.00   50.77/  50.90
  ancestor183_it299_24583292 1826.02/1826.14 1762.19/1762.32   50.53/  50.66   51.87/  52.00   50.77/  50.90
  top2_940c553ff051848b      1931.78/1931.89 1807.49/1807.62   50.37/  50.49   51.70/  51.83   50.69/  50.82
  contemp_1ab23ae10d3baa1e   1878.17/1878.29 1890.65/1890.78   51.27/  51.40   51.51/  51.64   51.94/  52.07
  top1_192c0d79bfcd40dc      1869.98/1870.08 1899.85/1899.97   50.53/  50.65   51.87/  51.99   51.87/  51.99
  ancestor1_it0_d02a3abcf6f4 2000.09/2000.12 2000.08/2000.12   50.08/  50.12   50.08/  50.12   50.08/  50.12

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610
  contemp_b2010f220490371c       1/36    49     2/30    49     1/12    47     0/12    50     8/30  1517     6/30  1702
  bestever_2310e316b3217861      3/36    49     1/30    50     0/12    50     0/12    50     4/30  1790     9/30  1527
  ancestor92_it162_037f4aca8     2/36    48     0/30    50     1/12    48     0/12    50     5/30  1731     7/30  1601
  contemp_ca115b1f56eb74ed       0/36    50     0/30    50     1/12    47     0/12    50     5/30  1685     6/30  1620
  top3_1d4b70b33ec77d7a          1/36    49     0/30    50     1/12    48     0/12    50     4/30  1762     5/30  1700
  ancestor183_it299_24583292     1/36    49     0/30    50     1/12    48     0/12    50     4/30  1762     5/30  1700
  top2_940c553ff051848b          1/36    49     0/30    50     1/12    48     0/12    50     2/30  1868     4/30  1748
  contemp_1ab23ae10d3baa1e       1/36    49     1/30    50     0/12    50     0/12    50     3/30  1808     3/30  1820
  top1_192c0d79bfcd40dc          1/36    49     0/30    50     0/12    50     0/12    50     3/30  1804     3/30  1833
  ancestor1_it0_d02a3abcf6f4     0/36     1     0/30     1     0/12     1     0/12     1     0/30     1     0/30     1

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.27    49.53    36.27    36.27    49.53    49.53    49.53   5.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.56    49.55    49.56    49.56    49.55    49.55    49.55   2.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ENUMERATE_VM_C1               51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  RANDOM_C1                     49.64       --    49.64    49.64    49.64    49.64    49.64   0.0
  contemp_b2010f220490371c      50.71    50.72    50.44    50.71    50.44    50.44    50.44   1.0
  bestever_2310e316b3217861     51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  ancestor92_it162_037f4aca8    50.97    50.97    50.97    50.97    50.97    50.97    50.97   1.0
  contemp_ca115b1f56eb74ed      51.48    51.48    51.48    51.48    51.48    51.48    51.48   1.0
  top3_1d4b70b33ec77d7a         51.38    51.39    51.38    51.38    51.39    51.39    51.39   1.0
  ancestor183_it299_24583292    51.38    51.39    51.38    51.38    51.39    51.39    51.39   1.0
  top2_940c553ff051848b         51.25    51.26    51.25    51.25    51.26    51.26    51.26   1.0
  contemp_1ab23ae10d3baa1e      51.70    51.71    51.70    51.70    51.71    51.71    51.71   1.0
  top1_192c0d79bfcd40dc         51.87    51.88    51.87    51.87    51.88    51.88    51.88   1.0
  ancestor1_it0_d02a3abcf6f4    50.08    50.08    50.08    50.08    50.08    50.08    50.08   1.0

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
  contemp_b2010f220490371c
    0_competence_kept_ACC_ge_FRESH         2/3  successes ACC [4, 9, 5] vs FRESH [4, 9, 7]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [21.8, 5.8, 15.6] vs 5% of FRESH cost [1535.6, 1531.4, 1558.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.81, 50.18, 51.15] vs CODE_ONLY [50.81, 50.18, 50.35]
    4_scramble_or_reset_damages            0/3  eff ACC [4.183, 9.26, 5.206] SCR [4.183, 9.26, 5.206] RESET [4.183, 9.26, 5.206]
    5_transfers_to_fresh_copy              0/3  FULL [50.81, 50.18, 51.15] vs ACC remainder [50.81, 50.18, 51.15]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [50.82, 50.19, 51.16] vs ACC remainder [50.81, 50.18, 51.15]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.81, 50.18, 50.35] STORAGE_MATCHED [50.81, 50.18, 50.35] vs ACC remainder [50.81, 50.18, 51.15]
  bestever_2310e316b3217861
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [3, 4, 10] vs FRESH [3, 4, 10]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [3.6, 3.6, 3.6] vs 5% of FRESH cost [1556.7, 1542.8, 1546.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.77, 51.77, 51.87] vs CODE_ONLY [51.78, 51.78, 51.88]
    4_scramble_or_reset_damages            0/3  eff ACC [3.196, 4.173, 10.256] SCR [3.196, 4.173, 10.256] RESET [3.196, 4.173, 10.256]
    5_transfers_to_fresh_copy              0/3  FULL [51.77, 51.77, 51.87] vs ACC remainder [51.77, 51.77, 51.87]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.78, 51.78, 51.88] vs ACC remainder [51.77, 51.77, 51.87]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.78, 51.78, 51.88] STORAGE_MATCHED [51.78, 51.78, 51.88] vs ACC remainder [51.77, 51.77, 51.87]
  ancestor92_it162_037f4aca8d4e11ce
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [4, 4, 7] vs FRESH [4, 4, 7]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [3.3, 3.3, 3.2] vs 5% of FRESH cost [1541.1, 1502.7, 1478.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.26, 51.26, 50.38] vs CODE_ONLY [51.27, 51.27, 50.39]
    4_scramble_or_reset_damages            0/3  eff ACC [4.216, 4.185, 7.229] SCR [4.216, 4.185, 7.229] RESET [4.216, 4.185, 7.229]
    5_transfers_to_fresh_copy              0/3  FULL [51.26, 51.26, 50.38] vs ACC remainder [51.26, 51.26, 50.38]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.27, 51.27, 50.39] vs ACC remainder [51.26, 51.26, 50.38]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.27, 51.27, 50.39] STORAGE_MATCHED [51.27, 51.27, 50.39] vs ACC remainder [51.26, 51.26, 50.38]
  contemp_ca115b1f56eb74ed
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [2, 8, 2] vs FRESH [2, 8, 2]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [3.9, 3.9, 3.9] vs 5% of FRESH cost [1565.1, 1534.7, 1565.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.04, 50.35, 52.04] vs CODE_ONLY [52.05, 50.36, 52.05]
    4_scramble_or_reset_damages            0/3  eff ACC [2.18, 8.262, 2.18] SCR [2.18, 8.262, 2.18] RESET [2.18, 8.262, 2.18]
    5_transfers_to_fresh_copy              0/3  FULL [52.04, 50.35, 52.04] vs ACC remainder [52.04, 50.35, 52.04]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.05, 50.36, 52.05] vs ACC remainder [52.04, 50.35, 52.04]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.05, 50.36, 52.05] STORAGE_MATCHED [52.05, 50.36, 52.05] vs ACC remainder [52.04, 50.35, 52.04]
  top3_1d4b70b33ec77d7a
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [3, 4, 4] vs FRESH [3, 4, 4]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [3.9, 3.8, 3.9] vs 5% of FRESH cost [1560.0, 1485.4, 1560.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.87, 50.41, 51.87] vs CODE_ONLY [51.88, 50.41, 51.88]
    4_scramble_or_reset_damages            0/3  eff ACC [3.199, 4.179, 4.21] SCR [3.199, 4.179, 4.21] RESET [3.199, 4.179, 4.21]
    5_transfers_to_fresh_copy              0/3  FULL [51.87, 50.41, 51.87] vs ACC remainder [51.87, 50.41, 51.87]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.88, 50.41, 51.88] vs ACC remainder [51.87, 50.41, 51.87]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.88, 50.41, 51.88] STORAGE_MATCHED [51.88, 50.41, 51.88] vs ACC remainder [51.87, 50.41, 51.87]
  ancestor183_it299_2458329266a0e722
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [3, 4, 4] vs FRESH [3, 4, 4]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [3.9, 3.8, 3.9] vs 5% of FRESH cost [1560.0, 1485.4, 1560.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.87, 50.41, 51.87] vs CODE_ONLY [51.88, 50.41, 51.88]
    4_scramble_or_reset_damages            0/3  eff ACC [3.199, 4.179, 4.21] SCR [3.199, 4.179, 4.21] RESET [3.199, 4.179, 4.21]
    5_transfers_to_fresh_copy              0/3  FULL [51.87, 50.41, 51.87] vs ACC remainder [51.87, 50.41, 51.87]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.88, 50.41, 51.88] vs ACC remainder [51.87, 50.41, 51.87]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.88, 50.41, 51.88] STORAGE_MATCHED [51.88, 50.41, 51.88] vs ACC remainder [51.87, 50.41, 51.87]
  top2_940c553ff051848b
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [1, 5, 2] vs FRESH [1, 5, 2]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [3.9, 3.8, 3.9] vs 5% of FRESH cost [1554.9, 1482.6, 1554.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.7, 50.35, 51.7] vs CODE_ONLY [51.71, 50.36, 51.71]
    4_scramble_or_reset_damages            0/3  eff ACC [1.168, 5.199, 2.184] SCR [1.168, 5.199, 2.184] RESET [1.168, 5.199, 2.184]
    5_transfers_to_fresh_copy              0/3  FULL [51.7, 50.35, 51.7] vs ACC remainder [51.7, 50.35, 51.7]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.71, 50.36, 51.71] vs ACC remainder [51.7, 50.35, 51.7]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.71, 50.36, 51.71] STORAGE_MATCHED [51.71, 50.36, 51.71] vs ACC remainder [51.7, 50.35, 51.7]
  contemp_1ab23ae10d3baa1e
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [3, 3, 2] vs FRESH [3, 3, 2]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [3.9, 3.9, 3.9] vs 5% of FRESH cost [1538.0, 1562.1, 1549.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.94, 51.94, 51.23] vs CODE_ONLY [51.95, 51.95, 51.23]
    4_scramble_or_reset_damages            0/3  eff ACC [3.18, 3.198, 2.165] SCR [3.18, 3.198, 2.165] RESET [3.18, 3.198, 2.165]
    5_transfers_to_fresh_copy              0/3  FULL [51.94, 51.94, 51.23] vs ACC remainder [51.94, 51.94, 51.23]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.95, 51.95, 51.23] vs ACC remainder [51.94, 51.94, 51.23]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.95, 51.95, 51.23] STORAGE_MATCHED [51.95, 51.95, 51.23] vs ACC remainder [51.94, 51.94, 51.23]
  top1_192c0d79bfcd40dc
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [1, 4, 2] vs FRESH [1, 4, 2]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [3.6, 3.5, 3.6] vs 5% of FRESH cost [1559.7, 1511.5, 1559.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.87, 51.87, 51.87] vs CODE_ONLY [51.88, 51.88, 51.88]
    4_scramble_or_reset_damages            0/3  eff ACC [1.167, 4.193, 2.183] SCR [1.167, 4.193, 2.183] RESET [1.167, 4.193, 2.183]
    5_transfers_to_fresh_copy              0/3  FULL [51.87, 51.87, 51.87] vs ACC remainder [51.87, 51.87, 51.87]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.88, 51.88, 51.88] vs ACC remainder [51.87, 51.87, 51.87]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.88, 51.88, 51.88] STORAGE_MATCHED [51.88, 51.88, 51.88] vs ACC remainder [51.87, 51.87, 51.87]
  ancestor1_it0_d02a3abcf6f45a39
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [1.2, 1.2, 1.2] vs 5% of FRESH cost [1503.6, 1503.6, 1503.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.08, 50.08, 50.08] vs CODE_ONLY [50.08, 50.08, 50.08]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 0.163] SCR [0.163, 0.163, 0.163] RESET [0.163, 0.163, 0.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.08, 50.08, 50.08] vs ACC remainder [50.08, 50.08, 50.08]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [50.08, 50.08, 50.08] vs ACC remainder [50.08, 50.08, 50.08]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.08, 50.08, 50.08] STORAGE_MATCHED [50.08, 50.08, 50.08] vs ACC remainder [50.08, 50.08, 50.08]

MACHINERY OF top1_192c0d79bfcd40dc (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:   729    0    3   91    0 |   1    32
    task  9:  4096    0    3  512    0 |   1    32
    task 19:  4096    0    3  512    0 |   1    32
    task 31:  4096    0    3  512    0 |   1    32
    task 41:  4096    0    3  512    0 |   1    32
    task 49:  4096    0    3  512    0 |   1    32
  artifact events: 1 (create 1, delete 0, patch/append 0); invocations by block: {}; edges: 0
    block 0 origin=calibration len=0 state=[[2, 3, 6, 8, -1, 4, 9, 11, 5, 0, -1, -1], [9, -1, 0, 1, 5, 8, 2, -1, 3, 6, -1, 7], 0] instr=[]
  adaptation curve ACC:   2073 2073 2073 2073 2073 2073 2073 2073 2073 2073 5 2073 2073 2073 2073 2073 2073 2073 2073 2073 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
  adaptation curve FRESH: 2073 2073 2073 2073 2073 2073 2073 2073 2073 2073 5 2073 2073 2073 2073 2073 2073 2073 2073 2073 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
  reuse_gain per task:    0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0

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

