# Draft migrations (point release) -- NOT applied

Files here are DRAFTS. `viv.db.apply_migrations` globs `migrations/*.sql`
(non-recursive) and cannot pick them up. Promotion into `migrations/` is the
deploy act, taken only in the coordinated window after Stage 3 review
(Operator Amendment 1 s3/s11; Stage 1/2 direction s20).

    006_execution_attempts_and_steps.sql   attempts, design-keyed steps, provenance envelope (EXPERIMENT_TRANSACTION_MODEL.md)
    007_backfill_attempts_reversible.sql   one attempt per pre-release row; UNKNOWN reason; no steps; reversible
    008_bundles_receipts_gates.sql         start bundles, intervention receipts, gate receipts
    009_pew_outbox.sql                     the durable, ordered, idempotent PEW outbox

`check_drafts.py` applies 001-005 + the drafts to a THROWAWAY schema on the
canonical server (VIV_SCHEMA=viv_draft_<hex>, dropped at the end; the
production schema `viv` is refused by drop_schema and never named) and
exercises every trigger: VIV11/12/14/15/17 (attempts), VIV20/21/22 (step
keys and replay), VIV40/42 (outbox), and the backfill's UNKNOWN reason.
Run: `python migrations/drafts/check_drafts.py` from vivarium/ with
EW_DB_HOST/VIV_DB_HOST set. Last run 2026-09-17: 15/15 ok.
