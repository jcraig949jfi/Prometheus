"""Retry only the 4 errored hypotheses from the frontier batch."""
import sys, io, json, time, os
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
# Import first (the module will wrap sys.stdout internally — avoid double wrap)
from harmonia_frontier_runner import (
    HypothesisResult, connect,
    h11_ade_gatekeeping_nf, h60_artin_frontier_clusters,
    h61_artin_dimensional_gap, h85_chowla_g2_discriminants,
)
import traceback

RETRIES = [
    ('H11', 'ADE Gatekeeping in NF Discriminants', h11_ade_gatekeeping_nf),
    ('H60', 'Artin Frontier Clusters', h60_artin_frontier_clusters),
    ('H61', 'Artin Dimensional Gap', h61_artin_dimensional_gap),
    ('H85', 'Chowla at Genus-2 Discriminants', h85_chowla_g2_discriminants),
]


conn_lmfdb = connect('lmfdb')
conn_fire = connect('prometheus_fire')

# Load existing results
path = os.path.join(os.path.dirname(__file__), '..', '..', 'docs',
                    'harmonia_frontier_results_20260417.json')
with open(path) as f:
    data = json.load(f)

# Build id -> index map
idx = {r['id']: i for i, r in enumerate(data['results'])}

for hid, title, fn in RETRIES:
    r = HypothesisResult(hid, title)
    r.started_at = datetime.now(timezone.utc).isoformat()
    t0 = time.time()
    print(f"\n--- {hid}: {title} (retry) ---")
    try:
        fn(conn_lmfdb, conn_fire, r)
    except Exception as e:
        r.status = 'ERROR'
        r.error = str(e) + '\n' + traceback.format_exc()
    r.duration_seconds = round(time.time() - t0, 2)
    r.finished_at = datetime.now(timezone.utc).isoformat()
    print(f"  [{r.duration_seconds}s] {r.status}: {r.verdict}")

    # Update record
    if hid in idx:
        data['results'][idx[hid]] = r.to_dict()

with open(path, 'w') as f:
    json.dump(data, f, indent=2, default=str)

print("\nUpdated:", path)
conn_lmfdb.close(); conn_fire.close()
