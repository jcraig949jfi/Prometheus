+=====================================================================+
|  DAMAGE GEOMETRY MAP V2 -- representation B beside the total one     |
|  Archaeon[m2-49ee5a4d]   Campaign 5   built by geometry_map_v2.py    |
+=====================================================================+

Attempts of record: C5-03 a02, C5-04 a01, C5-05 a01, C5-06 a02, C5-07 a01, C5-08 a01.
V1 (Campaign 4, total interpreter) is unchanged at archaeon/campaign4/DAMAGE_GEOMETRY_MAP.md.

1. SINGLE-EDIT BINS (share of applied children; 57 parents x 12 operators x 8 draws)
   grammar   interp      D2     D3     D4     D5     D6     D7     DT     DF
   v0.4      OLD        0.451  0.087  0.014  0.439  0.008  0.000  0.000  0.000
   v0.4      B_FAIL     0.293  0.055  0.008  0.311  0.005  0.000  0.327  0.000
   v0.4      B_FIZZLE   0.293  0.055  0.008  0.311  0.005  0.000  0.000  0.327
   B         OLD        0.459  0.087  0.013  0.435  0.007  0.000  0.000  0.000
   B         B_FAIL     0.438  0.079  0.011  0.410  0.006  0.000  0.057  0.000
   B         B_FIZZLE   0.438  0.079  0.011  0.410  0.006  0.000  0.000  0.057
   crossing share: v0.4 0.386, B 0.055.  DF sub-bins v0.4 {'D2': 682, 'D3': 155, 'D4': 27, 'D5': 718, 'D6': 12, 'D7': 0}; B {'D2': 128, 'D3': 35, 'D4': 9, 'D5': 103, 'D6': 1, 'D7': 0}
   C4-01 replicated 5586/5586 (digest and label).

2. THE BOUNDARY (per grammar): executed-crossing (T1) 0.8363 / 0.8593; D5 of non-crossing children under FAIL vs OLD 0.441 vs 0.442 / 0.428 vs 0.429
   D6 (exaptation) v0.4 OLD/FAIL/FIZZLE {'OLD': 0.008, 'B_FAIL': 0.0055, 'B_FIZZLE': 0.0055}; B {'OLD': 0.0072, 'B_FAIL': 0.0062, 'B_FIZZLE': 0.0064}; D7 = 0 everywhere.

3. MATCHED RECOVERY (C5-06; executed-crossing children of non-degenerate parents, n=1449)
   v04   {'BOTH_DIE': 418, 'BOTH_LIVE': 508, 'INSULATION_LOSS': 123, 'RECOVERY': 219}
   B     {'BOTH_DIE': 49, 'BOTH_LIVE': 83, 'INSULATION_LOSS': 34, 'RECOVERY': 15}
   fault kinds {'INSULATION_LOSS/opcode': 15, 'INSULATION_LOSS/register': 142, 'RECOVERY/opcode': 209, 'RECOVERY/register': 25}; replicated RECOVERY 229, INSULATION_LOSS 154; disposition REAL_LOCAL_RECOVERY

4. COST OF INSULATION (C5-07): K1 median ops ratio 1.0 (> 1.10x: 0.0218); K2 second-edit neutral children 0.5317 vs parents 0.5087 (diff 0.023); K3 lost elsewhere 0.0437; INSULATION_CHEAP

5. ROBUSTNESS MECHANISM (C5-08): R_old full 0.435 -> ablated 0.409 (dead share 0.110); GAP 0.021 / 0.021; tests {'M1': False, 'M1_bins': 1, 'M2': True, 'M3': True, 'M4': True}; MIXED
   by length bin (R_old full/ablated): 1-8 0.171/0.175; 9-16 0.456/0.418; 17-32 0.572/0.574; 33+ 0.714/0.571

6. GENERATOR x REPRESENTATION (C5-04, viable share): injected2 x B_FAIL 0.017; injected2 x B_FIZZLE 0.118; injected2 x OLD 0.170; raw x B_FAIL 0.000; raw x B_FIZZLE 0.000; raw x OLD 0.170; valid x B_FAIL 0.150; valid x B_FIZZLE 0.152; valid x OLD 0.152; predictions {'P1': True, 'P2': True, 'P3': True, 'P4': True}

