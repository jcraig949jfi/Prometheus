CRIUS CAMPAIGN 0 REPORT  run=search_c1b_recombination_s2  arm=recombination
code_commit=6364d6994 dirty=True config_hash=bbf684cd638167f2 world=7c53db874324b532 partitions=624728b00fdd3f2f
==============================================================================
SEARCH PROGRESS (fitness = C1_FITNESS, mean over search streams; ACCUMULATED)
  iter   best     pop_mean  children_mean  best_len  elapsed_s
     1  16.3223   15.8023         4.2070        46          7
    26  25.4295   24.6822        16.3483        58         62
    51  17.3638   16.4709        10.4698        64        109
    76  19.4149   19.1655        14.9370        61        152
   101  23.4810   23.4805        18.2873        61        192
   126  19.2996   19.2989        11.1532        63        219
   151  23.3776   21.8168        16.7859        64        255
   176  22.3651   21.4982        16.8076        64        286
   201  25.4411   25.4411        20.2486        63        313
   226  24.4748   22.8468        20.4393        64        343
   251  16.3926   16.3922        13.8895        63        374
   276  22.4472   22.1974        17.4640        63        409
   300  25.4416   23.6878        15.4075        60        442
  candidates evaluated: 7208   best_ever 30.4864 (afca59f94cb88786)  wall 442s

BEST PROGRAM afca59f94cb88786 (len 43, iteration 2, modification swap@23,41)
  search seed 201002: fit 18.4307 succ 18/50 inter 8085 steps 43077 ws_cost 150 blocks 0 invoked 0 ws_bytes 0
    by stage (mean cost, success rate): {"A": [326.349, 0.9], "B": [366.858, 0.9], "C": [52.84, 0.0], "D": [52.84, 0.0], "E": [52.84, 0.0]}
  listing:
      0  INPUT          R1, num_ops
      1  CONST          R5, 1
      2  BLK_COPY       R3, R1
      3  CONST          R0, 0
      4  MOV            R2, R1
      5  LT             R3, R0, R2
      6  BRZ            R3, 11
      7  ACT            R1
      8  ACT            R0
      9  ADD            R0, R0, R5
     10  JMP            5
     11  CONST          R0, 0
     12  MUL            R2, R1, R1
     13  LT             R3, R0, R2
     14  BRZ            R3, 24
     15  ACT            R1
     16  BLK_REC_BEGIN  
     17  MOD            R3, R0, R1
     18  ACT            R3
     19  DIV            R4, R0, R1
     20  MOD            R3, R4, R1
     21  ACT            R3
     22  ADD            R0, R0, R5
     23  JMP            27
     24  CONST          R0, 0
     25  MUL            R2, R1, R1
     26  MUL            R2, R2, R1
     27  LT             R3, R0, R2
     28  BRZ            R3, 42
     29  ACT            R1
     30  MUL            R2, R1, R1
     31  MUL            R2, R2, R1
     32  MOD            R3, R0, R1
     33  ACT            R3
     34  DIV            R4, R0, R1
     35  MOD            R3, R4, R1
     36  ACT            R3
     37  DIV            R4, R4, R1
     38  MOD            R3, R4, R1
     39  ACT            R3
     40  ADD            R0, R0, R5
     41  JMP            13
     42  HALT           
  ancestry (2 steps, newest first): iteration/fitness/modification
    it    2  18.4307  len 43  swap@23,41
    it    1  16.2932  len 43  insert@2+insert@16+splice@30<-donor[25:27]:44430fa470b190c7
    it    0  18.4130  len 39  seed:ENUMERATE_VM

