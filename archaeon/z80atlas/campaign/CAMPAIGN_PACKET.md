+==============================================================================+
| Z80 x ATLAS COMBINATORIAL CAMPAIGN -- PACKET (code-generated; no interpretation)|
| Archaeon (M2) build of the NESTOR directive; grammar 63ffdeca16db3333; started 2026-09-19T14:18:03Z|
| frozen 2026-09-22T13:55:56Z; runs 101003; errors 0; families 31522; retired 0|
+==============================================================================+

0. POSITIVE CONTROLS
----------------------------------------
  PASS     external_evolves                     z80
  PASS     external_evolves                     vmcopy
  PASS     endogenous_invades_when_seeded       vmcopy
  PASS     endogenous_invades_when_seeded       z80
  PASS     replicator_replicates                z80
  uncalibrated substrates: none

1. FLAG TOTALS (mechanical triggers; promotion = more compute, not a claim)
----------------------------------------
  spontaneous_replication    26
  moat_crossed               70315
  moat_advantage             3110
  compression                6914
  new_arch_events            100185
  coexistence                52043
  longevity                  0
  transport                  35893
  env_lineage                832
  ruler_gain                 7
  persistence_over_control   6162
  exploit                    0

2. AXIS MAP  (level: runs | spont moat moat_adv compr arch coex long transp env ruler persist exploit)
----------------------------------------
  world.topology
    graph                  11621 |   0 7481  70 632 11483 5409   0   0   0   0 105   0
    grid_vn                11673 |   0 7453  48 605 11534 5402   0   0   0   0 101   0
    niches                 54363 |  22 40209 2864 4340 54232 30383   0 35893 832   7 5723   0
    ring_soup              11637 |   0 7286  64 652 11292 5865   0   0   0   0 124   0
    well_mixed             11709 |   4 7886  64 685 11644 4984   0   0   0   0 109   0
  world.migration
    competence             10048 |   0 7321 582 713 10028 5473   0 3865 179   1 1102   0
    env_dependent          10414 |  10 7799 512 957 10377 5707   0 10004 181   1 1038   0
    high                   10453 |   6 7704 480 868 10421 5595   0 10328 137   1 1016   0
    low                    10128 |   6 7493 448 824 10109 5868   0 6138 132   2 893   0
    none                   50059 |   4 32818 610 2902 49370 23865   0   0  20   0 1165   0
    periodic                9901 |   0 7180 478 650 9880 5535   0 5558 183   2 948   0
  world.resources
    limited                50596 |  16 35257 1550 3508 50200 26090   0 18083 431   2 3058   0
    unlimited              50407 |  10 35058 1560 3406 49985 25953   0 17810 401   5 3104   0
  world.env_dynamics
    env_coevolve           14659 |   5 10395 565 1241 14621 8142   0 10122 832   5 1421   0
    env_mutate             23504 |   3 15235 416 1485 23283 11732   0 5219   0   1 926   0
    fixed                  23651 |   6 15234 415 1515 23397 11749   0 5255   0   1 1020   0
    local_shift            15241 |   9 11694 1006 1123 15203 8449   0 10005   0   0 1650   0
    nonstationary          23948 |   3 17757 708 1550 23681 11971   0 5292   0   0 1145   0
  world.reservoir
    False                  63947 |  20 43138 1265 4072 63215 31761   0 10684 241   1 2470   0
    True                   37056 |   6 27177 1845 2842 36970 20282   0 25209 591   6 3692   0
  representation.substrate
    vmcopy                 52229 |  20 37097 1683 5013 51881 29139   0 20238 494   5 3196   0
    z80                    48774 |   6 33218 1427 1901 48304 22904   0 15655 338   2 2966   0
  representation.genome
    32                     51400 |  22 35558 1453 4161 50894 28341   0 19361 502   4 2912   0
    64                     49603 |   4 34757 1657 2753 49291 23702   0 16532 330   3 3250   0
  representation.layout
    separated              49603 |   9 36270 1399 3230 49139 23194   0 16540 340   7 2991   0
    shared                 51400 |  17 34045 1711 3684 51046 28849   0 19353 492   0 3171   0
  reproduction
    CONSTRUCTIVE           10135 |   0 5670  10 151 10048 2077   0 2103 244   0  12   0
    ENDOGENOUS_COPY        15392 |  21 8684 442 1786 15313 3384   0 5650   4   1 321   0
    ENDOGENOUS_PARTIAL     11523 |   5 7193  88 3907 11462 3466   0 3724  28   0 117   0
    EXTERNAL               43131 |   0 37195 2531   0 43131 40316   0 20213 536   5 5659   0
    OVERWRITE              10783 |   0 6159  32 1016 10718 2027   0 2648  15   1  53   0
    PAIR_EXECUTION         10039 |   0 5414   7  54 9513 773   0 1555   5   0   0   0
  pressure
    competence_gated        4671 |   0 3140 106 126 4594 2446   0 2222  52   0 253   0
    competence_gated+exec_  1052 |   0 689  16  37 1029 530   0 222   5   0  45   0
    competence_gated+expli   116 |   0 107  28   0 116  60   0 104   0   0  47   0
    competence_gated+impli   952 |   0 642  31  31 935 492   0 198   9   0  42   0
    competence_gated+metab   972 |   0 549  22  28 966 364   0 164   0   0  40   0
    competence_gated+minim  1013 |   0 613  16  11 815 443   0 222   0   0  38   0
    competence_gated+novel  1036 |   0 692  10  35 1013 523   0 227   2   0  34   0
    competence_gated+qd      997 |   0 704   8  30 970 500   0 207   3   0   7   0
    competence_gated+recom   105 |   0  96  17   0 105 101   0  87   0   0  43   0
    competence_gated+resou   929 |   0 636   8  21 897 454   0 189   4   0  12   0
    competence_gated+resou  1046 |   0 684  15  45 1021 550   0 218   5   0  25   0
    competence_gated+tape_   997 |   0 697  22  30 970 513   0 256   3   0  33   0
    exec_time               5048 |   0 3632  81 531 5033 2851   0 2285  24   0 216   0
    exec_time+explicit_fit    81 |   0  79   3   0  81  21   0  72  11   0  21   0
    exec_time+implicit_sur   923 |   0 671   8 109 922 495   0 222   0   0  21   0
    exec_time+metabolic      965 |   0 587   5  71 963 383   0 156   0   0  24   0
    exec_time+minimal_crit  1049 |   0 711  19  14 1032 487   0 190   7   0  31   0
    exec_time+novelty       1127 |   0 814  29  83 1124 591   0 230   0   0  54   0
    exec_time+qd            1075 |   0 775  10 103 1071 584   0 263   8   0  21   0
    exec_time+recombinatio   133 |   0 130  48   0 133 133   0  99   0   0  73   0
    exec_time+resource_com  1071 |   0 750  13  96 1063 568   0 295   3   0  28   0
    exec_time+resource_gat   959 |   0 683  12  81 954 517   0 218   5   0  19   0
    exec_time+tape_cost     1048 |   0 719  13  84 1041 544   0 232   2   0  30   0
    explicit_fitness         967 |   0 882 191   0 967 264   0 825 178   1 453   0
    explicit_fitness+impli   129 |   0 119  22   0 129  42   0 110  23   0  62   0
    explicit_fitness+metab    97 |   0  86  20   0  97  34   0  75   9   0  61   0
    explicit_fitness+minim    93 |   0  82  18   0  93  23   0  89  24   0  52   0
    explicit_fitness+novel   149 |   0 142  38   0 149  50   0 132  31   0  77   0
    explicit_fitness+qd      124 |   0 113  30   0 124  27   0 109  28   0  67   0
    explicit_fitness+recom   842 |   0 768 181   0 842 426   0 716 151   0 399   0
    explicit_fitness+resou    99 |   0  93  11   0  99  30   0  80  24   0  43   0
    explicit_fitness+resou   105 |   0  96  25   0 105  17   0  94  25   0  48   0
    explicit_fitness+tape_   113 |   0 106  22   0 113  33   0 102  32   1  57   0
    implicit_survival       6438 |   6 4355 250 687 6434 3218   0 3218  22   0 322   0
    implicit_survival+meta   907 |   0 567  13  61 906 366   0 149   0   0  23   0
    implicit_survival+mini   924 |   0 630   6  14 905 425   0 177   2   0  26   0
    implicit_survival+nove  1066 |   3 766  15 112 1064 594   0 261   2   0  29   0
    implicit_survival+qd    1007 |   0 736  18  87 1003 538   0 201   0   0  31   0
    implicit_survival+reco   101 |   0  89  38   0 101 100   0  90   0   0  65   0
    implicit_survival+reso   985 |   0 674   7  57 981 487   0 192   2   0  19   0
    implicit_survival+reso   935 |   0 676  12  92 931 503   0 226   2   0  27   0
    implicit_survival+tape   925 |   0 647  11  84 923 489   0 210   3   0  23   0
    metabolic               4450 |   0 2662 104 283 4446 1814   0 1550   0   0 194   0
    metabolic+minimal_crit  1002 |   0 570  11   9 996 401   0 168   0   0  26   0
    metabolic+novelty       1073 |   0 699  26  66 1070 450   0 194   0   0  64   0
    metabolic+qd            1114 |   0 705  17  78 1114 452   0 212   0   0  37   0
    metabolic+recombinatio   103 |   0  96  39   0 103 102   0  91   0   0  70   0
    metabolic+resource_com  1121 |   0 621  36  48 1099 439   0 168   0   0  74   0
    metabolic+resource_gat  1056 |   0 572  28  38 1050 408   0 110   0   0  44   0
    metabolic+tape_cost     1008 |   0 621  24  53 1008 404   0 121   0   0  36   0
    minimal_criterion       4365 |   0 2839  75  45 4324 2051   0 1718  14   1 160   0
    minimal_criterion+nove   998 |   0 679  24  17 986 448   0 143   0   0  34   0
    minimal_criterion+qd    1059 |   0 703   9  10 1045 464   0 160   2   0  26   0
    minimal_criterion+reco    87 |   0  84  24   0  87  87   0  72   0   0  50   0
    minimal_criterion+reso  1050 |   0 713  22  10 1039 481   0 216   0   0  36   0
    minimal_criterion+reso   948 |   0 640   3   8 936 423   0 166   1   0  11   0
    minimal_criterion+tape  1003 |   0 664  13   9 993 467   0 181   0   0  25   0
    novelty                 5121 |   5 3730 144 519 5114 2941   0 2421  21   0 241   0
    novelty+qd               973 |   2 710  28 102 967 534   0 193   4   0  32   0
    novelty+recombination     48 |   0  45  18   0  48  48   0  37   0   0  20   0
    novelty+resource_compe  1065 |   0 743   9  98 1061 559   0 268   0   0  28   0
    novelty+resource_gated  1043 |   0 752  10 111 1038 562   0 216   0   0  29   0
    novelty+tape_cost       1037 |   3 760  30  93 1033 536   0 205   3   0  43   0
    qd                      4942 |   4 3582 106 550 4929 2800   0 2202  18   0 208   0
    qd+recombination          79 |   0  73  29   0  79  78   0  64   0   0  62   0
    qd+resource_competitio  1177 |   0 828  24 125 1172 623   0 332   2   0  44   0
    qd+resource_gated       1009 |   0 714   9 105 1001 536   0 235   0   0  29   0
    qd+tape_cost            1066 |   0 770  27  92 1059 577   0 261   0   0  52   0
    recombination            968 |   0 893 258   0 968 962   0 822   0   1 487   0
    recombination+resource    97 |   0  85  19   0  97  96   0  70   0   0  43   0
    recombination+resource    79 |   0  64  12   0  79  78   0  71   0   0  39   0
    recombination+tape_cos   116 |   0 101  16   0 116 115   0  88   0   0  72   0
    resource_competition    5008 |   2 3584 138 461 4994 2835   0 2226  17   0 225   0
    resource_competition+r  1048 |   0 773  17  97 1040 582   0 258   0   0  27   0
    resource_competition+t  1010 |   0 711  12  67 1008 513   0 197   4   0  28   0
    resource_gated          5291 |   0 3859 111 518 5275 3060   0 2495  24   3 231   0
    resource_gated+tape_co  1067 |   0 734  12  95 1060 545   0 218   1   0  32   0
    tape_cost               4951 |   1 3509 158 447 4937 2756   0 2110  20   0 262   0
  task
    ADD2                    9610 |   5 6002 361 641 9537 5501   0 3052  39   2 589   0
    COND_1edit             11055 |   0 8794 254 949 10946 5427   0 4347  62   0 622   0
    COND_multi             11113 |  11 7746 393 1031 11003 5386   0 4305  52   1 653   0
    CONST_atomic           10890 |   1 6959 452 645 10803 5309   0 4155  94   0 785   0
    CONST_incremental      10834 |   6 7050 423 624 10753 5220   0 4293 157   2 712   0
    ECHO_abr               10600 |   0 9093  69 747 10497 5041   0 3851 140   0 465   0
    ECHO_forced            10698 |   1 9167  91 713 10617 5065   0 3904 151   1 484   0
    INC1                    9623 |   0 7077 339 622 9554 5487   0 3165  62   1 688   0
    NEG                     9633 |   1 6688 375 566 9559 5472   0 3030  64   0 757   0
    none                    6947 |   1 1739 353 376 6916 4135   0 1791  11   0 407   0
  mutation
    local_byte             25081 |   3 17482 747 1648 24886 12827   0 8774 184   1 1448   0
    opcode_bias            25014 |   7 17577 717 1678 24826 12792   0 8679 220   0 1446   0
    operand_bias           25355 |  10 17493 777 1780 25117 13186   0 9134 221   1 1539   0
    structural             25553 |   6 17763 869 1808 25356 13238   0 9306 207   5 1729   0
  init
    random                 48818 |  26 21483 2178 1509 48471 19963   0 15334 291   3 3888   0
    seeded_replicator      52185 |   0 48832 932 5405 51714 32080   0 20559 541   4 2274   0

