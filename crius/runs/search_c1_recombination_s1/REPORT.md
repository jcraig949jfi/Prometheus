CRIUS CAMPAIGN 0 REPORT  run=search_c1_recombination_s1  arm=recombination
code_commit=97af44f88 dirty=True config_hash=32dfb243be9fdec9 world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  32.3371   24.6644         9.0128        45          9
    26  22.2928   20.7746        10.5943        60         86
    51  24.2936   23.2908        16.6594        62        155
    76  34.3676   34.3676        25.5911        60        207
   101  26.3099   25.9289        18.0671        62        269
   126  30.3575   29.8499        21.8581        63        328
   151  31.3212   30.4473        18.9896        64        380
   176  33.3776   32.4908        26.1880        64        437
   201  33.3574   33.3574        19.5843        63        509
   226  26.3250   23.6913        18.9020        62        577
   251  32.3759   32.3747        25.0176        57        641
   276  29.3044   29.3040        19.4810        62        710
   300  22.2909   22.2907        15.9799        64        769
  candidates evaluated: 7208   best_ever 48.4625 (25082ee08fd1bcbb)  wall 769s

BEST PROGRAM 25082ee08fd1bcbb (len 64, iteration 292, modification delete@51+duplicate@61+1->16+delete@16+splice@12<-donor[47:49]:00dd1d09c80e7fb9)
  search seed 101292: fit 48.4625 succ 48/50 inter 6488 steps 22517 ws_cost 150 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [23.566, 1.0], "B": [18.398, 1.0], "C": [96.912, 1.0], "D": [141.981, 1.0], "E": [464.035, 0.75]}
  listing:
      0  INPUT          R1, num_ops
      1  BRZ            R3, 11
      2  INPUT          R2, task_index
      3  WS_FREE        R0
      4  LT             R0, R0, R0
      5  BLK_INVOKE     R2
      6  CONST          R6, -3
      7  WS_LINK        R1, R2, R0
      8  WS_SREAD       R2, R2, R2
      9  BRZ            R3, 11
     10  BLK_COUNT      R3
     11  JMP            30
     12  ACT            R3
     13  DIV            R4, R0, R1
     14  ADD            R0, R0, R5
     15  BLK_COUNT      R6
     16  ACT            R3
     17  DIV            R4, R0, R1
     18  MOD            R3, R4, R1
     19  ACT            R3
     20  INPUT          R7, current_block
     21  MOV            R2, R4
     22  MUL            R5, R3, R0
     23  ACT            R1
     24  MOV            R2, R4
     25  LT             R3, R0, R7
     26  JMP            14
     27  INPUT          R5, interactions_left
     28  VLEN           R5, R6
     29  DIV            R4, R0, R1
     30  ACT            R3
     31  INPUT          R5, interactions_left
     32  ADD            R0, R3, R5
     33  BLK_LEN        R0, R0
     34  ADD            R0, R0, R5
     35  ADD            R0, R0, R5
     36  MOV            R2, R6
     37  ADD            R0, R0, R5
     38  ADD            R0, R0, R5
     39  WS_FIND        R7, R4
     40  ADD            R0, R0, R5
     41  BLK_COUNT      R3
     42  INPUT          R1, num_ops
     43  ADD            R0, R0, R5
     44  BRNZ           R1, 53
     45  ACT            R1
     46  INPUT          R5, current
     47  ACT            R3
     48  MOD            R3, R0, R1
     49  ACT            R3
     50  DIV            R4, R0, R1
     51  MOD            R3, R4, R1
     52  ACT            R3
     53  MOD            R3, R4, R1
     54  ACT            R1
     55  ADD            R0, R0, R5
     56  JMP            47
     57  WS_REC_NEW     R2
     58  WS_READ        R5, R2
     59  BLK_DELETE     R0
     60  INPUT          R3, current
     61  DIV            R4, R4, R5
     62  VSET           R1, R7, R0
     63  MUL            R2, R1, R2
  ancestry (169 steps, newest first): iteration/fitness/modification
    it  292  48.4625  len 64  delete@51+duplicate@61+1->16+delete@16+splice@12<-donor[47:49]:00dd1d09c80e7fb9
    it  290  29.3420  len 63  const@6
    it  289  36.3503  len 63  const@6
    it  288  23.2914  len 63  const@6
    it  287  30.3297  len 63  insert@27+delete@31+delete@41+splice@14<-donor[44:48]:5f09fd1e0b0e7460
    it  285  32.2821  len 60  arg@57.2
    it  281  23.3214  len 60  delete@4+const@6+replace@4
    it  280  29.2875  len 61  delete@41
    it  279  36.3586  len 62  arg@14.0
    it  275  38.3868  len 62  arg@27.1+splice@31<-donor[33:34]:90508c9a76a06325
    it  274  39.3736  len 61  delete@15
    it  271  24.3081  len 62  replace@57
    it  270  22.3081  len 62  arg@16.0
    it  268  32.3305  len 62  delete@44
    it  267  22.3159  len 63  swap@44,52+replace@33+arg@21.0+splice@19<-donor[43:44]:9b574ff802f1fc7f
    ... 155 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          47.117  26.961  27.664  27.999  46.7  26.7     8916    38056   29005.3    4.3   74.7
  ancestor88_it141_d0a211e9c  30.328  30.328  30.328  30.328  30.0  30.0    30649    30649       0.0    0.0    0.0
  ancestor174_it299_dd8ae2e4  27.985  27.985  27.985  27.985  27.7  27.7    32602    32602       0.0    0.0    0.0
  top1_de08b338928aca30       27.984  27.984  27.984  27.984  27.7  27.7    32712    32712       0.0    0.0    0.0
  top2_24ed3516b81dd955       27.984  27.984  27.984  27.984  27.7  27.7    32759    32759       0.0    0.0    0.0
  top3_bab9c713b07833ca       27.984  27.984  27.984  27.984  27.7  27.7    32759    32759       0.0    0.0    0.0
  contemp_1729a0471fbcb860    27.982  27.982  27.982  27.982  27.7  27.7    32759    32759       0.0    0.0    0.0
  ENUMERATE_C1                26.964  26.964  26.964  26.964  26.7  26.7    37456    37456       0.0    0.0    0.0
  TABLE_MEMO_C1               26.964  26.964  26.964  26.964  26.7  26.7    37456    37456     -17.9    0.0    0.0
  PROCEDURE_NOCAL_C1          26.962  26.962  26.962  26.962  26.7  26.7    37759    37756     -23.8    3.3    1.7
  contemp_a8611f9249a33726    26.274  26.274  26.274  26.274  26.0  26.0    38582    38582       0.0    0.0    0.0
  ancestor1_it0_0875253d162c  25.287  25.287  25.287  25.287  25.0  25.0    37856    37856       0.0    0.0    0.0
  ENUMERATE_VM_C1             25.287  25.287  25.287  25.287  25.0  25.0    37856    37856       0.0    0.0    0.0
  bestever_25082ee08fd1bcbb   22.627  22.627  22.627  22.627  22.3  22.3    37057    37057       0.0    0.0    0.0
  QUIT_C1                     19.605  19.605  19.605  19.605  19.3  19.3     9448     9448       0.0    0.0    0.0
  RANDOM_C1                   10.160  10.160  10.160  10.160  10.0  10.0    62546    62546       0.0    0.0    0.0
  contemp_134a4366b42957f1     0.108   0.108   0.108   0.108   0.0   0.0       50       50       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.00/ 455.13   14.90/ 539.10   36.22/ 623.47  177.39/1089.94  477.07/1237.03
  ancestor88_it141_d0a211e9c  265.89/ 265.89  260.89/ 260.89  582.91/ 582.91  974.83/ 974.83 1233.56/1233.56
  ancestor174_it299_dd8ae2e4  230.88/ 230.88  405.52/ 405.52  606.33/ 606.33 1031.49/1031.49 1231.48/1231.48
  top1_de08b338928aca30       231.55/ 231.55  417.28/ 417.28  606.60/ 606.60 1030.57/1030.57 1230.97/1230.97
  top2_24ed3516b81dd955       233.60/ 233.60  419.13/ 419.13  606.65/ 606.65 1031.16/1031.16 1231.28/1231.28
  top3_bab9c713b07833ca       233.60/ 233.60  419.13/ 419.13  606.65/ 606.65 1031.16/1031.16 1231.28/1231.28
  contemp_1729a0471fbcb860    235.10/ 235.10  421.82/ 421.82  610.54/ 610.54 1037.79/1037.79 1239.19/1239.19
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31  615.85/ 615.85 1086.47/1086.47 1232.75/1232.75
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34  616.29/ 615.86 1086.97/1086.48 1233.28/1232.76
  PROCEDURE_NOCAL_C1          444.13/ 443.81  528.11/ 527.79  619.85/ 619.71 1088.59/1088.26 1236.48/1234.94
  contemp_a8611f9249a33726    716.96/ 716.96  576.54/ 576.54  631.92/ 631.92 1060.25/1060.25 1351.08/1351.08
  ancestor1_it0_0875253d162c  494.04/ 494.04  523.26/ 523.26  664.50/ 664.50 1116.70/1116.70 1283.87/1283.87
  ENUMERATE_VM_C1             494.04/ 494.04  523.26/ 523.26  664.50/ 664.50 1116.70/1116.70 1283.87/1283.87
  bestever_25082ee08fd1bcbb   386.74/ 386.74  568.88/ 568.88  595.94/ 595.94 1135.40/1135.40 1280.01/1280.01
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31  800.00/ 800.00 1200.00/1200.00 1400.00/1400.00
  RANDOM_C1                  1661.96/1661.96 1626.54/1626.54  726.73/ 726.73 1161.23/1161.23 1244.20/1244.20
  contemp_134a4366b42957f1   2000.41/2000.41 2000.41/2000.41  800.41/ 800.41 1200.41/1200.41 1400.41/1400.41

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            36/36    33    27/30   167     6/12   809    11/12   117    30/30   301    30/30    14
  ancestor88_it141_d0a211e9c    16/36   560     9/30   937     2/12  1411     3/12   962    30/30   256    30/30   251
  ancestor174_it299_dd8ae2e4    13/36   585     9/30   995     2/12  1349     2/12  1027    30/30   223    27/30   391
  top1_de08b338928aca30         13/36   585     9/30   994     2/12  1348     2/12  1026    30/30   223    27/30   402
  top2_24ed3516b81dd955         13/36   585     9/30   995     2/12  1349     2/12  1027    30/30   225    27/30   404
  top3_bab9c713b07833ca         13/36   585     9/30   995     2/12  1349     2/12  1027    30/30   225    27/30   404
  contemp_1729a0471fbcb860      13/36   585     9/30   995     2/12  1349     2/12  1027    30/30   225    27/30   404
  ENUMERATE_C1                  13/36   613     5/30  1082     2/12  1350     2/12  1106    29/30   431    29/30   514
  TABLE_MEMO_C1                 13/36   613     5/30  1082     2/12  1350     2/12  1106    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1            13/36   617     5/30  1084     2/12  1352     2/12  1108    29/30   442    29/30   526
  contemp_a8611f9249a33726      13/36   581     7/30   976     2/12  1360     1/12  1127    25/30   660    30/30   530
  ancestor1_it0_0875253d162c    11/36   635     6/30  1068     2/12  1350     2/12  1107    27/30   472    27/30   500
  ENUMERATE_VM_C1               11/36   635     6/30  1068     2/12  1350     2/12  1107    27/30   472    27/30   500
  bestever_25082ee08fd1bcbb     12/36   577     3/30  1099     2/12  1352     1/12  1126    26/30   374    23/30   550
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  RANDOM_C1                      6/36   720     2/30  1150     2/12  1430     2/12  1034    10/30  1646     8/30  1610
  contemp_134a4366b42957f1       0/36     1     0/30     1     0/12     1     0/12     1     0/30     1     0/30     1

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1           310.58  1153.44   310.58   310.58  1153.44  1153.44  1153.44   4.0
  ancestor88_it141_d0a211e9c  1089.82       --  1089.82  1089.82  1089.82  1089.82  1089.82   0.0
  ancestor174_it299_dd8ae2e4  1120.37       --  1120.37  1120.37  1120.37  1120.37  1120.37   0.0
  top1_de08b338928aca30       1119.64       --  1119.64  1119.64  1119.64  1119.64  1119.64   0.0
  top2_24ed3516b81dd955       1120.10       --  1120.10  1120.10  1120.10  1120.10  1120.10   0.0
  top3_bab9c713b07833ca       1120.10       --  1120.10  1120.10  1120.10  1120.10  1120.10   0.0
  contemp_1729a0471fbcb860    1127.30       --  1127.30  1127.30  1127.30  1127.30  1127.30   0.0
  ENUMERATE_C1                1151.49       --  1151.49  1151.49  1151.49  1151.49  1151.49   0.0
  TABLE_MEMO_C1               1152.00       --  1151.52  1152.00  1151.52  1151.52  1151.52   0.0
  PROCEDURE_NOCAL_C1          1154.32  1153.42  1154.32  1154.32  1153.42  1153.42  1153.42   1.3
  contemp_a8611f9249a33726    1189.51       --  1189.51  1189.51  1189.51  1189.51  1189.51   0.0
  ancestor1_it0_0875253d162c  1191.00       --  1191.00  1191.00  1191.00  1191.00  1191.00   0.0
  ENUMERATE_VM_C1             1191.00       --  1191.00  1191.00  1191.00  1191.00  1191.00   0.0
  bestever_25082ee08fd1bcbb   1199.67       --  1199.67  1199.67  1199.67  1199.67  1199.67   0.0
  QUIT_C1                     1288.89       --  1288.89  1288.89  1288.89  1288.89  1288.89   0.0
  RANDOM_C1                   1198.10       --  1198.10  1198.10  1198.10  1198.10  1198.10   0.0
  contemp_134a4366b42957f1    1289.30       --  1289.30  1289.30  1289.30  1289.30  1289.30   0.0

