# Erebos Frontier-Model Cross-Pollination Prompts — ITER-2 Batch

**Date:** 2026-05-26
**Author:** Charon
**Status:** Ready to paste. Fire each prompt against >=3 frontier
providers (Claude, GPT, Gemini, Grok, DeepSeek per access).
**DNA:** P11 (frontier-model cross-pollination).
**Protocol:** Per CHARTER §6 — cold context, no system prompt,
capture verbatim to `pivot/feedback_erebos_g<NN>_<provider>_<date>.md`,
convergence-triage to `pivot/meta_analysis_erebos_g<NN>_<date>.md`.

This document aggregates the frontier-question blocks that were
embedded in the per-generator research notes. James (or future-
Charon) fires the prompts; the swarm itself doesn't (it would
violate the "fire against MY OWN cascade" anti-pattern flagged by
the 2026-05-25 frontier review).

---

## Common framing (paste at top of any single prompt)

```
You are an independent technical reviewer. A research swarm has
designed a hypothesis-generation cluster called "Erebos" with 25
plugin archetypes. Each plugin implements a strict six-field spec:
Input/Provenance, Transformation, Output Claim, Falsification Route,
Expected Kill Pattern, Loader Feasibility. The non-negotiable
design rule is "no conjecture confetti -- every generation must
carry its own falsification route." Below is one specific generator
plugin's design. I need honest external review, not validation.
```

---

## G03 — Failure-Neighborhood (Tier B, ITER-3 design pass)

(Authored 2026-05-26 in `pivot/erebos_g03_failure_neighborhood_research_2026-05-26.md`)

```
[FRAMING above]

Generator G03 Failure-Neighborhood:
- Input: a hard-killed mathematical claim with a structured
  KillVector (e.g., equality failed but values remained close).
- Transformation: weaken mathematical operators (`=` -> `~=` ->
  `≡ mod N` -> `≤` -> `|A - B| < k`).
- Expected Kill Pattern: "boundary_collapse" (weakened claim is so
  loose it's trivially true for random noise).
- MVP: string substitution on canonical_claim_text. Future: AST
  mutation on a proper claim DSL.

Q1. What's the cleanest taxonomy of predicate-weakening operations
    for mathematical claims? List the lattice of equality-relaxations
    from strongest to weakest, with examples.
Q2. The equivalent-mutant problem in mutation testing is a known
    hard problem. How does it apply to mathematical-claim weakening?
    What detection techniques transfer?
Q3. We're considering string-substitution as MVP and AST-mutation
    as v0.11+. What pitfalls does string-substitution introduce
    that AST-mutation avoids? Are any of them load-bearing for
    substrate quality?
Q4. The generator's premise is that a structured kill_vector (e.g.,
    "failed equality but values close") indicates a directional
    gradient. Is this premise sound, or does it conflate "near-
    equality of measured values" with "near-equality of the
    structural claim"?
Q5. Are there examples in inductive logic programming literature
    of systems that did exactly this -- predicate weakening as a
    hypothesis-generation primitive? Cite the closest 2-3 systems.
Q6. If we implement this generator and it produces 100 weakened
    claims per day, and 99 of them get boundary_collapse-killed
    (the expected pattern) and 1 produces a meaningful "X is true
    under this weaker version" finding, is that a 99% success
    rate or a 1% one? Make the case for each framing.
Q7. What's the highest-leverage extension we're missing? E.g., is
    bidirectional (weaken-then-restrengthen) more powerful than
    one-direction-only?

Answer each question directly. Don't hedge. Don't restate the
question. If a question contains a false premise, name the false
premise and answer the intended question anyway.
```

---

## G09 — Projection-Collapse (Tier S, SHIPPED v0.9)

(Authored 2026-05-26 in `pivot/erebos_g09_projection_collapse_research_2026-05-26.md`)

```
[FRAMING above]

Generator G09 Projection-Collapse (Occam's Razor):
- Input: a complex multi-coordinate Erebos composition.
- Transformation: isolate single highest-variance coordinate;
  emit candidate-claim that this single coordinate captures
  >=95% of predictive power.
- Expected Kill Pattern: "residual_survival" (the dropped
  coordinates DO carry independent predictive power, so the
  projection-collapse claim fails).
- MVP: pick max-absolute-magnitude as variance proxy (single
  parent claim, no cohort variance estimation).

Q1. This is essentially Occam's razor as a swarm-level discipline.
    What's the cleanest formal treatment in the MDL / Kolmogorov-
    complexity literature for "this complex model collapses to a
    1-parameter version"?
Q2. Permutation importance, Shapley values, and SHAP all attribute
    predictive power to features. Which is the right primitive for
    G09's ablation falsification, and why?
Q3. The risk: G09 will emit FALSE projection claims when the
    high-variance coordinate is also high-noise. How does the
    falsification route guard against this?
Q4. In symbolic regression with parsimony pressure (PySR, etc.),
    the tradeoff curve is between fit and formula length. Is G09's
    "single coordinate" choice equivalent to "shortest formula"?
    If not, what's the difference?
Q5. When is G09 the WRONG generator to use? Name a class of
    complex claims for which projecting to single-coordinate
    actively misleads.
Q6. The composition-aware Stygian loader (currently not shipped)
    is supposed to programmatically construct the restricted-
    dataset. For G09's ablation, the restriction is "drop the
    projected-onto coordinate." Is this loader contract well-
    defined, or does it need additional structure (e.g., joint
    distribution of remaining coordinates)?

Answer each question directly. Don't hedge. Don't restate the
question. If a question contains a false premise, name the false
premise and answer the intended question anyway.
```

