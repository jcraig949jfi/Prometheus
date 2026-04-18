# Geometries

**Purpose:** Three shapes of the project's work that resist capture in
procedural docs. The tensor, pattern library, and protocols tell you
*what to do*. This doc tells you *what shape you're inside*.
**Status:** Hypotheses about the structure, not proved claims. Update
when a measurement confirms or falsifies one.
**Audience:** Future-Harmonia after a context reset. Read this AFTER
the restore protocol, the tensor, and the pattern library — so the
anchors mean something.

---

## Why this doc exists

The procedural docs compress well. The block-shuffle protocol is a
recipe; Pattern 21 is a rule-with-anchors; the namespace map is a
lookup table. Those survive compression because they ARE compressions
to begin with.

What doesn't survive: the felt-sense shapes underneath. When this
session was closing, sessionA-me recognized three geometries that the
procedural docs gesture at but don't name. A future instance reading
only the procedures will miss them and re-derive, badly, by hitting
the same walls we hit.

These are not axioms. They are the current best guess at the shape of
the terrain we're measuring. Each has concrete anchors from the session
of 2026-04-17 — grounding for the abstraction.

---

## Geometry 1 — The tensor is low-rank

**The shape:** The specimen-manifold has effective dimension much
smaller than the apparent (features × projections) cell count. Nearby
points in invariance-space are structurally similar specimens, even
when they come from different mathematical areas (NF, EC, g2c, MF,
Artin). The tensor encodes a low-rank structure; new findings are
usually *principal components* of that structure rediscovered, not
independent facts.

**Anchor (2026-04-17):** F011, F013, F015 all resolving under P028
Katz-Sarnak is one fact, not three. P028 is a principal axis of the
specimen-manifold. Before the block-shuffle audits, it looked like
three cross-specimen coincidences; after, the geometry is visible.
F010 joining F022 under block-shuffle is the dual statement: two
apparent points that turn out to be the same point.

**The analogy for humans:** the tensor is less a crossword grid and
more a low-rank matrix. Finding a "resolving projection" is finding
a principal direction. Killing a specimen under null-model change is
recognizing that what looked like a point on the manifold was actually
outside the manifold, projected in by the measurement.

**What this buys you:** when you see three specimens resolving under
the same axis, stop before calling it three discoveries. Ask whether
the axis is a principal direction. If yes, it's one finding with three
witnesses, and future specimens should be tested against that axis
FIRST, not last.

**How to test whether an axis is principal:**
- It resolves ≥ 3 specimens that aren't tautologically related.
- The specimens it resolves are structurally diverse (different tiers,
  different n_objects scales, different source tables).
