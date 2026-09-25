CRIUS CAMPAIGN 0 REPORT  run=search_c2c_recombination_s1  arm=recombination
code_commit=cabe092b4 dirty=True config_hash=416bbe8b9be34706 world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  21.9592   20.9509        11.5015        39         20
    26  21.4401   21.4400        10.8665        50        125
    51  25.9525   24.6392        14.4089        44        238
    76  20.4108   20.4108        13.7148        58        366
   101  24.9525   24.9524        18.0439        72        510
   126  24.4443   24.4443        14.4154        79        639
   151  25.4111   24.9561        13.8726        88        755
   176  21.9156   21.9149        16.5947        87        873
   201  24.4578   24.4533        18.3296        81        992
   226  27.4677   27.4403        25.0132        78       1097
   251  19.3845   19.3845        16.7007        82       1200
   276  18.8971   18.8971        15.7964        83       1301
   300  21.9386   21.9386        15.9365        84       1380
  candidates evaluated: 7208   best_ever 28.4067 (599ad727908c3235)  wall 1380s

BEST PROGRAM 599ad727908c3235 (len 53, iteration 10, modification swap@22,15)
  search seed 1010100: fit 30.4534 succ 30/50 inter 5425 steps 30189 ws_cost 65 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [206.643, 1.0], "B": [236.058, 1.0], "C": [38.449, 0.5], "D": [44.782, 0.3], "E": [48.915, 0.125]}
  search seed 1010101: fit 26.3599 succ 26/50 inter 16457 steps 77185 ws_cost 65 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [771.085, 1.0], "B": [813.129, 0.9], "C": [37.924, 0.5], "D": [52.32, 0.0], "E": [51.134, 0.125]}
  listing:
      0  INPUT          R1, num_ops
      1  CONST          R5, 1
      2  CONST          R0, 0
      3  BLK_APPEND     R7, R3
      4  BRZ            R3, 11
      5  ADD            R0, R0, R5
      6  JMP            28
      7  ACT            R1
      8  ACT            R0
      9  ADD            R0, R0, R5
     10  JMP            3
     11  CONST          R0, 1
     12  MUL            R2, R1, R1
     13  LT             R3, R0, R2
     14  MOD            R3, R0, R1
     15  INPUT          R1, num_ops
     16  MOD            R3, R4, R1
     17  ACT            R3
     18  ADD            R0, R0, R5
     19  JMP            35
     20  DIV            R4, R0, R1
     21  MOD            R3, R4, R1
     22  ACT            R3
     23  CONST          R5, 1
     24  BRZ            R3, 34
     25  BLK_STATE_GET  R5, R7, R7
     26  ACT            R1
     27  MOD            R3, R0, R1
     28  ACT            R3
     29  DIV            R4, R0, R1
     30  MOD            R3, R4, R1
     31  VLEN           R3, R0
     32  MOV            R5, R0
     33  JMP            13
     34  CONST          R0, 0
     35  MUL            R2, R2, R1
     36  LT             R3, R0, R2
     37  MUL            R2, R1, R1
     38  MUL            R2, R2, R1
     39  LT             R3, R0, R2
     40  BRZ            R3, 52
     41  ACT            R1
     42  MOD            R3, R0, R1
     43  ACT            R3
     44  DIV            R4, R0, R1
     45  MOD            R3, R4, R1
     46  ACT            R3
     47  DIV            R4, R4, R1
     48  MOD            R3, R4, R1
     49  ACT            R3
     50  ADD            R0, R0, R5
     51  JMP            39
     52  HALT           
  ancestry (6 steps, newest first): iteration/fitness/modification
    it   10  28.4067  len 53  swap@22,15
    it    8  20.8788  len 53  replace@3+duplicate@0+2->22+replace@31
    it    6  16.3227  len 51  duplicate@41+4->16+replace@29+insert@23
    it    3  21.9009  len 46  arg@6.0+const@11
    it    2  20.9443  len 46  delete@3+duplicate@23+2->5
    it    1  21.4565  len 45  duplicate@24+2->23+splice@13<-donor[27:31]:5cd41b9c6d1da0a9
    it    0  17.8392  len 39  seed:ENUMERATE_VM

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7315.4    5.3   74.7
  top1_0fcce4e9606f75c4       22.098  22.098  22.098  22.098  21.7  21.7     8064     8064       7.2    1.0    0.0
  top2_6f6cb7e8ca983ef7       22.098  22.098  22.098  22.098  21.7  21.7     8064     8064       7.2    1.0    0.0
  top3_877967bc5f9375df       22.098  22.098  22.098  22.098  21.7  21.7     8064     8064       7.2    1.0    0.0
  contemp_e6ed56080dd74526    22.098  22.098  22.098  22.098  21.7  21.7     8064     8064       7.2    1.0    0.0
  contemp_2428c9f255988738    22.098  22.098  22.098  22.098  21.7  21.7     8064     8064       7.2    1.0    0.0
  contemp_efb19fa45d60bcf5    22.098  22.098  22.098  22.098  21.7  21.7     8064     8064       7.2    1.0    0.0
  ancestor136_it297_623371b0  22.098  22.098  22.098  22.098  21.7  21.7     8064     8064       7.2    1.0    0.0
  ancestor68_it165_1a8c356a7  22.091  22.091  22.091  22.091  21.7  21.7     8925     8925       7.2    1.0    0.0
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.9    3.7    1.7
  bestever_599ad727908c3235   20.080  20.080  20.080  20.080  19.7  19.7    10224    10224       7.2    1.0    0.0
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ancestor1_it0_0875253d162c  19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.02/ 455.13   14.92/ 539.10   21.12/  47.94   33.22/  48.94   40.08/  50.52
  top1_0fcce4e9606f75c4       317.15/ 317.27  372.00/ 372.15   49.86/  50.01   50.36/  50.50   51.49/  51.64
  top2_6f6cb7e8ca983ef7       317.15/ 317.27  372.00/ 372.15   49.86/  50.01   50.36/  50.50   51.49/  51.64
  top3_877967bc5f9375df       317.15/ 317.27  372.00/ 372.15   49.86/  50.01   50.36/  50.50   51.49/  51.64
  contemp_e6ed56080dd74526    317.15/ 317.27  372.00/ 372.15   49.86/  50.01   50.36/  50.50   51.49/  51.64
  contemp_2428c9f255988738    317.15/ 317.27  372.00/ 372.15   49.86/  50.01   50.36/  50.50   51.49/  51.64
  contemp_efb19fa45d60bcf5    317.15/ 317.27  372.00/ 372.15   49.86/  50.01   50.36/  50.50   51.49/  51.64
  ancestor136_it297_623371b0  317.15/ 317.27  372.00/ 372.15   49.86/  50.01   50.36/  50.50   51.49/  51.64
  ancestor68_it165_1a8c356a7  368.52/ 368.65  409.55/ 409.70   50.52/  50.67   50.45/  50.60   52.08/  52.23
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.14/ 443.81  528.13/ 527.79   47.94/  47.89   48.86/  48.88   50.43/  50.46
  bestever_599ad727908c3235   459.52/ 459.65  458.29/ 458.43   50.87/  51.01   50.71/  50.86   52.32/  52.47
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ancestor1_it0_0875253d162c  495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  ENUMERATE_VM_C1             495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  RANDOM_C1                  1662.62/1662.62 1627.07/1627.07   50.50/  50.50   50.50/  50.50   48.56/  48.56

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  top1_0fcce4e9606f75c4          3/36    48     1/30    48     0/12    50     1/12    49    30/30   304    30/30   357
  top2_6f6cb7e8ca983ef7          3/36    48     1/30    48     0/12    50     1/12    49    30/30   304    30/30   357
  top3_877967bc5f9375df          3/36    48     1/30    48     0/12    50     1/12    49    30/30   304    30/30   357
  contemp_e6ed56080dd74526       3/36    48     1/30    48     0/12    50     1/12    49    30/30   304    30/30   357
  contemp_2428c9f255988738       3/36    48     1/30    48     0/12    50     1/12    49    30/30   304    30/30   357
  contemp_efb19fa45d60bcf5       3/36    48     1/30    48     0/12    50     1/12    49    30/30   304    30/30   357
  ancestor136_it297_623371b0     3/36    48     1/30    48     0/12    50     1/12    49    30/30   304    30/30   357
  ancestor68_it165_1a8c356a7     4/36    48     1/30    48     0/12    50     0/12    50    30/30   353    30/30   393
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  bestever_599ad727908c3235      2/36    48     2/30    48     0/12    50     0/12    50    27/30   439    28/30   437
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ancestor1_it0_0875253d162c     2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.27    49.53    36.27    36.27    49.53    49.53    49.53   5.0
  top1_0fcce4e9606f75c4         50.86    50.87    50.86    50.86    50.87    50.87    50.87   1.0
  top2_6f6cb7e8ca983ef7         50.86    50.87    50.86    50.86    50.87    50.87    50.87   1.0
  top3_877967bc5f9375df         50.86    50.87    50.86    50.86    50.87    50.87    50.87   1.0
  contemp_e6ed56080dd74526      50.86    50.87    50.86    50.86    50.87    50.87    50.87   1.0
  contemp_2428c9f255988738      50.86    50.87    50.86    50.86    50.87    50.87    50.87   1.0
  contemp_efb19fa45d60bcf5      50.86    50.87    50.86    50.86    50.87    50.87    50.87   1.0
  ancestor136_it297_623371b0    50.86    50.87    50.86    50.86    50.87    50.87    50.87   1.0
  ancestor68_it165_1a8c356a7    51.18    51.18    51.18    51.18    51.18    51.18    51.18   1.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.56    49.55    49.56    49.56    49.55    49.55    49.55   2.0
  bestever_599ad727908c3235     51.43    51.44    51.43    51.43    51.44    51.44    51.44   1.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ancestor1_it0_0875253d162c    51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  ENUMERATE_VM_C1               51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
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
  top1_0fcce4e9606f75c4
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [22, 21, 22] vs FRESH [22, 21, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.4] vs 5% of FRESH cost [1520.3, 1555.6, 1478.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.36, 51.88, 49.34] vs CODE_ONLY [51.37, 51.89, 49.35]
    4_scramble_or_reset_damages            0/3  eff ACC [22.434, 21.41, 22.451] SCR [22.434, 21.41, 22.451] RESET [22.434, 21.41, 22.451]
    5_transfers_to_fresh_copy              0/3  FULL [51.36, 51.88, 49.34] vs ACC remainder [51.36, 51.88, 49.34]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.37, 51.89, 49.35] vs ACC remainder [51.36, 51.88, 49.34]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.37, 51.89, 49.35] STORAGE_MATCHED [51.37, 51.89, 49.35] vs ACC remainder [51.36, 51.88, 49.34]
  top2_6f6cb7e8ca983ef7
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [22, 21, 22] vs FRESH [22, 21, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.4] vs 5% of FRESH cost [1520.3, 1555.6, 1478.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.36, 51.88, 49.34] vs CODE_ONLY [51.37, 51.89, 49.35]
    4_scramble_or_reset_damages            0/3  eff ACC [22.434, 21.41, 22.451] SCR [22.434, 21.41, 22.451] RESET [22.434, 21.41, 22.451]
    5_transfers_to_fresh_copy              0/3  FULL [51.36, 51.88, 49.34] vs ACC remainder [51.36, 51.88, 49.34]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.37, 51.89, 49.35] vs ACC remainder [51.36, 51.88, 49.34]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.37, 51.89, 49.35] STORAGE_MATCHED [51.37, 51.89, 49.35] vs ACC remainder [51.36, 51.88, 49.34]
  top3_877967bc5f9375df
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [22, 21, 22] vs FRESH [22, 21, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.4] vs 5% of FRESH cost [1520.3, 1555.6, 1478.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.36, 51.88, 49.34] vs CODE_ONLY [51.37, 51.89, 49.35]
    4_scramble_or_reset_damages            0/3  eff ACC [22.434, 21.41, 22.451] SCR [22.434, 21.41, 22.451] RESET [22.434, 21.41, 22.451]
    5_transfers_to_fresh_copy              0/3  FULL [51.36, 51.88, 49.34] vs ACC remainder [51.36, 51.88, 49.34]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.37, 51.89, 49.35] vs ACC remainder [51.36, 51.88, 49.34]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.37, 51.89, 49.35] STORAGE_MATCHED [51.37, 51.89, 49.35] vs ACC remainder [51.36, 51.88, 49.34]
  contemp_e6ed56080dd74526
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [22, 21, 22] vs FRESH [22, 21, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.4] vs 5% of FRESH cost [1520.3, 1555.6, 1478.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.36, 51.88, 49.34] vs CODE_ONLY [51.37, 51.89, 49.35]
    4_scramble_or_reset_damages            0/3  eff ACC [22.434, 21.41, 22.451] SCR [22.434, 21.41, 22.451] RESET [22.434, 21.41, 22.451]
    5_transfers_to_fresh_copy              0/3  FULL [51.36, 51.88, 49.34] vs ACC remainder [51.36, 51.88, 49.34]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.37, 51.89, 49.35] vs ACC remainder [51.36, 51.88, 49.34]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.37, 51.89, 49.35] STORAGE_MATCHED [51.37, 51.89, 49.35] vs ACC remainder [51.36, 51.88, 49.34]
  contemp_2428c9f255988738
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [22, 21, 22] vs FRESH [22, 21, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.4] vs 5% of FRESH cost [1520.3, 1555.6, 1478.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.36, 51.88, 49.34] vs CODE_ONLY [51.37, 51.89, 49.35]
    4_scramble_or_reset_damages            0/3  eff ACC [22.434, 21.41, 22.451] SCR [22.434, 21.41, 22.451] RESET [22.434, 21.41, 22.451]
    5_transfers_to_fresh_copy              0/3  FULL [51.36, 51.88, 49.34] vs ACC remainder [51.36, 51.88, 49.34]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.37, 51.89, 49.35] vs ACC remainder [51.36, 51.88, 49.34]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.37, 51.89, 49.35] STORAGE_MATCHED [51.37, 51.89, 49.35] vs ACC remainder [51.36, 51.88, 49.34]
  contemp_efb19fa45d60bcf5
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [22, 21, 22] vs FRESH [22, 21, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.4] vs 5% of FRESH cost [1520.3, 1555.6, 1478.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.36, 51.88, 49.34] vs CODE_ONLY [51.37, 51.89, 49.35]
    4_scramble_or_reset_damages            0/3  eff ACC [22.434, 21.41, 22.451] SCR [22.434, 21.41, 22.451] RESET [22.434, 21.41, 22.451]
    5_transfers_to_fresh_copy              0/3  FULL [51.36, 51.88, 49.34] vs ACC remainder [51.36, 51.88, 49.34]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.37, 51.89, 49.35] vs ACC remainder [51.36, 51.88, 49.34]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.37, 51.89, 49.35] STORAGE_MATCHED [51.37, 51.89, 49.35] vs ACC remainder [51.36, 51.88, 49.34]
  ancestor136_it297_623371b0560f0f1a
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [22, 21, 22] vs FRESH [22, 21, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.4] vs 5% of FRESH cost [1520.3, 1555.6, 1478.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.36, 51.88, 49.34] vs CODE_ONLY [51.37, 51.89, 49.35]
    4_scramble_or_reset_damages            0/3  eff ACC [22.434, 21.41, 22.451] SCR [22.434, 21.41, 22.451] RESET [22.434, 21.41, 22.451]
    5_transfers_to_fresh_copy              0/3  FULL [51.36, 51.88, 49.34] vs ACC remainder [51.36, 51.88, 49.34]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.37, 51.89, 49.35] vs ACC remainder [51.36, 51.88, 49.34]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.37, 51.89, 49.35] STORAGE_MATCHED [51.37, 51.89, 49.35] vs ACC remainder [51.36, 51.88, 49.34]
  ancestor68_it165_1a8c356a79d1feb2
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 23, 22] vs FRESH [20, 23, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.3] vs 5% of FRESH cost [1566.9, 1549.1, 1479.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.08, 52.08, 49.37] vs CODE_ONLY [52.09, 52.09, 49.38]
    4_scramble_or_reset_damages            0/3  eff ACC [20.441, 23.396, 22.436] SCR [20.441, 23.396, 22.436] RESET [20.441, 23.396, 22.436]
    5_transfers_to_fresh_copy              0/3  FULL [52.08, 52.08, 49.37] vs ACC remainder [52.08, 52.08, 49.37]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.09, 52.09, 49.38] vs ACC remainder [52.08, 52.08, 49.37]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.09, 52.09, 49.38] STORAGE_MATCHED [52.09, 52.09, 49.38] vs ACC remainder [52.08, 52.08, 49.37]
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
  bestever_599ad727908c3235
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 18, 23] vs FRESH [18, 18, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.5, 4.3] vs 5% of FRESH cost [1574.1, 1560.5, 1487.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.32, 52.32, 49.64] vs CODE_ONLY [52.33, 52.33, 49.65]
    4_scramble_or_reset_damages            0/3  eff ACC [18.383, 18.413, 23.443] SCR [18.383, 18.413, 23.443] RESET [18.383, 18.413, 23.443]
    5_transfers_to_fresh_copy              0/3  FULL [52.32, 52.32, 49.64] vs ACC remainder [52.32, 52.32, 49.64]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.33, 52.33, 49.65] vs ACC remainder [52.32, 52.32, 49.64]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.33, 52.33, 49.65] STORAGE_MATCHED [52.33, 52.33, 49.65] vs ACC remainder [52.32, 52.32, 49.64]
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
  RANDOM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 6, 9] vs FRESH [6, 6, 9]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1493.8, 1515.0, 1489.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.32, 50.5, 49.1] vs CODE_ONLY [49.32, 50.5, 49.1]
    4_scramble_or_reset_damages            0/3  eff ACC [6.205, 6.235, 9.221] SCR [6.205, 6.235, 9.221] RESET [6.205, 6.235, 9.221]
    5_transfers_to_fresh_copy              0/3  FULL [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.32, 50.5, 49.1]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.32, 50.5, 49.1] STORAGE_MATCHED [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]

MACHINERY OF top1_0fcce4e9606f75c4 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   1    32
    task  9:     0    0    0    0    0 |   1    32
    task 19:     0    0    0    0    0 |   1    32
    task 31:     0    0    0    0    0 |   1    32
    task 41:     0    0    0    0    0 |   1    32
    task 49:     0    0    0    0    0 |   1    32
  artifact events: 1 (create 1, delete 0, patch/append 0); invocations by block: {}; edges: 0
    block 0 origin=calibration len=0 state=[[2, 3, 6, 8, 10, 4, 9, 11, 5, 0, 7, 1], [9, 11, 0, 1, 5, 8, 2, 10, 3, 6, 4, 7], 0] instr=[]
  adaptation curve ACC:   45 117 41 997 14 45 4 951 265 204 79 41 997 997 45 773 773 41 117 17 52 52 52 52 52 52 21 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 42 52 52 52 52 52 52 52
  adaptation curve FRESH: 45 117 42 997 15 45 4 951 266 204 79 42 997 997 45 773 773 42 117 17 52 52 52 52 52 52 21 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 43 52 52 52 52 52 52 52
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

