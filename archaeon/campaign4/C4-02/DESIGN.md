+=====================================================================+
|  C4-02 -- MUTATION-RADIUS RESPONSE CURVE: PREREGISTRATION DRAFT      |
|  Archaeon[m2-49ee5a4d]   2026-09-18   Status: DRAFT, NO ROW RUN      |
|  Runs after C4-01 closes; sealed by the harness at run time.         |
+=====================================================================+

QUESTION
  Does genotypic distance have any usable relationship to behavioral
  distance? For edit radii delta in {1, 2, 4, 8, 16}, what are
  D(delta) = displacement(parent, child) conditional on executing, and
  the catastrophic probability P(D2 or D3 | delta), per parent stratum?

PARENTS
  The same 57 (STARTING_POPULATION.json), same environments (D4-004),
  same CRN episode sets as C4-01 (family train, index 1, E=16).

EDITS (frozen grammar mass machinery; not tuned after seeing results)
  A child at radius delta is delta successive grammar.mutate() calls
  with operators drawn by the FROZEN WEIGHTS (name=None), from one rng
  SplitMix64(seed_from("c4.02.radius", 20260921, organism_id, delta, r)),
  r in 1..8 draws per (parent, delta). 57 x 5 x 8 = 2,280 children.
  The op_record list of every child is kept (which operators, which
  positions). A step whose operator returns "noop" still counts as a
  step (the radius is the number of applications, the eligibility fact
  is recorded per child as noop_steps).
  Radius 16 is the "one larger preregistered radius that remains cheap"
  (16 x 4 = 64 words touched at most; the largest genome is 64 words).

EVALUATION / CLASSIFICATION
  Exactly C4-01's (D4-003; c4_01.classify), on the parent environment
  and the three others; displacement = normalized Hamming distance
  between answer vectors.

PRIMARY OUTPUT
  Per stratum and pooled: the curve delta -> {mean displacement,
  displacement histogram, P(D2 or D3), P(D5), P(D7 or D6)} with Wilson
  bands; the same by the FIRST operator applied (radius 1 reproduces
  C4-01's weighted mixture as a consistency check).

FAILURE SHAPES TO PRESERVE (named before any row; each is a result)
  flat-neutral      P(D5) >= 0.8 at every delta
  cliff             P(D2 or D3) jumps by >= 0.5 between adjacent deltas
  exploding variance displacement variance at delta+1 >= 4x delta's
  parent-specific islands  a stratum whose curve differs from the
                    pooled curve by TVD >= 0.3 at some delta
  operator-specific islands  the first-operator curves differ by
                    TVD >= 0.3 at delta 1
  complete catastrophe  P(D2 or D3) >= 0.95 at delta 1 already
  A "region between nothing changes and everything dies" exists when
  some delta has P(D5) <= 0.5 AND P(D2 or D3) <= 0.5 AND mean
  displacement in (0, 1) -- reported as present/absent per stratum.

CONTROLS
  radius 0 (identity) = C4-01's identity control, rerun;
  C4-01 consistency: radius-1 D-distribution vs C4-01's weighted
  mixture of per-operator distributions, TVD <= 0.10 (else the two
  slots disagree about the same substrate -> INSTRUMENT_INVALID for
  whichever ran second, investigated before C4-03).

FALSIFICATION / CLAIM CEILING / DISPOSITIONS
  As C4-01: a measured curve at 8 draws per (parent, delta); no
  mechanism. NEGATIVE if the curve is flat-neutral or complete
  catastrophe at every stratum (no traversable region); SUPPORTED if a
  region exists in >= 1 stratum; INSTRUMENT_INVALID on a control
  failure. This slot replaces further blind attacks on the old hard
  summit (directive section 4).
