CRIUS CAMPAIGN 0 REPORT  run=search_c2d_random_s2  arm=random
code_commit=52c58d0d4 dirty=True config_hash=7ab056c39e1821fd world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1   1.1787    0.4166         0.1933        17          6
    26   0.1626    0.1626         0.1626         1         25
    51   0.1626    0.1626         0.1626         1         42
    76   0.1626    0.1626         0.1558         1         64
   101   0.1626    0.1626         0.1490         1         87
   126   0.6628    0.2251         0.1834         1        103
   151   0.1626    0.1626         0.1626         1        112
   176   0.1626    0.1626         0.1626         1        131
   201   0.1626    0.1626         0.1558         1        157
   226   0.1626    0.1626         0.1702         1        179
   251   0.1626    0.1626         0.1626         1        196
   276   0.1626    0.1626         0.2193         1        220
   300   0.1626    0.1626         0.1626         1        261
  candidates evaluated: 7208   best_ever 4.2196 (48549100542c0ef6)  wall 261s

BEST PROGRAM 48549100542c0ef6 (len 2, iteration 33, modification arg@0.0+duplicate@0+1->0)
  search seed 2010330: fit 1.1788 succ 1/50 inter 99 steps 100 ws_cost 4 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [1800.124, 0.1], "B": [2000.02, 0.0], "C": [50.02, 0.0], "D": [50.02, 0.0], "E": [50.02, 0.0]}
  search seed 2010331: fit 0.1626 succ 0/50 inter 100 steps 100 ws_cost 4 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [2000.024, 0.0], "B": [2000.02, 0.0], "C": [50.02, 0.0], "D": [50.02, 0.0], "E": [50.02, 0.0]}
  listing:
      0  ACT            R1
      1  ACT            R1
  ancestry (14 steps, newest first): iteration/fitness/modification
    it   33  0.6707  len  2  arg@0.0+duplicate@0+1->0
    it   26  0.1626  len  1  replace@0
    it   20  0.1626  len  1  arg@0.1
    it   18  0.1626  len  1  replace@0+replace@0
    it   15  0.1626  len  1  replace@0
    it   14  0.1626  len  1  arg@0.0
    it   13  0.1626  len  1  arg@0.0
    it   10  0.1626  len  1  delete@0
    it    9  0.1626  len  2  replace@1
    it    7  0.1626  len  2  delete@1+swap@1,2+delete@2
    it    5  0.1626  len  4  delete@4
    it    3  0.1626  len  5  delete@1+delete@5
    it    2  0.1626  len  7  swap@3,2
    it    1  0.1626  len  7  delete@1+arg@5.0
    it    0  0.1626  len  8  random_init

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7315.4    5.3   74.7
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.9    3.7    1.7
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0
  top1_00550ee99d42d8e0        0.163   0.163   0.163   0.163   0.0   0.0        0        0       0.0    0.0    0.0
  top2_00f3560aaeb060aa        0.163   0.163   0.163   0.163   0.0   0.0        0        0       0.0    0.0    0.0
  top3_01e345eaf323574b        0.163   0.163   0.163   0.163   0.0   0.0        0        0       0.0    0.0    0.0
  contemp_09c22a7bdfc8a52b     0.163   0.163   0.163   0.163   0.0   0.0        0        0       0.0    0.0    0.0
  ancestor31_it146_0f4b80283   0.163   0.163   0.163   0.163   0.0   0.0        0        0       0.0    0.0    0.0
  ancestor16_it53_15486ff9d6   0.163   0.163   0.163   0.163   0.0   0.0        0        0       0.0    0.0    0.0
  bestever_48549100542c0ef6    0.163   0.163   0.163   0.163   0.0   0.0      100      100       2.0    1.0    0.0
  contemp_b396a264513d7c30     0.163   0.163   0.163   0.163   0.0   0.0        0        0       0.0    0.0    0.0
  contemp_6322334122999d20     0.163   0.163   0.163   0.163   0.0   0.0        0        0       0.0    0.0    0.0
  ancestor1_it0_587acbe8f559   0.163   0.163   0.163   0.163   0.0   0.0        0        0       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.02/ 455.13   14.92/ 539.10   21.12/  47.94   33.22/  48.94   40.08/  50.52
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.14/ 443.81  528.13/ 527.79   47.94/  47.89   48.86/  48.88   50.43/  50.46
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ENUMERATE_VM_C1             495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  RANDOM_C1                  1662.62/1662.62 1627.07/1627.07   50.50/  50.50   50.50/  50.50   48.56/  48.56
  top1_00550ee99d42d8e0      2000.01/2000.01 2000.01/2000.01   50.01/  50.01   50.01/  50.01   50.01/  50.01
  top2_00f3560aaeb060aa      2000.01/2000.01 2000.01/2000.01   50.01/  50.01   50.01/  50.01   50.01/  50.01
  top3_01e345eaf323574b      2000.01/2000.01 2000.01/2000.01   50.01/  50.01   50.01/  50.01   50.01/  50.01
  contemp_09c22a7bdfc8a52b   2000.01/2000.01 2000.01/2000.01   50.01/  50.01   50.01/  50.01   50.01/  50.01
  ancestor31_it146_0f4b80283 2000.01/2000.01 2000.01/2000.01   50.01/  50.01   50.01/  50.01   50.01/  50.01
  ancestor16_it53_15486ff9d6 2000.01/2000.01 2000.01/2000.01   50.01/  50.01   50.01/  50.01   50.01/  50.01
  bestever_48549100542c0ef6  2000.02/2000.06 2000.02/2000.06   50.02/  50.06   50.02/  50.06   50.02/  50.06
  contemp_b396a264513d7c30   2000.04/2000.04 2000.04/2000.04   50.04/  50.04   50.04/  50.04   50.04/  50.04
  contemp_6322334122999d20   2000.09/2000.09 2000.09/2000.09   50.09/  50.09   50.09/  50.09   50.09/  50.09
  ancestor1_it0_587acbe8f559 2000.11/2000.11 2000.11/2000.11   50.11/  50.11   50.11/  50.11   50.11/  50.11

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610
  top1_00550ee99d42d8e0          0/36     0     0/30     0     0/12     0     0/12     0     0/30     0     0/30     0
  top2_00f3560aaeb060aa          0/36     0     0/30     0     0/12     0     0/12     0     0/30     0     0/30     0
  top3_01e345eaf323574b          0/36     0     0/30     0     0/12     0     0/12     0     0/30     0     0/30     0
  contemp_09c22a7bdfc8a52b       0/36     0     0/30     0     0/12     0     0/12     0     0/30     0     0/30     0
  ancestor31_it146_0f4b80283     0/36     0     0/30     0     0/12     0     0/12     0     0/30     0     0/30     0
  ancestor16_it53_15486ff9d6     0/36     0     0/30     0     0/12     0     0/12     0     0/30     0     0/30     0
  bestever_48549100542c0ef6      0/36     2     0/30     2     0/12     2     0/12     2     0/30     2     0/30     2
  contemp_b396a264513d7c30       0/36     0     0/30     0     0/12     0     0/12     0     0/30     0     0/30     0
  contemp_6322334122999d20       0/36     0     0/30     0     0/12     0     0/12     0     0/30     0     0/30     0
  ancestor1_it0_587acbe8f559     0/36     0     0/30     0     0/12     0     0/12     0     0/30     0     0/30     0

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.27    49.53    36.27    36.27    49.53    49.53    49.53   5.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.56    49.55    49.56    49.56    49.55    49.55    49.55   2.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ENUMERATE_VM_C1               51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  RANDOM_C1                     49.64       --    49.64    49.64    49.64    49.64    49.64   0.0
  top1_00550ee99d42d8e0         50.01       --    50.01    50.01    50.01    50.01    50.01   0.0
  top2_00f3560aaeb060aa         50.01       --    50.01    50.01    50.01    50.01    50.01   0.0
  top3_01e345eaf323574b         50.01       --    50.01    50.01    50.01    50.01    50.01   0.0
  contemp_09c22a7bdfc8a52b      50.01       --    50.01    50.01    50.01    50.01    50.01   0.0
  ancestor31_it146_0f4b80283    50.01       --    50.01    50.01    50.01    50.01    50.01   0.0
  ancestor16_it53_15486ff9d6    50.01       --    50.01    50.01    50.01    50.01    50.01   0.0
  bestever_48549100542c0ef6     50.02    50.02    50.02    50.02    50.02    50.02    50.02   1.0
  contemp_b396a264513d7c30      50.04       --    50.04    50.04    50.04    50.04    50.04   0.0
  contemp_6322334122999d20      50.09       --    50.09    50.09    50.09    50.09    50.09   0.0
  ancestor1_it0_587acbe8f559    50.11       --    50.11    50.11    50.11    50.11    50.11   0.0

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
  top1_00550ee99d42d8e0
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1500.3, 1500.3, 1500.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.01, 50.01, 50.01] vs CODE_ONLY [50.01, 50.01, 50.01]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 0.163] SCR [0.163, 0.163, 0.163] RESET [0.163, 0.163, 0.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.01, 50.01, 50.01] vs ACC remainder [50.01, 50.01, 50.01]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.01, 50.01, 50.01]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.01, 50.01, 50.01] STORAGE_MATCHED [50.01, 50.01, 50.01] vs ACC remainder [50.01, 50.01, 50.01]
  top2_00f3560aaeb060aa
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1500.3, 1500.3, 1500.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.01, 50.01, 50.01] vs CODE_ONLY [50.01, 50.01, 50.01]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 0.163] SCR [0.163, 0.163, 0.163] RESET [0.163, 0.163, 0.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.01, 50.01, 50.01] vs ACC remainder [50.01, 50.01, 50.01]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.01, 50.01, 50.01]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.01, 50.01, 50.01] STORAGE_MATCHED [50.01, 50.01, 50.01] vs ACC remainder [50.01, 50.01, 50.01]
  top3_01e345eaf323574b
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1500.3, 1500.3, 1500.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.01, 50.01, 50.01] vs CODE_ONLY [50.01, 50.01, 50.01]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 0.163] SCR [0.163, 0.163, 0.163] RESET [0.163, 0.163, 0.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.01, 50.01, 50.01] vs ACC remainder [50.01, 50.01, 50.01]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.01, 50.01, 50.01]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.01, 50.01, 50.01] STORAGE_MATCHED [50.01, 50.01, 50.01] vs ACC remainder [50.01, 50.01, 50.01]
  contemp_09c22a7bdfc8a52b
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1500.3, 1500.3, 1500.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.01, 50.01, 50.01] vs CODE_ONLY [50.01, 50.01, 50.01]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 0.163] SCR [0.163, 0.163, 0.163] RESET [0.163, 0.163, 0.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.01, 50.01, 50.01] vs ACC remainder [50.01, 50.01, 50.01]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.01, 50.01, 50.01]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.01, 50.01, 50.01] STORAGE_MATCHED [50.01, 50.01, 50.01] vs ACC remainder [50.01, 50.01, 50.01]
  ancestor31_it146_0f4b8028315a91ed
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1500.3, 1500.3, 1500.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.01, 50.01, 50.01] vs CODE_ONLY [50.01, 50.01, 50.01]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 0.163] SCR [0.163, 0.163, 0.163] RESET [0.163, 0.163, 0.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.01, 50.01, 50.01] vs ACC remainder [50.01, 50.01, 50.01]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.01, 50.01, 50.01]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.01, 50.01, 50.01] STORAGE_MATCHED [50.01, 50.01, 50.01] vs ACC remainder [50.01, 50.01, 50.01]
  ancestor16_it53_15486ff9d61631ff
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1500.3, 1500.3, 1500.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.01, 50.01, 50.01] vs CODE_ONLY [50.01, 50.01, 50.01]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 0.163] SCR [0.163, 0.163, 0.163] RESET [0.163, 0.163, 0.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.01, 50.01, 50.01] vs ACC remainder [50.01, 50.01, 50.01]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.01, 50.01, 50.01]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.01, 50.01, 50.01] STORAGE_MATCHED [50.01, 50.01, 50.01] vs ACC remainder [50.01, 50.01, 50.01]
  bestever_48549100542c0ef6
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [1.2, 1.2, 1.2] vs 5% of FRESH cost [1501.8, 1501.8, 1501.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.02, 50.02, 50.02] vs CODE_ONLY [50.02, 50.02, 50.02]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 0.163] SCR [0.163, 0.163, 0.163] RESET [0.163, 0.163, 0.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.02, 50.02, 50.02] vs ACC remainder [50.02, 50.02, 50.02]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [50.02, 50.02, 50.02] vs ACC remainder [50.02, 50.02, 50.02]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.02, 50.02, 50.02] STORAGE_MATCHED [50.02, 50.02, 50.02] vs ACC remainder [50.02, 50.02, 50.02]
  contemp_b396a264513d7c30
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1501.2, 1501.2, 1501.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.04, 50.04, 50.04] vs CODE_ONLY [50.04, 50.04, 50.04]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 0.163] SCR [0.163, 0.163, 0.163] RESET [0.163, 0.163, 0.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.04, 50.04, 50.04] vs ACC remainder [50.04, 50.04, 50.04]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.04, 50.04, 50.04]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.04, 50.04, 50.04] STORAGE_MATCHED [50.04, 50.04, 50.04] vs ACC remainder [50.04, 50.04, 50.04]
  contemp_6322334122999d20
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1502.7, 1502.7, 1502.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.09, 50.09, 50.09] vs CODE_ONLY [50.09, 50.09, 50.09]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 0.163] SCR [0.163, 0.163, 0.163] RESET [0.163, 0.163, 0.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.09, 50.09, 50.09] vs ACC remainder [50.09, 50.09, 50.09]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.09, 50.09, 50.09]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.09, 50.09, 50.09] STORAGE_MATCHED [50.09, 50.09, 50.09] vs ACC remainder [50.09, 50.09, 50.09]
  ancestor1_it0_587acbe8f5596182
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1503.3, 1503.3, 1503.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.11, 50.11, 50.11] vs CODE_ONLY [50.11, 50.11, 50.11]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 0.163] SCR [0.163, 0.163, 0.163] RESET [0.163, 0.163, 0.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.11, 50.11, 50.11] vs ACC remainder [50.11, 50.11, 50.11]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.11, 50.11, 50.11]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.11, 50.11, 50.11] STORAGE_MATCHED [50.11, 50.11, 50.11] vs ACC remainder [50.11, 50.11, 50.11]

MACHINERY OF top1_00550ee99d42d8e0 (qualification seed 201, ACCUMULATED)
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

BASELINES ON SEARCH SUITE (crius/runs/baselines_c2d): effA effF effR effS  succA  interA interF  reuse_gain  blocks
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

