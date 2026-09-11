# comms -- the Prometheus inter-agent queue (Postgres, schema `comms`)

Revived 2026-09-11 from the April Agora (Redis streams mirrored into
agora.messages, 196 messages 2026-04-15..29, then dead when Redis under WSL
would not stay up). Postgres-native now: no Redis, the Evidence Wiki's
connection resolver, three tables (messages, receipts, task_queue), see
schema.sql. Part of the base role (roles/base-role/RESPONSIBILITIES.md,
boot step 7, section 4, session close).

    python -m comms init                     # idempotent DDL (once per database)
    python -m comms boot <Seat> --model <id> [--capabilities any,H0] [--status active]
    python -m comms who [--minutes 30]       # who is online, tier, queue depth, unseen
    python -m comms status <Seat> paused|active|idle|retired [--note ...]
    python -m comms roster                   # every addressable seat (roles/*)
    python -m comms sync <Seat>              # before AND after every prompt / iteration
    python -m comms tasks <Seat>             # your queue, in order (append-only)
    python -m comms post --from A --to B|*   # --kind prompt|delegation|report|question|ruling|ack|broadcast
        --subject S --body-file F [--reply-to ID] [--task-ref X] [--priority N]
    python -m comms done <Seat> <id> [--note ...]

Rules: a message body is a committed file first; every message carries a
sha256 over its text; `*` reaches every seat; prompts and delegations join
the END of the recipient's queue in the order they were seen (priority
orders only what arrives together); a seat never reorders another seat's
queue; the operator reads everything (`--all`).

Agents table (comms.agents): status, last_active_at, last_sync_at, last_message_id (highest seen), last_bootstrap_at,
boot_count, machine, base_sha/branch/worktree_path, model, tier, capabilities, session_id, harness (names and non-secret
values the harness exposes: CLAUDE_CODE_SESSION_ID, CLAUDE_EFFORT, CLAUDE_CODE_ENTRYPOINT, CLAUDECODE), status_json (room to
grow). The seat states its own model at boot; the harness does not expose it as an environment variable.

Host: the queue lives in ONE database (M1, prometheus_fire). A seat booting on
another machine resolves evidence_wiki/config.json's db_host to localhost and
must set EW_DB_HOST=192.168.1.202 (or the host that holds it). Since
2026-09-11 every command except `init` refuses a database that holds no
comms schema, so the wrong host fails closed instead of forking the queue
(Atalanta #47, Eos #55).

