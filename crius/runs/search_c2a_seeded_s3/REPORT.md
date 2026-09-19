CRIUS CAMPAIGN 0 REPORT  run=search_c2a_seeded_s3  arm=seeded
code_commit=6eb2d2ac7 dirty=True config_hash=401915ec4da9443a world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  20.4007   17.8781         8.6835        40          2
    26  19.8876   19.8876        13.6502        39         92
    51  20.9574   20.4815        10.4663        41        171
    76  19.9184   19.9182        11.3569        33        257
   101  17.8549   17.8549         9.2286        40        350
   126  22.3822   22.3820        15.2262        43        439
   151  22.9689   22.9689        13.8777        35        512
   176  25.4526   25.4526        20.5215        53        573
   201  23.9652   23.9651        19.6083        42        624
   226  20.9228   20.9228        15.4542        36        672
   251  23.4701   23.4518        13.7002        29        742
   276  21.9526   21.9526        18.1587        35        813
   300  22.9278   22.0520        15.1273        40        879
  candidates evaluated: 7208   best_ever 29.4616 (5de679d26b929ddd)  wall 879s

BEST PROGRAM 5de679d26b929ddd (len 46, iteration 113, modification const@1+arg@16.0)
  search seed 3011130: fit 30.4822 succ 30/50 inter 2047 steps 14001 ws_cost 50 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [60.473, 1.0], "B": [31.655, 1.0], "C": [38.43, 0.5], "D": [38.955, 0.4], "E": [51.94, 0.0]}
  search seed 3011131: fit 28.4410 succ 28/50 inter 6936 steps 31510 ws_cost 50 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [269.358, 1.0], "B": [314.659, 1.0], "C": [43.011, 0.417], "D": [49.444, 0.1], "E": [50.108, 0.25]}
  listing:
      0  CONST          R0, 4
      1  CONST          R0, -19
      2  MOV            R2, R1
      3  MOV            R6, R2
      4  WS_LINK_GET    R5, R2, R0
      5  ADD            R0, R0, R5
      6  BRZ            R3, 24
      7  LT             R3, R7, R2
      8  ACT            R1
      9  MOD            R3, R4, R1
     10  VLEN           R0, R1
     11  VSET           R4, R5, R1
     12  BLK_STATE_SET  R5, R7, R3
     13  MUL            R7, R1, R1
     14  EQ             R3, R0, R5
     15  MUL            R2, R3, R1
     16  ADD            R3, R0, R5
     17  JMP            4
     18  DIV            R4, R4, R1
     19  MOD            R3, R4, R1
     20  ACT            R3
     21  ADD            R0, R0, R5
     22  JMP            26
     23  VSET           R4, R5, R1
     24  BRZ            R3, 29
     25  ACT            R4
     26  ACT            R7
     27  BLK_REC_BEGIN  
     28  DIV            R4, R5, R1
     29  INPUT          R1, num_ops
     30  MUL            R7, R1, R1
     31  MUL            R2, R3, R1
     32  ACT            R1
     33  MOD            R3, R0, R1
     34  ACT            R3
     35  DIV            R4, R0, R1
     36  MOD            R3, R4, R1
     37  ACT            R3
     38  DIV            R4, R4, R1
     39  MOD            R3, R4, R1
     40  ACT            R3
     41  ADD            R0, R0, R5
     42  JMP            32
     43  VSET           R4, R5, R1
     44  BLK_STATE_SET  R5, R7, R3
     45  MUL            R4, R1, R1
  ancestry (46 steps, newest first): iteration/fitness/modification
    it  113  29.4616  len 46  const@1+arg@16.0
    it  105  21.3580  len 46  duplicate@32+6->18+const@1+arg@28.1
    it  100  22.9591  len 40  arg@39.0
    it   97  22.4418  len 40  const@1
    it   94  22.4472  len 40  delete@9
    it   93  19.8860  len 41  const@1+insert@15
    it   92  19.9185  len 40  const@0+duplicate@12+3->37+const@1
    it   91  26.9720  len 37  insert@3+insert@12
    it   89  17.9059  len 35  insert@6+insert@11
    it   88  24.9008  len 33  const@0
    it   86  20.9364  len 33  const@1
    it   85  23.9744  len 33  duplicate@18+2->10
    it   84  19.4212  len 31  const@0
    it   83  19.9149  len 31  arg@7.1+replace@7+const@1
    it   81  21.4271  len 31  delete@8+delete@13+arg@18.0
    ... 32 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7316.0    4.3   74.7
  top1_0f33f6bb4fa2d99d       21.782  21.782  21.782  21.782  21.3  21.3     6074     6074       0.0    0.0    0.0
  ancestor132_it298_751f8d07  21.781  21.781  21.781  21.781  21.3  21.3     6144     6144       0.0    0.0    0.0
  top2_e64d013a9cf1a3b5       21.781  21.781  21.781  21.781  21.3  21.3     6174     6174       0.0    0.0    0.0
  top3_565c6fdaf09ab5a8       21.781  21.781  21.781  21.781  21.3  21.3     6174     6174       0.0    0.0    0.0
  contemp_c176f31b333a9dc6    21.781  21.781  21.781  21.781  21.3  21.3     6174     6174       0.0    0.0    0.0
  ancestor66_it155_aa7a2e5d5  21.447  21.447  21.447  21.447  21.0  21.0     6302     6302       0.0    0.0    0.0
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.3    2.7    1.7
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ancestor1_it0_0875253d162c  19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       0.0    0.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       0.0    0.0    0.0
  bestever_5de679d26b929ddd   19.387  19.387  19.387  19.387  19.0  19.0    13342    13342       0.0    0.0    0.0
  contemp_4b7cab2986e8e4f4    13.325  13.325  13.325  13.325  13.0  13.0    19501    19501       0.0    0.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0
  contemp_8c325eb8c92fc55b     4.879   4.879   4.879   4.879   4.7   4.7    34224    34224       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.00/ 455.13   14.90/ 539.10   21.11/  47.94   33.21/  48.94   40.07/  50.52
  top1_0f33f6bb4fa2d99d       230.13/ 230.13  251.00/ 251.00   50.65/  50.65   51.25/  51.25   52.01/  52.01
  ancestor132_it298_751f8d07  233.32/ 233.32  255.43/ 255.43   50.07/  50.07   51.39/  51.39   51.95/  51.95
  top2_e64d013a9cf1a3b5       234.86/ 234.86  256.98/ 256.98   50.06/  50.06   51.38/  51.38   51.94/  51.94
  top3_565c6fdaf09ab5a8       234.86/ 234.86  256.98/ 256.98   50.06/  50.06   51.38/  51.38   51.94/  51.94
  contemp_c176f31b333a9dc6    234.86/ 234.86  256.98/ 256.98   50.06/  50.06   51.38/  51.38   51.94/  51.94
  ancestor66_it155_aa7a2e5d5  241.60/ 241.60  263.71/ 263.71   50.60/  50.60   50.41/  50.41   51.93/  51.93
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.13/ 443.81  528.11/ 527.79   47.93/  47.89   48.85/  48.88   50.42/  50.46
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ancestor1_it0_0875253d162c  495.80/ 495.80  525.01/ 525.01   50.10/  50.10   51.09/  51.09   52.68/  52.68
  ENUMERATE_VM_C1             495.80/ 495.80  525.01/ 525.01   50.10/  50.10   51.09/  51.09   52.68/  52.68
  bestever_5de679d26b929ddd   521.97/ 521.97  715.90/ 715.90   48.04/  48.04   50.41/  50.41   51.94/  51.94
  contemp_4b7cab2986e8e4f4   1181.89/1181.89  811.60/ 811.60   53.31/  53.31   52.83/  52.83   55.14/  55.14
  RANDOM_C1                  1662.62/1662.62 1627.07/1627.07   50.50/  50.50   50.50/  50.50   48.56/  48.56
  contemp_8c325eb8c92fc55b   1659.65/1659.65 1725.75/1725.75   50.02/  50.02   51.25/  51.25   51.80/  51.80

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  top1_0f33f6bb4fa2d99d          3/36    49     1/30    49     0/12    50     0/12    50    30/30   220    30/30   240
  ancestor132_it298_751f8d07     3/36    48     1/30    49     0/12    50     0/12    50    30/30   223    30/30   244
  top2_e64d013a9cf1a3b5          3/36    48     1/30    49     0/12    50     0/12    50    30/30   225    30/30   246
  top3_565c6fdaf09ab5a8          3/36    48     1/30    49     0/12    50     0/12    50    30/30   225    30/30   246
  contemp_c176f31b333a9dc6       3/36    48     1/30    49     0/12    50     0/12    50    30/30   225    30/30   246
  ancestor66_it155_aa7a2e5d5     2/36    49     1/30    48     0/12    50     0/12    50    30/30   231    30/30   252
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ancestor1_it0_0875253d162c     2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  bestever_5de679d26b929ddd      5/36    46     2/30    48     0/12    50     0/12    50    27/30   502    23/30   689
  contemp_4b7cab2986e8e4f4       2/36    48     2/30    48     0/12    50     0/12    50    15/30  1070    20/30   734
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610
  contemp_8c325eb8c92fc55b       2/36    48     1/30    49     0/12    50     0/12    50     6/30  1606     5/30  1670

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.26    49.53    36.26    36.26    49.53    49.53    49.53   4.0
  top1_0f33f6bb4fa2d99d         51.59       --    51.59    51.59    51.59    51.59    51.59   0.0
  ancestor132_it298_751f8d07    51.64       --    51.64    51.64    51.64    51.64    51.64   0.0
  top2_e64d013a9cf1a3b5         51.63       --    51.63    51.63    51.63    51.63    51.63   0.0
  top3_565c6fdaf09ab5a8         51.63       --    51.63    51.63    51.63    51.63    51.63   0.0
  contemp_c176f31b333a9dc6      51.63       --    51.63    51.63    51.63    51.63    51.63   0.0
  ancestor66_it155_aa7a2e5d5    51.08       --    51.08    51.08    51.08    51.08    51.08   0.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.55    49.55    49.55    49.55    49.55    49.55    49.55   1.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ancestor1_it0_0875253d162c    51.80       --    51.80    51.80    51.80    51.80    51.80   0.0
  ENUMERATE_VM_C1               51.80       --    51.80    51.80    51.80    51.80    51.80   0.0
  bestever_5de679d26b929ddd     51.09       --    51.09    51.09    51.09    51.09    51.09   0.0
  contemp_4b7cab2986e8e4f4      53.86       --    53.86    53.86    53.86    53.86    53.86   0.0
  RANDOM_C1                     49.64       --    49.64    49.64    49.64    49.64    49.64   0.0
  contemp_8c325eb8c92fc55b      51.49       --    51.49    51.49    51.49    51.49    51.49   0.0

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
  top1_0f33f6bb4fa2d99d
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 21, 23] vs FRESH [20, 21, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1560.3, 1534.3, 1514.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.01, 52.01, 50.74] vs CODE_ONLY [52.01, 52.01, 50.74]
    4_scramble_or_reset_damages            0/3  eff ACC [20.458, 21.419, 23.469] SCR [20.458, 21.419, 23.469] RESET [20.458, 21.419, 23.469]
    5_transfers_to_fresh_copy              0/3  FULL [52.01, 52.01, 50.74] vs ACC remainder [52.01, 52.01, 50.74]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.01, 52.01, 50.74]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.01, 52.01, 50.74] STORAGE_MATCHED [52.01, 52.01, 50.74] vs ACC remainder [52.01, 52.01, 50.74]
  ancestor132_it298_751f8d0731944745
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 21, 23] vs FRESH [20, 21, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1558.5, 1538.7, 1494.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.95, 51.95, 51.02] vs CODE_ONLY [51.95, 51.95, 51.02]
    4_scramble_or_reset_damages            0/3  eff ACC [20.457, 21.418, 23.468] SCR [20.457, 21.418, 23.468] RESET [20.457, 21.418, 23.468]
    5_transfers_to_fresh_copy              0/3  FULL [51.95, 51.95, 51.02] vs ACC remainder [51.95, 51.95, 51.02]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.95, 51.95, 51.02]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.95, 51.95, 51.02] STORAGE_MATCHED [51.95, 51.95, 51.02] vs ACC remainder [51.95, 51.95, 51.02]
  top2_e64d013a9cf1a3b5
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 21, 23] vs FRESH [20, 21, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1558.2, 1538.4, 1493.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.94, 51.94, 51.01] vs CODE_ONLY [51.94, 51.94, 51.01]
    4_scramble_or_reset_damages            0/3  eff ACC [20.457, 21.418, 23.468] SCR [20.457, 21.418, 23.468] RESET [20.457, 21.418, 23.468]
    5_transfers_to_fresh_copy              0/3  FULL [51.94, 51.94, 51.01] vs ACC remainder [51.94, 51.94, 51.01]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.94, 51.94, 51.01]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.94, 51.94, 51.01] STORAGE_MATCHED [51.94, 51.94, 51.01] vs ACC remainder [51.94, 51.94, 51.01]
  top3_565c6fdaf09ab5a8
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 21, 23] vs FRESH [20, 21, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1558.2, 1538.4, 1493.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.94, 51.94, 51.01] vs CODE_ONLY [51.94, 51.94, 51.01]
    4_scramble_or_reset_damages            0/3  eff ACC [20.457, 21.418, 23.468] SCR [20.457, 21.418, 23.468] RESET [20.457, 21.418, 23.468]
    5_transfers_to_fresh_copy              0/3  FULL [51.94, 51.94, 51.01] vs ACC remainder [51.94, 51.94, 51.01]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.94, 51.94, 51.01]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.94, 51.94, 51.01] STORAGE_MATCHED [51.94, 51.94, 51.01] vs ACC remainder [51.94, 51.94, 51.01]
  contemp_c176f31b333a9dc6
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 21, 23] vs FRESH [20, 21, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1558.2, 1538.4, 1493.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.94, 51.94, 51.01] vs CODE_ONLY [51.94, 51.94, 51.01]
    4_scramble_or_reset_damages            0/3  eff ACC [20.457, 21.418, 23.468] SCR [20.457, 21.418, 23.468] RESET [20.457, 21.418, 23.468]
    5_transfers_to_fresh_copy              0/3  FULL [51.94, 51.94, 51.01] vs ACC remainder [51.94, 51.94, 51.01]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.94, 51.94, 51.01]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.94, 51.94, 51.01] STORAGE_MATCHED [51.94, 51.94, 51.01] vs ACC remainder [51.94, 51.94, 51.01]
  ancestor66_it155_aa7a2e5d50b6f92a
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 21, 22] vs FRESH [20, 21, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1557.9, 1546.4, 1475.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.93, 51.93, 49.39] vs CODE_ONLY [51.93, 51.93, 49.39]
    4_scramble_or_reset_damages            0/3  eff ACC [20.456, 21.417, 22.467] SCR [20.456, 21.417, 22.467] RESET [20.456, 21.417, 22.467]
    5_transfers_to_fresh_copy              0/3  FULL [51.93, 51.93, 49.39] vs ACC remainder [51.93, 51.93, 49.39]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.93, 51.93, 49.39]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.93, 51.93, 49.39] STORAGE_MATCHED [51.93, 51.93, 49.39] vs ACC remainder [51.93, 51.93, 49.39]
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
  ancestor1_it0_0875253d162cdf0f
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 18, 22] vs FRESH [18, 18, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1580.4, 1531.9, 1488.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.68, 52.68, 50.04] vs CODE_ONLY [52.68, 52.68, 50.04]
    4_scramble_or_reset_damages            0/3  eff ACC [18.368, 18.4, 22.445] SCR [18.368, 18.4, 22.445] RESET [18.368, 18.4, 22.445]
    5_transfers_to_fresh_copy              0/3  FULL [52.68, 52.68, 50.04] vs ACC remainder [52.68, 52.68, 50.04]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.68, 52.68, 50.04]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.68, 52.68, 50.04] STORAGE_MATCHED [52.68, 52.68, 50.04] vs ACC remainder [52.68, 52.68, 50.04]
  ENUMERATE_VM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 18, 22] vs FRESH [18, 18, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1580.4, 1531.9, 1488.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.68, 52.68, 50.04] vs CODE_ONLY [52.68, 52.68, 50.04]
    4_scramble_or_reset_damages            0/3  eff ACC [18.368, 18.4, 22.445] SCR [18.368, 18.4, 22.445] RESET [18.368, 18.4, 22.445]
    5_transfers_to_fresh_copy              0/3  FULL [52.68, 52.68, 50.04] vs ACC remainder [52.68, 52.68, 50.04]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.68, 52.68, 50.04]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.68, 52.68, 50.04] STORAGE_MATCHED [52.68, 52.68, 50.04] vs ACC remainder [52.68, 52.68, 50.04]
  bestever_5de679d26b929ddd
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [16, 18, 23] vs FRESH [16, 18, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1555.0, 1449.1, 1484.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.76, 51.94, 49.58] vs CODE_ONLY [51.76, 51.94, 49.58]
    4_scramble_or_reset_damages            0/3  eff ACC [16.354, 18.376, 23.432] SCR [16.354, 18.376, 23.432] RESET [16.354, 18.376, 23.432]
    5_transfers_to_fresh_copy              0/3  FULL [51.76, 51.94, 49.58] vs ACC remainder [51.76, 51.94, 49.58]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.76, 51.94, 49.58]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.76, 51.94, 49.58] STORAGE_MATCHED [51.76, 51.94, 49.58] vs ACC remainder [51.76, 51.94, 49.58]
  contemp_4b7cab2986e8e4f4
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [10, 10, 19] vs FRESH [10, 10, 19]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1635.5, 1654.2, 1537.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [55.14, 55.14, 51.29] vs CODE_ONLY [55.14, 55.14, 51.29]
    4_scramble_or_reset_damages            0/3  eff ACC [10.278, 10.293, 19.403] SCR [10.278, 10.293, 19.403] RESET [10.278, 10.293, 19.403]
    5_transfers_to_fresh_copy              0/3  FULL [55.14, 55.14, 51.29] vs ACC remainder [55.14, 55.14, 51.29]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [55.14, 55.14, 51.29]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [55.14, 55.14, 51.29] STORAGE_MATCHED [55.14, 55.14, 51.29] vs ACC remainder [55.14, 55.14, 51.29]
  RANDOM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 6, 9] vs FRESH [6, 6, 9]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1493.8, 1515.0, 1489.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.32, 50.5, 49.1] vs CODE_ONLY [49.32, 50.5, 49.1]
    4_scramble_or_reset_damages            0/3  eff ACC [6.205, 6.235, 9.221] SCR [6.205, 6.235, 9.221] RESET [6.205, 6.235, 9.221]
    5_transfers_to_fresh_copy              0/3  FULL [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.32, 50.5, 49.1]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.32, 50.5, 49.1] STORAGE_MATCHED [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
  contemp_8c325eb8c92fc55b
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [9, 3, 2] vs FRESH [9, 3, 2]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1554.0, 1534.3, 1492.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.8, 51.8, 50.88] vs CODE_ONLY [51.8, 51.8, 50.88]
    4_scramble_or_reset_damages            0/3  eff ACC [9.3, 3.185, 2.152] SCR [9.3, 3.185, 2.152] RESET [9.3, 3.185, 2.152]
    5_transfers_to_fresh_copy              0/3  FULL [51.8, 51.8, 50.88] vs ACC remainder [51.8, 51.8, 50.88]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.8, 51.8, 50.88]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.8, 51.8, 50.88] STORAGE_MATCHED [51.8, 51.8, 50.88] vs ACC remainder [51.8, 51.8, 50.88]

MACHINERY OF top1_0f33f6bb4fa2d99d (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   0     0
    task  9:     0    0    0    0    0 |   0     0
    task 19:     0    0    0    0    0 |   0     0
    task 31:     0    0    0    0    0 |   0     0
    task 41:     0    0    0    0    0 |   0     0
    task 49:     0    0    0    0    0 |   0     0
  artifact events: 0 (create 0, delete 0, patch/append 0); invocations by block: {}; edges: 0
  adaptation curve ACC:   304 162 177 34 304 304 67 246 319 46 102 229 34 34 304 296 296 177 162 5 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
  adaptation curve FRESH: 304 162 177 34 304 304 67 246 319 46 102 229 34 34 304 296 296 177 162 5 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
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

