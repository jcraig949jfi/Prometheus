-- Atlas migration 005 (2026-09-19): identity correction, recorded in
-- roles/Atlas/calibration/LEDGER.md. npe/1..3 keyed G-R16-* experiments
-- under a fabricated campaign nestor.graphworld/r16 (R16 is a regime
-- label, not a round). npe/4 keys them under nestor.graphworld/unassigned.
-- Atlas's own mis-keyed rows are removed here; no source data is touched.
DELETE FROM atlas.source_link WHERE entity_key LIKE 'nestor.graphworld/r16%';
DELETE FROM atlas.fact WHERE subject_key LIKE 'nestor.graphworld/r16%';
DELETE FROM atlas.conclusion WHERE subject_key LIKE 'nestor.graphworld/r16%';
DELETE FROM atlas.edge WHERE src_key LIKE 'nestor.graphworld/r16%' OR dst_key LIKE 'nestor.graphworld/r16%';
DELETE FROM atlas.entity_commit WHERE entity_key LIKE 'nestor.graphworld/r16%';
DELETE FROM atlas.signal WHERE subject_key LIKE 'nestor.graphworld/r16%';
DELETE FROM atlas.experiment WHERE campaign_key = 'nestor.graphworld/r16';
DELETE FROM atlas.campaign WHERE campaign_key = 'nestor.graphworld/r16';
