-- Atlas migration 006 (claimed in comms #501, 2026-09-19): one index, two
-- seats. Operator: Atlas (M1) and Atlas-M2 (M2) are separate seats that
-- build ONE set of atlas tables on M1, coordinated. harvest_run.seat names
-- the seat that wrote each pass (beside host_id and instance_tag).
ALTER TABLE atlas.harvest_run ADD COLUMN IF NOT EXISTS seat text;
UPDATE atlas.harvest_run SET seat = 'Atlas' WHERE seat IS NULL;   -- every pass before 006 was Atlas[m1-1c645957]
CREATE OR REPLACE VIEW atlas.v_writers AS
SELECT seat, host_id, instance_tag, harvester, count(*) AS passes, max(finished_at) AS last_finished
FROM atlas.harvest_run GROUP BY 1,2,3,4;
