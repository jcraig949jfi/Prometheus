CRIUS CAMPAIGN 0 REPORT  run=search_c2c_recombination_s2  arm=recombination
code_commit=cabe092b4 dirty=True config_hash=416bbe8b9be34706 world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  22.9741   21.7861         9.0303        46         19
    26  21.9303   21.8679         7.5812        50        161
    51  20.4289   20.4289        11.1029        54        262
    76  23.9147   23.2840        14.8806        72        361
   101  23.9287   23.8851        17.3313        84        472
   126  22.9201   22.5389        21.5262        96        566
   151  20.8943   20.8943        17.0176        90        666
   176  24.9225   20.9777        19.9432        94        763
   201  20.8959   20.8955        19.0557        90        854
   226  14.8548   14.8546        13.0898        89        954
   251  21.9485   21.9485        18.6019        89       1044
   276  24.4494   23.5838        20.7668        95       1131
   300  20.9518   20.5191        16.9791        96       1192
  candidates evaluated: 7208   best_ever 28.9772 (a1dbd5ee2aa28cb6)  wall 1192s

BEST PROGRAM a1dbd5ee2aa28cb6 (len 90, iteration 199, modification swap@67,54+delete@42)
  search seed 2011990: fit 28.4758 succ 28/50 inter 2797 steps 17888 ws_cost 15 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [62.762, 1.0], "B": [99.248, 1.0], "C": [38.751, 0.5], "D": [48.988, 0.1], "E": [50.13, 0.125]}
  search seed 2011991: fit 29.4785 succ 29/50 inter 2471 steps 16792 ws_cost 15 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [66.406, 1.0], "B": [70.55, 1.0], "C": [34.677, 0.5], "D": [48.458, 0.2], "E": [46.101, 0.125]}
  listing:
      0  INPUT          R1, num_ops
      1  VGET           R7, R0, R4
      2  JMP            59
      3  BRZ            R3, 45
      4  MOV            R7, R6
      5  MOD            R3, R4, R1
      6  BLK_COPY       R5, R6
      7  ACT            R3
      8  BRNZ           R1, 81
      9  WS_LINK        R6, R6, R2
     10  BLK_REC_BEGIN  
     11  MUL            R4, R4, R4
     12  VGET           R4, R0, R1
     13  DIV            R6, R2, R5
     14  BLK_REC_BEGIN  
     15  ADD            R0, R0, R5
     16  MOV            R7, R6
     17  ADD            R0, R0, R0
     18  MUL            R6, R4, R6
     19  CONST          R0, 19
     20  MUL            R2, R1, R1
     21  CONST          R5, -19
     22  CONST          R0, -6
     23  ACT            R3
     24  DIV            R4, R0, R1
     25  ADD            R0, R0, R5
     26  CONST          R0, 1
     27  ACT            R3
     28  ADD            R0, R0, R5
     29  JMP            76
     30  CONST          R0, -3
     31  BLK_DELETE     R5
     32  BLK_INVOKE     R5
     33  MOD            R6, R1, R3
     34  ACT            R0
     35  MUL            R3, R1, R1
     36  BLK_REC_BEGIN  
     37  WS_REC_NEW     R6
     38  CONST          R0, 16
     39  ADD            R0, R2, R5
     40  MOV            R3, R4
     41  ADD            R0, R0, R5
     42  BLK_COMPOSE    R7, R0, R4
     43  CONST          R5, -2
     44  MOD            R3, R4, R1
     45  ADD            R0, R0, R5
     46  BLK_DELETE     R5
     47  VLEN           R2, R2
     48  JMP            56
     49  ADD            R0, R0, R5
     50  CONST          R0, 11
     51  ADD            R0, R2, R5
     52  BLK_REC_END    R2
     53  MUL            R2, R1, R1
     54  WS_SREAD       R7, R0, R1
     55  BLK_COMPOSE    R7, R0, R4
     56  WS_REC_SET     R4, R6, R1
     57  CONST          R0, 7
     58  BLK_INVOKE     R5
     59  SUB            R7, R5, R0
     60  VGET           R7, R0, R4
     61  ADD            R0, R0, R5
     62  ADD            R0, R0, R5
     63  CONST          R0, -2
     64  BLK_REC_END    R2
     65  LT             R7, R1, R6
     66  MUL            R2, R1, R1
     67  BLK_REC_BEGIN  
     68  ADD            R0, R0, R5
     69  VGET           R7, R0, R0
     70  ADD            R0, R0, R5
     71  ADD            R0, R0, R5
     72  ADD            R0, R0, R5
     73  ADD            R0, R0, R5
     74  ACT            R2
     75  CONST          R5, -17
     76  MUL            R3, R1, R1
     77  BRNZ           R1, 78
     78  MOD            R6, R1, R3
     79  ACT            R1
     80  ADD            R0, R0, R5
     81  MOD            R3, R0, R1
     82  ACT            R3
     83  DIV            R4, R0, R1
     84  MOD            R3, R4, R1
     85  ACT            R3
     86  DIV            R4, R4, R1
     87  MOD            R3, R4, R1
     88  ACT            R3
     89  JMP            78
  ancestry (102 steps, newest first): iteration/fitness/modification
    it  199  28.9772  len 90  swap@67,54+delete@42
    it  196  22.4241  len 91  swap@76,68
    it  195  17.3737  len 91  insert@13+delete@24
    it  194  18.4086  len 91  swap@3,46+const@21+swap@53,16
    it  193  18.9019  len 91  swap@78,76+const@20+delete@90
    it  191  21.4452  len 92  delete@25
    it  190  23.4139  len 93  delete@71+insert@9
    it  188  21.9573  len 93  delete@64+const@20
    it  186  24.4563  len 94  delete@22+delete@28
    it  185  25.4530  len 96  swap@12,51+arg@55.2+replace@42
    it  184  25.4443  len 96  const@39+duplicate@88+1->5+splice:none:1e53f56f7e775268
    it  183  24.4290  len 95  duplicate@71+1->84+arg@93.0
    it  178  20.9250  len 94  const@19+delete@58
    it  177  23.9415  len 95  duplicate@2+3->11+const@52+delete@65
    it  173  21.4119  len 93  delete@13
    ... 88 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7315.4    5.3   74.7
  ancestor80_it157_c1b94725a  23.416  23.416  23.416  23.416  23.0  23.0     9854     9854       6.9    2.0    0.0
  bestever_a1dbd5ee2aa28cb6   23.415  23.414  23.415  23.415  23.0  23.0    10053    10053       7.2    1.0    0.0
  top1_790a654baede04ee       22.446  22.446  22.446  22.446  22.0  22.0     6297     6297       7.2   32.0   49.0
  contemp_921c013113967e36    22.446  22.446  22.446  22.446  22.0  22.0     6297     6297       7.2   32.0   49.0
  top2_12b3935715b1aa23       22.100  22.100  22.100  22.100  21.7  21.7     7836     7836       7.1    1.0   49.0
  top3_1e48619c0545a267       22.100  22.100  22.100  22.100  21.7  21.7     7836     7836       7.1    1.0   49.0
  ancestor160_it298_826dd256  22.100  22.100  22.100  22.100  21.7  21.7     7836     7836       7.1   32.0   49.0
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.9    3.7    1.7
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ancestor1_it0_0875253d162c  19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0
  contemp_8ce786c2929e0d25     1.495   1.495   1.495   1.495   1.3   1.3    40142    40142       4.4    1.0   49.0
  contemp_1e32ce8c518f6074     0.153   0.153   0.153   0.153   0.0   0.0    41500    41500       2.0   32.0   49.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.02/ 455.13   14.92/ 539.10   21.12/  47.94   33.22/  48.94   40.08/  50.52
  ancestor80_it157_c1b94725a  447.03/ 447.14  435.63/ 435.77   46.62/  46.77   51.78/  51.93   50.74/  50.88
  bestever_a1dbd5ee2aa28cb6   459.42/ 459.55  442.45/ 442.59   47.93/  48.07   50.90/  51.05   51.18/  51.33
  top1_790a654baede04ee       249.18/ 249.31  256.98/ 257.12   49.77/  49.91   51.04/  51.19   52.11/  52.26
  contemp_921c013113967e36    249.18/ 249.31  256.98/ 257.12   49.77/  49.91   51.04/  51.19   52.11/  52.26
  top2_12b3935715b1aa23       374.53/ 374.66  293.47/ 293.61   49.82/  49.97   49.28/  49.42   51.04/  51.19
  top3_1e48619c0545a267       374.53/ 374.66  293.47/ 293.61   49.82/  49.97   49.28/  49.42   51.04/  51.19
  ancestor160_it298_826dd256  374.55/ 374.68  293.49/ 293.63   49.84/  49.99   49.30/  49.44   51.06/  51.21
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.14/ 443.81  528.13/ 527.79   47.94/  47.89   48.86/  48.88   50.43/  50.46
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ancestor1_it0_0875253d162c  495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  ENUMERATE_VM_C1             495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  RANDOM_C1                  1662.62/1662.62 1627.07/1627.07   50.50/  50.50   50.50/  50.50   48.56/  48.56
  contemp_8ce786c2929e0d25   2004.69/2004.77 2004.82/2004.91   49.60/  49.69   52.05/  52.14   52.05/  52.14
  contemp_1e32ce8c518f6074   2055.27/2055.31 2055.27/2055.31   51.64/  51.68   51.64/  51.68   51.64/  51.68

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  ancestor80_it157_c1b94725a     7/36    44     1/30    49     0/12    50     1/12    47    30/30   428    30/30   417
  bestever_a1dbd5ee2aa28cb6      7/36    46     1/30    49     0/12    50     1/12    48    30/30   440    30/30   423
  top1_790a654baede04ee          5/36    47     1/30    49     0/12    50     0/12    50    30/30   238    30/30   246
  contemp_921c013113967e36       5/36    47     1/30    49     0/12    50     0/12    50    30/30   238    30/30   246
  top2_12b3935715b1aa23          4/36    48     2/30    47     1/12    48     0/12    50    28/30   359    30/30   281
  top3_1e48619c0545a267          4/36    48     2/30    47     1/12    48     0/12    50    28/30   359    30/30   281
  ancestor160_it298_826dd256     4/36    48     2/30    47     1/12    48     0/12    50    28/30   359    30/30   281
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ancestor1_it0_0875253d162c     2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610
  contemp_8ce786c2929e0d25       2/36    48     0/30    50     0/12    50     0/12    50     1/30  1934     1/30  1934
  contemp_1e32ce8c518f6074       0/36    50     0/30    50     0/12    50     0/12    50     0/30  2000     0/30  2000

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.27    49.53    36.27    36.27    49.53    49.53    49.53   5.0
  ancestor80_it157_c1b94725a    51.31    51.32    51.31    51.31    51.33    51.33    51.33   1.0
  bestever_a1dbd5ee2aa28cb6     51.02    51.03    51.02    51.02    51.03    51.03    51.03   1.0
  top1_790a654baede04ee         51.51    51.52    51.51    51.51    51.52    51.52    51.52  32.0
  contemp_921c013113967e36      51.51    51.52    51.51    51.51    51.52    51.52    51.52  32.0
  top2_12b3935715b1aa23         50.06    50.07    50.06    50.06    50.07    50.07    50.07   1.0
  top3_1e48619c0545a267         50.06    50.07    50.06    50.06    50.07    50.07    50.07   1.0
  ancestor160_it298_826dd256    50.08    50.09    50.08    50.08    50.09    50.09    50.09  32.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.56    49.55    49.56    49.56    49.55    49.55    49.55   2.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ancestor1_it0_0875253d162c    51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  ENUMERATE_VM_C1               51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  RANDOM_C1                     49.64       --    49.64    49.64    49.64    49.64    49.64   0.0
  contemp_8ce786c2929e0d25      52.05    52.05    52.05    52.05    52.05    52.05    52.05   1.0
  contemp_1e32ce8c518f6074      51.64    51.64    51.64    51.64    51.64    51.64    51.64  32.0

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
  ancestor80_it157_c1b94725a5360899
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [22, 24, 23] vs FRESH [22, 24, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.4, 4.4, 4.4] vs 5% of FRESH cost [1494.2, 1479.5, 1488.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.22, 52.3, 51.43] vs CODE_ONLY [50.23, 52.32, 51.45]
    4_scramble_or_reset_damages            0/3  eff ACC [22.397, 24.416, 23.436] SCR [22.397, 24.416, 23.436] RESET [22.397, 24.416, 23.436]
    5_transfers_to_fresh_copy              0/3  FULL [50.22, 52.3, 51.43] vs ACC remainder [50.22, 52.3, 51.43]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [50.22, 52.31, 51.44] vs ACC remainder [50.22, 52.3, 51.43]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.23, 52.32, 51.45] STORAGE_MATCHED [50.23, 52.32, 51.45] vs ACC remainder [50.22, 52.3, 51.43]
  bestever_a1dbd5ee2aa28cb6
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [22, 24, 23] vs FRESH [22, 24, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.3] vs 5% of FRESH cost [1516.8, 1527.1, 1450.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.83, 52.22, 50.02] vs CODE_ONLY [50.84, 52.23, 50.03]
    4_scramble_or_reset_damages            0/3  eff ACC [22.395, 24.414, 23.435] SCR [22.395, 24.414, 23.435] RESET [22.395, 24.414, 23.435]
    5_transfers_to_fresh_copy              0/3  FULL [50.83, 52.22, 50.02] vs ACC remainder [50.83, 52.22, 50.02]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [50.84, 52.23, 50.03] vs ACC remainder [50.83, 52.22, 50.02]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.84, 52.23, 50.03] STORAGE_MATCHED [50.84, 52.23, 50.03] vs ACC remainder [50.83, 52.22, 50.02]
  top1_790a654baede04ee
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 21, 25] vs FRESH [20, 21, 25]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.4] vs 5% of FRESH cost [1567.8, 1551.1, 1467.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.11, 52.11, 50.32] vs CODE_ONLY [52.12, 52.12, 50.33]
    4_scramble_or_reset_damages            0/3  eff ACC [20.449, 21.437, 25.454] SCR [20.449, 21.437, 25.454] RESET [20.449, 21.437, 25.454]
    5_transfers_to_fresh_copy              0/3  FULL [52.11, 52.11, 50.32] vs ACC remainder [52.11, 52.11, 50.32]
    6_executable_components_reused         0/3  invocations [49, 49, 49]; ABLATION_ALL cost [52.12, 52.12, 50.33] vs ACC remainder [52.11, 52.11, 50.32]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.12, 52.12, 50.33] STORAGE_MATCHED [52.12, 52.12, 50.33] vs ACC remainder [52.11, 52.11, 50.32]
  contemp_921c013113967e36
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 21, 25] vs FRESH [20, 21, 25]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.4] vs 5% of FRESH cost [1567.8, 1551.1, 1467.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.11, 52.11, 50.32] vs CODE_ONLY [52.12, 52.12, 50.33]
    4_scramble_or_reset_damages            0/3  eff ACC [20.449, 21.437, 25.454] SCR [20.449, 21.437, 25.454] RESET [20.449, 21.437, 25.454]
    5_transfers_to_fresh_copy              0/3  FULL [52.11, 52.11, 50.32] vs ACC remainder [52.11, 52.11, 50.32]
    6_executable_components_reused         0/3  invocations [49, 49, 49]; ABLATION_ALL cost [52.12, 52.12, 50.33] vs ACC remainder [52.11, 52.11, 50.32]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.12, 52.12, 50.33] STORAGE_MATCHED [52.12, 52.12, 50.33] vs ACC remainder [52.11, 52.11, 50.32]
  top2_12b3935715b1aa23
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [21, 21, 23] vs FRESH [21, 21, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.3] vs 5% of FRESH cost [1541.9, 1532.5, 1435.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.69, 52.08, 47.41] vs CODE_ONLY [50.7, 52.09, 47.41]
    4_scramble_or_reset_damages            0/3  eff ACC [21.45, 21.402, 23.448] SCR [21.45, 21.402, 23.448] RESET [21.45, 21.402, 23.448]
    5_transfers_to_fresh_copy              0/3  FULL [50.69, 52.08, 47.41] vs ACC remainder [50.69, 52.08, 47.41]
    6_executable_components_reused         0/3  invocations [49, 49, 49]; ABLATION_ALL cost [50.7, 52.09, 47.41] vs ACC remainder [50.69, 52.08, 47.41]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.7, 52.09, 47.41] STORAGE_MATCHED [50.7, 52.09, 47.41] vs ACC remainder [50.69, 52.08, 47.41]
  top3_1e48619c0545a267
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [21, 21, 23] vs FRESH [21, 21, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.3] vs 5% of FRESH cost [1541.9, 1532.5, 1435.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.69, 52.08, 47.41] vs CODE_ONLY [50.7, 52.09, 47.41]
    4_scramble_or_reset_damages            0/3  eff ACC [21.45, 21.402, 23.448] SCR [21.45, 21.402, 23.448] RESET [21.45, 21.402, 23.448]
    5_transfers_to_fresh_copy              0/3  FULL [50.69, 52.08, 47.41] vs ACC remainder [50.69, 52.08, 47.41]
    6_executable_components_reused         0/3  invocations [49, 49, 49]; ABLATION_ALL cost [50.7, 52.09, 47.41] vs ACC remainder [50.69, 52.08, 47.41]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.7, 52.09, 47.41] STORAGE_MATCHED [50.7, 52.09, 47.41] vs ACC remainder [50.69, 52.08, 47.41]
  ancestor160_it298_826dd2569772aa8e
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [21, 21, 23] vs FRESH [21, 21, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.3] vs 5% of FRESH cost [1542.5, 1533.1, 1436.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.71, 52.1, 47.43] vs CODE_ONLY [50.72, 52.11, 47.43]
    4_scramble_or_reset_damages            0/3  eff ACC [21.45, 21.402, 23.448] SCR [21.45, 21.402, 23.448] RESET [21.45, 21.402, 23.448]
    5_transfers_to_fresh_copy              0/3  FULL [50.71, 52.1, 47.43] vs ACC remainder [50.71, 52.1, 47.43]
    6_executable_components_reused         0/3  invocations [49, 49, 49]; ABLATION_ALL cost [50.72, 52.11, 47.43] vs ACC remainder [50.71, 52.1, 47.43]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.72, 52.11, 47.43] STORAGE_MATCHED [50.72, 52.11, 47.43] vs ACC remainder [50.71, 52.1, 47.43]
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
  contemp_8ce786c2929e0d25
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [1, 3, 0] vs FRESH [1, 3, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [2.7, 2.7, 2.7] vs 5% of FRESH cost [1520.6, 1519.5, 1564.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.05, 52.05, 52.05] vs CODE_ONLY [52.05, 52.05, 52.05]
    4_scramble_or_reset_damages            0/3  eff ACC [1.151, 3.184, 0.15] SCR [1.151, 3.184, 0.15] RESET [1.15, 3.184, 0.15]
    5_transfers_to_fresh_copy              0/3  FULL [52.05, 52.05, 52.05] vs ACC remainder [52.05, 52.05, 52.05]
    6_executable_components_reused         0/3  invocations [49, 49, 49]; ABLATION_ALL cost [52.05, 52.05, 52.05] vs ACC remainder [52.05, 52.05, 52.05]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.05, 52.05, 52.05] STORAGE_MATCHED [52.05, 52.05, 52.05] vs ACC remainder [52.05, 52.05, 52.05]
  contemp_1e32ce8c518f6074
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [1.2, 1.2, 1.2] vs 5% of FRESH cost [1550.4, 1550.4, 1550.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.64, 51.64, 51.64] vs CODE_ONLY [51.64, 51.64, 51.64]
    4_scramble_or_reset_damages            0/3  eff ACC [0.153, 0.153, 0.153] SCR [0.153, 0.153, 0.153] RESET [0.153, 0.153, 0.153]
    5_transfers_to_fresh_copy              0/3  FULL [51.64, 51.64, 51.64] vs ACC remainder [51.64, 51.64, 51.64]
    6_executable_components_reused         0/3  invocations [49, 49, 49]; ABLATION_ALL cost [51.64, 51.64, 51.64] vs ACC remainder [51.64, 51.64, 51.64]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.64, 51.64, 51.64] STORAGE_MATCHED [51.64, 51.64, 51.64] vs ACC remainder [51.64, 51.64, 51.64]

