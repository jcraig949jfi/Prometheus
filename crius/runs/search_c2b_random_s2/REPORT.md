CRIUS CAMPAIGN 0 REPORT  run=search_c2b_random_s2  arm=random
code_commit=9c5caf812 dirty=True config_hash=c9c87cec99eb063f world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1   0.1626    0.1626         0.1490        19          7
    26   0.1626    0.1626         0.1837         1         16
    51   0.1626    0.1626         0.1490         1         44
    76   2.6890    2.5584         1.2619         9        154
   101   4.1906    3.7461         2.3410        30        338
   126   4.2070    2.6749         2.0450        41        505
   151   2.1743    1.7296         1.6873        38        668
   176   3.1985    3.1983         2.2913        44        837
   201   5.7394    2.8192         2.1780        43       1011
   226   3.1707    1.6061         0.9231        47       1175
   251   3.6923    2.8689         1.5220        50       1271
   276   5.7097    3.2285         2.8772        59       1347
   300  10.2967    5.4171         4.2527        62       1482
  candidates evaluated: 7208   best_ever 10.2967 (58a19cab3af267af)  wall 1482s

BEST PROGRAM 58a19cab3af267af (len 62, iteration 300, modification insert@28+const@53)
  search seed 2013000: fit 13.3484 succ 13/50 inter 17597 steps 82039 ws_cost 22676 blocks 3 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [856.447, 0.6], "B": [853.999, 0.6], "C": [48.912, 0.083], "D": [52.93, 0.0], "E": [52.93, 0.0]}
  search seed 2013001: fit 7.2450 succ 7/50 inter 29646 steps 134981 ws_cost 37378 blocks 3 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [1490.131, 0.3], "B": [1490.118, 0.3], "C": [51.197, 0.083], "D": [52.93, 0.0], "E": [52.93, 0.0]}
  listing:
      0  ADD            R7, R6, R4
      1  MOV            R1, R3
      2  MOD            R1, R2, R3
      3  BRZ            R3, 43
      4  MOD            R5, R0, R0
      5  MOD            R5, R0, R0
      6  WS_REC_NEW     R0
      7  EQ             R6, R3, R5
      8  MOD            R5, R5, R1
      9  WS_WRITE       R5, R6
     10  BRZ            R3, 39
     11  MOD            R5, R1, R0
     12  BRZ            R3, 35
     13  MOD            R5, R0, R0
     14  WS_LINK_GET    R0, R2, R5
     15  EQ             R1, R3, R5
     16  WS_LINK        R4, R6, R3
     17  WS_REC_NEW     R5
     18  PREC_BEGIN     
     19  MOD            R5, R0, R0
     20  VGET           R2, R6, R1
     21  BLK_STATE_SET  R7, R1, R5
     22  ADD            R7, R6, R4
     23  INPUT          R0, interactions_left
     24  VGET           R2, R5, R3
     25  BRZ            R3, 19
     26  VGET           R0, R7, R4
     27  EQ             R4, R7, R5
     28  BLK_DELETE     R4
     29  CONST          R0, 15
     30  BLK_DELETE     R0
     31  ADD            R7, R6, R4
     32  BLK_COMPOSE    R3, R6, R2
     33  BRZ            R6, 43
     34  VGET           R4, R6, R2
     35  ACTI           2
     36  ACTI           8
     37  WS_WRITE       R7, R3
     38  WS_LINKS       R0, R6
     39  BLK_INVOKE     R3
     40  ACTI           12
     41  MOD            R5, R0, R0
     42  ACT            R0
     43  ADD            R7, R6, R4
     44  WS_LINK_GET    R0, R2, R5
     45  VGET           R0, R7, R4
     46  MOD            R7, R5, R0
     47  MOD            R7, R5, R0
     48  BLK_DELETE     R0
     49  INPUT          R0, interactions_left
     50  MOD            R5, R0, R0
     51  INPUT          R5, last_action
     52  ACTI           8
     53  ACTI           8
     54  VLEN           R7, R0
     55  ACTI           9
     56  ACTI           5
     57  BRNZ           R5, 31
     58  BLK_STATE_SET  R1, R5, R7
     59  WS_WRITE       R7, R3
     60  WS_WRITE       R7, R3
     61  WS_REC_NEW     R4
  ancestry (166 steps, newest first): iteration/fitness/modification
    it  300  10.2967  len 62  insert@28+const@53
    it  299  5.2111  len 61  swap@19,25
    it  298  5.1699  len 61  arg@27.0+insert@27+const@51
    it  296  2.1519  len 60  replace@2+insert@27
    it  295  3.1775  len 59  duplicate@56+1->34
    it  294  1.1520  len 58  insert@54+swap@27,43+const@49
    it  293  4.2020  len 57  replace@50
    it  291  0.6508  len 57  delete@55
    it  289  2.1768  len 58  duplicate@47+5->50
    it  287  3.1633  len 53  arg@31.0+insert@47
    it  286  1.1629  len 52  swap@25,14+arg@8.2
    it  284  0.6627  len 52  arg@29.1+const@34+delete@0
    it  283  1.6710  len 53  const@35+delete@33
    it  281  0.1625  len 54  delete@46
    it  279  0.6706  len 55  arg@12.1
    ... 152 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7315.4    5.3   74.7
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.9    3.7    1.7
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0
  top1_58a19cab3af267af        2.838   2.838   2.838   2.838   2.7   2.7    38164    38164       6.3    3.0    0.0
  contemp_2758567a9c39e075     1.827   1.827   1.827   1.827   1.7   1.7    39507    39507       6.3    3.0    0.0
  top2_23ca09310119aec1        1.819   1.819   1.819   1.819   1.7   1.7    40809    40809       6.8    2.0    0.0
  top3_08f8a59661fdbb4a        1.816   1.816   1.816   1.816   1.7   1.7    40809    40809       7.3    3.0    0.0
  ancestor166_it299_5522b0f5   1.816   1.816   1.816   1.816   1.7   1.7    40809    40809       7.3    3.0    0.0
  contemp_89053a88d214b1a5     1.476   1.476   1.476   1.476   1.3   1.3    40795    40795       6.3    3.0    0.0
  contemp_6a6e05e9298e047b     1.154   1.154   1.154   1.154   1.0   1.0    40185    40185       7.3    3.0    0.0
  ancestor84_it158_386b49e82   0.830   0.830   0.830   0.830   0.7   0.7    40828    40828       2.5    1.0    0.0
  ancestor1_it0_d059030c15c0   0.163   0.163   0.163   0.163   0.0   0.0        0        0       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.02/ 455.13   14.92/ 539.10   21.12/  47.94   33.22/  48.94   40.08/  50.52
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.14/ 443.81  528.13/ 527.79   47.94/  47.89   48.86/  48.88   50.43/  50.46
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ENUMERATE_VM_C1             495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  RANDOM_C1                  1662.62/1662.62 1627.07/1627.07   50.50/  50.50   50.50/  50.50   48.56/  48.56
  top1_58a19cab3af267af      2044.71/2044.82 1835.71/1835.84   52.44/  52.57   52.28/  52.41   51.27/  51.40
  contemp_2758567a9c39e075   1974.72/1974.83 2046.78/2046.91   51.59/  51.72   52.70/  52.83   52.93/  53.06
  top2_23ca09310119aec1      2095.02/2095.15 2028.57/2028.71   49.81/  49.94   50.92/  51.05   51.32/  51.46
  top3_08f8a59661fdbb4a      2114.99/2115.12 2047.91/2048.06   50.28/  50.43   51.39/  51.54   51.80/  51.95
  ancestor166_it299_5522b0f5 2114.99/2115.12 2047.91/2048.06   50.28/  50.43   51.39/  51.54   51.80/  51.95
  contemp_89053a88d214b1a5   2082.50/2082.61 2153.35/2153.48   51.15/  51.28   53.85/  53.98   51.98/  52.11
  contemp_6a6e05e9298e047b   2114.99/2115.12 1977.77/1977.92   51.59/  51.74   52.93/  53.08   52.93/  53.08
  ancestor84_it158_386b49e82 1962.91/1962.95 2030.03/2030.08   50.78/  50.83   50.78/  50.83   49.64/  49.69
  ancestor1_it0_d059030c15c0 2000.01/2000.01 2000.01/2000.01   50.01/  50.01   50.01/  50.01   50.01/  50.01

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610
  top1_58a19cab3af267af          1/36    49     1/30    49     0/12    50     1/12    47     1/30  1933     4/30  1736
  contemp_2758567a9c39e075       1/36    49     1/30    50     0/12    50     0/12    50     2/30  1867     1/30  1935
  top2_23ca09310119aec1          2/36    47     1/30    48     0/12    50     1/12    48     0/30  2000     1/30  1936
  top3_08f8a59661fdbb4a          2/36    47     1/30    48     0/12    50     1/12    48     0/30  2000     1/30  1936
  ancestor166_it299_5522b0f5     2/36    47     1/30    48     0/12    50     1/12    48     0/30  2000     1/30  1936
  contemp_89053a88d214b1a5       2/36    47     0/30    50     1/12    46     0/12    50     1/30  1934     0/30  2000
  contemp_6a6e05e9298e047b       1/36    49     0/30    50     0/12    50     0/12    50     0/30  2000     2/30  1870
  ancestor84_it158_386b49e82     0/36    50     0/30    50     0/12    50     1/12    48     1/30  1934     0/30  2000
  ancestor1_it0_d059030c15c0     0/36     0     0/30     0     0/12     0     0/12     0     0/30     0     0/30     0

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.27    49.53    36.27    36.27    49.53    49.53    49.53   5.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.56    49.55    49.56    49.56    49.55    49.55    49.55   2.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ENUMERATE_VM_C1               51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  RANDOM_C1                     49.64       --    49.64    49.64    49.64    49.64    49.64   0.0
  top1_58a19cab3af267af         51.83    51.83    51.83    51.83    51.84    51.84    51.84   2.0
  contemp_2758567a9c39e075      52.80    52.81    52.80    52.80    52.81    52.81    52.81   2.0
  top2_23ca09310119aec1         51.10    51.10    51.10    51.10    51.10    51.10    51.10   1.0
  top3_08f8a59661fdbb4a         51.57    51.58    51.57    51.57    51.58    51.58    51.58   2.0
  ancestor166_it299_5522b0f5    51.57    51.58    51.57    51.57    51.58    51.58    51.58   2.0
  contemp_89053a88d214b1a5      53.02    53.02    53.02    53.02    53.03    53.03    53.03   2.0
  contemp_6a6e05e9298e047b      52.93    52.93    52.93    52.93    52.94    52.94    52.94   2.0
  ancestor84_it158_386b49e82    50.27    50.27    50.27    50.27    50.27    50.27    50.27   1.0
  ancestor1_it0_d059030c15c0    50.01       --    50.01    50.01    50.01    50.01    50.01   0.0

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
  top1_58a19cab3af267af
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [1, 4, 3] vs FRESH [1, 4, 3]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [3.9, 3.9, 3.9] vs 5% of FRESH cost [1552.0, 1591.8, 1554.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.72, 52.93, 51.84] vs CODE_ONLY [50.73, 52.94, 51.85]
    4_scramble_or_reset_damages            0/3  eff ACC [1.144, 4.212, 3.16] SCR [1.144, 4.212, 3.16] RESET [1.144, 4.212, 3.16]
    5_transfers_to_fresh_copy              0/3  FULL [50.72, 52.93, 51.84] vs ACC remainder [50.72, 52.93, 51.84]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [50.73, 52.93, 51.84] vs ACC remainder [50.72, 52.93, 51.84]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.73, 52.94, 51.85] STORAGE_MATCHED [50.73, 52.94, 51.85] vs ACC remainder [50.72, 52.93, 51.84]
  contemp_2758567a9c39e075
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [1, 1, 3] vs FRESH [1, 1, 3]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [3.9, 3.9, 3.8] vs 5% of FRESH cost [1584.9, 1591.8, 1543.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.55, 52.93, 52.93] vs CODE_ONLY [52.55, 52.94, 52.94]
    4_scramble_or_reset_damages            0/3  eff ACC [1.143, 1.16, 3.178] SCR [1.143, 1.16, 3.178] RESET [1.143, 1.16, 3.178]
    5_transfers_to_fresh_copy              0/3  FULL [52.55, 52.93, 52.93] vs ACC remainder [52.55, 52.93, 52.93]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.55, 52.93, 52.93] vs ACC remainder [52.55, 52.93, 52.93]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.55, 52.94, 52.94] STORAGE_MATCHED [52.55, 52.94, 52.94] vs ACC remainder [52.55, 52.93, 52.93]
  top2_23ca09310119aec1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [1, 3, 1] vs FRESH [1, 3, 1]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.2, 4.1, 4.1] vs 5% of FRESH cost [1550.6, 1484.5, 1529.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.95, 49.89, 52.45] vs CODE_ONLY [50.95, 49.9, 52.46]
    4_scramble_or_reset_damages            0/3  eff ACC [1.147, 3.164, 1.147] SCR [1.147, 3.164, 1.147] RESET [1.147, 3.164, 1.147]
    5_transfers_to_fresh_copy              0/3  FULL [50.95, 49.89, 52.45] vs ACC remainder [50.95, 49.89, 52.45]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [50.95, 49.9, 52.45] vs ACC remainder [50.95, 49.89, 52.45]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.95, 49.9, 52.46] STORAGE_MATCHED [50.95, 49.9, 52.46] vs ACC remainder [50.95, 49.89, 52.45]
  top3_08f8a59661fdbb4a
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [1, 3, 1] vs FRESH [1, 3, 1]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.3, 4.4] vs 5% of FRESH cost [1565.3, 1498.9, 1544.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.43, 50.36, 52.93] vs CODE_ONLY [51.44, 50.37, 52.94]
    4_scramble_or_reset_damages            0/3  eff ACC [1.143, 3.16, 1.144] SCR [1.143, 3.16, 1.144] RESET [1.143, 3.16, 1.144]
    5_transfers_to_fresh_copy              0/3  FULL [51.43, 50.36, 52.93] vs ACC remainder [51.43, 50.36, 52.93]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.43, 50.37, 52.93] vs ACC remainder [51.43, 50.36, 52.93]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.44, 50.37, 52.94] STORAGE_MATCHED [51.44, 50.37, 52.94] vs ACC remainder [51.43, 50.36, 52.93]
  ancestor166_it299_5522b0f5ebafa18e
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [1, 3, 1] vs FRESH [1, 3, 1]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.3, 4.4] vs 5% of FRESH cost [1565.3, 1498.9, 1544.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.43, 50.36, 52.93] vs CODE_ONLY [51.44, 50.37, 52.94]
    4_scramble_or_reset_damages            0/3  eff ACC [1.143, 3.16, 1.144] SCR [1.143, 3.16, 1.144] RESET [1.143, 3.16, 1.144]
    5_transfers_to_fresh_copy              0/3  FULL [51.43, 50.36, 52.93] vs ACC remainder [51.43, 50.36, 52.93]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.43, 50.37, 52.93] vs ACC remainder [51.43, 50.36, 52.93]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.44, 50.37, 52.94] STORAGE_MATCHED [51.44, 50.37, 52.94] vs ACC remainder [51.43, 50.36, 52.93]
  contemp_89053a88d214b1a5
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [2, 1, 1] vs FRESH [2, 1, 1]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [3.9, 3.8, 3.8] vs 5% of FRESH cost [1574.5, 1571.2, 1570.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.36, 53.85, 53.85] vs CODE_ONLY [51.36, 53.86, 53.86]
    4_scramble_or_reset_damages            0/3  eff ACC [2.154, 1.137, 1.137] SCR [2.154, 1.137, 1.137] RESET [2.154, 1.137, 1.137]
    5_transfers_to_fresh_copy              0/3  FULL [51.36, 53.85, 53.85] vs ACC remainder [51.36, 53.85, 53.85]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.36, 53.85, 53.85] vs ACC remainder [51.36, 53.85, 53.85]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.36, 53.86, 53.86] STORAGE_MATCHED [51.36, 53.86, 53.86] vs ACC remainder [51.36, 53.85, 53.85]
  contemp_6a6e05e9298e047b
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [1, 1, 1] vs FRESH [1, 1, 1]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.4] vs 5% of FRESH cost [1592.4, 1592.4, 1544.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.93, 52.93, 52.93] vs CODE_ONLY [52.94, 52.94, 52.94]
    4_scramble_or_reset_damages            0/3  eff ACC [1.16, 1.16, 1.144] SCR [1.16, 1.16, 1.144] RESET [1.16, 1.16, 1.144]
    5_transfers_to_fresh_copy              0/3  FULL [52.93, 52.93, 52.93] vs ACC remainder [52.93, 52.93, 52.93]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.93, 52.93, 52.93] vs ACC remainder [52.93, 52.93, 52.93]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.94, 52.94, 52.94] STORAGE_MATCHED [52.94, 52.94, 52.94] vs ACC remainder [52.93, 52.93, 52.93]
  ancestor84_it158_386b49e821c40d6c
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [1, 0, 1] vs FRESH [1, 0, 1]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [1.5, 1.5, 1.5] vs 5% of FRESH cost [1497.5, 1524.9, 1524.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.26, 50.78, 50.78] vs CODE_ONLY [49.26, 50.78, 50.78]
    4_scramble_or_reset_damages            0/3  eff ACC [1.158, 0.158, 1.174] SCR [1.158, 0.158, 1.174] RESET [1.158, 0.158, 1.174]
    5_transfers_to_fresh_copy              0/3  FULL [49.26, 50.78, 50.78] vs ACC remainder [49.26, 50.78, 50.78]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [49.26, 50.78, 50.78] vs ACC remainder [49.26, 50.78, 50.78]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.26, 50.78, 50.78] STORAGE_MATCHED [49.26, 50.78, 50.78] vs ACC remainder [49.26, 50.78, 50.78]
  ancestor1_it0_d059030c15c073b9
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1500.3, 1500.3, 1500.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.01, 50.01, 50.01] vs CODE_ONLY [50.01, 50.01, 50.01]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 0.163] SCR [0.163, 0.163, 0.163] RESET [0.163, 0.163, 0.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.01, 50.01, 50.01] vs ACC remainder [50.01, 50.01, 50.01]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.01, 50.01, 50.01]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.01, 50.01, 50.01] STORAGE_MATCHED [50.01, 50.01, 50.01] vs ACC remainder [50.01, 50.01, 50.01]

MACHINERY OF top1_58a19cab3af267af (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   2    42
    task  9:     0    0    0    0    0 |   2    42
    task 19:     0    0    0    0    0 |   2    42
    task 31:     0    0    0    0    0 |   2    42
    task 41:     0    0    0    0    0 |   2    42
    task 49:     0    0    0    0    0 |   2    42
  artifact events: 4 (create 3, delete 1, patch/append 0); invocations by block: {}; edges: 2
    block 1 origin=compose len=0 state=[0, 0, 0] instr=[]
    block 2 origin=calibration len=0 state=[[-1, -1, -1, -1, -1, 4, -1, -1, 5, 0, -1, -1], [9, -1, -1, -1, 5, 8, -1, -1, -1, -1, -1, -1], 0] instr=[]
  adaptation curve ACC:   2115 2115 2115 2115 2115 2115 2115 2115 2115 2115 2115 2115 2115 2115 2115 2115 2115 2115 2115 2115 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 13 53 53 53 53 53 53 53
  adaptation curve FRESH: 2115 2115 2115 2115 2115 2115 2115 2115 2115 2115 2115 2115 2115 2115 2115 2115 2115 2115 2115 2115 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 53 13 53 53 53 53 53 53 53
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

