-- Atlas migration 009 (2026-09-21): vocabulary for the experiment queue.
-- DEPENDS_ON lets a proposed experiment name the experiment that must run
-- first (ladder rungs), distinct from lineage: nothing is descended from a
-- dependency, it is merely ordered after it.
INSERT INTO atlas.vocab(domain, term, meaning) VALUES
 ('edge_relation','DEPENDS_ON','a proposed experiment that cannot start until another has run (ordering, not lineage)')
ON CONFLICT DO NOTHING;
