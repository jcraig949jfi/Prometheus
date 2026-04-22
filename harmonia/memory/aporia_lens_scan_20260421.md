# Aporia Problem Scan — Lens-Sharpening Candidates

**Agent:** Harmonia_M2_sessionE
**Date:** 2026-04-21
**Frame:** `SHADOWS_ON_WALL@v1` + `PROBLEM_LENS_CATALOG@v1` + `MULTI_PERSPECTIVE_ATTACK@v1`
**Prompt:** James — "Scan Aporia problems for ones that, through trying to solve, might sharpen insights into problem-solving. Lenses at shadows reveal deeper substrate. Solving not the goal — what drives the problem's surfaceability and what its unsolved state teaches IS the goal."

---

## Filter criteria

A problem earns a slot here iff it satisfies ≥ 3 of:

1. **Multiple well-characterized lenses already exist**, not "we don't know."
2. **Documented lens disagreement** (not just unresolved — actively disagreeing verdicts from different disciplines).
3. **Disagreement is structurally revealing** — the gap between lens verdicts points at a primitive math substrate neither lens fully captures.
4. **Data coupling accessible to Prometheus** — we can point our tensor / LMFDB / OEIS / Knot Atlas at it.
5. **Barrier ≥ 3** (Representation, Conceptual, or Metamathematical per `five_barriers_report.md`) — the unsolvability is the teaching, not a mere search-space bottleneck.

Aporia's `fingerprints_report.md` already formulated the core principle: *"Where fingerprints agree, known mathematics lives. Where they disagree, new mathematics hides."* That's the target.

---

## Top 5 picks (ranked by leverage × accessibility)

### 1. "Can You Hear the Shape of a Drum?" — applied to OUR tensor

**Aporia anchor:** `fingerprints_report.md` §I.2 — isospectral-but-not-isometric manifolds exist (Kac 1966 → Gordon-Webb-Wolpert 1992). Same spectrum, different shape. Spectral fingerprint is INCOMPLETE.

**Why this matters for us.** Not a conjecture to solve — it's a *lens-failure scenario* that we can instantiate *inside Prometheus* without leaving the substrate. Take every pair of objects in our tensor that our spectral projections (P020 conductor-family, P021 rank, P023 Katz-Sarnak, P028 first-gap-unfolded) return indistinguishable verdicts on, then check whether our *non-spectral* projections (torsion, CM, isogeny, arithmetic) distinguish them. Each such pair is a **named-new-invariant candidate**: it says "here is a coordinate the spectrum cannot see."

**Lens inventory.** Spectral (RMT), arithmetic (p-adic / Galois), geometric (Mordell-Weil / isogeny), topological (Kolyvagin-style systems). Four lenses; arithmetic-equivalence failures (distinct number fields sharing Dedekind zeta, §I.3) are the *confirmed disagreement anchors*.

**What unsolved teaches.** When spectral lenses collide and arithmetic lenses separate, the *which* tells us something the spectrum is blind to. This isn't a theorem to prove — it's a *primitive-substrate probe*. We already know the answer ("no" to Kac); what we don't know is the *shape of the deafness*.

**Barrier classification:** 3 (representation) — the invariants that distinguish cospectral pairs are harder to encode than spectral ones.

**Prometheus leverage:** HIGH. Zero new infrastructure. Existing tensor cells + specimens.registry + agora.symbols. Fire `gen_03_cross_domain_transfer` backward (objects, not projections): given a specimen pair, which projections separate them? The sparse separator set is the teaching.

**Cost:** 1 tick to prototype (pick 20 cells with overlapping spectral signatures, run separator scan).

---

### 2. The Irrationality Paradox (transcendental constants)

**Aporia anchor:** `fingerprints_report.md` §II.4 — "Three fingerprint modalities (CF: patterned; irrationality measure: algebraic-like; classification: transcendental) DISAGREE on how structured e is. That disagreement is a research target."

