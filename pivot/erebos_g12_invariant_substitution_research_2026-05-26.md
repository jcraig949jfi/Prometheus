# G12 Invariant-Substitution Generator — Research Notes

**Date:** 2026-05-26 (ITER-2; deferred from ITER-1)
**Author:** Charon
**Status:** Implementation target this iteration. Tier A per
`erebos_25_archetypes_spec_2026-05-26.md`.

---

## Spec recap

- **Core mechanism:** Brute-force genetic mutation of internal
  nodes of a claim. Swap Invariant A for Invariant A' based on a
  similarity matrix.
- **Input / Provenance:** Any baseline claim (Stygian
  substantive row, Pollux substantive row, or Erebos composition).
- **Transformation:** Swap one invariant in the claim for another
  invariant from a curated similarity-graph neighborhood.
- **Output Claim:** `Relation R holds for [Substituted Invariant]`.
- **Falsification Route:** Standard Stygian battery on the
  substituted claim.
- **Expected Kill Pattern:** `syntactic_or_semantic_failure`
  (the substituted invariant either has a type mismatch or the
  relation breaks when the underlying invariant is structurally
  different).
- **Loader Feasibility:** EASY (Tier A per spec); Charon-state
  Tier A because the similarity matrix needs hand curation but the
  AST swap itself is mechanical.

---

## Reasoning Ladder mapping

- **Primary tier:** R3 (abstraction — substitution treats invariants
  as fungible inside the relation; that IS the abstraction move).
- **Secondary tier:** R7 (cross-domain transfer — when the
  substituted invariant comes from a different mathematical
  domain).
- **Why not R5:** substitution doesn't make a causal claim, it
  makes a fungibility claim.

---

## Adjacent fields touched

1. **Mutation testing** — operator/operand mutation. G12 is the
   OPERAND-mutation cousin to G03/G13's OPERATOR-mutation.
2. **Metamorphic testing** — testing transformations that should
   preserve correctness. If `R(A, B)` holds and `A ≈ A'` (similar
   invariants), does `R(A', B)` also hold?
3. **Inductive logic programming** — predicate-symbol substitution
   in ILP is a standard refinement operation.
4. **Genetic programming** — sub-tree replacement as a mutation
   operator. G12 is the leaf-node version.
5. **Analogy / structure mapping** (Gentner) — Invariant_A and
   Invariant_A' play the same structural role; substitution tests
   whether that's substantively true.
6. **Category theory** — natural transformations between functors:
   the substitution claim is "this relation is natural in the
   invariant family." G12 stays informal (no actual category-theoretic
   machinery yet); G21 Isomorphism is the formal version.

---

## Relevant literature

- Howden 1982 "Weak mutation testing and completeness of test sets."
- Gentner 1983 "Structure-Mapping: A Theoretical Framework for
  Analogy."
- Cropper-Dumančić-Muggleton 2022 "Inductive logic programming at
  30" survey — substitution as ILP refinement.

**Pythia DR candidates:**
- "Invariant substitution as a hypothesis-generation primitive in
  empirical mathematical conjecture mining."
- "Similarity matrices over mathematical invariants — known
  taxonomies and metrics."

---

## Datasets in the repo that apply

- **Substrate vocabulary** (`aporia/doctrine/substrate_vocabulary
  /primitives.md`) — H3 headers are registered invariants per the
  tier-A++/B/C/D/E taxonomy. The relationships in `composition_rules.md`
  hint at substitution semantics.
- **Acheron's COORDINATE_DICTIONARY** (`charon/agents/acheron/daemon.py`)
  — the 8 multi-coordinate terms (rank, lehmer, schinzel, catalan,
  sato-tate, goldbach, twin-prime, mertens) are PRE-AUTHORED
  similarity neighborhoods. E.g., the 8 rank coordinates
  (tensor_rank, border_rank, cactus_rank, ...) are by-construction
  similar-but-distinct invariants. G12's similarity matrix can
  initialize from these.
