CRIUS CAMPAIGN 0 REPORT  run=search_c1b_seeded_s3  arm=seeded
code_commit=6364d6994 dirty=True config_hash=bbf684cd638167f2 world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  26.4779   25.7276        12.1572        43          2
    26  20.4000   20.4000         7.9884        43         49
    51  19.4403   18.5693        11.7872        42         79
    76  10.3094   10.3001         5.0949        45        104
   101  23.3697   22.4948        10.2934        39        132
   126  12.3134   12.3133         5.9408        29        155
   151  23.4787   21.7029        12.2416        53        176
   176  13.3434   13.3431        10.1683        53        205
   201  33.4843   33.4843        22.0737        48        240
   226  17.3914   17.3912         9.4022        40        274
   251  19.3960   18.5202        10.3987        28        319
   276  16.3971   15.6434         8.1346        17        371
   300   6.2487    6.2486         2.8879        22        416
  candidates evaluated: 7208   best_ever 33.4843 (10175652a8ff2f23)  wall 416s

BEST PROGRAM 10175652a8ff2f23 (len 48, iteration 201, modification const@37+replace@16+delete@47)
  search seed 301201: fit 33.4843 succ 33/50 inter 1852 steps 7573 ws_cost 50 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [52.783, 1.0], "B": [29.487, 1.0], "C": [33.057, 0.5], "D": [41.426, 0.4], "E": [36.822, 0.375]}
  listing:
      0  INPUT          R1, num_ops
      1  CONST          R5, -1
      2  WS_REC_GET     R0, R1, R5
      3  ACT            R1
      4  MOD            R3, R0, R1
      5  ACT            R3
      6  DIV            R4, R0, R1
      7  MOD            R3, R4, R1
      8  ACT            R3
      9  ADD            R0, R0, R5
     10  JMP            3
     11  BLK_PATCH      R1, R0, R5
     12  WS_WRITE       R4, R2
     13  BLK_PATCH      R3, R4, R0
     14  BLK_PATCH      R2, R0, R5
     15  BLK_DELETE     R2
     16  WS_APPEND      R4, R0
     17  WS_REC_GET     R7, R5, R3
     18  WS_SREAD       R5, R0, R4
     19  WS_REC_GET     R0, R1, R5
     20  BLK_APPEND     R7, R3
     21  MUL            R2, R1, R1
     22  MOD            R3, R0, R1
     23  ACT            R3
     24  MOV            R1, R0
     25  BLK_STATE_SET  R1, R4, R3
     26  BLK_COPY       R1, R5
     27  WS_REC_GET     R7, R5, R6
     28  BLK_COMPOSE    R5, R6, R5
     29  WS_SREAD       R6, R0, R4
     30  WS_SREAD       R1, R0, R5
     31  BLK_APPEND     R7, R3
     32  WS_REC_GET     R7, R5, R3
     33  MOV            R1, R7
     34  WS_ALLOC       R3, R6
     35  ADD            R0, R0, R5
     36  ACT            R7
     37  ACTI           -17
     38  BLK_PATCH      R7, R1, R1
     39  WS_LINKS       R7, R7
     40  BLK_COMPOSE    R5, R6, R5
     41  WS_SREAD       R1, R0, R5
     42  BLK_STATE_SET  R1, R2, R3
     43  VLEN           R3, R0
     44  BLK_COPY       R5, R0
     45  MOV            R1, R0
     46  MOV            R6, R3
     47  HALT           
  ancestry (126 steps, newest first): iteration/fitness/modification
    it  201  33.4843  len 48  const@37+replace@16+delete@47
    it  200  17.4106  len 49  arg@33.1
    it  199  22.4750  len 49  delete@38+delete@47
    it  197  26.4820  len 51  const@37+delete@42+replace@40
    it  196  21.4680  len 52  delete@50
    it  195  27.4764  len 53  delete@11+swap@47,45
    it  194  20.4708  len 54  arg@28.2
    it  193  27.4822  len 54  replace@14+delete@30
    it  192  20.4322  len 55  swap@44,20+delete@53+insert@39
    it  190  9.2494  len 55  arg@46.1+delete@2+replace@43
    it  189  13.3433  len 56  arg@42.1
    it  188  24.4748  len 56  delete@15
    it  187  16.4069  len 57  swap@49,19
    it  186  18.3814  len 57  delete@30
    it  185  9.2945  len 58  duplicate@46+1->3
    ... 112 more

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7316.0    4.3   74.7
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.3    2.7    1.7
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ancestor1_it0_0875253d162c  19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       0.0    0.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       0.0    0.0    0.0
  top1_eed569b9f71c3338       16.037  16.037  16.037  16.037  15.7  15.7    15370    15370       0.0    0.0    0.0
  top2_66565858d26cedee       16.037  16.037  16.037  16.037  15.7  15.7    15370    15370       0.0    0.0    0.0
  top3_4a3afe469fc4af46       16.037  16.037  16.037  16.037  15.7  15.7    15370    15370       0.0    0.0    0.0
  contemp_15fd3bb0bdffebc1    16.037  16.037  16.037  16.037  15.7  15.7    15386    15386       0.0    0.0    0.0
  bestever_10175652a8ff2f23   16.034  16.034  16.034  16.034  15.7  15.7    15687    15687       0.0    0.0    0.0
  ancestor182_it292_325eca3b  15.701  15.701  15.701  15.701  15.3  15.3    15657    15657       0.0    0.0    0.0
  ancestor92_it155_d02546dcc  15.018  15.018  15.018  15.018  14.7  14.7     4623     4623       0.0    0.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0
  contemp_076a0ff4fded98dd     0.163   0.163   0.163   0.163   0.0   0.0        0        0       0.0    0.0    0.0
  contemp_d3fe24304691f37e     0.163   0.163   0.163   0.163   0.0   0.0      100      100       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.00/ 455.13   14.90/ 539.10   21.11/  47.94   33.21/  48.94   40.07/  50.52
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.13/ 443.81  528.11/ 527.79   47.93/  47.89   48.85/  48.88   50.42/  50.46
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ancestor1_it0_0875253d162c  494.04/ 494.04  523.26/ 523.26   49.99/  49.99   50.96/  50.96   52.68/  52.68
  ENUMERATE_VM_C1             494.04/ 494.04  523.26/ 523.26   49.99/  49.99   50.96/  50.96   52.68/  52.68
  top1_eed569b9f71c3338       699.76/ 699.76  748.53/ 748.53   49.47/  49.47   49.99/  49.99   51.71/  51.71
  top2_66565858d26cedee       699.76/ 699.76  748.53/ 748.53   49.47/  49.47   49.99/  49.99   51.71/  51.71
  top3_4a3afe469fc4af46       699.77/ 699.77  748.54/ 748.54   49.48/  49.48   50.00/  50.00   51.72/  51.72
  contemp_15fd3bb0bdffebc1    700.47/ 700.47  749.21/ 749.21   49.54/  49.54   50.04/  50.04   51.73/  51.73
  bestever_10175652a8ff2f23   705.68/ 705.68  777.23/ 777.23   48.07/  48.07   51.02/  51.02   50.03/  50.03
  ancestor182_it292_325eca3b  703.48/ 703.48  775.14/ 775.14   47.71/  47.71   50.90/  50.90   52.01/  52.01
  ancestor92_it155_d02546dcc  877.71/ 877.71  795.39/ 795.39   49.26/  49.26   49.90/  49.90   50.77/  50.77
  RANDOM_C1                  1661.96/1661.96 1626.54/1626.54   50.44/  50.44   50.50/  50.50   48.40/  48.40
  contemp_076a0ff4fded98dd   2000.02/2000.02 2000.02/2000.02   50.02/  50.02   50.02/  50.02   50.02/  50.02
  contemp_d3fe24304691f37e   2000.25/2000.25 2000.25/2000.25   50.25/  50.25   50.25/  50.25   50.25/  50.25

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ancestor1_it0_0875253d162c     2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  top1_eed569b9f71c3338          3/36    47     2/30    48     1/12    49     0/12    50    21/30   673    20/30   720
  top2_66565858d26cedee          3/36    47     2/30    48     1/12    49     0/12    50    21/30   673    20/30   720
  top3_4a3afe469fc4af46          3/36    47     2/30    48     1/12    49     0/12    50    21/30   673    20/30   720
  contemp_15fd3bb0bdffebc1       3/36    48     2/30    48     1/12    49     0/12    50    21/30   673    20/30   720
  bestever_10175652a8ff2f23      4/36    46     1/30    49     0/12    50     1/12    46    21/30   678    20/30   747
  ancestor182_it292_325eca3b     4/36    46     1/30    49     0/12    50     0/12    50    21/30   676    20/30   745
  ancestor92_it155_d02546dcc     4/36    47     2/30    48     1/12    47     0/12    50    18/30   171    19/30   148
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610
  contemp_076a0ff4fded98dd       0/36     0     0/30     0     0/12     0     0/12     0     0/30     0     0/30     0
  contemp_d3fe24304691f37e       0/36     2     0/30     2     0/12     2     0/12     2     0/30     2     0/30     2

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.26    49.53    36.26    36.26    49.53    49.53    49.53   4.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.55    49.55    49.55    49.55    49.55    49.55    49.55   1.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ancestor1_it0_0875253d162c    51.73       --    51.73    51.73    51.73    51.73    51.73   0.0
  ENUMERATE_VM_C1               51.73       --    51.73    51.73    51.73    51.73    51.73   0.0
  top1_eed569b9f71c3338         50.75       --    50.75    50.75    50.75    50.75    50.75   0.0
  top2_66565858d26cedee         50.75       --    50.75    50.75    50.75    50.75    50.75   0.0
  top3_4a3afe469fc4af46         50.76       --    50.76    50.76    50.76    50.76    50.76   0.0
  contemp_15fd3bb0bdffebc1      50.79       --    50.79    50.79    50.79    50.79    50.79   0.0
  bestever_10175652a8ff2f23     50.58       --    50.58    50.58    50.58    50.58    50.58   0.0
  ancestor182_it292_325eca3b    51.39       --    51.39    51.39    51.39    51.39    51.39   0.0
  ancestor92_it155_d02546dcc    50.29       --    50.29    50.29    50.29    50.29    50.29   0.0
  RANDOM_C1                     49.57       --    49.57    49.57    49.57    49.57    49.57   0.0
  contemp_076a0ff4fded98dd      50.02       --    50.02    50.02    50.02    50.02    50.02   0.0
  contemp_d3fe24304691f37e      50.25       --    50.25    50.25    50.25    50.25    50.25   0.0

