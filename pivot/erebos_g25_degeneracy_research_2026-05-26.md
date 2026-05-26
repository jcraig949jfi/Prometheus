# G25 Degeneracy / Trivial-Case Generator — Research Notes

**Date:** 2026-05-26
**Author:** Charon
**Status:** Iteration-1 research; implementation target v0.9
(Iteration 2 of current loop). Tier A per spec.

---

## Spec recap

- **Core mechanism:** Sanity check. Asks how the claim behaves
  when the mathematical object collapses into its simplest
  possible state.
- **Input / Provenance:** A highly complex, highly specific composed
  claim from Erebos.
- **Transformation:** Strips all complexity (sets rank to 0, genus
  to 0, degree to 1).
- **Output Claim:** `The complex Relation R must trivially hold
  (or elegantly zero out) for Degenerate State D`.
- **Falsification Route:** Run the claim exclusively on degenerate
  objects.
- **Expected Kill Pattern:** Division-by-zero or structural
  type-error — proving the logic wasn't generalized properly.
- **Loader Feasibility:** EASY (Tier A in Charon-state because the
  per-domain trivial-case rules need curation, but each rule is
  trivial).

---

## Reasoning Ladder mapping

- **Primary tier:** R6 (self-correction — testing the claim's
  behavior at extremes is a self-test discipline).
- **Secondary tier:** R1 (rule execution — at degenerate state,
  the claim either applies or doesn't).
- **Why not R3:** G25 doesn't abstract; it specializes. The
  abstraction was already done by whatever generator produced the
  input.

---

## Adjacent fields touched

1. **Boundary-case unit testing** (standard SE practice). G25 is
   property-based-testing's degenerate-case minimizer applied to
   math claims.
2. **Hypothesis library shrinking** — Hypothesis (Python) shrinks
   failing examples toward minimal cases. G25 starts at the
   minimal case and works outward.
3. **Edge-case generation in fuzzing** — AFL/libFuzzer corpus
   minimization.
4. **Degeneracy in algebraic geometry** — degenerate varieties,
   limit objects, special fibers. Mathematically PRINCIPLED
   degeneracy (rank-0 elliptic curves are CM, degree-1 polynomials
   have trivial Mahler measure, genus-0 curves are rational).
5. **Identity collapse in tensor decomposition** — when a tensor
   factor reduces to a scalar, the decomposition's structure
   should reflect that.
6. **Mathematical induction base cases** — G25 is essentially "the
   base case better hold."
7. **Empty-set / trivial-group / unit-element conventions** in
   abstract algebra. "What does this claim say about the empty
   case?"

---

## Relevant literature

**Edge cases as tests:**
- Beizer "Software Testing Techniques" — boundary value analysis.
- MacIver "Hypothesis" docs — shrinking semantics.

**Degeneracy in math:**
- Hartshorne "Algebraic Geometry" — special fibers in moduli
  spaces.
- Silverman "The Arithmetic of Elliptic Curves" — CM curves as
  degenerate cases of generic elliptic curves.

**Pythia DR candidates:**
- "Boundary value analysis as a hypothesis-generation primitive."
- "Degenerate object catalogs for systematic mathematical claim
  testing — survey of available libraries."

---

## Datasets in the repo that apply

- **`prometheus_math/databases/mahler.py`** — `smallest_known(degree=1)`
  gives degree-1 polynomials (trivially M=1 if reciprocal, M=|root|
  otherwise). G25's degenerate case for Lehmer claims.
- **`prometheus_math/databases/bsd_rich.json.gz`** — entries with
  `rank=0` are the degenerate case for BSD-rank claims. The
  dataset HAS 500 rank-0 entries — direct test material.
- **`prometheus_math/databases/knots.json.gz`** — entries with
  `crossing_number=0` (the unknot) are the degenerate case for
  knot claims. Unknot has trivial Alexander polynomial = 1.

Each per-domain "degenerate state" needs a small registered table:

```
DEGENERATE_STATES = {
    "BL-C-001 Lehmer": {"degree": 1, "salem_class": False},
    "BL-C-002 BSD": {"rank": 0, "torsion": "trivial"},
    "BL-C-003 Mahler spectrum": {"degree": 1},
    "knots": {"crossing_number": 0},  # the unknot
    "BSD-CM": {"cm": False, "rank": 0},  # composite degenerate
    ...
}
```

---

## Open-source tools to evaluate

- **Hypothesis (`HypothesisWorks/hypothesis`)** — shrinking semantics
  is directly applicable. G25's MVP could use Hypothesis's `note()`
  + `assume()` patterns to mark degenerate-state preconditions.
- **PARI/GP** — already in repo via `mahler.py`. PARI has native
  degenerate-object accessors (`elliptic_curve` with rank=0,
  polynomial of degree 1).

---

## Simple test claims for MVP

**MVP test set v0:**

1. Input: any Erebos G01 composed claim on BL-C-001 Lehmer.
   Transformation: substitute "degree-10 Lehmer polynomial" with
   "degree-1 polynomial".
   Output claim: "The G01 composition's structural claim must hold
   trivially when restricted to degree-1 polynomials (where Mahler
   measure is just |root| and ALL polynomials are Salem-class
   trivially)."
   Expected kill: if the G01 claim was 'Lehmer-bound holds for
   Salem-class polynomials', the degenerate version is 'Lehmer-bound
   holds for degree-1 Salem polynomials', which is trivially
   true (M = leading coefficient, Lehmer bound 1.176 vs degree-1
   roots typically ≥ 1.176).

2. Input: any Erebos G02 contrast claim on BL-C-002 BSD CM-vs-nonCM.
   Transformation: restrict to rank-0 entries (the degenerate
   rank state).
   Output: "G02 CM-vs-nonCM divergence must hold at rank=0
   (where the BSD rank L-function vanishing order is 0)."
   Expected kill: rank=0 distribution between CM and non-CM IS
   non-uniform empirically — claim survives the degenerate check
   meaningfully (not a vacuous pass).

3. Input: any composed claim about knots.
   Transformation: substitute knot K with the unknot.
   Output: "Pattern must trivially hold for the unknot (Alexander
   polynomial = 1, crossing number = 0)."
   Expected kill: most knot-invariant claims involve denominators
   that go to zero at the unknot → division_by_zero kill_pattern.

