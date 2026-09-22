CRIUS CAMPAIGN 0 REPORT  run=search_c2a_recombination_s3  arm=recombination
code_commit=6eb2d2ac7 dirty=True config_hash=401915ec4da9443a world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  21.4212   20.0844         8.5104        42         14
    26  24.4237   24.4234        17.0450        74         95
    51  18.4006   18.3994        13.1966        74        170
    76  17.3557   17.3557        12.8015        89        234
   101  22.9165   22.9165        14.2880        82        317
   126  22.8783   22.4413        13.7261        72        386
   151  19.9166   19.9166        14.8846        61        444
   176  23.4640   23.4640        16.8799        64        513
   201  22.4451   22.4451        14.2869        53        590
   226  17.8796   17.8796        13.1785        44        670
   251  26.4408   23.3738        13.0446        36        735
   276  24.4388   23.3127        15.3782        30        792
   300  21.9215   20.1598        13.6802        28        848
  candidates evaluated: 7208   best_ever 31.4681 (9d04f6a1ef1a5ffc)  wall 848s

BEST PROGRAM 9d04f6a1ef1a5ffc (len 73, iteration 121, modification arg@24.2+const@60)
  search seed 3011210: fit 21.4358 succ 21/50 inter 7575 steps 32353 ws_cost 0 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [321.79, 0.9], "B": [318.775, 1.0], "C": [49.917, 0.083], "D": [47.859, 0.1], "E": [51.91, 0.0]}
  search seed 3011211: fit 21.4263 succ 21/50 inter 8704 steps 36496 ws_cost 0 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [276.17, 1.0], "B": [486.523, 0.8], "C": [48.622, 0.083], "D": [44.329, 0.2], "E": [51.91, 0.0]}
  listing:
      0  INPUT          R1, num_ops
      1  CONST          R5, 1
      2  JMP            47
      3  JMP            49
      4  ACT            R3
      5  LT             R3, R0, R2
      6  MOD            R3, R0, R1
      7  CONST          R0, -2
      8  WS_SREAD       R1, R7, R6
      9  JMP            43
     10  CONST          R5, 22
     11  LT             R3, R0, R2
     12  MOV            R2, R1
     13  WS_ALLOC       R7, R1
     14  MUL            R1, R6, R5
     15  ADD            R0, R0, R5
     16  ACT            R1
     17  CONST          R0, 23
     18  BRZ            R3, 55
     19  MOD            R3, R0, R1
     20  ACT            R1
     21  MUL            R2, R6, R1
     22  MOV            R4, R1
     23  CONST          R5, 21
     24  LT             R3, R0, R3
     25  MOV            R2, R5
     26  BLK_APPEND     R5, R5
     27  MUL            R2, R1, R1
     28  LT             R3, R0, R2
     29  ACT            R1
     30  MOD            R3, R0, R1
     31  JMP            52
     32  MUL            R2, R6, R1
     33  BLK_APPEND     R5, R5
     34  BRZ            R3, 65
     35  BLK_REC_BEGIN  
     36  NOT            R1, R3
     37  ADD            R0, R1, R3
     38  LT             R3, R0, R2
     39  BRZ            R3, 51
     40  BLK_PATCH      R2, R7, R3
     41  BRNZ           R3, 51
     42  JMP            3
     43  LT             R5, R0, R2
     44  BRZ            R0, 52
     45  MOD            R5, R1, R1
     46  CONST          R0, 18
     47  LT             R3, R0, R2
     48  BRZ            R3, 58
     49  ACT            R1
     50  MOD            R3, R0, R2
     51  ADD            R0, R5, R5
     52  DIV            R4, R0, R7
     53  MOD            R3, R4, R1
     54  LT             R3, R0, R2
     55  MOD            R3, R0, R1
     56  JMP            10
     57  BLK_COPY       R7, R2
     58  CONST          R0, 6
     59  MOD            R3, R4, R1
     60  CONST          R0, 27
     61  ADD            R0, R0, R5
     62  ACT            R1
     63  MOD            R3, R0, R1
     64  ACT            R3
     65  DIV            R4, R0, R1
     66  MOD            R3, R4, R1
     67  ACT            R3
     68  DIV            R4, R4, R1
     69  MOD            R3, R4, R1
     70  ACT            R3
     71  JMP            61
     72  HALT           
  ancestry (71 steps, newest first): iteration/fitness/modification
    it  121  21.4310  len 73  arg@24.2+const@60
    it  120  22.4577  len 73  replace@21+insert@13+delete@59
    it  119  22.8892  len 73  const@58+arg@43.0+delete@56
    it  118  23.9509  len 74  delete@54+arg@36.2
    it  117  21.9209  len 75  replace@24+replace@34
    it  116  22.9271  len 75  delete@37+arg@30.0
    it  115  24.4457  len 76  delete@19
    it  113  25.4597  len 77  replace@41+const@61+const@7+splice@14<-donor[65:66]:42a205ef0198ec21
    it  112  23.9138  len 76  delete@54+arg@52.2
    it  110  21.4117  len 77  delete@57+swap@40,19
    it  108  24.9307  len 78  delete@7+swap@3,50
    it  106  18.3987  len 79  delete@44+delete@47
    it  105  20.3753  len 81  delete@32+const@68+replace@7
    it  102  20.3782  len 82  delete@55+const@39
    it   99  21.3995  len 83  delete@7
    ... 57 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7316.0    4.3   74.7
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.3    2.7    1.7
  top1_cf94c8c3142ac028       20.087  20.087  20.087  20.087  19.7  19.7     9433     9433       0.0    0.0    0.0
  top2_01ac931138b75600       20.077  20.077  20.077  20.077  19.7  19.7    10627    10627       0.0    0.0    0.0
  top3_b685d1a9180d80f7       20.077  20.077  20.077  20.077  19.7  19.7    10627    10627       0.0    0.0    0.0
  ancestor152_it293_ef08afbd  20.077  20.077  20.077  20.077  19.7  19.7    10627    10627       0.0    0.0    0.0
  contemp_174b602c25853433    20.076  20.076  20.076  20.076  19.7  19.7    10627    10627       0.0    0.0    0.0
  contemp_774626ae0f461d81    20.076  20.076  20.076  20.076  19.7  19.7    10627    10627       0.0    0.0    0.0
  bestever_9d04f6a1ef1a5ffc   20.076  20.076  20.076  20.076  19.7  19.7    10703    10703       0.0    0.0    0.0
  ancestor76_it126_5ebc279ac  20.076  20.076  20.076  20.076  19.7  19.7    10703    10703       0.0    0.0    0.0
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ancestor1_it0_0875253d162c  19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       0.0    0.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       0.0    0.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0
  contemp_16978371733ae6da     3.169   3.169   3.169   3.169   3.0   3.0    39337    39337       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.00/ 455.13   14.90/ 539.10   21.11/  47.94   33.21/  48.94   40.07/  50.52
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.13/ 443.81  528.11/ 527.79   47.93/  47.89   48.85/  48.88   50.42/  50.46
  top1_cf94c8c3142ac028       358.88/ 358.88  474.96/ 474.96   48.92/  48.92   49.60/  49.60   49.90/  49.90
  top2_01ac931138b75600       452.98/ 452.98  502.11/ 502.11   48.80/  48.80   50.68/  50.68   51.89/  51.89
  top3_b685d1a9180d80f7       452.98/ 452.98  502.11/ 502.11   48.80/  48.80   50.68/  50.68   51.89/  51.89
  ancestor152_it293_ef08afbd  452.98/ 452.98  502.11/ 502.11   48.80/  48.80   50.68/  50.68   51.89/  51.89
  contemp_174b602c25853433    456.02/ 456.02  505.47/ 505.47   49.12/  49.12   51.00/  51.00   52.21/  52.21
  contemp_774626ae0f461d81    456.04/ 456.04  505.49/ 505.49   49.14/  49.14   51.02/  51.02   52.23/  52.23
  bestever_9d04f6a1ef1a5ffc   466.44/ 466.44  494.84/ 494.84   49.77/  49.77   51.32/  51.32   51.91/  51.91
  ancestor76_it126_5ebc279ac  466.44/ 466.44  494.84/ 494.84   49.77/  49.77   51.32/  51.32   51.91/  51.91
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ancestor1_it0_0875253d162c  495.80/ 495.80  525.01/ 525.01   50.10/  50.10   51.09/  51.09   52.68/  52.68
  ENUMERATE_VM_C1             495.80/ 495.80  525.01/ 525.01   50.10/  50.10   51.09/  51.09   52.68/  52.68
  RANDOM_C1                  1662.62/1662.62 1627.07/1627.07   50.50/  50.50   50.50/  50.50   48.56/  48.56
  contemp_16978371733ae6da   1986.87/1986.87 1930.04/1930.04   48.67/  48.67   50.51/  50.51   49.87/  49.87

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  top1_cf94c8c3142ac028          3/36    47     2/30    48     1/12    46     0/12    50    28/30   344    25/30   456
  top2_01ac931138b75600          3/36    47     1/30    49     0/12    50     0/12    50    27/30   435    28/30   482
  top3_b685d1a9180d80f7          3/36    47     1/30    49     0/12    50     0/12    50    27/30   435    28/30   482
  ancestor152_it293_ef08afbd     3/36    47     1/30    49     0/12    50     0/12    50    27/30   435    28/30   482
  contemp_174b602c25853433       3/36    47     1/30    49     0/12    50     0/12    50    27/30   435    28/30   482
  contemp_774626ae0f461d81       3/36    47     1/30    49     0/12    50     0/12    50    27/30   435    28/30   482
  bestever_9d04f6a1ef1a5ffc      3/36    48     1/30    49     0/12    50     0/12    50    27/30   448    28/30   475
  ancestor76_it126_5ebc279ac     3/36    48     1/30    49     0/12    50     0/12    50    27/30   448    28/30   475
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ancestor1_it0_0875253d162c     2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610
  contemp_16978371733ae6da       3/36    47     1/30    49     0/12    50     1/12    46     2/30  1923     2/30  1868

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.26    49.53    36.26    36.26    49.53    49.53    49.53   4.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.55    49.55    49.55    49.55    49.55    49.55    49.55   1.0
  top1_cf94c8c3142ac028         49.74       --    49.74    49.74    49.74    49.74    49.74   0.0
  top2_01ac931138b75600         51.22       --    51.22    51.22    51.22    51.22    51.22   0.0
  top3_b685d1a9180d80f7         51.22       --    51.22    51.22    51.22    51.22    51.22   0.0
  ancestor152_it293_ef08afbd    51.22       --    51.22    51.22    51.22    51.22    51.22   0.0
  contemp_174b602c25853433      51.54       --    51.54    51.54    51.54    51.54    51.54   0.0
  contemp_774626ae0f461d81      51.56       --    51.56    51.56    51.56    51.56    51.56   0.0
  bestever_9d04f6a1ef1a5ffc     51.58       --    51.58    51.58    51.58    51.58    51.58   0.0
  ancestor76_it126_5ebc279ac    51.58       --    51.58    51.58    51.58    51.58    51.58   0.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ancestor1_it0_0875253d162c    51.80       --    51.80    51.80    51.80    51.80    51.80   0.0
  ENUMERATE_VM_C1               51.80       --    51.80    51.80    51.80    51.80    51.80   0.0
  RANDOM_C1                     49.64       --    49.64    49.64    49.64    49.64    49.64   0.0
  contemp_16978371733ae6da      50.23       --    50.23    50.23    50.23    50.23    50.23   0.0

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
  top1_cf94c8c3142ac028
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [16, 21, 22] vs FRESH [16, 21, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1516.2, 1481.9, 1448.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.89, 49.24, 48.08] vs CODE_ONLY [51.89, 49.24, 48.08]
    4_scramble_or_reset_damages            0/3  eff ACC [16.367, 21.453, 22.44] SCR [16.367, 21.453, 22.44] RESET [16.367, 21.453, 22.44]
    5_transfers_to_fresh_copy              0/3  FULL [51.89, 49.24, 48.08] vs ACC remainder [51.89, 49.24, 48.08]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.89, 49.24, 48.08]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.89, 49.24, 48.08] STORAGE_MATCHED [51.89, 49.24, 48.08] vs ACC remainder [51.89, 49.24, 48.08]
  top2_01ac931138b75600
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 18, 22] vs FRESH [19, 18, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1512.0, 1517.2, 1493.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.89, 51.89, 49.87] vs CODE_ONLY [51.89, 51.89, 49.87]
    4_scramble_or_reset_damages            0/3  eff ACC [19.378, 18.411, 22.441] SCR [19.378, 18.411, 22.441] RESET [19.378, 18.411, 22.441]
    5_transfers_to_fresh_copy              0/3  FULL [51.89, 51.89, 49.87] vs ACC remainder [51.89, 51.89, 49.87]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.89, 51.89, 49.87]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.89, 51.89, 49.87] STORAGE_MATCHED [51.89, 51.89, 49.87] vs ACC remainder [51.89, 51.89, 49.87]
  top3_b685d1a9180d80f7
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 18, 22] vs FRESH [19, 18, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1512.0, 1517.2, 1493.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.89, 51.89, 49.87] vs CODE_ONLY [51.89, 51.89, 49.87]
    4_scramble_or_reset_damages            0/3  eff ACC [19.378, 18.411, 22.441] SCR [19.378, 18.411, 22.441] RESET [19.378, 18.411, 22.441]
    5_transfers_to_fresh_copy              0/3  FULL [51.89, 51.89, 49.87] vs ACC remainder [51.89, 51.89, 49.87]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.89, 51.89, 49.87]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.89, 51.89, 49.87] STORAGE_MATCHED [51.89, 51.89, 49.87] vs ACC remainder [51.89, 51.89, 49.87]
  ancestor152_it293_ef08afbd6b437779
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 18, 22] vs FRESH [19, 18, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1512.0, 1517.2, 1493.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.89, 51.89, 49.87] vs CODE_ONLY [51.89, 51.89, 49.87]
    4_scramble_or_reset_damages            0/3  eff ACC [19.378, 18.411, 22.441] SCR [19.378, 18.411, 22.441] RESET [19.378, 18.411, 22.441]
    5_transfers_to_fresh_copy              0/3  FULL [51.89, 51.89, 49.87] vs ACC remainder [51.89, 51.89, 49.87]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.89, 51.89, 49.87]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.89, 51.89, 49.87] STORAGE_MATCHED [51.89, 51.89, 49.87] vs ACC remainder [51.89, 51.89, 49.87]
  contemp_174b602c25853433
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 18, 22] vs FRESH [19, 18, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1521.5, 1526.7, 1502.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.21, 52.21, 50.19] vs CODE_ONLY [52.21, 52.21, 50.19]
    4_scramble_or_reset_damages            0/3  eff ACC [19.377, 18.411, 22.441] SCR [19.377, 18.411, 22.441] RESET [19.377, 18.411, 22.441]
    5_transfers_to_fresh_copy              0/3  FULL [52.21, 52.21, 50.19] vs ACC remainder [52.21, 52.21, 50.19]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.21, 52.21, 50.19]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.21, 52.21, 50.19] STORAGE_MATCHED [52.21, 52.21, 50.19] vs ACC remainder [52.21, 52.21, 50.19]
  contemp_774626ae0f461d81
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 18, 22] vs FRESH [19, 18, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1522.1, 1527.3, 1503.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.23, 52.23, 50.21] vs CODE_ONLY [52.23, 52.23, 50.21]
    4_scramble_or_reset_damages            0/3  eff ACC [19.377, 18.411, 22.441] SCR [19.377, 18.411, 22.441] RESET [19.377, 18.411, 22.441]
    5_transfers_to_fresh_copy              0/3  FULL [52.23, 52.23, 50.21] vs ACC remainder [52.23, 52.23, 50.21]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.23, 52.23, 50.21]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.23, 52.23, 50.21] STORAGE_MATCHED [52.23, 52.23, 50.21] vs ACC remainder [52.23, 52.23, 50.21]
  bestever_9d04f6a1ef1a5ffc
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 18, 23] vs FRESH [18, 18, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1557.3, 1536.5, 1483.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.91, 51.91, 50.93] vs CODE_ONLY [51.91, 51.91, 50.93]
    4_scramble_or_reset_damages            0/3  eff ACC [18.38, 18.412, 23.436] SCR [18.38, 18.412, 23.436] RESET [18.38, 18.412, 23.436]
    5_transfers_to_fresh_copy              0/3  FULL [51.91, 51.91, 50.93] vs ACC remainder [51.91, 51.91, 50.93]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.91, 51.91, 50.93]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.91, 51.91, 50.93] STORAGE_MATCHED [51.91, 51.91, 50.93] vs ACC remainder [51.91, 51.91, 50.93]
  ancestor76_it126_5ebc279ac3ebf3f8
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 18, 23] vs FRESH [18, 18, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1557.3, 1536.5, 1483.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.91, 51.91, 50.93] vs CODE_ONLY [51.91, 51.91, 50.93]
    4_scramble_or_reset_damages            0/3  eff ACC [18.38, 18.412, 23.436] SCR [18.38, 18.412, 23.436] RESET [18.38, 18.412, 23.436]
    5_transfers_to_fresh_copy              0/3  FULL [51.91, 51.91, 50.93] vs ACC remainder [51.91, 51.91, 50.93]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.91, 51.91, 50.93]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.91, 51.91, 50.93] STORAGE_MATCHED [51.91, 51.91, 50.93] vs ACC remainder [51.91, 51.91, 50.93]
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
  RANDOM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 6, 9] vs FRESH [6, 6, 9]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1493.8, 1515.0, 1489.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.32, 50.5, 49.1] vs CODE_ONLY [49.32, 50.5, 49.1]
    4_scramble_or_reset_damages            0/3  eff ACC [6.205, 6.235, 9.221] SCR [6.205, 6.235, 9.221] RESET [6.205, 6.235, 9.221]
    5_transfers_to_fresh_copy              0/3  FULL [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.32, 50.5, 49.1]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.32, 50.5, 49.1] STORAGE_MATCHED [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
  contemp_16978371733ae6da
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [2, 3, 4] vs FRESH [2, 3, 4]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1507.1, 1512.3, 1445.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.25, 51.72, 49.71] vs CODE_ONLY [49.25, 51.72, 49.71]
    4_scramble_or_reset_damages            0/3  eff ACC [2.154, 3.185, 4.169] SCR [2.154, 3.185, 4.169] RESET [2.154, 3.185, 4.169]
    5_transfers_to_fresh_copy              0/3  FULL [49.25, 51.72, 49.71] vs ACC remainder [49.25, 51.72, 49.71]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.25, 51.72, 49.71]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.25, 51.72, 49.71] STORAGE_MATCHED [49.25, 51.72, 49.71] vs ACC remainder [49.25, 51.72, 49.71]

MACHINERY OF top1_cf94c8c3142ac028 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   0     0
    task  9:     0    0    0    0    0 |   0     0
    task 19:     0    0    0    0    0 |   0     0
    task 31:     0    0    0    0    0 |   0     0
    task 41:     0    0    0    0    0 |   0     0
    task 49:     0    0    0    0    0 |   0     0
  artifact events: 0 (create 0, delete 0, patch/append 0); invocations by block: {}; edges: 0
  adaptation curve ACC:   29 1579 32 2073 29 11 41 618 88 119 175 32 2073 2073 18 2073 2073 32 1579 51 52 11 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
  adaptation curve FRESH: 29 1579 32 2073 29 11 41 618 88 119 175 32 2073 2073 18 2073 2073 32 1579 51 52 11 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
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

