"""Conductor tick response: seed Liouville side-check, F013 tensor update, log decisions."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ['AGORA_REDIS_HOST'] = '192.168.1.176'
os.environ['AGORA_REDIS_PASSWORD'] = 'prometheus'

import redis, json
from datetime import datetime, timezone
from agora.work_queue import push_task, queue_status, steal_stale_claims

r = redis.Redis(host='192.168.1.176', port=6379, password='prometheus', decode_responses=True)

# 1) Steal stale
stolen = steal_stale_claims()
print(f'Stale claims returned: {len(stolen)}')

# 2) Seed Liouville side-check task — critical followup to F012 kill
push_task(
    task_id='liouville_side_check_F012',
    task_type='weak_signal_walk',
    priority=-10.0,  # most urgent
    payload={
        'specimen_id': 'F012_liouville',
        'specimen_label': 'H85 Möbius-vs-Liouville definitional audit',
        'target_projections': ['P022', 'P040'],
        'method': 'Re-run sessionB wsw_F012 with LIOUVILLE λ(n) = (-1)^Ω(n) INSTEAD of Möbius μ(n). Liouville is ±1 everywhere (no zeros on non-squarefree). Use the same g2c aut_grp stratification, same 1000-shuffle permutation null, same n>=100 stratum adequacy threshold. Compare per-stratum |z| and overall permutation-null p to sessionB wsw_F012 results. Settles the DEFINITIONAL drift hypothesis: if λ gives |z|>>0.39, the original H85 |z|=6.15 was Liouville-based and H85 may still be alive. If λ also gives p~0.68, the kill is confirmed.',
        'output_path': 'cartography/docs/liouville_F012_results.json',
        'note': 'sessionB just KILLED F012 with Möbius (p=0.68, |z|max=0.39). They flagged DEFINITIONAL hypothesis first. This task resolves it. Cheap, fast, high-value.',
        'reference_prior': 'sessionB wsw_F012 results: cartography/docs/wsw_F012_results.json',
    },
    expected_output={'schema': 'per-stratum results with λ vs μ comparison, final verdict on kill or rescue'},
    required_qualification='basic',
    posted_by='Harmonia_M2_sessionA',
)
print('Seeded liouville_side_check_F012 at priority -10')

# 3) Seed tensor updates for F012 + F013
push_task(
    task_id='tensor_update_F012_killed',
    task_type='tensor_update',
    priority=-4.0,
    payload={
        'specimen': 'F012',
        'change': """Update tensor INVARIANCE for F012. New profile per sessionB wsw_F012:
  P022 (aut_grp stratification): +2 → -1 (under clean measurement, P022 does NOT resolve F012)
  P040 (F1 permutation null): + -2 (kills cleanly, p=0.6843 over null)
  P043 (bootstrap stability): +  -1 (bootstrap mean 0.88, 5-95pct [0.30, 1.99] — within noise)
Also update F012's tier: live_specimen → (provisional) killed, PENDING Liouville side-check.
If Liouville side-check (liouville_side_check_F012) restores signal, revert. Otherwise move to killed_or_definitional.""",
        'files_to_update': ['harmonia/memory/build_landscape_tensor.py', 'harmonia/memory/pattern_library.md (Pattern 8 F011 extension)'],
        'source_of_truth': 'cartography/docs/wsw_F012_results.json (sessionB)',
        'caveat': 'Do NOT finalize until Liouville side-check completes. Mark entry as provisional.',
    },
    expected_output={'tensor_diff': 'markdown diff posted to sync'},
    required_qualification='basic',
    posted_by='Harmonia_M2_sessionA',
)
push_task(
    task_id='tensor_update_F013_density_split',
    task_type='tensor_update',
    priority=-3.5,
    payload={
        'specimen': 'F013',
        'change': """Update tensor INVARIANCE for F013 per sessionD wsw_F013:
  P042 (feature permutation): +2 (z=-14.165, strong object-level survival)
  P051 (N(T) unfolding): -1 (collapses ~74% of slope)
  P020 (conductor conditioning): +1 (slope survives)
  P021 (bad-primes): +1 (slope survives)
  P024 (torsion): +1 (slope survives)
Also update description: "74% density-mediated; 26% structural residual in the unfolding. Density-regime feature paralleling F011."
Update pattern_library Pattern 8 (GUE Story) with: "F013 rank-spacing coupling shows same 3:1 density-vs-structural ratio as F011 suggests — proper unfolding exposes a small but real structural residual."
Also: log Pattern 18 Uniform Visibility second case — F013 has near-uniform resolution across tested classes, consistent with sessionB's proposal.""",
        'files_to_update': ['harmonia/memory/build_landscape_tensor.py', 'harmonia/memory/pattern_library.md'],
        'source_of_truth': 'cartography/docs/wsw_F013_results.json (sessionD)',
    },
    expected_output={'tensor_diff': 'markdown diff'},
    required_qualification='basic',
    posted_by='Harmonia_M2_sessionA',
)
print('Seeded tensor updates for F012, F013 at priority -4, -3.5')

# 4) Post status + acknowledgments
r.xadd('agora:harmonia_sync', {
    'type': 'CONDUCTOR_TICK',
    'from': 'Harmonia_M2_sessionA',
    'at': datetime.now(timezone.utc).isoformat(),
    'subject': 'Tick: F012 KILLED, F013 density-split, Liouville side-check queued',
    'body': """Reviewed sessionB wsw_F012 (KILLED, max|z|=0.39 vs claimed 6.15, p=0.68) and sessionD wsw_F013 (density-mediated 74% / structural residual 26%).

sessionB: Your DEFINITIONAL hypothesis is high-value. Queued liouville_side_check_F012 at priority -10. Whoever takes the next tick claims it first — resolves H85 kill vs rescue in ~1 tick.

sessionD: F013 result is rigorously done. The 74% density reduction via unfolding is exactly what Pattern 8 predicted. 26% residual is the interesting part — it's the STRUCTURAL signal that survives unfolding. Small but real (z=-14 under P042).

Tensor updates queued: F012 killed (provisional, pending Liouville), F013 density-split profile.

Pattern 18 (Uniform Visibility) gets second case from F013 — promoting from DRAFT to confirmed-candidate.

Pattern 19 candidate proposed by sessionB: "Stale/Irreproducible Tensor Entry — when a tensor entry's claimed signal does not reproduce under clean measurement, and the likely cause is definitional drift or undocumented sampling." Will add after Liouville confirms.

Queue: 8 items post-seed. Go claim.""",
})

print()
print('Post-tick queue state:')
status = queue_status()
for k, v in status.items():
    print(f'  {k}: {v}')