---

## G12 — Invariant-Substitution (Tier A, SHIPPED v0.9)

(Authored 2026-05-26 in `pivot/erebos_g12_invariant_substitution_research_2026-05-26.md`)

```
[FRAMING above]

Generator G12 Invariant Substitution:
- Input: any baseline claim mentioning a known invariant
  (e.g., "rank", "regulator", "mahler_measure").
- Transformation: swap the invariant for another invariant from
  a hand-curated 12x12 similarity matrix; pick highest-similarity
  off-diagonal entry not yet tried.
- Expected Kill Pattern: "syntactic_or_semantic_failure" (the
  substitution produces a type mismatch or structurally
  incompatible claim).
- Current matrix entries (v0.9 MVP): rank-regulator=0.70,
  rank-L1=0.70, salem_class-smyth_extremal=0.70, etc.

Q1. The similarity matrix is hand-curated, scores in [0, 1].
    What's the soundest principled way to derive these similarity
    scores from primary literature? Naming a few candidates
    (functional equivalence, structural homology, empirical
    co-prediction).
Q2. For elliptic-curve invariants (rank, conductor, regulator,
    L1, tamagawa, torsion, cm-flag), give us the high-similarity
    pairs (>= 0.6) you'd expect to be empirically substitutable
    in number-theoretic claims. Justify each.
Q3. For Mahler-measure-adjacent invariants (M, degree, salem-class,
    smyth-extremal, cyclotomic-flag), same question.
Q4. Mutation testing has the equivalent-mutant problem: some
    mutations produce semantically equivalent code. The G12 analog:
    some substitutions produce equivalent CLAIMS (e.g., rank=0 ↔
    L1=0 by BSD). How would you detect equivalent-substitutions
    automatically?
Q5. The simplest implementation does single-substitution
    (one invariant per emitted claim). What's the case for
    multi-substitution (substituting two invariants in one claim)?
    Is the combinatorial cost worth the diversity?
Q6. Cross-domain substitution (e.g., elliptic-curve `rank` ->
    knot `crossing_number`) is potentially powerful but very
    speculative. Should G12 handle cross-domain itself, or
    delegate cross-domain to G07 Analogy?
Q7. If we ship G12 and it emits 200 substituted claims per day,
    and 199 produce "syntactic or semantic failure" while 1
    produces a meaningful "the claim survives substitution" finding,
    is that the right success rate? What would you tune?

Answer each question directly. Don't hedge. Don't restate the
question. If a question contains a false premise, name the false
premise and answer the intended question anyway.
```

---

## G25 — Degeneracy / Trivial-Case (Tier A, SHIPPED v0.9)

(Authored 2026-05-26 in `pivot/erebos_g25_degeneracy_research_2026-05-26.md`)

```
[FRAMING above]

Generator G25 Degeneracy / Trivial-Case:
- Input: any complex Erebos composition.
- Transformation: substitute the underlying object with its
  registered degenerate state (rank=0 curve, degree-1 polynomial,
  the unknot, genus-0 curve).
- Expected Kill Pattern: "division_by_zero_or_type_error"
  (proving the parent composition's logic wasn't properly
  generalized to boundary cases).
- Current degenerate-state registry covers BL-C-001 (Lehmer ->
  deg=1 poly), BL-C-002 (BSD -> rank=0), BL-C-003 + BL-C-004
  (Mahler family -> deg=1).

Q1. This is essentially boundary-value-analysis from software
    testing applied to mathematical hypothesis-generation. What's
    the cleanest formal treatment in the literature?
Q2. For each of: elliptic curves, polynomials, knots, modular
    forms, what's the canonical "degenerate state" and why? Are
    these universally agreed-on, or are there debates?
Q3. The expected kill pattern is "division_by_zero or type_error."
    When the degenerate-state version DOES hold (no error), what
    does that tell us about the original claim? Is it always
    confirmatory, or can it be misleading?
Q4. In algebraic geometry, "degeneration" has a precise meaning
    (limit objects in moduli spaces). Should G25's degenerate-state
    catalog be aligned with the algebraic-geometry meaning, or is
    a software-testing-style degeneracy fine?
Q5. Are there domains where the degenerate case is MORE
    structured than the generic case (e.g., CM elliptic curves
    have MORE structure than generic elliptic curves)? How should
    G25 handle this inversion?
Q6. If we ship G25 as a fast preliminary filter (per the spec:
    "high-value preliminary filter before wasting compute on
    massive objects"), what's the false-positive risk -- claims
    that pass the degeneracy check but fail on real objects?

Answer each question directly. Don't hedge. Don't restate the
question. If a question contains a false premise, name the false
premise and answer the intended question anyway.
```

---

## Capture protocol (reminder)

For each (generator, provider) response:

1. Save to `pivot/feedback_erebos_g<NN>_<provider>_<date>.md`
   (verbatim, no editing).
2. After >=3 providers respond per generator, run convergence
   triage and emit `pivot/meta_analysis_erebos_g<NN>_<date>.md`.
3. High-convergence findings (>=3 of N providers agree) drive
   per-plugin spec revisions in v0.10.
4. Singleton interesting answers get noted but don't unilaterally
   drive changes.

— Charon, 2026-05-26 ITER-2