3. TOP FAMILIES (by best mechanical score)
----------------------------------------
  2ace470e5c47 score 17 runs 33 flags coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,spontaneous_replication,transport
      ENDOGENOUS_COPY z80 shared task=COND_multi press=tape_cost init=random topo=niches mig=env_dependent env=env_coevolve
  5b237a475b69 score 17 runs 29 flags coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,spontaneous_replication,transport
      ENDOGENOUS_COPY vmcopy separated task=ADD2 press=novelty+tape_cost init=random topo=niches mig=env_dependent env=nonstationary
  e8394eee206d score 17 runs 37 flags compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,spontaneous_replication
      ENDOGENOUS_COPY vmcopy shared task=CONST_incremental press=qd init=random topo=well_mixed mig=none env=env_mutate
  19a0e0a5300a score 14 runs 23 flags coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
      ENDOGENOUS_PARTIAL vmcopy separated task=ADD2 press=resource_competition init=seeded_replicator topo=niches mig=env_dependent env=env_coevolve
  4aa428bd90bd score 14 runs 33 flags coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
      ENDOGENOUS_COPY vmcopy separated task=ADD2 press=implicit_survival+novelty init=seeded_replicator topo=niches mig=low env=fixed
  dd2e76a1189b score 14 runs 31 flags coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
      ENDOGENOUS_COPY vmcopy shared task=CONST_atomic press=implicit_survival init=seeded_replicator topo=niches mig=low env=local_shift
  5bb46451d5fb score 14 runs 37 flags coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
      ENDOGENOUS_COPY z80 shared task=CONST_incremental press=novelty init=seeded_replicator topo=niches mig=high env=fixed
  ac675613ecd5 score 14 runs 24 flags coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
      ENDOGENOUS_COPY vmcopy shared task=NEG press=novelty+qd init=seeded_replicator topo=niches mig=high env=local_shift
  070c3a9ab655 score 14 runs 37 flags coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
      ENDOGENOUS_COPY z80 shared task=CONST_incremental press=implicit_survival init=seeded_replicator topo=niches mig=high env=local_shift
  636158e75708 score 14 runs 31 flags coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
      ENDOGENOUS_COPY vmcopy shared task=none press=implicit_survival init=seeded_replicator topo=niches mig=env_dependent env=local_shift
  fd8719c6af75 score 14 runs 22 flags coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
      ENDOGENOUS_PARTIAL vmcopy separated task=NEG press=qd init=seeded_replicator topo=niches mig=env_dependent env=local_shift
  d130e2d3e25f score 14 runs 34 flags coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
      ENDOGENOUS_PARTIAL vmcopy shared task=CONST_incremental press=novelty init=seeded_replicator topo=niches mig=env_dependent env=env_coevolve
  f85407d4d325 score 14 runs 21 flags coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
      ENDOGENOUS_COPY vmcopy shared task=NEG press=implicit_survival init=seeded_replicator topo=niches mig=periodic env=env_coevolve
  fd435eace669 score 14 runs 22 flags coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
      ENDOGENOUS_COPY vmcopy separated task=ADD2 press=implicit_survival init=seeded_replicator topo=niches mig=competence env=local_shift
  bc2e3e5602ea score 14 runs 27 flags coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
      ENDOGENOUS_PARTIAL vmcopy shared task=COND_multi press=resource_competition+resource_gated init=seeded_replicator topo=niches mig=low env=env_mutate
  1804582d6f19 score 14 runs 26 flags coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
      ENDOGENOUS_COPY vmcopy shared task=CONST_atomic press=exec_time+novelty init=seeded_replicator topo=niches mig=env_dependent env=fixed
  32b5c3dd4c45 score 14 runs 27 flags coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
      ENDOGENOUS_COPY vmcopy shared task=CONST_atomic press=resource_competition init=seeded_replicator topo=niches mig=competence env=env_coevolve
  4189c2c18fc2 score 14 runs 17 flags coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
      ENDOGENOUS_COPY vmcopy separated task=ADD2 press=implicit_survival init=seeded_replicator topo=niches mig=low env=env_coevolve
  e4148c8c2968 score 14 runs 21 flags coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
      ENDOGENOUS_COPY vmcopy shared task=NEG press=implicit_survival init=seeded_replicator topo=niches mig=env_dependent env=local_shift
  3ae856c8eb40 score 14 runs 20 flags coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
      ENDOGENOUS_COPY vmcopy shared task=INC1 press=novelty init=seeded_replicator topo=niches mig=env_dependent env=env_mutate
  1f1cb3176483 score 14 runs 29 flags coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
      ENDOGENOUS_COPY vmcopy shared task=COND_multi press=resource_competition init=seeded_replicator topo=niches mig=low env=fixed
  f03bf63b3a6a score 14 runs 21 flags coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
      ENDOGENOUS_COPY vmcopy shared task=none press=tape_cost init=seeded_replicator topo=niches mig=low env=nonstationary
  e0c8e95860f8 score 14 runs 30 flags coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
      ENDOGENOUS_COPY vmcopy shared task=COND_multi press=qd+resource_gated init=seeded_replicator topo=niches mig=low env=fixed
  00d75b431ee8 score 14 runs 26 flags coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
      ENDOGENOUS_COPY vmcopy shared task=INC1 press=resource_gated init=seeded_replicator topo=niches mig=high env=env_coevolve
  cff1bc285b45 score 14 runs 23 flags coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
      ENDOGENOUS_PARTIAL vmcopy shared task=COND_multi press=tape_cost init=seeded_replicator topo=niches mig=high env=env_mutate
  0964a1a156e1 score 14 runs 25 flags coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
      ENDOGENOUS_COPY vmcopy separated task=COND_1edit press=resource_competition init=seeded_replicator topo=niches mig=env_dependent env=env_mutate
  e50017b04a3a score 14 runs 22 flags coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
      ENDOGENOUS_COPY vmcopy shared task=NEG press=exec_time+tape_cost init=seeded_replicator topo=niches mig=periodic env=env_coevolve
  d66d67b02b42 score 14 runs 27 flags coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
      OVERWRITE vmcopy separated task=ECHO_forced press=qd init=seeded_replicator topo=niches mig=periodic env=env_mutate
  c933207af712 score 14 runs 21 flags coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
      ENDOGENOUS_COPY vmcopy separated task=ADD2 press=exec_time+novelty init=seeded_replicator topo=niches mig=low env=env_coevolve
  708f54fd28d2 score 14 runs 23 flags coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
      ENDOGENOUS_COPY vmcopy shared task=none press=implicit_survival init=seeded_replicator topo=niches mig=periodic env=env_coevolve

