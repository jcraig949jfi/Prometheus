# Mnemosyne Request Queue

Append-only ingest / data-steward request queue for Mnemosyne, modeled on
`techne/queue/requests.jsonl`. One JSON object per line.

## Schema

```json
{
  "id": "REQ-NNN",
  "requested_by": "<agent or role name>",
  "date": "YYYY-MM-DD",
  "need": "<one-sentence task statement>",
  "source": "<URL or path to the source data>",
  "target_schema": "<destination — usually a path under aporia/mathematics/, charon/data/, or a Postgres table name>",
  "scope": "<expected row count or size estimate>",
  "urgency": "low | medium | high | critical",
  "context": "<why this is being requested; cross-references to Stoa proposals, memory entries, or session journals>",
  "known_issues": "<rate-limiting, gating, schema drift, etc.>",
  "status": "open | in_progress | fulfilled | blocked | cancelled",
  "fulfilled_date": null,
  "fulfilled_note": null
}
```

## Conventions

- Append only. Do not edit prior entries except to update `status` / `fulfilled_*` fields when a request resolves.
- IDs are sequential `REQ-NNN`, zero-padded to three digits. Renumbering not allowed.
- Status transitions: `open` → `in_progress` (when claimed) → `fulfilled` or `blocked`. `cancelled` is terminal.
- `context` field should cite specific Stoa documents or memory entries so the request is auditable later.
- Per `feedback_rate_limits`, design for resilience — assume APIs throttle, plan local mirrors, polite scraping with backoff for any web-sourced ingest.

## Active queue

See `requests.jsonl` for live entries.