CHARTER s13 CHECKLIST (seeds passing / seeds; thresholds: 5 percent relative; guard 0 added 2026-09-19, see report.py)
  PROCEDURE_REUSE_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [48, 48, 44] vs FRESH [27, 21, 32]
    1_cost_declines_via_accumulation       3/3  reuse_gain C-E per seed [24737.6, 26217.9, 15800.8] vs 5% of FRESH cost [28628.2, 30079.1, 26124.2] (and 0 held)
    2_reproduces_on_heldout                3/3  same test, qualification suite; seeds passing = 3/3
    3_state_causal_FULL_vs_CODE_ONLY       3/3  remainder mean cost FULL [203.42, 202.97, 525.35] vs CODE_ONLY [1150.72, 1208.34, 1101.26]
    4_scramble_or_reset_damages            3/3  eff ACC [48.449, 48.467, 44.435] SCR [27.316, 24.332, 32.35] RESET [27.316, 23.326, 32.351]
    5_transfers_to_fresh_copy              3/3  FULL [203.42, 202.97, 525.35] vs ACC remainder [203.42, 202.97, 525.35]
    6_executable_components_reused         3/3  invocations [82, 81, 61]; ABLATION_ALL cost [1150.72, 1208.34, 1101.26] vs ACC remainder [203.42, 202.97, 525.35]
    7_not_compute_or_storage               3/3  COMPUTE_MATCHED [1150.72, 1208.34, 1101.26] STORAGE_MATCHED [1150.72, 1208.34, 1101.26] vs ACC remainder [203.42, 202.97, 525.35]
  ancestor88_it141_d0a211e9ca65b364
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [28, 29, 33] vs FRESH [28, 29, 33]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [29315.6, 27031.8, 23487.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1157.71, 1127.32, 984.44] vs CODE_ONLY [1157.71, 1127.32, 984.44]
    4_scramble_or_reset_damages            0/3  eff ACC [28.308, 29.326, 33.35] SCR [28.308, 29.326, 33.35] RESET [28.308, 29.326, 33.35]
    5_transfers_to_fresh_copy              0/3  FULL [1157.71, 1127.32, 984.44] vs ACC remainder [1157.71, 1127.32, 984.44]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1157.71, 1127.32, 984.44]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1157.71, 1127.32, 984.44] STORAGE_MATCHED [1157.71, 1127.32, 984.44] vs ACC remainder [1157.71, 1127.32, 984.44]
  ancestor174_it299_dd8ae2e4d5d2a13a
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [28, 24, 31] vs FRESH [28, 24, 31]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [28347.7, 29384.3, 24596.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1113.33, 1193.5, 1054.3] vs CODE_ONLY [1113.33, 1193.5, 1054.3]
    4_scramble_or_reset_damages            0/3  eff ACC [28.321, 24.295, 31.337] SCR [28.321, 24.295, 31.337] RESET [28.321, 24.295, 31.337]
    5_transfers_to_fresh_copy              0/3  FULL [1113.33, 1193.5, 1054.3] vs ACC remainder [1113.33, 1193.5, 1054.3]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1113.33, 1193.5, 1054.3]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1113.33, 1193.5, 1054.3] STORAGE_MATCHED [1113.33, 1193.5, 1054.3] vs ACC remainder [1113.33, 1193.5, 1054.3]
  top1_de08b338928aca30
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [28, 24, 31] vs FRESH [28, 24, 31]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [28323.1, 29366.0, 24608.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1112.48, 1192.99, 1053.44] vs CODE_ONLY [1112.48, 1192.99, 1053.44]
    4_scramble_or_reset_damages            0/3  eff ACC [28.321, 24.296, 31.335] SCR [28.321, 24.296, 31.335] RESET [28.321, 24.296, 31.335]
    5_transfers_to_fresh_copy              0/3  FULL [1112.48, 1192.99, 1053.44] vs ACC remainder [1112.48, 1192.99, 1053.44]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1112.48, 1192.99, 1053.44]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1112.48, 1192.99, 1053.44] STORAGE_MATCHED [1112.48, 1192.99, 1053.44] vs ACC remainder [1112.48, 1192.99, 1053.44]
  top2_24ed3516b81dd955
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [28, 24, 31] vs FRESH [28, 24, 31]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [28339.0, 29377.7, 24608.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1113.02, 1193.3, 1053.98] vs CODE_ONLY [1113.02, 1193.3, 1053.98]
    4_scramble_or_reset_damages            0/3  eff ACC [28.321, 24.295, 31.334] SCR [28.321, 24.295, 31.334] RESET [28.321, 24.295, 31.334]
    5_transfers_to_fresh_copy              0/3  FULL [1113.02, 1193.3, 1053.98] vs ACC remainder [1113.02, 1193.3, 1053.98]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1113.02, 1193.3, 1053.98]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1113.02, 1193.3, 1053.98] STORAGE_MATCHED [1113.02, 1193.3, 1053.98] vs ACC remainder [1113.02, 1193.3, 1053.98]
  top3_bab9c713b07833ca
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [28, 24, 31] vs FRESH [28, 24, 31]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [28339.0, 29377.7, 24608.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1113.02, 1193.3, 1053.98] vs CODE_ONLY [1113.02, 1193.3, 1053.98]
    4_scramble_or_reset_damages            0/3  eff ACC [28.321, 24.295, 31.334] SCR [28.321, 24.295, 31.334] RESET [28.321, 24.295, 31.334]
    5_transfers_to_fresh_copy              0/3  FULL [1113.02, 1193.3, 1053.98] vs ACC remainder [1113.02, 1193.3, 1053.98]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1113.02, 1193.3, 1053.98]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1113.02, 1193.3, 1053.98] STORAGE_MATCHED [1113.02, 1193.3, 1053.98] vs ACC remainder [1113.02, 1193.3, 1053.98]
  contemp_1729a0471fbcb860
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [28, 24, 31] vs FRESH [28, 24, 31]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [28521.1, 29566.5, 24766.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1120.17, 1200.97, 1060.76] vs CODE_ONLY [1120.17, 1200.97, 1060.76]
    4_scramble_or_reset_damages            0/3  eff ACC [28.32, 24.294, 31.333] SCR [28.32, 24.294, 31.333] RESET [28.32, 24.294, 31.333]
    5_transfers_to_fresh_copy              0/3  FULL [1120.17, 1200.97, 1060.76] vs ACC remainder [1120.17, 1200.97, 1060.76]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1120.17, 1200.97, 1060.76]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1120.17, 1200.97, 1060.76] STORAGE_MATCHED [1120.17, 1200.97, 1060.76] vs ACC remainder [1120.17, 1200.97, 1060.76]
  ENUMERATE_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [27, 21, 32] vs FRESH [27, 21, 32]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [28451.7, 30023.5, 25875.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1148.47, 1207.55, 1098.44] vs CODE_ONLY [1148.47, 1207.55, 1098.44]
    4_scramble_or_reset_damages            0/3  eff ACC [27.27, 21.287, 32.335] SCR [27.27, 21.287, 32.335] RESET [27.27, 21.287, 32.335]
    5_transfers_to_fresh_copy              0/3  FULL [1148.47, 1207.55, 1098.44] vs ACC remainder [1148.47, 1207.55, 1098.44]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1148.47, 1207.55, 1098.44]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1148.47, 1207.55, 1098.44] STORAGE_MATCHED [1148.47, 1207.55, 1098.44] vs ACC remainder [1148.47, 1207.55, 1098.44]
  TABLE_MEMO_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [27, 21, 32] vs FRESH [27, 21, 32]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [-14.6, -11.9, -16.3] vs 5% of FRESH cost [28451.9, 30023.6, 25875.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1148.99, 1207.95, 1099.05] vs CODE_ONLY [1148.51, 1207.55, 1098.51]
    4_scramble_or_reset_damages            0/3  eff ACC [27.27, 21.287, 32.335] SCR [27.27, 21.287, 32.335] RESET [27.27, 21.287, 32.335]
    5_transfers_to_fresh_copy              0/3  FULL [1148.99, 1207.95, 1099.05] vs ACC remainder [1148.99, 1207.95, 1099.05]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1148.99, 1207.95, 1099.05]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1148.51, 1207.55, 1098.51] STORAGE_MATCHED [1148.51, 1207.55, 1098.51] vs ACC remainder [1148.99, 1207.95, 1099.05]
  PROCEDURE_NOCAL_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [27, 21, 32] vs FRESH [27, 21, 32]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [-0.3, -3.0, -48.6] vs 5% of FRESH cost [28541.5, 30052.8, 26001.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1150.66, 1208.36, 1103.94] vs CODE_ONLY [1150.62, 1208.35, 1101.27]
    4_scramble_or_reset_damages            0/3  eff ACC [27.268, 21.286, 32.332] SCR [27.268, 21.286, 32.332] RESET [27.269, 21.286, 32.333]
    5_transfers_to_fresh_copy              0/3  FULL [1150.66, 1208.36, 1103.94] vs ACC remainder [1150.66, 1208.36, 1103.94]
    6_executable_components_reused         0/3  invocations [3, 1, 1]; ABLATION_ALL cost [1150.62, 1208.35, 1101.27] vs ACC remainder [1150.66, 1208.36, 1103.94]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1150.62, 1208.35, 1101.27] STORAGE_MATCHED [1150.62, 1208.35, 1101.27] vs ACC remainder [1150.66, 1208.36, 1103.94]
  contemp_a8611f9249a33726
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [28, 23, 27] vs FRESH [28, 23, 27]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [29403.2, 31250.1, 26329.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1211.04, 1247.37, 1110.11] vs CODE_ONLY [1211.04, 1247.37, 1110.11]
    4_scramble_or_reset_damages            0/3  eff ACC [28.29, 23.289, 27.243] SCR [28.29, 23.289, 27.243] RESET [28.29, 23.289, 27.243]
    5_transfers_to_fresh_copy              0/3  FULL [1211.04, 1247.37, 1110.11] vs ACC remainder [1211.04, 1247.37, 1110.11]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1211.04, 1247.37, 1110.11]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1211.04, 1247.37, 1110.11] STORAGE_MATCHED [1211.04, 1247.37, 1110.11] vs ACC remainder [1211.04, 1247.37, 1110.11]
  ancestor1_it0_0875253d162cdf0f
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [24, 20, 31] vs FRESH [24, 20, 31]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [30138.8, 31267.0, 26830.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1176.4, 1257.27, 1139.33] vs CODE_ONLY [1176.4, 1257.27, 1139.33]
    4_scramble_or_reset_damages            0/3  eff ACC [24.259, 20.274, 31.328] SCR [24.259, 20.274, 31.328] RESET [24.259, 20.274, 31.328]
    5_transfers_to_fresh_copy              0/3  FULL [1176.4, 1257.27, 1139.33] vs ACC remainder [1176.4, 1257.27, 1139.33]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1176.4, 1257.27, 1139.33]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1176.4, 1257.27, 1139.33] STORAGE_MATCHED [1176.4, 1257.27, 1139.33] vs ACC remainder [1176.4, 1257.27, 1139.33]
  ENUMERATE_VM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [24, 20, 31] vs FRESH [24, 20, 31]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [30138.8, 31267.0, 26830.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1176.4, 1257.27, 1139.33] vs CODE_ONLY [1176.4, 1257.27, 1139.33]
    4_scramble_or_reset_damages            0/3  eff ACC [24.259, 20.274, 31.328] SCR [24.259, 20.274, 31.328] RESET [24.259, 20.274, 31.328]
    5_transfers_to_fresh_copy              0/3  FULL [1176.4, 1257.27, 1139.33] vs ACC remainder [1176.4, 1257.27, 1139.33]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1176.4, 1257.27, 1139.33]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1176.4, 1257.27, 1139.33] STORAGE_MATCHED [1176.4, 1257.27, 1139.33] vs ACC remainder [1176.4, 1257.27, 1139.33]
  bestever_25082ee08fd1bcbb
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [22, 17, 28] vs FRESH [22, 17, 28]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [30008.4, 29078.5, 27149.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1197.13, 1193.22, 1208.67] vs CODE_ONLY [1197.13, 1193.22, 1208.67]
    4_scramble_or_reset_damages            0/3  eff ACC [22.304, 17.245, 28.332] SCR [22.304, 17.245, 28.332] RESET [22.304, 17.245, 28.332]
    5_transfers_to_fresh_copy              0/3  FULL [1197.13, 1193.22, 1208.67] vs ACC remainder [1197.13, 1193.22, 1208.67]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1197.13, 1193.22, 1208.67]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1197.13, 1193.22, 1208.67] STORAGE_MATCHED [1197.13, 1193.22, 1208.67] vs ACC remainder [1197.13, 1193.22, 1208.67]
  QUIT_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [20, 18, 20] vs FRESH [20, 18, 20]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [32800.0, 32800.0, 32800.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1288.89, 1288.89, 1288.89] vs CODE_ONLY [1288.89, 1288.89, 1288.89]
    4_scramble_or_reset_damages            0/3  eff ACC [20.247, 18.272, 20.297] SCR [20.247, 18.272, 20.297] RESET [20.247, 18.272, 20.297]
    5_transfers_to_fresh_copy              0/3  FULL [1288.89, 1288.89, 1288.89] vs ACC remainder [1288.89, 1288.89, 1288.89]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1288.89, 1288.89, 1288.89]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1288.89, 1288.89, 1288.89] STORAGE_MATCHED [1288.89, 1288.89, 1288.89] vs ACC remainder [1288.89, 1288.89, 1288.89]
  RANDOM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [10, 8, 12] vs FRESH [10, 8, 12]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [29757.7, 31845.3, 29256.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1210.09, 1230.52, 1153.7] vs CODE_ONLY [1210.09, 1230.52, 1153.7]
    4_scramble_or_reset_damages            0/3  eff ACC [10.152, 8.161, 12.165] SCR [10.152, 8.161, 12.165] RESET [10.152, 8.161, 12.165]
    5_transfers_to_fresh_copy              0/3  FULL [1210.09, 1230.52, 1153.7] vs ACC remainder [1210.09, 1230.52, 1153.7]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1210.09, 1230.52, 1153.7]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1210.09, 1230.52, 1153.7] STORAGE_MATCHED [1210.09, 1230.52, 1153.7] vs ACC remainder [1210.09, 1230.52, 1153.7]
  contemp_134a4366b42957f1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [32812.3, 32812.3, 32812.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1289.3, 1289.3, 1289.3] vs CODE_ONLY [1289.3, 1289.3, 1289.3]
    4_scramble_or_reset_damages            0/3  eff ACC [0.108, 0.108, 0.108] SCR [0.108, 0.108, 0.108] RESET [0.108, 0.108, 0.108]
    5_transfers_to_fresh_copy              0/3  FULL [1289.3, 1289.3, 1289.3] vs ACC remainder [1289.3, 1289.3, 1289.3]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1289.3, 1289.3, 1289.3]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1289.3, 1289.3, 1289.3] STORAGE_MATCHED [1289.3, 1289.3, 1289.3] vs ACC remainder [1289.3, 1289.3, 1289.3]