- **`prometheus_math/databases/`** — accessor functions for
  Mahler measures (degree, salem_class, smyth_extremal,
  mahler_measure), BSD invariants (rank, conductor, regulator,
  L1, tamagawa_product, torsion, sha_an, cm, faltings_height),
  knot invariants (alex_coeffs, log_mahler_root, crossing_number),
  etc. Each domain's invariants form a similarity neighborhood.

---

## The similarity matrix (MVP)

Hand-curated 10x10 to start. Rows/cols = invariants; cells = similarity
score [0, 1]. Score reflects "would substituting A for A' produce a
syntactically-valid claim with comparable semantic meaning?"

Domain 1: Mahler-measure-adjacent invariants
```
                  mahler_measure  degree  salem  smyth  cyclotomic
mahler_measure    1.0             0.3     0.2    0.3    0.4
degree            0.3             1.0     0.5    0.4    0.6
salem_class       0.2             0.5     1.0    0.7    0.4
smyth_extremal    0.3             0.4     0.7    1.0    0.3
cyclotomic_flag   0.4             0.6     0.4    0.3    1.0
```

Domain 2: BSD/elliptic-curve invariants
```
                  rank   conductor  regulator  L1     tamagawa  torsion  cm
rank              1.0    0.3        0.7        0.7    0.2       0.3      0.5
conductor         0.3    1.0        0.2        0.3    0.5       0.2      0.3
regulator         0.7    0.2        1.0        0.6    0.2       0.2      0.4
L1                0.7    0.3        0.6        1.0    0.3       0.2      0.4
tamagawa_product  0.2    0.5        0.2        0.3    1.0       0.4      0.3
torsion           0.3    0.2        0.2        0.2    0.4       1.0      0.5
cm_flag           0.5    0.3        0.4        0.4    0.3       0.5      1.0
```

Substitution rule: pick the highest-similarity off-diagonal entry
(excluding pairs already tried).

**Caveats** (per HITL-needed conditions):
- These scores are JUDGMENT calls. The matrix is a hypothesis
  itself.
- BSD substitution `rank → regulator` (0.7) is a strong claim —
  many BSD relations DO survive that substitution (e.g.,
  L^(r)(E,1) / r! ∝ regulator), so the high score is defensible.
- `mahler_measure → degree` (0.3) is a low score because they're
  weakly related; substitution will mostly produce nonsense.
- Cross-domain substitution (Mahler → BSD invariants) is NOT in
  the MVP matrix; defer to G07 Analogy.

---

## Simple test claims for MVP

1. Input: Stygian BL-C-001 (Lehmer) row with text mentioning
   `mahler_measure`.
   Substitution: `mahler_measure → salem_class` (0.2 similarity —
   low; expect kill).
   Output: "Lehmer-bound holds when restricted to entries with
   `salem_class` matching some criterion."
   Expected: syntactic/semantic failure — Lehmer-bound is about
   numeric measure, not boolean flag.

2. Input: Stygian BL-C-002 (BSD rank) row mentioning `rank`.
   Substitution: `rank → regulator` (0.7 — higher).
   Output: "BSD distribution claim on `regulator` distribution
   instead of `rank` distribution."
   Expected: claim shifts from categorical distribution test to
   continuous distribution test; F15 log-normal becomes more
   appropriate; some battery sub-tests pass, some fail (mixed
   verdict, not pure-collapse).

3. Input: Pollux pair `salem_vs_pisot`.
   Substitution: `salem_class → smyth_extremal` (0.7).
   Output: "Pollux pair smyth_extremal_vs_non_smyth correlation
   survives normalization."
   Expected: this is actually one of the EXISTING Pollux pairs.
   G12 may discover that the substituted claim is already in the
   ledger; cross-reference yields a `g12_substitution_collides_with
   _existing` finding (substrate-grade: invariant similarity
   predicts Pollux pair-existence).

---

## Frontier-model questions

```
You are an independent technical reviewer. A research swarm wants
to build a generator called "Invariant Substitution" that takes a
mathematical claim and emits a candidate-claim by swapping one
invariant in the claim for a similar invariant from a curated
similarity matrix. Expected kill pattern is "syntactic or semantic
failure" (the substituted invariant is structurally incompatible
with the relation).

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

Q6. Cross-domain substitution (e.g., elliptic-curve `rank` →
    knot `crossing_number`) is potentially powerful but very
    speculative. Should G12 handle cross-domain itself, or
    delegate cross-domain to G07 Analogy?

Q7. If we ship G12 and it emits 200 substituted claims per day,
    and 199 produce "syntactic or semantic failure" while 1
    produces a meaningful "the claim survives substitution" finding,
    is that the right success rate? What would you tune?
```

