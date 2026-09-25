CRIUS CAMPAIGN 0 REPORT  run=search_c2c_seeded_s2  arm=seeded
code_commit=f16d49322 dirty=True config_hash=416bbe8b9be34706 world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  21.4764   21.4738        11.0382        39          7
    26  21.4315   21.4315        13.1519        36        137
    51  20.4300   20.4295        11.1763        35        265
    76  23.9155   23.7288        15.7703        50        384
   101  19.8207   19.8202        14.9074        48        489
   126  23.4006   23.4002        16.8538        53        596
   151  24.4335   22.8419        14.2843        50        717
   176  22.4031   22.4031        14.6737        40        830
   201  21.3962   21.3961        12.1008        36        954
   226  20.9055   20.9055        14.6809        29       1061
   251  24.4552   24.4552        13.7827        24       1186
   276  24.9687   24.9432        14.6559        23       1312
   300  20.9617   20.9531         9.2675        23       1431
  candidates evaluated: 7208   best_ever 29.4694 (1e4b4964aec87ca6)  wall 1431s

BEST PROGRAM 1e4b4964aec87ca6 (len 35, iteration 198, modification arg@29.0)
  search seed 2011980: fit 22.4357 succ 22/50 inter 7582 steps 32332 ws_cost 15 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [284.118, 1.0], "B": [352.418, 1.0], "C": [50.553, 0.167], "D": [51.86, 0.0], "E": [51.86, 0.0]}
  search seed 2011981: fit 19.4021 succ 19/50 inter 11578 steps 46382 ws_cost 15 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [378.66, 1.0], "B": [669.957, 0.9], "C": [51.86, 0.0], "D": [51.86, 0.0], "E": [51.86, 0.0]}
  listing:
      0  INPUT          R1, num_ops
      1  CONST          R5, -5
      2  BRZ            R2, 8
      3  NOT            R5, R2
      4  EQ             R5, R5, R6
      5  BLK_COUNT      R6
      6  BLK_DELETE     R4
      7  JMP            5
      8  CONST          R0, 16
      9  ACT            R1
     10  MOD            R3, R0, R1
     11  ACT            R3
     12  DIV            R4, R0, R1
     13  MOD            R3, R4, R1
     14  ACT            R3
     15  DIV            R4, R4, R1
     16  MOD            R3, R4, R1
     17  ACT            R3
     18  ADD            R0, R0, R5
     19  JMP            9
     20  SUB            R1, R2, R0
     21  PSIM           R1, R4, R5
     22  BLK_NEW        R4
     23  BLK_DELETE     R2
     24  PSIM           R3, R5, R4
     25  BRZ            R0, 5
     26  WS_ALLOC       R0, R7
     27  BLK_APPEND     R3, R0
     28  WS_FREE        R1
     29  BLK_COMPOSE    R0, R0, R7
     30  BLK_DELETE     R4
     31  EQ             R6, R3, R6
     32  PSIM           R5, R5, R7
     33  WS_APPEND      R4, R3
     34  ACT            R2
  ancestry (87 steps, newest first): iteration/fitness/modification
    it  198  20.9189  len 35  arg@29.0
    it  194  16.8764  len 35  delete@4+replace@25+delete@8
    it  190  21.4002  len 37  swap@27,29+delete@35+arg@2.0
    it  188  21.9523  len 38  insert@37+delete@6
    it  186  25.9697  len 38  delete@37
    it  185  23.4515  len 39  delete@25+replace@28+replace@3
    it  184  24.9643  len 40  swap@33,34
    it  183  23.9066  len 40  replace@4
    it  178  18.3840  len 40  arg@35.0+delete@29
    it  171  22.9568  len 41  delete@12+arg@29.0+arg@40.0
    it  169  24.4627  len 42  swap@10,34
    it  168  18.9132  len 42  swap@30,31
    it  167  20.4557  len 42  delete@6
    it  164  22.4260  len 43  delete@30+replace@37
    it  163  22.4319  len 44  swap@30,9
    ... 73 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7315.4    5.3   74.7
  top3_e4eea048c0ecae78       22.432  22.432  22.432  22.432  22.0  22.0     7992     7992       7.0    1.0    0.0
  contemp_8411b5ff0e62152b    22.432  22.432  22.432  22.432  22.0  22.0     7992     7992       7.0    1.0    0.0
  ancestor124_it290_34b1a5ed  22.432  22.432  22.432  22.432  22.0  22.0     7992     7992       7.0    1.0    0.0
  top2_082f2939581c0419       22.090  22.090  22.090  22.090  21.7  21.7     9076     9076       7.2    1.0    0.0
  bestever_1e4b4964aec87ca6   21.764  21.764  21.764  21.764  21.3  21.3     8190     8190       7.1    1.0    0.0
  top1_ccccac14c9e9c953       21.091  21.091  21.091  21.091  20.7  20.7     8921     8921       7.1    1.0    0.0
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.9    3.7    1.7
  ancestor62_it129_547492fc0  20.065  20.065  20.065  20.065  19.7  19.7    12061    12061       5.7    1.0    0.0
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ancestor1_it0_0875253d162c  19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  contemp_b1add4435d34e17f    16.019  16.019  16.019  16.019  15.7  15.7    17429    17429       7.1    1.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0
  contemp_87d3356b01958f8f     0.149   0.149   0.149   0.149   0.0   0.0    41500    41500       2.0    1.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.02/ 455.13   14.92/ 539.10   21.12/  47.94   33.22/  48.94   40.08/  50.52
  top3_e4eea048c0ecae78       321.38/ 321.50  362.66/ 362.80   48.35/  48.49   49.52/  49.66   51.87/  52.02
  contemp_8411b5ff0e62152b    321.40/ 321.52  362.68/ 362.82   48.37/  48.51   49.54/  49.68   51.89/  52.04
  ancestor124_it290_34b1a5ed  321.40/ 321.52  362.68/ 362.82   48.37/  48.51   49.54/  49.68   51.89/  52.04
  top2_082f2939581c0419       343.03/ 343.16  451.45/ 451.59   48.83/  48.98   50.88/  51.03   51.89/  52.04
  bestever_1e4b4964aec87ca6   317.05/ 317.17  384.14/ 384.28   50.01/  50.16   50.75/  50.90   51.86/  52.01
  top1_ccccac14c9e9c953       362.71/ 362.84  417.85/ 417.99   49.28/  49.42   50.84/  50.99   52.06/  52.21
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.14/ 443.81  528.13/ 527.79   47.94/  47.89   48.86/  48.88   50.43/  50.46
  ancestor62_it129_547492fc0  343.01/ 343.12  757.77/ 757.90   51.87/  51.98   49.93/  50.04   51.87/  51.98
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ancestor1_it0_0875253d162c  495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  ENUMERATE_VM_C1             495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  contemp_b1add4435d34e17f    806.59/ 806.72  856.70/ 856.83   51.65/  51.80   50.91/  51.06   50.10/  50.25
  RANDOM_C1                  1662.62/1662.62 1627.07/1627.07   50.50/  50.50   50.50/  50.50   48.56/  48.56
  contemp_87d3356b01958f8f   2080.06/2080.10 2080.06/2080.10   52.06/  52.10   52.06/  52.10   52.06/  52.10

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  top3_e4eea048c0ecae78          4/36    46     2/30    48     0/12    50     0/12    50    30/30   308    30/30   348
  contemp_8411b5ff0e62152b       4/36    46     2/30    48     0/12    50     0/12    50    30/30   308    30/30   348
  ancestor124_it290_34b1a5ed     4/36    46     2/30    48     0/12    50     0/12    50    30/30   308    30/30   348
  top2_082f2939581c0419          3/36    47     2/30    49     0/12    50     0/12    50    30/30   329    30/30   434
  bestever_1e4b4964aec87ca6      2/36    48     2/30    49     0/12    50     0/12    50    30/30   304    30/30   369
  top1_ccccac14c9e9c953          4/36    47     1/30    49     0/12    50     0/12    50    28/30   347    29/30   400
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  ancestor62_it129_547492fc0     0/36    50     2/30    48     0/12    50     0/12    50    30/30   329    27/30   729
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ancestor1_it0_0875253d162c     2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  contemp_b1add4435d34e17f       2/36    50     1/30    49     0/12    50     1/12    46    22/30   774    21/30   822
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610
  contemp_87d3356b01958f8f       0/36    50     0/30    50     0/12    50     0/12    50     0/30  2000     0/30  2000

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.27    49.53    36.27    36.27    49.53    49.53    49.53   5.0
  top3_e4eea048c0ecae78         50.56    50.57    50.56    50.56    50.57    50.57    50.57   1.0
  contemp_8411b5ff0e62152b      50.58    50.59    50.58    50.58    50.59    50.59    50.59   1.0
  ancestor124_it290_34b1a5ed    50.58    50.59    50.58    50.58    50.59    50.59    50.59   1.0
  top2_082f2939581c0419         51.33    51.34    51.33    51.33    51.34    51.34    51.34   1.0
  bestever_1e4b4964aec87ca6     51.24    51.25    51.24    51.24    51.25    51.25    51.25   1.0
  top1_ccccac14c9e9c953         51.38    51.39    51.38    51.38    51.39    51.39    51.39   1.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.56    49.55    49.56    49.56    49.55    49.55    49.55   2.0
  ancestor62_it129_547492fc0    50.79    50.80    50.79    50.79    50.80    50.80    50.80   1.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ancestor1_it0_0875253d162c    51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  ENUMERATE_VM_C1               51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  contemp_b1add4435d34e17f      50.55    50.56    50.55    50.55    50.56    50.56    50.56   1.0
  RANDOM_C1                     49.64       --    49.64    49.64    49.64    49.64    49.64   0.0
  contemp_87d3356b01958f8f      52.06    52.06    52.06    52.06    52.06    52.06    52.06   1.0

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
  top3_e4eea048c0ecae78
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [21, 23, 22] vs FRESH [21, 23, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.4, 4.4, 4.4] vs 5% of FRESH cost [1513.8, 1473.2, 1497.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.87, 49.97, 49.85] vs CODE_ONLY [51.88, 49.97, 49.86]
    4_scramble_or_reset_damages            0/3  eff ACC [21.44, 23.419, 22.437] SCR [21.44, 23.419, 22.437] RESET [21.44, 23.419, 22.437]
    5_transfers_to_fresh_copy              0/3  FULL [51.87, 49.97, 49.85] vs ACC remainder [51.87, 49.97, 49.85]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.88, 49.97, 49.86] vs ACC remainder [51.87, 49.97, 49.85]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.88, 49.97, 49.86] STORAGE_MATCHED [51.88, 49.97, 49.86] vs ACC remainder [51.87, 49.97, 49.85]
  contemp_8411b5ff0e62152b
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [21, 23, 22] vs FRESH [21, 23, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.4, 4.4, 4.4] vs 5% of FRESH cost [1514.4, 1473.8, 1497.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.89, 49.98, 49.87] vs CODE_ONLY [51.9, 49.99, 49.88]
    4_scramble_or_reset_damages            0/3  eff ACC [21.44, 23.419, 22.437] SCR [21.44, 23.419, 22.437] RESET [21.44, 23.419, 22.437]
    5_transfers_to_fresh_copy              0/3  FULL [51.89, 49.98, 49.87] vs ACC remainder [51.89, 49.98, 49.87]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.9, 49.99, 49.88] vs ACC remainder [51.89, 49.98, 49.87]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.9, 49.99, 49.88] STORAGE_MATCHED [51.9, 49.99, 49.88] vs ACC remainder [51.89, 49.98, 49.87]
  ancestor124_it290_34b1a5ede0915824
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [21, 23, 22] vs FRESH [21, 23, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.4, 4.4, 4.4] vs 5% of FRESH cost [1514.4, 1473.8, 1497.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.89, 49.98, 49.87] vs CODE_ONLY [51.9, 49.99, 49.88]
    4_scramble_or_reset_damages            0/3  eff ACC [21.44, 23.419, 22.437] SCR [21.44, 23.419, 22.437] RESET [21.44, 23.419, 22.437]
    5_transfers_to_fresh_copy              0/3  FULL [51.89, 49.98, 49.87] vs ACC remainder [51.89, 49.98, 49.87]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.9, 49.99, 49.88] vs ACC remainder [51.89, 49.98, 49.87]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.9, 49.99, 49.88] STORAGE_MATCHED [51.9, 49.99, 49.88] vs ACC remainder [51.89, 49.98, 49.87]
  top2_082f2939581c0419
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 21, 24] vs FRESH [20, 21, 24]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.4] vs 5% of FRESH cost [1561.2, 1516.5, 1465.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.89, 51.89, 50.21] vs CODE_ONLY [51.9, 51.9, 50.22]
    4_scramble_or_reset_damages            0/3  eff ACC [20.435, 21.404, 24.43] SCR [20.435, 21.404, 24.43] RESET [20.435, 21.404, 24.43]
    5_transfers_to_fresh_copy              0/3  FULL [51.89, 51.89, 50.21] vs ACC remainder [51.89, 51.89, 50.21]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.9, 51.9, 50.22] vs ACC remainder [51.89, 51.89, 50.21]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.9, 51.9, 50.22] STORAGE_MATCHED [51.9, 51.9, 50.22] vs ACC remainder [51.89, 51.89, 50.21]
  bestever_1e4b4964aec87ca6
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [21, 21, 22] vs FRESH [21, 21, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.5] vs 5% of FRESH cost [1544.7, 1520.8, 1515.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.99, 51.86, 50.88] vs CODE_ONLY [51.0, 51.87, 50.89]
    4_scramble_or_reset_damages            0/3  eff ACC [21.428, 21.414, 22.45] SCR [21.428, 21.414, 22.45] RESET [21.428, 21.414, 22.45]
    5_transfers_to_fresh_copy              0/3  FULL [50.99, 51.86, 50.88] vs ACC remainder [50.99, 51.86, 50.88]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.0, 51.87, 50.89] vs ACC remainder [50.99, 51.86, 50.88]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.0, 51.87, 50.89] STORAGE_MATCHED [51.0, 51.87, 50.89] vs ACC remainder [50.99, 51.86, 50.88]
  top1_ccccac14c9e9c953
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 21, 23] vs FRESH [18, 21, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.4] vs 5% of FRESH cost [1550.6, 1528.7, 1482.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.06, 52.06, 50.03] vs CODE_ONLY [52.07, 52.07, 50.04]
    4_scramble_or_reset_damages            0/3  eff ACC [18.403, 21.405, 23.465] SCR [18.403, 21.405, 23.465] RESET [18.403, 21.405, 23.465]
    5_transfers_to_fresh_copy              0/3  FULL [52.06, 52.06, 50.03] vs ACC remainder [52.06, 52.06, 50.03]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.07, 52.07, 50.04] vs ACC remainder [52.06, 52.06, 50.03]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.07, 52.07, 50.04] STORAGE_MATCHED [52.07, 52.07, 50.04] vs ACC remainder [52.06, 52.06, 50.03]
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
  ancestor62_it129_547492fc03656577
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 20, 20] vs FRESH [19, 20, 20]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [3.3, 3.3, 3.2] vs 5% of FRESH cost [1559.4, 1550.0, 1510.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.87, 51.35, 49.16] vs CODE_ONLY [51.88, 51.35, 49.17]
    4_scramble_or_reset_damages            0/3  eff ACC [19.379, 20.399, 20.416] SCR [19.379, 20.399, 20.416] RESET [19.379, 20.399, 20.416]
    5_transfers_to_fresh_copy              0/3  FULL [51.87, 51.35, 49.16] vs ACC remainder [51.87, 51.35, 49.16]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.88, 51.35, 49.17] vs ACC remainder [51.87, 51.35, 49.16]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.88, 51.35, 49.17] STORAGE_MATCHED [51.88, 51.35, 49.17] vs ACC remainder [51.87, 51.35, 49.16]
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
  contemp_b1add4435d34e17f
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [14, 14, 19] vs FRESH [14, 14, 19]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.4, 4.4, 4.5] vs 5% of FRESH cost [1505.8, 1530.8, 1566.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.45, 50.15, 52.05] vs CODE_ONLY [49.46, 50.16, 52.06]
    4_scramble_or_reset_damages            0/3  eff ACC [14.327, 14.329, 19.401] SCR [14.327, 14.329, 19.401] RESET [14.327, 14.329, 19.401]
    5_transfers_to_fresh_copy              0/3  FULL [49.45, 50.15, 52.05] vs ACC remainder [49.45, 50.15, 52.05]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [49.46, 50.16, 52.06] vs ACC remainder [49.45, 50.15, 52.05]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.46, 50.16, 52.06] STORAGE_MATCHED [49.46, 50.16, 52.06] vs ACC remainder [49.45, 50.15, 52.05]
  RANDOM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 6, 9] vs FRESH [6, 6, 9]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1493.8, 1515.0, 1489.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.32, 50.5, 49.1] vs CODE_ONLY [49.32, 50.5, 49.1]
    4_scramble_or_reset_damages            0/3  eff ACC [6.205, 6.235, 9.221] SCR [6.205, 6.235, 9.221] RESET [6.205, 6.235, 9.221]
    5_transfers_to_fresh_copy              0/3  FULL [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.32, 50.5, 49.1]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.32, 50.5, 49.1] STORAGE_MATCHED [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
  contemp_87d3356b01958f8f
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [1.2, 1.2, 1.2] vs 5% of FRESH cost [1563.0, 1563.0, 1563.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.06, 52.06, 52.06] vs CODE_ONLY [52.06, 52.06, 52.06]
    4_scramble_or_reset_damages            0/3  eff ACC [0.149, 0.149, 0.149] SCR [0.149, 0.149, 0.149] RESET [0.149, 0.149, 0.149]
    5_transfers_to_fresh_copy              0/3  FULL [52.06, 52.06, 52.06] vs ACC remainder [52.06, 52.06, 52.06]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.06, 52.06, 52.06] vs ACC remainder [52.06, 52.06, 52.06]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.06, 52.06, 52.06] STORAGE_MATCHED [52.06, 52.06, 52.06] vs ACC remainder [52.06, 52.06, 52.06]

MACHINERY OF top1_ccccac14c9e9c953 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   1    32
    task  9:     0    0    0    0    0 |   1    32
    task 19:     0    0    0    0    0 |   1    32
    task 31:     0    0    0    0    0 |   1    32
    task 41:     0    0    0    0    0 |   1    32
    task 49:     0    0    0    0    0 |   1    32
  artifact events: 1 (create 1, delete 0, patch/append 0); invocations by block: {}; edges: 0
    block 0 origin=calibration len=0 state=[[2, 3, 6, 8, 10, 4, 9, 11, 5, 0, 7, 1], [9, 11, 0, 1, 5, 8, 2, 10, 3, 6, 4, 7], 0] instr=[]
  adaptation curve ACC:   58 2080 7 932 11 58 73 2080 326 176 14 7 932 932 76 224 224 7 2080 138 52 52 52 52 52 52 36 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
  adaptation curve FRESH: 58 2080 7 932 11 58 73 2080 326 176 14 7 932 932 76 224 224 7 2080 138 52 52 52 52 52 52 37 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
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

