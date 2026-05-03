# Catalog Consistency — Usage Guide

Teammate-facing guide for `prometheus_math.catalog_consistency`. Any
agent (Aporia, Charon, Ergon, Harmonia, Mnemosyne, ...) can use this
tool to ask "is this polynomial recorded in any of our consulted
catalogs?".

Last updated: 2026-04-29 · Tool forged 2026-04-29 (commit `1666c4a4`)
· Source: `prometheus_math/catalog_consistency.py`

---

## What the tool is and isn't

**One-line summary.** `run_consistency_check(coeffs, mahler_measure)`
runs an integer polynomial through five catalog adapters in parallel
(Mossinghoff snapshot, Lehmer-literature snapshot, LMFDB nf_fields,
OEIS sequence search, arXiv title fuzzy) and aggregates hits / misses
into a single typed dict.

**Built by**: Techne, in execution of §6.3 of
`harmonia/memory/architecture/discovery_via_rediscovery.md`.

**In scope.**
- Determine whether a polynomial appears in any of the consulted
  catalogs.
- Return a typed `CatalogResult` per catalog, with hit/miss/error and
  query latency.
- Skip cleanly when external catalogs are unreachable; never raise
  from an adapter into the caller.

**NOT in scope.**
- *Novelty verification.* Catalog-miss in N consulted catalogs is a
  **stronger** signal than catalog-miss in 1, but it is **bounded
  above** by the union of those catalogs' coverage. `unanimous_miss
  = True` is not proof that the polynomial is genuinely new
  mathematics — see "Honest framing" below.
- *Polynomial-equality checks.* The Mossinghoff adapter matches by
  M-value within `tol`, not by coefficient vector. For
  coefficient-equality consult `mahler.lookup_polynomial(coeffs)`
  directly.
- *Polredabs canonicalization.* The LMFDB adapter expects
  polredabs-canonical coefficient vectors; we do not run polredabs
  ourselves (heavyweight). False-negative rate is non-trivial.

### Sharp boundary: catalog-miss vs. novelty

> A polynomial absent from N consulted snapshots is more likely
> unrecorded in the literature than a polynomial absent from one,
> but the negative-evidence shape doesn't change.

Use `unanimous_miss` as a **filter** that flags candidates worth
deeper investigation. Do not use it as a **claim** that the
polynomial is new. The discovery pipeline routes catalog-missing
survivors to `SHADOW_CATALOG`, which is precisely the bucket for
"passed the mechanical kill-paths but lacks independent verification."

---

## Quick-start (the 80% use case)

```python
from prometheus_math.catalog_consistency import run_consistency_check

# Lehmer's polynomial (1933).
coeffs = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
mahler_measure = 1.17628081826

result = run_consistency_check(coeffs, mahler_measure)
if result["unanimous_miss"]:
    print("polynomial absent from all consulted catalogs")
else:
    for hit in result["hits"]:
        print(f"  {hit.catalog_name}: {hit.match_label}")
```

Expected output for Lehmer's polynomial (live, all catalogs reachable):

```
  Mossinghoff: Lehmer x Phi_19
  lehmer_literature: Lehmer-1933
  OEIS: A070178
