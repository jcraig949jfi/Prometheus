# GPU Reservation System — 2026-05-23

**Status:** shipped, smoke-tested end-to-end on M1 (RTX 5060 Ti detected, full lifecycle verified).
**Author:** Aporia
**Triggered by:** James 2026-05-23 — "We probably need a per-machine reservation system for GPU usage. Lock, unlock with TTL."

---

## What it is

A Postgres-backed, cross-machine, per-GPU lock with TTL semantics. Any agent on any machine that wants to use a GPU calls `acquire_gpu(machine, gpu_id, holder, ...)`. If the slot is free, they get a reservation; if not, they get None and can see who's holding it. Holders renew while working; if they die without renewing, the TTL expires and the slot frees automatically (lazy sweep on the next acquire).

No new agent. No new infrastructure. Library helpers in `scripts/agora_persist.py`; operator CLI at `scripts/gpu_reservation.py`. Schema is part of the same `agora.*` namespace as `research_queue` and `agent_heartbeats`.

## Why Postgres (not Redis, not flock, not flat files)

- **Cross-machine visibility**: a reservation made on M1 must be visible from M3. Postgres at 192.168.1.176:5432 is already the shared substrate.
- **Atomicity**: partial unique index `(machine, gpu_id) WHERE status='active' AND released_at IS NULL` enforces "at most one active reservation per slot" at the DB level. Race losers get `UniqueViolation`; helper catches and returns None. No application-level locking needed.
- **Durability**: survives reboots and process death. Per-machine flock files don't.
- **Already plumbed**: every agent on the program already imports `agora_persist` for heartbeats / log_work / research-queue ops. Zero new dependencies.
- Redis was the alternative; it has native TTL but lacks the partial-unique-index trick. Could be added later as a faster-cache layer if Postgres becomes a bottleneck (unlikely at single-digit-per-day reservation rate).

## The 5 helper functions

All in `scripts/agora_persist.py`:

```python
acquire_gpu(machine, gpu_id, holder, purpose=None,
            ttl_seconds=3600, holder_pid=None, tags=None) -> dict | None
release_gpu(reservation_id, holder) -> bool
renew_gpu(reservation_id, holder, ttl_seconds=3600) -> bool
list_gpu_reservations(machine=None, status='active',
                      include_released=False, limit=100) -> list
force_release_gpu(reservation_id, by, reason) -> bool   # admin override
sweep_expired_gpu_reservations() -> int                  # called lazily by acquire
```

Holder-name checks on `release_gpu` + `renew_gpu` protect against accidental release by another agent's mistake. They are NOT auth — we're on a trusted LAN. For real release by someone else, use `force_release_gpu` which records the override in `tags` for audit.

## Schema

```sql
CREATE TABLE agora.gpu_reservations (
    id BIGSERIAL PRIMARY KEY,
    machine TEXT NOT NULL,                  -- 'M1', 'M2', 'M3', 'M4'
    gpu_id TEXT NOT NULL,                   -- 'GPU0', 'GPU1', or UUID
    holder TEXT NOT NULL,                   -- 'Rhea', 'Talos', 'Apollo', ...
    holder_pid INTEGER,                     -- optional liveness check hint
    purpose TEXT,                           -- short description
    reserved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,        -- failsafe TTL
    last_renewed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    released_at TIMESTAMPTZ,                -- NULL = active
    status TEXT NOT NULL DEFAULT 'active',  -- active | released | expired
    tags JSONB
);

-- The load-bearing constraint:
CREATE UNIQUE INDEX idx_gpu_reservations_one_active_per_slot
    ON agora.gpu_reservations (machine, gpu_id)
    WHERE status = 'active' AND released_at IS NULL;
```

The partial unique index is the atomicity primitive. Without it, two concurrent acquires could both succeed; with it, the loser gets `UniqueViolation` (caught by `acquire_gpu`).

## TTL semantics

- Default `ttl_seconds = 3600` (1 hour). Per-call overridable.
- Holders should renew at roughly `ttl/3` to avoid losing the slot to a sweep. E.g., `ttl=14400` (4h) → renew every 1800s (30m).
- Sweep is lazy: every `acquire_gpu` call first runs `sweep_expired_gpu_reservations` to evict dead holders. No standalone sweeper daemon. (If acquire frequency is too low, an explicit periodic sweep is one cron line away.)
- A dead holder's slot frees within `ttl` seconds of death, max.

