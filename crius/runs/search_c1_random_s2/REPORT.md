CRIUS CAMPAIGN 0 REPORT  run=search_c1_random_s2  arm=random
code_commit=97af44f88 dirty=True config_hash=32dfb243be9fdec9 world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1   0.1116    0.1116         0.1115         8          0
    26   0.1116    0.1116         0.1116         1         11
    51   0.1116    0.1116         0.1116         1         21
    76   0.1116    0.1116         0.1116         1         30
   101   0.1116    0.1116         0.1070         1         44
   126   0.1116    0.1116         0.1116         1         51
   151   0.1116    0.1116         0.1116         1         60
   176   5.1598    1.9969         0.8197        28        103
   201  14.2108    9.2940         4.8478        57        136
   226  21.2356   17.3290         9.7887        63        177
   251  11.1905    9.4188         5.6829        64        221
   276   9.1527    7.6461         4.2106        64        268
   300  17.2355   14.9655         9.8427        61        314
  candidates evaluated: 7208   best_ever 26.2939 (8391ff52b738b7fb)  wall 314s

BEST PROGRAM 8391ff52b738b7fb (len 63, iteration 231, modification arg@33.0+replace@22+delete@35)
  search seed 201231: fit 11.1885 succ 11/50 inter 54692 steps 88282 ws_cost 23901 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [1496.975, 0.3], "B": [1332.88, 0.4], "C": [722.374, 0.167], "D": [1068.267, 0.2], "E": [1020.515, 0.0]}
  listing:
      0  BLK_APPEND     R4, R5
      1  ACT            R7
      2  ACTI           4
      3  ACT            R7
      4  ACTI           3
      5  BLK_STATE_GET  R5, R5, R6
      6  WS_REC_SET     R3, R5, R3
      7  ACT            R7
      8  ACT            R7
      9  ACT            R7
     10  ACTI           1
     11  ACT            R7
     12  WS_REC_GET     R1, R3, R7
     13  ACTI           4
     14  ACT            R7
     15  ACTI           4
     16  ACTI           4
     17  ACTI           2
     18  ACTI           1
     19  ACTI           4
     20  ACTI           8
     21  WS_LINKS       R6, R3
     22  MOD            R4, R6, R3
     23  ACTI           6
     24  WS_REC_GET     R1, R3, R7
     25  ACTI           -6
     26  WS_LINKS       R6, R3
     27  BLK_DELETE     R6
     28  ACTI           3
     29  BLK_PATCH      R5, R4, R5
     30  WS_FIND        R2, R5
     31  ACT            R7
     32  ACTI           3
     33  ACT            R6
     34  ACT            R7
     35  ACTI           3
     36  BLK_STATE_GET  R7, R0, R5
     37  ACTI           -17
     38  ACTI           3
     39  ACTI           3
     40  ACTI           4
     41  WS_LINKS       R6, R3
     42  ACTI           3
     43  ACT            R7
     44  WS_LINKS       R6, R3
     45  ACTI           1
     46  BLK_PATCH      R5, R4, R5
     47  SUB            R7, R1, R5
     48  ACT            R7
     49  ACTI           4
     50  BRZ            R2, 0
     51  VGET           R6, R5, R7
     52  BLK_STATE_GET  R6, R1, R6
     53  ACT            R7
     54  ACTI           1
     55  BLK_STATE_SET  R2, R0, R3
     56  ACTI           4
     57  ACT            R7
     58  BRZ            R2, 0
     59  ACTI           2
     60  ACTI           3
     61  ACT            R7
     62  BRZ            R4, 0
  ancestry (62 steps, newest first): iteration/fitness/modification
    it  231  11.1885  len 63  arg@33.0+replace@22+delete@35
    it  228  13.2001  len 64  const@46+replace@6
    it  227  14.1908  len 64  duplicate@26+1->42
    it  226  19.2031  len 63  const@40+const@54+swap@41,7
    it  223  12.1759  len 63  delete@18
    it  222  14.1959  len 64  replace@52
    it  218  9.1599  len 64  delete@46+insert@56+const@24
    it  215  9.1461  len 64  arg@39.0
    it  212  11.1588  len 64  duplicate@36+2->55+const@24
    it  210  18.2317  len 62  arg@26.0+replace@53+insert@49
    it  209  12.1716  len 61  const@21+delete@59+delete@13
    it  207  8.1642  len 63  delete@26+replace@32
    it  206  7.1556  len 64  swap@34,17+duplicate@28+1->52+swap@5,26
    it  205  11.1590  len 63  delete@42
    it  204  9.1717  len 64  replace@26
    ... 48 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          47.117  26.961  27.664  27.999  46.7  26.7     8916    38056   29005.3    4.3   74.7
  ENUMERATE_C1                26.964  26.964  26.964  26.964  26.7  26.7    37456    37456       0.0    0.0    0.0
  TABLE_MEMO_C1               26.964  26.964  26.964  26.964  26.7  26.7    37456    37456     -17.9    0.0    0.0
  PROCEDURE_NOCAL_C1          26.962  26.962  26.962  26.962  26.7  26.7    37759    37756     -23.8    3.3    1.7
  ENUMERATE_VM_C1             25.287  25.287  25.287  25.287  25.0  25.0    37856    37856       0.0    0.0    0.0
  QUIT_C1                     19.605  19.605  19.605  19.605  19.3  19.3     9448     9448       0.0    0.0    0.0
  RANDOM_C1                   10.160  10.160  10.160  10.160  10.0  10.0    62546    62546       0.0    0.0    0.0
  ancestor118_it297_07080731   9.835   9.835   9.835   9.835   9.7   9.7    60111    60111       0.0    0.0    0.0
  top1_d95cba58ac8f3f95        8.487   8.487   8.487   8.487   8.3   8.3    62843    62843       0.0    0.0    0.0
  top2_bb032553939e52e6        8.487   8.487   8.487   8.487   8.3   8.3    62843    62843       0.0    0.0    0.0
  top3_ae1ac55fa01b24ba        8.486   8.486   8.486   8.486   8.3   8.3    62843    62843       0.0    0.0    0.0
  bestever_8391ff52b738b7fb    8.146   8.146   8.146   8.146   8.0   8.0    64418    64418       0.0    0.0    0.0
  ancestor60_it226_ac9d84497   8.145   8.145   8.145   8.145   8.0   8.0    64716    64716       0.0    0.0    0.0
  contemp_8921a8a056084680     7.482   7.482   7.482   7.482   7.3   7.3    63536    63536       0.0    0.0    0.0
  contemp_e876dba148999d16     7.144   7.144   7.144   7.144   7.0   7.0    64328    64328       0.0    0.0    0.0
  contemp_a093a010b74b0070     5.143   5.143   5.143   5.143   5.0   5.0    64740    64740       0.0    0.0    0.0
  ancestor1_it0_917933876bd5   0.108   0.108   0.108   0.108   0.0   0.0        0        0       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.00/ 455.13   14.90/ 539.10   36.22/ 623.47  177.39/1089.94  477.07/1237.03
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31  615.85/ 615.85 1086.47/1086.47 1232.75/1232.75
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34  616.29/ 615.86 1086.97/1086.48 1233.28/1232.76
  PROCEDURE_NOCAL_C1          444.13/ 443.81  528.11/ 527.79  619.85/ 619.71 1088.59/1088.26 1236.48/1234.94
  ENUMERATE_VM_C1             494.04/ 494.04  523.26/ 523.26  664.50/ 664.50 1116.70/1116.70 1283.87/1283.87
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31  800.00/ 800.00 1200.00/1200.00 1400.00/1400.00
  RANDOM_C1                  1661.96/1661.96 1626.54/1626.54  726.73/ 726.73 1161.23/1161.23 1244.20/1244.20
  ancestor118_it297_07080731 1543.17/1543.17 1573.28/1573.28  743.48/ 743.48 1133.04/1133.04 1260.11/1260.11
  top1_d95cba58ac8f3f95      1758.85/1758.85 1648.71/1648.71  719.08/ 719.08 1054.68/1054.68 1384.38/1384.38
  top2_bb032553939e52e6      1758.85/1758.85 1648.71/1648.71  719.08/ 719.08 1054.68/1054.68 1384.38/1384.38
  top3_ae1ac55fa01b24ba      1760.22/1760.22 1650.00/1650.00  719.64/ 719.64 1055.51/1055.51 1385.46/1385.46
  bestever_8391ff52b738b7fb  1865.34/1865.34 1752.00/1752.00  725.82/ 725.82 1078.67/1078.67 1258.59/1258.59
  ancestor60_it226_ac9d84497 1938.53/1938.53 1668.19/1668.19  724.68/ 724.68 1078.76/1078.76 1299.51/1299.51
  contemp_8921a8a056084680   1772.17/1772.17 1657.72/1657.72  763.97/ 763.97 1069.79/1069.79 1369.73/1369.73
  contemp_e876dba148999d16   1848.94/1848.94 1671.85/1671.85  749.85/ 749.85 1172.05/1172.05 1257.62/1257.62
  contemp_a093a010b74b0070   1719.14/1719.14 1798.61/1798.61  796.66/ 796.66 1155.09/1155.09 1251.95/1251.95
  ancestor1_it0_917933876bd5 2000.13/2000.13 2000.13/2000.13  800.13/ 800.13 1200.13/1200.13 1400.13/1400.13

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            36/36    33    27/30   167     6/12   809    11/12   117    30/30   301    30/30    14
  ENUMERATE_C1                  13/36   613     5/30  1082     2/12  1350     2/12  1106    29/30   431    29/30   514
  TABLE_MEMO_C1                 13/36   613     5/30  1082     2/12  1350     2/12  1106    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1            13/36   617     5/30  1084     2/12  1352     2/12  1108    29/30   442    29/30   526
  ENUMERATE_VM_C1               11/36   635     6/30  1068     2/12  1350     2/12  1107    27/30   472    27/30   500
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  RANDOM_C1                      6/36   720     2/30  1150     2/12  1430     2/12  1034    10/30  1646     8/30  1610
  ancestor118_it297_07080731     4/36   727     3/30  1108     2/12  1378     2/12  1085     9/30  1508     9/30  1538
  top1_d95cba58ac8f3f95          7/36   702     5/30  1030     0/12  1600     1/12  1105     5/30  1718     7/30  1611
  top2_bb032553939e52e6          7/36   702     5/30  1030     0/12  1600     1/12  1105     5/30  1718     7/30  1611
  top3_ae1ac55fa01b24ba          7/36   702     5/30  1030     0/12  1600     1/12  1105     5/30  1718     7/30  1611
  bestever_8391ff52b738b7fb      8/36   711     5/30  1057     2/12  1340     1/12  1126     3/30  1828     5/30  1717
  ancestor60_it226_ac9d84497     7/36   711     5/30  1059     1/12  1469     2/12  1081     2/30  1902     7/30  1637
  contemp_8921a8a056084680       4/36   745     5/30  1044     1/12  1473     0/12  1200     5/30  1729     7/30  1617
  contemp_e876dba148999d16       5/36   731     2/30  1143     3/12  1252     0/12  1200     4/30  1802     7/30  1630
  contemp_a093a010b74b0070       1/36   778     2/30  1128     3/12  1245     0/12  1200     5/30  1679     4/30  1756
  ancestor1_it0_917933876bd5     0/36     0     0/30     0     0/12     0     0/12     0     0/30     0     0/30     0

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1           310.58  1153.44   310.58   310.58  1153.44  1153.44  1153.44   4.0
  ENUMERATE_C1                1151.49       --  1151.49  1151.49  1151.49  1151.49  1151.49   0.0
  TABLE_MEMO_C1               1152.00       --  1151.52  1152.00  1151.52  1151.52  1151.52   0.0
  PROCEDURE_NOCAL_C1          1154.32  1153.42  1154.32  1154.32  1153.42  1153.42  1153.42   1.3
  ENUMERATE_VM_C1             1191.00       --  1191.00  1191.00  1191.00  1191.00  1191.00   0.0
  QUIT_C1                     1288.89       --  1288.89  1288.89  1288.89  1288.89  1288.89   0.0
  RANDOM_C1                   1198.10       --  1198.10  1198.10  1198.10  1198.10  1198.10   0.0
  ancestor118_it297_07080731  1189.52       --  1189.52  1189.52  1189.52  1189.52  1189.52   0.0
  top1_d95cba58ac8f3f95       1201.21       --  1201.21  1201.21  1201.21  1201.21  1201.21   0.0
  top2_bb032553939e52e6       1201.21       --  1201.21  1201.21  1201.21  1201.21  1201.21   0.0
  top3_ae1ac55fa01b24ba       1202.15       --  1202.15  1202.15  1202.15  1202.15  1202.15   0.0
  bestever_8391ff52b738b7fb   1158.63       --  1158.63  1158.63  1158.63  1158.63  1158.63   0.0
  ancestor60_it226_ac9d84497  1176.87       --  1176.87  1176.87  1176.87  1176.87  1176.87   0.0
  contemp_8921a8a056084680    1203.10       --  1203.10  1203.10  1203.10  1203.10  1203.10   0.0
  contemp_e876dba148999d16    1210.08       --  1210.08  1210.08  1210.08  1210.08  1210.08   0.0
  contemp_a093a010b74b0070    1198.14       --  1198.14  1198.14  1198.14  1198.14  1198.14   0.0
  ancestor1_it0_917933876bd5  1289.02       --  1289.02  1289.02  1289.02  1289.02  1289.02   0.0

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
  ancestor118_it297_07080731bdb87813
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [3, 13, 13] vs FRESH [3, 13, 13]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [31129.0, 30833.4, 29036.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1262.4, 1167.32, 1138.83] vs CODE_ONLY [1262.4, 1167.32, 1138.83]
    4_scramble_or_reset_damages            0/3  eff ACC [3.112, 13.202, 13.192] SCR [3.112, 13.202, 13.192] RESET [3.112, 13.202, 13.192]
    5_transfers_to_fresh_copy              0/3  FULL [1262.4, 1167.32, 1138.83] vs ACC remainder [1262.4, 1167.32, 1138.83]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1262.4, 1167.32, 1138.83]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1262.4, 1167.32, 1138.83] STORAGE_MATCHED [1262.4, 1167.32, 1138.83] vs ACC remainder [1262.4, 1167.32, 1138.83]
  top1_d95cba58ac8f3f95
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 15, 4] vs FRESH [6, 15, 4]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [28765.3, 31002.7, 30984.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1133.12, 1254.42, 1216.1] vs CODE_ONLY [1133.12, 1254.42, 1216.1]
    4_scramble_or_reset_damages            0/3  eff ACC [6.135, 15.212, 4.112] SCR [6.135, 15.212, 4.112] RESET [6.135, 15.212, 4.112]
    5_transfers_to_fresh_copy              0/3  FULL [1133.12, 1254.42, 1216.1] vs ACC remainder [1133.12, 1254.42, 1216.1]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1133.12, 1254.42, 1216.1]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1133.12, 1254.42, 1216.1] STORAGE_MATCHED [1133.12, 1254.42, 1216.1] vs ACC remainder [1133.12, 1254.42, 1216.1]
  top2_bb032553939e52e6
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 15, 4] vs FRESH [6, 15, 4]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [28765.3, 31002.7, 30984.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1133.12, 1254.42, 1216.1] vs CODE_ONLY [1133.12, 1254.42, 1216.1]
    4_scramble_or_reset_damages            0/3  eff ACC [6.135, 15.212, 4.112] SCR [6.135, 15.212, 4.112] RESET [6.135, 15.212, 4.112]
    5_transfers_to_fresh_copy              0/3  FULL [1133.12, 1254.42, 1216.1] vs ACC remainder [1133.12, 1254.42, 1216.1]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1133.12, 1254.42, 1216.1]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1133.12, 1254.42, 1216.1] STORAGE_MATCHED [1133.12, 1254.42, 1216.1] vs ACC remainder [1133.12, 1254.42, 1216.1]
  top3_ae1ac55fa01b24ba
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 15, 4] vs FRESH [6, 15, 4]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [28787.7, 31026.9, 31008.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1134.01, 1255.4, 1217.05] vs CODE_ONLY [1134.01, 1255.4, 1217.05]
    4_scramble_or_reset_damages            0/3  eff ACC [6.135, 15.212, 4.112] SCR [6.135, 15.212, 4.112] RESET [6.135, 15.212, 4.112]
    5_transfers_to_fresh_copy              0/3  FULL [1134.01, 1255.4, 1217.05] vs ACC remainder [1134.01, 1255.4, 1217.05]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1134.01, 1255.4, 1217.05]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1134.01, 1255.4, 1217.05] STORAGE_MATCHED [1134.01, 1255.4, 1217.05] vs ACC remainder [1134.01, 1255.4, 1217.05]
  bestever_8391ff52b738b7fb
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [3, 13, 8] vs FRESH [3, 13, 8]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [31949.2, 25622.0, 31124.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1259.59, 995.16, 1221.15] vs CODE_ONLY [1259.59, 995.16, 1221.15]
    4_scramble_or_reset_damages            0/3  eff ACC [3.119, 13.172, 8.147] SCR [3.119, 13.172, 8.147] RESET [3.119, 13.172, 8.147]
    5_transfers_to_fresh_copy              0/3  FULL [1259.59, 995.16, 1221.15] vs ACC remainder [1259.59, 995.16, 1221.15]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1259.59, 995.16, 1221.15]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1259.59, 995.16, 1221.15] STORAGE_MATCHED [1259.59, 995.16, 1221.15] vs ACC remainder [1259.59, 995.16, 1221.15]
  ancestor60_it226_ac9d8449713c13a1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [8, 6, 10] vs FRESH [8, 6, 10]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [30076.5, 29940.0, 29623.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1176.97, 1207.88, 1145.77] vs CODE_ONLY [1176.97, 1207.88, 1145.77]
    4_scramble_or_reset_damages            0/3  eff ACC [8.144, 6.13, 10.16] SCR [8.144, 6.13, 10.16] RESET [8.144, 6.13, 10.16]
    5_transfers_to_fresh_copy              0/3  FULL [1176.97, 1207.88, 1145.77] vs ACC remainder [1176.97, 1207.88, 1145.77]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1176.97, 1207.88, 1145.77]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1176.97, 1207.88, 1145.77] STORAGE_MATCHED [1176.97, 1207.88, 1145.77] vs ACC remainder [1176.97, 1207.88, 1145.77]
  contemp_8921a8a056084680
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 9, 7] vs FRESH [6, 9, 7]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [30030.8, 31713.8, 30725.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1198.9, 1234.1, 1176.3] vs CODE_ONLY [1198.9, 1234.1, 1176.3]
    4_scramble_or_reset_damages            0/3  eff ACC [6.138, 9.167, 7.142] SCR [6.138, 9.167, 7.142] RESET [6.138, 9.167, 7.142]
    5_transfers_to_fresh_copy              0/3  FULL [1198.9, 1234.1, 1176.3] vs ACC remainder [1198.9, 1234.1, 1176.3]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1198.9, 1234.1, 1176.3]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1198.9, 1234.1, 1176.3] STORAGE_MATCHED [1198.9, 1234.1, 1176.3] vs ACC remainder [1198.9, 1234.1, 1176.3]
  contemp_e876dba148999d16
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [10, 9, 2] vs FRESH [10, 9, 2]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [29395.6, 30881.1, 32062.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1153.09, 1242.97, 1234.19] vs CODE_ONLY [1153.09, 1242.97, 1234.19]
    4_scramble_or_reset_damages            0/3  eff ACC [10.164, 9.152, 2.117] SCR [10.164, 9.152, 2.117] RESET [10.164, 9.152, 2.117]
    5_transfers_to_fresh_copy              0/3  FULL [1153.09, 1242.97, 1234.19] vs ACC remainder [1153.09, 1242.97, 1234.19]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1153.09, 1242.97, 1234.19]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1153.09, 1242.97, 1234.19] STORAGE_MATCHED [1153.09, 1242.97, 1234.19] vs ACC remainder [1153.09, 1242.97, 1234.19]
  contemp_a093a010b74b0070
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [3, 8, 4] vs FRESH [3, 8, 4]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [30011.6, 30590.4, 32776.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1121.11, 1153.27, 1320.03] vs CODE_ONLY [1121.11, 1153.27, 1320.03]
    4_scramble_or_reset_damages            0/3  eff ACC [3.118, 8.175, 4.136] SCR [3.118, 8.175, 4.136] RESET [3.118, 8.175, 4.136]
    5_transfers_to_fresh_copy              0/3  FULL [1121.11, 1153.27, 1320.03] vs ACC remainder [1121.11, 1153.27, 1320.03]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1121.11, 1153.27, 1320.03]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1121.11, 1153.27, 1320.03] STORAGE_MATCHED [1121.11, 1153.27, 1320.03] vs ACC remainder [1121.11, 1153.27, 1320.03]
  ancestor1_it0_917933876bd532c2
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [32803.9, 32803.9, 32803.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1289.02, 1289.02, 1289.02] vs CODE_ONLY [1289.02, 1289.02, 1289.02]
    4_scramble_or_reset_damages            0/3  eff ACC [0.108, 0.108, 0.108] SCR [0.108, 0.108, 0.108] RESET [0.108, 0.108, 0.108]
    5_transfers_to_fresh_copy              0/3  FULL [1289.02, 1289.02, 1289.02] vs ACC remainder [1289.02, 1289.02, 1289.02]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1289.02, 1289.02, 1289.02]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1289.02, 1289.02, 1289.02] STORAGE_MATCHED [1289.02, 1289.02, 1289.02] vs ACC remainder [1289.02, 1289.02, 1289.02]

MACHINERY OF top1_d95cba58ac8f3f95 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   0     0
    task  9:     0    0    0    0    0 |   0     0
    task 19:     0    0    0    0    0 |   0     0
    task 31:     0    0    0    0    0 |   0     0
    task 41:     0    0    0    0    0 |   0     0
    task 49:     0    0    0    0    0 |   0     0
  artifact events: 0 (create 0, delete 0, patch/append 0); invocations by block: {}; edges: 0
  adaptation curve ACC:   2047 2047 2047 2047 2047 2047 2047 2047 2047 2047 2047 2047 2047 2047 4 2047 2047 2047 2047 2047 819 819 177 819 819 3 819 819 819 819 819 819 1228 1228 81 1228 1228 7 1228 246 1228 1228 1228 1638 1638 1638 1228 1228 1228 1638
  adaptation curve FRESH: 2047 2047 2047 2047 2047 2047 2047 2047 2047 2047 2047 2047 2047 2047 4 2047 2047 2047 2047 2047 819 819 177 819 819 3 819 819 819 819 819 819 1228 1228 81 1228 1228 7 1228 246 1228 1228 1228 1638 1638 1638 1228 1228 1228 1638
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

