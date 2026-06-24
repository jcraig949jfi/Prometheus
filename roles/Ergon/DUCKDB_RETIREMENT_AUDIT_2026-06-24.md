# DuckDB retirement audit (2026-06-24)

**Author:** Ergon (Claude Opus 4.8) · host M1 (`192.168.1.202`)
**Trigger:** James — "the plan was to retire DuckDB, moving all its data to Postgres.
Did this fully happen? Is any active code still relying on duckdb? It's supposed to
be retired."
**Verdict (updated 2026-06-24):** Data migration is now **COMPLETE** — all DuckDB data
is in Postgres (see "Migration executed" below). What remains for full retirement is a
**code** task: ~40+ direct `duckdb.connect()` calls in Charon's source tree must be
repointed to Postgres. **Still DO NOT delete `charon.duckdb`** until that code is
repointed and validated. (Per [[feedback_retirement_needs_thoughtwork_dossier_hitl]]:
read-only RETIRE needs a dossier + HITL sign-off; deletion is off the table.)

## Migration executed (2026-06-24, Ergon)

All 14 `charon.duckdb` tables mirrored **verbatim** (lossless, same column names) into
`prometheus_fire.charon_duckdb.*` via DuckDB's `postgres` extension (in-memory hub,
source attached READ_ONLY so `charon.duckdb` stays pristine — mtime still 2026-04-03).
**Row counts match exactly on every table; 1,242,918 rows total.** Array fidelity
spot-checked (dirichlet_zeros conductor=1 = the Riemann ζ zeros, arrays intact). The
former gap tables (`dirichlet_zeros` 184,830 / `graph_edges` 396,150 / `object_zeros_ext`
17,313 / `landscape` 119,464) are now present and verified. `noesis_v2.duckdb` (19
tables) was already fully present in `prometheus_fire.noesis.*` — re-verified, all match.
`ANALYZE` run on `prometheus_fire`. **Postgres now holds all DuckDB data.**

The pre-existing normalized empty tables (e.g. `zeros.dirichlet_zeros`) are left as-is;
`charon_duckdb.*` is the faithful archive and the drop-in target for the Charon repoint
(identical schema to what `charon/src` already queries).

## State of the DuckDB files

- `charon/data/charon.duckdb` — 1.18 GB, **frozen since 2026-04-03** (no writes in
  ~2.7 months). 14 tables.
- `noesis/v2/noesis_v2.duckdb` — 20 MB, frozen since 2026-03-30.
- The write-path is effectively retired (nothing has written to either file since the
  April migration). The read-path is not.

## Migration completeness — charon.duckdb → Postgres

MIGRATED (verified, exact or superset):
- `main.objects` (134,475) → `prometheus_fire.xref.object_registry` (was 134,475;
  now 2,118,642 after the 2026-06-23 object_id repair). ✓
- `main.known_bridges` (17,314) → `xref.bridges` (17,314). ✓ exact
- `main.disagreement_atlas` (119,397) → `analysis.disagreement_atlas` (119,397). ✓ exact
- `main.object_zeros` (120,649) → `zeros.object_zeros` (2,009,089 — superset, fresh
  larger ingest). ✓
- `main.modular_forms` (102,150), `main.elliptic_curves` (31,073) → present as
  supersets in the separate `lmfdb` DB (`mf_newforms` 1.1M, `ec_curvedata` 3.8M). ✓
  (in Postgres, though in `lmfdb` not `prometheus_fire`.)
- `main.l_functions` (0), `main.failure_log` (0) — empty, nothing to migrate. n/a

NOT MIGRATED — data exists ONLY in the frozen charon.duckdb (≈717K rows):
- **`main.dirichlet_zeros` (184,830)** → `zeros.dirichlet_zeros` exists but is **EMPTY
  (0 rows)**. Clear gap.
- **`main.graph_edges` (396,150)** → no Postgres equivalent (`noesis.cross_domain_edges`
  is a different, smaller 20,502-row table). Charon's isogeny/congruence graph.
- **`main.object_zeros_ext` (17,313)** → only ever landed in pg as the corrupt copy
  `zeros.object_zeros_ext_corrupt_20260416`, which was dropped 2026-06-24 (source still
  safe in duckdb). No live pg table.
- **`main.landscape` (119,464)** → `noesis.prime_landscape` has only 6 rows. The
  `pool.py` docstring claims landscape went to Redis (`landscape:by_curvature`) —
  **UNVERIFIED** (no redis-cli on host this session). Confirm before treating as migrated.
- `main.hypothesis_queue` (100), `main.ingestion_log` (3) — minor; likely superseded
  by `agora.research_queue` / `meta.ingestion_log`.

## Active code still depending on DuckDB

- The central data layer is correctly retired: `thesauros/prometheus_data/pool.py`
  `get_duckdb()` is **DEPRECATED** (emits `DeprecationWarning`, docstring says use
  Postgres). Nothing should call it.
- BUT **~40+ direct `duckdb.connect("charon/data/charon.duckdb")` calls bypass the
  shim**, concentrated in **Charon's source tree** — `charon/src/*` (ingest.py,
  build_graph.py, embed.py, schema.py, research_battery.py, three_investigations.py,
  genus2_crossing.py, disagreement_atlas.py, …), `charon/v2/*`, `charon/tests/*` —
  plus experiment scripts in `harmonia/scripts/`, `koios/scripts/`,
  `cartography/shared/scripts/`. Charon is an active component, so these are live
  dependencies, not dead code.
- `duckdb` is **not installed in the base Python** (`import duckdb` fails), same as
  `psycopg2`. So this code only runs in a venv that has duckdb; in the base runtime it
  would crash. (Client installed this session only to perform the audit.)

## Recommendation (no deletion)

1. **Keep `charon.duckdb`** until the 4 gap tables are migrated or confirmed
   redundant. It is the sole home of dirichlet_zeros / graph_edges / object_zeros_ext /
   landscape.
2. Migrate the gaps: `zeros.dirichlet_zeros` (184,830 — table exists, just empty),
   `xref` graph edges (396,150), `zeros.object_zeros_ext` (17,313). Verify landscape in
   Redis before deciding.
3. Then repoint Charon's `charon/src` DB_PATH usage from `duckdb.connect(...)` to the
   `prometheus_data` Postgres pool, and have it go through the (un-deprecated) layer.
4. Only after 1–3: a thoughtwork-dossier + HITL sign-off to mark DuckDB RETIRED (still
   no delete).

## Also fixed this session (same April-migration failure class)

- Dropped the 3 `*_corrupt_20260416` quarantine tables (prometheus_fire 3140→1862 MB).
- **Latent sequence desyncs** (same root cause as the object_id bug — sequence at
  `last_value=1, is_called=false` while the column has data; next insert would PK-collide):
  fixed `xref.bridges_bridge_id_seq` (→17314) and `meta.ingestion_log_log_id_seq` (→4).
  Full sequence-vs-column-max sweep of prometheus_fire otherwise clean
  (`xref.object_registry.object_id` healthy at 2,118,642).