7. QUALIFICATION (C5-03 a02): REPRESENTATION_QUALIFIED; fixtures {'F1': True, 'F2': True, 'F3': True, 'F4': True, 'F5': True, 'F6': True, 'F7': True, 'controls': True}; count-TVD {'raw_vs_injected2': 0.42, 'raw_vs_valid': 1.0, 'valid_vs_injected2': 0.83}; site-TVD {'raw_vs_injected2': 0.785, 'raw_vs_valid': 0.99, 'valid_vs_injected2': 0.83}; grammar-B crossing by operator {'config_perturbation': 0.0625, 'operand_perturbation': 0.5198}

8. PER-OPERATOR BINS (counts; grammar x interpreter)
   config_perturbation
      B x B_FAIL       n  442 crossing   21  {'D2': 171, 'D3': 14, 'D5': 235, 'DT': 22}
      B x B_FIZZLE     n  442 crossing   21  {'D2': 171, 'D3': 14, 'D5': 235, 'DF': 22}
      B x OLD          n  442 crossing   21  {'D2': 178, 'D3': 17, 'D4': 1, 'D5': 242, 'D6': 4}
      v04 x B_FAIL     n  442 crossing   39  {'D2': 158, 'D3': 12, 'D4': 1, 'D5': 233, 'DT': 38}
      v04 x B_FIZZLE   n  442 crossing   39  {'D2': 158, 'D3': 12, 'D4': 1, 'D5': 233, 'DF': 38}
      v04 x OLD        n  442 crossing   39  {'D2': 165, 'D3': 15, 'D4': 1, 'D5': 260, 'D6': 1}
   deletion
      B x B_FAIL       n  440 crossing    0  {'D2': 222, 'D3': 66, 'D4': 8, 'D5': 133, 'D6': 9, 'DT': 2}
      B x B_FIZZLE     n  440 crossing    0  {'D2': 222, 'D3': 66, 'D4': 8, 'D5': 133, 'D6': 9, 'DF': 2}
      B x OLD          n  440 crossing    0  {'D2': 223, 'D3': 67, 'D4': 8, 'D5': 133, 'D6': 9}
      v04 x B_FAIL     n  440 crossing    0  {'D2': 232, 'D3': 73, 'D4': 9, 'D5': 116, 'D6': 8, 'DT': 2}
      v04 x B_FIZZLE   n  440 crossing    0  {'D2': 232, 'D3': 73, 'D4': 9, 'D5': 116, 'D6': 8, 'DF': 2}
      v04 x OLD        n  440 crossing    0  {'D2': 232, 'D3': 74, 'D4': 9, 'D5': 117, 'D6': 8}
   duplication
      B x B_FAIL       n  368 crossing    0  {'D2': 197, 'D3': 28, 'D4': 5, 'D5': 133, 'DT': 5}
      B x B_FIZZLE     n  368 crossing    0  {'D2': 197, 'D3': 28, 'D4': 5, 'D5': 133, 'DF': 5}
      B x OLD          n  368 crossing    0  {'D2': 197, 'D3': 31, 'D4': 6, 'D5': 134}
      v04 x B_FAIL     n  368 crossing    0  {'D2': 199, 'D3': 25, 'D4': 5, 'D5': 135, 'DT': 4}
      v04 x B_FIZZLE   n  368 crossing    0  {'D2': 199, 'D3': 25, 'D4': 5, 'D5': 135, 'DF': 4}
      v04 x OLD        n  368 crossing    0  {'D2': 200, 'D3': 27, 'D4': 6, 'D5': 135}
   insertion
      B x B_FAIL       n  368 crossing    0  {'D2': 197, 'D3': 20, 'D4': 2, 'D5': 142, 'D6': 1, 'DT': 6}
      B x B_FIZZLE     n  368 crossing    0  {'D2': 197, 'D3': 20, 'D4': 2, 'D5': 142, 'D6': 1, 'DF': 6}
      B x OLD          n  368 crossing    0  {'D2': 198, 'D3': 23, 'D4': 3, 'D5': 143, 'D6': 1}
      v04 x B_FAIL     n  368 crossing  368  {'D2': 27, 'D3': 3, 'D4': 1, 'D5': 36, 'DT': 301}
      v04 x B_FIZZLE   n  368 crossing  368  {'D2': 27, 'D3': 3, 'D4': 1, 'D5': 36, 'DF': 301}
      v04 x OLD        n  368 crossing  368  {'D2': 185, 'D3': 38, 'D4': 5, 'D5': 139, 'D6': 1}
   movement
      B x B_FAIL       n  418 crossing    0  {'D2': 174, 'D3': 42, 'D4': 8, 'D5': 185, 'D6': 4, 'DT': 5}
      B x B_FIZZLE     n  418 crossing    0  {'D2': 174, 'D3': 42, 'D4': 8, 'D5': 185, 'D6': 4, 'DF': 5}
      B x OLD          n  418 crossing    0  {'D2': 175, 'D3': 45, 'D4': 9, 'D5': 185, 'D6': 4}
      v04 x B_FAIL     n  412 crossing    0  {'D2': 163, 'D3': 40, 'D4': 9, 'D5': 190, 'D6': 3, 'DT': 7}
      v04 x B_FIZZLE   n  412 crossing    0  {'D2': 163, 'D3': 40, 'D4': 9, 'D5': 190, 'D6': 3, 'DF': 7}
      v04 x OLD        n  412 crossing    0  {'D2': 163, 'D3': 44, 'D4': 10, 'D5': 191, 'D6': 4}
   operand_perturbation
      B x B_FAIL       n  456 crossing  249  {'D2': 61, 'D3': 3, 'D4': 3, 'D5': 176, 'DT': 213}
      B x B_FIZZLE     n  456 crossing  249  {'D2': 61, 'D3': 3, 'D4': 3, 'D5': 176, 'DF': 213}
      B x OLD          n  456 crossing  249  {'D2': 149, 'D3': 20, 'D4': 5, 'D5': 281, 'D6': 1}
      v04 x B_FAIL     n  456 crossing  249  {'D2': 70, 'D3': 5, 'D4': 2, 'D5': 173, 'D6': 1, 'DT': 205}
      v04 x B_FIZZLE   n  456 crossing  249  {'D2': 70, 'D3': 5, 'D4': 2, 'D5': 173, 'D6': 1, 'DF': 205}
      v04 x OLD        n  456 crossing  249  {'D2': 140, 'D3': 19, 'D4': 7, 'D5': 288, 'D6': 2}
   randomization
      B x B_FAIL       n  456 crossing    0  {'D2': 268, 'D3': 52, 'D4': 5, 'D5': 119, 'D6': 6, 'DT': 6}
      B x B_FIZZLE     n  456 crossing    0  {'D2': 268, 'D3': 52, 'D4': 5, 'D5': 119, 'D6': 6, 'DF': 6}
      B x OLD          n  456 crossing    0  {'D2': 269, 'D3': 54, 'D4': 7, 'D5': 120, 'D6': 6}
      v04 x B_FAIL     n  456 crossing  456  {'D2': 23, 'D5': 40, 'DT': 393}
      v04 x B_FIZZLE   n  456 crossing  456  {'D2': 23, 'D5': 40, 'DF': 393}
      v04 x OLD        n  456 crossing  456  {'D2': 283, 'D3': 48, 'D4': 6, 'D5': 113, 'D6': 6}
   reference_redirection
      B x B_FAIL       n  456 crossing    0  {'D2': 127, 'D3': 15, 'D4': 6, 'D5': 305, 'D6': 2, 'DT': 1}
      B x B_FIZZLE     n  456 crossing    0  {'D2': 127, 'D3': 15, 'D4': 6, 'D5': 305, 'D6': 2, 'DF': 1}
      B x OLD          n  456 crossing    0  {'D2': 127, 'D3': 15, 'D4': 6, 'D5': 306, 'D6': 2}
      v04 x B_FAIL     n  456 crossing  314  {'D2': 55, 'D3': 1, 'D5': 135, 'D6': 1, 'DT': 264}
      v04 x B_FIZZLE   n  456 crossing  314  {'D2': 55, 'D3': 1, 'D5': 135, 'D6': 1, 'DF': 264}
      v04 x OLD        n  456 crossing  314  {'D2': 128, 'D3': 8, 'D4': 3, 'D5': 316, 'D6': 1}
   region_swap
      B x B_FAIL       n  440 crossing    0  {'D2': 250, 'D3': 57, 'D4': 3, 'D5': 123, 'D6': 3, 'DT': 4}
      B x B_FIZZLE     n  440 crossing    0  {'D2': 250, 'D3': 57, 'D4': 3, 'D5': 123, 'D6': 3, 'DF': 4}
      B x OLD          n  440 crossing    0  {'D2': 250, 'D3': 59, 'D4': 4, 'D5': 124, 'D6': 3}
      v04 x B_FAIL     n  440 crossing    0  {'D2': 215, 'D3': 65, 'D4': 10, 'D5': 141, 'D6': 6, 'DT': 3}
      v04 x B_FIZZLE   n  440 crossing    0  {'D2': 215, 'D3': 65, 'D4': 10, 'D5': 141, 'D6': 6, 'DF': 3}
      v04 x OLD        n  440 crossing    0  {'D2': 216, 'D3': 66, 'D4': 11, 'D5': 141, 'D6': 6}
   replacement
      B x B_FAIL       n  456 crossing    0  {'D2': 210, 'D3': 48, 'D4': 6, 'D5': 184, 'D6': 1, 'DT': 7}
      B x B_FIZZLE     n  456 crossing    0  {'D2': 210, 'D3': 47, 'D4': 6, 'D5': 184, 'D6': 2, 'DF': 7}
      B x OLD          n  456 crossing    0  {'D2': 213, 'D3': 49, 'D4': 7, 'D5': 186, 'D6': 1}
      v04 x B_FAIL     n  456 crossing  456  {'D2': 24, 'D5': 57, 'DT': 375}
      v04 x B_FIZZLE   n  456 crossing  456  {'D2': 24, 'D5': 57, 'DF': 375}
      v04 x OLD        n  456 crossing  456  {'D2': 226, 'D3': 41, 'D4': 8, 'D5': 179, 'D6': 2}
   splice
      B x B_FAIL       n  418 crossing    0  {'D2': 233, 'D3': 42, 'D4': 5, 'D5': 129, 'D6': 4, 'DT': 5}
      B x B_FIZZLE     n  418 crossing    0  {'D2': 233, 'D3': 42, 'D4': 5, 'D5': 129, 'D6': 4, 'DF': 5}
      B x OLD          n  418 crossing    0  {'D2': 235, 'D3': 43, 'D4': 6, 'D5': 130, 'D6': 4}
      v04 x B_FAIL     n  424 crossing    0  {'D2': 238, 'D3': 45, 'D4': 4, 'D5': 127, 'D6': 8, 'DT': 2}
      v04 x B_FIZZLE   n  424 crossing    0  {'D2': 238, 'D3': 45, 'D4': 4, 'D5': 127, 'D6': 8, 'DF': 2}
      v04 x OLD        n  424 crossing    0  {'D2': 239, 'D3': 46, 'D4': 4, 'D5': 127, 'D6': 8}
   unreachable_removal
      B x B_FAIL       n  160 crossing    0  {'D2': 24, 'D5': 136}
      B x B_FIZZLE     n  160 crossing    0  {'D2': 24, 'D5': 136}
      B x OLD          n  160 crossing    0  {'D2': 24, 'D5': 136}
      v04 x B_FAIL     n  160 crossing    0  {'D2': 24, 'D5': 136}
      v04 x B_FIZZLE   n  160 crossing    0  {'D2': 24, 'D5': 136}
      v04 x OLD        n  160 crossing    0  {'D2': 24, 'D5': 136}
