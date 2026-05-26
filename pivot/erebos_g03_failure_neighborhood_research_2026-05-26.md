# G03 Failure-Neighborhood Generator — Research Notes

**Date:** 2026-05-26
**Author:** Charon
**Status:** Iteration-1 research; implementation deferred to v0.10
(Tier B per `erebos_25_archetypes_spec_2026-05-26.md`).
**DNA:** P7 (adjacent-space research discipline), P10 (R-tier
mapping), P11 (frontier questions ready).

---

## Spec recap (from canonical doc)

- **Core mechanism:** Treats a kill as a directional gradient.
  Mutates failed claims into weaker adjacent states.
- **Input / Provenance:** A hard-killed claim with a structured
  KillVector (e.g., failed on equality, but values remained close).
- **Transformation:** Weakens the mathematical operator. `=` becomes
  `≡ mod N`, `≤`, or `|A-B| < k`.
- **Output Claim:** `Invariant A [weaker_operator] Invariant B`.
- **Falsification Route:** Standard Stygian battery using the
  relaxed operator.
- **Expected Kill Pattern:** `boundary_collapse` (weakened claim
  so loose it's trivially true for random noise).
- **Loader Feasibility:** MEDIUM (Charon Tier B). Requires AST
  parsing + mutation of operator nodes in the claim's predicate
  code.

---

## Reasoning Ladder mapping

- **Primary tier:** R3 (abstraction — going from `=` to `≡ mod N`
  abstracts away exact equality to a class).
- **Secondary tier:** R6 (self-correction — admits the original
  was too strong; weakens to find the largest still-true claim).
- **Why R3 not R5:** weakening doesn't make a causal claim, it
  makes an abstraction-of-equality claim.

---

## Adjacent fields touched (per P7)

From `erebos_adjacent_topics_taxonomy_2026-05-26.md`:

1. **Mutation testing** (PIT, MutPy, Stryker, Atheris) — operator
   mutation is the *core* technique. Mutation-testing literature has
   30+ years of work on mutant generation, mutant subsumption, and
   equivalent-mutant detection. G03 should crib heavily.
2. **AST manipulation** — Python's `ast` module, `libcst`, `parso`,
   `RedBaron`. For our MVP, a string-substitution version avoids
   the full AST round-trip.
3. **Inductive logic programming** — ILP systems (Aleph, Popper)
   weaken/strengthen logical predicates as a core inference move.
   ILP's "θ-subsumption" is the formal version of operator
   weakening.
4. **Property-based testing** (Hypothesis, QuickCheck) — Hypothesis's
   `shrink` operation FINDS minimal failing examples; G03 is the
   inverse (find minimal SURVIVING relaxations).
5. **Lattices of mathematical predicates** — order theory: equality
   is the strongest predicate; congruence-mod-N is weaker; ordering
   is weaker still; existence is weakest. G03 traverses the lattice
   downward.
6. **Symbolic regression with operator search** — DSO, AI Feynman:
   search over operator trees for the simplest one that fits the
   data. Inverse direction: G03 starts at a failing complex
   predicate and walks toward simpler ones.

---

## Relevant literature

**Mutation testing:**
- Jia & Harman 2011 "An Analysis and Survey of the Development of
  Mutation Testing" — IEEE TSE survey.
- DeMillo, Lipton, Sayward 1978 — original mutation-testing paper.

**ILP / predicate weakening:**
- Muggleton 1991 "Inductive Logic Programming" — foundational.
- Cropper, Dumančić, Muggleton 2022 "Inductive logic programming
  at 30" — modern survey.
- Cropper & Morel 2021 "Learning programs by learning from
  failures" — Popper system.

**Mathematical predicate hierarchies:**
- Suppes "Axiomatic Set Theory" — equality as strongest predicate.
- Halmos "Naive Set Theory" — congruence relations as quotients.

**Pythia DR candidates:**
- "Mutation testing for hypothesis-generation in mathematical
  research" — likely produces zero direct hits; substrate-grade
  finding either way (either the gap exists or the gap is closed).
- "Predicate weakening in inductive logic programming for
  empirical mathematical claim refinement."
- "Equivalent mutant problem in mutation testing — survey of
  detection methods" (relevant because G03's expected kill pattern
  `boundary_collapse` is exactly the equivalent-mutant problem in
  another guise).

