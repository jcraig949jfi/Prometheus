---
name: math-tdd
description: Test-driven development for mathematical research software. Enforces test-first workflow with authority-based, property-based, edge-case, and composition tests. Use whenever forging a new mathematical operation in prometheus_math or techne/lib, or when adding new tests to existing operations.
---

# math-tdd

Mathematical software fails in unique ways: silently wrong results, off
by integer factors, invariants violated under composition. Plain unit
tests rarely catch these. This skill enforces a test-first workflow
designed for the failure modes that bite mathematicians.

## When to invoke

Invoke this skill any time you are about to add or modify a function in
`prometheus_math/`, `techne/lib/`, or any module that produces a
mathematical result. Also invoke when extending tests for an existing
operation that lacks any of the four required test categories.

Do NOT invoke for:
- Pure documentation changes
- CI/CD configuration changes
- Database wrapper plumbing that doesn't compute mathematical objects
  (use ordinary unit tests)

## The four required test categories

Every mathematical operation must have at least one test in each of
these categories. The skill enforces this gate.

### 1. Authority-based test

The output of the operation, on a specific input, must equal an
authoritative reference value. The reference must come from one of:

- A peer-reviewed published table (Mossinghoff Mahler, ATLAS character
  tables, knotinfo)
- The LMFDB (`pm.databases.lmfdb`) for curves, NFs, modular forms, etc.
- The OEIS (`pm.databases.oeis`) for integer sequences
- Hand-computation by the implementer, with the computation steps
  recorded in the test docstring
- An authoritative Magma / Mathematica run, captured as a snapshot

The test docstring MUST cite the reference. Reference-less tests are
not authority-based and don't count for this gate.

```python
def test_class_number_q_sqrt_minus_5_against_cohen_table_1_1():
    """Q(sqrt(-5)) has class number 2.

    Reference: Cohen, "Advanced Topics in Computational Number Theory",
    Table 1.1, p.10. Cross-checks against LMFDB nf_fields with
    label '2.0.20.1' (class_number=2). Hand-verified: ideal class
    [(2, 1+sqrt(-5))] is non-principal of order 2.
    """
    assert class_number('x^2 + 5') == 2
```

### 2. Property-based test (Hypothesis)

The operation satisfies invariants that hold across many inputs.
Examples:

- `mahler_measure(coeffs) >= 1` for any non-zero integer poly
- `class_number(K) >= 1` for any number field
- `lll(B)` preserves `|det(B)|`
- Idempotence: `polredabs(polredabs(p)) == polredabs(p)`
- Compatibility: `degree(field) == len(coeffs) - 1`

Use the `hypothesis` library. Register strategies for mathematical
inputs (small primes, irreducible polynomials, valid a-invariants).

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers(min_value=-5, max_value=5), min_size=2, max_size=8))
def test_mahler_measure_is_at_least_one(coeffs):
    """For any non-trivial integer poly, M(P) >= 1."""
    if all(c == 0 for c in coeffs):
        return  # skip zero polynomial
    assert mahler_measure(coeffs) >= 1.0 - 1e-9
```

### 3. Edge-case test

The operation handles each documented edge case correctly. Required
sub-tests:

- **Empty input**: explicit ValueError or sensible default
- **Singleton input**: special-case behavior
- **Boundary**: smallest/largest valid input (Heegner-disc D=-163,
  conductor 11, etc.)
- **Malformed input**: explicit ValueError with informative message
- **Numerical precision boundary**: where `bits_prec` becomes
  insufficient
- **Pathological scale**: when class number > 50, polynomial degree > 50,
  etc.

The test docstring should explicitly enumerate which edges are
covered. Missing edges = test category not satisfied.

```python
def test_class_number_edge_cases():
    """Class number edges:
    - empty polynomial: ValueError
    - non-irreducible polynomial: PARI raises (we re-raise as ValueError)
    - Heegner disc -163: returns 1
    - large-h field 2.0.7751.1: passes through max_class_number guard
    """
    with pytest.raises(ValueError):
        class_number([])
    assert class_number('x^2 + 163') == 1  # Heegner
    with pytest.raises(ValueError):
        class_number('x^2 + x + 1938', max_class_number=50)  # h=110
