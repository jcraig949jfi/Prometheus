-- ===========================================================================
-- sigma_kernel migration 002 — create bindings + evaluations tables
-- Apply via:  psql -h <host> -U <user> -d prometheus_fire -f 002_create_bind_eval_tables.sql
-- Default schema: sigma. For prototype isolation:
--     psql -v schema=sigma_proto -f 002_create_bind_eval_tables.sql
-- ===========================================================================
--
-- BIND/EVAL extension. Adds two tables to the sigma schema:
--   bindings     — symbols whose def_blob holds an executable callable ref
--   evaluations  — symbols whose def_blob holds a callable output + cost trace
--
-- Both reference sigma.symbols by (name, version). The substrate's
-- append-only discipline applies: rows here are immutable once written.
-- ===========================================================================

\set schema 'sigma'
SET search_path = :schema, public;

CREATE TABLE IF NOT EXISTS bindings (
    name              TEXT NOT NULL,
    version           INTEGER NOT NULL,
    callable_ref      TEXT NOT NULL,        -- "<module.path>:<qualname>"
    callable_hash     TEXT NOT NULL,        -- sha256 of inspect.getsource(fn)
    cost_model        TEXT NOT NULL,        -- JSON {max_seconds, max_memory_mb, max_oracle_calls}
    postconditions    TEXT NOT NULL,        -- JSON array of strings
    authority_refs    TEXT NOT NULL,        -- JSON array of strings (LMFDB labels, etc.)
    created_at        DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (name, version),
    FOREIGN KEY (name, version) REFERENCES symbols(name, version)
);

CREATE INDEX IF NOT EXISTS idx_bindings_callable_hash
    ON bindings (callable_hash);

CREATE TABLE IF NOT EXISTS evaluations (
    name              TEXT NOT NULL,
    version           INTEGER NOT NULL,
    binding_name      TEXT NOT NULL,
    binding_version   INTEGER NOT NULL,
    args_hash         TEXT NOT NULL,
    args_blob         TEXT NOT NULL,
    output_repr       TEXT NOT NULL,
    actual_cost       TEXT NOT NULL,        -- JSON {elapsed_seconds, memory_mb, oracle_calls}
    success           INTEGER NOT NULL,     -- 1 = ok, 0 = caller fn raised
    error_repr        TEXT NOT NULL,        -- empty if success
    created_at        DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (name, version),
    FOREIGN KEY (name, version) REFERENCES symbols(name, version),
    FOREIGN KEY (binding_name, binding_version) REFERENCES bindings(name, version)
);

CREATE INDEX IF NOT EXISTS idx_evaluations_binding
    ON evaluations (binding_name, binding_version);
CREATE INDEX IF NOT EXISTS idx_evaluations_args_hash
    ON evaluations (args_hash);

-- ---------------------------------------------------------------------------
-- Permissions (parallel to migration 001):
--     GRANT SELECT, INSERT ON bindings, evaluations TO ergon;
-- No DELETE/UPDATE — append-only discipline.
-- ---------------------------------------------------------------------------

-- ===========================================================================
-- End of migration 002
-- ===========================================================================
