CRIUS CAMPAIGN 0 REPORT  run=search_c2c_seeded_s1  arm=seeded
code_commit=f16d49322 dirty=True config_hash=416bbe8b9be34706 world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  21.9592   21.5793         9.4213        39          3
    26  21.4378   21.0014        13.2652        51         93
    51  25.4516   25.4516        18.2396        46        207
    76  21.4164   21.4158        13.1819        42        309
   101  20.4203   20.4203        14.4207        38        428
   126  25.4362   25.0031        15.2280        31        588
   151  21.3390   21.3390         8.8382        27        764
   176  19.3766   19.3766         8.2999        23        920
   201  24.4576   24.0815        12.3791        23       1096
   226  25.4389   25.4389        12.6341        20       1274
   251  20.8950   20.8934         7.8594        20       1461
   276  16.8708   16.8706         9.5295        20       1632
   300  23.4087   22.9705        13.1777        21       1805
  candidates evaluated: 7208   best_ever 28.4473 (4fa36c3fce886357)  wall 1805s

BEST PROGRAM 4fa36c3fce886357 (len 48, iteration 46, modification delete@6+const@29)
  search seed 1010460: fit 23.4768 succ 23/50 inter 2698 steps 15748 ws_cost 15 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [57.102, 1.0], "B": [80.49, 1.0], "C": [45.204, 0.25], "D": [52.07, 0.0], "E": [52.07, 0.0]}
  search seed 1010461: fit 33.4179 succ 33/50 inter 9647 steps 45549 ws_cost 15 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [582.822, 1.0], "B": [303.361, 1.0], "C": [35.481, 0.5], "D": [41.008, 0.5], "E": [50.62, 0.25]}
  listing:
      0  INPUT          R1, num_ops
      1  CONST          R5, 1
      2  CONST          R0, -1
      3  BRZ            R3, 29
      4  MOV            R0, R7
      5  LT             R3, R0, R2
      6  DIV            R1, R4, R1
      7  PMATCH         R7, R4, R6
      8  BRZ            R3, 19
      9  ACT            R3
     10  BRZ            R3, 44
     11  JMP            27
     12  HALT           
     13  EQ             R0, R0, R0
     14  MUL            R2, R1, R1
     15  MUL            R2, R2, R1
     16  ACT            R0
     17  WS_LINKS       R5, R5
     18  ADD            R0, R0, R5
     19  CONST          R0, 0
     20  MUL            R2, R1, R1
     21  LT             R3, R0, R2
     22  MOV            R2, R3
     23  ACT            R1
     24  MOD            R3, R0, R1
     25  DIV            R4, R0, R1
     26  PMATCH         R4, R0, R4
     27  ADD            R0, R0, R5
     28  ACTI           -11
     29  CONST          R0, 8
     30  MUL            R2, R1, R1
     31  MOD            R4, R4, R3
     32  LT             R3, R0, R2
     33  MOD            R3, R0, R1
     34  ACT            R1
     35  ADD            R0, R0, R5
     36  ACT            R3
     37  DIV            R4, R0, R1
     38  MOD            R3, R4, R1
     39  ACT            R3
     40  DIV            R4, R4, R1
     41  MOD            R3, R4, R1
     42  ACT            R3
     43  JMP            32
     44  BLK_LEN        R1, R7
     45  HALT           
     46  CONST          R0, 1
     47  HALT           
  ancestry (21 steps, newest first): iteration/fitness/modification
    it   46  28.4473  len 48  delete@6+const@29
    it   43  19.3982  len 49  swap@34,36
    it   42  20.8917  len 49  delete@15
    it   41  22.3975  len 50  delete@48
    it   37  23.9528  len 51  delete@27+const@2+arg@7.0
    it   35  22.4572  len 52  swap@24,3+duplicate@13+3->48+replace@34
    it   32  26.9536  len 49  arg@4.1
    it   30  21.4298  len 49  const@15+delete@30
    it   27  21.4640  len 50  const@32+insert@8+swap@48,49
    it   26  20.9390  len 49  replace@31
    it   23  19.9340  len 49  const@33+arg@22.0+delete@17
    it   19  19.3724  len 50  delete@5
    it   17  22.4495  len 51  delete@49+delete@22+arg@50.0
    it   16  22.9249  len 53  swap@11,39
    it   13  24.4446  len 53  insert@4+insert@5+insert@52
    ... 7 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7315.4    5.3   74.7
  ancestor48_it98_20dbc5f1ec  21.420  21.420  21.420  21.420  21.0  21.0     9378     9378       6.8    1.0    0.0
  top1_34a7c4a1bfe1b4da       21.081  21.081  21.081  21.081  20.7  20.7    10144    10144       7.3    1.0    0.0
  top2_b1e984305a213e83       21.080  21.080  21.080  21.080  20.7  20.7    10206    10206       7.3    1.0    0.0
  top3_0af9932720c878a7       21.080  21.080  21.080  21.080  20.7  20.7    10257    10257       7.3    1.0    0.0
  ancestor94_it281_30775555a  21.080  21.080  21.080  21.080  20.7  20.7    10257    10257       7.3    1.0    0.0
  bestever_4fa36c3fce886357   20.748  20.748  20.748  20.748  20.3  20.3    10035    10035       7.0    1.0    0.0
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.9    3.7    1.7
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ancestor1_it0_0875253d162c  19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  contemp_4881e87730bf5b03    12.604  12.604  12.604  12.604  12.3  12.3    26670    26670       4.9    1.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0
  contemp_6e8b7736ae0197e9     5.534   5.534   5.534   5.534   5.3   5.3    35574    35574       6.4    1.0    0.0
  contemp_38bd11233a242107     0.000   0.000   0.000   0.000   0.0   0.0        0        0       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.02/ 455.13   14.92/ 539.10   21.12/  47.94   33.22/  48.94   40.08/  50.52
  ancestor48_it98_20dbc5f1ec  408.49/ 408.61  421.60/ 421.72   48.41/  48.55   49.54/  49.69   50.33/  50.47
  top1_34a7c4a1bfe1b4da       437.53/ 437.66  468.34/ 468.49   48.92/  49.07   51.24/  51.39   51.93/  52.08
  top2_b1e984305a213e83       440.43/ 440.57  471.35/ 471.50   49.27/  49.42   51.34/  51.49   51.93/  52.08
  top3_0af9932720c878a7       443.33/ 443.47  474.36/ 474.50   49.62/  49.76   50.30/  50.45   51.93/  52.08
  ancestor94_it281_30775555a  443.33/ 443.47  474.36/ 474.50   49.62/  49.76   50.30/  50.45   51.93/  52.08
  bestever_4fa36c3fce886357   439.79/ 439.91  457.14/ 457.28   49.49/  49.64   50.40/  50.55   51.63/  51.78
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.14/ 443.81  528.13/ 527.79   47.94/  47.89   48.86/  48.88   50.43/  50.46
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ancestor1_it0_0875253d162c  495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  ENUMERATE_VM_C1             495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  contemp_4881e87730bf5b03   1433.42/1433.55 1231.82/1231.96   52.88/  52.95   51.22/  51.29   52.88/  52.95
  RANDOM_C1                  1662.62/1662.62 1627.07/1627.07   50.50/  50.50   50.50/  50.50   48.56/  48.56
  contemp_6e8b7736ae0197e9   1637.80/1637.93 1884.31/1884.46   51.71/  51.83   51.71/  51.83   51.71/  51.83
  contemp_38bd11233a242107   2400.04/2400.04 2400.04/2400.04  450.04/ 450.04  450.04/ 450.04  450.04/ 450.04

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  ancestor48_it98_20dbc5f1ec     3/36    46     2/30    48     1/12    47     0/12    50    28/30   392    29/30   404
  top1_34a7c4a1bfe1b4da          4/36    47     1/30    49     0/12    50     0/12    50    28/30   420    29/30   449
  top2_b1e984305a213e83          4/36    47     1/30    49     0/12    50     0/12    50    28/30   422    29/30   452
  top3_0af9932720c878a7          4/36    48     1/30    48     0/12    50     0/12    50    28/30   425    29/30   455
  ancestor94_it281_30775555a     4/36    48     1/30    48     0/12    50     0/12    50    28/30   425    29/30   455
  bestever_4fa36c3fce886357      3/36    47     2/30    48     1/12    49     0/12    50    27/30   421    28/30   438
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ancestor1_it0_0875253d162c     2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  contemp_4881e87730bf5b03       0/36    50     1/30    48     0/12    50     0/12    50    18/30  1355    18/30  1164
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610
  contemp_6e8b7736ae0197e9       0/36    50     0/30    50     0/12    50     0/12    50    10/30  1584     6/30  1823
  contemp_38bd11233a242107       0/36     0     0/30     0     0/12     0     0/12     0     0/30     0     0/30     0

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.27    49.53    36.27    36.27    49.53    49.53    49.53   5.0
  ancestor48_it98_20dbc5f1ec    49.89    49.90    49.89    49.89    49.90    49.90    49.90   1.0
  top1_34a7c4a1bfe1b4da         51.54    51.55    51.54    51.54    51.55    51.55    51.55   1.0
  top2_b1e984305a213e83         51.60    51.61    51.60    51.60    51.61    51.61    51.61   1.0
  top3_0af9932720c878a7         51.03    51.03    51.03    51.03    51.03    51.03    51.03   1.0
  ancestor94_it281_30775555a    51.03    51.03    51.03    51.03    51.03    51.03    51.03   1.0
  bestever_4fa36c3fce886357     50.95    50.96    50.95    50.95    50.96    50.96    50.96   1.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.56    49.55    49.56    49.56    49.55    49.55    49.55   2.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ancestor1_it0_0875253d162c    51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  ENUMERATE_VM_C1               51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  contemp_4881e87730bf5b03      51.96    51.96    51.96    51.96    51.96    51.96    51.96   1.0
  RANDOM_C1                     49.64       --    49.64    49.64    49.64    49.64    49.64   0.0
  contemp_6e8b7736ae0197e9      51.71    51.72    51.71    51.71    51.72    51.72    51.72   1.0
  contemp_38bd11233a242107     450.04       --   450.04   450.04   450.04   850.12   450.04   0.0

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
  ancestor48_it98_20dbc5f1ec63ff86
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 21, 23] vs FRESH [19, 21, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.4, 4.4, 4.3] vs 5% of FRESH cost [1518.6, 1489.5, 1441.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.93, 49.79, 47.95] vs CODE_ONLY [51.94, 49.8, 47.95]
    4_scramble_or_reset_damages            0/3  eff ACC [19.384, 21.424, 23.454] SCR [19.384, 21.424, 23.454] RESET [19.384, 21.424, 23.454]
    5_transfers_to_fresh_copy              0/3  FULL [51.93, 49.79, 47.95] vs ACC remainder [51.93, 49.79, 47.95]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.94, 49.8, 47.95] vs ACC remainder [51.93, 49.79, 47.95]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.94, 49.8, 47.95] STORAGE_MATCHED [51.94, 49.8, 47.95] vs ACC remainder [51.93, 49.79, 47.95]
  top1_34a7c4a1bfe1b4da
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 20, 24] vs FRESH [18, 20, 24]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.4] vs 5% of FRESH cost [1562.4, 1538.5, 1457.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.93, 51.93, 50.77] vs CODE_ONLY [51.94, 51.94, 50.78]
    4_scramble_or_reset_damages            0/3  eff ACC [18.385, 20.417, 24.441] SCR [18.385, 20.417, 24.441] RESET [18.385, 20.417, 24.441]
    5_transfers_to_fresh_copy              0/3  FULL [51.93, 51.93, 50.77] vs ACC remainder [51.93, 51.93, 50.77]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.94, 51.94, 50.78] vs ACC remainder [51.93, 51.93, 50.77]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.94, 51.94, 50.78] STORAGE_MATCHED [51.94, 51.94, 50.78] vs ACC remainder [51.93, 51.93, 50.77]
  top2_b1e984305a213e83
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 20, 24] vs FRESH [18, 20, 24]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.4] vs 5% of FRESH cost [1562.4, 1541.6, 1469.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.93, 51.93, 50.95] vs CODE_ONLY [51.94, 51.94, 50.96]
    4_scramble_or_reset_damages            0/3  eff ACC [18.384, 20.416, 24.44] SCR [18.384, 20.416, 24.44] RESET [18.384, 20.416, 24.44]
    5_transfers_to_fresh_copy              0/3  FULL [51.93, 51.93, 50.95] vs ACC remainder [51.93, 51.93, 50.95]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.94, 51.94, 50.96] vs ACC remainder [51.93, 51.93, 50.95]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.94, 51.94, 50.96] STORAGE_MATCHED [51.94, 51.94, 50.96] vs ACC remainder [51.93, 51.93, 50.95]
  top3_0af9932720c878a7
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 20, 24] vs FRESH [18, 20, 24]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.3] vs 5% of FRESH cost [1562.4, 1544.7, 1447.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.93, 51.93, 49.22] vs CODE_ONLY [51.94, 51.94, 49.23]
    4_scramble_or_reset_damages            0/3  eff ACC [18.384, 20.416, 24.44] SCR [18.384, 20.416, 24.44] RESET [18.384, 20.416, 24.44]
    5_transfers_to_fresh_copy              0/3  FULL [51.93, 51.93, 49.22] vs ACC remainder [51.93, 51.93, 49.22]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.94, 51.94, 49.23] vs ACC remainder [51.93, 51.93, 49.22]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.94, 51.94, 49.23] STORAGE_MATCHED [51.94, 51.94, 49.23] vs ACC remainder [51.93, 51.93, 49.22]
  ancestor94_it281_30775555a9d889b3
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 20, 24] vs FRESH [18, 20, 24]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.3] vs 5% of FRESH cost [1562.4, 1544.7, 1447.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.93, 51.93, 49.22] vs CODE_ONLY [51.94, 51.94, 49.23]
    4_scramble_or_reset_damages            0/3  eff ACC [18.384, 20.416, 24.44] SCR [18.384, 20.416, 24.44] RESET [18.384, 20.416, 24.44]
    5_transfers_to_fresh_copy              0/3  FULL [51.93, 51.93, 49.22] vs ACC remainder [51.93, 51.93, 49.22]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.94, 51.94, 49.23] vs ACC remainder [51.93, 51.93, 49.22]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.94, 51.94, 49.23] STORAGE_MATCHED [51.94, 51.94, 49.23] vs ACC remainder [51.93, 51.93, 49.22]
  bestever_4fa36c3fce886357
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 19, 23] vs FRESH [19, 19, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.4, 4.4, 4.4] vs 5% of FRESH cost [1528.0, 1522.7, 1495.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.07, 51.49, 49.29] vs CODE_ONLY [52.08, 51.5, 49.3]
    4_scramble_or_reset_damages            0/3  eff ACC [19.38, 19.416, 23.448] SCR [19.38, 19.416, 23.448] RESET [19.38, 19.416, 23.448]
    5_transfers_to_fresh_copy              0/3  FULL [52.07, 51.49, 49.29] vs ACC remainder [52.07, 51.49, 49.29]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.08, 51.5, 49.3] vs ACC remainder [52.07, 51.49, 49.29]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.08, 51.5, 49.3] STORAGE_MATCHED [52.08, 51.5, 49.3] vs ACC remainder [52.07, 51.49, 49.29]
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
  contemp_4881e87730bf5b03
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [12, 10, 15] vs FRESH [12, 10, 15]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [2.1, 2.1, 2.1] vs 5% of FRESH cost [1588.5, 1588.5, 1538.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.88, 52.88, 50.12] vs CODE_ONLY [52.88, 52.88, 50.12]
    4_scramble_or_reset_damages            0/3  eff ACC [12.302, 10.24, 15.27] SCR [12.302, 10.24, 15.27] RESET [12.302, 10.24, 15.27]
    5_transfers_to_fresh_copy              0/3  FULL [52.88, 52.88, 50.12] vs ACC remainder [52.88, 52.88, 50.12]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.88, 52.88, 50.12] vs ACC remainder [52.88, 52.88, 50.12]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.88, 52.88, 50.12] STORAGE_MATCHED [52.88, 52.88, 50.12] vs ACC remainder [52.88, 52.88, 50.12]
  RANDOM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 6, 9] vs FRESH [6, 6, 9]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1493.8, 1515.0, 1489.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.32, 50.5, 49.1] vs CODE_ONLY [49.32, 50.5, 49.1]
    4_scramble_or_reset_damages            0/3  eff ACC [6.205, 6.235, 9.221] SCR [6.205, 6.235, 9.221] RESET [6.205, 6.235, 9.221]
    5_transfers_to_fresh_copy              0/3  FULL [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.32, 50.5, 49.1]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.32, 50.5, 49.1] STORAGE_MATCHED [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
  contemp_6e8b7736ae0197e9
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [8, 4, 4] vs FRESH [8, 4, 4]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [3.6, 3.6, 3.6] vs 5% of FRESH cost [1554.9, 1554.9, 1554.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.71, 51.71, 51.71] vs CODE_ONLY [51.72, 51.72, 51.72]
    4_scramble_or_reset_damages            0/3  eff ACC [8.238, 4.189, 4.177] SCR [8.238, 4.189, 4.177] RESET [8.238, 4.189, 4.177]
    5_transfers_to_fresh_copy              0/3  FULL [51.71, 51.71, 51.71] vs ACC remainder [51.71, 51.71, 51.71]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.72, 51.72, 51.72] vs ACC remainder [51.71, 51.71, 51.71]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.72, 51.72, 51.72] STORAGE_MATCHED [51.72, 51.72, 51.72] vs ACC remainder [51.71, 51.71, 51.71]
  contemp_38bd11233a242107
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [13501.2, 13501.2, 13501.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [450.04, 450.04, 450.04] vs CODE_ONLY [450.04, 450.04, 450.04]
    4_scramble_or_reset_damages            0/3  eff ACC [0.0, 0.0, 0.0] SCR [0.0, 0.0, 0.0] RESET [0.0, 0.0, 0.0]
    5_transfers_to_fresh_copy              0/3  FULL [450.04, 450.04, 450.04] vs ACC remainder [450.04, 450.04, 450.04]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [450.04, 450.04, 450.04]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [850.12, 850.12, 850.12] STORAGE_MATCHED [450.04, 450.04, 450.04] vs ACC remainder [450.04, 450.04, 450.04]

MACHINERY OF top1_34a7c4a1bfe1b4da (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   1    32
    task  9:     0    0    0    0    0 |   1    32
    task 19:     0    0    0    0    0 |   1    32
    task 31:     0    0    0    0    0 |   1    32
    task 41:     0    0    0    0    0 |   1    32
    task 49:     0    0    0    0    0 |   1    32
  artifact events: 1 (create 1, delete 0, patch/append 0); invocations by block: {}; edges: 0
    block 0 origin=calibration len=0 state=[[2, 3, 6, 8, 10, 4, 9, 11, 5, 0, 7, 1], [9, 11, 0, 1, 5, 8, 2, 10, 3, 6, 4, 7], 0] instr=[]
  adaptation curve ACC:   167 2076 61 862 64 133 86 1500 94 179 235 334 862 862 30 1319 1319 27 2076 350 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
  adaptation curve FRESH: 167 2077 61 862 64 133 86 1500 95 179 235 334 862 862 30 1320 1320 27 2077 350 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
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

