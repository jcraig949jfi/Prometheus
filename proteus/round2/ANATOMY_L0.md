# Round 2 L0 anatomy -- STRUCTURE of Archaeon's specimens (PROTEUS-37)

Input archaeon/campaign4/SPECIMENS_FOR_PROTEUS.json; counts {"delay_general": 11, "w0_solver": 15, "shelf": 23}; behavioural columns read: 0.
Permutation floor: 20000 relabellings, seed 20260921, 24 statistics per pair, UNCORRECTED.

## delay_general vs w0_solver

    statistic                          mean_delay mean_w0_so      diff  floor_p
    tick_budget                          267.636    82.133   185.503   0.0062 
    has_conditional_branch                 0.818     0.333     0.485   0.0213 
    reachable_share_arithmetic             0.047     0.106    -0.060   0.0701 
    genome_instructions                   17.636    13.000     4.636   0.0796 
    reachable_share_comparison             0.104     0.054     0.050   0.0916 
    reachable_count                       16.727    12.200     4.527   0.0980 
    reachable_share_halt_yield             0.062     0.033     0.029   0.1338 
    reachable_share_control                0.083     0.052     0.031   0.1402 
    reachable_distinct_opcodes            10.818     8.600     2.218   0.1472 
    n_regs                                 5.727     7.867    -2.139   0.1598 
    reachable_share_read_write             0.078     0.049     0.029   0.2992 
    reachable_share_logical                0.199     0.238    -0.039   0.3131 
    reachable_share_opaque_io              0.347     0.399    -0.052   0.3690 
    has_RND                                0.455     0.267     0.188   0.4144 
    persist_tape_or_all                    0.273     0.467    -0.194   0.4239 
    reachable_share_randomness             0.039     0.024     0.015   0.4721 
    registers_used_count                   5.545     6.400    -0.855   0.5375 
    tape_words                           174.545   147.200    27.345   0.5794 
    code_writable                          0.727     0.600     0.127   0.6857 
    has_tape_memory                        0.545     0.400     0.145   0.6917 
    reachable_share_indirection            0.041     0.043    -0.003   0.9016 
    reachable_fraction                     0.940     0.937     0.003   0.9522 
    has_INQ                                0.455     0.467    -0.012   1.0000 
    persist_regs_or_all                    1.000     1.000     0.000   1.0000 constant

## delay_general vs shelf

    statistic                          mean_delay mean_shelf      diff  floor_p
    n_regs                                 5.727    11.261    -5.534   0.0008 
    registers_used_count                   5.545    10.435    -4.889   0.0013 
    reachable_share_comparison             0.104     0.047     0.057   0.0103 
    code_writable                          0.727     0.304     0.423   0.0295 
    reachable_share_arithmetic             0.047     0.086    -0.040   0.0739 
    reachable_share_randomness             0.039     0.014     0.025   0.0845 
    genome_instructions                   17.636    23.435    -5.798   0.1204 
    reachable_share_halt_yield             0.062     0.098    -0.036   0.1431 
    persist_tape_or_all                    0.273     0.565    -0.292   0.1534 
    has_conditional_branch                 0.818     0.957    -0.138   0.2399 
    reachable_share_control                0.083     0.108    -0.024   0.2428 
    reachable_count                       16.727    19.174    -2.447   0.4173 
    has_RND                                0.455     0.261     0.194   0.4344 
    reachable_fraction                     0.940     0.881     0.058   0.4371 
    has_INQ                                0.455     0.304     0.150   0.4592 
    reachable_share_opaque_io              0.347     0.318     0.029   0.4825 
    reachable_share_read_write             0.078     0.064     0.014   0.4843 
    reachable_share_logical                0.199     0.219    -0.020   0.4869 
    reachable_distinct_opcodes            10.818    11.739    -0.921   0.5253 
    has_tape_memory                        0.545     0.435     0.111   0.7145 
    tape_words                           174.545   160.000    14.545   0.7830 
    reachable_share_indirection            0.041     0.045    -0.005   0.8228 
    tick_budget                          267.636   299.130   -31.494   0.8650 
    persist_regs_or_all                    1.000     1.000     0.000   1.0000 constant

