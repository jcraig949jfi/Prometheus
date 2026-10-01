"""Nestor harvest check U-T5: internalization hazard per lineage organism-epoch, C-A3-INTERNALIZE committed rows.
Run from roles/Nestor/campaigns/npe-arc3-2026-09-28/c_a3_internalize:  python <this file>"""
import json, glob, sys
sys.path.insert(0, '.')
from run_ci import event
for p in sorted(glob.glob('results/*.json')):
    r = json.load(open(p))
    if not r['d0_free'] or any(r['d0_free']) or not any(c['L_share'] >= 0.5 for c in r['checkpoints']):
        continue
    ev, rp = event(r)
    first = next((c['epoch'] for c in r['checkpoints'] if c['free'] > 0 and c['free_in_L'] > 0), None)
    cum = sum(c['L_share'] * 256 * 100 for c in r['checkpoints'] if first is None or c['epoch'] <= first)
    print(r['cell'], r['seed'], 'EVENT' if ev else ('REPL' if rp else 'none'), r['depth'], first, round(cum / 1e3, 1))
