# Beta-04 E1 foundry v2 pilot: qualification report

generator config_sha `c199f0ae8845f60fc16303840c25f68df640572bb41ba382dd2c96308da66ddf`; qualification config_sha `22d2c38767a22e3a4ceb34c5f8424be8363cafe18d027c911016afcf97dee089`.

## 1. Controls (run first)

| planted family | expectation | solved by |
|---|---|---|
| PLANTED-LOOKUP | lookup solves (test inputs == dev inputs; not contract-conformant) | lookup, history2 |
| PLANTED-RANDOM | nothing solves | none |
| PLANTED-REACTIVE | reactive (elementwise table) solves | reactive |
| PLANTED-REGRESSION-W | regression (W) solves | regression |
| PLANTED-REGRESSION-E | regression (E) solves | regression |
| PLANTED-NONLINEAR-FOLD | regression does NOT solve (multiplicative accumulator) | none |

| world | R0 solved by a trivial rung | R1 solved by regression (must be 0) | witnesses verified |
|---|---|---|---|
| Wc025415a | 6/6 | 0/10 | 52/52 |
| W2bdef02f | 6/6 | 0/10 | 52/52 |
| W09efdf93 | 6/6 | 0/10 | 52/52 |
| Wd1490fbb | 6/6 | 0/10 | 52/52 |
| Wb49b6a5f | 6/6 | 0/10 | 52/52 |
| W483b8c31 | 6/6 | 0/10 | 52/52 |
| W0321d83c | 6/6 | 0/10 | 52/52 |
| W3a22e2ee | 6/6 | 0/10 | 52/52 |
| W8f6a223e | 6/6 | 0/8 | 50/50 |
| W480ffd54 | 6/6 | 0/10 | 52/52 |
| W38fc86d7 | 6/6 | 0/10 | 52/52 |
| W6eb945cc | 6/6 | 0/10 | 52/52 |

## 2. Admission by world and rung

