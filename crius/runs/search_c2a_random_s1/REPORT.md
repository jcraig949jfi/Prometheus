CRIUS CAMPAIGN 0 REPORT  run=search_c2a_random_s1  arm=random
code_commit=96d299784 dirty=True config_hash=401915ec4da9443a world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1   0.6627    0.2876         0.1089        12          8
    26   0.1626    0.1626         0.1694         1         41
    51   2.1872    1.6125         0.9407         1         67
    76   4.6945    4.0129         2.8667        16        127
   101   8.7714    8.0673         6.7396        24        205
   126   3.6705    1.9148         1.5585        27        279
   151   4.1978    2.4210         1.3429        49        374
   176   5.2298    4.3075         3.2587        46        494
   201   9.2599    5.7839         4.2461        63        582
   226  11.7645   10.4394         8.1887        73        658
   251   8.7345    4.8320         4.0114        78        740
   276   9.7547    8.7375         5.8598        91        826
   300  12.7795    8.8689         6.8281        94        895
  candidates evaluated: 7208   best_ever 14.8087 (24ee1a8400fb9d73)  wall 895s

BEST PROGRAM 24ee1a8400fb9d73 (len 91, iteration 296, modification arg@70.0)
  search seed 1012960: fit 15.3534 succ 15/50 inter 17752 steps 26335 ws_cost 1384 blocks 32 invoked 469 ws_bytes 0
    by stage (mean cost, success rate): {"A": [1169.983, 0.5], "B": [485.737, 0.9], "C": [46.691, 0.083], "D": [50.65, 0.0], "E": [50.65, 0.0]}
  search seed 1012961: fit 14.2641 succ 14/50 inter 28595 steps 40295 ws_cost 2144 blocks 32 invoked 720 ws_bytes 0
    by stage (mean cost, success rate): {"A": [1204.889, 0.8], "B": [1547.122, 0.5], "C": [48.965, 0.083], "D": [50.65, 0.0], "E": [50.65, 0.0]}
  listing:
      0  WS_SREAD       R4, R2, R6
      1  BRZ            R2, 33
      2  CONST          R7, -2
      3  WS_SREAD       R4, R7, R6
      4  DIV            R5, R4, R7
      5  BLK_STATE_SET  R3, R5, R1
      6  WS_LINK        R7, R6, R4
      7  ACTI           15
      8  WS_FIND        R5, R0
      9  VGET           R4, R0, R5
     10  WS_REC_NEW     R2
     11  BLK_INVOKE     R4
     12  INPUT          R0, current_block
     13  BRZ            R2, 20
     14  WS_REC_SET     R3, R6, R2
     15  WS_WRITE       R0, R0
     16  MOV            R7, R7
     17  MUL            R6, R3, R6
     18  MUL            R6, R3, R6
     19  ACTI           -9
     20  WS_REC_NEW     R2
     21  BLK_INVOKE     R4
     22  INPUT          R0, current_block
     23  BRZ            R2, 25
     24  WS_REC_SET     R3, R6, R2
     25  MOV            R6, R0
     26  BLK_INVOKE     R4
     27  BRZ            R2, 25
     28  WS_REC_SET     R3, R6, R2
     29  DIV            R5, R4, R7
     30  BLK_STATE_SET  R3, R5, R1
     31  INPUT          R1, current_block
     32  BLK_INVOKE     R4
     33  CONST          R5, 14
     34  BLK_INVOKE     R5
     35  ACTI           1
     36  MUL            R6, R3, R6
     37  MOD            R1, R6, R3
     38  CONST          R7, -1
     39  BLK_REC_END    R7
     40  ACTI           7
     41  CONST          R7, -5
     42  VSET           R4, R2, R7
     43  ACTI           7
     44  MOV            R5, R0
     45  EQ             R5, R0, R4
     46  BLK_REC_BEGIN  
     47  ACTI           8
     48  ACTI           7
     49  ACTI           5
     50  VGET           R4, R5, R1
     51  SUB            R5, R4, R2
     52  MOV            R7, R7
     53  ACTI           2
     54  ACTI           5
     55  ACT            R7
     56  ACTI           9
     57  ACTI           7
     58  CONST          R7, -5
     59  VSET           R0, R2, R7
     60  MOV            R5, R0
     61  ACTI           6
     62  ACTI           9
     63  ACTI           7
     64  ACT            R5
     65  ACTI           7
     66  ACTI           8
     67  VSET           R3, R1, R5
     68  NOT            R3, R1
     69  BLK_INVOKE     R4
     70  ACTI           -7
     71  BRNZ           R1, 80
     72  ACTI           7
     73  CONST          R7, -2
     74  WS_LINK_GET    R1, R0, R3
     75  BRZ            R2, 33
     76  WS_READ        R2, R4
     77  ACTI           -2
     78  WS_FIND        R0, R6
     79  BLK_STATE_SET  R3, R5, R1
     80  INPUT          R3, num_ops
     81  WS_APPEND      R5, R2
     82  BLK_INVOKE     R5
     83  BLK_INVOKE     R5
     84  ACTI           1
     85  ACTI           9
     86  WS_REC_SET     R7, R3, R2
     87  WS_FREE        R7
     88  ACTI           6
     89  EQ             R5, R4, R0
     90  ACTI           5
  ancestry (178 steps, newest first): iteration/fitness/modification
    it  296  14.8087  len 91  arg@70.0
    it  294  6.7194  len 91  delete@34
    it  293  10.2594  len 92  duplicate@71+1->49+insert@56
    it  292  6.2062  len 90  arg@43.0
    it  289  8.7577  len 90  replace@86
    it  286  10.7723  len 90  const@68+arg@63.0+insert@66
    it  285  7.2315  len 89  const@42
    it  284  8.2168  len 89  delete@16
    it  283  12.2928  len 90  replace@88+arg@3.1
    it  280  10.7316  len 90  delete@61+arg@9.2+delete@43
    it  279  9.7474  len 92  swap@17,91+replace@87
    it  278  11.7843  len 92  duplicate@4+2->30
    it  277  9.7558  len 90  swap@26,20+delete@26+delete@80
    it  276  8.2327  len 92  const@86
    it  275  12.2562  len 92  arg@7.0+const@54
    ... 164 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7316.0    4.3   74.7
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.3    2.7    1.7
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       0.0    0.0    0.0
  top1_933ec6955715f0cc        7.233   6.199   7.233   6.900   7.0   6.0    32329    36401    4192.4   32.0  848.7
  contemp_1fe355158f1a998d     7.225   6.893   6.891   7.558   7.0   6.7    33355    33091    -209.1   32.0 1183.7
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0
  top3_3b17c4a717ac2baa        5.888   6.546   6.221   5.888   5.7   6.3    33776    34794    1088.2   32.0  869.0
  bestever_24ee1a8400fb9d73    5.888   6.546   6.221   5.888   5.7   6.3    33776    34794    1090.2   32.0  869.0
  ancestor180_it297_2a6dc450   5.888   6.546   6.221   5.888   5.7   6.3    33776    34794    1099.9   32.0  868.7
  top2_76e8e79eee810f98        5.531   4.526   4.864   5.864   5.3   4.3    36637    37206     646.3   32.0  947.0
  ancestor90_it152_c14b914d8   2.516   2.516   2.516   2.516   2.3   2.3    37688    37688       0.0    0.0    0.0
  contemp_5cc49bec8db5be35     1.843   3.867   1.843   2.176   1.7   3.7    39186    36161   -3002.7   32.0 1215.3
  contemp_be02547a1584f1bf     1.168   1.501   1.168   0.834   1.0   1.3     2507     3107      15.7    1.0  101.0
  ancestor1_it0_071a88bd5e8e   0.163   0.163   0.163   0.163   0.0   0.0       50       50       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.00/ 455.13   14.90/ 539.10   21.11/  47.94   33.21/  48.94   40.07/  50.52
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.13/ 443.81  528.11/ 527.79   47.93/  47.89   48.85/  48.88   50.42/  50.46
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ENUMERATE_VM_C1             495.80/ 495.80  525.01/ 525.01   50.10/  50.10   51.09/  51.09   52.68/  52.68
  top1_933ec6955715f0cc      1456.04/1754.83 1675.47/1795.05   49.42/  49.35   50.71/  51.27   50.71/  51.19
  contemp_1fe355158f1a998d   1598.20/1643.65 1638.91/1570.58   49.45/  50.01   50.51/  51.34   50.74/  51.34
  RANDOM_C1                  1662.62/1662.62 1627.07/1627.07   50.50/  50.50   50.50/  50.50   48.56/  48.56
  top3_3b17c4a717ac2baa      1581.73/1656.70 1693.61/1726.58   49.39/  49.43   50.68/  51.15   50.68/  51.15
  bestever_24ee1a8400fb9d73  1581.93/1656.97 1693.81/1726.86   49.40/  49.45   50.69/  51.17   50.69/  51.17
  ancestor180_it297_2a6dc450 1582.95/1658.34 1694.85/1728.29   49.42/  49.55   50.71/  51.27   50.71/  51.27
  top2_76e8e79eee810f98      1601.89/1768.22 1965.85/1860.03   49.49/  50.78   50.70/  51.32   48.89/  51.32
  ancestor90_it152_c14b914d8 1939.85/1939.85 1814.91/1814.91   50.60/  50.60   51.86/  51.86   51.86/  51.86
  contemp_5cc49bec8db5be35   1916.64/1635.00 1913.38/1893.66   49.54/  49.88   50.83/  51.21   50.83/  51.21
  contemp_be02547a1584f1bf   1934.58/1935.23 2001.14/2001.86   49.76/  49.45   51.12/  51.43   50.95/  51.28
  ancestor1_it0_071a88bd5e8e 2000.22/2000.22 2000.22/2000.22   50.22/  50.22   50.22/  50.22   50.22/  50.22

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  top1_933ec6955715f0cc          1/36    49     0/30    50     0/12    50     0/12    50    11/30  1434     9/30  1651
  contemp_1fe355158f1a998d       1/36    49     1/30    50     0/12    50     0/12    50    11/30  1573     8/30  1614
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610
  top3_3b17c4a717ac2baa          1/36    49     0/30    50     0/12    50     0/12    50     9/30  1559     7/30  1670
  bestever_24ee1a8400fb9d73      1/36    49     0/30    50     0/12    50     0/12    50     9/30  1559     7/30  1670
  ancestor180_it297_2a6dc450     1/36    49     0/30    50     0/12    50     0/12    50     9/30  1559     7/30  1670
  top2_76e8e79eee810f98          1/36    49     0/30    50     0/12    50     1/12    46    12/30  1578     2/30  1938
  ancestor90_it152_c14b914d8     1/36    49     0/30    50     0/12    50     0/12    50     2/30  1870     4/30  1750
  contemp_5cc49bec8db5be35       1/36    49     0/30    50     0/12    50     0/12    50     2/30  1887     2/30  1884
  contemp_be02547a1584f1bf       1/36    49     0/30    50     0/12    50     1/12    50     1/30    51     0/30    51
  ancestor1_it0_071a88bd5e8e     0/36     1     0/30     1     0/12     1     0/12     1     0/30     1     0/30     1

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.26    49.53    36.26    36.26    49.53    49.53    49.53   4.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.55    49.55    49.55    49.55    49.55    49.55    49.55   1.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ENUMERATE_VM_C1               51.80       --    51.80    51.80    51.80    51.80    51.80   0.0
  top1_933ec6955715f0cc         50.71    51.44    50.71    50.71    51.13    51.13    51.13  32.0
  contemp_1fe355158f1a998d      50.61    51.60    50.61    50.61    51.02    51.02    51.02  32.0
  RANDOM_C1                     49.64       --    49.64    49.64    49.64    49.64    49.64   0.0
  top3_3b17c4a717ac2baa         50.68    51.33    50.68    50.68    51.03    51.03    51.03  32.0
  bestever_24ee1a8400fb9d73     50.69    51.36    50.69    50.69    51.05    51.05    51.05  32.0
  ancestor180_it297_2a6dc450    50.71    51.51    50.71    50.71    51.14    51.14    51.14  32.0
  top2_76e8e79eee810f98         49.89    51.47    49.89    49.89    50.16    50.16    50.16  32.0
  ancestor90_it152_c14b914d8    51.86       --    51.86    51.86    51.86    51.86    51.86   0.0
  contemp_5cc49bec8db5be35      50.83    51.55    50.83    50.83    51.12    51.12    51.12  32.0
  contemp_be02547a1584f1bf      51.05    50.84    51.00    51.05    51.06    51.06    51.06   1.0
  ancestor1_it0_071a88bd5e8e    50.22       --    50.22    50.22    50.22    50.22    50.22   0.0

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
  top1_933ec6955715f0cc
    0_competence_kept_ACC_ge_FRESH         2/3  successes ACC [5, 5, 11] vs FRESH [5, 7, 6]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [18.3, -36.0, 43.6] vs 5% of FRESH cost [1538.1, 1488.2, 1516.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.66, 50.81, 50.66] vs CODE_ONLY [51.13, 51.13, 51.13]
    4_scramble_or_reset_damages            1/3  eff ACC [5.222, 5.221, 11.256] SCR [5.222, 5.221, 10.256] RESET [5.222, 6.222, 10.255]
    5_transfers_to_fresh_copy              0/3  FULL [50.66, 50.81, 50.66] vs ACC remainder [50.66, 50.81, 50.66]
    6_executable_components_reused         0/3  invocations [804, 1011, 731]; ABLATION_ALL cost [51.51, 51.51, 51.3] vs ACC remainder [50.66, 50.81, 50.66]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.13, 51.13, 51.13] STORAGE_MATCHED [51.13, 51.13, 51.13] vs ACC remainder [50.66, 50.81, 50.66]
  contemp_1fe355158f1a998d
    0_competence_kept_ACC_ge_FRESH         2/3  successes ACC [4, 8, 9] vs FRESH [1, 11, 8]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [18.0, -30.0, 71.5] vs 5% of FRESH cost [1540.2, 1492.2, 1540.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.74, 50.74, 50.35] vs CODE_ONLY [51.02, 51.02, 51.02]
    4_scramble_or_reset_damages            0/3  eff ACC [4.191, 8.248, 9.235] SCR [4.191, 8.248, 10.236] RESET [4.191, 9.248, 7.235]
    5_transfers_to_fresh_copy              0/3  FULL [50.74, 50.74, 50.35] vs ACC remainder [50.74, 50.74, 50.35]
    6_executable_components_reused         0/3  invocations [1231, 1027, 1293]; ABLATION_ALL cost [51.6, 51.6, 51.6] vs ACC remainder [50.74, 50.74, 50.35]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.02, 51.02, 51.02] STORAGE_MATCHED [51.02, 51.02, 51.02] vs ACC remainder [50.74, 50.74, 50.35]
  RANDOM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 6, 9] vs FRESH [6, 6, 9]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1493.8, 1515.0, 1489.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.32, 50.5, 49.1] vs CODE_ONLY [49.32, 50.5, 49.1]
    4_scramble_or_reset_damages            0/3  eff ACC [6.205, 6.235, 9.221] SCR [6.205, 6.235, 9.221] RESET [6.205, 6.235, 9.221]
    5_transfers_to_fresh_copy              0/3  FULL [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.32, 50.5, 49.1]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.32, 50.5, 49.1] STORAGE_MATCHED [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
  top3_3b17c4a717ac2baa
    0_competence_kept_ACC_ge_FRESH         1/3  successes ACC [4, 9, 4] vs FRESH [5, 10, 4]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [15.0, -35.9, 47.4] vs 5% of FRESH cost [1534.5, 1486.6, 1520.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.65, 50.75, 50.65] vs CODE_ONLY [51.02, 51.02, 51.05]
    4_scramble_or_reset_damages            0/3  eff ACC [4.196, 9.27, 4.198] SCR [4.196, 9.27, 4.198] RESET [4.196, 10.27, 4.198]
    5_transfers_to_fresh_copy              0/3  FULL [50.65, 50.75, 50.65] vs ACC remainder [50.65, 50.75, 50.65]
    6_executable_components_reused         0/3  invocations [877, 858, 872]; ABLATION_ALL cost [51.33, 51.33, 51.33] vs ACC remainder [50.65, 50.75, 50.65]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.02, 51.02, 51.05] STORAGE_MATCHED [51.02, 51.02, 51.05] vs ACC remainder [50.65, 50.75, 50.65]
  bestever_24ee1a8400fb9d73
    0_competence_kept_ACC_ge_FRESH         1/3  successes ACC [4, 9, 4] vs FRESH [5, 10, 4]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [15.6, -35.6, 48.0] vs 5% of FRESH cost [1535.1, 1487.2, 1521.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.65, 50.76, 50.65] vs CODE_ONLY [51.04, 51.04, 51.07]
    4_scramble_or_reset_damages            0/3  eff ACC [4.196, 9.27, 4.198] SCR [4.196, 9.27, 4.198] RESET [4.196, 10.27, 4.198]
    5_transfers_to_fresh_copy              0/3  FULL [50.65, 50.76, 50.65] vs ACC remainder [50.65, 50.76, 50.65]
    6_executable_components_reused         0/3  invocations [877, 858, 872]; ABLATION_ALL cost [51.36, 51.36, 51.36] vs ACC remainder [50.65, 50.76, 50.65]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.04, 51.04, 51.07] STORAGE_MATCHED [51.04, 51.04, 51.07] vs ACC remainder [50.65, 50.76, 50.65]
  ancestor180_it297_2a6dc450d6113aa3
    0_competence_kept_ACC_ge_FRESH         1/3  successes ACC [4, 9, 4] vs FRESH [5, 10, 4]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [18.3, -34.2, 50.8] vs 5% of FRESH cost [1538.1, 1490.1, 1524.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.66, 50.81, 50.66] vs CODE_ONLY [51.13, 51.13, 51.16]
    4_scramble_or_reset_damages            0/3  eff ACC [4.196, 9.27, 4.198] SCR [4.196, 9.27, 4.198] RESET [4.196, 10.27, 4.198]
    5_transfers_to_fresh_copy              0/3  FULL [50.66, 50.81, 50.66] vs ACC remainder [50.66, 50.81, 50.66]
    6_executable_components_reused         0/3  invocations [877, 858, 871]; ABLATION_ALL cost [51.51, 51.51, 51.51] vs ACC remainder [50.66, 50.81, 50.66]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.13, 51.13, 51.16] STORAGE_MATCHED [51.13, 51.13, 51.16] vs ACC remainder [50.66, 50.81, 50.66]
  top2_76e8e79eee810f98
    0_competence_kept_ACC_ge_FRESH         2/3  successes ACC [1, 7, 8] vs FRESH [4, 3, 6]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [3.4, 58.0, 62.1] vs 5% of FRESH cost [1524.4, 1535.5, 1539.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.7, 48.28, 50.7] vs CODE_ONLY [50.97, 48.55, 50.97]
    4_scramble_or_reset_damages            1/3  eff ACC [1.172, 7.188, 8.233] SCR [2.173, 8.188, 7.232] RESET [1.172, 6.188, 7.232]
    5_transfers_to_fresh_copy              0/3  FULL [50.7, 48.28, 50.7] vs ACC remainder [50.7, 48.28, 50.7]
    6_executable_components_reused         1/3  invocations [1009, 982, 850]; ABLATION_ALL cost [51.62, 51.17, 51.62] vs ACC remainder [50.7, 48.28, 50.7]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.97, 48.55, 50.97] STORAGE_MATCHED [50.97, 48.55, 50.97] vs ACC remainder [50.7, 48.28, 50.7]
  ancestor90_it152_c14b914d8df73c11
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 1, 6] vs FRESH [0, 1, 6]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1555.8, 1555.8, 1510.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.86, 51.86, 51.86] vs CODE_ONLY [51.86, 51.86, 51.86]
    4_scramble_or_reset_damages            0/3  eff ACC [0.15, 1.166, 6.231] SCR [0.15, 1.166, 6.231] RESET [0.15, 1.166, 6.231]
    5_transfers_to_fresh_copy              0/3  FULL [51.86, 51.86, 51.86] vs ACC remainder [51.86, 51.86, 51.86]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.86, 51.86, 51.86]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.86, 51.86, 51.86] STORAGE_MATCHED [51.86, 51.86, 51.86] vs ACC remainder [51.86, 51.86, 51.86]
  contemp_5cc49bec8db5be35
    0_competence_kept_ACC_ge_FRESH         1/3  successes ACC [1, 3, 1] vs FRESH [3, 3, 5]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [11.4, -36.5, 58.0] vs 5% of FRESH cost [1536.3, 1488.4, 1536.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.83, 50.83, 50.83] vs CODE_ONLY [51.12, 51.12, 51.12]
    4_scramble_or_reset_damages            0/3  eff ACC [1.172, 3.2, 1.158] SCR [1.172, 4.2, 1.158] RESET [1.172, 4.2, 0.157]
    5_transfers_to_fresh_copy              0/3  FULL [50.83, 50.83, 50.83] vs ACC remainder [50.83, 50.83, 50.83]
    6_executable_components_reused         0/3  invocations [1230, 1134, 1282]; ABLATION_ALL cost [51.55, 51.55, 51.55] vs ACC remainder [50.83, 50.83, 50.83]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.12, 51.12, 51.12] STORAGE_MATCHED [51.12, 51.12, 51.12] vs ACC remainder [50.83, 50.83, 50.83]
  contemp_be02547a1584f1bf
    0_competence_kept_ACC_ge_FRESH         2/3  successes ACC [0, 3, 0] vs FRESH [0, 3, 1]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [9.3, 10.1, -13.3] vs 5% of FRESH cost [1542.9, 1490.8, 1520.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.12, 50.9, 51.12] vs CODE_ONLY [51.14, 50.92, 51.14]
    4_scramble_or_reset_damages            1/3  eff ACC [0.162, 3.179, 0.162] SCR [0.162, 2.179, 0.162] RESET [0.162, 3.179, 0.162]
    5_transfers_to_fresh_copy              0/3  FULL [51.12, 50.9, 51.12] vs ACC remainder [51.12, 50.9, 51.12]
    6_executable_components_reused         0/3  invocations [101, 101, 101]; ABLATION_ALL cost [50.84, 50.84, 50.84] vs ACC remainder [51.12, 50.9, 51.12]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.14, 50.92, 51.14] STORAGE_MATCHED [51.14, 50.92, 51.14] vs ACC remainder [51.12, 50.9, 51.12]
  ancestor1_it0_071a88bd5e8eed21
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1506.6, 1506.6, 1506.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.22, 50.22, 50.22] vs CODE_ONLY [50.22, 50.22, 50.22]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 0.163] SCR [0.163, 0.163, 0.163] RESET [0.163, 0.163, 0.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.22, 50.22, 50.22] vs ACC remainder [50.22, 50.22, 50.22]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.22, 50.22, 50.22]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.22, 50.22, 50.22] STORAGE_MATCHED [50.22, 50.22, 50.22] vs ACC remainder [50.22, 50.22, 50.22]

