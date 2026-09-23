CRIUS CAMPAIGN 0 REPORT  run=search_c1_seeded_s2  arm=seeded
code_commit=97af44f88 dirty=True config_hash=32dfb243be9fdec9 world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  16.2182   13.1989         3.9204        37          3
    26  35.3537   34.4767        13.6583        37         76
    51  18.2253   14.7146        10.3392        46        156
    76  27.3031   26.4194        15.3252        40        232
   101  37.3856   37.3852        24.9994        42        307
   126  20.2030   20.2030        13.4105        46        374
   151  33.3460   33.3460        20.7005        35        451
   176  30.3161   30.0629        18.5916        38        542
   201  33.3548   30.3446        21.9372        46        622
   226  40.4036   40.4036        21.3327        41        698
   251  27.3265   27.3235        16.8160        46        770
   276  28.3378   28.3378        20.8463        59        835
   300  36.3707   35.7285        23.2656        58        892
  candidates evaluated: 7208   best_ever 46.4187 (aca1ba02cfb4da1d)  wall 892s

BEST PROGRAM aca1ba02cfb4da1d (len 55, iteration 291, modification replace@10+replace@12+delete@50)
  search seed 201291: fit 46.4187 succ 46/50 inter 14106 steps 42566 ws_cost 2941 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [223.618, 1.0], "B": [182.018, 1.0], "C": [274.238, 0.833], "D": [605.123, 0.8], "E": [145.328, 1.0]}
  listing:
      0  BRZ            R3, 32
      1  ACT            R7
      2  INPUT          R1, num_ops
      3  ACT            R3
      4  NOT            R2, R6
      5  VSET           R3, R6, R1
      6  MOD            R3, R0, R3
      7  NOT            R7, R2
      8  INPUT          R5, task_index
      9  BLK_COPY       R6, R5
     10  BLK_REC_END    R1
     11  WS_WRITE       R2, R1
     12  WS_FREE        R5
     13  LT             R3, R3, R5
     14  WS_FIND        R5, R5
     15  WS_REC_SET     R4, R3, R1
     16  BLK_LEN        R1, R1
     17  WS_FREE        R7
     18  DIV            R0, R7, R1
     19  INPUT          R5, steps_left
     20  BLK_REC_BEGIN  
     21  BLK_COMPOSE    R2, R7, R3
     22  BRZ            R6, 1
     23  WS_WRITE       R3, R0
     24  WS_REC_SET     R3, R6, R2
     25  ACT            R3
     26  DIV            R4, R4, R1
     27  DIV            R4, R0, R1
     28  WS_REC_GET     R3, R2, R5
     29  BRZ            R7, 27
     30  EQ             R2, R1, R6
     31  BLK_DELETE     R3
     32  BLK_LEN        R1, R1
     33  WS_LINK_GET    R0, R7, R3
     34  ACT            R1
     35  INPUT          R1, num_ops
     36  ACT            R3
     37  WS_FIND        R5, R5
     38  MOD            R3, R4, R1
     39  ACT            R3
     40  DIV            R4, R4, R1
     41  MOD            R3, R4, R1
     42  ACT            R3
     43  ACTI           8
     44  DIV            R4, R0, R1
     45  MOD            R3, R0, R3
     46  ADD            R0, R0, R5
     47  ACT            R3
     48  JMP            34
     49  WS_WRITE       R2, R1
     50  DIV            R3, R0, R1
     51  HALT           
     52  ADD            R0, R0, R5
     53  WS_WRITE       R2, R1
     54  ADD            R1, R0, R1
  ancestry (173 steps, newest first): iteration/fitness/modification
    it  291  46.4187  len 55  replace@10+replace@12+delete@50
    it  289  31.3561  len 56  insert@43
    it  287  22.2313  len 55  replace@55+delete@13
    it  286  36.3843  len 56  delete@26
    it  285  24.2982  len 57  delete@15+delete@7
    it  282  32.3658  len 59  arg@32.1+swap@6,9
    it  281  26.3224  len 59  replace@8+arg@6.0
    it  274  35.3724  len 59  arg@6.1+delete@38+delete@8
    it  273  41.3835  len 61  delete@39+replace@11
    it  272  30.3032  len 62  insert@36+delete@25+arg@25.1
    it  270  36.3678  len 62  duplicate@43+6->8+arg@27.0+duplicate@43+1->53
    it  269  35.3730  len 55  duplicate@23+1->12+replace@4
    it  268  23.2599  len 54  delete@44+delete@24+arg@21.1
    it  267  29.3272  len 56  replace@26+duplicate@29+2->13+arg@22.1
    it  266  25.2816  len 54  delete@49+delete@1+arg@18.0
    ... 159 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          47.117  26.961  27.664  27.999  46.7  26.7     8916    38056   29005.3    4.3   74.7
  bestever_aca1ba02cfb4da1d   28.644  28.644  28.644  28.644  28.3  28.3    33968    33968       0.0    0.0    0.0
  contemp_a2b3a0212d70618e    28.644  28.644  28.644  28.644  28.3  28.3    33968    33968       0.0    0.0    0.0
  ancestor181_it298_40206d78  28.644  28.644  28.644  28.644  28.3  28.3    33968    33968       0.0    0.0    0.0
  top1_004f85fcb612a651       27.633  27.633  27.633  27.633  27.3  27.3    35978    35978       0.0    0.0    0.0
  top2_588c0c61972ec326       27.633  27.633  27.633  27.633  27.3  27.3    35978    35978       0.0    0.0    0.0
  top3_5e5b294f552c03da       27.633  27.633  27.633  27.633  27.3  27.3    35978    35978       0.0    0.0    0.0
  ancestor91_it146_f0fe81e6e  26.965  26.965  26.965  26.965  26.7  26.7    36022    36022       0.0    0.0    0.0
  ENUMERATE_C1                26.964  26.964  26.964  26.964  26.7  26.7    37456    37456       0.0    0.0    0.0
  TABLE_MEMO_C1               26.964  26.964  26.964  26.964  26.7  26.7    37456    37456     -17.9    0.0    0.0
  PROCEDURE_NOCAL_C1          26.962  26.962  26.962  26.962  26.7  26.7    37759    37756     -23.8    3.3    1.7
  ancestor1_it0_0875253d162c  25.287  25.287  25.287  25.287  25.0  25.0    37856    37856       0.0    0.0    0.0
  ENUMERATE_VM_C1             25.287  25.287  25.287  25.287  25.0  25.0    37856    37856       0.0    0.0    0.0
  QUIT_C1                     19.605  19.605  19.605  19.605  19.3  19.3     9448     9448       0.0    0.0    0.0
  contemp_a9aaab1628449d87    17.213  17.213  17.213  17.213  17.0  17.0    51283    51283       0.0    0.0    0.0
  RANDOM_C1                   10.160  10.160  10.160  10.160  10.0  10.0    62546    62546       0.0    0.0    0.0
  contemp_77a5b50b96ae51c9     7.810   7.810   7.810   7.810   7.7   7.7    63682    63682       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.00/ 455.13   14.90/ 539.10   36.22/ 623.47  177.39/1089.94  477.07/1237.03
  bestever_aca1ba02cfb4da1d   384.11/ 384.11  432.86/ 432.86  640.12/ 640.12  926.68/ 926.68 1242.49/1242.49
  contemp_a2b3a0212d70618e    384.11/ 384.11  432.86/ 432.86  640.12/ 640.12  926.68/ 926.68 1242.49/1242.49
  ancestor181_it298_40206d78  384.11/ 384.11  432.86/ 432.86  640.12/ 640.12  926.68/ 926.68 1242.49/1242.49
  top1_004f85fcb612a651       523.19/ 523.19  736.99/ 736.99  572.04/ 572.04  875.74/ 875.74 1113.58/1113.58
  top2_588c0c61972ec326       523.19/ 523.19  736.99/ 736.99  572.04/ 572.04  875.74/ 875.74 1113.58/1113.58
  top3_5e5b294f552c03da       523.19/ 523.19  736.99/ 736.99  572.04/ 572.04  875.74/ 875.74 1113.58/1113.58
  ancestor91_it146_f0fe81e6e  459.75/ 459.75  461.48/ 461.48  620.90/ 620.90 1070.37/1070.37 1262.14/1262.14
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31  615.85/ 615.85 1086.47/1086.47 1232.75/1232.75
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34  616.29/ 615.86 1086.97/1086.48 1233.28/1232.76
  PROCEDURE_NOCAL_C1          444.13/ 443.81  528.11/ 527.79  619.85/ 619.71 1088.59/1088.26 1236.48/1234.94
  ancestor1_it0_0875253d162c  494.04/ 494.04  523.26/ 523.26  664.50/ 664.50 1116.70/1116.70 1283.87/1283.87
  ENUMERATE_VM_C1             494.04/ 494.04  523.26/ 523.26  664.50/ 664.50 1116.70/1116.70 1283.87/1283.87
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31  800.00/ 800.00 1200.00/1200.00 1400.00/1400.00
  contemp_a9aaab1628449d87   1035.06/1035.06 1343.93/1343.93  742.61/ 742.61 1069.67/1069.67 1226.28/1226.28
  RANDOM_C1                  1661.96/1661.96 1626.54/1626.54  726.73/ 726.73 1161.23/1161.23 1244.20/1244.20
  contemp_77a5b50b96ae51c9   1653.78/1653.78 1597.76/1597.76  824.41/ 824.41 1247.95/1247.95 1417.43/1417.43

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            36/36    33    27/30   167     6/12   809    11/12   117    30/30   301    30/30    14
  bestever_aca1ba02cfb4da1d     12/36   620    10/30   898     4/12  1258     2/12  1150    30/30   372    27/30   419
  contemp_a2b3a0212d70618e      12/36   620    10/30   898     4/12  1258     2/12  1150    30/30   372    27/30   419
  ancestor181_it298_40206d78    12/36   620    10/30   898     4/12  1258     2/12  1150    30/30   372    27/30   419
  top1_004f85fcb612a651         14/36   554    11/30   849     3/12  1266     5/12   892    27/30   507    22/30   714
  top2_588c0c61972ec326         14/36   554    11/30   849     3/12  1266     5/12   892    27/30   507    22/30   714
  top3_5e5b294f552c03da         14/36   554    11/30   849     3/12  1266     5/12   892    27/30   507    22/30   714
  ancestor91_it146_f0fe81e6e    14/36   597     6/30  1029     2/12  1356     3/12  1072    27/30   442    28/30   444
  ENUMERATE_C1                  13/36   613     5/30  1082     2/12  1350     2/12  1106    29/30   431    29/30   514
  TABLE_MEMO_C1                 13/36   613     5/30  1082     2/12  1350     2/12  1106    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1            13/36   617     5/30  1084     2/12  1352     2/12  1108    29/30   442    29/30   526
  ancestor1_it0_0875253d162c    11/36   635     6/30  1068     2/12  1350     2/12  1107    27/30   472    27/30   500
  ENUMERATE_VM_C1               11/36   635     6/30  1068     2/12  1350     2/12  1107    27/30   472    27/30   500
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  contemp_a9aaab1628449d87       6/36   716     6/30  1031     4/12  1274     2/12  1090    20/30   998    13/30  1295
  RANDOM_C1                      6/36   720     2/30  1150     2/12  1430     2/12  1034    10/30  1646     8/30  1610
  contemp_77a5b50b96ae51c9       2/36   793     0/30  1200     0/12  1600     1/12  1126    10/30  1590    10/30  1536

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1           310.58  1153.44   310.58   310.58  1153.44  1153.44  1153.44   4.0
  bestever_aca1ba02cfb4da1d   1067.04       --  1067.04  1067.04  1067.04  1067.04  1067.04   0.0
  contemp_a2b3a0212d70618e    1067.04       --  1067.04  1067.04  1067.04  1067.04  1067.04   0.0
  ancestor181_it298_40206d78  1067.04       --  1067.04  1067.04  1067.04  1067.04  1067.04   0.0
  top1_004f85fcb612a651        981.44       --   981.44   981.44   981.44   981.44   981.44   0.0
  top2_588c0c61972ec326        981.44       --   981.44   981.44   981.44   981.44   981.44   0.0
  top3_5e5b294f552c03da        981.44       --   981.44   981.44   981.44   981.44   981.44   0.0
  ancestor91_it146_f0fe81e6e  1155.60       --  1155.60  1155.60  1155.60  1155.60  1155.60   0.0
  ENUMERATE_C1                1151.49       --  1151.49  1151.49  1151.49  1151.49  1151.49   0.0
  TABLE_MEMO_C1               1152.00       --  1151.52  1152.00  1151.52  1151.52  1151.52   0.0
  PROCEDURE_NOCAL_C1          1154.32  1153.42  1154.32  1154.32  1153.42  1153.42  1153.42   1.3
  ancestor1_it0_0875253d162c  1191.00       --  1191.00  1191.00  1191.00  1191.00  1191.00   0.0
  ENUMERATE_VM_C1             1191.00       --  1191.00  1191.00  1191.00  1191.00  1191.00   0.0
  QUIT_C1                     1288.89       --  1288.89  1288.89  1288.89  1288.89  1288.89   0.0
  contemp_a9aaab1628449d87    1139.28       --  1139.28  1139.28  1139.28  1139.28  1139.28   0.0
  RANDOM_C1                   1198.10       --  1198.10  1198.10  1198.10  1198.10  1198.10   0.0
  contemp_77a5b50b96ae51c9    1323.27       --  1323.27  1323.27  1323.27  1323.27  1323.27   0.0

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
  bestever_aca1ba02cfb4da1d
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [27, 27, 31] vs FRESH [27, 27, 31]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [28416.5, 27126.6, 25121.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1107.09, 1103.26, 990.77] vs CODE_ONLY [1107.09, 1103.26, 990.77]
    4_scramble_or_reset_damages            0/3  eff ACC [27.317, 27.304, 31.312] SCR [27.317, 27.304, 31.312] RESET [27.317, 27.304, 31.312]
    5_transfers_to_fresh_copy              0/3  FULL [1107.09, 1103.26, 990.77] vs ACC remainder [1107.09, 1103.26, 990.77]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1107.09, 1103.26, 990.77]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1107.09, 1103.26, 990.77] STORAGE_MATCHED [1107.09, 1103.26, 990.77] vs ACC remainder [1107.09, 1103.26, 990.77]
  contemp_a2b3a0212d70618e
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [27, 27, 31] vs FRESH [27, 27, 31]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [28416.5, 27126.6, 25121.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1107.09, 1103.26, 990.77] vs CODE_ONLY [1107.09, 1103.26, 990.77]
    4_scramble_or_reset_damages            0/3  eff ACC [27.317, 27.304, 31.312] SCR [27.317, 27.304, 31.312] RESET [27.317, 27.304, 31.312]
    5_transfers_to_fresh_copy              0/3  FULL [1107.09, 1103.26, 990.77] vs ACC remainder [1107.09, 1103.26, 990.77]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1107.09, 1103.26, 990.77]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1107.09, 1103.26, 990.77] STORAGE_MATCHED [1107.09, 1103.26, 990.77] vs ACC remainder [1107.09, 1103.26, 990.77]
  ancestor181_it298_40206d785b191555
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [27, 27, 31] vs FRESH [27, 27, 31]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [28416.5, 27126.6, 25121.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1107.09, 1103.26, 990.77] vs CODE_ONLY [1107.09, 1103.26, 990.77]
    4_scramble_or_reset_damages            0/3  eff ACC [27.317, 27.304, 31.312] SCR [27.317, 27.304, 31.312] RESET [27.317, 27.304, 31.312]
    5_transfers_to_fresh_copy              0/3  FULL [1107.09, 1103.26, 990.77] vs ACC remainder [1107.09, 1103.26, 990.77]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1107.09, 1103.26, 990.77]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1107.09, 1103.26, 990.77] STORAGE_MATCHED [1107.09, 1103.26, 990.77] vs ACC remainder [1107.09, 1103.26, 990.77]
  top1_004f85fcb612a651
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [28, 24, 30] vs FRESH [28, 24, 30]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [22892.4, 25604.4, 25094.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [892.9, 1066.91, 984.52] vs CODE_ONLY [892.9, 1066.91, 984.52]
    4_scramble_or_reset_damages            0/3  eff ACC [28.301, 24.288, 30.311] SCR [28.301, 24.288, 30.311] RESET [28.301, 24.288, 30.311]
    5_transfers_to_fresh_copy              0/3  FULL [892.9, 1066.91, 984.52] vs ACC remainder [892.9, 1066.91, 984.52]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [892.9, 1066.91, 984.52]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [892.9, 1066.91, 984.52] STORAGE_MATCHED [892.9, 1066.91, 984.52] vs ACC remainder [892.9, 1066.91, 984.52]
  top2_588c0c61972ec326
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [28, 24, 30] vs FRESH [28, 24, 30]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [22892.4, 25604.4, 25094.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [892.9, 1066.91, 984.52] vs CODE_ONLY [892.9, 1066.91, 984.52]
    4_scramble_or_reset_damages            0/3  eff ACC [28.301, 24.288, 30.311] SCR [28.301, 24.288, 30.311] RESET [28.301, 24.288, 30.311]
    5_transfers_to_fresh_copy              0/3  FULL [892.9, 1066.91, 984.52] vs ACC remainder [892.9, 1066.91, 984.52]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [892.9, 1066.91, 984.52]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [892.9, 1066.91, 984.52] STORAGE_MATCHED [892.9, 1066.91, 984.52] vs ACC remainder [892.9, 1066.91, 984.52]
  top3_5e5b294f552c03da
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [28, 24, 30] vs FRESH [28, 24, 30]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [22892.4, 25604.4, 25094.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [892.9, 1066.91, 984.52] vs CODE_ONLY [892.9, 1066.91, 984.52]
    4_scramble_or_reset_damages            0/3  eff ACC [28.301, 24.288, 30.311] SCR [28.301, 24.288, 30.311] RESET [28.301, 24.288, 30.311]
    5_transfers_to_fresh_copy              0/3  FULL [892.9, 1066.91, 984.52] vs ACC remainder [892.9, 1066.91, 984.52]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [892.9, 1066.91, 984.52]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [892.9, 1066.91, 984.52] STORAGE_MATCHED [892.9, 1066.91, 984.52] vs ACC remainder [892.9, 1066.91, 984.52]
  ancestor91_it146_f0fe81e6ec879ce6
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [26, 22, 32] vs FRESH [26, 22, 32]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [28626.3, 31111.7, 25016.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1134.94, 1248.81, 1083.06] vs CODE_ONLY [1134.94, 1248.81, 1083.06]
    4_scramble_or_reset_damages            0/3  eff ACC [26.277, 22.283, 32.335] SCR [26.277, 22.283, 32.335] RESET [26.277, 22.283, 32.335]
    5_transfers_to_fresh_copy              0/3  FULL [1134.94, 1248.81, 1083.06] vs ACC remainder [1134.94, 1248.81, 1083.06]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1134.94, 1248.81, 1083.06]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1134.94, 1248.81, 1083.06] STORAGE_MATCHED [1134.94, 1248.81, 1083.06] vs ACC remainder [1134.94, 1248.81, 1083.06]
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
  contemp_a9aaab1628449d87
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 19, 14] vs FRESH [18, 19, 14]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [30252.7, 29090.8, 28911.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1177.15, 1134.15, 1106.54] vs CODE_ONLY [1177.15, 1134.15, 1106.54]
    4_scramble_or_reset_damages            0/3  eff ACC [18.237, 19.213, 14.189] SCR [18.237, 19.213, 14.189] RESET [18.237, 19.213, 14.189]
    5_transfers_to_fresh_copy              0/3  FULL [1177.15, 1134.15, 1106.54] vs ACC remainder [1177.15, 1134.15, 1106.54]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1177.15, 1134.15, 1106.54]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1177.15, 1134.15, 1106.54] STORAGE_MATCHED [1177.15, 1134.15, 1106.54] vs ACC remainder [1177.15, 1134.15, 1106.54]
  RANDOM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [10, 8, 12] vs FRESH [10, 8, 12]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [29757.7, 31845.3, 29256.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1210.09, 1230.52, 1153.7] vs CODE_ONLY [1210.09, 1230.52, 1153.7]
    4_scramble_or_reset_damages            0/3  eff ACC [10.152, 8.161, 12.165] SCR [10.152, 8.161, 12.165] RESET [10.152, 8.161, 12.165]
    5_transfers_to_fresh_copy              0/3  FULL [1210.09, 1230.52, 1153.7] vs ACC remainder [1210.09, 1230.52, 1153.7]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1210.09, 1230.52, 1153.7]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1210.09, 1230.52, 1153.7] STORAGE_MATCHED [1210.09, 1230.52, 1153.7] vs ACC remainder [1210.09, 1230.52, 1153.7]
  contemp_77a5b50b96ae51c9
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [10, 3, 10] vs FRESH [10, 3, 10]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [33186.0, 34110.5, 33839.2] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [1289.03, 1340.39, 1340.39] vs CODE_ONLY [1289.03, 1340.39, 1340.39]
    4_scramble_or_reset_damages            0/3  eff ACC [10.182, 3.111, 10.137] SCR [10.182, 3.111, 10.137] RESET [10.182, 3.111, 10.137]
    5_transfers_to_fresh_copy              0/3  FULL [1289.03, 1340.39, 1340.39] vs ACC remainder [1289.03, 1340.39, 1340.39]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [1289.03, 1340.39, 1340.39]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [1289.03, 1340.39, 1340.39] STORAGE_MATCHED [1289.03, 1340.39, 1340.39] vs ACC remainder [1289.03, 1340.39, 1340.39]

MACHINERY OF top1_004f85fcb612a651 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   0     0
    task  9:     0    0    0    0    0 |   0     0
    task 19:     0    0    0    0    0 |   0     0
    task 31:     0    0    0    0    0 |   0     0
    task 41:     0    0    0    0    0 |   0     0
    task 49:     0    0    0    0    0 |   0     0
  artifact events: 0 (create 0, delete 0, patch/append 0); invocations by block: {}; edges: 0
  adaptation curve ACC:   340 588 7 2064 40 138 229 916 33 80 165 7 2064 2064 340 2064 2064 7 588 318 826 54 826 339 826 826 391 826 826 154 103 826 163 395 1238 1238 1238 1238 1238 1238 443 164 630 1651 1651 205 1238 392 57 1651
  adaptation curve FRESH: 340 588 7 2064 40 138 229 916 33 80 165 7 2064 2064 340 2064 2064 7 588 318 826 54 826 339 826 826 391 826 826 154 103 826 163 395 1238 1238 1238 1238 1238 1238 443 164 630 1651 1651 205 1238 392 57 1651
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

