-- 007 (DRAFT; separate and REVERSIBLE): one attempt row per pre-release queue row.
--      (Vivarium, 2026-09-17; EXPERIMENT_TRANSACTION_MODEL.md s7; STAGE2_SELF_CRITIQUE.md Q5)
--
-- History is REPRESENTED, not reinterpreted: attempt_number 1, design_digest
-- = spec_hash, bundle_hash NULL (UNKNOWN), terminal_state from status,
-- termination_reason UNKNOWN. NO steps are fabricated. Old error strings are
-- NEVER parsed into a termination reason (forbidden; a test asserts it).
-- Reversal: DELETE FROM execution_attempt WHERE claim_grant->>'backfill' = '007'
-- -- the immutability trigger is bypassed for this exact predicate by the
-- reversal script, which is the only DELETE path and is itself a draft.

INSERT INTO {schema}.execution_attempt
    (experiment_id, attempt_number, design_digest, worker_id, claim_grant, opened_at, closed_at,
     terminal_state, termination, of_record)
SELECT q.experiment_id, 1, q.spec_hash, coalesce(q.claimed_by, 'UNKNOWN'),
       jsonb_build_object('backfill', '007', 'note', 'pre-release row; no ClaimGrant existed'),
       coalesce(q.claimed_at, q.created_at), q.finished_at,
       CASE q.status WHEN 'completed' THEN 'COMPLETED' WHEN 'failed' THEN 'FAILED'
                     WHEN 'cancelled' THEN 'CANCELLED' ELSE NULL END,
       CASE WHEN q.status IN ('completed','failed','cancelled') THEN
            jsonb_build_object('envelope_version', 'viv.termination.v1',
                               'termination_reason', 'UNKNOWN',
                               'terminal_state', CASE q.status WHEN 'completed' THEN 'COMPLETED'
                                                               WHEN 'failed' THEN 'FAILED' ELSE 'CANCELLED' END,
                               'censored', NULL, 'censoring_reason', NULL, 'partial', NULL,
                               'observations_recorded', NULL,
                               'note', 'backfilled 007; reason not inferred from error text')
       ELSE NULL END,
       (q.status = 'completed')
  FROM {schema}.research_experiment_queue q
 WHERE q.status IN ('completed','failed','cancelled')
   -- PRE-RELEASE means created before the window (C4-20260917-W1). apply_migrations
   -- runs on every consumer start; without this cutoff a post-release row cancelled
   -- while queued (which has no attempt by design) would be backfilled as if it
   -- were history.
   AND q.created_at < TIMESTAMPTZ '2026-09-17 14:00:00+00'
   AND NOT EXISTS (SELECT 1 FROM {schema}.execution_attempt a WHERE a.experiment_id = q.experiment_id);

-- queued / claimed / running rows at migration time get NO backfilled attempt:
-- the loop opens attempt 1 for them when it claims (queued) or the operator
-- releases them (claimed/running are, at the window, stranded by definition).
