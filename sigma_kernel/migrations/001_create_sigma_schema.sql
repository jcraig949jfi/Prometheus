-- ===========================================================================
-- sigma_kernel migration 001 -- create the `sigma` schema in prometheus_fire
-- Apply via:  psql -h <host> -U <user> -d prometheus_fire -f 001_create_sigma_schema.sql
-- Owner: Mnemosyne (DBA). Kernel uses RW connection via thesauros.prometheus_data.get_fire().
-- ===========================================================================
--
-- Why prometheus_fire:
--   The kernel writes (PROMOTE / ERRATA / FALSIFY-binding). prometheus_sci is
--   read-only per pool.py's get_sci(); only get_fire() is RW. The kernel's
--   substrate is conceptually fire-side (computed/derived state, not LMFDB
--   raw mathematical data), so this fits.
--
-- Why a `sigma` schema (not new DB):
--   Reversible. If the kernel earns its own DB later, ALTER ... SET SCHEMA
--   moves these tables out cleanly. New DB requires a separate provisioning
--   request and isolates the kernel from the rest of fire's tooling.
-- ===========================================================================

CREATE SCHEMA IF NOT EXISTS sigma;

-- ---------------------------------------------------------------------------
-- symbols: append-only substrate
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sigma.symbols (
    name        TEXT NOT NULL,
    version     INTEGER NOT NULL,
    def_hash    TEXT NOT NULL,
    def_blob    TEXT NOT NULL,
    provenance  TEXT NOT NULL,    -- JSON array of dependency hashes
    tier        TEXT NOT NULL,
    created_at  DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (name, version)
);

CREATE INDEX IF NOT EXISTS idx_sigma_symbols_def_hash
    ON sigma.symbols (def_hash);

-- ---------------------------------------------------------------------------
-- claims: provisional hypotheses, replayable
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sigma.claims (
    id                  TEXT PRIMARY KEY,
    target_name         TEXT NOT NULL,
    hypothesis          TEXT NOT NULL,
    evidence            TEXT NOT NULL,    -- JSON
    kill_path           TEXT NOT NULL,
    target_tier         TEXT NOT NULL,
    status              TEXT NOT NULL DEFAULT 'pending',
    verdict_status      TEXT,
    verdict_rationale   TEXT,
    verdict_input_hash  TEXT,
    verdict_seed        INTEGER,
    verdict_runtime_ms  INTEGER
);

-- ---------------------------------------------------------------------------
-- capabilities: linear capability tokens; double-spend rejected by `consumed`
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sigma.capabilities (
    cap_id      TEXT PRIMARY KEY,
    cap_type    TEXT NOT NULL,
    consumed    INTEGER NOT NULL DEFAULT 0
);

-- ---------------------------------------------------------------------------
-- Permissions (adjust to your DBA conventions)
-- ---------------------------------------------------------------------------
-- Assuming the kernel connects as the `ergon` user (per pool.py's get_fire).
-- Mnemosyne may want to create a dedicated `sigma` role and GRANT explicitly.
-- For now, the schema owner gets write; ergon needs read+write:
--
-- GRANT USAGE ON SCHEMA sigma TO ergon;
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA sigma TO ergon;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA sigma
--   GRANT SELECT, INSERT, UPDATE ON TABLES TO ergon;
--
-- Note: kernel discipline enforces append-only at the API layer; we do NOT
-- grant DELETE. UPDATE is needed only for capabilities.consumed flip and
-- claims.verdict/status updates (claims are not part of the immutable
-- substrate — only symbols are).

-- ===========================================================================
-- End of migration 001
-- ===========================================================================
