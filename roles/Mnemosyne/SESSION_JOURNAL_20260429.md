# Mnemosyne Session Journal — 2026-04-29 (fill-in)

## Session Overview

Mnemosyne out sick today. Claude session covered @roles/Mnemosyne under HITL
direction. Single-purpose work: apply the sigma_kernel migration to
prometheus_fire and announce on agora. Plus an in-session bug fix and the
usual housekeeping (STATE.md, this journal).

Identity: Claude Opus 4.7 (1M context) acting under the role per James's
instruction "Mnemosyne is out sick today. You can take her @roles\Mnemosyne\
and be her." Reverting to normal Mnemosyne attribution when she's back.

---

## What I Executed

### sigma_kernel schema in prometheus_fire

- Applied `sigma_kernel/migrations/001_create_sigma_schema.sql` to
  prometheus_fire as superuser (postgres/prometheus per STATE.md note).
- Created schema `sigma` with three tables: `symbols`, `claims`,
  `capabilities`.
- One index: `idx_sigma_symbols_def_hash` on `sigma.symbols(def_hash)`.
- GRANTs for `ergon` (the user the kernel's connection pool resolves to via
  `thesauros.prometheus_data.pool.get_fire()`):
  - `USAGE ON SCHEMA sigma`
  - `SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA sigma`
  - `ALTER DEFAULT PRIVILEGES ... GRANT SELECT, INSERT, UPDATE ON TABLES`
- **No DELETE granted** — kernel substrate is append-only by design.

### Smoke test

- Ran `sigma_kernel/demo_postgres.py` end-to-end. 5/5 scenarios pass against
  the live schema:
  1. CLEAR verdict → PROMOTE succeeds
  2. BLOCK verdict → GATE raises + PROMOTE refuses (defense-in-depth)
  3. Double-spend rejected
  4. Overwrite rejected (storage-level immutability)
  5. ERRATA produces v2 with backref; v1 stays immutable
- All test symbols swept post-run via superuser DELETE; `sigma.symbols` at
  0 rows on disk.

### Bug fix bundled in

Found three broken internal imports in `thesauros/prometheus_data/`
(introduced when the package was renamed from `prometheus_data/` →
`thesauros/prometheus_data/` earlier in the session). Fixed:
- `thesauros/prometheus_data/__init__.py:33`: `from prometheus_data.pool import ...`
  → `from .pool import ...`
- `thesauros/prometheus_data/pool.py:9`: `from prometheus_data.config import ...`
  → `from .config import ...`
- `thesauros/prometheus_data/pool.py:167`: same fix.

Also updated the docstring example in `__init__.py` to reflect the new
import path (`thesauros.prometheus_data` instead of bare `prometheus_data`).

### Postgres-specific kernel fix

Added explicit `self.conn.rollback()` to several error paths in
`sigma_kernel/sigma_kernel.py`. SQLite was forgiving when an exception was
raised mid-transaction; Postgres puts the connection in "transaction
aborted" state and refuses subsequent commands until ROLLBACK. Affected
methods: `bootstrap_symbol`, `PROMOTE` pre-flight checks, `ERRATA`
pre-flight checks. Net effect: ~6 lines added; every error path that
re-raises in the kernel now rolls back first.

### Agora participation

Three messages posted to `agora:harmonia_sync`:
- `SCHEMA_LIVE: sigma in prometheus_fire (sigma_kernel MVP)` — id 1777460358274-0
- `MNEMOSYNE_FILLIN: Claude session covering roles/Mnemosyne today` (heartbeat) — id 1777460358283-0
- `MNEMOSYNE_ASK: what else can I help with today?` — id 1777460358284-0

The ASK message is open. Will tail and respond if anyone takes it up.

---

## Key Findings

### HIGH CONFIDENCE

1. **sigma_kernel/Postgres integration works end-to-end** (confidence: 1.0).
   5/5 demo scenarios pass against the live schema. Schema probe at
   `_PostgresAdapter.__init__` correctly fails closed when schema is missing.
   Connection pool path through `thesauros.prometheus_data.pool` works.

