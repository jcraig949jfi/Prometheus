-- ===========================================================================
-- sigma_kernel migration 004 -- add `caveats` column to `sigma.claims`
-- Apply via:  psql -h <host> -U <user> -d prometheus_fire -f 004_add_caveats_to_claims.sql
-- Owner: Mnemosyne (DBA). Apply ONCE per environment (dev, staging, prod).
-- ===========================================================================
--
-- Purpose:
--   Operationalizes ChatGPT's structural fix to the AI-to-AI inflation
--   pattern (C3 in stoa/discussions/2026-05-03-team-review-techne-bind-eval-and-pivot.md).
--   Caveats become typed fields on the CLAIM. Documents referencing the
--   result inherit them automatically rather than maintaining them at
--   every documentation layer manually.
--
--   See `stoa/proposals/2026-05-04-techne-caveat-as-metadata-schema.md`
--   for the rationale, schema, and propagation rules.
--
-- Idempotency:
--   The `ADD COLUMN IF NOT EXISTS` clause makes this migration safe to
--   re-apply. Existing claims rows pick up the new column with the
--   default value `'[]'` (empty JSON array). Old kernel code that does
--   not select `caveats` continues to work unchanged.
-- ===========================================================================

\set schema 'sigma'
SET search_path = :schema, public;

-- ---------------------------------------------------------------------------
-- Add `caveats` column. JSON array of strings, default empty.
-- ---------------------------------------------------------------------------
ALTER TABLE claims
    ADD COLUMN IF NOT EXISTS caveats TEXT NOT NULL DEFAULT '[]';

-- ---------------------------------------------------------------------------
-- Optional: index for "find all claims with this caveat" queries.
-- LIKE-pattern is good enough for the MVP scale (≤1M claims). A future
-- migration can replace this with a JSONB column + GIN index if scale
-- demands it.
-- ---------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_claims_caveats
    ON claims (caveats text_pattern_ops);

-- ---------------------------------------------------------------------------
-- Permissions: parallels migration 001. The `caveats` column inherits
-- the table-level grants already in place. No additional GRANT needed.
-- ---------------------------------------------------------------------------

-- ===========================================================================
-- End of migration 004
-- ===========================================================================
