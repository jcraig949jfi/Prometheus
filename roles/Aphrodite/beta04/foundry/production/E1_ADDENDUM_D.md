# E1 v2 PRODUCTION: Addendum D evaluation

Frozen v2 code and config: generator `c199f0ae`, qualification `22d2c387`, regression `439e168c`.

## E1 outcome

**WORLD_DEMAND_NOT_QUALIFIED (gate PASS 5/12 worlds; 2 mechanism-kind pairings among admitted R3/R4)**

* Per-world gate (>= 1 admitted R2 AND >= 1 admitted R3): **5 / 12** worlds pass.
* Pooled rule 7: mechanism-kind pairings among admitted R3/R4, after merging and caps: **2** (fp, fs); required >= 3.
* Admitted by rung (pooled): {'R2': 38, 'R3': 8, 'R4': 7}. R5 admitted: 0.
* Hindsight-regression diagnostic (descriptive, NOT a gate): it solves **0** of 53 admitted families (0 timeouts).

## Per world

| idx | world | mechanisms (unfilled) | admitted by rung | gate |
|---|---|---|---|---|
| 0 | Wc025415a | f0, f1, p0, s0, s1 (-) | {'R2': 1, 'R4': 2} | FAIL |
| 1 | W2bdef02f | f0, f1, p0, s0, s1 (-) | {'R2': 5, 'R3': 1, 'R4': 2} | PASS |
| 2 | W09efdf93 | f0, f1, p0, s0, s1 (-) | {'R2': 3} | FAIL |
| 3 | Wd1490fbb | f0, f1, p0, s0, s1 (-) | {'R2': 3} | FAIL |
| 4 | Wb49b6a5f | f0, f1, p0, s0, s1 (-) | {'R2': 2, 'R4': 2} | FAIL |
| 5 | W483b8c31 | f0, f1, p0, s0, s1 (-) | {'R2': 3, 'R3': 2} | PASS |
| 6 | W0321d83c | f0, f1, p0, s0, s1 (-) | {'R2': 2, 'R3': 1} | PASS |
| 7 | W3a22e2ee | f0, f1, p0, s0, s1 (-) | {'R2': 4} | FAIL |
| 8 | W8f6a223e | f1, p0, s0, s1 (f0) | {'R2': 2} | FAIL |
| 9 | W480ffd54 | f0, f1, p0, s0, s1 (-) | {'R2': 5, 'R3': 2, 'R4': 1} | PASS |
| 10 | W38fc86d7 | f0, f1, p0, s0, s1 (-) | {'R2': 4} | FAIL |
| 11 | W6eb945cc | f0, f1, p0, s0, s1 (-) | {'R2': 4, 'R3': 2} | PASS |

## Pooled rejection histogram (gen-screen rejects included)

