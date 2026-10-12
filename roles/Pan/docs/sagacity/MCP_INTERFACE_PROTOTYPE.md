# MCP_INTERFACE_PROTOTYPE

Owner: Pan (data infrastructure). Status: prototype BUILT and controlled, 2026-10-11. It is
registered nowhere (Q-015).
Directive: roles/Pan/prompts/2026-10-11_sagacity_foundation s5 ("a minimal local, read-only MCP
prototype after priorities 1 and 2"). P1 and P2 were done first: SAGACITY_FOUNDATION_MAP.md and
NEGATIVE_SPACE_EVALUATION.md.
Code: `pan/mcpserve.py`. Commands:
- `python -m pan.mcpserve` (or `python -m pan mcp serve`)
- `python -m pan mcp controls`

## 1. What it is

A local stdio process. A client (Claude Code, or any MCP client) starts it as a child and speaks
newline-delimited JSON-RPC 2.0 on its stdin and stdout. The process has no socket and no port, so
nothing network-facing is added.

It wraps four existing, tested Pan operations and adds no retrieval logic of its own (the
directive: "Do not recreate Pan's retrieval system inside an MCP server"):

| tool | wraps | returns |
|---|---|---|
| `pan_search` | `search.hybrid` (full text + chunk vectors, reciprocal-rank fusion) | ranked passages: path, line range, chunk id, heading, snippet (<= 300 chars), score, fusion trace |
| `pan_pivot` | `pivot.collect` | subject, cited-by, cites, changed-with, nearest documents |
| `pan_refs` | `links.refs` | backlinks and forward links, with totals |
| `atlas_lookup` | `atlas_snap.lookup` | rows of `atlas.fact`, `atlas.proposition` or `atlas.blind_spot` containing a literal text |

`pivot.collect` and `links.refs` were split out of the CLI functions for this. Each CLI now prints
from the shared data function, and its output on a 242-backlink path was byte-identical before and
after the split.

`atlas_snap.lookup` is new: before PAN-44, Pan read Atlas only into the Iceberg copy. It is also a
CLI command, `python -m pan atlas lookup --table T --text X`.

Not in v0:
- the frontier "nearest outside" section of the pivot (it stays CLI-only);
- the cross-encoder rerank (off by default to keep the server CPU-only; `PAN_MCP_RERANK=1` turns
  it on);
- MCP resources and prompts;
- any write tool, ever.

## 2. Contract

### 2.1 Protocol

- Versions: the server echoes the client's `protocolVersion` if it is one of 2025-11-25,
  2025-06-18, 2025-03-26 or 2024-11-05; otherwise it answers 2025-11-25.
- Capabilities: tools only (`listChanged: false`).
- Methods: `initialize`, `ping`, `tools/list`, `tools/call`; notifications are accepted silently.
- Batches are refused (-32600) and unknown methods get -32601.
- Bad arguments or an unknown tool get -32602, before any tool code runs.
- A tool that fails returns a normal result with `isError: true` and the reason.

### 2.2 Inputs

The input schemas are closed (`additionalProperties: false`):

| tool | arguments |
|---|---|
| `pan_search` | `query` (1-500 chars), `k` (1-25, default 10), `kind`, `seat` (comma lists, <= 80 chars) |
| `pan_pivot` | `path` (<= 400 chars), `k` (1-25, default 8) |
| `pan_refs` | `path`, `k` (1-50, default 40) |
| `atlas_lookup` | `table` (enum: fact, proposition, blind_spot), `text` (<= 200 chars, literal, case-insensitive), `k` (1-50, default 10) |

No argument names a role, a clearance, a table outside the enum, or raw SQL.

### 2.3 Output envelope

Every `tools/call` returns the same envelope, both as `structuredContent` and as JSON text:

```
{ "tool": "...", "clearance": "generator", "read_only": true,
  "retrieved_at": "2026-10-11T10:41:30+00:00",
  "excluded": { "refused_rule": 0, "outside_clearance": 0, "uncatalogued": 0
                [, "atlas_mentions_hidden_artifact": 0] },
  "result": { ..., "records": [ { ..., "provenance": { ... } } ] } }
```

### 2.4 Provenance on every record

**Pan records** (`store: "pan.artifact"`):
- `source`: git, comms, moonshot or fs;
- `host`;
- `blob_sha`;
- `last_commit_sha` and `last_commit_at`;
- `access_class`;
- `index_current`: true when the indexed blob equals the catalogued blob;
- `catalog_run_id`;
- `mtime` and `size_bytes`.

Search records also carry `chunk_id` and the line range. Pivot and refs records carry their
`section`.

**Atlas records** (`store: "atlas.<table>"`):
- facts: `author`, `method`, `stated_at`, `first_harvest_id`, `last_harvest_id`;
- propositions: `first_stated_at`, `last_reviewed_at` and the harvest ids;
- blind spots: the harvest ids.

Text fields are capped at 600 characters.

A hidden path and a nonexistent path get the same answer:
`{"visible": false, "note": "not in the catalog, or not visible at this server's clearance", "records": []}`.

## 3. Enforcement (in the order a request meets it)

1. **Clearance is fixed at launch.**
   - `PAN_CLEARANCE` defaults to generator. Only generator or evaluator may launch a server.
   - Adjudicator, infrastructure or any unknown role makes the process exit 2 before it serves.
   - No tool argument can change the clearance; the closed schemas refuse the attempt.
2. **Access classes (foundation map s6, migration 014).**
   - Every SQL path the wrapped operations take applies `access.filter_sql` for the clearance.
   - At generator clearance, BURNED_HOLDOUT, EMBARGOED_OUTCOME and PRIVILEGED_CRITIQUE stay
     invisible. SEALED never enters Pan.
3. **REFUSE rules.**
   - Credential-shaped files are catalogued with their content purged, so the wrapped operations
     alone would still return their path metadata.
   - The server drops any record, and any requested path, matching a REFUSE rule (`access.refused`).
   - Content scope (PAN-47, migration 015, added 2026-10-11 after the prototype): files whose text
     carries a literal credential are refused whole. That covers a credential assigned to a
     password/secret/key/token name, a private-key block, or a provider token shape.
     - 132 artifacts were refused, with their chunks, vectors, links and text-derived titles
       purged; only the path stays.
     - The chunker refuses such files before inserting chunks.
     - Before this, `pan_search` could have returned them as PROGRAM snippets, for example a
       committed config with a non-empty `db_password`.
     - Receipt: `ACCESS_20261011T110930Z.json` (20/20). Pan never selects or prints a value.
4. **Inheritance by mention (Atlas).**
   - Atlas rows have no access class.
   - A row whose text mentions the path or basename of an artifact hidden at the clearance is
     dropped and counted.
   - 2026-10-11 measurement: 0 of 41,784 facts, 10 propositions and 7 blind spots mention one.
   - The rule is a fail-closed heuristic, not proof (section 5).
5. **Read-only session.**
   - The server starts with `PAN_DB_READ_ONLY=1`, so every connection has the server-side setting
     `default_transaction_read_only=on`.
   - Startup checks `show transaction_read_only` and refuses to serve unless it is `on`.
   - The server writes nothing, holds no cache, and loads the query encoder from the local model
     cache with Hugging Face offline mode forced.

## 4. Evidence

### 4.1 Live controls

`roles/Pan/reports/controls/MCP_20261011T104148Z.json`: **15/15 PASS**. These run against two
real server processes (generator and evaluator) on pipes:

| kind | control | observed |
|---|---|---|
| PROTOCOL | initialize negotiates; 4 read-only tools with closed schemas | echo 2025-06-18; unknown version -> 2025-11-25 |
| POSITIVE | pan_search records carry provenance (blob sha, access class, catalog run) | 10 records |
| POSITIVE | pan_pivot: subject + lineage + co-change + neighbours, each with provenance | 21 records; cited_by 242 |
| POSITIVE | pan_refs totals equal the wrapped CLI operation's | cited_by 242, cites 94 |
| POSITIVE | atlas_lookup facts with provenance | 5 of 97 matched |
| NEGATIVE | burned holdout via pivot: evaluator sees it; generator gets the nonexistent-path answer | visible True / False; identical to a nonexistent path |
| NEGATIVE | burned holdout via search: a query that reaches it at evaluator clearance returns none of it to a generator | non-vacuity query found (sha cd3f33b0cfe9); 0 generator hits |
| NEGATIVE (widened 11:56Z, MCP_20261011T115620Z) | a query family per burned file (lead words, mid-file window, tail, path words) | 16 queries over 4 files; 12 reach a burned file at evaluator clearance; 0 generator hits from any |
| CHEAT | prompt text asking for evaluator clearance | 0 burned hits |
| CHEAT | `clearance` argument | -32602 unknown argument |
| CHEAT | credential-shaped path | the wrapped operation alone returns it; the server does not (path sha af759744cf0c) |
| CHEAT | SQL text in a lookup | matched 0; atlas.fact 41,784 -> 41,784 rows |
| CHEAT | listening sockets / network-server imports | 0 / none |
| CHEAT | launch at adjudicator, infrastructure | exit 2 (both) |
| CHEAT | write through a read-only process | transaction_read_only=on; CREATE TEMP TABLE refused |

Each negative has a non-vacuity twin. The burned file is shown to be reachable at evaluator
clearance through the same tool, and the credential path is shown to be returned by the wrapped
operation without the server's filter.

### 4.2 Protocol tests and SDK conformance

- **Protocol tests** (`pan/tests/test_mcpserve.py`, 5 tests, no database): negotiation, tool shapes,
  seven invalid-argument cases, JSON-RPC edge cases, refused privileged launch.
- **Conformance with the official MCP Python SDK client.**
  - Receipt: `roles/Pan/reports/controls/MCP_SDK_20261011T104316Z.json`, PASS.
  - Client: mcp==2.3.0, in a scratch venv, deliberately not in Pan's venv.
  - It negotiated 2025-11-25, listed the 4 tools and called each one. Every call returned at
    generator clearance with provenance on every record.
  - The escalation argument was refused as an MCP error.
  - Script: `pan/tests/mcp_sdk_conformance.py`.

## 5. Limits: what this does NOT establish

- **Enforcement is application-level.**
  - The server connects as the superuser `postgres`, like every program session, so RLS would not
    bind it. No live table has RLS.
  - What stops a write is the server-side read-only default plus the absence of any write path.
  - What stops a hidden read is Pan's filter code.
  - A bug in `access.filter_sql` or in a wrapped operation would leak. That is why the controls
    test through the server, not the functions.
  - Least privilege (a login role with SELECT on six tables, plus RLS) is Q-014, which needs the
    operator.
- **Inheritance by mention is a heuristic.** An Atlas fact derived from a hidden artifact without
  naming its path or basename would pass. True inheritance needs Atlas rows to carry source
  artifact ids. This is part of foundation-map gap G6 (access unenforced); Atlas owns that
  schema.
- **The UNKNOWN/hidden equivalence covers content, not timing.** A hidden path and a missing path
  return the same JSON, but no constant-time guarantee is attempted.
- **The launching user is the boundary.** Whoever can start the process chooses the clearance,
  within generator or evaluator. A stdio server has no caller authentication of its own.
- **Retrieval quality is inherited.** Hybrid R@10 is 0.765 on 200 independent queries (bar 0.80,
  inside its interval). The server makes retrieval reachable; it does not make it better.
- **Index currency is that of Pan's last refresh.** Every record states `index_current` and its
  blob/commit, so staleness is visible, not hidden.

## 6. Using it (local opt-in only; Q-015 default)

```
claude mcp add pan -- C:\Prometheus-data\pan\venv\Scripts\python.exe -m pan.mcpserve
```

Run this from a checkout of the repository, so that `pan` is importable from the working
directory. Set `PAN_CLEARANCE=evaluator` only for an evaluator seat.

Nothing is registered by Pan. A project-scoped `.mcp.json` would expose it to every seat; that is
the operator's call.

## 7. What comes next (not built)

- PAN-46: the Fabric/A2A advertisement of this server and a minimal Redis cache of pointers. The
  design comes first, per the operator note ("minimal at first if done at all").
- Atlas owns adding source-artifact ids to Atlas rows (true inheritance).
- The DBA owns Q-014 roles and RLS, if approved.
- More tools only by the same rule: each one wraps an existing tested operation and ships with
  controls.
