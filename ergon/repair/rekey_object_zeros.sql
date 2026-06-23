-- rekey_object_zeros.sql — one slow-roll tick of the object_id repair.
-- Invoke:  psql -1 -q -v ON_ERROR_STOP=1 -v batch=4000 -f rekey_object_zeros.sql
-- Idempotent + resumable: only touches rows where object_id IS NULL, only
-- registers labels not already present. Runs as ONE transaction (psql -1).
--
-- Context: zeros.object_zeros had object_id NULL on 1,984,167 / 2,009,089 EC
-- rows (the 2026-04-16 load only id'd the 24,922 curves already in the registry;
-- the registry sequence was desynced at last_value=1 vs max(object_id)=134475,
-- so the loader collided on the PK and left the rest NULL). lmfdb_label is the
-- intact true identity. Fix = mint a registry id per unregistered label, then
-- backfill object_zeros from the registry. New ids are > 134475 (the watermark),
-- which makes the whole operation reversible. See README_rekey_2026-06-23.md.

-- Phase 1 — mint registry ids for a batch of still-unregistered EC labels.
-- object_id is assigned by xref.object_registry_object_id_seq (setval'd to the
-- table max during setup). ON CONFLICT guards the (source_db,source_table,
-- source_key) unique key.
WITH todo AS (
  SELECT lmfdb_label, conductor
  FROM zeros.object_zeros
  WHERE object_id IS NULL
    AND NOT EXISTS (
      SELECT 1 FROM xref.object_registry r
      WHERE r.source_db = 'charon_duckdb'
        AND r.source_table = 'elliptic_curve'
        AND r.source_key = lmfdb_label)
  ORDER BY lmfdb_label
  LIMIT :batch
)
INSERT INTO xref.object_registry (source_db, source_table, source_key, object_type, conductor)
SELECT 'charon_duckdb', 'elliptic_curve', lmfdb_label, 'elliptic_curve', conductor
FROM todo
ON CONFLICT (source_db, source_table, source_key) DO NOTHING;

-- Phase 2 — backfill object_zeros.object_id from the registry for a batch of
-- NULL rows whose label is now registered (includes the ones just minted).
WITH todo AS (
  SELECT z.ctid, r.object_id AS oid
  FROM zeros.object_zeros z
  JOIN xref.object_registry r
    ON r.source_db = 'charon_duckdb'
   AND r.source_table = 'elliptic_curve'
   AND r.source_key = z.lmfdb_label
  WHERE z.object_id IS NULL
  LIMIT :batch
)
UPDATE zeros.object_zeros z
SET object_id = t.oid
FROM todo t
WHERE z.ctid = t.ctid;
