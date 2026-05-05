-- ===========================================================================
-- sigma_kernel migration 005 -- add `precision_metadata` column to `sigma.claims`
-- Apply via:  psql -h <host> -U <user> -d prometheus_fire -f 005_add_precision_metadata.sql
-- Owner: Mnemosyne (DBA). Apply ONCE per environment (dev, staging, prod).
-- ===========================================================================
--
-- Purpose:
--   Promotes verification precision (mpmath dps, method, convergence
--   status, stability) to a first-class field on the CLAIM. Before this
--   migration, a dps=30 PASS and a dps=100 PASS look identical in the
--   ledger -- the substrate's epistemic ledger was under-specified.
--
--   Triggering observation (2026-05-04): a Lehmer brute-force run had
--   17 entries failing mpmath at dps=30 that ALL converged at dps=60
--   via factor-then-nroots. The 17 are not noise -- they're
--   resolution-dependent boundary objects. ChatGPT's reframe said it
--   plainly: "verification depth is a first-class axis of truth, not
--   a runtime detail."
--
--   See `sigma_kernel/PRECISION_METADATA_SPEC.md` for the rationale,
--   schema, and auto-caveat propagation rules. See
--   `prometheus_math/kill_vector.py` for the per-component
--   (precision_dps, method, convergence_status, stability) fields and
--   the matching aggregate fields on KillVector.
--
-- Idempotency:
--   The `ADD COLUMN IF NOT EXISTS` clause makes this migration safe to
--   re-apply. Existing claims rows pick up the new column with the
--   default value `NULL` (no precision recorded -- legacy/unrecorded).
--   Old kernel code that does not select `precision_metadata` continues
--   to work unchanged. The kernel auto-detects whether the column
--   exists at __init__ time and operates in legacy mode if not.
-- ===========================================================================

\set schema 'sigma'
SET search_path = :schema, public;

-- ---------------------------------------------------------------------------
-- Add `precision_metadata` column. JSON object or NULL; default NULL.
-- Shape: {"dps": int|null, "method": str, "convergence": str, "stability": float|null}
-- Stored as TEXT (mirrors the caveats column type from migration 004).
-- ---------------------------------------------------------------------------
ALTER TABLE claims
    ADD COLUMN IF NOT EXISTS precision_metadata TEXT DEFAULT NULL;

-- ---------------------------------------------------------------------------
-- Optional: index for "find all claims below the precision floor" queries.
-- LIKE-pattern is good enough for the MVP scale; rolling to JSONB + GIN can
-- happen in a later migration if the precision-audit query load demands it.
-- ---------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_claims_precision_metadata
    ON claims (precision_metadata text_pattern_ops);

-- ---------------------------------------------------------------------------
-- Permissions: parallels migrations 001 + 004. The new column inherits
-- the table-level grants already in place. No additional GRANT needed.
-- ---------------------------------------------------------------------------

-- ===========================================================================
-- End of migration 005
-- ===========================================================================
