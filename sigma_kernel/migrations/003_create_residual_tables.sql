-- ===========================================================================
-- sigma_kernel migration 003 — create residuals + refinements tables
-- Apply via:  psql -h <host> -U <user> -d prometheus_fire -f 003_create_residual_tables.sql
-- Default schema: sigma. For prototype isolation:
--     psql -v schema=sigma_proto -f 003_create_residual_tables.sql
-- ===========================================================================
--
-- Residual primitive extension. Adds two tables to the sigma schema:
--   residuals    — typed records of non-uniform falsifications
--   refinements  — edges from a parent claim to a child refined claim,
--                  tagged with the residual that minted the refinement
--
-- Both reference sigma.claims by id. The substrate's append-only
-- discipline applies: rows are immutable once written.
--
-- See sigma_kernel/residuals.py and the proposal at
-- stoa/discussions/2026-05-02-techne-on-residual-aware-falsification.md
-- ===========================================================================

\set schema 'sigma'
SET search_path = :schema, public;

CREATE TABLE IF NOT EXISTS residuals (
    id                       TEXT PRIMARY KEY,
    parent_claim_id          TEXT NOT NULL REFERENCES claims(id),
    test_id                  TEXT NOT NULL,
    magnitude                DOUBLE PRECISION NOT NULL,
    surviving_subset_hash    TEXT NOT NULL,
    failure_shape            TEXT NOT NULL,        -- JSON
    classification           TEXT NOT NULL CHECK (classification IN
        ('signal', 'noise', 'instrument_drift', 'unclassified')),
    refinement_depth         INTEGER NOT NULL DEFAULT 0,
    cost_budget_remaining    DOUBLE PRECISION NOT NULL,
    instrument_id            TEXT NOT NULL,
    created_at               DOUBLE PRECISION NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_residuals_parent
    ON residuals (parent_claim_id);
CREATE INDEX IF NOT EXISTS idx_residuals_classification
    ON residuals (classification);

CREATE TABLE IF NOT EXISTS refinements (
    parent_claim_id   TEXT NOT NULL REFERENCES claims(id),
    child_claim_id    TEXT NOT NULL REFERENCES claims(id),
    via_residual_id   TEXT NOT NULL REFERENCES residuals(id),
    created_at        DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (parent_claim_id, child_claim_id)
);

CREATE INDEX IF NOT EXISTS idx_refinements_via_residual
    ON refinements (via_residual_id);

-- ---------------------------------------------------------------------------
-- Permissions (parallel to migration 001):
--     GRANT SELECT, INSERT ON residuals, refinements TO ergon;
-- No DELETE/UPDATE — append-only discipline.
-- ---------------------------------------------------------------------------

-- ===========================================================================
-- End of migration 003
-- ===========================================================================
