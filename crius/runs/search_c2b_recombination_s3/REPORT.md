CRIUS CAMPAIGN 0 REPORT  run=search_c2b_recombination_s3  arm=recombination
code_commit=713b2773f dirty=True config_hash=c9c87cec99eb063f world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  20.9038   19.9571         8.5032        40         17
    26  24.4237   24.4233        10.9971        46        111
    51  18.4008   18.4004        12.7195        46        199
    76  19.8817   17.6686        10.1648        43        286
   101  23.9131   23.4748        15.2771        26        399
   126  23.9171   22.5156        11.5138        33        521
   151  23.4366   23.4366        12.8600        30        634
   176  25.4714   25.4713        19.3932        59        742
   201  25.4570   25.4570        20.0224        61        830
   226  19.9044   19.9044        16.5074        64        918
   251  25.9428   22.4469        15.0737        74       1016
   276  21.9467   21.9366        17.6859        65       1090
   300  24.4396   24.4394        14.7428        63       1167
  candidates evaluated: 7208   best_ever 29.4613 (7da60e275698f1a1)  wall 1167s

BEST PROGRAM 7da60e275698f1a1 (len 80, iteration 236, modification arg@72.1+delete@4+replace@33+splice@43<-donor[20:28]:54bcd0935deda836)
  search seed 3012360: fit 21.4299 succ 21/50 inter 8271 steps 35153 ws_cost 15 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [313.864, 1.0], "B": [395.331, 1.0], "C": [49.621, 0.083], "D": [51.96, 0.0], "E": [51.96, 0.0]}
  search seed 3012361: fit 22.4684 succ 22/50 inter 3706 steps 18620 ws_cost 15 blocks 1 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [89.635, 1.0], "B": [144.772, 1.0], "C": [51.96, 0.0], "D": [50.908, 0.2], "E": [51.96, 0.0]}
  listing:
      0  LT             R7, R0, R2
      1  MOD            R3, R0, R1
      2  INPUT          R1, num_ops
      3  CONST          R5, -1
      4  ADD            R0, R0, R5
      5  BRNZ           R0, 25
      6  BLK_STATE_GET  R7, R7, R0
      7  CONST          R0, -3
      8  MOD            R3, R0, R1
      9  ACT            R3
     10  DIV            R4, R0, R1
     11  MOD            R3, R4, R1
     12  LT             R4, R7, R6
     13  MOD            R3, R0, R1
     14  ACT            R5
     15  DIV            R4, R0, R1
     16  VGET           R3, R2, R3
     17  JMP            25
     18  ACT            R1
     19  LT             R6, R7, R2
     20  MOD            R3, R0, R1
     21  ACT            R3
     22  MUL            R2, R1, R1
     23  ADD            R0, R0, R5
     24  VGET           R3, R2, R4
     25  MUL            R2, R1, R1
     26  VGET           R3, R2, R3
     27  LT             R7, R0, R2
     28  LT             R7, R0, R2
     29  BRZ            R6, 70
     30  WS_REC_SET     R6, R5, R4
     31  MUL            R2, R1, R4
     32  VGET           R3, R2, R3
     33  PREC_END       R2
     34  BLK_DELETE     R2
     35  WS_WRITE       R1, R6
     36  CONST          R5, -3
     37  LT             R7, R0, R2
     38  BRNZ           R0, 25
     39  WS_LINKS       R2, R3
     40  MUL            R2, R1, R1
     41  ADD            R0, R0, R5
     42  VGET           R3, R2, R4
     43  WS_WRITE       R1, R6
     44  ACT            R3
     45  MUL            R2, R1, R1
     46  VGET           R3, R2, R3
     47  LT             R7, R0, R2
     48  LT             R7, R5, R2
     49  BRZ            R6, 62
     50  WS_REC_SET     R6, R5, R4
     51  VGET           R3, R2, R3
     52  MOD            R3, R0, R1
     53  ACT            R3
     54  DIV            R4, R0, R1
     55  MOD            R3, R4, R1
     56  ACT            R3
     57  ADD            R2, R5, R0
     58  MUL            R2, R1, R1
     59  MUL            R2, R1, R1
     60  CONST          R2, -2
     61  JMP            62
     62  ACT            R1
     63  MOD            R3, R0, R1
     64  ACT            R3
     65  DIV            R4, R0, R1
     66  MOD            R3, R4, R1
     67  ACT            R3
     68  DIV            R4, R4, R1
     69  MOD            R3, R4, R3
     70  ACT            R3
     71  ADD            R0, R0, R5
     72  JMP            62
     73  VGET           R3, R2, R3
     74  ACT            R1
     75  MOD            R3, R0, R1
     76  ACT            R3
     77  DIV            R4, R0, R1
     78  LT             R7, R0, R2
     79  VSET           R1, R3, R5
  ancestry (98 steps, newest first): iteration/fitness/modification
    it  236  21.9491  len 80  arg@72.1+delete@4+replace@33+splice@43<-donor[20:28]:54bcd0935deda836
    it  234  26.9705  len 73  swap@7,72+delete@45+delete@71
    it  232  25.9608  len 75  delete@22+arg@9.0+swap@8,13+splice@9<-donor[51:55]:63ef71ff729d2e22
    it  230  23.4559  len 72  delete@33+insert@13+duplicate@35+3->19
    it  229  21.9441  len 69  arg@34.2+const@4+delete@13+splice@40<-donor[51:56]:3a3fd0ca4b1fb68d
    it  228  24.9364  len 65  delete@19+const@4+splice@58<-donor[48:52]:17f9da382473bea9
    it  227  20.9338  len 62  swap@33,29
    it  222  21.9550  len 62  swap@28,8+const@4
    it  218  26.9496  len 62  delete@6
    it  217  19.4135  len 63  duplicate@22+1->45
    it  216  22.9600  len 62  replace@43+const@2+splice@0<-donor[27:29]:35fa93c9a76bfc5a
    it  215  24.4622  len 60  const@2+const@2
    it  213  25.9356  len 60  arg@15.2
    it  210  23.4506  len 60  swap@38,43+const@31
    it  207  22.9423  len 60  arg@4.0
    ... 84 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7315.4    5.3   74.7
  top1_fb5a6561255806ec       22.777  22.777  22.777  22.777  22.3  22.3     6671     6671       7.1    1.0    0.0
  top2_ac901bbd9bf3ed43       22.777  22.776  22.777  22.777  22.3  22.3     6693     6693       7.1    1.0    0.0
  top3_0e59ab25a484a522       22.777  22.776  22.777  22.777  22.3  22.3     6693     6693       7.1    1.0    0.0
  contemp_a20a88d3455913f7    22.777  22.776  22.777  22.777  22.3  22.3     6693     6693       7.1    1.0    0.0
  ancestor125_it295_518501f0  22.777  22.776  22.777  22.777  22.3  22.3     6693     6693       7.1    1.0    0.0
  bestever_7da60e275698f1a1   22.452  22.452  22.452  22.452  22.0  22.0     5663     5663       7.1    1.0    0.0
  ancestor63_it158_a8e7c0856  22.452  22.451  22.452  22.452  22.0  22.0     5685     5685       7.1    1.0    0.0
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.9    3.7    1.7
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ancestor1_it0_0875253d162c  19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       7.2    1.0    0.0
  contemp_87735083646ccb8c    17.723  17.722  17.723  17.723  17.3  17.3    13108    13108       5.9    1.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0
  contemp_3df92ecabeca1f04     1.155   1.155   1.155   1.155   1.0   1.0    40804    40804       2.5    1.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.02/ 455.13   14.92/ 539.10   21.12/  47.94   33.22/  48.94   40.08/  50.52
  top1_fb5a6561255806ec       246.09/ 246.22  301.92/ 302.06   47.72/  47.86   51.22/  51.37   50.59/  50.74
  top2_ac901bbd9bf3ed43       247.01/ 247.14  302.84/ 302.98   47.75/  47.90   51.15/  51.30   50.52/  50.67
  top3_0e59ab25a484a522       247.01/ 247.14  302.84/ 302.98   47.75/  47.90   51.15/  51.30   50.52/  50.67
  contemp_a20a88d3455913f7    247.01/ 247.14  302.84/ 302.98   47.75/  47.90   51.15/  51.30   50.52/  50.67
  ancestor125_it295_518501f0  247.01/ 247.14  302.84/ 302.98   47.75/  47.90   51.15/  51.30   50.52/  50.67
  bestever_7da60e275698f1a1   222.15/ 222.28  219.86/ 220.00   47.83/  47.98   51.16/  51.31   51.96/  52.11
  ancestor63_it158_a8e7c0856  223.85/ 223.98  221.55/ 221.69   48.09/  48.24   51.32/  51.47   52.09/  52.24
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.14/ 443.81  528.13/ 527.79   47.94/  47.89   48.86/  48.88   50.43/  50.46
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ancestor1_it0_0875253d162c  495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  ENUMERATE_VM_C1             495.81/ 495.94  525.01/ 525.16   50.10/  50.25   51.09/  51.24   52.68/  52.83
  contemp_87735083646ccb8c    667.64/ 667.76  542.98/ 543.11   50.12/  50.23   51.91/  52.02   50.01/  50.11
  RANDOM_C1                  1662.62/1662.62 1627.07/1627.07   50.50/  50.50   50.50/  50.50   48.56/  48.56
  contemp_3df92ecabeca1f04   2080.09/2080.14 2010.97/2011.02   50.82/  50.87   52.09/  52.14   50.14/  50.19

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  top1_fb5a6561255806ec          5/36    46     1/30    49     0/12    50     1/12    47    30/30   235    30/30   289
  top2_ac901bbd9bf3ed43          5/36    46     1/30    49     0/12    50     1/12    47    30/30   236    30/30   290
  top3_0e59ab25a484a522          5/36    46     1/30    49     0/12    50     1/12    47    30/30   236    30/30   290
  contemp_a20a88d3455913f7       5/36    46     1/30    49     0/12    50     1/12    47    30/30   236    30/30   290
  ancestor125_it295_518501f0     5/36    46     1/30    49     0/12    50     1/12    47    30/30   236    30/30   290
  bestever_7da60e275698f1a1      5/36    46     1/30    49     0/12    50     0/12    50    30/30   212    30/30   210
  ancestor63_it158_a8e7c0856     5/36    46     1/30    49     0/12    50     0/12    50    30/30   213    30/30   211
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ancestor1_it0_0875253d162c     2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  contemp_87735083646ccb8c       2/36    48     0/30    50     0/12    50     1/12    46    23/30   642    26/30   522
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610
  contemp_3df92ecabeca1f04       1/36    49     0/30    50     0/12    50     1/12    46     0/30  2000     1/30  1933

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.27    49.53    36.27    36.27    49.53    49.53    49.53   5.0
  top1_fb5a6561255806ec         50.94    50.95    50.94    50.94    50.95    50.95    50.95   1.0
  top2_ac901bbd9bf3ed43         50.87    50.88    50.87    50.87    50.88    50.88    50.88   1.0
  top3_0e59ab25a484a522         50.87    50.88    50.87    50.87    50.88    50.88    50.88   1.0
  contemp_a20a88d3455913f7      50.87    50.88    50.87    50.87    50.88    50.88    50.88   1.0
  ancestor125_it295_518501f0    50.87    50.88    50.87    50.87    50.88    50.88    50.88   1.0
  bestever_7da60e275698f1a1     51.52    51.53    51.52    51.52    51.53    51.53    51.53   1.0
  ancestor63_it158_a8e7c0856    51.66    51.67    51.66    51.66    51.67    51.67    51.67   1.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.56    49.55    49.56    49.56    49.55    49.55    49.55   2.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ancestor1_it0_0875253d162c    51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  ENUMERATE_VM_C1               51.80    51.81    51.80    51.80    51.81    51.81    51.81   1.0
  contemp_87735083646ccb8c      51.06    51.07    51.06    51.06    51.07    51.07    51.07   1.0
  RANDOM_C1                     49.64       --    49.64    49.64    49.64    49.64    49.64   0.0
  contemp_3df92ecabeca1f04      51.23    51.23    51.23    51.23    51.23    51.23    51.23   1.0

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
  top1_fb5a6561255806ec
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [22, 22, 23] vs FRESH [22, 22, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.4] vs 5% of FRESH cost [1511.0, 1488.1, 1482.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.12, 52.02, 50.69] vs CODE_ONLY [50.12, 52.03, 50.7]
    4_scramble_or_reset_damages            0/3  eff ACC [22.434, 22.448, 23.448] SCR [22.434, 22.448, 23.448] RESET [22.434, 22.448, 23.448]
    5_transfers_to_fresh_copy              0/3  FULL [50.12, 52.02, 50.69] vs ACC remainder [50.12, 52.02, 50.69]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [50.12, 52.03, 50.7] vs ACC remainder [50.12, 52.02, 50.69]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.12, 52.03, 50.7] STORAGE_MATCHED [50.12, 52.03, 50.7] vs ACC remainder [50.12, 52.02, 50.69]
  top2_ac901bbd9bf3ed43
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [22, 22, 23] vs FRESH [22, 22, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.4] vs 5% of FRESH cost [1509.7, 1486.9, 1482.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.06, 51.91, 50.64] vs CODE_ONLY [50.07, 51.92, 50.65]
    4_scramble_or_reset_damages            0/3  eff ACC [22.434, 22.447, 23.448] SCR [22.434, 22.447, 23.448] RESET [22.434, 22.447, 23.448]
    5_transfers_to_fresh_copy              0/3  FULL [50.06, 51.91, 50.64] vs ACC remainder [50.06, 51.91, 50.64]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [50.07, 51.92, 50.65] vs ACC remainder [50.06, 51.91, 50.64]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.07, 51.92, 50.65] STORAGE_MATCHED [50.07, 51.92, 50.65] vs ACC remainder [50.06, 51.91, 50.64]
  top3_0e59ab25a484a522
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [22, 22, 23] vs FRESH [22, 22, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.4] vs 5% of FRESH cost [1509.7, 1486.9, 1482.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.06, 51.91, 50.64] vs CODE_ONLY [50.07, 51.92, 50.65]
    4_scramble_or_reset_damages            0/3  eff ACC [22.434, 22.447, 23.448] SCR [22.434, 22.447, 23.448] RESET [22.434, 22.447, 23.448]
    5_transfers_to_fresh_copy              0/3  FULL [50.06, 51.91, 50.64] vs ACC remainder [50.06, 51.91, 50.64]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [50.07, 51.92, 50.65] vs ACC remainder [50.06, 51.91, 50.64]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.07, 51.92, 50.65] STORAGE_MATCHED [50.07, 51.92, 50.65] vs ACC remainder [50.06, 51.91, 50.64]
  contemp_a20a88d3455913f7
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [22, 22, 23] vs FRESH [22, 22, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.4] vs 5% of FRESH cost [1509.7, 1486.9, 1482.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.06, 51.91, 50.64] vs CODE_ONLY [50.07, 51.92, 50.65]
    4_scramble_or_reset_damages            0/3  eff ACC [22.434, 22.447, 23.448] SCR [22.434, 22.447, 23.448] RESET [22.434, 22.447, 23.448]
    5_transfers_to_fresh_copy              0/3  FULL [50.06, 51.91, 50.64] vs ACC remainder [50.06, 51.91, 50.64]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [50.07, 51.92, 50.65] vs ACC remainder [50.06, 51.91, 50.64]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.07, 51.92, 50.65] STORAGE_MATCHED [50.07, 51.92, 50.65] vs ACC remainder [50.06, 51.91, 50.64]
  ancestor125_it295_518501f023d4493d
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [22, 22, 23] vs FRESH [22, 22, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.4] vs 5% of FRESH cost [1509.7, 1486.9, 1482.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.06, 51.91, 50.64] vs CODE_ONLY [50.07, 51.92, 50.65]
    4_scramble_or_reset_damages            0/3  eff ACC [22.434, 22.447, 23.448] SCR [22.434, 22.447, 23.448] RESET [22.434, 22.447, 23.448]
    5_transfers_to_fresh_copy              0/3  FULL [50.06, 51.91, 50.64] vs ACC remainder [50.06, 51.91, 50.64]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [50.07, 51.92, 50.65] vs ACC remainder [50.06, 51.91, 50.64]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.07, 51.92, 50.65] STORAGE_MATCHED [50.07, 51.92, 50.65] vs ACC remainder [50.06, 51.91, 50.64]
  bestever_7da60e275698f1a1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [21, 23, 22] vs FRESH [21, 23, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.3, 4.4] vs 5% of FRESH cost [1543.5, 1467.6, 1506.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.96, 51.96, 50.63] vs CODE_ONLY [51.97, 51.97, 50.64]
    4_scramble_or_reset_damages            0/3  eff ACC [21.456, 23.455, 22.445] SCR [21.456, 23.455, 22.445] RESET [21.456, 23.455, 22.445]
    5_transfers_to_fresh_copy              0/3  FULL [51.96, 51.96, 50.63] vs ACC remainder [51.96, 51.96, 50.63]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [51.97, 51.97, 50.64] vs ACC remainder [51.96, 51.96, 50.63]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.97, 51.97, 50.64] STORAGE_MATCHED [51.97, 51.97, 50.64] vs ACC remainder [51.96, 51.96, 50.63]
  ancestor63_it158_a8e7c0856127ea57
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [21, 23, 22] vs FRESH [21, 23, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [4.5, 4.4, 4.5] vs 5% of FRESH cost [1548.4, 1474.2, 1511.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.09, 52.09, 50.81] vs CODE_ONLY [52.1, 52.1, 50.82]
    4_scramble_or_reset_damages            0/3  eff ACC [21.456, 23.455, 22.444] SCR [21.456, 23.455, 22.444] RESET [21.456, 23.455, 22.444]
    5_transfers_to_fresh_copy              0/3  FULL [52.09, 52.09, 50.81] vs ACC remainder [52.09, 52.09, 50.81]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [52.1, 52.1, 50.82] vs ACC remainder [52.09, 52.09, 50.81]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.1, 52.1, 50.82] STORAGE_MATCHED [52.1, 52.1, 50.82] vs ACC remainder [52.09, 52.09, 50.81]
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
  contemp_87735083646ccb8c
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 18, 14] vs FRESH [20, 18, 14]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [3.2, 3.3, 3.2] vs 5% of FRESH cost [1514.8, 1560.6, 1496.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.37, 51.91, 51.91] vs CODE_ONLY [49.38, 51.92, 51.92]
    4_scramble_or_reset_damages            0/3  eff ACC [20.445, 18.382, 14.341] SCR [20.445, 18.382, 14.341] RESET [20.445, 18.382, 14.341]
    5_transfers_to_fresh_copy              0/3  FULL [49.37, 51.91, 51.91] vs ACC remainder [49.37, 51.91, 51.91]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [49.38, 51.92, 51.92] vs ACC remainder [49.37, 51.91, 51.91]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.38, 51.92, 51.92] STORAGE_MATCHED [49.38, 51.92, 51.92] vs ACC remainder [49.37, 51.91, 51.91]
  RANDOM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 6, 9] vs FRESH [6, 6, 9]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1493.8, 1515.0, 1489.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.32, 50.5, 49.1] vs CODE_ONLY [49.32, 50.5, 49.1]
    4_scramble_or_reset_damages            0/3  eff ACC [6.205, 6.235, 9.221] SCR [6.205, 6.235, 9.221] RESET [6.205, 6.235, 9.221]
    5_transfers_to_fresh_copy              0/3  FULL [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.32, 50.5, 49.1]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.32, 50.5, 49.1] STORAGE_MATCHED [49.32, 50.5, 49.1] vs ACC remainder [49.32, 50.5, 49.1]
  contemp_3df92ecabeca1f04
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [1, 0, 2] vs FRESH [1, 0, 2]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [1.5, 1.5, 1.5] vs 5% of FRESH cost [1517.5, 1564.2, 1518.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.49, 52.09, 52.09] vs CODE_ONLY [49.5, 52.09, 52.09]
    4_scramble_or_reset_damages            0/3  eff ACC [1.149, 0.149, 2.166] SCR [1.149, 0.149, 2.166] RESET [1.149, 0.149, 2.166]
    5_transfers_to_fresh_copy              0/3  FULL [49.49, 52.09, 52.09] vs ACC remainder [49.49, 52.09, 52.09]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [49.5, 52.09, 52.09] vs ACC remainder [49.49, 52.09, 52.09]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.5, 52.09, 52.09] STORAGE_MATCHED [49.5, 52.09, 52.09] vs ACC remainder [49.49, 52.09, 52.09]

MACHINERY OF top1_fb5a6561255806ec (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   1    32
    task  9:     0    0    0    0    0 |   1    32
    task 19:     0    0    0    0    0 |   1    32
    task 31:     0    0    0    0    0 |   1    32
    task 41:     0    0    0    0    0 |   1    32
    task 49:     0    0    0    0    0 |   1    32
  artifact events: 1 (create 1, delete 0, patch/append 0); invocations by block: {}; edges: 0
    block 0 origin=calibration len=0 state=[[2, 3, 6, 8, 10, 4, 9, 11, 5, 0, 7, 1], [9, 11, 0, 1, 5, 8, 2, 10, 3, 6, 4, 7], 0] instr=[]
  adaptation curve ACC:   89 578 24 714 295 89 127 512 20 51 107 35 714 714 298 699 699 15 578 259 52 32 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 18 52 52 52 52 52 52 52
  adaptation curve FRESH: 89 578 24 715 295 89 127 512 20 51 107 36 715 715 298 699 699 15 578 259 52 32 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 18 52 52 52 52 52 52 52
  reuse_gain per task:    0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0

BASELINES ON SEARCH SUITE (crius/runs/baselines_c2b): effA effF effR effS  succA  interA interF  reuse_gain  blocks
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

