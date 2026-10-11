-- Moonshot native-execution schema, version 1 (C-012, OP-NF2). Interface: moonshot/nf/INTERFACE_CONTRACT.md.
-- {schema} is substituted by moonshot.nf.pg.init_schema, which runs this file AS the owner role {schema}_owner
-- and then applies the grants (PUBLIC gets nothing; each functional role exactly its function).
-- Every invariant that matters is enforced HERE, not in a client: content addresses, one live publication per
-- lineage position, one open contest per chain, guarded head moves, append-only evidence.

CREATE TABLE IF NOT EXISTS {schema}.meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
INSERT INTO {schema}.meta (key, value) VALUES ('schema_version', '1') ON CONFLICT (key) DO NOTHING;

-- Immutable content-addressed objects: the database checks every address.
CREATE TABLE IF NOT EXISTS {schema}.objects (
    sha256      TEXT PRIMARY KEY,
    size_bytes  BIGINT NOT NULL,
    content     BYTEA NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT objects_address CHECK (sha256 = encode(sha256(content), 'hex')),
    CONSTRAINT objects_size CHECK (size_bytes = octet_length(content))
);

-- One row per chain; generation +1 on EVERY head move (advance or rewind), so no (parent, generation) pair can be
-- satisfied twice.
CREATE TABLE IF NOT EXISTS {schema}.chains (
    chain_id                  TEXT PRIMARY KEY CHECK (chain_id ~ '^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$'),
    namespace                 TEXT NOT NULL,
    genesis_sha256            TEXT NOT NULL REFERENCES {schema}.objects(sha256),
    initial_checkpoint_sha256 TEXT NOT NULL REFERENCES {schema}.objects(sha256),
    runtime                   JSONB NOT NULL,
    approved_code_sha         TEXT NOT NULL CHECK (approved_code_sha ~ '^[0-9a-f]{40}$'),
    epochs_target             INT NOT NULL CHECK (epochs_target >= 1),
    head_index                INT NOT NULL DEFAULT 0,
    head_epoch_digest         TEXT,
    head_checkpoint_sha256    TEXT NOT NULL,
    generation                BIGINT NOT NULL DEFAULT 0,
    state                     TEXT NOT NULL DEFAULT 'OPEN' CHECK (state IN ('OPEN', 'HALTED', 'COMPLETE')),
    created_by                TEXT NOT NULL,
    created_at                TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at                TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chains_head_shape CHECK ((head_index = 0) = (head_epoch_digest IS NULL)),
    CONSTRAINT chains_head_range CHECK (head_index BETWEEN 0 AND epochs_target)
);

-- Every DISTINCT result ever seen for a work identity: disagreements are preserved, never overwritten.
CREATE TABLE IF NOT EXISTS {schema}.results (
    work_id                  TEXT NOT NULL,
    epoch_digest             TEXT NOT NULL,
    chain_id                 TEXT NOT NULL REFERENCES {schema}.chains(chain_id),
    epoch_index              INT NOT NULL CHECK (epoch_index >= 1),
    input_checkpoint_sha256  TEXT NOT NULL,
    manifest_sha256          TEXT NOT NULL REFERENCES {schema}.objects(sha256),
    spec_sha256              TEXT NOT NULL REFERENCES {schema}.objects(sha256),
    trace_sha256             TEXT NOT NULL REFERENCES {schema}.objects(sha256),
    output_checkpoint_sha256 TEXT NOT NULL REFERENCES {schema}.objects(sha256),
    first_attempt_id         TEXT NOT NULL,
    first_seen_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (work_id, epoch_digest)
);
CREATE INDEX IF NOT EXISTS results_chain ON {schema}.results (chain_id, epoch_index);

-- The lineage: one row per head advance. Rejected rows stay as evidence.
CREATE TABLE IF NOT EXISTS {schema}.publications (
    publication_id      BIGSERIAL PRIMARY KEY,
    chain_id            TEXT NOT NULL REFERENCES {schema}.chains(chain_id),
    epoch_index         INT NOT NULL CHECK (epoch_index >= 1),
    work_id             TEXT NOT NULL,
    epoch_digest        TEXT NOT NULL,
    parent_epoch_digest TEXT,
    generation          BIGINT NOT NULL,
    attempt_id          TEXT NOT NULL,
    published_by        TEXT NOT NULL,
    published_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    rejected_at         TIMESTAMPTZ,
    rejected_by         TEXT,
    rejected_contest    BIGINT,
    FOREIGN KEY (work_id, epoch_digest) REFERENCES {schema}.results(work_id, epoch_digest),
    UNIQUE (chain_id, generation)
);
-- Exactly ONE live published successor per lineage position, enforced by the database.
CREATE UNIQUE INDEX IF NOT EXISTS publications_one_live ON {schema}.publications (chain_id, epoch_index)
    WHERE rejected_at IS NULL;