```

### 4. Composition test

The operation composes correctly with other operations to produce
a known invariant. This is the hardest category to write but the most
valuable for catching subtle bugs that pass unit tests.

Composition examples:

- BSD: `analytic_sha(C) * regulator(C) * conductor.tamagawa(C) ≈
  L^(r)(C, 1) / r! / Omega(C) * |torsion(C)|^2`
- HCF degree: `degree(hilbert_class_field(K)) == class_number(K)`
- Knot Alexander roots inside knot trace field
- Galois group order divides `n!` for degree-n field
- Functional equation residual is "small" for any zeta-style L-fn

```python
def test_bsd_consistency_for_11a1():
    """11.a1 satisfies the BSD identity exactly.

    Composition test: every BSD-chain tool must agree on the formula.
    Cross-checks the entire chain in one assertion.
    """
    a = [0, -1, 1, -10, -20]  # 11.a1
    sha = analytic_sha(a)
    reg = regulator(a)
    cond = conductor(a)
    glob = global_reduction(a)
    tors = sympy_elltors(a)  # via cypari
    # ... compose into BSD identity, assert ~ 1
```

## Workflow

When you invoke this skill on a new operation:

### Step 1 — Identify the authoritative reference

Before writing any code: WHAT is the source of truth?

- For known invariants: cite the textbook / table
- For LMFDB-keyed objects: cite the LMFDB label
- For OEIS-keyed sequences: cite the A-number
- For hand-computed values: write out the computation in the test
  docstring
- For "no published value exists": flag this — you may need to compute
  via a different open-source tool first (Magma, Mathematica) and
  treat that as the reference

If no authority exists, the skill BLOCKS implementation. Add the
operation to the `pending_authority/` queue at
`techne/PENDING_AUTHORITY.md` and move on to a different task.

### Step 2 — Write the four required tests FIRST

In `techne/tests/test_<NAME>.py` or
`prometheus_math/tests/test_<NAME>.py`, write all four:
1. Authority test (cite reference)
2. Property test (Hypothesis)
3. Edge-case test (enumerate covered edges)
4. Composition test (chain with at least one other operation)

Each test is initially RED (the implementation doesn't exist).

### Step 3 — Verify the tests fail correctly

Run the tests. They should fail with `ImportError: cannot import name
<OP>` or similar. Confirm all four fail. If a test passes accidentally
(because the operation already exists or because of a bug), pause and
investigate.

### Step 4 — Write the minimum implementation

Write only enough code to make all four tests green. Resist
gold-plating. If you find yourself adding features the tests don't
cover, stop and write a test for them first.

### Step 5 — Run the four tests

All four green. If any is red, fix only that one — do NOT add features
unrelated to the failing test.

### Step 6 — Refactor

Now that all tests are green, refactor for clarity, performance, and
naming. Re-run tests after each refactor. If a refactor breaks a test,
the test is the source of truth — restore green before continuing.

### Step 7 — Add the operation to the registry / facade

- Add to the relevant `prometheus_math/<category>.py` `__all__` list
- Add a one-line export
- Regenerate ARSENAL.md via `python -c "import prometheus_math;
  prometheus_math.doc.arsenal()"`

### Step 8 — Commit with descriptive message

The commit message must:
- Name the new operation
- Cite the authoritative reference used
- List the test counts in each of the 4 categories
- Co-author Claude

