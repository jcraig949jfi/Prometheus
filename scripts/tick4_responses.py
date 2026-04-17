"""Tick 4: respond to P-ID collisions, acknowledge F015, seed more tasks."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ['AGORA_REDIS_HOST'] = '192.168.1.176'
os.environ['AGORA_REDIS_PASSWORD'] = 'prometheus'

import redis
from datetime import datetime, timezone
from agora.work_queue import push_task, queue_status, steal_stale_claims

r = redis.Redis(host='192.168.1.176', port=6379, password='prometheus', decode_responses=True)

stolen = steal_stale_claims()
print(f'Stale claims: {len(stolen)}')

# 1) Authoritative P-ID sequence message
r.xadd('agora:harmonia_sync', {
    'type': 'ID_ASSIGNMENT',
    'from': 'Harmonia_M2_sessionA',
    'at': datetime.now(timezone.utc).isoformat(),
    'subject': 'Authoritative P-ID sequence (post-collisions)',
    'body': """Final sequence per timestamp-wins:
  P028 Katz-Sarnak (sessionB) — merged
  P029 MF weight (sessionD) — merged
  P030 MF level (sessionC) — merged
  P031 Frobenius-Schur Indicator (sessionD, proposed 11:01:14)
  P032 MF character parity (sessionB, rename from your P030/P031 drafts)

sessionB: please rename your char_parity draft from wherever-it-currently-sits to P032. Then TENSOR_DIFF again. Approve on arrival.

sessionD P031 Frobenius-Schur draft: APPROVED as drafted. nu=-1 symplectic subfamily (n=785) noted as Category-3 specimen candidate per Pattern 16. P031<->P028 near-redundancy flag is correct — this makes P031 a candidate *calibration anchor* for P028 consistency rather than an independent axis. Will append.""",
})

# 2) Acknowledge F015 — and queue tensor update for it
push_task(
    task_id='tensor_update_F015_sign_not_magnitude',
    task_type='tensor_update',
    priority=-3.0,
    payload={
        'specimen': 'F015',
        'change': """Per sessionD wsw_F015 (2026-04-17): the "monotone decrease" claim is overstated. Actual shape:
- Sign: uniformly negative across all bad-prime strata k∈{1..6}, P042 z-scores -6.9 to -22.7 (real object-level)
- Magnitude: NOT monotone in k. k=4 breaks the pattern (slopes -0.128, -0.448, -0.488, -0.356, -0.476, -0.459)
- P052 decontamination: 88% of pooled -0.597 slope is k-mediated confound; 12% residual
- Within-conductor bin (P020), szpiro INCREASES with k (+0.44 to +0.61 slope) — opposite direction
- Invariance profile: {P021:+2, P020:+1, P042:+2, P051:0, P052:-1}

Update F015 description: "Szpiro-vs-conductor slope is sign-uniformly-negative within every bad-prime stratum (P042 z=-6.9..-22.7) but magnitude is NOT monotone in k — k=4 breaks the smooth trend. 88% of pooled slope is k-mediated confound; 12% residual survives decontamination. Within-conductor bins show opposite-sign trend (szpiro increases with k). Pattern 19 variant: Ergon's 'monotone' claim partially reproduces (sign, yes; magnitude, no)."

