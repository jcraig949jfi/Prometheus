+=====================================================================+
|  C4-10 -- HELD-OUT EVOLVABILITY TRIAL: PREREGISTRATION                |
|  Archaeon[m2-49ee5a4d]   2026-09-18   Status: DRAFT, NO ROW RUN      |
|  Written BEFORE C4-08 and C4-09 report (the selection rule is fixed   |
|  now; the conditions are chosen from their committed evidence later)  |
+=====================================================================+

THE SELECTION RULE (directive, made operational)
  At most TWO conditions enter, chosen solely from committed C4-01..09
  evidence; a condition qualifies iff, relative to the frozen baseline
  in its own slot, it (a) DECREASED catastrophic loss (the share of
  edits or births below the viability floor) by >= 0.05 with
  non-overlapping Wilson bands, AND (b) INCREASED non-trivial viable
  variation (the coherent share: D3/D4/D6/D7 or D5 with displacement,
  or the equivalent birth-level measure) by >= 0.05. Task score is not
  a criterion.
  Evidence as of this writing (C4-01..07):
    radius > 1 (C4-02)         loss UP          disqualified
    recombination (C4-06)      loss UP, no reach disqualified
    HARD/FIZZLE, addressing,   REPRESENTATION_BLOCKED / no condition
      insulation cost (03,04,07)
    neutral walk (C4-05)       not a damage condition; walkers are a
                               starting population, not an intervention
  Pending: C4-08 (selection under mutation load, n_ops=2) qualifies iff
  its perturbed descendants' single-edit loss is lower than the
  ancestral by >= 0.05 (bands apart) AND their coherent share higher by
  >= 0.05. C4-09 (lateral entry) qualifies iff rescue survival >= 0.25
  AND rescued lineages raised a world's held-out (P1 and P2 both) --
  read as "loss converted to viable variation at the ecology level".
  If NO condition qualifies, the trial runs the BASELINE ALONE on the
  held-out family (the geometry map's held-out column is still
  produced) and the campaign disposition is NO_CONDITION_SELECTED, which
  the directive's three-part claim rule cannot satisfy; that is a
  result, recorded as such.

THE HELD-OUT FAMILY (cheap; never used to develop any C4 condition)
  W1_d2   K=1, delay 2, 4-bit      (a C3 ladder rung; not a C4 world)
  W1_d3   K=1, delay 3, 4-bit      (never run in any campaign)
  W2_K2d1 K=2, delay 1, 4-bit      (never run)
  W0_8b   K=1, 8-bit values        (never run in C2-C4)
  Same starting population CLASS: the 57 C4 starting parents (not the
  walkers), repeated to N by the evolver's rule; same mutation budget
  (N=200, G=60), same execution budget (E=16), same 4 seeds, same
  selection algorithm (tournament 4, elitism 4), no manual rescue.

MEASUREMENTS (per condition x world x seed; Wilson bands over births)
  fatal mutation mass          births with reward < 3/16 (per birth)
  nontrivial executable yield  births >= 3/16 and not degenerate
  behavioural diversity        distinct answer vectors among the final
                               population on the world's held-out set
  lineage depth                ancestry depth of the final elite
  cross-world transfer         final elite's held-out on the OTHER
                               family worlds
  successful recombination     (only if a recombination condition was
                               selected; else not applicable)
  novel held-out capability    elite held-out >= 0.75 on the world
  compute                      evaluations per run (primary + any extra)
  useful descendants per unit  viable births / total births
    mutation budget

THE CLAIM RULE (directive; each with its measurement)
  1  less computation lost at the damage boundary: fatal mutation mass
     lower than baseline by >= 0.05 (bands apart), pooled over the family
  2  the recovered mass is non-trivial: nontrivial yield higher by >=
     0.05 and behavioural diversity not lower
  3  greater downstream reach: novel held-out capability in more
     (world, seed) cells than baseline by >= 2 of 16, or lineage depth /
     useful-descendant rate higher by >= 0.10
  all three  SUPPORTED_DAMAGE_GEOMETRY_EFFECT
  1 only     ROBUST_BUT_INERT
  1 and 2    LOCALITY_WITHOUT_EVOLVABILITY
  3 alone    not attributed to damage-boundary repair
  none / no condition selected   NO_CONDITION_SELECTED or NEGATIVE
  The baseline is preserved and its rows are the map's held-out column
  regardless.

CONTROLS
  negative   the starting population's best held-out on each family
             world is < 0.75 (else the world is already solved and is
             dropped from the family, recorded)
  positive   the baseline reaches the shelf (train >= .45) on W1_d2 in
             >= 2 of 4 seeds (the ladder rung is known reachable)
  cheat      a hand-set elite row with held-out 1.0 reads as a novel
             capability
  determinism  seed 1 baseline reproduces its trace

BUDGET
  (1 + selected conditions) x 4 worlds x 4 seeds x G=60 x N=200; at
  most 3 x 16 x 12,000 = 576k evaluations; minutes to tens of minutes.
