# Pivot-Stack Bug-Hunt Report — 2026-04-29

Techne systematic edge-case / corner-case / bug-hunt over the
4-day pivot stack (commit 1666c4a4).

## Modules audited

Kernel-side (sigma_kernel/):
- `bind_eval.py` — BIND/EVAL v1 + C2 instrumentation
- `bind_eval_v2.py` — CLAIM/FALSIFY/PROMOTE-routed BIND/EVAL
- `residuals.py` — Residual + REFINE primitive
- `omega_validators.py` — in-process verdict validators (probed indirectly)

Pivot-side (prometheus_math/):
- `sigma_env.py` — Gymnasium bandit env
- `discovery_env.py` — generative reciprocal-poly env
- `discovery_pipeline.py` — DISCOVERY_CANDIDATE → CLAIM pipeline
- `obstruction_env.py` — OBSTRUCTION_SHAPE predicate-discovery env
- `_obstruction_corpus_live.py` — Charon live-data adapter
- `four_counts_pilot.py` — §6.2 + §6.4 harness (smoke-checked, no new probes)
- `withheld_benchmark.py` — §6.2.5 partition + benchmark
- `catalog_consistency.py` — §6.3 multi-catalog
- `arsenal_meta.py` + `_metadata_table.py` — registry of 85 ops

## Probes written

Total: **101 new probes** (60 pivot-side, 41 kernel-side, plus 2 regression
tests for in-session fixes). Distribution by category:

| Category | # probes | Notes |
| --- | --- | --- |
| 1 — Boundary value analysis | 28 | M=1.001, M=1.18, magnitude=0/1/NaN/inf, degree=0/1/2, holdout=0/1, tol=0, NaN cost models |
| 2 — Equivalence class partitioning | 12 | Residual classifier subclasses, callable_ref shapes, reward bucket coverage |
| 3 — Property-based fuzzing | 12 | Hypothesis @ deadline=10000, max_examples=50: round-trip, monotonic, determinism |
| 4 — Adversarial inputs | 14 | empty containers, unserialisable subsets, all-zero polys, all-positive corpora, action_table=[] |
| 5 — State-machine testing | 8 | reset/close/reset, double-spend caps, REFINE chain walking |
| 6 — Differential testing | 11 | hash-stability, manual-mirror palindromic, registry-key consistency, M-self-match |
| 7 — Error injection | 7 | source-hash drift, broken cost-model blob, PROMOTE failure → REJECTED, missing live data |
| **Total** | **92 unique** + 9 regressions | |

(Some tests appear in two categories; primary category counted.)

## Bugs found

| ID | Module | Category | Status |
| --- | --- | --- | --- |
| **B-BUGHUNT-001** | `bind_eval._resolve_callable` | 2 (equiv class) | filed; not fixed |
| **B-BUGHUNT-002** | `sigma_env.SigmaMathEnv.__init__` | 4 (adversarial) | **FIXED in session** |
| **B-BUGHUNT-003** | `bind_eval._patch_postgres_tables` | 7 (global state) | filed; design call |
| **B-BUGHUNT-004** | `bind_eval` cap.consumed dataclass attr | 5 (state) | filed; cosmetic |
| **B-BUGHUNT-005** | `sigma_env.SigmaMathEnv.__init__` | 4 (adversarial) | **FIXED in session** |

5 bugs found. 2 fixed in-session with regression tests. 3 filed for
follow-up.

### Bug summaries

**B-BUGHUNT-001 (NOT FIXED):** `BIND(callable_ref=None, ...)` raises
`TypeError: argument of type 'NoneType' is not iterable` from the `":"
not in callable_ref` membership check, instead of the typed
`BindingError`. Marked `@pytest.mark.xfail(strict=True)` in
`test_bughunt.py::test_callable_ref_none_raises_BindingError`. Fix is
one line but the BIND public contract needs to assert the type.

