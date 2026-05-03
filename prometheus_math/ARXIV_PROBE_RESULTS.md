# ARXIV_PROBE_RESULTS — Multi-Catalog Cross-Check Against Recent arXiv Polynomials

Honest writeup of the rediscovery benchmark built in
`prometheus_math/_arxiv_polynomial_corpus.py` and
`prometheus_math/arxiv_polynomial_probe.py`.  This experiment tests:
**if a polynomial appears in a recent (post-2018) arXiv paper but NOT
in our embedded Mossinghoff snapshot, do our other 4 catalogs catch
it?**

Run via:

    python -m prometheus_math.arxiv_polynomial_probe

Test parity:

    python -m pytest prometheus_math/tests/test_arxiv_polynomial_probe.py


## 1. Curated entries

**Count: 17 entries** drawn from two real, recent arXiv papers (with
verified IDs, abstracts, and PDF tables).  Every M-value was
independently recomputed via `mahler_measure(reversed(coeffs))` and
agrees with the paper-quoted value to better than 1e-6.

### Sources

| ID | Year | Title | Entries |
| --- | --- | --- | --- |
| `2409.11159` (Sac-Épée) | 2024 | Salem numbers less than 49/37 | 11 |
| `2601.11486` (Idris/Sac-Épée) | 2026 | Algorithmic aspects of Newman polynomials and their divisors | 6 |

### Year distribution

* 2024: 11 entries
* 2026: 6 entries (including the Lehmer anchor, reproduced explicitly
  in proof of Prop 2.1 of `2601.11486`).

### Sub-partitions

* `likely_outside_snapshot_entries()` returns **12 entries** the agent
  predicted are NOT in our embedded 178-entry Mossinghoff slice (and
  one further entry that the live LMFDB cross-check turned up,
  surprising us in the positive direction).
* All 17 entries have `paper_year >= 2019` (post-2018 by construction).


## 2. Per-entry catalog-hit pattern

Live probe results (LMFDB + OEIS + arXiv title-fuzzy reachable from
Skullport, 2026-04-29).

| Deg | M | Paper | Mossinghoff | lehmer_literature | LMFDB | OEIS | arXiv |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 12 | 1.302269 | 2409.11159 | miss | **HIT** Boyd-1989-deg12 | **HIT** 12.2.10129... | miss | miss |
| 16 | 1.308409 | 2409.11159 | miss | miss | miss | **HIT** A016373 | miss |
| 14 | 1.318198 | 2409.11159 | miss | miss | miss | miss | miss |
| 18 | 1.323198 | 2409.11159 | miss | miss | miss | miss | miss |
| 26 | 1.304698 | 2409.11159 | miss | miss | miss | miss | miss |
| 28 | 1.324231 | 2409.11159 | miss | miss | miss | miss | miss |
| 30 | 1.303385 | 2409.11159 | miss | miss | miss | miss | miss |
| 32 | 1.302721 | 2409.11159 | miss | miss | miss | miss | miss |
| 38 | 1.306474 | 2409.11159 | miss | miss | miss | miss | miss |
| 44 | 1.308071 | 2409.11159 | miss | miss | miss | miss | miss |
| 40 | 1.316069 | 2409.11159 | miss | miss | miss | miss | miss |
| 10 | 1.419405 | 2601.11486 | miss | miss | miss | **HIT** A327580 | miss |
| 9 | 1.436632 | 2601.11486 | miss | miss | miss | **HIT** A015794 | miss |
| 12 | 1.448290 | 2601.11486 | miss | miss | miss | **HIT** A281010 | miss |
| 8 | 1.489581 | 2601.11486 | miss | miss | miss | **HIT** A123706 | miss |
| 6 | 1.556014 | 2601.11486 | miss | miss | miss | **HIT** A074272 | miss |
| 10 | 1.176281 | 2601.11486 (Lehmer) | **HIT** | **HIT** Lehmer-1933 | miss | **HIT** A070178 | miss |


## 3. Aggregate hit rate per catalog

Live probe, N = 17 entries, single run:

| Catalog | Hits | Rate | Errors |
| --- | --- | --- | --- |
| Mossinghoff (embedded snapshot) | 1/17 | **5.9%** | 0 |
| lehmer_literature (embedded snapshot) | 2/17 | **11.8%** | 0 |
| LMFDB nf_fields (live) | 1/17 | **5.9%** | 0 |
| OEIS coefficient match (live) | 7/17 | **41.2%** | 0 |
| arXiv title-fuzzy (live) | 0/17 | **0.0%** | 0 |

OEIS dominates by a factor of ~7x over any other catalog.

The arXiv title-fuzzy adapter went 0/17 — confirming the
documented limitation in `catalog_consistency.py`: arXiv abstracts
rarely quote M-values to high enough precision for a numerical
abstract scan to land within tolerance.  This catalog is structurally
the wrong tool for this job; the right tool is paper-body extraction
of polynomial tables, which is the §6.3-2 follow-up.


