# SFE archaeology schema note

**Purpose.** What an independent future agent needs to reconstruct
`world → artifact → experiment → work → observation → event anchor`
from an SFE database or event export, with no access to the people or code that
produced it.

Fields below were read from the live schema of build `c358a53b`
(`schema_version 3`), 2026-09-04. The Engine's own tables are authoritative.

---

## 1. The universal anchor: `events.event_seq`

Every reconstructable object carries a `*_seq` integer that **is** an
`events.event_seq`. That is the join key for the whole graph and the only
total order you should trust.

| Table | Anchor field(s) | Anchors to |
|---|---|---|
| `artifacts` | `created_seq` | the `ARTIFACT_CREATED` / `ARTIFACT_IMPORTED` event |
| `experiments` | `created_seq`, **`committed_seq`** | `EXPERIMENT_CREATED`, `EXPERIMENT_COMMITTED` |
| `observations` | `created_seq` | `OBSERVATION_RECORDED` |
| `lineage_edges` | `created_seq` | `LINEAGE_EDGE_ADDED` |
| `worlds` | `next_index`, `head_hash` | ledger tip |
| `checkpoints` | `world_index`, `head_hash`, `state_hash` | `CHECKPOINT_CREATED` |

`events` itself: `event_seq` (global monotonic), `event_id`, `world_id`,
`world_index` (per-world ordinal), `event_type`, `ts`, `actor`, `payload`,
`refs`, `causal`, `artifacts`, `prev_hash`, `entry_hash`, `schema_ver`.

**Do not order by `ts`.** Wall-clock is informational; `event_seq` is the
authority. `world_index` orders within one world, `event_seq` across all.

## 2. Tamper-evidence

`events.prev_hash` / `events.entry_hash` form a per-world hash chain.
`GET /v2/worlds/{wid}/status` → `ledger_integrity_ok` verifies it **at read
time**, not at write time. A reconstruction that does not re-verify the chain
is asserting the record was not altered rather than checking it.

## 3. The chain, link by link

```
worlds.world_id
   │   parent_world_id + fork_point ....... provenance across a fork
   │   seed_root, sharing_policy, budget_root, head_hash
   ▼
artifacts.world_id → artifact_id
   │   blob_hash ........ sha256 of the BYTES; world-INDEPENDENT.
   │                      Use this to prove one payload entered N worlds.
   │   artifact_id ...... content_hash({world, kind, blob, meta}); world-SCOPED.
   │   origin / source_world / source_artifact / import_seq
   │                      ... NATIVE here, or legally imported from there.
   │   created_seq ...... event anchor
   ▼
experiments.exp_id  (world_id, hyp_id, pred_id)
   │   spec_hash ....... identity of what was run
   │   committed_seq ... THE PROSPECTIVE BOUNDARY. A prediction counts as
   │                     foresight iff predictions.created_seq < committed_seq.
   │   work_id ......... the execution, if one was enqueued
   ▼
work_items.work_id  (world_id)
   │   payload ......... carries exp_id
   │   status, attempts, claimed_by, claim_id (server-issued fencing token)
   │   result, result_hash, completed_ts
   ▼
observations.obs_id  (world_id, exp_id, pred_id, work_id)
       evidence_class .. ENGINE_WORK_RESULT (engine-attested, work_id bound and
                         verified) vs CLIENT_ASSERTED (the client's word)
       pred_prospective  1/0, computed at write time against committed_seq
       outcome ......... FALSIFIED | SURVIVED | INCONCLUSIVE
       created_seq ..... event anchor
```

`hypotheses` (`hyp_id`, `statement`, `content_hash`, `created_seq`, `state`) and
`predictions` (`pred_id`, `hyp_id`, `content`, `created_seq`) hang off the same
anchors. `lineage_edges` (`src_kind`/`src_id` → `dst_kind`/`dst_id`,
`relation`, `claimed`) carries explicit derivation the objects do not imply.

## 4. Which instrument produced it

`EXPERIMENT_COMMITTED.payload` carries **`engine_source_hash`** (verified
present), alongside `spec_hash`, `prospective_rule` and `budget_resource`. So
every committed experiment binds to the exact engine build that committed it —
including across a rebuild, which is what makes results attributable after the
code has moved on.

`source_commit` on `GET /v2/version` is **best-effort git metadata**: the HEAD
of whatever tree the process was launched from, which may be an unrelated
branch. It is not the commit containing the engine code. Use
`engine_source_hash`.

## 5. Event vocabulary present in the ledger

`WORLD_CREATED` · `WORLD_STARTED` · `WORLD_FORKED` · `WORLD_TERMINATED` ·
`CHECKPOINT_CREATED` · `ARTIFACT_CREATED` · `ARTIFACT_IMPORTED` ·
`HYPOTHESIS_PROPOSED` · `PREDICTION_REGISTERED` · `EXPERIMENT_CREATED` ·
`EXPERIMENT_COMMITTED` · `WORK_ENQUEUED` · `WORK_CLAIMED` · `WORK_HEARTBEAT` ·
`WORK_COMPLETED` · `OBSERVATION_RECORDED` · `CLAIM_SURVIVED` ·
`CLAIM_FALSIFIED` · `FAILURE_RECORDED` · `BUDGET_CONSUMED` ·
`BUDGET_EXHAUSTED` · `LINEAGE_EDGE_ADDED`

## 6. Four traps a future reconstruction will hit

1. **`artifact_id` is not a content hash of the bytes.** It hashes an envelope
   — `{world, kind, blob, meta}` — so the *same* bytes yield *different*
   `artifact_id`s in different worlds, and a changed `meta` yields a different
   id for identical bytes. Cross-world identity is `blob_hash`, never
   `artifact_id`.

2. **Terminal-state semantics CHANGED on 2026-09-04, and the record spans both
   rules.** Before that date a TERMINATED world still accepted artifact,
   hypothesis and budget writes; from build `6a4f3aee` onward all three are
   `409` while reads, checkpoint and fork stay open.

   For archaeology this means `created_seq` **can legitimately postdate
   `WORLD_TERMINATED`** in pre-2026-09-04 records — 38 such artifacts exist on
   M1 and are not corruption. **Do not infer a world's active window from its
   terminate event**, and do not "repair" those rows: they were written under
   the rule in force at the time. Date the record before judging it.

3. **`pred_prospective` is frozen at write time**, computed against
   `committed_seq`. Do not recompute it from timestamps later and expect a
   match — and never read `CLIENT_ASSERTED` as "false", only as
   "not engine-attested".

4. **Bytes written before 2026-09-04 may have been silently truncated** if
   their producer used URL-safe base64: builds up to `5274ddbe` accepted it with
   a 200 and stored the mis-decoded result. `blob_hash` hashes what was
   *stored*, so it cannot detect this — only comparison against the producer's
   own digest can. Fixed in `c358a53b`, which rejects such input with a 422.

## 7. Minimum export for a reconstructable record

`events` (all fields, including `prev_hash`/`entry_hash`), plus `worlds`,
`artifacts`, `experiments`, `work_items`, `observations`, `hypotheses`,
`predictions`, `lineage_edges`, `checkpoints`. Blob bytes live outside the DB
in `var/blobs/`, addressed by `blob_hash`; an export without them preserves the
graph and the hashes but not the payloads.
