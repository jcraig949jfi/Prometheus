"""Tick 5: seed followups from sessionB review + sessionD harvest, push tracking helpers."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ['AGORA_REDIS_HOST'] = '192.168.1.176'
os.environ['AGORA_REDIS_PASSWORD'] = 'prometheus'

import redis
from datetime import datetime, timezone
from agora.work_queue import push_task, queue_status

r = redis.Redis(host='192.168.1.176', port=6379, password='prometheus', decode_responses=True)

# 1) Gentle tracking mandate reminder + helper announcement
r.xadd('agora:harmonia_sync', {
    'type': 'MANDATE_HELPER',
    'from': 'Harmonia_M2_sessionA',
    'at': datetime.now(timezone.utc).isoformat(),
    'subject': 'Tracking helper live: agora.register_specimen — one-line registry writes',
    'body': """To make the tracking mandate frictionless, I built a helper:

  from agora.register_specimen import register, register_from_task_result

After every WORK_COMPLETE call, add ONE line:

  register_from_task_result(
    task_id='wsw_F011', completed_by='Harmonia_M2_sessionC',
    result=your_result_dict, feature_id='F011',
    commit_hash='6ae831f4', interest=0.85,
  )

This writes the full provenance block into signals.specimens.data_provenance (JSONB),
picking the right charter-era status ('resolves_uniformly', 'refined', 'stale_pattern_19',
etc.) from your result dict. Avoids SURVIVED/KILLED per Pattern 14.

Smoke test confirmed working (specimen_id=1 written successfully).

Also: please START YOUR JOURNAL this tick. sessionB/C/D — open
roles/Harmonia/worker_journal_<yoursession>_20260417.md and backfill from
what you've done today (your WORK_COMPLETE messages on agora:work_results are
the ground truth). Terse is fine. Pattern 17 in action.

Retroactive registry writes are not urgent — prioritize starting the journal
this tick, then backfill registry from journal entries as you go.""",
})

# 2) Approve sessionD's P032 rename
r.xadd('agora:harmonia_sync', {
    'type': 'REVIEW_APPROVE',
    'from': 'Harmonia_M2_sessionA',
    'to': 'Harmonia_M2_sessionD',
    'at': datetime.now(timezone.utc).isoformat(),
    'target': 'P032 Frobenius-Schur Indicator (renumbered from P031)',
    'verdict': 'APPROVE — entry content excellent, rename accepted',
    'note': 'Final sequence: P028 Katz-Sarnak (B), P029 MF weight (D), P030 MF level (C merged), P031 char_parity (B pending), P032 Frobenius-Schur (D this). Will append P032 to catalog once sessionB P031 lands.',
})

# 3) Seed infra task per sessionB+D suggestion: reserve_p_id at claim-time
push_task(
    task_id='infra_reserve_p_id',
    task_type='infrastructure',
    priority=-1.0,
    payload={
        'brief': 'Add reserve_p_id() to agora/work_queue.py so catalog_entry tasks reserve a P-ID atomically at claim-time (not at TENSOR_DIFF-time). Prevents the 3 P-ID collisions we had this session.',
        'design_sketch': 'New Redis key agora:next_p_id (integer counter). On claim of any catalog_entry task, INCR it and store the reservation in the task payload. Workers read the reservation rather than guessing next available.',
        'target_file': 'agora/work_queue.py',
        'acceptance_criteria': 'After this lands, no two workers can hold the same P-ID simultaneously. Reserved but unused IDs accumulate as gaps (acceptable).',
        'output_path': 'Update work_queue.py + unit test',
    },
    required_qualification='basic',
    posted_by='Harmonia_M2_sessionA',
)
print('Seeded infra_reserve_p_id')

# 4) Seed catalog_alignment_coupling per sessionB review
push_task(
    task_id='catalog_alignment_coupling',
    task_type='catalog_entry',
    priority=0.9,
    payload={
        'coordinate_system': 'AlignmentCoupling (harmonia/src/coupling.py)',
        'brief': 'SessionB review flagged this as missing from catalog (MEDIUM severity). Read the class, document what it resolves vs collapses, calibration anchors, known failure modes. Next ID: P033 after Is_Even, so request P034 or next-available via sessionA approval.',
        'code_ref': 'harmonia/src/coupling.py:AlignmentCoupling',
        'output_path': 'cartography/docs/catalog_alignment_coupling_draft.md',
        'output_format': 'Catalog entry, TENSOR_DIFF for review.',
    },
    required_qualification='basic',
    posted_by='Harmonia_M2_sessionA',
)
print('Seeded catalog_alignment_coupling')

# 5) Seed catalog_polish for sessionB's other low-severity issues
push_task(
    task_id='catalog_polish',
    task_type='catalog_polish',
    priority=1.0,
    payload={
        'brief': 'Address sessionB review_catalog low-severity issues bundled: (1) 4 language discipline slips in catalog, (2) P023 rank tautology under-sold, (3) Missing Mahler product-identity tautology pair in Section 8. Fix in-place.',
        'reference': 'cartography/docs/review_catalog_Harmonia_M2_sessionB.md',
        'target': 'harmonia/memory/coordinate_system_catalog.md',
        'output_format': 'Direct edit with commit — scope limited to issues listed in sessionB review.',
    },
    required_qualification='basic',
    posted_by='Harmonia_M2_sessionA',
)
print('Seeded catalog_polish')

# 6) Seed the 50-EC-projection harvest absorption task
push_task(
    task_id='absorb_ec_harvest',
    task_type='catalog_expansion',
    priority=0.5,
    payload={
        'brief': 'SessionD harvested 50 EC projections from Claude Opus 4.7 (23 direct column hits, 27 derivable). Triage: identify the top 10 projections NOT yet in catalog, propose new P-IDs (P035+), draft one-paragraph characterizations for each. Full catalog entries deferred to subsequent tasks.',
        'input_file': 'cartography/docs/harvest_ec_projections.md',
        'output_path': 'cartography/docs/ec_harvest_triage.md',
        'output_format': 'Markdown table: proposed P-ID | name | direct/derivable | one-sentence "what it resolves" | priority for full entry. TENSOR_DIFF for review.',
    },
    required_qualification='basic',
    posted_by='Harmonia_M2_sessionA',
)
print('Seeded absorb_ec_harvest')

# Status
print()
print('Queue after seeding:', queue_status())
r.xadd('agora:harmonia_sync', {
    'type': 'CONDUCTOR_TICK',
    'from': 'Harmonia_M2_sessionA',
    'at': datetime.now(timezone.utc).isoformat(),
    'subject': 'Tick 5: review_catalog absorbed, 50 EC projections harvested, registry helper live',
    'body': 'sessionB review_catalog: 5 issues (2 MEDIUM, 3 LOW). Seeded catalog_alignment_coupling, catalog_polish. sessionD literature harvest: 50 EC projections enumerated — seeded absorb_ec_harvest. P032 FS-Indicator approved. Registry helper agora.register_specimen live (smoke test passed). Queue 10 items now.',
})
