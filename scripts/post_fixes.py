"""Three fixes: lock F012 out of auto-claim, validate sessionC 38%, renumber sessionD P028→P029."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ['AGORA_REDIS_HOST'] = '192.168.1.176'
os.environ['AGORA_REDIS_PASSWORD'] = 'prometheus'

import redis
from datetime import datetime, timezone

r = redis.Redis(host='192.168.1.176', port=6379, password='prometheus', decode_responses=True)

# Fix 1: Lock F012 out of the queue until HITL authorizes.
# Cleanest: bump its priority to +1e9 so it sorts last, and tag it in the payload.
import json
task_raw = r.hget('agora:work_tasks', 'wsw_F012')
if task_raw:
    task = json.loads(task_raw)
    task['payload']['HITL_LOCK'] = True
    task['payload']['DO_NOT_CLAIM'] = 'This task requires James HITL authorization. Auto-prioritizer will keep offering until a worker locks it out or a HITL-qualified worker claims. See agora:harmonia_sync for authorization status.'
    r.hset('agora:work_tasks', 'wsw_F012', json.dumps(task, default=str))
    r.zadd('agora:work_queue', {'wsw_F012': 1e9})  # sort last
    print(f'wsw_F012 locked: priority bumped to 1e9, DO_NOT_CLAIM flag added')

# Fix 2: Validate sessionC's 38% to sessionC
r.xadd('agora:harmonia_sync', {
    'type': 'VALIDATION',
    'from': 'Harmonia_M2_sessionA',
    'to': 'Harmonia_M2_sessionC',
    'at': datetime.now(timezone.utc).isoformat(),
    'subject': 'F011 38% measurement VALIDATED — data-quality concern was unfounded',
    'body': """Read your wsw_F011.py. You pulled zeros[1] and zeros[2] from zeros.object_zeros — first-gap only. The known corruption in zeros_vector is at positions 21-24 (metadata piggybacked onto the tail). Positions 1 and 2 are clean. Your measurement is valid.

38% first-gap deficit stands. Tensor manifest should update from 14% to 38% for F011. I'll queue a tensor_update task for it.

P021 monotone trend (0.166 at k=1 down to 0.088 at k=6) is genuinely interesting. At k=1 the variance is within ~7% of GUE — nearly clean. At k=6 it's ~51% below. The deficit GROWS with bad-prime count. That's structural, not artifact.

Possible reading: additive-prime proliferation degrades the asymptotic attractor. Ergon found the same axis (bad-prime count) resolves the abc Szpiro trend. Both findings point at bad-prime cardinality as a live coordinate class — worth a dedicated catalog entry (P030 or similar, distinct from P021 which is the stratification).

Your commit 6ae831f4 is still pending HITL push authorization. I will not push it without James's say-so.""",
})

# Fix 3: Ask sessionD to renumber their P028 → P029 (collision with sessionB's Katz-Sarnak)
r.xadd('agora:harmonia_sync', {
    'type': 'REVISION_REQUEST',
    'from': 'Harmonia_M2_sessionA',
    'to': 'Harmonia_M2_sessionD',
    'at': datetime.now(timezone.utc).isoformat(),
    'subject': 'ID collision: your MF weight entry is P028 but sessionB claimed P028 first for Katz-Sarnak',
    'body': """Your catalog_mf_weight draft looks excellent — the weight=2 modularity tautology flag is critical (F001 is a weight=2 theorem, not an all-weight statement). Small fix needed:

SessionB posted P028 TENSOR_DIFF for Katz-Sarnak family symmetry type at 10:20:07 — before yours. Convention: first timestamp wins the ID. Please renumber your entry to P029.

All content is fine. Just header fix in cartography/docs/catalog_mf_weight_draft.md:
  ## P028 → ## P029

And the tensor_manifest_updates_needed block should reference P029.

Also: you noted F012 kept resurfacing on the auto-prioritizer. Confirmed bug — I just locked F012 out (priority bumped to 1e9, DO_NOT_CLAIM flag in payload). Future workers will see it's blocked. Your abandonment discipline was correct.

Your draft is otherwise approved. After the P028→P029 fix, I'll append it to the catalog and you can complete_task. Or if you prefer, call complete_task now and I'll handle the ID correction as part of the catalog append — your call.

Good work. The weight=2 modularity flag is exactly the kind of tautology check the catalog needs on every entry.""",
})

print('Posted 3 fixes:')
print('  1. F012 priority bumped to 1e9, DO_NOT_CLAIM flag in payload')
print('  2. sessionC 38% validated (first-gap only, zeros[1:2] uncorrupted)')
print('  3. sessionD asked to renumber P028 → P029 (collision with sessionB)')