| world | rung | generated | gen OK | admitted | class histogram |
|---|---|---|---|---|---|
| Wc025415a | R0 | 6 | 6 | (control) | TRIVIAL_BY_REACTIVE 3; TRIVIAL_BY_REGRESSION 3 |
| Wc025415a | R1 | 10 | 10 | (control) | QUALIFIED 7; TRIVIAL_BY_REACTIVE 1; TRIVIAL_BY_SMALL_SEARCH 2 |
| Wc025415a | R2 | 10 | 10 | 1 | KNOWN_POSITIVE_FAIL:DEV_UNDERDETERMINED 1; KNOWN_POSITIVE_FAIL:HORIZON 4; NEAR_TRIVIAL 2; QUALIFIED 1; TRIVIAL_BY_BASE_1E6 1; TRIVIAL_BY_REGRESSION 1 |
| Wc025415a | R3 | 14 | 12 | 0 | CHAIN_C_FAIL:f0 4; CHAIN_C_FAIL:f0+s0 1; CHAIN_C_FAIL:f0+s1 1; CHAIN_C_FAIL:s0 4; CHAIN_C_FAIL:s0+s1 2; DUPLICATE 2 |
| Wc025415a | R4 | 6 | 6 | 2 | CHAIN_C_FAIL:s1 4; QUALIFIED 2 |
| Wc025415a | R5 | 11 | 8 | 0 | CHAIN_C_FAIL:f0 6; CHAIN_C_FAIL:f0+s0 1; CHAIN_C_FAIL:s0+s1 1; DEGENERATE 1; DUPLICATE 2 |
| W2bdef02f | R0 | 6 | 6 | (control) | TRIVIAL_BY_LIBRARY 1; TRIVIAL_BY_REACTIVE 5 |
| W2bdef02f | R1 | 16 | 10 | (control) | DUPLICATE 6; NEAR_TRIVIAL 2; QUALIFIED 6; TRIVIAL_BY_REACTIVE 1; TRIVIAL_BY_SMALL_SEARCH 1 |
| W2bdef02f | R2 | 12 | 10 | 5 | DEGENERATE 1; DUPLICATE 1; KNOWN_POSITIVE_FAIL:DEV_UNDERDETERMINED 1; KNOWN_POSITIVE_FAIL:HORIZON 2; NEAR_TRIVIAL 1; QUALIFIED 5; TRIVIAL_BY_REACTIVE 1 |
| W2bdef02f | R3 | 12 | 12 | 1 | CHAIN_C_FAIL:f1 5; CHAIN_C_FAIL:s1 3; CHAIN_D_FAIL:HORIZON 2; QUALIFIED 1; SYNTHETIC_DEPTH 1 |
| W2bdef02f | R4 | 6 | 6 | 2 | CHAIN_C_FAIL:f1+s1 2; CHAIN_C_FAIL:s1 2; QUALIFIED 2 |
| W2bdef02f | R5 | 11 | 8 | 0 | CHAIN_C_FAIL:f1 5; CHAIN_C_FAIL:s1 2; DEGENERATE 2; FAIL_PRONE 1; SYNTHETIC_DEPTH 1 |
| W09efdf93 | R0 | 6 | 6 | (control) | TRIVIAL_BY_REACTIVE 3; TRIVIAL_BY_REGRESSION 3 |
| W09efdf93 | R1 | 12 | 10 | (control) | DUPLICATE 2; QUALIFIED 8; TRIVIAL_BY_SMALL_SEARCH 2 |
| W09efdf93 | R2 | 14 | 10 | 3 | DEGENERATE 3; FAIL_PRONE 1; KNOWN_POSITIVE_FAIL:HORIZON 3; NEAR_TRIVIAL 1; QUALIFIED 3; SYNTHETIC_DEPTH 1; TRIVIAL_BY_REACTIVE 1; TRIVIAL_BY_REGRESSION 1 |
| W09efdf93 | R3 | 14 | 12 | 0 | CHAIN_C_FAIL:f1 4; CHAIN_C_FAIL:f1+s1 2; CHAIN_C_FAIL:p0 1; CHAIN_C_FAIL:p0+s1 2; CHAIN_D_FAIL:NOT_FOUND 2; FAIL_PRONE 2; NEAR_TRIVIAL 1 |
| W09efdf93 | R4 | 10 | 6 | 0 | CHAIN_C_FAIL:f1+p0 4; CHAIN_C_FAIL:p0 2; DUPLICATE 1; FAIL_PRONE 3 |
| W09efdf93 | R5 | 9 | 8 | 0 | CHAIN_C_FAIL:f1 2; CHAIN_C_FAIL:f1+s1 3; CHAIN_C_FAIL:p0 2; CHAIN_D_FAIL:HORIZON 1; DUPLICATE 1 |
| Wd1490fbb | R0 | 6 | 6 | (control) | TRIVIAL_BY_LIBRARY 2; TRIVIAL_BY_REACTIVE 4 |
| Wd1490fbb | R1 | 13 | 10 | (control) | DEGENERATE 3; NEAR_TRIVIAL 2; QUALIFIED 8 |
| Wd1490fbb | R2 | 11 | 10 | 3 | DUPLICATE 1; KNOWN_POSITIVE_FAIL:HORIZON 3; NEAR_TRIVIAL 2; QUALIFIED 3; TRIVIAL_BY_LIBRARY 1; TRIVIAL_BY_REACTIVE 1 |
| Wd1490fbb | R3 | 13 | 12 | 0 | CHAIN_C_FAIL:f0+f1 1; CHAIN_C_FAIL:f0+s1 2; CHAIN_C_FAIL:f1 2; CHAIN_C_FAIL:f1+s1 2; CHAIN_C_FAIL:s1 2; CHAIN_D_FAIL:HORIZON 2; DEGENERATE 1; NEAR_TRIVIAL 1 |
| Wd1490fbb | R4 | 8 | 6 | 0 | CHAIN_C_FAIL:f0 6; FAIL_PRONE 2 |
| Wd1490fbb | R5 | 10 | 8 | 0 | CHAIN_C_FAIL:f0+s1 2; CHAIN_C_FAIL:f1 3; CHAIN_C_FAIL:f1+s1 3; DUPLICATE 2 |
| Wb49b6a5f | R0 | 6 | 6 | (control) | TRIVIAL_BY_LIBRARY 2; TRIVIAL_BY_REACTIVE 3; TRIVIAL_BY_REGRESSION 1 |
| Wb49b6a5f | R1 | 11 | 10 | (control) | DUPLICATE 1; QUALIFIED 9; TRIVIAL_BY_REACTIVE 1 |
| Wb49b6a5f | R2 | 14 | 10 | 2 | DEGENERATE 1; DUPLICATE 1; FAIL_PRONE 2; KNOWN_POSITIVE_FAIL:HORIZON 4; QUALIFIED 2; SYNTHETIC_DEPTH 1; TRIVIAL_BY_LIBRARY 1; TRIVIAL_BY_REGRESSION 2 |
| Wb49b6a5f | R3 | 16 | 12 | 0 | CHAIN_C_FAIL:f0 4; CHAIN_C_FAIL:s0 3; CHAIN_D_FAIL:HORIZON 2; DUPLICATE 1; FAIL_PRONE 3; TRIVIAL_BY_REGRESSION 3 |
| Wb49b6a5f | R4 | 9 | 6 | 2 | CHAIN_C_FAIL:f0 3; FAIL_PRONE 3; QUALIFIED 2; SYNTHETIC_DEPTH 1 |
| Wb49b6a5f | R5 | 9 | 8 | 0 | CHAIN_C_FAIL:f0 4; CHAIN_C_FAIL:s0 2; CHAIN_D_FAIL:HORIZON 2; DEGENERATE 1 |
| W483b8c31 | R0 | 6 | 6 | (control) | TRIVIAL_BY_LIBRARY 1; TRIVIAL_BY_REACTIVE 3; TRIVIAL_BY_REGRESSION 2 |
| W483b8c31 | R1 | 14 | 10 | (control) | DUPLICATE 4; QUALIFIED 10 |
| W483b8c31 | R2 | 11 | 10 | 3 | DEGENERATE 1; KNOWN_POSITIVE_FAIL:HORIZON 4; MOTIF_CAP 1; QUALIFIED 3; TRIVIAL_BY_REGRESSION 2 |
| W483b8c31 | R3 | 21 | 12 | 2 | CHAIN_C_FAIL:s0 5; CHAIN_C_FAIL:s1 3; DEGENERATE 1; DUPLICATE 2; FAIL_PRONE 6; QUALIFIED 2; TRIVIAL_BY_BASE_1E6 1; TRIVIAL_BY_LOOKUP 1 |
| W483b8c31 | R4 | 7 | 6 | 0 | CHAIN_C_FAIL:s0 2; CHAIN_C_FAIL:s1 2; FAIL_PRONE 1; SYNTHETIC_DEPTH 2 |
| W483b8c31 | R5 | 11 | 8 | 0 | CHAIN_C_FAIL:s0 2; CHAIN_C_FAIL:s1 2; CHAIN_D_FAIL:HORIZON 3; DEGENERATE 3; TRIVIAL_BY_BASE_1E6 1 |
| W0321d83c | R0 | 6 | 6 | (control) | TRIVIAL_BY_LIBRARY 1; TRIVIAL_BY_REACTIVE 3; TRIVIAL_BY_REGRESSION 1; TRIVIAL_BY_SMALL_SEARCH 1 |
| W0321d83c | R1 | 14 | 10 | (control) | DUPLICATE 4; QUALIFIED 7; TRIVIAL_BY_LIBRARY 1; TRIVIAL_BY_SMALL_SEARCH 2 |
| W0321d83c | R2 | 11 | 10 | 2 | DEGENERATE 1; KNOWN_POSITIVE_FAIL:HORIZON 5; NEAR_TRIVIAL 1; QUALIFIED 2; TRIVIAL_BY_REGRESSION 2 |
| W0321d83c | R3 | 13 | 12 | 1 | CHAIN_C_FAIL:f1 1; CHAIN_C_FAIL:f1+s0 2; CHAIN_C_FAIL:f1+s1 1; CHAIN_C_FAIL:s0 2; CHAIN_C_FAIL:s1 4; DEGENERATE 1; NEAR_TRIVIAL 1; QUALIFIED 1 |
| W0321d83c | R4 | 9 | 6 | 0 | CHAIN_C_FAIL:f1 1; CHAIN_C_FAIL:s0 3; FAIL_PRONE 3; TRIVIAL_BY_REGRESSION 2 |
| W0321d83c | R5 | 10 | 8 | 0 | CHAIN_C_FAIL:f1+s0 2; CHAIN_C_FAIL:s0 1; CHAIN_C_FAIL:s1 2; DEGENERATE 1; DUPLICATE 1; NEAR_TRIVIAL 2; TRIVIAL_BY_REGRESSION 1 |
| W3a22e2ee | R0 | 6 | 6 | (control) | TRIVIAL_BY_REACTIVE 4; TRIVIAL_BY_REGRESSION 2 |
| W3a22e2ee | R1 | 18 | 10 | (control) | DEGENERATE 3; DUPLICATE 5; NEAR_TRIVIAL 1; QUALIFIED 6; TRIVIAL_BY_REACTIVE 1; TRIVIAL_BY_SMALL_SEARCH 2 |
| W3a22e2ee | R2 | 17 | 10 | 4 | DEGENERATE 4; DUPLICATE 2; FAIL_PRONE 1; KNOWN_POSITIVE_FAIL:HORIZON 4; MOTIF_CAP 1; NEAR_TRIVIAL 1; QUALIFIED 4 |
| W3a22e2ee | R3 | 14 | 12 | 0 | CHAIN_C_FAIL:f1+s0 1; CHAIN_C_FAIL:f1+s1 2; CHAIN_C_FAIL:s0 4; CHAIN_C_FAIL:s1 4; DEGENERATE 1; DUPLICATE 1; TRIVIAL_BY_REGRESSION 1 |
| W3a22e2ee | R4 | 11 | 6 | 0 | CHAIN_C_FAIL:f1 4; DUPLICATE 1; FAIL_PRONE 4; SYNTHETIC_DEPTH 1; TRIVIAL_BY_REACTIVE 1 |
| W3a22e2ee | R5 | 11 | 8 | 0 | CHAIN_C_FAIL:f1+s1 2; CHAIN_C_FAIL:s0 2; CHAIN_C_FAIL:s1 3; DEGENERATE 2; DUPLICATE 1; TRIVIAL_BY_REACTIVE 1 |
| W8f6a223e | R0 | 6 | 6 | (control) | TRIVIAL_BY_LIBRARY 1; TRIVIAL_BY_REACTIVE 5 |
| W8f6a223e | R1 | 10 | 8 | (control) | DUPLICATE 2; QUALIFIED 7; TRIVIAL_BY_REACTIVE 1 |
| W8f6a223e | R2 | 10 | 10 | 2 | KNOWN_POSITIVE_FAIL:HORIZON 3; MOTIF_CAP 2; QUALIFIED 2; SYNTHETIC_DEPTH 1; TRIVIAL_BY_BASE_1E6 1; TRIVIAL_BY_REGRESSION 1 |
| W8f6a223e | R3 | 15 | 12 | 0 | CHAIN_C_FAIL:f1 2; CHAIN_C_FAIL:f1+s1 3; CHAIN_C_FAIL:s1 6; DUPLICATE 3; NEAR_TRIVIAL 1 |
| W8f6a223e | R4 | 8 | 6 | 0 | CHAIN_C_FAIL:f1 3; CHAIN_D_FAIL:HORIZON 3; DEGENERATE 1; DUPLICATE 1 |
| W8f6a223e | R5 | 12 | 8 | 0 | CHAIN_C_FAIL:f1 2; CHAIN_C_FAIL:f1+s1 4; CHAIN_C_FAIL:s1 2; DEGENERATE 2; DUPLICATE 2 |
| W480ffd54 | R0 | 6 | 6 | (control) | TRIVIAL_BY_REACTIVE 5; TRIVIAL_BY_REGRESSION 1 |
| W480ffd54 | R1 | 15 | 10 | (control) | DEGENERATE 2; DUPLICATE 3; QUALIFIED 7; TRIVIAL_BY_REACTIVE 1; TRIVIAL_BY_SMALL_SEARCH 2 |
| W480ffd54 | R2 | 14 | 10 | 5 | DEGENERATE 4; KNOWN_POSITIVE_FAIL:HORIZON 3; QUALIFIED 5; SYNTHETIC_DEPTH 1; TRIVIAL_BY_REGRESSION 1 |
| W480ffd54 | R3 | 15 | 12 | 2 | CHAIN_C_FAIL:s0 6; CHAIN_C_FAIL:s0+s1 2; DEGENERATE 1; DUPLICATE 2; QUALIFIED 2; TRIVIAL_BY_BASE_1E6 1; TRIVIAL_BY_REGRESSION 1 |
| W480ffd54 | R4 | 7 | 6 | 1 | CHAIN_C_FAIL:s1 4; DUPLICATE 1; QUALIFIED 1; TRIVIAL_BY_REGRESSION 1 |
| W480ffd54 | R5 | 9 | 8 | 0 | CHAIN_C_FAIL:s0 4; CHAIN_C_FAIL:s0+s1 2; DUPLICATE 1; SYNTHETIC_DEPTH 1; TRIVIAL_BY_REGRESSION 1 |
| W38fc86d7 | R0 | 8 | 6 | (control) | DUPLICATE 2; TRIVIAL_BY_REACTIVE 5; TRIVIAL_BY_REGRESSION 1 |
| W38fc86d7 | R1 | 16 | 10 | (control) | DUPLICATE 6; QUALIFIED 9; TRIVIAL_BY_REACTIVE 1 |
| W38fc86d7 | R2 | 14 | 10 | 4 | DEGENERATE 2; DUPLICATE 2; KNOWN_POSITIVE_FAIL:HORIZON 5; QUALIFIED 4; TRIVIAL_BY_BASE_1E6 1 |
| W38fc86d7 | R3 | 14 | 12 | 0 | CHAIN_C_FAIL:f1 2; CHAIN_C_FAIL:s0 4; CHAIN_C_FAIL:s0+s1 1; CHAIN_C_FAIL:s1 4; DUPLICATE 2; TRIVIAL_BY_REGRESSION 1 |
| W38fc86d7 | R4 | 7 | 6 | 0 | CHAIN_C_FAIL:f1 2; CHAIN_C_FAIL:f1+s0 2; CHAIN_C_FAIL:f1+s1 2; DEGENERATE 1 |
| W38fc86d7 | R5 | 12 | 8 | 0 | CHAIN_C_FAIL:f1 1; CHAIN_C_FAIL:s0 4; CHAIN_C_FAIL:s1 1; DEGENERATE 1; DUPLICATE 3; TRIVIAL_BY_REACTIVE 1; TRIVIAL_BY_REGRESSION 1 |
| W6eb945cc | R0 | 6 | 6 | (control) | TRIVIAL_BY_LIBRARY 3; TRIVIAL_BY_REACTIVE 2; TRIVIAL_BY_SMALL_SEARCH 1 |
| W6eb945cc | R1 | 13 | 10 | (control) | DUPLICATE 3; QUALIFIED 9; TRIVIAL_BY_REACTIVE 1 |
| W6eb945cc | R2 | 12 | 10 | 4 | DEGENERATE 2; KNOWN_POSITIVE_FAIL:DEV_UNDERDETERMINED 1; KNOWN_POSITIVE_FAIL:HORIZON 2; QUALIFIED 4; TRIVIAL_BY_BASE_1E6 1; TRIVIAL_BY_REACTIVE 1; TRIVIAL_BY_REGRESSION 1 |
| W6eb945cc | R3 | 17 | 12 | 2 | CHAIN_C_FAIL:f1 5; CHAIN_C_FAIL:f1+s1 3; CHAIN_D_FAIL:HORIZON 1; CHAIN_D_FAIL:TRIBUNAL 1; DEGENERATE 1; DUPLICATE 4; QUALIFIED 2 |
| W6eb945cc | R4 | 6 | 6 | 0 | CHAIN_C_FAIL:s1 4; TRIVIAL_BY_LIBRARY 1; TRIVIAL_BY_REACTIVE 1 |
| W6eb945cc | R5 | 8 | 8 | 0 | CHAIN_C_FAIL:f1 5; CHAIN_C_FAIL:f1+s1 1; CHAIN_D_FAIL:HORIZON 2 |

