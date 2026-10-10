-- Atlas migration 014 (2026-10-10, Atlas[m1-073da007]): vocabulary for the catch-up adapters
-- (atlas/harvest/workgraph.py, theseus.py, aether.py). Native words are added, not mapped onto near-synonyms.
INSERT INTO atlas.vocab(domain, term, meaning) VALUES
 ('edge_relation','EVALUATES','an evaluation experiment reads the outputs of the destination run (it does not descend from it)'),
 ('fact_kind','executed_check','a command the executor states it ran, with the result it states (workgraph receipt evidence_executed)'),
 ('fact_kind','known_escape','a limit the executor declares on its own evidence (workgraph receipt known_escapes)')
ON CONFLICT DO NOTHING;
