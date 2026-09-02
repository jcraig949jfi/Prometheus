-- V1: ontology v2 (failure-metabolization relations), mechanism governance
-- registry (append-only versioning), fixture namespace isolation, and
-- production views that exclude fixtures from scientific retrieval.

INSERT INTO ew.ontology_versions(version, description)
VALUES (2, 'V1: metabolization relations (FAILS_TO_REPLICATE, EXTENDS, TESTS, FALSIFIES); mechanism governance registry; fixture namespace')
ON CONFLICT DO NOTHING;

INSERT INTO ew.vocab(domain, term, ontology_version) VALUES
    ('relation_type', 'FAILS_TO_REPLICATE', 2),
    ('relation_type', 'EXTENDS', 2),
    ('relation_type', 'TESTS', 2),
    ('relation_type', 'FALSIFIES', 2)
ON CONFLICT DO NOTHING;

-- Mechanism governance: every mechanism is versioned, append-only. A
-- refinement inserts (term_id, version+1) and sets superseded_by on nothing;
-- the OLD row gains superseded_by via a NEW row? No -- rows are immutable:
-- supersession is recorded on the NEW row (supersedes column), and status
-- of the old version is derived (a term version is active iff no later
-- version supersedes it and deprecated=false).
CREATE TABLE IF NOT EXISTS ew.mechanism_registry (
    term_id            text NOT NULL,
    version            int  NOT NULL,
    dimension          text NOT NULL DEFAULT 'mechanism',
    label              text NOT NULL,
    definition         text NOT NULL,
    inclusion_criteria text,
    exclusion_criteria text,
    examples           text,          -- finding ids / short refs
    counterexamples    text,
    parent_term        text,
    supersedes         text,          -- 'term_id#vN' this version refines
    deprecated         boolean NOT NULL DEFAULT false,
    created_by         text NOT NULL,
    creation_method    text NOT NULL,
    ontology_version   int  NOT NULL,
    rationale          text,
    created_at         timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (term_id, version)
);

-- Fixture / namespace isolation (append-only classification, never deletion)
CREATE TABLE IF NOT EXISTS ew.object_namespace (
    object_type text NOT NULL,        -- claim|evidence|relation|packet|hypothesis
    object_id   text NOT NULL,
    namespace   text NOT NULL,        -- fixture|test|prod-exception
    reason      text NOT NULL,
    created_by  text NOT NULL,
    created_at  timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (object_type, object_id, namespace)
);

-- Production views: scientific retrieval, statistics, coordinates and wiki
-- default to these; raw tables remain for audit/explicit-fixture queries.
CREATE OR REPLACE VIEW ew.claims_prod AS
    SELECT c.* FROM ew.claims c WHERE NOT EXISTS (
        SELECT 1 FROM ew.object_namespace ns
        WHERE ns.object_type='claim' AND ns.object_id=c.claim_id
          AND ns.namespace IN ('fixture','test'));

CREATE OR REPLACE VIEW ew.evidence_prod AS
    SELECT e.* FROM ew.evidence e WHERE NOT EXISTS (
        SELECT 1 FROM ew.object_namespace ns
        WHERE ns.object_type='evidence' AND ns.object_id=e.evidence_id
          AND ns.namespace IN ('fixture','test'))
    AND (e.claim_id IS NULL OR EXISTS (
        SELECT 1 FROM ew.claims_prod cp WHERE cp.claim_id=e.claim_id));

CREATE OR REPLACE VIEW ew.relations_prod AS
    SELECT r.* FROM ew.relations r WHERE NOT EXISTS (
        SELECT 1 FROM ew.object_namespace ns
        WHERE ns.object_type='relation' AND ns.object_id=r.relation_id
          AND ns.namespace IN ('fixture','test'));

-- Mark the V0 smoke/demo fixtures (idempotent inserts by content pattern).
INSERT INTO ew.object_namespace(object_type, object_id, namespace, reason, created_by)
SELECT 'claim', claim_id, 'fixture',
       'V0 smoke test / distributed demo fixture', 'Mnemosyne'
FROM ew.claims
WHERE text_canonical LIKE 'FIXTURE:%' OR text_canonical LIKE 'Smoke-test claim:%'
ON CONFLICT DO NOTHING;

INSERT INTO ew.object_namespace(object_type, object_id, namespace, reason, created_by)
SELECT 'evidence', evidence_id, 'fixture',
       'V0 smoke test / distributed demo fixture', 'Mnemosyne'
FROM ew.evidence
WHERE source_quote IN ('idempotency probe quote',
                       'concurrent multi-writer probe quote')
   OR source_quote LIKE 'Ran sigma_kernel/demo_postgres.py end-to-end%'
   OR claim_id IN (SELECT claim_id FROM ew.claims
                   WHERE text_canonical LIKE 'FIXTURE:%'
                      OR text_canonical LIKE 'Smoke-test claim:%')
ON CONFLICT DO NOTHING;

INSERT INTO ew.object_namespace(object_type, object_id, namespace, reason, created_by)
SELECT 'relation', r.relation_id, 'fixture',
       'V0 distributed demo fixture relation', 'Mnemosyne'
FROM ew.relations r
WHERE r.src_id IN (SELECT object_id FROM ew.object_namespace
                   WHERE object_type='claim' AND namespace='fixture')
   OR r.dst_id IN (SELECT object_id FROM ew.object_namespace
                   WHERE object_type='claim' AND namespace='fixture')
ON CONFLICT DO NOTHING;