Example:
```
prometheus_math.number_theory: pari_classpoly added

cross-checks against LMFDB nf_fields disc -23 (poly x^2 + x + 6,
classpoly should be x for h=1) and Cohen Table 1.1 entry.

Tests:
  authority: 5 (LMFDB-keyed)
  property:  4 (h >= 1, classpoly degree == h, etc.)
  edge:      4 (D=-3 fundamental, D=-163 Heegner, D=-12 non-max, D > 0 raises)
  composition: 2 (h(K) = degree(classpoly), polredabs idempotence)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

## Test-quality rubric

When reviewing your own tests, score each category:

| Category | Score 1 | Score 2 | Score 3 |
|---|---|---|---|
| Authority | 1 cited reference | 3+ references covering distinct corners | Cross-checked against 2+ open-source tools (e.g., PARI + Sage + LMFDB) |
| Property | 1 Hypothesis test | 4+ properties with diverse strategies | Properties include compositional / categorical invariants |
| Edge | Empty + boundary | All documented failure modes | + numerical precision boundary + pathological scale |
| Composition | 1 chain | 3+ chains (BSD-style multi-tool) | Chain spans 2+ categorical modules |

A test suite is "TDD-quality" iff it scores ≥ 2 in every category. Aim
for ≥ 2 in every category before submitting a project as complete.

## Failure modes to catch (unique to mathematical software)

1. **Off-by-factorial**: `ellanalyticrank` returns L^(r)(1), not L^(r)(1)/r!
   — silent factor-of-r! error. (Caught by composition test against BSD.)
2. **Off-by-2 from real-period convention**: `Omega = 2*omega[1]` if
   disc > 0, else `omega[1]`. (Caught by authority cross-check against
   LMFDB real_period.)
3. **Saturation index error**: `ellrank` returns independent points,
   not Z-basis; raw `det(height_matrix)` is `index^2` too large.
   (Caught by composition test against `ellsaturation`.)
4. **Variable-priority error**: PARI's `bnrclassfield` requires base
   variable to have lower priority than relative variable.
   (Caught by edge case: trivial input where you'd expect identity.)
5. **Polredabs convention**: `polredabs` may flip x → -x for some
   polynomials, preserving M but changing the sequence of coefficients.
   (Caught by property test: M is invariant under polredabs.)
6. **Encoding errors**: cypari needs `sys.stdout.reconfigure(encoding='utf-8')`
   on Windows. (Caught by integration test that runs cypari on a CI
   Windows runner.)
7. **PARI stack overflow**: large-discriminant fields exhaust 4 GB.
   (Caught by edge case: pathological scale, with `max_class_number`
   guard verified.)

These seven categories cover ~90% of the bugs that have shipped through
Techne's tools. The composition tests in particular catch them.

## Skill output

When you complete this skill cycle on an operation, append a one-line
entry to `techne/TDD_LOG.md`:

```
2026-04-25 | pm.number_theory.pari_classpoly | A:3 P:2 E:3 C:2 | commit abc1234
```

Format: `date | operation | A:authority P:property E:edge C:composition |
commit ref`. This becomes the long-term TDD-quality audit log.

## Anti-patterns to avoid

- **"It looks right" testing**: writing tests that just check the
  output is non-None or non-zero. Useless.
- **Tautological testing**: testing that `mahler_measure(coeffs) ==
  mahler_measure(coeffs)`. Useless.
- **Catch-all assertions**: `assert result is not None`. Too weak.
- **Hardcoding the implementation's output as the test**: writing the
  function, computing one output, then asserting the function produces
  that output. Doesn't catch the function being wrong.
- **Skipping property tests because "they're hard to write"**: every
  mathematical operation has at least one invariant. If you can't
  identify one, you don't fully understand the operation; pause and
  research.
- **Skipping composition tests because "they require other tools"**:
  the whole point of an arsenal is composition. If your tool can't
  compose, why is it in the arsenal?
- **Only running tests on small inputs**: include at least one
  large-scale input in each property test.

## Integration with the broader stack

This skill produces tests that run via:

- `pytest` for unit + property + edge + composition tests
- `pytest-hypothesis` for property tests
- `pytest --benchmark-only` for performance regression (Tier-2 promotion)
- CI workflow `.github/workflows/arsenal.yml` runs the full suite on
  every push and on schedule

The TDD log at `techne/TDD_LOG.md` is the long-term quality artifact.
ARSENAL.md is the user-facing reference; TDD_LOG.md is the
quality-history reference.