---

## Frontier-model questions

```
You are an independent technical reviewer. A research swarm wants
to build a generator called "Degeneracy / Trivial-Case" whose job
is to take a complex mathematical claim and emit a degenerate-state
version: "this claim should trivially hold (or elegantly zero out)
when the mathematical object reduces to its simplest case (rank=0,
genus=0, degree=1, unknot, etc.)." Expected kill pattern is
"division-by-zero or structural type-error" — proving the original
logic wasn't generalized properly.

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
    massive objects"), what's the false-positive risk — claims
    that pass the degeneracy check but fail on real objects?
```

---

## TDD test list

1. `test_g25_applicability_no_compositions` — applicable() returns
   False with no Erebos composition rows.
2. `test_g25_applicability_unknown_domain` — applicable() returns
   False when parent claim's domain has no registered degenerate
   state.
3. `test_g25_picks_known_degenerate_lehmer` — for BL-C-001 parent,
   the chosen degenerate state is `{"degree": 1}`.
4. `test_g25_picks_known_degenerate_bsd` — for BL-C-002 parent,
   `{"rank": 0}`.
5. `test_g25_six_field_spec` — emitted ComposedClaim has all six
   fields.
6. `test_g25_kill_pattern_is_division_by_zero_or_type_error` —
   `expected_kill_pattern == "division_by_zero_or_type_error"`.
7. `test_g25_does_not_re_degenerate_same_parent` — tried_pairs
   prevents repeat.
8. `test_g25_reasoning_tier_R6` — declared attribute.
9. `test_g25_falsification_route_names_restricted_dataset` —
   falsification route text says "run the claim exclusively on
   degenerate objects from <domain registry>".
10. `test_g25_degenerate_state_registry_completeness` — every
    known parent domain has a registered degenerate state.

---

## Logging requirements

- `transformation_path`: which degenerate state was selected
  (e.g., `degenerate_to_degree_1`, `degenerate_to_rank_0`).
- G25-specific extras: the chosen degenerate state dict; the
  parent's domain string.
- `inputs_summary`: count of Erebos composition rows with KNOWN
  degenerate-state domain vs UNKNOWN.

---

## HITL escalation conditions

- **DOMAIN-EXPERT NEEDED:** when a composition's parent comes from
  an unregistered domain. HITL ticket asks "what's the degenerate
  state for this domain?"
- **PLATEAUED:** every registered (parent × degenerate-state)
  combination already tried. Adds to backlog: register more
  domains.
- **DRIFT:** if N=20 consecutive G25 emissions all get
  `division_by_zero` kill (the expected pattern) without any
  `claim_holds_trivially` outcome, that's substrate-grade evidence
  that the parent generators are producing badly-generalized claims.
  Surface to per-plugin review for upstream investigation.

---

## Implementation sketch for v0.9

```python
class DegeneracyGenerator:
    id = "g25_degeneracy"
    name = "Degeneracy / Trivial-Case"
    spec_phase = 5
    feasibility_tier = "A"
    reasoning_tier = "R6"
    expected_kill_pattern = "division_by_zero_or_type_error"

    # Registered degenerate states per parent-domain hint
    DEGENERATE_REGISTRY = {
        "BL-C-001": {"name": "degree_1_polynomial", "state": {"degree": 1}},
        "BL-C-002": {"name": "rank_0_curve", "state": {"rank": 0}},
        "BL-C-003": {"name": "degree_1_polynomial", "state": {"degree": 1}},
        "BL-C-004": {"name": "degree_1_polynomial", "state": {"degree": 1}},
        # Subsequent BL-C-* added as Stygian loaders ship
    }

    def applicable(self, state: SwarmState) -> bool:
        # Need Erebos compositions whose parent domain is registered
        for r in state.erebos_self_ledger:
            parent_problem = self._extract_parent_problem(r)
            if parent_problem in self.DEGENERATE_REGISTRY:
                key = f"{self.id}|{r.get('record_id','')}"
                if key not in state.tried_pairs:
                    return True
        return False

    def generate(self, state: SwarmState) -> Optional[ComposedClaim]:
        # ... pick uncomposed parent + emit degenerate-version claim
```

ETA: ~150 LOC including tests, registry, logging hooks.

---

## Cross-iteration handoff

- **Iteration 2:** implement per sketch; ship with the 4 currently-
  registered domains (BL-C-001 through 004); flag unknown-domain
  HITL events for new domains as they appear.
- **Iteration 3:** grow the registry as new Stygian loaders ship.
- **Iteration 4+:** integrate with composition-aware loader so the
  degeneracy attack actually executes the restricted-to-degenerate
  test path (not just emit the candidate claim).

— Charon, 2026-05-26
