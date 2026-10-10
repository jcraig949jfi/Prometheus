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
| W0467897d | 6/6 | 0/8 | 49/49 |
| Wf294d5d9 | 6/6 | 0/10 | 52/52 |
| W1d5301d0 | 6/6 | 0/8 | 50/50 |

## 2. Admission by world and rung

| world | rung | generated | gen OK | admitted | class histogram |
|---|---|---|---|---|---|
| W0467897d | R0 | 6 | 6 | (control) | TRIVIAL_BY_REACTIVE 5; TRIVIAL_BY_REGRESSION 1 |
| W0467897d | R1 | 13 | 8 | (control) | DEGENERATE 3; DUPLICATE 2; QUALIFIED 7; TRIVIAL_BY_REACTIVE 1 |
| W0467897d | R2 | 15 | 10 | 3 | DEGENERATE 3; FAIL_PRONE 2; KNOWN_POSITIVE_FAIL:HORIZON 3; NEAR_TRIVIAL 1; QUALIFIED 3; TRIVIAL_BY_BASE_1E6 1; TRIVIAL_BY_REGRESSION 2 |
| W0467897d | R3 | 68 | 12 | 3 | CHAIN_C_FAIL:s1 3; CHAIN_D_FAIL:HORIZON 1; DEGENERATE 16; DUPLICATE 16; FAIL_PRONE 24; NEAR_TRIVIAL 3; QUALIFIED 3; SYNTHETIC_DEPTH 1; TRIVIAL_BY_BASE_1E6 1 |
| W0467897d | R4 | 200 | 5 | 0 | CHAIN_C_FAIL:s0 4; DEGENERATE 42; DUPLICATE 110; FAIL_PRONE 43; TRIVIAL_BY_REACTIVE 1 |
| W0467897d | R5 | 9 | 8 | 0 | CHAIN_C_FAIL:s1 2; CHAIN_D_FAIL:HORIZON 4; FAIL_PRONE 1; NEAR_TRIVIAL 2 |
| Wf294d5d9 | R0 | 7 | 6 | (control) | DUPLICATE 1; TRIVIAL_BY_LIBRARY 1; TRIVIAL_BY_REACTIVE 4; TRIVIAL_BY_SMALL_SEARCH 1 |
| Wf294d5d9 | R1 | 19 | 10 | (control) | DEGENERATE 8; DUPLICATE 1; QUALIFIED 8; TRIVIAL_BY_REACTIVE 1; TRIVIAL_BY_SMALL_SEARCH 1 |
| Wf294d5d9 | R2 | 13 | 10 | 0 | DEGENERATE 2; DUPLICATE 1; KNOWN_POSITIVE_FAIL:HORIZON 6; SYNTHETIC_DEPTH 1; TRIVIAL_BY_BASE_1E6 1; TRIVIAL_BY_REGRESSION 1; TRIVIAL_BY_SMALL_SEARCH 1 |
| Wf294d5d9 | R3 | 22 | 12 | 0 | CHAIN_C_FAIL:f0 2; CHAIN_C_FAIL:f0+f1 1; CHAIN_C_FAIL:f0+s1 2; CHAIN_C_FAIL:s1 6; DEGENERATE 8; DUPLICATE 2; TRIVIAL_BY_REACTIVE 1 |
| Wf294d5d9 | R4 | 21 | 6 | 0 | CHAIN_C_FAIL:f1 2; CHAIN_D_FAIL:HORIZON 4; DEGENERATE 11; DUPLICATE 4 |
| Wf294d5d9 | R5 | 13 | 8 | 0 | CHAIN_C_FAIL:f0+f1 2; CHAIN_C_FAIL:f0+s1 1; CHAIN_C_FAIL:s1 4; DEGENERATE 4; DUPLICATE 1; TRIVIAL_BY_REACTIVE 1 |
| W1d5301d0 | R0 | 6 | 6 | (control) | TRIVIAL_BY_REACTIVE 2; TRIVIAL_BY_REGRESSION 2; TRIVIAL_BY_SMALL_SEARCH 2 |
| W1d5301d0 | R1 | 9 | 8 | (control) | DUPLICATE 1; QUALIFIED 5; TRIVIAL_BY_REACTIVE 1; TRIVIAL_BY_SMALL_SEARCH 2 |
| W1d5301d0 | R2 | 12 | 10 | 3 | DEGENERATE 1; DUPLICATE 1; KNOWN_POSITIVE_FAIL:HORIZON 4; NEAR_TRIVIAL 1; QUALIFIED 3; TRIVIAL_BY_BASE_1E6 1; TRIVIAL_BY_REGRESSION 1 |
| W1d5301d0 | R3 | 43 | 12 | 2 | CHAIN_C_FAIL:s1 6; CHAIN_D_FAIL:HORIZON 4; DUPLICATE 31; QUALIFIED 2 |
| W1d5301d0 | R4 | 11 | 6 | 2 | CHAIN_C_FAIL:s1 2; DEGENERATE 4; DUPLICATE 1; QUALIFIED 2; SYNTHETIC_DEPTH 1; TRIVIAL_BY_REACTIVE 1 |
| W1d5301d0 | R5 | 10 | 8 | 0 | CHAIN_C_FAIL:s1 4; CHAIN_D_FAIL:HORIZON 4; DEGENERATE 1; DUPLICATE 1 |

