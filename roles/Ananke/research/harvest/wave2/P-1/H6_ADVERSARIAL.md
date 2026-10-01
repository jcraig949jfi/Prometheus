# P-1: recursive adversarial pass on H6 ("search reachability bounds PTE")

Principal, Wave 2, 2026-10-01. DRAFT v1. Inputs: H-PLANT (REPORT, PRINCIPAL_REVIEW), W2-G, W2-A2, and the
principal checks P-1a (light cone) and P-2 (plant specificity). Pending: W2-D (chain instruments, plant
neighbourhood, seeded GA) and W2-J (XOR plants on the uncapped rows).

## 0. The claim as written
ARC3 (7fc642367): "H6: search reachability bounds PTE." The harvest weakened it to "search, not physics"
and then left it undecided for XOR, FLIP and multi-hop.

## 1. Strongest explanation (A): the NULLs are search-limited
- FLIP @ d9cc: a 16-line plant inside C1's own genome space scores .97-.98 (replicated on disjoint seeds).
  The searched cell 6f82f9c7 held .479; its final generation peaked at max_acc .578, contrast .25.
- Multi-hop RELAY @ d9cc: relay_flood scores .97-.98 at d5.
- A1: multi-hop RELAY 1/26 vs one-hop 3/18. Rarer, consistent with a harder search.

## 2. Strongest incompatible explanation (B): the NULLs are construction-limited
The env, the placement, the ruler and the sampling decide most outcomes before search runs.
- 43% of XOR evolve rows (36/83) are light-cone-capped below .60 (W2-G F3; principal-verified). The XOR
  actuator has no upper distance bound (DESIGN s7), so on rings it is out of reach.
- MAJ placement does not honour d. All 19 MAJ SIGNALs are one-hop placements; multi-hop placements went
  0/55 (W2-A2 F3).
- 150/196 RELAY evolve rows only demand one hop (P-1b). "Evolved transport is one hop" is ~77% a
  statement about what was asked.
- "Topology-bound" is hop count: topology->random turns 1 hop into 3, and at d=1 all 4 laws keep SIGNAL
  (W2-G F1).
- Controls forced by construction: zero_comm (COMM_DEPENDENT == SIGNAL).
- relay_flood viability, C1's "physics map", is ~0-5% at decay > 0 vs 17% at decay 0 in A0 (P-2).
  Whether that is physics or this plant's design is under test.

## 3. Attack on A
- A rests on two cells at ONE physics point (d9cc). Selection of that point was not random: it is the
  most-studied point, chosen because a RELAY lineage succeeded there. One success of a plant where search
  failed is an existence proof at one cell, not a bound on PTE.
- Of the three d9cc NULLs H-PLANT cited, two are transfers (W2-G F4). Only ONE FLIP NULL and ZERO
  multi-hop NULLs at d9cc are search outcomes.
- "Search failed" conflates three things:
  - S: the GA never samples the solution;
  - U: it samples it but selection does not keep it;
  - objective misspecification: the GA optimises f = acc + .10*sens_act+ + .02*sens_any, not acc.
  W2-A2 F1 shows the shaped terms dominate selection on NULL cells (NULL champions sit ~80x above random
  genomes on persist/beyond_hop). A NULL cell's champion is a sensitivity maximiser. That is a success of
  search at the wrong objective, not a failure of reachability.

## 4. Attack on B
- Construction explains the capped and placement-forced rows. It cannot explain the uncapped rows: 47
  XOR evolve rows, the 30 light-cone-reachable multi-hop RELAY rows (2/30 competent), and FLIP @ d9cc
  (bound 1.0, plant .97, search .479).
- B's controls argument cuts against C1's POSITIVE labels (COMM_DEPENDENT, CAUSAL_SUPPORT), not against
  the NULLs.

## 5. Third explanation (C): reject the shared assumption
A and B share the assumption that a C1 cell is an independent measurement of "competence at task T under
physics P". The record contradicts this:
- 50 RELAY SIGNAL rows = 17 distinct conditions; 32/50 descend from one A1 cell (W2-G F5).
- Post-A1 waves were targeted at winners (W2-G F7).
- Held worlds share the cell's graph and constants (W2-A2 S1).
- The NULL population mixes capped, transferred, plant-dead, placement-forced and genuinely-unsolved rows.

So at the population level, C1 does not identify H6 at all. Neither "search bounds PTE" nor "physics
bounds PTE" is a C1 result. What C1 plus H-PLANT can support is CELL-LEVEL attributions, each needing an
upper bound (light cone or a derived physics bound) and a lower bound (a plant).