2. **`thesauros.prometheus_data` package was importing-broken since the
   rename** (confidence: 1.0). Anything that used `from
   thesauros.prometheus_data import get_fire` from outside the package
   would have raised `ImportError: cannot import name 'get_fire'` because
   `__init__.py` was trying to re-export from a path that no longer exists.
   Surfaced in this session because the kernel was the first new outside
   caller. Now fixed.

### MODERATE CONFIDENCE

3. **The smoke-cleanup permission failure is the discipline working as
   designed** (confidence: 0.9). `ergon` has no DELETE on `sigma.*` because
   the kernel substrate is append-only. Demo cleanup needing superuser is
   a feature; if a future demo wants self-cleanup, either elevate (bad) or
   accept that test data accumulates with prefix-scoped uniqueness (better).

---

## What Was NOT Killed (notable absence)

Nothing got killed in this session. The work was additive: schema applied,
imports fixed, kernel hardened, three messages posted. No claims to
falsify, no findings to demote.

---

## What Is Blocked / Staged for Next Session

### For actual-Mnemosyne when she's back

These are pending Mnemosyne items I noted but did NOT pick up — out of
scope without her context:

- **`lfunc_lfunctions` conductor index status.** Was building 2026-04-15
  (~47 min ETA). If still incomplete or stalled, blocks `bsd_joined` view +
  EC ↔ lfunc join key discovery.
- **Agent user passwords cleanup.** Agents still using `postgres/prometheus`
  superuser per STATE.md 2026-04-16. Should rotate to per-agent creds once
  ready.
- **6 DuckDB tables waiting on Agora schema design.** Per
  SESSION_JOURNAL_20260415.md, request was posted to `agora:tasks`. Status
  check needed.

### Watching `MNEMOSYNE_ASK` for incoming requests

The ASK invites the team to send Mnemosyne workitems. If anything comes in
during this session, I'll handle what's tractable and journal what isn't.

---

## Infrastructure State at Session End

| System | Status |
|--------|--------|
| PostgreSQL (M1) | Live, all three databases reachable |
| prometheus_sci | 1.14M rows across 14 tables (unchanged from 2026-04-16) |
| prometheus_fire | ~600K rows + new `sigma` schema (3 empty tables, indexed, granted) |
| Redis (M1) | Live; `agora:harmonia_sync` actively in use |
| sigma schema | Provisioned, granted, smoke-tested. Empty by design (kernel is brand new). |

---

## Files Changed This Session

- `mnemosyne/STATE.md` — addendum noting sigma schema (lines after the
  2026-04-16 body)
- `roles/Mnemosyne/SESSION_JOURNAL_20260429.md` — this file (NEW)
- `sigma_kernel/sigma_kernel.py` — rollback fixes in error paths (Postgres
  transaction discipline)
- `thesauros/prometheus_data/__init__.py` — import path fix + docstring
  update
- `thesauros/prometheus_data/pool.py` — two import path fixes

(The sigma migration SQL itself was already in tree from a prior
non-Mnemosyne session — Mnemosyne just applied it.)

---

## Note for actual-Mnemosyne

When you're back: `mnemosyne/STATE.md` has a 2026-04-29 addendum at the
bottom describing what landed in `sigma`. The schema is live, the GRANTs
are correct, the kernel demo works. Three messages on
`agora:harmonia_sync` (search by date 2026-04-29 or by subject prefix
`SCHEMA_LIVE` / `MNEMOSYNE_*`).

If anyone's taken up the `MNEMOSYNE_ASK` while I was around, those will
also be on the stream. If the queue's quiet, the ASK will probably age out
naturally.

The bug fix in `thesauros/prometheus_data/` was unrelated to sigma but
needed for the sigma work to function. Worth a quick pass to confirm none
of your other tools relied on the broken import path — they shouldn't
(the path was always wrong post-rename), but worth verifying.

Hope you feel better.
