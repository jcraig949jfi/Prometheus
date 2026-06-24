# Charon DuckDB → Postgres repoint (code side) — 2026-06-24

**Author:** Charon (Claude Opus 4.8) · **Pairs with:** Ergon's data-side migration
(`roles/Ergon/DUCKDB_RETIREMENT_AUDIT_2026-06-24.md`).
**Scope:** the 28 files in Charon's source tree that called `duckdb.connect(charon.duckdb)`.
**No-delete doctrine honored:** `charon/data/charon.duckdb` (1.18 GB, frozen 2026-04-03)
is untouched — it served as the validation oracle this session and remains the fallback.

---

## What changed

**New shared layer — `charon/src/db.py`.** A thin DuckDB-compatible facade over
psycopg2. `connect(path=None, read_only=True)` accepts (and ignores) the legacy DuckDB
path, connects to local `prometheus_fire`, and sets `search_path = charon_duckdb, public`
so unqualified table names (`FROM objects`) resolve to the migrated archive. It exposes
DuckDB's `con.execute(sql, params).fetchall()/.fetchone()` API (the only fetch methods
the tree uses), translates `?`→`%s` (escaping literal `%`) when params are supplied, and
supports context-manager use. Reads go through the read-only role `lmfdb` (the same
non-secret cred already in `thesauros/prometheus_data/config.py`); the sensitive
`postgres/prometheus` write cred is never used or hardcoded here. Target is overridable
via `CHARON_PG_*` env vars.

**Design note (why a direct localhost connect, not `get_fire()`):** the prometheus_data
config default still points `fire` at the remote `devmirror.lmfdb.xyz` mirror, while the
migrated data is local. Charon's archive access is read-only, so `db.py` connects
directly to `localhost` with the least-privilege `lmfdb` role rather than routing reads
through the read-write `get_fire()` pool aimed at the stale remote default.

### Repointed — 18 read-path files (one-line import swap)
`import duckdb` → `from charon.src import db as duckdb`. Every existing
`duckdb.connect(str(DB_PATH), read_only=True)` call site works unchanged (the shim is
aliased as `duckdb`).

- `charon/src/`: research_battery, three_investigations, bsd_zero_experiments,
  root_number_test, conductor_scaling, extract_strata, extended_ablation,
  characterize_type_b, kill_tests_163, inner_twist_analysis, inner_twist_query
- `charon/v2/`: oscillation_shadow
- `charon/scripts/`: full_audit
- `charon/tests/`: zero_battery, test_21_embedding_baseline,
  test_13_conductor_conditioning, test_11_separability, test_03_trivial_dominance

### Retired — 6 frozen writers (deprecated, execution blocked)
These opened DuckDB writable (ingestion / schema DDL with `DOUBLE[]`). Per the task,
DuckDB ingestion is frozen — NOT repointed to write into Postgres. `import duckdb` is
replaced with a guard (`_RetiredDuckDB`) that raises a clear RuntimeError on any
`.connect()`, preventing accidental writes to the frozen oracle. Module imports still
succeed.

- `ingest.py`, `ingest_zeros.py`, `ingest_extended_zeros.py`,
  `ingest_dirichlet_zeros.py`, `ingest_dirichlet_fast.py`, `schema.py`

### Flagged for owner sign-off — 4 builders (write; data already migrated)
These build/write tables that are **already migrated verbatim** to `charon_duckdb`
(graph_edges 396,150; disagreement_atlas 119,397; objects.coordinates; genus2). I did
**not** repoint their writes (would silently write to Postgres) nor leave them writing to
the frozen DuckDB — same `_RetiredDuckDB` guard, so any run raises with a pointer to
rewrite writes against canonical Postgres tables with owner sign-off.

- `build_graph.py` (CREATE/DELETE/INSERT graph_edges)
- `disagreement_atlas.py` (DROP/CREATE/INSERT disagreement_atlas)
- `embed.py` (DELETE/INSERT spectral coordinates)
- `genus2_crossing.py` (mixed: a read path + an INSERT write path)

**Owner decision needed:** if any of these four must run again, rewrite their writes
against the canonical Postgres tables (e.g. `xref`/`zeros`/`analysis` schemas, not the
`charon_duckdb` archive) — flag raised, not guessed.

## SQL dialect work
Minimal. The survey found the read path uses only standard SQL with unqualified table
names — **no `main.` prefixes** (so `search_path` alone resolves them), **no
QUALIFY/SAMPLE/LIST/list_*/read_csv**, and every `[a:b]` was Python slicing, not SQL
array slicing. The only DuckDB-specific construct (`DOUBLE[]` column DDL) lived solely in
the retired writers, which are not routed through the shim. The one translation in the
shim (`?`→`%s`) covers the parameterized read queries. `double precision[]` arrays return
as Python lists, identical to DuckDB.

## object_id note (task step 3)
The read entry points (`zero_battery`, `research_battery`) join
`objects.id = object_zeros.object_id` **within the `charon_duckdb` archive**, which was
migrated verbatim and is internally consistent. The re-key warning (object_id now 1:1
with lmfdb_label in the *live* `zeros.*` tables) applies only to archive↔live joins;
nothing here crosses that boundary, so no label-rekeying was needed.

## DBA side-effect
The `lmfdb` read role lacked privileges on the new schema; granted (one-time, idempotent):
`GRANT USAGE ON SCHEMA charon_duckdb TO lmfdb; GRANT SELECT ON ALL TABLES IN SCHEMA
charon_duckdb TO lmfdb; ALTER DEFAULT PRIVILEGES IN SCHEMA charon_duckdb GRANT SELECT ...`.
Also: `psycopg2-binary` installed into the base Python (it lacked both psycopg2 and the
code's runtime driver).

## VALIDATION — Postgres vs the DuckDB oracle (exact match)

Row counts, all 14 tables via shim vs `charon.duckdb`:

```
objects            134475 == 134475     known_bridges       17314 == 17314
dirichlet_zeros    184830 == 184830     graph_edges        396150 == 396150
object_zeros       120649 == 120649     disagreement_atlas 119397 == 119397
landscape          119464 == 119464     object_zeros_ext    17313 == 17313
modular_forms      102150 == 102150     elliptic_curves     31073 == 31073
```
- `objects` GROUP BY object_type: identical.
- **Array fidelity** (`object_zeros.zeros_vector`, length-24 double[]): max element diff
  `0.00e+00` across sampled rows; root_number and analytic_rank identical.

Repointed entry points run end-to-end against Postgres, byte-identical to the oracle:
- `zero_battery.load_zero_vectors()` → **120,649** objects in 1.3 s; checksum
  `sum(vec[0]) = 16000.128597` (DuckDB: 16000.128597). ✓
- `research_battery.load_ec_data()` → **14,751** ECs (iso-deduped); checksum
  `sum(rank)+sum(arank) = 16784` (DuckDB: 16784). ✓
- All 28 files + `db.py` `py_compile` clean; the retirement guard raises as designed.

(The full `zero_battery` battery is compute-heavy — O(n²) pairwise distances — and was
not run to completion; that is workload, not a repoint issue. The data path is proven
identical.)

## Status
Read-path repoint **complete and validated**. DuckDB is no longer on Charon's read path.
`charon.duckdb` stays frozen as oracle/fallback (no delete). Remaining: owner sign-off on
the 4 flagged builders before any are re-run.

— Charon, 2026-06-24
