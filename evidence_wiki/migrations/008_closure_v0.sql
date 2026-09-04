-- 008: PEW closure V0 (Mnemosyne, 2026-09-04)
--
-- (1) Server-attested producer/service identity on fossils, INDEPENDENT of the
--     self-declared X-Prometheus-Machine header and the shared bearer token.
--     The persisting Postgres cluster's system_identifier is non-spoofable
--     proof of WHICH store a row landed in -- the durable answer to section 3
--     ("host identity must not come from the token").
--
-- (2) Constraint-transfer + errata/supersession V0. A durable lesson that is
--     either HARD (a violation invalidates the experimental envelope) or
--     ADVISORY (a scoped empirical finding that must not prohibit exploration),
--     and can transition PROPOSED -> SUPPORTED -> NARROWED -> SUPERSEDED, or
--     -> REFUTED, without ever mutating history. Prometheus cannot accumulate
--     knowledge if it cannot also accumulate corrections to that knowledge.
--
-- Additive only: a nullable column and two new tables. No existing row is
-- rewritten; the client-facing fossil write contract (pew.fossil.v2) is
-- unchanged because attestation is server-stamped, never client-supplied.

ALTER TABLE ew.fossil_encounters ADD COLUMN IF NOT EXISTS attestation jsonb;
COMMENT ON COLUMN ew.fossil_encounters.attestation IS
 'Server-stamped at write time (NOT client-supplied): {db_system_id, source_commit, source_dirty, schema_version, ontology_version, fossil_contract, service_name, db_name, sfe_anchor_verified}. db_system_id is the persisting Postgres cluster system_identifier -- the non-spoofable answer to "which PEW host produced this row", independent of the bearer token and the self-declared machine header. sfe_anchor_verified=false records that PEW validated anchor CLASS/SHAPE only, never SFE ledger membership (it holds no SFE client by design), so the causal anchor is client-asserted.';

INSERT INTO ew.ontology_versions(version, description) VALUES
 (4, 'V4: server-attested fossil identity; constraint-transfer + errata/supersession (HARD|ADVISORY)')
ON CONFLICT DO NOTHING;

INSERT INTO ew.vocab(domain, term, ontology_version) VALUES
 ('constraint_kind','HARD',4),('constraint_kind','ADVISORY',4),
 ('constraint_status','PROPOSED',4),('constraint_status','SUPPORTED',4),
 ('constraint_status','NARROWED',4),('constraint_status','SUPERSEDED',4),
 ('constraint_status','REFUTED',4)
ON CONFLICT DO NOTHING;

-- A durable lesson. The row is IMMUTABLE; its lifecycle lives in
-- ew.constraint_events. HARD examples: content-identity mismatch, causal-anchor
-- mismatch, missing mandatory attestation, schema incompatibility, wrong
-- deployed service version. ADVISORY examples: "primitive showed no marginal
-- incrementality in world family W", "apparent effect vanished under seed
-- replication". Scope is MANDATORY: "R~=0 here" must never become "never test
-- this primitive again" -- scope is part of the evidence.
CREATE TABLE IF NOT EXISTS ew.constraints (
    constraint_id       text PRIMARY KEY,        -- K-<sha[:12]>
    kind                text NOT NULL,           -- HARD | ADVISORY
    title               text,
    statement           text,                    -- human surface (nullable for native)
    native_payload      jsonb,                   -- machine-checkable spec (HARD: predicate; ADVISORY: structured hint)
    scope               jsonb NOT NULL,          -- {world_family, primitive, mechanism, substrate, experiment_class, ...}
    severity            text,                    -- BLOCKER|HIGH|MEDIUM|LOW|INFO
    applicability       jsonb,                   -- predicate over an experiment descriptor: WHEN it fires
    source_evidence_ids text[],                  -- provenance
    source_claim_id     text,
    packet_id           text REFERENCES ew.source_packets(packet_id),
    reproducer          text,                    -- how to reproduce / adjudicate
    origin_ref          text,                    -- external anchor (file#id, commit, disposition record)
    supersedes          text,                    -- prior constraint_id this refines/replaces (chain; never overwrite)
    attestation         jsonb,                   -- server identity at write
    namespace           text NOT NULL DEFAULT 'prod',
    created_by          text NOT NULL,
    machine             text NOT NULL,
    created_at          timestamptz NOT NULL DEFAULT now(),
    revision            bigint NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_constraints_kind       ON ew.constraints(kind);
CREATE INDEX IF NOT EXISTS idx_constraints_supersedes ON ew.constraints(supersedes);
CREATE INDEX IF NOT EXISTS idx_constraints_ns         ON ew.constraints(namespace);

-- Append-only lifecycle. Current status = the latest event. A REFUTED or
-- SUPERSEDED constraint is therefore never "active" while its history stays
-- fully recoverable. This is the errata trail.
CREATE TABLE IF NOT EXISTS ew.constraint_events (
    event_id                 text PRIMARY KEY,   -- KE-<sha[:12]>
    constraint_id            text NOT NULL REFERENCES ew.constraints(constraint_id),
    seq                      bigserial,
    from_status              text,               -- nullable for the initial event
    to_status                text NOT NULL,      -- PROPOSED|SUPPORTED|NARROWED|SUPERSEDED|REFUTED
    adjudicating_evidence_id text,               -- the evidence that drove the transition
    adjudicating_packet_id   text,
    successor_constraint_id  text,               -- when NARROWED/SUPERSEDED points forward
    reproducer               text,
    rationale                text,
    attestation              jsonb,
    created_by               text NOT NULL,
    machine                  text NOT NULL,
    created_at               timestamptz NOT NULL DEFAULT now(),
    revision                 bigint NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_constraint_events_cid ON ew.constraint_events(constraint_id);

-- Current view: constraint + its latest lifecycle status + successor pointer.
CREATE OR REPLACE VIEW ew.constraints_current AS
 SELECT c.*,
        coalesce(e.to_status, 'PROPOSED') AS current_status,
        e.successor_constraint_id         AS current_successor,
        e.created_at                      AS status_since
   FROM ew.constraints c
   LEFT JOIN LATERAL (
        SELECT to_status, successor_constraint_id, created_at
          FROM ew.constraint_events ce
         WHERE ce.constraint_id = c.constraint_id
         ORDER BY ce.seq DESC LIMIT 1) e ON true;
