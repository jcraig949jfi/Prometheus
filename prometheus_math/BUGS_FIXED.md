# Prometheus — Fixed Bugs Ledger

Resolved bugs in `prometheus_math` and adjacent code. Companion to the
open-bugs file at `F:/Prometheus/BUGS.md` (same entry format), but for
issues that have been diagnosed AND fixed AND have a regression test.

Started 2026-04-29.

Format per entry:
- File / location
- Reporter / discovery date
- Symptom (what the user / agent saw)
- Root cause (why it happened)
- Fix (what changed)
- Regression test (pointer)
- Lesson (transferable principle)

---

## prometheus_math/catalog_consistency.py

### F-CAT-001: LMFDB nf_fields.coeffs cast — integer[] vs numeric[]

**File:** `prometheus_math/catalog_consistency.py` (`lmfdb_check` adapter)
**Reporter:** Stream C, during §6.3 multi-catalog cross-check rollout
**Date discovered:** 2026-04-28
**Date fixed:** 2026-04-29
**Commit:** `1666c4a4`

**Symptom.** Live LMFDB queries from `lmfdb_check` against the
`nf_fields` table raised
`psycopg2.errors.DatatypeMismatch: operator does not exist: numeric[] = integer[]`
whenever the parameter was a Python `list[int]`. The adapter then
returned `CatalogResult(hit=False, error="query_failed: DatatypeMismatch: ...")`
instead of finding the record. Concretely, the call

```python
lmfdb_check([1, 0, 1], 1.0)   # Q(i), label 2.0.4.1
```

never landed a hit even though `2.0.4.1` is in LMFDB's `nf_fields`
with `coeffs = [1, 0, 1]`.

**Root cause.** The Postgres column `nf_fields.coeffs` is declared as
`numeric[]` (LMFDB stores the polredabs-canonical coefficient list as
arbitrary-precision numerics, even though the values are always
integers). psycopg2's default `adapt(list[int])` produces an
`integer[]` array literal at the wire level. Postgres does NOT
implicitly unify `integer[]` with `numeric[]` for the `=` operator —
unlike scalar `integer` vs. `numeric`, the array element types do
not coerce automatically. The result is a `DatatypeMismatch` error
inside the planner.

**Fix.** Cast the parameter to `numeric[]` in the SQL itself, so the
binding is unambiguous regardless of how psycopg2 adapts the
Python list:

```sql
SELECT "label", "coeffs", "degree", "disc_abs"
FROM "nf_fields"
WHERE "coeffs" = %s::numeric[]
LIMIT 5
```

The cast runs once on the bound parameter (cheap; constant-time per
query). No psycopg2 type-handler registration is required — the
SQL-level cast subsumes whatever array-literal psycopg2 emits.

**Regression test.**
`test_authority_lmfdb_cast_handles_array_binding` in
`prometheus_math/tests/test_catalog_consistency.py`. The test:

1. Calls `lmfdb.probe(timeout=5.0)`; skips cleanly if unreachable.
2. Exercises `lmfdb_check([1, 0, 1], 1.0)` (degree 2, Q(i)) and
   asserts `hit=True` with `match_label == "2.0.4.1"`.
3. Exercises `lmfdb_check([1, -1, 1, -1, 1], 1.0)` (degree 4,
   Q(zeta_5)) and asserts `hit=True` with `match_label == "4.0.125.1"`.

We test two degrees specifically because the original bug report
only covered degree 2; the cast must work uniformly across array
sizes.

**Lesson.** When binding Python lists to Postgres array columns,
**always check the element type of the column**. `integer[]` and
`numeric[]` are distinct types in Postgres, and the planner does
NOT coerce between them for array operators. The default
psycopg2 array adaptation infers from the Python list's element
type (`int -> integer`, `float -> double precision`, ...), which is
rarely what you want for a `numeric[]` column. Solutions in
preference order:

1. **Inline cast in SQL** (this fix): `%s::numeric[]`. Clearest,
   no global state.
2. **Per-call type adapter**: `psycopg2.extensions.AsIs` with a
   pre-formatted literal. More invasive.
3. **Module-wide register_adapter**: register a custom adapter for
   `list` to emit `numeric[]`. NEVER do this; it changes behavior
   globally and breaks every other call site.

The same pattern applies to `nf_fields.disc_abs` (declared
`numeric` not `bigint`) and `mf_newforms.atkin_lehner_eigenvals`
(declared `jsonb`). Cast at the call site.

---
