# BIND/EVAL v2 — implementation notes

Author: Techne (2026-05-03)
Status: shipped alongside v1; v1 retained as reference for one cycle.

## Why v2 exists

The v1 ``BindEvalExtension`` (in ``sigma_kernel/bind_eval.py``) bypassed the
kernel's central CLAIM → FALSIFY → PROMOTE discipline. Two MVP comments
admitted this self-exception:

- ``bind_eval.py:355-376`` — *"this is the MVP path; in production this
  would go through CLAIM → FALSIFY → PROMOTE, but BIND is itself a
  discipline-bearing op so we let the cap consumption + content hash do
  the integrity work."*
- ``bind_eval.py:514`` — same self-exception for the EVAL path.

Per the consolidated 2026-05-03 team review (Aporia + Ergon + Charon)
and the external pressure-test (ChatGPT), this was the single
load-bearing structural concern. ChatGPT's framing:

> If BIND bypasses CLAIM → FALSIFY → PROMOTE, the Σ-kernel stops being
> an epistemic system and becomes a logging system with vibes.

The kernel's value proposition depends on no opcode having a
self-exception. v2 fixes this.

## How v2 differs from v1 mechanically

### Opcode flow

v1 BIND (single mutation through ``bootstrap_symbol``):

    BIND → consume_cap → bootstrap_symbol → write bindings row

v2 BIND (full kernel pipeline):

    BIND → CLAIM → in-process bind_validation Ω → bind verdict → GATE
         → consume_user_cap → mint internal PromoteCap → kernel.PROMOTE
         → write bindings row

v2 EVAL (full kernel pipeline):

    EVAL → CLAIM → pre-execution eval_validation Ω (drift check)
         → execute under tracemalloc + oracle counter
         → 3-dim BudgetExceeded enforcement
         → post-execution eval_validation Ω (cost ceiling)
         → bind verdict → GATE
         → consume_user_cap → mint internal PromoteCap → kernel.PROMOTE
         → write evaluations row

### Claims/symbols/bindings ratio

| Path        | claims rows | symbols rows | bindings rows | evaluations rows |
|-------------|-------------|--------------|---------------|------------------|
| v1 BIND     |           0 |            1 |             1 |                0 |
| v2 BIND     |           1 |            1 |             1 |                0 |
| v1 EVAL     |           0 |            1 |             0 |                1 |
| v2 EVAL     |           1 |            1 |             0 |                1 |

v2 doubles the claims-table footprint per opcode; the substrate growth is
+1 claim row per BIND/EVAL on top of v1's existing 3 rows/EVAL. Acceptable
for the integrity gain.

### Capability handling — dual-cap pattern

The kernel's ``PROMOTE`` enforces ``cap_type='PromoteCap'``. v1 callers
pass a ``BindCap`` / ``EvalCap`` and v1's BIND/EVAL consumes them
directly via a manual ``UPDATE capabilities ... consumed=1``. v2 cannot
do that because routing through ``kernel.PROMOTE`` requires a
``PromoteCap``.

Rather than break the v1 API or modify ``sigma_kernel.py`` (forbidden by
the task scope), v2 implements a **dual-cap consume**: the user-supplied
cap (``BindCap`` / ``EvalCap``) is consumed for linear-discipline
accounting via ``_consume_user_cap``, then v2 mints a fresh internal
``PromoteCap`` and passes it to ``kernel.PROMOTE``. Both consumptions
are persisted in ``capabilities``; any cross-process auditor sees both
rows.

This is an MVP compromise. The cleanest fix is to relax
``kernel.PROMOTE``'s ``cap_type`` filter to accept any cap that
authorizes promotion; that requires a ``sigma_kernel.py`` edit and is
deferred to the next kernel revision.

### In-process Ω validators

A new module ``sigma_kernel/omega_validators.py`` exposes two validators:

- ``bind_validation(payload, seed) -> (Verdict, rationale)``
  - imports ``callable_ref``
  - hash drift check against ``expected_callable_hash`` if supplied
  - ``cost_model`` finite-positive checks (``max_seconds > 0``,
    ``max_memory_mb > 0``, ``max_oracle_calls >= 0``)
  - postconditions / authority_refs shape (None or non-empty list of
    non-empty strings)

- ``eval_validation(payload, seed) -> (Verdict, rationale)``
  - imports ``callable_ref``
  - drift check against ``stored_callable_hash``
  - ``args`` shape
  - 3-dim ``actual_cost`` vs ``cost_model`` budget verification

**Divergence from ``omega_oracle.py``.** The production Ω oracle runs
as a separate subprocess (control-plane / data-plane split, the kernel
sees only the signed result blob). The new validators run in-process.
This is **deliberate** and **load-bearing for the perf claim**: routing
every BIND/EVAL through a subprocess Ω adds 50ms+ of fork+JSON
overhead, which would put each BIND/EVAL into the 50ms range — three
orders of magnitude over the target. The validators only do mechanical
structural checks (hash equality, finite-positive numeric checks,
list-shape checks); subprocess isolation buys nothing because the
checks are pure-function and don't touch external state.

If the kernel ever needs cross-process isolation for these checks
(e.g., to defend against a maliciously crafted binding that hijacks the
parent interpreter), they hoist into ``omega_oracle.py`` cleanly — the
contract returned (``(Verdict, rationale)``) is identical.

## Performance comparison

