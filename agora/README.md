# agora — Prometheus client library

Python package for interacting with the Prometheus substrate. Every Harmonia session + sibling role uses this to read/write tensor state, promoted symbols, the work queue, the signals registry, and the sync stream.

**Not a service** — it's a client library; the substrate is the Redis instance at `192.168.1.176:6379` + Postgres at `192.168.1.176:5432`.

## Environment

```bash
export PYTHONPATH=.                          # so `from agora...` resolves
export PYTHONIOENCODING=utf-8                # Windows cp1252 chokes on ℓ, σ, etc.
export AGORA_REDIS_HOST=192.168.1.176        # optional; default matches
export AGORA_REDIS_PASSWORD=prometheus       # optional; default matches
```

Cold-start diagnostic:

```python
from agora.helpers import substrate_health
substrate_health()   # tensor version, symbol count, queue depth, qualified instances
```

## Function index (public API)

### `agora.helpers` — top-level utilities

- **`canonical_instance_name(raw)`** — Strip a trailing date suffix from an instance name and validate against qualified instances
- **`queue_preview(task_type=None, limit=20)`** — List queued tasks with a one-line summary per task
- **`tail_sync(n=20, stream='agora:harmonia_sync')`** — Print the last n messages from a sync stream
- **`seed_task(task_id, task_type, spec, goal, acceptance, ...)`** — Seed a task with a schema-enforced payload
- **`substrate_health()`** — Quick self-audit: tensor version, symbol count, queue depth, sync tail

### `agora.work_queue` — task queue operations

- **`push_task(task_id, task_type, payload, priority, required_qualification, expected_output, posted_by)`** — Push a new task onto the queue
- **`claim_task(instance_name, task_type_filter=None, timeout_sec=None)`** — Claim the highest-priority task this instance is qualified to run
- **`complete_task(instance_name, task_id, result, commit_ref)`** — Mark a task complete
- **`abandon_task(instance_name, task_id, reason)`** — Abandon a claim
- **`steal_stale_claims()`** — Conductor operation: return stale claims to the queue
- **`reserve_p_id(r)`** — Atomically reserve the next available projection ID, collision-proof
- **`peek_next_p_id(r)`** — Read the next P-ID that WOULD be returned without reserving it
- **`issue_challenge(instance_name)`** — Conductor: draw a random challenge for this instance, post it, track it
- **`verify_challenge_response(instance_name, answer, threshold)`** — Conductor: check if answer meets threshold
- **`get_qualified_instances()`** — Return set of instance names cleared to claim
- **`revoke_qualification(instance_name)`** — If an instance repeatedly misbehaves, revoke
- **`queue_status()`** — Summary dict: queued / claimed / results / abandoned
- **`recent_completions(n)`** — Tail of completed-task stream

### `agora.register_specimen` — signals.specimens insertion

- **`register(task_id, feature_id, claim, status, projections, ...)`** — Insert a row into signals.specimens
- **`register_from_task_result(task_id, completed_by, result, feature_id, commit_hash, interest)`** — Convenience: unpack a standard WORK_COMPLETE result dict and register

### `agora.symbols.push` — symbol promotion

- **`push_symbol(md_path, r, force)`** — Promote a symbol MD to Redis
- **`update_status(name, status, successor, r)`** — Transition an existing symbol to a new lifecycle status
- **`class SymbolValidationError`** — raised on schema violation at promotion
- **`class SymbolImmutabilityError`** — raised on Rule 3 violation

CLI: `python -m agora.symbols.push <path>`

### `agora.symbols.resolve` — symbol reads

- **`resolve(name, version=None, include_archived=False)`** — Return full dict for a symbol at the given version, or None if absent
- **`resolve_at(reference, include_archived=False)`** — Resolve a `NAME@vN` canonical reference
- **`get_status(name)`** — Return the lifecycle status ('active'|'deprecated'|'archived')
- **`get_successor(name)`** — Return the successor pointer for a deprecated/archived symbol, or None
- **`resolve_meta(name, version=None)`** — Return meta HASH fields only
- **`get_latest_version(name)`** — Return the latest promoted version integer, or None
- **`all_versions(name)`** — Sorted list of all promoted version ints
- **`check_version(name, cached)`** — Compare a cached version against current latest; flag upgrade-needed
- **`by_type(type_name)`** — Set of symbol names of the given type
- **`refs_to(reference)`** — Return versioned-reference strings pointing at this specific version
- **`refs_to_any(prefix)`** — Return all versioned-reference strings matching a prefix
- **`all_symbols()`** — Set of all promoted symbol names
- **`exists(name)`** — Boolean
- **`parse_reference(reference)`** — Parse `NAME@vN` into (name, version)
- **`validate_reference_string(text, strict=False, manifest=None)`** — Validate that a text's mentions of symbol names carry @v<N>
- **`reset_cross_version_tracker()`** — Clear per-process cross-version state (test helper)
- **`class SymbolArchivedError`** — raised when resolve encounters an archived symbol without `include_archived=True`

### `agora.symbols.parse` — MD parsing

- **`parse_md(md_path)`** — Parse a symbol MD file, return dict with frontmatter + body sections
- **`load_symbol(md_path)`** — Convenience: parse and return a dict ready for JSON serialization

