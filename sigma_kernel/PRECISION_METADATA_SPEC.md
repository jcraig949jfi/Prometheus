# Precision Metadata Spec — Verification Depth as a First-Class Field

**Status:** Active (as of 2026-05-04)
**Migration:** `sigma_kernel/migrations/005_add_precision_metadata.sql`
**Tests:** `sigma_kernel/test_precision_metadata.py`,
`prometheus_math/tests/test_kill_vector_precision.py`
**Substrate impact:** Backwards-compatible. All existing Claims,
KillVectors, KillComponents continue to load without these fields and
behave as before.

## 1. Why precision is first-class

ChatGPT's reframe (2026-05-04): _"verification depth is a first-class
axis of truth, not a runtime detail."_

The triggering observation: today's Lehmer brute-force run had **17
entries** that failed mpmath at `dps=30`. ALL 17 converged at `dps=60`
via factor-then-nroots. The 17 are not noise — they are
resolution-dependent boundary objects.

Without precision logged on the substrate's evaluation event, the
ledger is epistemically under-specified:

> A `dps=30` PASS and a `dps=100` PASS look identical.

That conflation breaks every downstream consumer that reasons about
the substrate's verdicts: TRACE, kill-vector-based learners, RLVF
critics, and human reviewers all see the same `verdict.status="CLEAR"`
without any idea whether the underlying computation was numerically
trustworthy.

This spec promotes the missing axis to a typed substrate field.

## 2. The added fields

### 2.1 KillComponent (per-evaluation event)

Four new fields, all backwards-compatible (defaults reproduce
pre-change behavior):

| Field | Type | Default | Meaning |
|-------|------|---------|---------|
| `precision_dps` | `int \| None` | `None` | mpmath dps used (None = no mpmath). |
| `method` | `str` | `"unknown"` | One of `mpmath_polyroots`, `mpmath_nroots`, `numpy_eigvals`, `sympy_factor`, `catalog_lookup`, `exact`, `heuristic`, `unknown`. |
| `convergence_status` | `str` | `"n/a"` | One of `converged`, `failed_max_steps`, `nan_returned`, `exact`, `n/a`. |
| `stability` | `float \| None` | `None` | Bootstrap/perturbation-based stability score in `[0, 1]`. None = not computed. |

Vocabularies live in `prometheus_math.kill_vector` as `METHOD_VALUES`
and `CONVERGENCE_VALUES`. They are an open list (callers may pass
arbitrary strings); the named values are what downstream tooling
special-cases.

### 2.2 KillVector (aggregate across components)

Three derived fields (Python `@property`, no storage):

| Field | Type | Meaning |
|-------|------|---------|
| `min_precision_dps` | `int \| None` | Lowest non-None `precision_dps` across components — the weakest link. None iff no component recorded a dps. |
| `methods_used` | `tuple[str, ...]` | Sorted tuple representing the unordered set of methods invoked across components. |
| `convergence_summary` | `str` | One of `all_converged`, `partial_failure`, `all_failed`, `mixed_unrecorded`, `n/a`. |

Aggregate semantics:

* **all_converged** — every component is `converged` or `exact`.
* **all_failed** — every component is `failed_max_steps` or `nan_returned`.
* **partial_failure** — at least one good AND at least one bad.
* **mixed_unrecorded** — some good, no bad, some `n/a`.
* **n/a** — every component is `n/a` (legacy data).

### 2.3 Claim (per-CLAIM substrate metadata)

One new field on `sigma_kernel.sigma_kernel.Claim`:

| Field | Type | Default | Meaning |
|-------|------|---------|---------|
| `precision_metadata` | `dict \| None` | `None` | `{"dps": int\|None, "method": str, "convergence": str, "stability": float\|None}`. |

Persisted as JSON in the Postgres column `sigma.claims.precision_metadata
TEXT` (NULL when not provided). Hash-locked into the symbol's
`def_blob` at PROMOTE time so the substrate cannot lose precision
without changing the symbol's hash — same property as caveats
(migration 004).

## 3. Auto-caveat rules

Two rules fire at CLAIM time when `precision_metadata` is provided:

| Rule | Trigger | Caveat |
|------|---------|--------|
| Below floor | `dps != None` AND `dps < expected_min_dps` (default 60) | `precision_below_expected` |
| Convergence failure | `convergence in {"failed_max_steps", "nan_returned"}` | `verification_failed` |

Both auto-caveats:

* Are appended to whatever caveats the user passed (user tokens are
  never silently dropped).
* Get deduped if the user already supplied them explicitly.
* Auto-propagate via TRACE (same propagation as user caveats — see
  `caveat-as-metadata-on-CLAIM` proposal).

The default expected-minimum dps is **60** — the value Path A
confirmed converges for the 17 Lehmer entries that failed at dps=30.
Changing this default is itself a substrate-level change.

## 4. Backfill approach

The 17 INCONCLUSIVE entries from the Lehmer brute-force run were
rerun via three paths:

* **Path A** — `dps=60` converges via factor-then-nroots
* **Path B** — exact via `sympy.factor`
* **Path C** — catalog lookup against the literature