| rung | class counts |
|---|---|
| R0 | DUPLICATE 2; TRIVIAL_BY_LIBRARY 11; TRIVIAL_BY_REACTIVE 45; TRIVIAL_BY_REGRESSION 14; TRIVIAL_BY_SMALL_SEARCH 2 |
| R1 | DEGENERATE 8; DUPLICATE 36; NEAR_TRIVIAL 5; QUALIFIED 93; TRIVIAL_BY_LIBRARY 1; TRIVIAL_BY_REACTIVE 8; TRIVIAL_BY_SMALL_SEARCH 11 |
| R2 | DEGENERATE 19; DUPLICATE 7; FAIL_PRONE 4; KNOWN_POSITIVE_FAIL:DEV_UNDERDETERMINED 3; KNOWN_POSITIVE_FAIL:HORIZON 42; MOTIF_CAP 4; NEAR_TRIVIAL 8; QUALIFIED 38; SYNTHETIC_DEPTH 4; TRIVIAL_BY_BASE_1E6 4; TRIVIAL_BY_LIBRARY 2; TRIVIAL_BY_REACTIVE 4; TRIVIAL_BY_REGRESSION 11 |
| R3 | CHAIN_C_FAIL:f0 8; CHAIN_C_FAIL:f0+f1 1; CHAIN_C_FAIL:f0+s0 1; CHAIN_C_FAIL:f0+s1 3; CHAIN_C_FAIL:f1 21; CHAIN_C_FAIL:f1+s0 3; CHAIN_C_FAIL:f1+s1 13; CHAIN_C_FAIL:p0 1; CHAIN_C_FAIL:p0+s1 2; CHAIN_C_FAIL:s0 28; CHAIN_C_FAIL:s0+s1 5; CHAIN_C_FAIL:s1 26; CHAIN_D_FAIL:HORIZON 7; CHAIN_D_FAIL:NOT_FOUND 2; CHAIN_D_FAIL:TRIBUNAL 1; DEGENERATE 6; DUPLICATE 17; FAIL_PRONE 11; NEAR_TRIVIAL 4; QUALIFIED 8; SYNTHETIC_DEPTH 1; TRIVIAL_BY_BASE_1E6 2; TRIVIAL_BY_LOOKUP 1; TRIVIAL_BY_REGRESSION 6 |
| R4 | CHAIN_C_FAIL:f0 9; CHAIN_C_FAIL:f1 10; CHAIN_C_FAIL:f1+p0 4; CHAIN_C_FAIL:f1+s0 2; CHAIN_C_FAIL:f1+s1 4; CHAIN_C_FAIL:p0 2; CHAIN_C_FAIL:s0 5; CHAIN_C_FAIL:s1 16; CHAIN_D_FAIL:HORIZON 3; DEGENERATE 2; DUPLICATE 4; FAIL_PRONE 16; QUALIFIED 7; SYNTHETIC_DEPTH 4; TRIVIAL_BY_LIBRARY 1; TRIVIAL_BY_REACTIVE 2; TRIVIAL_BY_REGRESSION 3 |
| R5 | CHAIN_C_FAIL:f0 10; CHAIN_C_FAIL:f0+s0 1; CHAIN_C_FAIL:f0+s1 2; CHAIN_C_FAIL:f1 18; CHAIN_C_FAIL:f1+s0 2; CHAIN_C_FAIL:f1+s1 13; CHAIN_C_FAIL:p0 2; CHAIN_C_FAIL:s0 15; CHAIN_C_FAIL:s0+s1 3; CHAIN_C_FAIL:s1 12; CHAIN_D_FAIL:HORIZON 8; DEGENERATE 13; DUPLICATE 13; FAIL_PRONE 1; NEAR_TRIVIAL 2; SYNTHETIC_DEPTH 2; TRIVIAL_BY_BASE_1E6 1; TRIVIAL_BY_REACTIVE 2; TRIVIAL_BY_REGRESSION 3 |

## Admitted families: headroom and diagnostic

