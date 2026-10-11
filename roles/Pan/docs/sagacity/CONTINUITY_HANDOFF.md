# CONTINUITY_HANDOFF

Owner: Pan (data infrastructure). Written 2026-10-11 ~10:55Z. It is updated at the
2026-10-12T10:40Z checkpoint, and again at the end of the extended loop (2026-10-16T10:40Z).
Directive: roles/Pan/prompts/2026-10-11_sagacity_foundation, deliverable 4. It asks what should
be maintained after the window closes, what remains unimplemented, and who should own it.

## 0. Recommendation first: the standing maintenance owner

**Keep a Pan seat in maintenance mode, with Mnemosyne as database co-owner and Aporia as the
watcher.**

- **Why a Pan seat and not absorption into another seat.**
  - The directive's ownership split keeps infrastructure, retrieval, provenance and transport
    with Pan. Atlas, Hades, Cosmos, Nyx and Harmonia own the science.
  - Absorbing Pan into a science seat would let the owner of claims also own the index they are
    retrieved from. That is the conflict the split prevents.
- **The seat's mode.**
  - Maintenance needs about one hour of seat time a day: section 1, items 1-5.
  - It does not need a three-day build window.
  - Charter: the existing Pan charter (roles/Pan/prompts/2026-10-09_charter) with build items
    suspended. Keep refreshes, controls and answers to seats; take new work only by operator
    ruling.
- **Mnemosyne (DBA) co-owns the database side:**
  - applying any approved migration (Atlas proposals, Q-014 roles and RLS);
  - schema-size budget (Q-007);
  - vacuum and index health on M1.
  - Pan writes migrations; the DBA applies the ones that touch authorization.
- **Aporia watches the PanWorkLoop MONITORS row:** a bound of 6 h without a pan.run row or Pan
  commit, reported once.
- **If the operator does not keep a Pan seat:**
  - Mnemosyne owns items 1-5 below.
  - Items 6-9 freeze until someone needs them.
  - Nothing in Pan degrades silently except index currency. Every record carries its blob and
    commit, and `index_current` flags staleness.

## 1. What must be maintained

| # | item | cadence | command (M2, venv `C:\Prometheus-data\pan\venv`, `EW_DB_HOST=192.168.1.202`) | healthy when | if neglected |
|---|---|---|---|---|---|
| 1 | Index to origin/main (catalog, commits, chunks, vectors, links, comms, Moonshot; access rules applied before indexing, 2026-10-11) | every loop tick; at least daily | `PAN_EMBED_DEVICE=cpu python -m pan refresh` (CPU while M2 runs operator experiments) | `python -m pan status`: "commits not yet indexed: 0" | search and MCP answer from an older tree; staleness stays visible per record |
| 2 | Access classes | after any new sealed or holdout location; weekly controls | new location: add a CLASSIFY rule in a migration, then `python -m pan access apply`; check: `python -m pan access controls` | controls PASS (20 checks: drift + its rolled-back twin, content rule PAN-47); drift 0 | a new sealed file becomes visible to generators. Refresh now applies rules, but only for patterns that exist |
| 3 | Frontier intake | daily (~14:30Z) | `PAN_EMBED_DEVICE=cpu python -m pan frontier daily`, then `python -m pan frontier digest` | frontier-* runs OK in `pan status` | "outside work like this" goes stale; nothing breaks |
| 4 | Atlas analytical copy | every tick (skips unless Atlas harvested) | `python -m pan atlas snapshot` | manifest fingerprints equal (controls ATLAS_SNAP 6/6) | Iceberg copy lags Atlas; live Atlas is unaffected |
| 5 | Status and questions | every 6 h while a loop runs; daily in maintenance | roles/Pan/STATUS.md, reports/STATUS_*.md, QUESTIONS.md (apply ANSWER lines) | operator answers acted on within a tick | Q-002..Q-015 defaults stay in force (all safe) |
| 6 | Fleet tabs and data-map dashboard | when the fleet changes | `python -m pan fleet probe`; `roles/Pan/tools/mk_datamap.py --only fleet`; republish the artifact | page shows the probe time | the dashboard shows an old fleet |
| 7 | pgvector and HNSW on M1 | monthly look | `select pg_size_pretty(sum(pg_total_relation_size(c.oid))) from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname='pan'` | schema pan under the 10 GB self-cap (3,590 MB on 2026-10-10) | cluster growth; Q-007 sets the real budget |
| 8 | Iceberg snapshots (pan_iceberg; pan_atlas keeps time travel) | monthly | expire snapshots older than 90 days. Not built yet: write it when the catalog passes ~5 GB | lake under budget (3.5 GB on M2 C: NVMe on 2026-10-11) | slow growth only |
| 9 | Instruments re-run on change: reviewcal (PAN-37/39), repobench (PAN-34), negspace calibration (PAN-43), MCP controls (PAN-44) | only when their inputs change (a new reviewer, model, domain, or a change to access/search/pivot/links) | `python -m pan reviewcal ...`, `repobench ...`, `negspace calibrate`, `mcp controls` | the receipt verdict as frozen in each prereg | an unrecalibrated instrument is used as if calibrated; each prereg forbids that |

The stores and their locations are listed in roles/Pan/docs/DATA_ARCHITECTURE.md:
- schema `pan` on M1 `prometheus_fire`;
- Iceberg SqlCatalog `pan_iceberg` / `pan_atlas`;
- the lake at `C:\Prometheus-data\pan\lake` (M2 NVMe, never the SMR D:);
- the comms and Moonshot indexes inside `pan`.

