# object_id re-key repair — slow-roll (2026-06-23)

Repairs `prometheus_fire.zeros.object_zeros`, where `object_id` was NULL on
**1,984,167 / 2,009,089** elliptic-curve rows.

## Root cause

The 2026-04-16 load only assigned `object_id` to the 24,922 curves already
present in `xref.object_registry`. The registry's id sequence
(`xref.object_registry_object_id_seq`) was **desynced** — `last_value=1,
is_called=false` while `max(object_id)=134475` — so any insert using the
sequence default would have collided on the primary key. The loader therefore
left the remaining ~1.98M curves with NULL `object_id`. `lmfdb_label` (the true
identity) is intact on every row; arrays/labels are clean. The same NULL pattern
exists in the `*_corrupt_20260416` quarantine copies.

## The fix

1. **Setup (one-time, done):** `setval` the sequence to `max(object_id)` (next id
   = 134476), create a partial index `ix_oz_null_label ON zeros.object_zeros
   (lmfdb_label) WHERE object_id IS NULL` (shrinks as rows are fixed).
2. **Per tick** (`rekey_object_zeros.sql`, one transaction):
   - *register* a batch of unregistered labels into `xref.object_registry`
     (`source_db='charon_duckdb', source_table='elliptic_curve'`; id from the
     sequence; `ON CONFLICT` on the unique key);
   - *backfill* `object_zeros.object_id` from the registry by label join, only
     where `object_id IS NULL`.
3. **Driver:** `rekey_tick.ps1`, run by the Windows Scheduled Task
   **`PrometheusRekeyObjectZeros`** every minute (batch=4000 → ~8 h). The wrapper
   logs each tick, and on `remaining_null=0` runs a final `VACUUM ANALYZE`, writes
   `rekey.done`, and disables the task.

Credentials: psql reads `%APPDATA%\postgresql\pgpass.conf`
(`localhost:5432:*:postgres:…`). No password is stored in these files.

**Reversibility watermark = 134475.** Every row this repair touches gets an
`object_id > 134475`. Originally-valid ids are ≤ 31073.

## Monitor

```
tail -f ergon/repair/rekey_progress.log
# or
psql -h localhost -U postgres -d prometheus_fire -tAc \
  "SELECT count(*) FILTER (WHERE object_id IS NULL) AS remaining,
          count(*) FILTER (WHERE object_id>134475) AS minted FROM zeros.object_zeros;"
```

## Control

```
# pause / resume / stop
schtasks /Change /TN PrometheusRekeyObjectZeros /DISABLE
schtasks /Change /TN PrometheusRekeyObjectZeros /ENABLE
schtasks /Delete  /TN PrometheusRekeyObjectZeros /F
# change batch size: set a machine env var REKEY_BATCH before next tick
```

## Reverse (undo everything this repair did)

```sql
-- un-key the rows we backfilled
UPDATE zeros.object_zeros SET object_id = NULL WHERE object_id > 134475;
-- remove the registry rows we minted
DELETE FROM xref.object_registry WHERE object_id > 134475;
-- (optional) restore the sequence
SELECT setval('xref.object_registry_object_id_seq', 134475, true);
```

## After completion (separate, optional)

The three `*_corrupt_20260416` quarantine tables (`zeros.object_zeros_corrupt_*`,
`zeros.object_zeros_ext_corrupt_*`, `zeros.dirichlet_zeros_corrupt_*`, ~1.28 GB)
can be dropped to reclaim space — they are stale copies of the same data and are
NOT touched by this repair. Drop only after confirming the live tables are good.
