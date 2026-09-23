CRIUS CAMPAIGN 0 REPORT  run=search_c1_random_s3  arm=random
code_commit=97af44f88 dirty=True config_hash=32dfb243be9fdec9 world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1   3.1293    1.1180         0.3538        19          2
    26   3.1406    0.4902         0.1116         4         11
    51   0.1116    0.1116         0.1116         1         16
    76   0.1116    0.1116         0.1116         1         25
   101   0.1116    0.1116         0.1070         1         35
   126   0.1116    0.1116         0.1070         1         46
   151   0.1116    0.1116         0.1070         1         57
   176   1.1161    0.9768         0.3488         2         71
   201   0.1116    0.1116         0.1070         1         82
   226   0.1116    0.1116         0.1023         1         89
   251   1.1227    0.2380         0.1537         2        101
   276   2.1339    0.3644         0.1959         2        116
   300   0.1116    0.1116         0.1116         1        126
  candidates evaluated: 7208   best_ever 7.1734 (46adb031e81a7c7f)  wall 126s

BEST PROGRAM 46adb031e81a7c7f (len 6, iteration 9, modification insert@3)
  search seed 301009: fit 7.1734 succ 7/50 inter 56831 steps 170464 ws_cost 0 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [1443.441, 0.3], "B": [1443.544, 0.3], "C": [823.99, 0.0], "D": [1235.99, 0.0], "E": [927.251, 0.125]}
  listing:
      0  BLK_REC_END    R5
      1  ACTI           7
      2  DIV            R7, R0, R2
      3  JMP            1
      4  WS_LINK_GET    R4, R0, R7
      5  WS_LINKS       R0, R6
  ancestry (8 steps, newest first): iteration/fitness/modification
    it    9  7.1734  len  6  insert@3
    it    8  1.1227  len  5  swap@1,0+insert@0
    it    7  0.1116  len  4  insert@4+const@1+delete@3
    it    6  3.1451  len  4  delete@0
    it    5  0.1116  len  5  delete@3+delete@0+duplicate@3+1->1
    it    4  1.1227  len  6  replace@2+const@2
    it    3  0.1116  len  6  delete@6
    it    1  0.1116  len  7  delete@6+delete@0+duplicate@4+1->1
    it    0  0.1116  len  8  random_init

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          47.117  26.961  27.664  27.999  46.7  26.7     8916    38056   29005.3    4.3   74.7
  ENUMERATE_C1                26.964  26.964  26.964  26.964  26.7  26.7    37456    37456       0.0    0.0    0.0
  TABLE_MEMO_C1               26.964  26.964  26.964  26.964  26.7  26.7    37456    37456     -17.9    0.0    0.0
  PROCEDURE_NOCAL_C1          26.962  26.962  26.962  26.962  26.7  26.7    37759    37756     -23.8    3.3    1.7
  ENUMERATE_VM_C1             25.287  25.287  25.287  25.287  25.0  25.0    37856    37856       0.0    0.0    0.0
  QUIT_C1                     19.605  19.605  19.605  19.605  19.3  19.3     9448     9448       0.0    0.0    0.0
  RANDOM_C1                   10.160  10.160  10.160  10.160  10.0  10.0    62546    62546       0.0    0.0    0.0
  top2_0077b1c7c23b0e2e        0.108   0.108   0.108   0.108   0.0   0.0        0        0       0.0    0.0    0.0
  top3_010ba9c537cbbdb7        0.108   0.108   0.108   0.108   0.0   0.0        0        0       0.0    0.0    0.0
  ancestor54_it250_0722c3995   0.108   0.108   0.108   0.108   0.0   0.0        0        0       0.0    0.0    0.0
  top1_0075e6ffbef86f40        0.108   0.108   0.108   0.108   0.0   0.0        0        0       0.0    0.0    0.0
  contemp_761baf27a2e1e08e     0.108   0.108   0.108   0.108   0.0   0.0       50       50       0.0    0.0    0.0
  contemp_53758e98b1c38e29     0.108   0.108   0.108   0.108   0.0   0.0        0        0       0.0    0.0    0.0
  contemp_ee9ec0a76041d91e     0.108   0.108   0.108   0.108   0.0   0.0        0        0       0.0    0.0    0.0
  ancestor28_it71_0780ded709   0.108   0.108   0.108   0.108   0.0   0.0       50       50       0.0    0.0    0.0
  ancestor1_it0_085e5a21a759   0.108   0.108   0.108   0.108   0.0   0.0        0        0       0.0   32.0    0.0
  bestever_46adb031e81a7c7f    0.096   0.096   0.096   0.096   0.0   0.0    72800    72800       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.00/ 455.13   14.90/ 539.10   36.22/ 623.47  177.39/1089.94  477.07/1237.03
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31  615.85/ 615.85 1086.47/1086.47 1232.75/1232.75
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34  616.29/ 615.86 1086.97/1086.48 1233.28/1232.76
  PROCEDURE_NOCAL_C1          444.13/ 443.81  528.11/ 527.79  619.85/ 619.71 1088.59/1088.26 1236.48/1234.94
  ENUMERATE_VM_C1             494.04/ 494.04  523.26/ 523.26  664.50/ 664.50 1116.70/1116.70 1283.87/1283.87
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31  800.00/ 800.00 1200.00/1200.00 1400.00/1400.00
  RANDOM_C1                  1661.96/1661.96 1626.54/1626.54  726.73/ 726.73 1161.23/1161.23 1244.20/1244.20
  top2_0077b1c7c23b0e2e      2000.01/2000.01 2000.01/2000.01  800.01/ 800.01 1200.01/1200.01 1400.01/1400.01
  top3_010ba9c537cbbdb7      2000.01/2000.01 2000.01/2000.01  800.01/ 800.01 1200.01/1200.01 1400.01/1400.01
  ancestor54_it250_0722c3995 2000.01/2000.01 2000.01/2000.01  800.01/ 800.01 1200.01/1200.01 1400.01/1400.01
  top1_0075e6ffbef86f40      2000.02/2000.02 2000.02/2000.02  800.02/ 800.02 1200.02/1200.02 1400.02/1400.02
  contemp_761baf27a2e1e08e   2000.02/2000.02 2000.02/2000.02  800.02/ 800.02 1200.02/1200.02 1400.02/1400.02
  contemp_53758e98b1c38e29   2000.02/2000.02 2000.02/2000.02  800.02/ 800.02 1200.02/1200.02 1400.02/1400.02
  contemp_ee9ec0a76041d91e   2000.04/2000.04 2000.04/2000.04  800.04/ 800.04 1200.04/1200.04 1400.04/1400.04
  ancestor28_it71_0780ded709 2000.03/2000.03 2000.03/2000.03  800.03/ 800.03 1200.03/1200.03 1400.03/1400.03
  ancestor1_it0_085e5a21a759 2000.08/2000.08 2000.08/2000.08  800.08/ 800.08 1200.08/1200.08 1400.08/1400.08
  bestever_46adb031e81a7c7f  2059.99/2059.99 2059.99/2059.99  823.99/ 823.99 1235.99/1235.99 1441.99/1441.99

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            36/36    33    27/30   167     6/12   809    11/12   117    30/30   301    30/30    14
  ENUMERATE_C1                  13/36   613     5/30  1082     2/12  1350     2/12  1106    29/30   431    29/30   514
  TABLE_MEMO_C1                 13/36   613     5/30  1082     2/12  1350     2/12  1106    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1            13/36   617     5/30  1084     2/12  1352     2/12  1108    29/30   442    29/30   526
  ENUMERATE_VM_C1               11/36   635     6/30  1068     2/12  1350     2/12  1107    27/30   472    27/30   500
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  RANDOM_C1                      6/36   720     2/30  1150     2/12  1430     2/12  1034    10/30  1646     8/30  1610
  top2_0077b1c7c23b0e2e          0/36     0     0/30     0     0/12     0     0/12     0     0/30     0     0/30     0
  top3_010ba9c537cbbdb7          0/36     0     0/30     0     0/12     0     0/12     0     0/30     0     0/30     0
  ancestor54_it250_0722c3995     0/36     0     0/30     0     0/12     0     0/12     0     0/30     0     0/30     0
  top1_0075e6ffbef86f40          0/36     0     0/30     0     0/12     0     0/12     0     0/30     0     0/30     0
  contemp_761baf27a2e1e08e       0/36     1     0/30     1     0/12     1     0/12     1     0/30     1     0/30     1
  contemp_53758e98b1c38e29       0/36     0     0/30     0     0/12     0     0/12     0     0/30     0     0/30     0
  contemp_ee9ec0a76041d91e       0/36     0     0/30     0     0/12     0     0/12     0     0/30     0     0/30     0
  ancestor28_it71_0780ded709     0/36     1     0/30     1     0/12     1     0/12     1     0/30     1     0/30     1
  ancestor1_it0_085e5a21a759     0/36     0     0/30     0     0/12     0     0/12     0     0/30     0     0/30     0
  bestever_46adb031e81a7c7f      0/36   800     0/30  1200     0/12  1600     0/12  1200     0/30  2000     0/30  2000

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1           310.58  1153.44   310.58   310.58  1153.44  1153.44  1153.44   4.0
  ENUMERATE_C1                1151.49       --  1151.49  1151.49  1151.49  1151.49  1151.49   0.0
  TABLE_MEMO_C1               1152.00       --  1151.52  1152.00  1151.52  1151.52  1151.52   0.0
  PROCEDURE_NOCAL_C1          1154.32  1153.42  1154.32  1154.32  1153.42  1153.42  1153.42   1.3
  ENUMERATE_VM_C1             1191.00       --  1191.00  1191.00  1191.00  1191.00  1191.00   0.0
  QUIT_C1                     1288.89       --  1288.89  1288.89  1288.89  1288.89  1288.89   0.0
  RANDOM_C1                   1198.10       --  1198.10  1198.10  1198.10  1198.10  1198.10   0.0
  top2_0077b1c7c23b0e2e       1288.90       --  1288.90  1288.90  1288.90  1288.90  1288.90   0.0
  top3_010ba9c537cbbdb7       1288.90       --  1288.90  1288.90  1288.90  1288.90  1288.90   0.0
  ancestor54_it250_0722c3995  1288.90       --  1288.90  1288.90  1288.90  1288.90  1288.90   0.0
  top1_0075e6ffbef86f40       1288.91       --  1288.91  1288.91  1288.91  1288.91  1288.91   0.0
  contemp_761baf27a2e1e08e    1288.91       --  1288.91  1288.91  1288.91  1288.91  1288.91   0.0
  contemp_53758e98b1c38e29    1288.91       --  1288.91  1288.91  1288.91  1288.91  1288.91   0.0
  contemp_ee9ec0a76041d91e    1288.93       --  1288.93  1288.93  1288.93  1288.93  1288.93   0.0
  ancestor28_it71_0780ded709  1288.92       --  1288.92  1288.92  1288.92  1288.92  1288.92   0.0
  ancestor1_it0_085e5a21a759  1288.97  1288.97  1288.97  1288.97  1288.97  1288.97  1288.97  32.0
  bestever_46adb031e81a7c7f   1327.55       --  1327.55  1327.55  1327.55  1327.55  1327.55   0.0

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
  top2_0077b1c7c23b0e2e
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [32800.3, 32800.3, 32800.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1288.9, 1288.9, 1288.9] vs CODE_ONLY [1288.9, 1288.9, 1288.9]
    4_scramble_or_reset_damages            0/3  eff ACC [0.108, 0.108, 0.108] SCR [0.108, 0.108, 0.108] RESET [0.108, 0.108, 0.108]
    5_transfers_to_fresh_copy              0/3  FULL [1288.9, 1288.9, 1288.9] vs ACC remainder [1288.9, 1288.9, 1288.9]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1288.9, 1288.9, 1288.9]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1288.9, 1288.9, 1288.9] STORAGE_MATCHED [1288.9, 1288.9, 1288.9] vs ACC remainder [1288.9, 1288.9, 1288.9]
  top3_010ba9c537cbbdb7
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [32800.3, 32800.3, 32800.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1288.9, 1288.9, 1288.9] vs CODE_ONLY [1288.9, 1288.9, 1288.9]
    4_scramble_or_reset_damages            0/3  eff ACC [0.108, 0.108, 0.108] SCR [0.108, 0.108, 0.108] RESET [0.108, 0.108, 0.108]
    5_transfers_to_fresh_copy              0/3  FULL [1288.9, 1288.9, 1288.9] vs ACC remainder [1288.9, 1288.9, 1288.9]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1288.9, 1288.9, 1288.9]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1288.9, 1288.9, 1288.9] STORAGE_MATCHED [1288.9, 1288.9, 1288.9] vs ACC remainder [1288.9, 1288.9, 1288.9]
  ancestor54_it250_0722c39950ded333
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [32800.3, 32800.3, 32800.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1288.9, 1288.9, 1288.9] vs CODE_ONLY [1288.9, 1288.9, 1288.9]
    4_scramble_or_reset_damages            0/3  eff ACC [0.108, 0.108, 0.108] SCR [0.108, 0.108, 0.108] RESET [0.108, 0.108, 0.108]
    5_transfers_to_fresh_copy              0/3  FULL [1288.9, 1288.9, 1288.9] vs ACC remainder [1288.9, 1288.9, 1288.9]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1288.9, 1288.9, 1288.9]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1288.9, 1288.9, 1288.9] STORAGE_MATCHED [1288.9, 1288.9, 1288.9] vs ACC remainder [1288.9, 1288.9, 1288.9]
  top1_0075e6ffbef86f40
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [32800.6, 32800.6, 32800.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1288.91, 1288.91, 1288.91] vs CODE_ONLY [1288.91, 1288.91, 1288.91]
    4_scramble_or_reset_damages            0/3  eff ACC [0.108, 0.108, 0.108] SCR [0.108, 0.108, 0.108] RESET [0.108, 0.108, 0.108]
    5_transfers_to_fresh_copy              0/3  FULL [1288.91, 1288.91, 1288.91] vs ACC remainder [1288.91, 1288.91, 1288.91]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1288.91, 1288.91, 1288.91]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1288.91, 1288.91, 1288.91] STORAGE_MATCHED [1288.91, 1288.91, 1288.91] vs ACC remainder [1288.91, 1288.91, 1288.91]
  contemp_761baf27a2e1e08e
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [32800.6, 32800.6, 32800.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1288.91, 1288.91, 1288.91] vs CODE_ONLY [1288.91, 1288.91, 1288.91]
    4_scramble_or_reset_damages            0/3  eff ACC [0.108, 0.108, 0.108] SCR [0.108, 0.108, 0.108] RESET [0.108, 0.108, 0.108]
    5_transfers_to_fresh_copy              0/3  FULL [1288.91, 1288.91, 1288.91] vs ACC remainder [1288.91, 1288.91, 1288.91]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1288.91, 1288.91, 1288.91]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1288.91, 1288.91, 1288.91] STORAGE_MATCHED [1288.91, 1288.91, 1288.91] vs ACC remainder [1288.91, 1288.91, 1288.91]
  contemp_53758e98b1c38e29
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [32800.6, 32800.6, 32800.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1288.91, 1288.91, 1288.91] vs CODE_ONLY [1288.91, 1288.91, 1288.91]
    4_scramble_or_reset_damages            0/3  eff ACC [0.108, 0.108, 0.108] SCR [0.108, 0.108, 0.108] RESET [0.108, 0.108, 0.108]
    5_transfers_to_fresh_copy              0/3  FULL [1288.91, 1288.91, 1288.91] vs ACC remainder [1288.91, 1288.91, 1288.91]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1288.91, 1288.91, 1288.91]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1288.91, 1288.91, 1288.91] STORAGE_MATCHED [1288.91, 1288.91, 1288.91] vs ACC remainder [1288.91, 1288.91, 1288.91]
  contemp_ee9ec0a76041d91e
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [32801.2, 32801.2, 32801.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1288.93, 1288.93, 1288.93] vs CODE_ONLY [1288.93, 1288.93, 1288.93]
    4_scramble_or_reset_damages            0/3  eff ACC [0.108, 0.108, 0.108] SCR [0.108, 0.108, 0.108] RESET [0.108, 0.108, 0.108]
    5_transfers_to_fresh_copy              0/3  FULL [1288.93, 1288.93, 1288.93] vs ACC remainder [1288.93, 1288.93, 1288.93]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1288.93, 1288.93, 1288.93]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1288.93, 1288.93, 1288.93] STORAGE_MATCHED [1288.93, 1288.93, 1288.93] vs ACC remainder [1288.93, 1288.93, 1288.93]
  ancestor28_it71_0780ded709bdf167
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [32800.9, 32800.9, 32800.9] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1288.92, 1288.92, 1288.92] vs CODE_ONLY [1288.92, 1288.92, 1288.92]
    4_scramble_or_reset_damages            0/3  eff ACC [0.108, 0.108, 0.108] SCR [0.108, 0.108, 0.108] RESET [0.108, 0.108, 0.108]
    5_transfers_to_fresh_copy              0/3  FULL [1288.92, 1288.92, 1288.92] vs ACC remainder [1288.92, 1288.92, 1288.92]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1288.92, 1288.92, 1288.92]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1288.92, 1288.92, 1288.92] STORAGE_MATCHED [1288.92, 1288.92, 1288.92] vs ACC remainder [1288.92, 1288.92, 1288.92]
  ancestor1_it0_085e5a21a759324b
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [32802.4, 32802.4, 32802.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1288.97, 1288.97, 1288.97] vs CODE_ONLY [1288.97, 1288.97, 1288.97]
    4_scramble_or_reset_damages            0/3  eff ACC [0.108, 0.108, 0.108] SCR [0.108, 0.108, 0.108] RESET [0.108, 0.108, 0.108]
    5_transfers_to_fresh_copy              0/3  FULL [1288.97, 1288.97, 1288.97] vs ACC remainder [1288.97, 1288.97, 1288.97]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [1288.97, 1288.97, 1288.97] vs ACC remainder [1288.97, 1288.97, 1288.97]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1288.97, 1288.97, 1288.97] STORAGE_MATCHED [1288.97, 1288.97, 1288.97] vs ACC remainder [1288.97, 1288.97, 1288.97]
  bestever_46adb031e81a7c7f
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [33783.7, 33783.7, 33783.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1327.55, 1327.55, 1327.55] vs CODE_ONLY [1327.55, 1327.55, 1327.55]
    4_scramble_or_reset_damages            0/3  eff ACC [0.096, 0.096, 0.096] SCR [0.096, 0.096, 0.096] RESET [0.096, 0.096, 0.096]
    5_transfers_to_fresh_copy              0/3  FULL [1327.55, 1327.55, 1327.55] vs ACC remainder [1327.55, 1327.55, 1327.55]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1327.55, 1327.55, 1327.55]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1327.55, 1327.55, 1327.55] STORAGE_MATCHED [1327.55, 1327.55, 1327.55] vs ACC remainder [1327.55, 1327.55, 1327.55]

MACHINERY OF top1_0075e6ffbef86f40 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   0     0
    task  9:     0    0    0    0    0 |   0     0
    task 19:     0    0    0    0    0 |   0     0
    task 31:     0    0    0    0    0 |   0     0
    task 41:     0    0    0    0    0 |   0     0
    task 49:     0    0    0    0    0 |   0     0
  artifact events: 0 (create 0, delete 0, patch/append 0); invocations by block: {}; edges: 0
  adaptation curve ACC:   2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 800 800 800 800 800 800 800 800 800 800 800 800 1200 1200 1200 1200 1200 1200 1200 1200 1200 1200 1200 1600 1600 1600 1200 1200 1200 1600
  adaptation curve FRESH: 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 2000 800 800 800 800 800 800 800 800 800 800 800 800 1200 1200 1200 1200 1200 1200 1200 1200 1200 1200 1200 1600 1600 1600 1200 1200 1200 1600
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

