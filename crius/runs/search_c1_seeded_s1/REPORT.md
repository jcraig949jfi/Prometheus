CRIUS CAMPAIGN 0 REPORT  run=search_c1_seeded_s1  arm=seeded
code_commit=97af44f88 dirty=True config_hash=32dfb243be9fdec9 world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  32.3335   30.1931        11.6285        40          6
    26  20.2390   19.4848        10.5881        50         82
    51  31.3216   30.5699        18.1019        57        153
    76  42.3964   42.3964        30.8333        53        210
   101  23.2969   23.2795        18.5628        53        274
   126  32.3506   31.4760        24.5446        56        328
   151  31.3207   29.0679        18.2427        57        380
   176  38.3883   36.5018        28.5259        63        432
   201  33.3370   30.9628        25.3844        61        480
   226  34.3281   34.3277        23.2647        62        525
   251  38.3700   38.3700        23.8213        55        568
   276  32.2964   32.2964        23.6693        62        616
   300  27.3148   25.8052        19.1272        56        654
  candidates evaluated: 7208   best_ever 49.4333 (031f3601dbc4f896)  wall 655s

BEST PROGRAM 031f3601dbc4f896 (len 59, iteration 292, modification delete@34)
  search seed 101292: fit 49.4333 succ 49/50 inter 11564 steps 38014 ws_cost 0 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [100.755, 1.0], "B": [109.112, 1.0], "C": [222.081, 1.0], "D": [385.516, 0.9], "E": [415.668, 1.0]}
  listing:
      0  INPUT          R1, num_ops
      1  CONST          R5, 10
      2  JMP            44
      3  ACT            R3
      4  INPUT          R1, target
      5  CONST          R5, 11
      6  SUB            R7, R3, R2
      7  ACT            R6
      8  HALT           
      9  BLK_NEW        R7
     10  HALT           
     11  VGET           R2, R1, R1
     12  MOV            R2, R1
     13  VSET           R4, R0, R7
     14  ADD            R0, R1, R5
     15  WS_REC_NEW     R2
     16  WS_READ        R6, R4
     17  ADD            R3, R4, R1
     18  BLK_REC_BEGIN  
     19  NOT            R3, R2
     20  NOT            R2, R6
     21  JMP            16
     22  WS_FIND        R7, R1
     23  BLK_PATCH      R5, R0, R4
     24  MOV            R2, R1
     25  CONST          R5, 10
     26  BLK_NEW        R7
     27  ACT            R3
     28  INPUT          R1, target
     29  WS_REC_GET     R6, R6, R2
     30  WS_FIND        R4, R1
     31  ACT            R3
     32  WS_LINK_GET    R0, R2, R5
     33  BLK_REC_BEGIN  
     34  WS_FIND        R7, R3
     35  MUL            R2, R1, R6
     36  WS_LINKS       R3, R2
     37  CONST          R0, -2
     38  ACT            R3
     39  MOD            R3, R0, R1
     40  BLK_COUNT      R2
     41  WS_FIND        R7, R4
     42  MOV            R1, R5
     43  WS_REC_NEW     R5
     44  ADD            R3, R4, R1
     45  CONST          R0, -8
     46  ACT            R3
     47  MOD            R3, R0, R1
     48  CONST          R5, 19
     49  ACT            R3
     50  DIV            R4, R0, R1
     51  MOD            R3, R4, R1
     52  DIV            R4, R4, R1
     53  ACT            R3
     54  ACT            R2
     55  ADD            R0, R0, R5
     56  MOD            R3, R4, R1
     57  ACT            R1
     58  JMP            46
  ancestry (181 steps, newest first): iteration/fitness/modification
    it  292  49.4333  len 59  delete@34
    it  291  43.4162  len 60  delete@13
    it  290  32.3149  len 61  arg@16.1+delete@11+swap@13,27
    it  288  28.2935  len 62  delete@38
    it  286  26.2918  len 63  replace@11+replace@45+delete@32
    it  285  29.2107  len 64  delete@42+insert@11
    it  284  26.3017  len 64  const@5+swap@13,11+const@50
    it  283  36.3576  len 64  const@50
    it  281  22.3149  len 64  insert@49+duplicate@1+4->26+const@53
    it  280  30.3156  len 59  arg@28.1+const@37
    it  279  35.3312  len 59  arg@4.1+delete@12+delete@42
    it  277  30.3473  len 61  delete@19
    it  276  32.2964  len 62  delete@48+arg@44.0
    it  275  44.4264  len 63  replace@14+replace@44
    it  273  33.3541  len 63  delete@42+const@39+replace@6
    ... 167 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          47.117  26.961  27.664  27.999  46.7  26.7     8916    38056   29005.3    4.3   74.7
  top2_0ec4f004769eb410       31.322  31.322  31.322  31.322  31.0  31.0    31959    31959       0.0    0.0    0.0
  top1_d467f76689979ce2       30.988  30.988  30.988  30.988  30.7  30.7    32168    32168       0.0    0.0    0.0
  top3_0b20db083dab8f96       30.656  30.656  30.656  30.656  30.3  30.3    31797    31797       0.0    0.0    0.0
  bestever_031f3601dbc4f896   30.656  30.656  30.656  30.656  30.3  30.3    31797    31797       0.0    0.0    0.0
  contemp_2c2161eaa8e76828    30.656  30.656  30.656  30.656  30.3  30.3    31797    31797       0.0    0.0    0.0
  ancestor186_it297_ce91dd38  30.656  30.656  30.656  30.656  30.3  30.3    31797    31797       0.0    0.0    0.0
  contemp_16fd3ed761c82bec    29.987  29.987  29.987  29.987  29.7  29.7    32352    32352       0.0    0.0    0.0
  ancestor94_it161_721c6ef35  28.991  28.991  28.991  28.991  28.7  28.7    31637    31637       0.0    0.0    0.0
  ENUMERATE_C1                26.964  26.964  26.964  26.964  26.7  26.7    37456    37456       0.0    0.0    0.0
  TABLE_MEMO_C1               26.964  26.964  26.964  26.964  26.7  26.7    37456    37456     -17.9    0.0    0.0
  PROCEDURE_NOCAL_C1          26.962  26.962  26.962  26.962  26.7  26.7    37759    37756     -23.8    3.3    1.7
  ancestor1_it0_0875253d162c  25.287  25.287  25.287  25.287  25.0  25.0    37856    37856       0.0    0.0    0.0
  ENUMERATE_VM_C1             25.287  25.287  25.287  25.287  25.0  25.0    37856    37856       0.0    0.0    0.0
  QUIT_C1                     19.605  19.605  19.605  19.605  19.3  19.3     9448     9448       0.0    0.0    0.0
  RANDOM_C1                   10.160  10.160  10.160  10.160  10.0  10.0    62546    62546       0.0    0.0    0.0
  contemp_8dfaa332b4b2f03d     1.741   1.741   1.741   1.741   1.7   1.7    70572    70572       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.00/ 455.13   14.90/ 539.10   36.22/ 623.47  177.39/1089.94  477.07/1237.03
  top2_0ec4f004769eb410       403.33/ 403.33  396.74/ 396.74  564.32/ 564.32  902.80/ 902.80 1160.09/1160.09
  top1_d467f76689979ce2       375.30/ 375.30  363.59/ 363.59  587.65/ 587.65  921.30/ 921.30 1195.40/1195.40
  top3_0b20db083dab8f96       317.30/ 317.30  456.28/ 456.28  587.71/ 587.71  874.66/ 874.66 1162.40/1162.40
  bestever_031f3601dbc4f896   317.30/ 317.30  456.28/ 456.28  587.71/ 587.71  874.66/ 874.66 1162.40/1162.40
  contemp_2c2161eaa8e76828    317.30/ 317.30  456.28/ 456.28  587.71/ 587.71  874.66/ 874.66 1162.40/1162.40
  ancestor186_it297_ce91dd38  317.30/ 317.30  456.28/ 456.28  587.71/ 587.71  874.66/ 874.66 1162.40/1162.40
  contemp_16fd3ed761c82bec    334.93/ 334.93  292.25/ 292.25  600.52/ 600.52 1036.42/1036.42 1195.57/1195.57
  ancestor94_it161_721c6ef35  265.10/ 265.10  283.30/ 283.30  627.40/ 627.40  990.71/ 990.71 1210.25/1210.25
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31  615.85/ 615.85 1086.47/1086.47 1232.75/1232.75
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34  616.29/ 615.86 1086.97/1086.48 1233.28/1232.76
  PROCEDURE_NOCAL_C1          444.13/ 443.81  528.11/ 527.79  619.85/ 619.71 1088.59/1088.26 1236.48/1234.94
  ancestor1_it0_0875253d162c  494.04/ 494.04  523.26/ 523.26  664.50/ 664.50 1116.70/1116.70 1283.87/1283.87
  ENUMERATE_VM_C1             494.04/ 494.04  523.26/ 523.26  664.50/ 664.50 1116.70/1116.70 1283.87/1283.87
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31  800.00/ 800.00 1200.00/1200.00 1400.00/1400.00
  RANDOM_C1                  1661.96/1661.96 1626.54/1626.54  726.73/ 726.73 1161.23/1161.23 1244.20/1244.20
  contemp_8dfaa332b4b2f03d   2165.73/2165.73 2166.89/2166.89  847.81/ 847.81 1299.90/1299.90 1568.06/1568.06

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            36/36    33    27/30   167     6/12   809    11/12   117    30/30   301    30/30    14
  top2_0ec4f004769eb410         18/36   545    13/30   872     2/12  1370     4/12   872    28/30   390    28/30   383
  top1_d467f76689979ce2         16/36   569    14/30   892     2/12  1388     5/12   928    28/30   363    27/30   352
  top3_0b20db083dab8f96         15/36   569    12/30   847     2/12  1384     4/12   868    29/30   307    29/30   442
  bestever_031f3601dbc4f896     15/36   569    12/30   847     2/12  1384     4/12   868    29/30   307    29/30   442
  contemp_2c2161eaa8e76828      15/36   569    12/30   847     2/12  1384     4/12   868    29/30   307    29/30   442
  ancestor186_it297_ce91dd38    15/36   569    12/30   847     2/12  1384     4/12   868    29/30   307    29/30   442
  contemp_16fd3ed761c82bec      15/36   582     9/30  1004     2/12  1351     3/12   965    30/30   324    30/30   283
  ancestor94_it161_721c6ef35    12/36   609     9/30   962     3/12  1241     3/12  1108    29/30   257    30/30   275
  ENUMERATE_C1                  13/36   613     5/30  1082     2/12  1350     2/12  1106    29/30   431    29/30   514
  TABLE_MEMO_C1                 13/36   613     5/30  1082     2/12  1350     2/12  1106    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1            13/36   617     5/30  1084     2/12  1352     2/12  1108    29/30   442    29/30   526
  ancestor1_it0_0875253d162c    11/36   635     6/30  1068     2/12  1350     2/12  1107    27/30   472    27/30   500
  ENUMERATE_VM_C1               11/36   635     6/30  1068     2/12  1350     2/12  1107    27/30   472    27/30   500
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  RANDOM_C1                      6/36   720     2/30  1150     2/12  1430     2/12  1034    10/30  1646     8/30  1610
  contemp_8dfaa332b4b2f03d       2/36   757     1/30  1161     0/12  1600     0/12  1200     1/30  1934     1/30  1935

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1           310.58  1153.44   310.58   310.58  1153.44  1153.44  1153.44   4.0
  top2_0ec4f004769eb410       1017.15       --  1017.15  1017.15  1017.15  1017.15  1017.15   0.0
  top1_d467f76689979ce2       1043.12       --  1043.12  1043.12  1043.12  1043.12  1043.12   0.0
  top3_0b20db083dab8f96       1002.55       --  1002.55  1002.55  1002.55  1002.55  1002.55   0.0
  bestever_031f3601dbc4f896   1002.55       --  1002.55  1002.55  1002.55  1002.55  1002.55   0.0
  contemp_2c2161eaa8e76828    1002.55       --  1002.55  1002.55  1002.55  1002.55  1002.55   0.0
  ancestor186_it297_ce91dd38  1002.55       --  1002.55  1002.55  1002.55  1002.55  1002.55   0.0
  contemp_16fd3ed761c82bec    1107.15       --  1107.15  1107.15  1107.15  1107.15  1107.15   0.0
  ancestor94_it161_721c6ef35  1088.28       --  1088.28  1088.28  1088.28  1088.28  1088.28   0.0
  ENUMERATE_C1                1151.49       --  1151.49  1151.49  1151.49  1151.49  1151.49   0.0
  TABLE_MEMO_C1               1152.00       --  1151.52  1152.00  1151.52  1151.52  1151.52   0.0
  PROCEDURE_NOCAL_C1          1154.32  1153.42  1154.32  1154.32  1153.42  1153.42  1153.42   1.3
  ancestor1_it0_0875253d162c  1191.00       --  1191.00  1191.00  1191.00  1191.00  1191.00   0.0
  ENUMERATE_VM_C1             1191.00       --  1191.00  1191.00  1191.00  1191.00  1191.00   0.0
  QUIT_C1                     1288.89       --  1288.89  1288.89  1288.89  1288.89  1288.89   0.0
  RANDOM_C1                   1198.10       --  1198.10  1198.10  1198.10  1198.10  1198.10   0.0
  contemp_8dfaa332b4b2f03d    1419.08       --  1419.08  1419.08  1419.08  1419.08  1419.08   0.0

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
  top2_0ec4f004769eb410
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [30, 26, 37] vs FRESH [30, 26, 37]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [24787.2, 27840.4, 22613.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [913.92, 1128.68, 1008.85] vs CODE_ONLY [913.92, 1128.68, 1008.85]
    4_scramble_or_reset_damages            0/3  eff ACC [30.303, 26.304, 37.358] SCR [30.303, 26.304, 37.358] RESET [30.303, 26.304, 37.358]
    5_transfers_to_fresh_copy              0/3  FULL [913.92, 1128.68, 1008.85] vs ACC remainder [913.92, 1128.68, 1008.85]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [913.92, 1128.68, 1008.85]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [913.92, 1128.68, 1008.85] STORAGE_MATCHED [913.92, 1128.68, 1008.85] vs ACC remainder [913.92, 1128.68, 1008.85]
  top1_d467f76689979ce2
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [31, 25, 36] vs FRESH [31, 25, 36]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [25534.7, 28549.6, 23399.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [966.32, 1141.44, 1021.61] vs CODE_ONLY [966.32, 1141.44, 1021.61]
    4_scramble_or_reset_damages            0/3  eff ACC [31.315, 25.292, 36.356] SCR [31.315, 25.292, 36.356] RESET [31.315, 25.292, 36.356]
    5_transfers_to_fresh_copy              0/3  FULL [966.32, 1141.44, 1021.61] vs ACC remainder [966.32, 1141.44, 1021.61]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [966.32, 1141.44, 1021.61]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [966.32, 1141.44, 1021.61] STORAGE_MATCHED [966.32, 1141.44, 1021.61] vs ACC remainder [966.32, 1141.44, 1021.61]
  top3_0b20db083dab8f96
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [29, 28, 34] vs FRESH [29, 28, 34]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [25201.2, 27806.2, 22287.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [984.84, 1099.1, 923.7] vs CODE_ONLY [984.84, 1099.1, 923.7]
    4_scramble_or_reset_damages            0/3  eff ACC [29.312, 28.306, 34.351] SCR [29.312, 28.306, 34.351] RESET [29.312, 28.306, 34.351]
    5_transfers_to_fresh_copy              0/3  FULL [984.84, 1099.1, 923.7] vs ACC remainder [984.84, 1099.1, 923.7]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [984.84, 1099.1, 923.7]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [984.84, 1099.1, 923.7] STORAGE_MATCHED [984.84, 1099.1, 923.7] vs ACC remainder [984.84, 1099.1, 923.7]
  bestever_031f3601dbc4f896
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [29, 28, 34] vs FRESH [29, 28, 34]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [25201.2, 27806.2, 22287.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [984.84, 1099.1, 923.7] vs CODE_ONLY [984.84, 1099.1, 923.7]
    4_scramble_or_reset_damages            0/3  eff ACC [29.312, 28.306, 34.351] SCR [29.312, 28.306, 34.351] RESET [29.312, 28.306, 34.351]
    5_transfers_to_fresh_copy              0/3  FULL [984.84, 1099.1, 923.7] vs ACC remainder [984.84, 1099.1, 923.7]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [984.84, 1099.1, 923.7]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [984.84, 1099.1, 923.7] STORAGE_MATCHED [984.84, 1099.1, 923.7] vs ACC remainder [984.84, 1099.1, 923.7]
  contemp_2c2161eaa8e76828
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [29, 28, 34] vs FRESH [29, 28, 34]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [25201.2, 27806.2, 22287.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [984.84, 1099.1, 923.7] vs CODE_ONLY [984.84, 1099.1, 923.7]
    4_scramble_or_reset_damages            0/3  eff ACC [29.312, 28.306, 34.351] SCR [29.312, 28.306, 34.351] RESET [29.312, 28.306, 34.351]
    5_transfers_to_fresh_copy              0/3  FULL [984.84, 1099.1, 923.7] vs ACC remainder [984.84, 1099.1, 923.7]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [984.84, 1099.1, 923.7]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [984.84, 1099.1, 923.7] STORAGE_MATCHED [984.84, 1099.1, 923.7] vs ACC remainder [984.84, 1099.1, 923.7]
  ancestor186_it297_ce91dd382905b6d1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [29, 28, 34] vs FRESH [29, 28, 34]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [25201.2, 27806.2, 22287.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [984.84, 1099.1, 923.7] vs CODE_ONLY [984.84, 1099.1, 923.7]
    4_scramble_or_reset_damages            0/3  eff ACC [29.312, 28.306, 34.351] SCR [29.312, 28.306, 34.351] RESET [29.312, 28.306, 34.351]
    5_transfers_to_fresh_copy              0/3  FULL [984.84, 1099.1, 923.7] vs ACC remainder [984.84, 1099.1, 923.7]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [984.84, 1099.1, 923.7]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [984.84, 1099.1, 923.7] STORAGE_MATCHED [984.84, 1099.1, 923.7] vs ACC remainder [984.84, 1099.1, 923.7]
  contemp_16fd3ed761c82bec
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [31, 25, 33] vs FRESH [31, 25, 33]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [26939.9, 29653.2, 24812.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1095.55, 1198.62, 1027.29] vs CODE_ONLY [1095.55, 1198.62, 1027.29]
    4_scramble_or_reset_damages            0/3  eff ACC [31.311, 25.306, 33.343] SCR [31.311, 25.306, 33.343] RESET [31.311, 25.306, 33.343]
    5_transfers_to_fresh_copy              0/3  FULL [1095.55, 1198.62, 1027.29] vs ACC remainder [1095.55, 1198.62, 1027.29]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1095.55, 1198.62, 1027.29]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1095.55, 1198.62, 1027.29] STORAGE_MATCHED [1095.55, 1198.62, 1027.29] vs ACC remainder [1095.55, 1198.62, 1027.29]
  ancestor94_it161_721c6ef3500b7c38
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [29, 26, 31] vs FRESH [29, 26, 31]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [26695.3, 29137.3, 25521.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1021.66, 1174.38, 1068.81] vs CODE_ONLY [1021.66, 1174.38, 1068.81]
    4_scramble_or_reset_damages            0/3  eff ACC [29.322, 26.309, 31.341] SCR [29.322, 26.309, 31.341] RESET [29.322, 26.309, 31.341]
    5_transfers_to_fresh_copy              0/3  FULL [1021.66, 1174.38, 1068.81] vs ACC remainder [1021.66, 1174.38, 1068.81]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1021.66, 1174.38, 1068.81]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1021.66, 1174.38, 1068.81] STORAGE_MATCHED [1021.66, 1174.38, 1068.81] vs ACC remainder [1021.66, 1174.38, 1068.81]
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
  contemp_8dfaa332b4b2f03d
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 3, 2] vs FRESH [0, 3, 2]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [36737.8, 35851.9, 34561.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1443.62, 1443.62, 1370.01] vs CODE_ONLY [1443.62, 1443.62, 1370.01]
    4_scramble_or_reset_damages            0/3  eff ACC [0.061, 3.089, 2.072] SCR [0.061, 3.089, 2.072] RESET [0.061, 3.089, 2.072]
    5_transfers_to_fresh_copy              0/3  FULL [1443.62, 1443.62, 1370.01] vs ACC remainder [1443.62, 1443.62, 1370.01]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1443.62, 1443.62, 1370.01]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1443.62, 1443.62, 1370.01] STORAGE_MATCHED [1443.62, 1443.62, 1370.01] vs ACC remainder [1443.62, 1443.62, 1370.01]

MACHINERY OF top1_d467f76689979ce2 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   0     0
    task  9:     0    0    0    0    0 |   0     0
    task 19:     0    0    0    0    0 |   0     0
    task 31:     0    0    0    0    0 |   0     0
    task 41:     0    0    0    0    0 |   0     0
    task 49:     0    0    0    0    0 |   0     0
  artifact events: 0 (create 0, delete 0, patch/append 0); invocations by block: {}; edges: 0
  adaptation curve ACC:   38 659 3 2064 38 38 34 226 23 212 55 387 2065 2065 38 122 122 3 659 22 826 47 826 826 826 826 320 826 826 826 379 787 948 72 1239 1239 1239 1239 569 1239 548 1184 393 1652 1652 191 1239 185 912 1652
  adaptation curve FRESH: 38 659 3 2064 38 38 34 226 23 212 55 387 2065 2065 38 122 122 3 659 22 826 47 826 826 826 826 320 826 826 826 379 787 948 72 1239 1239 1239 1239 569 1239 548 1184 393 1652 1652 191 1239 185 912 1652
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