## w0_solver vs shelf

    statistic                          mean_w0_so mean_shelf      diff  floor_p
    has_conditional_branch                 0.333     0.957    -0.623   0.0000 
    genome_instructions                   13.000    23.435   -10.435   0.0019 
    registers_used_count                   6.400    10.435    -4.035   0.0034 
    reachable_share_halt_yield             0.033     0.098    -0.065   0.0072 
    reachable_count                       12.200    19.174    -6.974   0.0101 
    reachable_share_control                0.052     0.108    -0.055   0.0101 
    reachable_distinct_opcodes             8.600    11.739    -3.139   0.0213 
    n_regs                                 7.867    11.261    -3.394   0.0251 
    tick_budget                           82.133   299.130  -216.997   0.0368 
    reachable_share_opaque_io              0.399     0.318     0.081   0.0566 
    code_writable                          0.600     0.304     0.296   0.0954 
    reachable_share_randomness             0.024     0.014     0.010   0.3624 
    reachable_fraction                     0.937     0.881     0.055   0.3960 
    reachable_share_arithmetic             0.106     0.086     0.020   0.4431 
    reachable_share_read_write             0.049     0.064    -0.015   0.4479 
    has_INQ                                0.467     0.304     0.162   0.4908 
    reachable_share_logical                0.238     0.219     0.019   0.5298 
    tape_words                           147.200   160.000   -12.800   0.7244 
    persist_tape_or_all                    0.467     0.565    -0.099   0.7408 
    reachable_share_comparison             0.054     0.047     0.006   0.7553 
    reachable_share_indirection            0.043     0.045    -0.002   0.9196 
    has_RND                                0.267     0.261     0.006   1.0000 
    has_tape_memory                        0.400     0.435    -0.035   1.0000 
    persist_regs_or_all                    1.000     1.000     0.000   1.0000 constant

## Reachable programs (address order), by stratum

### delay_general
     0  OUT OUT LT OR XOR NOP MOV LT LT XOR JNZ OUT OUT OR MUL IN
     1  IN MOV IN INQ ST OUT OR OUT
     2  OR SUB INQ RND SHL ADD NOP MUL NOP OUT XOR LD SHL IN XOR SHR LT OR SUB INQ RND JNZ LT JNZ SHL LT SHL
     3  IN MOV IN OR OUT NOP OUT ST MOV INQ JNZ LD OR EQ NOP
     4  IN IN EQ MOV OUT MOV IN YIELD OUT SHR JMP
     5  OUT MUL JNZ OUT OUT AND AND OR EQ LT JNZ MOV RND EQ AND ADD NOP LT IN IN JZ LT JNZ SHR XOR XOR ST
     6  IN INQ LDC OUT JZ EQ OUT IN NOT INQ IN XOR LD MOV EQ SHL LT YIELD OR JNZ SHL OUT JZ EQ
     7  OUT JNZ SUB RND IN MOV IN LDC XOR SHR IN HALT
     8  OUT OUT OUT NOT OUT OR JNZ XOR RND AND SUB NOT IN EQ SHR IN JNZ LT IN
     9  SUB IN OUT RND JNZ EQ RND IN SHL IN HALT
    10  OR IN LD OUT EQ SHL AND IN EQ MOV JZ INQ IN HALT

### w0_solver
     0  OUT SHR IN SHL RND ADD SUB XOR IN SUB SHR
     1  SHL NOP OUT MOV LDC LD IN IN EQ IN JZ AND SHL MOV
     2  OUT IN INQ INQ JNZ INQ NOT RND HALT AND SHL
     3  ADD IN OUT INQ NOT AND IN JNZ RND LDC MOV HALT
     4  ST AND OUT XOR IN JMP
     5  EQ EQ MOV MUL ST ADD OUT IN INQ AND SUB SHR OUT LT XOR OR INQ LD LDC LD JZ LD ADD AND OR
     6  OUT IN OUT JNZ ADD OUT ADD OUT
     7  OUT SHR IN
     8  OUT SHL IN
     9  SHR EQ OR NOP OUT AND IN IN IN NOT NOT LD OUT ADD XOR SHR EQ HALT
    10  IN INQ EQ LT MOV OUT SHL EQ OUT SHL ST SUB IN SHR EQ SUB IN INQ XOR
    11  INQ MUL EQ SHR IN IN EQ IN MUL OUT EQ NOT MOV LDC JMP
    12  OUT NOT NOP OUT SUB IN JMP
    13  INQ OUT XOR IN RND SUB IN IN XOR ADD
    14  ST OR OR EQ OUT IN NOT LDC INQ MUL EQ OUT SHR LDC MUL SUB ST MUL XOR ST INQ

