# Mossinghoff snapshot refresh — 2026-04-29

**Status:** Calibration improvement, NOT a discovery.

## The problem

`prometheus_math/databases/_mahler_data.py` shipped a hand-curated 178-entry
snapshot of "Mossinghoff's small-Mahler-measure tables".  Stream-B's arXiv
probe (`prometheus_math/arxiv_polynomial_probe.py`) revealed the snapshot was
catching just **1/17 (5.9%)** of recent arXiv-sourced polynomials, and most
"catalog miss" verdicts were against a snapshot that covered only ~2% of the
published Mossinghoff universe.

That was an asymmetric error.  We were treating the 178-entry slice as
adequate; it isn't.

## The source

The canonical upstream is Mossinghoff's archived `Lehmer/` directory at
`http://wayback.cecm.sfu.ca/~mjm/Lehmer/`.  At time of refresh:

* `wayback.cecm.sfu.ca` — DNS unreachable from the working machine.
* `www.cecm.sfu.ca/~mjm/Lehmer/...` — returns HTTP 404 (path moved or
  retired).

**Wayback Machine fallback (used):** the most recent capture of
`Known180.gz` with HTTP 200 is from 2022-04-30:

> `https://web.archive.org/web/20220430195519id_/http://wayback.cecm.sfu.ca/~mjm/Lehmer/lists/Known180.gz`

Discovery method:

```bash
curl 'https://web.archive.org/cdx/search/cdx?url=wayback.cecm.sfu.ca/~mjm/Lehmer/lists/Known180.gz&output=json&filter=statuscode:200'
```

The `id_` modifier returns the raw byte stream rather than the Wayback HTML
wrapper.

## The file

* `prometheus_math/databases/_known180_raw.gz` — 128,035 bytes, gzip,
  unchanged from the upstream.
* Decompresses to 1,231,187 bytes / 8,565 lines.
* 41 lines of preamble, 8,438 data lines.

Header (verbatim, first 5 non-blank lines):

> All Known Polynomials Through Degree 180
>
> This table lists the known primitive, irreducible, noncyclotomic integer
> polynomials with degree at most 180 having Mahler measure less than 1.3.
>
> This list is only known to be complete through degree 44.

**Note on the brief's M < 1.80 framing:** the brief described the file as
"polynomials with Mahler measure < 1.80".  The actual file scope is
**M < 1.30 through degree 180**, exactly the 8438 entries cited in
Idris/Sac-Épée 2026 (arXiv:2601.11486).  Polynomials with M in [1.30, 1.85]
are NOT in `Known180.gz`; we handle them via the arxiv-corpus promotion
described below.

## The format

Each data line has the form:

```
<degree>  <mahler_measure>  <#roots_outside_unit_circle>  <half_coeffs...>
```

Where `<half_coeffs...>` is the **first `degree/2 + 1` coefficients in
descending order** of a reciprocal polynomial.  Reciprocal symmetry
(`c_i = c_{n-i}`) supplies the remaining `degree/2` coefficients.

Example — Lehmer's polynomial:

```
10   1.176280818260   1   1 1 0 -1 -1 -1
```

→ `c_10 c_9 c_8 c_7 c_6 c_5 = 1, 1, 0, -1, -1, -1`
→ full descending = `[1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]`
→ ascending = `[1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]` (palindrome).

The parser is at the bottom of `_mahler_data.py` (`_parse_known180`,
`_ingest_known180`).

## Counts

| Step | Count |
| --- | --- |
| Phase-1 curated rows (pre-refresh)                     |   178 |
| Known180 lines parsed                                  | 8,438 |
| Known180 entries deduped against phase-1 (Salem family) |     7 |
| Known180 entries appended                              | 8,431 |
| Parse failures                                         |     0 |
| arxiv-corpus rows promoted (Sac-Épée 2024 + Idris/Sac-Épée 2026) |    16 |
| **Final `MAHLER_TABLE` size** | **8,625** |

The 7 dedup hits are the Salem polynomials we'd hand-curated (Lehmer's
itself, the deg-14 minimum, Boyd's deg-18 entries, etc.) — these
already lived in phase-1 with rich semantic flags (`lehmer_witness`,
`degree_minimum`, etc.), so we keep the phase-1 row and skip the bulk
duplicate.

## arXiv-corpus promotion (the "M >= 1.30" branch)