4. VERIFICATION (late stage: fresh seeds, matched controls, transplants: same / physics_swap / world_swap / environment_swap)
----------------------------------------
  19a0e0a5300a
    fresh_seed@s100                              pop 0.98 endo 347701 best 1.00 cross True  arch  62 compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    fresh_seed@s101                              pop 0.98 endo 331192 best 1.00 cross True  arch  60 coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    fresh_seed@s102                              pop 0.97 endo 354492 best 1.00 cross True  arch  59 moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    matched_control:reproduction@s100            pop 0.98 endo      0 best 1.00 cross True  arch  61 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    transplant:environment_swap@s100             pop 0.97 endo 340880 best 1.00 cross True  arch  57 coexistence,moat_crossed,new_arch_events,spontaneous_replication,transport
    transplant:physics_swap@s100                 pop 0.97 endo      0 best 0.67 cross False arch  63 coexistence,new_arch_events,persistence_over_control,transport
    transplant:same@s100                         pop 0.98 endo 349894 best 0.67 cross False arch  63 new_arch_events,persistence_over_control,spontaneous_replication,transport
  4aa428bd90bd
    fresh_seed@s100                              pop 0.95 endo 356648 best 1.00 cross True  arch  55 coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    fresh_seed@s101                              pop 0.96 endo 316361 best 1.00 cross True  arch  52 coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    fresh_seed@s102                              pop 0.97 endo 330797 best 1.00 cross True  arch  52 coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    matched_control:reproduction@s100            pop 0.99 endo      0 best 1.00 cross True  arch  60 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    transplant:environment_swap@s100             pop 0.99 endo 345615 best 1.00 cross True  arch  48 coexistence,moat_crossed,new_arch_events,spontaneous_replication,transport
    transplant:physics_swap@s100                 pop 0.98 endo      0 best 1.00 cross True  arch  61 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    transplant:same@s100                         pop 0.99 endo 354773 best 0.67 cross False arch  47 coexistence,new_arch_events,persistence_over_control,spontaneous_replication,transport
    transplant:world_swap@s100                   pop 0.99 endo 367693 best 0.67 cross False arch  41 new_arch_events,persistence_over_control,spontaneous_replication
  dd2e76a1189b
    fresh_seed@s100                              pop 0.94 endo 196380 best 1.00 cross True  arch  52 coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    fresh_seed@s101                              pop 0.96 endo 191426 best 1.00 cross True  arch  52 coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    fresh_seed@s102                              pop 1.00 endo 193548 best 1.00 cross True  arch  51 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    matched_control:accessibility@s100           pop 0.94 endo 198723 best 1.00 cross True  arch  52 coexistence,moat_crossed,new_arch_events,transport
    matched_control:reproduction@s100            pop 0.94 endo      0 best 1.00 cross True  arch  55 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    transplant:environment_swap@s100             pop 0.96 endo 190396 best 0.33 cross False arch  41 coexistence,new_arch_events,spontaneous_replication,transport
    transplant:physics_swap@s100                 pop 0.98 endo      0 best 1.00 cross True  arch  55 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    transplant:same@s100                         pop 0.98 endo 187172 best 0.33 cross False arch  48 coexistence,compression,new_arch_events,persistence_over_control,spontaneous_replication,transport
  2ace470e5c47
    fresh_seed@s100                              pop 0.97 endo 188429 best 1.00 cross True  arch  37 coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    fresh_seed@s101                              pop 0.98 endo 187720 best 1.00 cross True  arch  39 coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    fresh_seed@s102                              pop 0.98 endo 182901 best 1.00 cross True  arch  42 moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    matched_control:accessibility@s100           pop 0.96 endo 191951 best 1.00 cross True  arch  37 coexistence,compression,moat_crossed,new_arch_events,transport
    matched_control:reproduction@s100            pop 0.98 endo      0 best 1.00 cross True  arch  50 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    transplant:environment_swap@s100             pop 0.99 endo 190166 best 1.00 cross True  arch  32 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,spontaneous_replication,transport
    transplant:physics_swap@s100                 pop 0.96 endo      0 best 1.00 cross True  arch  57 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
  5bb46451d5fb
    fresh_seed@s100                              pop 1.00 endo 188973 best 1.00 cross True  arch  46 moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    fresh_seed@s101                              pop 0.98 endo 188773 best 1.00 cross True  arch  39 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    fresh_seed@s102                              pop 0.95 endo 188061 best 1.00 cross True  arch  38 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    matched_control:accessibility@s100           pop 0.97 endo 192052 best 1.00 cross True  arch  41 coexistence,moat_crossed,new_arch_events,transport
    matched_control:reproduction@s100            pop 1.00 endo      0 best 1.00 cross True  arch  55 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    transplant:environment_swap@s100             pop 0.98 endo 187675 best 1.00 cross True  arch  36 coexistence,moat_crossed,new_arch_events,spontaneous_replication,transport
    transplant:physics_swap@s100                 pop 0.98 endo      0 best 0.98 cross False arch  56 coexistence,new_arch_events,persistence_over_control,transport
    transplant:same@s100                         pop 0.98 endo 184453 best 0.93 cross False arch  32 coexistence,new_arch_events,persistence_over_control,spontaneous_replication,transport
    transplant:world_swap@s100                   pop 0.98 endo 186603 best 0.99 cross False arch  34 new_arch_events,persistence_over_control,spontaneous_replication
  ac675613ecd5
    fresh_seed@s100                              pop 0.98 endo 191808 best 1.00 cross True  arch  48 coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    fresh_seed@s101                              pop 0.98 endo 194765 best 1.00 cross True  arch  42 compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    fresh_seed@s102                              pop 0.95 endo 190287 best 1.00 cross True  arch  49 compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    matched_control:reproduction@s100            pop 0.97 endo      0 best 1.00 cross True  arch  48 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    transplant:environment_swap@s100             pop 0.96 endo 189639 best 0.67 cross False arch  40 new_arch_events,spontaneous_replication,transport
    transplant:physics_swap@s100                 pop 0.98 endo      0 best 1.00 cross True  arch  54 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    transplant:same@s100                         pop 0.96 endo 190128 best 0.33 cross False arch  36 coexistence,new_arch_events,persistence_over_control,spontaneous_replication,transport
  070c3a9ab655
    fresh_seed@s100                              pop 0.97 endo 188870 best 1.00 cross True  arch  36 coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    fresh_seed@s101                              pop 0.98 endo 188815 best 1.00 cross True  arch  42 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    fresh_seed@s102                              pop 0.96 endo 192562 best 1.00 cross True  arch  44 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    matched_control:accessibility@s100           pop 0.99 endo 190646 best 1.00 cross True  arch  40 moat_crossed,new_arch_events,transport
    matched_control:reproduction@s100            pop 0.98 endo      0 best 1.00 cross True  arch  56 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    transplant:environment_swap@s100             pop 0.91 endo 189648 best 0.33 cross False arch  31 coexistence,new_arch_events,persistence_over_control,spontaneous_replication,transport
    transplant:physics_swap@s100                 pop 1.00 endo      0 best 1.00 cross True  arch  55 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    transplant:same@s100                         pop 0.98 endo 187831 best 0.91 cross False arch  29 coexistence,new_arch_events,persistence_over_control,spontaneous_replication,transport
  636158e75708
    fresh_seed@s100                              pop 0.98 endo 233251 best 0.33 cross False arch  52 coexistence,new_arch_events,persistence_over_control,transport
    fresh_seed@s101                              pop 0.98 endo 223341 best 0.33 cross False arch  45 compression,new_arch_events,persistence_over_control,transport
    fresh_seed@s102                              pop 0.96 endo 231449 best 1.00 cross True  arch  42 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    matched_control:reproduction@s100            pop 0.98 endo      0 best 1.00 cross True  arch  57 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    transplant:environment_swap@s100             pop 0.98 endo 190806 best 1.00 cross True  arch  51 coexistence,moat_crossed,new_arch_events,spontaneous_replication,transport
    transplant:physics_swap@s100                 pop 0.98 endo      0 best 1.00 cross True  arch  58 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    transplant:same@s100                         pop 0.98 endo 223673 best 0.33 cross False arch  44 coexistence,compression,new_arch_events,persistence_over_control,spontaneous_replication,transport
  5b237a475b69
    fresh_seed@s100                              pop 0.96 endo 382438 best 1.00 cross True  arch  47 coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    fresh_seed@s101                              pop 0.97 endo 370989 best 1.00 cross True  arch  49 coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    fresh_seed@s102                              pop 0.96 endo 399100 best 1.00 cross True  arch  48 coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    matched_control:reproduction@s100            pop 0.98 endo      0 best 1.00 cross True  arch  54 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    transplant:environment_swap@s100             pop 0.98 endo 406291 best 1.00 cross True  arch  52 moat_crossed,new_arch_events,spontaneous_replication,transport
    transplant:physics_swap@s100                 pop 0.95 endo      0 best 1.00 cross True  arch  48 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    transplant:same@s100                         pop 0.99 endo 381361 best 1.00 cross True  arch  44 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,spontaneous_replication,transport
    transplant:world_swap@s100                   pop 0.98 endo 389992 best 1.00 cross True  arch  50 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,spontaneous_replication
  fd8719c6af75
    fresh_seed@s100                              pop 0.94 endo 346597 best 1.00 cross True  arch  58 compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    fresh_seed@s101                              pop 0.98 endo 365688 best 1.00 cross True  arch  61 compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    fresh_seed@s102                              pop 0.94 endo 338052 best 1.00 cross True  arch  57 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    matched_control:reproduction@s100            pop 1.00 endo      0 best 1.00 cross True  arch  60 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    transplant:environment_swap@s100             pop 0.98 endo 347369 best 1.00 cross True  arch  61 moat_crossed,new_arch_events,spontaneous_replication,transport
    transplant:physics_swap@s100                 pop 0.98 endo      0 best 1.00 cross True  arch  60 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    transplant:same@s100                         pop 0.97 endo 332050 best 1.00 cross True  arch  59 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
  d130e2d3e25f
    fresh_seed@s100                              pop 0.98 endo 187023 best 1.00 cross True  arch  55 coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    fresh_seed@s101                              pop 0.97 endo 195364 best 1.00 cross True  arch  55 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    fresh_seed@s102                              pop 0.93 endo 184830 best 1.00 cross True  arch  56 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    matched_control:accessibility@s100           pop 0.98 endo 185750 best 1.00 cross True  arch  58 coexistence,moat_crossed,new_arch_events,transport
    matched_control:reproduction@s100            pop 0.98 endo      0 best 1.00 cross True  arch  58 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    transplant:environment_swap@s100             pop 0.98 endo 185046 best 0.98 cross False arch  56 coexistence,compression,new_arch_events,spontaneous_replication,transport
    transplant:physics_swap@s100                 pop 0.98 endo      0 best 0.99 cross False arch  58 coexistence,new_arch_events,persistence_over_control,transport
    transplant:same@s100                         pop 0.97 endo 189724 best 0.99 cross False arch  57 coexistence,compression,new_arch_events,persistence_over_control,spontaneous_replication,transport
  e8394eee206d
    fresh_seed@s100                              pop 0.99 endo 196775 best 1.00 cross True  arch  48 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    fresh_seed@s101                              pop 0.99 endo 192205 best 1.00 cross True  arch  52 coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    fresh_seed@s102                              pop 0.98 endo 188662 best 1.00 cross True  arch  48 coexistence,compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    matched_control:accessibility@s100           pop 0.98 endo 188492 best 1.00 cross True  arch  53 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    matched_control:reproduction@s100            pop 1.00 endo      0 best 1.00 cross True  arch  61 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    transplant:environment_swap@s100             pop 0.99 endo 188836 best 0.67 cross False arch  44 coexistence,new_arch_events,spontaneous_replication,transport
    transplant:physics_swap@s100                 pop 0.98 endo      0 best 1.00 cross True  arch  57 coexistence,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,transport
    transplant:same@s100                         pop 0.99 endo 189989 best 0.94 cross False arch  37 coexistence,compression,new_arch_events,persistence_over_control,spontaneous_replication,transport
    transplant:world_swap@s100                   pop 0.98 endo 191325 best 1.00 cross True  arch  48 compression,moat_advantage,moat_crossed,new_arch_events,persistence_over_control,spontaneous_replication

