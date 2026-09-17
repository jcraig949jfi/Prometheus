-- 015: duplicate deliveries under a NEW sequence are seen sequences
--      (Mnemosyne, 2026-09-17, pre-Campaign-4 repair; Vivarium #335)
--
-- Vivarium's outbox mints event_id from CONTENT (producer | stream |
-- source_attempt | source_step | kind | payload digest), so a REPLAYED step
-- re-enqueues the same fact under a new dense sequence number. PEW answers
-- "duplicate" (correct: one fact, one row) but must still count that
-- sequence as delivered, or the checkpoint shows a phantom gap forever.
-- This column records those sequences; gap detection and the contiguous
-- sequence treat them as seen. Additive; default empty; no route semantics
-- change beyond two new response fields (duplicate, contiguous_seq).

ALTER TABLE ew.ingestion_checkpoints
    ADD COLUMN IF NOT EXISTS duplicate_seqs jsonb NOT NULL DEFAULT '[]'::jsonb;

INSERT INTO ew.schema_migrations (migration_id, applied_by, notes)
VALUES ('015', current_user, 'ingestion_checkpoints.duplicate_seqs: sequences delivered as content-duplicates count as seen')
ON CONFLICT (migration_id) DO NOTHING;