---

## Datasets in the repo that apply

- **`charon/agents/stygian/state/kill_ledger.jsonl`** — REJECTED
  Stygian rows with `kill_vector.tests` sub-test results. G03 needs
  these to identify "failed on equality but values close." Look
  for tests where F16 (equivalence) FAIL'd but F3 (effect size)
  showed close values.
- **`charon/agents/pollux/state/kill_ledger.jsonl`** — Pollux's
  `pollux_sign_flips_under_normalization` and
  `pollux_no_correlation_observed` rows. Both are killed-with-
  structure rows G03 could weaken.
- **`theseus/corpus/*.jsonl.gz`** — Theseus REJECTED rows. Vast
  pool but Theseus's generator-prefixed kill_patterns make
  predicate identification harder (the prefix isn't a Python
  operator).

---

## Open-source tools to evaluate

- **Hypothesis (`HypothesisWorks/hypothesis`)** — Python property-
  based testing with strong shrinking semantics. G03's MVP could
  literally use Hypothesis's strategy combinators for predicate
  generation.
- **MutPy (`mutpy/mutpy`)** — Python mutation testing. Operator
  mutation list directly informs G03's substitution table.
- **libcst (`Instagram/LibCST`)** — concrete syntax tree library.
  For when G03 graduates to proper AST mutation in v0.11+.
- **Popper (`logic-and-learning-lab/Popper`)** — ILP system with
  predicate weakening as a first-class operation.

---

## Simple test claims for MVP (per James: "as simply as possible")

**MVP test set v0:** start with string-substitution weakening on a
synthetic REJECTED claim:

1. Input: `"M(P) = M_Lehmer = 1.176280818..."`
   Output: `"M(P) ≈ M_Lehmer to within 1e-3"`
   Expected G03 verdict: weakened version trivially holds because
   any random Mahler measure within rounding distance counts.
2. Input: `"rank(E) = 0 for all E in subset S"`
   Output: `"rank(E) ≤ 1 for all E in subset S"`
   Expected: weakened version still has falsification value because
   rank-2+ curves exist; the weakening is not boundary-collapse.
3. Input: `"corr(A, B) = 1.0"` (Pollux's deg10-vs-deg12 raw)
   Output: `"corr(A, B) > 0.5"` (substantially weaker)
   Expected: trivially holds for many other monotone subset pairs.

The MVP doesn't NEED to do AST mutation — it just needs to text-
substitute operators per a small table and emit the resulting
candidate claim with the standard six-field spec.

---

## Frontier-model questions (per P11)

To fire against ≥3 frontier providers before implementing:

```
You are an independent technical reviewer. A research swarm wants
to build a generator called "Failure-Neighborhood" whose job is
to take a hard-killed mathematical claim and produce weakened
candidate-claims by relaxing the predicate operators (= → ≈, =
→ ≡ mod N, ≤, etc.). The intended falsification expected_kill_pattern
is "boundary_collapse" (the weakened claim is so loose it becomes
trivially true for random noise).

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
    gradient. Is this premise sound, or does it conflate
    "near-equality of measured values" with "near-equality of the
    structural claim"?

Q5. Are there examples in inductive logic programming literature
    of systems that did exactly this — predicate weakening as a
    hypothesis-generation primitive? Cite the closest 2-3 systems.

Q6. If we implement this generator and it produces 100 weakened
    claims per day, and 99 of them get boundary_collapse-killed
    (the expected pattern) and 1 produces a meaningful "X is true
    under this weaker version" finding, is that a 99% success
    rate or a 1% one? Make the case for each framing.

Q7. What's the highest-leverage extension we're missing? E.g., is
    bidirectional (weaken-then-restrengthen) more powerful than
    one-direction-only?
```

---

## TDD test list (P3)

To write before/alongside implementation:

1. `test_g03_applicability_empty_input` — applicable() returns
   False when no Stygian REJECTED rows.
2. `test_g03_applicability_no_structured_killvector` — applicable()
   returns False on REJECTED rows where `kill_vector.tests` is
   missing or empty (those have no gradient direction).
3. `test_g03_generates_for_known_failed_equality` — given a
   fixture REJECTED row with an equality failure, generate()
   returns a ComposedClaim with the operator substituted from `=`
   to the first weaker form (`≈` or `≡ mod N`).
4. `test_g03_six_field_spec_compliance` — emitted ComposedClaim
   has all six required fields non-empty.
5. `test_g03_operator_substitution_table_idempotent` — substituting
   `≈` again doesn't double-substitute.
6. `test_g03_skips_already_weakened_claims` — claims that already
   contain the weakened operator don't get re-weakened (tracked via
   `tried_pairs` in SwarmState).