CHARTER s13 CHECKLIST (seeds passing / seeds; thresholds: 5 percent relative; guard 0 added 2026-09-19, see report.py)
  PROCEDURE_REUSE_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [48, 48, 41] vs FRESH [20, 19, 22]
    1_cost_declines_via_accumulation       3/3  reuse_gain C-E per seed [736.2, 717.2, 235.3] vs 5% of FRESH cost [1515.6, 1467.2, 1423.8] (and 0 held)
    2_reproduces_on_heldout                3/3  same test, qualification suite; seeds passing = 3/3
    3_state_causal_FULL_vs_CODE_ONLY       2/3  remainder mean cost FULL [30.57, 30.13, 48.08] vs CODE_ONLY [50.41, 50.41, 47.78]
    4_scramble_or_reset_damages            3/3  eff ACC [48.449, 48.475, 41.476] SCR [20.443, 21.469, 22.474] RESET [20.443, 21.469, 22.475]
    5_transfers_to_fresh_copy              2/3  FULL [30.57, 30.13, 48.08] vs ACC remainder [30.57, 30.13, 48.08]
    6_executable_components_reused         2/3  invocations [82, 81, 61]; ABLATION_ALL cost [50.41, 50.41, 47.78] vs ACC remainder [30.57, 30.13, 48.08]
    7_not_compute_or_storage               2/3  COMPUTE_MATCHED [50.41, 50.41, 47.78] STORAGE_MATCHED [50.41, 50.41, 47.78] vs ACC remainder [30.57, 30.13, 48.08]
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
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [1.2, -1.6, 0.8] vs 5% of FRESH cost [1513.8, 1465.5, 1422.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.42, 50.42, 47.8] vs CODE_ONLY [50.42, 50.42, 47.8]
    4_scramble_or_reset_damages            0/3  eff ACC [20.37, 19.409, 22.447] SCR [20.37, 19.409, 22.447] RESET [20.37, 19.409, 22.447]
    5_transfers_to_fresh_copy              0/3  FULL [50.42, 50.42, 47.8] vs ACC remainder [50.42, 50.42, 47.8]
    6_executable_components_reused         0/3  invocations [3, 1, 1]; ABLATION_ALL cost [50.42, 50.42, 47.8] vs ACC remainder [50.42, 50.42, 47.8]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.42, 50.42, 47.8] STORAGE_MATCHED [50.42, 50.42, 47.8] vs ACC remainder [50.42, 50.42, 47.8]
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
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1580.4, 1529.9, 1482.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.68, 52.68, 49.82] vs CODE_ONLY [52.68, 52.68, 49.82]
    4_scramble_or_reset_damages            0/3  eff ACC [18.368, 18.401, 22.446] SCR [18.368, 18.401, 22.446] RESET [18.368, 18.401, 22.446]
    5_transfers_to_fresh_copy              0/3  FULL [52.68, 52.68, 49.82] vs ACC remainder [52.68, 52.68, 49.82]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.68, 52.68, 49.82]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.68, 52.68, 49.82] STORAGE_MATCHED [52.68, 52.68, 49.82] vs ACC remainder [52.68, 52.68, 49.82]
  ENUMERATE_VM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 18, 22] vs FRESH [18, 18, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1580.4, 1529.9, 1482.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.68, 52.68, 49.82] vs CODE_ONLY [52.68, 52.68, 49.82]
    4_scramble_or_reset_damages            0/3  eff ACC [18.368, 18.401, 22.446] SCR [18.368, 18.401, 22.446] RESET [18.368, 18.401, 22.446]
    5_transfers_to_fresh_copy              0/3  FULL [52.68, 52.68, 49.82] vs ACC remainder [52.68, 52.68, 49.82]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.68, 52.68, 49.82]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.68, 52.68, 49.82] STORAGE_MATCHED [52.68, 52.68, 49.82] vs ACC remainder [52.68, 52.68, 49.82]
  top1_eed569b9f71c3338
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [13, 13, 21] vs FRESH [13, 13, 21]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1559.9, 1503.8, 1458.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.1, 51.58, 48.58] vs CODE_ONLY [52.1, 51.58, 48.58]
    4_scramble_or_reset_damages            0/3  eff ACC [13.348, 13.327, 21.435] SCR [13.348, 13.327, 21.435] RESET [13.348, 13.327, 21.435]
    5_transfers_to_fresh_copy              0/3  FULL [52.1, 51.58, 48.58] vs ACC remainder [52.1, 51.58, 48.58]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.1, 51.58, 48.58]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.1, 51.58, 48.58] STORAGE_MATCHED [52.1, 51.58, 48.58] vs ACC remainder [52.1, 51.58, 48.58]
  top2_66565858d26cedee
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [13, 13, 21] vs FRESH [13, 13, 21]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1559.9, 1503.8, 1458.0] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.1, 51.58, 48.58] vs CODE_ONLY [52.1, 51.58, 48.58]
    4_scramble_or_reset_damages            0/3  eff ACC [13.348, 13.327, 21.435] SCR [13.348, 13.327, 21.435] RESET [13.348, 13.327, 21.435]
    5_transfers_to_fresh_copy              0/3  FULL [52.1, 51.58, 48.58] vs ACC remainder [52.1, 51.58, 48.58]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.1, 51.58, 48.58]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.1, 51.58, 48.58] STORAGE_MATCHED [52.1, 51.58, 48.58] vs ACC remainder [52.1, 51.58, 48.58]
  top3_4a3afe469fc4af46
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [13, 13, 21] vs FRESH [13, 13, 21]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1560.2, 1504.1, 1458.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.11, 51.59, 48.59] vs CODE_ONLY [52.11, 51.59, 48.59]
    4_scramble_or_reset_damages            0/3  eff ACC [13.348, 13.327, 21.435] SCR [13.348, 13.327, 21.435] RESET [13.348, 13.327, 21.435]
    5_transfers_to_fresh_copy              0/3  FULL [52.11, 51.59, 48.59] vs ACC remainder [52.11, 51.59, 48.59]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.11, 51.59, 48.59]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.11, 51.59, 48.59] STORAGE_MATCHED [52.11, 51.59, 48.59] vs ACC remainder [52.11, 51.59, 48.59]
  contemp_15fd3bb0bdffebc1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [13, 13, 21] vs FRESH [13, 13, 21]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1560.3, 1505.3, 1460.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.08, 51.62, 48.67] vs CODE_ONLY [52.08, 51.62, 48.67]
    4_scramble_or_reset_damages            0/3  eff ACC [13.348, 13.327, 21.435] SCR [13.348, 13.327, 21.435] RESET [13.348, 13.327, 21.435]
    5_transfers_to_fresh_copy              0/3  FULL [52.08, 51.62, 48.67] vs ACC remainder [52.08, 51.62, 48.67]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.08, 51.62, 48.67]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.08, 51.62, 48.67] STORAGE_MATCHED [52.08, 51.62, 48.67] vs ACC remainder [52.08, 51.62, 48.67]
  bestever_10175652a8ff2f23
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [14, 13, 20] vs FRESH [14, 13, 20]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1485.8, 1481.6, 1494.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.36, 52.02, 50.35] vs CODE_ONLY [49.36, 52.02, 50.35]
    4_scramble_or_reset_damages            0/3  eff ACC [14.34, 13.331, 20.432] SCR [14.34, 13.331, 20.432] RESET [14.34, 13.331, 20.432]
    5_transfers_to_fresh_copy              0/3  FULL [49.36, 52.02, 50.35] vs ACC remainder [49.36, 52.02, 50.35]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.36, 52.02, 50.35]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.36, 52.02, 50.35] STORAGE_MATCHED [49.36, 52.02, 50.35] vs ACC remainder [49.36, 52.02, 50.35]
  ancestor182_it292_325eca3b438c08d4
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [13, 13, 20] vs FRESH [13, 13, 20]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1530.2, 1475.1, 1487.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.01, 52.01, 50.16] vs CODE_ONLY [52.01, 52.01, 50.16]
    4_scramble_or_reset_damages            0/3  eff ACC [13.34, 13.331, 20.432] SCR [13.34, 13.331, 20.432] RESET [13.34, 13.331, 20.432]
    5_transfers_to_fresh_copy              0/3  FULL [52.01, 52.01, 50.16] vs ACC remainder [52.01, 52.01, 50.16]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.01, 52.01, 50.16]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.01, 52.01, 50.16] STORAGE_MATCHED [52.01, 52.01, 50.16] vs ACC remainder [52.01, 52.01, 50.16]
  ancestor92_it155_d02546dcc0e72090
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [9, 13, 22] vs FRESH [9, 13, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1539.9, 1501.2, 1447.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.52, 50.19, 48.15] vs CODE_ONLY [52.52, 50.19, 48.15]
    4_scramble_or_reset_damages            0/3  eff ACC [9.281, 13.334, 22.441] SCR [9.281, 13.334, 22.441] RESET [9.281, 13.334, 22.441]
    5_transfers_to_fresh_copy              0/3  FULL [52.52, 50.19, 48.15] vs ACC remainder [52.52, 50.19, 48.15]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.52, 50.19, 48.15]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.52, 50.19, 48.15] STORAGE_MATCHED [52.52, 50.19, 48.15] vs ACC remainder [52.52, 50.19, 48.15]
  RANDOM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 6, 9] vs FRESH [6, 6, 9]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1491.8, 1515.0, 1485.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.21, 50.5, 48.99] vs CODE_ONLY [49.21, 50.5, 48.99]
    4_scramble_or_reset_damages            0/3  eff ACC [6.205, 6.235, 9.221] SCR [6.205, 6.235, 9.221] RESET [6.205, 6.235, 9.221]
    5_transfers_to_fresh_copy              0/3  FULL [49.21, 50.5, 48.99] vs ACC remainder [49.21, 50.5, 48.99]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.21, 50.5, 48.99]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.21, 50.5, 48.99] STORAGE_MATCHED [49.21, 50.5, 48.99] vs ACC remainder [49.21, 50.5, 48.99]
  contemp_076a0ff4fded98dd
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1500.6, 1500.6, 1500.6] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.02, 50.02, 50.02] vs CODE_ONLY [50.02, 50.02, 50.02]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 0.163] SCR [0.163, 0.163, 0.163] RESET [0.163, 0.163, 0.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.02, 50.02, 50.02] vs ACC remainder [50.02, 50.02, 50.02]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.02, 50.02, 50.02]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.02, 50.02, 50.02] STORAGE_MATCHED [50.02, 50.02, 50.02] vs ACC remainder [50.02, 50.02, 50.02]
  contemp_d3fe24304691f37e
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [0, 0, 0] vs FRESH [0, 0, 0]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1507.5, 1507.5, 1507.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.25, 50.25, 50.25] vs CODE_ONLY [50.25, 50.25, 50.25]
    4_scramble_or_reset_damages            0/3  eff ACC [0.163, 0.163, 0.163] SCR [0.163, 0.163, 0.163] RESET [0.163, 0.163, 0.163]
    5_transfers_to_fresh_copy              0/3  FULL [50.25, 50.25, 50.25] vs ACC remainder [50.25, 50.25, 50.25]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.25, 50.25, 50.25]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.25, 50.25, 50.25] STORAGE_MATCHED [50.25, 50.25, 50.25] vs ACC remainder [50.25, 50.25, 50.25]