## 4. The interesting cell — entries with ZERO catalog hits

**9 of 17 entries** (53%) were caught by NO catalog.  All 9 are from
the Sac-Épée 2024 Salem table (`2409.11159`):

| Deg | M | Status per Sac-Épée |
| --- | --- | --- |
| 14 | 1.318198 | pre-2024 known (Mossinghoff online list) |
| 18 | 1.323198 | pre-2024 known (Mossinghoff online list) |
| 26 | 1.304698 | **NEW** per author |
| 28 | 1.324231 | **NEW** per author |
| 30 | 1.303385 | **NEW** per author |
| 32 | 1.302721 | **NEW** per author |
| 38 | 1.306474 | **NEW** per author |
| 44 | 1.308071 | **NEW** per author |
| 40 | 1.316069 | **NEW** per author |

These are real Salem polynomials — already verified by the LP method
of `2409.11159` to be Salem of the stated degree with the stated M
— and our 5-catalog union doesn't see them.  The 7 marked **NEW**
are particularly interesting: they're claimed-new in 2024, and our
union still misses them as of 2026-04-29.

This is the genuinely-uncaught real-world signal the experiment was
designed to surface.


## 5. The reverse — entries with MULTIPLE catalog hits

**2 entries** had ≥2 catalogs agree:

| Deg | M | Catalogs that agreed |
| --- | --- | --- |
| 12 | 1.302269 (Sac-Épée 2024 deg-12) | lehmer_literature + LMFDB |
| 10 | 1.176281 (Lehmer's polynomial, anchor) | Mossinghoff + lehmer_literature + OEIS |

The Lehmer anchor (3-catalog agreement) is the strongest "known"
signal in the corpus and behaves like a calibration anchor.  The
Sac-Épée degree-12 entry's surprise: LMFDB's `nf_fields` table
contains a number field with this exact integer coefficient list
(label `12.2.1012933461...`).  This is a positive surprise — the LMFDB
adapter validated a polynomial we had predicted it wouldn't see, by
exact polynomial-coefficient match rather than M-value match.


## 6. Surprises (predicted vs actual)

| Catalog | Surprise count |
| --- | --- |
| LMFDB | 1 (deg-12 entry; `false_positive` — predicted miss, actual hit) |

The original prediction set had 2 calibration mistakes:

* **Original prediction**: Sac-Épée deg-12 IS in our Mossinghoff
  snapshot (because its M < 1.30).
* **Actual**: NOT in our snapshot — our 178-entry slice is narrower
  than Mossinghoff's online list of 8438.  The corpus prediction was
  corrected to `Mossinghoff: False`, with a comment explaining the
  finding.

* **Original prediction**: LMFDB miss for the deg-12 entry.
* **Actual**: LMFDB hit, by exact polynomial-coefficient match.

Both calibration mistakes are themselves substantive findings — they
confirm that the Mossinghoff snapshot is narrower than its online
namesake, and that LMFDB has wider polynomial coverage than the
"polredabs flip" disclaimer in `catalog_consistency.py` admitted.


## 7. Qualitative observation

**Are our catalogs covering the recent arxiv space?**  Mostly **no**,
with a sharp sub-divide:

* For small-M (<1.42) Salem polynomials of high degree (>=14), our
  catalog union is **structurally too narrow**: 9 of 11 entries from
  `2409.11159` (the dedicated Salem-list paper) are uncaught.
* For non-reciprocal Newman-divisor polynomials (M in [1.42, 1.56])
  from `2601.11486`, **OEIS is doing all the work** — it caught
  5 of 5 such entries via coefficient-sequence match, while every
  other catalog missed.
* The Lehmer anchor is correctly identified by 3 of 5 catalogs, which
  is the calibration anchor showing the cross-check apparatus
  itself works.

**Where the catalog union needs to grow:**

* The Mossinghoff embedded snapshot needs an update; refreshing from
  the `Known180.txt` file referenced in `2601.11486` (the 8438-entry
  list) would close most of the high-degree-Salem gap.
* Even with a refresh, the 7 "NEW" entries from `2409.11159`
  (degrees 26-44) would remain uncovered until they're ingested
  upstream.  They are the genuine new-knowledge cases.
* OEIS over-performs as a coefficient-sequence index for these
  polynomials; this is a useful routing hint for the discovery
  pipeline (route coefficient lookups through OEIS first).
* The arXiv title-fuzzy adapter is structurally inadequate for this
  task; the §6.3-2 follow-up (paper-body extraction of polynomial
  tables) is the right next step.

**Honest framing.**  This is a small-N benchmark (17 entries).  Hit
rates have wide error bars; do not over-interpret the absolute
percentages.  The interesting-cell counts (9 zero-hits, 2 multi-hits,
1 surprise) are the substantive output, not the per-catalog
percentages.
