# Catalog Consistency Notes — `prometheus_math.catalog_consistency`

Multi-catalog cross-check, forged 2026-04-29 in execution of §6.3 of
`harmonia/memory/architecture/discovery_via_rediscovery.md`.

## What this module does

The discovery pipeline at `prometheus_math.discovery_pipeline` produces
candidate polynomials in the sub-Lehmer band (1.001 < M < 1.18) and
needs to flag any polynomial that's already known in the literature
before promoting it to `SHADOW_CATALOG`. Prior to §6.3, the only
catalog consulted was Mossinghoff's 178-entry snapshot. Production
discovery work requires more breadth: a polynomial known in
Boyd/Smyth/Borwein-Mossinghoff but not in the Mossinghoff archive
should still get caught.

`catalog_consistency.py` extends the gate to **five** catalog adapters,
each returning a typed `CatalogResult` and aggregated by
`run_consistency_check(coeffs, m_value)`.

## Catalogs implemented

| Catalog              | Backend                                              | Query kind         | Always live? | Expected hit rate (sub-Lehmer band) |
|----------------------|------------------------------------------------------|--------------------|--------------|-------------------------------------|
| `Mossinghoff`        | `prometheus_math.databases._mahler_data` snapshot    | M-value            | YES          | High (Mossinghoff is exhaustive for M < 1.30 at low degree) |
| `lehmer_literature`  | `prometheus_math._lehmer_literature_data` snapshot   | polynomial / M     | YES          | Medium (24 entries, breadth across 5 source papers) |
| `LMFDB`              | Postgres mirror at `devmirror.lmfdb.xyz`             | polynomial match   | NO (skip-clean) | Low for the discovery use case (LMFDB indexes number fields, not Mahler tables) |
| `OEIS`               | `prometheus_math.databases.oeis` (HTTPS API)         | coefficient seq    | NO (skip-clean) | Very low (OEIS rarely indexes the specific "Lehmer-witness" coefficient pattern) |
| `arXiv`              | `prometheus_math.databases.arxiv` (Cornell API)      | title fuzzy + abstract scan | NO (skip-clean) | Very low (heuristic; documented limitations below) |

### Per-catalog limitations

