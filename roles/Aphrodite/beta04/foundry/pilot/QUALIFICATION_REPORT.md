# Beta-04 E1 foundry pilot: qualification report

generator config_sha `6e337ef5392387c81e67342b5e243d9adeb0138144a481b309e2c59947eca418`; qualification config_sha `948917b61b3feac0cef9c04cccb2fe08a11f0c6bc61f45b20308c419738f81de`; B_small=100000, B_oracle=1000000. Closed-form nulls in HINDSIGHT mode.

## 1. Controls (run first)

### 1a. Planted controls

| family | expectation | solved by | oracle-library KP |
|---|---|---|---|
| PLANTED-LOOKUP | lookup solves (history2 tables also memorise, since test inputs == dev inputs); constant fails | lookup, history2 | NOT_FOUND |
| PLANTED-RANDOM | no baseline solves; oracle-library search fails -> KNOWN_POSITIVE_FAIL | none | NOT_FOUND |
| PLANTED-REACTIVE | reactive (elementwise table) solves; constant/lookup/small fail | reactive | NOT_FOUND |

### 1b. Per-world controls

| world | R0 solved by a trivial baseline | R1 KP pass | admitted with KP pass | witness verified (A) | promoted==expanded |
|---|---|---|---|---|---|
| W1 | 6/6 | 10/10 | 15/15 | 44/44 | 44/44 |
| W2 | 6/6 | 10/10 | 11/11 | 44/44 | 44/44 |
| W3 | 6/6 | 10/10 | 13/13 | 44/44 | 44/44 |

## 2. Admission by world and rung

| world | rung | generated | passed gen screens | admitted (R>=2) / qualified controls (R0-R1) | KP pass | KP rank <= B_small | oracle median rank | class histogram |
|---|---|---|---|---|---|---|---|---|
| W1 | R0 | 7 | 6 | 0 | 6 | 6 | 375.0 | DUPLICATE 1; TRIVIAL_BY_REACTIVE 4; TRIVIAL_BY_SMALL_SEARCH 2 |
| W1 | R1 | 14 | 10 | 7 | 10 | 10 | 583.5 | DUPLICATE 4; QUALIFIED 7; TRIVIAL_BY_REACTIVE 2; TRIVIAL_BY_SMALL_SEARCH 1 |
| W1 | R2 | 16 | 10 | 6 | 7 | 5 | 5202 | DEGENERATE 4; DUPLICATE 1; FAIL_PRONE 1; KNOWN_POSITIVE_FAIL:NOT_FOUND 3; QUALIFIED 6; TRIVIAL_BY_SMALL_SEARCH 1 |
| W1 | R3 | 14 | 12 | 7 | 7 | 2 | 552779 | DEGENERATE 1; DUPLICATE 1; KNOWN_POSITIVE_FAIL:NOT_FOUND 5; QUALIFIED 7 |
| W1 | R4 | 8 | 6 | 2 | 3 | 3 | 436 | FAIL_PRONE 2; KNOWN_POSITIVE_FAIL:NOT_FOUND 3; QUALIFIED 2; TRIVIAL_BY_REACTIVE 1 |
| W2 | R0 | 6 | 6 | 0 | 4 | 4 | 245.0 | TRIVIAL_BY_REACTIVE 5; TRIVIAL_BY_SMALL_SEARCH 1 |
| W2 | R1 | 11 | 10 | 5 | 10 | 10 | 558.5 | DUPLICATE 1; QUALIFIED 5; TRIVIAL_BY_REACTIVE 3; TRIVIAL_BY_SMALL_SEARCH 2 |
| W2 | R2 | 11 | 10 | 3 | 6 | 4 | 876.0 | FAIL_PRONE 1; KNOWN_POSITIVE_FAIL:NOT_FOUND 4; QUALIFIED 3; TRIVIAL_BY_LIBRARY 1; TRIVIAL_BY_REACTIVE 2 |
| W2 | R3 | 12 | 12 | 6 | 9 | 7 | 71226 | KNOWN_POSITIVE_FAIL:NOT_FOUND 3; QUALIFIED 6; SYNTHETIC_DEPTH 1; TRIVIAL_BY_LIBRARY 2 |
| W2 | R4 | 6 | 6 | 2 | 3 | 1 | 542395 | KNOWN_POSITIVE_FAIL:NOT_FOUND 3; QUALIFIED 2; SYNTHETIC_DEPTH 1 |
| W3 | R0 | 6 | 6 | 0 | 5 | 5 | 111 | TRIVIAL_BY_LIBRARY 1; TRIVIAL_BY_REACTIVE 4; TRIVIAL_BY_SMALL_SEARCH 1 |
| W3 | R1 | 14 | 10 | 5 | 10 | 10 | 715.0 | DEGENERATE 2; DUPLICATE 2; QUALIFIED 5; TRIVIAL_BY_REACTIVE 2; TRIVIAL_BY_SMALL_SEARCH 3 |
| W3 | R2 | 12 | 10 | 6 | 8 | 5 | 35328.5 | DEGENERATE 2; KNOWN_POSITIVE_FAIL:NOT_FOUND 2; QUALIFIED 6; TRIVIAL_BY_REACTIVE 1; TRIVIAL_BY_SMALL_SEARCH 1 |
| W3 | R3 | 13 | 12 | 4 | 7 | 3 | 116797 | DUPLICATE 1; KNOWN_POSITIVE_FAIL:NOT_FOUND 5; QUALIFIED 4; SYNTHETIC_DEPTH 1; TRIVIAL_BY_REACTIVE 1; TRIVIAL_BY_SMALL_SEARCH 1 |
| W3 | R4 | 7 | 6 | 3 | 6 | 4 | 72479.0 | DUPLICATE 1; QUALIFIED 3; SYNTHETIC_DEPTH 3 |

