-- Custody registry (C-004-OP2; draft B B5; MWO-0004 D2-1 form). Registrar: Aporia. Keeper/authority: operator.
-- Append-only, hash-chained, identifiers and hashes only (no content).
-- Location: M1 SKULLPORT Postgres 17, database prometheus_fire, table custody.registry.
--
-- Integrity model:
--   * registered_at_utc is set by the server (clock_timestamp), never by the caller: no backdating.
--   * each row carries prev_hash (row_hash of the previous row; genesis = 64 zeros) and
--     row_hash = sha256(row_id|registered_at_utc|registrar|record_kind|repo_path|blob_sha256|commit_sha|prev_hash),
--     computed by the server; any later edit or deletion breaks the chain (python -m ops.custody.registry verify).
--   * UPDATE, DELETE and TRUNCATE raise.
-- Residual (stated, not hidden): every seat connects as the same superuser, which can disable triggers. Write
-- exclusivity is therefore procedural (only the Aporia registrar tool inserts; registrar must be 'Aporia'), and
-- tampering is detected, not prevented: the chain head is published on comms at every registration.
CREATE SCHEMA IF NOT EXISTS custody;

CREATE TABLE IF NOT EXISTS custody.registry (
    row_id            bigint PRIMARY KEY,
    registered_at_utc timestamptz NOT NULL,
    registrar         text NOT NULL CHECK (registrar = 'Aporia'),
    record_kind       text NOT NULL CHECK (record_kind IN ('EVIDENCE_MANIFEST','RUN_INVENTORY','STAGE_RECORD',
                                                           'WITHDRAWAL','EXPECTED_ANSWER_TABLE')),
    repo_path         text NOT NULL CHECK (repo_path <> '' AND repo_path !~ '^/' AND repo_path !~ '\\'),
    blob_sha256       char(64) NOT NULL CHECK (blob_sha256 ~ '^[0-9a-f]{64}$'),
    commit_sha        char(40) NOT NULL CHECK (commit_sha ~ '^[0-9a-f]{40}$'),
    campaign          text NOT NULL DEFAULT 'C-004',
    prev_hash         char(64) NOT NULL,
    row_hash          char(64) NOT NULL UNIQUE
);

CREATE OR REPLACE FUNCTION custody.row_digest(r custody.registry) RETURNS char(64) LANGUAGE sql IMMUTABLE AS $$
  SELECT encode(sha256(convert_to(concat_ws('|', r.row_id::text,
      to_char(r.registered_at_utc AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS.US"Z"'),
      r.registrar, r.record_kind, r.repo_path, r.blob_sha256, r.commit_sha, r.prev_hash), 'UTF8')), 'hex')::char(64)
$$;

CREATE OR REPLACE FUNCTION custody.before_insert() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE head custody.registry;
BEGIN
  LOCK TABLE custody.registry IN SHARE ROW EXCLUSIVE MODE;
  SELECT * INTO head FROM custody.registry ORDER BY row_id DESC LIMIT 1;
  NEW.row_id := COALESCE(head.row_id, 0) + 1;
  NEW.registered_at_utc := clock_timestamp();
  NEW.prev_hash := COALESCE(head.row_hash, repeat('0', 64));
  NEW.row_hash := custody.row_digest(NEW);
  RETURN NEW;
END $$;

CREATE OR REPLACE FUNCTION custody.refuse_change() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'custody.registry is append-only: % refused', TG_OP;
END $$;

DROP TRIGGER IF EXISTS registry_before_insert ON custody.registry;
CREATE TRIGGER registry_before_insert BEFORE INSERT ON custody.registry
  FOR EACH ROW EXECUTE FUNCTION custody.before_insert();
DROP TRIGGER IF EXISTS registry_no_update_delete ON custody.registry;
CREATE TRIGGER registry_no_update_delete BEFORE UPDATE OR DELETE ON custody.registry
  FOR EACH ROW EXECUTE FUNCTION custody.refuse_change();
DROP TRIGGER IF EXISTS registry_no_truncate ON custody.registry;
CREATE TRIGGER registry_no_truncate BEFORE TRUNCATE ON custody.registry
  FOR EACH STATEMENT EXECUTE FUNCTION custody.refuse_change();