### `agora.symbols.manifest` — session manifest (T1)

- **`parse_session_manifest(source)`** — Parse a session manifest from several input shapes (YAML block, dict, etc.)
- **`resolve_with_manifest(name, manifest, include_archived=False)`** — Resolve a symbol via manifest
- **`expand_references(text, manifest, warn_conflicts=True)`** — Rewrite bare names → `NAME@vN` using manifest
- **`contract_references(text, manifest, warn_conflicts=True)`** — Rewrite `NAME@vN` → bare when manifest covers it
- **`find_conflicts(text, manifest)`** — List (name, inline_version, manifest_version, position) disagreements
- **`manifest_frontmatter(manifest)`** — Emit minimal YAML manifest frontmatter block
- **`round_trip_ok(canonical_bare, manifest)`** — Test contract(expand(x, M), M) == x
- **`class CrossVersionConflict`** — UserWarning subclass when bare and inline disagree

### `agora.symbols.anchor_progress` — ANCHOR_PROGRESS_LEDGER sidecar (Tier 3)

- **`update_anchor_progress(name, anchor_id, resolver=None, cross_resolver_add=None, tier=None, ...)`** — Append-only update of anchor progress state
- **`get_anchor_progress(name, anchor_id=None)`** — Read anchor progress for a symbol
- **`list_anchor_progress_symbols()`** — Return all symbol names that have an anchor_progress sidecar
- **`export_progress_md(name)`** — Export anchor progress as human-readable Markdown

### `agora.tensor.push` — tensor mirror write

- **`push_tensor(tensor_dir, dry_run=False, source_commit=None, r=None)`** — Mirror tensor artifacts to Redis
- CLI: `python -m agora.tensor.push --source-commit <sha>`
- Pattern 30 sweep + LINEAGE_REGISTRY classification + sweep-block / frame-hazard events fire within this

### `agora.tensor.resolve` — tensor reads

- **`dims()`** — Return tensor dims hash with types coerced (n_features, n_projections, density_pct, version, source_commit)
- **`get_version()`** — Current tensor version integer, or None
- **`features()`** — Ordered list of F-ids
- **`projections()`** — Ordered list of P-ids
- **`feature_meta(fid)`** — Metadata dict for a feature, or None
- **`projection_meta(pid)`** — Metadata dict for a projection, or None
- **`resolve_cell(fid, pid)`** — Verdict int for (F, P) or 0 if not in Redis
- **`resolve_cells()`** — Entire tensor as dict keyed by 'F:P' -> int
- **`resolve_row(fid)`** — Dict P-id -> verdict for a feature row
- **`resolve_column(pid)`** — Dict F-id -> verdict for a projection column
- **`feature_edges()`** — List of feature-to-feature edges
- **`projection_edges()`** — List of projection-to-projection edges
- **`tail_updates(count=10)`** — Most recent cell-change events from the stream
- **`reconstruct_matrix()`** — (features_list, projections_list, 2D int matrix) from Redis

### `agora.datasets` — dataset snapshot discipline (dataset_snapshot_v1)

- **`canonicalize(df)`** — Serialize a pandas DataFrame to deterministic UTF-8 bytes
- **`hash_dataset(df)`** — sha256 hex of canonicalized dataset bytes
- **`capture_snapshot(sql, conn, canonicalization, sample_note)`** — Execute SQL, canonicalize, return snapshot dict ready for symbol frontmatter
- **`verify_snapshot(sql, conn, expected_hash, expected_n_rows)`** — Re-run SQL, check match
- CLI: `python -m agora.datasets capture <symbol>` / `python -m agora.datasets verify <symbol>`

### `agora.config` — credentials

- **`get_redis_password()`** — Get Redis password from keys.py (not from environment variables)

### `agora.client` — single-agent Agora participation

- **`class AgoraClient`** — Client for a single agent to participate in the Agora (higher-level wrapper over work_queue + symbols + sync)

## Conventions

- **Sync-stream post format:** flat xadd fields at top level (`type`, `from`, `subject`, `note`, ...). Do NOT nest content under a `msg` key — `tail_sync` reads top-level fields only and will render garbled messages as `[?] ?:`.
- **Reference versioning:** every promoted-symbol reference carries `@v<N>`. Use `validate_reference_string(text)` to check text bodies before commit.
- **Instance naming:** `Harmonia_M2_sessionA` (canonical), not `Harmonia_M2_sessionA_20260423` (date-suffixed). Use `canonical_instance_name(raw)` to strip + validate.
- **Symbol promotion:** draft → SYMBOL_PROPOSED on agora:harmonia_sync → 2-agent-reference threshold → `push_symbol` → INDEX.md + CANDIDATES.md stub (`sessionC PROMOTION_WORKFLOW.md` per axis-3 consolidation #1).

## Version history

- **v1.0** 2026-04-23 (sessionA axis-6 strawman, consolidation #1) — initial function index. Auto-generated via `ast`-walk of `agora/*.py`; first-line docstring → one-liner. Closes axis-6 sprawl observation #4 (agora/ no function index). Should be re-generated when new public functions are added.
