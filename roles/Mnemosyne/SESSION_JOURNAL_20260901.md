# Mnemosyne Session Journal — 2026-09-01 (world-state refresh, read-only)

## Session Overview

First Mnemosyne session since 2026-04-29. James's directive: get the state of
the world up to date; **no ingestion, no action**. Everything this session did
was read-only against the live databases plus two documentation writes
(`mnemosyne/STATE.md` rewrite, this journal). Zero database writes, zero queue
changes, zero bus posts.

Identity: Claude session under @roles/Mnemosyne per James. Running on M1.

---

## What I verified (live queries, 2026-09-01)

1. **Postgres spine is local and healthy on M1** — PostgreSQL 17.9 on
   localhost serves lmfdb (365 GB), prometheus_sci (320 MB), prometheus_fire
   (2.76 GB). The `.176` host in my April docs is dead.
2. **The spine is in active daily use** — `agora.machine_probes` (112K rows)
   and `agora.intelligence_outputs` (13K rows) have entries written TODAY;
   Pronoia (M4) and Elenchus (M2) heartbeating online.
3. **Redis retired → PgRedis** (`prometheus_fire.bus`), but the bus itself is
   nearly unused (8 entries ever, all tables empty now). Coordination moved to
   the `agora.*` relational tables.
4. **DuckDB retired** → `prometheus_fire.charon_duckdb.*` (14 tables, 1.24M
   rows).
5. **The rekey campaign landed**: xref.object_registry 134K → 2,118,642;
   zeros.object_zeros 121K → 2,009,089 (real COUNT(*), not estimates).
6. **zeros.dirichlet_zeros is now 0** (was 184,830; rows exist in the
   charon_duckdb mirror). Looks like dedup, but undocumented — flagged as an
   open question in STATE.md, not "fixed."
7. **sigma schema evolved** — 7 tables (was 3), 1,079 claims recorded,
   claims columns differ from the 04-29 MVP. Substrate-Tester fire commits
   own that history.
8. **nf_fields is FULL** (22.18M rows) — the old P6 partial-pull item is done.
9. **Queue**: REQ-001 (Bloom Erdős) and REQ-002 (MathNet) both still open;
   HELD per today's no-ingest directive. Statuses left untouched (append-only
   discipline; a hold is a directive, not a resolution).

## What was NOT done (deliberately)
- No ANALYZE (it's overdue, but it mutates stats — "take no action").
- No queue status edits, no agora/bus posts, no RESPONSIBILITIES.md rewrite.
- No git commit — the working tree carries another seat's in-flight work on
  branch daedalus/serendipity-foundry-engine; the two files written
  (`mnemosyne/STATE.md`, this journal) are left for James to commit or for a
  pathspec-scoped commit when authorized.

---

# Addendum (same session, later): data-existence audit + legacy-store sweep

## Data-existence audit (James-approved; read-only vs DBs)

Artifacts: `mnemosyne/data_existence_audit_20260901.{py,jsonl}` +
`mnemosyne/DATA_EXISTENCE_AUDIT_2026-09-01.md`. Key results over 534
catalog problems: 253 UNCLAIMED_CANDIDATE_DATA (bucket-C "no data coupling"
defaults whose subdomain HAS loaded spine data — number_theory 75,
additive_combinatorics 41, combinatorics 33, discrete_geometry 32, …),
222 NO_KNOWN_COUPLING, 22 pure-compute, 20 claimed-and-present, 17
requires-extension, 0 claimed-but-absent (no drift).

Join-integrity defects found in the catalog files (reported, not fixed):
- MATH-0491/0492/0493: id COLLISIONS — same id, two different problems.
- 18 authored A2 specs appended as duplicate triage lines over old
  bucket-C rows (safe for last-wins readers like backlog_gen.py:67 only).
- 24 questions (MATH-0514..0537) appended post-May, never triaged.

## Legacy-store inventory (Explore agent, read-only) + todo notes

Full verdicts recorded in STATE.md ("Legacy non-Postgres stores"). Headline:
**kill_taxonomy was never migrated because my own migrate_m2.py:231 loader
reads the wrong source and returns 0 as success** — 21 kills live in
`forge/v3/kill_taxonomy.db` (SQLite) and Ergon's hypothesis gate reads them
from there today. Also: charon/src IS repointed (fa8f625a1; the 06-24 audit
is stale on this), and the real duckdb-deletion blocker is ~180 legacy
read-only call sites in cartography/harmonia/koios.

Per James: placed `todo_20260901.md` in roles/{Charon, CrossDomainCartographer,
Harmonia, Koios, Ergon} — each specifies the outstanding repoint with
file:line, and the protocol: flip Status to DONE, Mnemosyne sweeps
`roles/*/todo_*.md`, and the `.duckdb`/SQLite files are deleted only after
all seats flip (row-for-row verification first). Charon's note was REVISED
mid-session when the inventory showed her main repoint already landed.

## Files changed this session
- `mnemosyne/STATE.md` — full rewrite (2026-09-01 snapshot) + legacy-store section
- `roles/Mnemosyne/SESSION_JOURNAL_20260901.md` — this file (NEW)
- `mnemosyne/data_existence_audit_20260901.py` + `.jsonl` +
  `mnemosyne/DATA_EXISTENCE_AUDIT_2026-09-01.md` (NEW)
- `roles/{Charon,CrossDomainCartographer,Harmonia,Koios,Ergon}/todo_20260901.md` (NEW)
