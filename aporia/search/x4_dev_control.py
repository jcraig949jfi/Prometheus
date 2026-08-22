"""CAMPAIGN X-4 pass 2 supplement — the control that decides whether the
development L2 gain is real or an artifact of a collapsed space.

THE OBSERVATION THAT DEMANDS THIS. The learned metric raises development L2 from
56/320 to 122/320 while L1 COLLAPSES from ~0.96 (X-3's V2) to 272/400 = 0.680,
with binomial at 3/80. A metric that improves relational proximity while
destroying identity is one story. A metric that has simply COARSENED the space —
so that any query's top-10 is more likely to contain any small set of sequences —
produces the same two symptoms and is not a discovery at all.

TWO CONTROLS, both preregistered here before either is run:

  C1  PERMUTATION NULL ON ANSWER SETS. For each development pair, score the
      source's top-10 against a DIFFERENT pair's answer set. A genuinely
      relational metric should score near zero here while scoring high on the
      true answer sets. A merely coarsened space lifts BOTH. The diagnostic is
      the ratio true:permuted, compared between the learned and raw arms.

  C2  LIKE-FOR-LIKE PROCESSING. The pre-committed skew > 1.0 rule applied local
      scaling to the learned space (skew 1.305) but NOT to raw (skew 0.952), so
      the two arms received different processing and the headline D confounds
      representation with correction. Both arms are re-scored with NO local
      scaling so the comparison is like-for-like.

Neither control can change the preregistered branches; both are development-only
diagnostics that determine what the pass may honestly claim.

NO FROZEN QUANTITY IS COMPUTED IN THIS FILE.
"""
from __future__ import annotations

import importlib.util
import json
import math
import pathlib
import random

import numpy as np

SEARCH = pathlib.Path(r'F:\Prometheus\aporia\search')
spec = importlib.util.spec_from_file_location('xf', SEARCH / 'x4_dev_fit.py')
xf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(xf)

LEARN, RAWZ, ids, idx_of = xf.LEARN, xf.RAWZ, xf.ids, xf.idx_of
asets, DEV, POS, K = xf.asets, xf.DEV, xf.POS, xf.K
RK_L, RK_R = xf.RK_L, xf.RK_R

REAL = [i for i in DEV if i in asets and POS[i]['op'] != 'shift']
rng = random.Random(20260826)

def top10(Z, src_id, rk=None, use=False):
    d = np.linalg.norm(Z - Z[idx_of[src_id]], axis=1)
    if use and rk is not None:
        kq = np.sort(np.partition(d, K)[:K + 1])[K - 1]
        d = d / np.sqrt(max(kq, 1e-6) * rk)
    d[idx_of[src_id]] = np.inf
    return set(ids[j] for j in np.argsort(d, kind='stable')[:10])

def wilson(k_, n_, z=1.96):
    if n_ == 0: return (0.0, 0.0)
    p = k_/n_; dd = 1 + z*z/n_
    c = (p + z*z/(2*n_))/dd
    h = z*math.sqrt(p*(1-p)/n_ + z*z/(4*n_*n_))/dd
    return (round(c-h, 4), round(c+h, 4))

# permuted assignment of answer sets, fixed once and shared by both arms
perm = REAL[:]
rng.shuffle(perm)
while any(a == b for a, b in zip(REAL, perm)):          # derangement
    rng.shuffle(perm)

out = {'n_real_ops': len(REAL)}
for label, Z, rk in (('learned', LEARN, RK_L), ('raw', RAWZ, RK_R)):
    for corr in (True, False):
        t = p_ = 0
        for i, j in zip(REAL, perm):
            top = top10(Z, POS[i]['src'], rk, corr)
            t += bool(top & asets[i])
            p_ += bool(top & asets[j])
        key = f"{label}_{'localscaled' if corr else 'plain'}"
        out[key] = {'true': f"{t}/{len(REAL)}", 'true_rate': round(t/len(REAL), 4),
                    'true_wilson': list(wilson(t, len(REAL))),
                    'permuted': f"{p_}/{len(REAL)}", 'permuted_rate': round(p_/len(REAL), 4),
                    'permuted_wilson': list(wilson(p_, len(REAL))),
                    'ratio_true_over_permuted': (round(t/p_, 2) if p_ else None)}
        print(f"{key:22s} true {t:3d}/{len(REAL)} = {t/len(REAL):.4f} | permuted {p_:3d}/{len(REAL)} "
              f"= {p_/len(REAL):.4f} | ratio {out[key]['ratio_true_over_permuted']}", flush=True)

# like-for-like D, both arms UNCORRECTED
hl = {i: bool(top10(LEARN, POS[i]['src']) & asets[i]) for i in REAL}
hr = {i: bool(top10(RAWZ, POS[i]['src']) & asets[i]) for i in REAL}
b = sum(1 for i in REAL if hl[i] and not hr[i]); c = sum(1 for i in REAL if hr[i] and not hl[i])
n = len(REAL); D = (b - c)/n
se = math.sqrt(max((b + c) - (b - c)**2/n, 0))/n
out['D_like_for_like_no_local_scaling'] = {
    'value': round(D, 4), 'b': b, 'c': c, 'n': n, 'se_paired': round(se, 5),
    'ci95_paired': [round(D - 1.96*se, 4), round(D + 1.96*se, 4)],
    'discordance': round((b + c)/n, 4)}
print(f"\nlike-for-like D (neither arm local-scaled) = {D:+.4f} "
      f"CI {out['D_like_for_like_no_local_scaling']['ci95_paired']} (b={b}, c={c})")
out['frozen_quantities_computed'] = False
(SEARCH / 'x4_dev_control.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
print("\nNO frozen quantity computed.")
