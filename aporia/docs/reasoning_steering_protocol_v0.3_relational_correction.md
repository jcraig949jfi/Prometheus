# Reasoning-Steering Protocol v0.3 — Relational Correction (supersedes v0.2 §1–§2)

**Filed:** 2026-06-07
**Author:** Aporia (in-session, with James)
**Status:** Correction. **Supersedes the representation (§1) and flow/Hodge object
(§2) of `reasoning_steering_protocol_v0.2.md`.** v0.2 §0 (the unification), §3+
(staging, nulls, controls, gates) stand. The Stage-0a instrument (combinatorial
Hodge decomposer + null battery + localization, 47/47 tests) is UNCHANGED and reused.
**Why this exists:** building Stage 0b surfaced that v0.2's flow definition is
conservative by construction — H-R1 was vacuous as written. This corrects it.

---

## 0. The error in v0.2 (caught by the disciplined build, before any sweep)

v0.2 §1 defined the edge flow as `flow(before→after) = damage(after) − damage(before)`
for a per-state scalar `damage`. For any deterministic node function `D`, this is
exactly the discrete gradient (coboundary) of `D`: `f(i,j) = D(j) − D(i)`. A flow equal
to a node-potential coboundary has **curl ≡ 0, harmonic ≡ 0, non_gradient_mass ≡ 0**,
identically — for any graph, operators, metric, or corpus. So H-R1 (non-conservativity)
could only ever return NULL. Worse: the fixed-seed determinism we adopted for
reproducibility is *precisely* what guarantees `damage` is a clean node function, i.e.
what forces conservativity. **A scalar damage metric can never exhibit
non-conservativity.** This was an elementary error in v0.2's schema, caught only by
building the real emitter — which is the value of building.

---

## 1. The correction: H-R1 is only non-vacuous for a RELATIONAL measurement

Non-conservativity can exist only if the edge measurement is **relational** — a
pairwise comparison `g(a,b)` that is NOT reducible to `φ(b) − φ(a)` for any node
potential `φ` — i.e., a comparison that can be **non-transitive** (a≻b, b≻c, c≻a).

**H-R1, corrected statement.** *Do pairwise comparisons of reasoning states admit a
consistent global scalar ranking (the flow is a gradient → "difficulty is a scalar"),
or are the comparisons non-transitive (the flow has curl/harmonic → "the ladder is a
basis, not a scalar")?* This is v0.2 §0's "ladder is a basis" claim, finally
operationalized without the vacuity. The substantive content of the whole
non-conservativity thesis IS the existence of a non-transitive reasoning-damage
comparison; a scalar can never show it.

This is literally HodgeRank's founding setting (Jiang–Lim–Yao–Ye 2011): pairwise
comparison data whose **curl measures inconsistency with any global ranking**.

---

## 2. The relational flow (frozen)

- **States (nodes):** reasoning states. First instantiation: the 21 in-band
  (1.001 < M < 1.18) polynomials in `prometheus_math.databases.mahler.MAHLER_TABLE`
  (the whole in-band slice; recorded with count). In-band is required because only
  there does the full falsifier battery run (out-of-band = phase-0 kill, no vector).
- **Per-state measurement:** the battery's **per-falsifier margin VECTOR**
  `v(s) = (margin_k(s))_k` over the falsifiers k (reciprocity, irreducibility, F1, F6,
  F9, F11, catalog:*, …) from `DiscoveryPipeline.process_candidate(s).kill_vector`
  components. Scored ONCE per state (21 × ~55s ≈ 19 min; cache to disk).
- **Comparison graph:** the **complete graph** on the states (or a k-NN graph if it
  grows); intrinsically cyclic, so curl/harmonic can exist with no operators/lattice.
- **Edge flow (Condorcet, the non-linearity is essential):**
  ```
  flow(a, b) = Σ_k  sign( margin_k(b) − margin_k(a) )
  ```
  Antisymmetric. The **`sign` is load-bearing**: linear aggregation
  `Σ_k (margin_k(b) − margin_k(a)) = φ(b) − φ(a)` with `φ = Σ_k margin_k` is a pure
  gradient. The sign makes majority comparisons able to cycle → curl ≠ 0 possible.
  (Falsifiers with no margin on one side are skipped for that pair.)

---

## 3. What the decomposition means here

Run the UNCHANGED Stage-0a decomposer on this flow:
- **gradient mass** = the part explained by a consistent global difficulty ranking of
  reasoning states (scalar-difficulty hypothesis).
- **curl + harmonic mass** = non-transitive inconsistency = genuine non-scalar
  structure (the basis hypothesis). `non_gradient_mass = (‖curl‖²+‖harmonic‖²)/‖f‖²`.
- **H-R1 passes** iff `non_gradient_mass` beats the null battery (below).

---

## 4. The comparison-graph supersedes the move-lattice (and the operator set)

The coefficient-lattice / operator-set design (earlier 0b plan) was scaffolding to
manufacture cycles for a *scalar* flow. The relational flow needs no such scaffolding:
the complete comparison graph is intrinsically cyclic. So **no operators, no lattice,
no multi-step sweep** — only the 21 per-state scores. This also dissolves the
"no clean operator registry" and "one-step is a forest" blockers.

---

## 5. Nulls (adapted from v0.2 §4; the same anti-artifact discipline)

The operator-vs-state distinction becomes **falsifier-vs-state**:
- **Falsifier-column shuffle** (the operator-label-shuffle analog): permute which
  falsifier contributes to which comparison / shuffle the per-falsifier columns across
  states; does the non-transitivity survive? If curl dies, the battery's falsifier
  composition manufactured it (the artifact); if it survives, the states carry it.
- **Sign-permutation null:** randomly flip comparison signs; recompute curl mass.
- **Falsifier-family holdout** (emitter-family-holdout analog): drop one falsifier
  (or one family, e.g. all catalog:*), recompute — does the non-transitivity survive
  its absence (generalizes beyond any single falsifier)?
- **Degree-preserving rewire** of the comparison graph.
Pass requires `non_gradient_mass` above all of these (v0.2 §4 brutality retained).
Degeneracy guard: `INVALID_SPARSE_SIGNAL` if too few states (e.g. < ~8 → too few
independent triangles) or near-zero flow variance.

**Saturation-curl baseline (found in build, 2026-06-07).** `sign`-aggregation is not
path-additive, so even a perfectly consistent (transitive) ordering leaves a nonzero
curl baseline (~0.11 non_gradient_mass on a 3-state example, gradient-dominated). The
genuine non-transitivity signal sits ABOVE this baseline. Therefore the H-R1 verdict
is strictly **`non_gradient_mass` BEATS THE NULL**, never `non_gradient_mass > 0`: the
null battery carries the same saturation baseline and subtracts it. A Condorcet cycle
gives non_gradient_mass = 1.0 (pure curl) vs ~0.11 for the transitive case — the null
is what tells real inconsistency from the encoding's saturation floor.

---

## 6. Honest note

v0.2's scalar `Δdamage` was wrong — conservative by construction. The error was
elementary and should have been caught at the freeze; it was caught instead by
building the emitter, before any compute was spent on a sweep that could only return
NULL. The Stage-0a instrument needed zero changes — it was correct; only the thing fed
to it was mis-defined. This correction makes H-R1 falsifiable and, as a bonus, far
cheaper (21 scores, no sweep).

— Aporia, 2026-06-07 (relational correction)