| world | mechanisms (unfilled) | chain (c) by mechanism | E1 gate |
|---|---|---|---|
| W0467897d | f1, p0, s0, s1 (f0) | f1: ACQUIRED/ACQUIRED; p0: ACQUIRED/UNDERDETERMINED; s0: HORIZON/HORIZON; s1: HORIZON/HORIZON | **PASS** |
| Wf294d5d9 | f0, f1, p0, s0, s1 (-) | f0: NOT_EXTRACTABLE/TRIBUNAL; f1: HORIZON/HORIZON; p0: ACQUIRED/ACQUIRED; s0: ACQUIRED/ACQUIRED; s1: HORIZON/HORIZON | **FAIL** |
| W1d5301d0 | f1, p0, s0, s1 (f0) | f1: ACQUIRED/ACQUIRED; p0: ACQUIRED/ACQUIRED; s0: HORIZON/ACQUIRED; s1: HORIZON/HORIZON | **PASS** |

## 3. Pooled

| rung | generated | gen OK | admitted | class histogram |
|---|---|---|---|---|
| R0 | 19 | 18 | (control) | DUPLICATE 1; TRIVIAL_BY_LIBRARY 1; TRIVIAL_BY_REACTIVE 11; TRIVIAL_BY_REGRESSION 3; TRIVIAL_BY_SMALL_SEARCH 3 |
| R1 | 41 | 26 | (control) | DEGENERATE 11; DUPLICATE 4; QUALIFIED 20; TRIVIAL_BY_REACTIVE 3; TRIVIAL_BY_SMALL_SEARCH 3 |
| R2 | 40 | 30 | 6 | DEGENERATE 6; DUPLICATE 2; FAIL_PRONE 2; KNOWN_POSITIVE_FAIL:HORIZON 13; NEAR_TRIVIAL 2; QUALIFIED 6; SYNTHETIC_DEPTH 1; TRIVIAL_BY_BASE_1E6 3; TRIVIAL_BY_REGRESSION 4; TRIVIAL_BY_SMALL_SEARCH 1 |
| R3 | 133 | 36 | 5 | CHAIN_C_FAIL:f0 2; CHAIN_C_FAIL:f0+f1 1; CHAIN_C_FAIL:f0+s1 2; CHAIN_C_FAIL:s1 15; CHAIN_D_FAIL:HORIZON 5; DEGENERATE 24; DUPLICATE 49; FAIL_PRONE 24; NEAR_TRIVIAL 3; QUALIFIED 5; SYNTHETIC_DEPTH 1; TRIVIAL_BY_BASE_1E6 1; TRIVIAL_BY_REACTIVE 1 |
| R4 | 232 | 17 | 2 | CHAIN_C_FAIL:f1 2; CHAIN_C_FAIL:s0 4; CHAIN_C_FAIL:s1 2; CHAIN_D_FAIL:HORIZON 4; DEGENERATE 57; DUPLICATE 115; FAIL_PRONE 43; QUALIFIED 2; SYNTHETIC_DEPTH 1; TRIVIAL_BY_REACTIVE 2 |
| R5 | 32 | 24 | 0 | CHAIN_C_FAIL:f0+f1 2; CHAIN_C_FAIL:f0+s1 1; CHAIN_C_FAIL:s1 10; CHAIN_D_FAIL:HORIZON 8; DEGENERATE 5; DUPLICATE 2; FAIL_PRONE 1; NEAR_TRIVIAL 2; TRIVIAL_BY_REACTIVE 1 |