| world | mechanisms (unfilled) | chain (c) by mechanism | E1 gate |
|---|---|---|---|
| Wc025415a | f0, f1, p0, s0, s1 (-) | f0: HORIZON/HORIZON; f1: ACQUIRED/ACQUIRED; p0: ACQUIRED/ACQUIRED; s0: HORIZON/HORIZON; s1: HORIZON/HORIZON | **FAIL** |
| W2bdef02f | f0, f1, p0, s0, s1 (-) | f0: ACQUIRED/ACQUIRED; f1: UNDERDETERMINED/UNDERDETERMINED; p0: UNDERDETERMINED/ACQUIRED; s0: HORIZON/ACQUIRED; s1: HORIZON/HORIZON | **PASS** |
| W09efdf93 | f0, f1, p0, s0, s1 (-) | f0: ACQUIRED/ACQUIRED; f1: HORIZON/HORIZON; p0: UNDERDETERMINED/UNDERDETERMINED; s0: ACQUIRED/HORIZON; s1: HORIZON/HORIZON | **FAIL** |
| Wd1490fbb | f0, f1, p0, s0, s1 (-) | f0: HORIZON/UNDERDETERMINED; f1: UNDERDETERMINED/UNDERDETERMINED; p0: ACQUIRED/ACQUIRED; s0: ACQUIRED/ACQUIRED; s1: HORIZON/HORIZON | **FAIL** |
| Wb49b6a5f | f0, f1, p0, s0, s1 (-) | f0: HORIZON/HORIZON; f1: ACQUIRED/ACQUIRED; p0: HORIZON/ACQUIRED; s0: HORIZON/HORIZON; s1: ACQUIRED/ACQUIRED | **FAIL** |
| W483b8c31 | f0, f1, p0, s0, s1 (-) | f0: ACQUIRED/ACQUIRED; f1: HORIZON/ACQUIRED; p0: ACQUIRED/ACQUIRED; s0: HORIZON/HORIZON; s1: HORIZON/HORIZON | **PASS** |
| W0321d83c | f0, f1, p0, s0, s1 (-) | f0: ACQUIRED/ACQUIRED; f1: HORIZON/HORIZON; p0: ACQUIRED/ACQUIRED; s0: HORIZON/HORIZON; s1: HORIZON/HORIZON | **PASS** |
| W3a22e2ee | f0, f1, p0, s0, s1 (-) | f0: ACQUIRED/ACQUIRED; f1: HORIZON/HORIZON; p0: ACQUIRED/ACQUIRED; s0: HORIZON/HORIZON; s1: HORIZON/HORIZON | **FAIL** |
| W8f6a223e | f1, p0, s0, s1 (f0) | f1: HORIZON/HORIZON; p0: UNDERDETERMINED/ACQUIRED; s0: ACQUIRED/ACQUIRED; s1: HORIZON/HORIZON | **FAIL** |
| W480ffd54 | f0, f1, p0, s0, s1 (-) | f0: ACQUIRED/ACQUIRED; f1: ACQUIRED/ACQUIRED; p0: ACQUIRED/ACQUIRED; s0: HORIZON/HORIZON; s1: HORIZON/HORIZON | **PASS** |
| W38fc86d7 | f0, f1, p0, s0, s1 (-) | f0: ACQUIRED/ACQUIRED; f1: HORIZON/HORIZON; p0: UNDERDETERMINED/ACQUIRED; s0: HORIZON/HORIZON; s1: HORIZON/HORIZON | **FAIL** |
| W6eb945cc | f0, f1, p0, s0, s1 (-) | f0: ACQUIRED/ACQUIRED; f1: HORIZON/HORIZON; p0: ACQUIRED/ACQUIRED; s0: HORIZON/ACQUIRED; s1: HORIZON/HORIZON | **PASS** |