**B-BUGHUNT-002 (FIXED):** `SigmaMathEnv(action_table=[])` silently
swapped the empty list for a 13-row default via `action_table or
default_table()`. After the fix, `None` → default, `[]` →
caller-empty (which fall back to `n=1` minimal action_space for
gymnasium compat). Regression test:
`test_empty_action_table_is_honored`.

**B-BUGHUNT-003 (NOT FIXED):** Both `BindEvalExtension._patch_postgres_tables`
and `ResidualExtension._patch_postgres_tables` permanently extend the
module-level `core._TABLES` tuple with no rollback. On postgres
backends this leaks state across kernel instances. Out of scope —
kernel-core change.

**B-BUGHUNT-004 (NOT FIXED):** Every opcode begins with
`if cap.consumed: raise CapabilityError(...)`. But `Capability` is a
frozen dataclass and no code path mutates `consumed`. The check is
dead defense-in-depth; the only real guard is the DB-level
`UPDATE ... SET consumed=1 WHERE consumed=0` returning rowcount==0.
Cosmetic; not a security bug.

**B-BUGHUNT-005 (FIXED):** `SigmaMathEnv` stashed the caller's
`action_table` by reference, so `table.clear()` after construction
emptied the env's internal table. Defensive copy applied.

## Bug-hunt categories: density of findings

| Category | Probes | Findings | Density |
| --- | --- | --- | --- |
| 1 — Boundary | 28 | 0 | 0 — discipline tight |
| 2 — Equiv class | 12 | 1 (B-001) | low |
| 3 — Hypothesis | 12 | 0 | 0 — properties hold |
| 4 — Adversarial | 14 | 2 (B-002, B-005) | medium |
| 5 — State machine | 8 | 1 (B-004) | cosmetic |
| 6 — Differential | 11 | 0 | 0 |
| 7 — Error injection | 7 | 1 (B-003) | medium |

**Tight categories** (no probes failed):
- Boundary values on M (`_compute_reward`), magnitude (residuals),
  cost-model fields, partition fractions — every documented edge is
  honoured.
- Property-based: round-trip and determinism properties hold on the
  cost-model serializer, the args-hash, and the obstruction-env split.
- Differential: `_palindromic_from_half` is genuinely palindromic;
  the registry's keys round-trip; mossinghoff self-matches at default tol.

**Productive categories** (bugs found):
- Adversarial inputs: the `or` falsiness footgun + reference-aliasing
  footgun in `SigmaMathEnv` were both adversarial-input-specific.
- Error injection / global state: postgres table mutation + dead
  defense-in-depth `cap.consumed` check both surfaced via "what happens
  when X is broken / lying".

## Honest assessment — under-covered categories

**Cross-process linearity (claimed in docs, untested in code).** The
docstring of `BindEvalExtension._consume_cap` claims that double-spend
is rejected at the DB level. We tested same-process double-spend
through the same Python `Capability` object (passes). We did NOT test
cross-process: two threads/processes calling EVAL with the same cap
simultaneously. SQLite's UPDATE-with-WHERE-not-consumed is atomic, so
this likely works, but it is not proven. The substrate's value
proposition includes cross-process linearity claims; needs a real
parallel-EVAL test. **Domain expert needed:** someone who writes
SQLite concurrency tests, with the postgres backend story too.

**SQL parameter type mismatches (LMFDB array binding).** The
`lmfdb_check` function casts `coeffs` to `numeric[]` via the
`%s::numeric[]` cast. We did not exercise this path — it requires the
LMFDB mirror to be reachable, and our test suite skips the network. A
silent type-mismatch (e.g. when `coeffs` contains floats vs ints) could
make every catalog query miss without raising. **Domain expert needed:**
LMFDB / psycopg2 wire-format specialist.

**F-check false positives/negatives on edge polynomials.** The
discovery_pipeline F1/F6/F9/F11 checks were tested at *interface* level
(does it return a tuple? does it not crash?). We did not probe
mathematical edge cases: a polynomial with M just barely above the
permutation-null median; a polynomial where the cross-validation
agrees to 1e-7 but disagrees at 1e-6. The kill-rate calibration
matters at sub-percent rates; a domain expert should curate 30-50
edge polynomials and verify the F-check verdicts match
hand-computation. **Domain expert needed:** Mahler-measure / Salem
specialist; current tests rely on the published catalog.

