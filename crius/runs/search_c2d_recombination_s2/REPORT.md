CRIUS CAMPAIGN 0 REPORT  run=search_c2d_recombination_s2  arm=recombination
code_commit=52c58d0d4 dirty=True config_hash=7ab056c39e1821fd world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  22.9741   21.7861         8.9307        46         16
    26  21.4314   21.4312        11.4343        55        167
    51  20.4284   20.4284         9.4840        47        313
    76  23.9380   23.9377        15.3556        68        461
   101  24.4054   20.6440        15.4919        80        574
   126  23.4302   23.4302        18.3273        82        684
   151  23.4140   23.4140        18.8622        74        794
   176  23.4379   21.6644        16.0404        77        890
   201  20.3838   20.3837        15.3301        60        966
   226  20.4115   19.9372        10.6692        50       1050
   251  23.9662   23.7162        11.6731        47       1139
   276  23.9622   23.9619        13.6481        42       1224
   300  21.9624   21.4595        10.5073        37       1325
  candidates evaluated: 7208   best_ever 27.9768 (0bd52f90add68bf8)  wall 1325s

BEST PROGRAM 0bd52f90add68bf8 (len 56, iteration 31, modification replace@22+splice@18<-donor[42:47]:PART:P_PLAN)
  search seed 2010310: fit 23.4735 succ 23/50 inter 3080 steps 17307 ws_cost 181 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [95.264, 1.0], "B": [82.523, 1.0], "C": [46.978, 0.167], "D": [52.07, 0.0], "E": [49.071, 0.125]}
  search seed 2010311: fit 32.4801 succ 32/50 inter 2282 steps 15874 ws_cost 181 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [68.602, 1.0], "B": [61.101, 1.0], "C": [35.254, 0.417], "D": [39.039, 0.4], "E": [41.51, 0.375]}
  listing:
      0  INPUT          R1, num_ops
      1  CONST          R5, 1
      2  BRZ            R3, 25
      3  ACT            R1
      4  BLK_INVOKE     R7
      5  LT             R3, R0, R2
      6  DIV            R4, R0, R1
      7  MOD            R3, R4, R1
      8  ADD            R0, R0, R5
      9  VGET           R7, R5, R2
     10  DIV            R3, R5, R0
     11  ACT            R3
     12  ACT            R1
     13  ACT            R0
     14  ADD            R0, R0, R5
     15  JMP            11
     16  WS_SLEN        R4, R5
     17  MUL            R2, R1, R1
     18  MUL            R2, R1, R1
     19  MUL            R2, R2, R1
     20  LT             R3, R0, R2
     21  BRZ            R3, 57
     22  ACT            R1
     23  LT             R3, R0, R2
     24  BRZ            R3, 42
     25  ACT            R1
     26  WS_ALLOC       R2, R2
     27  WS_REC_GET     R4, R5, R3
     28  ACT            R3
     29  DIV            R4, R0, R1
     30  ACT            R3
     31  ADD            R0, R0, R5
     32  JMP            41
     33  WS_SLEN        R5, R1
     34  VGET           R7, R5, R2
     35  DIV            R3, R5, R0
     36  ACT            R3
     37  MOD            R3, R4, R1
     38  JMP            11
     39  ADD            R0, R0, R5
     40  WS_LINK        R6, R3, R1
     41  JMP            23
     42  MUL            R2, R1, R1
     43  LT             R3, R0, R2
     44  ACT            R1
     45  MOD            R3, R0, R1
     46  ACT            R3
     47  DIV            R4, R0, R1
     48  MOD            R3, R4, R1
     49  ACT            R3
     50  DIV            R4, R4, R1
     51  MOD            R3, R4, R1
     52  ACT            R3
     53  ADD            R0, R0, R5
     54  JMP            43
     55  BLK_INVOKE     R5
  ancestry (15 steps, newest first): iteration/fitness/modification
    it   31  27.9768  len 56  replace@22+splice@18<-donor[42:47]:PART:P_PLAN
    it   29  22.4257  len 51  insert@29+delete@16+delete@38
    it   28  22.4248  len 52  delete@40
    it   27  25.8997  len 53  swap@5,11+duplicate@9+3->29
    it   25  22.9699  len 50  replace@22+insert@32
    it   20  21.4266  len 49  const@16
    it   18  22.4076  len 49  replace@30+swap@30,9
    it   17  23.9338  len 49  duplicate@41+3->25+const@16+insert@23
    it   13  22.4224  len 45  insert@17
    it   12  22.9395  len 44  const@16
    it   11  23.4395  len 44  replace@4+delete@28
    it    8  21.9155  len 45  delete@2
    it    4  21.9543  len 46  replace@11
    it    1  22.9741  len 46  arg@2.1+replace@37+splice@3<-donor[13:21]:9cd16c9471ef698c
    it    0  4.0461  len 38  const@2+delete@5
    ... 1 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7315.4    5.3   74.7
  top2_c4cfc03b70faa9c3       22.116  22.115  21.782  22.116  21.7  21.7     6013     6093      86.8    1.0    0.0
  top3_a9e4cabfcd465e96       22.116  22.115  21.782  22.116  21.7  21.7     6013     6093      86.8    1.0    0.0
  contemp_b4f709313a2bd303    22.116  22.115  21.782  22.116  21.7  21.7     6013     6093      86.8    1.0    0.0
  top1_66871687158cfab1       22.115  22.115  22.115  22.115  21.7  21.7     6093     6093       7.1    1.0    0.0
  ancestor117_it291_3e9aceca  21.762  21.429  21.762  21.762  21.3  21.0     8365     8379      17.0    1.0    0.0
  ancestor59_it114_8e3bf733d  21.762  21.762  21.762  21.762  21.3  21.3     8420     8380     -36.7    1.0    0.0
  contemp_23720e14bfde0595    21.762  21.428  21.762  21.762  21.3  21.0     8365     8379      17.0    1.0    0.0
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.9    3.7    1.7
  bestever_0bd52f90add68bf8   19.746  19.746  19.746  19.746  19.3  19.3    10242    10242       5.6    1.0    0.0
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ancestor1_it0_0875253d162c  19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0
  contemp_f3d72b942df45120     0.674   1.014   0.674   0.674   0.7   1.0      150      149    -796.6    1.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.02/ 455.13   14.92/ 539.10   21.12/  47.94   33.22/  48.94   40.08/  50.52
  top2_c4cfc03b70faa9c3       220.02/ 224.72  257.98/ 261.18   49.37/  49.72   51.07/  51.26   50.11/  50.33
  top3_a9e4cabfcd465e96       220.02/ 224.72  257.98/ 261.18   49.37/  49.72   51.07/  51.26   50.11/  50.33
  contemp_b4f709313a2bd303    220.02/ 224.72  257.98/ 261.18   49.37/  49.72   51.07/  51.26   50.11/  50.33
  top1_66871687158cfab1       224.59/ 224.72  261.03/ 261.18   49.57/  49.72   51.11/  51.26   50.18/  50.33
  ancestor117_it291_3e9aceca  386.89/ 389.34  333.08/ 332.85   49.95/  50.24   51.48/  50.43   51.02/  51.24
  ancestor59_it114_8e3bf733d  387.13/ 388.49  339.34/ 333.17   49.56/  50.04   51.30/  51.58   50.78/  51.12
  contemp_23720e14bfde0595    389.53/ 392.00  335.37/ 335.14   50.29/  50.58   51.83/  50.76   51.36/  51.58
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.14/ 443.81  528.13/ 527.79   47.94/  47.89   48.86/  48.88   50.43/  50.46
  bestever_0bd52f90add68bf8   457.74/ 457.98  459.73/ 459.65   49.85/  49.96   50.61/  50.76   52.07/  52.22
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ancestor1_it0_0875253d162c  495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  ENUMERATE_VM_C1             495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  RANDOM_C1                  1662.62/1662.62 1627.07/1627.07   50.50/  50.50   50.50/  50.50   48.56/  48.56
  contemp_f3d72b942df45120   2400.03/2320.24 2320.16/2320.21  437.66/ 450.07  450.02/ 435.17  450.02/ 450.07

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  top2_c4cfc03b70faa9c3          3/36    47     1/30    49     1/12    46     0/12    50    30/30   210    30/30   247
  top3_a9e4cabfcd465e96          3/36    47     1/30    49     1/12    46     0/12    50    30/30   210    30/30   247
  contemp_b4f709313a2bd303       3/36    47     1/30    49     1/12    46     0/12    50    30/30   210    30/30   247
  top1_66871687158cfab1          3/36    48     1/30    49     1/12    46     0/12    50    30/30   215    30/30   250
  ancestor117_it291_3e9aceca     4/36    48     1/30    49     1/12    48     0/12    50    29/30   371    29/30   319
  ancestor59_it114_8e3bf733d     4/36    47     1/30    49     1/12    48     0/12    50    29/30   371    29/30   325
  contemp_23720e14bfde0595       4/36    48     1/30    49     1/12    48     0/12    50    29/30   371    29/30   319
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  bestever_0bd52f90add68bf8      2/36    48     1/30    49     0/12    50     0/12    50    27/30   438    28/30   440
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ancestor1_it0_0875253d162c     2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610
  contemp_f3d72b942df45120       1/36     3     0/30     3     0/12     3     0/12     3     0/30     3     1/30     3

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.27    49.53    36.27    36.27    49.53    49.53    49.53   5.0
  top2_c4cfc03b70faa9c3         50.64    50.65    50.66    50.64    50.67    50.67    50.67   1.0
  top3_a9e4cabfcd465e96         50.64    50.65    50.66    50.64    50.67    50.67    50.67   1.0
  contemp_b4f709313a2bd303      50.64    50.65    50.66    50.64    50.67    50.67    50.67   1.0
  top1_66871687158cfab1         50.70    50.71    50.70    50.70    50.71    50.71    50.71   1.0
  ancestor117_it291_3e9aceca    51.28    51.28    51.29    51.28    51.30    51.30    51.30   1.0
  ancestor59_it114_8e3bf733d    51.07    51.07    51.05    51.07    51.05    51.05    51.05   1.0
  contemp_23720e14bfde0595      51.62    51.63    51.63    51.62    51.64    51.64    51.64   1.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.56    49.55    49.56    49.56    49.55    49.55    49.55   2.0
  bestever_0bd52f90add68bf8     51.26    51.27    51.33    51.26    51.34    51.34    51.34   1.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ancestor1_it0_0875253d162c    51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  ENUMERATE_VM_C1               51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  RANDOM_C1                     49.64       --    49.64    49.64    49.64    49.64    49.64   0.0
  contemp_f3d72b942df45120     450.02   450.02   450.02   450.02   450.03   850.07   450.03   1.0

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
  top2_c4cfc03b70faa9c3
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 22, 23] vs FRESH [20, 22, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [2.7, 8.8, 12.0] vs 5% of FRESH cost [1561.8, 1480.7, 1493.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.97, 49.49, 50.47] vs CODE_ONLY [51.99, 49.51, 50.49]
    4_scramble_or_reset_damages            0/3  eff ACC [20.442, 22.441, 23.464] SCR [20.442, 22.441, 23.464] RESET [20.442, 21.441, 23.464]
    5_transfers_to_fresh_copy              0/3  FULL [51.97, 49.49, 50.47] vs ACC remainder [51.97, 49.49, 50.47]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.98, 49.5, 50.48] vs ACC remainder [51.97, 49.49, 50.47]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.99, 49.51, 50.49] STORAGE_MATCHED [51.99, 49.51, 50.49] vs ACC remainder [51.97, 49.49, 50.47]
  top3_a9e4cabfcd465e96
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 22, 23] vs FRESH [20, 22, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [2.7, 8.8, 12.0] vs 5% of FRESH cost [1561.8, 1480.7, 1493.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.97, 49.49, 50.47] vs CODE_ONLY [51.99, 49.51, 50.49]
    4_scramble_or_reset_damages            0/3  eff ACC [20.442, 22.441, 23.464] SCR [20.442, 22.441, 23.464] RESET [20.442, 21.441, 23.464]
    5_transfers_to_fresh_copy              0/3  FULL [51.97, 49.49, 50.47] vs ACC remainder [51.97, 49.49, 50.47]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.98, 49.5, 50.48] vs ACC remainder [51.97, 49.49, 50.47]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.99, 49.51, 50.49] STORAGE_MATCHED [51.99, 49.51, 50.49] vs ACC remainder [51.97, 49.49, 50.47]
  contemp_b4f709313a2bd303
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 22, 23] vs FRESH [20, 22, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [2.7, 8.8, 12.0] vs 5% of FRESH cost [1561.8, 1480.7, 1493.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.97, 49.49, 50.47] vs CODE_ONLY [51.99, 49.51, 50.49]
    4_scramble_or_reset_damages            0/3  eff ACC [20.442, 22.441, 23.464] SCR [20.442, 22.441, 23.464] RESET [20.442, 21.441, 23.464]
    5_transfers_to_fresh_copy              0/3  FULL [51.97, 49.49, 50.47] vs ACC remainder [51.97, 49.49, 50.47]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.98, 49.5, 50.48] vs ACC remainder [51.97, 49.49, 50.47]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.99, 49.51, 50.49] STORAGE_MATCHED [51.99, 49.51, 50.49] vs ACC remainder [51.97, 49.49, 50.47]
  top1_66871687158cfab1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 22, 23] vs FRESH [20, 22, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.5] vs 5% of FRESH cost [1561.8, 1480.7, 1493.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.91, 49.6, 50.58] vs CODE_ONLY [51.92, 49.61, 50.59]
    4_scramble_or_reset_damages            0/3  eff ACC [20.441, 22.441, 23.463] SCR [20.441, 22.441, 23.463] RESET [20.441, 22.441, 23.463]
    5_transfers_to_fresh_copy              0/3  FULL [51.91, 49.6, 50.58] vs ACC remainder [51.91, 49.6, 50.58]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.92, 49.61, 50.59] vs ACC remainder [51.91, 49.6, 50.58]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.92, 49.61, 50.59] STORAGE_MATCHED [51.92, 49.61, 50.59] vs ACC remainder [51.91, 49.6, 50.58]
  ancestor117_it291_3e9acecabbfacdfb
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 22, 22] vs FRESH [19, 22, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [3.8, 8.8, -28.5] vs 5% of FRESH cost [1542.0, 1517.0, 1492.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.7, 51.97, 51.16] vs CODE_ONLY [50.72, 51.99, 51.19]
    4_scramble_or_reset_damages            0/3  eff ACC [20.426, 22.403, 22.458] SCR [20.426, 22.403, 22.458] RESET [20.426, 22.403, 22.458]
    5_transfers_to_fresh_copy              0/3  FULL [50.7, 51.97, 51.16] vs ACC remainder [50.7, 51.97, 51.16]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [50.71, 51.98, 51.17] vs ACC remainder [50.7, 51.97, 51.16]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.72, 51.99, 51.19] STORAGE_MATCHED [50.72, 51.99, 51.19] vs ACC remainder [50.7, 51.97, 51.16]
  ancestor59_it114_8e3bf733dc32e477
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 22, 22] vs FRESH [20, 22, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [14.8, 4.4, 14.8] vs 5% of FRESH cost [1541.2, 1511.1, 1523.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.37, 51.99, 50.83] vs CODE_ONLY [50.36, 51.98, 50.82]
    4_scramble_or_reset_damages            0/3  eff ACC [20.423, 22.404, 22.459] SCR [20.423, 22.404, 22.459] RESET [20.423, 22.404, 22.459]
    5_transfers_to_fresh_copy              0/3  FULL [50.37, 51.99, 50.83] vs ACC remainder [50.37, 51.99, 50.83]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [50.38, 52.0, 50.84] vs ACC remainder [50.37, 51.99, 50.83]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.36, 51.98, 50.82] STORAGE_MATCHED [50.36, 51.98, 50.82] vs ACC remainder [50.37, 51.99, 50.83]
  contemp_23720e14bfde0595
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 22, 22] vs FRESH [19, 22, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [3.7, 8.9, -28.7] vs 5% of FRESH cost [1552.2, 1527.2, 1502.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.04, 52.31, 51.5] vs CODE_ONLY [51.06, 52.34, 51.53]
    4_scramble_or_reset_damages            0/3  eff ACC [20.426, 22.403, 22.458] SCR [20.426, 22.403, 22.458] RESET [20.426, 22.403, 22.458]
    5_transfers_to_fresh_copy              0/3  FULL [51.04, 52.31, 51.5] vs ACC remainder [51.04, 52.31, 51.5]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.05, 52.32, 51.51] vs ACC remainder [51.04, 52.31, 51.5]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.06, 52.34, 51.53] STORAGE_MATCHED [51.06, 52.34, 51.53] vs ACC remainder [51.04, 52.31, 51.5]
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
  bestever_0bd52f90add68bf8
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 18, 22] vs FRESH [18, 18, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.1, 4.0, 3.9] vs 5% of FRESH cost [1566.6, 1519.6, 1488.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.07, 52.07, 49.64] vs CODE_ONLY [52.17, 52.17, 49.68]
    4_scramble_or_reset_damages            0/3  eff ACC [18.383, 18.413, 22.443] SCR [18.383, 18.413, 22.443] RESET [18.383, 18.413, 22.443]
    5_transfers_to_fresh_copy              0/3  FULL [52.07, 52.07, 49.64] vs ACC remainder [52.07, 52.07, 49.64]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.08, 52.08, 49.65] vs ACC remainder [52.07, 52.07, 49.64]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.17, 52.17, 49.68] STORAGE_MATCHED [52.17, 52.17, 49.68] vs ACC remainder [52.07, 52.07, 49.64]
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
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.3] vs 5% of FRESH cost [1584.9, 1536.3, 1492.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.68, 52.68, 50.04] vs CODE_ONLY [52.69, 52.69, 50.05]
    4_scramble_or_reset_damages            0/3  eff ACC [18.368, 18.4, 22.445] SCR [18.368, 18.4, 22.445] RESET [18.368, 18.4, 22.445]
    5_transfers_to_fresh_copy              0/3  FULL [52.68, 52.68, 50.04] vs ACC remainder [52.68, 52.68, 50.04]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.69, 52.69, 50.05] vs ACC remainder [52.68, 52.68, 50.04]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.69, 52.69, 50.05] STORAGE_MATCHED [52.69, 52.69, 50.05] vs ACC remainder [52.68, 52.68, 50.04]
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
  contemp_f3d72b942df45120
    0_competence_kept_ACC_ge_FRESH         2/3  successes ACC [1, 1, 0] vs FRESH [0, 1, 2]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [1.5, 446.3, -445.4] vs 5% of FRESH cost [13502.1, 13502.1, 13055.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [450.02, 450.02, 450.02] vs CODE_ONLY [450.03, 450.03, 450.03]
    4_scramble_or_reset_damages            0/3  eff ACC [1.019, 1.004, 0.0] SCR [1.019, 1.004, 0.0] RESET [1.019, 1.004, 0.0]
    5_transfers_to_fresh_copy              0/3  FULL [450.02, 450.02, 450.02] vs ACC remainder [450.02, 450.02, 450.02]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [450.02, 450.02, 450.02] vs ACC remainder [450.02, 450.02, 450.02]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [850.07, 850.07, 850.07] STORAGE_MATCHED [450.03, 450.03, 450.03] vs ACC remainder [450.02, 450.02, 450.02]

MACHINERY OF top1_66871687158cfab1 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   1    32
    task  9:     0    0    0    0    0 |   1    32
    task 19:     0    0    0    0    0 |   1    32
    task 31:     0    0    0    0    0 |   1    32
    task 41:     0    0    0    0    0 |   1    32
    task 49:     0    0    0    0    0 |   1    32
  artifact events: 1 (create 1, delete 0, patch/append 0); invocations by block: {}; edges: 0
    block 0 origin=calibration len=0 state=[[2, 3, 6, 8, 10, 4, 9, 11, 5, 0, 7, 1], [9, 11, 0, 1, 5, 8, 2, 10, 3, 6, 4, 7], 0] instr=[]
  adaptation curve ACC:   52 556 94 285 88 52 61 1908 132 256 101 94 285 285 8 385 385 58 556 35 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
  adaptation curve FRESH: 52 556 94 285 88 52 61 1909 132 256 101 94 285 285 8 385 385 58 556 35 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
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