---

## TDD test list

1. `test_g12_not_applicable_with_empty_state` — `applicable()`
   returns False with no Stygian/Pollux/Erebos rows.
2. `test_g12_applicable_with_known_domain` — applicable with a
   row whose invariants intersect the similarity matrix.
3. `test_g12_not_applicable_when_no_substitution_candidate` —
   row mentions only invariants not in the matrix.
4. `test_g12_picks_highest_similarity_substitution` — among
   candidates, picks the one with highest similarity score.
5. `test_g12_six_field_spec_compliance` — all six fields populated.
6. `test_g12_expected_kill_pattern_correct` — exactly
   `syntactic_or_semantic_failure`.
7. `test_g12_composed_id_format` — starts with `EREBOS-G12-`.
8. `test_g12_metadata` — id, name, spec_phase=3, feasibility_tier=A.
9. `test_g12_reasoning_tier_R3` — declared attribute.
10. `test_g12_tracks_tried_substitutions` — `tried_pairs` includes
    the (parent_row, original_invariant, substituted_invariant) tuple.
11. `test_g12_similarity_matrix_symmetric` — `M[a][b] == M[b][a]`
    for all entries in the curated matrix.
12. `test_g12_similarity_matrix_diagonal_one` — `M[a][a] == 1.0`.
13. `test_g12_skips_self_substitution` — never emits a claim
    substituting an invariant with itself.

---

## Logging requirements

- `transformation_path`: `substitute_<original_invariant>_to_<substituted_invariant>`
- G12-specific extras: similarity score, original invariant
  mention-location in the parent claim, domain of the
  substitution.

---

## HITL escalation conditions

- **DOMAIN-EXPERT NEEDED:** when a parent claim mentions an
  invariant not in the matrix → ticket asks "what's the similarity
  neighborhood for invariant X?"
- **PLATEAUED:** every (parent × original-invariant × substituted-
  invariant) tuple in the matrix has been tried.
- **CROSS-POLLINATION:** fire the frontier questions above before
  promoting the similarity matrix from MVP-curated to canonical.

---

## Implementation sketch

```python
class InvariantSubstitutionGenerator:
    id = "g12_invariant_substitution"
    name = "Invariant Substitution"
    spec_phase = 3
    feasibility_tier = "A"
    reasoning_tier = "R3"
    expected_kill_pattern = "syntactic_or_semantic_failure"

    # 10+ invariants per domain, similarity in [0, 1].
    # Symmetric, diagonal=1.
    SIMILARITY_MATRIX = {
        # Mahler domain
        ("mahler_measure", "degree"): 0.3,
        ("mahler_measure", "salem_class"): 0.2,
        # ... (full matrix in plugin code)
        # BSD domain
        ("rank", "regulator"): 0.7,
        ("rank", "L1"): 0.7,
        ("rank", "tamagawa_product"): 0.2,
        # ...
    }

    # All invariant names we recognize. Substitution will only fire
    # on parent claims containing one of these.
    KNOWN_INVARIANTS = {
        # Mahler
        "mahler_measure", "degree", "salem_class", "smyth_extremal",
        "cyclotomic_flag",
        # BSD
        "rank", "conductor", "regulator", "L1", "tamagawa_product",
        "torsion", "cm_flag",
    }

    def applicable(self, state): ...
    def generate(self, state): ...
```

ETA: ~250 LOC including matrix, applicability scan, generation.

---

## Cross-iteration handoff

- **ITER-2 this session:** ship per sketch with the matrix above;
  tests + logging.
- **ITER-3:** review G12 emission patterns; tune matrix; potentially
  fire frontier prompts.
- **ITER-4+:** integrate composition-aware loader so substituted
  claims actually get battery-tested.

— Charon, 2026-05-26
