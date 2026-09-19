CRIUS CAMPAIGN 0 REPORT  run=search_c2b_recombination_s2  arm=recombination
code_commit=713b2773f dirty=True config_hash=c9c87cec99eb063f world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  22.9741   21.7861         9.0303        46         17
    26  21.4316   21.4313        16.5436        61        162
    51  20.4293   20.4291        12.9647        64        303
    76  23.4163   23.4161        15.0444        47        452
   101  17.8178   16.8790        10.5410        65        554
   126  23.9311   23.9311        17.8188        55        660
   151  22.3995   22.3991        14.3890        57        768
   176  19.9063   19.9026        10.8847        55        877
   201  21.8782   21.0030        14.4332        66        984
   226  21.3672   20.4955        15.2071        54       1078
   251  23.9486   23.5106        15.2800        59       1183
   276  23.4518   23.0121        16.2013        89       1271
   300  21.9603   21.9602        15.8616        95       1350
  candidates evaluated: 7208   best_ever 27.9770 (41606b6b46f6ba99)  wall 1350s

BEST PROGRAM 41606b6b46f6ba99 (len 58, iteration 31, modification const@3+arg@10.0+arg@41.0+splice@33<-donor[22:23]:b5110f6c424befb0)
  search seed 2010310: fit 23.4745 succ 23/50 inter 2960 steps 17151 ws_cost 15 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [88.687, 1.0], "B": [78.897, 1.0], "C": [45.802, 0.167], "D": [52.14, 0.0], "E": [48.1, 0.125]}
  search seed 2010311: fit 32.4794 succ 32/50 inter 2366 steps 16575 ws_cost 15 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [71.63, 1.0], "B": [58.514, 1.0], "C": [38.668, 0.5], "D": [42.444, 0.3], "E": [42.75, 0.375]}
  listing:
      0  INPUT          R1, num_ops
      1  CONST          R5, 1
      2  CONST          R0, -7
      3  CONST          R0, 2
      4  ADD            R0, R0, R5
      5  DIV            R4, R0, R1
      6  MOD            R3, R4, R1
      7  VGET           R7, R5, R2
      8  LT             R3, R0, R2
      9  JMP            16
     10  DIV            R2, R5, R0
     11  CONST          R5, 1
     12  MUL            R2, R1, R1
     13  ACT            R3
     14  DIV            R4, R1, R1
     15  MOD            R3, R4, R1
     16  BRZ            R3, 21
     17  ADD            R3, R3, R5
     18  CONST          R0, -1
     19  ACT            R1
     20  ACT            R0
     21  BRZ            R3, 42
     22  MOV            R2, R1
     23  MUL            R2, R1, R1
     24  LT             R3, R0, R2
     25  ACT            R3
     26  ACT            R1
     27  BRZ            R3, 26
     28  ACT            R0
     29  DIV            R4, R0, R1
     30  MOD            R3, R4, R1
     31  ACT            R3
     32  ADD            R0, R0, R5
     33  ACT            R1
     34  ADD            R0, R0, R5
     35  CONST          R0, -1
     36  MUL            R2, R1, R1
     37  LT             R3, R0, R2
     38  ACT            R3
     39  BRZ            R3, 27
     40  ACT            R0
     41  JMP            24
     42  ADD            R6, R0, R5
     43  MUL            R2, R1, R1
     44  MUL            R2, R2, R1
     45  LT             R3, R0, R2
     46  ACT            R1
     47  MOD            R3, R0, R1
     48  ACT            R3
     49  DIV            R4, R0, R1
     50  MOD            R3, R4, R1
     51  ACT            R3
     52  DIV            R4, R4, R1
     53  MOD            R3, R4, R0
     54  ACT            R3
     55  ADD            R0, R0, R5
     56  JMP            45
     57  BLK_INVOKE     R5
  ancestry (19 steps, newest first): iteration/fitness/modification
    it   31  27.9770  len 58  const@3+arg@10.0+arg@41.0+splice@33<-donor[22:23]:b5110f6c424befb0
    it   30  21.4305  len 57  delete@4+delete@16+delete@38
    it   27  25.8999  len 60  delete@46+swap@20,24
    it   26  21.4316  len 61  swap@23,5+arg@30.0
    it   25  22.9697  len 61  const@2
    it   24  21.9509  len 61  arg@10.0+replace@19+arg@56.2
    it   21  18.3733  len 61  delete@5+delete@41+splice@35<-donor[24:32]:e2b527d3ec500ac4
    it   20  21.4267  len 55  arg@16.1
    it   19  21.9561  len 55  replace@30+swap@30,9
    it   18  22.4077  len 55  delete@25
    it   17  23.9339  len 56  swap@28,6+duplicate@17+1->10
    it   10  21.9213  len 55  delete@20+delete@21+arg@31.0
    it    7  22.4358  len 57  swap@3,9+splice@14<-donor[40:43]:72ad7f491fd236a3
    it    6  19.9335  len 54  swap@9,36
    it    4  21.9543  len 54  replace@11
    ... 5 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7315.4    5.3   74.7
  top1_b655bc7181e19770       20.750  20.750  20.750  20.750  20.3  20.3     9871     9871       6.8   32.0    0.0
  top2_df13599b07f073e8       20.750  20.750  20.750  20.750  20.3  20.3     9871     9871       6.8   32.0    0.0
  top3_b4a6f3695b46d989       20.750  20.750  20.750  20.750  20.3  20.3     9871     9871       6.8   32.0    0.0
  contemp_919967a736927546    20.750  20.750  20.750  20.750  20.3  20.3     9871     9871       6.8   32.0    0.0
  contemp_22c421679051533b    20.750  20.750  20.750  20.750  20.3  20.3     9871     9871       6.8   32.0    0.0
  ancestor141_it297_f70bef0b  20.750  20.750  20.750  20.750  20.3  20.3     9871     9871       6.8   32.0    0.0
  ancestor71_it137_142461056  20.749  20.749  20.749  20.749  20.3  20.3     9945     9945       7.1    1.0    0.0
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.9    3.7    1.7
  bestever_41606b6b46f6ba99   20.414  20.414  20.414  20.414  20.0  20.0    10157    10157       7.2    1.0    0.0
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ancestor1_it0_0875253d162c  19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0
  contemp_aa7c592cc10fc069     2.034   2.034   2.034   2.034   2.0   2.0      344      387       2.9   32.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.02/ 455.13   14.92/ 539.10   21.12/  47.94   33.22/  48.94   40.08/  50.52
  top1_b655bc7181e19770       439.46/ 439.57  438.99/ 439.12   49.90/  50.04   50.27/  50.42   51.66/  51.81
  top2_df13599b07f073e8       439.49/ 439.60  439.02/ 439.15   49.93/  50.07   50.30/  50.45   51.69/  51.84
  top3_b4a6f3695b46d989       439.49/ 439.60  439.02/ 439.15   49.93/  50.07   50.30/  50.45   51.69/  51.84
  contemp_919967a736927546    439.49/ 439.60  439.02/ 439.15   49.93/  50.07   50.30/  50.45   51.69/  51.84
  contemp_22c421679051533b    439.49/ 439.60  439.02/ 439.15   49.93/  50.07   50.30/  50.45   51.69/  51.84
  ancestor141_it297_f70bef0b  439.49/ 439.60  439.02/ 439.15   49.93/  50.07   50.30/  50.45   51.69/  51.84
  ancestor71_it137_142461056  440.43/ 440.56  447.15/ 447.30   47.68/  47.82   51.36/  51.51   50.80/  50.95
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.14/ 443.81  528.13/ 527.79   47.94/  47.89   48.86/  48.88   50.43/  50.46
  bestever_41606b6b46f6ba99   454.32/ 454.45  452.95/ 453.09   50.46/  50.61   51.51/  51.66   52.14/  52.29
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ancestor1_it0_0875253d162c  495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  ENUMERATE_VM_C1             495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  RANDOM_C1                  1662.62/1662.62 1627.07/1627.07   50.50/  50.50   50.50/  50.50   48.56/  48.56
  contemp_aa7c592cc10fc069   2080.80/2080.85 2320.42/2320.48  437.87/ 437.92  450.28/ 450.34  450.28/ 450.34

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  top1_b655bc7181e19770          3/36    47     2/30    48     1/12    48     0/12    50    27/30   422    28/30   421
  top2_df13599b07f073e8          3/36    47     2/30    48     1/12    48     0/12    50    27/30   422    28/30   421
  top3_b4a6f3695b46d989          3/36    47     2/30    48     1/12    48     0/12    50    27/30   422    28/30   421
  contemp_919967a736927546       3/36    47     2/30    48     1/12    48     0/12    50    27/30   422    28/30   421
  contemp_22c421679051533b       3/36    47     2/30    48     1/12    48     0/12    50    27/30   422    28/30   421
  ancestor141_it297_f70bef0b     3/36    47     2/30    48     1/12    48     0/12    50    27/30   422    28/30   421
  ancestor71_it137_142461056     4/36    45     1/30    49     0/12    50     1/12    47    27/30   423    28/30   429
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  bestever_41606b6b46f6ba99      3/36    48     2/30    49     0/12    50     0/12    50    27/30   435    28/30   434
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ancestor1_it0_0875253d162c     2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610
  contemp_aa7c592cc10fc069       1/36     7     0/30     7     0/12     7     0/12     7     4/30     7     1/30     7

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.27    49.53    36.27    36.27    49.53    49.53    49.53   5.0
  top1_b655bc7181e19770         50.89    50.90    50.89    50.89    50.90    50.90    50.90  32.0
  top2_df13599b07f073e8         50.92    50.93    50.92    50.92    50.93    50.93    50.93  32.0
  top3_b4a6f3695b46d989         50.92    50.93    50.92    50.92    50.93    50.93    50.93  32.0
  contemp_919967a736927546      50.92    50.93    50.92    50.92    50.93    50.93    50.93  32.0
  contemp_22c421679051533b      50.92    50.93    50.92    50.92    50.93    50.93    50.93  32.0
  ancestor141_it297_f70bef0b    50.92    50.93    50.92    50.92    50.93    50.93    50.93  32.0
  ancestor71_it137_142461056    51.11    51.12    51.11    51.11    51.12    51.12    51.12   1.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.56    49.55    49.56    49.56    49.55    49.55    49.55   2.0
  bestever_41606b6b46f6ba99     51.79    51.80    51.79    51.79    51.80    51.80    51.80   1.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ancestor1_it0_0875253d162c    51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  ENUMERATE_VM_C1               51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  RANDOM_C1                     49.64       --    49.64    49.64    49.64    49.64    49.64   0.0
  contemp_aa7c592cc10fc069     450.28   450.27   450.28   450.28   450.29   850.85   450.29  32.0

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
  top1_b655bc7181e19770
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 19, 23] vs FRESH [19, 19, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.3] vs 5% of FRESH cost [1553.1, 1518.8, 1485.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.35, 51.42, 48.89] vs CODE_ONLY [52.36, 51.43, 48.9]
    4_scramble_or_reset_damages            0/3  eff ACC [19.384, 19.417, 23.448] SCR [19.384, 19.417, 23.448] RESET [19.384, 19.417, 23.448]
    5_transfers_to_fresh_copy              0/3  FULL [52.35, 51.42, 48.89] vs ACC remainder [52.35, 51.42, 48.89]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.36, 51.43, 48.9] vs ACC remainder [52.35, 51.42, 48.89]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.36, 51.43, 48.9] STORAGE_MATCHED [52.36, 51.43, 48.9] vs ACC remainder [52.35, 51.42, 48.89]
  top2_df13599b07f073e8
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 19, 23] vs FRESH [19, 19, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.3] vs 5% of FRESH cost [1554.0, 1519.7, 1486.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.38, 51.45, 48.92] vs CODE_ONLY [52.39, 51.46, 48.92]
    4_scramble_or_reset_damages            0/3  eff ACC [19.384, 19.417, 23.448] SCR [19.384, 19.417, 23.448] RESET [19.384, 19.417, 23.448]
    5_transfers_to_fresh_copy              0/3  FULL [52.38, 51.45, 48.92] vs ACC remainder [52.38, 51.45, 48.92]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.39, 51.46, 48.92] vs ACC remainder [52.38, 51.45, 48.92]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.39, 51.46, 48.92] STORAGE_MATCHED [52.39, 51.46, 48.92] vs ACC remainder [52.38, 51.45, 48.92]
  top3_b4a6f3695b46d989
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 19, 23] vs FRESH [19, 19, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.3] vs 5% of FRESH cost [1554.0, 1519.7, 1486.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.38, 51.45, 48.92] vs CODE_ONLY [52.39, 51.46, 48.92]
    4_scramble_or_reset_damages            0/3  eff ACC [19.384, 19.417, 23.448] SCR [19.384, 19.417, 23.448] RESET [19.384, 19.417, 23.448]
    5_transfers_to_fresh_copy              0/3  FULL [52.38, 51.45, 48.92] vs ACC remainder [52.38, 51.45, 48.92]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.39, 51.46, 48.92] vs ACC remainder [52.38, 51.45, 48.92]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.39, 51.46, 48.92] STORAGE_MATCHED [52.39, 51.46, 48.92] vs ACC remainder [52.38, 51.45, 48.92]
  contemp_919967a736927546
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 19, 23] vs FRESH [19, 19, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.3] vs 5% of FRESH cost [1554.0, 1519.7, 1486.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.38, 51.45, 48.92] vs CODE_ONLY [52.39, 51.46, 48.92]
    4_scramble_or_reset_damages            0/3  eff ACC [19.384, 19.417, 23.448] SCR [19.384, 19.417, 23.448] RESET [19.384, 19.417, 23.448]
    5_transfers_to_fresh_copy              0/3  FULL [52.38, 51.45, 48.92] vs ACC remainder [52.38, 51.45, 48.92]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.39, 51.46, 48.92] vs ACC remainder [52.38, 51.45, 48.92]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.39, 51.46, 48.92] STORAGE_MATCHED [52.39, 51.46, 48.92] vs ACC remainder [52.38, 51.45, 48.92]
  contemp_22c421679051533b
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 19, 23] vs FRESH [19, 19, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.3] vs 5% of FRESH cost [1554.0, 1519.7, 1486.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.38, 51.45, 48.92] vs CODE_ONLY [52.39, 51.46, 48.92]
    4_scramble_or_reset_damages            0/3  eff ACC [19.384, 19.417, 23.448] SCR [19.384, 19.417, 23.448] RESET [19.384, 19.417, 23.448]
    5_transfers_to_fresh_copy              0/3  FULL [52.38, 51.45, 48.92] vs ACC remainder [52.38, 51.45, 48.92]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.39, 51.46, 48.92] vs ACC remainder [52.38, 51.45, 48.92]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.39, 51.46, 48.92] STORAGE_MATCHED [52.39, 51.46, 48.92] vs ACC remainder [52.38, 51.45, 48.92]
  ancestor141_it297_f70bef0b4e125534
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 19, 23] vs FRESH [19, 19, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.3] vs 5% of FRESH cost [1554.0, 1519.7, 1486.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.38, 51.45, 48.92] vs CODE_ONLY [52.39, 51.46, 48.92]
    4_scramble_or_reset_damages            0/3  eff ACC [19.384, 19.417, 23.448] SCR [19.384, 19.417, 23.448] RESET [19.384, 19.417, 23.448]
    5_transfers_to_fresh_copy              0/3  FULL [52.38, 51.45, 48.92] vs ACC remainder [52.38, 51.45, 48.92]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.39, 51.46, 48.92] vs ACC remainder [52.38, 51.45, 48.92]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.39, 51.46, 48.92] STORAGE_MATCHED [52.39, 51.46, 48.92] vs ACC remainder [52.38, 51.45, 48.92]
  ancestor71_it137_14246105605e194f
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 19, 23] vs FRESH [19, 19, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.4] vs 5% of FRESH cost [1536.9, 1486.7, 1466.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.34, 52.19, 50.8] vs CODE_ONLY [50.35, 52.2, 50.81]
    4_scramble_or_reset_damages            0/3  eff ACC [19.383, 19.411, 23.453] SCR [19.383, 19.411, 23.453] RESET [19.383, 19.411, 23.453]
    5_transfers_to_fresh_copy              0/3  FULL [50.34, 52.19, 50.8] vs ACC remainder [50.34, 52.19, 50.8]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [50.35, 52.2, 50.81] vs ACC remainder [50.34, 52.19, 50.8]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.35, 52.2, 50.81] STORAGE_MATCHED [50.35, 52.2, 50.81] vs ACC remainder [50.34, 52.19, 50.8]
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
  bestever_41606b6b46f6ba99
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 18, 23] vs FRESH [19, 18, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.4] vs 5% of FRESH cost [1568.6, 1550.9, 1507.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.14, 52.14, 51.09] vs CODE_ONLY [52.15, 52.15, 51.1]
    4_scramble_or_reset_damages            0/3  eff ACC [19.384, 18.414, 23.444] SCR [19.384, 18.414, 23.444] RESET [19.384, 18.414, 23.444]
    5_transfers_to_fresh_copy              0/3  FULL [52.14, 52.14, 51.09] vs ACC remainder [52.14, 52.14, 51.09]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.15, 52.15, 51.1] vs ACC remainder [52.14, 52.14, 51.09]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.15, 52.15, 51.1] STORAGE_MATCHED [52.15, 52.15, 51.1] vs ACC remainder [52.14, 52.14, 51.09]
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
  contemp_aa7c592cc10fc069
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [4, 2, 0] vs FRESH [4, 2, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [1.8, 1.8, 1.8] vs 5% of FRESH cost [13510.2, 13063.2, 13510.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [450.28, 450.28, 450.28] vs CODE_ONLY [450.29, 450.29, 450.29]
    4_scramble_or_reset_damages            0/3  eff ACC [4.078, 2.023, 0.0] SCR [4.078, 2.023, 0.0] RESET [4.078, 2.023, 0.0]
    5_transfers_to_fresh_copy              0/3  FULL [450.28, 450.28, 450.28] vs ACC remainder [450.28, 450.28, 450.28]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [450.27, 450.27, 450.27] vs ACC remainder [450.28, 450.28, 450.28]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [850.85, 850.85, 850.85] STORAGE_MATCHED [450.29, 450.29, 450.29] vs ACC remainder [450.28, 450.28, 450.28]

MACHINERY OF top1_b655bc7181e19770 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     1    0    0    0    1 |   3    52
    task  9:    10    0    0    0   10 |  21   232
    task 19:    20    0    0    0   20 |  32   342
    task 31:    32    0    0    0   32 |  32   342
    task 41:    42    0    0    0   42 |  32   342
    task 49:    50    0    0    0   50 |  32   342
  artifact events: 32 (create 32, delete 0, patch/append 0); invocations by block: {}; edges: 0
    block 0 origin=new len=0 state=[0, 0, 0] instr=[]
    block 1 origin=new len=0 state=[0, 0, 0] instr=[]
    block 2 origin=calibration len=0 state=[[2, 3, 6, 8, 10, 4, 9, 11, 5, 0, 7, 1], [9, 11, 0, 1, 5, 8, 2, 10, 3, 6, 4, 7], 0] instr=[]
    block 3 origin=new len=0 state=[0, 0, 0] instr=[]
    block 4 origin=new len=0 state=[0, 0, 0] instr=[]
  adaptation curve ACC:   11 2074 8 995 11 11 149 1725 194 250 39 8 995 995 11 1492 1492 8 2074 160 52 30 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
  adaptation curve FRESH: 11 2074 8 995 11 11 149 1726 194 250 39 8 995 995 11 1492 1492 8 2074 160 52 31 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
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

