+=====================================================================+
|  C4-06 -- LATENT STRUCTURE, RECOMBINATION, VALLEY CROSSING: READOUT  |
|  Archaeon[m2-49ee5a4d]   2026-09-18 08:10Z   attempt of record a01   |
|  Disposition: INCONCLUSIVE as preregistered (no arm crossed; shelf    |
|  control holds); harness TARGET_UNREACHABLE; damage table measured    |
+=====================================================================+

Starting population: the 188 depth-16 C4-05 walkers (regenerated from
seeds, 188/188 digests equal to the committed steps), repeated to N=200.
Challenge W2_K2 summit (held-out >= 0.90 on 48 held-out episodes, probed
every 10 generations). Two arms x 6 seeds, N=200, G=100, E=16, identical
seeds and rng streams; the arms differ only in whether descend() gets a
mate. Negative control: starting best held-out .531 (< .90). 12 engine
records, 12 reachability rows, 0 errors, 125 s.

-----------------------------------------------------------------------
1. CROSSINGS AND TRAJECTORIES
-----------------------------------------------------------------------
  arm              crossings   shelf (train >= .45)   held-out at G=100 (6 seeds)
  mutation_only       0/6           6/6 (at gen 0)     .531 .354 .531 .510 .562 .521
  recombination       0/6           6/6 (at gen 0)     .531 .354 .531 .510 .562 .521
  Training best rose from .56-.75 at generation 0 to a maximum of .66-.81
  in every run (noisy per-generation episode draws); the held-out reward
  of the elite never left the shelf band and is IDENTICAL between arms at
  every probe of every seed. The population means differ between arms
  (e.g. seed 1 final mean .381 vs .412; seed 3 .453 vs .508), and the
  final elites are different programs -- neutral variants of the same
  initial best walker, kept by elitism, scoring the same 48 held-out
  episodes identically. The C4-05 network is what the search walked on.

-----------------------------------------------------------------------
2. BIRTH-KIND DAMAGE TABLE (recombination arm; 6 seeds pooled)
-----------------------------------------------------------------------
  birth kind        births    viable share (train >= 3/16)
  mutation             787        .815
  mated, no splice 111,640        .818   (a mate was drawn; the operator
                                          drawn did not use it)
  mated, splice      6,218        .734   (5.2% of births; the mate's
                                          region copied in)
  mutation_only arm, all births 118,627: .820.
  P2 ("mate-splice births >= .10 more catastrophic"): .266 vs .186,
  difference .081 -- LOST by .019; the direction holds, the size does not.

-----------------------------------------------------------------------
3. NOVELTY
-----------------------------------------------------------------------
  structural novelty (new category-vector x length pairs per run):
  13.1k-13.9k in both arms (no difference); distinct held-out elite
  behaviours over the run: mutation_only 2-7, recombination 1-4.

-----------------------------------------------------------------------
4. THE PREDICTIONS AND THE READING
-----------------------------------------------------------------------
  P1 recombination crosses >= 2 more seeds       LOST (0 vs 0)
  P2 mate-splice >= .10 more catastrophic        LOST (.081)
  Harness: TARGET_UNREACHABLE (0/12 runs reach; Wilson upper .243;
  table class OBSERVED_UNREACHABLE_AT_BUDGET for the W2_K2 summit).
R1  At this budget neither operator set turns 188 independently drifted
    shelf lineages into a W2_K2 summit; the C3-SFE-01 reading (0/24)
    stands with 12 more runs and a different, structure-rich start.
R2  Recombination in this grammar is a region copy in 5% of births; it
    is measurably more damaging than a single edit (8 points less viable)
    and adds no crossings and no structural novelty beyond mutation.
    "Multiplies damage" is the direction; "modestly" is the size.
R3  The positive control (shelf) is weak: the walkers start on the
    shelf, so "shelf reached at generation 0" tests nothing about the
    search. Recorded as a defect of the preregistration, not repaired
    after the fact.

-----------------------------------------------------------------------
5. FEEDS
-----------------------------------------------------------------------
C4-08 reruns the mutation_only arm (traces are its negative control) and
adds a mutation-load arm; C4-10's condition selection has, from C4-06,
no candidate: recombination decreased viability and did not increase
reach.
+=====================================================================+