## 3. Admitted families (headroom proof)

| family | skeleton | promoted witness | witness esize | oracle solution | oracle rank | KP <= B_small | oracle uses all witness mechanisms | base search solves at B_oracle | null capture (band) |
|---|---|---|---|---|---|---|---|---|---|
| W1-F023-R2 | R2:p:base_post | `(add 1 (sum (filter (lam x (p0 x)) xs)))` | 10 | `(add 1 (sum (filter (lam x (p0 x)) xs)))` | 227265 | False | True | False | 0.000 (DESERT_HARSH) |
| W1-F026-R2 | R2:f:base_fold | `(foldl (lam a (lam b (sub a b))) 0 (map (lam x (f0 x)) xs))` | 14 | `(neg (sum (map (lam x (f0 x)) xs)))` | 5202 | True | True | False | 0.000 (DESERT_HARSH) |
| W1-F027-R2 | R2:f:self_compose+red | `(last (map (lam x (f1 (f1 x))) xs))` | 34 | `(f1 (f1 (last xs)))` | 194 | True | True | False | 0.050 (DESERT_HARSH) |
| W1-F031-R2 | R2:f:base_post | `(add (head (map (lam x (f0 x)) xs)) 2)` | 12 | `(add 2 (f0 (head xs)))` | 2608 | True | True | False | 0.375 (GOLDILOCKS) |
| W1-F033-R2 | R2:p:extra_f | `(map (lam x (add x 1)) (filter (lam x (p0 x)) xs))` | 11 | `(map (lam x (add x 1)) (filter (lam x (p0 x)) xs))` | 348322 | False | True | False | 0.050 (DESERT_HARSH) |
| W1-F036-R2 | R2:f:self_compose | `(map (lam x (f0 (f0 x))) xs)` | 21 | `(map (lam x (f0 (f0 x))) xs)` | 424 | True | True | False | 0.475 (GOLDILOCKS) |
| W1-F037-R3 | R3:fp:guard_p | `(map (lam x (if (p0 x) (f0 x) x)) xs)` | 16 | `(map (lam x (if (p0 x) (f0 x) x)) xs)` | 509983 | False | True | False | 0.350 (GOLDILOCKS) |
| W1-F038-R3 | R3:fs:scan_of_map | `(scanl (lam a (lam b (s0 a b))) 1 (map (lam x (f0 x)) xs))` | 18 | `(scanl (lam a (lam b (s0 a (f0 b)))) 1 xs)` | 72810 | True | True | False | 0.000 (DESERT_HARSH) |
| W1-F042-R3 | R3:fs:step_of_f | `(foldl (lam a (lam b (s0 a (f1 b)))) 0 xs)` | 16 | `(foldl (lam a (lam b (s0 a (f1 b)))) 0 xs)` | 552791 | False | True | False | 0.000 (DESERT_HARSH) |
| W1-F043-R3 | R3:fs:step_of_f | `(foldl (lam a (lam b (s1 a (f0 b)))) 1 xs)` | 14 | `(foldl (lam a (lam b (s1 a (f0 b)))) 1 xs)` | 553488 | False | True | False | 0.000 (DESERT_HARSH) |
| W1-F045-R3 | R3:fs:fold_of_map | `(foldl (lam a (lam b (s0 a b))) 0 (map (lam x (f0 x)) xs))` | 18 | `(foldl (lam a (lam b (s0 a (f0 b)))) 0 xs)` | 552779 | False | True | False | 0.000 (DESERT_HARSH) |
| W1-F046-R3 | R3:fp:map_of_filter | `(map (lam x (f1 x)) (filter (lam x (p0 x)) xs))` | 15 | `(map (lam x (f1 x)) (filter (lam x (p0 x)) xs))` | 33204 | True | True | False | 0.000 (DESERT_HARSH) |
| W1-F050-R3 | R3:fs:step_of_f | `(foldl (lam a (lam b (s1 a (f0 b)))) 0 xs)` | 14 | `(foldl (lam a (lam b (s1 a (f0 b)))) 0 xs)` | 553487 | False | True | False | 0.000 (DESERT_HARSH) |
| W1-F054-R4 | R4:ff:two_maps | `(map (lam x (f1 x)) (map (lam x (f0 x)) xs))` | 17 | `(map (lam x (f1 (f0 x))) xs)` | 436 | True | True | False | 0.375 (GOLDILOCKS) |
| W1-F057-R4 | R4:ff:compose+red | `(min (map (lam x (f1 (f0 x))) xs))` | 34 | `(min (map (lam x (f1 (f0 x))) xs))` | 12127 | True | True | False | 0.150 (DESERT_HARSH) |
| W2-F019-R2 | R2:p:base_fold | `(foldl (lam a (lam b (add a b))) 0 (filter (lam x (p0 x)) xs))` | 12 | `(sum (filter (lam x (p0 x)) xs))` | 1321 | True | True | True | 0.825 (NEAR_TRIVIAL) |
| W2-F024-R2 | R2:p:extra_f | `(map (lam x (mul x x)) (filter (lam x (p0 x)) xs))` | 11 | `(map (lam x (mul x x)) (filter (lam x (p0 x)) xs))` | 340254 | False | True | False | 0.100 (DESERT_HARSH) |
| W2-F027-R2 | R2:f:self_compose+red | `(head (map (lam x (f0 (f0 x))) xs))` | 28 | `(f0 (f0 (head xs)))` | 143 | True | True | True | 0.200 (GOLDILOCKS) |
| W2-F028-R3 | R3:fs:scan_of_map | `(scanl (lam a (lam b (s0 a b))) 1 (map (lam x (f0 x)) xs))` | 18 | `(scanl (lam a (lam b (s0 a (f0 b)))) 1 xs)` | 71226 | True | True | False | 0.000 (DESERT_HARSH) |
| W2-F029-R3 | R3:fs:scan_of_map | `(scanl (lam a (lam b (s1 a b))) 1 (map (lam x (f0 x)) xs))` | 18 | `(scanl (lam a (lam b (s1 a (f0 b)))) 1 xs)` | 71902 | True | True | False | 0.000 (DESERT_HARSH) |
| W2-F032-R3 | R3:fs:fold_of_map | `(foldl (lam a (lam b (s0 a b))) 0 (map (lam x (f1 x)) xs))` | 16 | `(foldl (lam a (lam b (s0 a (f1 b)))) 0 xs)` | 541719 | False | True | False | 0.000 (DESERT_HARSH) |
| W2-F035-R3 | R3:fs:scan_of_map | `(scanl (lam a (lam b (s0 a b))) 0 (map (lam x (f0 x)) xs))` | 18 | `(scanl (lam a (lam b (s0 a (f0 b)))) 0 xs)` | 71225 | True | True | False | 0.000 (DESERT_HARSH) |
| W2-F036-R3 | R3:fs:fold_of_map | `(foldl (lam a (lam b (s1 a b))) 0 (map (lam x (f0 x)) xs))` | 18 | `(foldl (lam a (lam b (s1 a (f0 b)))) 0 xs)` | 542375 | False | True | False | 0.050 (DESERT_HARSH) |
| W2-F039-R3 | R3:fs:scan_of_map | `(scanl (lam a (lam b (s0 a b))) 1 (map (lam x (f1 x)) xs))` | 16 | `(scanl (lam a (lam b (s0 a (f1 b)))) 1 xs)` | 71246 | True | True | False | 0.000 (DESERT_HARSH) |
| W2-F042-R4 | R4:fs:fold_of_map | `(foldl (lam a (lam b (s1 a b))) 0 (map (lam x (f1 x)) xs))` | 16 | `(foldl (lam a (lam b (s1 a (f1 b)))) 0 xs)` | 542395 | False | True | False | 0.025 (DESERT_HARSH) |
| W2-F045-R4 | R4:fs:step_of_f | `(foldl (lam a (lam b (s1 a (f1 b)))) 1 xs)` | 14 | `(foldl (lam a (lam b (s1 a (f1 b)))) 1 xs)` | 542396 | False | True | False | 0.000 (DESERT_HARSH) |
| W3-F021-R2 | R2:f:extra_f+red | `(max (map (lam x (add x x)) (map (lam x (f1 x)) xs)))` | 12 | `(f1 (f1 (max xs)))` | 199 | True | True | False | 0.275 (GOLDILOCKS) |
| W3-F022-R2 | R2:p:base_post | `(add (sum (filter (lam x (p0 x)) xs)) 3)` | 10 | `(add 3 (sum (filter (lam x (p0 x)) xs)))` | 234454 | False | True | False | 0.025 (DESERT_HARSH) |
| W3-F024-R2 | R2:s:self_compose | `(foldl (lam a (lam b (s1 a b))) 0 (scanl (lam a (lam b (s1 a b))) 0 xs))` | 19 | `(sum (scanl (lam a (lam b (s1 a b))) 3 xs))` | 119721 | False | True | False | 0.000 (DESERT_HARSH) |
| W3-F025-R2 | R2:f:base_fold | `(foldl (lam a (lam b (sub a b))) 0 (map (lam x (f0 x)) xs))` | 14 | `(neg (sum (map (lam x (f0 x)) xs)))` | 5141 | True | True | False | 0.025 (DESERT_HARSH) |
| W3-F027-R2 | R2:p:base_post | `(mul 2 (len (filter (lam x (p0 x)) xs)))` | 10 | `(f1 (len (filter (lam x (p0 x)) xs)))` | 17050 | True | True | False | 0.125 (DESERT_HARSH) |
| W3-F030-R2 | R2:f:base_fold | `(foldl (lam a (lam b (sub b a))) 0 (map (lam x (f0 x)) xs))` | 14 | `(foldl (lam a (lam b (sub (f0 b) a))) 0 xs)` | 546672 | False | True | False | 0.025 (DESERT_HARSH) |
| W3-F032-R3 | R3:fs:scan_of_map | `(scanl (lam a (lam b (s0 a b))) 0 (map (lam x (f1 x)) xs))` | 14 | `(scanl (lam a (lam b (s0 a (f1 b)))) 0 xs)` | 72153 | True | True | False | 0.000 (DESERT_HARSH) |
| W3-F039-R3 | R3:fs:step_of_f | `(foldl (lam a (lam b (s0 a (f1 b)))) 0 xs)` | 12 | `(foldl (lam a (lam b (s0 a (f1 b)))) 0 xs)` | 549260 | False | True | False | 0.000 (DESERT_HARSH) |
| W3-F041-R3 | R3:fs:post_fold | `(f1 (foldl (lam a (lam b (s1 a b))) 1 xs))` | 23 | `(f1 (foldl (lam a (lam b (s1 a b))) 1 xs))` | 225295 | False | True | False | 0.300 (GOLDILOCKS) |
| W3-F043-R3 | R3:fp:guard_p | `(map (lam x (if (p0 x) (f0 x) x)) xs)` | 16 | `(map (lam x (if (p0 x) (f0 x) x)) xs)` | 505844 | False | True | False | 0.200 (GOLDILOCKS) |
| W3-F047-R4 | R4:fs:scan_of_map | `(scanl (lam a (lam b (s0 a b))) 0 (map (lam x (f0 x)) xs))` | 16 | `(scanl (lam a (lam b (s0 a (f0 b)))) 0 xs)` | 72137 | True | True | False | 0.000 (DESERT_HARSH) |
| W3-F048-R4 | R4:fs:scan_of_map | `(scanl (lam a (lam b (s1 a b))) 0 (map (lam x (f0 x)) xs))` | 18 | `(scanl (lam a (lam b (s1 a (f0 b)))) 0 xs)` | 72821 | True | True | False | 0.000 (DESERT_HARSH) |
| W3-F049-R4 | R4:ff:two_maps+red | `(last (map (lam x (f0 x)) (map (lam x (f1 x)) xs)))` | 16 | `(f0 (f1 (last xs)))` | 165 | True | True | False | 0.500 (GOLDILOCKS) |
