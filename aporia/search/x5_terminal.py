"""CAMPAIGN X-5 pass 3/3 — TERMINAL. frozen-B read exactly ONCE.

There is no reserve behind this split. The preregistration in X5_PASS1 is applied
UNAMENDED: representation as fitted (RAW_K=20, lambda>1.0 rule, local scaling per
the pre-committed skew rule), imported unchanged from x5_refit.py. The OVERLAP
ARTIFACT found in pass 2 is deliberately NOT fixed — correcting a representation
after seeing development results and before the frozen read is exactly the
adaptivity a held-out split exists to prevent.

ORDER, WHICH IS THE EXPERIMENT:
  1  frozen-B answer sets; mean |V| computed ON FROZEN-B; adjusted chance and the
     3x G-pos threshold derived from that value, never inherited from development
  2  G-pos on the MEAN over 20 derangements, BOTH arms. Violated -> PARK, nothing
     further computed.
  3  L2 on the 640 four-real-operator pairs; D with paired McNemar CI
  4  G-null evaluated ONLY if the CI on D contains zero (direction-conditional)
  5  N1-N6 as written, MDE 0.0367
"""
from __future__ import annotations

import importlib.util
import json
import math
import pathlib
import random
from collections import defaultdict

import numpy as np

SEARCH = pathlib.Path(r'F:\Prometheus\aporia\search')
spec = importlib.util.spec_from_file_location('xr', SEARCH / 'x5_refit.py')
xr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(xr)

pool, ids, idx_of = xr.pool, xr.ids, xr.idx_of
LEARN, RAWZ, RK_L, RK_R, UL, UR = xr.LEARN, xr.RAWZ, xr.RK_L, xr.RK_R, xr.UL, xr.UR
mu, sd, P, KEEP, K = xr.mu, xr.sd, xr.P, xr.KEEP, xr.K
feat, valid_partners, OPS, POS = xr.feat, xr.valid_partners, xr.OPS, xr.POS
split = xr.split
MDE = 0.0367

FB = sorted(split['frozenB_indices'])
N_POOL = len(pool)
print(f"\n=== X-5 frozen-B READ (once): {len(FB)} pairs | pool {N_POOL:,} ===", flush=True)
print(f"representation unchanged: RAW_K=20, k={KEEP}, local scaling learned={UL} raw={UR}", flush=True)

def wilson(k_, n_, z=1.96):
    if n_ == 0: return (0.0, 0.0)
    p = k_/n_; d = 1 + z*z/n_
    c = (p + z*z/(2*n_))/d
    h = z*math.sqrt(p*(1-p)/n_ + z*z/(4*n_*n_))/d
    return (round(c-h, 4), round(c+h, 4))

# ------------------------------------------------- STEP 1
asets = {}
for i in FB:
    p = POS[i]
    if p['src'] in pool and p['tgt'] in pool:
        asets[i] = valid_partners(p['src'], p['op'])
missing = sum(1 for i in FB if i in asets and POS[i]['tgt'] not in asets[i])
REAL = [i for i in FB if i in asets and POS[i]['op'] != 'shift']
SHIFT = [i for i in FB if i in asets and POS[i]['op'] == 'shift']
mV = float(np.mean([len(asets[i]) for i in REAL]))
ADJ = 10*mV/N_POOL
THR = 3*ADJ
print(f"\nsanity: recorded target absent from own answer set = {missing}")
print(f"frozen-B mean |V| (four real ops) = {mV:.4f} -> adjusted chance {ADJ:.6f}, G-pos threshold {THR:.6f}")
print(f"per-draw granularity at n={len(REAL)}: 1 hit = {1/len(REAL):.6f}")

def top10(Z, sid, rk, use):
    d = np.linalg.norm(Z - Z[idx_of[sid]], axis=1)
    if use:
        kq = np.sort(np.partition(d, K)[:K+1])[K-1]
        d = d/np.sqrt(max(kq, 1e-6)*rk)
    d[idx_of[sid]] = np.inf
    return set(ids[j] for j in np.argsort(d, kind='stable')[:10])

