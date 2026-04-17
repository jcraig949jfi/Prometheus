"""Authorize F012, unlock it, seed more tasks for the parallel crew."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ['AGORA_REDIS_HOST'] = '192.168.1.176'
os.environ['AGORA_REDIS_PASSWORD'] = 'prometheus'

import redis
from datetime import datetime, timezone
from agora.work_queue import push_task, queue_status

r = redis.Redis(host='192.168.1.176', port=6379, password='prometheus', decode_responses=True)

# ---- 1. UNLOCK F012 ----
task_raw = r.hget('agora:work_tasks', 'wsw_F012')
if task_raw:
    task = json.loads(task_raw)
    # Remove the lock flags
    task['payload'].pop('HITL_LOCK', None)
    task['payload'].pop('DO_NOT_CLAIM', None)
    task['payload'].pop('WARNING', None)
    task['payload']['HITL_AUTHORIZATION'] = 'Authorized by James 2026-04-17. Any qualified worker may claim.'
    r.hset('agora:work_tasks', 'wsw_F012', json.dumps(task, default=str))
    # Restore original priority -9 (urgent)
    r.zadd('agora:work_queue', {'wsw_F012': -9.0})
    print('wsw_F012 UNLOCKED: priority -9, HITL authorization recorded in payload')

# ---- 2. Announce F012 authorization on sync ----
r.xadd('agora:harmonia_sync', {
    'type': 'AUTHORIZATION',
    'from': 'Harmonia_M2_sessionA',
    'at': datetime.now(timezone.utc).isoformat(),
    'subject': 'F012 AUTHORIZED by James',
    'body': """James authorized the F012 run. Task wsw_F012 is now unlocked on the queue at priority -9 (urgent). Any qualified worker may claim. SessionB previously held HANDOFF authority — if you want to claim it, go. Otherwise first-qualified-worker takes it.

Target: H85 Möbius x aut_grp permutation null audit. Design as sessionB specced at 1776419377755-1:
  - Fix object set = genus-2 curves with g2c data and known aut_grp
  - Compute Möbius-on-abs_disc stratified by aut_grp, record baseline |z| per stratum
  - Shuffle aut_grp labels 1000x, re-measure, check survival and per-stratum carriers

Projection: P022 × P040 per tensor. Expected: either SURVIVES (real object-level coupling, aut_grp is the resolving axis) or KILLED (distributional artifact).""",
})

# ---- 3. Seed more tasks ----
new_tasks = [
    # More weak signal walks
    {
        'task_id': 'wsw_F010',
        'task_type': 'weak_signal_walk',
        'priority': -8.0,
        'payload': {
            'specimen_id': 'F010',
            'specimen_label': 'NF backbone via Galois-label coupling',
            'target_projections': ['P010', 'P020', 'P021', 'P042', 'P052'],
            'method': 'Apply each listed projection to the NF↔Artin Galois-label coupling. Record invariance profile. Use P010 baseline from prior ρ=0.40 z=3.64 result. Data: nf_fields + artin_reps via joint Galois label.',
            'output_path': 'cartography/docs/wsw_F010_results.json',
            'note': 'Verify whether the Galois-label coupling survives conductor conditioning (P020), bad-prime stratification (P021), and preprocessing via prime decontamination (P052).',
        },
        'expected_output': {'schema': 'per_projection invariance dict + shape summary'},
        'required_qualification': 'basic',
    },
    {
        'task_id': 'wsw_F013',
        'task_type': 'weak_signal_walk',
        'priority': -7.0,
        'payload': {
            'specimen_id': 'F013',
            'specimen_label': 'Zero spacing rigidity vs rank (slope=-0.0019, R²=0.399)',
            'target_projections': ['P020', 'P021', 'P024', 'P025', 'P042', 'P051'],
            'method': 'Retest Pattern: spacing variance decreases linearly with rank. Add preprocessing (P051 N(T) unfolding, P042 feature permutation). Check if the rank-coupling survives conductor conditioning.',
            'output_path': 'cartography/docs/wsw_F013_results.json',
        },
        'required_qualification': 'basic',
    },
    {
        'task_id': 'wsw_F014',
        'task_type': 'weak_signal_walk',
        'priority': -6.0,
        'payload': {
            'specimen_id': 'F014',
            'specimen_label': 'Lehmer spectrum gap (4.4% between bound and next smallest Mahler measure)',
            'target_projections': ['P053', 'P023', 'P021', 'P020'],
            'method': 'Apply Mahler measure projection (P053) stratified by degree, bad_primes count, conductor. Verify the 4.4% gap persists across all strata. Check for degree-dependent structure in the gap width.',
            'output_path': 'cartography/docs/wsw_F014_results.json',
            'data_source': 'nf_fields on lmfdb mirror (all 2.4M+ rows)',
        },
        'required_qualification': 'basic',
    },

    # More catalog entries (filling Section 9 gaps)
    {
        'task_id': 'catalog_mf_level',
        'task_type': 'catalog_entry',
        'priority': 0.5,
        'payload': {
            'coordinate_system': 'MF level stratification',
            'brief': 'Document splitting by mf_newforms.level. What features resolve? Complement catalog_mf_weight. Check tautology pair: level and conductor for EC L-functions. Use next available P-ID (P030 or later — check current catalog for max assigned).',
            'output_path': 'cartography/docs/catalog_mf_level_draft.md',
            'output_format': 'Catalog entry, post as TENSOR_DIFF for review.',
        },
        'required_qualification': 'basic',
    },
    {
        'task_id': 'catalog_character_parity',
        'task_type': 'catalog_entry',
        'priority': 0.6,
        'payload': {
            'coordinate_system': 'MF character parity stratification',
            'brief': 'Document splitting by char_parity (0 or 1). What features does this resolve in the Dirichlet/MF zero structure? Connect to Katz-Sarnak symmetry types (P028).',
            'output_path': 'cartography/docs/catalog_character_parity_draft.md',
            'output_format': 'Catalog entry, TENSOR_DIFF for review.',
        },
        'required_qualification': 'basic',
    },
    {
        'task_id': 'catalog_artin_indicator',
        'task_type': 'catalog_entry',
        'priority': 0.7,
        'payload': {
            'coordinate_system': 'Frobenius-Schur Indicator stratification',
            'brief': 'Document splitting artin_reps by Indicator field. What does Frobenius-Schur +1 vs -1 vs 0 resolve about the representation? Check tautology: Indicator correlates with Is_Even for small dimensions.',
            'output_path': 'cartography/docs/catalog_artin_indicator_draft.md',
            'output_format': 'Catalog entry, TENSOR_DIFF for review.',
        },
        'required_qualification': 'basic',
    },

    # Frontier-model literature harvest task
    {
        'task_id': 'harvest_ec_complexity_projections',
        'task_type': 'literature_harvest',
        'priority': 1.5,
        'payload': {
            'brief': 'Query a frontier model: "List all the ways mathematicians measure complexity or structure of elliptic curves. Include both classical invariants (rank, regulator, etc.) and less-used projections from 1970s-2000s literature. Return 30-50 projections."',
            'method': 'Prompt the model once with that exact question. Do NOT ask the model to validate or judge. Just enumerate. Record each projection with: name, year first used, what it resolves (model\'s claim), what data LMFDB has for it (you check).',
            'output_path': 'cartography/docs/harvest_ec_projections.md',
            'output_format': 'Markdown table. One row per projection. Columns: Name, Year, Resolves, LMFDB column/derivable, Checked-by-you',
            'model_note': 'Claude Opus via API. Use keys.get_key(\"CLAUDE\") for the key. Single API call, cap at ~2000 tokens.',
        },
        'required_qualification': 'basic',
    },

    # Tensor update task (the F011 deficit correction)
    {
        'task_id': 'tensor_update_F011_deficit',
        'task_type': 'tensor_update',
        'priority': -5.0,
        'payload': {
            'specimen': 'F011',
            'change': 'Update tensor manifest + pattern_library.md Pattern 8 to reflect sessionC\'s wsw_F011 measurement: 38% first-gap deficit (up from 14%), with P021 monotone trend (0.166 at k=1 → 0.088 at k=6). Add note that 7 projections (P050, P051, P021, P023, P024, P025, P026) all show +1 invariance.',
            'files_to_update': ['harmonia/memory/build_landscape_tensor.py', 'harmonia/memory/pattern_library.md'],
            'source_of_truth': 'cartography/docs/wsw_F011_results.json (commit 6ae831f4)',
            'output_path': 'Update in place, post diff as TENSOR_DIFF for review.',
        },
        'required_qualification': 'basic',
    },
]

for t in new_tasks:
    push_task(
        task_id=t['task_id'],
        task_type=t['task_type'],
        payload=t['payload'],
        priority=t['priority'],
        required_qualification=t['required_qualification'],
        expected_output=t.get('expected_output'),
        posted_by='Harmonia_M2_sessionA',
    )
    print(f"  seeded {t['task_id']} priority {t['priority']}")

# ---- 4. Post the 4-minute loop plan ----
loop_body = """James authorized 4-minute loops for all 4 instances. Coordinated cycle plan:

EACH TICK (every 4 min), each instance does:

sessionA (conductor + reviewer):
  1. Read last 20 sync messages since last tick
  2. Handle any unqualified PINGs via issue_challenge
  3. Review any pending TENSOR_DIFFs or revision requests
  4. steal_stale_claims() — return timed-out claims to queue
  5. If queue < 3 tasks, seed more from the backlog
  6. Post queue status summary if sync is quiet

sessionB, sessionC, sessionD (workers):
  1. Read sync messages addressed to you (revision requests, approvals)
  2. If you have an open task, progress it
  3. If no open task, claim_task(your_name) — highest priority non-blocked
  4. Execute, post WORK_COMPLETE
  5. Post heartbeat on sync if you had nothing to do this tick

Discipline per tick:
  - No git push without explicit HITL from James on a per-commit basis
  - Abandon tasks cleanly if you can't progress (reason in abandon message)
  - Keep status posts terse (1-line summary per tick is fine)
  - Watch for revision requests from sessionA — they often matter more than new claims

F012 is now UNLOCKED on the queue at priority -9. sessionB had prior HANDOFF authority. First qualified worker to claim it executes.

Queue currently has these tasks seeded (after F012 unlock and new seeds):
  wsw_F012 (-9, urgent)
  wsw_F010 (-8)
  wsw_F013 (-7)
  wsw_F014 (-6)
  tensor_update_F011_deficit (-5, high value)
  catalog_artin_dim (2)
  catalog_mf_level (0.5)
  catalog_character_parity (0.6)
  catalog_artin_indicator (0.7)
  harvest_ec_complexity_projections (1.5)
  review_catalog (3, pending)
  ingest_codata (5, blocked on Mnemosyne)

11 tasks queued, 3-4 workers, 4-minute ticks. Expected throughput: ~3 tasks per tick across the crew. The queue drains in ~4 ticks (~16 min). I'll seed more as we go."""

r.xadd('agora:harmonia_sync', {
    'type': 'LOOP_PLAN',
    'from': 'Harmonia_M2_sessionA',
    'at': datetime.now(timezone.utc).isoformat(),
    'subject': 'James authorized 4-min loops — coordinated cycle plan',
    'body': loop_body,
})

print('\nAll posted. Queue status:')
status = queue_status()
for k, v in status.items():
    print(f'  {k}: {v}')
