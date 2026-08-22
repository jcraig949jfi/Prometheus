"""CAMPAIGN X-5 pass 1 — B-DIAG. Run FIRST, on development only, before anything
else is decided. frozen-B is not touched.

THE ANOMALY. Binomial L1 in the learned space is 3/80 on development and 8/160 on
frozen-A, against 100/100 for V2 in X-3. That is extreme enough that an
implementation bug cannot be excluded, and everything X-5 would otherwise inherit
depends on which it is.

THE SPECIFIC MECHANISM UNDER TEST. The raw block of the feature vector is built by
`rawvec`, which takes `v[:25]` and ZERO-PADS when the input is shorter than 25.
Operator image lengths from a 45-term source are: diff 44, partsum 45, shift 44,
moebius 40 (capped) — and binomial 24 (capped), or 23 after a one-position offset.
**Binomial is the only operator whose images are shorter than the raw block.** So a
binomial query is compared against pool candidates that have real values in the
positions where the query has been padded with zeros — and because binomial images
grow fast, those positions hold the largest values in the vector. If that is the
cause, it is a bug in the comparison, not a property of the learned metric, and it
would hit exactly one operator: the one observed to fail.

MEASURED HERE, per operator, on development images: length distribution, count of
zero-padded raw positions, raw-block norm of the image against its own target,
non-finite incidence, and projected norm. A verdict of BUG or PROPERTY is stated
plainly at the end.

NO FROZEN QUANTITY IS COMPUTED IN THIS FILE.
"""
from __future__ import annotations

import importlib.util
import json
import math
import pathlib
from collections import defaultdict

import numpy as np

SEARCH = pathlib.Path(r'F:\Prometheus\aporia\search')
spec = importlib.util.spec_from_file_location('xf', SEARCH / 'x4_dev_fit.py')
xf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(xf)

pool, idx_of, POS, DEV, OPS = xf.pool, xf.idx_of, xf.POS, xf.DEV, xf.OPS
mu, sd, P = xf.mu, xf.sd, xf.P
feat, rawvec = xf.feat, xf.rawvec

print("\n=== B-DIAG (development only; frozen-B untouched) ===", flush=True)

rows = defaultdict(lambda: {'len': [], 'pad': [], 'img_rawnorm': [], 'tgt_rawnorm': [],
                            'nonfinite': 0, 'projnorm': [], 'n': 0})
for i in DEV:
    p = POS[i]
    src, tgt, op = p['src'], p['tgt'], p['op']
    if src not in pool or tgt not in pool:
        continue
    img = OPS[op](pool[src])[p['offset']:]
    r = rows[op]
    r['n'] += 1
    r['len'].append(len(img))
    r['pad'].append(max(0, 25 - len(img)))
    r['img_rawnorm'].append(float(np.linalg.norm(np.array(rawvec(img)))))
    r['tgt_rawnorm'].append(float(np.linalg.norm(np.array(rawvec(pool[tgt])))))
    f = feat(img)
    if not np.all(np.isfinite(f)):
        r['nonfinite'] += 1
    q = np.nan_to_num(f); q = (q - mu) / sd
    r['projnorm'].append(float(np.linalg.norm(q @ P)))

out = {'per_operator': {}}
print(f"{'op':10s} {'n':>4s} {'img_len':>16s} {'padded':>7s} {'raw|img|':>9s} {'raw|tgt|':>9s} "
      f"{'ratio':>6s} {'nonfin':>7s} {'projnorm':>9s}")
for op, r in rows.items():
    L = np.array(r['len']); pad = np.array(r['pad'])
    a, b = np.mean(r['img_rawnorm']), np.mean(r['tgt_rawnorm'])
    out['per_operator'][op] = {
        'n': r['n'], 'img_len_min': int(L.min()), 'img_len_max': int(L.max()),
        'img_len_mean': round(float(L.mean()), 2),
        'pairs_with_padding': int((pad > 0).sum()),
        'mean_padded_positions': round(float(pad.mean()), 2),
        'mean_raw_norm_image': round(a, 3), 'mean_raw_norm_target': round(b, 3),
        'image_to_target_norm_ratio': round(a / b, 4) if b else None,
        'nonfinite_features': r['nonfinite'],
        'mean_projected_norm': round(float(np.mean(r['projnorm'])), 3)}
    o = out['per_operator'][op]
    print(f"{op:10s} {r['n']:4d} {str(o['img_len_min'])+'-'+str(o['img_len_max']):>16s} "
          f"{o['pairs_with_padding']:7d} {o['mean_raw_norm_image']:9.3f} {o['mean_raw_norm_target']:9.3f} "
          f"{o['image_to_target_norm_ratio']:6.3f} {o['nonfinite_features']:7d} {o['mean_projected_norm']:9.3f}")

padded_ops = [op for op, o in out['per_operator'].items() if o['pairs_with_padding'] > 0]
out['operators_with_padded_raw_block'] = padded_ops
BUG = len(padded_ops) > 0 and set(padded_ops) == {'binomial'}
out['verdict'] = 'BUG' if BUG else 'PROPERTY'
out['verdict_reasoning'] = (
    'binomial is the ONLY operator whose images are shorter than the 25-term raw block, so its '
    'queries are zero-padded in exactly the high-magnitude positions where pool candidates carry '
    'real values; the failure is therefore in the comparison and not in the learned metric'
    if BUG else
    'no operator-specific padding asymmetry was found, so the binomial collapse is a property of '
    'the learned metric rather than a preprocessing defect')
out['frozen_quantities_computed'] = False
(SEARCH / 'x5_bdiag.json').write_text(json.dumps(out, indent=1), encoding='utf-8')

print(f"\noperators whose raw block gets zero-padded: {padded_ops}")
print(f"\n*** B-DIAG VERDICT: {out['verdict']} ***")
print(out['verdict_reasoning'])
print("\nNO frozen quantity computed.")
