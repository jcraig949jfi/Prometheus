CRIUS CAMPAIGN 0 REPORT  run=search_c1_seeded_s3  arm=seeded
code_commit=97af44f88 dirty=True config_hash=32dfb243be9fdec9 world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  30.3615   28.3567        14.1338        39          3
    26  32.3174   29.9412        21.7198        62         57
    51  26.3212   26.3207        22.7075        63        111
    76  27.3085   27.3080        14.9632        61        172
   101  39.3676   38.3584        29.0874        59        226
   126  26.3052   25.4348        18.7904        60        282
   151  29.3400   29.3393        20.6968        51        338
   176  24.2789   22.8971        13.4052        55        392
   201  48.4557   48.4557        35.5700        59        445
   226  34.3350   34.3349        23.9748        64        492
   251  32.3312   29.7217        22.0362        63        537
   276  32.3383   30.5728        19.7916        62        582
   300  26.2843   26.2752        17.6337        51        628
  candidates evaluated: 7208   best_ever 48.4557 (f6e45198da1da565)  wall 628s

BEST PROGRAM f6e45198da1da565 (len 59, iteration 201, modification replace@34+replace@28+const@39)
  search seed 301201: fit 48.4557 succ 48/50 inter 7635 steps 30911 ws_cost 50 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [76.946, 1.0], "B": [47.202, 1.0], "C": [172.461, 0.917], "D": [311.56, 0.9], "E": [189.75, 1.0]}
  listing:
      0  BLK_REC_BEGIN  
      1  INPUT          R1, num_ops
      2  MOD            R3, R4, R1
      3  WS_LINK_GET    R0, R5, R7
      4  BRZ            R7, 27
      5  WS_WRITE       R6, R6
      6  HALT           
      7  MOD            R3, R0, R1
      8  BLK_PATCH      R4, R3, R5
      9  BLK_STATE_GET  R0, R1, R3
     10  ADD            R0, R0, R6
     11  BLK_REC_BEGIN  
     12  BRZ            R3, 35
     13  HALT           
     14  WS_WRITE       R6, R6
     15  LT             R3, R0, R2
     16  HALT           
     17  WS_REC_GET     R4, R6, R6
     18  ACT            R5
     19  ACT            R1
     20  VLEN           R4, R4
     21  ACT            R3
     22  DIV            R4, R0, R1
     23  MOD            R3, R4, R1
     24  ACT            R1
     25  ACT            R1
     26  WS_FIND        R5, R4
     27  CONST          R5, -1
     28  BRNZ           R7, 20
     29  ADD            R0, R0, R0
     30  JMP            43
     31  MOD            R3, R0, R1
     32  ACT            R1
     33  BLK_STATE_GET  R5, R0, R4
     34  BLK_COMPOSE    R6, R0, R2
     35  ADD            R0, R0, R0
     36  ADD            R0, R0, R0
     37  ACT            R1
     38  BLK_REC_BEGIN  
     39  CONST          R5, 4
     40  WS_SREAD       R6, R4, R7
     41  ADD            R0, R0, R0
     42  MOD            R3, R0, R1
     43  MUL            R6, R3, R3
     44  ACT            R3
     45  MOD            R3, R0, R1
     46  ACT            R3
     47  DIV            R4, R0, R1
     48  MOD            R3, R4, R1
     49  ACT            R3
     50  DIV            R4, R4, R3
     51  MOD            R3, R4, R1
     52  ADD            R0, R0, R5
     53  ACT            R3
     54  ACTI           13
     55  ACT            R1
     56  JMP            45
     57  ACT            R3
     58  ACT            R3
  ancestry (126 steps, newest first): iteration/fitness/modification
    it  201  48.4557  len 59  replace@34+replace@28+const@39
    it  200  30.3299  len 59  arg@28.2
    it  198  39.3810  len 59  duplicate@25+1->32+delete@42
    it  197  36.3870  len 59  delete@6
    it  194  20.3138  len 60  const@55
    it  191  30.3221  len 60  const@28+duplicate@55+2->31+swap@45,32
    it  190  27.2937  len 58  replace@18
    it  188  38.3698  len 58  arg@39.1+arg@13.1+const@40
    it  187  27.3210  len 58  const@31+replace@31+const@37
    it  186  35.3788  len 58  const@53
    it  184  42.4256  len 58  delete@19+insert@7+arg@52.0
    it  183  23.2704  len 58  const@54+delete@24
    it  180  24.2964  len 59  replace@54
    it  178  25.2931  len 59  insert@9+duplicate@27+6->36+replace@28
    it  176  22.2683  len 52  swap@48,22+delete@34
    ... 112 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          47.117  26.961  27.664  27.999  46.7  26.7     8916    38056   29005.3    4.3   74.7
  top1_001cc78e9ce9aee1       30.982  30.982  30.982  30.982  30.7  30.7    33442    33442       0.0    0.0    0.0
  top2_57aecef6de7fd442       30.643  30.643  30.643  30.643  30.3  30.3    34402    34402       0.0    0.0    0.0
  top3_6b9dc74466bc2e93       30.643  30.643  30.643  30.643  30.3  30.3    34402    34402       0.0    0.0    0.0
  ancestor195_it299_cfcba1eb  30.643  30.643  30.643  30.643  30.3  30.3    34402    34402       0.0    0.0    0.0
  contemp_e0c2cc39a7d1bd5a    30.643  30.643  30.643  30.643  30.3  30.3    34402    34402       0.0    0.0    0.0
  ENUMERATE_C1                26.964  26.964  26.964  26.964  26.7  26.7    37456    37456       0.0    0.0    0.0
  TABLE_MEMO_C1               26.964  26.964  26.964  26.964  26.7  26.7    37456    37456     -17.9    0.0    0.0
  PROCEDURE_NOCAL_C1          26.962  26.962  26.962  26.962  26.7  26.7    37759    37756     -23.8    3.3    1.7
  ancestor98_it152_69903ccaf  26.298  26.298  26.298  26.298  26.0  26.0    36094    36094       0.0    0.0    0.0
  bestever_f6e45198da1da565   26.297  26.297  26.297  26.297  26.0  26.0    36243    36243       0.0    0.0    0.0
  ancestor1_it0_0875253d162c  25.287  25.287  25.287  25.287  25.0  25.0    37856    37856       0.0    0.0    0.0
  ENUMERATE_VM_C1             25.287  25.287  25.287  25.287  25.0  25.0    37856    37856       0.0    0.0    0.0
  contemp_b9e197081faeb3b5    21.608  21.608  21.608  21.608  21.3  21.3    40876    40876       0.0    0.0    0.0
  QUIT_C1                     19.605  19.605  19.605  19.605  19.3  19.3     9448     9448       0.0    0.0    0.0
  RANDOM_C1                   10.160  10.160  10.160  10.160  10.0  10.0    62546    62546       0.0    0.0    0.0
  contemp_08932b75de781483     0.097   0.097   0.097   0.097   0.0   0.0    72800    72800       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.00/ 455.13   14.90/ 539.10   36.22/ 623.47  177.39/1089.94  477.07/1237.03
  top1_001cc78e9ce9aee1       310.68/ 310.68  488.78/ 488.78  560.66/ 560.66  959.93/ 959.93 1249.64/1249.64
  top2_57aecef6de7fd442       358.35/ 358.35  549.15/ 549.15  588.41/ 588.41  968.24/ 968.24 1185.77/1185.77
  top3_6b9dc74466bc2e93       358.35/ 358.35  549.15/ 549.15  588.41/ 588.41  968.24/ 968.24 1185.77/1185.77
  ancestor195_it299_cfcba1eb  358.35/ 358.35  549.15/ 549.15  588.41/ 588.41  968.24/ 968.24 1185.77/1185.77
  contemp_e0c2cc39a7d1bd5a    358.36/ 358.36  549.16/ 549.16  588.42/ 588.42  968.25/ 968.25 1185.78/1185.78
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31  615.85/ 615.85 1086.47/1086.47 1232.75/1232.75
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34  616.29/ 615.86 1086.97/1086.48 1233.28/1232.76
  PROCEDURE_NOCAL_C1          444.13/ 443.81  528.11/ 527.79  619.85/ 619.71 1088.59/1088.26 1236.48/1234.94
  ancestor98_it152_69903ccaf  414.61/ 414.61  567.72/ 567.72  617.95/ 617.95 1022.38/1022.38 1245.25/1245.25
  bestever_f6e45198da1da565   422.43/ 422.43  574.89/ 574.89  620.60/ 620.60 1027.30/1027.30 1250.39/1250.39
  ancestor1_it0_0875253d162c  494.04/ 494.04  523.26/ 523.26  664.50/ 664.50 1116.70/1116.70 1283.87/1283.87
  ENUMERATE_VM_C1             494.04/ 494.04  523.26/ 523.26  664.50/ 664.50 1116.70/1116.70 1283.87/1283.87
  contemp_b9e197081faeb3b5    592.85/ 592.85  723.13/ 723.13  646.31/ 646.31 1111.89/1111.89 1228.97/1228.97
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31  800.00/ 800.00 1200.00/1200.00 1400.00/1400.00
  RANDOM_C1                  1661.96/1661.96 1626.54/1626.54  726.73/ 726.73 1161.23/1161.23 1244.20/1244.20
  contemp_08932b75de781483   2056.12/2056.12 2056.12/2056.12  822.52/ 822.52 1233.72/1233.72 1439.32/1439.32

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            36/36    33    27/30   167     6/12   809    11/12   117    30/30   301    30/30    14
  top1_001cc78e9ce9aee1         16/36   546    13/30   935     2/12  1418     5/12  1017    29/30   303    27/30   476
  top2_57aecef6de7fd442         15/36   573    11/30   944     2/12  1381     5/12   930    30/30   349    28/30   535
  top3_6b9dc74466bc2e93         15/36   573    11/30   944     2/12  1381     5/12   930    30/30   349    28/30   535
  ancestor195_it299_cfcba1eb    15/36   573    11/30   944     2/12  1381     5/12   930    30/30   349    28/30   535
  contemp_e0c2cc39a7d1bd5a      15/36   573    11/30   944     2/12  1381     5/12   930    30/30   349    28/30   535
  ENUMERATE_C1                  13/36   613     5/30  1082     2/12  1350     2/12  1106    29/30   431    29/30   514
  TABLE_MEMO_C1                 13/36   613     5/30  1082     2/12  1350     2/12  1106    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1            13/36   617     5/30  1084     2/12  1352     2/12  1108    29/30   442    29/30   526
  ancestor98_it152_69903ccaf    13/36   596     7/30   986     2/12  1360     2/12  1042    27/30   400    27/30   548
  bestever_f6e45198da1da565     13/36   597     7/30   988     2/12  1361     2/12  1043    27/30   406    27/30   553
  ancestor1_it0_0875253d162c    11/36   635     6/30  1068     2/12  1350     2/12  1107    27/30   472    27/30   500
  ENUMERATE_VM_C1               11/36   635     6/30  1068     2/12  1350     2/12  1107    27/30   472    27/30   500
  contemp_b9e197081faeb3b5       9/36   631     4/30  1086     2/12  1381     2/12  1019    24/30   579    23/30   706
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  RANDOM_C1                      6/36   720     2/30  1150     2/12  1430     2/12  1034    10/30  1646     8/30  1610
  contemp_08932b75de781483       0/36   800     0/30  1200     0/12  1600     0/12  1200     0/30  2000     0/30  2000

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1           310.58  1153.44   310.58   310.58  1153.44  1153.44  1153.44   4.0
  top1_001cc78e9ce9aee1       1088.69       --  1088.69  1088.69  1088.69  1088.69  1088.69   0.0
  top2_57aecef6de7fd442       1064.92       --  1064.92  1064.92  1064.92  1064.92  1064.92   0.0
  top3_6b9dc74466bc2e93       1064.92       --  1064.92  1064.92  1064.92  1064.92  1064.92   0.0
  ancestor195_it299_cfcba1eb  1064.92       --  1064.92  1064.92  1064.92  1064.92  1064.92   0.0
  contemp_e0c2cc39a7d1bd5a    1064.93       --  1064.93  1064.93  1064.93  1064.93  1064.93   0.0
  ENUMERATE_C1                1151.49       --  1151.49  1151.49  1151.49  1151.49  1151.49   0.0
  TABLE_MEMO_C1               1152.00       --  1151.52  1152.00  1151.52  1151.52  1151.52   0.0
  PROCEDURE_NOCAL_C1          1154.32  1153.42  1154.32  1154.32  1153.42  1153.42  1153.42   1.3
  ancestor98_it152_69903ccaf  1121.43       --  1121.43  1121.43  1121.43  1121.43  1121.43   0.0
  bestever_f6e45198da1da565   1126.45       --  1126.45  1126.45  1126.45  1126.45  1126.45   0.0
  ancestor1_it0_0875253d162c  1191.00       --  1191.00  1191.00  1191.00  1191.00  1191.00   0.0
  ENUMERATE_VM_C1             1191.00       --  1191.00  1191.00  1191.00  1191.00  1191.00   0.0
  contemp_b9e197081faeb3b5    1163.92       --  1163.92  1163.92  1163.92  1163.92  1163.92   0.0
  QUIT_C1                     1288.89       --  1288.89  1288.89  1288.89  1288.89  1288.89   0.0
  RANDOM_C1                   1198.10       --  1198.10  1198.10  1198.10  1198.10  1198.10   0.0
  contemp_08932b75de781483    1325.10       --  1325.10  1325.10  1325.10  1325.10  1325.10   0.0

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
  top1_001cc78e9ce9aee1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [32, 24, 36] vs FRESH [32, 24, 36]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [25935.5, 28912.8, 24124.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1031.56, 1176.85, 1057.66] vs CODE_ONLY [1031.56, 1176.85, 1057.66]
    4_scramble_or_reset_damages            0/3  eff ACC [32.304, 24.306, 36.335] SCR [32.304, 24.306, 36.335] RESET [32.304, 24.306, 36.335]
    5_transfers_to_fresh_copy              0/3  FULL [1031.56, 1176.85, 1057.66] vs ACC remainder [1031.56, 1176.85, 1057.66]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1031.56, 1176.85, 1057.66]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1031.56, 1176.85, 1057.66] STORAGE_MATCHED [1031.56, 1176.85, 1057.66] vs ACC remainder [1031.56, 1176.85, 1057.66]
  top2_57aecef6de7fd442
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [27, 29, 35] vs FRESH [27, 29, 35]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [27673.4, 26179.6, 24835.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1083.2, 1059.2, 1052.36] vs CODE_ONLY [1083.2, 1059.2, 1052.36]
    4_scramble_or_reset_damages            0/3  eff ACC [27.278, 29.328, 35.323] SCR [27.278, 29.328, 35.323] RESET [27.278, 29.328, 35.323]
    5_transfers_to_fresh_copy              0/3  FULL [1083.2, 1059.2, 1052.36] vs ACC remainder [1083.2, 1059.2, 1052.36]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1083.2, 1059.2, 1052.36]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1083.2, 1059.2, 1052.36] STORAGE_MATCHED [1083.2, 1059.2, 1052.36] vs ACC remainder [1083.2, 1059.2, 1052.36]
  top3_6b9dc74466bc2e93
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [27, 29, 35] vs FRESH [27, 29, 35]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [27673.4, 26179.6, 24835.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1083.2, 1059.2, 1052.36] vs CODE_ONLY [1083.2, 1059.2, 1052.36]
    4_scramble_or_reset_damages            0/3  eff ACC [27.278, 29.328, 35.323] SCR [27.278, 29.328, 35.323] RESET [27.278, 29.328, 35.323]
    5_transfers_to_fresh_copy              0/3  FULL [1083.2, 1059.2, 1052.36] vs ACC remainder [1083.2, 1059.2, 1052.36]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1083.2, 1059.2, 1052.36]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1083.2, 1059.2, 1052.36] STORAGE_MATCHED [1083.2, 1059.2, 1052.36] vs ACC remainder [1083.2, 1059.2, 1052.36]
  ancestor195_it299_cfcba1eb016d558d
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [27, 29, 35] vs FRESH [27, 29, 35]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [27673.4, 26179.6, 24835.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1083.2, 1059.2, 1052.36] vs CODE_ONLY [1083.2, 1059.2, 1052.36]
    4_scramble_or_reset_damages            0/3  eff ACC [27.278, 29.328, 35.323] SCR [27.278, 29.328, 35.323] RESET [27.278, 29.328, 35.323]
    5_transfers_to_fresh_copy              0/3  FULL [1083.2, 1059.2, 1052.36] vs ACC remainder [1083.2, 1059.2, 1052.36]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1083.2, 1059.2, 1052.36]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1083.2, 1059.2, 1052.36] STORAGE_MATCHED [1083.2, 1059.2, 1052.36] vs ACC remainder [1083.2, 1059.2, 1052.36]
  contemp_e0c2cc39a7d1bd5a
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [27, 29, 35] vs FRESH [27, 29, 35]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [27673.7, 26179.9, 24836.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1083.21, 1059.21, 1052.37] vs CODE_ONLY [1083.21, 1059.21, 1052.37]
    4_scramble_or_reset_damages            0/3  eff ACC [27.278, 29.327, 35.323] SCR [27.278, 29.327, 35.323] RESET [27.278, 29.327, 35.323]
    5_transfers_to_fresh_copy              0/3  FULL [1083.21, 1059.21, 1052.37] vs ACC remainder [1083.21, 1059.21, 1052.37]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1083.21, 1059.21, 1052.37]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1083.21, 1059.21, 1052.37] STORAGE_MATCHED [1083.21, 1059.21, 1052.37] vs ACC remainder [1083.21, 1059.21, 1052.37]
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
  ancestor98_it152_69903ccaf4809d9a
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [24, 24, 30] vs FRESH [24, 24, 30]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [28738.0, 26939.4, 27126.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1129.86, 1074.05, 1160.39] vs CODE_ONLY [1129.86, 1074.05, 1160.39]
    4_scramble_or_reset_damages            0/3  eff ACC [24.278, 24.289, 30.328] SCR [24.278, 24.289, 30.328] RESET [24.278, 24.289, 30.328]
    5_transfers_to_fresh_copy              0/3  FULL [1129.86, 1074.05, 1160.39] vs ACC remainder [1129.86, 1074.05, 1160.39]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1129.86, 1074.05, 1160.39]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1129.86, 1074.05, 1160.39] STORAGE_MATCHED [1129.86, 1074.05, 1160.39] vs ACC remainder [1129.86, 1074.05, 1160.39]
  bestever_f6e45198da1da565
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [24, 24, 30] vs FRESH [24, 24, 30]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [28879.4, 27006.4, 27284.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1135.04, 1079.06, 1165.26] vs CODE_ONLY [1135.04, 1079.06, 1165.26]
    4_scramble_or_reset_damages            0/3  eff ACC [24.277, 24.288, 30.326] SCR [24.277, 24.288, 30.326] RESET [24.277, 24.288, 30.326]
    5_transfers_to_fresh_copy              0/3  FULL [1135.04, 1079.06, 1165.26] vs ACC remainder [1135.04, 1079.06, 1165.26]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1135.04, 1079.06, 1165.26]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1135.04, 1079.06, 1165.26] STORAGE_MATCHED [1135.04, 1079.06, 1165.26] vs ACC remainder [1135.04, 1079.06, 1165.26]
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
  contemp_b9e197081faeb3b5
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 18, 28] vs FRESH [18, 18, 28]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [30316.4, 28854.2, 26948.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1180.27, 1144.71, 1166.79] vs CODE_ONLY [1180.27, 1144.71, 1166.79]
    4_scramble_or_reset_damages            0/3  eff ACC [18.263, 18.254, 28.306] SCR [18.263, 18.254, 28.306] RESET [18.263, 18.254, 28.306]
    5_transfers_to_fresh_copy              0/3  FULL [1180.27, 1144.71, 1166.79] vs ACC remainder [1180.27, 1144.71, 1166.79]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1180.27, 1144.71, 1166.79]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1180.27, 1144.71, 1166.79] STORAGE_MATCHED [1180.27, 1144.71, 1166.79] vs ACC remainder [1180.27, 1144.71, 1166.79]
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
  contemp_08932b75de781483
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [33722.0, 33722.0, 33722.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1325.1, 1325.1, 1325.1] vs CODE_ONLY [1325.1, 1325.1, 1325.1]
    4_scramble_or_reset_damages            0/3  eff ACC [0.097, 0.097, 0.097] SCR [0.097, 0.097, 0.097] RESET [0.097, 0.097, 0.097]
    5_transfers_to_fresh_copy              0/3  FULL [1325.1, 1325.1, 1325.1] vs ACC remainder [1325.1, 1325.1, 1325.1]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1325.1, 1325.1, 1325.1]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1325.1, 1325.1, 1325.1] STORAGE_MATCHED [1325.1, 1325.1, 1325.1] vs ACC remainder [1325.1, 1325.1, 1325.1]

MACHINERY OF top1_001cc78e9ce9aee1 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     1    1    0    0    0 |   0     0
    task  9:     1    1    0    0    0 |   0     0
    task 19:     1    1    0    0    0 |   0     0
    task 31:     1    1    0    0    0 |   0     0
    task 41:     1    1    0    0    0 |   0     0
    task 49:     1    1    0    0    0 |   0     0
  artifact events: 0 (create 0, delete 0, patch/append 0); invocations by block: {}; edges: 0
  adaptation curve ACC:   199 362 100 753 106 36 207 75 7 120 28 100 2052 2052 199 1768 1768 45 362 64 821 36 821 821 821 291 502 821 821 821 143 650 978 644 1231 1231 1231 1231 810 1231 922 794 531 1642 1642 587 1231 461 529 1642
  adaptation curve FRESH: 199 362 100 753 106 36 207 75 7 120 28 100 2052 2052 199 1768 1768 45 362 64 821 36 821 821 821 291 502 821 821 821 143 650 978 644 1231 1231 1231 1231 810 1231 922 794 531 1642 1642 587 1231 461 529 1642
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