**NaN propagation through composite reward shapes.** We tested NaN at
direct entry points (residual magnitude, _compute_reward). We did NOT
test NaN downstream: what if `mahler_measure` legitimately returns
NaN inside the EVAL? What if a single NaN in the obstruction-env
substrate eval poisons the obs vector? Both paths catch the NaN, but
the propagation across the substrate boundary is fragile and a single
unguarded `np.array(...)` could surprise.

**Hash truncation collisions (`output_repr` truncated before sha256).**
The eval_name uses `args_hash[:8]` which has a 50% collision rate at
~80K different argsets (birthday bound). The `(name, version)` PK on
symbols saves us: a collision just bumps the version. But the
`evaluation` rows would conflict, and the `evaluations.PRIMARY KEY
(name, version)` would reject the second insert. We did not write a
collision-test (it'd be slow). **Risk:** medium-low; the env mints
fresh versions per step so it's unlikely to bite at training-scale
(50 episodes × 10 steps = 500 args), but a long-running discovery
session at 10K+ episodes will eventually hit one. **Filed via this
report only; not as B-BUGHUNT entry.**

## Test counts — pivot stack after this session

| File | Tests |
| --- | --- |
| Existing pivot-stack tests | 269 |
| `prometheus_math/tests/test_pivot_bughunt.py` | 60 |
| `sigma_kernel/test_bughunt.py` | 41 |
| **Total pivot-stack tests** | **370** + 1 xfail |

Plus ~2480 non-pivot tests in the broader `prometheus_math/` and
`sigma_kernel/` suites — unaffected by this work.

## Most interesting findings

1. **The `or` falsiness footgun (B-BUGHUNT-002).** A single character
   (`or` vs `if ... is None`) means an explicit empty container is
   silently replaced with the default. This pattern recurs in Python
   APIs and tends to ship in v0.x because the default-value test
   passes; only the empty-collection test surfaces it. The fix is
   trivial; the discovery is the value.

2. **Dead defense-in-depth on capabilities (B-BUGHUNT-004).** All
   three opcodes (BIND, EVAL, REFINE) begin with `if cap.consumed:
   raise CapabilityError(...)`. The intent is clear (defense-in-depth
   against double-spend before the DB roundtrip). But `Capability` is
   frozen, so this check NEVER FIRES IN PRACTICE. The DB UPDATE saves
   us anyway, but the pattern looks like a guarantee that isn't.
   Worth either deleting or making real.

3. **Catalog tolerance with default tol=1e-5 has a soft limit on
   bookkeeping.** The Lehmer poly's mahler_measure is 1.176280818
   (9 sig figs in the snapshot). Our pipeline uses `1e-6` checks for
   F11 cross-validation but `1e-5` for catalog match. If F11 starts
   reporting M to 1e-7 precision, a polynomial whose true M is in
   the catalog but quoted to lower precision could miss the catalog
   check. The probe `test_M_drift` (passes) catches this exact case
   in `discovery_pipeline._f11_cross_validation`: the F11 mismatch
   message says "M drift 1.176281 vs reported 1.176000" — confirming
   the precision difference matters in practice.

## Suggested follow-up

1. Fix B-BUGHUNT-001 (typed BindingError on None callable_ref).
   Trivial; one line in `_resolve_callable`. Removes one xfail.
2. Decide on B-BUGHUNT-003 (postgres `_TABLES` mutation):
   instance-scoped vs context-managed vs accept-and-document.
3. Decide on B-BUGHUNT-004 (`cap.consumed` dataclass attr): mutate it,
   delete it, or document it.
4. Cross-process linearity test (load-bearing claim, currently untested).
5. Domain-expert review of F-check verdicts on a curated 30-50
   edge-polynomial set.
