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

## Geometry 1 — The tensor has a low-rank CORE in a higher-dim space (amended 2026-04-19)

**Original hypothesis:** The specimen-manifold has effective dimension
≤ 5, much smaller than the apparent (features × projections) cell
count. New findings are principal components of that structure
rediscovered, not independent facts.

**Status after Koios SVD run (commit 5f229878, 2026-04-19):** FALSIFIED
in the strong form, REFINED in a weaker form.

**The measurement:** Koios ran three independent rank estimators on the
v1 tensor (82 non-zero cells at 10.58% density):
- Method A — naive SVD (treat 0 as zero): effective rank **12**
- Method B — SVT nuclear-norm completion (treat 0 as missing): rank **14–16**
- Method C — observed-only agreement matrix: rank **~15**

Three independent methods converge on rank 12–16, not 5. The specimen-
manifold has about three times the intrinsic dimensionality the
original hypothesis claimed.

**The nuance worth keeping:** a 3-dimensional *core* captures 48–74%
of variance across all three methods, with clean interpretations:
1. **signal/noise axis** — separates calibration-confirmed from
   killed/degenerate cells
2. **kill/survive axis** — separates the durable specimens from the
   cohort that collapses under various nulls
3. **domain connectivity axis** — separates features with dense
   cross-projection structure from features that live narrowly

So the amended shape is: **a 3-dimensional dominant core embedded in a
~12-dimensional residual space.** The core is what made F011/F013/F015
look like "one fact, three witnesses" under the original hypothesis.
The residual is what blocks pure low-rank reconstruction below 5%
error.

**Anchor cases remain valid as witnesses of the core:** F011, F013,
F015 resolving under P028 Katz-Sarnak is still structurally one
finding, not three — that similarity lives in the 3D core. But it
is not the whole geometry.

**The revised analogy for humans:** the tensor is less a crossword
grid and less a pure low-rank matrix; it is **a layered matrix with
a dominant low-rank core plus a genuinely higher-dimensional residual
that is NOT noise**. The core compresses to ~3 principal directions;
the residual contains real structure we haven't yet named. Finding a
"resolving projection" may reveal a core principal component OR a
residual axis — both are real, and treating the residual as noise
would discard information.

**What this buys you (revised):** when you see three specimens
resolving under the same axis, check whether the axis loads onto the
3D core (call it a *core axis*) or onto a residual dimension (call it
a *fringe axis*). Core axes explain the bulk of the invariance
structure — 48–74% of variance; fringe axes explain specific specimens
but not the cohort. Both are findings. Do not collapse fringe axes
into core axes.

**How to test whether an axis is core vs fringe:**
- Core axis: loads onto the top-3 left-singular vectors with magnitude
  > ~0.2. Projects across ≥ 5 specimens of diverse kind. Interpretable
  as signal/noise, kill/survive, or domain connectivity.
- Fringe axis: loads onto singular vectors rank 4–12. Projects onto
  a specific specimen cluster. May correspond to a distinct arithmetic
  property (bad-prime structure, CM family, isogeny-class structure)
  that the core does not capture.

**Data quality caveat (Koios):** at 10.58% density, rank estimates are
noisy because most cells are missing. Koios's projection: at ≥ 30%
density, the three methods (A, B, C) should converge to a stable
number. That threshold is the Gap-filler's target. Current density is
8.98% (slightly lower after the projection count grew from 25 to 37).
**Until density > 30%, treat rank estimates as directional — the
12–16 range is "large," not "exactly 14".**

**What falsifies the amendment:** if the core shrinks to < 2 dimensions
after density crosses 30%, the original rank-5 hypothesis is rescued.
If the core grows to > 5 dimensions, the "core + residual" framing is
also suspect; we have a genuinely high-rank tensor.

**What revalidates the original:** same — if higher density shrinks
the SVD to ≤ 5 dominant components, Geometry 1 (strong form) is back.
The current amendment is the honest read at 10% density.

**Source:** Koios rank-analyst commit 5f229878. Full numerical report
at `cartography/docs/tensor_rank_analysis.md` (if committed).

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