MACHINERY OF top1_790a654baede04ee (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   2    42
    task  9:     0    0    0    0    0 |  11   132
    task 19:     0    0    0    0    0 |  21   232
    task 31:     0    0    0    0    0 |  32   342
    task 41:     0    0    0    0    0 |  32   342
    task 49:     0    0    0    0    0 |  32   342
  artifact events: 32 (create 32, delete 0, patch/append 0); invocations by block: {"0": 49}; edges: 0
    block 0 origin=calibration len=0 state=[[2, 3, 6, 8, 10, 4, 9, 11, 5, 0, 7, 1], [9, 11, 0, 1, 5, 8, 2, 10, 3, 6, 4, 7], 0] instr=[]
    block 1 origin=new len=0 state=[0, 0, 0] instr=[]
    block 2 origin=new len=0 state=[0, 0, 0] instr=[]
    block 3 origin=new len=0 state=[0, 0, 0] instr=[]
    block 4 origin=new len=0 state=[0, 0, 0] instr=[]
  adaptation curve ACC:   90 1026 15 492 89 89 127 31 105 49 61 15 492 492 89 190 190 15 1026 12 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
  adaptation curve FRESH: 90 1027 15 492 90 90 127 31 105 49 62 15 492 492 90 190 190 15 1027 12 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
  reuse_gain per task:    0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0

BASELINES ON SEARCH SUITE (crius/runs/baselines_c2c): effA effF effR effS  succA  interA interF  reuse_gain  blocks
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

