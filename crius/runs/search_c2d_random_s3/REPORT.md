CRIUS CAMPAIGN 0 REPORT  run=search_c2d_random_s3  arm=random
code_commit=52c58d0d4 dirty=True config_hash=7ab056c39e1821fd world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1   1.1787    0.6706         0.3404        22          7
    26   0.1626    0.1626         0.1626         2         12
    51   0.1626    0.1626         0.1626         1         28
    76   0.1626    0.1626         0.1558         1         54
   101   0.1626    0.1626         0.1558         1         71
   126   1.1788    0.9248         0.3320         1         90
   151   0.1626    0.1626         0.1558         1        114
   176   5.7150    1.9960         1.0910         4        136
   201   5.2238    4.3851         2.7230         7        257
   226   6.7396    4.7209         2.8998        35        434
   251   5.2001    3.9260         3.5499        35        599
   276   6.2185    4.9502         3.1851        34        775
   300   7.2293    6.2195         4.0630        42        957
  candidates evaluated: 7208   best_ever 13.7744 (b398c43eb3719f6e)  wall 957s

BEST PROGRAM b398c43eb3719f6e (len 32, iteration 237, modification replace@25+delete@8+delete@24)
  search seed 3012370: fit 16.3003 succ 16/50 inter 23643 steps 69573 ws_cost 22407 blocks 32 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [1480.329, 0.3], "B": [835.921, 0.6], "C": [39.271, 0.5], "D": [51.505, 0.1], "E": [51.75, 0.0]}
  search seed 3012371: fit 11.2485 succ 11/50 inter 29794 steps 85922 ws_cost 27682 blocks 32 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [1273.873, 0.4], "B": [1670.305, 0.2], "C": [50.764, 0.083], "D": [47.895, 0.3], "E": [50.017, 0.125]}
  listing:
      0  BLK_STATE_GET  R0, R6, R7
      1  ACTI           10
      2  ACTI           1
      3  BLK_LEN        R7, R5
      4  ACTI           3
      5  ACTI           9
      6  ACTI           5
      7  NOT            R2, R5
      8  ACTI           11
      9  VGET           R6, R5, R6
     10  BLK_LEN        R7, R5
     11  BLK_LEN        R7, R5
     12  ACTI           2
     13  VGET           R6, R5, R6
     14  MOV            R7, R3
     15  ACTI           15
     16  EQ             R7, R1, R3
     17  VGET           R6, R5, R6
     18  VGET           R6, R1, R6
     19  BLK_NEW        R3
     20  VGET           R3, R5, R6
     21  ACTI           9
     22  EQ             R7, R1, R3
     23  ACTI           3
     24  BLK_LEN        R7, R5
     25  ACTI           11
     26  BLK_APPEND     R1, R4
     27  VGET           R6, R5, R6
     28  ACTI           11
     29  BLK_LEN        R7, R5
     30  BRZ            R5, 0
     31  WS_REC_GET     R0, R6, R2
  ancestry (91 steps, newest first): iteration/fitness/modification
    it  237  13.7744  len 32  replace@25+delete@8+delete@24
    it  236  5.7141  len 34  insert@29+delete@2
    it  235  3.6763  len 34  const@14
    it  234  5.6924  len 34  swap@24,14
    it  232  2.6677  len 34  insert@16+const@29+duplicate@5+1->25
    it  230  3.1661  len 32  swap@17,29
    it  228  2.1829  len 32  swap@17,9+const@3
    it  227  3.1590  len 32  delete@21+delete@6
    it  225  4.7093  len 34  arg@20.1+const@30+const@8
    it  223  2.1751  len 34  arg@23.0
    it  221  5.7177  len 34  duplicate@5+2->6+duplicate@18+6->7+arg@27.1
    it  219  2.6819  len 26  swap@11,23
    it  218  4.7142  len 26  const@14+const@21+delete@11
    it  217  2.6891  len 27  swap@10,3
    it  215  5.7235  len 27  delete@12+const@14
    ... 77 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7315.4    5.3   74.7
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.9    3.7    1.7
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0
  ancestor64_it190_679946966   2.511   2.511   2.511   2.511   2.3   2.3    38849    38849       3.4    1.0    0.0
  contemp_58d5517aab15d201     2.171   2.171   2.171   2.171   2.0   2.0    37762    37762       4.9    1.0    0.0
  ancestor128_it297_8baa84d7   2.168   2.168   2.168   2.168   2.0   2.0    39000    39000       5.4    1.0    0.0
  top1_5b47569ca88afb66        2.164   2.164   2.164   2.164   2.0   2.0    39549    39549       5.4    1.0    0.0
  top2_bbfd730ba0c54457        2.164   2.164   2.164   2.164   2.0   2.0    39549    39549       5.4    1.0    0.0
  top3_dd9dc2ace7b8e9eb        2.163   2.163   2.163   2.163   2.0   2.0    39549    39549       5.4    1.0    0.0
  contemp_462f6fa1c6c8d1ce     1.486   1.486   1.486   1.486   1.3   1.3    40794    40794       5.4    1.0    0.0
  bestever_b398c43eb3719f6e    1.484   1.484   1.484   1.484   1.3   1.3    41461    41461       4.9   32.0    0.0
  contemp_4503b657b2dac500     1.474   1.474   1.474   1.474   1.3   1.3    41449    41449       4.9    1.0    0.0
  ancestor1_it0_68bd7cf8fe6f   0.163   0.163   0.163   0.163   0.0   0.0        0        0       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.02/ 455.13   14.92/ 539.10   21.12/  47.94   33.22/  48.94   40.08/  50.52
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.14/ 443.81  528.13/ 527.79   47.94/  47.89   48.86/  48.88   50.43/  50.46
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ENUMERATE_VM_C1             495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  RANDOM_C1                  1662.62/1662.62 1627.07/1627.07   50.50/  50.50   50.50/  50.50   48.56/  48.56
  ancestor64_it190_679946966 1975.21/1975.27 1839.15/1839.22   48.44/  48.51   50.98/  51.05   49.38/  49.44
  contemp_58d5517aab15d201   2079.96/2080.05 1808.96/1809.06   53.68/  53.78   53.68/  53.78   53.68/  53.78
  ancestor128_it297_8baa84d7 2033.58/2033.68 1901.17/1901.28   49.88/  49.99   52.38/  52.49   52.38/  52.49
  top1_5b47569ca88afb66      2028.68/2028.78 1954.68/1954.79   49.35/  49.46   52.26/  52.37   52.26/  52.37
  top2_bbfd730ba0c54457      2028.68/2028.78 1954.68/1954.79   49.35/  49.46   52.26/  52.37   52.26/  52.37
  top3_dd9dc2ace7b8e9eb      2031.90/2032.00 1957.78/1957.89   49.43/  49.54   52.34/  52.45   52.34/  52.45
  contemp_462f6fa1c6c8d1ce   2091.69/2091.79 2022.26/2022.37   48.92/  49.02   52.26/  52.37   52.26/  52.37
  bestever_b398c43eb3719f6e  2074.53/2074.62 2074.52/2074.62   50.32/  50.42   49.79/  49.89   51.75/  51.85
  contemp_4503b657b2dac500   2134.53/2134.62 2134.52/2134.62   49.20/  49.30   53.43/  53.53   53.43/  53.53
  ancestor1_it0_68bd7cf8fe6f 2000.14/2000.14 2000.14/2000.14   50.14/  50.14   50.14/  50.14   50.14/  50.14

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610
  ancestor64_it190_679946966     2/36    47     0/30    50     1/12    47     0/12    50     1/30  1936     3/30  1803
  contemp_58d5517aab15d201       0/36    50     0/30    50     0/12    50     0/12    50     1/30  1940     5/30  1687
  ancestor128_it297_8baa84d7     2/36    47     0/30    50     0/12    50     0/12    50     1/30  1940     3/30  1813
  top1_5b47569ca88afb66          3/36    47     0/30    50     0/12    50     0/12    50     1/30  1940     2/30  1869
  top2_bbfd730ba0c54457          3/36    47     0/30    50     0/12    50     0/12    50     1/30  1940     2/30  1869
  top3_dd9dc2ace7b8e9eb          3/36    47     0/30    50     0/12    50     0/12    50     1/30  1940     2/30  1869
  contemp_462f6fa1c6c8d1ce       3/36    47     0/30    50     0/12    50     0/12    50     0/30  2000     1/30  1934
  bestever_b398c43eb3719f6e      2/36    48     2/30    48     0/12    50     0/12    50     0/30  2000     0/30  2000
  contemp_4503b657b2dac500       4/36    46     0/30    50     0/12    50     0/12    50     0/30  2000     0/30  2000
  ancestor1_it0_68bd7cf8fe6f     0/36     0     0/30     0     0/12     0     0/12     0     0/30     0     0/30     0

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.27    49.53    36.27    36.27    49.53    49.53    49.53   5.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.56    49.55    49.56    49.56    49.55    49.55    49.55   2.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ENUMERATE_VM_C1               51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  RANDOM_C1                     49.64       --    49.64    49.64    49.64    49.64    49.64   0.0
  ancestor64_it190_679946966    50.27    50.27    50.27    50.27    50.27    50.27    50.27   1.0
  contemp_58d5517aab15d201      53.68    53.69    53.68    53.68    53.69    53.69    53.69   1.0
  ancestor128_it297_8baa84d7    52.38    52.39    52.38    52.38    52.39    52.39    52.39   1.0
  top1_5b47569ca88afb66         52.26    52.27    52.26    52.26    52.27    52.27    52.27   1.0
  top2_bbfd730ba0c54457         52.26    52.27    52.26    52.26    52.27    52.27    52.27   1.0
  top3_dd9dc2ace7b8e9eb         52.34    52.35    52.34    52.34    52.35    52.35    52.35   1.0
  contemp_462f6fa1c6c8d1ce      52.26    52.27    52.26    52.26    52.27    52.27    52.27   1.0
  bestever_b398c43eb3719f6e     50.66    50.66    50.66    50.66    50.66    50.66    50.66  32.0
  contemp_4503b657b2dac500      53.43    53.44    53.43    53.43    53.44    53.44    53.44   1.0
  ancestor1_it0_68bd7cf8fe6f    50.14       --    50.14    50.14    50.14    50.14    50.14   0.0

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
  ancestor64_it190_679946966934679d
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [1, 2, 4] vs FRESH [1, 2, 4]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [2.1, 2.1, 2.1] vs 5% of FRESH cost [1531.5, 1531.5, 1401.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.98, 50.98, 48.84] vs CODE_ONLY [50.98, 50.98, 48.84]
    4_scramble_or_reset_damages            0/3  eff ACC [1.172, 2.188, 4.173] SCR [1.172, 2.188, 4.173] RESET [1.172, 2.188, 4.173]
    5_transfers_to_fresh_copy              0/3  FULL [50.98, 50.98, 48.84] vs ACC remainder [50.98, 50.98, 48.84]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [50.98, 50.98, 48.84] vs ACC remainder [50.98, 50.98, 48.84]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.98, 50.98, 48.84] STORAGE_MATCHED [50.98, 50.98, 48.84] vs ACC remainder [50.98, 50.98, 48.84]
  contemp_58d5517aab15d201
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [1, 1, 4] vs FRESH [1, 1, 4]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [3.0, 3.0, 3.0] vs 5% of FRESH cost [1613.4, 1613.4, 1613.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [53.68, 53.68, 53.68] vs CODE_ONLY [53.69, 53.69, 53.69]
    4_scramble_or_reset_damages            0/3  eff ACC [1.156, 1.156, 4.201] SCR [1.156, 1.156, 4.201] RESET [1.156, 1.156, 4.201]
    5_transfers_to_fresh_copy              0/3  FULL [53.68, 53.68, 53.68] vs ACC remainder [53.68, 53.68, 53.68]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [53.69, 53.69, 53.69] vs ACC remainder [53.68, 53.68, 53.68]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [53.69, 53.69, 53.69] STORAGE_MATCHED [53.69, 53.69, 53.69] vs ACC remainder [53.68, 53.68, 53.68]
  ancestor128_it297_8baa84d7c1f51916
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [1, 4, 1] vs FRESH [1, 4, 1]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [3.3, 3.3, 3.3] vs 5% of FRESH cost [1530.3, 1574.7, 1529.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.38, 52.38, 52.38] vs CODE_ONLY [52.39, 52.39, 52.39]
    4_scramble_or_reset_damages            0/3  eff ACC [1.147, 4.209, 1.147] SCR [1.147, 4.209, 1.147] RESET [1.147, 4.209, 1.147]
    5_transfers_to_fresh_copy              0/3  FULL [52.38, 52.38, 52.38] vs ACC remainder [52.38, 52.38, 52.38]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.39, 52.39, 52.39] vs ACC remainder [52.38, 52.38, 52.38]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.39, 52.39, 52.39] STORAGE_MATCHED [52.39, 52.39, 52.39] vs ACC remainder [52.38, 52.38, 52.38]
  top1_5b47569ca88afb66
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [4, 1, 1] vs FRESH [4, 1, 1]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [3.3, 3.3, 3.3] vs 5% of FRESH cost [1511.7, 1571.1, 1525.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.26, 52.26, 52.26] vs CODE_ONLY [52.27, 52.27, 52.27]
    4_scramble_or_reset_damages            0/3  eff ACC [4.179, 1.164, 1.148] SCR [4.179, 1.164, 1.148] RESET [4.179, 1.164, 1.148]
    5_transfers_to_fresh_copy              0/3  FULL [52.26, 52.26, 52.26] vs ACC remainder [52.26, 52.26, 52.26]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.27, 52.27, 52.27] vs ACC remainder [52.26, 52.26, 52.26]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.27, 52.27, 52.27] STORAGE_MATCHED [52.27, 52.27, 52.27] vs ACC remainder [52.26, 52.26, 52.26]
  top2_bbfd730ba0c54457
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [4, 1, 1] vs FRESH [4, 1, 1]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [3.3, 3.3, 3.3] vs 5% of FRESH cost [1511.7, 1571.1, 1525.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.26, 52.26, 52.26] vs CODE_ONLY [52.27, 52.27, 52.27]
    4_scramble_or_reset_damages            0/3  eff ACC [4.179, 1.164, 1.148] SCR [4.179, 1.164, 1.148] RESET [4.179, 1.164, 1.148]
    5_transfers_to_fresh_copy              0/3  FULL [52.26, 52.26, 52.26] vs ACC remainder [52.26, 52.26, 52.26]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.27, 52.27, 52.27] vs ACC remainder [52.26, 52.26, 52.26]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.27, 52.27, 52.27] STORAGE_MATCHED [52.27, 52.27, 52.27] vs ACC remainder [52.26, 52.26, 52.26]
  top3_dd9dc2ace7b8e9eb
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [4, 1, 1] vs FRESH [4, 1, 1]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [3.3, 3.3, 3.3] vs 5% of FRESH cost [1514.0, 1573.5, 1528.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.34, 52.34, 52.34] vs CODE_ONLY [52.35, 52.35, 52.35]
    4_scramble_or_reset_damages            0/3  eff ACC [4.179, 1.164, 1.147] SCR [4.179, 1.164, 1.147] RESET [4.179, 1.164, 1.147]
    5_transfers_to_fresh_copy              0/3  FULL [52.34, 52.34, 52.34] vs ACC remainder [52.34, 52.34, 52.34]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.35, 52.35, 52.35] vs ACC remainder [52.34, 52.34, 52.34]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.35, 52.35, 52.35] STORAGE_MATCHED [52.35, 52.35, 52.35] vs ACC remainder [52.34, 52.34, 52.34]
  contemp_462f6fa1c6c8d1ce
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [1, 1, 2] vs FRESH [1, 1, 2]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [3.3, 3.3, 3.3] vs 5% of FRESH cost [1526.8, 1571.1, 1495.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.26, 52.26, 52.26] vs CODE_ONLY [52.27, 52.27, 52.27]
    4_scramble_or_reset_damages            0/3  eff ACC [1.147, 1.164, 2.148] SCR [1.147, 1.164, 2.148] RESET [1.147, 1.164, 2.148]
    5_transfers_to_fresh_copy              0/3  FULL [52.26, 52.26, 52.26] vs ACC remainder [52.26, 52.26, 52.26]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.27, 52.27, 52.27] vs ACC remainder [52.26, 52.26, 52.26]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.27, 52.27, 52.27] STORAGE_MATCHED [52.27, 52.27, 52.27] vs ACC remainder [52.26, 52.26, 52.26]
  bestever_b398c43eb3719f6e
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [1, 0, 3] vs FRESH [1, 0, 3]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [3.0, 3.0, 3.0] vs 5% of FRESH cost [1515.7, 1555.5, 1484.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.54, 51.75, 50.69] vs CODE_ONLY [49.55, 51.76, 50.69]
    4_scramble_or_reset_damages            0/3  eff ACC [1.15, 0.15, 3.151] SCR [1.15, 0.15, 3.151] RESET [1.15, 0.15, 3.151]
    5_transfers_to_fresh_copy              0/3  FULL [49.54, 51.75, 50.69] vs ACC remainder [49.54, 51.75, 50.69]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [49.55, 51.76, 50.69] vs ACC remainder [49.54, 51.75, 50.69]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.55, 51.76, 50.69] STORAGE_MATCHED [49.55, 51.76, 50.69] vs ACC remainder [49.54, 51.75, 50.69]
  contemp_4503b657b2dac500
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [2, 0, 2] vs FRESH [2, 0, 2]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [3.0, 3.0, 3.0] vs 5% of FRESH cost [1536.1, 1605.9, 1523.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [53.43, 53.43, 53.43] vs CODE_ONLY [53.44, 53.44, 53.44]
    4_scramble_or_reset_damages            0/3  eff ACC [2.14, 0.14, 2.141] SCR [2.14, 0.14, 2.141] RESET [2.14, 0.14, 2.141]
    5_transfers_to_fresh_copy              0/3  FULL [53.43, 53.43, 53.43] vs ACC remainder [53.43, 53.43, 53.43]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [53.44, 53.44, 53.44] vs ACC remainder [53.43, 53.43, 53.43]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [53.44, 53.44, 53.44] STORAGE_MATCHED [53.44, 53.44, 53.44] vs ACC remainder [53.43, 53.43, 53.43]
  ancestor1_it0_68bd7cf8fe6f77e8
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1504.2, 1504.2, 1504.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.14, 50.14, 50.14] vs CODE_ONLY [50.14, 50.14, 50.14]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 0.163] SCR [0.163, 0.163, 0.163] RESET [0.163, 0.163, 0.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.14, 50.14, 50.14] vs ACC remainder [50.14, 50.14, 50.14]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.14, 50.14, 50.14]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.14, 50.14, 50.14] STORAGE_MATCHED [50.14, 50.14, 50.14] vs ACC remainder [50.14, 50.14, 50.14]

