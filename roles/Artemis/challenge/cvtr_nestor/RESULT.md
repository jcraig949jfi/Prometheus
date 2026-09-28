# RESULT -- CVT-R on Nestor's three genome sets (comms #802)

Artemis, 2026-09-28. Prereg PREREG_CVTR_NESTOR.md committed 77bc0dbce
BEFORE this run; no amendment. Inputs: origin/main b5b77af8c (git
archive). 140 rows / 138 distinct genomes, 161 CPU-s, 81 s wall.
Unscorable: 0. Environment gate for (b): 100/100 genomes reproduced
Nestor's recorded rate_full exactly with Nestor's seeds.

## Per set (CVT-R accept = accept on either side)

| set | n | P-11 fresh-certified | CVT-2 accept | CVT-R accept | rate (Wilson 95%) |
|---|---|---|---|---|---|
| (a) all donors | 32 | 28 | 27 | 23 | 0.72 (0.55-0.84) |
| (a) x_p2_bridge | 16 | 12 | 14 | 12 | 0.75 (0.51-0.90) |
| (a) c_zero_specific | 16 | 16 | 13 | 11 | 0.69 (0.44-0.86) |
| (b) q1 sample | 100 | 95 | 91 | 83 | 0.83 (0.74-0.89) |
| (b) DENSE only | 96 | 92 | 87 | 80 | 0.83 (0.75-0.89) |
| (c) 16000006 epoch-700 | 8 | 8 | 8 | 8 | 1.00 (0.68-1.00) |

## P-11 certified (fresh) but CVT-R rejects: 19 genomes

(a) x_p2_bridge 1, 8; c_zero_specific 2, 11, 12, 13, 14.
(b) q1_competent 2, 7, 13, 19, 36, 54, 59, 64, 84, 86, 88, 94.
Shape of failure: 11 of 19 also fail CVT-2 -- parental byte changes
appear in the first copy (CVT-1 accepts; e.g. x_p2_bridge 1, side 1:
169 classes) but are NOT re-transmitted by that copy in generation 2:
the child is built but does not itself carry the variation forward.
8 of 19 pass CVT-2 and fail only CVT-R's recurrence clause.
Recorded-competent but CVT-R rejects (Nestor's recorded status, the
literal reading of the request): 26 genomes, listed in SUMMARY.json.
One genome (c_zero_specific 4) is accepted by CVT-R only on the side
where P-11 did not certify it.

## What this says and does not say

- Nestor's one recurring North-Star candidate lineage (c) passes: all 8
  epoch-700 genomes are CVT-R accepted, including vid 27200, which the
  forensic file marks FR False.
- Most P-11-competent genomes in Nestor's corpora carry heritable
  variation (83% of the q1 sample), consistent with Nestor's DOM screen
  finding no painters. But about 1 in 6 (b) and about 1 in 4 (a) do not
  pass CVT-R, and most of those fail at generation 2, not by painting.
  "Competent" and "heritable" differ on a sizeable minority, so any claim
  that uses a specific donor from (a) as a heredity carrier should check
  it against the list above.
- CVT-R accept certifies that single-byte parental variation is
  transmitted and re-transmitted in the pair assay at copy rate 0. It
  does not certify a lineage's heredity claim in the evolving world.
