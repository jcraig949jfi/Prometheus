---
name: Tensor Views — Where to Read What
purpose: Single navigation doc answering "which tensor view do I use for which question?" Closes the Axis-2 sprawl observation that tensor state lives in git source + Redis mirror + cartography viewer with no document explaining the role of each.
status: living. Edit when a new tensor view is added (e.g., a future Postgres mirror per long_term_architecture.md tier 2).
related:
  - `TENSOR_REDIS.md` — Redis mirror protocol (key layout + push/read semantics).
  - `cartography/viewer/README.md` — viewer features + launch + API.
  - `build_landscape_tensor.py` — git source-of-truth (FEATURES, PROJECTIONS, INVARIANCE, edges).
  - `harmonia/memory/concept_map.md` — Axis 2 (Mapping) section that surfaced the need for this artifact.
---

# Tensor Views — Where to Read What

The tensor (features × projections) has three live views. Each answers different questions and has different update semantics. This doc tells you which to use; the deeper docs (TENSOR_REDIS.md + viewer README + tensor builder source) tell you how.

---

## The three views

| View | Location | Update mechanism | Read latency | When to use |
|---|---|---|---|---|
| **Git source-of-truth** | `harmonia/memory/build_landscape_tensor.py` (FEATURES, PROJECTIONS, INVARIANCE dict, FEATURE_EDGES, PROJECTION_EDGES) | Edit + commit | filesystem (instant local) | Authoritative reference; reproducible across time; full prose F/P descriptions |
| **Redis mirror** | `tensor:*` keys at 192.168.1.176:6379 | `agora.tensor.push_tensor()` after build script runs | sub-millisecond | Agent reads at runtime; cross-machine state sharing; change events via `tensor:updates` stream |
| **Cartographer viewer** | http://localhost:8777/map (`cartography/viewer/server.py`) | Auto-poll `/api/updates` every 5 seconds against Redis | 5s polling | Human visual inspection; hover metadata; force-directed edge graphs; gap-banner for missing projections |

---

## Which view answers which question

### "What is the canonical definition of F011 / P028 / cell (F011, P028)?"

**Use:** `harmonia/memory/build_landscape_tensor.py` — git source.

The Python source is authoritative for definitions, descriptions, and historical provenance. Every other view derives from this. If the Redis mirror disagrees with git, the mirror is stale; re-push.

### "What is the current verdict at cell (F, P) for a measurement I'm running right now?"

**Use:** Redis via `agora.tensor.resolve_cell(F, P)` or `agora.tensor.reconstruct_matrix()`.

Redis is the agent-facing low-latency view. Git source updates lag Redis between commit and push (and between push and other-machine pull). For runtime measurement code, always read Redis.

### "I want to eyeball the tensor — which cells are red, which are dense, what are the gaps?"

**Use:** Cartographer viewer at http://localhost:8777/map.

Launch with `cd cartography/viewer && python server.py`. Heatmap + hover + force-directed edge graphs + gap banner. See `cartography/viewer/README.md` for full feature list.

### "What changed in the tensor recently?"

**Use:** Redis stream `tensor:updates` via `agora.tensor.tail_updates(N)`.

Capped at 5000 events; auto-evicted FIFO. For older changes, walk git history of `build_landscape_tensor.py` (or future tensor-changelog artifact, per Axis-2 consolidation candidate #5).

### "I need to verify a measurement reproduces under the same tensor state."

**Use:** `tensor:dims` HASH `source_commit` field — pin a specific git commit + verify Redis was pushed from that commit. The (commit, version) tuple is the canonical reproducibility identifier per `long_term_architecture.md` §2.1 idempotence discipline.

### "I'm cold-starting and need to know the tensor's structure."

**Use:** Both — `restore_protocol.md` v4.3 §Step 3 reads `build_landscape_tensor.py` (FEATURES + PROJECTIONS lists, lines 1-400) for shape; then `agora.helpers.substrate_health()` queries Redis for current density + cell count + symbol count. Two-step: structure (git) + state (Redis).

---

## Update flow (canonical)

```
1. Edit FEATURES / PROJECTIONS / INVARIANCE in build_landscape_tensor.py.
2. python harmonia/memory/build_landscape_tensor.py  (rebuild .npz + .json artifacts)
3. python -c "from agora.tensor import push_tensor; push_tensor()"
   → bumps tensor:version, writes all tensor:* keys, appends to tensor:updates stream.
4. Cartographer viewer auto-refreshes within 5 seconds (Redis poll).
5. Commit the build script + .npz + .json to git.
```

Skipping step 3 leaves Redis stale. Skipping step 5 leaves git behind Redis (the mirror is now ahead of source-of-truth — recoverable but disorienting). Order matters; the tensor builder runner (when shipped per axis-6 automation_index candidate) should enforce all 5 steps as one operation.

---

## What this doc does NOT cover

- **Per-key TTL / Redis eviction discipline.** Currently undocumented (see Axis-2 sprawl observation). If Redis evicts a `tensor:*` key, recovery is "re-run step 3 above"; should be added to `TENSOR_REDIS.md` as explicit fail-safe.
- **Future Postgres mirror** (`long_term_architecture.md` tier 2 deferred). When/if it ships, add a 4th row to the table above.
- **Future Zarr store for >10MB N-dimensional tensors** (`long_term_architecture.md` tier 3 deferred). When/if it ships, add a 5th row.
- **Cross-machine consistency model.** Both M1 and M2 hit the same Redis (single source of truth at runtime). No multi-master replication; if Redis goes down, both machines lose the live mirror until restored.

---

## Version history

- **v1** 2026-04-23, sessionC. Drafted as Axis-2 concept_map consolidation candidate #2. Closes the "three-views-one-truth navigation gap" sprawl observation. Composes with TENSOR_REDIS.md (mirror protocol) + cartography/viewer/README.md (viewer features) + build_landscape_tensor.py (source).
