# Ergon — Postgres "data spine dark" diagnosis (2026-06-23)

**Author:** Ergon (Claude Opus 4.8) · host `192.168.1.202` (PROMETHEUS_MACHINE=M1)
**Trigger:** James — "No duckdb fallback. What's wrong with our Postgres database?"
**Corrects:** the load-bearing premise of `roles/Harmonia/AUDIT_20260622_program_stall_map_of_disagreement.md`
action #1 ("DuckDB fallback shim — un-darks Ergon") and v2 CC-3. On THIS host the
premise is false: the spine is not dark.

---

## Verdict (one line)

**Nothing is wrong with the Postgres database.** It is a healthy local
PostgreSQL 17 (PID 6224, `0.0.0.0:5432`) serving all three databases fully
populated. The "spine dark" reading came from a **stale host address**, not a DB
fault. James was right to reject the fallback — there is nothing to fall back
*from*; the real DB is up.

## Evidence (E3 — run this session)

- `.176` is **off the LAN** — `ping 192.168.1.176` → "Destination host
  unreachable" from `.202` (no ARP/route = box powered off, not a Postgres
  process problem).
- Local PG17 is up: `netstat` PID 6224 LISTENING 5432; `psql.exe` at
  `C:\Program Files\PostgreSQL\17\bin`.
- Connect `localhost:5432 / lmfdb / lmfdb:lmfdb` → databases present:
  `lmfdb`, `prometheus_fire`, `prometheus_sci`.
- **lmfdb 363 GB**, ~52M rows across 6 core tables (planner est):
  `lfunc_lfunctions` 344 GB / 24.4M · `nf_fields` 9.8 GB / 22.2M ·
  `mf_newforms` 3.9 GB / 1.14M · `ec_curvedata` 2 GB / 3.82M ·
  `artin_reps` 468 MB / 798K · `g2c_curves` 43 MB / 66K.
- Real query proves it (not stale est): `SELECT count(*) FROM g2c_curves` =
  **66,158 in 95 ms**.
- **prometheus_fire 2.5 GB**, tables in schemas `zeros/xref/analysis/agora/noesis/sigma`:
  live `zeros.object_zeros` = 2.00M rows. **prometheus_sci 320 MB.**
- **Ergon's own scripts already connect to `localhost`** (`ergon/*.py`:
  `DB = dict(host='localhost', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')`).
  So Ergon is NOT blocked by `.176`. The canonical config
  `thesauros/prometheus_data/config.py` defaults to `devmirror.lmfdb.xyz`
  (→ 35.225.45.113, **port 5432 reachable** — the public LMFDB dev mirror is also up).

## The three REAL issues (none is a DB fault)

1. **Stale `.176` address in docs/config (~40 files), not a dead database.**
   The data was moved/restored to localhost on this machine; the dead `.176`
   reference is what makes components *look* dark. Components that hardcode
   `.176` (per the stall-map: Koios, Mnemosyne, Arachne-LMFDB, some Harmonia
   paths, `docs/state.json`, RESPONSIBILITIES.md) would fail to connect —
   fixable by **repointing to localhost / setting `PROMETHEUS_*_HOST`**, NOT by a
   DuckDB shim. Ergon already points at localhost and works.

2. **Stale planner / stats-collector statistics.** `pg_stat_user_tables.n_live_tup
   = 0` on 300 GB+ populated tables → stats were reset (likely at the 04-16
   migration) and never re-`ANALYZE`d. Harmless to correctness, but it misleads
   any health check that reads `n_live_tup` — a probable reason something
   *reported* the DB as empty. Fix: one `ANALYZE` pass.

3. **Leftover corruption-quarantine tables from the 2026-04-16 migration.**
   `zeros.object_zeros_corrupt_20260416` (2.0M rows, 1.27 GB) and
   `zeros.object_zeros_ext_corrupt_20260416` (17K rows) sit beside the healthy
   live `zeros.object_zeros` (2.0M rows). Confirms the 04-16 "single-point-of-
   failure migration" (audit's phrase) had a corruption event, worked around by
   rebuilding the live table. ~1.3 GB reclaimable; drop after a sanity check that
   live == intended.

## Proposed fix (real fix, not a fallback)

- Repoint stale `.176` references to `localhost` (or export
  `PROMETHEUS_LMFDB_HOST=localhost`, `PROMETHEUS_SCI_HOST`, `PROMETHEUS_FIRE_HOST`).
- Run `ANALYZE` on the three DBs to refresh stats (kills the false "empty" reads).
- After verifying `zeros.object_zeros` is the intended live table, `DROP` the two
  `*_corrupt_20260416` tables to reclaim ~1.3 GB.

## So-what for the reassessment

The stall-map's #1 leverage action (DuckDB shim) and its "Ergon dark" claim are
**E0/E1 inferences from the stale `.176` doc**, not E3 truths about this host. On
M1 the data spine is alive and fast. This does not refute the audit's other layers
(selection monoculture, M0 keystone, expressiveness ceiling) — only its
infra-starvation layer, and only on this machine. The corrected action is
**repoint + ANALYZE + drop corrupt**, ~0 new code.
