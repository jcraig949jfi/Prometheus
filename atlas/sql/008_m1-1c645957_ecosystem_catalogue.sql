-- Atlas migration 008 (claimed in comms #517, 2026-09-19): catalogue of
-- world x organism x pressure ECOSYSTEMS -- external ALife / open-endedness
-- systems (POET, Avida, Lenia, ...) beside Prometheus's own engines, so one
-- classification matrix covers both. Operator request verbatim:
-- roles/Atlas/prompts/2026-09-19_alife_survey/. Pointers, not copies: a
-- record names papers and repositories; nothing is downloaded.
-- Source of truth: roles/Atlas/catalog/ECOSYSTEMS.jsonl (harvester 'catalog').

CREATE TABLE IF NOT EXISTS atlas.ecosystem (
    ecosystem_id     text PRIMARY KEY,            -- kebab slug: poet, avida, lenia; prometheus ones: prometheus-sfe ...
    origin           text NOT NULL,               -- external | prometheus
    name             text NOT NULL,
    aliases          text[] NOT NULL DEFAULT '{}',
    cluster          text,                        -- survey cluster label
    year_first       integer,
    people           text[] NOT NULL DEFAULT '{}',
    institution      text,
    motivation       text[] NOT NULL DEFAULT '{}',
    world_kind       text,                        -- controlled-ish vocabulary, see catalog/SCHEMA.md
    world_notes      text,
    organism_repr    text,
    organism_development boolean,
    organism_notes   text,
    pressure_kinds   text[] NOT NULL DEFAULT '{}',
    pressure_notes   text,
    search           text,
    environment_generation text,
    language         text,
    accelerator      text,
    scale_note       text,
    key_claims       text[] NOT NULL DEFAULT '{}',
    oee_evidence     text,                        -- open-endedness evidence as claimed
    runnable_today   text,
    status           text,
    prometheus_analogue text,
    internal_coverage text,                       -- where Prometheus already holds it (paths), if anywhere
    verification     text,                        -- summary: how many links VERIFIED
    notes            text,
    record           jsonb NOT NULL DEFAULT '{}'::jsonb,   -- the full catalogue line, verbatim
    first_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id),
    last_harvest_id  bigint REFERENCES atlas.harvest_run(harvest_id)
);
CREATE INDEX IF NOT EXISTS ecosystem_axes_idx ON atlas.ecosystem(world_kind, organism_repr);

CREATE TABLE IF NOT EXISTS atlas.ecosystem_reference (
    ref_uri          text NOT NULL,               -- the URL, or doi:<doi> / arxiv:<id> when no URL
    ecosystem_id     text NOT NULL REFERENCES atlas.ecosystem(ecosystem_id) ON DELETE CASCADE,
    kind             text NOT NULL,               -- paper | code | website | demo | dataset | video | docs | list
    title            text,
    year             integer,
    venue            text,
    doi              text,
    arxiv            text,
    license          text,
    language         text,
    last_activity_year integer,
    official         boolean,
    url_status       text,                        -- VERIFIED | SEARCH_RESULT | UNVERIFIED (as recorded by the surveyor)
    last_harvest_id  bigint REFERENCES atlas.harvest_run(harvest_id),
    PRIMARY KEY (ref_uri, ecosystem_id)
);

INSERT INTO atlas.vocab(domain, term, meaning) VALUES
 ('edge_relation','RELATED_TO','catalogue: a declared relative (variant, parent, reimplementation) of another ecosystem'),
 ('edge_relation','ANALOGUE_OF','ATLAS_DERIVED: an external ecosystem sharing world/organism/pressure axes with a Prometheus engine or experiment')
ON CONFLICT DO NOTHING;