QUALIFICATION suite=qual seeds=[201, 202, 203] (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED; fit = campaign fitness)
  player                        fitA    fitF    fitR    fitS  sucA  sucF   interA   interF  reuse_gn    blk   invk
  PROCEDURE_REUSE_C1          46.133  20.741  21.462  21.462  45.7  20.3     3816    11350    7316.0    4.3   74.7
  ancestor95_it145_72ea6a4ef  21.083  21.083  21.083  21.083  20.7  20.7     9916     9916       0.0    0.0    0.0
  top2_14b79c43721b5009       20.747  20.747  20.747  20.747  20.3  20.3    10208    10208       0.0    0.0    0.0
  top3_2c878740b698bf20       20.747  20.747  20.747  20.747  20.3  20.3    10208    10208       0.0    0.0    0.0
  contemp_f28acc8d38ba8521    20.747  20.747  20.747  20.747  20.3  20.3    10208    10208       0.0    0.0    0.0
  ancestor189_it298_76682cb2  20.747  20.747  20.747  20.747  20.3  20.3    10208    10208       0.0    0.0    0.0
  ENUMERATE_C1                20.744  20.744  20.744  20.744  20.3  20.3    10902    10902       0.0    0.0    0.0
  TABLE_MEMO_C1               20.744  20.744  20.744  20.744  20.3  20.3    10902    10902     -15.7    0.0    0.0
  PROCEDURE_NOCAL_C1          20.742  20.742  20.742  20.742  20.3  20.3    11129    11126      -6.3    2.7    1.7
  bestever_afca59f94cb88786   20.417  20.417  20.417  20.417  20.0  20.0     9724     9724       0.0    0.0    0.0
  top1_f31ebd4d500ce6d6       19.747  19.747  19.747  19.747  19.3  19.3    10223    10223       0.0    0.0    0.0
  QUIT_C1                     19.744  19.744  19.744  19.744  19.3  19.3     9448     9448       0.0    0.0    0.0
  ancestor1_it0_0875253d162c  19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       0.0    0.0    0.0
  ENUMERATE_VM_C1             19.738  19.738  19.738  19.738  19.3  19.3    11178    11178       0.0    0.0    0.0
  contemp_a9ffe9e28e7b277f    18.064  18.064  18.064  18.064  17.7  17.7    11900    11900       0.0    0.0    0.0
  contemp_a5cd1491f4d9e394     9.931   9.931   9.931   9.931   9.7   9.7    27874    27874       0.0    0.0    0.0
  RANDOM_C1                    7.220   7.220   7.220   7.220   7.0   7.0    34042    34042       0.0    0.0    0.0

ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)
  player                                   A               B               C               D               E
  PROCEDURE_REUSE_C1          304.00/ 455.13   14.90/ 539.10   21.11/  47.94   33.21/  48.94   40.07/  50.52
  ancestor95_it145_72ea6a4ef  441.49/ 441.49  441.08/ 441.08   48.37/  48.37   50.11/  50.11   51.47/  51.47
  top2_14b79c43721b5009       446.45/ 446.45  467.31/ 467.31   50.05/  50.05   50.61/  50.61   52.42/  52.42
  top3_2c878740b698bf20       446.45/ 446.45  467.31/ 467.31   50.05/  50.05   50.61/  50.61   52.42/  52.42
  contemp_f28acc8d38ba8521    446.47/ 446.47  467.33/ 467.33   50.07/  50.07   50.63/  50.63   52.44/  52.44
  ancestor189_it298_76682cb2  446.47/ 446.47  467.33/ 467.33   50.07/  50.07   50.63/  50.63   52.44/  52.44
  ENUMERATE_C1                432.34/ 432.34  516.31/ 516.31   47.74/  47.74   48.73/  48.73   50.31/  50.31
  TABLE_MEMO_C1               432.46/ 432.37  516.62/ 516.34   48.13/  47.74   49.14/  48.74   50.72/  50.31
  PROCEDURE_NOCAL_C1          444.13/ 443.81  528.11/ 527.79   47.93/  47.89   48.85/  48.88   50.42/  50.46
  bestever_afca59f94cb88786   424.83/ 424.83  445.70/ 445.70   50.15/  50.15   51.19/  51.19   52.84/  52.84
  top1_f31ebd4d500ce6d6       456.79/ 456.79  458.35/ 458.35   50.00/  50.00   50.87/  50.87   52.43/  52.43
  QUIT_C1                     432.34/ 432.34  516.31/ 516.31   50.00/  50.00   50.00/  50.00   50.00/  50.00
  ancestor1_it0_0875253d162c  494.04/ 494.04  523.26/ 523.26   49.99/  49.99   50.96/  50.96   52.68/  52.68
  ENUMERATE_VM_C1             494.04/ 494.04  523.26/ 523.26   49.99/  49.99   50.96/  50.96   52.68/  52.68
  contemp_a9ffe9e28e7b277f    541.21/ 541.21  572.04/ 572.04   49.29/  49.29   52.19/  52.19   51.67/  51.67
  contemp_a5cd1491f4d9e394   1479.21/1479.21 1265.18/1265.18   52.21/  52.21   52.21/  52.21   50.87/  50.87
  RANDOM_C1                  1661.96/1661.96 1626.54/1626.54   50.44/  50.44   50.50/  50.50   48.40/  48.40

HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds
  player                             chain2         chain3         chain4  chain_repeat3         single single_new_arg
  PROCEDURE_REUSE_C1            34/36    18    26/30    23     6/12    34    11/12    21    30/30   301    30/30    14
  ancestor95_it145_72ea6a4ef     4/36    46     2/30    48     1/12    49     0/12    50    27/30   424    28/30   424
  top2_14b79c43721b5009          4/36    48     2/30    48     0/12    50     0/12    50    27/30   428    28/30   448
  top3_2c878740b698bf20          4/36    48     2/30    48     0/12    50     0/12    50    27/30   428    28/30   448
  contemp_f28acc8d38ba8521       4/36    48     2/30    48     0/12    50     0/12    50    27/30   428    28/30   448
  ancestor189_it298_76682cb2     4/36    48     2/30    48     0/12    50     0/12    50    27/30   428    28/30   448
  ENUMERATE_C1                   2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  TABLE_MEMO_C1                  2/36    47     1/30    48     0/12    50     0/12    50    29/30   431    29/30   514
  PROCEDURE_NOCAL_C1             2/36    47     1/30    48     0/12    50     0/12    50    29/30   442    29/30   526
  bestever_afca59f94cb88786      2/36    47     1/30    48     0/12    50     0/12    50    28/30   404    29/30   423
  top1_f31ebd4d500ce6d6          2/36    48     1/30    48     0/12    50     0/12    50    27/30   438    28/30   439
  QUIT_C1                        0/36     0     0/30     0     0/12     0     0/12     0    29/30   431    29/30   514
  ancestor1_it0_0875253d162c     2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  ENUMERATE_VM_C1                2/36    47     2/30    48     0/12    50     0/12    50    27/30   472    27/30   500
  contemp_a9ffe9e28e7b277f       4/36    46     1/30    49     0/12    50     1/12    47    24/30   509    23/30   538
  contemp_a5cd1491f4d9e394       0/36    50     0/30    50     0/12    50     1/12    47    11/30  1422    17/30  1216
  RANDOM_C1                      1/36    50     0/30    50     1/12    48     1/12    48    10/30  1646     8/30  1610

CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)
  player                      ACC_rem  ABL_all   ART_tr  FULL_tr     CODE  COMPUTE  STORAGE  nblk
  PROCEDURE_REUSE_C1            36.26    49.53    36.26    36.26    49.53    49.53    49.53   4.0
  ancestor95_it145_72ea6a4ef    50.72       --    50.72    50.72    50.72    50.72    50.72   0.0
  top2_14b79c43721b5009         51.42       --    51.42    51.42    51.42    51.42    51.42   0.0
  top3_2c878740b698bf20         51.42       --    51.42    51.42    51.42    51.42    51.42   0.0
  contemp_f28acc8d38ba8521      51.44       --    51.44    51.44    51.44    51.44    51.44   0.0
  ancestor189_it298_76682cb2    51.44       --    51.44    51.44    51.44    51.44    51.44   0.0
  ENUMERATE_C1                  49.43       --    49.43    49.43    49.43    49.43    49.43   0.0
  TABLE_MEMO_C1                 49.84       --    49.44    49.84    49.44    49.44    49.44   0.0
  PROCEDURE_NOCAL_C1            49.55    49.55    49.55    49.55    49.55    49.55    49.55   1.0
  bestever_afca59f94cb88786     51.92       --    51.92    51.92    51.92    51.92    51.92   0.0
  top1_f31ebd4d500ce6d6         51.56       --    51.56    51.56    51.56    51.56    51.56   0.0
  QUIT_C1                       50.00       --    50.00    50.00    50.00    50.00    50.00   0.0
  ancestor1_it0_0875253d162c    51.73       --    51.73    51.73    51.73    51.73    51.73   0.0
  ENUMERATE_VM_C1               51.73       --    51.73    51.73    51.73    51.73    51.73   0.0
  contemp_a9ffe9e28e7b277f      51.96       --    51.96    51.96    51.96    51.96    51.96   0.0
  contemp_a5cd1491f4d9e394      51.61       --    51.61    51.61    51.61    51.61    51.61   0.0
  RANDOM_C1                     49.57       --    49.57    49.57    49.57    49.57    49.57   0.0

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
  ancestor95_it145_72ea6a4ef32ab62a
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 20, 23] vs FRESH [19, 20, 23]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1542.8, 1459.7, 1477.4] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.12, 51.26, 48.77] vs CODE_ONLY [52.12, 51.26, 48.77]
    4_scramble_or_reset_damages            0/3  eff ACC [19.384, 20.417, 23.448] SCR [19.384, 20.417, 23.448] RESET [19.384, 20.417, 23.448]
    5_transfers_to_fresh_copy              0/3  FULL [52.12, 51.26, 48.77] vs ACC remainder [52.12, 51.26, 48.77]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.12, 51.26, 48.77]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.12, 51.26, 48.77] STORAGE_MATCHED [52.12, 51.26, 48.77] vs ACC remainder [52.12, 51.26, 48.77]
  top2_14b79c43721b5009
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 20, 22] vs FRESH [19, 20, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1542.4, 1510.1, 1525.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.42, 50.97, 50.86] vs CODE_ONLY [52.42, 50.97, 50.86]
    4_scramble_or_reset_damages            0/3  eff ACC [19.382, 20.411, 22.448] SCR [19.382, 20.411, 22.448] RESET [19.382, 20.411, 22.448]
    5_transfers_to_fresh_copy              0/3  FULL [52.42, 50.97, 50.86] vs ACC remainder [52.42, 50.97, 50.86]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.42, 50.97, 50.86]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.42, 50.97, 50.86] STORAGE_MATCHED [52.42, 50.97, 50.86] vs ACC remainder [52.42, 50.97, 50.86]
  top3_2c878740b698bf20
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 20, 22] vs FRESH [19, 20, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1542.4, 1510.1, 1525.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.42, 50.97, 50.86] vs CODE_ONLY [52.42, 50.97, 50.86]
    4_scramble_or_reset_damages            0/3  eff ACC [19.382, 20.411, 22.448] SCR [19.382, 20.411, 22.448] RESET [19.382, 20.411, 22.448]
    5_transfers_to_fresh_copy              0/3  FULL [52.42, 50.97, 50.86] vs ACC remainder [52.42, 50.97, 50.86]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.42, 50.97, 50.86]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.42, 50.97, 50.86] STORAGE_MATCHED [52.42, 50.97, 50.86] vs ACC remainder [52.42, 50.97, 50.86]
  contemp_f28acc8d38ba8521
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 20, 22] vs FRESH [19, 20, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1543.0, 1510.7, 1526.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.44, 50.99, 50.88] vs CODE_ONLY [52.44, 50.99, 50.88]
    4_scramble_or_reset_damages            0/3  eff ACC [19.382, 20.411, 22.448] SCR [19.382, 20.411, 22.448] RESET [19.382, 20.411, 22.448]
    5_transfers_to_fresh_copy              0/3  FULL [52.44, 50.99, 50.88] vs ACC remainder [52.44, 50.99, 50.88]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.44, 50.99, 50.88]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.44, 50.99, 50.88] STORAGE_MATCHED [52.44, 50.99, 50.88] vs ACC remainder [52.44, 50.99, 50.88]
  ancestor189_it298_76682cb25c66b78c
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [19, 20, 22] vs FRESH [19, 20, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1543.0, 1510.7, 1526.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.44, 50.99, 50.88] vs CODE_ONLY [52.44, 50.99, 50.88]
    4_scramble_or_reset_damages            0/3  eff ACC [19.382, 20.411, 22.448] SCR [19.382, 20.411, 22.448] RESET [19.382, 20.411, 22.448]
    5_transfers_to_fresh_copy              0/3  FULL [52.44, 50.99, 50.88] vs ACC remainder [52.44, 50.99, 50.88]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.44, 50.99, 50.88]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.44, 50.99, 50.88] STORAGE_MATCHED [52.44, 50.99, 50.88] vs ACC remainder [52.44, 50.99, 50.88]
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
  bestever_afca59f94cb88786
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 20, 22] vs FRESH [18, 20, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1585.2, 1534.6, 1489.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.84, 52.84, 50.09] vs CODE_ONLY [52.84, 52.84, 50.09]
    4_scramble_or_reset_damages            0/3  eff ACC [18.385, 20.419, 22.447] SCR [18.385, 20.419, 22.447] RESET [18.385, 20.419, 22.447]
    5_transfers_to_fresh_copy              0/3  FULL [52.84, 52.84, 50.09] vs ACC remainder [52.84, 52.84, 50.09]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.84, 52.84, 50.09]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.84, 52.84, 50.09] STORAGE_MATCHED [52.84, 52.84, 50.09] vs ACC remainder [52.84, 52.84, 50.09]
  top1_f31ebd4d500ce6d6
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [18, 18, 22] vs FRESH [18, 18, 22]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1572.9, 1522.9, 1488.5] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [52.43, 52.43, 49.82] vs CODE_ONLY [52.43, 52.43, 49.82]
    4_scramble_or_reset_damages            0/3  eff ACC [18.383, 18.413, 22.443] SCR [18.383, 18.413, 22.443] RESET [18.383, 18.413, 22.443]
    5_transfers_to_fresh_copy              0/3  FULL [52.43, 52.43, 49.82] vs ACC remainder [52.43, 52.43, 49.82]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [52.43, 52.43, 49.82]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [52.43, 52.43, 49.82] STORAGE_MATCHED [52.43, 52.43, 49.82] vs ACC remainder [52.43, 52.43, 49.82]
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
  contemp_a9ffe9e28e7b277f
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [14, 18, 21] vs FRESH [14, 18, 21]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1524.2, 1518.9, 1537.1] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [51.11, 53.35, 51.41] vs CODE_ONLY [51.11, 53.35, 51.41]
    4_scramble_or_reset_damages            0/3  eff ACC [14.343, 18.399, 21.449] SCR [14.343, 18.399, 21.449] RESET [14.343, 18.399, 21.449]
    5_transfers_to_fresh_copy              0/3  FULL [51.11, 53.35, 51.41] vs ACC remainder [51.11, 53.35, 51.41]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [51.11, 53.35, 51.41]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [51.11, 53.35, 51.41] STORAGE_MATCHED [51.11, 53.35, 51.41] vs ACC remainder [51.11, 53.35, 51.41]
  contemp_a5cd1491f4d9e394
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [11, 6, 12] vs FRESH [11, 6, 12]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1534.1, 1566.3, 1566.3] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [50.42, 52.21, 52.21] vs CODE_ONLY [50.42, 52.21, 52.21]
    4_scramble_or_reset_damages            0/3  eff ACC [11.302, 6.201, 12.289] SCR [11.302, 6.201, 12.289] RESET [11.302, 6.201, 12.289]
    5_transfers_to_fresh_copy              0/3  FULL [50.42, 52.21, 52.21] vs ACC remainder [50.42, 52.21, 52.21]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [50.42, 52.21, 52.21]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [50.42, 52.21, 52.21] STORAGE_MATCHED [50.42, 52.21, 52.21] vs ACC remainder [50.42, 52.21, 52.21]
  RANDOM_C1
    0_competence_kept_ACC_ge_FRESH         3/3  successes ACC [6, 6, 9] vs FRESH [6, 6, 9]
    1_cost_declines_via_accumulation       0/3  reuse_gain C-E per seed [0.0, 0.0, 0.0] vs 5% of FRESH cost [1491.8, 1515.0, 1485.7] (and 0 held)
    2_reproduces_on_heldout                0/3  same test, qualification suite; seeds passing = 0/3
    3_state_causal_FULL_vs_CODE_ONLY       0/3  remainder mean cost FULL [49.21, 50.5, 48.99] vs CODE_ONLY [49.21, 50.5, 48.99]
    4_scramble_or_reset_damages            0/3  eff ACC [6.205, 6.235, 9.221] SCR [6.205, 6.235, 9.221] RESET [6.205, 6.235, 9.221]
    5_transfers_to_fresh_copy              0/3  FULL [49.21, 50.5, 48.99] vs ACC remainder [49.21, 50.5, 48.99]
    6_executable_components_reused         0/3  invocations [0, 0, 0]; ABLATION_ALL cost [None, None, None] vs ACC remainder [49.21, 50.5, 48.99]
    7_not_compute_or_storage               0/3  COMPUTE_MATCHED [49.21, 50.5, 48.99] STORAGE_MATCHED [49.21, 50.5, 48.99] vs ACC remainder [49.21, 50.5, 48.99]

MACHINERY OF top1_f31ebd4d500ce6d6 (qualification seed 201, ACCUMULATED)
  workspace timeline (task: bytes cells streams records links | blocks bytes):
    task  0:     0    0    0    0    0 |   0     0
    task  9:     0    0    0    0    0 |   0     0
    task 19:     0    0    0    0    0 |   0     0
    task 31:     0    0    0    0    0 |   0     0
    task 41:     0    0    0    0    0 |   0     0
    task 49:     0    0    0    0    0 |   0     0
  artifact events: 0 (create 0, delete 0, patch/append 0); invocations by block: {}; edges: 0
  adaptation curve ACC:   3 2087 35 1028 3 3 25 1764 223 279 66 35 1028 1028 3 1529 1529 20 2087 16 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
  adaptation curve FRESH: 3 2087 35 1028 3 3 25 1764 223 279 66 35 1028 1028 3 1529 1529 20 2087 16 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52 52
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

