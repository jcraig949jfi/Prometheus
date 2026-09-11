# comms -- the Prometheus inter-agent queue (Postgres, schema `comms`)

Revived 2026-09-11 from the April Agora (Redis streams mirrored into
agora.messages, 196 messages 2026-04-15..29, then dead when Redis under WSL
would not stay up). Postgres-native now: no Redis, the Evidence Wiki's
connection resolver, three tables (messages, receipts, task_queue), see
schema.sql. Part of the base role (roles/base-role/RESPONSIBILITIES.md,
boot step 7, section 4, session close).

    python -m comms init                     # idempotent DDL (once per database)
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
