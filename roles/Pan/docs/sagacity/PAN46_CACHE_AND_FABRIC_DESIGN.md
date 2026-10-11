# PAN-46: high-value cache and Fabric advertisement (design note; nothing built)

Owner: Pan. Written 2026-10-11 ~11:15Z.

Source: the operator note of 2026-10-11 (roles/Pan/prompts/2026-10-11_sagacity_foundation):
- "starting to cache the absolute highest value information to the program in a Redis cache";
- "the A2A fabric can and should be expanded to incorporate your skills, mcp, caches";
- "memory is extremely expensive in 2026 so this should be minimal at first if done at all".

**Decision: build no cache yet. Advertise through what already exists. Precommit the trigger that
would justify a cache.**

## 1. Measured facts (2026-10-11)

| fact | measurement |
|---|---|
| Redis on M1 from M2 | TCP connect to 192.168.1.202:6379 timed out (3 s) at ~10:57Z. Whatever Redis runs on M1 is not reachable from Pan's host |
| Pointer reads from Postgres | single-row and index lookups on schema pan are milliseconds; Pan search takes 0.1-2.6 s, dominated by query encoding and fusion, not storage |
| Demand signal | none recorded. Pan keeps no read log, and the MCP server may not write one (directive: no writes) |
| Fabric | v0.2 is FROZEN by operator ruling (fabric/FREEZE.md): no new capability, method, option or protocol feature; proposals go to fabric/BACKLOG_AFTER_FREEZE.md |
| Fabric agent card | skills are derived from live worker capabilities (fabric/gateway.py `agent_card`) |
| Fabric script executor | already runs "a repo file or module at the pinned SHA, no shell, env allow-list" |
| Windows node worker | itself a post-freeze backlog item, so M2 (Windows) cannot host a fabric worker today |

## 2. Why no Redis cache now

1. **No measured need.** Nothing Pan serves is latency-bound on storage, and no consumer has
   asked for faster pointer reads.
2. **No measured demand.** "Highest value" needs a definition that can be measured. Without a
   read log there is no evidence of which pointers are read repeatedly. A cache chosen by
   intuition is decoration.
3. **A cache is a second copy, and a second place to enforce access.**
   - It can go stale relative to the catalog.
   - Every key would need the clearance discipline that search, pivot, refs and the MCP now
     have: generator-only content, a hidden path answering like a missing one.
   - The content-rule purge (PAN-47) showed how easily an index amplifies what it should not.
     A cache would amplify it again, with less provenance.
4. **Redis is not reachable from Pan's host.** Using it would mean a network change on M1. That
   is not Pan's call, and the directive authorizes no new network-facing service.

## 3. The precommitted trigger (when to build it)

Build the pointer cache when either condition is met. Neither is met today.

- **(a) Repeated shared demand.** At least 2 distinct consumers read the same pointer set at
  least 20 times per hour over 3 days. This is measured from a read log written by the CLI
  (not the MCP) to the lake on M2 C:. The log itself needs operator approval, because it records
  who asked what.
- **(b) A latency budget Postgres misses.** A consumer documents a budget for pointer reads, and
  Postgres p95 exceeds it (for example p95 > 50 ms measured from that consumer's host).

## 4. The design, if triggered

- **Content: pointers, never payloads.**
  - Each entry is (path, blob_sha, last_commit_sha, access_class, catalog SHA, why it is hot).
  - PROGRAM class only. No text, snippets or titles.
- **Candidate sets** (all exist as SQL today):
  - catalog currency (catalog SHA vs origin/main);
  - the 50 most-cited artifacts (pan.link in-degree);
  - the newest STATUS report per seat;
  - the newest control receipt per control family;
  - the Atlas propositions with their evidence links.
- **Keyspace** `pan:ptr:v1:<set>`:
  - JSON values of at most 64 KB per key, at most 1 MB in total, self-capped by Pan;
  - TTL 26 h;
  - rebuilt by `pan refresh`;
  - every value carries the catalog SHA, and consumers drop values whose SHA is older than they
    accept.
- **Source of truth stays Postgres.** A cache miss or an unreachable Redis falls back to
  Postgres. Nothing ever depends on the cache.
- **Controls before use:**
  - POSITIVE: a hot pointer is served with its SHA.
  - NEGATIVE: a burned or refused path is never present in any key.
  - CHEAT: a stale-SHA value is rejected by the consumer helper.
  - BUDGET: total bytes stay at or under 1 MB after a rebuild.

## 5. Fabric advertisement: what exists, and what is proposed

- **Pan's skills.** The `pan-search` skill (.claude/skills/pan-search) is how seats use Pan
  today. It now documents the access classes and the MCP option (2026-10-11).
- **Fabric capability, a zero-code path under the freeze.**
  - A node operator can declare capabilities `pan.search` / `pan.pivot` on a worker that has
    Pan's Python dependencies.
  - Tasks then run `python -m pan search ... --json` through the existing script executor.
  - Vectors come from M1 pgvector, so no lake is needed off M2.
  - The agent card lists declared capabilities automatically.
  - No fabric code changes. The proposal is filed in fabric/BACKLOG_AFTER_FREEZE.md; whether any
    node serves it is a node operator's decision.
- **MCP.** MCP and A2A are different protocols, and Pan proposes no bridge. The MCP server is a
  local stdio tool for a session that wants it; the Fabric capability is the A2A route.
- **Caches.** Nothing to advertise until section 3's trigger fires.

## 6. What this note does not decide

- A read log (trigger (a)) needs the operator's approval. This note only names it.
- Redis networking on M1 belongs to the DBA and the operator.
- Whether any fabric node declares `pan.*` capabilities belongs to the node operators (Odysseus
  owns the Fabric).
