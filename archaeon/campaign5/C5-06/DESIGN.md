+=====================================================================+
|  C5-06 -- LOCAL FAILURE VERSUS LOCAL RECOVERY: PREREGISTRATION        |
|  Archaeon[m2-49ee5a4d]   2026-09-18   Status: DRAFT, NO ROW RUN      |
|  Campaign 5, Phase B (written while C5-05 runs, before it reports)   |
+=====================================================================+

QUESTION. When a single edit carries a program across the boundary and
the fault is executed, does the boundary merely change how the program
dies (FAIL: trap; OLD: silent reinterpretation), or does skipping the
fault (FIZZLE) preserve function that reinterpretation would have lost?
A "real local recovery event" is defined here, before any row is read.

INPUT. C5-05's attempt of record: every child that is CROSSING (static)
with faults > 0 under B_FIZZLE (the fault is executed on the parent
environment), with its three matched readings (OLD, B_FAIL, B_FIZZLE)
of the SAME child, both grammar arms; parents that are degenerate on
their environment (no answer or one constant answer) are excluded --
they have no function to recover.

MATCHED CLASSES (from the C5-05 readings; competent = D5, D6 or D7)
  RECOVERY    FIZZLE competent AND OLD not competent (D2/D3/D4): the
              boundary kept function that reinterpretation lost
  BOTH_LIVE   FIZZLE competent AND OLD competent
  INSULATION_LOSS  OLD competent AND FIZZLE not competent: skipping cost
              function that reinterpretation preserved
  BOTH_DIE    neither competent
  (B_FAIL reads DT on all of them by construction: reported as a check)

NEW MEASUREMENT (not in C5-05): every RECOVERY and INSULATION_LOSS
child is re-evaluated under FIZZLE and OLD on the parent environment's
HELD-OUT family (16 episodes, index 2) with rng seeds 1, 2, 3; the class
is REPLICATED iff it reads the same way in >= 2 of 3 replicates.

THE GATE FOR C5-07 (fixed):
  real recovery exists iff REPLICATED RECOVERY events >= 10 pooled over
  both grammar arms AND the Wilson lower bound of the replicated
  recovery share among executed-crossing children > .01.
  If not: C5-07 is SKIPPED as the directive instructs and C5-06 records
  LOCAL_FAILURE_ONLY.

REPORTED, NO THRESHOLD: the class table by grammar, by operator and by
fault kind (opcode word vs register field); the OLD label distribution
of recovery children; displacement of recovered children (FIZZLE vs
parent); the INSULATION_LOSS count beside the RECOVERY count (the
directive's "merely changed how programs die" reads as
INSULATION_LOSS >= RECOVERY with both replicated).

CONTROLS: the C5-05 cheat program reads BOTH_DIE (its fault sits before
the output; skipping it leaves a wrong constant) -- verified in code;
class assignment is deterministic on re-read (same rows -> same table);
an identity edit is never in the input (crossing is required).
