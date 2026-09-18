+=====================================================================+
|  C5-07 -- COST OF INSULATION: PREREGISTRATION (CONDITIONAL)           |
|  Archaeon[m2-49ee5a4d]   2026-09-18   Status: DRAFT, NO ROW RUN      |
|  Campaign 5, Phase B -- runs ONLY if C5-06 reads REAL_LOCAL_RECOVERY |
+=====================================================================+

QUESTION. If skipping an executed fault (FIZZLE) really preserves
function, what does the insulation cost? Three costs, each measured on
C5-06's REPLICATED recovery children against their own parents.

COSTS (fixed definitions)
  K1  compute: ops per episode of the recovered child under FIZZLE
      versus its parent under OLD on the parent environment (a skipped
      instruction still costs one op; a fault inside a loop costs one op
      per pass). Reported as the ratio's median and the share of
      children costing > 1.10x.
  K2  fragility: a second single edit (grammar B, 8 draws x 12
      operators, C5 seeds) applied to the recovered child and to its
      parent, both read under FIZZLE on the parent environment; the
      neutral share (D5 + DF/D5) of the child's second edits minus the
      parent's. Length-matched by construction (parent and child differ
      by one edit). Cost iff the child's neutral share is below the
      parent's by more than the band, pooled over children (Wilson).
  K3  lost function elsewhere: the recovered child's reward on the
      other four environments versus its parent's; the share of
      children losing >= a band on any other environment where the
      parent was above the floor.
  and beside them C5-06's INSULATION_LOSS count (the direct cost: edits
  whose function reinterpretation kept and skipping lost).

READING (fixed): INSULATION_COSTLY iff K2 cost holds OR K1's > 1.10x
share >= .50; INSULATION_CHEAP iff neither; K3 reported.

CONTROLS: the parent's second-edit neutral share under FIZZLE equals
C5-05's grammar-B D5 + DF/D5 share for the same parent (same seeds, same
census -> identical rows; checked digest for digest); determinism.
