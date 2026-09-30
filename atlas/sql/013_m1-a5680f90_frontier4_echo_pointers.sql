-- Atlas migration 013 (frontier/4, 2026-09-30): retire the per-line source pointers that frontier/3 minted
-- for pre-repair BLOCKED_BY_SUPPRESSION retry echoes (git:...EVENTS.jsonl#BLOCKED_BY_SUPPRESSION:<line>).
-- frontier/4 replaces them with ONE range pointer (#BLOCKED_BY_SUPPRESSION:<first>-<last>) on one aggregated
-- fact carrying occurrences and line runs (producer semantics: Archaeon comms #735). Raw provenance is
-- preserved in Archaeon's EVENTS.jsonl, which Atlas never alters. Only pointers that nothing references any
-- more are removed; a pointer still referenced by any row is kept.
DELETE FROM atlas.source s
WHERE s.uri LIKE 'git:archaeon/frontier/registry/EVENTS.jsonl#BLOCKED\_BY\_SUPPRESSION:%'
  AND s.uri !~ '#BLOCKED_BY_SUPPRESSION:[0-9]+-[0-9]+$'
  AND NOT EXISTS (SELECT 1 FROM atlas.fact_evidence x WHERE x.source_id = s.source_id)
  AND NOT EXISTS (SELECT 1 FROM atlas.source_link x WHERE x.source_id = s.source_id)
  AND NOT EXISTS (SELECT 1 FROM atlas.conclusion x WHERE x.source_id = s.source_id)
  AND NOT EXISTS (SELECT 1 FROM atlas.edge x WHERE x.source_id = s.source_id)
  AND NOT EXISTS (SELECT 1 FROM atlas.proposition_evidence x WHERE x.source_id = s.source_id)
  AND NOT EXISTS (SELECT 1 FROM atlas.portfolio_update x WHERE x.source_id = s.source_id);
