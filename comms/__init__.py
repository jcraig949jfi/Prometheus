"""Prometheus inter-agent comms: inboxes, broadcasts, receipts and per-agent
task queues in Postgres (schema `comms`), revived 2026-09-11 from the
April Agora (Redis streams mirrored to agora.messages; Redis under WSL did
not stay live). Postgres-native; no Redis.

Every seat, before and after each prompt or loop iteration:

    python -m comms sync <Seat>        # print unseen inbox + broadcasts,
                                       # mark them seen, append prompts and
                                       # delegations to the seat's task queue
    python -m comms tasks <Seat>       # the seat's queue, in order
    python -m comms post --from <Seat> --to <Seat|*> --kind <kind> \\
        --subject "..." --body-file <path> [--reply-to ID] [--task-ref X]
    python -m comms done <Seat> <message_id> [--note "..."]

Doctrine: a message is committed text (sha256 recorded); chat is not a
channel; a prompt delivered here is as binding as one the operator pastes.
"""
from .api import (broadcast, done, enqueue, inbox, init_schema, mark_seen, post, roster, sync, tasks)

__all__ = ["broadcast", "done", "enqueue", "inbox", "init_schema", "mark_seen", "post", "roster", "sync", "tasks"]
