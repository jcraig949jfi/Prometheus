-- Prometheus comms (2026-09-11). Idempotent; {schema} is substituted by comms.api.init_schema.
CREATE SCHEMA IF NOT EXISTS {schema};

CREATE TABLE IF NOT EXISTS {schema}.messages (
    id          BIGSERIAL PRIMARY KEY,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    sender      TEXT NOT NULL,
    recipients  TEXT[] NOT NULL,                  -- seat names; '*' = broadcast to every seat
    kind        TEXT NOT NULL CHECK (kind IN ('prompt','delegation','report','question','ruling','ack','broadcast')),
    subject     TEXT NOT NULL,
    body        TEXT NOT NULL,
    sha256      TEXT NOT NULL,                    -- over subject || "\n" || body, so a message is what it says it is
    reply_to    BIGINT REFERENCES {schema}.messages(id),
    task_ref    TEXT,                             -- backlog id, decision id, request key
    priority    INT NOT NULL DEFAULT 100,         -- lower first
    machine     TEXT,
    expires_at  TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS messages_recipients_gin ON {schema}.messages USING GIN (recipients);
CREATE INDEX IF NOT EXISTS messages_created_idx ON {schema}.messages (created_at);

CREATE TABLE IF NOT EXISTS {schema}.receipts (
    message_id  BIGINT NOT NULL REFERENCES {schema}.messages(id),
    agent       TEXT NOT NULL,
    seen_at     TIMESTAMPTZ,
    queued_at   TIMESTAMPTZ,
    done_at     TIMESTAMPTZ,
    note        TEXT,
    PRIMARY KEY (message_id, agent)
);

CREATE TABLE IF NOT EXISTS {schema}.task_queue (
    id          BIGSERIAL PRIMARY KEY,
    agent       TEXT NOT NULL,
    message_id  BIGINT NOT NULL REFERENCES {schema}.messages(id),
    position    INT NOT NULL,                     -- append-only ordering per agent
    status      TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued','active','done','dropped')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (agent, message_id)
);
CREATE INDEX IF NOT EXISTS task_queue_agent_idx ON {schema}.task_queue (agent, status, position);

-- Who is online, for delegation (2026-09-11). One row per seat, upserted at boot and on every sync.
CREATE TABLE IF NOT EXISTS {schema}.agents (
    agent               TEXT PRIMARY KEY,
    status              TEXT NOT NULL DEFAULT 'unknown',   -- booting | active | idle | paused | retired
    last_active_at      TIMESTAMPTZ,                      -- any comms call by the seat
    last_sync_at        TIMESTAMPTZ,
    last_message_id     BIGINT,                           -- highest message id the seat has seen
    last_bootstrap_at   TIMESTAMPTZ,
    boot_count          INT NOT NULL DEFAULT 0,
    machine             TEXT,
    base_sha            TEXT,                             -- workspace receipt (D-23 s4)
    branch              TEXT,
    worktree_path       TEXT,
    model               TEXT,                             -- e.g. claude-fable-5-1, claude-sonnet-5 (the seat states its own)
    tier                TEXT CHECK (tier IN ('light','heavy','unknown')) DEFAULT 'unknown',
    capabilities        TEXT[] NOT NULL DEFAULT '{}',     -- what work the seat will take: 'any', lanes, kinds
    session_id          TEXT,
    harness             JSONB,                            -- harness metadata captured at boot (names only, never tokens)
    status_json         JSONB NOT NULL DEFAULT '{}'::jsonb,  -- room to grow
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Presence is DERIVED from sync receipts, never from a row's existence (operator ruling 2026-09-11):
-- "read through message N at SHA X from worktree Y at time Z".
ALTER TABLE {schema}.agents ADD COLUMN IF NOT EXISTS last_sync_sha TEXT;
ALTER TABLE {schema}.agents ADD COLUMN IF NOT EXISTS last_sync_worktree TEXT;
ALTER TABLE {schema}.agents ADD COLUMN IF NOT EXISTS last_sync_branch TEXT;


-- One seat, many instances (Harmonia #154, 2026-09-11; D-24 amendment 3). ADDITIVE: the
-- seat-level tables above keep their keys so a seat running older code keeps working; an
-- instance is <machine label>-<8 hex of the harness session id>, derived, never chosen.
CREATE TABLE IF NOT EXISTS {schema}.agent_instances (
    agent               TEXT NOT NULL,
    instance            TEXT NOT NULL,
    first_boot_at       TIMESTAMPTZ NOT NULL DEFAULT now(),   -- the instance's unseen window starts here
    last_bootstrap_at   TIMESTAMPTZ,
    last_active_at      TIMESTAMPTZ,
    last_sync_at        TIMESTAMPTZ,
    last_message_id     BIGINT,
    boot_count          INT NOT NULL DEFAULT 0,
    machine             TEXT,
    base_sha            TEXT,
    branch              TEXT,
    worktree_path       TEXT,
    model               TEXT,
    session_id          TEXT,
    PRIMARY KEY (agent, instance)
);
CREATE TABLE IF NOT EXISTS {schema}.receipt_instances (
    message_id  BIGINT NOT NULL REFERENCES {schema}.messages(id),
    agent       TEXT NOT NULL,
    instance    TEXT NOT NULL,
    seen_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (message_id, agent, instance)
);
ALTER TABLE {schema}.task_queue ADD COLUMN IF NOT EXISTS claimed_by TEXT;      -- the instance that won the claim
ALTER TABLE {schema}.messages ADD COLUMN IF NOT EXISTS sender_instance TEXT;   -- --from Seat[tag]