## Per-machine GPU enumeration

The CLI tool exposes `enumerate` which calls `pynvml` first, then falls back to `nvidia-smi --query-gpu=...`. Output gives `(gpu_id, name, uuid, memory_mb_total, memory_mb_free)`. Use this to know what GPU IDs are valid for the `gpu_id` parameter when acquiring.

Tested on M1 (SKULLPORT): detected RTX 5060 Ti, GPU0, 16 GB total, 15.1 GB free (no GPU work running). Uses nvidia-smi (pynvml not installed; that's fine).

## CLI usage

```bash
# One-time, per database:
python scripts/gpu_reservation.py init

# What GPUs does this machine have?
python scripts/gpu_reservation.py enumerate

# Who's holding what right now?
python scripts/gpu_reservation.py list
python scripts/gpu_reservation.py list --machine M2

# Reserve / renew / release:
python scripts/gpu_reservation.py acquire M2 GPU0 Talos --purpose "LoRA run 1" --ttl 14400
python scripts/gpu_reservation.py renew <id> Talos --ttl 14400
python scripts/gpu_reservation.py release <id> Talos

# Admin override (records audit info in tags):
python scripts/gpu_reservation.py force-release <id> --by Aporia --reason "stuck job"

# Manual sweep (normally automatic):
python scripts/gpu_reservation.py sweep
```

## Required usage pattern for agents

```python
from agora_persist import acquire_gpu, renew_gpu, release_gpu

res = acquire_gpu(
    machine=socket.gethostname()[:2],  # 'M1' / 'M2' / 'M3' / 'M4'
    gpu_id="GPU0",
    holder="Talos",                    # who is registering
    purpose="Talos LoRA run X",
    ttl_seconds=14400,                 # 4 hours
    holder_pid=os.getpid(),
)
if not res:
    log.error("Could not acquire GPU; another holder. See: gpu_reservation.py list")
    return

try:
    train_with_periodic_renewer(res, renew_every=1800)
finally:
    release_gpu(res["id"], holder="Talos")
```

A `gpu_reserved(...)` context manager that wraps acquire + thread-renewer + release is a natural Phase-1 helper if multiple training runs end up wanting the same pattern. Not needed yet.

## Known limitations

- **Process-death detection**: the only mechanism is TTL. If a trainer dies and TTL is set to 4h, the slot is dead for up to 4h. Mitigation: agents should set short TTLs (1h) and renew aggressively (every 20m) — the dead-slot window shrinks to ≤1h.
- **No GPU-fraction sharing**: this is whole-GPU reservation only. If the substrate ever wants to share a GPU between two jobs (e.g., a small inference + a small fine-tune), this design needs extending (sub-IDs, memory budgets). Not needed for current scale.
- **Trust**: no auth. A misbehaving agent can release someone else's reservation only via `force_release_gpu` (which leaves an audit trail). The normal `release_gpu` checks the holder name as a guard against accidents, not against malice.
- **Single Postgres**: if the Postgres at 192.168.1.176:5432 is down, no reservations can be made or released. The whole substrate already depends on that Postgres for `research_queue` + `agent_heartbeats`; no new dependency added.

## What this unblocks

- **Talos Phase 1** (LoRA training) — config now declares `gpu_reservation.required: true` per `agents/talos/training/lora_config.yaml`. The Phase-1 GPU-loop owner reads this config and calls `acquire_gpu` before training starts.
- **Rhea fine-tuning runs** — should adopt the same pattern.
- **Apollo organism evolution** — currently runs continuously; could hold a long-lived reservation with very long TTL + frequent renew, OR could mark its GPU as "permanently held" via a special long-TTL row.
- **Future Learner training** — any GPU-bound work coordinates here.

## What's NOT in this system (deferred)

- Queue / wait-for-slot semantics. Right now `acquire_gpu` is non-blocking: success or None. If callers want to wait, they poll. A "request and notify on free" layer (with priority) is a Phase 2 addition if multiple agents start contending.
- GPU performance metrics (utilization, memory, temperature). The `enumerate` CLI shows static info; live telemetry per GPU would be a separate cron writing to a sibling table.
- Cross-machine cost accounting (which agent burned how many GPU-hours). The `tags` JSONB column gives a place to record this once we want it; aggregation is a SQL query, not new infrastructure.

— Aporia, 2026-05-23
