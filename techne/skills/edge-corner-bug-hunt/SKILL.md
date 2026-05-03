---
name: edge-corner-bug-hunt
description: Systematic search for hidden failure modes in substrate code AFTER math-tdd's correctness gate has passed. Enforces seven surface-area probe categories (boundary, equivalence-class, fuzzing, adversarial, state-machine, differential, error-injection) on every public function the substrate exposes. Use whenever a new sidecar / opcode / kernel extension lands, during code review of substrate-grade modules, or when extracting a generalized probe from a bug-report post-mortem.
---

# edge-corner-bug-hunt

`math-tdd` enforces that every forged operation has 4 categories of
correctness tests. That gate keeps the math right. It does NOT exhaust
the surface area an LLM agent can hit at runtime.

The bugs that have actually shipped in the substrate weren't bugs of
mathematical correctness — the math was right. They were bugs of
*surface area*: an input shape the author didn't picture, a
side-effect on module-level state, a SQL cast that worked in unit
tests but blew up in live integration, a truncation that silently
corrupted a hash. None of those would be caught by "test on Heegner
discriminant -163 and confirm h=1."

This skill is the systematic search for that second class of bug. It
is invoked AFTER `math-tdd`'s 4-category gate passes, before the
operation is declared substrate-ready.

## When to invoke

Invoke this skill any time:

- A new operation, sidecar, opcode, or kernel extension has just
  passed `math-tdd`'s 4-category gate and is one step from being
  declared production.
- You are reviewing a PR that touches substrate-grade code (anything
  under `prometheus_math/`, `techne/lib/`, `aporia/scripts/` that
  Hephaestus or Athena might call from a forged tool, or any
  Postgres / LMFDB / OEIS adapter).
- A bug has been reported that wasn't caught by tests. Bug-hunt then
  extracts a *generalized probe* from the post-mortem and adds it to
  a per-module checklist so the same shape of bug can't recur silently
  elsewhere.
- You are auditing an existing module that predates this skill — walk
  the seven categories and add the missing probes.

Do NOT invoke for:
- Internal helper functions with no public surface, never called
  outside their defining module, with no LLM-agent reachability.
- Cosmetic / formatting changes (whitespace, type-hint additions
  with no semantic shift, comment edits).
- Documentation-only commits.
- One-off scratch scripts that will be deleted within 24 hours
  (mark them `scratch/` and skip).

The default presumption is **invoke**. If a function is reachable
from a forged tool, an Athena evaluation, a Hephaestus search, an
agora message handler, or any HTTP/CLI surface, it is public from the
substrate's perspective even if Python's `_underscore` says otherwise.

## The seven bug-hunt categories

Every public function, method, or class on the surface of the module
must have at least one probe in each category. These categories were
chosen because each one names a class of bug the substrate has
actually shipped (citations live in §5 anti-patterns and §6 worked
examples).

### 1. Boundary value analysis

For every numeric input to the operation, write probes that exercise:

- `0`
- `1`
- `-1`
- `INT_MAX` / largest documented valid value
- `INT_MAX + 1` / one past the largest documented valid value
- `INT_MIN` / smallest documented valid value
- `INT_MIN - 1` / one past the smallest
- `float('inf')`, `float('-inf')`
- `float('nan')`
- very small positive: `1e-300`
- very large positive: `1e300`

