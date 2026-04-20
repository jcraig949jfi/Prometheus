"""
gen_05 executor: score (killed F-ID, untested projection) replay candidates.

Reads tensor Redis state, enumerates killed/artifact F-IDs, scores every
untested projection per killed F-ID, emits top-N candidates + writes the
JSON companion for gen_log_builder.py.

Run from project root:
  PYTHONPATH=. python harmonia/runners/gen_05_attention_replay.py

Output: harmonia/memory/kill_replay_candidates.json

Scoring v1:
  score = adjacency + 2 * type_novelty + 1.5 * recency
where
  adjacency   — count of live specimens P resolves at +1/+2
  type_novelty — 1 if P's type new to this F-ID's tested set
  recency     — 1.0 for P-ID >= 100, 0.5 for >= 28, else 0

The scorer is a heuristic; top-of-queue will be dominated by high-adjacency
projections (e.g., P023 rank stratification). Per-F-ID guarantee ensures
every killed F-ID receives >= 1 replay slot.
"""
import os
import json
import datetime as dt
from pathlib import Path

os.environ.setdefault('AGORA_REDIS_HOST', '192.168.1.176')
os.environ.setdefault('AGORA_REDIS_PASSWORD', 'prometheus')
from agora.tensor import features, projections, feature_meta, projection_meta, resolve_row, resolve_cell


KILLED_TIERS = {'killed', 'killed_tautology', 'data_artifact'}


def enumerate_killed():
    feats = features()
    killed = []
    for f in feats:
        m = feature_meta(f)
        if m.get('tier') in KILLED_TIERS:
            killed.append({'id': f, 'tier': m.get('tier', ''), 'label': m.get('label', '')})
    return killed


def proj_live_adjacency(projs, live_feats):
    out = {}
    for p in projs:
        out[p] = sum(1 for f in live_feats if resolve_cell(f, p) in (1, 2))
    return out


def score_pair(pid, pmeta, tested, tested_types, proj_live):
    adjacency = proj_live.get(pid, 0)
    type_novelty = 1 if pmeta.get('type') not in tested_types else 0
    try:
        pnum = int(pid[1:])
    except ValueError:
        pnum = 0
    recency = 1.0 if pnum >= 100 else (0.5 if pnum >= 28 else 0.0)
    score = adjacency + 2 * type_novelty + 1.5 * recency
    return score, adjacency, type_novelty, recency


def main(top_n=30):
    feats = features()
    projs = projections()
    live_feats = [f for f in feats if feature_meta(f).get('tier') not in KILLED_TIERS]

    killed = enumerate_killed()
    proj_live = proj_live_adjacency(projs, live_feats)
    proj_meta_cache = {p: projection_meta(p) for p in projs}

    candidates = []
    for k in killed:
        f = k['id']
        row = resolve_row(f)
        tested = {p for p, v in row.items() if v != 0}
        tested_types = {proj_meta_cache[p].get('type') for p in tested}
        for p in projs:
            if p in tested:
                continue
            pmeta = proj_meta_cache[p]
            score, adj, tn, rec = score_pair(p, pmeta, tested, tested_types, proj_live)
            candidates.append({
                'feature_id': f,
                'feature_tier': k['tier'],
                'projection_id': p,
                'projection_type': pmeta.get('type', ''),
                'score': round(score, 2),
                'adjacency': adj,
                'type_novelty': tn,
                'recency': rec,
            })

    candidates.sort(key=lambda c: -c['score'])

    # Top-N with per-F-ID guarantee (>=1 per killed F-ID)
    seeded = []
    chosen = {}
    for c in candidates:
        f = c['feature_id']
        if chosen.get(f, 0) < 1:
            seeded.append(c)
            chosen[f] = chosen.get(f, 0) + 1
    for c in candidates:
        if c in seeded:
            continue
        if len(seeded) >= top_n:
            break
        seeded.append(c)

    out = {
        'generated_at': dt.datetime.now(dt.timezone.utc).isoformat(),
        'n_candidates_total': len(candidates),
        'n_seeded': len(seeded),
        'all_candidates': candidates,
        'seeded': seeded,
    }
    Path('harmonia/memory').mkdir(exist_ok=True)
    Path('harmonia/memory/kill_replay_candidates.json').write_text(
        json.dumps(out, indent=2), encoding='utf-8')

    print('Killed F-IDs inspected: {}'.format(len(killed)))
    print('Candidate (F, P) pairs: {}'.format(len(candidates)))
    print('Seeded (top {} + per-F guarantee): {}'.format(top_n, len(seeded)))
    print('Top 10:')
    for c in seeded[:10]:
        print('  {:6s} x {:6s} [{:25s}] score={:5.2f}'.format(
            c['feature_id'], c['projection_id'], c['projection_type'], c['score']))


if __name__ == '__main__':
    main(top_n=30)