Bench: ``python sigma_kernel/bench_bind_eval.py`` (n=200 each, p50 of
sorted timings, in-memory SQLite, Python 3.11, Windows 11, mahler_measure
on the Lehmer polynomial as the bench callable).

| Metric         | v1 p50  | v2 p50  | v2/v1 | < 5ms target |
|----------------|---------|---------|-------|--------------|
| BIND           | 0.28 ms | 0.34 ms | 1.23x | yes          |
| EVAL           | 0.50 ms | 0.84 ms | 1.67x | yes          |
| BIND p95       | 0.39 ms | 0.49 ms | 1.26x | yes          |
| EVAL p95       | 0.68 ms | 1.13 ms | 1.66x | yes          |

The v2/v1 ratio is dominated by the extra CLAIM row write + the
``in-process`` Ω validator call. Both opcodes stay an order of magnitude
under the 5ms target; the integrity gain is paid for in microseconds.

### Why p50 stayed under target

The validators are ~50µs (no subprocess), the extra ``CLAIM`` row is
~100µs, and the extra ``mint_capability`` + dual-consume + PROMOTE adds
~200µs. Total v2 overhead vs v1 is ~350µs. We have 9000µs of headroom.

## C2 instrumentation status

The ``CostModel`` declares three cost dimensions; v1's MVP measured
only ``elapsed_seconds`` and recorded zeros for the other two. ChatGPT's
review framed this as *"a guaranteed RL exploit, not a hypothetical
one"* — any RL agent will discover and route through unmetered
dimensions.

v2 (and v1, via the inherited C2 code) now tracks all three:

### oracle_calls (thread-local counter)

- ``_ORACLE_DISPATCH_COUNTER`` is a ``threading.local()`` object;
  per-EVAL it is reset to 0 then read after the callable returns.
- **Covered dispatch sites:**
  - ``cypari.pari(*args, **kwargs)`` and any ``cypari.pari.<method>``
    proxy call — patched by wrapping ``cypari.pari`` with a counting
    proxy at first-EVAL time. Idempotent + thread-safe.
  - ``subprocess.run`` — patched at module level; any callable that
    shells out to PARI/SymPy/external solvers via subprocess
    increments the counter once per call.
- **Uncovered dispatch sites:**
  - LMFDB HTTP queries (no current arsenal callables route through
    LMFDB API at EVAL time; if added, an HTTPSConnection-level patch
    belongs here).
  - Direct C-extension calls that bypass Python frame entry (current
    arsenal does not exercise this path; flint/numpy operations are
    pure-CPU and don't count as oracle dispatch).
  - Network calls via ``urllib`` / ``requests`` (not currently used in
    arsenal callables; would need their own patches).

The contract is **monotonic accountability, not precision**. If an
agent learns to evade the counter by routing through an unhooked path,
that path is a substrate gap to fix; the counter never under-reports
known dispatch sites.

### memory_mb (tracemalloc peak-delta)

- Each EVAL snapshots ``tracemalloc.get_traced_memory()`` before the
  callable runs and reads peak after; reports ``(peak - before) /
  1024^2`` MB.
- ``tracemalloc.reset_peak()`` is called when available (Python ≥ 3.9).
- If ``tracemalloc`` was already running for an outer profile, the v2
  EVAL leaves it running; otherwise it starts and stops locally.
- **Accuracy.** ``tracemalloc`` reports actual Python-allocator
  bytes; for a callable that allocates a list of 200k ints, the
  reported value is within 5-10% of the underlying ``sys.getsizeof``
  total. **The 2x-of-actual claim from the task spec holds for
  Python allocations** (lists, dicts, ndarrays via numpy's Python
  allocator). It does NOT cover allocations from C extensions that
  use ``malloc`` directly (e.g. parts of cypari or some flint paths);
  those are invisible to ``tracemalloc``. For the current arsenal
  this is acceptable because the dominant cost dimension for cypari
  is ``oracle_calls`` (already counted) rather than memory.

### 3-dim budget enforcement

``BudgetExceeded`` is now raised on overshoot of any of the three
dimensions, not just ``elapsed_seconds``. v1 (the inherited code) and
v2 share the enforcement block; v2's tests exercise each dimension
independently.

## Migration path

v1 stays for one cycle as the reference implementation. Downstream
consumers update to v2 in the next session:

- ``prometheus_math/sigma_env.py`` — currently constructs
  ``BindEvalExtension``. After v2 acceptance, swap to
  ``BindEvalKernelV2``. The composition test
  ``test_composition_sigma_env_works_with_v2_extension`` already
  validates this swap closes the loop.
- ``prometheus_math/discovery_env.py`` — same swap.
- ``prometheus_math/obstruction_env.py`` — same swap.

After all three envs migrate, v1 can be removed in the cycle after
that. The two-cycle window gives any in-flight RL training runs time
to checkpoint and restart.

## Test counts

Test file: ``sigma_kernel/test_bind_eval_v2.py`` (~600 LOC).

| Category    | Count |
|-------------|-------|
| Authority   |     5 |
| Property    |     5 |
| Edge        |     5 |
| Composition |     4 |
| Oracle-coverage (auth) | 1 |
| **Total**   |    20 |

Each category is at math-tdd skill score ≥ 2 (≥ 3 distinct concerns
covered). The full suite is RED before v2 + omega_validators are added,
GREEN after.
