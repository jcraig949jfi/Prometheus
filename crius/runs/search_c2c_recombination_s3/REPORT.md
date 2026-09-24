CRIUS CAMPAIGN 0 REPORT  run=search_c2c_recombination_s3  arm=recombination
code_commit=cabe092b4 dirty=True config_hash=416bbe8b9be34706 world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  20.9038   19.9571         8.5032        40         19
    26  24.4250   24.4242        14.4231        47        119
    51  20.9557   19.3587        12.1873        56        217
    76  17.3528   17.3525         8.0053        47        314
   101  24.4147   24.4147        15.8894        42        402
   126  23.9064   23.0063        16.1046        38        500
   151  19.9158   19.9152        13.6386        42        602
   176  23.4677   23.0305        16.6438        48        697
   201  22.9500   22.9500        13.8308        44        788
   226  20.4041   19.9458        12.4864        46        865
   251  21.4374   21.4374        12.2851        41        945
   276  22.9392   20.2941        14.4643        48       1002
   300  22.4230   20.0355        13.2264        45       1070
  candidates evaluated: 7208   best_ever 29.4678 (4e2e38814d0af54e)  wall 1070s

BEST PROGRAM 4e2e38814d0af54e (len 38, iteration 122, modification delete@18+arg@15.0)
  search seed 3011220: fit 28.4556 succ 28/50 inter 5212 steps 24892 ws_cost 15 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [246.083, 1.0], "B": [150.9, 1.0], "C": [48.131, 0.333], "D": [49.471, 0.2], "E": [52.37, 0.25]}
  search seed 3011221: fit 30.4801 succ 30/50 inter 2305 steps 14649 ws_cost 15 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [79.183, 1.0], "B": [44.96, 1.0], "C": [38.111, 0.333], "D": [46.466, 0.2], "E": [36.028, 0.5]}
  listing:
      0  INPUT          R1, num_ops
      1  CONST          R5, 1
      2  BRZ            R3, 24
      3  BRNZ           R6, 13
      4  CONST          R0, 20
      5  MUL            R7, R4, R6
      6  HALT           
      7  MOV            R2, R1
      8  JMP            18
      9  BLK_APPEND     R1, R2
     10  BLK_PATCH      R6, R0, R0
     11  BRZ            R3, 35
     12  MUL            R2, R2, R1
     13  LT             R3, R0, R2
     14  ACT            R3
     15  LT             R6, R6, R2
     16  ADD            R0, R0, R5
     17  JMP            22
     18  BLK_INVOKE     R3
     19  WS_LINKS       R4, R3
     20  ACT            R1
     21  MUL            R7, R4, R6
     22  ACT            R3
     23  BRNZ           R6, 15
     24  CONST          R0, 20
     25  MUL            R2, R1, R1
     26  ACT            R1
     27  MOD            R3, R0, R1
     28  ACT            R3
     29  DIV            R4, R0, R1
     30  MOD            R3, R4, R1
     31  ACT            R3
     32  DIV            R4, R4, R1
     33  MOD            R3, R4, R1
     34  ACT            R3
     35  ADD            R0, R0, R5
     36  JMP            26
     37  HALT           
  ancestry (59 steps, newest first): iteration/fitness/modification
    it  122  29.4678  len 38  delete@18+arg@15.0
    it  121  21.4310  len 39  const@23+duplicate@22+2->3+delete@26
    it  120  20.4608  len 38  replace@18
    it  117  22.4182  len 38  const@24+delete@9
    it  112  22.4115  len 39  delete@22+delete@39+delete@11
    it  109  19.4363  len 42  swap@9,15
    it  105  19.8737  len 42  swap@24,19+swap@32,15+delete@11
    it  102  21.3761  len 43  delete@29
    it  101  24.4147  len 44  swap@22,27+splice@3<-donor[18:19]:5e052a4e52c52d32
    it   97  20.9149  len 43  swap@20,4
    it   96  21.4212  len 43  const@26
    it   94  21.9330  len 43  const@26
    it   91  23.4674  len 43  delete@30
    it   88  22.4127  len 44  arg@11.2+replace@19+delete@19
    it   84  20.4109  len 45  delete@30
    ... 45 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7315.4    5.3   74.7
  contemp_2b6265bfb7f6213c    22.087  22.087  22.087  22.087  21.7  21.7     9360     9360       7.1    1.0    0.0
  top3_1ab26511190ba2b4       20.749  20.749  20.749  20.749  20.3  20.3    10005    10005       7.1    1.0    0.0
  ancestor140_it298_6b418415  20.748  20.748  20.748  20.748  20.3  20.3    10044    10044       7.1    1.0    0.0
  contemp_52165ce9f26b999f    20.748  20.748  20.748  20.748  20.3  20.3    10044    10044       7.1    1.0    0.0
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.9    3.7    1.7
  bestever_4e2e38814d0af54e   20.411  20.411  20.411  20.411  20.0  20.0    10556    10556       7.1    1.0    0.0
  ancestor70_it140_f186280fd  20.077  20.077  20.077  20.077  19.7  19.7    10568    10568       7.1    1.0    0.0
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ancestor1_it0_0875253d162c  19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  top2_394179bed88c8d07       18.374  18.374  18.374  18.374  18.0  18.0    14944    14944       5.3    1.0    0.0
  top1_b0815fab4759654b       18.054  18.054  18.054  18.054  17.7  17.7    13306    13306       7.2    1.0    0.0
  contemp_83f7444a35299697    12.262  12.262  12.262  12.262  12.0  12.0    27447    27447       4.4    1.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.02/ 455.13   14.92/ 539.10   21.12/  47.94   33.22/  48.94   40.08/  50.52
  contemp_2b6265bfb7f6213c    446.53/ 446.66  376.19/ 376.33   49.84/  49.99   50.82/  50.97   51.81/  51.96
  top3_1ab26511190ba2b4       442.35/ 442.48  447.21/ 447.35   50.18/  50.33   50.40/  50.55   51.55/  51.70
  ancestor140_it298_6b418415  447.95/ 448.08  445.58/ 445.72   49.67/  49.81   50.82/  50.97   51.81/  51.96
  contemp_52165ce9f26b999f    447.97/ 448.10  445.60/ 445.74   49.69/  49.83   50.84/  50.99   51.83/  51.98
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.14/ 443.81  528.13/ 527.79   47.94/  47.89   48.86/  48.88   50.43/  50.46
  bestever_4e2e38814d0af54e   450.10/ 450.23  498.78/ 498.92   49.01/  49.16   50.87/  51.01   49.88/  50.03
  ancestor70_it140_f186280fd  450.17/ 450.30  499.19/ 499.33   48.52/  48.67   50.55/  50.70   51.87/  52.02
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ancestor1_it0_0875253d162c  495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  ENUMERATE_VM_C1             495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  top2_394179bed88c8d07       788.85/ 788.97  614.60/ 614.73   49.58/  49.68   49.71/  49.81   50.39/  50.49
  top1_b0815fab4759654b       513.99/ 514.12  716.31/ 716.45   50.41/  50.56   51.17/  51.32   51.43/  51.57
  contemp_83f7444a35299697   1473.68/1473.80 1293.75/1293.89   52.28/  52.34   52.93/  52.99   53.25/  53.31
  RANDOM_C1                  1662.62/1662.62 1627.07/1627.07   50.50/  50.50   50.50/  50.50   48.56/  48.56

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  contemp_2b6265bfb7f6213c       2/36    48     2/30    49     1/12    50     0/12    50    30/30   429    30/30   361
  top3_1ab26511190ba2b4          3/36    48     2/30    48     1/12    49     0/12    50    27/30   425    28/30   430
  ancestor140_it298_6b418415     3/36    48     2/30    49     1/12    50     0/12    50    27/30   430    28/30   428
  contemp_52165ce9f26b999f       3/36    48     2/30    49     1/12    50     0/12    50    27/30   430    28/30   428
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  bestever_4e2e38814d0af54e      3/36    47     1/30    49     1/12    46     0/12    50    27/30   432    28/30   479
  ancestor70_it140_f186280fd     3/36    47     1/30    49     0/12    50     0/12    50    27/30   432    28/30   480
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ancestor1_it0_0875253d162c     2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  top2_394179bed88c8d07          3/36    48     3/30    48     0/12    50     1/12    47    22/30   760    25/30   591
  top1_b0815fab4759654b          3/36    48     1/30    49     0/12    50     1/12    49    26/30   494    22/30   690
  contemp_83f7444a35299697       1/36    49     1/30    50     0/12    50     0/12    50    16/30  1383    18/30  1214
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.27    49.53    36.27    36.27    49.53    49.53    49.53   5.0
  contemp_2b6265bfb7f6213c      51.26    51.27    51.26    51.26    51.27    51.27    51.27   1.0
  top3_1ab26511190ba2b4         50.92    50.92    50.92    50.92    50.92    50.92    50.92   1.0
  ancestor140_it298_6b418415    51.26    51.27    51.26    51.26    51.27    51.27    51.27   1.0
  contemp_52165ce9f26b999f      51.28    51.29    51.28    51.28    51.29    51.29    51.29   1.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.56    49.55    49.56    49.56    49.55    49.55    49.55   2.0
  bestever_4e2e38814d0af54e     50.43    50.44    50.43    50.43    50.44    50.44    50.44   1.0
  ancestor70_it140_f186280fd    51.14    51.15    51.14    51.14    51.15    51.15    51.15   1.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ancestor1_it0_0875253d162c    51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  ENUMERATE_VM_C1               51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  top2_394179bed88c8d07         50.01    50.02    50.01    50.01    50.02    50.02    50.02   1.0
  top1_b0815fab4759654b         51.28    51.29    51.28    51.28    51.29    51.29    51.29   1.0
  contemp_83f7444a35299697      53.07    53.08    53.07    53.07    53.08    53.08    53.08   1.0
  RANDOM_C1                     49.64       --    49.64    49.64    49.64    49.64    49.64   0.0

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
  contemp_2b6265bfb7f6213c
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 22, 23] vs FRESH [20, 22, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.4] vs 5% of FRESH cost [1560.3, 1535.2, 1480.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.86, 51.8, 50.12] vs CODE_ONLY [51.87, 51.81, 50.13]
    4_scramble_or_reset_damages            0/3  eff ACC [20.397, 22.417, 23.448] SCR [20.397, 22.417, 23.448] RESET [20.397, 22.417, 23.448]
    5_transfers_to_fresh_copy              0/3  FULL [51.86, 51.8, 50.12] vs ACC remainder [51.86, 51.8, 50.12]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.87, 51.81, 50.13] vs ACC remainder [51.86, 51.8, 50.12]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.87, 51.81, 50.13] STORAGE_MATCHED [51.87, 51.81, 50.13] vs ACC remainder [51.86, 51.8, 50.12]
  top3_1ab26511190ba2b4
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 19, 23] vs FRESH [19, 19, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.4] vs 5% of FRESH cost [1547.8, 1522.8, 1498.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.86, 51.45, 49.43] vs CODE_ONLY [51.87, 51.46, 49.44]
    4_scramble_or_reset_damages            0/3  eff ACC [19.384, 19.416, 23.446] SCR [19.384, 19.416, 23.446] RESET [19.384, 19.416, 23.446]
    5_transfers_to_fresh_copy              0/3  FULL [51.86, 51.45, 49.43] vs ACC remainder [51.86, 51.45, 49.43]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.87, 51.46, 49.44] vs ACC remainder [51.86, 51.45, 49.43]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.87, 51.46, 49.44] STORAGE_MATCHED [51.87, 51.46, 49.44] vs ACC remainder [51.86, 51.45, 49.43]
  ancestor140_it298_6b418415528ef184
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 19, 23] vs FRESH [19, 19, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.4] vs 5% of FRESH cost [1554.0, 1535.2, 1480.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.86, 51.8, 50.12] vs CODE_ONLY [51.87, 51.81, 50.13]
    4_scramble_or_reset_damages            0/3  eff ACC [19.385, 19.415, 23.445] SCR [19.385, 19.415, 23.445] RESET [19.385, 19.415, 23.445]
    5_transfers_to_fresh_copy              0/3  FULL [51.86, 51.8, 50.12] vs ACC remainder [51.86, 51.8, 50.12]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.87, 51.81, 50.13] vs ACC remainder [51.86, 51.8, 50.12]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.87, 51.81, 50.13] STORAGE_MATCHED [51.87, 51.81, 50.13] vs ACC remainder [51.86, 51.8, 50.12]
  contemp_52165ce9f26b999f
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 19, 23] vs FRESH [19, 19, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.4] vs 5% of FRESH cost [1554.6, 1535.8, 1480.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.88, 51.82, 50.14] vs CODE_ONLY [51.89, 51.83, 50.15]
    4_scramble_or_reset_damages            0/3  eff ACC [19.385, 19.415, 23.445] SCR [19.385, 19.415, 23.445] RESET [19.385, 19.415, 23.445]
    5_transfers_to_fresh_copy              0/3  FULL [51.88, 51.82, 50.14] vs ACC remainder [51.88, 51.82, 50.14]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.89, 51.83, 50.15] vs ACC remainder [51.88, 51.82, 50.14]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.89, 51.83, 50.15] STORAGE_MATCHED [51.89, 51.83, 50.15] vs ACC remainder [51.88, 51.82, 50.14]
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
  bestever_4e2e38814d0af54e
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 19, 22] vs FRESH [19, 19, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.4, 4.3, 4.4] vs 5% of FRESH cost [1522.1, 1469.0, 1509.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.87, 49.22, 50.2] vs CODE_ONLY [51.88, 49.23, 50.2]
    4_scramble_or_reset_damages            0/3  eff ACC [19.379, 19.413, 22.44] SCR [19.379, 19.413, 22.44] RESET [19.379, 19.413, 22.44]
    5_transfers_to_fresh_copy              0/3  FULL [51.87, 49.22, 50.2] vs ACC remainder [51.87, 49.22, 50.2]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.88, 49.23, 50.2] vs ACC remainder [51.87, 49.22, 50.2]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.88, 49.23, 50.2] STORAGE_MATCHED [51.88, 49.23, 50.2] vs ACC remainder [51.87, 49.22, 50.2]
  ancestor70_it140_f186280fdf189981
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 18, 22] vs FRESH [19, 18, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.4, 4.4, 4.4] vs 5% of FRESH cost [1512.7, 1518.0, 1490.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.87, 51.87, 49.68] vs CODE_ONLY [51.88, 51.88, 49.69]
    4_scramble_or_reset_damages            0/3  eff ACC [19.378, 18.412, 22.442] SCR [19.378, 18.412, 22.442] RESET [19.378, 18.412, 22.442]
    5_transfers_to_fresh_copy              0/3  FULL [51.87, 51.87, 49.68] vs ACC remainder [51.87, 51.87, 49.68]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.88, 51.88, 49.69] vs ACC remainder [51.87, 51.87, 49.68]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.88, 51.88, 49.69] STORAGE_MATCHED [51.88, 51.88, 49.69] vs ACC remainder [51.87, 51.87, 49.68]
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
  top2_394179bed88c8d07
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [15, 18, 21] vs FRESH [15, 18, 21]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [3.0, 3.0, 3.0] vs 5% of FRESH cost [1523.4, 1494.3, 1476.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.89, 50.47, 49.67] vs CODE_ONLY [49.9, 50.48, 49.67]
    4_scramble_or_reset_damages            0/3  eff ACC [15.329, 18.368, 21.424] SCR [15.329, 18.368, 21.424] RESET [15.329, 18.368, 21.424]
    5_transfers_to_fresh_copy              0/3  FULL [49.89, 50.47, 49.67] vs ACC remainder [49.89, 50.47, 49.67]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [49.9, 50.48, 49.67] vs ACC remainder [49.89, 50.47, 49.67]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.9, 50.48, 49.67] STORAGE_MATCHED [49.9, 50.48, 49.67] vs ACC remainder [49.89, 50.47, 49.67]
  top1_b0815fab4759654b
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [16, 16, 21] vs FRESH [16, 16, 21]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.5] vs 5% of FRESH cost [1549.9, 1538.4, 1509.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.28, 51.86, 50.7] vs CODE_ONLY [51.29, 51.87, 50.71]
    4_scramble_or_reset_damages            0/3  eff ACC [16.369, 16.369, 21.425] SCR [16.369, 16.369, 21.425] RESET [16.369, 16.369, 21.425]
    5_transfers_to_fresh_copy              0/3  FULL [51.28, 51.86, 50.7] vs ACC remainder [51.28, 51.86, 50.7]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.29, 51.87, 50.71] vs ACC remainder [51.28, 51.86, 50.7]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.29, 51.87, 50.71] STORAGE_MATCHED [51.29, 51.87, 50.71] vs ACC remainder [51.28, 51.86, 50.7]
  contemp_83f7444a35299697
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [11, 11, 14] vs FRESH [11, 11, 14]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [1.8, 1.8, 1.8] vs 5% of FRESH cost [1599.3, 1564.2, 1589.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [53.25, 53.25, 52.72] vs CODE_ONLY [53.25, 53.25, 52.73]
    4_scramble_or_reset_damages            0/3  eff ACC [11.302, 11.23, 14.254] SCR [11.302, 11.23, 14.254] RESET [11.302, 11.23, 14.254]
    5_transfers_to_fresh_copy              0/3  FULL [53.25, 53.25, 52.72] vs ACC remainder [53.25, 53.25, 52.72]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [53.25, 53.25, 52.73] vs ACC remainder [53.25, 53.25, 52.72]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [53.25, 53.25, 52.73] STORAGE_MATCHED [53.25, 53.25, 52.73] vs ACC remainder [53.25, 53.25, 52.72]
  RANDOM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 6, 9] vs FRESH [6, 6, 9]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1493.8, 1515.0, 1489.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.32, 50.5, 49.1] vs CODE_ONLY [49.32, 50.5, 49.1]
    4_scramble_or_reset_damages            0/3  eff ACC [6.205, 6.235, 9.221] SCR [6.205, 6.235, 9.221] RESET [6.205, 6.235, 9.221]
    5_transfers_to_fresh_copy              0/3  FULL [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.32, 50.5, 49.1]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.32, 50.5, 49.1] STORAGE_MATCHED [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]

MACHINERY OF top1_b0815fab4759654b (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   1    32
    task  9:     0    0    0    0    0 |   1    32
    task 19:     0    0    0    0    0 |   1    32
    task 31:     0    0    0    0    0 |   1    32
    task 41:     0    0    0    0    0 |   1    32
    task 49:     0    0    0    0    0 |   1    32
  artifact events: 1 (create 1, delete 0, patch/append 0); invocations by block: {}; edges: 0
    block 0 origin=calibration len=0 state=[[2, 3, 6, 8, 10, 4, 9, 11, 5, 0, 7, 1], [9, 11, 0, 1, 5, 8, 2, 10, 3, 6, 4, 7], 0] instr=[]
  adaptation curve ACC:   35 1551 4 2073 27 35 13 590 60 91 147 4 2073 2073 35 2073 2073 4 1551 23 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 41 52 52 52 52 52 52 52
  adaptation curve FRESH: 35 1551 4 2074 27 35 14 590 60 91 147 4 2074 2074 35 2074 2074 4 1551 23 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 42 52 52 52 52 52 52 52
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

