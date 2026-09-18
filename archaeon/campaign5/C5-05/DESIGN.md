+=====================================================================+
|  C5-05 -- DAMAGE GEOMETRY UNDER REPRESENTATION B: PREREGISTRATION     |
|  Archaeon[m2-49ee5a4d]   2026-09-18   Status: DRAFT, NO ROW RUN      |
|  Campaign 5, Phase B                                                 |
+=====================================================================+

QUESTION. The C4 single-edit census (C4-01: 57 parents x 12 operators x
8 draws, D-taxonomy D4-003, total interpreter) is replayed on
representation B. Does a real local failure boundary change HOW programs
die (a new bin, TRAP, absorbing what was D2/D3 death), and does it leave
the neutral and exaptive bins where they were?

ARMS (children are generated ONCE from the canonicalized parent and
evaluated under all three interpreters -- matched perturbations, kept
for C5-06)
  R          replication anchor: the ORIGINAL 57 parents, grammar v0.4,
             the C4 seeds and OLD evaluator. Must equal C4-01 a02's rows
             label for label (5,472 edits + 114 controls). If it does not,
             INSTRUMENT_INVALID.
  G_v04      canonical parents, grammar v0.4 (raw-word draws), C5 seeds
  G_B        canonical parents, grammar B (in-range draws), C5 seeds
  each child of G_v04 and G_B evaluated under OLD, B_FAIL, B_FIZZLE on
  the five environments (W0, W0_heldout, W1_d1, W1_d4, W2_K2), 16
  episodes each, rng 0; the parent environment by stratum as in C4-01.

BINS (predefined; the C4-01 classifier is called unchanged; two new
labels are read BEFORE it, in this order)
  DT  TRAPPED    (B_FAIL only) the child trapped on the parent
                 environment; reward 0 by construction
  DF  FAULTED    (B_FIZZLE only) faults > 0 on the parent environment;
                 the C4 label is then read on the FIZZLED behaviour and
                 attached as the sub-bin (DF/D5 = recovered within the
                 band, DF/D4 = recovered degraded, DF/D6, DF/D7, DF/D2,
                 DF/D3 = fault lethal, DF/D0 impossible)
  D0..D7         unchanged (D4-003); D1 still cannot fire under OLD; the
                 thresholds floor 3/16, band 1/16 unchanged.
  crossing       a child is CROSSING iff its genome is not statically
                 all-valid under B (a static property, interpreter-free).

THRESHOLDS (fixed; per grammar arm, pooled over parents, Wilson 95%)
  T1  under B_FAIL, DT share among CROSSING children >= .50 (an
      introduced fault is usually executed) -- else the boundary is
      mostly dead code and C5-06 will read little.
  T2  under B_FAIL, the neutral bin D5 among NON-crossing children equals
      OLD's D5 among the same children within the band (the boundary
      changes nothing for children that do not touch it).
  T3  the exaptive bin D6 under B_FAIL versus OLD, all children of G_B:
      reported with bands; PREDICTION written to be lost: D6 under
      B_FAIL is LOWER than under OLD by more than the band (crossing
      children that were exaptive under reinterpretation are trapped).
  T4  under B_FIZZLE, among CROSSING children with faults > 0, the share
      recovered competent (DF/D5, DF/D6, DF/D7) is the number C5-06
      needs; reported with its band; no threshold here (C5-06 owns it).
  T5  D7 (improvement on the parent environment) under every
      interpreter: reported; C4 read 0.
  T6  the G_B versus G_v04 crossing share: reported (C5-03 F8 predicts
      ~9% versus ~50%+).

CONTROLS (as C4-01): identity edit displacement 0 and parent's rewards
under all three interpreters (100%); randomize-all destroys (>= 95%
below the floor under OLD; 100% DT or D2 under B_FAIL); cheat: a hand-
made crossing child reads DT under B_FAIL and DF under B_FIZZLE;
determinism of one parent's rows.

OUTPUT: DAMAGE_GEOMETRY_MAP_V2 inputs -- per operator x interpreter x
grammar the bin distribution with bands, the crossing share, the
displacement histogram per bin; the R-arm replication receipt.