## 3. Pooled

| rung | generated | gen OK | admitted | class histogram |
|---|---|---|---|---|
| R0 | 74 | 72 | (control) | DUPLICATE 2; TRIVIAL_BY_LIBRARY 11; TRIVIAL_BY_REACTIVE 45; TRIVIAL_BY_REGRESSION 14; TRIVIAL_BY_SMALL_SEARCH 2 |
| R1 | 162 | 118 | (control) | DEGENERATE 8; DUPLICATE 36; NEAR_TRIVIAL 5; QUALIFIED 93; TRIVIAL_BY_LIBRARY 1; TRIVIAL_BY_REACTIVE 8; TRIVIAL_BY_SMALL_SEARCH 11 |
| R2 | 150 | 120 | 38 | DEGENERATE 19; DUPLICATE 7; FAIL_PRONE 4; KNOWN_POSITIVE_FAIL:DEV_UNDERDETERMINED 3; KNOWN_POSITIVE_FAIL:HORIZON 42; MOTIF_CAP 4; NEAR_TRIVIAL 8; QUALIFIED 38; SYNTHETIC_DEPTH 4; TRIVIAL_BY_BASE_1E6 4; TRIVIAL_BY_LIBRARY 2; TRIVIAL_BY_REACTIVE 4; TRIVIAL_BY_REGRESSION 11 |
| R3 | 178 | 144 | 8 | CHAIN_C_FAIL:f0 8; CHAIN_C_FAIL:f0+f1 1; CHAIN_C_FAIL:f0+s0 1; CHAIN_C_FAIL:f0+s1 3; CHAIN_C_FAIL:f1 21; CHAIN_C_FAIL:f1+s0 3; CHAIN_C_FAIL:f1+s1 13; CHAIN_C_FAIL:p0 1; CHAIN_C_FAIL:p0+s1 2; CHAIN_C_FAIL:s0 28; CHAIN_C_FAIL:s0+s1 5; CHAIN_C_FAIL:s1 26; CHAIN_D_FAIL:HORIZON 7; CHAIN_D_FAIL:NOT_FOUND 2; CHAIN_D_FAIL:TRIBUNAL 1; DEGENERATE 6; DUPLICATE 17; FAIL_PRONE 11; NEAR_TRIVIAL 4; QUALIFIED 8; SYNTHETIC_DEPTH 1; TRIVIAL_BY_BASE_1E6 2; TRIVIAL_BY_LOOKUP 1; TRIVIAL_BY_REGRESSION 6 |
| R4 | 94 | 72 | 7 | CHAIN_C_FAIL:f0 9; CHAIN_C_FAIL:f1 10; CHAIN_C_FAIL:f1+p0 4; CHAIN_C_FAIL:f1+s0 2; CHAIN_C_FAIL:f1+s1 4; CHAIN_C_FAIL:p0 2; CHAIN_C_FAIL:s0 5; CHAIN_C_FAIL:s1 16; CHAIN_D_FAIL:HORIZON 3; DEGENERATE 2; DUPLICATE 4; FAIL_PRONE 16; QUALIFIED 7; SYNTHETIC_DEPTH 4; TRIVIAL_BY_LIBRARY 1; TRIVIAL_BY_REACTIVE 2; TRIVIAL_BY_REGRESSION 3 |
| R5 | 123 | 96 | 0 | CHAIN_C_FAIL:f0 10; CHAIN_C_FAIL:f0+s0 1; CHAIN_C_FAIL:f0+s1 2; CHAIN_C_FAIL:f1 18; CHAIN_C_FAIL:f1+s0 2; CHAIN_C_FAIL:f1+s1 13; CHAIN_C_FAIL:p0 2; CHAIN_C_FAIL:s0 15; CHAIN_C_FAIL:s0+s1 3; CHAIN_C_FAIL:s1 12; CHAIN_D_FAIL:HORIZON 8; DEGENERATE 13; DUPLICATE 13; FAIL_PRONE 1; NEAR_TRIVIAL 2; SYNTHETIC_DEPTH 2; TRIVIAL_BY_BASE_1E6 1; TRIVIAL_BY_REACTIVE 2; TRIVIAL_BY_REGRESSION 3 |