For each of those eleven slots, document in a comment beside the
probe **either** the expected behavior (raises `X`, returns `Y`,
clamps to `Z`) **or** the explicit reason the slot is excluded
(e.g., "input is `Optional[int]`, NaN unreachable; explicitly
filtered at line 47"). Excluded-without-justification = the slot is
not yet probed; come back to it.

For non-numeric inputs (strings, lists, dicts), the analogous
boundaries are: empty, single element, very long element, length 0
vs 1 vs 2 (Python's off-by-one slice trap), and structural extremes
(deeply nested vs flat).

### 2. Equivalence class partitioning

For every input domain, partition the input space into equivalence
classes — sets of inputs that the function should treat the same
way. Then write a probe at the boundary BETWEEN each adjacent pair
of classes.

A typical integer input partitions as: zero / positive small / positive
large / negative small / negative large / overflow. The boundaries
are at 0, ±1, ±SMALL_LARGE_THRESHOLD, ±OVERFLOW_THRESHOLD. A typical
polynomial-coefficient input partitions as: degree-0 / degree-1 /
degree-2-to-cyclotomic-bound / degree-above-cyclotomic-bound. A
typical LMFDB-label input partitions as: well-formed / malformed /
ASCII-but-unknown / Unicode-but-syntactically-valid.

For each pair of adjacent classes, write one probe at each side of
the boundary. The boundary between classes is where most logic bugs
live — guards written as `>` instead of `>=`, casts that round
mid-class, etc.

### 3. Property-based fuzzing with Hypothesis

For every public function, write at least one Hypothesis strategy
that generates valid-but-unusual inputs. The strategy must:

- Generate inputs that **satisfy the function's documented
  precondition** (no garbage-in / garbage-out, that's category 4).
- Check that the **postcondition holds** on every generated input.
- Run for at least 100 examples (Hypothesis default).

Set `deadline=10000` (10s per example) to handle slow numerical
work; set `max_examples=500` for fast operations. Use
`@settings(deadline=None)` only as a last resort, and document why.

The goal is to find at least one input where the postcondition is
*questionable* — the function returns something the implementer did
not predict. Note such inputs even if you decide they are not bugs;
they belong in the docstring as "documented quirky behavior."

```python
from hypothesis import given, settings, strategies as st

@given(coeffs=st.lists(st.integers(min_value=-20, max_value=20),
                       min_size=2, max_size=15))
@settings(deadline=10000, max_examples=200)
def test_fuzz_distinct_abs_coefficient_count(coeffs):
    """The F6 base-rate check must distinguish 'reciprocal' from
    'palindromic-by-coincidence'. Hypothesis fuzz."""
    if all(c == 0 for c in coeffs):
        return
    rate = f6_base_rate_check(coeffs)
    assert 0.0 <= rate <= 1.0
```

### 4. Adversarial inputs

Explicitly try to *break* the operation. The mindset is "if I were
an attacker / a confused LLM agent / a corrupted upstream pipeline,
what would I send?" Probe categories:

- Empty containers: `[]`, `{}`, `''`, `set()`, `tuple()`.
- All-zeros, all-ones, all-same.
- Palindromes (when the function processes sequences — palindromes
  often defeat naive directional logic).
- Very long inputs (length 1e6 of a list, 1e9 of a string).
- Inputs that violate the function's *implicit* assumptions (e.g.,
  the function's docstring says "polynomial," you pass a non-monic
  with leading zero; the function says "sorted," you pass unsorted).
- Malformed JSON / malformed Python source / malformed SQL / malformed
  LMFDB label.
- Unicode trickery: zero-width joiners, RTL marks, lookalike
  characters (Cyrillic 'а' vs Latin 'a'), combining accents.
- SQL injection patterns in any string passed to a database adapter.
- Path traversal patterns (`../../../etc/passwd`) in any string passed
  to a file adapter.

For each adversarial input, document the expected response: graceful
ValueError with diagnostic message / sanitization to safe form / raise
and propagate. Silent swallow of an adversarial input is a bug.

### 5. State-machine testing for stateful APIs

For every method that mutates state — every `__init__`, `reset`,
`step`, `set_*`, `register_*`, `clear_*`, etc. — write probes that
run sequences of method calls in different orders.

The failure mode this category catches is asymmetry between two
mutators that *should* be inverses or commutative but aren't. The
canonical substrate example: `SigmaMathEnv.reset()` recreates the
kernel; `DiscoveryEnv.reset()` does not. Same word, different
contract — and tests that only call `reset()` once never see it.

Required probes:

- **Round trip**: for any `init` / `reset` pair, verify
  `init(); state == reset(); state` modulo documented exceptions.
- **Commutation**: for any two mutators A, B, verify whether
  `A(); B()` equals `B(); A()` AND document the result either way.
  Non-commutativity is fine; *unintended* non-commutativity is a bug.
- **Idempotence**: for any operation that should be idempotent
  (`reset`, `flush`, `close`), verify
  `op(); op() == op()`.
- **Re-entrancy**: invoke the same method from within a callback
  fired by the method (where applicable). Document whether the
  module supports re-entrant calls or rejects them.
- **Cross-instance contamination**: instantiate two copies, mutate
  one, verify the other is unchanged. Catches module-level state
  leaks (the `_patch_postgres_tables` failure mode).

Use the `hypothesis.stateful` `RuleBasedStateMachine` for complex
state spaces; for simple two-or-three-state machines, hand-rolled
`pytest` fixtures suffice.

### 6. Differential testing

When there exists a *second implementation* of the same operation —
an alternative backend, a naive reference, a slow-but-correct version,
a published table the operation was meant to reproduce — run both
and compare on a sampled input set.

Differential testing is the highest-yield category for substrate
bugs because most substrate operations have a slow reference
implementation (PARI / Sage / Mathematica / hand-computation) that
the fast version is an optimization of.

Required probes when a second implementation exists:

- Sample 50–500 inputs from the operation's typical use distribution.
- Run both implementations on each.
- Assert agreement modulo a documented tolerance.
- For disagreements: log the input, both outputs, and either fix the
  fast version OR document the disagreement as a known limitation
  (rare; usually it's a bug).

When NO second implementation exists, this category is satisfied by:

- Writing a naive reference implementation in the test file (slow,
  obviously correct, ~10 lines), and using it as the reference for
  the differential test. This is itself a high-quality forcing
  function on the implementer's understanding of the spec.

### 7. Error injection

For every external dependency call — subprocess, HTTP, database
query, file read, any I/O the operation performs — simulate the call
failing. Use `unittest.mock` or `pytest-mock` to inject:

- Timeout (`socket.timeout`, `requests.Timeout`).
- Connection refused (`ConnectionRefusedError`).
- Connection reset mid-stream (`ConnectionResetError`).
- DNS failure (`socket.gaierror`).
- Malformed response (HTTP 200 with garbage body, JSON that doesn't
  parse, SQL result with unexpected column types).
- Partial response (truncated stream, HTTP `Content-Length` wrong).
- Exception during parse (`json.JSONDecodeError`,
  `psycopg2.errors.DataError`).
- Rate-limit response (HTTP 429, server-sent retry-after).
- Server error (HTTP 500, 502, 503).
- Permission denied (HTTP 403, OS `PermissionError`).
- Disk full (`OSError` with `errno.ENOSPC`).
- Out-of-memory during result materialization (raise `MemoryError`).

For each failure mode, verify the operation:
- Either degrades gracefully (returns a documented sentinel, raises
  a documented exception type with a diagnostic message).
- Or, if the failure is unrecoverable, terminates the operation
  cleanly without leaking file handles, DB connections, or
  partially-mutated state.

The substrate's `LMFDB nf_fields.coeffs %s::numeric[]` cast bug is
this category: the unit test mocked the DB call with valid output,
but live Postgres rejected the cast. Error injection probes that
inject "DB returns DataError" would have flagged the brittle cast
path.

## The hunt protocol

When you invoke this skill on a module:

### Step 1 — Enumerate the public surface

List every public function, method, and class in the target module.
"Public" means **reachable from outside the module**, including:

- Items in `__all__`.
- Items not prefixed with underscore.
- Items prefixed with underscore that are imported from sibling
  modules (Python convention says "internal", but the substrate
  reaches them — count them).
- Module-level callables (yes, including the `if __name__ ==
  "__main__"` script block, if it does work).

Write the list to a scratch file at the top of the bug-hunt session.

### Step 2 — Walk the seven categories per surface item

For each item from Step 1, walk the seven categories and write down
**at least one specific probe per category** (or an explicit
exclusion with justification). 7 categories × N items = ~7N probe
descriptions. This is a lot; that's the point. The substrate has
many small surfaces; each surface is small but the product is large.

The output of this step is a markdown table (or plain text list) of
shape:

```
catalog_consistency.run_consistency_check
  boundary:        coeffs=[], coeffs=[0], coeffs=[1, 0, 0, 0, ..., 0]*1e6
  equivalence:     degree=0|1, degree=2|3, degree=cyclotomic-bound|+1
  fuzz:            hypothesis strategy on small int polys
  adversarial:     unicode label, SQL injection in label, malformed LMFDB id
  state-machine:   N/A — pure function (document in comment)
  differential:    compare against PARI's `polisirreducible` for irreducibility
  error-injection: LMFDB returns 503; OEIS returns truncated JSON
```

### Step 3 — Implement the probes

In `tests/test_<module>_bughunt.py`, sibling to the existing
per-module tests, implement each probe as a `pytest` test. One probe
per `def test_*` (so failures point to a specific surface×category
intersection).

Naming convention: `test_bughunt_<surface>_<category>_<scenario>`.
Example: `test_bughunt_run_consistency_check_boundary_empty_coeffs`.

### Step 4 — Run them

Run `pytest tests/test_<module>_bughunt.py -v`. Every probe that
fails IS one of:

- A bug.
- A documented edge that the test asserted incorrectly.
- An ambiguous case — the function does something, you don't know
  if it's right.

Failing probes are the deliverable of this skill. Zero failures on
first run is suspicious; either the probes are too weak or the module
is unusually mature. (For first-time bug-hunts on substrate code we
have empirically found 1–4 real bugs per ~50 probes.)

### Step 5 — Triage failing probes

For each failing probe, decide:

- **(a) Bug** → file in `BUGS.md` with the probe, the failure, and
  the proposed fix. Fix it. Re-run probe; verify green.
- **(b) Intentional edge** → document the behavior in the function's
  docstring (the "Documented quirky behavior" section). Update the
  probe to assert the documented behavior. Re-run; verify green.
- **(c) Ambiguous** → escalate to the operator/architect. Mark the
  probe with `@pytest.mark.xfail(reason="ambiguous; awaiting decision
  from <person>")` and proceed.

Category (a) outcomes are pure wins — bugs found before they could
corrupt provenance. Category (b) outcomes are documentation wins —
the function's contract is now sharper. Category (c) outcomes
surface architectural questions that need a human decision.

### Step 6 — Commit the probes to the permanent suite

Once all probes are either green or `xfail`-with-rationale, commit
the file. The probes now run on every CI cycle and become part of
the module's permanent surface-coverage harness.

The commit message must:
- Name the module bug-hunted.
- Cite the categories scored (per the rubric in §4).
- List the bug count by triage category: `bugs: N, docs: M, xfail: K`.
- Co-author Claude.

## Hunt-quality rubric

Score each category 1–3, mirroring `math-tdd`'s rubric.

| Category          | Score 1                           | Score 2                                           | Score 3                                                                |
|---|---|---|---|
| Boundary          | One numeric boundary probe       | All eleven boundary slots probed or excluded       | + non-numeric boundaries (empty/single/long/nested)                  |
| Equivalence       | One class boundary probed         | All adjacent class pairs probed                   | + class partition documented in module docstring                       |
| Fuzz (Hypothesis) | One strategy, default settings   | One strategy per public surface, deadline tuned   | Strategies include valid-but-unusual generators (e.g., palindromic)   |
| Adversarial       | Empty / all-zeros probed          | + malformed input, unicode trickery               | + injection patterns (SQL, path, prompt) where applicable              |
| State-machine     | Round-trip probed (or N/A noted)  | + commutation + idempotence                      | + re-entrancy + cross-instance contamination                           |
| Differential      | One comparison vs reference       | + 50–500 sampled inputs                          | + reference implementation written in-test if no external one exists  |
| Error injection   | One I/O failure probed            | + timeout + malformed response + 5xx              | + partial response + rate-limit + resource-exhaustion                  |

A bug-hunt is "substrate-grade" iff it scores ≥ 2 in every category
applicable to the module. Modules that are pure (no I/O) are exempt
from category 7; modules that are stateless are exempt from category
5; document the exemption explicitly so future auditors don't think
the category was forgotten.

Aim for ≥ 2 in every applicable category before declaring the
operation substrate-ready.

## Anti-patterns

These are anti-patterns the substrate has actually shipped — each
one is cited from the bug list in the spec for this skill.

### "It's an internal function, doesn't need bug-hunting"

Wrong. Every callable an LLM agent might invoke — directly via
forged tool, indirectly via a sidecar opcode, transitively via a
pipeline orchestrator — is a public surface from the substrate's
perspective. The Python convention of "underscore = internal" is
about source-code modularity, not about runtime reachability.

The `_patch_postgres_tables` bug is the canonical case: an
underscore-prefixed helper that mutated module-level state.
Pre-skill, no test caught it; Aporia's code review caught it. Under
this skill, category-5 (state-machine, cross-instance contamination)
catches it because the probe explicitly creates two instances and
verifies they don't share state.

### "Hypothesis tests are slow, we'll skip them"

Wrong. Hypothesis is the highest-yield category-3 mechanism we have.
The mitigations:

- Set `@settings(deadline=10000, max_examples=200)` per test —
  caps the wall time at 10s × 200 = 33 minutes worst-case, usually
  far less.
- Use `--hypothesis-seed=0` in CI for reproducibility; tests still
  fail on the same input every run.
- Profile the strategy and tighten it (e.g., `min_size=2,
  max_size=8` instead of unbounded lists).
- Run the slow Hypothesis suite in a separate CI job tagged
  `@pytest.mark.slow`, so the fast feedback loop stays fast and the
  slow loop runs nightly.

The 2000-char `output_repr` truncation bug would have been found by
a Hypothesis test that generates inputs with `len(repr(x)) > 2000`
and asserts no two distinct inputs collide on hash. Skipping
Hypothesis = leaving the bug in.

### "We can fix the bug if it's reported"

Wrong, and dangerous, for substrate-grade code. The substrate's
purpose is to produce *trusted research artifacts* — Mossinghoff
verifications, Lehmer surveys, BSD checks. A bug that ships in
substrate code corrupts the provenance of every downstream artifact
that relied on it. There is no clean rollback for "this paper used
the buggy version."

The F6 base-rate distinct-|coefficient| bug is the canonical case:
caught at TDD time, but only because the implementer chose to probe
a specific failure mode (Lehmer's polynomial). The category-2
equivalence-class probe ("polynomials whose distinct |coefficients|
count differs from distinct coefficients count") would have caught
it systematically rather than by lucky inspection.

The discipline is: find them first.

### "Six categories already covered by math-tdd, why seven more"

Wrong framing. `math-tdd`'s four are correctness gates: did you
implement the math right? `bug-hunt`'s seven are surface-area
probes: did you handle every shape of input the substrate can
deliver? Different jobs.

A function can be 100% mathematically correct on the inputs it was
designed for, and still ship the LMFDB `%s::numeric[]` cast bug
because the SQL adapter's input shape wasn't part of the math
contract. `math-tdd` doesn't know SQL adapters exist; `bug-hunt`
category 7 (error injection) does.

### "The cross-process double-spend is fine, the in-process test passed"

Wrong. The substrate is multi-process: agora messages are processed
by independent daemons; Hephaestus search runs in a worker pool;
Athena evaluation forks subprocesses. A claim that "double-spend is
prevented" must be tested at the process boundary it actually
crosses.

This is bug-hunt category 5 (state-machine) plus category 7 (error
injection: simulate the lock-acquisition call failing partway). The
in-process test passes because it's testing in-process semantics; the
production failure is at the SQL `SELECT ... FOR UPDATE` boundary.

## Worked example 1 — bug-hunting `catalog_consistency`

Module under hunt:
`techne/lib/catalog_consistency.py` (hypothetical but representative
of substrate adapter modules).

Public surface (Step 1):
- `run_consistency_check(coeffs, *, sources=...) -> CatalogResult`
- `lmfdb_nf_adapter(coeffs) -> Optional[LMFDBHit]`
- `lmfdb_ec_adapter(label) -> Optional[LMFDBHit]`
- `oeis_adapter(seq) -> Optional[OEISHit]`
- `magma_adapter(payload) -> Optional[MagmaHit]`
- `sage_adapter(payload) -> Optional[SageHit]`
- `CatalogResult` (dataclass; constructor + `as_dict`)

Walking the seven categories on `run_consistency_check`:

```
boundary:
  coeffs=[]               -> ValueError("empty polynomial")
  coeffs=[0]              -> ValueError("zero polynomial")
  coeffs=[1]              -> documented edge: degree-0 polys not in LMFDB,
                             returns CatalogResult(hits=[], skipped=['lmfdb_nf'])
  coeffs=[1] + [0]*1000   -> length 1001 — passes through; verify no
                             SQL parameter overflow

equivalence:
  degree=0 vs degree=1    -> probe both sides of the LMFDB-coverage boundary
  degree=49 vs degree=50  -> LMFDB nf_fields max degree is 47; verify
                             clean degradation at 48, 49, 50
  cyclotomic vs non-cyc   -> known LMFDB indexing quirk, partition by
                             irreducibility class

fuzz:
  hypothesis: lists of integers in [-20, 20], min_size=2, max_size=15
  postcondition: result is None OR result.hits is a list and every
    hit has fields {label, source, degree}

adversarial:
  coeffs containing very large ints (Python bigint > 2^63) — does the
    %s::numeric[] cast handle it? <-- CITES the LMFDB cast bug.
  label="'; DROP TABLE nf_fields; --" passed to lmfdb_ec_adapter
  label="../../../etc/passwd" passed to lmfdb_ec_adapter
  unicode label with combining marks

state-machine:
  call run_consistency_check, then call again with same input — both
    runs should agree (idempotence in the read direction)
  call adapter mid-call from a callback — re-entrancy probe
  spawn two threads calling adapters simultaneously — module-level
    cache safe?

differential:
  for degree-2 polys, compare lmfdb_nf_adapter vs computing class
    number directly via PARI; compare on 200 random discriminants
  for irreducibility, compare against pari.polisirreducible

error-injection:
  LMFDB returns 503 -> retry with backoff, then raise ConnectionError
  LMFDB returns 200 with malformed JSON -> raise CatalogError
  LMFDB returns truncated row -> raise CatalogError, not silent None
  Postgres returns DataError on cast <-- CITES the LMFDB cast bug.
  OEIS times out -> CatalogResult.skipped includes 'oeis'
```

Three probes that found real concerns on a representative module of
this shape:

1. **LMFDB called with very-large-integer coefficients vs typical
   small-int coefficients** — the `%s::numeric[]` cast accepts small
   ints but raises `DataError` on Python `int`s exceeding the
   server-side `numeric` precision. Found by category-7 + category-1
   crossover probe.

2. **OEIS adapter called with all-zero coefficients vs only-leading-coef-nonzero**
   — the OEIS search-string builder concatenates non-zero coefficients;
   for `[0, 0, 0, 1]` it emits `"1"`, which matches A000012 (all
   ones) and returns a spurious hit. Found by category-4 (adversarial:
   all-zeros except one).

3. **`run_consistency_check` invoked while one adapter is mid-call
   from another thread** — module-level connection pool was shared;
   one adapter's transaction state leaked into the other's. Found
   by category-5 (state-machine: cross-instance / cross-thread
   contamination).

These three are exactly the shape of bug `math-tdd` would not catch
because they aren't bugs of mathematical correctness; they are bugs
of the surface the math is wrapped in.

## Worked example 2 — bug-hunting `SigmaMathEnv` / `DiscoveryEnv`

Module under hunt: the two RL environments cited in the bug list.
Public surface (per env):
- `__init__(config) -> None`
- `reset() -> Observation`
- `step(action) -> (Observation, reward, done, info)`
- `close() -> None`

The bug the spec cites: `SigmaMathEnv.reset()` recreates the kernel;
`DiscoveryEnv.reset()` does not. Same word, different contract.

Walking category 5 (state-machine) on this asymmetry:

```
state-machine probes for SigmaMathEnv:
  P1 round-trip: env=SigmaMathEnv(cfg); s1=env.reset(); env.step(a);
                 s2=env.reset(); assert s1 == s2
       — passes for SigmaMathEnv (reset recreates kernel, full reset)
       — FAILS for DiscoveryEnv (reset preserves kernel state, so the
         second reset returns post-step internal state in info)

  P2 commutation: env=Env(cfg); env.reset(); env.step(a); k1 = env.kernel
                  env=Env(cfg); env.step(a); env.reset(); k2 = env.kernel
       — DiscoveryEnv: k1 != k2 (asymmetric)
       — SigmaMathEnv: k1 == k2 (symmetric reset)

  P3 cross-instance: e1=Env(cfg); e2=Env(cfg); e1.reset() should NOT
                     change e2's state
       — module-level kernel registry caught here if shared

  P4 differential: run identical (action sequence) against both envs
                   from identical configs; they should agree on
                   trajectory mod the documented config differences
       — this catches the asymmetric-reset divergence
```

The probe `P1` for `DiscoveryEnv` fails: `s1 != s2` because the
kernel state survives `reset()`. Triage:
- (a) bug if the contract is "reset returns env to initial state"
- (b) intentional if the contract is "reset preserves the kernel and
  resets only the agent's local state"

Either way, the contract becomes explicit in the docstring after the
hunt. Pre-hunt: the contract was implicit; both envs claimed
`reset() -> Observation` but meant different things. Post-hunt:
docstrings disagree, tests assert the documented behavior, and any
caller relying on the wrong contract gets a CI failure.

## Worked example 3 — bug-hunting `output_repr` truncation hash

Module under hunt: the substrate's tool-output deduplication layer,
which hashes `repr(output)` truncated to 2000 characters. Spec cites
this as a silent collision risk that review caught but tests didn't.

Public surface:
- `output_hash(obj: Any) -> str`
- `dedupe_outputs(items: list) -> list`
- `seen_outputs: set[str]` (module-level state)

Walking the seven categories:

```
boundary:
  obj=None              -> hash a stable sentinel
  obj=""                -> hash of empty repr; document
  obj of repr length 1999  vs  2000  vs  2001
                        -> 2001 truncates; verify the truncated portion
                           still uniquely identifies the input

equivalence:
  repr-length classes: <2000, =2000, =2001, >>2000
  probe boundaries between each pair

fuzz:
  hypothesis strategy: generate two distinct large objects whose first
                       2000 chars of repr() agree; assert
                       output_hash(a) != output_hash(b)
       — this is the probe that finds the bug. Strategy:
         st.lists(...).map(lambda L: ('A'*2000 + str(i) for i in (1,2)))
       — Hypothesis finds the collision in <50 examples.

adversarial:
  obj whose repr() raises (custom __repr__ that throws) — does
    output_hash crash, or does it have a fallback?
  obj whose repr() is non-deterministic (e.g., contains object id) —
    document that hashes are unstable for such objects
  obj that's a recursive structure (a = []; a.append(a)) — does
    repr() recurse? Python truncates at 'Ellipsis'; verify hash
    behavior

state-machine:
  module-level seen_outputs across two runs of dedupe_outputs:
    is the second run isolated from the first? Test cross-instance
    contamination.
  reset/clear method exists? If not, document.

differential:
  alternate hash scheme: hashlib.sha256(pickle.dumps(obj)) — compare
    collision rates on a 10k-input sample; if the truncation hash
    has materially higher collision rate, that's a finding

error-injection:
  obj.__repr__ raises MemoryError mid-call (simulate via mock)
  obj.__repr__ takes 60s (simulate via mock with sleep)
```

The category-3 fuzz probe is the one that catches the spec-cited
bug. Hypothesis generates two large strings that share a 2000-char
prefix; both hash to the same value; `output_hash(a) ==
output_hash(b)` despite `a != b`. The fix is either to lengthen the
truncation, hash the full repr, or use a structural hash that
doesn't truncate. The probe stays in the suite as a regression test
for whichever fix is chosen.

## Integration with `math-tdd`

The two skills compose:

1. `math-tdd` runs first. The 4-category gate (authority, property,
   edge, composition) ensures the math is correct on the inputs the
   implementer envisioned.

2. `edge-corner-bug-hunt` runs second, AFTER `math-tdd`'s gate
   passes. The 7-category gate (boundary, equivalence, fuzz,
   adversarial, state-machine, differential, error-injection)
   ensures every shape of input the substrate can deliver is
   handled.

3. When `bug-hunt` finds a bug, the fix flows back to `math-tdd` as
   a new test in whichever of the four categories applies. (E.g., a
   fuzz-found bug becomes a new property test; an adversarial-found
   malformed-input bug becomes a new edge-case test.)

4. The TDD log at `techne/TDD_LOG.md` gets a parallel entry from
   `bug-hunt`. Format:

   ```
   2026-04-29 | catalog_consistency | B:3 E:2 F:3 A:3 S:2 D:2 I:3 | bugs:3 docs:2 xfail:1 | commit abc1234
   ```

   Categories: B=boundary, E=equivalence, F=fuzz, A=adversarial,
   S=state-machine, D=differential, I=injection.

5. The two skills together form the substrate-grade quality bar:
   `math-tdd` says the math is right; `bug-hunt` says the surface
   is hardened. A module is substrate-ready iff both gates pass at
   ≥ 2 in every applicable category.

## What this skill cannot do

The skill is a search heuristic, not a proof of correctness. It will
miss:

- **Bugs that require domain knowledge the bug-hunter lacks**: a
  subtle math error (off-by-half on a regulator, wrong sign on a
  Tate twist) that doesn't trigger any of the seven probe
  categories. These belong to `math-tdd` and to expert review.
- **Bugs in code paths that have no public surface**: dead code,
  branches not reachable from any caller. Bug-hunt only probes
  reachable callables. (Use coverage analysis to find dead branches
  separately.)
- **Bugs that only manifest under load**: race conditions that
  require thousands of concurrent calls, memory leaks that only
  matter over weeks of runtime, fragmentation patterns. Stress
  testing and long-running fuzz are separate disciplines.
- **Bugs in the dependency tree**: a bug in PARI, in psycopg2, in
  numpy. We can probe our wrapping of those tools; we cannot probe
  through them. (When found, file upstream and add a workaround
  probe so we don't regress when the dep is upgraded.)
- **Architectural bugs**: "this whole module shouldn't exist" or
  "the abstraction is wrong." Bug-hunt assumes the architecture is
  fixed and probes its surface. Architecture review is a separate,
  human-driven activity.

It is NOT a substitute for:
- `math-tdd`'s correctness gate (different job).
- Human code review (humans see architectural smell that no probe
  catches).
- Production monitoring (probes catch shapes; production catches
  distributions).

It IS a substitute for:
- Hoping the bug doesn't happen.
- Catching the bug "in review" by reading the code carefully (review
  is necessary but not sufficient — Aporia's review caught
  `_patch_postgres_tables`, but the four other bugs in the spec list
  shipped despite review).
- Catching the bug "in production" (which corrupts provenance).

## Skill output

When you complete this skill cycle on a module, append to
`techne/BUG_HUNT_LOG.md` (create if absent):

```
2026-04-29 | catalog_consistency | B:3 E:2 F:3 A:3 S:2 D:2 I:3 | bugs:3 docs:2 xfail:1 | commit abc1234
```

Format: `date | module | B:N E:N F:N A:N S:N D:N I:N | triage |
commit ref`. This becomes the long-term substrate-hardening audit
log, parallel to `TDD_LOG.md`.

The two logs together answer two questions a future auditor will ask:
- "Was the math right?" → `TDD_LOG.md`
- "Was the surface hardened?" → `BUG_HUNT_LOG.md`

Both are required. Neither is sufficient.
