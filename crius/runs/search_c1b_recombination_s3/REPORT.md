CRIUS CAMPAIGN 0 REPORT  run=search_c1b_recombination_s3  arm=recombination
code_commit=6364d6994 dirty=True config_hash=bbf684cd638167f2 world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  26.4739   25.6015        10.2374        42          7
    26  20.3943   20.3943        12.2427        45         54
    51  18.4442   18.4438         9.2123        51         89
    76  10.2992   10.2987         8.3969        50        123
   101  27.3959   27.3959        15.1692        58        166
   126  16.3620   14.6080         9.9564        55        205
   151  24.4653   24.4653        19.7312        59        242
   176  13.3397   13.3397         9.7831        58        284
   201  33.4849   33.4849        28.2645        63        323
   226  22.3917   22.3917        15.1034        63        363
   251  19.3957   18.5201        11.9719        57        398
   276  17.3969   17.3969        12.4928        57        440
   300   7.2127    6.3695         4.9686        62        467
  candidates evaluated: 7208   best_ever 34.4820 (de4511a66946a04a)  wall 467s

BEST PROGRAM de4511a66946a04a (len 64, iteration 263, modification duplicate@2+1->9+swap@16,27+delete@34+splice@28<-donor[23:24]:135006c05e270e74)
  search seed 301263: fit 34.4820 succ 34/50 inter 2114 steps 9436 ws_cost 500 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [21.504, 1.0], "B": [91.0, 1.0], "C": [28.727, 0.667], "D": [37.318, 0.5], "E": [46.302, 0.125]}
  listing:
      0  INPUT          R1, num_ops
      1  CONST          R5, 1
      2  CONST          R2, -7
      3  ADD            R0, R4, R5
      4  BRNZ           R3, 49
      5  BRZ            R0, 35
      6  WS_REC_NEW     R0
      7  MOD            R3, R5, R1
      8  ADD            R0, R1, R5
      9  CONST          R2, -7
     10  WS_READ        R6, R3
     11  BLK_STATE_GET  R4, R6, R4
     12  MOD            R3, R4, R1
     13  WS_REC_NEW     R0
     14  BLK_COUNT      R6
     15  MOD            R3, R4, R1
     16  BLK_COUNT      R6
     17  ACT            R0
     18  BRZ            R3, 51
     19  JMP            24
     20  BLK_COUNT      R5
     21  ADD            R0, R0, R1
     22  WS_REC_GET     R1, R1, R4
     23  CONST          R2, -10
     24  MOD            R3, R5, R1
     25  ADD            R0, R1, R5
     26  WS_READ        R6, R3
     27  WS_REC_NEW     R0
     28  ADD            R0, R1, R5
     29  MOD            R3, R4, R1
     30  JMP            39
     31  ACT            R0
     32  ACT            R7
     33  VGET           R1, R1, R2
     34  ACT            R5
     35  ADD            R2, R7, R6
     36  BRNZ           R0, 26
     37  BRZ            R3, 23
     38  LT             R3, R0, R2
     39  WS_READ        R6, R3
     40  MOD            R3, R4, R0
     41  BLK_STATE_GET  R7, R1, R1
     42  CONST          R1, 16
     43  BLK_REC_BEGIN  
     44  ACT            R0
     45  ACT            R3
     46  BRZ            R3, 46
     47  CONST          R5, 0
     48  BRNZ           R2, 26
     49  WS_LINKS       R0, R7
     50  MOD            R3, R0, R1
     51  ACT            R1
     52  MOD            R3, R0, R1
     53  DIV            R4, R0, R1
     54  ACT            R3
     55  MOD            R3, R4, R1
     56  ADD            R0, R0, R5
     57  ACT            R3
     58  JMP            51
     59  BLK_REC_BEGIN  
     60  JMP            40
     61  BLK_APPEND     R0, R1
     62  MOD            R4, R7, R7
     63  SUB            R0, R2, R3
  ancestry (143 steps, newest first): iteration/fitness/modification
    it  263  34.4820  len 64  duplicate@2+1->9+swap@16,27+delete@34+splice@28<-donor[23:24]:135006c05e270e74
    it  262  17.3589  len 63  arg@47.0
    it  261  12.3431  len 63  delete@28
    it  259  11.2787  len 64  swap@6,28+arg@31.0
    it  258  20.3982  len 64  const@46+splice@41<-donor[26:27]:0abdc00f2d3e951e
    it  255  13.3299  len 63  insert@17+arg@32.0+swap@5,4+splice@13<-donor[22:26]:40e79fb8b1c9e86f
    it  254  21.4710  len 58  replace@29+arg@15.0+replace@10
    it  253  28.4783  len 58  swap@13,39+splice@24<-donor[53:54]:a4f3abd77547a76b
    it  251  19.3957  len 57  duplicate@12+6->7+delete@34
    it  249  11.2995  len 52  delete@53+delete@37
    it  246  17.3704  len 54  const@2+delete@14
    it  245  9.2721  len 55  insert@29
    it  244  10.3103  len 54  arg@36.0+swap@26,9
    it  243  18.3566  len 54  swap@6,10
    it  242  16.3802  len 54  delete@21
    ... 129 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7316.0    4.3   74.7
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.3    2.7    1.7
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ancestor1_it0_0875253d162c  19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       0.0    0.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       0.0    0.0    0.0
  contemp_7f9797e5cf8a95bd    16.037  16.037  16.037  16.037  15.7  15.7    15378    15374      -4.9    0.0    0.0
  ancestor86_it166_6e69bae95  16.037  16.037  16.037  16.037  15.7  15.7    15386    15386       0.0    0.0    0.0
  bestever_de4511a66946a04a   16.034  16.037  16.034  16.034  15.7  15.7    15623    15369    -264.9    0.0    0.0
  top2_c2808507d1d8d858       15.366  16.037  16.366  15.366  15.0  15.7    15837    15368    -487.4    0.0    0.0
  top3_57510d741aef0f0d       15.366  16.037  16.366  15.366  15.0  15.7    15837    15368    -487.4    0.0    0.0
  contemp_c3b5dd55914602a9    15.366  16.037  16.366  15.366  15.0  15.7    15837    15368    -487.4    0.0    0.0
  contemp_bf565069febe94c7    15.366  16.037  16.366  15.366  15.0  15.7    15837    15368    -487.4    0.0    0.0
  ancestor171_it299_f90a1a34  15.366  16.037  16.366  15.366  15.0  15.7    15837    15368    -487.4    0.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0
  top1_05932a87aec14f1b        6.865   9.243   7.532   6.865   6.7   9.0    35637    30344   -5523.9    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.00/ 455.13   14.90/ 539.10   21.11/  47.94   33.21/  48.94   40.07/  50.52
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.13/ 443.81  528.11/ 527.79   47.93/  47.89   48.85/  48.88   50.42/  50.46
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ancestor1_it0_0875253d162c  494.04/ 494.04  523.26/ 523.26   49.99/  49.99   50.96/  50.96   52.68/  52.68
  ENUMERATE_VM_C1             494.04/ 494.04  523.26/ 523.26   49.99/  49.99   50.96/  50.96   52.68/  52.68
  contemp_7f9797e5cf8a95bd    692.78/ 680.30  757.61/ 770.99   48.19/  48.25   50.53/  50.53   52.23/  50.41
  ancestor86_it166_6e69bae95  700.50/ 700.50  749.24/ 749.24   49.57/  49.57   50.07/  50.07   51.76/  51.76
  bestever_de4511a66946a04a   695.34/ 699.86  781.02/ 748.68   48.59/  49.59   50.93/  50.14   50.72/  51.86
  top2_c2808507d1d8d858       707.47/ 700.81  789.00/ 747.34   50.03/  50.03   50.52/  49.90   51.44/  51.70
  top3_57510d741aef0f0d       707.48/ 700.82  789.01/ 747.35   50.04/  50.04   50.53/  49.91   51.45/  51.71
  contemp_c3b5dd55914602a9    707.48/ 700.82  789.01/ 747.35   50.04/  50.04   50.53/  49.91   51.45/  51.71
  contemp_bf565069febe94c7    707.48/ 700.82  789.01/ 747.35   50.04/  50.04   50.53/  49.91   51.45/  51.71
  ancestor171_it299_f90a1a34  707.48/ 700.82  789.01/ 747.35   50.04/  50.04   50.53/  49.91   51.45/  51.71
  RANDOM_C1                  1661.96/1661.96 1626.54/1626.54   50.44/  50.44   50.50/  50.50   48.40/  48.40
  top1_05932a87aec14f1b      1807.23/1499.32 1748.55/1502.24   51.57/  51.83   47.90/  50.15   52.23/  51.31

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ancestor1_it0_0875253d162c     2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  contemp_7f9797e5cf8a95bd       5/36    46     1/30    48     0/12    50     0/12    50    21/30   666    20/30   728
  ancestor86_it166_6e69bae95     3/36    48     2/30    48     1/12    49     0/12    50    21/30   673    20/30   720
  bestever_de4511a66946a04a      4/36    46     1/30    49     1/12    47     0/12    50    21/30   668    20/30   751
  top2_c2808507d1d8d858          2/36    48     1/30    48     0/12    50     1/12    48    21/30   680    20/30   758
  top3_57510d741aef0f0d          2/36    48     1/30    48     0/12    50     1/12    48    21/30   680    20/30   758
  contemp_c3b5dd55914602a9       2/36    48     1/30    48     0/12    50     1/12    48    21/30   680    20/30   758
  contemp_bf565069febe94c7       2/36    48     1/30    48     0/12    50     1/12    48    21/30   680    20/30   758
  ancestor171_it299_f90a1a34     2/36    48     1/30    48     0/12    50     1/12    48    21/30   680    20/30   758
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610
  top1_05932a87aec14f1b          1/36    49     3/30    46     0/12    50     0/12    50     8/30  1738     8/30  1681

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.26    49.53    36.26    36.26    49.53    49.53    49.53   4.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.55    49.55    49.55    49.55    49.55    49.55    49.55   1.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ancestor1_it0_0875253d162c    51.73       --    51.73    51.73    51.73    51.73    51.73   0.0
  ENUMERATE_VM_C1               51.73       --    51.73    51.73    51.73    51.73    51.73   0.0
  contemp_7f9797e5cf8a95bd      51.29       --    51.17    51.29    51.17    51.17    51.17   0.0
  ancestor86_it166_6e69bae95    50.82       --    50.82    50.82    50.82    50.82    50.82   0.0
  bestever_de4511a66946a04a     50.84       --    51.08    50.84    51.08    51.08    51.08   0.0
  top2_c2808507d1d8d858         50.93       --    50.47    50.93    50.47    50.47    50.47   0.0
  top3_57510d741aef0f0d         50.94       --    50.48    50.94    50.48    50.48    50.48   0.0
  contemp_c3b5dd55914602a9      50.94       --    50.48    50.94    50.48    50.48    50.48   0.0
  contemp_bf565069febe94c7      50.94       --    50.48    50.94    50.48    50.48    50.48   0.0
  ancestor171_it299_f90a1a34    50.94       --    50.48    50.94    50.48    50.48    50.48   0.0
  RANDOM_C1                     49.57       --    49.57    49.57    49.57    49.57    49.57   0.0
  top1_05932a87aec14f1b         49.82       --    49.39    49.82    49.39    49.39    49.39   0.0

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
  contemp_7f9797e5cf8a95bd
    0_competence_kept_ACC_ge_FRESH         1/3  successes ACC [12, 12, 23] vs FRESH [14, 13, 20]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [-66.5, -45.7, 70.7] vs 5% of FRESH cost [1500.4, 1478.6, 1483.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.23, 52.23, 49.4] vs CODE_ONLY [52.23, 51.88, 49.4]
    4_scramble_or_reset_damages            0/3  eff ACC [12.347, 12.327, 23.435] SCR [12.347, 12.327, 23.435] RESET [14.347, 13.328, 20.435]
    5_transfers_to_fresh_copy              0/3  FULL [52.23, 52.23, 49.4] vs ACC remainder [52.23, 52.23, 49.4]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.23, 52.23, 49.4]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.23, 51.88, 49.4] STORAGE_MATCHED [52.23, 51.88, 49.4] vs ACC remainder [52.23, 52.23, 49.4]
  ancestor86_it166_6e69bae95d6aadb2
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [13, 13, 21] vs FRESH [13, 13, 21]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1561.2, 1506.2, 1461.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.11, 51.65, 48.7] vs CODE_ONLY [52.11, 51.65, 48.7]
    4_scramble_or_reset_damages            0/3  eff ACC [13.348, 13.327, 21.435] SCR [13.348, 13.327, 21.435] RESET [13.348, 13.327, 21.435]
    5_transfers_to_fresh_copy              0/3  FULL [52.11, 51.65, 48.7] vs ACC remainder [52.11, 51.65, 48.7]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.11, 51.65, 48.7]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.11, 51.65, 48.7] STORAGE_MATCHED [52.11, 51.65, 48.7] vs ACC remainder [52.11, 51.65, 48.7]
  bestever_de4511a66946a04a
    0_competence_kept_ACC_ge_FRESH         2/3  successes ACC [12, 13, 22] vs FRESH [13, 13, 21]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [-4.0, 14.7, 29.2] vs 5% of FRESH cost [1564.4, 1507.2, 1462.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.28, 50.2, 50.03] vs CODE_ONLY [52.27, 52.27, 48.69]
    4_scramble_or_reset_damages            0/3  eff ACC [12.342, 13.33, 22.431] SCR [12.342, 13.33, 22.431] RESET [13.342, 13.33, 21.431]
    5_transfers_to_fresh_copy              0/3  FULL [52.28, 50.2, 50.03] vs ACC remainder [52.28, 50.2, 50.03]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.28, 50.2, 50.03]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.27, 52.27, 48.69] STORAGE_MATCHED [52.27, 52.27, 48.69] vs ACC remainder [52.28, 50.2, 50.03]
  top2_c2808507d1d8d858
    0_competence_kept_ACC_ge_FRESH         1/3  successes ACC [13, 12, 20] vs FRESH [13, 13, 21]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [12.5, -6.2, -18.7] vs 5% of FRESH cost [1560.4, 1526.1, 1452.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.18, 52.22, 49.39] vs CODE_ONLY [52.22, 52.22, 46.97]
    4_scramble_or_reset_damages            0/3  eff ACC [13.338, 12.328, 20.432] SCR [13.338, 12.328, 20.432] RESET [13.338, 13.328, 22.432]
    5_transfers_to_fresh_copy              0/3  FULL [51.18, 52.22, 49.39] vs ACC remainder [51.18, 52.22, 49.39]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.18, 52.22, 49.39]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.22, 52.22, 46.97] STORAGE_MATCHED [52.22, 52.22, 46.97] vs ACC remainder [51.18, 52.22, 49.39]
  top3_57510d741aef0f0d
    0_competence_kept_ACC_ge_FRESH         1/3  successes ACC [13, 12, 20] vs FRESH [13, 13, 21]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [12.5, -6.2, -18.7] vs 5% of FRESH cost [1560.7, 1526.4, 1452.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.19, 52.23, 49.4] vs CODE_ONLY [52.23, 52.23, 46.98]
    4_scramble_or_reset_damages            0/3  eff ACC [13.338, 12.328, 20.432] SCR [13.338, 12.328, 20.432] RESET [13.338, 13.328, 22.432]
    5_transfers_to_fresh_copy              0/3  FULL [51.19, 52.23, 49.4] vs ACC remainder [51.19, 52.23, 49.4]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.19, 52.23, 49.4]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.23, 52.23, 46.98] STORAGE_MATCHED [52.23, 52.23, 46.98] vs ACC remainder [51.19, 52.23, 49.4]
  contemp_c3b5dd55914602a9
    0_competence_kept_ACC_ge_FRESH         1/3  successes ACC [13, 12, 20] vs FRESH [13, 13, 21]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [12.5, -6.2, -18.7] vs 5% of FRESH cost [1560.7, 1526.4, 1452.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.19, 52.23, 49.4] vs CODE_ONLY [52.23, 52.23, 46.98]
    4_scramble_or_reset_damages            0/3  eff ACC [13.338, 12.328, 20.432] SCR [13.338, 12.328, 20.432] RESET [13.338, 13.328, 22.432]
    5_transfers_to_fresh_copy              0/3  FULL [51.19, 52.23, 49.4] vs ACC remainder [51.19, 52.23, 49.4]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.19, 52.23, 49.4]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.23, 52.23, 46.98] STORAGE_MATCHED [52.23, 52.23, 46.98] vs ACC remainder [51.19, 52.23, 49.4]
  contemp_bf565069febe94c7
    0_competence_kept_ACC_ge_FRESH         1/3  successes ACC [13, 12, 20] vs FRESH [13, 13, 21]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [12.5, -6.2, -18.7] vs 5% of FRESH cost [1560.7, 1526.4, 1452.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.19, 52.23, 49.4] vs CODE_ONLY [52.23, 52.23, 46.98]
    4_scramble_or_reset_damages            0/3  eff ACC [13.338, 12.328, 20.432] SCR [13.338, 12.328, 20.432] RESET [13.338, 13.328, 22.432]
    5_transfers_to_fresh_copy              0/3  FULL [51.19, 52.23, 49.4] vs ACC remainder [51.19, 52.23, 49.4]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.19, 52.23, 49.4]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.23, 52.23, 46.98] STORAGE_MATCHED [52.23, 52.23, 46.98] vs ACC remainder [51.19, 52.23, 49.4]
  ancestor171_it299_f90a1a3489b0ba84
    0_competence_kept_ACC_ge_FRESH         1/3  successes ACC [13, 12, 20] vs FRESH [13, 13, 21]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [12.5, -6.2, -18.7] vs 5% of FRESH cost [1560.7, 1526.4, 1452.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.19, 52.23, 49.4] vs CODE_ONLY [52.23, 52.23, 46.98]
    4_scramble_or_reset_damages            0/3  eff ACC [13.338, 12.328, 20.432] SCR [13.338, 12.328, 20.432] RESET [13.338, 13.328, 22.432]
    5_transfers_to_fresh_copy              0/3  FULL [51.19, 52.23, 49.4] vs ACC remainder [51.19, 52.23, 49.4]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.19, 52.23, 49.4]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.23, 52.23, 46.98] STORAGE_MATCHED [52.23, 52.23, 46.98] vs ACC remainder [51.19, 52.23, 49.4]
  RANDOM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 6, 9] vs FRESH [6, 6, 9]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1491.8, 1515.0, 1485.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.21, 50.5, 48.99] vs CODE_ONLY [49.21, 50.5, 48.99]
    4_scramble_or_reset_damages            0/3  eff ACC [6.205, 6.235, 9.221] SCR [6.205, 6.235, 9.221] RESET [6.205, 6.235, 9.221]
    5_transfers_to_fresh_copy              0/3  FULL [49.21, 50.5, 48.99] vs ACC remainder [49.21, 50.5, 48.99]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.21, 50.5, 48.99]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.21, 50.5, 48.99] STORAGE_MATCHED [49.21, 50.5, 48.99] vs ACC remainder [49.21, 50.5, 48.99]
  top1_05932a87aec14f1b
    0_competence_kept_ACC_ge_FRESH         0/3  successes ACC [8, 5, 7] vs FRESH [11, 6, 10]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [-12.0, 44.1, 22.6] vs 5% of FRESH cost [1554.9, 1542.5, 1504.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.23, 49.75, 47.5] vs CODE_ONLY [52.18, 49.76, 46.24]
    4_scramble_or_reset_damages            0/3  eff ACC [8.219, 5.185, 7.192] SCR [8.219, 5.185, 7.192] RESET [8.219, 4.184, 10.192]
    5_transfers_to_fresh_copy              0/3  FULL [52.23, 49.75, 47.5] vs ACC remainder [52.23, 49.75, 47.5]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.23, 49.75, 47.5]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.18, 49.76, 46.24] STORAGE_MATCHED [52.18, 49.76, 46.24] vs ACC remainder [52.23, 49.75, 47.5]

MACHINERY OF top1_05932a87aec14f1b (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    3    0 |   0     0
    task  9:     0    0    0   30    0 |   0     0
    task 19:     0    0    0   60    0 |   0     0
    task 31:     0    0    0   96    0 |   0     0
    task 41:     0    0    0  126    0 |   0     0
    task 49:     0    0    0  150    0 |   0     0
  artifact events: 0 (create 0, delete 0, patch/append 0); invocations by block: {}; edges: 0
  adaptation curve ACC:   33 2080 2080 1718 2080 2080 2080 2080 133 2079 2080 2080 2080 1138 2080 2080 840 2080 1175 873 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
  adaptation curve FRESH: 33 2080 2080 1746 33 33 1177 2080 2080 47 2080 2080 1746 517 33 2080 1634 2080 2080 11 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
  reuse_gain per task:    0 -0 -0 28 -2047 -2047 -903 -0 1946 -2033 -0 -0 -334 -621 -2047 -0 794 -0 904 -862 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0 -0

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

