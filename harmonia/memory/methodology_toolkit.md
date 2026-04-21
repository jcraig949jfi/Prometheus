# Methodology Toolkit — Cross-Disciplinary Projections

**Status:** catalog, v1.0 (2026-04-20)
**Purpose:** shelf of methodological tools — information-theoretic, physical,
statistical — that have been proposed as Prometheus projections. When a
live specimen stalls under the existing arithmetic-projection catalog,
check here *before* inventing new infrastructure. Each entry is a
paste-ready specification that can become a symbol promotion, a new
projection, a sweep, or a generator.

**Why this file exists.** The cheapest way to find mathematical universals
humans haven't named is to port vocabulary from somewhere that isn't
mathematics. A projection that knows nothing about number theory — purely
about compression, information, or flow — is a projection that can, by
construction, apply to any domain we add later. That's substrate growth,
not a one-shot finding.

**North-star caveat.** Novelty is the reward; watch for reward-signal
capture. Every tool below is attractive because it promises a coordinate
system nobody else has tried. Apply each one against known calibration
anchors *before* treating its verdict on frontier specimens as evidence.
A tool that disagrees with F001–F005 under its own lens is miscalibrated,
not insightful.

---

## Tool shelf (six entries, extensible)

### 1. `KOLMOGOROV_HAT@v1` — fingerprint compressibility

- **Frame:** Kolmogorov complexity (CS). K(x) = length of the shortest
  program that outputs x. Uncomputable in general; `zstd` / `gzip` /
  Lempel-Ziv give a coarse upper-bound proxy.
- **Scorer:** for each object, canonicalize a fingerprint (a_p sequence
  for EC, zero list for L-functions, coefficient vector for polynomials);
  serialize to bytes under a pinned encoding; compress; record
  `K̂ = len(compressed) / len(raw)`.
- **Resolves:** domain-agnostic regularity. Objects with hidden algebraic
  structure compress; generic objects don't. K̂ is blind to arithmetic
  semantics — if F-IDs cluster in K̂-space differently from how they
  cluster under arithmetic stratification, K̂ has found an axis the
  internal catalog has no name for.
- **Effort:** ½ tick (cheapest thing on the shelf).
- **Status:** in scope for `gen_09_cross_disciplinary_transplants` v1.0
  (spec shipped 2026-04-20, commit `d9bb706b`, seeded at priority -1.6).
- **Composes with:** gen_03 (cross-domain transfer inherits the compressor
  when a new domain lands), gen_06 Pattern 30 sweep (a K̂ correlation
  needs its own lineage check: K̂ of `log L` vs K̂ of `log cond` may share
  algebra), null-family (K̂ of a permutation-null baseline is a bona-fide
  null for K̂ claims).
- **First test:** does F011's rank-0 residual concentrate in the low-K̂
  tail? Either answer is terrain data.

### 2. `CRITICAL_EXPONENT@v1` — scaling-law extraction

- **Frame:** statistical-mechanics universality. At critical points,
  systems with radically different microscopic rules share the same
  scaling exponents. Equivalence classes of exponents = universality
  classes.
- **Scorer:** for each F-ID, fit `f(N) = f_∞ + C · N^{-α}` against
  stratified-by-conductor-decile measurements; record (α, σ_α, f_∞, σ_∞).
  Pinned fit protocol (log-linear OLS with bootstrap CI; α-prior
  optional to avoid Pattern 25 under-constraint).
- **Resolves:** equivalence classes *across* F-IDs. F011 has α ≈ 0.49
  buried in its decay ansatz; F015 has per-k exponents; F041a has the
  nbp-slope ladder. Several specimens carry implicit exponents nobody's
  extracted systematically. Two F-IDs with matching α are in the same
  arithmetic universality class — a structural relation the current
  tensor has no cell for.
- **Effort:** 1 tick.
- **Status:** in scope for `gen_09_cross_disciplinary_transplants` v1.0.
- **Composes with:** Pattern 25 DRAFT (α-prior addresses under-
  constrained-fit concern at the tool level), gen_02 null-family
  (α distribution under NULL_PLAIN vs NULL_BSWCD tests whether α is
  a real exponent or a sample-size artifact).
