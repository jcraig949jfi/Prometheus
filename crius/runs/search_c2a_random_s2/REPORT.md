CRIUS CAMPAIGN 0 REPORT  run=search_c2a_random_s2  arm=random
code_commit=96d299784 dirty=True config_hash=401915ec4da9443a world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1   0.1626    0.1625         0.1625         8          0
    26   0.1626    0.1567         0.1553        15         63
    51   1.1745    1.1744         1.0738        13        183
    76   0.1626    0.1626         0.1558         1        246
   101   0.6628    0.6628         0.3293         2        275
   126   0.1626    0.1626         0.1838         1        290
   151   0.1626    0.1626         0.1626         1        308
   176   0.1626    0.1626         0.1838         1        333
   201   4.1995    2.2330         1.7747         9        378
   226   4.7234    3.0736         1.9298        35        457
   251   8.2406    6.2913         4.7533        58        542
   276  10.7352    7.4099         5.3788        79        620
   300   8.7443    8.0473         4.8728        94        692
  candidates evaluated: 7208   best_ever 16.3029 (8998e101040d890b)  wall 692s

BEST PROGRAM 8998e101040d890b (len 83, iteration 277, modification insert@69+duplicate@39+3->67)
  search seed 2012770: fit 17.2992 succ 17/50 inter 24214 steps 41141 ws_cost 7366 blocks 33 invoked 0 ws_bytes 51
    by stage (mean cost, success rate): {"A": [1104.495, 0.7], "B": [1233.392, 0.5], "C": [33.322, 0.417], "D": [51.13, 0.0], "E": [51.13, 0.0]}
  search seed 2012771: fit 15.3067 succ 15/50 inter 23310 steps 39393 ws_cost 7067 blocks 33 invoked 0 ws_bytes 51
    by stage (mean cost, success rate): {"A": [1185.479, 0.6], "B": [1049.387, 0.6], "C": [48.102, 0.083], "D": [47.701, 0.1], "E": [46.463, 0.125]}
  listing:
      0  ADD            R7, R2, R2
      1  BLK_DELETE     R7
      2  BLK_PATCH      R5, R5, R3
      3  ACTI           12
      4  ACTI           1
      5  SUB            R3, R3, R5
      6  BRNZ           R7, 21
      7  ACTI           5
      8  BLK_STATE_SET  R3, R4, R7
      9  BRNZ           R7, 33
     10  BLK_STATE_SET  R3, R4, R7
     11  VSET           R2, R0, R1
     12  ACTI           4
     13  ACTI           7
     14  ACTI           8
     15  WS_APPEND      R6, R4
     16  ACT            R0
     17  ACTI           -20
     18  ACTI           7
     19  BLK_DELETE     R7
     20  WS_LINK_GET    R6, R6, R0
     21  INPUT          R0, current
     22  WS_WRITE       R7, R7
     23  LT             R3, R1, R1
     24  BLK_PATCH      R5, R5, R3
     25  ACTI           12
     26  ACTI           1
     27  ACTI           12
     28  BRNZ           R7, 21
     29  ACTI           5
     30  ACTI           1
     31  WS_SREAD       R3, R0, R0
     32  ACT            R7
     33  ACTI           7
     34  INPUT          R0, current
     35  ACTI           7
     36  ACTI           8
     37  ACTI           8
     38  ACTI           -20
     39  ACT            R0
     40  ACTI           7
     41  ACTI           20
     42  ACTI           7
     43  BLK_DELETE     R7
     44  ACTI           5
     45  ACTI           7
     46  ACTI           8
     47  ACT            R0
     48  ACTI           8
     49  ACTI           -20
     50  ACTI           5
     51  ACTI           5
     52  ACTI           7
     53  ACTI           8
     54  ACT            R0
     55  WS_READ        R1, R2
     56  WS_FREE        R6
     57  MOV            R7, R5
     58  BLK_NEW        R3
     59  ACTI           6
     60  ACTI           7
     61  BLK_DELETE     R7
     62  ACTI           5
     63  ACTI           7
     64  ACTI           8
     65  ACT            R0
     66  ACTI           5
     67  ACT            R0
     68  ACTI           7
     69  ACTI           20
     70  ACTI           -19
     71  ACTI           5
     72  BLK_REC_END    R1
     73  ACTI           -7
     74  ACT            R0
     75  ACTI           7
     76  ACTI           -20
     77  ACTI           5
     78  BLK_DELETE     R7
     79  ACTI           7
     80  ACTI           2
     81  JMP            30
     82  ACTI           5
  ancestry (134 steps, newest first): iteration/fitness/modification
    it  277  16.3029  len 83  insert@69+duplicate@39+3->67
    it  276  10.7352  len 79  delete@51
    it  275  9.7575  len 80  const@67+duplicate@47+5->71+const@48
    it  273  5.2119  len 75  arg@63.0+duplicate@42+6->61+insert@15
    it  272  7.7109  len 68  replace@5
    it  271  7.2360  len 68  insert@0+arg@31.0+delete@17
    it  270  7.7354  len 68  const@11+duplicate@1+6->23
    it  269  8.2024  len 62  insert@22+delete@14+replace@50
    it  268  5.2061  len 62  replace@11+arg@25.0+delete@9
    it  267  8.2383  len 63  delete@19
    it  265  6.7062  len 64  delete@59+swap@22,32
    it  263  7.7185  len 65  delete@21
    it  262  9.2514  len 66  insert@15
    it  261  6.2173  len 65  swap@22,46+duplicate@33+5->11
    it  260  6.7156  len 60  swap@6,11
    ... 120 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7316.0    4.3   74.7
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.3    2.7    1.7
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       0.0    0.0    0.0
  top1_f51ccd5faa432f7f        9.244   8.572   9.244   9.244   9.0   8.3    30959    31514     560.2   54.0    0.0
  top2_4cc3f4be87c74ce5        9.243   8.572   9.243   9.243   9.0   8.3    30959    31514     560.3   54.0    0.0
  ancestor150_it299_4cc3f4be   9.243   8.572   9.243   9.243   9.0   8.3    30959    31514     560.3   54.0    0.0
  contemp_fa8c9f7abb2a3415     9.243   8.572   9.243   9.243   9.0   8.3    30959    31514     560.3   54.0    0.0
  bestever_8998e101040d890b    8.921   8.921   8.921   8.921   8.7   8.7    29709    29709       0.0   33.0    0.0
  top3_13c82e1869116ba5        8.908   7.233   8.908   8.908   8.7   7.0    31204    32218    1025.0   53.7    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0
  contemp_02a1a2a30e6e7e42     6.553   8.904   6.553   6.553   6.3   8.7    33742    31712   -2063.8   34.0    0.0
  contemp_ecc964113e03043e     1.851   1.851   1.851   1.851   1.7   1.7      391      391       0.0    0.0    0.0
  ancestor76_it185_938c865db   0.163   0.163   0.163   0.163   0.0   0.0      200      200       0.0    0.0    0.0
  ancestor1_it0_439be783deb6   0.163   0.163   0.163   0.163   0.0   0.0       50       50       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.00/ 455.13   14.90/ 539.10   21.11/  47.94   33.21/  48.94   40.07/  50.52
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.13/ 443.81  528.11/ 527.79   47.93/  47.89   48.85/  48.88   50.42/  50.46
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ENUMERATE_VM_C1             495.80/ 495.80  525.01/ 525.01   50.10/  50.10   51.09/  51.09   52.68/  52.68
  top1_f51ccd5faa432f7f      1701.90/1592.63 1301.82/1467.11   48.69/  48.69   51.18/  51.18   51.18/  51.18
  top2_4cc3f4be87c74ce5      1702.29/1593.00 1302.13/1467.45   48.70/  48.70   51.19/  51.19   51.19/  51.19
  ancestor150_it299_4cc3f4be 1702.29/1593.00 1302.13/1467.45   48.70/  48.70   51.19/  51.19   51.19/  51.19
  contemp_fa8c9f7abb2a3415   1702.31/1593.02 1302.15/1467.47   48.72/  48.72   51.21/  51.21   51.21/  51.21
  bestever_8998e101040d890b  1551.66/1551.66 1327.92/1327.92   48.71/  48.71   49.56/  49.56   49.70/  49.70
  top3_13c82e1869116ba5      1587.58/1530.65 1443.62/1603.05   48.76/  48.76   51.18/  51.18   51.18/  51.18
  RANDOM_C1                  1662.62/1662.62 1627.07/1627.07   50.50/  50.50   50.50/  50.50   48.56/  48.56
  contemp_02a1a2a30e6e7e42   1649.17/1689.45 1643.42/1396.77   48.32/  48.32   51.23/  51.23   51.23/  51.23
  contemp_ecc964113e03043e   2000.41/2000.41 1734.18/1734.18   49.05/  49.05   50.41/  50.41   50.41/  50.41
  ancestor76_it185_938c865db 2000.06/2000.06 2000.06/2000.06   50.06/  50.06   50.06/  50.06   50.06/  50.06
  ancestor1_it0_439be783deb6 2000.21/2000.21 2000.21/2000.21   50.21/  50.21   50.21/  50.21   50.21/  50.21

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  top1_f51ccd5faa432f7f          3/36    47     0/30    50     0/12    50     0/12    50     9/30  1671    15/30  1278
  top2_4cc3f4be87c74ce5          3/36    47     0/30    50     0/12    50     0/12    50     9/30  1671    15/30  1278
  ancestor150_it299_4cc3f4be     3/36    47     0/30    50     0/12    50     0/12    50     9/30  1671    15/30  1278
  contemp_fa8c9f7abb2a3415       3/36    47     0/30    50     0/12    50     0/12    50     9/30  1671    15/30  1278
  bestever_8998e101040d890b      2/36    48     2/30    48     0/12    50     1/12    47     9/30  1523    12/30  1303
  top3_13c82e1869116ba5          2/36    48     0/30    50     0/12    50     0/12    50    12/30  1558    12/30  1416
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610
  contemp_02a1a2a30e6e7e42       3/36    47     0/30    50     0/12    50     0/12    50    10/30  1617     6/30  1611
  contemp_ecc964113e03043e       1/36     8     0/30     8     0/12     8     0/12     8     0/30     8     4/30     7
  ancestor76_it185_938c865db     0/36     4     0/30     4     0/12     4     0/12     4     0/30     4     0/30     4
  ancestor1_it0_439be783deb6     0/36     1     0/30     1     0/12     1     0/12     1     0/30     1     0/30     1

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.26    49.53    36.26    36.26    49.53    49.53    49.53   4.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.55    49.55    49.55    49.55    49.55    49.55    49.55   1.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ENUMERATE_VM_C1               51.80       --    51.80    51.80    51.80    51.80    51.80   0.0
  top1_f51ccd5faa432f7f         51.18    51.18    51.18    51.18    51.18    51.18    51.18  32.0
  top2_4cc3f4be87c74ce5         51.19    51.19    51.19    51.19    51.19    51.19    51.19  32.0
  ancestor150_it299_4cc3f4be    51.19    51.19    51.19    51.19    51.19    51.19    51.19  32.0
  contemp_fa8c9f7abb2a3415      51.21    51.21    51.21    51.21    51.21    51.21    51.21  32.0
  bestever_8998e101040d890b     49.62    49.62    49.62    49.62    49.62    49.62    49.62  32.0
  top3_13c82e1869116ba5         51.18    51.18    51.18    51.18    51.18    51.18    51.18  32.0
  RANDOM_C1                     49.64       --    49.64    49.64    49.64    49.64    49.64   0.0
  contemp_02a1a2a30e6e7e42      51.23    51.23    51.23    51.23    51.23    51.23    51.23  32.0
  contemp_ecc964113e03043e      50.41       --    50.41    50.41    50.41    50.41    50.41   0.0
  ancestor76_it185_938c865db    50.06       --    50.06    50.06    50.06    50.06    50.06   0.0
  ancestor1_it0_439be783deb6    50.21       --    50.21    50.21    50.21    50.21    50.21   0.0

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
  ENUMERATE_VM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 18, 22] vs FRESH [18, 18, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1580.4, 1531.9, 1488.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.68, 52.68, 50.04] vs CODE_ONLY [52.68, 52.68, 50.04]
    4_scramble_or_reset_damages            0/3  eff ACC [18.368, 18.4, 22.445] SCR [18.368, 18.4, 22.445] RESET [18.368, 18.4, 22.445]
    5_transfers_to_fresh_copy              0/3  FULL [52.68, 52.68, 50.04] vs ACC remainder [52.68, 52.68, 50.04]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.68, 52.68, 50.04]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.68, 52.68, 50.04] STORAGE_MATCHED [52.68, 52.68, 50.04] vs ACC remainder [52.68, 52.68, 50.04]
  top1_f51ccd5faa432f7f
    0_competence_kept_ACC_ge_FRESH         2/3  successes ACC [7, 12, 8] vs FRESH [6, 9, 10]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1535.4, 1494.0, 1487.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.18, 51.18, 51.18] vs CODE_ONLY [51.18, 51.18, 51.18]
    4_scramble_or_reset_damages            0/3  eff ACC [7.239, 12.265, 8.226] SCR [7.239, 12.265, 8.226] RESET [7.239, 12.265, 8.226]
    5_transfers_to_fresh_copy              0/3  FULL [51.18, 51.18, 51.18] vs ACC remainder [51.18, 51.18, 51.18]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.18, 51.18, 51.18] vs ACC remainder [51.18, 51.18, 51.18]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.18, 51.18, 51.18] STORAGE_MATCHED [51.18, 51.18, 51.18] vs ACC remainder [51.18, 51.18, 51.18]
  top2_4cc3f4be87c74ce5
    0_competence_kept_ACC_ge_FRESH         2/3  successes ACC [7, 12, 8] vs FRESH [6, 9, 10]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1535.7, 1494.3, 1487.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.19, 51.19, 51.19] vs CODE_ONLY [51.19, 51.19, 51.19]
    4_scramble_or_reset_damages            0/3  eff ACC [7.239, 12.265, 8.226] SCR [7.239, 12.265, 8.226] RESET [7.239, 12.265, 8.226]
    5_transfers_to_fresh_copy              0/3  FULL [51.19, 51.19, 51.19] vs ACC remainder [51.19, 51.19, 51.19]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.19, 51.19, 51.19] vs ACC remainder [51.19, 51.19, 51.19]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.19, 51.19, 51.19] STORAGE_MATCHED [51.19, 51.19, 51.19] vs ACC remainder [51.19, 51.19, 51.19]
  ancestor150_it299_4cc3f4be87c74ce5
    0_competence_kept_ACC_ge_FRESH         2/3  successes ACC [7, 12, 8] vs FRESH [6, 9, 10]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1535.7, 1494.3, 1487.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.19, 51.19, 51.19] vs CODE_ONLY [51.19, 51.19, 51.19]
    4_scramble_or_reset_damages            0/3  eff ACC [7.239, 12.265, 8.226] SCR [7.239, 12.265, 8.226] RESET [7.239, 12.265, 8.226]
    5_transfers_to_fresh_copy              0/3  FULL [51.19, 51.19, 51.19] vs ACC remainder [51.19, 51.19, 51.19]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.19, 51.19, 51.19] vs ACC remainder [51.19, 51.19, 51.19]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.19, 51.19, 51.19] STORAGE_MATCHED [51.19, 51.19, 51.19] vs ACC remainder [51.19, 51.19, 51.19]
  contemp_fa8c9f7abb2a3415
    0_competence_kept_ACC_ge_FRESH         2/3  successes ACC [7, 12, 8] vs FRESH [6, 9, 10]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1536.3, 1494.9, 1488.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.21, 51.21, 51.21] vs CODE_ONLY [51.21, 51.21, 51.21]
    4_scramble_or_reset_damages            0/3  eff ACC [7.239, 12.265, 8.226] SCR [7.239, 12.265, 8.226] RESET [7.239, 12.265, 8.226]
    5_transfers_to_fresh_copy              0/3  FULL [51.21, 51.21, 51.21] vs ACC remainder [51.21, 51.21, 51.21]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.21, 51.21, 51.21] vs ACC remainder [51.21, 51.21, 51.21]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.21, 51.21, 51.21] STORAGE_MATCHED [51.21, 51.21, 51.21] vs ACC remainder [51.21, 51.21, 51.21]
  bestever_8998e101040d890b
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [5, 13, 8] vs FRESH [5, 13, 8]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1499.6, 1477.4, 1456.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.23, 50.64, 49.0] vs CODE_ONLY [49.23, 50.64, 49.0]
    4_scramble_or_reset_damages            0/3  eff ACC [5.202, 13.316, 8.243] SCR [5.202, 13.316, 8.243] RESET [5.202, 13.316, 8.243]
    5_transfers_to_fresh_copy              0/3  FULL [49.23, 50.64, 49.0] vs ACC remainder [49.23, 50.64, 49.0]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [49.23, 50.64, 49.0] vs ACC remainder [49.23, 50.64, 49.0]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.23, 50.64, 49.0] STORAGE_MATCHED [49.23, 50.64, 49.0] vs ACC remainder [49.23, 50.64, 49.0]
  top3_13c82e1869116ba5
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [5, 11, 10] vs FRESH [5, 8, 8]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1535.4, 1496.0, 1487.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.18, 51.18, 51.18] vs CODE_ONLY [51.18, 51.18, 51.18]
    4_scramble_or_reset_damages            0/3  eff ACC [5.204, 11.257, 10.263] SCR [5.204, 11.257, 10.263] RESET [5.204, 11.257, 10.263]
    5_transfers_to_fresh_copy              0/3  FULL [51.18, 51.18, 51.18] vs ACC remainder [51.18, 51.18, 51.18]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.18, 51.18, 51.18] vs ACC remainder [51.18, 51.18, 51.18]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.18, 51.18, 51.18] STORAGE_MATCHED [51.18, 51.18, 51.18] vs ACC remainder [51.18, 51.18, 51.18]
  RANDOM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 6, 9] vs FRESH [6, 6, 9]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1493.8, 1515.0, 1489.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.32, 50.5, 49.1] vs CODE_ONLY [49.32, 50.5, 49.1]
    4_scramble_or_reset_damages            0/3  eff ACC [6.205, 6.235, 9.221] SCR [6.205, 6.235, 9.221] RESET [6.205, 6.235, 9.221]
    5_transfers_to_fresh_copy              0/3  FULL [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.32, 50.5, 49.1]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.32, 50.5, 49.1] STORAGE_MATCHED [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
  contemp_02a1a2a30e6e7e42
    0_competence_kept_ACC_ge_FRESH         1/3  successes ACC [4, 8, 7] vs FRESH [10, 12, 4]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1521.0, 1495.5, 1489.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.23, 51.23, 51.23] vs CODE_ONLY [51.23, 51.23, 51.23]
    4_scramble_or_reset_damages            0/3  eff ACC [4.192, 8.238, 7.23] SCR [4.192, 8.238, 7.23] RESET [4.192, 8.238, 7.23]
    5_transfers_to_fresh_copy              0/3  FULL [51.23, 51.23, 51.23] vs ACC remainder [51.23, 51.23, 51.23]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.23, 51.23, 51.23] vs ACC remainder [51.23, 51.23, 51.23]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.23, 51.23, 51.23] STORAGE_MATCHED [51.23, 51.23, 51.23] vs ACC remainder [51.23, 51.23, 51.23]
  contemp_ecc964113e03043e
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 2, 3] vs FRESH [0, 2, 3]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1512.3, 1512.3, 1463.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.41, 50.41, 50.41] vs CODE_ONLY [50.41, 50.41, 50.41]
    4_scramble_or_reset_damages            0/3  eff ACC [0.162, 2.195, 3.195] SCR [0.162, 2.195, 3.195] RESET [0.162, 2.195, 3.195]
    5_transfers_to_fresh_copy              0/3  FULL [50.41, 50.41, 50.41] vs ACC remainder [50.41, 50.41, 50.41]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.41, 50.41, 50.41]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.41, 50.41, 50.41] STORAGE_MATCHED [50.41, 50.41, 50.41] vs ACC remainder [50.41, 50.41, 50.41]
  ancestor76_it185_938c865dbb1cd9f6
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1501.8, 1501.8, 1501.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.06, 50.06, 50.06] vs CODE_ONLY [50.06, 50.06, 50.06]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 0.163] SCR [0.163, 0.163, 0.163] RESET [0.163, 0.163, 0.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.06, 50.06, 50.06] vs ACC remainder [50.06, 50.06, 50.06]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.06, 50.06, 50.06]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.06, 50.06, 50.06] STORAGE_MATCHED [50.06, 50.06, 50.06] vs ACC remainder [50.06, 50.06, 50.06]
  ancestor1_it0_439be783deb69522
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1506.3, 1506.3, 1506.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.21, 50.21, 50.21] vs CODE_ONLY [50.21, 50.21, 50.21]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 0.163] SCR [0.163, 0.163, 0.163] RESET [0.163, 0.163, 0.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.21, 50.21, 50.21] vs ACC remainder [50.21, 50.21, 50.21]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.21, 50.21, 50.21]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.21, 50.21, 50.21] STORAGE_MATCHED [50.21, 50.21, 50.21] vs ACC remainder [50.21, 50.21, 50.21]

