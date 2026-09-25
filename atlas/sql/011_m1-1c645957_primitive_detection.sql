-- 011: a primitive with no detection rule is UNMEASURED, not untested.
-- The promotion charter (2026-09-24) requires Atlas to distinguish
--   unexplored           we could look and have not
--   unmeasurable here    no rule exists, so silence means nothing
-- Keeping that in prose (measured_by describes how it WOULD be measured)
-- let a rule-less primitive read as untested. It is now a column, and
-- atlas/harvest/theory.py fills it from PRIMITIVES.jsonl.detection_status.
ALTER TABLE atlas.primitive ADD COLUMN IF NOT EXISTS detection_status text;