```

(LMFDB and arXiv miss; LMFDB because Lehmer's polynomial is not a
number-field defining polynomial in their `nf_fields` table, arXiv
because the heuristic abstract scan rarely lands.)

---

## API reference

### `run_consistency_check(coeffs, mahler_measure, catalogs=None, tol=1e-5) -> dict`

Run the polynomial through every adapter in `catalogs` (or
`DEFAULT_CATALOGS` if `None`) and aggregate.

**Parameters**

| name | type | default | meaning |
|---|---|---|---|
| `coeffs` | `list[int]` | (required) | Ascending integer coefficient list, e.g. `[c0, c1, c2, ...]` for `c0 + c1*x + c2*x^2 + ...`. |
| `mahler_measure` | `float` | (required) | Mahler measure (must be `>= 0` and finite). |
| `catalogs` | `dict[str, adapter] | None` | `None` (= `DEFAULT_CATALOGS`) | Adapter registry. Pass a subset to restrict; `{}` for the vacuous case. |
| `tol` | `float` | `1e-5` | Tolerance passed to each adapter (M-match within `tol`). |

**Returns** — `dict` with keys:

| key | type | meaning |
|---|---|---|
| `by_catalog` | `dict[str, CatalogResult]` | Per-catalog typed result. |
| `any_hit` | `bool` | True iff any catalog flagged a hit. |
| `hits` | `list[CatalogResult]` | The hits, ordered by registry. |
| `unanimous_miss` | `bool` | True iff every catalog missed (errors and skips count as miss for this aggregate). |
| `errors` | `list[CatalogResult]` | Adapter results with non-None `error` field. |
| `catalogs_checked` | `list[str]` | Catalog names actually consulted. |
| `warning` | `Optional[str]` | Set when `catalogs={}` (vacuous miss). |

**Raises** — `ValueError` on empty `coeffs`, negative or non-finite
`mahler_measure` (BEFORE any adapter is called).

### `CatalogResult` dataclass

Frozen dataclass returned by every adapter.

| field | type | when set | when `None` |
|---|---|---|---|
| `catalog_name` | `str` | always | never |
| `query_kind` | `str` | always (one of `"M_value"`, `"coeff_sequence"`, `"title_fuzzy"`, `"polynomial_match"`, `"?"`) | never |
| `hit` | `bool` | always | never |
| `match_label` | `Optional[str]` | on hit (e.g. LMFDB label, OEIS A-number, literature label) | on miss or error |
| `match_distance` | `Optional[float]` | on hit (`|stored - observed|` for M-match, `0.0` for exact-coeff) | on miss or error |
| `query_runtime_ms` | `float` | always (>= 0) | never |
| `error` | `Optional[str]` | on adapter failure (typed string, never an exception object) | on success |

Inspecting a hit:

```python
result = run_consistency_check(coeffs, m)
if result["any_hit"]:
    h = result["hits"][0]
    print(h.catalog_name, h.match_label, h.match_distance)
```

### Individual adapter functions

If you want to consult just one catalog (e.g. fast offline check, or
testing a specific adapter in isolation), call it directly:

```python
from prometheus_math.catalog_consistency import (
    mossinghoff_check,
    lehmer_literature_check,
    lmfdb_check,
    oeis_check,
    arxiv_title_fuzzy_check,
)

r = mossinghoff_check([1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1], 1.17628)
# CatalogResult(catalog_name='Mossinghoff', hit=True, match_label='Lehmer x Phi_19', ...)
```

Each adapter has the signature `(coeffs, m_value, tol=1e-5) ->
CatalogResult`. The arXiv adapter additionally accepts `m_tol` /
`max_results` kwargs (a thin wrapper aliases `tol -> m_tol` for
registry consistency).

---

## Adapter-by-adapter cheat sheet

| adapter | backend | query_kind | always live? | typical latency | hit rate (sub-Lehmer band) | known limits |
|---|---|---|---|---|---|---|
| `mossinghoff_check` | embedded snapshot (`databases._mahler_data.MAHLER_TABLE`) | `M_value` | YES | < 1 ms | high (Mossinghoff is exhaustive for M < 1.30 at low degree) | matches by M only, not coefficients |
| `lehmer_literature_check` | embedded snapshot (`_lehmer_literature_data.LEHMER_LITERATURE_TABLE`) | `polynomial_match` then `M_value` | YES | < 1 ms | medium (24 hand-curated entries from Boyd / Smyth / Borwein-Mossinghoff / Lehmer / Mossinghoff) | not exhaustive of any single source paper |
| `lmfdb_check` | Postgres mirror at `devmirror.lmfdb.xyz` | `polynomial_match` (exact `nf_fields.coeffs`) | NO (skip-clean) | 100–800 ms typical | low for the discovery use case | requires polredabs-canonical coeffs; LMFDB doesn't index Mahler measures |
| `oeis_check` | OEIS HTTPS API via `databases.oeis.is_known` | `coeff_sequence` | NO (skip-clean) | 1 s typical (rate-limited) | low–medium | skips trivially for sequences with < 3 nonzero entries |
| `arxiv_title_fuzzy_check` | arXiv API via `databases.arxiv` | `title_fuzzy` | NO (skip-clean) | ~3 s (rate-limit compliant) | very low (heuristic) | abstract-text scan; rarely lands |

**When to call standalone.**
- Fast offline check (no network, no Postgres dependency): use
  `mossinghoff_check + lehmer_literature_check` — two embedded
  snapshots, sub-millisecond total.
- LMFDB-only verification (e.g. "is this polynomial a known number
  field?"): call `lmfdb_check` directly; the adapter handles probe
  + skip-clean for you.
- OEIS coefficient-sequence lookup unrelated to Mahler measures:
  `oeis_check` is the cleanest path; it short-circuits on trivial
  sequences.

**An offline-only registry** for tests / no-network runs:

```python
from prometheus_math.catalog_consistency import (
    run_consistency_check,
    mossinghoff_check,
    lehmer_literature_check,
)