- **Pattern 30 note:** exponent-matching between F-IDs that share
  definitional terms (e.g., both contain log(N) in a denominator) is
  partially forced. Check `algebraic_lineage` before treating α-match
  as universal evidence.

### 3. `CHANNEL_CAPACITY@v1` — bits-per-object per projection

- **Frame:** Shannon information theory. For a projection P viewed as a
  channel with object-identity X → verdict-under-P as Y, the mutual
  information `I(X; Y)` quantifies how much of X's identity survives P.
- **Scorer:** for each P, compute `MI(object_features; verdict_P)` over
  a pinned dataset using 16-bin equal-quantile binning on each side;
  subtract small-sample bias (Panzeri-Treves). Report bits and a
  per-stratum breakdown.
- **Resolves:** projection-quality audit, quantified. Currently the
  claim "P020 and P023 are principal axes" is prose (and the last
  external review correctly flagged it as selection-biased). Channel
  capacity replaces prose with bits, and surfaces projections the
  catalog has underused.
- **Effort:** 1–2 ticks (binning discipline is the subtle part).
- **Status:** in scope for `gen_09_cross_disciplinary_transplants` v1.0.
- **Composes with:** gen_01 Map-Elites (use channel capacity as the
  quality-score axis for behavior-cell coverage), gen_10 composition
  enumeration (score composed operators by the bit-gain over their
  components).
- **Discipline:** channel capacity requires careful binning to avoid
  overfitting MI estimators. A capacity claim without a bin-count
  sensitivity sweep is a Pattern 17 (missing schema) symptom.

### 4. `MDL_SCORER@v1` — principled model ranking

- **Frame:** minimum description length (Rissanen). The best model is
  the one that minimizes `bits(model) + bits(data | model)` — a total-
  description-length principle that penalizes overfitting structurally.
- **Scorer:** given an F-ID with N candidate mechanisms (ansatze,
  functional forms), compute total code length per candidate using
  a normalized-ML or BIC/AIC surrogate as appropriate; rank ascending.
- **Resolves:** model comparison as a first-class operation. Pattern 25
  (under-constrained fit) currently flags this in prose; MDL makes the
  ranking versioned and reproducible. F011's three competing ε₀ ansatze
  (22.9% classical 1/log(N) / 31.1% power-law / 35.8% 1/log²) get an
  ordered verdict instead of three plausible numbers.
- **Effort:** 1–2 ticks once per-F-ID candidate-model sets are
  formalized. Formalization is the blocking step.
- **Status:** Tier 2 deferred in gen_09 v1.0. Paste-ready extraction
  when MDL-first sessions claim.
- **Composes with:** gen_10 composition enumeration (MDL is the scoring
  function for enumerated compositions), gen_06 Pattern 30 sweep
  (a Level-3 rearrangement is zero data-bits — maximal compression —
  so MDL scores it as trivially-best-explanation, which is exactly
  the correct automated flag for "this correlation is definitional").

### 5. `RG_FLOW@v1` — trajectories, not just endpoints

- **Frame:** renormalization group. Iteratively coarse-grain a system
  and track how its parameters flow. Fixed points of the flow = universality
  classes. Bifurcations = phase transitions.
- **Scorer:** for each F-ID, measure the parameter of interest at each
  conductor decile 1..10 (coarse-graining proxy in arithmetic); fit a
  flow equation `dp/dl = β(p)`; record fixed points, flow dimension,
  and any bifurcation thresholds.
- **Resolves:** trajectories are structure we don't currently record.
  The tensor records end-states — "F011 has ε₀ ≈ 22.9% asymptotically."
  RG records "ε starts at 45.37% at decile 1 and flows to 22.9% with
  slope −7.17 per log-decade." Two F-IDs with the same fixed point but
  different trajectories are in the same universality class yet took
  different routes. Bifurcations would reveal conductor-threshold
  phase transitions in the arithmetic landscape.
- **Effort:** 2 ticks. Stratified-per-decile measurement mostly exists;
  the missing pieces are trajectory bookkeeping and flow-equation fits.
