CRIUS CAMPAIGN 0 REPORT  run=search_c1b_random_s2  arm=random
code_commit=553ccff52 dirty=True config_hash=bbf684cd638167f2 world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1   0.1626    0.1625         0.1625         8          0
    26   0.1626    0.1626         0.1558         1          3
    51   0.1626    0.1626         0.1626         1         14
    76   0.1626    0.1626         0.1558         1         24
   101   6.2443    4.7199         2.4022         2         34
   126   0.1626    0.1626         0.1626         1         38
   151   0.1626    0.1626         0.1626         1         47
   176   0.1626    0.1626         0.1626         2         57
   201   1.1788    0.2896         0.2049         2         66
   226   0.1626    0.1626         0.1490         1         76
   251   0.1626    0.1626         0.1626         1         85
   276   1.1630    0.2877         0.1907         2         97
   300   2.1792    0.4147         0.2398         2        110
  candidates evaluated: 7208   best_ever 7.2763 (3de9517a0c4f2326)  wall 110s

BEST PROGRAM 3de9517a0c4f2326 (len 3, iteration 113, modification delete@0+insert@0+delete@0)
  search seed 201113: fit 2.1951 succ 2/50 inter 98 steps 150 ws_cost 50 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [1800.14, 0.1], "B": [1800.14, 0.1], "C": [50.04, 0.0], "D": [50.04, 0.0], "E": [50.04, 0.0]}
  listing:
      0  BLK_DELETE     R4
      1  ACTI           2
      2  ACTI           7
  ancestry (33 steps, newest first): iteration/fitness/modification
    it  113  2.1951  len  3  delete@0+insert@0+delete@0
    it  112  1.1788  len  4  replace@1+arg@2.0
    it  111  1.1788  len  4  replace@1+arg@4.2+delete@4
    it  110  3.1796  len  5  const@3+const@2
    it  107  3.1955  len  5  swap@2,0+duplicate@2+1->2
    it  106  2.1951  len  4  const@1
    it  105  4.2276  len  4  const@0+insert@3
    it  104  1.1788  len  3  replace@1+duplicate@0+2->1+delete@2
    it  102  0.1626  len  2  const@0
    it  101  6.2443  len  2  delete@2
    it  100  1.1630  len  3  swap@2,0
    it   99  1.1788  len  3  insert@0
    it   98  4.2118  len  2  arg@0.0+duplicate@0+1->1+const@1
    it   36  0.1626  len  1  const@0+const@0
    it   31  0.1626  len  1  const@0+arg@0.0
    ... 19 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7316.0    4.3   74.7
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.3    2.7    1.7
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       0.0    0.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0
  bestever_3de9517a0c4f2326    0.496   0.496   0.496   0.496   0.3   0.3      100      100       0.0    0.0    0.0
  top2_02cdd0228a96f092        0.163   0.163   0.163   0.163   0.0   0.0        0        0       0.0    0.0    0.0
  top3_03418e27884ad420        0.163   0.163   0.163   0.163   0.0   0.0        0        0       0.0    0.0    0.0
  ancestor52_it276_0f4b80283   0.163   0.163   0.163   0.163   0.0   0.0        0        0       0.0    0.0    0.0
  top1_108ed018eab82162        0.163   0.163   0.163   0.163   0.0   0.0       50       50       0.0    0.0    0.0
  contemp_605d6227e00a3cb9     0.163   0.163   0.163   0.163   0.0   0.0        0        0       0.0    0.0    0.0
  contemp_95d6a2e3a41ad157     0.163   0.163   0.163   0.163   0.0   0.0        0        0       0.0    0.0    0.0
  ancestor26_it102_5a424940d   0.163   0.163   0.163   0.163   0.0   0.0      100      100       0.0    0.0    0.0
  contemp_480a441845ebb003     0.163   0.163   0.163   0.163   0.0   0.0        0        0       0.0   32.0    0.0
  ancestor1_it0_917933876bd5   0.163   0.163   0.163   0.163   0.0   0.0        0        0       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.00/ 455.13   14.90/ 539.10   21.11/  47.94   33.21/  48.94   40.07/  50.52
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.13/ 443.81  528.11/ 527.79   47.93/  47.89   48.85/  48.88   50.42/  50.46
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ENUMERATE_VM_C1             494.04/ 494.04  523.26/ 523.26   49.99/  49.99   50.96/  50.96   52.68/  52.68
  RANDOM_C1                  1661.96/1661.96 1626.54/1626.54   50.44/  50.44   50.50/  50.50   48.40/  48.40
  bestever_3de9517a0c4f2326  2000.04/2000.04 2000.04/2000.04   50.04/  50.04   48.41/  48.41   50.04/  50.04
  top2_02cdd0228a96f092      2000.01/2000.01 2000.01/2000.01   50.01/  50.01   50.01/  50.01   50.01/  50.01
  top3_03418e27884ad420      2000.01/2000.01 2000.01/2000.01   50.01/  50.01   50.01/  50.01   50.01/  50.01
  ancestor52_it276_0f4b80283 2000.01/2000.01 2000.01/2000.01   50.01/  50.01   50.01/  50.01   50.01/  50.01
  top1_108ed018eab82162      2000.02/2000.02 2000.02/2000.02   50.02/  50.02   50.02/  50.02   50.02/  50.02
  contemp_605d6227e00a3cb9   2000.02/2000.02 2000.02/2000.02   50.02/  50.02   50.02/  50.02   50.02/  50.02
  contemp_95d6a2e3a41ad157   2000.03/2000.03 2000.03/2000.03   50.03/  50.03   50.03/  50.03   50.03/  50.03
  ancestor26_it102_5a424940d 2000.02/2000.02 2000.02/2000.02   50.02/  50.02   50.02/  50.02   50.02/  50.02
  contemp_480a441845ebb003   2000.10/2000.10 2000.10/2000.10   50.10/  50.10   50.10/  50.10   50.10/  50.10
  ancestor1_it0_917933876bd5 2000.13/2000.13 2000.13/2000.13   50.13/  50.13   50.13/  50.13   50.13/  50.13

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610
  bestever_3de9517a0c4f2326      0/36     2     1/30     2     0/12     2     0/12     2     0/30     2     0/30     2
  top2_02cdd0228a96f092          0/36     0     0/30     0     0/12     0     0/12     0     0/30     0     0/30     0
  top3_03418e27884ad420          0/36     0     0/30     0     0/12     0     0/12     0     0/30     0     0/30     0
  ancestor52_it276_0f4b80283     0/36     0     0/30     0     0/12     0     0/12     0     0/30     0     0/30     0
  top1_108ed018eab82162          0/36     1     0/30     1     0/12     1     0/12     1     0/30     1     0/30     1
  contemp_605d6227e00a3cb9       0/36     0     0/30     0     0/12     0     0/12     0     0/30     0     0/30     0
  contemp_95d6a2e3a41ad157       0/36     0     0/30     0     0/12     0     0/12     0     0/30     0     0/30     0
  ancestor26_it102_5a424940d     0/36     2     0/30     2     0/12     2     0/12     2     0/30     2     0/30     2
  contemp_480a441845ebb003       0/36     0     0/30     0     0/12     0     0/12     0     0/30     0     0/30     0
  ancestor1_it0_917933876bd5     0/36     0     0/30     0     0/12     0     0/12     0     0/30     0     0/30     0

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.26    49.53    36.26    36.26    49.53    49.53    49.53   4.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.55    49.55    49.55    49.55    49.55    49.55    49.55   1.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ENUMERATE_VM_C1               51.73       --    51.73    51.73    51.73    51.73    51.73   0.0
  RANDOM_C1                     49.57       --    49.57    49.57    49.57    49.57    49.57   0.0
  bestever_3de9517a0c4f2326     49.13       --    49.13    49.13    49.13    49.13    49.13   0.0
  top2_02cdd0228a96f092         50.01       --    50.01    50.01    50.01    50.01    50.01   0.0
  top3_03418e27884ad420         50.01       --    50.01    50.01    50.01    50.01    50.01   0.0
  ancestor52_it276_0f4b80283    50.01       --    50.01    50.01    50.01    50.01    50.01   0.0
  top1_108ed018eab82162         50.02       --    50.02    50.02    50.02    50.02    50.02   0.0
  contemp_605d6227e00a3cb9      50.02       --    50.02    50.02    50.02    50.02    50.02   0.0
  contemp_95d6a2e3a41ad157      50.03       --    50.03    50.03    50.03    50.03    50.03   0.0
  ancestor26_it102_5a424940d    50.02       --    50.02    50.02    50.02    50.02    50.02   0.0
  contemp_480a441845ebb003      50.10    50.10    50.10    50.10    50.10    50.10    50.10  32.0
  ancestor1_it0_917933876bd5    50.13       --    50.13    50.13    50.13    50.13    50.13   0.0

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
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1580.4, 1529.9, 1482.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.68, 52.68, 49.82] vs CODE_ONLY [52.68, 52.68, 49.82]
    4_scramble_or_reset_damages            0/3  eff ACC [18.368, 18.401, 22.446] SCR [18.368, 18.401, 22.446] RESET [18.368, 18.401, 22.446]
    5_transfers_to_fresh_copy              0/3  FULL [52.68, 52.68, 49.82] vs ACC remainder [52.68, 52.68, 49.82]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.68, 52.68, 49.82]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.68, 52.68, 49.82] STORAGE_MATCHED [52.68, 52.68, 49.82] vs ACC remainder [52.68, 52.68, 49.82]
  RANDOM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 6, 9] vs FRESH [6, 6, 9]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1491.8, 1515.0, 1485.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.21, 50.5, 48.99] vs CODE_ONLY [49.21, 50.5, 48.99]
    4_scramble_or_reset_damages            0/3  eff ACC [6.205, 6.235, 9.221] SCR [6.205, 6.235, 9.221] RESET [6.205, 6.235, 9.221]
    5_transfers_to_fresh_copy              0/3  FULL [49.21, 50.5, 48.99] vs ACC remainder [49.21, 50.5, 48.99]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.21, 50.5, 48.99]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.21, 50.5, 48.99] STORAGE_MATCHED [49.21, 50.5, 48.99] vs ACC remainder [49.21, 50.5, 48.99]
  bestever_3de9517a0c4f2326
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 1] vs FRESH [0, 0, 1]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1501.2, 1501.2, 1452.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.04, 50.04, 47.32] vs CODE_ONLY [50.04, 50.04, 47.32]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 1.163] SCR [0.163, 0.163, 1.163] RESET [0.163, 0.163, 1.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.04, 50.04, 47.32] vs ACC remainder [50.04, 50.04, 47.32]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.04, 50.04, 47.32]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.04, 50.04, 47.32] STORAGE_MATCHED [50.04, 50.04, 47.32] vs ACC remainder [50.04, 50.04, 47.32]
  top2_02cdd0228a96f092
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1500.3, 1500.3, 1500.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.01, 50.01, 50.01] vs CODE_ONLY [50.01, 50.01, 50.01]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 0.163] SCR [0.163, 0.163, 0.163] RESET [0.163, 0.163, 0.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.01, 50.01, 50.01] vs ACC remainder [50.01, 50.01, 50.01]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.01, 50.01, 50.01]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.01, 50.01, 50.01] STORAGE_MATCHED [50.01, 50.01, 50.01] vs ACC remainder [50.01, 50.01, 50.01]
  top3_03418e27884ad420
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1500.3, 1500.3, 1500.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.01, 50.01, 50.01] vs CODE_ONLY [50.01, 50.01, 50.01]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 0.163] SCR [0.163, 0.163, 0.163] RESET [0.163, 0.163, 0.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.01, 50.01, 50.01] vs ACC remainder [50.01, 50.01, 50.01]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.01, 50.01, 50.01]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.01, 50.01, 50.01] STORAGE_MATCHED [50.01, 50.01, 50.01] vs ACC remainder [50.01, 50.01, 50.01]
  ancestor52_it276_0f4b8028315a91ed
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1500.3, 1500.3, 1500.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.01, 50.01, 50.01] vs CODE_ONLY [50.01, 50.01, 50.01]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 0.163] SCR [0.163, 0.163, 0.163] RESET [0.163, 0.163, 0.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.01, 50.01, 50.01] vs ACC remainder [50.01, 50.01, 50.01]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.01, 50.01, 50.01]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.01, 50.01, 50.01] STORAGE_MATCHED [50.01, 50.01, 50.01] vs ACC remainder [50.01, 50.01, 50.01]
  top1_108ed018eab82162
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1500.6, 1500.6, 1500.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.02, 50.02, 50.02] vs CODE_ONLY [50.02, 50.02, 50.02]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 0.163] SCR [0.163, 0.163, 0.163] RESET [0.163, 0.163, 0.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.02, 50.02, 50.02] vs ACC remainder [50.02, 50.02, 50.02]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.02, 50.02, 50.02]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.02, 50.02, 50.02] STORAGE_MATCHED [50.02, 50.02, 50.02] vs ACC remainder [50.02, 50.02, 50.02]
  contemp_605d6227e00a3cb9
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1500.6, 1500.6, 1500.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.02, 50.02, 50.02] vs CODE_ONLY [50.02, 50.02, 50.02]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 0.163] SCR [0.163, 0.163, 0.163] RESET [0.163, 0.163, 0.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.02, 50.02, 50.02] vs ACC remainder [50.02, 50.02, 50.02]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.02, 50.02, 50.02]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.02, 50.02, 50.02] STORAGE_MATCHED [50.02, 50.02, 50.02] vs ACC remainder [50.02, 50.02, 50.02]
  contemp_95d6a2e3a41ad157
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1500.9, 1500.9, 1500.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.03, 50.03, 50.03] vs CODE_ONLY [50.03, 50.03, 50.03]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 0.163] SCR [0.163, 0.163, 0.163] RESET [0.163, 0.163, 0.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.03, 50.03, 50.03] vs ACC remainder [50.03, 50.03, 50.03]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.03, 50.03, 50.03]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.03, 50.03, 50.03] STORAGE_MATCHED [50.03, 50.03, 50.03] vs ACC remainder [50.03, 50.03, 50.03]
  ancestor26_it102_5a424940df5d6b0e
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1500.6, 1500.6, 1500.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.02, 50.02, 50.02] vs CODE_ONLY [50.02, 50.02, 50.02]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 0.163] SCR [0.163, 0.163, 0.163] RESET [0.163, 0.163, 0.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.02, 50.02, 50.02] vs ACC remainder [50.02, 50.02, 50.02]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.02, 50.02, 50.02]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.02, 50.02, 50.02] STORAGE_MATCHED [50.02, 50.02, 50.02] vs ACC remainder [50.02, 50.02, 50.02]
  contemp_480a441845ebb003
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1503.0, 1503.0, 1503.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.1, 50.1, 50.1] vs CODE_ONLY [50.1, 50.1, 50.1]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 0.163] SCR [0.163, 0.163, 0.163] RESET [0.163, 0.163, 0.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.1, 50.1, 50.1] vs ACC remainder [50.1, 50.1, 50.1]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [50.1, 50.1, 50.1] vs ACC remainder [50.1, 50.1, 50.1]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.1, 50.1, 50.1] STORAGE_MATCHED [50.1, 50.1, 50.1] vs ACC remainder [50.1, 50.1, 50.1]
  ancestor1_it0_917933876bd532c2
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1503.9, 1503.9, 1503.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.13, 50.13, 50.13] vs CODE_ONLY [50.13, 50.13, 50.13]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 0.163] SCR [0.163, 0.163, 0.163] RESET [0.163, 0.163, 0.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.13, 50.13, 50.13] vs ACC remainder [50.13, 50.13, 50.13]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.13, 50.13, 50.13]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.13, 50.13, 50.13] STORAGE_MATCHED [50.13, 50.13, 50.13] vs ACC remainder [50.13, 50.13, 50.13]

MACHINERY OF top1_108ed018eab82162 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   0     0
    task  9:     0    0    0    0    0 |   0     0
    task 19:     0    0    0    0    0 |   0     0
    task 31:     0    0    0    0    0 |   0     0
    task 41:     0    0    0    0    0 |   0     0
    task 49:     0    0    0    0    0 |   0     0
  artifact events: 0 (create 0, delete 0, patch/append 0); invocations by block: {}; edges: 0
  adaptation curve ACC:   2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50
  adaptation curve FRESH: 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50 50
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