print("\ncomputing top-10 sets on frozen-B...", flush=True)
TL = {i: top10(LEARN, POS[i]['src'], RK_L, UL) for i in REAL}
TR = {i: top10(RAWZ, POS[i]['src'], RK_R, UR) for i in REAL}

# ------------------------------------------------- STEP 2: G-pos
prng = random.Random(20260829)
pl, pr = [], []
for _ in range(20):
    perm = REAL[:]
    prng.shuffle(perm)
    while any(a == b for a, b in zip(REAL, perm)):
        prng.shuffle(perm)
    pl.append(sum(bool(TL[i] & asets[j]) for i, j in zip(REAL, perm))/len(REAL))
    pr.append(sum(bool(TR[i] & asets[j]) for i, j in zip(REAL, perm))/len(REAL))
pl, pr = np.array(pl), np.array(pr)
GPOS = bool(pl.mean() <= THR and pr.mean() <= THR)
print(f"\nG-pos (mean over 20 derangements, threshold {THR:.6f}):")
print(f"  learned mean {pl.mean():.6f} (min {pl.min():.6f} max {pl.max():.6f})")
print(f"  raw     mean {pr.mean():.6f} (min {pr.min():.6f} max {pr.max():.6f})")
print(f"  -> G-pos {'HOLDS' if GPOS else 'VIOLATED'}")

res = {'frozenB_pairs': len(FB), 'pool_size': N_POOL, 'real_op_pairs': len(REAL),
       'recorded_target_absent_from_answer_set': missing,
       'frozenB_mean_V': round(mV, 4), 'adjusted_chance': round(ADJ, 6),
       'G_pos_threshold': round(THR, 6),
       'per_draw_granularity': round(1/len(REAL), 6),
       'G_pos': {'learned_mean': round(float(pl.mean()), 6), 'learned_min': round(float(pl.min()), 6),
                 'learned_max': round(float(pl.max()), 6),
                 'raw_mean': round(float(pr.mean()), 6), 'raw_min': round(float(pr.min()), 6),
                 'raw_max': round(float(pr.max()), 6), 'HOLDS': GPOS},
       'representation': {'RAW_K': 20, 'k_kept': int(KEEP), 'overlap_artifact_fixed': False}}

if not GPOS:
    res.update({'L2_measured': False, 'branch_fired': 'G-pos violated',
                'TERMINAL': 'PARK', 'reason': 'G-pos violated on frozen-B; artifact suspected'})
    print("\nG-pos violated. Nothing further computed. TERMINAL: PARK")
