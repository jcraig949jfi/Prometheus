+=====================================================================+
|  C5-08 -- ROBUSTNESS MECHANISM TEST: READOUT                          |
|  Archaeon[m2-49ee5a4d]   2026-09-18 14:54Z   attempt of record a01   |
|  MIXED: length carries robustness; dead code does not; the boundary  |
|  adds a small, dead-code-independent component                       |
+=====================================================================+

P_full = C5-05's grammar-B rows (57 canonical parents, 4,878 edits).
P_ablated = the same parents with statically unreachable instructions
removed (mean dead share .110; 57/57 preserve reward and answer vector
under OLD on the parent environment; none excluded), fresh census of
4,792 edits under the three interpreters. Identity 57/57. 1 engine
record, 0 errors, 231 s.

-----------------------------------------------------------------------
1. THE QUANTITIES (neutral share of single edits; Wilson 95%)
-----------------------------------------------------------------------
  set        R_old           R_fail          R_fizz          GAP    exec-crossing
  full      .435 [.421,.449] .410 [.396,.424] .431 [.417,.445] .021     .048
  ablated   .409 [.395,.423] .384 [.371,.398] .405 [.391,.419] .021     .051
  by length bin (canonical instructions), R_old full / ablated:
    1-8   .171 / .175     9-16  .456 / .418     17-32  .572 / .574
    33+   .714 / .571  (the only bin where ablation moves R_old by more
                        than a band: the longest programs carry the
                        dead code that matters)
  GAP by bin (full): .006 / .023 / .036 / .017.

-----------------------------------------------------------------------
2. TESTS (band 1/16)
-----------------------------------------------------------------------
  M1 dead code carries robustness (pooled drop > band AND >= 2 bins)
       pooled drop .026; bins over the band: 1 of 4              FAIL
  M2 the boundary's contribution is independent of dead code
       GAP .021 vs .021                                          PASS
  M3 GAP equals the executed-crossing share within a band
       .021 vs .048 (inside the band, but half: half of the executed-
       crossing children are dead under FIZZLE anyway)           PASS
  M4 length-matched: FAIL loses no more than the crossing share
       every bin                                                 PASS
  Reading by the preregistered rule: MIXED (M2 and M4 hold, M1 fails).
  Prediction (M1, M2, M4 hold) LOST on M1.

-----------------------------------------------------------------------
3. READING
-----------------------------------------------------------------------
R1  Length carries robustness -- .17 for programs of at most 8
    instructions to .71 for 33 and more -- but statically dead code
    does not: removing 11% of instructions that can never execute
    moves the neutral share by .026, and only the longest programs
    lose anything. C4's "neutrality plus length" survives as LENGTH
    plus behavioural neutrality (reachable instructions whose effect
    the output never sees), not as unreachable code. That is a
    correction to C4-07's mechanism reading, not to its numbers.
R2  The boundary's own component (FIZZLE over FAIL, .021) is the same
    with and without dead code and is about half of the executed-
    crossing rate: of the children that cross and execute the fault,
    half are neutral once skipped and half are dead either way (C5-06).
R3  For the reach question this says: the boundary changes robustness
    by two points on a .43 base, on a grammar that crosses 5% of the
    time. Whatever C5-09 finds will not be a robustness effect.
+=====================================================================+