`prometheus_math.kill_vector.backfill_precision_from_legacy(record)`
reads a legacy record-shaped dict and returns a NEW dict with sensible
precision fields populated:

```python
record = {"candidate_hash": "...", "path_a_converged": True}
out = backfill_precision_from_legacy(record)
# out = {..., "precision_dps": 60, "method": "mpmath_polyroots",
#        "convergence_status": "converged", "_backfilled": "path_a"}
```

Inference rules:

1. `path_a_converged` → `dps=60`, `mpmath_polyroots`, `converged`
2. `path_b_exact` → `dps=None`, `sympy_factor`, `exact`
3. `path_c_catalog_match` → `dps=None`, `catalog_lookup`, `exact`
4. `mpmath_dps` field present → use it; convergence from `mpmath_failed`
5. Default → `dps=30`, `unknown`, `n/a` (the substrate's old default,
   epistemically honest)

The `_backfilled` stamp on the output dict prevents inferred values
from being mistaken for fresh measurements.

**Important:** per the task spec, this helper does NOT modify the
brute-force JSON files. Backfill happens at **load time** when reading
existing data via `KillComponent.from_dict`, which falls back to safe
defaults when the four new keys are absent.

## 5. Migration path (Postgres)

Migration 005 (`sigma_kernel/migrations/005_add_precision_metadata.sql`):

```sql
ALTER TABLE claims
    ADD COLUMN IF NOT EXISTS precision_metadata TEXT DEFAULT NULL;
CREATE INDEX IF NOT EXISTS idx_claims_precision_metadata
    ON claims (precision_metadata text_pattern_ops);
```

Both statements are idempotent (`IF NOT EXISTS`). Re-applying is safe.

The kernel's Postgres adapter probes for the column at `__init__`
time:

* If the column **exists**, the kernel uses 14-column INSERT.
* If the column **does not exist**, the kernel falls back to 13-column
  legacy INSERT. precision_metadata is silently dropped.

This means migration 005 can be applied **on its own schedule** —
deployments that have not yet rolled it out continue to function in
legacy mode, with precision_metadata=None for all new claims until
Mnemosyne applies the ALTER.

The SQLite path always carries the new column (created in `SCHEMA`
inside `sigma_kernel.py`), so local development and tests need no
migration — they get the new column automatically.

## 6. Open question: stability score computation

The `stability` field on KillComponent is reserved but unspecified.
What's the right cheap approximation?

Candidate proposals (open for stoa amendment):

1. **Bootstrap variance** — rerun the verifier on N≥10 perturbed
   inputs (small numerical noise on coefficients), compute the
   fraction of agreeing verdicts. Cost: O(N × verifier).
2. **DPS sweep** — rerun at dps=30/60/100, count how many agree with
   the dps=60 verdict. Cost: 3× verifier; falls out naturally if the
   substrate is doing precision audit anyway.
3. **Margin shape** — derived from existing kill_vector margins; no
   extra compute. But "shape of margins across falsifiers" is not
   what the substrate change asked for ("convergence stability"),
   so this would be a different thing under the same name.
4. **DEFER** — leave stability=None until the cheap approximation
   question is settled by a stoa proposal. Current default.

This spec leaves stability as `None` in all auto-emitted paths. A
caller computing it explicitly must specify which approximation was
used (in the metadata or in a follow-up proposal).

## 7. Acceptance test for adoption

If a downstream consumer of TRACE drops the precision_metadata, this
spec has failed. The test is:

```python
sym = k.PROMOTE(claim_with_precision, cap)
graph = k.TRACE(sym)
assert graph["precision_metadata"] == claim_with_precision.precision_metadata
```

This assertion lives in `test_composition_full_pipeline_claim_falsify_promote_trace`
in `sigma_kernel/test_precision_metadata.py`. Removing it would weaken
the substrate's epistemic guarantees.

## 8. Summary table — what changed

| Layer | Object | Fields added |
|-------|--------|--------------|
| `prometheus_math.kill_vector` | `KillComponent` | `precision_dps`, `method`, `convergence_status`, `stability` |
| `prometheus_math.kill_vector` | `KillVector` (derived) | `min_precision_dps`, `methods_used`, `convergence_summary` |
| `sigma_kernel.sigma_kernel` | `Claim` | `precision_metadata` |
| `sigma_kernel.sigma_kernel` | `SigmaKernel.CLAIM` | `precision_metadata` kwarg + auto-caveat firing |
| `sigma_kernel.sigma_kernel` | `SigmaKernel.PROMOTE` | hash-lock precision_metadata into def_blob |
| `sigma_kernel.sigma_kernel` | `SigmaKernel.TRACE` | propagate precision_metadata in graph nodes |
| Postgres schema | `sigma.claims` | `precision_metadata TEXT DEFAULT NULL` (migration 005) |
| SQLite schema | `claims` | `precision_metadata TEXT` (in `SCHEMA`) |

Net: **2 auto-caveat rules**, **8 substrate-level field additions**
(4 KillComponent + 3 KillVector aggregates + 1 Claim), **1 idempotent
migration**, **0 regressions**.