## 6. Implementation evidence neither A nor B considered
- The fitness bonus (search.py:332) changes the objective that "search" is searching. At FLIP @ d9cc the
  plant's shaped fitness is about .97 + bonus, far above the champion's .61, so the objective cannot be
  why the plant was missed. Prediction for W2-D (c): plant f > champion f. If so, FLIP @ d9cc is S
  (reachability) or U, not objective.
- C1's plant-viability lower bound is plant-specific (relay_flood writes S0 only on change, which decay
  erases; flooding meets cap/collision). Wherever C1 called a region "physics-dead" from relay_flood
  failure, the attribution is a lower bound for ONE plant family. P-2 is testing this.

## 7. Distinguishing predictions (per cell; the instruments of W2-D's chain)
| link | test | A predicts | B predicts | C predicts |
|---|---|---|---|---|
| P physics | light-cone / derived bound | bound >= plant acc | bound < threshold on capped rows | mixture by row |
| R representation | plant exists in genome space | yes | (n/a on capped rows) | yes on some uncapped rows only |
| S search | unseeded GA at 1x/10x budget | rises with budget | flat | row-dependent |
| U selection | plant-seeded population retains plant | retained | n/a | retained iff plant f > shaped-champion f |
| V ruler | known plant through C1 labels | SIGNAL | label cheatable (XOR one-flag .763) | mixture |

## 8. Revised statement (v1, to be revised after W2-D / W2-J)
"H6 is not a C1 population result. At the cell level:
- FLIP @ d9cc (one searched cell) is representation-feasible and search-missed (S or U pending);
- XOR is physics-capped on 43% of its evolve rows and undecided elsewhere;
- multi-hop RELAY is plant-feasible at d9cc but was never searched there, and is 2/30 competent across
  the reachable A-wave rows (plant feasibility at those rows: P-1b, running).
Search reachability is FALSIFIABLE per cell: it is refuted at a cell by a physics bound below threshold,
by loss of a seeded plant under selection (U), or by a ruler that cannot register a known solution (V).
It is supported only where an upper bound and a plant bracket the search outcome."

## 9. Attack on the revision
- "Cell-level only" may be too modest. If W2-J finds plants solve most of the 47 uncapped XOR rows and
  P-1b finds relay_flood solves most of the 30 reachable multi-hop rows, then search-limitation is
  general at the population level, conditional on uncapped rows.
- Conversely, if plants fail broadly at uncapped rows, the honest reading is "undecided", not "physics".
  Plant failure is a lower bound only.
OPEN: pending W2-D, W2-J and P-1b.

## 10. v2 revision (after W2-D and P-1b, ~01:10Z)
Section 6's prediction is confirmed: the plant's shaped fitness is 1.05 vs the champion's .50 (W2-D F2).
The objective is not the barrier at FLIP @ d9cc. All of R, P, U and V(full) are excluded there, so the
link is S. Its form is an isolated peak (6% of mutate() offspring retain function) plus an unclimbed
.60 relay basin. That is ONE search seed.

P-1b answers section 9's first branch for multi-hop:
- 21 of 30 light-cone-reachable multi-hop RELAY rows are relay_flood-dead.
- Conditional on a working plant, search succeeds 2/9 multi-hop vs 40/99 one-hop (not significant;
  5 distinct conditions).
- "Multi-hop is rare" is mostly a fact about the upper/lower bracket (plant viability under decay, caps,
  async), not evidence of search limitation.

New element neither A nor B had: the SELECTOR CEILING (W2-D F7). With 8 train worlds and 96 genomes,
the max-of-96 chance accuracy is ~.55-.58. Competence below that is invisible to selection. Hence a
fourth explanation (D): for many uncapped NULLs, the search was BLIND in the band where the stepping
stones live (relay .60 for FLIP). That is neither "unreachable" nor "physics". It is a resolution limit
of the objective's estimator (M = 8), a design parameter.

Distinguishing prediction for D vs S-needle: raising M (train worlds) to 32 at fixed budget should raise
FLIP success from the .60 basin if D holds, and should not if the needle alone binds. W2-D Q1 (seed
relay_flood) and an M-sweep are the decisive cheap tests. Both are searches; NOT authorized in this
harvest.

v2 statement:
"H6 holds at exactly one cell (FLIP @ d9cc) with the full link chain, and there it is S under a blind
selector (M = 8). Across C1, NULLs are mostly bracketed by construction: light cone (XOR 43%, FLIP 29%),
placement (MAJ), and plant viability (multi-hop). The residual uncapped, plant-viable NULLs are where
search limitation is possible. Their placement is pending W2-J (XOR), W2-L (FLIP) and W2-M (MAJ). A
family-level H6 claim requires >= 3 cells per family meeting W2-D's F-R/P, F-U and F-V, plus F-S
(response to M/budget/seeding)."