MACHINERY OF top1_933ec6955715f0cc (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |  31  6566
    task  9:     0    0    0    0    0 |  32  6832
    task 19:     0    0    0    0    0 |  32  6832
    task 31:     0    0    0    0    0 |  32  6832
    task 41:     0    0    0    0    0 |  32  6832
    task 49:     0    0    0    0    0 |  32  6832
  artifact events: 32 (create 32, delete 0, patch/append 0); invocations by block: {"0": 185, "1": 200, "14": 419}; edges: 0
    block 0 origin=record len=15 state=[0, 0, 0] instr=[[19, 8, 0, 0], [19, 7, 0, 0], [19, 5, 0, 0], [19, 2, 0, 0], [19, 5, 0, 0], [19, 9, 0, 0]]
    block 1 origin=record len=30 state=[0, 0, 0] instr=[[19, 8, 0, 0], [19, 7, 0, 0], [19, 5, 0, 0], [19, 2, 0, 0], [19, 5, 0, 0], [19, 9, 0, 0]]
    block 2 origin=record len=45 state=[0, 0, 0] instr=[[19, 8, 0, 0], [19, 7, 0, 0], [19, 5, 0, 0], [19, 2, 0, 0], [19, 5, 0, 0], [19, 9, 0, 0]]
    block 3 origin=record len=30 state=[0, 0, 0] instr=[[19, 8, 0, 0], [19, 7, 0, 0], [19, 5, 0, 0], [19, 2, 0, 0], [19, 5, 0, 0], [19, 9, 0, 0]]
    block 4 origin=record len=45 state=[0, 0, 0] instr=[[19, 8, 0, 0], [19, 7, 0, 0], [19, 5, 0, 0], [19, 2, 0, 0], [19, 5, 0, 0], [19, 9, 0, 0]]
  adaptation curve ACC:   2032 261 2029 2029 2029 2029 2029 2029 248 1122 2029 2029 2029 2029 2029 325 2029 2029 261 2029 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51
  adaptation curve FRESH: 2032 1903 2032 2032 2032 2032 2032 2032 129 131 2032 2032 2032 2032 2032 467 2032 2032 1903 2032 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51 51
  reuse_gain per task:    0 1643 3 3 3 3 3 3 -119 -991 3 3 3 3 3 143 3 3 1643 3 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1

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

