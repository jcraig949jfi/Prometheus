+=====================================================================+
|  C5-01 -- DEEP NEUTRAL WALK: READOUT                                  |
|  Archaeon[m2-49ee5a4d]   2026-09-18 14:30Z   attempt of record a01   |
|  Branch: MIXED (a slow, decelerating rise); PRESERVE: NO             |
+=====================================================================+

47 competent parents x 6 walkers x 64 accepted steps (32 proposals per
step, band 1/16 around the original parent, frozen grammar), archived
at 0/16/32/48/64 and exposed to the four other environments. 57 engine
records, 0 errors, 51 s. Controls: identity walker 64/64, randomize-all
stalls at 0, cheat ok; REPLICATION: walkers 1-4's first 16 steps equal
C4-05's committed steps digest for digest, 3,648/3,648.

-----------------------------------------------------------------------
1. EXAPTATION PROBABILITY VERSUS DEPTH (282 walkers per depth)
-----------------------------------------------------------------------
  depth   rate    Wilson 95%       shelf   w0_solver  delay   gen0
    16    .050   [.030, .082]      .088     .044       0       0
    32    .064   [.041, .099]      .123     .044       0       0
    48    .078   [.052, .115]      .149     .056       0       0
    64    .082   [.055, .119]      .167     .044       0       0
  282/282 walkers reached depth 64; acceptance .55 / .58 / .57 / .56 by
  16-step bin (no exhaustion); structural diversity .79 -> 1.00;
  behavioural diversity on the parent environment flat at ~.065.
  Marginal rate per accepted step: 16->32 .00089, 32->48 .00089,
  48->64 .00023 (a fourfold deceleration in the last quarter).

-----------------------------------------------------------------------
2. DISCOVERY YIELD PER EVALUATION (cumulative)
-----------------------------------------------------------------------
  depth   evaluations   exaptive walkers (first found)   yield / eval
    16       11,024               14                       .00127
    32       20,226               21                       .00104
    48       29,508               28                       .00095
    64       38,961               32                       .00082
  Comparator: a random single edit, .006 per edit at 5 evaluations
  each = .0012 per evaluation. Neutral depth 16 matches it; every
  deeper archive is BELOW it, and falling.

-----------------------------------------------------------------------
3. THE BRANCHES, AS PREREGISTERED
-----------------------------------------------------------------------
  continued gradient   NO  (r32 - r16 = .014 < .02; r64 - r32 = .018 < .02)
  plateau              NO  (|r64 - r16| = .032 >= .02)
  degradation          NO  (r64 > r16)
  -> MIXED: probability keeps rising slowly; marginal yield per step
     and per evaluation fall.
  PRESERVE_NEUTRAL_MECHANISM: NO (the continued-gradient branch is not
  met, and Y_64 = .00082 < 2 x .0012).

-----------------------------------------------------------------------
4. READING
-----------------------------------------------------------------------
R1  The C4-05 gradient is real and continues -- exaptation probability
    at depth 64 is .082, thirteen times a single edit's .006 -- but it
    is bought by evaluations that a random single edit spends at least
    as productively. The network is not a yield plateau in probability;
    it is a plateau in efficiency, and past depth 48 it decelerates.
R2  The entire signal is the shelf stratum (K=2 programs finding W0 or
    W1 competence: .167 at depth 64); W0 solvers hold .044 at every
    depth; delay-general programs never gain anything. "Hierarchical
    exploitation" of neutral depth would be exploitation of one
    stratum's one direction.
R3  Nothing was moved: the .02 step, the band, the comparator and the
    factor-two rule were all fixed before the run (D5-003).

For Phase A's disposition: the neutral mechanism is NOT preserved.
+=====================================================================+
