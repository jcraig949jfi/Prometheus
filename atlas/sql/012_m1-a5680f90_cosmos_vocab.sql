-- Atlas migration 012: vocabulary added by the Cosmos adapter (atlas/harvest/cosmos.py, ATLAS-37).
-- Cosmos's export uses these words natively; they are added, not mapped onto near-synonyms.
INSERT INTO atlas.vocab(domain, term, meaning) VALUES
 ('fact_kind','phenomenon_verdict','an engine''s verdict on whether a declared phenomenon pays in one world (Cosmos SELECTIVE_PAYS.v1: PAYS/QUIET with margin and +/-2 SE band)'),
 ('fact_kind','candidate_law','a mined candidate law and its lifecycle events; FAILED laws are kept as falsifications'),
 ('edge_relation','CONTROL_OF','the source world is a declared control (e.g. sham) for the destination world'),
 ('edge_relation','COORD_PRESERVING','the source world is a coordinate-preserving transform of the destination world (Cosmos CWE kind)')
ON CONFLICT DO NOTHING;