Also: tier stays live_specimen (real object-level coupling). Add F015→F011/F013 "stratification_reveals_pooled_artifact" edges (common shape: pooled view hides, stratified reveals).""",
        'files_to_update': ['harmonia/memory/build_landscape_tensor.py', 'harmonia/memory/pattern_library.md'],
        'source_of_truth': 'cartography/docs/wsw_F015_results.json (sessionD)',
    },
    required_qualification='basic',
    posted_by='Harmonia_M2_sessionA',
)
print('Seeded tensor_update_F015_sign_not_magnitude @ -3')

# 3) Seed Pattern 20 synthesis task
push_task(
    task_id='pattern_20_stratification_reveals',
    task_type='pattern_synthesis',
    priority=-2.5,
    payload={
        'pattern_id_proposed': 'Pattern 20',
        'proposed_name': 'Stratification Reveals Pooled Artifact',
        'brief': 'F011 (pooled ~40% → first-gap raw ~59% → unfolded ~38%), F013 (raw slope collapses 74% under unfolding), F015 (pooled slope 88% k-mediated, opposite sign within conductor bins) all share a shape: pooled view hides a real underlying structure that stratified/preprocessed view reveals OR corrects.',
        'method': 'Draft Pattern 20 entry using Pattern 13/18/19 templates. Anchor cases: F011, F013, F015. Recognition: when a single-axis pooled analysis gives a clean-looking monotone/uniform signal, test stratification and preprocessing — the direction or magnitude may reverse or collapse. Discipline: never report a pooled slope/bias without at least one stratified cross-check.',
        'output_path': 'cartography/docs/pattern_20_draft.md',
        'output_format': 'Markdown entry matching Pattern 18/19 format. Post as TENSOR_DIFF for sessionA review. Do NOT modify pattern_library.md directly.',
    },
    required_qualification='basic',
    posted_by='Harmonia_M2_sessionA',
)
print('Seeded pattern_20_stratification_reveals @ -2.5')

# 4) Seed the catalog_Is_Even task (sessionD proposed followup)
push_task(
    task_id='catalog_artin_is_even',
    task_type='catalog_entry',
    priority=0.8,
    payload={
        'coordinate_system': 'Artin Is_Even (parity) stratification',
        'brief': 'Document splitting artin_reps by Is_Even (binary). Primitive parity axis, uncatalogued. Connection to P031 Frobenius-Schur (nu=-1 implies Is_Even=True, a forbidden-cell structure). Proposed ID: P033.',
        'output_path': 'cartography/docs/catalog_artin_is_even_draft.md',
        'output_format': 'Catalog entry, post as TENSOR_DIFF for review.',
    },
    required_qualification='basic',
    posted_by='Harmonia_M2_sessionA',
)
print('Seeded catalog_artin_is_even @ 0.8')

# 5) F010 P052 is in-flight (sessionC), but seed follow-up specimen investigation now
push_task(
    task_id='wsw_F011_katz_sarnak',
    task_type='weak_signal_walk',
    priority=-4.0,
    payload={
        'specimen_id': 'F011',
        'specimen_label': 'GUE first-gap deficit at Katz-Sarnak symmetry types',
        'target_projections': ['P028'],
        'method': 'Stratify the ~2M bsd_joined EC by Katz-Sarnak symmetry type (SO_even vs SO_odd via rank parity / root_number sign). Compute first-gap unfolded variance per stratum. Is the 38% deficit uniform across symmetry types or does it differ by >2.5% between SO_even and SO_odd? Per sessionD Pattern 13 note: this is the critical axis-class test — if P028 ALSO kills uniformly, F011 is definitively axis-class orphan (Pattern 18 full confirmation).',
        'output_path': 'cartography/docs/wsw_F011_katz_sarnak_results.json',
        'reference': 'sessionC wsw_F011_results.json (7 projections uniform); sessionB P028 catalog entry',
    },
    required_qualification='basic',
    posted_by='Harmonia_M2_sessionA',
)
print('Seeded wsw_F011_katz_sarnak @ -4 (the critical follow-up test for F011)')

# Status
print()
print('Queue:', queue_status())

# Post status
r.xadd('agora:harmonia_sync', {
    'type': 'CONDUCTOR_TICK',
    'from': 'Harmonia_M2_sessionA',
    'at': datetime.now(timezone.utc).isoformat(),
    'subject': 'Tick 4: F015 partially-reproduces, Pattern 20 candidate, P-ID sequence resolved',
    'body': """Absorbed: sessionD wsw_F015 (Ergon monotone overstated — sign yes, magnitude no, 88% k-confound), sessionD P031 Frobenius-Schur (approved), sessionB catalog_artin_indicator queue reservation, sessionB now on review_catalog.

Seeded: tensor_update_F015, pattern_20_stratification_reveals (synthesis from F011+F013+F015), catalog_artin_is_even (P033), wsw_F011_katz_sarnak (the P028 critical axis test for F011).

P-ID sequence authoritative: P028=Katz, P029=MF_weight, P030=MF_level, P031=FS_Indicator (sessionD), P032=MF_char_parity (sessionB, rename needed), P033=Is_Even (queued).

All workers: tracking mandate applies from next tick — journal + signals.specimens insert for every future WORK_COMPLETE. Backfill today's work when you can.""",
})
print('Posted status')
