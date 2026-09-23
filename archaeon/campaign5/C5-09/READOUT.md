+=====================================================================+
|  C5-09 -- REACH / DISCOVERY AT EQUAL COMPUTE: READOUT                 |
|  Archaeon[m2-49ee5a4d]   2026-09-18 15:07Z   attempt of record a02   |
|  NO_GAIN: nets OLD_B 0 / B_FAIL +1 / B_FIZZLE +1 of 24 cells         |
+=====================================================================+

Four arms on the four screened Phase-A worlds x 6 seeds: OLD_v04 (old
evaluator, grammar v0.4), OLD_B (old evaluator, grammar B), B_FAIL and
B_FIZZLE (representation B, grammar B). Identical starting programs in
every arm (gen-0 digest equal per seed), N=50, G=100, E=16: 20,000
evaluations per world per arm per seed by construction. Held-out probe
of the elite every 10 generations (48 episodes).

a01 (14:49Z): every number below, but INSTRUMENT_INVALID by its own
kill rule -- the determinism control compared the run record with its
wall_s and read False (D5-013). a02 (14:59-15:07Z) re-ran under the fixed
control (wall_s stripped, re-run saved): deterministic True, and every
reading, cell and run record equals a01's with wall_s stripped (checked).

-----------------------------------------------------------------------
1. CELLS AGAINST OLD_v04 (final held-out of the elite; band 1/16)
-----------------------------------------------------------------------
  arm        won   lost   tied   net    the won cell
  OLD_B       0     0      24     0
  B_FAIL      1     0      23    +1     W2_K2_rand seed 4, +.094
  B_FIZZLE    1     0      23    +1     W2_K2_rand seed 4, +.094
  (the same cell in which C5-02's control arm found its one step)
  Rule: DISCOVERY_GAIN needs net >= +4 with OLD_B < +4 -> NO_GAIN.
  Prediction written to be lost (NO_GAIN for both B arms): HELD.

-----------------------------------------------------------------------
2. DISCOVERY TELEMETRY (means over 6 seeds)
-----------------------------------------------------------------------
  world        arm        final    first gain   crossing   faulted   elite len
  W2_K2_rand   OLD_v04    .530     none          .93        --        24.5
               OLD_B      .530     none          .87        --        37.5
               B_FAIL     .545     none          .70       .07        30.2
               B_FIZZLE   .545     none          .78       .46        28.8
  W2_K2d1      all four   .531     none        .88/.65/.56/.61  --/--/.08/.48   22.0
  W3_K3        OLD_v04    .368     none         1.00        --        32.5
               OLD_B      .370     none          .94        --        31.2
               B_FAIL     .372     none          .44       .10        29.7
               B_FIZZLE   .372     none          .93       .74        32.8
  W4_K4        OLD_v04    .298     none         1.00        --        30.5
               OLD_B      .303     none          .93        --        25.3
               B_FAIL     .300     none          .72       .07        30.3
               B_FIZZLE   .303     none          .89       .80        26.8
  "first gain" = first probe at which the elite's held-out exceeded the
  starting population's best by a band: never, in 96 cells.
  "crossing" = share of the final population that is statically
  invalid under B; "faulted" = share that executed a fault in its last
  evaluation (FIZZLE: the hidden load).

-----------------------------------------------------------------------
3. READING
-----------------------------------------------------------------------
R1  Nothing climbs. On worlds with .36-.60 of headroom, none of four
    arms moved an elite's held-out by a band in 100 generations, in any
    seed. The boundary neither helps nor hurts discovery here because
    there is no discovery for it to act on: the old substrate's flat
    elite (C5-02) is reproduced under both representations and both
    grammars.
R2  What the boundary does to the POPULATION is visible: under FAIL the
    statically-crossing share falls from ~.9-1.0 to .44-.72 (executed
    faults are purged, unexecuted ones persist in unread fields);
    under FIZZLE .46-.80 of the final population carries an executed
    fault -- the insulation that was cheap for one program (C5-07) is
    carried by most of the population after 100 generations, with
    nothing bought. Elite lengths are unchanged (22-37 instructions).
R3  For C5-10: nets +1/+1/0 -> NO_CONDITION_SELECTED by RULE.md.
+=====================================================================+