MACHINERY OF top1_f51ccd5faa432f7f (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     2    1    1    0    0 |  32   320
    task  9:    11    1    1    0    0 |  32   320
    task 19:    21    1    1    0    0 |  32   320
    task 31:    33    1    1    0    0 |  32   320
    task 41:    43    1    1    0    0 |  32   320
    task 49:    51    1    1    0    0 |  32   320
  artifact events: 74 (create 53, delete 21, patch/append 0); invocations by block: {}; edges: 0
    block 21 origin=new len=0 state=[0, 0, 0] instr=[]
    block 22 origin=new len=0 state=[0, 0, 0] instr=[]
    block 23 origin=new len=0 state=[0, 0, 0] instr=[]
    block 24 origin=new len=0 state=[0, 0, 0] instr=[]
    block 25 origin=new len=0 state=[0, 0, 0] instr=[]
  adaptation curve ACC:   2036 2036 2036 150 2036 2036 2036 2036 2036 2036 2036 2036 783 425 1273 979 2036 389 2036 106 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51
  adaptation curve FRESH: 2036 769 178 2036 2036 857 2036 1395 2036 2036 2036 2036 2036 719 2036 2036 704 2036 2036 2036 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51
  reuse_gain per task:    0 -1267 -1858 1885 0 -1178 0 -641 0 0 0 -0 1252 294 763 1057 -1332 1646 -0 1929 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0

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

