# MIRROR LABEL AUDIT — lfunc_lfunctions is NOT label-unique (routed at ALL mirror consumers)

Aporia P74, 2026-08-21. Origin: the P73 pooled-0348 disjointness gate found 148 exact
duplicate rows in an 800-row fetch head. This audit measures the table-wide extent.

## Numbers (audited live, queries in WORKLOG P74)

- FULL TABLE: 24,351,376 rows, 19,653,467 distinct labels — **4,697,909 duplicate rows (19.3%)**.
- Per degree (rows / distinct / dup rows): every degree carries ~19% duplication —
  - degree 2: 16,265,797 / 13,145,542 / 3,120,255
  - degree 1: 7,712,393 / 6,221,141 / 1,491,252
  - degree 4: 235,130 / 188,759 / 46,371
  - degrees 6-32: same ratio, thousands each.
- Duplicate multiplicity in the inspected head: labels appear exactly TWICE (148 pairs
  in the sd degree-1 ASC-800 head; none higher observed there).

## Verdict on the pre-stated split (PURE-DUP vs CONFLICT)

Sampled census (TABLESAMPLE SYSTEM(0.05) → 12,081 labels re-fetched via the label
index): 4,426 duplicated, **0 with differing zero vectors → PURE-DUP** at sample scale.
Consistent with the P73 spot check (3/3 duplicate labels byte-identical). The
FULL-table conflict census is running under an extended timeout; its count will be
appended here when it lands. Until then the working verdict is PURE-DUP (ingestion
duplication), with the caveat that TABLESAMPLE is page-clustered, not uniform-random.

## What every consumer must do

1. **`DISTINCT ON (label)`** (or `GROUP BY label`) in EVERY fetch from
   `public.lfunc_lfunctions`. Nominal row counts overstate distinct L-functions by ~19%.
2. Any count/density statistic previously computed from this table without dedup is
   inflated in nominal n (not necessarily biased in value — duplicates observed so far
   are byte-identical; the 0348 dedup annex is the worked example: conclusion unchanged,
   slightly stronger).
3. If the full census ever finds a CONFLICT label (same label, different zeros), that is
   a data-integrity event, not a statistics footnote — instrument-first row comparison,
   then quarantine of the affected label range.

## Provenance

Duplication is mirror-side ingestion (row-level exact copies), not LMFDB semantics —
labels are unique upstream. A re-ingest or a `DELETE ... USING` dedup would fix the
table; until someone owns that, the DISTINCT ON doctrine stands.