else:
    kl = sum(bool(TL[i] & asets[i]) for i in REAL)
    kr = sum(bool(TR[i] & asets[i]) for i in REAL)
    n = len(REAL)
    b = sum(1 for i in REAL if (TL[i] & asets[i]) and not (TR[i] & asets[i]))
    c = sum(1 for i in REAL if (TR[i] & asets[i]) and not (TL[i] & asets[i]))
    D = (b - c)/n
    se = math.sqrt(max((b + c) - (b - c)**2/n, 0))/n
    dlo, dhi = round(D - 1.96*se, 4), round(D + 1.96*se, 4)
    TLs = {i: top10(LEARN, POS[i]['src'], RK_L, UL) for i in SHIFT}
    TRs = {i: top10(RAWZ, POS[i]['src'], RK_R, UR) for i in SHIFT}
    res['L2'] = {'learned': f"{kl}/{n}", 'learned_rate': round(kl/n, 4), 'learned_wilson': list(wilson(kl, n)),
                 'raw': f"{kr}/{n}", 'raw_rate': round(kr/n, 4), 'raw_wilson': list(wilson(kr, n)),
                 'shift_control_learned': f"{sum(bool(TLs[i] & asets[i]) for i in SHIFT)}/{len(SHIFT)}",
                 'shift_control_raw': f"{sum(bool(TRs[i] & asets[i]) for i in SHIFT)}/{len(SHIFT)}"}
    res['D'] = {'value': round(D, 4), 'b_learned_only': b, 'c_raw_only': c, 'n': n,
                'se_paired': round(se, 5), 'ci95_paired': [dlo, dhi],
                'discordance': round((b+c)/n, 4), 'MDE': MDE}
    print(f"\nL2 frozen-B (four real ops, n={n}):")
    print(f"  learned {kl}/{n} = {kl/n:.4f} CI {res['L2']['learned_wilson']}")
    print(f"  raw     {kr}/{n} = {kr/n:.4f} CI {res['L2']['raw_wilson']}")
    print(f"  shift control: learned {res['L2']['shift_control_learned']} raw {res['L2']['shift_control_raw']}")
    print(f"  D = {D:+.4f} CI [{dlo}, {dhi}] (b={b}, c={c}, discordance {(b+c)/n:.4f})")

    contains_zero = dlo <= 0 <= dhi
    GNULL = None
    if contains_zero:
        st = av = None
        stc = defaultdict(lambda: [0, 0]); avc = defaultdict(lambda: [0, 0])
        for i in FB:
            if i not in asets: continue
            p = POS[i]; src, tgt, op = p['src'], p['tgt'], p['op']
            img = OPS[op](pool[src])[p['offset']:]
            q = np.nan_to_num(feat(img)); q = ((q - mu)/sd) @ P
            q = q/(np.linalg.norm(q) + 1e-9)*np.sqrt(KEEP)
            d = np.linalg.norm(LEARN - q, axis=1)
            if UL:
                kq = np.sort(np.partition(d, K)[:K+1])[K-1]
                d = d/np.sqrt(max(kq, 1e-6)*RK_L)
            d[idx_of[src]] = np.inf
            top = ids[int(np.argmin(d))]
            stc[op][1] += 1; avc[op][1] += 1
            if top == tgt: stc[op][0] += 1
            if top in asets[i]: avc[op][0] += 1
        A = sum(v[0] for v in avc.values()); NN = sum(v[1] for v in avc.values())
        S = sum(v[0] for v in stc.values())
        lo, hi = wilson(A, NN)
        GNULL = lo > 0.90
        res['G_null'] = {'evaluated': True, 'strict': f"{S}/{NN}", 'any_valid': f"{A}/{NN}",
                         'any_valid_rate': round(A/NN, 4), 'wilson_95': [lo, hi],
                         'threshold': 0.90, 'MET': bool(GNULL),
                         'by_op_any_valid': {k_: f"{v[0]}/{v[1]}" for k_, v in avc.items()}}
        print(f"\nG-null (CI on D contains zero, so evaluated): L1 any-valid {A}/{NN} = {A/NN:.4f} "
              f"CI ({lo}, {hi}) -> {'MET' if GNULL else 'NOT MET'}")
    else:
        res['G_null'] = {'evaluated': False,
                         'reason': 'CI on D does not contain zero; direction-conditional design does not require it'}
        print("\nG-null NOT evaluated (CI on D excludes zero), per the direction-conditional design.")

    if dhi < 0:
        br, term = 'N5', 'REDESIGN'
    elif dlo > MDE:
        br, term = 'N1', 'ADVANCE'
    elif dlo > 0:
        br, term = 'N2', 'REDESIGN'
    elif not GNULL:
        br, term = 'N4', 'PARK'
    elif dhi < MDE:
        br, term = 'N3', 'KILL'
    else:
        br, term = 'N6', 'PARK'
    res['L2_measured'] = True
    res['branch_fired'] = br
    res['TERMINAL'] = term
    print(f"\nbranch fired: {br}")

res['pass1_predictions'] = {
    'predicted_G_null_would_likely_fail': True,
    'dev_D_for_transfer_check': 0.1906}
(SEARCH / 'x5_terminal_results.json').write_text(json.dumps(res, indent=1), encoding='utf-8')
print(f"\n*** CAMPAIGN X-5 TERMINAL: {res['TERMINAL']} ***")