Nothing of Pan's runs unattended. There are no scheduled tasks and no services; the MCP server
runs only when a client starts it. Q-016 asks whether to change that.

## 2. What was delivered in the Sagacity window (2026-10-11)

| deliverable | state | evidence |
|---|---|---|
| SAGACITY_FOUNDATION_MAP.md (P1) | DONE | measured populations, gaps G1-G7, access design s6 |
| Schema proposals: atlas.distinction_detail, atlas.boundary (+ recurrence view) | VERIFIED, NOT APPLIED (Atlas's call) | `pan proposals check` 15/15 in a throwaway DB |
| Access classes (migration 014) + RLS proof | APPLIED (Pan's own schema) | `pan access controls` 12/12; RLS proof in a throwaway DB |
| NEGATIVE_SPACE_EVALUATION.md (P2) | instrument PROMOTED; protocol frozen + A1-A4; NOT RUN | NEGSPACE_CALIBRATION_20261011T101839Z; review packet PAN43 |
| MCP_INTERFACE_PROTOTYPE.md (P3) | BUILT, controlled, registered nowhere | MCP_20261011T104148Z 15/15; MCP_SDK_20261011T104316Z PASS; review packet PAN44 |
| CONTINUITY_HANDOFF.md | this file | -- |
| Checkpoint packet | due 2026-10-12T10:40Z | -- |

## 3. What remains unimplemented (and who it belongs to)

| item | why not done | owner | next step |
|---|---|---|---|
| Atlas proposals applied (distinction_detail, boundary) | the directive allows proposals only | Atlas (DBA applies) | Atlas accepts, amends or rejects (comms #2113) |
| A3 family adjudication of novel classes | needs another seat by design; Pan must not adjudicate | Hades labels; Harmonia adjudicates | a mechanical family criterion would be better (offer, #2126) |
| Held-out calibration set from another seat | the instrument's designer cannot certify it | Nyx or Techne | four categories, kept from every generator (#2126) |
| Cosmos port of the negative-space instrument | the toy cannot answer the question | Cosmos supplies the domain; Pan ports the harness | domain module + failure references + calibration pairs |
| The toy generation run | the directive forbids a campaign; A2 floor risk | -- | not recommended (PAN43 packet s6) |
| Least-privilege DB role + RLS on pan.artifact/chunk | production authorization change | operator (Q-014), then DBA | default: application-level enforcement continues |
| True inheritance for Atlas rows (source-artifact ids) | Atlas's schema | Atlas | replaces the inheritance-by-mention heuristic in the MCP |
| MCP registration for seats | a prototype, not a deployment | operator (Q-015) | default: local opt-in |
| PAN-46: Redis pointer cache + Fabric/A2A advertisement | design first, "minimal at first if done at all" | Pan | design note before any keyspace |
| PAN-26: evidence-wiki index via API | PEW down on M2 since 2026-09-23 | Mnemosyne (API) | retry when PEW answers |
| Retrieval R@10 0.765 vs bar 0.80 | tuning stopped by Pan's own rule | Pan | only with a new held-out set and prereg |
| PAN-34 32B size arm | M2 memory (Q-013) | operator | default: dropped |
| Cold JSONL conversion (132 GB) | no consumer asked | Pan | convert a family when a consumer names it |
| Unattended maintenance (scheduled refresh) | needs a scheduled task on M2 | operator (Q-016) | default: session-driven |

## 4. Invariants a successor must not break

1. **Never read credential files.**
   - REFUSE rules purge them from the index, and the chunker checks before opening.
   - Keep R-credential-file first in any rule change.
   - The content rule R-credential-content (PAN-47) refuses files whose TEXT carries a literal
     secret.
   - Pan selects counts and paths only, never a value.
   - Its own source must not match it (pan/tests/test_content_rule.py).
2. **SEALED never enters Pan.**
   - Burned or declared-exposed material is classified, not deleted, so evaluators keep it.
   - Generators never see it: search, pivot, refs, cochange and MCP all filter.
3. **Derived data inherits by join.**
   - Declassification only through pan.declassification, with a reason and an approver.
4. **Every retrieval record carries provenance.** A hit is a pointer, not evidence.
5. **Frozen preregs are amended in text with a reason, never edited silently.**
   - The receipt carries the prereg sha256, LF-normalized.
6. **The worktree, never the canonical checkout; never `git pull`.**
   - Fetch, fast-forward push and verify ancestry.
7. **MWO-0004 R2:** a Fabric lease before heavy GPU/CPU (<= 4 GPU-h and <= 48 core-h per 24 h).
   Check real load first; M2 runs unleased operator experiments.
8. **No fsync-heavy store on M2 D: (SMR).** The lake lives on C: NVMe.

## 5. Where to start (a successor's first hour)

1. Read, in order:
   - roles/Pan/STATUS.md;
   - roles/Pan/TODO.md;
   - roles/Pan/QUESTIONS.md;
   - this file;
   - the latest reports/STATUS_*.md.
2. Run `python -m pan status`, then item 1 (refresh) and item 2 (`access controls`).
3. Run `python -m comms sync Pan` and answer anything addressed to Pan.
4. Load the `pan-search` skill (.claude/skills/pan-search). It is how the other seats use Pan.
