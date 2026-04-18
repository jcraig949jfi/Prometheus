# Tensor in Redis — Multi-Machine Read-Mirror

**Status:** Live as of 2026-04-18. Base Redis (strings, hashes, lists, streams).
**Purpose:** Let every agent (M1 and M2) read current tensor state without
waiting for git pull. Source of truth stays in git; Redis is the
low-latency mirror.

---

## Key layout (base Redis)

| Key | Type | Contents |
|---|---|---|
| `tensor:version` | STRING | integer, bumped on every push |
| `tensor:dims` | HASH | n_features, n_projections, density_pct, updated_at, version, source_commit |
| `tensor:features` | LIST | F-ids in row order |
| `tensor:projections` | LIST | P-ids in column order |
| `tensor:feature_meta:<F>` | STRING | JSON {label, tier, n_objects, description} |
| `tensor:projection_meta:<P>` | STRING | JSON {label, type, description} |
| `tensor:cells` | HASH | `<F>:<P>` → verdict string ("-2".."+2") |
| `tensor:feature_edges` | STRING | JSON array of {from, to, relation, note} |
| `tensor:projection_edges` | STRING | JSON array of same shape |
| `tensor:updates` | STREAM | change events {F, P, old, new, source, version, at}; capped at 5000 |

All values are plain strings or JSON blobs — no RedisJSON or RediSearch required.

---

## Write path

```bash
# Edit tensor definition as usual
vim harmonia/memory/build_landscape_tensor.py

# Rebuild artifacts
cd harmonia/memory && python build_landscape_tensor.py

# Push to Redis (bumps version, emits change events)
cd /d/Prometheus  # or ~/Prometheus on M1
COMMIT=$(git rev-parse --short HEAD)
python -m agora.tensor.push --source-commit $COMMIT

# Optional dry run
python -m agora.tensor.push --dry-run
```

`push_tensor()` is idempotent: cells that haven't changed since the last
push don't emit stream events. Version is incremented every push regardless.

---

## Read path (any agent, either machine)

```python
from agora.tensor import (
    dims, features, projections,
    resolve_cell, resolve_row, resolve_column, resolve_cells,
    feature_meta, projection_meta,
    feature_edges, projection_edges,
    tail_updates, get_version, reconstruct_matrix,
)

dims()                         # {n_features, n_projections, density_pct, ...}
features()                     # ordered list of F-ids
projections()                  # ordered list of P-ids
resolve_cell('F011', 'P020')   # int verdict, 0 if untested
resolve_row('F011')            # {P-id: verdict, ...} for this feature
resolve_column('P028')         # {F-id: verdict, ...} for this projection
feature_meta('F011')           # full dict with label, tier, description
tail_updates(10)               # recent change events
reconstruct_matrix()           # (features_list, projections_list, np.ndarray)
```

All helpers return native Python types. No numpy dependency needed
except for `reconstruct_matrix()`.

---

## Worker usage patterns

**Cartographer:** reads `resolve_cells()` + `feature_meta` + `projection_meta`
to render. Subscribes to `tensor:updates` stream for live-reload.

**Gap-filler:** reads `resolve_cells()` to find 0-cells; writes verdicts
via the git → rebuild → push path. Does NOT write to Redis directly.

**Re-auditor:** same write path. Reads `resolve_row(F)` to find this
feature's current +1 cells that need block-shuffle promotion.

**Rank analyst:** calls `reconstruct_matrix()` → numpy ndarray → SVD.

**Query-runner:** reads `resolve_cells()` and computes aggregates;
writes nothing.

**Edge-weaver:** reads `feature_meta(F)` descriptions to look for
relational language; writes new edges via git → rebuild → push.

---

## What's in Redis right now (v1)

```
31 features × 25 projections
82 non-zero cells, 693 untested (density 10.58%)
Value distribution: -2:17, -1:15, 0:693, +1:28, +2:22
12 feature edges, 9 projection edges
```

**Known gap caught by this mirror:** `build_landscape_tensor.py` has
only 25 projections in its PROJECTIONS list, while
`coordinate_system_catalog.md` has 42. Missing from tensor:
**P028 Katz-Sarnak**, P031-P033, P035-P039, P101, P103, P104.

This is a build-script gap, not a data-model gap. The Cartographer and
Gap-filler will surface it visually. Adding missing projections is a
next-pass task.

---

## Versioning

- Versioned: every `push_tensor()` call increments `tensor:version` and
  writes `dims.version` + `dims.source_commit`.
- Not snapshotted (yet): old cells are overwritten. If you need a
  snapshot of "tensor at version N", check out the corresponding git
  commit. Future tier-2 work: immutable `tensor:v<N>:cells` snapshots.
- Stream-retained: `tensor:updates` keeps up to 5000 recent change
  events with full provenance (old, new, source_commit, version).

---

## Cross-machine

Redis is at `192.168.1.176:6379` (password `prometheus` via env
`AGORA_REDIS_PASSWORD`). Both M1 and M2 hit the same instance. Workers
on either machine see the same live state instantly after any push.

No per-machine replica needed. Write from whichever machine ran the
build; read from everywhere.

---

## Commit policy

Treat Redis as a derived artifact. Git is authoritative. If Redis
drifts from git (e.g. someone ran `FLUSHDB` or an aborted push left
partial keys), just re-run `python -m agora.tensor.push` — it
rebuilds the full key set idempotently from the .npz + .json artifacts.