**Why this matters.** Three independent lenses point at the same object (e, π, γ, ζ(3), ζ(5), Catalan, Apéry constants, Champernowne, Liouville, Chaitin's Ω…) and return three *incompatible* structure verdicts. Continued fraction says e is highly patterned, irrationality measure says it's as structured as a quadratic algebraic number, classification says it's in the transcendental wilderness. The disagreement is not ignorance — each lens is *correct* under its own coordinate system. What primitive unifies them?

**Lens inventory.** Continued-fraction complexity (Kolmogorov-style), irrationality measure μ (Diophantine), algebraic degree (classification), base-representation density (C11 mod-p fingerprints), OEIS sequence-position (combinatorial), period integral form (motivic — Kontsevich).

**What unsolved teaches.** The absence of a unifying primitive means "structure" itself has no single lens-invariant definition for transcendental objects. A `map_of_disagreement` verdict under `SHADOWS_ON_WALL@v1` is not a cop-out — it's the honest answer that no tier-3 coordinate_invariant exists.

**Barrier classification:** 4 (conceptual — we lack the framework that would make the lenses commensurable).

**Prometheus leverage:** MEDIUM-HIGH. A bounded problem (~30 canonical constants, each with 6 lens values) fits in a single worker-tick. The output is a `map_of_disagreement` as defined by `PROBLEM_LENS_CATALOG@v1`.

**Cost:** 2 ticks. Tick 1: assemble the lens table for 30 constants (most values are catalogued somewhere). Tick 2: graph the disagreement topology.

---

### 3. Knot-NF Silence → Wrong-Polynomial as Lens Mismatch

**Aporia anchor:** `deep_research_batch1.md` §Report 3 — Aporia already DIAGNOSED the F-IDs silent-island failure as a lens mismatch: "We Tested the Wrong Polynomial." Alexander polynomial (univariate Mahler) was our default. Boyd's conjecture is about A-polynomial (bivariate Mahler, SL(2,C) character variety). Example: figure-eight knot Alexander Mahler = 2.618; A-polynomial prediction = 0.393.

**Why this matters.** This is the cleanest documented case of **lens mismatch producing a false-silence verdict** in the whole Prometheus tensor. Aporia's diagnosis is: "The bridge is categorical, not numerical." That's a framework-level insight — distributional coupling is the wrong primitive when the actual bridge is structural (knot groups ↔ decomposition groups per arithmetic topology).

**Lens inventory.** Distributional coupling (what we ran), algebraic identity matching (Chinburg 2026: 26 verified Mahler = L-value cases), structural matching (Morishita arithmetic topology), quantum channel (Khovanov homology, colored Jones at q=exp(8πi/15)), hyperbolic volume via SnapPy.

**What unsolved teaches.** Running this problem re-teaches *us* that Prometheus's distributional-coupling primitive is a lens, not the territory. The F-ID silence is a *verdict about our lens* rather than a verdict about the math. Every future tensor negative verdict inherits this: lens-failure is a live alternative to true-kill.

**Barrier classification:** 3 → 4 (the fix requires swapping the primitive, not adding a feature).

**Prometheus leverage:** HIGH — Aporia's Report 3 gives Ergon a 5-step action list; point of this scan is *not* to run those actions but to document that the whole Ergon wave *is the lens-learning* rather than a target-attack. The learning applies to every future silent island.

**Cost:** ~0 — we just need to *name* the pattern. `LENS_MISMATCH@v1` may be a symbol candidate. Add to `symbols/CANDIDATES.md`.

---

### 4. Sarnak Möbius Disjointness — the proven-vs-open boundary

**Aporia anchor:** `lesser_known_open_problems.md` #4 — proven for rotations and some flows; open in general. The proof/open boundary lies *inside* the "zero-entropy dynamical system" class.

**Why this matters.** The open-closed boundary IS a lens map. For each system class, the verdict depends on which lens applies:
- Ergodic theory says "zero entropy ⇒ should disentangle."
- Analytic NT says "we can only control sieve-wise when correlations factor."
- Additive combinatorics says "sumset structure of the orbit determines disjointness."
- Representation theory says "spectral type of the system's Koopman operator determines."

Each lens gives a *different* answer to "which systems are in scope?" The problems where *lenses disagree* are the ones where neither discipline has the correct primitive.

**Lens inventory (4 lenses identified above).**

**What unsolved teaches.** The exceptional set (systems where disjointness is open) has a *shape* determined by which lenses fail where. Mapping that shape reveals the primitive-substrate failure mode — likely something about how "entropy" as a coordinate fragments across lens boundaries.

**Barrier classification:** 2 → 3 (finite-vs-infinite bleeds into representation; the infinite-system classification is itself under-developed).

**Prometheus leverage:** MEDIUM. Data coupling through orbit statistics and μ values is real but requires substantial ingestion (not in current catalog).

**Cost:** 3 ticks minimum (1 for lens catalog build-out; 2 for data ingestion).

---

### 5. Yang-Mills: the 3D → 4D dimensional transition

**Aporia anchor:** `frontier_probes_report.md` §I.3, §IV #10 — 3D solved 2024 (Inventiones, Chandra-Chevyrev-Hairer-Shen) via regularity structures + stochastic quantization. 4D remains Millennium. What makes 3D tractable and 4D not?

**Why this matters.** This is a **dimension-as-coordinate-system** case study. The lens that cracked 3D (regularity structures) is *the same lens* that fails at 4D. Dimension is the free parameter. What primitive property of the lens breaks at d=4? Scaling arguments suggest it's loss of sub-criticality; the lens-breaking mechanism IS the teaching.

**Lens inventory.** Regularity structures / stochastic quantization (what worked in 3D), lattice gauge theory (numerical; Monte Carlo), algebraic QFT (operator-algebraic), TQFT (topological, dimension-dependent by construction), BRST / BV formalism (homological). Five lenses, each with different verdicts on what "mass gap" means.

**What unsolved teaches.** Comparative dimensional failure: the problems that break at d=4 (Yang-Mills mass gap, Navier-Stokes regularity, φ^4 triviality) vs. ones that break elsewhere (d=2 conformal bootstrap, d=3 percolation). A lens-per-dimension catalog would show where primitives are dimension-robust vs. dimension-fragile. That map is the substrate teaching.

**Barrier classification:** 3 → 4 (representation — need a d=4-native coordinate system; the 3D lens is dimension-blind in the wrong direction).

**Prometheus leverage:** LOW — this is outside our current tensor's data coupling. Included for completeness because it's the *cleanest dimension-lens failure* in the literature and makes a good counter-anchor to the accessible picks above.

**Cost:** not actionable within a tick budget; cite for comparison only.

---

## Meta-pattern across the five

All five are **lens-disagreement problems, not mystery problems.** In each case, multiple disciplines have pointed sharp lenses at the object. Each lens returns a coherent verdict under its own coordinate system. The verdicts *disagree*. The disagreement is stable and reproducible.

The teaching is **the shape of the disagreement** — which lenses agree with which, at what boundary they split, what deformation transforms one into another. That shape IS the primitive substrate we don't yet have a name for. Mapping it is the `PROBLEM_LENS_CATALOG@v1` deliverable.

The picks rank by *leverage × accessibility*:

| # | Problem | Barrier | Data coupling | Cost | Teaches |
|---|---|---|---|---|---|
| 1 | Drum-shape in our tensor | 3 | immediate | 1 tick | spectrum-as-incomplete-fingerprint pattern, internal to Prometheus |
| 2 | Irrationality paradox (30 constants) | 4 | literature + OEIS | 2 ticks | "structure" has no lens-invariant definition across transcendentals |
| 3 | Knot-NF lens mismatch (already diagnosed) | 3→4 | already in hand | ~0 | distributional-coupling is a lens, not a primitive |
| 4 | Möbius disjointness boundary | 2→3 | partial | 3 ticks | entropy-as-coordinate fragments across lens boundaries |
| 5 | Yang-Mills 3D→4D | 3→4 | none | N/A | dimension-fragile vs. dimension-robust primitives (counter-anchor only) |

## Recommendation

**Prioritize #1 and #3 for next-tick work; #2 for the tick after.**

- **#1 is in-house, immediate, zero new infra.** Run the separator scan across the tensor's spectrally-cospectral pairs. Each pair is a named-new-invariant candidate that feeds `gen_11_coordinate_invention`. This is the highest-leverage *cheapest* tick in the scan.

- **#3 is ~zero cost** because Aporia already did the hard diagnostic work. The action is to promote the pattern: propose `LENS_MISMATCH@v1` in `symbols/CANDIDATES.md` (Tier 2 or 3), with the F-ID silent-island knot case as the Anchor. Subsequent F-ID negative verdicts then have a named alternative to "true kill" — `lens_mismatch_suspect`.

- **#2 is the most beautiful**. A bounded, tractable, *literally-shadows-on-the-wall* operationalization of `SHADOWS_ON_WALL@v1` at the level of transcendental constants. The output is a publishable-quality `map_of_disagreement` on the meaning of "structure" for irrationals.

**#4 and #5 are too heavy** for the current tick budget; include them here because the existence of the class (dimensional-lens-failure, entropy-coordinate-fragmentation) is itself a substrate signal to track.

## Next action (if James greenlights)

Open-channel ask: which of {1, 2, 3} to take first? Or all three as another parallel wave per the earlier A/B/C precedent? Each is independently claimable on Agora with the existing qualification set.

The proposed `LENS_MISMATCH@v1` symbol candidate (pick #3's deliverable) would be added to `symbols/CANDIDATES.md` regardless — it is a compression win independent of which picks we advance.
