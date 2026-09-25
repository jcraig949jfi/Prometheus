CRIUS CAMPAIGN 0 REPORT  run=search_c1b_seeded_s2  arm=seeded
code_commit=6364d6994 dirty=True config_hash=bbf684cd638167f2 world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  16.3214   12.9195         4.0293        37          2
    26  17.4228   15.6460         9.7119        64         40
    51  14.3750    9.9353         6.2755        64         77
    76  17.3958   16.5195         5.8893        48        111
   101  29.4863   29.4857        20.7602        60        141
   126   2.1920    2.1919         1.6831        54        174
   151  14.3508   14.3487         9.2743        55        210
   176  10.3035   10.2995         6.6374        54        246
   201  22.4139   22.4136        15.5769        64        283
   226  25.4817   24.8513        17.7479        60        320
   251  13.3483   12.7241         9.9238        53        360
   276  23.4415   23.4415        15.3299        47        394
   300  23.4408   22.5686        16.4406        46        426
  candidates evaluated: 7208   best_ever 32.4861 (d9e5aeab69ffd965)  wall 426s

BEST PROGRAM d9e5aeab69ffd965 (len 43, iteration 6, modification const@9)
  search seed 201006: fit 32.4861 succ 32/50 inter 1628 steps 8572 ws_cost 0 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [26.877, 1.0], "B": [25.936, 1.0], "C": [39.277, 0.417], "D": [51.31, 0.2], "E": [25.145, 0.625]}
  listing:
      0  INPUT          R1, num_ops
      1  CONST          R5, 1
      2  CONST          R0, 2
      3  MOV            R2, R1
      4  LT             R3, R0, R2
      5  BRZ            R3, 9
      6  ACT            R0
      7  ADD            R0, R0, R5
      8  JMP            4
      9  CONST          R0, -2
     10  MUL            R2, R1, R1
     11  LT             R3, R0, R2
     12  BRZ            R3, 21
     13  ACT            R1
     14  MOD            R3, R0, R1
     15  ACT            R3
     16  DIV            R4, R0, R1
     17  MOD            R3, R4, R1
     18  ACT            R3
     19  ADD            R0, R0, R5
     20  JMP            11
     21  CONST          R0, 0
     22  MUL            R2, R1, R1
     23  MUL            R2, R2, R1
     24  LT             R3, R0, R2
     25  BRZ            R3, 43
     26  ACT            R1
     27  MOD            R3, R0, R1
     28  ACT            R3
     29  DIV            R4, R0, R1
     30  MOD            R3, R4, R1
     31  ACT            R3
     32  DIV            R4, R4, R1
     33  MOD            R3, R4, R1
     34  DIV            R4, R0, R1
     35  MOD            R3, R4, R1
     36  ACT            R3
     37  DIV            R4, R4, R1
     38  ACTI           -17
     39  ACT            R3
     40  ADD            R0, R0, R5
     41  JMP            24
     42  LT             R2, R1, R1
  ancestry (5 steps, newest first): iteration/fitness/modification
    it    6  32.4861  len 43  const@9
    it    3  11.3091  len 43  delete@6
    it    2  20.4417  len 44  delete@44
    it    1  12.3051  len 45  insert@42+const@2+insert@39
    it    0  14.3736  len 43  duplicate@29+5->35+delete@35
    it    0  18.4130  len 39  seed:ENUMERATE_VM

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7316.0    4.3   74.7
  top2_50ddf29d9fedf7a7       21.438  21.438  21.438  21.438  21.0  21.0     7343     7343       0.0    0.0    0.0
  top3_7a874306ab207e25       21.438  21.438  21.438  21.438  21.0  21.0     7343     7343       0.0    0.0    0.0
  ancestor195_it299_50ddf29d  21.438  21.438  21.438  21.438  21.0  21.0     7343     7343       0.0    0.0    0.0
  contemp_e8bdba59c20aef1b    21.438  21.438  21.438  21.438  21.0  21.0     7343     7343       0.0    0.0    0.0
  top1_d19ba9831f137eca       20.768  20.768  20.768  20.768  20.3  20.3     7840     7840       0.0    0.0    0.0
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.3    2.7    1.7
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ancestor1_it0_0875253d162c  19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       0.0    0.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       0.0    0.0    0.0
  bestever_d9e5aeab69ffd965   16.042  16.042  16.042  16.042  15.7  15.7    14650    14650       0.0    0.0    0.0
  ancestor98_it144_3cf01a2c4  16.039  16.039  16.039  16.039  15.7  15.7     4462     4462       0.0    0.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0
  contemp_6f0bbc91d719db89     0.501   0.501   0.501   0.501   0.3   0.3      150      150       0.0    0.0    0.0
  contemp_e29bb956874be9dc     0.163   0.163   0.163   0.163   0.0   0.0        0        0       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.00/ 455.13   14.90/ 539.10   21.11/  47.94   33.21/  48.94   40.07/  50.52
  top2_50ddf29d9fedf7a7       409.96/ 409.96  201.11/ 201.11   47.06/  47.06   49.54/  49.54   50.00/  50.00
  top3_7a874306ab207e25       409.96/ 409.96  201.11/ 201.11   47.06/  47.06   49.54/  49.54   50.00/  50.00
  ancestor195_it299_50ddf29d  409.96/ 409.96  201.11/ 201.11   47.06/  47.06   49.54/  49.54   50.00/  50.00
  contemp_e8bdba59c20aef1b    411.29/ 411.29  201.76/ 201.76   47.21/  47.21   49.70/  49.70   50.17/  50.17
  top1_d19ba9831f137eca       436.09/ 436.09  224.01/ 224.01   47.83/  47.83   49.40/  49.40   51.63/  51.63
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.13/ 443.81  528.11/ 527.79   47.93/  47.89   48.85/  48.88   50.42/  50.46
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ancestor1_it0_0875253d162c  494.04/ 494.04  523.26/ 523.26   49.99/  49.99   50.96/  50.96   52.68/  52.68
  ENUMERATE_VM_C1             494.04/ 494.04  523.26/ 523.26   49.99/  49.99   50.96/  50.96   52.68/  52.68
  bestever_d9e5aeab69ffd965   705.65/ 705.65  675.20/ 675.20   50.87/  50.87   50.85/  50.85   50.99/  50.99
  ancestor98_it144_3cf01a2c4  680.10/ 680.10  744.70/ 744.70   48.34/  48.34   50.76/  50.76   52.40/  52.40
  RANDOM_C1                  1661.96/1661.96 1626.54/1626.54   50.44/  50.44   50.50/  50.50   48.40/  48.40
  contemp_6f0bbc91d719db89   1933.67/1933.67 2000.24/2000.24   50.24/  50.24   50.24/  50.24   50.24/  50.24
  contemp_e29bb956874be9dc   2000.04/2000.04 2000.04/2000.04   50.04/  50.04   50.04/  50.04   50.04/  50.04

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  top2_50ddf29d9fedf7a7          5/36    46     2/30    48     0/12    50     1/12    47    26/30   398    29/30   195
  top3_7a874306ab207e25          5/36    46     2/30    48     0/12    50     1/12    47    26/30   398    29/30   195
  ancestor195_it299_50ddf29d     5/36    46     2/30    48     0/12    50     1/12    47    26/30   398    29/30   195
  contemp_e8bdba59c20aef1b       5/36    46     2/30    48     0/12    50     1/12    47    26/30   398    29/30   195
  top1_d19ba9831f137eca          4/36    46     2/30    48     0/12    50     0/12    50    26/30   423    29/30   217
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ancestor1_it0_0875253d162c     2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  bestever_d9e5aeab69ffd965      2/36    48     2/30    48     0/12    50     1/12    47    21/30   674    21/30   645
  ancestor98_it144_3cf01a2c4     5/36    46     1/30    48     0/12    50     0/12    50    21/30   148    20/30   154
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610
  contemp_6f0bbc91d719db89       0/36     3     0/30     3     0/12     3     0/12     3     1/30     3     0/30     3
  contemp_e29bb956874be9dc       0/36     0     0/30     0     0/12     0     0/12     0     0/30     0     0/30     0

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.26    49.53    36.26    36.26    49.53    49.53    49.53   4.0
  top2_50ddf29d9fedf7a7         49.74       --    49.74    49.74    49.74    49.74    49.74   0.0
  top3_7a874306ab207e25         49.74       --    49.74    49.74    49.74    49.74    49.74   0.0
  ancestor195_it299_50ddf29d    49.74       --    49.74    49.74    49.74    49.74    49.74   0.0
  contemp_e8bdba59c20aef1b      49.91       --    49.91    49.91    49.91    49.91    49.91   0.0
  top1_d19ba9831f137eca         50.39       --    50.39    50.39    50.39    50.39    50.39   0.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.55    49.55    49.55    49.55    49.55    49.55    49.55   1.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ancestor1_it0_0875253d162c    51.73       --    51.73    51.73    51.73    51.73    51.73   0.0
  ENUMERATE_VM_C1               51.73       --    51.73    51.73    51.73    51.73    51.73   0.0
  bestever_d9e5aeab69ffd965     50.91       --    50.91    50.91    50.91    50.91    50.91   0.0
  ancestor98_it144_3cf01a2c4    51.49       --    51.49    51.49    51.49    51.49    51.49   0.0
  RANDOM_C1                     49.57       --    49.57    49.57    49.57    49.57    49.57   0.0
  contemp_6f0bbc91d719db89      50.24       --    50.24    50.24    50.24    50.24    50.24   0.0
  contemp_e29bb956874be9dc      50.04       --    50.04    50.04    50.04    50.04    50.04   0.0

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
  top2_50ddf29d9fedf7a7
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [21, 19, 23] vs FRESH [21, 19, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1484.1, 1469.7, 1426.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.46, 51.63, 48.14] vs CODE_ONLY [49.46, 51.63, 48.14]
    4_scramble_or_reset_damages            0/3  eff ACC [21.45, 19.412, 23.454] SCR [21.45, 19.412, 23.454] RESET [21.45, 19.412, 23.454]
    5_transfers_to_fresh_copy              0/3  FULL [49.46, 51.63, 48.14] vs ACC remainder [49.46, 51.63, 48.14]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.46, 51.63, 48.14]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.46, 51.63, 48.14] STORAGE_MATCHED [49.46, 51.63, 48.14] vs ACC remainder [49.46, 51.63, 48.14]
  top3_7a874306ab207e25
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [21, 19, 23] vs FRESH [21, 19, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1484.1, 1469.7, 1426.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.46, 51.63, 48.14] vs CODE_ONLY [49.46, 51.63, 48.14]
    4_scramble_or_reset_damages            0/3  eff ACC [21.45, 19.412, 23.454] SCR [21.45, 19.412, 23.454] RESET [21.45, 19.412, 23.454]
    5_transfers_to_fresh_copy              0/3  FULL [49.46, 51.63, 48.14] vs ACC remainder [49.46, 51.63, 48.14]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.46, 51.63, 48.14]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.46, 51.63, 48.14] STORAGE_MATCHED [49.46, 51.63, 48.14] vs ACC remainder [49.46, 51.63, 48.14]
  ancestor195_it299_50ddf29d9fedf7a7
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [21, 19, 23] vs FRESH [21, 19, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1484.1, 1469.7, 1426.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.46, 51.63, 48.14] vs CODE_ONLY [49.46, 51.63, 48.14]
    4_scramble_or_reset_damages            0/3  eff ACC [21.45, 19.412, 23.454] SCR [21.45, 19.412, 23.454] RESET [21.45, 19.412, 23.454]
    5_transfers_to_fresh_copy              0/3  FULL [49.46, 51.63, 48.14] vs ACC remainder [49.46, 51.63, 48.14]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.46, 51.63, 48.14]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.46, 51.63, 48.14] STORAGE_MATCHED [49.46, 51.63, 48.14] vs ACC remainder [49.46, 51.63, 48.14]
  contemp_e8bdba59c20aef1b
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [21, 19, 23] vs FRESH [21, 19, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1488.9, 1474.5, 1431.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.62, 51.8, 48.3] vs CODE_ONLY [49.62, 51.8, 48.3]
    4_scramble_or_reset_damages            0/3  eff ACC [21.45, 19.411, 23.454] SCR [21.45, 19.411, 23.454] RESET [21.45, 19.411, 23.454]
    5_transfers_to_fresh_copy              0/3  FULL [49.62, 51.8, 48.3] vs ACC remainder [49.62, 51.8, 48.3]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.62, 51.8, 48.3]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.62, 51.8, 48.3] STORAGE_MATCHED [49.62, 51.8, 48.3] vs ACC remainder [49.62, 51.8, 48.3]
  top1_d19ba9831f137eca
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 18, 24] vs FRESH [19, 18, 24]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1548.9, 1533.5, 1360.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.63, 51.63, 47.91] vs CODE_ONLY [51.63, 51.63, 47.91]
    4_scramble_or_reset_damages            0/3  eff ACC [19.446, 18.408, 24.45] SCR [19.446, 18.408, 24.45] RESET [19.446, 18.408, 24.45]
    5_transfers_to_fresh_copy              0/3  FULL [51.63, 51.63, 47.91] vs ACC remainder [51.63, 51.63, 47.91]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.63, 51.63, 47.91]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.63, 51.63, 47.91] STORAGE_MATCHED [51.63, 51.63, 47.91] vs ACC remainder [51.63, 51.63, 47.91]
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
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1580.4, 1529.9, 1482.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.68, 52.68, 49.82] vs CODE_ONLY [52.68, 52.68, 49.82]
    4_scramble_or_reset_damages            0/3  eff ACC [18.368, 18.401, 22.446] SCR [18.368, 18.401, 22.446] RESET [18.368, 18.401, 22.446]
    5_transfers_to_fresh_copy              0/3  FULL [52.68, 52.68, 49.82] vs ACC remainder [52.68, 52.68, 49.82]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.68, 52.68, 49.82]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.68, 52.68, 49.82] STORAGE_MATCHED [52.68, 52.68, 49.82] vs ACC remainder [52.68, 52.68, 49.82]
  ENUMERATE_VM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 18, 22] vs FRESH [18, 18, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1580.4, 1529.9, 1482.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.68, 52.68, 49.82] vs CODE_ONLY [52.68, 52.68, 49.82]
    4_scramble_or_reset_damages            0/3  eff ACC [18.368, 18.401, 22.446] SCR [18.368, 18.401, 22.446] RESET [18.368, 18.401, 22.446]
    5_transfers_to_fresh_copy              0/3  FULL [52.68, 52.68, 49.82] vs ACC remainder [52.68, 52.68, 49.82]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.68, 52.68, 49.82]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.68, 52.68, 49.82] STORAGE_MATCHED [52.68, 52.68, 49.82] vs ACC remainder [52.68, 52.68, 49.82]
  bestever_d9e5aeab69ffd965
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [13, 12, 22] vs FRESH [13, 12, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1539.0, 1542.2, 1499.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.46, 52.56, 49.7] vs CODE_ONLY [50.46, 52.56, 49.7]
    4_scramble_or_reset_damages            0/3  eff ACC [13.346, 12.324, 22.456] SCR [13.346, 12.324, 22.456] RESET [13.346, 12.324, 22.456]
    5_transfers_to_fresh_copy              0/3  FULL [50.46, 52.56, 49.7] vs ACC remainder [50.46, 52.56, 49.7]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.46, 52.56, 49.7]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.46, 52.56, 49.7] STORAGE_MATCHED [50.46, 52.56, 49.7] vs ACC remainder [50.46, 52.56, 49.7]
  ancestor98_it144_3cf01a2c4c7f14a0
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [13, 13, 21] vs FRESH [13, 13, 21]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1526.1, 1508.4, 1486.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.4, 52.4, 49.67] vs CODE_ONLY [52.4, 52.4, 49.67]
    4_scramble_or_reset_damages            0/3  eff ACC [13.344, 13.337, 21.434] SCR [13.344, 13.337, 21.434] RESET [13.344, 13.337, 21.434]
    5_transfers_to_fresh_copy              0/3  FULL [52.4, 52.4, 49.67] vs ACC remainder [52.4, 52.4, 49.67]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.4, 52.4, 49.67]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.4, 52.4, 49.67] STORAGE_MATCHED [52.4, 52.4, 49.67] vs ACC remainder [52.4, 52.4, 49.67]
  RANDOM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 6, 9] vs FRESH [6, 6, 9]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1491.8, 1515.0, 1485.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.21, 50.5, 48.99] vs CODE_ONLY [49.21, 50.5, 48.99]
    4_scramble_or_reset_damages            0/3  eff ACC [6.205, 6.235, 9.221] SCR [6.205, 6.235, 9.221] RESET [6.205, 6.235, 9.221]
    5_transfers_to_fresh_copy              0/3  FULL [49.21, 50.5, 48.99] vs ACC remainder [49.21, 50.5, 48.99]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.21, 50.5, 48.99]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.21, 50.5, 48.99] STORAGE_MATCHED [49.21, 50.5, 48.99] vs ACC remainder [49.21, 50.5, 48.99]
  contemp_6f0bbc91d719db89
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 1] vs FRESH [0, 0, 1]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1507.2, 1507.2, 1507.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.24, 50.24, 50.24] vs CODE_ONLY [50.24, 50.24, 50.24]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 1.179] SCR [0.163, 0.163, 1.179] RESET [0.163, 0.163, 1.179]
    5_transfers_to_fresh_copy              0/3  FULL [50.24, 50.24, 50.24] vs ACC remainder [50.24, 50.24, 50.24]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.24, 50.24, 50.24]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.24, 50.24, 50.24] STORAGE_MATCHED [50.24, 50.24, 50.24] vs ACC remainder [50.24, 50.24, 50.24]
  contemp_e29bb956874be9dc
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1501.2, 1501.2, 1501.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.04, 50.04, 50.04] vs CODE_ONLY [50.04, 50.04, 50.04]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 0.163] SCR [0.163, 0.163, 0.163] RESET [0.163, 0.163, 0.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.04, 50.04, 50.04] vs ACC remainder [50.04, 50.04, 50.04]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.04, 50.04, 50.04]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.04, 50.04, 50.04] STORAGE_MATCHED [50.04, 50.04, 50.04] vs ACC remainder [50.04, 50.04, 50.04]