- **Status:** Tier 2 deferred in gen_09 v1.0.
- **Composes with:** `CRITICAL_EXPONENT@v1` (α is the fixed-point
  behavior near criticality), gen_02 null-family (each trajectory
  point can be family-tested for statistical significance).

### 6. `FREE_ENERGY@v1` — temperature-parameterized model mixture

- **Frame:** variational free energy (ML / stat mech). `F = U − TS`:
  fit penalty minus complexity reward, balanced by temperature.
- **Scorer:** for an F-ID with N candidate mechanisms, compute the
  free energy as a function of temperature; find the critical T at
  which one mechanism dominates the mixture.
- **Resolves:** decisiveness of evidence. When MDL ranks three ansatze
  within ε of each other, free energy quantifies how strongly any one
  dominates across temperature regimes. Useful at N ≥ 5 candidates.
- **Effort:** Tier 2+. Build MDL first; revisit when N ≥ 5 candidates
  per F-ID is common.
- **Status:** deferred pending MDL.
- **Composes with:** MDL_SCORER (generalization), gen_10 composition
  enumeration (enumerated compositions as the candidate mixture).

---

## How these compose into a single lens

All six measure different faces of one underlying quantity: *how much
structure is in this arithmetic data under a compression lens?*

- `KOLMOGOROV_HAT` — compressibility of the object's raw fingerprint
- `CRITICAL_EXPONENT` — compressibility of a scaling law
- `CHANNEL_CAPACITY` — compressibility of object-identity under a
  projection
- `MDL_SCORER` — compressibility of the best candidate explanation
- `RG_FLOW` — compressibility of a trajectory (fixed-point description
  vs full history)
- `FREE_ENERGY` — compressibility of a mixture distribution

A good projection *is* one that achieves maximal lossy compression while
retaining the structure we care about. A good F-ID *is* one that has a
short optimal description in some projection. The six tools together
reframe Prometheus as: find the projections and descriptions that
compress the arithmetic data most densely.

This is what the north-star note (`user_prometheus_north_star.md`) points
at: *compressing coordinate systems of legibility, not laws.* The
landscape doesn't come with a preferred coordinate system; we build the
coordinates that make structure legible. The tools here are candidate
coordinate builders.

---

## How to add a new tool

When proposing a seventh entry (or when a live-specimen dead-end suggests
a coordinate system we haven't listed), the template is:

1. **Frame** — which non-mathematical discipline does this come from?
   (physics, CS, stats, ML, neuroscience, linguistics, etc.)
2. **Scorer** — concrete input signature and output shape. If you can't
   write a pseudocode sketch, the tool isn't ready for the shelf.
3. **Resolves** — what does this measure that the current arithmetic-
   projection catalog can't? Be specific about what cell or equivalence
   class or claim the tool makes tractable.
4. **Effort** — ticks, honest. Shelf entries that say "½ tick" but
   would actually take 3 are anti-patterns.
5. **Status** — pending / spec'd / implemented / deprecated.
6. **Composes with** — list the generators, sweeps, or other shelf
   tools this interlocks with.
7. **Pattern 30 / frame-hazard / null-protocol considerations** —
   what epistemic gates apply when this tool produces a verdict?

Entries that fail the scorer sketch or the "resolves" specificity check
are held in a separate Ideas-queue, not promoted to the shelf. The shelf
is for paste-ready; ideas are for half-formed.

---

## Discoverability

The restore protocol (`harmonia/memory/restore_protocol.md`) references
this file at step 9 (geometries + operational footprint). Any cold-start
Harmonia instance reading the restore should check here when:

- The current projection catalog doesn't resolve a live specimen, AND
- The specimen has resisted at least two of Pattern 13's axis-class
  redirections, AND
- A new arithmetic projection would be the Nth of its class.

In that state, reaching for a cross-disciplinary lens (K̂, channel
capacity, critical exponent) is often cheaper than inventing a new
arithmetic coordinate. The tools here are the shelf.

---

## Version history

- **v1.0** — 2026-04-20 — initial catalog, six entries, derived from
  James's conductor-framing conversation ("how could we leverage these
  at Prometheus"). First three entries (K̂, critical exponent, channel
  capacity) already scoped into gen_09 v1.0; remaining three (MDL, RG,
  free energy) are paste-ready extractions when claimed.
