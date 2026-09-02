# D15A_TRACKB1_REPORT — the middle does not exist (in this object)

Harmonia A · 2026-09-02 · Track B.1 per the R-A brief: substrate
enlarged to Z_8 x Z_8, nothing else moved. Freeze: D15A_TRACKB1_FREEZE.md
(committed before generation). Engine untouched at pin 5274ddbe.

## RETURN GATE — five verdicts (frozen bands, no collapsing)

    D15A_TRACKB1_I2               = NOT_READY  (0 worlds / 12,000 seeds)
    D15A_TRACKB1_ORTHOGONALITY    = NOT_READY  (GOAL_ONLY cell empty)
    D15A_TRACKB1_DIFFICULTY_MATCH = NOT_READY  (I2 contrast unpopulatable)
    D15A_TRACKB1_FULL_GENERATOR   = NOT_READY  (I2 rung absent)
    D15A_TRACKB1_INSTRUMENT       = NOT_READY

    => Confirmatory D15-A remains forbidden. This is the brief's
       anticipated negative branch, returned as instructed, not rescued.

## THE FINDING: I2's absence is STRUCTURAL, not substrate-bound

Z_8x8 reproduced the Z_6^2 result exactly — 0 I2 worlds — while every
anchor survived enlargement untouched:

    I0 zero-info retained        1.00   (band >= 0.5)
    I1 passive-inf/active-finite 1.00   (band >= 0.99)
    I5 identified                1.00   (band >= 0.8)
    E1/E2 collapse median        3.0    (band >= 3.0)
    master-key top               0.095  (band <= 0.15)
    I3 passive==active equality  persists (confound check)
    difficulty common support    I0-I5: 76 pairs, I1-I3: 76 (band 30)

So enlargement did NOT repair I2 by damaging anything else; it repaired
nothing because nothing was substrate-limited. The census then forced
the real diagnosis:

**THEOREM (binary version space).** The frozen definitions are
E2class(q) = ( reach(T u {q}, x0) intersect G , soundness bit ) and
U = { q : G subset-of reach(T u {q}, x0) } (useful = FULL solver).
Every q in U has reach intersect G = G by the definition of U.
Therefore among useful repairs the E2 class is (G, sound_bit): AT MOST
TWO CLASSES — independent of substrate size, |G|, operator family, or
anything else. Empirical confirmation: every underidentified world
ever generated on BOTH substrates has E2_V0 min = max = 2 (v2 census:
I0/I1/I3/I4 all (2,2); B.1 census identical). H0 <= 1 bit always.

**COROLLARY (cost trichotomy).** With |V0| <= 2, any informative probe
collapses the space to 1. Identification cost is therefore in
{0, 1, infinity}. I2 requires finite(passive) AND finite(active) AND
active < passive — impossible when the only finite cost is 1.
**I2 is empty in EVERY substrate.** Z_6^3 cannot help; escalation is
declined analytically, per the brief's "only if necessary" and "do not
escalate for prettier geometry."

**COROLLARY 2 (goal-progress vacuity).** In a dynamics-failure world
(G outside reach(T, x0)) no T-step from the navigation reach enters G,
so the frozen goal bit ("s on a shortest-T-path frontier toward G") is
FALSE everywhere: the GOAL_ONLY and MIXED factorial cells are
structurally empty (measured: every informative probe in every
candidate world is INFORMATION_ONLY; io_frac = 1.00, go_frac = 0.00).
The 4-cell orthogonality factorial cannot be populated under the
frozen probe semantics in single-target dynamics-failure worlds —
the same theorem-shaped emptiness.

## CORRECTION of the Track-B claim

The Track-B report attributed I2's emptiness to "a substrate-size
limit, not a logic error." That attribution was WRONG. The cause is
the frozen scientific object itself: full-solver U + target-subset E2
makes the version space binary, and binary version spaces admit no
graded middle. The Z_6^2 and Z_8x8 failures have one cause. Recorded
here and in the journal; the Track-B report is left as issued
(history is not rewritten).

## WHAT THE SIX-RUNG THEORY ACTUALLY DEMANDS (for reconsideration)

A graded middle requires |V0| >= 3, i.e. useful repairs that differ in
WHAT they accomplish, not only in soundness. Under the frozen object
that is impossible. The minimal changes that would make I2 definable
(NOT executed — they touch frozen definitions and are the operator's
call):

  (a) MULTI-TARGET worlds with U admitting PARTIAL solvers
      (q useful iff it solves a nonempty subset of G). Then the
      target-subset component varies across U and |V0| can reach
      2^|G| x 2. Graded identification (WHICH subset does the true
      repair solve?) becomes a real multi-probe object, and passive
      vs active probe access can separate gradually.
  (b) A graded goal-progress notion (e.g. post-repair distance-to-G
      deltas) replacing the vacuous single-target frontier bit, so
      GOAL_ONLY/MIXED probes can exist in dynamics-failure worlds.

Both are changes to D15A_REPAIR_EQUIVALENCE_V2.md's frozen U/probe
semantics — beyond Track B.1's substrate-only mandate. The honest
statement: the six-rung ladder as frozen demands a distinction these
worlds CANNOT express, for provable reasons, not for lack of seeds,
states, or search.

## WHAT SURVIVES (unchanged, still exactly verified)

The five populated rungs {I0, I1, I3, I4, I5} with all anchors; the
sharp I1 active-information existence result (passive impossible /
active one probe, 100% of worlds); E1/E2 collapse (multiplicity is
not the object being measured); the oracle firewall; A3 replay; the
engine qualification at 5274ddbe with ENG-1/2/3 declared. Topology-2:
ABANDONED_PARTIAL_RUN_ENGINE_DISCONTINUITY (journaled in both
directories; artifacts preserved).

## RECOMMENDATION (one decision for the operator)

Adopt (a)+(b) as a Track B.2 revision of the frozen object — a REAL
change to the preregistered science, requiring a fresh freeze of
E2-over-partial-solvers, new rung definitions, and a re-run of the
full census including anchors — or accept the five-rung ladder with
I1 as the (existence-form) active rung and drop the graded claim from
D15-A's confirmatory scope. Track B.1's data supports either; it
cannot decide between them. No further generation will run until that
call is made.

## Artifacts

D15A_TRACKB1_FREEZE.md · trackb1_generator.py ·
D15A_TRACKB1_CENSUS.json (verdicts, paired distribution [empty],
factorial cells, difficulty pairs, confound provenance, anchors) ·
JOURNAL.jsonl. Prior: D15A_TRACKB_REPORT.md (its substrate-size
attribution corrected above), D15A_GENERATOR_CENSUS_V2.json.