OFFLINE = {
    "Mossinghoff": mossinghoff_check,
    "lehmer_literature": lehmer_literature_check,
}
result = run_consistency_check(coeffs, m, catalogs=OFFLINE)
```

---

## Common failure modes

| symptom | cause | what the adapter returns | what you should do |
|---|---|---|---|
| LMFDB `error="lmfdb_unreachable"` | Postgres mirror down or network blocked | `CatalogResult(hit=False, error=...)` | Check `result["errors"]`; treat as skip-with-warning, not as a miss. |
| LMFDB `error="query_failed: DatatypeMismatch: ..."` | (Should not occur post-fix; see Bugs Fixed below.) | `CatalogResult(hit=False, error=...)` | If you see this, regression alert — call out a bug, the cast is broken. |
| OEIS `error="oeis_unreachable: ..."` | Network down, OEIS API timeout, rate-limit | `CatalogResult(hit=False, error=...)` | Caller backoff; OEIS rate-limits at 1 req/sec by convention. |
| OEIS `error="trivial_sequence:not_searchable"` | Coefficient list has < 3 nonzero entries | `CatalogResult(hit=False, error=...)` | Expected behavior — OEIS won't match generic short sequences; skip silently. |
| arXiv `error="arxiv_unreachable"` | Network down or Cornell API throttling | `CatalogResult(hit=False, error=...)` | Backoff + retry later. The third-party `arxiv` client adds ~3s latency by design. |
| `ValueError("coeffs must be a non-empty list of integers")` | Empty `coeffs` passed to `run_consistency_check` | (raises before any adapter called) | Validate input. |
| `ValueError("m_value must be finite, got nan")` | NaN/inf Mahler measure | (raises before any adapter called) | Filter your candidate stream for finite M. |

The orchestrator NEVER propagates an exception from an adapter. If an
adapter raises (it shouldn't, by contract), the orchestrator wraps it
into `CatalogResult(error="adapter_raised: ...")` automatically.

---

## Bugs found and fixed (for transparency)

### LMFDB nf_fields.coeffs cast bug (fixed 2026-04-29)

- **Symptom**: queries against `nf_fields` with array-of-int parameters
  raised `psycopg2.errors.DatatypeMismatch` with message
  `operator does not exist: numeric[] = integer[]`.
- **Root cause**: the Postgres column `nf_fields.coeffs` is declared
  `numeric[]`. psycopg2's default array adaptation produces
  `integer[]` for a Python `list[int]`, which Postgres won't equate
  to `numeric[]` without an explicit cast.
- **Fix**: cast the parameter to `numeric[]` in the SQL:
  `WHERE coeffs = %s::numeric[]`. See `lmfdb_check` body in
  `prometheus_math/catalog_consistency.py`.
- **Regression test**:
  `test_authority_lmfdb_cast_handles_array_binding` in
  `prometheus_math/tests/test_catalog_consistency.py`. Exercises the
  live adapter at degree 2 (Q(i), label `2.0.4.1`) AND degree 4
  (Q(zeta_5), label `4.0.125.1`) to validate cast behavior across
  array sizes. Skips cleanly if LMFDB is unreachable.
- **Lesson**: when binding Python lists to Postgres array columns,
  always check the element type of the column. The default
  `psycopg2.extensions.adapt(list)` infers from the Python list's
  element type, which is rarely what you want for `numeric[]` columns
  — you must cast explicitly.

Full ledger: `prometheus_math/BUGS_FIXED.md`.

---

## When to use the catalog tool vs. the full DiscoveryPipeline

| your need | use this |
|---|---|
| "Is this polynomial in any catalog?" | `run_consistency_check(coeffs, m)` |
| "Run a polynomial through every kill-path (catalog + reciprocity + irreducibility + F1+F6+F9+F11)?" | `DiscoveryPipeline.process_candidate(coeffs, m)` |
| "Build a new discovery environment / RL training loop that needs the gate?" | use the pipeline; the catalog check is one stage of it. |
| "Single-catalog targeted query without orchestration overhead?" | call the individual adapter (e.g. `lmfdb_check`). |

The pipeline is the production caller. Most agents who need novelty
filtering should use `DiscoveryPipeline.process_candidate` and read
the returned `record.kill_pattern`. The catalog tool is a building
block — useful for ad-hoc lookups, bespoke filters, and tests.

---

## Adding a new catalog adapter

Conform to the contract:

```python
def my_catalog_check(
    coeffs: list[int],
    m_value: float,
    tol: float = 1e-5,
) -> CatalogResult:
    """Match docstring shape — see existing adapters for pattern."""
    _validate_inputs(coeffs, m_value)   # raises ValueError on bad input
    t0 = time.monotonic()
    try:
        # ... your catalog query ...
        # On hit: return CatalogResult(hit=True, match_label=..., ...)
        # On miss: return CatalogResult(hit=False, ...)
        # On network/parse failure: return
        #   CatalogResult(hit=False, error=f"my_catalog_unreachable: ...")
        ...
    except SomeNetworkError as e:
        return CatalogResult(
            catalog_name="MyCatalog",
            query_kind="...",
            hit=False,
            error=f"my_catalog_unreachable: {type(e).__name__}: {e}",
            query_runtime_ms=(time.monotonic() - t0) * 1000.0,
        )