Kind-pairs among admitted R3/R4/R5: fp, fs. **E1: WORLD_DEMAND_NOT_QUALIFIED (motif coverage: 2 kind-pairs < 3)**

## 4. Admitted families

| family | skeleton | promoted witness | solution found | rank (order-free) |
|---|---|---|---|---|
| W0467897d-F019-R2 | R2:f:self_compose+red | `(sum (map (lam x (f1 (f1 x))) xs))` | `(sum (map (lam x (f1 (f1 x))) xs))` | 8506 (21348) |
| W0467897d-F027-R2 | R2:f:base_post | `(pow (head (map (lam x (f1 x)) xs)) 3)` | `(f1 (f1 (head xs)))` | 135 (154) |
| W0467897d-F033-R2 | R2:s:base_fold | `(foldl (lam a (lam b (add a b))) 0 (scanl (lam a (lam b (s0 a b))) 1 xs))` | `(sum (scanl (lam a (lam b (s0 a b))) 1 xs))` | 96079 (268865) |
| W0467897d-F061-R3 | R3:fp:map_of_filter+red | `(sum (map (lam x (f1 x)) (filter (lam x (p0 x)) xs)))` | `(sum (map (lam x (q0 x)) (filter (lam x (q1 x)) xs)))` | 599623 (1490970) |
| W0467897d-F081-R3 | R3:fp:filter_of_map+red | `(sum (filter (lam x (p0 x)) (map (lam x (f1 x)) xs)))` | `(sum (filter (lam x (q1 x)) (map (lam x (q0 x)) xs)))` | 607087 (1490970) |
| W0467897d-F085-R3 | R3:fp:guard_p | `(map (lam x (if (p0 x) (f1 x) x)) xs)` | `(map (lam x (if (q1 x) (q0 x) x)) xs)` | 298494 (315301) |
| W1d5301d0-F015-R2 | R2:f:base_post | `(mul (sum (map (lam x (f1 x)) xs)) (sum (map (lam x (f1 x)) xs)))` | `(pow (sum (map (lam x (f1 x)) xs)) 2)` | 279282 (255758) |
| W1d5301d0-F018-R2 | R2:s:extra_struct | `(foldl (lam a (lam b (s1 a b))) 1 (rev xs))` | `(foldl (lam a (lam b (s1 a b))) 0 (rev xs))` | 355685 (255758) |
| W1d5301d0-F023-R2 | R2:f:self_compose+red | `(sum (map (lam x (f1 (f1 x))) xs))` | `(sum (map (lam x (f1 (f1 x))) xs))` | 7799 (19430) |
| W1d5301d0-F027-R3 | R3:fs:step_of_f | `(foldl (lam a (lam b (s0 a (f1 b)))) 0 xs)` | `(foldl (lam a (lam b (q2 a (q0 b)))) 0 xs)` | 286248 (196115) |
| W1d5301d0-F035-R3 | R3:fs:post_fold | `(f1 (foldl (lam a (lam b (s0 a b))) 0 xs))` | `(q0 (foldl (lam a (lam b (q2 a b))) 0 xs))` | 113606 (196115) |
| W1d5301d0-F071-R4 | R4:fp:filter_of_map | `(filter (lam x (p0 x)) (map (lam x (f1 x)) xs))` | `(filter (lam x (q1 x)) (map (lam x (q0 x)) xs))` | 32489 (35348) |
| W1d5301d0-F077-R4 | R4:fp:guard_p | `(map (lam x (if (p0 x) (f1 x) x)) xs)` | `(map (lam x (if (q1 x) (q0 x) x)) xs)` | 319649 (330288) |
