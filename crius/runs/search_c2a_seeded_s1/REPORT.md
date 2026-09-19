CRIUS CAMPAIGN 0 REPORT  run=search_c2a_seeded_s1  arm=seeded
code_commit=6eb2d2ac7 dirty=True config_hash=401915ec4da9443a world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  21.9630   21.5182        10.3728        39         15
    26  21.4378   21.0012        15.5631        52        109
    51  24.4542   24.4541        16.6345        52        211
    76  22.4156   20.2140        12.4196        52        315
   101  20.4177   20.4177        14.7650        49        402
   126  25.4384   25.4383        16.3233        43        480
   151  21.3372   21.3371        13.1176        40        559
   176  18.8779   18.8778        12.7573        48        640
   201  25.4557   25.4557        16.4992        47        702
   226  27.9251   26.8072        18.6806        42        772
   251  20.8985   20.5874        15.6481        43        849
   276  20.3968   19.0639        10.5381        40        926
   300  23.4193   22.7925        15.4728        33        998
  candidates evaluated: 7208   best_ever 29.9533 (acdc2bec37723319)  wall 998s

BEST PROGRAM acdc2bec37723319 (len 39, iteration 240, modification delete@17)
  search seed 1012400: fit 28.4239 succ 28/50 inter 8947 steps 41730 ws_cost 0 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [527.312, 1.0], "B": [274.667, 1.0], "C": [45.355, 0.25], "D": [46.201, 0.3], "E": [42.28, 0.25]}
  search seed 1012401: fit 31.4828 succ 31/50 inter 1975 steps 14343 ws_cost 0 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [53.737, 1.0], "B": [31.585, 1.0], "C": [37.093, 0.583], "D": [43.817, 0.2], "E": [47.74, 0.25]}
  listing:
      0  INPUT          R1, num_ops
      1  MOV            R2, R1
      2  BRZ            R7, 24
      3  BLK_APPEND     R2, R7
      4  ACT            R4
      5  INPUT          R6, current_block
      6  WS_SLEN        R0, R3
      7  JMP            17
      8  WS_APPEND      R5, R4
      9  DIV            R4, R0, R0
     10  ADD            R0, R0, R5
     11  LT             R5, R0, R2
     12  CONST          R0, 27
     13  DIV            R4, R7, R2
     14  ACTI           5
     15  ACT            R1
     16  BLK_LEN        R7, R2
     17  ADD            R0, R0, R5
     18  MOD            R4, R0, R5
     19  ADD            R0, R0, R4
     20  ADD            R0, R0, R5
     21  BRZ            R3, 26
     22  WS_SREAD       R0, R6, R1
     23  BLK_REC_END    R3
     24  LT             R5, R0, R2
     25  CONST          R0, 38
     26  VLEN           R5, R7
     27  ADD            R0, R0, R5
     28  MOD            R3, R0, R1
     29  ACT            R3
     30  DIV            R4, R0, R1
     31  MOD            R3, R4, R1
     32  BRZ            R3, 19
     33  ACT            R3
     34  DIV            R4, R4, R1
     35  MOD            R3, R4, R1
     36  ACT            R3
     37  ACT            R1
     38  JMP            27
  ancestry (125 steps, newest first): iteration/fitness/modification
    it  240  29.9533  len 39  delete@17
    it  237  22.9339  len 40  arg@27.0+replace@16+arg@20.2
    it  234  20.4341  len 40  const@12+delete@18
    it  233  24.9620  len 41  delete@5
    it  231  22.4073  len 42  replace@18+arg@4.0+const@15
    it  229  19.8655  len 42  arg@4.0
    it  227  24.4162  len 42  const@27+insert@3
    it  226  26.4345  len 41  arg@5.0
    it  224  20.9213  len 41  insert@21+delete@7
    it  222  20.9045  len 41  delete@17+insert@40+delete@40
    it  221  25.9367  len 42  delete@21
    it  220  20.9210  len 43  delete@9
    it  216  20.9388  len 44  delete@22
    it  213  20.4120  len 45  swap@24,18
    it  210  20.9349  len 45  const@31
    ... 111 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7316.0    4.3   74.7
  top1_8250b21b407b14dd       22.758  22.758  22.758  22.758  22.3  22.3     8860     8860       0.0    0.0    0.0
  contemp_c783c2b9ca157abb    22.424  22.424  22.424  22.424  22.0  22.0     8992     8992       0.0    0.0    0.0
  ancestor151_it297_76966cae  22.424  22.424  22.424  22.424  22.0  22.0     8992     8992       0.0    0.0    0.0
  top3_1f8b67db89bc64ce       22.423  22.423  22.423  22.423  22.0  22.0     9058     9058       0.0    0.0    0.0
  bestever_acdc2bec37723319   22.421  22.421  22.421  22.421  22.0  22.0     9276     9276       0.0    0.0    0.0
  top2_7095c6da3c6fc847       21.757  21.757  21.757  21.757  21.3  21.3     8960     8960       0.0    0.0    0.0
  ancestor76_it135_7473bb0c0  21.081  21.081  21.081  21.081  20.7  20.7    10113    10113       0.0    0.0    0.0
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.3    2.7    1.7
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ancestor1_it0_0875253d162c  19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       0.0    0.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       0.0    0.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0
  contemp_888cb11115e53533     1.155   1.822   0.822   1.155   1.0   1.7    40161    40132     -19.3    0.0    0.0
  contemp_faf56f6315ff0f7a     0.129   0.129   0.129   0.129   0.0   0.0    41500    41500       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.00/ 455.13   14.90/ 539.10   21.11/  47.94   33.21/  48.94   40.07/  50.52
  top1_8250b21b407b14dd       380.57/ 380.57  397.66/ 397.66   46.30/  46.30   50.71/  50.71   52.03/  52.03
  contemp_c783c2b9ca157abb    386.60/ 386.60  403.90/ 403.90   47.34/  47.34   50.92/  50.92   52.03/  52.03
  ancestor151_it297_76966cae  386.60/ 386.60  403.90/ 403.90   47.34/  47.34   50.92/  50.92   52.03/  52.03
  top3_1f8b67db89bc64ce       389.63/ 389.63  407.03/ 407.03   47.86/  47.86   51.02/  51.02   52.03/  52.03
  bestever_acdc2bec37723319   402.43/ 402.43  415.67/ 415.67   48.48/  48.48   51.56/  51.56   52.05/  52.05
  top2_7095c6da3c6fc847       378.17/ 378.17  410.71/ 410.71   49.48/  49.48   48.60/  48.60   51.56/  51.56
  ancestor76_it135_7473bb0c0  430.58/ 430.58  475.47/ 475.47   49.45/  49.45   51.16/  51.16   50.19/  50.19
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.13/ 443.81  528.11/ 527.79   47.93/  47.89   48.85/  48.88   50.42/  50.46
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ancestor1_it0_0875253d162c  495.80/ 495.80  525.01/ 525.01   50.10/  50.10   51.09/  51.09   52.68/  52.68
  ENUMERATE_VM_C1             495.80/ 495.80  525.01/ 525.01   50.10/  50.10   51.09/  51.09   52.68/  52.68
  RANDOM_C1                  1662.62/1662.62 1627.07/1627.07   50.50/  50.50   50.50/  50.50   48.56/  48.56
  contemp_888cb11115e53533   1970.28/1970.12 2110.27/2110.49   53.02/  51.85   53.02/  51.23   51.74/  53.24
  contemp_faf56f6315ff0f7a   2199.97/2199.97 2199.97/2199.97   54.97/  54.97   54.97/  54.97   54.97/  54.97

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  top1_8250b21b407b14dd          6/36    44     2/30    49     0/12    50     0/12    50    29/30   364    30/30   380
  contemp_c783c2b9ca157abb       6/36    45     1/30    49     0/12    50     0/12    50    29/30   370    30/30   386
  ancestor151_it297_76966cae     6/36    45     1/30    49     0/12    50     0/12    50    29/30   370    30/30   386
  top3_1f8b67db89bc64ce          6/36    46     1/30    49     0/12    50     0/12    50    29/30   373    30/30   389
  bestever_acdc2bec37723319      6/36    46     1/30    49     0/12    50     0/12    50    29/30   385    30/30   398
  top2_7095c6da3c6fc847          3/36    47     3/30    46     1/12    48     0/12    50    28/30   361    29/30   393
  ancestor76_it135_7473bb0c0     3/36    47     1/30    49     1/12    46     0/12    50    28/30   412    29/30   455
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ancestor1_it0_0875253d162c     2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610
  contemp_888cb11115e53533       0/36    50     0/30    50     0/12    50     1/12    47     2/30  1867     0/30  2000
  contemp_faf56f6315ff0f7a       0/36    50     0/30    50     0/12    50     0/12    50     0/30  2000     0/30  2000

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.26    49.53    36.26    36.26    49.53    49.53    49.53   4.0
  top1_8250b21b407b14dd         51.29       --    51.29    51.29    51.29    51.29    51.29   0.0
  contemp_c783c2b9ca157abb      51.41       --    51.41    51.41    51.41    51.41    51.41   0.0
  ancestor151_it297_76966cae    51.41       --    51.41    51.41    51.41    51.41    51.41   0.0
  top3_1f8b67db89bc64ce         51.47       --    51.47    51.47    51.47    51.47    51.47   0.0
  bestever_acdc2bec37723319     51.78       --    51.78    51.78    51.78    51.78    51.78   0.0
  top2_7095c6da3c6fc847         49.92       --    49.92    49.92    49.92    49.92    49.92   0.0
  ancestor76_it135_7473bb0c0    50.73       --    50.73    50.73    50.73    50.73    50.73   0.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.55    49.55    49.55    49.55    49.55    49.55    49.55   1.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ancestor1_it0_0875253d162c    51.80       --    51.80    51.80    51.80    51.80    51.80   0.0
  ENUMERATE_VM_C1               51.80       --    51.80    51.80    51.80    51.80    51.80   0.0
  RANDOM_C1                     49.64       --    49.64    49.64    49.64    49.64    49.64   0.0
  contemp_888cb11115e53533      52.45       --    52.46    52.45    52.46    52.46    52.46   0.0
  contemp_faf56f6315ff0f7a      54.97       --    54.97    54.97    54.97    54.97    54.97   0.0

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
  top1_8250b21b407b14dd
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 20, 27] vs FRESH [20, 20, 27]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1560.9, 1518.2, 1357.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.03, 52.03, 49.83] vs CODE_ONLY [52.03, 52.03, 49.83]
    4_scramble_or_reset_damages            0/3  eff ACC [20.398, 20.425, 27.451] SCR [20.398, 20.425, 27.451] RESET [20.398, 20.425, 27.451]
    5_transfers_to_fresh_copy              0/3  FULL [52.03, 52.03, 49.83] vs ACC remainder [52.03, 52.03, 49.83]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.03, 52.03, 49.83]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.03, 52.03, 49.83] STORAGE_MATCHED [52.03, 52.03, 49.83] vs ACC remainder [52.03, 52.03, 49.83]
  contemp_c783c2b9ca157abb
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 20, 26] vs FRESH [20, 20, 26]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1560.9, 1524.4, 1395.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.03, 52.03, 50.18] vs CODE_ONLY [52.03, 52.03, 50.18]
    4_scramble_or_reset_damages            0/3  eff ACC [20.397, 20.424, 26.45] SCR [20.397, 20.424, 26.45] RESET [20.397, 20.424, 26.45]
    5_transfers_to_fresh_copy              0/3  FULL [52.03, 52.03, 50.18] vs ACC remainder [52.03, 52.03, 50.18]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.03, 52.03, 50.18]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.03, 52.03, 50.18] STORAGE_MATCHED [52.03, 52.03, 50.18] vs ACC remainder [52.03, 52.03, 50.18]
  ancestor151_it297_76966cae20a7e265
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 20, 26] vs FRESH [20, 20, 26]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1560.9, 1524.4, 1395.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.03, 52.03, 50.18] vs CODE_ONLY [52.03, 52.03, 50.18]
    4_scramble_or_reset_damages            0/3  eff ACC [20.397, 20.424, 26.45] SCR [20.397, 20.424, 26.45] RESET [20.397, 20.424, 26.45]
    5_transfers_to_fresh_copy              0/3  FULL [52.03, 52.03, 50.18] vs ACC remainder [52.03, 52.03, 50.18]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.03, 52.03, 50.18]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.03, 52.03, 50.18] STORAGE_MATCHED [52.03, 52.03, 50.18] vs ACC remainder [52.03, 52.03, 50.18]
  top3_1f8b67db89bc64ce
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 20, 26] vs FRESH [20, 20, 26]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1560.9, 1527.5, 1413.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.03, 52.03, 50.35] vs CODE_ONLY [52.03, 52.03, 50.35]
    4_scramble_or_reset_damages            0/3  eff ACC [20.396, 20.423, 26.449] SCR [20.396, 20.423, 26.449] RESET [20.396, 20.423, 26.449]
    5_transfers_to_fresh_copy              0/3  FULL [52.03, 52.03, 50.35] vs ACC remainder [52.03, 52.03, 50.35]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.03, 52.03, 50.35]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.03, 52.03, 50.35] STORAGE_MATCHED [52.03, 52.03, 50.35] vs ACC remainder [52.03, 52.03, 50.35]
  bestever_acdc2bec37723319
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 20, 26] vs FRESH [20, 20, 26]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1561.5, 1543.7, 1436.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.05, 52.05, 51.24] vs CODE_ONLY [52.05, 52.05, 51.24]
    4_scramble_or_reset_damages            0/3  eff ACC [20.394, 20.422, 26.447] SCR [20.394, 20.422, 26.447] RESET [20.394, 20.422, 26.447]
    5_transfers_to_fresh_copy              0/3  FULL [52.05, 52.05, 51.24] vs ACC remainder [52.05, 52.05, 51.24]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.05, 52.05, 51.24]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.05, 52.05, 51.24] STORAGE_MATCHED [52.05, 52.05, 51.24] vs ACC remainder [52.05, 52.05, 51.24]
  top2_7095c6da3c6fc847
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 21, 23] vs FRESH [20, 21, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1501.7, 1502.5, 1472.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.89, 51.29, 48.57] vs CODE_ONLY [49.89, 51.29, 48.57]
    4_scramble_or_reset_damages            0/3  eff ACC [20.397, 21.424, 23.45] SCR [20.397, 21.424, 23.45] RESET [20.397, 21.424, 23.45]
    5_transfers_to_fresh_copy              0/3  FULL [49.89, 51.29, 48.57] vs ACC remainder [49.89, 51.29, 48.57]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.89, 51.29, 48.57]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.89, 51.29, 48.57] STORAGE_MATCHED [49.89, 51.29, 48.57] vs ACC remainder [49.89, 51.29, 48.57]
  ancestor76_it135_7473bb0c0eb51c45
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 21, 22] vs FRESH [19, 21, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1526.4, 1476.3, 1516.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.06, 49.57, 50.55] vs CODE_ONLY [52.06, 49.57, 50.55]
    4_scramble_or_reset_damages            0/3  eff ACC [19.382, 21.419, 22.441] SCR [19.382, 21.419, 22.441] RESET [19.382, 21.419, 22.441]
    5_transfers_to_fresh_copy              0/3  FULL [52.06, 49.57, 50.55] vs ACC remainder [52.06, 49.57, 50.55]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.06, 49.57, 50.55]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.06, 49.57, 50.55] STORAGE_MATCHED [52.06, 49.57, 50.55] vs ACC remainder [52.06, 49.57, 50.55]
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
  RANDOM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 6, 9] vs FRESH [6, 6, 9]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1493.8, 1515.0, 1489.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.32, 50.5, 49.1] vs CODE_ONLY [49.32, 50.5, 49.1]
    4_scramble_or_reset_damages            0/3  eff ACC [6.205, 6.235, 9.221] SCR [6.205, 6.235, 9.221] RESET [6.205, 6.235, 9.221]
    5_transfers_to_fresh_copy              0/3  FULL [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.32, 50.5, 49.1]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.32, 50.5, 49.1] STORAGE_MATCHED [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
  contemp_888cb11115e53533
    0_competence_kept_ACC_ge_FRESH         1/3  successes ACC [1, 1, 1] vs FRESH [3, 2, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [-23.1, -43.4, 6.6] vs 5% of FRESH cost [1536.8, 1547.3, 1597.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.31, 53.02, 53.02] vs CODE_ONLY [51.33, 53.03, 53.03]
    4_scramble_or_reset_damages            0/3  eff ACC [1.144, 1.161, 1.161] SCR [1.144, 1.161, 1.161] RESET [0.144, 1.161, 1.161]
    5_transfers_to_fresh_copy              0/3  FULL [51.31, 53.02, 53.02] vs ACC remainder [51.31, 53.02, 53.02]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.31, 53.02, 53.02]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.33, 53.03, 53.03] STORAGE_MATCHED [51.33, 53.03, 53.03] vs ACC remainder [51.31, 53.02, 53.02]
  contemp_faf56f6315ff0f7a
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1649.1, 1649.1, 1649.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [54.97, 54.97, 54.97] vs CODE_ONLY [54.97, 54.97, 54.97]
    4_scramble_or_reset_damages            0/3  eff ACC [0.129, 0.129, 0.129] SCR [0.129, 0.129, 0.129] RESET [0.129, 0.129, 0.129]
    5_transfers_to_fresh_copy              0/3  FULL [54.97, 54.97, 54.97] vs ACC remainder [54.97, 54.97, 54.97]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [54.97, 54.97, 54.97]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [54.97, 54.97, 54.97] STORAGE_MATCHED [54.97, 54.97, 54.97] vs ACC remainder [54.97, 54.97, 54.97]

MACHINERY OF top1_8250b21b407b14dd (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   0     0
    task  9:     0    0    0    0    0 |   0     0
    task 19:     0    0    0    0    0 |   0     0
    task 31:     0    0    0    0    0 |   0     0
    task 41:     0    0    0    0    0 |   0     0
    task 49:     0    0    0    0    0 |   0     0
  artifact events: 0 (create 0, delete 0, patch/append 0); invocations by block: {}; edges: 0
  adaptation curve ACC:   124 2005 43 759 11 86 33 1375 79 135 198 269 759 759 8 1141 1141 5 2005 45 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
  adaptation curve FRESH: 124 2005 43 759 11 86 33 1375 79 135 198 269 759 759 8 1141 1141 5 2005 45 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
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

