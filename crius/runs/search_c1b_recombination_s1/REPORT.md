CRIUS CAMPAIGN 0 REPORT  run=search_c1b_recombination_s1  arm=recombination
code_commit=6364d6994 dirty=True config_hash=bbf684cd638167f2 world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  23.4181   17.6121         7.5950        45          9
    26  21.4300   21.4299         8.4462        62         54
    51  21.4413   21.4407        12.8957        62        110
    76  21.3907   19.6795        14.0943        61        153
   101  21.3659   21.3659        13.7687        62        202
   126  24.4683   24.2171        17.3681        63        246
   151  23.4511   23.4170        17.3509        64        289
   176  24.4154   24.2954        14.8522        62        335
   201  23.4578   23.4517        19.1853        64        380
   226  19.3670   16.3654        10.3599        64        433
   251  23.4320   21.8003        14.9879        61        472
   276  24.3996   24.0200        15.4982        64        517
   300  17.3805   17.3706        10.2569        61        554
  candidates evaluated: 7208   best_ever 32.4763 (fc6c2deeb91c5dde)  wall 554s

BEST PROGRAM fc6c2deeb91c5dde (len 55, iteration 36, modification duplicate@11+1->36+arg@13.1+arg@19.0)
  search seed 101036: fit 22.4461 succ 22/50 inter 6323 steps 30113 ws_cost 50 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [241.992, 1.0], "B": [269.639, 1.0], "C": [52.71, 0.0], "D": [48.852, 0.1], "E": [48.41, 0.125]}
  listing:
      0  INPUT          R1, num_ops
      1  WS_READ        R7, R6
      2  CONST          R5, 1
      3  DIV            R4, R0, R1
      4  DIV            R4, R0, R1
      5  MOD            R3, R4, R1
      6  ACT            R3
      7  ADD            R0, R0, R5
      8  JMP            21
      9  MOD            R3, R4, R1
     10  ACT            R3
     11  ADD            R0, R0, R5
     12  JMP            20
     13  DIV            R6, R6, R1
     14  ACT            R3
     15  CONST          R0, 0
     16  ACT            R3
     17  LT             R3, R0, R2
     18  BRZ            R3, 22
     19  ACT            R2
     20  ACT            R0
     21  ADD            R0, R0, R5
     22  CONST          R0, 1
     23  MUL            R2, R1, R1
     24  LT             R3, R0, R2
     25  BRZ            R3, 38
     26  ACT            R1
     27  MOD            R3, R0, R1
     28  MOV            R2, R1
     29  ADD            R0, R0, R5
     30  JMP            35
     31  HALT           
     32  MOD            R3, R4, R1
     33  ADD            R0, R0, R5
     34  ACT            R3
     35  ADD            R0, R0, R5
     36  ADD            R0, R0, R5
     37  JMP            24
     38  DIV            R6, R5, R1
     39  MUL            R2, R1, R1
     40  MUL            R2, R2, R1
     41  LT             R3, R0, R2
     42  BRZ            R3, 54
     43  ACT            R1
     44  MOD            R3, R0, R1
     45  ACT            R3
     46  DIV            R4, R0, R1
     47  MOD            R3, R4, R1
     48  ACT            R3
     49  DIV            R4, R4, R1
     50  MOD            R3, R4, R1
     51  ACT            R3
     52  ADD            R0, R0, R5
     53  JMP            41
     54  HALT           
  ancestry (13 steps, newest first): iteration/fitness/modification
    it   36  22.4461  len 55  duplicate@11+1->36+arg@13.1+arg@19.0
    it   35  22.3909  len 54  duplicate@31+3->6+const@15+arg@1.0
    it   33  18.3439  len 51  const@8+duplicate@27+4->7
    it   30  20.4319  len 47  const@15
    it   27  26.4706  len 47  delete@22
    it   26  21.4299  len 48  arg@16.1+splice@27<-donor[13:14]:e3db4c3bfe8e4f52
    it   19  23.4651  len 47  replace@30
    it   16  16.3389  len 47  replace@30
    it   13  20.4251  len 47  delete@44+splice@23<-donor[41:44]:04f7f43282591ca3
    it   12  22.4072  len 45  insert@42+const@25+splice@4<-donor[36:38]:03a35b406430e700
    it   10  21.4336  len 42  swap@7,19
    it    7  20.3811  len 42  duplicate@29+3->2+insert@1+const@13
    it    6  20.4064  len 38  delete@9
    it    0  25.4606  len 39  seed:ENUMERATE_VM

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7316.0    4.3   74.7
  top1_a6d81c1c5184b346       21.409  21.409  21.409  21.409  21.0  21.0    10630    10630       0.0    0.0    0.0
  ancestor95_it154_a34c71100  21.103  21.103  21.103  21.103  20.7  20.7     7446     7446       0.0    0.0    0.0
  bestever_fc6c2deeb91c5dde   20.748  20.748  20.748  20.748  20.3  20.3    10084    10084       0.0    0.0    0.0
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.3    2.7    1.7
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ancestor1_it0_0875253d162c  19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       0.0    0.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       0.0    0.0    0.0
  top2_71f48a72b0813edc       18.733  18.733  18.733  18.733  18.3  18.3    11724    11724       0.0    0.0    0.0
  top3_1f735cb37c59019e       18.733  18.733  18.733  18.733  18.3  18.3    11724    11724       0.0    0.0    0.0
  contemp_1d9fe66b86095f69    18.733  18.733  18.733  18.733  18.3  18.3    11724    11724       0.0    0.0    0.0
  contemp_8a3624109261aae4    18.733  18.733  18.733  18.733  18.3  18.3    11724    11724       0.0    0.0    0.0
  ancestor189_it299_29540b8b  18.733  18.733  18.733  18.733  18.3  18.3    11724    11724       0.0    0.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0
  contemp_325b83f87533782c     5.534   5.534   5.534   5.534   5.3   5.3    34125    34125       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.00/ 455.13   14.90/ 539.10   21.11/  47.94   33.21/  48.94   40.07/  50.52
  top1_a6d81c1c5184b346       533.16/ 533.16  435.14/ 435.14   50.97/  50.97   52.25/  52.25   53.31/  53.31
  ancestor95_it154_a34c71100  386.36/ 386.36  242.27/ 242.27   50.76/  50.76   50.16/  50.16   52.56/  52.56
  bestever_fc6c2deeb91c5dde   450.24/ 450.24  454.13/ 454.13   49.38/  49.38   49.93/  49.93   51.58/  51.58
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.13/ 443.81  528.11/ 527.79   47.93/  47.89   48.85/  48.88   50.42/  50.46
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ancestor1_it0_0875253d162c  494.04/ 494.04  523.26/ 523.26   49.99/  49.99   50.96/  50.96   52.68/  52.68
  ENUMERATE_VM_C1             494.04/ 494.04  523.26/ 523.26   49.99/  49.99   50.96/  50.96   52.68/  52.68
  top2_71f48a72b0813edc       550.98/ 550.98  528.13/ 528.13   50.82/  50.82   52.09/  52.09   53.15/  53.15
  top3_1f735cb37c59019e       550.98/ 550.98  528.13/ 528.13   50.82/  50.82   52.09/  52.09   53.15/  53.15
  contemp_1d9fe66b86095f69    550.98/ 550.98  528.13/ 528.13   50.82/  50.82   52.09/  52.09   53.15/  53.15
  contemp_8a3624109261aae4    550.98/ 550.98  528.13/ 528.13   50.82/  50.82   52.09/  52.09   53.15/  53.15
  ancestor189_it299_29540b8b  550.98/ 550.98  528.13/ 528.13   50.82/  50.82   52.09/  52.09   53.15/  53.15
  RANDOM_C1                  1661.96/1661.96 1626.54/1626.54   50.44/  50.44   50.50/  50.50   48.40/  48.40
  contemp_325b83f87533782c   1873.37/1873.37 1657.38/1657.38   51.41/  51.41   51.23/  51.23   52.07/  52.07

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  top1_a6d81c1c5184b346          3/36    47     2/30    48     1/12    48     0/12    50    28/30   506    29/30   413
  ancestor95_it154_a34c71100     2/36    48     2/30    48     0/12    50     0/12    50    28/30   368    30/30   231
  bestever_fc6c2deeb91c5dde      3/36    47     2/30    47     1/12    48     0/12    50    27/30   431    28/30   435
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ancestor1_it0_0875253d162c     2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  top2_71f48a72b0813edc          3/36    47     2/30    48     1/12    48     0/12    50    24/30   525    25/30   503
  top3_1f735cb37c59019e          3/36    47     2/30    48     1/12    48     0/12    50    24/30   525    25/30   503
  contemp_1d9fe66b86095f69       3/36    47     2/30    48     1/12    48     0/12    50    24/30   525    25/30   503
  contemp_8a3624109261aae4       3/36    47     2/30    48     1/12    48     0/12    50    24/30   525    25/30   503
  ancestor189_it299_29540b8b     3/36    47     2/30    48     1/12    48     0/12    50    24/30   525    25/30   503
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610
  contemp_325b83f87533782c       2/36    48     2/30    47     1/12    46     0/12    50     4/30  1735     7/30  1535

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.26    49.53    36.26    36.26    49.53    49.53    49.53   4.0
  top1_a6d81c1c5184b346         52.72       --    52.72    52.72    52.72    52.72    52.72   0.0
  ancestor95_it154_a34c71100    51.22       --    51.22    51.22    51.22    51.22    51.22   0.0
  bestever_fc6c2deeb91c5dde     50.66       --    50.66    50.66    50.66    50.66    50.66   0.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.55    49.55    49.55    49.55    49.55    49.55    49.55   1.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ancestor1_it0_0875253d162c    51.73       --    51.73    51.73    51.73    51.73    51.73   0.0
  ENUMERATE_VM_C1               51.73       --    51.73    51.73    51.73    51.73    51.73   0.0
  top2_71f48a72b0813edc         52.56       --    52.56    52.56    52.56    52.56    52.56   0.0
  top3_1f735cb37c59019e         52.56       --    52.56    52.56    52.56    52.56    52.56   0.0
  contemp_1d9fe66b86095f69      52.56       --    52.56    52.56    52.56    52.56    52.56   0.0
  contemp_8a3624109261aae4      52.56       --    52.56    52.56    52.56    52.56    52.56   0.0
  ancestor189_it299_29540b8b    52.56       --    52.56    52.56    52.56    52.56    52.56   0.0
  RANDOM_C1                     49.57       --    49.57    49.57    49.57    49.57    49.57   0.0
  contemp_325b83f87533782c      51.60       --    51.60    51.60    51.60    51.60    51.60   0.0

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
  top1_a6d81c1c5184b346
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 21, 22] vs FRESH [20, 21, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1600.9, 1604.2, 1476.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [54.12, 53.04, 51.0] vs CODE_ONLY [54.12, 53.04, 51.0]
    4_scramble_or_reset_damages            0/3  eff ACC [20.382, 21.435, 22.409] SCR [20.382, 21.435, 22.409] RESET [20.382, 21.435, 22.409]
    5_transfers_to_fresh_copy              0/3  FULL [54.12, 53.04, 51.0] vs ACC remainder [54.12, 53.04, 51.0]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [54.12, 53.04, 51.0]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [54.12, 53.04, 51.0] STORAGE_MATCHED [54.12, 53.04, 51.0] vs ACC remainder [54.12, 53.04, 51.0]
  ancestor95_it154_a34c7110042ee4b2
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 21, 22] vs FRESH [19, 21, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1576.8, 1535.0, 1481.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.56, 52.56, 48.55] vs CODE_ONLY [52.56, 52.56, 48.55]
    4_scramble_or_reset_damages            0/3  eff ACC [19.443, 21.433, 22.433] SCR [19.443, 21.433, 22.433] RESET [19.443, 21.433, 22.433]
    5_transfers_to_fresh_copy              0/3  FULL [52.56, 52.56, 48.55] vs ACC remainder [52.56, 52.56, 48.55]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.56, 52.56, 48.55]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.56, 52.56, 48.55] STORAGE_MATCHED [52.56, 52.56, 48.55] vs ACC remainder [52.56, 52.56, 48.55]
  bestever_fc6c2deeb91c5dde
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 19, 23] vs FRESH [19, 19, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1549.0, 1504.1, 1460.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.71, 51.2, 48.08] vs CODE_ONLY [52.71, 51.2, 48.08]
    4_scramble_or_reset_damages            0/3  eff ACC [19.377, 19.418, 23.448] SCR [19.377, 19.418, 23.448] RESET [19.377, 19.418, 23.448]
    5_transfers_to_fresh_copy              0/3  FULL [52.71, 51.2, 48.08] vs ACC remainder [52.71, 51.2, 48.08]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.71, 51.2, 48.08]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.71, 51.2, 48.08] STORAGE_MATCHED [52.71, 51.2, 48.08] vs ACC remainder [52.71, 51.2, 48.08]
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
  top2_71f48a72b0813edc
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [13, 20, 22] vs FRESH [13, 20, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1596.2, 1599.4, 1472.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [53.96, 52.88, 50.85] vs CODE_ONLY [53.96, 52.88, 50.85]
    4_scramble_or_reset_damages            0/3  eff ACC [13.333, 20.44, 22.426] SCR [13.333, 20.44, 22.426] RESET [13.333, 20.44, 22.426]
    5_transfers_to_fresh_copy              0/3  FULL [53.96, 52.88, 50.85] vs ACC remainder [53.96, 52.88, 50.85]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [53.96, 52.88, 50.85]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [53.96, 52.88, 50.85] STORAGE_MATCHED [53.96, 52.88, 50.85] vs ACC remainder [53.96, 52.88, 50.85]
  top3_1f735cb37c59019e
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [13, 20, 22] vs FRESH [13, 20, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1596.2, 1599.4, 1472.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [53.96, 52.88, 50.85] vs CODE_ONLY [53.96, 52.88, 50.85]
    4_scramble_or_reset_damages            0/3  eff ACC [13.333, 20.44, 22.426] SCR [13.333, 20.44, 22.426] RESET [13.333, 20.44, 22.426]
    5_transfers_to_fresh_copy              0/3  FULL [53.96, 52.88, 50.85] vs ACC remainder [53.96, 52.88, 50.85]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [53.96, 52.88, 50.85]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [53.96, 52.88, 50.85] STORAGE_MATCHED [53.96, 52.88, 50.85] vs ACC remainder [53.96, 52.88, 50.85]
  contemp_1d9fe66b86095f69
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [13, 20, 22] vs FRESH [13, 20, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1596.2, 1599.4, 1472.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [53.96, 52.88, 50.85] vs CODE_ONLY [53.96, 52.88, 50.85]
    4_scramble_or_reset_damages            0/3  eff ACC [13.333, 20.44, 22.426] SCR [13.333, 20.44, 22.426] RESET [13.333, 20.44, 22.426]
    5_transfers_to_fresh_copy              0/3  FULL [53.96, 52.88, 50.85] vs ACC remainder [53.96, 52.88, 50.85]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [53.96, 52.88, 50.85]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [53.96, 52.88, 50.85] STORAGE_MATCHED [53.96, 52.88, 50.85] vs ACC remainder [53.96, 52.88, 50.85]
  contemp_8a3624109261aae4
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [13, 20, 22] vs FRESH [13, 20, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1596.2, 1599.4, 1472.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [53.96, 52.88, 50.85] vs CODE_ONLY [53.96, 52.88, 50.85]
    4_scramble_or_reset_damages            0/3  eff ACC [13.333, 20.44, 22.426] SCR [13.333, 20.44, 22.426] RESET [13.333, 20.44, 22.426]
    5_transfers_to_fresh_copy              0/3  FULL [53.96, 52.88, 50.85] vs ACC remainder [53.96, 52.88, 50.85]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [53.96, 52.88, 50.85]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [53.96, 52.88, 50.85] STORAGE_MATCHED [53.96, 52.88, 50.85] vs ACC remainder [53.96, 52.88, 50.85]
  ancestor189_it299_29540b8b822dcf12
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [13, 20, 22] vs FRESH [13, 20, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1596.2, 1599.4, 1472.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [53.96, 52.88, 50.85] vs CODE_ONLY [53.96, 52.88, 50.85]
    4_scramble_or_reset_damages            0/3  eff ACC [13.333, 20.44, 22.426] SCR [13.333, 20.44, 22.426] RESET [13.333, 20.44, 22.426]
    5_transfers_to_fresh_copy              0/3  FULL [53.96, 52.88, 50.85] vs ACC remainder [53.96, 52.88, 50.85]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [53.96, 52.88, 50.85]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [53.96, 52.88, 50.85] STORAGE_MATCHED [53.96, 52.88, 50.85] vs ACC remainder [53.96, 52.88, 50.85]
  RANDOM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 6, 9] vs FRESH [6, 6, 9]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1491.8, 1515.0, 1485.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.21, 50.5, 48.99] vs CODE_ONLY [49.21, 50.5, 48.99]
    4_scramble_or_reset_damages            0/3  eff ACC [6.205, 6.235, 9.221] SCR [6.205, 6.235, 9.221] RESET [6.205, 6.235, 9.221]
    5_transfers_to_fresh_copy              0/3  FULL [49.21, 50.5, 48.99] vs ACC remainder [49.21, 50.5, 48.99]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.21, 50.5, 48.99]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.21, 50.5, 48.99] STORAGE_MATCHED [49.21, 50.5, 48.99] vs ACC remainder [49.21, 50.5, 48.99]
  contemp_325b83f87533782c
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [1, 7, 8] vs FRESH [1, 7, 8]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1570.3, 1573.5, 1493.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [53.96, 51.44, 49.41] vs CODE_ONLY [53.96, 51.44, 49.41]
    4_scramble_or_reset_damages            0/3  eff ACC [1.136, 7.241, 8.224] SCR [1.136, 7.241, 8.224] RESET [1.136, 7.241, 8.224]
    5_transfers_to_fresh_copy              0/3  FULL [53.96, 51.44, 49.41] vs ACC remainder [53.96, 51.44, 49.41]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [53.96, 51.44, 49.41]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [53.96, 51.44, 49.41] STORAGE_MATCHED [53.96, 51.44, 49.41] vs ACC remainder [53.96, 51.44, 49.41]

MACHINERY OF top1_a6d81c1c5184b346 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   0     0
    task  9:     0    0    0    0    0 |   0     0
    task 19:     0    0    0    0    0 |   0     0
    task 31:     0    0    0    0    0 |   0     0
    task 41:     0    0    0    0    0 |   0     0
    task 49:     0    0    0    0    0 |   0     0
  artifact events: 0 (create 0, delete 0, patch/append 0); invocations by block: {}; edges: 0
  adaptation curve ACC:   9 2044 454 392 9 9 129 2108 244 1425 107 454 392 392 9 1078 1078 454 2044 122 54 31 54 54 54 54 54 54 54 54 54 54 54 54 54 54 54 54 54 54 54 54 54 54 54 54 54 54 54 54
  adaptation curve FRESH: 9 2044 454 392 9 9 129 2108 244 1425 107 454 392 392 9 1078 1078 454 2044 122 54 31 54 54 54 54 54 54 54 54 54 54 54 54 54 54 54 54 54 54 54 54 54 54 54 54 54 54 54 54
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