-- One classification per Fabric attempt: the idempotency key of publication, and durable accounting kept OUTSIDE
-- the canonical trace.
CREATE TABLE IF NOT EXISTS {schema}.attempts (
    attempt_id             TEXT PRIMARY KEY,
    task_id                TEXT NOT NULL,
    chain_id               TEXT NOT NULL REFERENCES {schema}.chains(chain_id),
    epoch_index            INT NOT NULL,
    expected_parent_digest TEXT,
    expected_generation    BIGINT NOT NULL,
    work_id                TEXT,
    epoch_digest           TEXT,
    outcome                TEXT NOT NULL CHECK (outcome IN ('PUBLISHED', 'DUPLICATE', 'DISAGREEMENT', 'STALE', 'INVALID',
                                                            'REFUSED_UNAPPROVED', 'HALTED')),
    publication_id         BIGINT REFERENCES {schema}.publications(publication_id),
    contest_id             BIGINT,
    detail                 JSONB NOT NULL DEFAULT '{}',
    classified_by          TEXT NOT NULL,
    classified_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS attempts_chain ON {schema}.attempts (chain_id, epoch_index);

CREATE TABLE IF NOT EXISTS {schema}.contests (
    contest_id              BIGSERIAL PRIMARY KEY,
    chain_id                TEXT NOT NULL REFERENCES {schema}.chains(chain_id),
    epoch_index             INT NOT NULL,
    work_id                 TEXT NOT NULL,
    published_epoch_digest  TEXT NOT NULL,
    challenger_epoch_digest TEXT,
    reason                  TEXT NOT NULL CHECK (reason IN ('DISAGREEMENT', 'AUDIT_MISMATCH', 'CORRUPT_BYTES')),
    state                   TEXT NOT NULL CHECK (state IN ('CONTESTED', 'TAINTED', 'UNRESOLVED', 'RESOLVED_UPHELD',
                                                          'RESOLVED_OVERTURNED')),
    opened_by               TEXT NOT NULL,
    opened_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_by             TEXT,
    resolved_at             TIMESTAMPTZ,
    replay_digests          TEXT[],
    detail                  JSONB NOT NULL DEFAULT '{}'
);
CREATE UNIQUE INDEX IF NOT EXISTS contests_one_open ON {schema}.contests (chain_id)
    WHERE state IN ('CONTESTED', 'TAINTED', 'UNRESOLVED');

CREATE TABLE IF NOT EXISTS {schema}.validations (
    validation_id   BIGSERIAL PRIMARY KEY,
    publication_id  BIGINT NOT NULL REFERENCES {schema}.publications(publication_id),
    chain_id        TEXT NOT NULL,
    epoch_index     INT NOT NULL,
    epoch_digest    TEXT NOT NULL,
    state           TEXT NOT NULL CHECK (state IN ('VALIDATED', 'INVALID', 'MISMATCH')),
    checks          TEXT[] NOT NULL,
    replay_digest   TEXT,
    replay_host     TEXT,
    validator       TEXT NOT NULL,
    validated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS {schema}.events (
    event_id   BIGSERIAL PRIMARY KEY,
    at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    actor      TEXT NOT NULL,
    kind       TEXT NOT NULL,
    chain_id   TEXT,
    attempt_id TEXT,
    detail     JSONB NOT NULL DEFAULT '{}'
);

-- ---------------------------------------------------------------------------------------------- append-only guards

CREATE OR REPLACE FUNCTION {schema}.forbid_change() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'moonshot: % on %.% is forbidden (append-only evidence)', TG_OP, TG_TABLE_SCHEMA, TG_TABLE_NAME;
END $$;

CREATE OR REPLACE TRIGGER objects_append_only BEFORE UPDATE OR DELETE ON {schema}.objects
    FOR EACH ROW EXECUTE FUNCTION {schema}.forbid_change();
CREATE OR REPLACE TRIGGER results_append_only BEFORE UPDATE OR DELETE ON {schema}.results
    FOR EACH ROW EXECUTE FUNCTION {schema}.forbid_change();
CREATE OR REPLACE TRIGGER attempts_append_only BEFORE UPDATE OR DELETE ON {schema}.attempts
    FOR EACH ROW EXECUTE FUNCTION {schema}.forbid_change();
CREATE OR REPLACE TRIGGER validations_append_only BEFORE UPDATE OR DELETE ON {schema}.validations
    FOR EACH ROW EXECUTE FUNCTION {schema}.forbid_change();
CREATE OR REPLACE TRIGGER events_append_only BEFORE UPDATE OR DELETE ON {schema}.events
    FOR EACH ROW EXECUTE FUNCTION {schema}.forbid_change();
CREATE OR REPLACE TRIGGER objects_no_truncate BEFORE TRUNCATE ON {schema}.objects
    FOR EACH STATEMENT EXECUTE FUNCTION {schema}.forbid_change();
CREATE OR REPLACE TRIGGER results_no_truncate BEFORE TRUNCATE ON {schema}.results
    FOR EACH STATEMENT EXECUTE FUNCTION {schema}.forbid_change();
CREATE OR REPLACE TRIGGER publications_no_truncate BEFORE TRUNCATE ON {schema}.publications
    FOR EACH STATEMENT EXECUTE FUNCTION {schema}.forbid_change();
CREATE OR REPLACE TRIGGER attempts_no_truncate BEFORE TRUNCATE ON {schema}.attempts
    FOR EACH STATEMENT EXECUTE FUNCTION {schema}.forbid_change();
CREATE OR REPLACE TRIGGER chains_no_truncate BEFORE TRUNCATE ON {schema}.chains
    FOR EACH STATEMENT EXECUTE FUNCTION {schema}.forbid_change();
CREATE OR REPLACE TRIGGER contests_no_truncate BEFORE TRUNCATE ON {schema}.contests
    FOR EACH STATEMENT EXECUTE FUNCTION {schema}.forbid_change();
CREATE OR REPLACE TRIGGER validations_no_truncate BEFORE TRUNCATE ON {schema}.validations
    FOR EACH STATEMENT EXECUTE FUNCTION {schema}.forbid_change();
CREATE OR REPLACE TRIGGER events_no_truncate BEFORE TRUNCATE ON {schema}.events
    FOR EACH STATEMENT EXECUTE FUNCTION {schema}.forbid_change();

-- A chain's identity is fixed at creation (its genesis bytes say the same); its generation never decreases, and
-- every head move -- advance or rewind -- raises it, which is what makes the (parent, generation) guard sound.
CREATE OR REPLACE FUNCTION {schema}.chain_guard() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'moonshot: chains are never deleted';
    END IF;
    IF (NEW.chain_id, NEW.namespace, NEW.genesis_sha256, NEW.initial_checkpoint_sha256, NEW.runtime,
        NEW.approved_code_sha, NEW.epochs_target, NEW.created_by, NEW.created_at)
       IS DISTINCT FROM
       (OLD.chain_id, OLD.namespace, OLD.genesis_sha256, OLD.initial_checkpoint_sha256, OLD.runtime,
        OLD.approved_code_sha, OLD.epochs_target, OLD.created_by, OLD.created_at) THEN
        RAISE EXCEPTION 'moonshot: a chain''s identity is immutable';
    END IF;
    IF NEW.generation < OLD.generation THEN
        RAISE EXCEPTION 'moonshot: a chain''s generation never decreases';
    END IF;
    IF (NEW.head_index, NEW.head_epoch_digest, NEW.head_checkpoint_sha256)
       IS DISTINCT FROM (OLD.head_index, OLD.head_epoch_digest, OLD.head_checkpoint_sha256)
       AND NEW.generation <= OLD.generation THEN
        RAISE EXCEPTION 'moonshot: a head move must advance the generation';
    END IF;
    RETURN NEW;
END $$;
CREATE OR REPLACE TRIGGER chains_guarded BEFORE UPDATE OR DELETE ON {schema}.chains
    FOR EACH ROW EXECUTE FUNCTION {schema}.chain_guard();

-- A contest's grounds never change; only its resolution moves, and a resolution (upheld/overturned) is final.
CREATE OR REPLACE FUNCTION {schema}.contest_guard() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'moonshot: contests are never deleted';
    END IF;
    IF (NEW.contest_id, NEW.chain_id, NEW.epoch_index, NEW.work_id, NEW.published_epoch_digest,
        NEW.challenger_epoch_digest, NEW.reason, NEW.opened_by, NEW.opened_at, NEW.detail)
       IS DISTINCT FROM
       (OLD.contest_id, OLD.chain_id, OLD.epoch_index, OLD.work_id, OLD.published_epoch_digest,
        OLD.challenger_epoch_digest, OLD.reason, OLD.opened_by, OLD.opened_at, OLD.detail) THEN
        RAISE EXCEPTION 'moonshot: a contest''s grounds are immutable';
    END IF;
    IF OLD.state IN ('RESOLVED_UPHELD', 'RESOLVED_OVERTURNED') THEN
        RAISE EXCEPTION 'moonshot: a resolved contest stays resolved';
    END IF;
    RETURN NEW;
END $$;
CREATE OR REPLACE TRIGGER contests_guarded BEFORE UPDATE OR DELETE ON {schema}.contests
    FOR EACH ROW EXECUTE FUNCTION {schema}.contest_guard();

-- A publication's content never changes; it may be marked rejected exactly once (by a resolution).
CREATE OR REPLACE FUNCTION {schema}.publication_guard() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'moonshot: publications are never deleted';
    END IF;
    IF (NEW.publication_id, NEW.chain_id, NEW.epoch_index, NEW.work_id, NEW.epoch_digest, NEW.parent_epoch_digest,
        NEW.generation, NEW.attempt_id, NEW.published_by, NEW.published_at)
       IS DISTINCT FROM
       (OLD.publication_id, OLD.chain_id, OLD.epoch_index, OLD.work_id, OLD.epoch_digest, OLD.parent_epoch_digest,
        OLD.generation, OLD.attempt_id, OLD.published_by, OLD.published_at) THEN
        RAISE EXCEPTION 'moonshot: a publication''s content is immutable';
    END IF;
    IF OLD.rejected_at IS NOT NULL THEN
        RAISE EXCEPTION 'moonshot: a rejected publication stays rejected';
    END IF;
    RETURN NEW;
END $$;
CREATE OR REPLACE TRIGGER publications_guarded BEFORE UPDATE OR DELETE ON {schema}.publications
    FOR EACH ROW EXECUTE FUNCTION {schema}.publication_guard();

-- ---------------------------------------------------------------------------------------------- functions

CREATE OR REPLACE FUNCTION {schema}.put_object(p_content BYTEA) RETURNS TEXT
LANGUAGE plpgsql SECURITY DEFINER SET search_path = {schema}, pg_temp AS $$
DECLARE
    h TEXT := encode(sha256(p_content), 'hex');
BEGIN
    INSERT INTO objects (sha256, size_bytes, content) VALUES (h, octet_length(p_content), p_content)
        ON CONFLICT (sha256) DO NOTHING;
    RETURN h;
END $$;

CREATE OR REPLACE FUNCTION {schema}.create_chain(p_chain_id TEXT, p_namespace TEXT, p_genesis BYTEA, p_initial BYTEA,
                                                 p_runtime JSONB, p_approved_code_sha TEXT, p_epochs INT, p_actor TEXT)
RETURNS TEXT LANGUAGE plpgsql SECURITY DEFINER SET search_path = {schema}, pg_temp AS $$
DECLARE
    g TEXT; i TEXT; gj JSONB;
BEGIN
    g := put_object(p_genesis);
    i := put_object(p_initial);
    gj := convert_from(p_genesis, 'UTF8')::jsonb;
    IF gj->>'chain_id' IS DISTINCT FROM p_chain_id OR (gj->>'epochs')::int IS DISTINCT FROM p_epochs
       OR gj->>'initial_checkpoint_sha256' IS DISTINCT FROM i OR gj->>'approved_code_sha' IS DISTINCT FROM p_approved_code_sha
       OR gj->'runtime' IS DISTINCT FROM p_runtime THEN
        RAISE EXCEPTION 'moonshot: the genesis bytes do not describe this chain row';
    END IF;
    INSERT INTO chains (chain_id, namespace, genesis_sha256, initial_checkpoint_sha256, runtime, approved_code_sha,
                        epochs_target, head_checkpoint_sha256, created_by)
    VALUES (p_chain_id, p_namespace, g, i, p_runtime, p_approved_code_sha, p_epochs, i, p_actor);
    INSERT INTO events (actor, kind, chain_id, detail)
    VALUES (p_actor, 'chain_created', p_chain_id, jsonb_build_object('genesis_sha256', g, 'namespace', p_namespace));
    RETURN g;
END $$;

-- The guarded publication. One transaction; the chain row lock serializes publishers of a chain.
CREATE OR REPLACE FUNCTION {schema}.publish(
    p_attempt_id TEXT, p_task_id TEXT, p_chain_id TEXT, p_epoch_index INT,
    p_expected_parent TEXT, p_expected_generation BIGINT,
    p_manifest BYTEA, p_spec BYTEA, p_trace BYTEA, p_checkpoint BYTEA,
    p_detail JSONB, p_actor TEXT)
RETURNS TABLE (outcome TEXT, publication_id BIGINT, contest_id BIGINT, generation BIGINT, replayed BOOLEAN)
LANGUAGE plpgsql SECURITY DEFINER SET search_path = {schema}, pg_temp AS $$
#variable_conflict use_column
DECLARE
    c        chains%ROWTYPE;
    a        attempts%ROWTYPE;
    live     publications%ROWTYPE;
    m        JSONB;
    h_man    TEXT; h_spec TEXT; h_trace TEXT; h_ckpt TEXT;
    v_work   TEXT; v_digest TEXT; v_input TEXT;
    v_out    TEXT; v_pub BIGINT; v_contest BIGINT; v_gen BIGINT;
    errs     TEXT[] := '{}';
BEGIN
    SELECT * INTO c FROM chains WHERE chains.chain_id = p_chain_id FOR UPDATE;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'moonshot: no chain %', p_chain_id;
    END IF;
    -- An attempt is classified exactly once: a retry (lost acknowledgement) gets the recorded answer.
    SELECT * INTO a FROM attempts WHERE attempts.attempt_id = p_attempt_id;
    IF FOUND THEN
        RETURN QUERY SELECT a.outcome, a.publication_id, a.contest_id, c.generation, TRUE;
        RETURN;
    END IF;
    h_man := put_object(p_manifest);
    h_spec := put_object(p_spec);
    h_trace := put_object(p_trace);
    h_ckpt := put_object(p_checkpoint);
    -- The manifest must name exactly these bytes and this position.
    BEGIN
        m := convert_from(p_manifest, 'UTF8')::jsonb;
        v_work := m->>'work_id';
        v_digest := m->>'epoch_digest';
        v_input := m->>'input_checkpoint_sha256';
        IF m->>'spec_sha256' IS DISTINCT FROM h_spec THEN errs := errs || 'spec_sha256'::text; END IF;
        IF m->>'trace_sha256' IS DISTINCT FROM h_trace THEN errs := errs || 'trace_sha256'::text; END IF;
        IF m->>'output_checkpoint_sha256' IS DISTINCT FROM h_ckpt THEN errs := errs || 'output_checkpoint_sha256'::text; END IF;
        IF (m->>'trace_bytes')::bigint IS DISTINCT FROM octet_length(p_trace) THEN errs := errs || 'trace_bytes'::text; END IF;
        IF (m->>'output_checkpoint_bytes')::bigint IS DISTINCT FROM octet_length(p_checkpoint) THEN
            errs := errs || 'output_checkpoint_bytes'::text;
        END IF;
        IF (m->>'epoch_index')::int IS DISTINCT FROM p_epoch_index OR m->>'chain_id' IS DISTINCT FROM p_chain_id THEN
            errs := errs || 'position'::text;
        END IF;
        IF v_work IS NULL OR v_digest IS NULL OR v_input IS NULL THEN errs := errs || 'identity fields'::text; END IF;
    EXCEPTION WHEN others THEN
        errs := errs || ('manifest unreadable: ' || SQLERRM);
    END;
    IF cardinality(errs) > 0 THEN
        INSERT INTO attempts (attempt_id, task_id, chain_id, epoch_index, expected_parent_digest, expected_generation,
                              work_id, epoch_digest, outcome, detail, classified_by)
        VALUES (p_attempt_id, p_task_id, p_chain_id, p_epoch_index, p_expected_parent, p_expected_generation,
                v_work, v_digest, 'INVALID', coalesce(p_detail, '{}'::jsonb) || jsonb_build_object('errors', to_jsonb(errs)),
                p_actor);
        INSERT INTO events (actor, kind, chain_id, attempt_id, detail)
        VALUES (p_actor, 'invalid', p_chain_id, p_attempt_id, jsonb_build_object('errors', to_jsonb(errs)));
        RETURN QUERY SELECT 'INVALID'::text, NULL::bigint, NULL::bigint, c.generation, FALSE;
        RETURN;
    END IF;
    -- Every distinct result is preserved, whatever happens next.
    INSERT INTO results (work_id, epoch_digest, chain_id, epoch_index, input_checkpoint_sha256, manifest_sha256,
                         spec_sha256, trace_sha256, output_checkpoint_sha256, first_attempt_id)
    VALUES (v_work, v_digest, p_chain_id, p_epoch_index, v_input, h_man, h_spec, h_trace, h_ckpt, p_attempt_id)
    ON CONFLICT (work_id, epoch_digest) DO NOTHING;
    v_gen := c.generation;
    IF c.state = 'HALTED' THEN
        v_out := 'HALTED';
    ELSIF c.state = 'OPEN' AND c.generation = p_expected_generation AND c.head_index = p_epoch_index - 1
          AND c.head_epoch_digest IS NOT DISTINCT FROM p_expected_parent AND c.head_checkpoint_sha256 = v_input THEN
        v_gen := c.generation + 1;
        INSERT INTO publications (chain_id, epoch_index, work_id, epoch_digest, parent_epoch_digest, generation,
                                  attempt_id, published_by)
        VALUES (p_chain_id, p_epoch_index, v_work, v_digest, p_expected_parent, v_gen, p_attempt_id, p_actor)
        RETURNING publications.publication_id INTO v_pub;
        UPDATE chains SET head_index = p_epoch_index, head_epoch_digest = v_digest, head_checkpoint_sha256 = h_ckpt,
                          generation = v_gen,
                          state = CASE WHEN p_epoch_index = c.epochs_target THEN 'COMPLETE' ELSE 'OPEN' END,
                          updated_at = now()
        WHERE chains.chain_id = p_chain_id;
        v_out := 'PUBLISHED';
    ELSE
        SELECT * INTO live FROM publications p
        WHERE p.chain_id = p_chain_id AND p.epoch_index = p_epoch_index AND p.rejected_at IS NULL;
        IF FOUND AND live.work_id = v_work THEN
            v_pub := live.publication_id;
            IF live.epoch_digest = v_digest THEN
                v_out := 'DUPLICATE';
            ELSE
                INSERT INTO contests (chain_id, epoch_index, work_id, published_epoch_digest, challenger_epoch_digest,
                                      reason, state, opened_by, detail)
                VALUES (p_chain_id, p_epoch_index, v_work, live.epoch_digest, v_digest, 'DISAGREEMENT',
                        CASE WHEN c.head_index > p_epoch_index THEN 'TAINTED' ELSE 'CONTESTED' END, p_actor,
                        jsonb_build_object('challenger_attempt', p_attempt_id, 'head_index_at_detection', c.head_index))
                RETURNING contests.contest_id INTO v_contest;
                UPDATE chains SET state = 'HALTED', updated_at = now() WHERE chains.chain_id = p_chain_id;
                v_out := 'DISAGREEMENT';
            END IF;
        ELSE
            v_out := 'STALE';
        END IF;
    END IF;
    INSERT INTO attempts (attempt_id, task_id, chain_id, epoch_index, expected_parent_digest, expected_generation,
                          work_id, epoch_digest, outcome, publication_id, contest_id, detail, classified_by)
    VALUES (p_attempt_id, p_task_id, p_chain_id, p_epoch_index, p_expected_parent, p_expected_generation,
            v_work, v_digest, v_out, v_pub, v_contest, coalesce(p_detail, '{}'::jsonb), p_actor);
    INSERT INTO events (actor, kind, chain_id, attempt_id, detail)
    VALUES (p_actor, lower(v_out), p_chain_id, p_attempt_id,
            jsonb_build_object('epoch_index', p_epoch_index, 'epoch_digest', v_digest, 'generation', v_gen));
    RETURN QUERY SELECT v_out, v_pub, v_contest, v_gen, FALSE;
END $$;

-- A durable receipt (C-012-T003): canonical bytes stored content-addressed, and an append-only event naming them
-- with the head they describe.
CREATE OR REPLACE FUNCTION {schema}.record_receipt(p_chain_id TEXT, p_receipt BYTEA, p_actor TEXT) RETURNS TEXT
LANGUAGE plpgsql SECURITY DEFINER SET search_path = {schema}, pg_temp AS $$
DECLARE
    c chains%ROWTYPE;
    h TEXT;
BEGIN
    SELECT * INTO c FROM chains WHERE chains.chain_id = p_chain_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'moonshot: no chain %', p_chain_id;
    END IF;
    h := put_object(p_receipt);
    INSERT INTO events (actor, kind, chain_id, detail)
    VALUES (p_actor, 'receipt', p_chain_id, jsonb_build_object('sha256', h, 'head_index', c.head_index,
                                                               'generation', c.generation, 'state', c.state));
    RETURN h;
END $$;

-- A materializer run's report (C-012-T005): the per-table row-count oracle, logged in Moonshot's own records.
CREATE OR REPLACE FUNCTION {schema}.record_materialization(p_report JSONB, p_actor TEXT) RETURNS BIGINT
LANGUAGE plpgsql SECURITY DEFINER SET search_path = {schema}, pg_temp AS $$
DECLARE
    eid BIGINT;
BEGIN
    INSERT INTO events (actor, kind, detail) VALUES (p_actor, 'materialization', p_report)
    RETURNING events.event_id INTO eid;
    RETURN eid;
END $$;

-- The catalogue Pan's refresh pulls into pan.artifact (contract s6): one row per LIVE published epoch.
CREATE OR REPLACE VIEW {schema}.catalog_v AS
SELECT r.manifest_sha256 AS object_sha256,
       'moonshot.epoch'::text AS kind,
       p.chain_id || ' epoch ' || p.epoch_index AS title,
       'Moonshot chain ' || p.chain_id || ' (' || c.namespace || '), epoch ' || p.epoch_index || ' of '
           || c.epochs_target || ', generation ' || p.generation || ', epoch digest ' || p.epoch_digest AS summary,
       p.published_at,
       '{schema}:' || p.chain_id || '/' || p.epoch_index AS ref
FROM {schema}.publications p
JOIN {schema}.results r ON r.work_id = p.work_id AND r.epoch_digest = p.epoch_digest
JOIN {schema}.chains c ON c.chain_id = p.chain_id
WHERE p.rejected_at IS NULL;

-- INVALID (failed the publisher's semantic checks) or REFUSED_UNAPPROVED (code not approved): recorded, never
-- published. Idempotent per attempt.
CREATE OR REPLACE FUNCTION {schema}.record_attempt_outcome(
    p_attempt_id TEXT, p_task_id TEXT, p_chain_id TEXT, p_epoch_index INT, p_expected_parent TEXT,
    p_expected_generation BIGINT, p_outcome TEXT, p_work_id TEXT, p_epoch_digest TEXT, p_detail JSONB, p_actor TEXT)
RETURNS TABLE (outcome TEXT, replayed BOOLEAN)
LANGUAGE plpgsql SECURITY DEFINER SET search_path = {schema}, pg_temp AS $$
#variable_conflict use_column
DECLARE
    a attempts%ROWTYPE;
BEGIN
    IF p_outcome NOT IN ('INVALID', 'REFUSED_UNAPPROVED') THEN
        RAISE EXCEPTION 'moonshot: record_attempt_outcome takes INVALID or REFUSED_UNAPPROVED, not %', p_outcome;
    END IF;
    PERFORM 1 FROM chains WHERE chains.chain_id = p_chain_id FOR UPDATE;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'moonshot: no chain %', p_chain_id;
    END IF;
    SELECT * INTO a FROM attempts WHERE attempts.attempt_id = p_attempt_id;
    IF FOUND THEN
        RETURN QUERY SELECT a.outcome, TRUE;
        RETURN;
    END IF;
    INSERT INTO attempts (attempt_id, task_id, chain_id, epoch_index, expected_parent_digest, expected_generation,
                          work_id, epoch_digest, outcome, detail, classified_by)
    VALUES (p_attempt_id, p_task_id, p_chain_id, p_epoch_index, p_expected_parent, p_expected_generation,
            p_work_id, p_epoch_digest, p_outcome, coalesce(p_detail, '{}'::jsonb), p_actor);
    INSERT INTO events (actor, kind, chain_id, attempt_id, detail)
    VALUES (p_actor, lower(p_outcome), p_chain_id, p_attempt_id, coalesce(p_detail, '{}'::jsonb));
    RETURN QUERY SELECT p_outcome, FALSE;
END $$;

-- Validation is a separate axis. MISMATCH (a replay disagrees) or INVALID (the published bytes do not verify)
-- opens a contest and halts the chain: fail closed. A validation names the digest it examined: one about a digest
-- that is no longer live (overturned and re-published meanwhile) is stale and refused, never re-attributed.
CREATE OR REPLACE FUNCTION {schema}.record_validation(p_chain_id TEXT, p_epoch_index INT, p_epoch_digest TEXT,
                                                      p_state TEXT, p_checks TEXT[], p_replay_digest TEXT,
                                                      p_replay_host TEXT, p_validator TEXT)
RETURNS BIGINT LANGUAGE plpgsql SECURITY DEFINER SET search_path = {schema}, pg_temp AS $$
DECLARE
    c    chains%ROWTYPE;
    live publications%ROWTYPE;
    vid  BIGINT;
BEGIN
    SELECT * INTO c FROM chains WHERE chains.chain_id = p_chain_id FOR UPDATE;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'moonshot: no chain %', p_chain_id;
    END IF;
    SELECT * INTO live FROM publications p
    WHERE p.chain_id = p_chain_id AND p.epoch_index = p_epoch_index AND p.rejected_at IS NULL;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'moonshot: epoch % of % is not published', p_epoch_index, p_chain_id;
    END IF;
    IF live.epoch_digest IS DISTINCT FROM p_epoch_digest THEN
        RAISE EXCEPTION 'moonshot: stale validation: epoch % of % is now %, not %', p_epoch_index, p_chain_id,
            live.epoch_digest, p_epoch_digest;
    END IF;
    IF 'REPLAY' = ANY(p_checks) AND p_replay_digest IS NULL THEN
        RAISE EXCEPTION 'moonshot: a REPLAY check needs its replay digest';
    END IF;
    IF p_state = 'VALIDATED' AND p_replay_digest IS DISTINCT FROM p_epoch_digest AND p_replay_digest IS NOT NULL THEN
        RAISE EXCEPTION 'moonshot: a replay that disagrees is a MISMATCH, not VALIDATED';
    END IF;
    IF p_state = 'MISMATCH' AND (p_replay_digest IS NULL OR p_replay_digest = p_epoch_digest) THEN
        RAISE EXCEPTION 'moonshot: a MISMATCH needs a disagreeing replay digest';
    END IF;
    INSERT INTO validations (publication_id, chain_id, epoch_index, epoch_digest, state, checks, replay_digest,
                             replay_host, validator)
    VALUES (live.publication_id, p_chain_id, p_epoch_index, live.epoch_digest, p_state, p_checks, p_replay_digest,
            p_replay_host, p_validator)
    RETURNING validations.validation_id INTO vid;
    IF p_state IN ('MISMATCH', 'INVALID') THEN
        INSERT INTO contests (chain_id, epoch_index, work_id, published_epoch_digest, challenger_epoch_digest, reason,
                              state, opened_by, detail)
        VALUES (p_chain_id, p_epoch_index, live.work_id, live.epoch_digest,
                CASE WHEN p_state = 'MISMATCH' THEN p_replay_digest END,
                CASE WHEN p_state = 'MISMATCH' THEN 'AUDIT_MISMATCH' ELSE 'CORRUPT_BYTES' END,
                CASE WHEN c.head_index > p_epoch_index THEN 'TAINTED' ELSE 'CONTESTED' END, p_validator,
                jsonb_build_object('validation_id', vid, 'replay_host', p_replay_host))
        ON CONFLICT DO NOTHING;                -- an already open contest keeps the chain halted
        UPDATE chains SET state = 'HALTED', updated_at = now() WHERE chains.chain_id = p_chain_id;
    END IF;
    INSERT INTO events (actor, kind, chain_id, detail)
    VALUES (p_validator, 'validation', p_chain_id,
            jsonb_build_object('epoch_index', p_epoch_index, 'state', p_state, 'validation_id', vid));
    RETURN vid;
END $$;

-- Resolution by deterministic replay only; the VERDICT is computed here from the replay digests.
CREATE OR REPLACE FUNCTION {schema}.resolve_contest(p_contest_id BIGINT, p_replay_digests TEXT[],
                                                    p_published_bytes_ok BOOLEAN, p_resolver TEXT)
RETURNS TEXT LANGUAGE plpgsql SECURITY DEFINER SET search_path = {schema}, pg_temp AS $$
DECLARE
    k        contests%ROWTYPE;
    c        chains%ROWTYPE;
    prev     publications%ROWTYPE;
    pend     validations%ROWTYPE;
    d        TEXT;
    verdict  TEXT;
    new_ckpt TEXT;
BEGIN
    SELECT * INTO k FROM contests WHERE contests.contest_id = p_contest_id FOR UPDATE;
    IF NOT FOUND OR k.state NOT IN ('CONTESTED', 'TAINTED', 'UNRESOLVED') THEN
        RAISE EXCEPTION 'moonshot: contest % is not open', p_contest_id;
    END IF;
    SELECT * INTO c FROM chains WHERE chains.chain_id = k.chain_id FOR UPDATE;
    IF cardinality(p_replay_digests) IS NULL OR cardinality(p_replay_digests) = 0
       OR (SELECT count(DISTINCT x) FROM unnest(p_replay_digests) x) <> 1 THEN
        verdict := 'UNRESOLVED';
    ELSE
        d := p_replay_digests[1];
        IF p_published_bytes_ok AND d = k.published_epoch_digest THEN
            verdict := 'UPHELD';
        ELSIF d = k.challenger_epoch_digest OR NOT p_published_bytes_ok THEN
            verdict := 'OVERTURNED';
        ELSE
            verdict := 'UNRESOLVED';
        END IF;
    END IF;
    IF verdict = 'UPHELD' THEN
        UPDATE contests SET state = 'RESOLVED_UPHELD', resolved_by = p_resolver, resolved_at = now(),
                            replay_digests = p_replay_digests WHERE contests.contest_id = p_contest_id;
        UPDATE chains SET state = CASE WHEN c.head_index = c.epochs_target THEN 'COMPLETE' ELSE 'OPEN' END,
                          updated_at = now() WHERE chains.chain_id = k.chain_id;
    ELSIF verdict = 'OVERTURNED' THEN
        UPDATE publications SET rejected_at = now(), rejected_by = p_resolver, rejected_contest = p_contest_id
        WHERE publications.chain_id = k.chain_id AND publications.epoch_index >= k.epoch_index
          AND publications.rejected_at IS NULL;
        IF k.epoch_index = 1 THEN
            new_ckpt := (SELECT initial_checkpoint_sha256 FROM chains WHERE chains.chain_id = k.chain_id);
            UPDATE chains SET head_index = 0, head_epoch_digest = NULL, head_checkpoint_sha256 = new_ckpt,
                              generation = c.generation + 1, state = 'OPEN', updated_at = now()
            WHERE chains.chain_id = k.chain_id;
        ELSE
            SELECT * INTO prev FROM publications p
            WHERE p.chain_id = k.chain_id AND p.epoch_index = k.epoch_index - 1 AND p.rejected_at IS NULL;
            new_ckpt := (SELECT r.output_checkpoint_sha256 FROM results r
                         WHERE r.work_id = prev.work_id AND r.epoch_digest = prev.epoch_digest);
            UPDATE chains SET head_index = k.epoch_index - 1, head_epoch_digest = prev.epoch_digest,
                              head_checkpoint_sha256 = new_ckpt, generation = c.generation + 1, state = 'OPEN',
                              updated_at = now()
            WHERE chains.chain_id = k.chain_id;
        END IF;
        UPDATE contests SET state = 'RESOLVED_OVERTURNED', resolved_by = p_resolver, resolved_at = now(),
                            replay_digests = p_replay_digests WHERE contests.contest_id = p_contest_id;
    ELSE
        UPDATE contests SET state = 'UNRESOLVED', resolved_by = p_resolver, resolved_at = now(),
                            replay_digests = p_replay_digests WHERE contests.contest_id = p_contest_id;
    END IF;
    INSERT INTO events (actor, kind, chain_id, detail)
    VALUES (p_resolver, 'resolution', k.chain_id,
            jsonb_build_object('contest_id', p_contest_id, 'verdict', verdict, 'replay_digests', to_jsonb(p_replay_digests)));
    IF verdict IN ('UPHELD', 'OVERTURNED') THEN
        -- Fail closed: an adverse validation of a live epoch, recorded while this contest was open, could not open
        -- its own (one open contest per chain). It opens now, and the chain stays halted.
        SELECT v.* INTO pend FROM validations v JOIN publications p ON p.publication_id = v.publication_id
        WHERE v.chain_id = k.chain_id AND p.rejected_at IS NULL AND v.state IN ('MISMATCH', 'INVALID')
          AND NOT EXISTS (SELECT 1 FROM contests x
                          WHERE x.chain_id = k.chain_id AND x.detail->>'validation_id' = v.validation_id::text)
        ORDER BY v.epoch_index, v.validation_id LIMIT 1;
        IF FOUND THEN
            SELECT * INTO c FROM chains WHERE chains.chain_id = k.chain_id;          -- the head after this verdict
            INSERT INTO contests (chain_id, epoch_index, work_id, published_epoch_digest, challenger_epoch_digest,
                                  reason, state, opened_by, detail)
            SELECT k.chain_id, pend.epoch_index, p.work_id, pend.epoch_digest,
                   CASE WHEN pend.state = 'MISMATCH' THEN pend.replay_digest END,
                   CASE WHEN pend.state = 'MISMATCH' THEN 'AUDIT_MISMATCH' ELSE 'CORRUPT_BYTES' END,
                   CASE WHEN c.head_index > pend.epoch_index THEN 'TAINTED' ELSE 'CONTESTED' END, p_resolver,
                   jsonb_build_object('validation_id', pend.validation_id, 'replay_host', pend.replay_host,
                                      'pending_behind_contest', p_contest_id)
            FROM publications p WHERE p.publication_id = pend.publication_id;
            UPDATE chains SET state = 'HALTED', updated_at = now() WHERE chains.chain_id = k.chain_id;
            INSERT INTO events (actor, kind, chain_id, detail)
            VALUES (p_resolver, 'pending_validation_contested', k.chain_id,
                    jsonb_build_object('validation_id', pend.validation_id, 'epoch_index', pend.epoch_index,
                                       'after_contest', p_contest_id));
        END IF;
    END IF;
    RETURN verdict;
END $$;
