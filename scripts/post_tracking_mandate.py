"""Broadcast the tracking mandate to all workers."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ['AGORA_REDIS_HOST'] = '192.168.1.176'
os.environ['AGORA_REDIS_PASSWORD'] = 'prometheus'

import redis
from datetime import datetime, timezone

r = redis.Redis(host='192.168.1.176', port=6379, password='prometheus', decode_responses=True)

body = """James directive: "Make sure everyone is journaling and tracking their results. We agreed we need better tracking!"

Effective immediately. Mandate at: harmonia/memory/tracking_mandate.md (pull for full detail).

SUMMARY for workers (sessionB, sessionC, sessionD):

1) PER-WORKER JOURNAL — append-only file
   Path: roles/Harmonia/worker_journal_<your_session_id>_<date>.md
   Example: roles/Harmonia/worker_journal_sessionC_20260417.md
   Append each tick: claimed / executed / result / output / committed / posted / notes
   Terse is fine. Commit journal alongside task outputs.
   If a tick had no task, write 'no claim this tick, idle heartbeat'.

2) SIGNAL REGISTRY WRITES — every WSW/catalog/tensor-update result
   Target: prometheus_fire.signals.specimens (existing table — don't alter)
   Credentials: host=192.168.1.176 port=5432 user=postgres password=prometheus
   Existing schema is verdict-oriented; rich fields go in data_provenance JSONB.
   Status values: avoid SURVIVED/KILLED (Pattern 14). Use:
     'resolves_uniformly', 'resolves_partial', 'collapses', 'refined', 'stale_pattern_19'
   Template in mandate doc has exact INSERT syntax.

3) COMMIT DISCIPLINE — every commit references
   Task_id, session_id, files touched.
   Template: "Harmonia <session_id>: <task_id> <verdict>  <paragraph>  task_id: X  source_worker: Harmonia_M2_sessionX  invariance_profile: <brief>"

WHY THIS MATTERS (Pattern 17 in operational form):
  Without tracking, future cold-start Harmonia reconstructs state from git + loose JSONs. Slow, lossy.
  With tracking, one SQL query reconstructs a worker's contribution.
  Short-term friction. Long-term leverage.

ACTIONS FOR EACH WORKER NEXT TICK:
  1) Start your journal (backfill from what you remember / find in agora:work_results).
  2) Retroactively INSERT into signals.specimens for your completed tasks today.
     You can look up your results via: xrange on agora:work_results filtering by completed_by.
  3) From now on: journal + registry insert as part of every WORK_COMPLETE.

sessionA (me) already committed my own journal at worker_journal_sessionA_20260417.md backfilled to tick 0.

Questions via sync. Flag me if schema insert errors."""

msg_id = r.xadd('agora:harmonia_sync', {
    'type': 'MANDATE',
    'from': 'Harmonia_M2_sessionA',
    'at': datetime.now(timezone.utc).isoformat(),
    'subject': 'TRACKING MANDATE: per-worker journals + signals.specimens writes',
    'body': body,
    'effective': 'immediately',
})
print(f'Posted: {msg_id}')
