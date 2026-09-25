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

## C2 RESULT (code 7b14ec99e, 2026-09-23T15:23Z; run dir c2_7b14ec99e)
G0 G1 G2 G4 G7 PASS; G5/G6 on D not run (spent). Ledger: c5cd50beb1 (v4) FAILED round 0 by the
location gate (regs -0.168; confident contradictions 0/106), revised to a079ad5ec1 (v4):
    log(Q - C K) <= -0.1577  AND  C - G exp(-N) <= -0.1022
SURVIVED round 1 (0/107 confident contradictions; location offsets ca -.006 regs -.015 ring -.015),
FROZEN a64cc593024be2e4...
Selection-vs-gate disagreement (instrument note): selection (6 bases, 800 episodes) measured the
round-0 law at regs 0.005; the gate (8 other bases, 1600 episodes) measured -0.168. Selection-time
location estimates are noisy; the gate is what caught it.
C2a HELD. C2b HELD (ceiling C <= G exp(-N) - 0.102; task economics: G exp(-N) - 0.10).
F adjudication follows (c1f runner: law A = C0b f852d782cb, law B = C2 a079ad5ec1).

## F ADJUDICATION (2026-09-23T15:24Z; F_adjudication.json; predictions receipted before F ran:
## A pred_hash 1a016c6a..., B pred_hash c3c17111..., G6F presc_hash f41667b4...)
Sealed F (clone, 240 worlds, base rate 0.192), first execution:
  law A (C0b f852d782cb, v3): BA 0.930, acc 0.954, Brier 0.045 (clim 0.155); 5-NN 0.841 -> G5F PASS
  law B (C2  a079ad5ec1, v4): BA 0.955, acc 0.954, Brier 0.042;               5-NN 0.833 -> G5F PASS
  H1 (BA B > BA A): HELD AS SCORED, NOT SUPPORTED STATISTICALLY: discordant worlds 10 (A wrong, B right)
     vs 10 (B wrong, A right), sign test p = 1.0; the BA gap is class weighting (A 6 FP / 5 FN,
     B 9 FP / 2 FN).
  Error SHAPE differs: A's unique errors include gross misses where v3's cost is badly wrong for a
     growing or dying clone (margins -0.57, -0.43 where the v4 expected cost is 3-4x the v3 cost;
     declining clones missed as QUIET); B's unique errors are all near the threshold (margins
     0.056-0.136, logger-floor region).
  G6F (law B, fresh F worlds, 398 candidates / 33 eligible / 12 scored): direction 11/12,
     precision 0.201 log2 vs best constant (f=4) 0.708 -> PASS.
Precommitments: C2c HELD, C2d HELD as scored (not significant), C2e HELD (law A passed; I gave 0.35).
CONCLUDED (scope): with location-aware selection the engine produced a law whose cost ceiling
matches the task economics and whose boundary sits within 0.015 log2 per visible family; on a third
sealed substrate designed so that v3 and v4 disagree, both frozen laws pass, the v4 law removes the
gross (coordinate) errors and keeps boundary noise, and its accuracy advantage is NOT significant.
