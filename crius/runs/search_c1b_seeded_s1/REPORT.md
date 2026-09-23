CRIUS CAMPAIGN 0 REPORT  run=search_c1b_seeded_s1  arm=seeded
code_commit=6364d6994 dirty=True config_hash=bbf684cd638167f2 world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  23.4146   22.0204         8.9720        40          4
    26  22.4290   21.7893        13.2595        51         48
    51  22.4477   21.6974        12.5761        49         88
    76  26.4764   26.4764        20.5971        60        130
   101  21.4142   21.3673        17.8454        59        164
   126  24.4687   23.9679        17.1939        61        194
   151  23.4355   23.4355        12.7911        45        235
   176  25.4543   22.8397        13.5314        34        292
   201  21.4592   21.4590        14.2639        34        331
   226  20.4634   20.4634        12.0727        25        371
   251  26.4664   24.7240        16.5010        30        406
   276  22.4067   20.3774        13.2967        59        439
   300  22.4273   21.8082        12.7368        61        462
  candidates evaluated: 7208   best_ever 34.4795 (76efdf61a9ca4e18)  wall 462s

BEST PROGRAM 76efdf61a9ca4e18 (len 49, iteration 37, modification delete@27+const@2+arg@7.0)
  search seed 101037: fit 34.4795 succ 34/50 inter 2416 steps 10229 ws_cost 0 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [77.187, 1.0], "B": [64.918, 1.0], "C": [28.799, 0.667], "D": [40.347, 0.3], "E": [43.523, 0.375]}
  listing:
      0  INPUT          R1, num_ops
      1  CONST          R5, 5
      2  CONST          R0, 23
      3  MOV            R2, R1
      4  JMP            12
      5  BRNZ           R0, 17
      6  LT             R3, R0, R2
      7  BRZ            R1, 11
      8  ACT            R2
      9  ADD            R0, R0, R5
     10  MOD            R3, R0, R1
     11  CONST          R1, 0
     12  MUL            R2, R1, R1
     13  ADD            R0, R0, R5
     14  BRZ            R3, 34
     15  ADD            R0, R0, R5
     16  JMP            14
     17  ADD            R0, R0, R5
     18  JMP            14
     19  CONST          R3, -1
     20  ACT            R7
     21  MOD            R3, R0, R1
     22  ACT            R3
     23  CONST          R3, 0
     24  JMP            6
     25  ACT            R3
     26  BRNZ           R6, 14
     27  MOD            R3, R0, R1
     28  SUB            R0, R7, R5
     29  DIV            R4, R0, R1
     30  MOD            R3, R4, R1
     31  BLK_NEW        R5
     32  ADD            R0, R0, R5
     33  JMP            14
     34  CONST          R3, -2
     35  MUL            R2, R2, R1
     36  LT             R3, R0, R4
     37  ACT            R1
     38  MOD            R3, R0, R1
     39  ACT            R3
     40  DIV            R4, R0, R1
     41  MOD            R3, R4, R1
     42  ACT            R3
     43  DIV            R4, R4, R1
     44  MOD            R3, R4, R1
     45  ACT            R3
     46  ADD            R0, R0, R5
     47  JMP            36
     48  HALT           
  ancestry (21 steps, newest first): iteration/fitness/modification
    it   37  34.4795  len 49  delete@27+const@2+arg@7.0
    it   35  25.4134  len 50  delete@14
    it   33  24.4271  len 51  replace@27+arg@8.0
    it   30  22.4404  len 51  duplicate@33+1->13+const@20
    it   29  24.4622  len 50  swap@10,24
    it   27  25.4726  len 50  delete@36
    it   25  20.3970  len 51  const@1+const@23
    it   24  20.4197  len 51  const@1
    it   23  19.3017  len 51  duplicate@37+3->24+const@23+arg@38.2
    it   22  20.4352  len 48  insert@5
    it   21  15.3471  len 47  delete@35
    it   20  23.4230  len 48  replace@28
    it   19  22.4666  len 48  const@2
    it   18  23.4151  len 48  replace@25+arg@23.0+const@18
    it   16  16.3575  len 48  arg@10.0
    ... 7 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7316.0    4.3   74.7
  contemp_f4d0efb14099e943    22.773  22.773  22.773  22.773  22.3  22.3     7199     7199       0.0    0.0    0.0
  ancestor94_it152_439cefba9  22.115  22.115  22.115  22.115  21.7  21.7     6136     6136       0.0    0.0    0.0
  contemp_d15b4a5a0763b57d    22.088  22.088  22.088  22.088  21.7  21.7     9359     9359       0.0    0.0    0.0
  contemp_c961211eb5fd86a1    21.776  21.776  21.776  21.776  21.3  21.3     6843     6843       0.0    0.0    0.0
  bestever_76efdf61a9ca4e18   21.425  21.425  21.425  21.425  21.0  21.0     8818     8818       0.0    0.0    0.0
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.3    2.7    1.7
  top1_83472f066ff4a2a5       20.062  20.062  20.062  20.062  19.7  19.7    12479    12479       0.0    0.0    0.0
  top2_20ee2e8103962911       20.062  20.062  20.062  20.062  19.7  19.7    12479    12479       0.0    0.0    0.0
  top3_63dea9cb63296b0d       20.062  20.062  20.062  20.062  19.7  19.7    12499    12499       0.0    0.0    0.0
  ancestor186_it298_2447cf36  20.062  20.062  20.062  20.062  19.7  19.7    12499    12499       0.0    0.0    0.0
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ancestor1_it0_0875253d162c  19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       0.0    0.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       0.0    0.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.00/ 455.13   14.90/ 539.10   21.11/  47.94   33.21/  48.94   40.07/  50.52
  contemp_f4d0efb14099e943    306.64/ 306.64  289.00/ 289.00   48.25/  48.25   50.96/  50.96   49.90/  49.90
  ancestor94_it152_439cefba9  224.64/ 224.64  261.09/ 261.09   49.53/  49.53   51.07/  51.07   50.13/  50.13
  contemp_d15b4a5a0763b57d    396.51/ 396.51  421.28/ 421.28   49.15/  49.15   50.66/  50.66   50.30/  50.30
  contemp_c961211eb5fd86a1    282.82/ 282.82  272.35/ 272.35   50.69/  50.69   50.34/  50.34   51.78/  51.78
  bestever_76efdf61a9ca4e18   322.28/ 322.28  443.96/ 443.96   49.23/  49.23   50.60/  50.60   52.09/  52.09
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.13/ 443.81  528.11/ 527.79   47.93/  47.89   48.85/  48.88   50.42/  50.46
  top1_83472f066ff4a2a5       481.45/ 481.45  658.08/ 658.08   48.87/  48.87   50.46/  50.46   51.77/  51.77
  top2_20ee2e8103962911       481.47/ 481.47  658.10/ 658.10   48.89/  48.89   50.48/  50.48   51.79/  51.79
  top3_63dea9cb63296b0d       482.40/ 482.40  658.96/ 658.96   48.97/  48.97   50.48/  50.48   51.75/  51.75
  ancestor186_it298_2447cf36  482.39/ 482.39  658.95/ 658.95   48.96/  48.96   50.47/  50.47   51.74/  51.74
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ancestor1_it0_0875253d162c  494.04/ 494.04  523.26/ 523.26   49.99/  49.99   50.96/  50.96   52.68/  52.68
  ENUMERATE_VM_C1             494.04/ 494.04  523.26/ 523.26   49.99/  49.99   50.96/  50.96   52.68/  52.68
  RANDOM_C1                  1661.96/1661.96 1626.54/1626.54   50.44/  50.44   50.50/  50.50   48.40/  48.40

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  contemp_f4d0efb14099e943       5/36    47     2/30    49     0/12    50     1/12    46    29/30   297    30/30   280
  ancestor94_it152_439cefba9     3/36    48     1/30    49     1/12    47     0/12    50    30/30   217    30/30   252
  contemp_d15b4a5a0763b57d       3/36    47     1/30    49     1/12    47     0/12    50    30/30   384    30/30   408
  contemp_c961211eb5fd86a1       2/36    49     2/30    49     0/12    50     0/12    50    30/30   274    30/30   263
  bestever_76efdf61a9ca4e18      4/36    47     1/30    49     0/12    50     0/12    50    30/30   310    28/30   427
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  top1_83472f066ff4a2a5          4/36    47     1/30    49     0/12    50     0/12    50    28/30   466    26/30   637
  top2_20ee2e8103962911          4/36    47     1/30    49     0/12    50     0/12    50    28/30   466    26/30   637
  top3_63dea9cb63296b0d          4/36    47     1/30    49     0/12    50     0/12    50    28/30   467    26/30   638
  ancestor186_it298_2447cf36     4/36    47     1/30    49     0/12    50     0/12    50    28/30   467    26/30   638
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ancestor1_it0_0875253d162c     2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.26    49.53    36.26    36.26    49.53    49.53    49.53   4.0
  contemp_f4d0efb14099e943      50.49       --    50.49    50.49    50.49    50.49    50.49   0.0
  ancestor94_it152_439cefba9    50.65       --    50.65    50.65    50.65    50.65    50.65   0.0
  contemp_d15b4a5a0763b57d      50.50       --    50.50    50.50    50.50    50.50    50.50   0.0
  contemp_c961211eb5fd86a1      50.98       --    50.98    50.98    50.98    50.98    50.98   0.0
  bestever_76efdf61a9ca4e18     51.26       --    51.26    51.26    51.26    51.26    51.26   0.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.55    49.55    49.55    49.55    49.55    49.55    49.55   1.0
  top1_83472f066ff4a2a5         51.04       --    51.04    51.04    51.04    51.04    51.04   0.0
  top2_20ee2e8103962911         51.06       --    51.06    51.06    51.06    51.06    51.06   0.0
  top3_63dea9cb63296b0d         51.04       --    51.04    51.04    51.04    51.04    51.04   0.0
  ancestor186_it298_2447cf36    51.03       --    51.03    51.03    51.03    51.03    51.03   0.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ancestor1_it0_0875253d162c    51.73       --    51.73    51.73    51.73    51.73    51.73   0.0
  ENUMERATE_VM_C1               51.73       --    51.73    51.73    51.73    51.73    51.73   0.0
  RANDOM_C1                     49.57       --    49.57    49.57    49.57    49.57    49.57   0.0

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
  contemp_f4d0efb14099e943
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [21, 23, 23] vs FRESH [21, 23, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1508.1, 1479.3, 1476.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.28, 51.41, 50.78] vs CODE_ONLY [49.28, 51.41, 50.78]
    4_scramble_or_reset_damages            0/3  eff ACC [21.451, 23.415, 23.452] SCR [21.451, 23.415, 23.452] RESET [21.451, 23.415, 23.452]
    5_transfers_to_fresh_copy              0/3  FULL [49.28, 51.41, 50.78] vs ACC remainder [49.28, 51.41, 50.78]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.28, 51.41, 50.78]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.28, 51.41, 50.78] STORAGE_MATCHED [49.28, 51.41, 50.78] vs ACC remainder [49.28, 51.41, 50.78]
  ancestor94_it152_439cefba927fd226
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 22, 23] vs FRESH [20, 22, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1555.8, 1475.0, 1487.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.86, 49.56, 50.54] vs CODE_ONLY [51.86, 49.56, 50.54]
    4_scramble_or_reset_damages            0/3  eff ACC [20.441, 22.441, 23.463] SCR [20.441, 22.441, 23.463] RESET [20.441, 22.441, 23.463]
    5_transfers_to_fresh_copy              0/3  FULL [51.86, 49.56, 50.54] vs ACC remainder [51.86, 49.56, 50.54]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.86, 49.56, 50.54]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.86, 49.56, 50.54] STORAGE_MATCHED [51.86, 49.56, 50.54] vs ACC remainder [51.86, 49.56, 50.54]
  contemp_d15b4a5a0763b57d
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [21, 21, 23] vs FRESH [21, 21, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1517.7, 1538.4, 1440.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.81, 51.76, 49.93] vs CODE_ONLY [49.81, 51.76, 49.93]
    4_scramble_or_reset_damages            0/3  eff ACC [21.416, 21.412, 23.436] SCR [21.416, 21.412, 23.436] RESET [21.416, 21.412, 23.436]
    5_transfers_to_fresh_copy              0/3  FULL [49.81, 51.76, 49.93] vs ACC remainder [49.81, 51.76, 49.93]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.81, 51.76, 49.93]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.81, 51.76, 49.93] STORAGE_MATCHED [49.81, 51.76, 49.93] vs ACC remainder [49.81, 51.76, 49.93]
  contemp_c961211eb5fd86a1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 22, 22] vs FRESH [20, 22, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1553.4, 1519.3, 1504.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.78, 50.63, 50.52] vs CODE_ONLY [51.78, 50.63, 50.52]
    4_scramble_or_reset_damages            0/3  eff ACC [20.442, 22.439, 22.447] SCR [20.442, 22.439, 22.447] RESET [20.442, 22.439, 22.447]
    5_transfers_to_fresh_copy              0/3  FULL [51.78, 50.63, 50.52] vs ACC remainder [51.78, 50.63, 50.52]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.78, 50.63, 50.52]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.78, 50.63, 50.52] STORAGE_MATCHED [51.78, 50.63, 50.52] vs ACC remainder [51.78, 50.63, 50.52]
  bestever_76efdf61a9ca4e18
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [22, 19, 22] vs FRESH [22, 19, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1518.0, 1539.9, 1482.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.09, 52.09, 49.61] vs CODE_ONLY [52.09, 52.09, 49.61]
    4_scramble_or_reset_damages            0/3  eff ACC [22.434, 19.41, 22.432] SCR [22.434, 19.41, 22.432] RESET [22.434, 19.41, 22.432]
    5_transfers_to_fresh_copy              0/3  FULL [52.09, 52.09, 49.61] vs ACC remainder [52.09, 52.09, 49.61]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.09, 52.09, 49.61]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.09, 52.09, 49.61] STORAGE_MATCHED [52.09, 52.09, 49.61] vs ACC remainder [52.09, 52.09, 49.61]
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
  top1_83472f066ff4a2a5
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 19, 22] vs FRESH [18, 19, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1553.1, 1498.4, 1464.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.77, 51.77, 49.59] vs CODE_ONLY [51.77, 51.77, 49.59]
    4_scramble_or_reset_damages            0/3  eff ACC [18.376, 19.394, 22.416] SCR [18.376, 19.394, 22.416] RESET [18.376, 19.394, 22.416]
    5_transfers_to_fresh_copy              0/3  FULL [51.77, 51.77, 49.59] vs ACC remainder [51.77, 51.77, 49.59]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.77, 51.77, 49.59]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.77, 51.77, 49.59] STORAGE_MATCHED [51.77, 51.77, 49.59] vs ACC remainder [51.77, 51.77, 49.59]
  top2_20ee2e8103962911
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 19, 22] vs FRESH [18, 19, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1553.7, 1499.0, 1464.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.79, 51.79, 49.61] vs CODE_ONLY [51.79, 51.79, 49.61]
    4_scramble_or_reset_damages            0/3  eff ACC [18.376, 19.394, 22.416] SCR [18.376, 19.394, 22.416] RESET [18.376, 19.394, 22.416]
    5_transfers_to_fresh_copy              0/3  FULL [51.79, 51.79, 49.61] vs ACC remainder [51.79, 51.79, 49.61]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.79, 51.79, 49.61]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.79, 51.79, 49.61] STORAGE_MATCHED [51.79, 51.79, 49.61] vs ACC remainder [51.79, 51.79, 49.61]
  top3_63dea9cb63296b0d
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 19, 22] vs FRESH [18, 19, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1552.5, 1499.9, 1466.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.75, 51.75, 49.63] vs CODE_ONLY [51.75, 51.75, 49.63]
    4_scramble_or_reset_damages            0/3  eff ACC [18.376, 19.393, 22.415] SCR [18.376, 19.393, 22.415] RESET [18.376, 19.393, 22.415]
    5_transfers_to_fresh_copy              0/3  FULL [51.75, 51.75, 49.63] vs ACC remainder [51.75, 51.75, 49.63]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.75, 51.75, 49.63]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.75, 51.75, 49.63] STORAGE_MATCHED [51.75, 51.75, 49.63] vs ACC remainder [51.75, 51.75, 49.63]
  ancestor186_it298_2447cf3613d7c2df
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 19, 22] vs FRESH [18, 19, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1552.2, 1499.6, 1466.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.74, 51.74, 49.62] vs CODE_ONLY [51.74, 51.74, 49.62]
    4_scramble_or_reset_damages            0/3  eff ACC [18.376, 19.393, 22.415] SCR [18.376, 19.393, 22.415] RESET [18.376, 19.393, 22.415]
    5_transfers_to_fresh_copy              0/3  FULL [51.74, 51.74, 49.62] vs ACC remainder [51.74, 51.74, 49.62]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.74, 51.74, 49.62]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.74, 51.74, 49.62] STORAGE_MATCHED [51.74, 51.74, 49.62] vs ACC remainder [51.74, 51.74, 49.62]
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
  RANDOM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 6, 9] vs FRESH [6, 6, 9]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1491.8, 1515.0, 1485.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.21, 50.5, 48.99] vs CODE_ONLY [49.21, 50.5, 48.99]
    4_scramble_or_reset_damages            0/3  eff ACC [6.205, 6.235, 9.221] SCR [6.205, 6.235, 9.221] RESET [6.205, 6.235, 9.221]
    5_transfers_to_fresh_copy              0/3  FULL [49.21, 50.5, 48.99] vs ACC remainder [49.21, 50.5, 48.99]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.21, 50.5, 48.99]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.21, 50.5, 48.99] STORAGE_MATCHED [49.21, 50.5, 48.99] vs ACC remainder [49.21, 50.5, 48.99]

MACHINERY OF top1_83472f066ff4a2a5 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     1    0    0    0    1 |   0     0
    task  9:    10    0    0    0   10 |   0     0
    task 19:    20    0    0    0   20 |   0     0
    task 31:    32    0    0    0   32 |   0     0
    task 41:    42    0    0    0   42 |   0     0
    task 49:    50    0    0    0   50 |   0     0
  artifact events: 0 (create 0, delete 0, patch/append 0); invocations by block: {}; edges: 0
  adaptation curve ACC:   1367 66 366 851 1136 193 88 482 180 68 195 366 851 851 1367 2067 2067 364 66 692 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
  adaptation curve FRESH: 1367 66 366 851 1136 193 88 482 180 68 195 366 851 851 1367 2067 2067 364 66 692 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
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

