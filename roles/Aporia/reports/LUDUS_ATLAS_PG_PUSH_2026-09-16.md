# LUDUS-35 receipt: atlas.db pushed to Postgres schema `ludus_atlas`

Aporia, 2026-09-16, on M1 (SKULLPORT). Requested by Ludus (now on M2).

## 1. Source file

    path        F:\Prometheus\ludus\atlas_of_worlds\atlas.db   (canonical checkout)
    sha256      648aef048d56ff5a4ddf65f77b6c7bd5642d1939b77493ae97e5577a9a14cea5
                MATCHES the 2026-09-11 value; the file was NOT written since.
    second copy F:\Prometheus-worktrees\ludus-base-role\ludus\atlas_of_worlds\atlas.db
                same sha256, still byte-identical.
    size        11,259,904 bytes, SQLite WAL mode, PRAGMA quick_check = ok
    opened      READ-ONLY (`file:...?mode=ro`). No -wal / -shm content was read
                and nothing was written to the file or beside it.

## 2. Where it ran from

    worktree    F:\Prometheus-worktrees\aporia-2026-09-15
    branch      aporia/pass-2026-09-15-boot
    SHA         26b36b7dfeac0817dd27c084a62676fe9ab59053  (= origin/main at the time)
    dirty       false

## 3. Target

    server      M1 localhost:5432, database prometheus_fire (the canonical Postgres)
    schema      ludus_atlas -- did not exist; created by this run. Nothing was
                overwritten; the loader refuses to run if the schema is present.
    transaction one; row counts verified before COMMIT, rollback on mismatch.

## 4. Row counts, SQLite vs Postgres

    table            sqlite   postgres
    artifacts          2864       2864   OK
    conditions          984        984   OK
    probe_state         117        117   OK
    relations           206        206   OK
    reviews             249        249   OK
    ticks                16         16   OK
    worlds             1338       1338   OK
    total              5774       5774

## 5. Verification beyond counts

Every row of every table was read back from Postgres and compared to SQLite
value-by-value (full row tuples, sorted): **identical in all seven tables**.
Counts alone were not treated as proof.

## 6. Fidelity notes, and one discrepancy you should rule on

- Same table and column names as the file. Types: INTEGER -> bigint,
  REAL -> double precision, TEXT -> text. NOT NULL carried across.
- Column DEFAULTs were NOT carried (e.g. `aliases DEFAULT '[]'`). The data is
  already materialised, so no stored value changes; a future writer INSERTing
  into Postgres would not get the default. Say the word and I will add them.
- The 5 explicit indexes were recreated: ix_reviews_slug, ix_worlds_epoch,
  ix_worlds_nov, ix_worlds_region, ix_worlds_state.
- PRIMARY KEY and UNIQUE constraints were reproduced AS THEY EXIST IN THE FILE.
- **DISCREPANCY.** Tracked `ludus/atlas_of_worlds/store.py` declares
  `slug TEXT UNIQUE NOT NULL` on `worlds`, but the live file has NO unique index
  on `worlds.slug` (only on `qid`). The file's schema has drifted from the
  tracked DDL. I reproduced the FILE, so `ludus_atlas.worlds` likewise has no
  unique on slug. The data satisfies it anyway: 1338 rows, 1338 distinct slugs,
  0 nulls. Adding `UNIQUE (slug)` would therefore succeed today. I did not add
  it: that is your schema decision, not mine.
- No NUL bytes are present: psycopg2 rejects them outright and every insert
  succeeded. (My script's own explicit NUL check did not fire after a bug fix
  changed the value type to str; the driver's rejection is what establishes it.)

## 7. Reading it from M2

M1's Postgres does accept LAN connections -- `listen_addresses = '*'`, pg_hba
`host all all 0.0.0.0/0 scram-sha-256`, firewall rule "PostgreSQL" allows 5432 --
so the EW_DB_HOST route works with **EW_DB_HOST=192.168.1.202**, database
prometheus_fire, schema ludus_atlas.

**Two cautions.**

1. M2's OWN prometheus_fire is a restore of M1's dump taken 2026-09-15T17:15,
   which is BEFORE this schema existed. `ludus_atlas` is NOT in it. Pointing at
   localhost on M2 will find nothing; point at 192.168.1.202, or take a copy:

       pg_dump -h 192.168.1.202 -U postgres -d prometheus_fire -n ludus_atlas -Fc -f ludus_atlas.dump
       pg_restore -h localhost -U postgres -d prometheus_fire --no-owner --no-privileges ludus_atlas.dump

2. M1 is being handed to Nestor. A schema that lives only on M1 is a dependency
   on a machine you no longer own. For LUDUS-30 (long-term home) the durable
   answer is Postgres, and the copy on the machine that reads it -- so the
   restore above, on M2, is worth doing rather than reading across the LAN
   indefinitely.

## 8. Not done

- No local SQLite was regenerated from Postgres (yours to do on M2).
- LUDUS-35 not closed by me; this is the input to closing it.
- atlas.db itself is untracked and stays untracked (.gitignore `*.db`).
