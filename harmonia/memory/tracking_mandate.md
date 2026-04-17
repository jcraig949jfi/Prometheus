# Tracking Mandate — Per-Worker Journals and Registry Writes
## Effective: 2026-04-17, from James
## Author: Harmonia_M2_sessionA (conductor)

---

## The problem

We're moving fast. 4 instances in parallel, 15+ completions in a single hour.
The *outputs* are landing (JSON results, catalog drafts, tensor updates) but
the *provenance chain* — who did what when, and what they discovered — is
scattered across Agora messages, git history, and loose JSON files.

That's Pattern 17 (language and organization bottleneck) in operational form.
If we can't reconstruct "what did sessionD find about F014 between 10:54 and 11:00"
without grepping 6 different files, we're accumulating tech debt on our own
understanding. Bad for future-Harmonia, bad for us now.

James's directive: **Make sure everyone is journaling and tracking their results.**

---

## Two tracking requirements

### Requirement 1: Per-session journals (like mine)

Every worker instance maintains a single running journal for their session at:

    roles/Harmonia/worker_journal_<session_id>_<date>.md

For example: `roles/Harmonia/worker_journal_sessionC_20260417.md`.

**Structure** (append at end of each tick):

```markdown
# Worker Journal — Harmonia_M2_sessionC — 2026-04-17

## Tick N @ HH:MM UTC
- Claimed: <task_id>
- Executed: <one-line what I did>
- Result: <verdict / summary>
- Output: <file path(s)>
- Committed: <commit hash or "none">
- Posted: <sync stream msg_id of WORK_COMPLETE>
- Notes: <flags, discrepancies, followup suggestions, ≤3 lines>

## Tick N+1 @ HH:MM UTC
...
```

**Rules:**
- Append only (never edit prior ticks)
- Terse is fine — journal is for auditability, not prose
- If a tick had no task, write "no claim this tick, idle heartbeat" (prevents gap mystery)
- Git-commit the journal alongside your task outputs

### Requirement 2: Signal registry writes

Every Weak Signal Walk, Catalog Entry, or Tensor Update MUST ALSO write a row
to `prometheus_fire.signals.specimens`. The Postgres schema exists (sessionA
built it). The discipline has been: workers write JSON to
`cartography/docs/wsw_*.json` but NOT the Postgres row.

**From now on:**

**Existing schema** (verified 2026-04-17, don't alter — it's Mnemosyne's):

```
signals.specimens (
  specimen_id      BIGINT PRIMARY KEY,
  claim            TEXT,
  status           TEXT,
  interest         DOUBLE PRECISION,
  kill_test        TEXT,
  domain_a         TEXT,
  domain_b         TEXT,
  created_at       TIMESTAMPTZ DEFAULT NOW(),
  killed_at        TIMESTAMPTZ,
  data_provenance  JSONB   -- *** THIS IS WHERE THE CHARTER-ERA FIELDS LIVE ***
)
```

The schema predates the charter (verdict-oriented). The `data_provenance` JSONB
column is where we put projection, feature_type, invariance_profile, etc. This
avoids stepping on Mnemosyne's ownership.

**Standard insert for a Weak Signal Walk result:**

```python
import psycopg2, json
conn = psycopg2.connect(host='192.168.1.176', port=5432, dbname='prometheus_fire',
                        user='postgres', password='prometheus')
cur = conn.cursor()

# `status` values: avoid raw SURVIVED/KILLED (Pattern 14). Use:
#   'resolves_uniformly' (uniform +1 across projections)
#   'resolves_partial'   (some projections +1, some -1)
#   'collapses'          (all tested projections -1)
#   'refined'            (signal survives but original magnitude was wrong)
#   'stale_pattern_19'   (original claim doesn't reproduce under clean measure)

# Map tensor feature_id into claim/domain_a (hacky but works with existing schema)
cur.execute("""
INSERT INTO signals.specimens
  (claim, status, interest, kill_test, domain_a, domain_b, data_provenance)
VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
RETURNING specimen_id
""", (
    'F011 GUE first-gap deficit — n=2M walk',                              # claim
    'resolves_uniformly',                                                   # status
    0.85,                                                                   # interest (0-1, my judgment)
    None,                                                                   # kill_test (null = not killed)
    'elliptic_curves',                                                      # domain_a
    'L-function_zeros',                                                     # domain_b
    json.dumps({                                                            # data_provenance (rich)
        'feature_id': 'F011',                                               # tensor ref
        'projections': ['P050','P051','P021','P023','P024','P025','P026'],
        'feature_type': 'flat_below_gue',                                   # ridge/edge/flat/fold/singularity
        'invariance_profile': {'P050':+1,'P051':+1,'P021':+1,'P023':+1,
                               'P024':+1,'P025':+1,'P026':+1,'P027':-1},
        'effect_size': 0.110,                                               # raw measurement
        'z_score': -383.0,
        'p_value': 0.0,
        'n_samples': 2009089,
        'machinery_required': 'balanced per-rank stratification + N(T) unfold',
        'tautology_check': {'checked': True, 'formula_lineage_overlap': False},
        'source_task': 'wsw_F011',                                          # work_queue task_id
        'source_commit': '6ae831f4',                                        # git hash
        'source_worker': 'Harmonia_M2_sessionC',
        'output_file': 'cartography/docs/wsw_F011_results.json',
    }),
))
specimen_id = cur.fetchone()[0]
conn.commit()
print(f'Registered specimen {specimen_id}')
```

**If a worker hits an insert error** (permission denied, schema mismatch):
flag sessionA on sync — will investigate. Schema is read-write for the postgres
user at `signals.specimens`.

### Requirement 3: Commit discipline

Every worker commit must reference:
- The task_id it completes
- The session_id of the worker
- The files touched

Standard commit message template:

```
Harmonia <session_id>: <task_id> <verdict>

<one paragraph what was done and found>

task_id: <task_id>
source_worker: Harmonia_M2_session<X>
invariance_profile: <brief summary>
```

---

## What I (sessionA) will do

1. Push this mandate to sync channel so all workers see it.
2. Start my own journal at `roles/Harmonia/worker_journal_sessionA_20260417.md` backfilled from my decisions log + this tick's action.
3. Confirm signals.specimens schema is live (or create it if not) before demanding workers use it.
4. Next conductor tick: verify each worker has started their journal, gently remind if not.
5. Update worker_protocol.md to make these requirements authoritative for future cold-start instances.

---

## Why this matters

Without journaling and registry writes:
- **Future cold-start Harmonia** has to reconstruct state from git history + JSON files.
  Slow and lossy.
- **James** can't answer "what did the team do between 10:30 and 11:00" in under 30 seconds.
- **Pattern 19** gets worse: entries without provenance accumulate. We've seen the cost.

With them:
- `SELECT * FROM signals.specimens WHERE source_worker='Harmonia_M2_sessionC'` tells you
  everything sessionC found in a single query.
- `cat roles/Harmonia/worker_journal_*_20260417.md` gives you the narrative.
- Cold-restore Harmonia reads journal + registry and is at ~95% instead of 80%.

Short-term friction. Long-term leverage.

---

*Tracking Mandate v1.0 — 2026-04-17*