Kind-pairs among admitted R3/R4/R5: fp, fs. **E1: WORLD_DEMAND_NOT_QUALIFIED (motif coverage: 2 kind-pairs < 3)**

## 4. Admitted families

| family | skeleton | promoted witness | solution found | rank (order-free) |
|---|---|---|---|---|
| Wc025415a-F021-R2 | R2:f:base_fold | `(foldl (lam a (lam b (add b a))) 1 (map (lam x (f0 x)) xs))` | `(sum (scanl (lam a (lam b (f0 b))) 1 xs))` | 9841 (27213) |
| Wc025415a-F041-R4 | R4:fp:guard_p | `(map (lam x (if (p0 x) (f1 x) x)) xs)` | `(map (lam x (if (q1 x) (q0 x) x)) xs)` | 273050 (288448) |
| Wc025415a-F044-R4 | R4:fp:filter_of_map | `(filter (lam x (p0 x)) (map (lam x (f1 x)) xs))` | `(filter (lam x (q1 x)) (map (lam x (q0 x)) xs))` | 29413 (31793) |
| W2bdef02f-F022-R2 | R2:f:guard | `(map (lam x (if (gt 1 x) (f0 x) x)) xs)` | `(map (lam x (max (scanl (lam a (lam b x)) (f0 x) xs))) xs)` | 368479 (495337) |
| W2bdef02f-F024-R2 | R2:p:base_post | `(mul (sum (filter (lam x (p0 x)) xs)) (sum (filter (lam x (p0 x)) xs)))` | `(pow (sum (filter (lam x (p0 x)) xs)) 2)` | 410414 (338651) |
| W2bdef02f-F026-R2 | R2:s:base_post | `(sub 0 (foldl (lam a (lam b (s1 a b))) 0 xs))` | `(neg (foldl (lam a (lam b (s1 a b))) 0 xs))` | 90142 (338651) |
| W2bdef02f-F027-R2 | R2:f:base_fold | `(foldl (lam a (lam b (sub a b))) 0 (map (lam x (f0 x)) xs))` | `(neg (sum (map (lam x (f0 x)) xs)))` | 4853 (28916) |
| W2bdef02f-F031-R2 | R2:s:base_fold | `(foldl (lam a (lam b (add a b))) 0 (scanl (lam a (lam b (s1 a b))) 0 xs))` | `(sum (scanl (lam a (lam b (s1 a b))) 0 xs))` | 114686 (338651) |
| W2bdef02f-F042-R3 | R3:fp:map_of_filter | `(map (lam x (f0 x)) (filter (lam x (p0 x)) xs))` | `(map (lam x (q0 x)) (filter (lam x (q1 x)) xs))` | 24088 (35491) |
| W2bdef02f-F048-R4 | R4:fs:post_fold | `(f0 (foldl (lam a (lam b (s0 a b))) 1 xs))` | `(q0 (foldl (lam a (lam b (q2 a b))) 1 xs))` | 114036 (196839) |
| W2bdef02f-F051-R4 | R4:fs:scan_of_map | `(scanl (lam a (lam b (s0 a b))) 1 (map (lam x (f0 x)) xs))` | `(scanl (lam a (lam b (q2 a (q0 b)))) 1 xs)` | 50929 (35491) |
| W09efdf93-F018-R2 | R2:f:base_post | `(mul (head (map (lam x (f0 x)) xs)) (head (map (lam x (f0 x)) xs)))` | `(pow (f0 (head xs)) 2)` | 3750 (3503) |
| W09efdf93-F024-R2 | R2:f:base_fold | `(foldl (lam a (lam b (add a b))) 0 (map (lam x (f1 x)) xs))` | `(sum (map (lam x (f1 x)) xs))` | 1299 (3503) |
| W09efdf93-F029-R2 | R2:f:extra_p | `(map (lam x (f1 x)) (filter (lam x (lt 2 x)) xs))` | `(map (lam x (f1 x)) (filter (lam x (lt 2 x)) xs))` | 320345 (491605) |
| Wd1490fbb-F019-R2 | R2:f:base_fold | `(foldl (lam a (lam b (add a b))) 0 (map (lam x (f0 x)) xs))` | `(sum (map (lam x (f0 x)) xs))` | 1289 (3472) |
| Wd1490fbb-F021-R2 | R2:p:base_post | `(mul (sum (filter (lam x (p0 x)) xs)) (sum (filter (lam x (p0 x)) xs)))` | `(pow (sum (filter (lam x (p0 x)) xs)) 2)` | 400874 (336104) |
| Wd1490fbb-F022-R2 | R2:s:base_fold | `(foldl (lam a (lam b (sub a b))) 0 (scanl (lam a (lam b (s0 a b))) 0 xs))` | `(neg (sum (scanl (lam a (lam b (s0 a b))) 0 xs)))` | 533359 (3542000) |
| Wb49b6a5f-F021-R2 | R2:s:base_fold | `(foldl (lam a (lam b (add b a))) 0 (scanl (lam a (lam b (s1 a b))) 0 xs))` | `(sum (scanl (lam a (lam b (s1 a b))) 0 xs))` | 119130 (352145) |
| Wb49b6a5f-F024-R2 | R2:p:base_post | `(neg (len (filter (lam x (p0 x)) xs)))` | `(neg (len (filter (lam x (p0 x)) xs)))` | 4855 (30434) |
| Wb49b6a5f-F052-R4 | R4:fp:guard_p | `(map (lam x (if (p0 x) (f1 x) x)) xs)` | `(map (lam x (if (q1 x) (q0 x) x)) xs)` | 350078 (362075) |
| Wb49b6a5f-F055-R4 | R4:fp:map_of_filter | `(map (lam x (f1 x)) (filter (lam x (p0 x)) xs))` | `(map (lam x (q0 x)) (filter (lam x (q1 x)) xs))` | 26446 (38276) |
| W483b8c31-F022-R2 | R2:p:extra_f | `(filter (lam x (p0 x)) (map (lam x (gcd x x)) xs))` | `(filter (lam x (p0 x)) (map (lam x (gcd x x)) xs))` | 498944 (508565) |
| W483b8c31-F026-R2 | R2:f:base_fold | `(foldl (lam a (lam b (mul b a))) 1 (map (lam x (f1 x)) xs))` | `(foldl (lam a (lam b (mul a (f1 b)))) 1 xs)` | 532052 (349404) |
| W483b8c31-F030-R2 | R2:f:self_compose | `(map (lam x (f0 (f0 x))) xs)` | `(map (lam x (f0 (f0 x))) xs)` | 412 (629) |
| W483b8c31-F045-R3 | R3:fp:guard_p | `(map (lam x (if (p0 x) (f0 x) x)) xs)` | `(map (lam x (if (q2 x) (q0 x) x)) xs)` | 361926 (386837) |
| W483b8c31-F046-R3 | R3:fp:map_of_filter | `(map (lam x (f1 x)) (filter (lam x (p0 x)) xs))` | `(map (lam x (q1 x)) (filter (lam x (q2 x)) xs))` | 27949 (39197) |
| W0321d83c-F024-R2 | R2:s:extra_struct | `(foldl (lam a (lam b (s1 a b))) 1 (rev xs))` | `(foldl (lam a (lam b (s1 a b))) 1 (rev xs))` | 539443 (351982) |
| W0321d83c-F026-R2 | R2:f:extra_struct+red | `(max (take 3 (map (lam x (f1 x)) xs)))` | `(max (take 3 (map (lam x (f1 x)) xs)))` | 120223 (351982) |
| W0321d83c-F040-R3 | R3:fp:map_of_filter | `(map (lam x (f0 x)) (filter (lam x (p0 x)) xs))` | `(map (lam x (q0 x)) (filter (lam x (q1 x)) xs))` | 22524 (31773) |
| W3a22e2ee-F024-R2 | R2:f:extra_f+red | `(max (map (lam x (neg x)) (map (lam x (f0 x)) xs)))` | `(neg (min (map (lam x (f0 x)) xs)))` | 4796 (27503) |
| W3a22e2ee-F025-R2 | R2:f:self_compose+red | `(max (map (lam x (f1 (f1 x))) xs))` | `(max (map (lam x (f1 (f1 x))) xs))` | 10282 (27503) |
| W3a22e2ee-F028-R2 | R2:s:base_fold | `(foldl (lam a (lam b (add a b))) 0 (scanl (lam a (lam b (s1 a b))) 1 xs))` | `(sum (scanl (lam a (lam b (s1 a b))) 1 xs))` | 111233 (328632) |
| W3a22e2ee-F031-R2 | R2:p:base_post | `(mul 2 (len (filter (lam x (p0 x)) xs)))` | `(sum (map (lam x 2) (filter (lam x (p0 x)) xs)))` | 107783 (328632) |
| W8f6a223e-F017-R2 | R2:p:base_post | `(mul (len (filter (lam x (p0 x)) xs)) (len (filter (lam x (p0 x)) xs)))` | `(pow (len (filter (lam x (p0 x)) xs)) 2)` | 305530 (269436) |
| W8f6a223e-F020-R2 | R2:f:self_compose | `(map (lam x (f1 (f1 x))) xs)` | `(map (lam x (f1 (f1 x))) xs)` | 390 (617) |
| W480ffd54-F023-R2 | R2:p:base_post | `(mul (len (filter (lam x (p0 x)) xs)) (len (filter (lam x (p0 x)) xs)))` | `(pow (len (filter (lam x (p0 x)) xs)) 2)` | 382349 (324454) |
| W480ffd54-F024-R2 | R2:s:base_fold | `(foldl (lam a (lam b (sub a b))) 0 (scanl (lam a (lam b (s0 a b))) 0 xs))` | `(neg (sum (scanl (lam a (lam b (s0 a b))) 0 xs)))` | 508498 (3371705) |
| W480ffd54-F026-R2 | R2:f:base_fold | `(foldl (lam a (lam b (add a b))) 0 (map (lam x (f0 x)) xs))` | `(sum (map (lam x (f0 x)) xs))` | 1250 (3375) |
| W480ffd54-F028-R2 | R2:p:base_fold | `(foldl (lam a (lam b (add b a))) 1 (filter (lam x (p0 x)) xs))` | `(add 1 (sum (filter (lam x (p0 x)) xs)))` | 207709 (324454) |
| W480ffd54-F031-R2 | R2:f:extra_struct | `(drop 3 (map (lam x (f0 x)) xs))` | `(drop 3 (map (lam x (f0 x)) xs))` | 2186 (3977) |
| W480ffd54-F039-R3 | R3:fp:filter_of_map | `(filter (lam x (p0 x)) (map (lam x (f0 x)) xs))` | `(filter (lam x (q2 x)) (map (lam x (q0 x)) xs))` | 34269 (36511) |
| W480ffd54-F046-R3 | R3:fp:map_of_filter | `(map (lam x (f0 x)) (filter (lam x (p0 x)) xs))` | `(map (lam x (q0 x)) (filter (lam x (q2 x)) xs))` | 25351 (36511) |
| W480ffd54-F055-R4 | R4:fp:map_of_filter | `(map (lam x (f1 x)) (filter (lam x (p0 x)) xs))` | `(map (lam x (q1 x)) (filter (lam x (q2 x)) xs))` | 25433 (36511) |
| W38fc86d7-F025-R2 | R2:f:extra_f | `(map (lam x (add x 1)) (map (lam x (f1 x)) xs))` | `(map (lam x (add 1 (f1 x))) xs)` | 4026 (4362) |
| W38fc86d7-F029-R2 | R2:f:extra_p+red | `(sum (filter (lam x (not (gt x 1))) (map (lam x (f0 x)) xs)))` | `(len (filter (lam x (eq 1 (f0 x))) xs))` | 96447 (346052) |
| W38fc86d7-F031-R2 | R2:p:base_post | `(add (sum (filter (lam x (p0 x)) xs)) 3)` | `(add 3 (sum (filter (lam x (p0 x)) xs)))` | 229691 (346052) |
| W38fc86d7-F035-R2 | R2:f:guard | `(map (lam x (if (lt x 3) (f1 x) x)) xs)` | `(map (lam x (max (scanl (lam a (lam b x)) (f1 x) xs))) xs)` | 379890 (510665) |
| W6eb945cc-F023-R2 | R2:s:base_post | `(sub 0 (foldl (lam a (lam b (s1 a b))) 1 xs))` | `(neg (foldl (lam a (lam b (s1 a b))) 1 xs))` | 90993 (341960) |
| W6eb945cc-F024-R2 | R2:f:base_post | `(div (sum (map (lam x (f0 x)) xs)) 3)` | `(div (sum (map (lam x (f0 x)) xs)) 3)` | 314813 (341960) |
| W6eb945cc-F025-R2 | R2:f:base_post | `(gcd (last (map (lam x (f1 x)) xs)) (last (map (lam x (f1 x)) xs)))` | `(gcd 0 (f1 (last xs)))` | 3489 (3549) |
| W6eb945cc-F028-R2 | R2:s:extra_struct | `(foldl (lam a (lam b (s1 a b))) 0 (rev xs))` | `(foldl (lam a (lam b (s1 a b))) 0 (rev xs))` | 517885 (341960) |
| W6eb945cc-F033-R3 | R3:fs:scan_of_map | `(scanl (lam a (lam b (s0 a b))) 1 (map (lam x (f0 x)) xs))` | `(scanl (lam a (lam b (q2 a (q0 b)))) 1 xs)` | 53685 (37162) |
| W6eb945cc-F047-R3 | R3:fs:post_fold | `(f0 (foldl (lam a (lam b (s0 a b))) 0 xs))` | `(q0 (foldl (lam a (lam b (q2 a b))) 0 xs))` | 118789 (205046) |
