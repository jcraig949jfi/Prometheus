"""Prometheus inter-agent comms: inboxes, broadcasts, receipts and per-agent
task queues in Postgres (schema `comms`), revived 2026-09-11 from the
April Agora (Redis streams mirrored to agora.messages; Redis under WSL did
not stay live). Postgres-native; no Redis.

Every seat, before and after each prompt or loop iteration:

    python -m comms boot <Seat> --model <model id> [--capabilities any,H0,H3] [--status active]
                                       # record the bootstrap: workspace, machine, model/tier, session
    python -m comms who                # who is online (active within 30 min), tier, queue depth, unseen
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
from .api import (boot, broadcast, claim, done, enqueue, inbox, init_schema, mark_seen, message_status, post, roster, set_status, sync, tasks, touch, who)

__all__ = ["boot", "broadcast", "claim", "message_status", "done", "enqueue", "inbox", "init_schema", "mark_seen", "post", "roster", "set_status", "sync", "tasks", "touch", "who"]
