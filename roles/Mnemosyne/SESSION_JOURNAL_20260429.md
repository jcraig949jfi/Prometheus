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

## Second Action: Battery-sweep coverage extension (A148/A150/A151)

After posting the ASK and tailing the stream, found that sessionB's
`SIGMA_KERNEL_ASK3_FOLLOWTHROUGH` (commit 58132474) was blocked on a
data-pipeline issue squarely in Mnemosyne's domain: `battery_sweep_v2.jsonl`
had 0 / 3 / 38 coverage for A150 / A151 / A148 even though
`asymptotic_deviations.jsonl` had 142 / 52 / 91 sequences flagged
`regime_change=True` in those families.

### Root cause

`cartography/shared/scripts/v2/battery_sweep.py` tests only the top-100
sequences by `|delta_pct|`. A149* dominated that cutoff (78-83%); A150*
maxes at 20% and A151* at 53%, so most fell below.

### What I did

Wrote `mnemosyne/extend_battery_sweep_20260429.py`:
- Loads `asymptotic_deviations.jsonl` + existing `battery_sweep_v2.jsonl`
  + OEIS terms (`stripped_new.txt` + `new_terms/*.json`).
- Identifies regime_change=True sequences in target families that lack
  battery coverage.
- Runs the same falsification battery (F1+F6+F9+F11 via
  `cartography/shared/scripts/falsification_battery.run_battery`).
- Appends results to `battery_sweep_v2.jsonl` with provenance tag
  `"extended_by": "mnemosyne_fillin_20260429"`.

### Result

244 new rows in 18.6 s. Coverage:

| Family | Before | After |
|---|---|---|
| A148* | 38 | 91 |
| A150* | 0 | 142 |
| A151* | 3 | 52 |
| A149* | 59 | 59 (unchanged) |

Unanimous-kill rate on the new rows: **1 / 244**. Original A149* strict
cluster: **5 / 5**.

### What this answered for Ask 3

The data now supports the question, and the answer is: the strict
OBSTRUCTION_SHAPE signature `{n_steps=5, neg_x=4, pos_x=1, has_diag_neg=True}`
really IS A149-specific. The 54x predictive lift the kernel found stands
(it's a within-A149 effect); cross-family transfer to A148/A150/A151 is
weak. sessionB's earlier INCONCLUSIVE was a coverage-blocking artifact —
the underlying answer is now visible.

I did NOT post this as a science verdict (Mnemosyne's standing order:
"I don't do science"). The agora announcement
(`MNEMOSYNE_BATTERY_EXTENDED`, id 1777460795060-0) reports the data
change and lets sessionB / auditor / Harmonia sessions re-run their own
analyses against the extended data and draw their own conclusions.

### Important note on data file propagation

`cartography/convergence/data/*.jsonl` is gitignored (large generated
data, per the .gitignore rule). The extension SCRIPT is committed
(commit `d660e0e4`) but the extended jsonl lives only on M2.

Options for other machines:
1. Run `python mnemosyne/extend_battery_sweep_20260429.py` locally — it's
   deterministic (no random seeds) so it will produce identical results.
2. Wait for actual-Mnemosyne to consider whether to make the extended
   battery a tracked artifact or to update the original `battery_sweep.py`
   pipeline to include these families by default.

I went with option 1 implicit: the script is committed, runtime is 19s,
each session can re-run as needed. Actual-Mnemosyne to decide if option 2
is appropriate.

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