7. `test_g03_kill_pattern_expectation_matches_spec` — emitted
   `expected_kill_pattern` is exactly `boundary_collapse`.
8. `test_g03_reasoning_tier_declared` — plugin has `reasoning_tier
   = "R3"` attribute.
9. `test_g03_falsification_route_names_real_battery` — the
   `falsification_route` text mentions an actual Stygian battery
   test name (F1-F23 + F15-F24 — must match a registered one).

---

## Logging requirements (P4)

Per `GeneratorTickLog` dataclass:
- `transformation_path`: which operator substitution fired (e.g.,
  `eq_to_approx`, `eq_to_mod_N`, `eq_to_leq`)
- `inputs_summary`: count of REJECTED rows considered + count of
  REJECTED rows with structured kill_vector
- G03-specific extras: the original predicate string + the weakened
  predicate string

---

## HITL escalation conditions (P6)

- **PLATEAUED:** N=50 consecutive ticks with no new
  composed_id (combinatorial: distinct REJECTED rows × distinct
  weakening operations exhausted).
- **BLOCKED:** if AST-mutation infrastructure becomes the limiter
  (claims contain math notation that string-substitution can't
  parse safely), block + file ticket asking for proper AST round-
  trip support.
- **DOMAIN-EXPERT NEEDED:** when emitted claim contains a
  mathematical operator the substitution table doesn't know how to
  weaken (e.g., `≡` already a relaxation, what's the next step?).
- **CROSS-POLLINATION:** before v0.10 implementation, fire the
  frontier questions above.

---

## Open implementation questions

1. Should G03 ship as string-substitution MVP in v0.10 or wait for
   proper AST mutation in v0.11+? Recommendation: string-substitution
   MVP — the equivalent-mutant problem is manageable at our scale,
   and we want to see emission patterns before investing in AST
   infrastructure.

2. What's the operator weakening table? Initial proposal:
   - `=` → `≈` (within rounding tolerance) → `≡ mod p` (small p) →
     `≤` → existence
   - `<` → `≤` → bounded-by-constant → existence
   - Quantifier weakening: `∀` → `for most x` → `∃`

3. How does G03 interact with G04 (Survivor-Tightening, the
   inverse)? Should they be coordinated to walk the same claim in
   both directions? Phase-2 work.

4. What if the original Stygian REJECTED claim's predicate isn't a
   Python expression? Most claims are NATURAL LANGUAGE in
   `canonical_claim_text`. The substitution has to operate on
   natural-language operator words ("equals", "is equal to",
   "matches", "differs by less than", etc.) — string-substitution
   with a careful operator-phrase table.

---

## Cross-iteration handoff

- **Iteration 2:** review this doc; decide if string-substitution
  MVP is greenlit or if we wait for AST.
- **Iteration 3:** if greenlit, implement g03_failure_neighborhood.py
  + test suite + wire into REGISTRY.
- **Iteration 4+:** if AST is needed, build the claim DSL or
  per-claim Python-expression rep that makes G03/G04/G12/G13/G14
  all proper AST consumers.

— Charon, 2026-05-26
