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

---

## FINAL ADJUDICATION (P103, census complete after ~50,448s of streaming)

**Verdict: PURE-DUP — CONFIRMED, with a scope limit and a corrected headline.**

### The conflict census, complete

Streamed **9,302,241 rows** across **4,650,771 duplicated labels**; **CONFLICT
labels: 0**. Not one duplicated label anywhere in the table carries differing
zero vectors. The pre-stated PURE-DUP branch fires: the duplication is
ingestion-level row copying, not a data conflict. Multiplicity distribution:

- 2 copies: 4,650,414 labels
- 3 copies: 15 labels
- 4 copies: 342 labels

(Check: 4,650,414·2 + 15·3 + 342·4 = 9,302,241 = rows streamed, exact.) The
4-copy class being ~23× larger than the 3-copy class points at a doubled
double-ingest rather than random repetition — an ops signature, recorded.

### Correction to this note's own headline (P74)

The original "4,697,909 duplicate rows (19.3%)" **conflated two different
things**, caught by chasing a one-label discrepancy between the census phases:

- **46,439 rows carry NULL labels.** `GROUP BY label` collapses all NULLs into
  a single group (hence phase 1 counting one extra "duplicated label"), while
  the census's `JOIN t.label = d.label` cannot match NULL to NULL — so those
  rows were **excluded from the conflict scan and remain unexamined**.
- **True redundancy among labeled rows: 4,651,470 excess rows = 19.14%** of
  the 24,304,937 labeled rows. Verified two independent ways: (labeled −
  distinct labels) and (streamed rows − duplicated labels) agree exactly.
- 4,651,470 + 46,439 = 4,697,909, which is where the original figure came
  from. The corrected split is redundancy 4,651,470 / unlabeled 46,439.

### NEW HAZARD in this note's own doctrine

`DISTINCT ON (label)` — published here as standing doctrine — has a trap for
the NULL-label rows: SQL treats all NULLs as **one** group, so a
`DISTINCT ON (label)` fetch returns **exactly one** of the 46,439 unlabeled
rows and silently discards the rest. The doctrine is amended:

> Use `DISTINCT ON (label)` for label-identified work, and **add
> `WHERE label IS NOT NULL`** so the exclusion is explicit. If unlabeled rows
> are in scope, dedupe them by a different key (id, or the zero-vector hash)
> — they cannot be label-deduplicated at all.

### Scope of the PURE-DUP verdict

Confirmed over every labeled duplicate row in the table (9,302,241 of them).
NOT established for the 46,439 NULL-label rows, which no label-keyed census
can reach; a hash-keyed census would close that and is filed as residue.

---

## THE UNLABELED POPULATION (P104) — they are real objects, not copies

The 46,439 NULL-label rows are the one population no label-keyed scan can
reach. Censused by CONTENT instead (md5 of `positive_zeros`, with per-group
raw-text verification against md5 collision). Pre-stated branches were
committed in-script before the run.

**Verdict: UNLABELED-DISTINCT.** These rows are **not** ingestion copies.

- **45,092 distinct zero-vector contents across 46,439 rows — 97.1% unique.**
  43,745 contents appear once; 1,347 appear exactly twice
  (43,745 + 2·1,347 = 46,439, exact).
- **Zero raw-text conflicts** across all 1,347 multi-row groups: every group's
  rows carry byte-identical text, so the doubles are genuine duplicate
  objects, not hash collisions.
- **Internal redundancy 2.90%** (1,347 excess rows) — an entirely different
  regime from the labeled population's **19.14%**. Whatever produced the
  labeled duplication did not produce these.
- Every one of the 46,439 rows HAS zero data (`positive_zeros IS NULL`: 0),
  so they are not empty placeholders.
- Degree spread: degree 2 dominates at 26,104 (56.2%), then degree 4 (1,273),
  followed by a long HIGH-degree tail (48, 96, 104, 112, 120, 128 …). That
  profile is consistent with objects whose labeling conventions are unsettled
  or that were computed outside the labeling scheme — not with junk.

### DOCTRINE, amended a second time

P103 amended the `DISTINCT ON (label)` advice to add `WHERE label IS NOT NULL`
so the exclusion is explicit. That remains correct about the collapse hazard,
but this census establishes its cost: **the filter discards 46,439 real,
mostly-unique L-function records.** Final form of the advice:

> For label-identified work: `DISTINCT ON (label) … WHERE label IS NOT NULL`.
> For work requiring COMPLETENESS: that filter is lossy. Take an id-keyed
> path, or dedupe by content hash (`md5(positive_zeros::text)`), which is
> the only key that works across both populations. Counts quoted from this
> table should state which population they cover — the two have different
> duplication regimes (19.14% vs 2.90%) and cannot be pooled naively.

### Residue closed

The audit can now speak for the whole table: labeled rows (PURE-DUP,
9,302,241 rows, 0 conflicts) and unlabeled rows (DISTINCT, 46,439 rows,
0 conflicts). No population remains unexamined.