MACHINERY OF top1_eed569b9f71c3338 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   0     0
    task  9:     0    0    0    0    0 |   0     0
    task 19:     0    0    0    0    0 |   0     0
    task 31:     0    0    0    0    0 |   0     0
    task 41:     0    0    0    0    0 |   0     0
    task 49:     0    0    0    0    0 |   0     0
  artifact events: 0 (create 0, delete 0, patch/append 0); invocations by block: {}; edges: 0
  adaptation curve ACC:   3 2080 24 2080 3 3 18 2080 149 186 45 24 2080 2080 3 2080 2080 24 2080 12 52 49 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
  adaptation curve FRESH: 3 2080 24 2080 3 3 18 2080 149 186 45 24 2080 2080 3 2080 2080 24 2080 12 52 49 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
  reuse_gain per task:    0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0

BASELINES ON SEARCH SUITE (crius/runs/baselines_c1b): effA effF effR effS  succA  interA interF  reuse_gain  blocks
  ENUMERATE_C1_seed301     21.473 21.473 21.473 21.473   21    3358   3358        0.0    0
  ENUMERATE_C1_seed302     19.412 19.412 19.412 19.412   19   10771  10771        0.0    0
  ENUMERATE_C1_seed303     22.479 22.479 22.479 22.479   22    2548   2548        0.0    0
  ENUMERATE_VM_C1_seed301  21.471 21.471 21.471 21.471   21    3358   3358        0.0    0
  ENUMERATE_VM_C1_seed302  19.397 19.397 19.397 19.397   19   12109  12109        0.0    0
  ENUMERATE_VM_C1_seed303  22.471 22.471 22.471 22.471   22    3428   3428        0.0    0
  PROCEDURE_NOCAL_C1_seed301 21.471 21.471 21.471 21.471   21    3538   3538      -49.9    3
  PROCEDURE_NOCAL_C1_seed302 19.410 19.411 19.411 19.410   19   10917  10915      -45.5    3
  PROCEDURE_NOCAL_C1_seed303 22.477 22.478 22.478 22.477   22    2732   2728      -59.1    5
  PROCEDURE_REUSE_C1_seed301 50.488 21.470 21.481 21.481   50    1338   3718     2288.5    4
  PROCEDURE_REUSE_C1_seed302 49.459 18.410 21.453 21.453   49    4787  11057     6085.5    6
  PROCEDURE_REUSE_C1_seed303 50.492 22.476 22.484 22.483   50     948   2908     1895.0    5
  QUIT_C1_seed301          20.472 20.472 20.472 20.472   20    1907   1907        0.0    0
  QUIT_C1_seed302          17.412 17.412 17.412 17.412   17    9331   9331        0.0    0
  QUIT_C1_seed303          20.479 20.479 20.479 20.479   20    1135   1135        0.0    0
  RANDOM_C1_seed301         7.237  7.237  7.237  7.237    7   32013  32013        0.0    0
  RANDOM_C1_seed302         9.240  9.240  9.240  9.240    9   31692  31692        0.0    0
  RANDOM_C1_seed303        12.283 12.283 12.283 12.283   12   26477  26477        0.0    0
  TABLE_MEMO_C1_seed301    21.472 21.473 21.473 21.472   21    3358   3358      -15.9    0
  TABLE_MEMO_C1_seed302    19.412 19.412 19.412 19.412   19   10771  10771      -13.8    0
  TABLE_MEMO_C1_seed303    22.479 22.479 22.479 22.479   22    2548   2548      -16.7    0

