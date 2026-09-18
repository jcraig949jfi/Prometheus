+=====================================================================+
|  C5-10 -- HELD-OUT TRIAL: THE SELECTION RULE                          |
|  Archaeon[m2-49ee5a4d]   2026-09-18 15:20Z                            |
|  COMMITTED BEFORE C5-04 AND C5-05 RAN (directive: before C5-05 reports)|
+=====================================================================+

HELD-OUT WORLDS (frozen now, from the screen's eligible reserve, never
used by any earlier C5 slot): W3_K3d1 (best starting parent .375) and
W2_K2d4 (.552). Held-out seeds: 11..16.

CONDITIONS THAT MAY BE SELECTED: exactly one of
  B_FAIL    representation B, FAIL mode, grammar B
  B_FIZZLE  representation B, FIZZLE mode, grammar B

SELECTION RULE (applied to C5-09's committed readout, nothing else):
  A condition is SELECTABLE iff, in C5-09 on the four Phase-A worlds x 6
  seeds (24 cells), it improved the elite's final held-out over the OLD
  arm (old representation, grammar v0.4, same seeds, same total compute)
  by >= 1/16 in at least 4 more cells than it lost by >= 1/16, AND the
  OLD+grammar-B arm did not (so the gain is the representation's, not the
  grammar's). If both are selectable, take the one with the larger net
  cell count; ties -> B_FAIL (the harder boundary).
  If no condition is selectable: NO_CONDITION_SELECTED, which is a
  success of the rule, and C5-10 records that and stops.

THE TRIAL (only if a condition is selected): the selected condition vs
OLD on the two held-out worlds x 6 held-out seeds (12 cells), N=50,
G=100, E=16, equal total compute by construction (same N, G, E).
  REPLICATED iff net cells (won by >= 1/16 minus lost by >= 1/16) >= 2 of
  12 and no cell lost by >= 2/16.
  FAILED_TO_REPLICATE otherwise.
Nothing in this file may change after this commit. The C5-09 readout is
written by its runner from preregistered rules; this file reads it.