MACHINERY OF top1_5b47569ca88afb66 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   1    32
    task  9:     0    0    0    0    0 |   1    32
    task 19:     0    0    0    0    0 |   1    32
    task 31:     0    0    0    0    0 |   1    32
    task 41:     0    0    0    0    0 |   1    32
    task 49:     0    0    0    0    0 |   1    32
  artifact events: 1 (create 1, delete 0, patch/append 0); invocations by block: {}; edges: 0
    block 0 origin=calibration len=0 state=[[2, 3, 6, -1, -1, -1, 9, 11, 5, 0, -1, 1], [9, 11, 0, 1, -1, 8, 2, -1, -1, 6, -1, 7], 0] instr=[]
  adaptation curve ACC:   2092 2092 2092 2092 2092 2092 2092 2092 201 2092 2092 2092 2092 2092 2092 64 2092 2092 2092 2092 52 8 52 52 52 37 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
  adaptation curve FRESH: 2092 2092 2092 2092 2092 2092 2092 2092 201 2092 2092 2092 2092 2092 2092 64 2092 2092 2092 2092 52 8 52 52 52 37 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
  reuse_gain per task:    0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0

BASELINES ON SEARCH SUITE (crius/runs/baselines_c2d): effA effF effR effS  succA  interA interF  reuse_gain  blocks
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