MACHINERY OF top1_de08b338928aca30 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   0     0
    task  9:     0    0    0    0    0 |   0     0
    task 19:     0    0    0    0    0 |   0     0
    task 31:     0    0    0    0    0 |   0     0
    task 41:     0    0    0    0    0 |   0     0
    task 49:     0    0    0    0    0 |   0     0
  artifact events: 0 (create 0, delete 0, patch/append 0); invocations by block: {}; edges: 0
  adaptation curve ACC:   5 543 241 606 23 5 63 142 91 148 98 241 606 606 23 288 288 114 543 151 830 17 830 301 830 515 830 830 830 830 830 830 733 609 1244 1244 1244 1244 1244 1244 1125 1244 54 1659 1659 85 1244 1244 1244 1659
  adaptation curve FRESH: 5 543 241 606 23 5 63 142 91 148 98 241 606 606 23 288 288 114 543 151 830 17 830 301 830 515 830 830 830 830 830 830 733 609 1244 1244 1244 1244 1244 1244 1125 1244 54 1659 1659 85 1244 1244 1244 1659
  reuse_gain per task:    0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0

BASELINES ON SEARCH SUITE (crius\runs\baselines_c1): effA effF effR effS  succA  interA interF  reuse_gain  blocks
  ENUMERATE_C1_seed301     31.359 31.359 31.359 31.359   31   25220  25220        0.0    0
  ENUMERATE_C1_seed302     26.311 26.311 26.311 26.311   26   33697  33697        0.0    0
  ENUMERATE_C1_seed303     28.363 28.363 28.363 28.363   28   24420  24420        0.0    0
  ENUMERATE_VM_C1_seed301  31.353 31.353 31.353 31.353   31   25220  25220        0.0    0
  ENUMERATE_VM_C1_seed302  26.300 26.300 26.300 26.300   26   34243  34243        0.0    0
  ENUMERATE_VM_C1_seed303  28.353 28.353 28.353 28.353   28   25190  25190        0.0    0
  PROCEDURE_NOCAL_C1_seed301 31.354 31.357 31.357 31.354   31   25522  25520     -461.2    6
  PROCEDURE_NOCAL_C1_seed302 25.310 25.310 25.310 25.310   25   33921  33919      -40.2    4
  PROCEDURE_NOCAL_C1_seed303 28.361 28.362 28.362 28.361   28   24676  24672      -60.6    5
  PROCEDURE_REUSE_C1_seed301 50.492 31.355 31.365 34.387   50    1338  25820    24477.4    4
  PROCEDURE_REUSE_C1_seed302 49.472 25.309 27.339 27.339   49    4787  34135    29253.1    6
  PROCEDURE_REUSE_C1_seed303 50.494 28.360 28.366 30.376   50     948  24924    23996.0    5
  QUIT_C1_seed301          20.324 20.324 20.324 20.324   20    1907   1907        0.0    0
  QUIT_C1_seed302          17.283 17.283 17.283 17.283   17    9331   9331        0.0    0
  QUIT_C1_seed303          20.328 20.328 20.328 20.328   20    1135   1135        0.0    0
  RANDOM_C1_seed301        18.191 18.191 18.191 18.191   18   54741  54741        0.0    0
  RANDOM_C1_seed302        15.179 15.179 15.179 15.179   15   56867  56867        0.0    0
  RANDOM_C1_seed303        21.224 21.224 21.224 21.224   21   49058  49058        0.0    0
  TABLE_MEMO_C1_seed301    31.359 31.359 31.359 31.359   31   25220  25220      -19.7    0
  TABLE_MEMO_C1_seed302    26.311 26.311 26.311 26.311   26   33697  33697      -15.6    0
  TABLE_MEMO_C1_seed303    28.363 28.363 28.363 28.363   28   24420  24420      -17.9    0

