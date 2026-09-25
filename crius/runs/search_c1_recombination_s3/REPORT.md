CRIUS CAMPAIGN 0 REPORT  run=search_c1_recombination_s3  arm=recombination
code_commit=97af44f88 dirty=True config_hash=32dfb243be9fdec9 world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  31.3640   29.9823        11.2624        42          8
    26  31.3454   31.3421        17.3059        42         61
    51  26.3289   24.5730        16.1168        64        119
    76  28.3172   23.0184        13.3463        64        176
   101  40.3823   39.5123        31.4010        62        235
   126  25.3131   25.3131        15.2110        59        291
   151  30.3504   29.9739        21.2339        52        352
   176  26.3019   26.3019        20.6341        51        405
   201  46.4470   42.9181        21.1674        55        451
   226  41.3614   37.9826        24.6866        46        503
   251  33.3439   31.5662        24.3588        64        559
   276  29.3299   28.9532        19.2095        63        604
   300  28.3036   25.7902        17.6869        64        648
  candidates evaluated: 7208   best_ever 46.4470 (fc9b4f48c2ff896c)  wall 648s

BEST PROGRAM fc9b4f48c2ff896c (len 55, iteration 201, modification replace@48+const@1+duplicate@1+1->41+splice@41<-donor[15:20]:1804024b0e2aa586)
  search seed 301201: fit 46.4470 succ 46/50 inter 9035 steps 41333 ws_cost 4780 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [96.265, 1.0], "B": [79.156, 1.0], "C": [164.334, 0.917], "D": [326.308, 0.8], "E": [313.354, 0.875]}
  listing:
      0  INPUT          R1, num_ops
      1  CONST          R5, 5
      2  BLK_INVOKE     R2
      3  BLK_COMPOSE    R4, R2, R0
      4  BRZ            R3, 38
      5  ADD            R7, R0, R5
      6  ACT            R3
      7  BLK_NEW        R3
      8  SUB            R7, R0, R5
      9  JMP            35
     10  MOD            R2, R4, R1
     11  BLK_COUNT      R0
     12  MUL            R2, R1, R1
     13  WS_SLEN        R1, R3
     14  WS_SLEN        R5, R3
     15  ACT            R3
     16  MOD            R2, R1, R5
     17  WS_FREE        R5
     18  INPUT          R7, num_ops
     19  MOD            R2, R1, R5
     20  WS_FIND        R4, R7
     21  WS_REC_SET     R7, R2, R4
     22  MOD            R5, R4, R1
     23  VSET           R4, R0, R6
     24  WS_FIND        R4, R7
     25  MOD            R3, R4, R1
     26  CONST          R5, 10
     27  BLK_PATCH      R4, R3, R6
     28  MOD            R3, R4, R1
     29  HALT           
     30  DIV            R0, R1, R5
     31  WS_FIND        R4, R7
     32  MOD            R3, R4, R1
     33  CONST          R5, 8
     34  LT             R0, R7, R5
     35  BLK_PATCH      R7, R3, R3
     36  ACT            R1
     37  ACT            R3
     38  MOD            R3, R4, R1
     39  ACT            R3
     40  DIV            R4, R4, R1
     41  MOD            R2, R1, R5
     42  WS_FREE        R5
     43  INPUT          R7, num_ops
     44  MOD            R2, R1, R5
     45  WS_FIND        R4, R7
     46  CONST          R5, 5
     47  MOD            R3, R4, R1
     48  ACT            R3
     49  ADD            R0, R0, R5
     50  MOD            R3, R0, R1
     51  ACT            R3
     52  DIV            R4, R0, R1
     53  JMP            36
     54  BLK_DELETE     R6
  ancestry (120 steps, newest first): iteration/fitness/modification
    it  201  46.4470  len 55  replace@48+const@1+duplicate@1+1->41+splice@41<-donor[15:20]:1804024b0e2aa586
    it  199  37.3798  len 49  arg@10.0
    it  198  42.4056  len 49  arg@7.0
    it  197  37.3966  len 49  replace@48
    it  196  31.3652  len 49  const@26+delete@49
    it  195  40.4009  len 50  delete@0
    it  192  34.3403  len 51  arg@12.0
    it  190  29.2928  len 51  insert@22
    it  188  39.3941  len 50  duplicate@27+3->23+insert@4
    it  184  43.4132  len 46  delete@9+delete@8+arg@18.0
    it  182  24.2947  len 48  const@32+delete@30
    it  181  38.3945  len 49  delete@19
    it  178  29.2968  len 50  const@49
    it  177  27.3409  len 50  delete@20
    it  176  26.3019  len 51  delete@7+replace@10+insert@21
    ... 106 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          47.117  26.961  27.664  27.999  46.7  26.7     8916    38056   29005.3    4.3   74.7
  top2_40ffef775b83c360       32.666  32.666  32.666  32.666  32.3  32.3    29924    29924       0.0    0.0    0.0
  top3_a1961e6c87824f13       32.001  32.001  32.001  32.001  31.7  31.7    29720    29720       0.0    0.0    0.0
  ancestor166_it298_716406c4  32.001  32.001  32.001  32.001  31.7  31.7    29720    29720       0.0    0.0    0.0
  contemp_58ddd504346504eb    32.001  32.001  32.001  32.001  31.7  31.7    29751    29751       0.0    0.0    0.0
  contemp_21cd9ff8d708de36    31.336  31.336  31.336  31.336  31.0  31.0    29476    29476       0.0    0.0    0.0
  top1_2d06de6fdc0a2a95       30.329  30.329  30.329  30.329  30.0  30.0    30776    30776       0.0    0.0    0.0
  ancestor84_it131_e88ffbc61  28.658  28.658  28.658  28.658  28.3  28.3    31399    31399       0.0    0.0    0.0
  ENUMERATE_C1                26.964  26.964  26.964  26.964  26.7  26.7    37456    37456       0.0    0.0    0.0
  TABLE_MEMO_C1               26.964  26.964  26.964  26.964  26.7  26.7    37456    37456     -17.9    0.0    0.0
  PROCEDURE_NOCAL_C1          26.962  26.962  26.962  26.962  26.7  26.7    37759    37756     -23.8    3.3    1.7
  contemp_bd8a72058a634c4d    25.651  25.651  25.651  25.651  25.3  25.3    32429    32429       0.0    0.0    0.0
  ancestor1_it0_0875253d162c  25.287  25.287  25.287  25.287  25.0  25.0    37856    37856       0.0    0.0    0.0
  ENUMERATE_VM_C1             25.287  25.287  25.287  25.287  25.0  25.0    37856    37856       0.0    0.0    0.0
  bestever_fc9b4f48c2ff896c   24.627  24.627  24.627  24.627  24.3  24.3    36383    36383       0.0    0.0    0.0
  QUIT_C1                     19.605  19.605  19.605  19.605  19.3  19.3     9448     9448       0.0    0.0    0.0
  RANDOM_C1                   10.160  10.160  10.160  10.160  10.0  10.0    62546    62546       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.00/ 455.13   14.90/ 539.10   36.22/ 623.47  177.39/1089.94  477.07/1237.03
  top2_40ffef775b83c360       276.26/ 276.26  355.91/ 355.91  539.37/ 539.37  871.64/ 871.64 1195.65/1195.65
  top3_a1961e6c87824f13       253.78/ 253.78  292.28/ 292.28  540.30/ 540.30  960.28/ 960.28 1153.44/1153.44
  ancestor166_it298_716406c4  253.78/ 253.78  292.28/ 292.28  540.30/ 540.30  960.28/ 960.28 1153.44/1153.44
  contemp_58ddd504346504eb    254.80/ 254.80  293.30/ 293.30  540.75/ 540.75  960.69/ 960.69 1153.74/1153.74
  contemp_21cd9ff8d708de36    265.75/ 265.75  235.70/ 235.70  592.82/ 592.82  916.19/ 916.19 1153.96/1153.96
  top1_2d06de6fdc0a2a95       282.83/ 282.83  298.93/ 298.93  543.96/ 543.96 1007.25/1007.25 1162.28/1162.28
  ancestor84_it131_e88ffbc61  228.86/ 228.86  262.93/ 262.93  614.03/ 614.03 1018.12/1018.12 1261.13/1261.13
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31  615.85/ 615.85 1086.47/1086.47 1232.75/1232.75
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34  616.29/ 615.86 1086.97/1086.48 1233.28/1232.76
  PROCEDURE_NOCAL_C1          444.13/ 443.81  528.11/ 527.79  619.85/ 619.71 1088.59/1088.26 1236.48/1234.94
  contemp_bd8a72058a634c4d    228.71/ 228.71  370.64/ 370.64  632.96/ 632.96 1075.65/1075.65 1187.82/1187.82
  ancestor1_it0_0875253d162c  494.04/ 494.04  523.26/ 523.26  664.50/ 664.50 1116.70/1116.70 1283.87/1283.87
  ENUMERATE_VM_C1             494.04/ 494.04  523.26/ 523.26  664.50/ 664.50 1116.70/1116.70 1283.87/1283.87
  bestever_fc9b4f48c2ff896c   610.41/ 610.41  605.47/ 605.47  633.93/ 633.93  886.55/ 886.55 1197.26/1197.26
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31  800.00/ 800.00 1200.00/1200.00 1400.00/1400.00
  RANDOM_C1                  1661.96/1661.96 1626.54/1626.54  726.73/ 726.73 1161.23/1161.23 1244.20/1244.20

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            36/36    33    27/30   167     6/12   809    11/12   117    30/30   301    30/30    14
  top2_40ffef775b83c360         16/36   519    15/30   839     4/12  1242     2/12  1061    30/30   266    30/30   343
  top3_a1961e6c87824f13         16/36   522    12/30   928     4/12  1249     3/12   979    30/30   245    30/30   282
  ancestor166_it298_716406c4    16/36   522    12/30   928     4/12  1249     3/12   979    30/30   245    30/30   282
  contemp_58ddd504346504eb      16/36   522    12/30   928     4/12  1249     3/12   980    30/30   246    30/30   283
  contemp_21cd9ff8d708de36      15/36   572    12/30   885     5/12  1163     2/12  1066    29/30   256    30/30   227
  top1_2d06de6fdc0a2a95         15/36   528     9/30   978     3/12  1253     3/12  1003    30/30   274    30/30   290
  ancestor84_it131_e88ffbc61    12/36   592     9/30   982     2/12  1345     2/12  1088    30/30   221    30/30   254
  ENUMERATE_C1                  13/36   613     5/30  1082     2/12  1350     2/12  1106    29/30   431    29/30   514
  TABLE_MEMO_C1                 13/36   613     5/30  1082     2/12  1350     2/12  1106    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1            13/36   617     5/30  1084     2/12  1352     2/12  1108    29/30   442    29/30   526
  contemp_bd8a72058a634c4d      10/36   606     5/30  1031     2/12  1344     3/12   932    29/30   219    27/30   355
  ancestor1_it0_0875253d162c    11/36   635     6/30  1068     2/12  1350     2/12  1107    27/30   472    27/30   500
  ENUMERATE_VM_C1               11/36   635     6/30  1068     2/12  1350     2/12  1107    27/30   472    27/30   500
  bestever_fc9b4f48c2ff896c     11/36   604    11/30   844     3/12  1237     2/12  1044    23/30   581    23/30   576
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  RANDOM_C1                      6/36   720     2/30  1150     2/12  1430     2/12  1034    10/30  1646     8/30  1610

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1           310.58  1153.44   310.58   310.58  1153.44  1153.44  1153.44   4.0
  top2_40ffef775b83c360       1015.64       --  1015.64  1015.64  1015.64  1015.64  1015.64   0.0
  top3_a1961e6c87824f13       1046.13       --  1046.13  1046.13  1046.13  1046.13  1046.13   0.0
  ancestor166_it298_716406c4  1046.13       --  1046.13  1046.13  1046.13  1046.13  1046.13   0.0
  contemp_58ddd504346504eb    1046.49       --  1046.49  1046.49  1046.49  1046.49  1046.49   0.0
  contemp_21cd9ff8d708de36    1021.87       --  1021.87  1021.87  1021.87  1021.87  1021.87   0.0
  top1_2d06de6fdc0a2a95       1076.15       --  1076.15  1076.15  1076.15  1076.15  1076.15   0.0
  ancestor84_it131_e88ffbc61  1126.12       --  1126.12  1126.12  1126.12  1126.12  1126.12   0.0
  ENUMERATE_C1                1151.49       --  1151.49  1151.49  1151.49  1151.49  1151.49   0.0
  TABLE_MEMO_C1               1152.00       --  1151.52  1152.00  1151.52  1151.52  1151.52   0.0
  PROCEDURE_NOCAL_C1          1154.32  1153.42  1154.32  1154.32  1153.42  1153.42  1153.42   1.3
  contemp_bd8a72058a634c4d    1125.51       --  1125.51  1125.51  1125.51  1125.51  1125.51   0.0
  ancestor1_it0_0875253d162c  1191.00       --  1191.00  1191.00  1191.00  1191.00  1191.00   0.0
  ENUMERATE_VM_C1             1191.00       --  1191.00  1191.00  1191.00  1191.00  1191.00   0.0
  bestever_fc9b4f48c2ff896c   1024.64       --  1024.64  1024.64  1024.64  1024.64  1024.64   0.0
  QUIT_C1                     1288.89       --  1288.89  1288.89  1288.89  1288.89  1288.89   0.0
  RANDOM_C1                   1198.10       --  1198.10  1198.10  1198.10  1198.10  1198.10   0.0

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
  top2_40ffef775b83c360
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [32, 29, 36] vs FRESH [32, 29, 36]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [25267.5, 27058.1, 21936.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1022.62, 1117.19, 907.11] vs CODE_ONLY [1022.62, 1117.19, 907.11]
    4_scramble_or_reset_damages            0/3  eff ACC [32.33, 29.316, 36.352] SCR [32.33, 29.316, 36.352] RESET [32.33, 29.316, 36.352]
    5_transfers_to_fresh_copy              0/3  FULL [1022.62, 1117.19, 907.11] vs ACC remainder [1022.62, 1117.19, 907.11]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1022.62, 1117.19, 907.11]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1022.62, 1117.19, 907.11] STORAGE_MATCHED [1022.62, 1117.19, 907.11] vs ACC remainder [1022.62, 1117.19, 907.11]
  top3_a1961e6c87824f13
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [33, 27, 35] vs FRESH [33, 27, 35]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [24337.3, 29265.8, 22338.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [970.03, 1238.71, 929.66] vs CODE_ONLY [970.03, 1238.71, 929.66]
    4_scramble_or_reset_damages            0/3  eff ACC [33.337, 27.307, 35.359] SCR [33.337, 27.307, 35.359] RESET [33.337, 27.307, 35.359]
    5_transfers_to_fresh_copy              0/3  FULL [970.03, 1238.71, 929.66] vs ACC remainder [970.03, 1238.71, 929.66]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [970.03, 1238.71, 929.66]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [970.03, 1238.71, 929.66] STORAGE_MATCHED [970.03, 1238.71, 929.66] vs ACC remainder [970.03, 1238.71, 929.66]
  ancestor166_it298_716406c4ce4bb63a
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [33, 27, 35] vs FRESH [33, 27, 35]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [24337.3, 29265.8, 22338.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [970.03, 1238.71, 929.66] vs CODE_ONLY [970.03, 1238.71, 929.66]
    4_scramble_or_reset_damages            0/3  eff ACC [33.337, 27.307, 35.359] SCR [33.337, 27.307, 35.359] RESET [33.337, 27.307, 35.359]
    5_transfers_to_fresh_copy              0/3  FULL [970.03, 1238.71, 929.66] vs ACC remainder [970.03, 1238.71, 929.66]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [970.03, 1238.71, 929.66]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [970.03, 1238.71, 929.66] STORAGE_MATCHED [970.03, 1238.71, 929.66] vs ACC remainder [970.03, 1238.71, 929.66]
  contemp_58ddd504346504eb
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [33, 27, 35] vs FRESH [33, 27, 35]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [24350.6, 29272.9, 22354.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [970.48, 1238.82, 930.17] vs CODE_ONLY [970.48, 1238.82, 930.17]
    4_scramble_or_reset_damages            0/3  eff ACC [33.337, 27.307, 35.359] SCR [33.337, 27.307, 35.359] RESET [33.337, 27.307, 35.359]
    5_transfers_to_fresh_copy              0/3  FULL [970.48, 1238.82, 930.17] vs ACC remainder [970.48, 1238.82, 930.17]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [970.48, 1238.82, 930.17]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [970.48, 1238.82, 930.17] STORAGE_MATCHED [970.48, 1238.82, 930.17] vs ACC remainder [970.48, 1238.82, 930.17]
  contemp_21cd9ff8d708de36
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [31, 29, 33] vs FRESH [31, 29, 33]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [26411.5, 27323.1, 22788.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1038.22, 1071.16, 956.22] vs CODE_ONLY [1038.22, 1071.16, 956.22]
    4_scramble_or_reset_damages            0/3  eff ACC [31.323, 29.323, 33.361] SCR [31.323, 29.323, 33.361] RESET [31.323, 29.323, 33.361]
    5_transfers_to_fresh_copy              0/3  FULL [1038.22, 1071.16, 956.22] vs ACC remainder [1038.22, 1071.16, 956.22]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1038.22, 1071.16, 956.22]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1038.22, 1071.16, 956.22] STORAGE_MATCHED [1038.22, 1071.16, 956.22] vs ACC remainder [1038.22, 1071.16, 956.22]
  top1_2d06de6fdc0a2a95
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [30, 28, 32] vs FRESH [30, 28, 32]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [25110.6, 27822.6, 24761.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1006.51, 1161.18, 1060.76] vs CODE_ONLY [1006.51, 1161.18, 1060.76]
    4_scramble_or_reset_damages            0/3  eff ACC [30.332, 28.316, 32.339] SCR [30.332, 28.316, 32.339] RESET [30.332, 28.316, 32.339]
    5_transfers_to_fresh_copy              0/3  FULL [1006.51, 1161.18, 1060.76] vs ACC remainder [1006.51, 1161.18, 1060.76]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1006.51, 1161.18, 1060.76]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1006.51, 1161.18, 1060.76] STORAGE_MATCHED [1006.51, 1161.18, 1060.76] vs ACC remainder [1006.51, 1161.18, 1060.76]
  ancestor84_it131_e88ffbc612047a6f
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [29, 25, 31] vs FRESH [29, 25, 31]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [27236.7, 30138.2, 25540.8] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1070.53, 1233.68, 1074.16] vs CODE_ONLY [1070.53, 1233.68, 1074.16]
    4_scramble_or_reset_damages            0/3  eff ACC [29.322, 25.306, 31.345] SCR [29.322, 25.306, 31.345] RESET [29.322, 25.306, 31.345]
    5_transfers_to_fresh_copy              0/3  FULL [1070.53, 1233.68, 1074.16] vs ACC remainder [1070.53, 1233.68, 1074.16]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1070.53, 1233.68, 1074.16]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1070.53, 1233.68, 1074.16] STORAGE_MATCHED [1070.53, 1233.68, 1074.16] vs ACC remainder [1070.53, 1233.68, 1074.16]
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
  contemp_bd8a72058a634c4d
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [24, 25, 27] vs FRESH [24, 25, 27]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [28472.9, 28830.8, 26260.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1135.34, 1127.34, 1113.84] vs CODE_ONLY [1135.34, 1127.34, 1113.84]
    4_scramble_or_reset_damages            0/3  eff ACC [24.306, 25.326, 27.32] SCR [24.306, 25.326, 27.32] RESET [24.306, 25.326, 27.32]
    5_transfers_to_fresh_copy              0/3  FULL [1135.34, 1127.34, 1113.84] vs ACC remainder [1135.34, 1127.34, 1113.84]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1135.34, 1127.34, 1113.84]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1135.34, 1127.34, 1113.84] STORAGE_MATCHED [1135.34, 1127.34, 1113.84] vs ACC remainder [1135.34, 1127.34, 1113.84]
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
  bestever_fc9b4f48c2ff896c
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 25, 29] vs FRESH [19, 25, 29]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [27295.5, 26508.1, 24348.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1021.96, 1095.51, 956.45] vs CODE_ONLY [1021.96, 1095.51, 956.45]
    4_scramble_or_reset_damages            0/3  eff ACC [19.255, 25.298, 29.33] SCR [19.255, 25.298, 29.33] RESET [19.255, 25.298, 29.33]
    5_transfers_to_fresh_copy              0/3  FULL [1021.96, 1095.51, 956.45] vs ACC remainder [1021.96, 1095.51, 956.45]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1021.96, 1095.51, 956.45]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1021.96, 1095.51, 956.45] STORAGE_MATCHED [1021.96, 1095.51, 956.45] vs ACC remainder [1021.96, 1095.51, 956.45]
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

MACHINERY OF top1_2d06de6fdc0a2a95 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   0     0
    task  9:     0    0    0    0    0 |   0     0
    task 19:     0    0    0    0    0 |   0     0
    task 31:     0    0    0    0    0 |   0     0
    task 41:     0    0    0    0    0 |   0     0
    task 49:     0    0    0    0    0 |   0     0
  artifact events: 0 (create 0, delete 0, patch/append 0); invocations by block: {}; edges: 0
  adaptation curve ACC:   22 667 32 469 22 22 98 1182 216 422 164 32 331 331 11 634 634 32 667 56 824 80 824 23 824 196 824 824 824 100 824 824 1032 217 1236 1236 1236 1236 1236 1236 536 1236 28 434 1648 210 1236 1236 1236 1648
  adaptation curve FRESH: 22 667 32 469 22 22 98 1182 216 422 164 32 331 331 11 634 634 32 667 56 824 80 824 23 824 196 824 824 824 100 824 824 1032 217 1236 1236 1236 1236 1236 1236 536 1236 28 434 1648 210 1236 1236 1236 1648
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

