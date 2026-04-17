"""Tick 2 seeding: followup tasks."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ['AGORA_REDIS_HOST'] = '192.168.1.176'
os.environ['AGORA_REDIS_PASSWORD'] = 'prometheus'

import redis
from datetime import datetime, timezone
from agora.work_queue import push_task, queue_status

r = redis.Redis(host='192.168.1.176', port=6379, password='prometheus', decode_responses=True)

# Seed followup tasks
tasks = [
    {
        'task_id': 'wsw_F010_P052',
        'priority': -2.0,
        'task_type': 'weak_signal_walk',
        'payload': {
            'specimen_id': 'F010',
            'specimen_label': 'NF backbone P052 prime decontamination check',
            'target_projections': ['P052'],
            'method': 'Apply 3-layer microscope (detrend + filter + normalize) to the NF log_disc and Artin log_conductor features before computing the Galois-label coupling. Compare ρ to the raw ρ=0.404. If it survives (ρ > 0.20 post-decontamination), F010 becomes strongest specimen. If it collapses, it was prime-factorization-mediated.',
            'output_path': 'cartography/docs/wsw_F010_P052_results.json',
            'reference': 'sessionC wsw_F010_results.json — 4/5 projections survive, P052 deferred',
        },
        'required_qualification': 'basic',
    },
    {
        'task_id': 'tensor_update_F014_lehmer_gap_refined',
        'priority': -3.0,
        'task_type': 'tensor_update',
        'payload': {
            'specimen': 'F014',
            'change': """Per sessionB wsw_F014 (81K polynomials): the claimed 4.4% Lehmer gap is FALSIFIED. Observed gap is 3.41% with 3 polynomials strictly inside (1.176, 1.228), minimum being a Salem poly at M=1.216.

Update F014 description from "Lehmer spectrum gap (4.4% between bound and next smallest Mahler measure)" to:
"Lehmer bound touched at degrees 10 and 20 (Lehmer polynomial and splitting field); small-gap density in (bound, 1.228) — 3 polynomials including Salem at 1.216; original 4.4% gap claim falsified by sessionB wsw_F014."

Update F014 tier: keep as live_specimen (structure remains interesting) but with refined claim.

Also: add entry to tautology-pair table or anti-pattern list: "Mahler-measure gap claims without degree stratification are suspect — Salem polynomials cluster in sub-1.22 region at specific degrees."
""",
            'files_to_update': ['harmonia/memory/build_landscape_tensor.py'],
            'source_of_truth': 'cartography/docs/wsw_F014_results.json (sessionB)',
        },
        'required_qualification': 'basic',
    },
    {
        'task_id': 'harvest_nf_complexity_projections',
        'priority': 1.8,
        'task_type': 'literature_harvest',
        'payload': {
            'brief': 'Query a frontier model: "List all ways mathematicians measure complexity or structural type of number fields (degree, discriminant, class number, regulator, Galois group, signature, unit rank, ...). Include projections from 1970s-2000s literature that might be obscure. Return 30-50 projections."',
            'method': 'Single API call via keys.get_key("CLAUDE"). Cap ~2000 tokens. Do NOT ask the model to judge; just enumerate.',
            'output_path': 'cartography/docs/harvest_nf_projections.md',
            'output_format': 'Markdown table — Name, Year, Resolves, LMFDB column/derivable, Checked.',
        },
        'required_qualification': 'basic',
    },
    {
        'task_id': 'wsw_F015',
        'priority': -1.0,
        'task_type': 'weak_signal_walk',
        'payload': {
            'specimen_id': 'F015',
            'specimen_label': 'abc/Szpiro monotone decrease at fixed bad-prime count (Ergon 2026-04-16)',
            'target_projections': ['P021', 'P020', 'P042', 'P051', 'P052'],
            'method': 'Ergon found Szpiro ratio decreases monotonically with conductor when stratified by num_bad_primes. Reproduce this and apply 5 projections. Use bsd_joined on postgres/prometheus. Is the monotone trend surviving preprocessing (P051 unfolding equivalents on szpiro, P052 prime decontamination)? Is it an independent effect from P021 (the stratification axis itself)?',
            'output_path': 'cartography/docs/wsw_F015_results.json',
            'warning': 'Pattern 1 (tautology) applies — szpiro and faltings share log|Disc|. Check formula lineage.',
        },
        'required_qualification': 'basic',
    },
]

for t in tasks:
    tid = push_task(
        task_id=t['task_id'],
        task_type=t['task_type'],
        payload=t['payload'],
        priority=t['priority'],
        required_qualification=t['required_qualification'],
        posted_by='Harmonia_M2_sessionA',
    )
    print(f'  seeded {tid} @ {t["priority"]}')

# Status post
r.xadd('agora:harmonia_sync', {
    'type': 'CONDUCTOR_TICK',
    'from': 'Harmonia_M2_sessionA',
    'at': datetime.now(timezone.utc).isoformat(),
    'subject': 'Tick: F014 Lehmer gap falsified, F010 NF reproduced, P030 merged',
    'body': """Absorbed this tick:
- sessionB wsw_F014: 4.4% Lehmer gap FALSIFIED. Salem poly at M=1.216 inside the claimed gap. Bound itself held at degrees 10/20. F014 refined, not killed.
- sessionC wsw_F010: NF backbone REPRODUCED at ρ=0.404. Survives 4/5 projections (conductor+bad-prime+feature-perm all positive; P052 deferred).
- sessionC catalog_mf_level P030: MERGED to catalog. Critical tautology flagged (level ≡ conductor for EC-MF weight-2 matched pairs).
- sessionD F011 tensor update: APPLIED. F011 now invariance {P050/P051/P021/P023/P024/P025/P026: +1, P027: -1}. F013→F011 parallel_density_regime edge added.

Seeded this tick: wsw_F010_P052 (-2), tensor_update_F014_lehmer_gap_refined (-3), harvest_nf_complexity_projections (+1.8), wsw_F015 (-1).

Liouville side-check running (sessionB, claimed 10:55:19, ~5 min expected).

Decisions_for_james.md updated with F014 and F010 outcomes.""",
})

print()
print('Queue:', queue_status())
