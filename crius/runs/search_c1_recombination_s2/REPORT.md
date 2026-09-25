CRIUS CAMPAIGN 0 REPORT  run=search_c1_recombination_s2  arm=recombination
code_commit=97af44f88 dirty=True config_hash=32dfb243be9fdec9 world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  16.2188   15.9545         4.3996        46          9
    26  37.3750   34.8547        19.7048        57         80
    51  18.2658   17.8794        13.7456        64        149
    76  31.3295   31.3266        24.0145        63        220
   101  44.4216   42.6671        33.3484        63        286
   126  29.2539   23.3771        15.7774        64        341
   151  34.3509   34.3509        26.6654        62        400
   176  32.3110   31.4342        20.8204        64        454
   201  35.3570   32.7179        27.8073        63        512
   226  42.3962   42.3943        29.5122        61        565
   251  31.3183   31.3161        20.9933        64        620
   276  30.3315   30.3311        19.4498        62        677
   300  35.3659   35.3659        25.1576        58        730
  candidates evaluated: 7208   best_ever 45.4564 (dfc3a8c68e1282ee)  wall 730s

BEST PROGRAM dfc3a8c68e1282ee (len 45, iteration 6, modification delete@23)
  search seed 201006: fit 45.4564 succ 45/50 inter 7468 steps 34590 ws_cost 0 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [35.182, 1.0], "B": [29.338, 1.0], "C": [265.173, 0.75], "D": [262.03, 0.9], "E": [170.791, 0.875]}
  listing:
      0  INPUT          R1, num_ops
      1  CONST          R5, 1
      2  CONST          R0, -8
      3  BRZ            R3, 21
      4  ACT            R1
      5  MOD            R3, R0, R1
      6  ACT            R3
      7  DIV            R4, R0, R1
      8  MOD            R3, R4, R1
      9  ADD            R0, R0, R5
     10  JMP            12
     11  MOV            R2, R1
     12  LT             R3, R0, R2
     13  ACT            R1
     14  ACT            R0
     15  ADD            R0, R0, R5
     16  JMP            12
     17  CONST          R0, 0
     18  MUL            R2, R1, R1
     19  LT             R3, R0, R2
     20  BRZ            R3, 28
     21  ACT            R1
     22  MOD            R3, R0, R1
     23  DIV            R4, R0, R1
     24  MOD            R3, R4, R1
     25  ACT            R3
     26  ADD            R0, R0, R5
     27  JMP            19
     28  CONST          R0, 0
     29  MUL            R2, R1, R1
     30  MUL            R2, R2, R1
     31  CONST          R3, 12
     32  BRZ            R3, 44
     33  ACT            R1
     34  MOD            R3, R0, R1
     35  ACT            R3
     36  DIV            R4, R0, R1
     37  MOD            R3, R4, R1
     38  ACT            R3
     39  DIV            R4, R4, R1
     40  MOD            R3, R4, R1
     41  ACT            R3
     42  ADD            R0, R0, R5
     43  JMP            31
     44  BLK_INVOKE     R5
  ancestry (5 steps, newest first): iteration/fitness/modification
    it    6  45.4564  len 45  delete@23
    it    4  23.2543  len 46  const@32
    it    2  23.3019  len 46  replace@32
    it    1  16.2188  len 46  arg@2.1+replace@37+splice@3<-donor[13:21]:9cd16c9471ef698c
    it    0  5.0668  len 38  const@2+delete@5
    it    0  20.2871  len 39  seed:ENUMERATE_VM

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          47.117  26.961  27.664  27.999  46.7  26.7     8916    38056   29005.3    4.3   74.7
  top1_db9a25ed1f5fd813       31.994  31.994  31.994  31.994  31.7  31.7    30875    30875       0.0    0.0    0.0
  top2_1df1df918c310042       31.994  31.994  31.994  31.994  31.7  31.7    30875    30875       0.0    0.0    0.0
  top3_269eb7f65441c397       31.994  31.994  31.994  31.994  31.7  31.7    30875    30875       0.0    0.0    0.0
  ancestor180_it298_5ea47ac8  31.994  31.994  31.994  31.994  31.7  31.7    30875    30875       0.0    0.0    0.0
  contemp_621a3e78425ad10e    31.994  31.994  31.994  31.994  31.7  31.7    30875    30875       0.0    0.0    0.0
  ancestor90_it146_c93e0b7b6  30.658  30.658  30.658  30.658  30.3  30.3    31283    31283       0.0    0.0    0.0
  ENUMERATE_C1                26.964  26.964  26.964  26.964  26.7  26.7    37456    37456       0.0    0.0    0.0
  TABLE_MEMO_C1               26.964  26.964  26.964  26.964  26.7  26.7    37456    37456     -17.9    0.0    0.0
  bestever_dfc3a8c68e1282ee   26.963  26.963  26.963  26.963  26.7  26.7    36155    36155       0.0    0.0    0.0
  PROCEDURE_NOCAL_C1          26.962  26.962  26.962  26.962  26.7  26.7    37759    37756     -23.8    3.3    1.7
  ancestor1_it0_0875253d162c  25.287  25.287  25.287  25.287  25.0  25.0    37856    37856       0.0    0.0    0.0
  ENUMERATE_VM_C1             25.287  25.287  25.287  25.287  25.0  25.0    37856    37856       0.0    0.0    0.0
  QUIT_C1                     19.605  19.605  19.605  19.605  19.3  19.3     9448     9448       0.0    0.0    0.0
  RANDOM_C1                   10.160  10.160  10.160  10.160  10.0  10.0    62546    62546       0.0    0.0    0.0
  contemp_c996ce6d7c83cda2     1.424   1.424   1.424   1.424   1.3   1.3    70145    70145       0.0    0.0    0.0
  contemp_28c83b3d75069735     0.072   0.072   0.072   0.072   0.0   0.0    72800    72800       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.00/ 455.13   14.90/ 539.10   36.22/ 623.47  177.39/1089.94  477.07/1237.03
  top1_db9a25ed1f5fd813       359.02/ 359.02  406.90/ 406.90  512.65/ 512.65  928.23/ 928.23 1130.44/1130.44
  top2_1df1df918c310042       359.04/ 359.04  406.92/ 406.92  512.67/ 512.67  928.25/ 928.25 1130.46/1130.46
  top3_269eb7f65441c397       359.04/ 359.04  406.92/ 406.92  512.67/ 512.67  928.25/ 928.25 1130.46/1130.46
  ancestor180_it298_5ea47ac8  359.04/ 359.04  406.92/ 406.92  512.67/ 512.67  928.25/ 928.25 1130.46/1130.46
  contemp_621a3e78425ad10e    359.03/ 359.03  406.93/ 406.93  512.68/ 512.68  928.29/ 928.29 1130.52/1130.52
  ancestor90_it146_c93e0b7b6  374.31/ 374.31  410.41/ 410.41  537.19/ 537.19  976.97/ 976.97 1050.16/1050.16
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31  615.85/ 615.85 1086.47/1086.47 1232.75/1232.75
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34  616.29/ 615.86 1086.97/1086.48 1233.28/1232.76
  bestever_dfc3a8c68e1282ee   466.35/ 466.35  468.26/ 468.26  625.34/ 625.34 1075.30/1075.30 1267.71/1267.71
  PROCEDURE_NOCAL_C1          444.13/ 443.81  528.11/ 527.79  619.85/ 619.71 1088.59/1088.26 1236.48/1234.94
  ancestor1_it0_0875253d162c  494.04/ 494.04  523.26/ 523.26  664.50/ 664.50 1116.70/1116.70 1283.87/1283.87
  ENUMERATE_VM_C1             494.04/ 494.04  523.26/ 523.26  664.50/ 664.50 1116.70/1116.70 1283.87/1283.87
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31  800.00/ 800.00 1200.00/1200.00 1400.00/1400.00
  RANDOM_C1                  1661.96/1661.96 1626.54/1626.54  726.73/ 726.73 1161.23/1161.23 1244.20/1244.20
  contemp_c996ce6d7c83cda2   2092.16/2092.16 1948.48/1948.48  865.57/ 865.57 1298.37/1298.37 1514.77/1514.77
  contemp_28c83b3d75069735   2184.89/2184.89 2184.89/2184.89  873.89/ 873.89 1310.89/1310.89 1529.39/1529.39

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            36/36    33    27/30   167     6/12   809    11/12   117    30/30   301    30/30    14
  top1_db9a25ed1f5fd813         19/36   492    13/30   892     2/12  1375     5/12   798    28/30   345    28/30   391
  top2_1df1df918c310042         19/36   492    13/30   892     2/12  1375     5/12   798    28/30   345    28/30   391
  top3_269eb7f65441c397         19/36   492    13/30   892     2/12  1375     5/12   798    28/30   345    28/30   391
  ancestor180_it298_5ea47ac8    19/36   492    13/30   892     2/12  1375     5/12   798    28/30   345    28/30   391
  contemp_621a3e78425ad10e      19/36   492    13/30   892     2/12  1375     5/12   798    28/30   345    28/30   391
  ancestor90_it146_c93e0b7b6    17/36   518    10/30   942     3/12  1303     6/12   721    28/30   361    27/30   395
  ENUMERATE_C1                  13/36   613     5/30  1082     2/12  1350     2/12  1106    29/30   431    29/30   514
  TABLE_MEMO_C1                 13/36   613     5/30  1082     2/12  1350     2/12  1106    29/30   431    29/30   514
  bestever_dfc3a8c68e1282ee     14/36   599     6/30  1030     2/12  1356     3/12  1073    27/30   447    28/30   448
  PROCEDURE_NOCAL_C1            13/36   617     5/30  1084     2/12  1352     2/12  1108    29/30   442    29/30   526
  ancestor1_it0_0875253d162c    11/36   635     6/30  1068     2/12  1350     2/12  1107    27/30   472    27/30   500
  ENUMERATE_VM_C1               11/36   635     6/30  1068     2/12  1350     2/12  1107    27/30   472    27/30   500
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  RANDOM_C1                      6/36   720     2/30  1150     2/12  1430     2/12  1034    10/30  1646     8/30  1610
  contemp_c996ce6d7c83cda2       0/36   800     0/30  1200     0/12  1600     0/12  1200     1/30  1934     3/30  1801
  contemp_28c83b3d75069735       0/36   800     0/30  1200     0/12  1600     0/12  1200     0/30  2000     0/30  2000

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1           310.58  1153.44   310.58   310.58  1153.44  1153.44  1153.44   4.0
  top1_db9a25ed1f5fd813       1018.10       --  1018.10  1018.10  1018.10  1018.10  1018.10   0.0
  top2_1df1df918c310042       1018.12       --  1018.12  1018.12  1018.12  1018.12  1018.12   0.0
  top3_269eb7f65441c397       1018.12       --  1018.12  1018.12  1018.12  1018.12  1018.12   0.0
  ancestor180_it298_5ea47ac8  1018.12       --  1018.12  1018.12  1018.12  1018.12  1018.12   0.0
  contemp_621a3e78425ad10e    1018.17       --  1018.17  1018.17  1018.17  1018.17  1018.17   0.0
  ancestor90_it146_c93e0b7b6  1009.50       --  1009.50  1009.50  1009.50  1009.50  1009.50   0.0
  ENUMERATE_C1                1151.49       --  1151.49  1151.49  1151.49  1151.49  1151.49   0.0
  TABLE_MEMO_C1               1152.00       --  1151.52  1152.00  1151.52  1151.52  1151.52   0.0
  bestever_dfc3a8c68e1282ee   1160.81       --  1160.81  1160.81  1160.81  1160.81  1160.81   0.0
  PROCEDURE_NOCAL_C1          1154.32  1153.42  1154.32  1154.32  1153.42  1153.42  1153.42   1.3
  ancestor1_it0_0875253d162c  1191.00       --  1191.00  1191.00  1191.00  1191.00  1191.00   0.0
  ENUMERATE_VM_C1             1191.00       --  1191.00  1191.00  1191.00  1191.00  1191.00   0.0
  QUIT_C1                     1288.89       --  1288.89  1288.89  1288.89  1288.89  1288.89   0.0
  RANDOM_C1                   1198.10       --  1198.10  1198.10  1198.10  1198.10  1198.10   0.0
  contemp_c996ce6d7c83cda2    1394.55       --  1394.55  1394.55  1394.55  1394.55  1394.55   0.0
  contemp_28c83b3d75069735    1408.00       --  1408.00  1408.00  1408.00  1408.00  1408.00   0.0

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
  top1_db9a25ed1f5fd813
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [33, 24, 38] vs FRESH [33, 24, 38]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [25510.7, 28005.3, 19917.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1023.34, 1143.65, 887.32] vs CODE_ONLY [1023.34, 1143.65, 887.32]
    4_scramble_or_reset_damages            0/3  eff ACC [33.324, 24.292, 38.364] SCR [33.324, 24.292, 38.364] RESET [33.324, 24.292, 38.364]
    5_transfers_to_fresh_copy              0/3  FULL [1023.34, 1143.65, 887.32] vs ACC remainder [1023.34, 1143.65, 887.32]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1023.34, 1143.65, 887.32]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1023.34, 1143.65, 887.32] STORAGE_MATCHED [1023.34, 1143.65, 887.32] vs ACC remainder [1023.34, 1143.65, 887.32]
  top2_1df1df918c310042
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [33, 24, 38] vs FRESH [33, 24, 38]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [25511.3, 28005.9, 19917.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1023.36, 1143.67, 887.34] vs CODE_ONLY [1023.36, 1143.67, 887.34]
    4_scramble_or_reset_damages            0/3  eff ACC [33.324, 24.292, 38.364] SCR [33.324, 24.292, 38.364] RESET [33.324, 24.292, 38.364]
    5_transfers_to_fresh_copy              0/3  FULL [1023.36, 1143.67, 887.34] vs ACC remainder [1023.36, 1143.67, 887.34]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1023.36, 1143.67, 887.34]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1023.36, 1143.67, 887.34] STORAGE_MATCHED [1023.36, 1143.67, 887.34] vs ACC remainder [1023.36, 1143.67, 887.34]
  top3_269eb7f65441c397
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [33, 24, 38] vs FRESH [33, 24, 38]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [25511.3, 28005.9, 19917.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1023.36, 1143.67, 887.34] vs CODE_ONLY [1023.36, 1143.67, 887.34]
    4_scramble_or_reset_damages            0/3  eff ACC [33.324, 24.292, 38.364] SCR [33.324, 24.292, 38.364] RESET [33.324, 24.292, 38.364]
    5_transfers_to_fresh_copy              0/3  FULL [1023.36, 1143.67, 887.34] vs ACC remainder [1023.36, 1143.67, 887.34]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1023.36, 1143.67, 887.34]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1023.36, 1143.67, 887.34] STORAGE_MATCHED [1023.36, 1143.67, 887.34] vs ACC remainder [1023.36, 1143.67, 887.34]
  ancestor180_it298_5ea47ac835c1d26f
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [33, 24, 38] vs FRESH [33, 24, 38]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [25511.3, 28005.9, 19917.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1023.36, 1143.67, 887.34] vs CODE_ONLY [1023.36, 1143.67, 887.34]
    4_scramble_or_reset_damages            0/3  eff ACC [33.324, 24.292, 38.364] SCR [33.324, 24.292, 38.364] RESET [33.324, 24.292, 38.364]
    5_transfers_to_fresh_copy              0/3  FULL [1023.36, 1143.67, 887.34] vs ACC remainder [1023.36, 1143.67, 887.34]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1023.36, 1143.67, 887.34]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1023.36, 1143.67, 887.34] STORAGE_MATCHED [1023.36, 1143.67, 887.34] vs ACC remainder [1023.36, 1143.67, 887.34]
  contemp_621a3e78425ad10e
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [33, 24, 38] vs FRESH [33, 24, 38]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [25512.4, 28007.2, 19918.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1023.41, 1143.73, 887.38] vs CODE_ONLY [1023.41, 1143.73, 887.38]
    4_scramble_or_reset_damages            0/3  eff ACC [33.324, 24.292, 38.364] SCR [33.324, 24.292, 38.364] RESET [33.324, 24.292, 38.364]
    5_transfers_to_fresh_copy              0/3  FULL [1023.41, 1143.73, 887.38] vs ACC remainder [1023.41, 1143.73, 887.38]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1023.41, 1143.73, 887.38]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1023.41, 1143.73, 887.38] STORAGE_MATCHED [1023.41, 1143.73, 887.38] vs ACC remainder [1023.41, 1143.73, 887.38]
  ancestor90_it146_c93e0b7b64fed77e
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [30, 23, 38] vs FRESH [30, 23, 38]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [25821.0, 28935.5, 19095.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1031.32, 1197.2, 799.97] vs CODE_ONLY [1031.32, 1197.2, 799.97]
    4_scramble_or_reset_damages            0/3  eff ACC [30.329, 23.281, 38.366] SCR [30.329, 23.281, 38.366] RESET [30.329, 23.281, 38.366]
    5_transfers_to_fresh_copy              0/3  FULL [1031.32, 1197.2, 799.97] vs ACC remainder [1031.32, 1197.2, 799.97]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1031.32, 1197.2, 799.97]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1031.32, 1197.2, 799.97] STORAGE_MATCHED [1031.32, 1197.2, 799.97] vs ACC remainder [1031.32, 1197.2, 799.97]
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
  bestever_dfc3a8c68e1282ee
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [26, 22, 32] vs FRESH [26, 22, 32]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [28772.9, 31250.7, 25172.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1140.18, 1253.84, 1088.42] vs CODE_ONLY [1140.18, 1253.84, 1088.42]
    4_scramble_or_reset_damages            0/3  eff ACC [26.275, 22.281, 32.334] SCR [26.275, 22.281, 32.334] RESET [26.275, 22.281, 32.334]
    5_transfers_to_fresh_copy              0/3  FULL [1140.18, 1253.84, 1088.42] vs ACC remainder [1140.18, 1253.84, 1088.42]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1140.18, 1253.84, 1088.42]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1140.18, 1253.84, 1088.42] STORAGE_MATCHED [1140.18, 1253.84, 1088.42] vs ACC remainder [1140.18, 1253.84, 1088.42]
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
  contemp_c996ce6d7c83cda2
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [3, 1, 0] vs FRESH [3, 1, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [35488.7, 35488.7, 35488.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1394.55, 1394.55, 1394.55] vs CODE_ONLY [1394.55, 1394.55, 1394.55]
    4_scramble_or_reset_damages            0/3  eff ACC [3.11, 1.087, 0.076] SCR [3.11, 1.087, 0.076] RESET [3.11, 1.087, 0.076]
    5_transfers_to_fresh_copy              0/3  FULL [1394.55, 1394.55, 1394.55] vs ACC remainder [1394.55, 1394.55, 1394.55]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1394.55, 1394.55, 1394.55]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1394.55, 1394.55, 1394.55] STORAGE_MATCHED [1394.55, 1394.55, 1394.55] vs ACC remainder [1394.55, 1394.55, 1394.55]
  contemp_28c83b3d75069735
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [35830.7, 35830.7, 35830.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1408.0, 1408.0, 1408.0] vs CODE_ONLY [1408.0, 1408.0, 1408.0]
    4_scramble_or_reset_damages            0/3  eff ACC [0.072, 0.072, 0.072] SCR [0.072, 0.072, 0.072] RESET [0.072, 0.072, 0.072]
    5_transfers_to_fresh_copy              0/3  FULL [1408.0, 1408.0, 1408.0] vs ACC remainder [1408.0, 1408.0, 1408.0]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1408.0, 1408.0, 1408.0]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1408.0, 1408.0, 1408.0] STORAGE_MATCHED [1408.0, 1408.0, 1408.0] vs ACC remainder [1408.0, 1408.0, 1408.0]

MACHINERY OF top1_db9a25ed1f5fd813 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   0     0
    task  9:     0    0    0    0    0 |   0     0
    task 19:     0    0    0    0    0 |   0     0
    task 31:     0    0    0    0    0 |   0     0
    task 41:     0    0    0    0    0 |   0     0
    task 49:     0    0    0    0    0 |   0     0
  artifact events: 0 (create 0, delete 0, patch/append 0); invocations by block: {}; edges: 0
  adaptation curve ACC:   135 180 221 1475 101 135 156 298 316 117 133 221 1475 1475 135 89 89 193 180 67 833 291 833 833 833 445 169 833 833 833 310 47 614 836 1249 1249 1249 1249 1249 1249 1225 974 192 1665 1665 368 1249 152 323 1665
  adaptation curve FRESH: 135 180 221 1475 101 135 156 298 316 117 133 221 1475 1475 135 89 89 193 180 67 833 291 833 833 833 445 169 833 833 833 310 47 614 836 1249 1249 1249 1249 1249 1249 1225 974 192 1665 1665 368 1249 152 323 1665
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