| world | family | rung | kind pair | promoted witness | route solution | CRN rank | order-free rank | base 1e6 dev-consistent | hindsight regression |
|---|---|---|---|---|---|---|---|---|---|
| Wc025415a | Wc025415a-F021-R2 | R2 | - | `(foldl (lam a (lam b (add b a))) 1 (map (lam x (f0 x)) xs))` | `(sum (scanl (lam a (lam b (f0 b))) 1 xs))` | 9841 | 27213 (est.) | 0 | no |
| Wc025415a | Wc025415a-F041-R4 | R4 | fp | `(map (lam x (if (p0 x) (f1 x) x)) xs)` | `(map (lam x (if (q1 x) (q0 x) x)) xs)` | 273050 | 288448 (est.) | 0 | no |
| Wc025415a | Wc025415a-F044-R4 | R4 | fp | `(filter (lam x (p0 x)) (map (lam x (f1 x)) xs))` | `(filter (lam x (q1 x)) (map (lam x (q0 x)) xs))` | 29413 | 31793 (est.) | 0 | no |
| W2bdef02f | W2bdef02f-F022-R2 | R2 | - | `(map (lam x (if (gt 1 x) (f0 x) x)) xs)` | `(map (lam x (max (scanl (lam a (lam b x)) (f0 x) xs))) xs)` | 368479 | 495337 (est.) | 0 | no |
| W2bdef02f | W2bdef02f-F024-R2 | R2 | - | `(mul (sum (filter (lam x (p0 x)) xs)) (sum (filter (lam x (p0 x)) xs)))` | `(pow (sum (filter (lam x (p0 x)) xs)) 2)` | 410414 | 338651 (est.) | 0 | no |
| W2bdef02f | W2bdef02f-F026-R2 | R2 | - | `(sub 0 (foldl (lam a (lam b (s1 a b))) 0 xs))` | `(neg (foldl (lam a (lam b (s1 a b))) 0 xs))` | 90142 | 338651 (est.) | 0 | no |
| W2bdef02f | W2bdef02f-F027-R2 | R2 | - | `(foldl (lam a (lam b (sub a b))) 0 (map (lam x (f0 x)) xs))` | `(neg (sum (map (lam x (f0 x)) xs)))` | 4853 | 28916 (est.) | 0 | no |
| W2bdef02f | W2bdef02f-F031-R2 | R2 | - | `(foldl (lam a (lam b (add a b))) 0 (scanl (lam a (lam b (s1 a b))) 0 xs))` | `(sum (scanl (lam a (lam b (s1 a b))) 0 xs))` | 114686 | 338651 (est.) | 0 | no |
| W2bdef02f | W2bdef02f-F042-R3 | R3 | fp | `(map (lam x (f0 x)) (filter (lam x (p0 x)) xs))` | `(map (lam x (q0 x)) (filter (lam x (q1 x)) xs))` | 24088 | 35491 (est.) | 0 | no |
| W2bdef02f | W2bdef02f-F048-R4 | R4 | fs | `(f0 (foldl (lam a (lam b (s0 a b))) 1 xs))` | `(q0 (foldl (lam a (lam b (q2 a b))) 1 xs))` | 114036 | 196839 (est.) | 0 | no |
| W2bdef02f | W2bdef02f-F051-R4 | R4 | fs | `(scanl (lam a (lam b (s0 a b))) 1 (map (lam x (f0 x)) xs))` | `(scanl (lam a (lam b (q2 a (q0 b)))) 1 xs)` | 50929 | 35491 (est.) | 0 | no |
| W09efdf93 | W09efdf93-F018-R2 | R2 | - | `(mul (head (map (lam x (f0 x)) xs)) (head (map (lam x (f0 x)) xs)))` | `(pow (f0 (head xs)) 2)` | 3750 | 3503 (est.) | 0 | no |
| W09efdf93 | W09efdf93-F024-R2 | R2 | - | `(foldl (lam a (lam b (add a b))) 0 (map (lam x (f1 x)) xs))` | `(sum (map (lam x (f1 x)) xs))` | 1299 | 3503 (est.) | 0 | no |
| W09efdf93 | W09efdf93-F029-R2 | R2 | - | `(map (lam x (f1 x)) (filter (lam x (lt 2 x)) xs))` | `(map (lam x (f1 x)) (filter (lam x (lt 2 x)) xs))` | 320345 | 491605 (est.) | 0 | no |
| Wd1490fbb | Wd1490fbb-F019-R2 | R2 | - | `(foldl (lam a (lam b (add a b))) 0 (map (lam x (f0 x)) xs))` | `(sum (map (lam x (f0 x)) xs))` | 1289 | 3472 (est.) | 0 | no |
| Wd1490fbb | Wd1490fbb-F021-R2 | R2 | - | `(mul (sum (filter (lam x (p0 x)) xs)) (sum (filter (lam x (p0 x)) xs)))` | `(pow (sum (filter (lam x (p0 x)) xs)) 2)` | 400874 | 336104 (est.) | 0 | no |
| Wd1490fbb | Wd1490fbb-F022-R2 | R2 | - | `(foldl (lam a (lam b (sub a b))) 0 (scanl (lam a (lam b (s0 a b))) 0 xs))` | `(neg (sum (scanl (lam a (lam b (s0 a b))) 0 xs)))` | 533359 | 3542000 (est.) | 0 | no |
| Wb49b6a5f | Wb49b6a5f-F021-R2 | R2 | - | `(foldl (lam a (lam b (add b a))) 0 (scanl (lam a (lam b (s1 a b))) 0 xs))` | `(sum (scanl (lam a (lam b (s1 a b))) 0 xs))` | 119130 | 352145 (est.) | 0 | no |
| Wb49b6a5f | Wb49b6a5f-F024-R2 | R2 | - | `(neg (len (filter (lam x (p0 x)) xs)))` | `(neg (len (filter (lam x (p0 x)) xs)))` | 4855 | 30434 (est.) | 0 | no |
| Wb49b6a5f | Wb49b6a5f-F052-R4 | R4 | fp | `(map (lam x (if (p0 x) (f1 x) x)) xs)` | `(map (lam x (if (q1 x) (q0 x) x)) xs)` | 350078 | 362075 (est.) | 0 | no |
| Wb49b6a5f | Wb49b6a5f-F055-R4 | R4 | fp | `(map (lam x (f1 x)) (filter (lam x (p0 x)) xs))` | `(map (lam x (q0 x)) (filter (lam x (q1 x)) xs))` | 26446 | 38276 (est.) | 0 | no |
| W483b8c31 | W483b8c31-F022-R2 | R2 | - | `(filter (lam x (p0 x)) (map (lam x (gcd x x)) xs))` | `(filter (lam x (p0 x)) (map (lam x (gcd x x)) xs))` | 498944 | 508565 (est.) | 0 | no |
| W483b8c31 | W483b8c31-F026-R2 | R2 | - | `(foldl (lam a (lam b (mul b a))) 1 (map (lam x (f1 x)) xs))` | `(foldl (lam a (lam b (mul a (f1 b)))) 1 xs)` | 532052 | 349404 (est.) | 0 | no |
| W483b8c31 | W483b8c31-F030-R2 | R2 | - | `(map (lam x (f0 (f0 x))) xs)` | `(map (lam x (f0 (f0 x))) xs)` | 412 | 629 (est.) | 0 | no |
| W483b8c31 | W483b8c31-F045-R3 | R3 | fp | `(map (lam x (if (p0 x) (f0 x) x)) xs)` | `(map (lam x (if (q2 x) (q0 x) x)) xs)` | 361926 | 386837 (est.) | 0 | no |
| W483b8c31 | W483b8c31-F046-R3 | R3 | fp | `(map (lam x (f1 x)) (filter (lam x (p0 x)) xs))` | `(map (lam x (q1 x)) (filter (lam x (q2 x)) xs))` | 27949 | 39197 (est.) | 0 | no |
| W0321d83c | W0321d83c-F024-R2 | R2 | - | `(foldl (lam a (lam b (s1 a b))) 1 (rev xs))` | `(foldl (lam a (lam b (s1 a b))) 1 (rev xs))` | 539443 | 351982 (est.) | 0 | no |
| W0321d83c | W0321d83c-F026-R2 | R2 | - | `(max (take 3 (map (lam x (f1 x)) xs)))` | `(max (take 3 (map (lam x (f1 x)) xs)))` | 120223 | 351982 (est.) | 0 | no |
| W0321d83c | W0321d83c-F040-R3 | R3 | fp | `(map (lam x (f0 x)) (filter (lam x (p0 x)) xs))` | `(map (lam x (q0 x)) (filter (lam x (q1 x)) xs))` | 22524 | 31773 (est.) | 0 | no |
| W3a22e2ee | W3a22e2ee-F024-R2 | R2 | - | `(max (map (lam x (neg x)) (map (lam x (f0 x)) xs)))` | `(neg (min (map (lam x (f0 x)) xs)))` | 4796 | 27503 (est.) | 0 | no |
| W3a22e2ee | W3a22e2ee-F025-R2 | R2 | - | `(max (map (lam x (f1 (f1 x))) xs))` | `(max (map (lam x (f1 (f1 x))) xs))` | 10282 | 27503 (est.) | 0 | no |
| W3a22e2ee | W3a22e2ee-F028-R2 | R2 | - | `(foldl (lam a (lam b (add a b))) 0 (scanl (lam a (lam b (s1 a b))) 1 xs))` | `(sum (scanl (lam a (lam b (s1 a b))) 1 xs))` | 111233 | 328632 (est.) | 0 | no |
| W3a22e2ee | W3a22e2ee-F031-R2 | R2 | - | `(mul 2 (len (filter (lam x (p0 x)) xs)))` | `(sum (map (lam x 2) (filter (lam x (p0 x)) xs)))` | 107783 | 328632 (est.) | 8 | no |
| W8f6a223e | W8f6a223e-F017-R2 | R2 | - | `(mul (len (filter (lam x (p0 x)) xs)) (len (filter (lam x (p0 x)) xs)))` | `(pow (len (filter (lam x (p0 x)) xs)) 2)` | 305530 | 269436 (est.) | 0 | no |
| W8f6a223e | W8f6a223e-F020-R2 | R2 | - | `(map (lam x (f1 (f1 x))) xs)` | `(map (lam x (f1 (f1 x))) xs)` | 390 | 617 (est.) | 0 | no |
| W480ffd54 | W480ffd54-F023-R2 | R2 | - | `(mul (len (filter (lam x (p0 x)) xs)) (len (filter (lam x (p0 x)) xs)))` | `(pow (len (filter (lam x (p0 x)) xs)) 2)` | 382349 | 324454 (est.) | 0 | no |
| W480ffd54 | W480ffd54-F024-R2 | R2 | - | `(foldl (lam a (lam b (sub a b))) 0 (scanl (lam a (lam b (s0 a b))) 0 xs))` | `(neg (sum (scanl (lam a (lam b (s0 a b))) 0 xs)))` | 508498 | 3371705 (est.) | 0 | no |
| W480ffd54 | W480ffd54-F026-R2 | R2 | - | `(foldl (lam a (lam b (add a b))) 0 (map (lam x (f0 x)) xs))` | `(sum (map (lam x (f0 x)) xs))` | 1250 | 3375 (est.) | 0 | no |
| W480ffd54 | W480ffd54-F028-R2 | R2 | - | `(foldl (lam a (lam b (add b a))) 1 (filter (lam x (p0 x)) xs))` | `(add 1 (sum (filter (lam x (p0 x)) xs)))` | 207709 | 324454 (est.) | 0 | no |
| W480ffd54 | W480ffd54-F031-R2 | R2 | - | `(drop 3 (map (lam x (f0 x)) xs))` | `(drop 3 (map (lam x (f0 x)) xs))` | 2186 | 3977 (est.) | 0 | no |
| W480ffd54 | W480ffd54-F039-R3 | R3 | fp | `(filter (lam x (p0 x)) (map (lam x (f0 x)) xs))` | `(filter (lam x (q2 x)) (map (lam x (q0 x)) xs))` | 34269 | 36511 (est.) | 0 | no |
| W480ffd54 | W480ffd54-F046-R3 | R3 | fp | `(map (lam x (f0 x)) (filter (lam x (p0 x)) xs))` | `(map (lam x (q0 x)) (filter (lam x (q2 x)) xs))` | 25351 | 36511 (est.) | 0 | no |
| W480ffd54 | W480ffd54-F055-R4 | R4 | fp | `(map (lam x (f1 x)) (filter (lam x (p0 x)) xs))` | `(map (lam x (q1 x)) (filter (lam x (q2 x)) xs))` | 25433 | 36511 (est.) | 0 | no |
| W38fc86d7 | W38fc86d7-F025-R2 | R2 | - | `(map (lam x (add x 1)) (map (lam x (f1 x)) xs))` | `(map (lam x (add 1 (f1 x))) xs)` | 4026 | 4362 (est.) | 0 | no |
| W38fc86d7 | W38fc86d7-F029-R2 | R2 | - | `(sum (filter (lam x (not (gt x 1))) (map (lam x (f0 x)) xs)))` | `(len (filter (lam x (eq 1 (f0 x))) xs))` | 96447 | 346052 (est.) | 0 | no |
| W38fc86d7 | W38fc86d7-F031-R2 | R2 | - | `(add (sum (filter (lam x (p0 x)) xs)) 3)` | `(add 3 (sum (filter (lam x (p0 x)) xs)))` | 229691 | 346052 (est.) | 0 | no |
| W38fc86d7 | W38fc86d7-F035-R2 | R2 | - | `(map (lam x (if (lt x 3) (f1 x) x)) xs)` | `(map (lam x (max (scanl (lam a (lam b x)) (f1 x) xs))) xs)` | 379890 | 510665 (est.) | 0 | no |
| W6eb945cc | W6eb945cc-F023-R2 | R2 | - | `(sub 0 (foldl (lam a (lam b (s1 a b))) 1 xs))` | `(neg (foldl (lam a (lam b (s1 a b))) 1 xs))` | 90993 | 341960 (est.) | 0 | no |
| W6eb945cc | W6eb945cc-F024-R2 | R2 | - | `(div (sum (map (lam x (f0 x)) xs)) 3)` | `(div (sum (map (lam x (f0 x)) xs)) 3)` | 314813 | 341960 (est.) | 0 | no |
| W6eb945cc | W6eb945cc-F025-R2 | R2 | - | `(gcd (last (map (lam x (f1 x)) xs)) (last (map (lam x (f1 x)) xs)))` | `(gcd 0 (f1 (last xs)))` | 3489 | 3549 (est.) | 0 | no |
| W6eb945cc | W6eb945cc-F028-R2 | R2 | - | `(foldl (lam a (lam b (s1 a b))) 0 (rev xs))` | `(foldl (lam a (lam b (s1 a b))) 0 (rev xs))` | 517885 | 341960 (est.) | 0 | no |
| W6eb945cc | W6eb945cc-F033-R3 | R3 | fs | `(scanl (lam a (lam b (s0 a b))) 1 (map (lam x (f0 x)) xs))` | `(scanl (lam a (lam b (q2 a (q0 b)))) 1 xs)` | 53685 | 37162 (est.) | 0 | no |
| W6eb945cc | W6eb945cc-F047-R3 | R3 | fs | `(f0 (foldl (lam a (lam b (s0 a b))) 0 xs))` | `(q0 (foldl (lam a (lam b (q2 a b))) 0 xs))` | 118789 | 205046 (est.) | 0 | no |
