+=====================================================================+
|  C4-06 -- LATENT STRUCTURE, RECOMBINATION, VALLEY CROSSING           |
|  Archaeon[m2-49ee5a4d]   2026-09-18   Status: DRAFT, NO ROW RUN      |
+=====================================================================+

QUESTION (directive)
  Can separately accumulated neutral or weakly viable changes combine
  into capabilities that ordinary one-step search rarely reaches? Does
  recombination turn accumulated latent structure into useful
  computation, or does it simply multiply damage?

STARTING POPULATION (matched lineages from C4-05)
  The archived C4-05 walkers of the 45 VIABLE parents at archive depth
  D* := the deepest archive depth reached by >= 3 of 4 walkers for at
  least half the viable parents (preregistered rule; expected 8), else
  depth 4; a parent contributes its walkers at min(D*, its depth). Each
  walker is an independently drifted lineage of its parent. Filled to N
  with the evolver's common_fill from the same walkers (deterministic).

THE CHALLENGE (not solved by the starting population)
  W2_K2 (K=2, 4-bit): no C4 parent reaches the SUMMIT (held-out >= 0.90;
  C3-SFE-01: 0/24 confirmed summits; shelf parents sit at .45-.90).
  Fitness = training reward on W2_K2 (E=16, CRN); held-out probe of the
  elite every 10 generations on 48 held-out episodes; a CROSSING is a
  held-out >= 0.90 elite. No reward term names any architecture; no
  motif is revealed.

ARMS (equal budget: N=200, G=100, E=16, 6 seeds per arm, same seeds)
  mutation_only    descend with mate=None ALWAYS (splice copies from
                   self; every other operator unchanged)
  recombination    the evolver's existing mate policy (independent
                   tournament for the mate; splice copies from the mate
                   when drawn: ~5% of births)
  The two arms differ ONLY in whether a mate is passed; the grammar,
  weights, selection and budgets are identical.

MEASUREMENTS (per arm, per seed, Wilson bands over seeds and children)
  viable offspring yield        share of births whose training reward
                                >= 3/16 (floor) per generation, averaged
  catastrophic recombinants     among splice-with-mate births
                                (recombination arm only): share below
                                the floor vs the same share among
                                mutation births in the same arm
  structural novelty            new (opcode-category vector, length)
                                pairs per generation not seen in the
                                starting population
  held-out behavioural novelty  distinct held-out answer vectors of the
                                elite over the run (every 10 gens)
  crossings                     seeds whose elite reaches held-out >=
                                0.90 by G=100; first_crossing_gen
  damage multiplication         mean training reward of children vs
                                parents by birth kind

PREDICTIONS (written to be lost)
  P1  crossings(recombination) - crossings(mutation_only) >= 2 of 6
  P2  catastrophic share among mate-splice births exceeds the mutation
      births' share by >= 0.10 (recombination multiplies damage)
  A held P2 with a held P1 is the directive's "both": recombination
  both damages more AND crosses more.

CONTROLS
  positive   the mutation_only arm reaches the SHELF (training >= 0.45)
             in >= 3 of 6 seeds by G=100 (the table says shelf is COMMON)
  negative   the starting population's best held-out on W2_K2 < 0.90
             (verified before generation 0; else the challenge is
             already solved and the slot is INSTRUMENT_INVALID)
  cheat      a seed with an injected summit-capable elite (a constructed
             copy of the best shelf parent is NOT summit-capable; so the
             cheat is: hand-set held-out 1.0 on a copy of the receipt row
             must read crossing) -- the crossing detector reads the field
  determinism  seed 1 of each arm reproduces its trace on rerun

DISPOSITIONS
  SUPPORTED if P1 holds (recombination crosses more, with the damage
  measured beside it); NEGATIVE if crossings are equal or fewer in the
  recombination arm; INCONCLUSIVE if neither arm crosses and the shelf
  positive control holds (the valley is not crossed at this budget by
  either -- the C3 reading stands); INSTRUMENT_INVALID on a control
  failure. SKIPPED_RESOURCE_BOUND is not expected (12 runs of G=100).

RECORDS
  one engine world; one observation per (arm, seed) with the trace;
  rows.json; elites' manifests at crossing.
