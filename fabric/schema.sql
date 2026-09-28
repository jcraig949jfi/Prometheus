-- Prometheus Agent Fabric v0 -- durable core (sidecar to comms; never alters comms).
-- {schema} is replaced by fabric.store.schema() (default "fabric"; tests use throwaway schemas).
-- Every time is the DATABASE's now(), so expiry never depends on a worker's clock.

CREATE SCHEMA IF NOT EXISTS {schema};

-- Logical agents and their running instances (the Agent Card is derived from these rows).
CREATE TABLE IF NOT EXISTS {schema}.agents (
    agent        TEXT PRIMARY KEY,                -- logical identity, e.g. "worker.ubu001" or "Archaeon"
    kind         TEXT NOT NULL CHECK (kind IN ('principal', 'worker', 'gateway')),
    description  TEXT NOT NULL DEFAULT '',
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS {schema}.agent_instances (
    agent         TEXT NOT NULL REFERENCES {schema}.agents(agent),
    instance      TEXT NOT NULL,                  -- e.g. "ubu001-3f2a9c1e"
    host          TEXT NOT NULL,
    capabilities  TEXT[] NOT NULL DEFAULT '{}',
    executors     TEXT[] NOT NULL DEFAULT '{}',   -- claude | script | synthetic
    input_modes   TEXT[] NOT NULL DEFAULT '{text/plain}',
    output_modes  TEXT[] NOT NULL DEFAULT '{text/plain}',
    endpoint      TEXT,                           -- A2A endpoint if the instance is reachable directly (pilot: none)
    capacity      INT NOT NULL DEFAULT 1,
    model         TEXT,
    status        TEXT NOT NULL DEFAULT 'online' CHECK (status IN ('online', 'draining', 'offline')),
    started_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (agent, instance)
);

-- One durable requested unit of work. State names follow A2A TaskState (lower-case wire form).
CREATE TABLE IF NOT EXISTS {schema}.tasks (
    task_id          TEXT PRIMARY KEY,            -- tsk-<12 hex>
    context_id       TEXT NOT NULL,               -- ctx-<12 hex> (A2A contextId)
    principal        TEXT NOT NULL,
    target_agent     TEXT,                        -- explicit routing (custody / independence); NULL = capability routing
    thread_id        TEXT,                        -- canonical Thread id (thr-<12 hex>); science lives in git
    campaign_id      TEXT,
    experiment_id    TEXT,
    base_sha         TEXT,
    title            TEXT NOT NULL DEFAULT '',
    instruction      TEXT NOT NULL,               -- the prompt / input text
    executor         TEXT NOT NULL CHECK (executor IN ('claude', 'script', 'synthetic')),
    params           JSONB NOT NULL DEFAULT '{}', -- executor parameters (model, wall_s, script path, args, ...)
    required_caps    TEXT[] NOT NULL DEFAULT '{}',
    resources        TEXT[] NOT NULL DEFAULT '{}',-- exclusive resources the Attempt must lease first, e.g. {pilot:cpu8}
    host_affinity    TEXT,                        -- optional: only this host may run it (data/service locality)
    priority         INT NOT NULL DEFAULT 0,
    max_attempts     INT NOT NULL DEFAULT 3 CHECK (max_attempts >= 1),
    state            TEXT NOT NULL DEFAULT 'submitted'
                     CHECK (state IN ('submitted', 'working', 'input-required', 'completed', 'canceled', 'failed', 'rejected')),
    waiting_reason   TEXT,                        -- set while submitted but held (e.g. "resource pilot:cpu8 busy")
    cancel_requested BOOLEAN NOT NULL DEFAULT FALSE,
    current_attempt  TEXT,
    attempts_made    INT NOT NULL DEFAULT 0,
    idempotency_key  TEXT,
    result_summary   TEXT,
    error_summary    TEXT,
    metadata         JSONB NOT NULL DEFAULT '{}', -- Prometheus extension metadata (small)
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    terminal_at      TIMESTAMPTZ,
    UNIQUE (principal, idempotency_key)
);
CREATE INDEX IF NOT EXISTS tasks_available ON {schema}.tasks (priority DESC, created_at) WHERE state = 'submitted';

-- One actual execution of a Task. A retry is a new row; the Task's identity never changes.
CREATE TABLE IF NOT EXISTS {schema}.attempts (
    attempt_id    TEXT PRIMARY KEY,               -- att-<12 hex>
    task_id       TEXT NOT NULL REFERENCES {schema}.tasks(task_id),
    seq           INT NOT NULL,                   -- 1, 2, 3 ... within the Task
    agent         TEXT NOT NULL,
    instance      TEXT NOT NULL,
    host          TEXT NOT NULL,
    model         TEXT,                           -- the model ACTUALLY used (from the executor's own report)
    status        TEXT NOT NULL CHECK (status IN ('running', 'succeeded', 'failed', 'abandoned', 'canceled')),
    base_sha      TEXT,
    worktree      TEXT,
    lease_ids     TEXT[] NOT NULL DEFAULT '{}',
    env_receipt   JSONB NOT NULL DEFAULT '{}',
    exit_code     INT,
    error         TEXT,
    started_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    heartbeat_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at    TIMESTAMPTZ NOT NULL,           -- no heartbeat by then => abandoned by any reaper
    ended_at      TIMESTAMPTZ,
    UNIQUE (task_id, seq)
);
-- At most ONE live Attempt per Task (the exclusive-ownership guarantee, enforced by the database).
CREATE UNIQUE INDEX IF NOT EXISTS attempts_one_live ON {schema}.attempts (task_id) WHERE status = 'running';

-- Content-addressed blobs (dedupe by sha256) and the artifacts that point at them.
CREATE TABLE IF NOT EXISTS {schema}.blobs (
    sha256      TEXT PRIMARY KEY,
    size_bytes  BIGINT NOT NULL,
    content     BYTEA NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS {schema}.artifacts (
    artifact_id  TEXT PRIMARY KEY,                -- art-<12 hex>
    task_id      TEXT NOT NULL REFERENCES {schema}.tasks(task_id),
    attempt_id   TEXT REFERENCES {schema}.attempts(attempt_id),
    name         TEXT NOT NULL,
    kind         TEXT NOT NULL,                   -- final_text | stdout | stderr | env_receipt | file | patch | bundle | report
    media_type   TEXT NOT NULL DEFAULT 'text/plain',
    sha256       TEXT NOT NULL REFERENCES {schema}.blobs(sha256),
    size_bytes   BIGINT NOT NULL,
    uri          TEXT,                            -- set only for content stored outside the database
    metadata     JSONB NOT NULL DEFAULT '{}',
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Exclusive resource leases: ONE convention for the fleet (directive principle 5).
CREATE TABLE IF NOT EXISTS {schema}.leases (
    lease_id       TEXT PRIMARY KEY,              -- lse-<12 hex>
    resource       TEXT NOT NULL,                 -- "<HOST>:<class>", e.g. M1:cpu8, M2:gpu, pilot:cpu8
    attempt_id     TEXT REFERENCES {schema}.attempts(attempt_id),
    holder         TEXT NOT NULL,                 -- agent[instance] or a principal holding it by hand
    host           TEXT NOT NULL,
    purpose        TEXT NOT NULL DEFAULT '',      -- envelope / what it is for
    token          TEXT NOT NULL,                 -- fencing token: required to renew or release
    acquired_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    renewed_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at     TIMESTAMPTZ NOT NULL,
    released_at    TIMESTAMPTZ,
    release_reason TEXT
);
-- At most ONE unreleased lease per resource (atomic exclusivity, enforced by the database).
CREATE UNIQUE INDEX IF NOT EXISTS leases_one_holder ON {schema}.leases (resource) WHERE released_at IS NULL;

-- Append-only forensic history.
CREATE TABLE IF NOT EXISTS {schema}.events (
    event_id    BIGSERIAL PRIMARY KEY,
    at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    task_id     TEXT,
    attempt_id  TEXT,
    lease_id    TEXT,
    actor       TEXT NOT NULL,
    kind        TEXT NOT NULL,                    -- submitted claimed attempt_started heartbeat artifact_added state_changed
                                                  -- attempt_failed attempt_abandoned requeued completed canceled
                                                  -- lease_acquired lease_released lease_expired resource_busy
    detail      JSONB NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS events_task ON {schema}.events (task_id, event_id);

-- A2A Message history per Task (the instruction as ROLE_USER, final reports as ROLE_AGENT).
CREATE TABLE IF NOT EXISTS {schema}.messages (
    task_id     TEXT NOT NULL REFERENCES {schema}.tasks(task_id),
    message_id  TEXT NOT NULL,
    role        TEXT NOT NULL CHECK (role IN ('user', 'agent')),
    parts       JSONB NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    seq         BIGSERIAL PRIMARY KEY
);
-- v0.1 migration (idempotent): A2A does not make messageId unique across requests (the TCK reuses one for successive
-- follow-ups), so history is keyed by arrival order, not by (task_id, message_id).
ALTER TABLE {schema}.messages ADD COLUMN IF NOT EXISTS seq BIGSERIAL;
ALTER TABLE {schema}.messages DROP CONSTRAINT IF EXISTS messages_pkey;
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conrelid = '{schema}.messages'::regclass AND contype = 'p') THEN
    ALTER TABLE {schema}.messages ADD PRIMARY KEY (seq);
  END IF;
END $$;
CREATE INDEX IF NOT EXISTS messages_task ON {schema}.messages(task_id, seq);
