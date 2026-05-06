# Queue Infrastructure for Pressure-Driven Iteration

**Date:** 2026-05-06
**Purpose:** persistent ticket queues for the 26-agent pressure-driven iteration architecture (`pivot/pressure_driven_iteration_2026-05-06.md`).

## Files

Each agent has an inbox JSONL:

- `techne_inbox.jsonl` — tickets for Techne (substrate work)
- `ergon_inbox.jsonl` — tickets for Ergon (Learner work)
- `charon_inbox.jsonl` — tickets for Charon (test runs requested by other agents)
- `aporia_inbox.jsonl` — tickets for Aporia (calibration reviews requested)

Each line is one ticket per the schema below.

## Ticket schema

```json
{
  "id": "T-2026-05-06-0001",
  "source": "harmonia-pressure-A | substrate-pressure-CLAIM-flood | ...",
  "target": "techne | ergon | charon | aporia",
  "type": "useless-answer | substrate-flaw | discipline-drift | bug | feature | review-request",
  "priority": "P0-blocker | P1-high | P2-normal | P3-low",
  "title": "short human-readable title",
  "payload": {
    "probe": "what was sent to the substrate / Learner",
    "expected": "what should have happened",
    "actual": "what did happen",
    "severity": "free-text severity assessment",
    "remediation_hint": "optional; what the source agent thinks would fix it"
  },
  "created_at": "2026-05-06T10:00:00Z",
  "created_by": "agent_id (matches source)",
  "deadline": "optional ISO timestamp",
  "status": "OPEN | IN_PROGRESS | DONE | BLOCKED | WONTFIX",
  "status_history": [
    {"status": "OPEN", "at": "2026-05-06T10:00:00Z", "by": "harmonia-pressure-A"}
  ],
  "consecutive_block_count": 0,
  "resolution": "filled when DONE: artifact paths, key findings, follow-up tickets"
}
```

## Lifecycle

1. **Pressure-applier fires.** Generates 1-N tickets with status `OPEN`.
2. **Producer wakes via /loop.** Reads its inbox, picks highest-priority `OPEN` ticket, marks `IN_PROGRESS`.
3. **Producer works the 6-step cycle** (read → pre-test → implement → test → self-review → commit). On success, marks `DONE` with resolution. On failure, marks `BLOCKED` with reason; increments `consecutive_block_count`.
4. **If `consecutive_block_count` reaches 3:** auto-escalate to James (file a P0 ticket in `aporia_inbox.jsonl` with type `escalation`).
5. **Watchers wake periodically.** Read recent commits + ticket resolutions. File new tickets if they catch failures producers missed.

## File-level ownership (prevents conflicts)

- **Techne owns:** `sigma_kernel/`, `prometheus_math/`, `harmonia/memory/architecture/sigma_kernel*.md`
- **Ergon owns:** `ergon/learner/`, `ergon/pipeline_d/`, `ergon/diagnostic_c/`
- **Charon owns:** `charon/diagnostics/`
- **Aporia owns:** `aporia/meta/`, `pivot/external_review_watchlist*.md`, `pivot/sister_projects*.md`
- **Shared (require ticket coordination):** `pivot/`, `roles/`, `whitepapers/`

If a ticket requires modification to a file outside the producer's ownership, producer files a coordination ticket in the owning agent's inbox first.

## Maintenance

- **Daily compaction:** done tickets older than 14 days move to `<agent>_inbox_archive_YYYYMM.jsonl` to keep active inbox files small.
- **Aporia owns the queue maintenance.** Runs the compaction in its /loop.
- **No manual editing of inboxes.** Tickets are append-only; status updates use the `status_history` array.

## Bootstrap state

All 4 inboxes start empty. The first pressure-applier fire seeds them.

The pressure-applier prompts live at `aporia/meta/pressure_appliers/`. Each one is a self-contained /loop startup prompt.