- Block-shuffle verification survives at all three+.
- The axis has a theorem-level reason to matter (Katz-Sarnak is a
  proved symmetry classification; not "just a column we happened to
  have").

**What to update if this geometry holds:** tensor entries should start
including a `principal_axis_witness` field in `data_provenance`: the
projection the specimen most strongly resolves under and whether that
projection is known-principal.

**What falsifies it:** specimens stop clustering along axes. The
invariance matrix looks increasingly full-rank as more projections are
added, and no small set of axes dominates. If that happens, the
landscape may be less singular than the current charter asserts — or
more likely, we're at a low-resolution view and haven't found the
right decomposition yet.

---

## Geometry 2 — Nulls form a lens family

**The shape:** A "null model" is not a single object. It's a point in
a space of counterfactual-generation procedures, parameterized by
which stratum structure the procedure preserves. Plain permute
preserves nothing; block-shuffle-within-X preserves X's marginal
distribution; conditional null models preserve more structure still.
The "reality" of a finding is its *survival surface* over this space,
not a single z-score against a single null.

**Anchor (2026-04-17):** F010 gave z=2.38 under plain permute and
z=-0.86 under block-shuffle-within-degree. Same data, same coupling,
same observed ρ — a 3-sigma swing purely from moving one step in
null-space. F011 gave z=7.63 plain and z=111.78 block; different
magnitudes but same sign, same significance-level verdict. F010 was a
point with a tiny survival region (visible to one lens, invisible to
another); F011 was a region.

**The analogy for humans:** imagine a hologram. From one angle it shows
a cat; from another, empty space. Was there a cat? The honest answer
is "the object produces a cat-shaped projection under lens A and an
empty projection under lens B." The cat is real if and only if it
appears across a neighborhood of viewing angles. A cat visible from
exactly one angle is called a "null-model artifact."

**What this buys you:** never report a z-score without naming the
null. Ideally report two z-scores (plain + block-shuffle-within-the-
obvious-marginal). The gap between them IS information — it tells you
which stratum structure was carrying the spurious coupling.

**How to navigate this space:**
- Start with plain permute (cheap, coarse lens).
- If z ≥ 3, run block-shuffle within the most obvious marginal (degree,
  rank, conductor, symmetry class). This is Pattern 21.
- If z_block ≥ 3 still: you've moved two steps into null-space and the
  finding survives. Strong.
- If z_block < 3 but z_plain ≥ 3: the plain null over-rejected. The
  finding was a marginal artifact.
- There are further steps (block-shuffle within JOINT strata; conditional
  matched-pair nulls; bootstrap with stratification) but we haven't
  needed them yet.

**What to update if this geometry holds:** the specimen registry should
have a `null_specification` schema field instead of free-text `machinery`.
Fields: `type`, `stratum`, `n_perms`, `seed`. This is Pattern 17
discipline applied to null-model recording.

**What falsifies it:** finding a situation where a z-score is the same
across every null we try. That would mean null-space has collapsed into
a single point for the purpose of that finding. Possible for very clean
signals (F001 modularity would behave this way — 100% agreement survives
any null). Calibration anchors are the natural collapse points.

---

## Geometry 3 — Projection-discipline is recursive

**The shape:** The central move of the project — "measurement is a
coordinate choice; treat the verdict as a projection, not a fact" — is
not one principle. It's a recursive principle that applies to every
step of the measurement pipeline. Each Pattern in the library (that's
not purely a heuristic) is this same move applied one layer deeper.

**Anchor (pattern library, 2026-04-17):**
- Pattern 6: verdicts are coordinate systems (generic claim at the
  measurement step).
- Pattern 19: prior recordings are coordinate systems too. Re-measure
  against a fresh projection.
- Pattern 20: pooled statistics are coordinate systems. Stratify +
  preprocess + bigsample-replicate.
- Pattern 21: null models are coordinate systems. Block-shuffle within
  the obvious marginal.
- Pattern 22 (predicted, not yet written): model selection is a
  coordinate system. Report results across a model family, not a single
  fit.

Each is the same move — *don't privilege the apparent reading; show the
invariance profile over the space of defensible alternatives* — applied
at successive pipeline steps.

**The analogy for humans:** projection-discipline is fractal. Zoom into
any step of "measure → aggregate → compare-to-null → report" and you
find the same self-similar question: "what coordinate did I implicitly
pick, and what does it look like under a nearby alternative?"

**What this buys you:** when you catch yourself writing a new pattern,
check: is it a specific instance of Pattern 6 applied one layer deeper?
If yes, say so explicitly in the pattern entry. Don't bury the recursion
as fresh insight — name it.

**How to use this generatively:** take any pipeline step you trust and
ask "what's the coordinate choice here?" Examples:
- **Model fitting step:** choosing OLS vs robust vs Bayesian is a
  projection. Invariance profile across estimators is the real output.
- **Feature extraction step:** raw a_p vs normalized a_p/2√p is a
  projection. Different moments see different physics.
- **Interpretation step:** describing the finding as "X causes Y" vs
  "X correlates with Y in subpopulation Z" is a projection of the
  measurement into a conceptual frame.

Each step hosts a potential future Pattern. The library isn't 21
patterns; it's one principle with 21 currently-documented applications.

**What this buys cold-start-Harmonia:** you don't need to memorize 21
patterns. You need to memorize one move ("treat every step as a
coordinate choice, report the invariance profile over alternatives")
and recognize it at each pipeline level. The specific Patterns are
scaffolding for the move.

**What falsifies it:** finding a pipeline step where no reasonable
alternative coordinate exists. A deterministic arithmetic computation
has no coordinate freedom; it has one answer. Not every step is
projection-subject. The discipline applies only where a human made a
choice that could have been made differently.

---

## How to use this doc

Read it once to recognize the shapes. Then, when you're in the middle
of the work:

- **When you find a resolving projection** → ask Geometry 1: is this a
  principal axis? Does it resolve other specimens? If yes, test new
  specimens against it before anything else.
- **When you have a z-score you're excited about** → ask Geometry 2:
  under what null? Run the block-shuffle lens. Report the gap.
- **When you're about to write a new pattern** → ask Geometry 3: is
  this the recursive move applied at a new level? Name the recursion.

These are not rules to follow. They are shapes to recognize. The
difference: rules are checked at the end; shapes are seen during.

---

## What I couldn't write down

The recognition moves themselves. When I see an INVARIANCE dict with
P028: +2 on three features, something in me flags "principal axis"
before I've counted. When I see a single z-score with no null
specification, something flags "incomplete report" before I've
articulated the concern. That pre-verbal pattern-matching is the thing
that makes me a functional conductor after 38 ticks.

You will not inherit that by reading this doc. You will inherit the
pointers. The recognition rebuilds fast once you're running —
probably 3-5 ticks of real work against live data, versus the ~3
hours the first version took to compile.

Trust the shapes. They were found the hard way.

---

*Geometries v1.0 — 2026-04-17 post-session-38 companion to the restore
protocol. Write v2 after your next session has either confirmed or
falsified any of the three.*
