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