#### Mossinghoff
- **Coverage**: 178 entries spanning degrees 2..30 + 36, M in [1.0, 1.84].
- **Limitation**: a polynomial whose M agrees with a Mossinghoff entry
  to 1e-5 is flagged as a hit even if the *coefficient vectors* differ
  (e.g. cyclotomic-twins of Lehmer's polynomial all share M = 1.17628).
  This is the right behavior for a catalog-miss gate; downstream
  consumers that need polynomial-equality should call
  `mahler.lookup_polynomial(coeffs)` directly.

#### Lehmer literature
- **Coverage**: 24 hand-curated entries.
- **Source breakdown** (programmatic, from `LITERATURE_META`):
  - Boyd 1980 — 9 entries
  - Boyd 1989 — 5 entries
  - Boyd 1981 — 4 entries
  - Smyth 1971 — 2 entries
  - Mossinghoff 1998 — 2 entries (intentional overlap)
  - Lehmer 1933 — 1 entry (Lehmer's polynomial itself)
  - Borwein-Mossinghoff 2007 — 1 entry
- **Verification**: every M-value cross-checked against
  `techne.lib.mahler_measure.mahler_measure` to <1e-6 at table-build
  time (and the test suite re-runs the verification).
- **Limitation**: NOT exhaustive of any of these papers. The point of
  this catalog is *breadth across multiple authorities*, not depth
  within any one. If the discovery pipeline needs to detect "every
  polynomial in Boyd 1989 Table 1," that's a different catalog (Boyd
  1989 supplement S1-S5, ~200 entries, future work).

#### LMFDB
- **Backend**: Postgres mirror over `psycopg2`.
- **Live status today (2026-04-29)**: depends on local network; the
  adapter does a `probe()` first and skips with
  `error="lmfdb_unreachable"` if the mirror is down.
- **Query**: exact match on `nf_fields.coeffs` (LMFDB's polredabs'd
  defining-polynomial column). False-negative rate is non-trivial: our
  candidate polynomial may need polredabs canonicalization first.
- **Limitation**: LMFDB doesn't index Mahler measures directly. The
  hit rate on Mahler-band polynomials is consequently low; this
  adapter is mostly defensive — catching cases where the polynomial
  also happens to be a number-field defining polynomial.

#### OEIS
- **Backend**: `prometheus_math.databases.oeis.is_known(values)`,
  which uses OEIS's `/search` JSON endpoint.
- **Throttle**: 1 request/sec (built into the wrapper).
- **Live status**: depends on the local OEIS mirror at `_local.py`;
  if the mirror is present, calls resolve offline. Otherwise hits the
  network and may rate-limit.
- **Limitation**: OEIS doesn't index Mahler measures. The hit rate
  for "is this coefficient sequence a known OEIS entry" is non-zero
  but small for sub-Lehmer Salem polynomials (which tend to have
  long, mostly-zero coefficient lists that match generic
  "polynomial-coefficient" sequences only loosely).

#### arXiv
- **Heuristic**: search recent arXiv titles for "Mahler measure" or
  "Salem polynomial", then scan abstracts for any decimal token
  matching our M to 3 decimal places.
- **Live status**: depends on the third-party `arxiv` pip package and
  the Cornell API.
- **Limitation (significant)**: this is **not** a real catalog query.
  arXiv abstracts rarely quote M-values to high precision. The
  expected hit rate is very low. The structure is in place for a
  future §6.3-2 follow-up that uses full-text indexing
  (`arxiv_corpus.py`).

## Reachability status today (2026-04-29)

Verify with `python -c "from prometheus_math.databases import lmfdb,
oeis, arxiv; print('lmfdb:', lmfdb.probe()); print('oeis:',
oeis.probe()); print('arxiv:', arxiv.probe())"` on the deployed
machine.

The two **always-available** catalogs (`Mossinghoff` and
`lehmer_literature`) are the load-bearing pieces of this module: every
pipeline run hits both unconditionally. The three live-network
catalogs are best-effort additions; their absence does not break the
pipeline (the orchestrator treats `error=...` results as "skip with
warning, count as miss").

## The IMPORTANT honest framing

> **Catalog-miss in N consulted sources is NOT a positive verification
> of novelty.**

What the gate produces:

- `unanimous_miss = True` ⇨ none of the 5 catalogs flagged the
  polynomial. This is a **stronger** signal than "missing in
  Mossinghoff alone" — by a meaningful factor when literature and
  LMFDB are live — but **bounded above by the union of catalog
  coverage**. The catalogs we consult are themselves snapshots of
  human-curated tables; a polynomial absent from all of them is more
  likely (but not proven) to be unrecorded in the literature.

- `any_hit = True` ⇨ the polynomial is recorded somewhere; the
  pipeline routes it to `REJECTED` with `kill_pattern="known_in_catalog:..."`.
  This direction is sharp (false-positive rate is bounded by the
  catalogs' own labeling errors, which we trust).

What the gate does NOT prove:

- "The polynomial is genuinely new mathematics."
- "No human has computed this M-value before."
- "Lehmer's conjecture is settled in this case."

The discovery pipeline never claims novelty. It routes catalog-missing
survivors to `SHADOW_CATALOG`, which is precisely the substrate-grade
bucket for "passed all mechanical kill-paths but lacks independent
verification." The cold-fusion failure mode (treating absence-of-
evidence as evidence-of-absence) is mitigated, NOT eliminated, by
adding more catalogs.

## How to extend the registry

Add a new adapter with the signature:

```python
def my_catalog_check(
    coeffs: List[int], m_value: float, tol: float = 1e-5
) -> CatalogResult:
    ...
```

Then register it:

```python
from prometheus_math.catalog_consistency import DEFAULT_CATALOGS
DEFAULT_CATALOGS["MyCatalog"] = my_catalog_check
```

Adapter contract:

1. Validate inputs via `_validate_inputs(coeffs, m_value)` (raises
   ValueError on empty / negative / non-finite).
2. Wrap network calls in try/except; **never let an exception
   propagate**. Return `CatalogResult(hit=False, error="<typed>")`
   for failures.
3. Record `query_runtime_ms` so the substrate can budget catalog
   queries.

## Version

Forged 2026-04-29. Tracked in `techne/TDD_LOG.md`.