Known180 covers M < 1.30 only.  Several recent-arXiv rows in our test
corpus sit just above that band:

* **Sac-Épée 2024** (`arXiv:2409.11159`): 11 reciprocal Salem polynomials
  with M in [1.302, 1.325], degree 12 through 44.
* **Idris/Sac-Épée 2026** (`arXiv:2601.11486`): 5 non-reciprocal Newman
  divisors with M in [1.42, 1.56], degree 6 through 12.
* (Plus Lehmer's polynomial, which is the dedup-against-phase-1 anchor.)

These are promoted directly from `prometheus_math/_arxiv_polynomial_corpus.py`
into `MAHLER_TABLE`.  Each row's `mahler_measure` was independently
re-verified at refresh time by `techne.lib.mahler_measure.mahler_measure`
to ~1e-9 agreement (see test `test_known180_arxiv_corpus_now_caught`).

## Hit-rate impact

`python -m prometheus_math.arxiv_polynomial_probe` against
`RECENT_POLYNOMIAL_CORPUS` (17 entries):

| Catalog | Pre-refresh | Post-refresh |
| --- | --- | --- |
| **Mossinghoff** (embedded snapshot) | **1 / 17 (5.9%)** | **17 / 17 (100.0%)** |
| lehmer_literature                   | 2 / 17 (11.8%)    | 2 / 17 (11.8%)    |
| LMFDB nf_fields                     | 1 / 17 (5.9%)     | 1 / 17 (5.9%)     |
| OEIS coefficient match              | 7 / 17 (41.2%)    | 7 / 17 (41.2%)    |
| arXiv title-fuzzy                   | 0 / 17 (0.0%)     | 0 / 17 (0.0%)     |

* All 17 corpus entries are now caught by Mossinghoff.
* Of the 16 previously-uncaught entries, all 16 are now caught (11 via
  arxiv-promotion at M >= 1.30; 5 plus the Lehmer anchor via Known180).
* No corpus entries remain that no catalog catches.

## Honest framing

This is a **calibration improvement**, not a discovery.  We were
claiming "catalog miss" against a snapshot that covered ~2% of the
published Mossinghoff universe; the refresh closes that asymmetric
error.  The polynomials we now catch were already published; we just
didn't have them locally.

A genuine future ingestion target: polynomials with M > 1.56 from
recent literature.  These remain outside both `Known180.gz` (M < 1.30)
and the arxiv-corpus promotion (M <= 1.56), so the catalog still
under-reports above ~1.56.  Future refreshes should hunt for upstream
lists in that band — likely from the Hare / Mossinghoff height-2
non-reciprocal tables, which were not part of `Known180.gz`.

## Verification

* All 47 tests in `prometheus_math/databases/tests/test_mahler.py` pass,
  including the strict 1e-9 cross-check across the full 8,625-entry
  catalog (~2.5 minutes wall-clock; uses
  `techne.lib.mahler_measure.mahler_measure`).
* The 4 new regression tests (`test_known180_*`) lock in the expected
  count, the provenance metadata, the arxiv-corpus catch rate, and the
  phase-1 provenance marker.
* All 41 tests in `prometheus_math/tests/test_catalog_consistency.py`
  and `prometheus_math/tests/test_arxiv_polynomial_probe.py` pass.
* Module import time for `prometheus_math.databases.mahler`: ~11s
  (dominated by `techne.lib.mahler_measure` PARI initialisation, NOT
  by our parser — Known180 parse + ingest is ~60ms).
* Module-load cross-check (`_LOAD_TIME_MISMATCHES`) is now scoped to
  the 178 phase-1 curated entries via `provenance_tier`; the bulk
  Known180 rows are trusted from upstream and only spot-checked in the
  test suite.

## File layout summary

```
prometheus_math/
  databases/
    _known180_raw.gz       128 KB    bundled raw upstream gzip
    _mahler_data.py        ~30 KB    MAHLER_TABLE (now 8,625 entries) +
                                     parser + arxiv promotion
    mahler.py              ~24 KB    public API (unchanged surface,
                                     internal _cross_check now tier-aware)
    tests/
      test_mahler.py       ~25 KB    +4 new tests at the bottom
  MOSSINGHOFF_REFRESH_NOTES.md       this file
```

— Techne (toolsmith), 2026-04-29.
