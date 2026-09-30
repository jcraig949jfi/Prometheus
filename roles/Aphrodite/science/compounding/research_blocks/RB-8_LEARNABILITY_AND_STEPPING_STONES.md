# RB-8 -- THE LEARNABILITY BOTTLENECK AND STEPPING-STONE LADDERS IN THE T4 WORLD
# (threads T07, T08, T24)

Medium, autonomous. Estimated 1-2 days. Read RB-00 first. Then read
science/compounding/rb2/TASK_WORLD_T4_DESIGN.md, engine/AMENDMENT_18_2026-09-27.md and
AMENDMENT_19_2026-09-28.md, and the C2 result under engine/A19_C2/ once it exists.

WHY
  RB-2: in the T4 world only 11-13% of survivors fall inside the PRISTINE learnability
  window (0 < p < 1), and only 21-23 families are solvable by L1 and not by PRISTINE. The
  task world is now rich, but mostly unlearnable from scratch at the frozen escrow.
  This is the classic stepping-stone problem (Avida EQU 23/50 with intermediates vs 0/50
  without, abstract-derived; E-POET direct-optimisation failures;
  PRIOR_ART_C s7 D2, s8 E3).

QUESTIONS
  Q1 Budget: what fraction of T4-world families does PRISTINE solve at 1x / 4x / 16x /
     64x escrow? This is the budget curve of the unlearnable mass.
  Q2 Ladders: for 10 unlearnable target families, construct ON-path intermediate
     families (one edit toward the target from a PRISTINE-solvable family) and matched
     OFF-path intermediates (same edit distance, not toward the target). Does a donor
     that observes the on-path ladder derive/select an abstraction that solves the
     target within escrow more often than off-path or no-ladder donors? (Lenski design;
     it needs a preregistered AMENDMENT if it becomes a disposition.)
  Q3 Endogenous supply: hindsight relabelling (every program a donor finds becomes a
     task). Over 3 generations from PRISTINE, does the relabelled supply drift into the
     learnability window, or collapse toward G1's span?
GUARDRAILS
  Ladders are built by a rule stated before any donor runs. The same rule builds the
  off-path controls. Use forensic labels "RB8-...". Novelty uses ruler v2 (or v2.1
  from RB-7).
DELIVERABLES: science/compounding/rb8/ (scripts, JSON, LEARNABILITY.md).