MACHINERY OF top1_d19ba9831f137eca (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    1    0 |   0     0
    task  9:     0    0    0   10    0 |   0     0
    task 19:     0    0    0   20    0 |   0     0
    task 31:     0    0    0   32    0 |   0     0
    task 41:     0    0    0   42    0 |   0     0
    task 49:     0    0    0   50    0 |   0     0
  artifact events: 0 (create 0, delete 0, patch/append 0); invocations by block: {}; edges: 0
  adaptation curve ACC:   56 298 16 434 56 56 75 2060 31 258 118 16 434 434 56 177 177 16 298 68 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
  adaptation curve FRESH: 56 298 16 434 56 56 75 2060 31 258 118 16 434 434 56 177 177 16 298 68 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
  reuse_gain per task:    0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0

BASELINES ON SEARCH SUITE (crius/runs/baselines_c1b): effA effF effR effS  succA  interA interF  reuse_gain  blocks
  ENUMERATE_C1_seed301     21.473 21.473 21.473 21.473   21    3358   3358        0.0    0
  ENUMERATE_C1_seed302     19.412 19.412 19.412 19.412   19   10771  10771        0.0    0
  ENUMERATE_C1_seed303     22.479 22.479 22.479 22.479   22    2548   2548        0.0    0
  ENUMERATE_VM_C1_seed301  21.471 21.471 21.471 21.471   21    3358   3358        0.0    0
  ENUMERATE_VM_C1_seed302  19.397 19.397 19.397 19.397   19   12109  12109        0.0    0
  ENUMERATE_VM_C1_seed303  22.471 22.471 22.471 22.471   22    3428   3428        0.0    0
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
  RANDOM_C1_seed303        12.283 12.283 12.283 12.283   12   26477  26477        0.0    0
  TABLE_MEMO_C1_seed301    21.472 21.473 21.473 21.472   21    3358   3358      -15.9    0
  TABLE_MEMO_C1_seed302    19.412 19.412 19.412 19.412   19   10771  10771      -13.8    0
  TABLE_MEMO_C1_seed303    22.479 22.479 22.479 22.479   22    2548   2548      -16.7    0