5. SPECIAL RESULTS
----------------------------------------
  spontaneous replication runs: 26  (67cef4faf5e7-t_s100_veri, 7252d77c58b8-t_s100_veri, 36f2d57cd4f2-t_s100_veri, 997f12c1740f-t_s100_veri, ee082f2db085-t_s100_veri, 11793ae99dd8-t_s100_veri, 8ac55dbf1309-t_s100_veri, 466dab00b7b6-t_s100_veri)
  exploit runs (specimens frozen): 0  ()
  moat_advantage families: 30
  blocked factor levels: {"representation.substrate": {"nestor_tape": "BLOCKED_MISSING_CAPABILITY: Nestor tape organisms not importable in this worktree", "nestor_tree": "BLOCKED_MISSING_CAPABILITY: Nestor tree organisms not importable in this worktree"}}

6. POINTERS
----------------------------------------
  runs         archaeon/z80atlas/campaign/runs/<family>/<run_id>/{SPEC,RECEIPT,TELEMETRY.json.gz,SNAPSHOTS.json.gz,FORENSICS,EXPLOITS}
  atlas_index  archaeon/z80atlas/campaign/ATLAS_INDEX.jsonl
  runs_log     archaeon/z80atlas/campaign/RUNS.jsonl
  grammar      archaeon/z80atlas/campaign/GRAMMAR_FROZEN.json
  log          archaeon/z80atlas/campaign/scheduler.log

END. Scientific promotion is post-campaign adjudication. 'Not worth continuing' remains a first-class answer.