### shelf
     0  OUT JNZ OR AND MOV NOP IN OUT
     1  EQ SHL OUT ADD JNZ IN AND INQ SHR INQ IN ADD IN JNZ
     2  OUT IN LD SHR IN JNZ ST IN HALT HALT
     3  MUL OUT AND JNZ XOR IN ADD OUT OUT LDC SHL IN JMP HALT NOT MOV JNZ NOP LT RND LT SUB SHL SHL EQ SUB OUT
     4  OR AND SHR EQ OUT IN MOV MUL JNZ LDC INQ SHL NOP JNZ LD MOV MUL SHR OUT OR OR NOT EQ OUT OR ADD LD EQ MUL LD JZ JNZ
     5  OUT MOV JNZ SHL IN JZ ADD JZ IN NOP EQ JZ MUL OUT XOR HALT OR LD
     6  EQ ST XOR SUB OUT JNZ IN ADD XOR SUB SHL JNZ AND LT SHL INQ
     7  MOV OUT OR SHL YIELD SHL OUT OR NOP IN IN IN SHL YIELD SHL OUT
     8  OUT EQ NOT JNZ IN IN MOV IN LT JZ MOV JMP
     9  OUT IN JZ JNZ IN LDC RND INQ NOP ADD AND JNZ XOR ST JNZ IN LD EQ NOP NOP SHL NOT YIELD SUB ST ST SHL SHR MOV SHR RND RND IN LD NOP LD IN LD JZ JNZ XOR INQ HALT
    10  IN OUT SUB SUB JZ NOT MOV AND MOV SUB LT IN IN SHL HALT
    11  NOP NOT LDC IN XOR YIELD NOP IN OUT OR JNZ OUT OR ADD IN IN
    12  NOP NOT LDC IN XOR YIELD NOP IN OUT OR JNZ OUT OR ADD IN IN
    13  MOV NOT LDC OR NOP OR EQ OUT OUT JNZ IN OUT EQ ADD IN IN
    14  NOP NOT LDC IN XOR YIELD NOP IN OUT OR JNZ OUT OR ADD IN IN
    15  OUT SHR IN JNZ ST IN NOP IN ST OUT SHR LD LDC LT SHR LT LDC NOP LD OUT LDC INQ JZ XOR JNZ LT AND ADD
    16  IN OUT SHL IN JNZ RND JZ SUB IN XOR
    17  OUT IN OUT JNZ IN IN LD IN MUL NOT JZ JMP OUT OUT LD INQ OUT OUT NOP MUL EQ RND IN
    18  NOP NOT LDC IN XOR YIELD NOP IN OUT OR JNZ OUT OR ADD IN IN
    19  SHR NOP NOP LD LDC LD ADD OUT JNZ XOR SUB OR ST SUB IN EQ NOP NOP OR SHR RND ADD NOT NOT MUL XOR IN EQ SHL NOT NOT IN
    20  NOP NOT LDC IN XOR YIELD NOP IN OUT OR JNZ OUT OR ADD IN IN
    21  JZ LD LDC IN RND SUB JNZ XOR IN LD OUT NOP OR JNZ IN LDC AND JMP OR XOR LT YIELD MUL OUT OUT
    22  ST INQ IN INQ ADD MUL SUB AND OR OUT JNZ IN SHL OR LDC IN

## Not established
- which structure CAUSES delay invariance (Archaeon lesions the ablation sets on the delay family)
- anything from Archaeon's held-out columns (not read)
- that any statistic below its floor is a finding: 24 statistics x 3 pairs were tested
