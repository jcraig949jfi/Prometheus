CRIUS CAMPAIGN 0 REPORT  run=search_c2a_seeded_s2  arm=seeded
code_commit=6eb2d2ac7 dirty=True config_hash=401915ec4da9443a world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  21.4764   21.4113        10.1499        39          4
    26  22.4315   22.4315        13.8855        47         89
    51  19.9326   19.9321        12.4811        45        161
    76  23.9163   23.4781        16.8981        56        241
   101  19.8201   19.8201        13.8349        54        304
   126  23.9187   23.9187        18.9667        59        364
   151  23.9162   22.1630        15.7744        58        413
   176  19.9119   18.5694        12.5758        56        471
   201  22.4001   22.4001        17.8735        48        525
   226  18.4122   18.4122        12.1693        36        583
   251  25.4454   23.1902        15.5125        29        646
   276  24.9420   24.8796        15.2275        27        720
   300  21.4500   21.4500        13.2005        20        795
  candidates evaluated: 7208   best_ever 28.4689 (1543189913659f15)  wall 795s

BEST PROGRAM 1543189913659f15 (len 50, iteration 199, modification replace@31+delete@8)
  search seed 2011990: fit 28.4707 succ 28/50 inter 3421 steps 18633 ws_cost 100 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [125.379, 1.0], "B": [104.54, 1.0], "C": [34.81, 0.5], "D": [48.004, 0.1], "E": [51.422, 0.125]}
  search seed 2011991: fit 28.4672 succ 28/50 inter 3835 steps 20147 ws_cost 100 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [123.509, 1.0], "B": [151.501, 1.0], "C": [38.186, 0.417], "D": [47.588, 0.1], "E": [44.158, 0.25]}
  listing:
      0  MUL            R6, R6, R0
      1  INPUT          R1, num_ops
      2  ACT            R1
      3  MOD            R3, R5, R1
      4  ADD            R0, R0, R5
      5  CONST          R5, 19
      6  CONST          R0, 5
      7  MOD            R3, R4, R1
      8  BLK_INVOKE     R1
      9  JMP            36
     10  WS_LINKS       R4, R7
     11  ACT            R2
     12  INPUT          R5, last_delta
     13  ACT            R6
     14  WS_FREE        R5
     15  NOT            R2, R0
     16  WS_LINKS       R4, R7
     17  ACT            R3
     18  BLK_STATE_SET  R3, R6, R4
     19  INPUT          R7, interactions_left
     20  BLK_INVOKE     R1
     21  BLK_REC_END    R7
     22  BLK_REC_END    R6
     23  ACT            R3
     24  DIV            R4, R0, R1
     25  WS_REC_NEW     R6
     26  JMP            40
     27  BLK_APPEND     R2, R3
     28  BLK_INVOKE     R6
     29  MOD            R3, R4, R1
     30  WS_WRITE       R7, R6
     31  JMP            41
     32  MOD            R3, R6, R1
     33  BLK_PATCH      R0, R7, R1
     34  BLK_INVOKE     R1
     35  DIV            R4, R0, R1
     36  BLK_LEN        R0, R2
     37  ADD            R0, R0, R5
     38  MOD            R3, R0, R1
     39  ACT            R3
     40  DIV            R4, R0, R1
     41  MOD            R3, R4, R1
     42  ACT            R3
     43  DIV            R4, R4, R1
     44  MOD            R3, R4, R1
     45  ACT            R3
     46  ACT            R1
     47  JMP            37
     48  MOD            R3, R0, R1
     49  WS_FREE        R5
  ancestry (87 steps, newest first): iteration/fitness/modification
    it  199  28.4689  len 50  replace@31+delete@8
    it  198  22.4020  len 51  duplicate@34+1->21
    it  197  20.4106  len 50  const@5
    it  196  23.9172  len 50  insert@25
    it  195  20.4156  len 49  delete@2+delete@8
    it  194  19.8741  len 51  delete@21+duplicate@13+1->19+delete@21
    it  192  22.4552  len 52  duplicate@39+2->26+const@7+const@7
    it  191  22.4490  len 50  delete@18+replace@16+delete@2
    it  187  21.9572  len 52  swap@39,48
    it  186  26.4466  len 52  delete@38
    it  182  20.4221  len 53  delete@25
    it  180  19.9260  len 54  delete@9
    it  179  20.9230  len 55  arg@8.1+swap@15,39+delete@37
    it  177  22.4542  len 56  delete@13
    it  175  21.9386  len 57  replace@0+replace@12
    ... 73 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7316.0    4.3   74.7
  ancestor64_it139_aeb781382  23.778  23.778  23.778  23.778  23.3  23.3     6441     6441       0.0    0.0    0.0
  top1_ce61878157317f70       22.094  22.094  22.094  22.094  21.7  21.7     8553     8553       0.0    0.0    0.0
  top2_0e8904e0574c0fe7       22.094  22.094  22.094  22.094  21.7  21.7     8553     8553       0.0    0.0    0.0
  ancestor126_it292_275577db  22.094  22.094  22.094  22.094  21.7  21.7     8553     8553       0.0    0.0    0.0
  top3_270cf31aef2ed97e       22.094  22.094  22.094  22.094  21.7  21.7     8553     8553       0.0    0.0    0.0
  bestever_1543189913659f15   21.091  21.091  21.091  21.091  20.7  20.7     8958     8958       0.0    0.0    0.0
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.3    2.7    1.7
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ancestor1_it0_0875253d162c  19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       0.0    0.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       0.0    0.0    0.0
  contemp_f312bc39b49f5c04    16.317   0.150  16.041  16.317  16.0   0.0    13919    41500   20460.7   32.0    0.0
  contemp_3320569baafc3c57     8.234   8.234   8.234   8.234   8.0   8.0    31553    31553       0.0    0.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0
  contemp_61d53edc45237fc8     2.844   2.844   2.844   2.844   2.7   2.7    37132    37132       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.00/ 455.13   14.90/ 539.10   21.11/  47.94   33.21/  48.94   40.07/  50.52
  ancestor64_it139_aeb781382  263.02/ 263.02  263.99/ 263.99   47.38/  47.38   50.21/  50.21   51.59/  51.59
  top1_ce61878157317f70       350.06/ 350.06  393.33/ 393.33   46.60/  46.60   50.33/  50.33   51.85/  51.85
  top2_0e8904e0574c0fe7       350.07/ 350.07  393.34/ 393.34   46.61/  46.61   50.34/  50.34   51.86/  51.86
  ancestor126_it292_275577db  350.07/ 350.07  393.34/ 393.34   46.61/  46.61   50.34/  50.34   51.86/  51.86
  top3_270cf31aef2ed97e       350.08/ 350.08  393.35/ 393.35   46.62/  46.62   50.35/  50.35   51.87/  51.87
  bestever_1543189913659f15   333.64/ 333.64  449.23/ 449.23   48.46/  48.46   51.15/  51.15   51.43/  51.43
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.13/ 443.81  528.11/ 527.79   47.93/  47.89   48.85/  48.88   50.42/  50.46
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ancestor1_it0_0875253d162c  495.80/ 495.80  525.01/ 525.01   50.10/  50.10   51.09/  51.09   52.68/  52.68
  ENUMERATE_VM_C1             495.80/ 495.80  525.01/ 525.01   50.10/  50.10   51.09/  51.09   52.68/  52.68
  contemp_f312bc39b49f5c04    633.37/2073.40  753.67/2073.40   49.45/  51.90  450.03/  51.90  450.03/  51.90
  contemp_3320569baafc3c57   1436.72/1436.72 1688.64/1688.64   47.67/  47.67   49.95/  49.95   50.30/  50.30
  RANDOM_C1                  1662.62/1662.62 1627.07/1627.07   50.50/  50.50   50.50/  50.50   48.56/  48.56
  contemp_61d53edc45237fc8   1939.48/1939.48 1875.24/1875.24   52.20/  52.20   53.51/  53.51   53.51/  53.51

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  ancestor64_it139_aeb781382     5/36    45     4/30    48     1/12    49     0/12    50    30/30   251    30/30   252
  top1_ce61878157317f70          7/36    45     1/30    48     0/12    50     0/12    50    29/30   336    28/30   378
  top2_0e8904e0574c0fe7          7/36    45     1/30    48     0/12    50     0/12    50    29/30   336    28/30   378
  ancestor126_it292_275577db     7/36    45     1/30    48     0/12    50     0/12    50    29/30   336    28/30   378
  top3_270cf31aef2ed97e          7/36    45     1/30    48     0/12    50     0/12    50    29/30   336    28/30   378
  bestever_1543189913659f15      3/36    46     1/30    49     0/12    50     1/12    49    29/30   320    28/30   431
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ancestor1_it0_0875253d162c     2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  contemp_f312bc39b49f5c04       2/36    48     0/30     0     0/12     0     0/12     0    24/30   609    22/30   726
  contemp_3320569baafc3c57       5/36    46     2/30    48     0/12    50     1/12    47    10/30  1385     6/30  1628
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610
  contemp_61d53edc45237fc8       1/36    49     0/30    50     0/12    50     0/12    50     3/30  1812     4/30  1752

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.26    49.53    36.26    36.26    49.53    49.53    49.53   4.0
  ancestor64_it139_aeb781382    50.82       --    50.82    50.82    50.82    50.82    50.82   0.0
  top1_ce61878157317f70         51.00       --    51.00    51.00    51.00    51.00    51.00   0.0
  top2_0e8904e0574c0fe7         51.01       --    51.01    51.01    51.01    51.01    51.01   0.0
  ancestor126_it292_275577db    51.01       --    51.01    51.01    51.01    51.01    51.01   0.0
  top3_270cf31aef2ed97e         51.02       --    51.02    51.02    51.02    51.02    51.02   0.0
  bestever_1543189913659f15     51.28       --    51.28    51.28    51.28    51.28    51.28   0.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.55    49.55    49.55    49.55    49.55    49.55    49.55   1.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ancestor1_it0_0875253d162c    51.80       --    51.80    51.80    51.80    51.80    51.80   0.0
  ENUMERATE_VM_C1               51.80       --    51.80    51.80    51.80    51.80    51.80   0.0
  contemp_f312bc39b49f5c04     450.03    51.61   450.03   450.03    51.94    51.94    51.94  32.0
  contemp_3320569baafc3c57      50.11       --    50.11    50.11    50.11    50.11    50.11   0.0
  RANDOM_C1                     49.64       --    49.64    49.64    49.64    49.64    49.64   0.0
  contemp_61d53edc45237fc8      53.51       --    53.51    53.51    53.51    53.51    53.51   0.0

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
  ancestor64_it139_aeb7813824103a6f
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [23, 22, 25] vs FRESH [23, 22, 25]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1491.7, 1492.9, 1465.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.36, 52.16, 49.95] vs CODE_ONLY [50.36, 52.16, 49.95]
    4_scramble_or_reset_damages            0/3  eff ACC [23.414, 22.461, 25.46] SCR [23.414, 22.461, 25.46] RESET [23.414, 22.461, 25.46]
    5_transfers_to_fresh_copy              0/3  FULL [50.36, 52.16, 49.95] vs ACC remainder [50.36, 52.16, 49.95]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.36, 52.16, 49.95]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.36, 52.16, 49.95] STORAGE_MATCHED [50.36, 52.16, 49.95] vs ACC remainder [50.36, 52.16, 49.95]
  top1_ce61878157317f70
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [21, 19, 25] vs FRESH [21, 19, 25]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1526.4, 1521.2, 1384.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.85, 51.85, 49.31] vs CODE_ONLY [51.85, 51.85, 49.31]
    4_scramble_or_reset_damages            0/3  eff ACC [21.429, 19.401, 25.452] SCR [21.429, 19.401, 25.452] RESET [21.429, 19.401, 25.452]
    5_transfers_to_fresh_copy              0/3  FULL [51.85, 51.85, 49.31] vs ACC remainder [51.85, 51.85, 49.31]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.85, 51.85, 49.31]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.85, 51.85, 49.31] STORAGE_MATCHED [51.85, 51.85, 49.31] vs ACC remainder [51.85, 51.85, 49.31]
  top2_0e8904e0574c0fe7
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [21, 19, 25] vs FRESH [21, 19, 25]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1526.7, 1521.5, 1384.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.86, 51.86, 49.32] vs CODE_ONLY [51.86, 51.86, 49.32]
    4_scramble_or_reset_damages            0/3  eff ACC [21.429, 19.401, 25.452] SCR [21.429, 19.401, 25.452] RESET [21.429, 19.401, 25.452]
    5_transfers_to_fresh_copy              0/3  FULL [51.86, 51.86, 49.32] vs ACC remainder [51.86, 51.86, 49.32]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.86, 51.86, 49.32]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.86, 51.86, 49.32] STORAGE_MATCHED [51.86, 51.86, 49.32] vs ACC remainder [51.86, 51.86, 49.32]
  ancestor126_it292_275577db7d224b86
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [21, 19, 25] vs FRESH [21, 19, 25]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1526.7, 1521.5, 1384.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.86, 51.86, 49.32] vs CODE_ONLY [51.86, 51.86, 49.32]
    4_scramble_or_reset_damages            0/3  eff ACC [21.429, 19.401, 25.452] SCR [21.429, 19.401, 25.452] RESET [21.429, 19.401, 25.452]
    5_transfers_to_fresh_copy              0/3  FULL [51.86, 51.86, 49.32] vs ACC remainder [51.86, 51.86, 49.32]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.86, 51.86, 49.32]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.86, 51.86, 49.32] STORAGE_MATCHED [51.86, 51.86, 49.32] vs ACC remainder [51.86, 51.86, 49.32]
  top3_270cf31aef2ed97e
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [21, 19, 25] vs FRESH [21, 19, 25]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1527.0, 1521.8, 1384.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.87, 51.87, 49.33] vs CODE_ONLY [51.87, 51.87, 49.33]
    4_scramble_or_reset_damages            0/3  eff ACC [21.429, 19.401, 25.452] SCR [21.429, 19.401, 25.452] RESET [21.429, 19.401, 25.452]
    5_transfers_to_fresh_copy              0/3  FULL [51.87, 51.87, 49.33] vs ACC remainder [51.87, 51.87, 49.33]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.87, 51.87, 49.33]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.87, 51.87, 49.33] STORAGE_MATCHED [51.87, 51.87, 49.33] vs ACC remainder [51.87, 51.87, 49.33]
  bestever_1543189913659f15
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [21, 18, 23] vs FRESH [21, 18, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1511.8, 1512.8, 1488.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.95, 51.95, 49.93] vs CODE_ONLY [51.95, 51.95, 49.93]
    4_scramble_or_reset_damages            0/3  eff ACC [21.422, 18.394, 23.456] SCR [21.422, 18.394, 23.456] RESET [21.422, 18.394, 23.456]
    5_transfers_to_fresh_copy              0/3  FULL [51.95, 51.95, 49.93] vs ACC remainder [51.95, 51.95, 49.93]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.95, 51.95, 49.93]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.95, 51.95, 49.93] STORAGE_MATCHED [51.95, 51.95, 49.93] vs ACC remainder [51.95, 51.95, 49.93]
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
  contemp_f312bc39b49f5c04
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [15, 16, 17] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [-7166.3, -7119.6, -7124.8] vs 5% of FRESH cost [1557.0, 1557.0, 1557.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [450.03, 450.03, 450.03] vs CODE_ONLY [52.01, 51.9, 51.9]
    4_scramble_or_reset_damages            0/3  eff ACC [15.317, 16.296, 17.337] SCR [15.317, 16.296, 17.337] RESET [15.375, 16.354, 16.395]
    5_transfers_to_fresh_copy              0/3  FULL [450.03, 450.03, 450.03] vs ACC remainder [450.03, 450.03, 450.03]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.9, 51.03, 51.9] vs ACC remainder [450.03, 450.03, 450.03]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.01, 51.9, 51.9] STORAGE_MATCHED [52.01, 51.9, 51.9] vs ACC remainder [450.03, 450.03, 450.03]
  contemp_3320569baafc3c57
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [11, 5, 8] vs FRESH [11, 5, 8]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1459.2, 1546.4, 1416.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.78, 51.86, 48.68] vs CODE_ONLY [49.78, 51.86, 48.68]
    4_scramble_or_reset_damages            0/3  eff ACC [11.276, 5.212, 8.214] SCR [11.276, 5.212, 8.214] RESET [11.276, 5.212, 8.214]
    5_transfers_to_fresh_copy              0/3  FULL [49.78, 51.86, 48.68] vs ACC remainder [49.78, 51.86, 48.68]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.78, 51.86, 48.68]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.78, 51.86, 48.68] STORAGE_MATCHED [49.78, 51.86, 48.68] vs ACC remainder [49.78, 51.86, 48.68]
  RANDOM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 6, 9] vs FRESH [6, 6, 9]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1493.8, 1515.0, 1489.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.32, 50.5, 49.1] vs CODE_ONLY [49.32, 50.5, 49.1]
    4_scramble_or_reset_damages            0/3  eff ACC [6.205, 6.235, 9.221] SCR [6.205, 6.235, 9.221] RESET [6.205, 6.235, 9.221]
    5_transfers_to_fresh_copy              0/3  FULL [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.32, 50.5, 49.1]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.32, 50.5, 49.1] STORAGE_MATCHED [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
  contemp_61d53edc45237fc8
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 5, 3] vs FRESH [0, 5, 3]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1605.3, 1558.1, 1605.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [53.51, 53.51, 53.51] vs CODE_ONLY [53.51, 53.51, 53.51]
    4_scramble_or_reset_damages            0/3  eff ACC [0.139, 5.204, 3.188] SCR [0.139, 5.204, 3.188] RESET [0.139, 5.204, 3.188]
    5_transfers_to_fresh_copy              0/3  FULL [53.51, 53.51, 53.51] vs ACC remainder [53.51, 53.51, 53.51]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [53.51, 53.51, 53.51]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [53.51, 53.51, 53.51] STORAGE_MATCHED [53.51, 53.51, 53.51] vs ACC remainder [53.51, 53.51, 53.51]

MACHINERY OF top1_ce61878157317f70 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   0     0
    task  9:     0    0    0    0    0 |   0     0
    task 19:     0    0    0    0    0 |   0     0
    task 31:     0    0    0    0    0 |   0     0
    task 41:     0    0    0    0    0 |   0     0
    task 49:     0    0    0    0    0 |   0     0
  artifact events: 0 (create 0, delete 0, patch/append 0); invocations by block: {}; edges: 0
  adaptation curve ACC:   262 158 188 1209 98 262 26 1227 259 110 122 188 1209 1209 262 89 89 18 158 73 52 23 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
  adaptation curve FRESH: 262 158 188 1209 98 262 26 1227 259 110 122 188 1209 1209 262 89 89 18 158 73 52 23 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
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