```

Register the adapter:

```python
from prometheus_math.catalog_consistency import DEFAULT_CATALOGS
DEFAULT_CATALOGS["MyCatalog"] = my_catalog_check
```

Add tests in `prometheus_math/tests/test_catalog_consistency.py`
covering authority (a known hit), property (the result has the
expected fields), edge (empty coeffs raises, unreachable -> skip
clean), and composition (orchestrator picks up the new adapter).

Document in this file's adapter cheat sheet:
- Backend (embedded vs. live).
- `query_kind` value.
- Expected hit rate on the discovery use case.
- Latency budget (so substrate callers can plan).
- Skip-clean behavior on network failure.

**Adapter contract recap.**

1. Validate inputs via `_validate_inputs(coeffs, m_value)`.
2. Wrap network/IO calls in `try/except`; **never let an exception
   propagate**. Return `CatalogResult(hit=False, error=<typed>)` on
   any failure.
3. Always record `query_runtime_ms` (use `time.monotonic()`).
4. Set `match_label` and `match_distance` on hit; leave them `None` on
   miss or error.

---

## Worked example: Lehmer's polynomial through all 5 catalogs

Live run, 2026-04-29 from a machine with full network access:

```python
from prometheus_math.catalog_consistency import run_consistency_check

coeffs = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
m = 1.17628081826
result = run_consistency_check(coeffs, m)

print("any_hit:", result["any_hit"])
print("unanimous_miss:", result["unanimous_miss"])
print("catalogs_checked:", result["catalogs_checked"])
for name, r in result["by_catalog"].items():
    print(f"  {name:18s} hit={r.hit}  label={r.match_label}  err={r.error}")
```

Output:

```
any_hit: True
unanimous_miss: False
catalogs_checked: ['Mossinghoff', 'lehmer_literature', 'LMFDB', 'OEIS', 'arXiv']
  Mossinghoff        hit=True   label=Lehmer x Phi_19   err=None
  lehmer_literature  hit=True   label=Lehmer-1933       err=None
  LMFDB              hit=False  label=None              err=None
  OEIS               hit=True   label=A070178           err=None
  arXiv              hit=False  label=None              err=None
```

Reading the result:
- **3 hits** (Mossinghoff, lehmer_literature, OEIS).
  Lehmer's polynomial is densely catalogued — three independent
  authorities flag it.
- **2 misses, no errors**. LMFDB misses because Lehmer's polynomial
  is not in its `nf_fields` table (LMFDB indexes number-field
  defining polynomials, and Lehmer's degree-10 polynomial is not the
  defining polynomial of any LMFDB-tabulated number field). arXiv
  misses because the abstract-scan heuristic rarely lands.
- **`unanimous_miss = False`**, so a `DiscoveryPipeline` would route
  this candidate to `REJECTED` with
  `kill_pattern="known_in_catalog:Mossinghoff:Lehmer x Phi_19"` (or
  similar — the first hit in registry order wins the kill-pattern
  string).

---

## Pointer to deeper notes

- Honest framing of catalog-miss vs. novelty:
  `prometheus_math/CATALOG_CONSISTENCY_NOTES.md`.
- Pipeline integration:
  `prometheus_math/discovery_pipeline.py` — see `process_candidate`
  and the `_check_catalog_miss` helper.
- Bug ledger: `prometheus_math/BUGS_FIXED.md`.
- §6.3 specification:
  `harmonia/memory/architecture/discovery_via_rediscovery.md`.
