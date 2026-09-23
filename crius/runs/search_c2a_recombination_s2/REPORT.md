CRIUS CAMPAIGN 0 REPORT  run=search_c2a_recombination_s2  arm=recombination
code_commit=6eb2d2ac7 dirty=True config_hash=401915ec4da9443a world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  22.9741   21.7862         9.0089        46         14
    26  21.4315   21.4310        16.9946        73        113
    51  20.4291   20.4290        15.6981        87        201
    76  23.4158   23.4158        15.9489        96        260
   101  18.3182   17.0042        15.0901        95        344
   126  23.9310   23.9310        20.4452        91        410
   151  21.9043   21.9043        17.0732        85        470
   176  20.4061   20.4052        18.5877        96        526
   201  21.8820   21.8820        15.0283        92        593
   226  20.3792   20.3790        15.4255        83        653
   251  23.4486   23.4486        19.2080        77        731
   276  23.4503   23.4503        19.7851        67        800
   300  21.9632   20.7063        15.9041        84        864
  candidates evaluated: 7208   best_ever 28.4795 (04712d1f8fd1e20b)  wall 864s

BEST PROGRAM 04712d1f8fd1e20b (len 88, iteration 106, modification replace@4+swap@3,67)
  search seed 2011060: fit 21.3939 succ 21/50 inter 12541 steps 50817 ws_cost 0 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [454.734, 1.0], "B": [697.316, 1.0], "C": [51.96, 0.0], "D": [51.96, 0.0], "E": [48.194, 0.125]}
  search seed 2011061: fit 17.4031 succ 17/50 inter 11457 steps 46045 ws_cost 0 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [406.331, 0.9], "B": [633.377, 0.7], "C": [51.96, 0.0], "D": [51.96, 0.0], "E": [47.156, 0.125]}
  listing:
      0  INPUT          R1, num_ops
      1  CONST          R5, 1
      2  BRZ            R3, 64
      3  BLK_COPY       R3, R6
      4  INPUT          R6, interactions_left
      5  MOD            R3, R0, R1
      6  WS_FREE        R7
      7  MUL            R2, R1, R1
      8  VSET           R6, R6, R5
      9  MOD            R3, R0, R1
     10  MOV            R2, R1
     11  ACT            R3
     12  BRZ            R3, 62
     13  ACT            R1
     14  BLK_APPEND     R6, R6
     15  JMP            63
     16  MUL            R2, R1, R1
     17  MOD            R3, R4, R1
     18  ADD            R0, R0, R5
     19  JMP            42
     20  INPUT          R1, num_ops
     21  MUL            R2, R1, R1
     22  BLK_INVOKE     R5
     23  WS_REC_SET     R1, R2, R3
     24  VSET           R6, R6, R5
     25  HALT           
     26  DIV            R1, R6, R3
     27  INPUT          R3, last_action
     28  ADD            R2, R2, R4
     29  CONST          R0, -3
     30  MUL            R2, R1, R1
     31  ADD            R0, R0, R7
     32  ADD            R2, R2, R4
     33  CONST          R0, -5
     34  MUL            R2, R1, R1
     35  VSET           R6, R6, R2
     36  BRZ            R7, 64
     37  DIV            R7, R1, R2
     38  WS_SREAD       R3, R5, R7
     39  JMP            74
     40  BLK_NEW        R5
     41  CONST          R0, 2
     42  ACT            R1
     43  BLK_COUNT      R7
     44  JMP            41
     45  MUL            R2, R1, R1
     46  ACT            R3
     47  MUL            R2, R1, R1
     48  LT             R3, R7, R2
     49  ADD            R0, R0, R5
     50  LT             R3, R7, R2
     51  ADD            R0, R0, R5
     52  VSET           R6, R6, R5
     53  JMP            62
     54  ACT            R0
     55  ACT            R0
     56  ADD            R0, R0, R5
     57  EQ             R2, R7, R7
     58  WS_SREAD       R4, R3, R1
     59  ACT            R3
     60  ACTI           -19
     61  MUL            R2, R1, R1
     62  MUL            R2, R1, R1
     63  ACT            R1
     64  CONST          R0, 0
     65  CONST          R0, -7
     66  MOD            R3, R4, R1
     67  ACT            R1
     68  DIV            R4, R0, R1
     69  CONST          R0, 7
     70  MUL            R2, R1, R1
     71  MOD            R3, R4, R1
     72  ADD            R0, R0, R5
     73  VSET           R6, R6, R5
     74  MUL            R2, R2, R1
     75  ACT            R1
     76  MOD            R3, R0, R1
     77  ACT            R3
     78  DIV            R4, R0, R1
     79  MOD            R3, R4, R1
     80  ACT            R3
     81  DIV            R4, R4, R1
     82  MOD            R3, R4, R1
     83  ACT            R4
     84  ADD            R0, R0, R5
     85  JMP            75
     86  ACT            R3
     87  WS_SLEN        R1, R6
  ancestry (67 steps, newest first): iteration/fitness/modification
    it  106  19.3985  len 88  replace@4+swap@3,67
    it  105  22.9700  len 88  replace@36
    it  104  21.4453  len 88  delete@2
    it  103  23.4441  len 89  swap@7,43+delete@29
    it  101  16.8165  len 90  swap@15,14
    it  100  21.9256  len 90  delete@49+insert@59
    it   99  21.4163  len 90  delete@53
    it   98  21.9500  len 91  delete@17
    it   97  19.3915  len 92  const@69+delete@44
    it   96  22.9269  len 93  delete@40
    it   92  17.8678  len 94  arg@31.1+delete@75+delete@24
    it   91  20.9303  len 96  replace@26+splice:none:76061e4e198f6aba
    it   90  21.9197  len 96  insert@14
    it   89  18.3734  len 95  const@2+duplicate@17+3->76+duplicate@8+1->50
    it   88  23.4555  len 91  const@69
    ... 53 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7316.0    4.3   74.7
  ancestor171_it298_d0e9e7d6  21.746  21.746  21.746  21.746  21.3  21.3    10350    10350       0.0    0.0    0.0
  contemp_fce8533943a57059    21.745  21.745  21.745  21.745  21.3  21.3    10350    10350       0.0    0.0    0.0
  top3_09b7fbc9d4ac79d5       21.414  21.414  21.414  21.414  21.0  21.0    10148    10148       0.0    0.0    0.0
  contemp_2282b9c1660c396b    21.414  21.414  21.414  21.414  21.0  21.0    10148    10148       0.0    0.0    0.0
  ancestor86_it140_047ad1b62  20.751  20.751  20.751  20.751  20.3  20.3     9810     9810       0.0    0.0    0.0
  bestever_04712d1f8fd1e20b   20.749  20.749  20.749  20.749  20.3  20.3     9944     9944       0.0    0.0    0.0
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.3    2.7    1.7
  top1_1e77e4c386f01d87       20.076  20.076  20.076  20.076  19.7  19.7    10809    10809       0.0    0.0    0.0
  top2_fa03a52a8475fc33       19.746  19.746  19.746  19.746  19.3  19.3    10223    10223       0.0    0.0    0.0
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ancestor1_it0_0875253d162c  19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       0.0    0.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       0.0    0.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0
  contemp_477121bdae127607     0.485   0.485   0.485   0.485   0.3   0.3    41484    41484       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.00/ 455.13   14.90/ 539.10   21.11/  47.94   33.21/  48.94   40.07/  50.52
  ancestor171_it298_d0e9e7d6  463.86/ 463.86  462.03/ 462.03   47.62/  47.62   49.83/  49.83   51.55/  51.55
  contemp_fce8533943a57059    468.67/ 468.67  466.84/ 466.84   48.11/  48.11   50.33/  50.33   52.06/  52.06
  top3_09b7fbc9d4ac79d5       452.29/ 452.29  450.70/ 450.70   49.60/  49.60   49.80/  49.80   51.04/  51.04
  contemp_2282b9c1660c396b    452.29/ 452.29  450.70/ 450.70   49.60/  49.60   49.80/  49.80   51.04/  51.04
  ancestor86_it140_047ad1b62  434.84/ 434.84  434.29/ 434.29   49.08/  49.08   49.50/  49.50   50.96/  50.96
  bestever_04712d1f8fd1e20b   439.64/ 439.64  444.41/ 444.41   50.02/  50.02   50.30/  50.30   51.52/  51.52
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.13/ 443.81  528.11/ 527.79   47.93/  47.89   48.85/  48.88   50.42/  50.46
  top1_1e77e4c386f01d87       470.50/ 470.50  499.02/ 499.02   50.11/  50.11   50.10/  50.10   51.72/  51.72
  top2_fa03a52a8475fc33       458.66/ 458.66  460.31/ 460.31   49.91/  49.91   50.72/  50.72   52.21/  52.21
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ancestor1_it0_0875253d162c  495.80/ 495.80  525.01/ 525.01   50.10/  50.10   51.09/  51.09   52.68/  52.68
  ENUMERATE_VM_C1             495.80/ 495.80  525.01/ 525.01   50.10/  50.10   51.09/  51.09   52.68/  52.68
  RANDOM_C1                  1662.62/1662.62 1627.07/1627.07   50.50/  50.50   50.50/  50.50   48.56/  48.56
  contemp_477121bdae127607   2066.75/2066.75 2066.75/2066.75   51.75/  51.75   50.13/  50.13   51.75/  51.75

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  ancestor171_it298_d0e9e7d6     4/36    46     2/30    48     1/12    50     0/12    50    28/30   447    29/30   445
  contemp_fce8533943a57059       4/36    46     2/30    48     1/12    50     0/12    50    28/30   447    29/30   445
  top3_09b7fbc9d4ac79d5          3/36    48     2/30    48     1/12    48     0/12    50    28/30   436    29/30   434
  contemp_2282b9c1660c396b       3/36    48     2/30    48     1/12    48     0/12    50    28/30   436    29/30   434
  ancestor86_it140_047ad1b62     3/36    47     2/30    48     1/12    48     0/12    50    27/30   419    28/30   418
  bestever_04712d1f8fd1e20b      3/36    48     2/30    48     1/12    49     0/12    50    27/30   422    28/30   427
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  top1_1e77e4c386f01d87          3/36    48     1/30    48     0/12    50     0/12    50    27/30   454    28/30   481
  top2_fa03a52a8475fc33          2/36    48     1/30    48     0/12    50     0/12    50    27/30   438    28/30   439
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ancestor1_it0_0875253d162c     2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610
  contemp_477121bdae127607       0/36    50     1/30    48     0/12    50     0/12    50     0/30  2000     0/30  2000

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.26    49.53    36.26    36.26    49.53    49.53    49.53   4.0
  ancestor171_it298_d0e9e7d6    50.60       --    50.60    50.60    50.60    50.60    50.60   0.0
  contemp_fce8533943a57059      51.10       --    51.10    51.10    51.10    51.10    51.10   0.0
  top3_09b7fbc9d4ac79d5         50.35       --    50.35    50.35    50.35    50.35    50.35   0.0
  contemp_2282b9c1660c396b      50.35       --    50.35    50.35    50.35    50.35    50.35   0.0
  ancestor86_it140_047ad1b62    50.15       --    50.15    50.15    50.15    50.15    50.15   0.0
  bestever_04712d1f8fd1e20b     50.84       --    50.84    50.84    50.84    50.84    50.84   0.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.55    49.55    49.55    49.55    49.55    49.55    49.55   1.0
  top1_1e77e4c386f01d87         50.82       --    50.82    50.82    50.82    50.82    50.82   0.0
  top2_fa03a52a8475fc33         51.38       --    51.38    51.38    51.38    51.38    51.38   0.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ancestor1_it0_0875253d162c    51.80       --    51.80    51.80    51.80    51.80    51.80   0.0
  ENUMERATE_VM_C1               51.80       --    51.80    51.80    51.80    51.80    51.80   0.0
  RANDOM_C1                     49.64       --    49.64    49.64    49.64    49.64    49.64   0.0
  contemp_477121bdae127607      50.85       --    50.85    50.85    50.85    50.85    50.85   0.0

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
  ancestor171_it298_d0e9e7d69325ca32
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 20, 25] vs FRESH [19, 20, 25]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1547.7, 1531.2, 1367.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.5, 51.73, 48.56] vs CODE_ONLY [51.5, 51.73, 48.56]
    4_scramble_or_reset_damages            0/3  eff ACC [19.386, 20.42, 25.432] SCR [19.386, 20.42, 25.432] RESET [19.386, 20.42, 25.432]
    5_transfers_to_fresh_copy              0/3  FULL [51.5, 51.73, 48.56] vs ACC remainder [51.5, 51.73, 48.56]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.5, 51.73, 48.56]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.5, 51.73, 48.56] STORAGE_MATCHED [51.5, 51.73, 48.56] vs ACC remainder [51.5, 51.73, 48.56]
  contemp_fce8533943a57059
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 20, 25] vs FRESH [19, 20, 25]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1562.7, 1546.0, 1382.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.0, 52.22, 49.06] vs CODE_ONLY [52.0, 52.22, 49.06]
    4_scramble_or_reset_damages            0/3  eff ACC [19.385, 20.419, 25.432] SCR [19.385, 20.419, 25.432] RESET [19.385, 20.419, 25.432]
    5_transfers_to_fresh_copy              0/3  FULL [52.0, 52.22, 49.06] vs ACC remainder [52.0, 52.22, 49.06]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.0, 52.22, 49.06]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.0, 52.22, 49.06] STORAGE_MATCHED [52.0, 52.22, 49.06] vs ACC remainder [52.0, 52.22, 49.06]
  top3_09b7fbc9d4ac79d5
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 20, 23] vs FRESH [20, 20, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1525.9, 1518.8, 1459.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.81, 51.73, 48.51] vs CODE_ONLY [50.81, 51.73, 48.51]
    4_scramble_or_reset_damages            0/3  eff ACC [20.388, 20.422, 23.434] SCR [20.388, 20.422, 23.434] RESET [20.388, 20.422, 23.434]
    5_transfers_to_fresh_copy              0/3  FULL [50.81, 51.73, 48.51] vs ACC remainder [50.81, 51.73, 48.51]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.81, 51.73, 48.51]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.81, 51.73, 48.51] STORAGE_MATCHED [50.81, 51.73, 48.51] vs ACC remainder [50.81, 51.73, 48.51]
  contemp_2282b9c1660c396b
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 20, 23] vs FRESH [20, 20, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1525.9, 1518.8, 1459.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.81, 51.73, 48.51] vs CODE_ONLY [50.81, 51.73, 48.51]
    4_scramble_or_reset_damages            0/3  eff ACC [20.388, 20.422, 23.434] SCR [20.388, 20.422, 23.434] RESET [20.388, 20.422, 23.434]
    5_transfers_to_fresh_copy              0/3  FULL [50.81, 51.73, 48.51] vs ACC remainder [50.81, 51.73, 48.51]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.81, 51.73, 48.51]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.81, 51.73, 48.51] STORAGE_MATCHED [50.81, 51.73, 48.51] vs ACC remainder [50.81, 51.73, 48.51]
  ancestor86_it140_047ad1b6280a8b8f
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 19, 23] vs FRESH [19, 19, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1528.5, 1491.3, 1455.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.78, 50.69, 47.98] vs CODE_ONLY [51.78, 50.69, 47.98]
    4_scramble_or_reset_damages            0/3  eff ACC [19.385, 19.418, 23.449] SCR [19.385, 19.418, 23.449] RESET [19.385, 19.418, 23.449]
    5_transfers_to_fresh_copy              0/3  FULL [51.78, 50.69, 47.98] vs ACC remainder [51.78, 50.69, 47.98]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.78, 50.69, 47.98]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.78, 50.69, 47.98] STORAGE_MATCHED [51.78, 50.69, 47.98] vs ACC remainder [51.78, 50.69, 47.98]
  bestever_04712d1f8fd1e20b
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 19, 23] vs FRESH [19, 19, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1543.2, 1515.1, 1488.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.96, 51.38, 49.19] vs CODE_ONLY [51.96, 51.38, 49.19]
    4_scramble_or_reset_damages            0/3  eff ACC [19.385, 19.416, 23.447] SCR [19.385, 19.416, 23.447] RESET [19.385, 19.416, 23.447]
    5_transfers_to_fresh_copy              0/3  FULL [51.96, 51.38, 49.19] vs ACC remainder [51.96, 51.38, 49.19]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.96, 51.38, 49.19]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.96, 51.38, 49.19] STORAGE_MATCHED [51.96, 51.38, 49.19] vs ACC remainder [51.96, 51.38, 49.19]
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
  top1_1e77e4c386f01d87
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 18, 23] vs FRESH [18, 18, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1551.6, 1537.1, 1459.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.72, 51.72, 49.02] vs CODE_ONLY [51.72, 51.72, 49.02]
    4_scramble_or_reset_damages            0/3  eff ACC [18.379, 18.411, 23.436] SCR [18.379, 18.411, 23.436] RESET [18.379, 18.411, 23.436]
    5_transfers_to_fresh_copy              0/3  FULL [51.72, 51.72, 49.02] vs ACC remainder [51.72, 51.72, 49.02]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.72, 51.72, 49.02]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.72, 51.72, 49.02] STORAGE_MATCHED [51.72, 51.72, 49.02] vs ACC remainder [51.72, 51.72, 49.02]
  top2_fa03a52a8475fc33
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 18, 22] vs FRESH [18, 18, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1566.3, 1518.6, 1486.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.21, 52.21, 49.73] vs CODE_ONLY [52.21, 52.21, 49.73]
    4_scramble_or_reset_damages            0/3  eff ACC [18.383, 18.413, 22.443] SCR [18.383, 18.413, 22.443] RESET [18.383, 18.413, 22.443]
    5_transfers_to_fresh_copy              0/3  FULL [52.21, 52.21, 49.73] vs ACC remainder [52.21, 52.21, 49.73]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.21, 52.21, 49.73]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.21, 52.21, 49.73] STORAGE_MATCHED [52.21, 52.21, 49.73] vs ACC remainder [52.21, 52.21, 49.73]
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
  contemp_477121bdae127607
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 1] vs FRESH [0, 0, 1]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1552.5, 1552.5, 1503.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.75, 51.75, 49.05] vs CODE_ONLY [51.75, 51.75, 49.05]
    4_scramble_or_reset_damages            0/3  eff ACC [0.151, 0.151, 1.152] SCR [0.151, 0.151, 1.152] RESET [0.151, 0.151, 1.152]
    5_transfers_to_fresh_copy              0/3  FULL [51.75, 51.75, 49.05] vs ACC remainder [51.75, 51.75, 49.05]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.75, 51.75, 49.05]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.75, 51.75, 49.05] STORAGE_MATCHED [51.75, 51.75, 49.05] vs ACC remainder [51.75, 51.75, 49.05]

MACHINERY OF top1_1e77e4c386f01d87 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   0     0
    task  9:     0    0    0    0    0 |   0     0
    task 19:     0    0    0    0    0 |   0     0
    task 31:     0    0    0    0    0 |   0     0
    task 41:     0    0    0    0    0 |   0     0
    task 49:     0    0    0    0    0 |   0     0
  artifact events: 0 (create 0, delete 0, patch/append 0); invocations by block: {}; edges: 0
  adaptation curve ACC:   188 2067 107 941 76 151 98 1670 144 199 261 333 941 941 39 1437 1437 70 2067 110 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
  adaptation curve FRESH: 188 2067 107 941 76 151 98 1670 144 199 261 333 941 941 39 1437 1437 70 2067 110 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
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

