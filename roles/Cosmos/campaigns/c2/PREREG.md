# C2 -- location-aware law selection -- PREREGISTRATION

Written 2026-09-23 ~14:25Z, before any C2 observation. F (sealed 7c9e0d58f, sha256
5e0064901277ef9e48571906dab60f998ad924b16a46bdb316d0db46bc504946) remains unexecuted.

## 0. The defect C2 answers
In C0b and C1, the law chosen by LOLO accuracy among near-tied candidates had a mislocated upper
(cost-ceiling) boundary: C0b +/- .15 log2 per family, C1 -.37 to -.55. LOLO balanced accuracy is
nearly flat across candidates whose boundaries differ by 30% in cost.

## 1. Procedure (config c2; everything else as c1: seed 20260929, random main 80/family, 10 cost lines
## per family kept for mining, adversary 48/family/round + location gate 0.10 log2, up to 3 rounds)
Selection (initial and every revision): candidates = the top-ranked structures of BOTH the v3 and v4
searches whose LOLO score is within 0.03 of that map's best and which pass the worst-fold gate (at
most 6 per map). Each candidate is refitted on all rows; the location attack (6 confident-PAYS
bases per family, 33-point ladder, 800 episodes, a selection rng distinct from the gate's) measures
its per-family upper-flip offsets; the chosen law minimises the worst family |mean offset|
(INDETERMINATE families count as 0.5 log2). The permutation null of each map's search is reported;
a law is CANDIDATE only if its map's search passed the null (p <= 0.05).
Declared weakness: selection and the location gate use the same criterion on the same visible
families (different bases and seeds); the gate is therefore NOT independent of selection. The only
independent test is sealed F.

## 2. F adjudication (if a C2 law survives): G5F for the C2 law AND for the C0b law (A), both
## receipted before any F world runs; H1: BA(C2 law on F) > BA(A on F); G6F for the C2 law.
Thresholds as c1/PREREG.md s2.

## 3. Precommitments
C2a  A C2 law survives (confident + location gate) within 3 rounds.        0.5
C2b  The C2 law's ceiling atom is multiplicative in exp(-N) (G exp(-N) - C form or equivalent).  0.6
C2c  G5F passes for the C2 law.                                            0.55
C2d  H1 holds.                                                             0.55
C2e  G5F passes for law A.                                                 0.35

## Pre-run disclosure
runtest --config c2 (quick) 20260923T142056Z PASS but did NOT exercise selection (5 permutations
cannot pass the null, so no candidate reached select); selection is exercised by
tests/test_select.py (slow): a well-located G exp(-N) - C ceiling is preferred over a C-only ceiling
with a HIGHER LOLO score (0.89 vs 0.90). Gate verdicts only were displayed.
