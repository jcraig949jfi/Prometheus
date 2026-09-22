+=====================================================================+
|  C5-02 -- FAIR LATERAL ECOLOGY: PREREGISTRATION                       |
|  Archaeon[m2-49ee5a4d]   2026-09-18   Status: DRAFT, NO ROW RUN      |
|  Campaign 5, Phase A                                                 |
+=====================================================================+

REPAIRS (only the defects C4-09/C4-10 identified)
  1  worlds screened for pre-solution against ALL 57 starting parents
     BEFORE this preregistration, with the rule fixed in code first
     (archaeon/campaign5/screen_worlds.py; receipt
     WORLD_SCREEN_2026-09-18.json, committed at 2999623c9; its sha256 is
     sealed into this slot's preregistration by the runner);
  2  EQUAL TOTAL COMPUTE: the control arm receives the lateral arm's
     total evaluations (primary + transfer) as additional generations;
  3  enough seeds (6) and an ancestry test that separates "the elite
     descended from a rescued lineage" from "the population improved
     while rescue happened".

FROZEN WORLD SET (D5-005; four eligible, distinct structures)
  W2_K2d1   K=2, delay 1   best parent .510   27 parents above floor
  W2_K2_rand K=2, random interleave   .542   45
  W3_K3     K=3            .382   29
  W4_K4     K=4            .302   27
  Starting population per world: the 57 parents subsampled to N=50 by
  the seed's rng (the walkers of C4-05 are within band of their parents
  and add nothing to headroom; the parents are the eligible starting
  class).

ARMS (6 seeds; N=50 per world, E=16)
  lateral   G=100 generations; after each generation's evaluation the
            below-floor non-degenerate children (at most B=24 per world,
            organism-id order) are evaluated on the other three worlds;
            entry iff reward there >= 3/16 AND fitness >= that world's
            current median (the C4-09 rule, D4-013); inject replaces the
            worst. Total evaluations T = primary + transfer.
  control   the same worlds, seeds and starting subsamples, NO lateral
            step, run for G_c = ceil(T / (4 x N)) generations so that
            its total evaluations equal the lateral arm's (within one
            generation). Held-out probes every 10 generations and at
            the end.

MEASUREMENTS (per seed, per world; pooled with Wilson bands over seeds)
  rescues, transfer matrix, rescue survival at end, rescued share of
  the final population (takeover); held-out best of the elite at the
  end (48 held-out episodes) per arm; improvement = lateral - control
  >= 1/16; ATTRIBUTION: for every lateral-arm elite at every probe,
  whether its origins carry "rescued" (descent from an injected
  organism; origins are unioned at every birth) AND the generation of
  the first rescue into that world; an improvement is ATTRIBUTABLE iff
  the improved elite carries the rescued origin and the improvement's
  first probe is at or after the first rescue into that world.

OUTCOME CLASSES (preregistered)
  B  reproducible improvement attributable to lateral entry: on some
     world, attributable improvement in >= 4 of 6 seeds
  A  takeover without improvement: rescued share >= .5 on >= 2 worlds
     pooled over seeds AND no world satisfies B
  C  no meaningful lateral effect: neither A nor B
  PRESERVE_LATERAL_MECHANISM iff B.
  Prediction written to be lost: B on W3_K3 or W4_K4 (the two worlds
  with the most headroom).

CONTROLS
  screen         the frozen worlds' best parent held-out re-measured at
                 run time equals the receipt (< .70)
  negative       control with B=0 equals the lateral arm generation for
                 generation until the first rescue (self-test)
  compute        control total evaluations within one generation of the
                 lateral arm's (reported per seed)
  cheat          a hand-set improved elite with the rescued origin reads
                 attributable
  determinism    seed 1 lateral reproduces its traces

DISPOSITIONS
  A / B / C as above; INSTRUMENT_INVALID on a control failure.
