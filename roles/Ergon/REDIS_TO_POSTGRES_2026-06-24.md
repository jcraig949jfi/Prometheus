# Redis → Postgres bus migration (2026-06-24)

**Author:** Ergon · host M1 (`192.168.1.202`)
**Trigger:** James — "Redis is too difficult to keep running under WSL. I have to
keep starting it manually. We should use postgres for now."
**Status:** Foundation DONE and tested. Bus now runs on Postgres for everything that
goes through `get_redis()`. Remaining: repoint 36 files that make their own
`redis.Redis(...)` connection (mechanical, handoff below).

## What was built

`thesauros/prometheus_data/pg_redis.py` — **PgRedis**, a Postgres-backed drop-in for
the redis-py subset the substrate actually uses (audited 2026-06-24):
- streams `xadd/xrange/xrevrange/xread/xlen`, hashes `hset/hget/hgetall/hdel`,
  sorted sets `zadd/zrange/zrevrange/zrangebyscore`, sets `sadd/smembers`,
  kv+ttl `get/set/setex/expire/delete/keys/incr`, plus `ping`/`pipeline`.
- `decode_responses` configurable (bytes for `get_redis()` callers, str for callers
  that made their own `decode_responses=True` connection).
- Stream ids are `'<ms>-<seq>'` (wall-clock ms) so existing catch-up logic like
  `xrange(min=f"{cutoff_ms}-0")` works unchanged. `xread(block=...)` emulated by a
  short poll loop (Postgres has no blocking pop). No consumer groups / pub/sub /
  clustering — nothing uses them.

Backing store: **`prometheus_fire` schema `bus`** — tables `stream_entries`, `hashes`,
`zsets`, `sets`, `kv`. `lmfdb` role granted read+write on `bus` (no superuser needed;
PgRedis connects as `lmfdb`).

Wiring in `thesauros/prometheus_data/pool.py`:
- `get_redis()` now returns a Postgres-backed PgRedis by default. Set env
  `PROMETHEUS_USE_REDIS=1` to use a real Redis if one is ever running again
  (fully reversible). Returns `None` only if even Postgres is down.
- New `get_bus(decode_responses=False)` — the migration target for direct-connect
  callers. Exported from `thesauros.prometheus_data`.

Verified: full roundtrip of every op in both decode modes; `get_redis()` returns
PgRedis with Redis down; post/read cycle on `agora:*` works. psycopg2 installed.

## Remaining: repoint 36 direct-connect files (handoff)

These bypass `get_redis()` and build their own client, so they still try (and fail to
reach) real Redis. Each needs the same one-line change:

    # before
    import redis
    r = redis.Redis(host=..., port=..., password=..., decode_responses=True)
    # after
    from thesauros.prometheus_data import get_bus
    r = get_bus(decode_responses=True)   # keep whatever decode flag the file used

Files (by owner):
- **Harmonia** (most): `harmonia/agents/_base.py`, `harmonia/agents/_scorer.py`,
  `harmonia/memory/sync_handshake.py`, `harmonia/src/domain_index.py`,
  `harmonia/sweeps/retrospective.py`, `harmonia/composers/{enumerate,scorer}.py`,
  `harmonia/memory/diagnostics/validate_retraction_registry.py`, and the one-off
  posters under `harmonia/tmp/*` and `scripts/{tick*,post_*,harmonia_conductor,
  harmonia_e_status_post,authorize_and_seed,session_telemetry,portfolio_monitor}.py`.
- **Cartography**: `cartography/viewer/server.py`.
- **Ergon**: `thesauros/prometheus_data/pool.py` (intentional — the `PROMETHEUS_USE_REDIS`
  fallback path; leave as is).
- Skip: `thesauros/migrate_p3_duckdb.py` (one-time migration, retired).

Validation after repointing a file: run it; posts should land in `bus.stream_entries`
(`SELECT stream,count(*) FROM bus.stream_entries GROUP BY 1`).

## Notes

- No data migration needed — Redis was down (its data is ephemeral and was already
  lost on restarts); this is a clean-slate backend swap. New bus traffic accrues in PG.
- `landscape:by_curvature` (the one sorted-set the old docstring cited) had no live
  Redis data; the source `landscape` rows are already in `charon_duckdb.landscape`.
