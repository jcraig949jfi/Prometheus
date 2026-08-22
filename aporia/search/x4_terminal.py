"""CAMPAIGN X-4 pass 3/3 — TERMINAL. frozen-A touched ONCE. frozen-B NEVER.

The preregistration is applied UNAMENDED, even though pass 2 showed it will
probably park a positive result. That is the point of preregistering.

frozen-B: its INDEX LIST is loaded only to be excluded and no frozen-B pair is
scored, ranked or inspected. Its term vectors are present in the shared retrieval
pool as candidates — unavoidable and harmless, since being a candidate leaks no
label and the successor campaign needs its targets retrievable.

STRUCTURE: the L2 block sits inside an `if` on K0. If K0 fails, no L2 quantity is
computed anywhere in this file — not gated behind a flag, absent.

The metric, normalisation, projection and pool are imported unchanged from
x4_dev_fit.py, so nothing here is attributable to a refit.
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

LEARN, RAWZ, ids, idx_of, pool = xf.LEARN, xf.RAWZ, xf.ids, xf.idx_of, xf.pool
POS, OPS, K = xf.POS, xf.OPS, xf.K
mu, sd, P, KEEP = xf.mu, xf.sd, xf.P, xf.KEEP
RK_L, USE_L, skL = xf.RK_L, xf.USE_L, xf.skL
feat, valid_partners = xf.feat, xf.valid_partners
split = xf.split

FA = sorted(split['frozenA_indices'])
FB_N = len(split['frozenB_indices'])          # counted, never opened
print(f"\n=== X-4 frozen-A TOUCHED (once): {len(FA)} pairs | frozen-B RESERVED: {FB_N}, not opened ===", flush=True)
print(f"learned space {LEARN.shape[1]} dims, hubness skew {skL:.3f}, local scaling {'ON' if USE_L else 'OFF'}", flush=True)

def wilson(k_, n_, z=1.96):
    if n_ == 0: return (0.0, 0.0)
    p = k_/n_; d = 1 + z*z/n_
    c = (p + z*z/(2*n_))/d
    h = z*math.sqrt(p*(1-p)/n_ + z*z/(4*n_*n_))/d
    return (round(c-h, 4), round(c+h, 4))

# ---------------------------------------------- STEP 1: frozen-A answer sets
asets, asize = {}, defaultdict(list)
for i in FA:
    p = POS[i]
    if p['src'] in pool and p['tgt'] in pool:
        asets[i] = valid_partners(p['src'], p['op'])
        asize[p['op']].append(len(asets[i]))
missing = sum(1 for i in FA if i in asets and POS[i]['tgt'] not in asets[i])
real_V = [len(asets[i]) for i in FA if i in asets and POS[i]['op'] != 'shift']
MEAN_V = float(np.mean(real_V))
print(f"\nsanity: recorded target absent from own answer set = {missing}")
print(f"frozen-A mean |V| on four real operators = {MEAN_V:.3f} (computed ON FROZEN-A)")

# ---------------------------------------------- STEP 2: K0
st = defaultdict(lambda: [0, 0]); av = defaultdict(lambda: [0, 0])
for i in FA:
    if i not in asets: continue
    p = POS[i]; src, tgt, op = p['src'], p['tgt'], p['op']
    img = OPS[op](pool[src])[p['offset']:]
    q = np.nan_to_num(feat(img)); q = (q - mu)/sd
    q = q @ P
    q = q/(np.linalg.norm(q) + 1e-9)*np.sqrt(KEEP)
    d = np.linalg.norm(LEARN - q, axis=1)
    if USE_L:
        kq = np.sort(np.partition(d, K)[:K+1])[K-1]
        d = d/np.sqrt(max(kq, 1e-6)*RK_L)
    d[idx_of[src]] = np.inf
    top = ids[int(np.argmin(d))]
    st[op][1] += 1; av[op][1] += 1
    if top == tgt: st[op][0] += 1
    if top in asets[i]: av[op][0] += 1

S = sum(v[0] for v in st.values()); A = sum(v[0] for v in av.values()); N = sum(v[1] for v in st.values())
lo, hi = wilson(A, N)
K0 = lo > 0.90
PREDICTED_FAIL = True                      # logged in P118 BEFORE frozen-A was read

res = {'frozenA_pairs': len(FA), 'frozenB_reserved_not_opened': FB_N,
       'pool_size': len(pool), 'learned_dims': int(LEARN.shape[1]),
       'hubness_skew_learned': round(skL, 3), 'local_scaling_applied': bool(USE_L),
       'recorded_target_absent_from_answer_set': missing,
       'frozenA_mean_V_four_real_ops': round(MEAN_V, 4),
       'answer_set_size': {op: {'n': len(v), 'mean': round(float(np.mean(v)), 3),
                                'max': int(np.max(v)), 'frac_gt_1': round(float(np.mean([x > 1 for x in v])), 4)}
                           for op, v in asize.items()},
       'K0': {'strict': f"{S}/{N}", 'strict_rate': round(S/N, 4),
              'any_valid': f"{A}/{N}", 'any_valid_rate': round(A/N, 4),
              'wilson_95': [lo, hi], 'threshold': 0.90, 'PASSED': bool(K0),
              'by_op_strict': {k_: f"{v[0]}/{v[1]}" for k_, v in st.items()},
              'by_op_any_valid': {k_: f"{v[0]}/{v[1]}" for k_, v in av.items()}},
       'pass2_prediction': {'predicted_K0_would_fail': PREDICTED_FAIL,
                            'actual_K0_failed': bool(not K0),
                            'prediction_correct': bool(PREDICTED_FAIL == (not K0)),
                            'dev_any_valid_for_reference': 0.6800,
                            'dev_wilson_for_reference': [0.6328, 0.7238]}}

print(f"\nFROZEN-A L1 strict    {S}/{N} = {S/N:.4f}   {res['K0']['by_op_strict']}")
print(f"FROZEN-A L1 any-valid {A}/{N} = {A/N:.4f}   {res['K0']['by_op_any_valid']}")
print(f"Wilson 95% CI ({lo}, {hi})   K0 threshold 0.90")
print(f"\n*** K0: {'PASSED' if K0 else 'FAILED'} ***")
print(f"pass-2 predicted K0 would FAIL -> prediction {'CORRECT' if res['pass2_prediction']['prediction_correct'] else 'WRONG'}")

if not K0:
    res.update({'L2_measured': False, 'branch_fired': 'M0', 'TERMINAL': 'PARK',
                'reason': 'K0 interval gate failed on frozen-A; the preregistration forbids computing '
                          'any L2 quantity, and it was applied unamended'})
    print("\nM0 fired. NO L2 computed. TERMINAL: PARK")
else:
    print("\nK0 passed — measuring L2...", flush=True)
    def hits(Z, rk=None, use=False):
        o = {}
        for i in FA:
            if i not in asets: continue
            src = POS[i]['src']
            d = np.linalg.norm(Z - Z[idx_of[src]], axis=1)
            if use and rk is not None:
                kq = np.sort(np.partition(d, K)[:K+1])[K-1]
                d = d/np.sqrt(max(kq, 1e-6)*rk)
            d[idx_of[src]] = np.inf
            o[i] = bool(set(ids[j] for j in np.argsort(d, kind='stable')[:10]) & asets[i])
        return o
    hl, hr = hits(LEARN, RK_L, USE_L), hits(RAWZ)
    REAL = [i for i in FA if i in asets and POS[i]['op'] != 'shift']
    b = sum(1 for i in REAL if hl[i] and not hr[i]); c = sum(1 for i in REAL if hr[i] and not hl[i])
    n = len(REAL); D = (b - c)/n
    se = math.sqrt(max((b + c) - (b - c)**2/n, 0))/n
    dlo, dhi = round(D - 1.96*se, 4), round(D + 1.96*se, 4)
    res['L2'] = {'learned': f"{sum(hl[i] for i in REAL)}/{n}", 'raw': f"{sum(hr[i] for i in REAL)}/{n}",
                 'D': round(D, 4), 'b': b, 'c': c, 'ci95_paired': [dlo, dhi],
                 'discordance': round((b+c)/n, 4)}
    res['L2_measured'] = True
    M1 = dlo > 0.03; M2 = 0 < dlo <= 0.03
    M3 = dlo <= 0 <= dhi and dhi < 0.03
    M4 = dlo <= 0 <= dhi and dhi >= 0.03
    M5 = dhi < 0
    res['branches'] = {'M1': M1, 'M2': M2, 'M3': M3, 'M4': M4, 'M5': M5}
    res['branch_fired'] = 'M1' if M1 else 'M2' if M2 else 'M3' if M3 else 'M4' if M4 else 'M5'
    res['TERMINAL'] = {'M1': 'ADVANCE', 'M2': 'REDESIGN', 'M3': 'KILL',
                       'M4': 'PARK', 'M5': 'REDESIGN'}[res['branch_fired']]
    print(f"D = {D:+.4f} CI [{dlo}, {dhi}] -> {res['branch_fired']}")

(SEARCH / 'x4_terminal_results.json').write_text(json.dumps(res, indent=1), encoding='utf-8')
print(f"\n*** CAMPAIGN X-4 TERMINAL: {res['TERMINAL']} (branch {res['branch_fired']}) ***")
print("frozen-B was never opened.")
