-- Atlas migration 004: vocabulary added by the Vivarium adapter.
INSERT INTO atlas.vocab(domain, term, meaning) VALUES
 ('edge_relation','EXECUTION_OF','an executor''s records that carry out another driver''s experiment (e.g. a Vivarium family executing an Archaeon experiment)'),
 ('edge_relation','SUPERSEDED_BY_WORK_IN','reserved: prose supersession that names no resolvable id')
ON CONFLICT DO NOTHING;
