+=====================================================================+
|  C4-09 -- LATERAL EXAPTATION / PAIRED ECOLOGY: READOUT               |
|  Archaeon[m2-49ee5a4d]   2026-09-18 09:05Z   attempt of record a01   |
|  Disposition: INCONCLUSIVE as preregistered (rescues persist; one    |
|  live world improved in 1 of 3 seeds); design defect recorded         |
+=====================================================================+

Four worlds (W0, W1_d1, W1_d4, W2_K2), N=50 each, G=100, E=16, 3 seeds,
same 188 walkers subsampled per world; control vs lateral (B=24
below-floor non-degenerate children per world per generation evaluated
on the other three; entry iff reward there >= 3/16 and >= that world's
median fitness; inject replaces the worst). 6 engine records, 0 errors,
175 s.

-----------------------------------------------------------------------
1. RESCUES AND THEIR FATE
-----------------------------------------------------------------------
  seed   rescues   survival at G=100   rescued share of final pops (W0/d1/d4/K2)   extra compute
   1       460         .404              .92 / .90 / .90 / 1.00                      .739
   2       446         .305              .92 / .86 / .00 / .94                       .728
   3       335         .546              .92 / .94 / .90 / .90                       .646
  Transfer direction (pooled): into W0 from W1_d1 448 and from W1_d4 512;
  into W2_K2 from W1_d1 40 and from W1_d4 65; out of W0 24. Programs
  that fail in a delay world usually still work in W0 (the easier
  world), and in W2_K2 often enough to enter.
  P1 (rescue survival >= .25): HELD in 3/3 seeds. Rescued lineages did
  not merely survive; they replaced the resident populations.

-----------------------------------------------------------------------
2. DID ANY WORLD GET BETTER?
-----------------------------------------------------------------------
  held-out of the elite at G=100 (control / lateral):
  W0     1.000 / 1.000    W1_d1  1.000 / 1.000    W1_d4  1.000 / 1.000
  W2_K2  .438 .563 .531 / .531 .563 .531  (seeds 1, 2, 3)
  Three of the four worlds were SOLVED BY THE STARTING WALKERS (held-out
  1.0 at generation 0 in the control arm): the C4-05 walkers descend
  from W0 solvers and delay-general parents. Only W2_K2 could improve,
  and the lateral arm improved it in seed 1 (+.094; the W2_K2 elite was
  a rescued lineage at 10 of 11 probes) and not in seeds 2 and 3.
  P2 (a world improved by >= 1/16 in >= 2 of 3 seeds): LOST (1 of 3).
  Overhead shape (survival < .10 and no improvement): NOT met.

-----------------------------------------------------------------------
3. READING
-----------------------------------------------------------------------
R1  Stepping stones exist and are cheap to find: a third to a half of
    the below-floor children of a delay world run in W0, and 2-4 per
    generation run well enough in W2_K2 to enter. They persist and
    dominate. The directive's failure shape ("permissive survival with
    no downstream consequence") does not describe this: the consequence
    is takeover.
R2  Takeover is not improvement. In the one live world the rescued
    lineages reached the elite in one seed of three and raised held-out
    by .094 there; elsewhere they displaced residents at equal held-out.
    Whether takeover by transplanted lineages is a stepping-stone
    mechanism or merely a second source of the same shelf programs is
    not decided by three seeds on one live world.
R3  DESIGN DEFECT (mine, recorded, not repaired after the fact): the
    ecology's worlds were not checked against the starting population
    before the run; three were pre-solved, so the "improvement" measure
    had one world of headroom. C4-10's preregistration carries that
    check (worlds at or above .75 are dropped).
R4  Extra compute .65-.74 of the primary budget: the lateral step is not
    free; at equal TOTAL budget the control would have run ~70% more
    generations, which this slot did not test.

-----------------------------------------------------------------------
4. FEEDS
-----------------------------------------------------------------------
C4-10's rule: lateral qualifies iff P1 AND P2 -> does NOT qualify.
Harness label CAPABLE_NEGATIVE (worlds improved .33 vs 1 required). The
transfer matrix and rescue logs are committed for a later slot that
re-runs the ecology on unsolved worlds at equal total budget.
+=====================================================================+
