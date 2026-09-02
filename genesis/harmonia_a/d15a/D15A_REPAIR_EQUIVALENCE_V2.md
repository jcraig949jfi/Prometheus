# D15A_REPAIR_EQUIVALENCE_V2

Harmonia A · 2026-09-02 · Track B redesign of the scientific object.
Fully-enumerable finite worlds; every relation below is computed exactly
by BFS, no sampling.

## Substrate
State space `S = Z_6 × Z_6` (|S| = 36 — small enough that every set,
closure, and version space is enumerated exhaustively). An **operator**
is a permutation of `S`. A world fixes: agent vocabulary `T` (a set of
operators), start `x0`, target set `G ⊆ S`, taboo set `Tb ⊆ S`, an
**observable universe** `O ⊆ S` (states a probe may legally read), the
**true missing operator** `h`, and a **repair pool** `R` (candidate
operators the agent may synthesize). Navigation reach `N = reach(T, x0)`
(BFS closure). The world is a DYNAMICS failure: `G ⊄ N` (T alone cannot
solve it).

## The three nested relations (E1 ⊃ E2 ⊃ E3)

**E1 — extensional operator equality.** `q1 =E1 q2` iff `q1(s)=q2(s)`
for all `s ∈ S`. Exact function identity. Retained only for
implementation sanity; it is the relation the failed v1 generator was
too close to.

**E2 — GOAL-RELEVANT REPAIR EQUIVALENCE (PRIMARY).**
`q1 ~E2 q2` iff the two repairs are indistinguishable for the task:
```
  reach(T ∪ {q1}, x0) ∩ G  ==  reach(T ∪ {q2}, x0) ∩ G      (same targets solved)
  (reach(T ∪ {q1}, x0) ∩ Tb == ∅) == (reach(T ∪ {q2}, x0) ∩ Tb == ∅)  (same soundness)
```
The E2 class of `q` is the pair `( frozenset(reach(T∪{q},x0) ∩ G),
sound_bit )`. This collapses operators that differ arbitrarily OFF the
goal-relevant reachable region but agree on which targets become
reachable and whether taboo is preserved — precisely the collapse v1
lacked.

**E3 — decision equivalence (coarser, secondary).** `q1 ~E3 q2` iff the
frozen warrant/repair endpoint returns the same decision for both
(e.g. both SOLVE within `B_solve`, or both leave the same admissible
target subset at the same synthesis cost tier). E3 is reported but not
the identifiability object.

**Why E2 is primary (frozen reason, not chosen for pretty counts):**
identifiability is about *what the reasoner must still learn to justify
a repair*. The scientifically meaningful unit is "a repair that makes
the same task-relevant difference," which is exactly E2. E1 measures
operator multiplicity (the v1 error); E3 is downstream of the endpoint
and would let the estimator's own thresholds define the object. E2 is
the coarsest relation that is (a) defined purely from the world+task,
(b) strictly finer than "solves-or-not," and (c) preserves the
soundness distinction the Court cares about.

## Observation model and the version space

The true dynamics is `h`. A **probe** at `s ∈ O` reveals `h(s)`. A
repair `q` is **consistent** with a probe set `P` iff `q(s)=h(s)` for
all `s ∈ P`. **Useful repairs** `U = { q ∈ R : G ⊆ reach(T∪{q},x0) }`
(fully solves; `h ∈ U` by construction). The **version space** over E2
classes:
```
  V(P) = { E2class(q) : q ∈ U and consistent(q, P) }
```
`h`'s own class never leaves `V` (h is consistent with observations of
h). `IDENTIFIED(P)` iff `|V(P)| = 1`. `H(P) = log2 |V(P)|`.
`UNDERIDENTIFIED` iff `|V(∅)| > 1`. A world is `ZERO_INFO` iff
`V(O) = V(∅)` with `|V(∅)|>1` (probing the entire observable universe
shrinks nothing). A probe `s` is **informative** given `P` iff
`V(P∪{s}) ⊊ V(P)`.

## Probe factorial (constructive, replaces the 1.1x tripwire)

Each probe state `s ∈ O` is typed by two independent bits:
- **INFO bit**: `s` is informative at `V(∅)` (splits some E2 class off).
- **GOAL bit**: `s ∈ N` AND `s` lies on a shortest T-path toward some
  `g ∈ G` frontier (navigational progress).
Four probe kinds are built to exist in ACTIVE worlds: INFORMATION_ONLY
(info=1,goal=0), GOAL_ONLY (info=0,goal=1), MIXED (1,1), NULL (0,0).
The active-information claim is then tested against this factorial, not
against a coverage correlation.

## Identifiability rungs (what each MEANS, populated by construction §3)

    I0 ZERO_INFO      |V(∅)|>1 AND V(O)=V(∅): fundamentally underident.
    I1 PASSIVE-SLOW   |V(∅)|>1; only teleport-probes in O\N distinguish
                      (random navigation cannot).
    I2 ACTIVE         |V(∅)|>1; a specific small probe set collapses V
                      fast; INFO/GOAL probes both exist and separate.
    I3 SMALL          |V(∅)| small (2-3); collapses in <=2 probes.
    I4 NEAR-UNIQUE    |V(∅)|=2 collapsing in 1 probe.
    I5 IDENTIFIED     |V(∅)|=1: one meaningful repair class from the
                      start (the EQUIV rung lives here: many E1 members,
                      one E2 class).

## Adversarial cases the E2 relation is built to survive (§9)

1. **same target reachability, different taboo reachability** — E2
   carries the soundness bit, so these are E2-DISTINCT. (Meaningful:
   an unsound repair is a different repair.)
2. **same finite-horizon behavior, different unbounded closure** — E2
   uses full BFS closure (unbounded), so a divergence that changes the
   reachable target subset splits them; a divergence that does not is
   correctly collapsed. (Meaningful iff it touches G.)
3. **same current-frontier effect, divergent after one later probe** —
   handled by the version space, not E2: such repairs are E2-equal now
   and the probe that would separate them is exactly what makes the
   world ACTIVE vs ZERO_INFO. This is the science, not a bug.
4. **same solver outcome, different cost/depth** — E2-equal (both solve
   G); the cost difference is an E3 distinction, reported separately.
5. **appear equivalent only because G is too small** — guarded by the
   census: G is sized so that at least the intended number of E2
   classes exist among U; a world where |V(∅)| collapses below its rung
   target is rejected.
Decisions frozen BEFORE census: soundness IS meaningful (in E2); cost
is NOT (E3 only); off-goal divergence is NOT (collapsed by E2 by
design). These choices are the scientific commitment.
