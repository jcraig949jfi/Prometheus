"""CAMPAIGN W pass 2/3 — measure W on DEVELOPMENT only.

Frozen and reserve splits are loaded only to be counted and excluded. Branches
W1-W5 are FINAL and are NOT adjudicated here.

DESIGN, as settled in pass 1:
  raw block FIXED at 20 terms in every variant (0.0% of pairs have exact_terms
  below 20, so the raw block never over-reads and windowing it is a no-op);
  V2 block either FIXED (full sequence, up to 45 terms) or WINDOWED to the pair's
  guaranteed overlap quantised to a bucket lower edge:
        E in 20-24 -> 20 | 25-32 -> 25 | 33-40 -> 33 | 41-45 -> 41
  Constant 145 dimensions in both variants, because sig_v2 returns 125 features
  regardless of input length.

THREE ARMS, and one of them is structurally zero:
  A combined   raw20 + V2   fixed vs windowed   <- the primary W
  B v2_only    V2 alone     fixed vs windowed   <- isolates the windowed component
  C raw_only   raw20 alone                      <- W is IDENTICALLY ZERO by
     construction, because raw@20 sits inside every pair's overlap so the window
     cannot change it. Reported as a structural control, not computed: if the
     machinery ever produced a non-zero W here it would be a bug.

NO LOCAL SCALING. Both variants of each arm receive identical treatment, so the
within-arm comparison is clean without it; adding hubness correction would require
measuring hubness separately in five spaces and would not improve the contrast.
Stated as a deliberate simplification.

NOTHING IS TUNED IN RESPONSE TO W. If the windowed path is worse, that is reported
and pass 3 still reads frozen once.
"""
from __future__ import annotations

import gzip
import importlib.util
import json
import math
import pathlib
import random
from collections import defaultdict

import numpy as np

ROOT = pathlib.Path(r'F:\Prometheus')
SEARCH = ROOT / 'aporia' / 'search'
spec = importlib.util.spec_from_file_location('xg', SEARCH / 'x2_entry_gate.py')
xg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(xg)
sig_v2, OPS = xg.sig_v2, xg.OPS

RAW_K, MIN_WINDOW, HASH_K, MIN_EXACT, MIN_TERMS, MAX_TERMS = 20, 12, 12, 20, 25, 45
BUCKETS = [(20, 24, 20), (25, 32, 25), (33, 40, 33), (41, 45, 41)]

pairs = json.loads((SEARCH / 'w_pairs.json').read_text(encoding='utf-8'))
split = json.loads((SEARCH / 'w_split.json').read_text(encoding='utf-8'))
terms = json.loads((SEARCH / 'w_terms.json').read_text(encoding='utf-8'))
DEV = sorted(split['dev_indices'])
print(f"\n=== CAMPAIGN W pass 2 — DEVELOPMENT ONLY: {len(DEV)} pairs "
      f"(frozen {len(split['frozen_indices'])} + reserve {len(split['reserve_indices'])} untouched) ===", flush=True)

def bucket_of(E):
    for lo, hi, edge in BUCKETS:
        if lo <= E <= hi:
            return edge
    return BUCKETS[-1][2] if E > 45 else BUCKETS[0][2]

def nondeg(v):
    w = v[:MIN_TERMS]
    return len(set(w)) >= 8 and not all(x == w[-1] for x in w[-6:])

rng = random.Random(20260823)
cands = []
with gzip.open(ROOT / 'prometheus_data/oeis/stripped.gz', 'rt', encoding='utf-8', errors='replace') as fh:
    for line in fh:
        if line.startswith('#'):
            continue
        p = line.strip().rstrip(',').split(',')
        if len(p) < MIN_TERMS + 1:
            continue
        try:
            t = [int(x) for x in p[1:MAX_TERMS + 1]]
        except ValueError:
            continue
        if len(t) >= MIN_TERMS and nondeg(t):
            cands.append(t)
rng.shuffle(cands)
pool = dict(terms)
for i, t in enumerate(cands[:20000]):
    pool[f"D{i:06d}"] = t
ids = list(pool); idx_of = {k: i for i, k in enumerate(ids)}
NP = len(pool)
print(f"pool: {NP:,}", flush=True)

index = defaultdict(list)
for k, v in pool.items():
    if len(v) >= HASH_K:
        index[tuple(v[:HASH_K])].append(k)

def overlap(a, b):
    n, i = min(len(a), len(b)), 0
    while i < n and a[i] == b[i]:
        i += 1
    return i

def valid_partners(src, op):
    try:
        img0 = OPS[op](pool[src])
    except (ValueError, OverflowError):
        return set()
    out = set()
    for drop in (0, 1):
        im = img0[drop:]
        if len(im) < HASH_K: continue
        for cid in index.get(tuple(im[:HASH_K]), ()):
            if cid != src and overlap(im, pool[cid]) >= MIN_EXACT:
                out.add(cid)
    return out

def rawvec(v):
    a = list(v[:RAW_K]) + [0]*max(0, RAW_K - len(v))
    return [math.copysign(math.log1p(abs(float(x))), x) for x in a]

# ------------------------------------------------- SANITY CHECKS FIRST
POS = pairs['positives']
sane = {'pairs_checked': 0, 'bucket_ok': 0, 'below_min_window': 0, 'window_gt_E': 0,
        'v2_dim_constant': True}
dims = set()
for i in DEV:
    p = POS[i]
    if p['src'] not in pool or p['tgt'] not in pool: continue
    E = p['exact_terms']; w = bucket_of(E)
    sane['pairs_checked'] += 1
    if any(lo <= E <= hi and w == edge for lo, hi, edge in BUCKETS): sane['bucket_ok'] += 1
    if w < MIN_WINDOW: sane['below_min_window'] += 1
    if w > E: sane['window_gt_E'] += 1
    if sane['pairs_checked'] <= 40:
        dims.add(len(sig_v2(pool[p['tgt']][:w])))
sane['v2_dim_constant'] = (len(dims) == 1)
sane['v2_dim'] = sorted(dims)
print(f"\nSANITY: pairs {sane['pairs_checked']} | bucket assignment correct {sane['bucket_ok']} | "
      f"below MIN_WINDOW {sane['below_min_window']} | window exceeding E {sane['window_gt_E']} | "
      f"V2 dim constant {sane['v2_dim_constant']} {sane['v2_dim']}")
assert sane['bucket_ok'] == sane['pairs_checked'] and sane['window_gt_E'] == 0

# ------------------------------------------------- featurise the pool
RAWP = np.vstack([rawvec(pool[i]) for i in ids])
print("\nfeaturising pool: 1 fixed + 4 bucket windows...", flush=True)
V2_FIXED = np.nan_to_num(np.vstack([sig_v2(pool[i]) for i in ids]))
V2_WIN = {}
for lo, hi, edge in BUCKETS:
    V2_WIN[edge] = np.nan_to_num(np.vstack([sig_v2(pool[i][:edge]) for i in ids]))
    print(f"  window {edge}: done", flush=True)
v2_calls = NP * (1 + len(BUCKETS))
print(f"V2 calls over pool: {NP:,} x {1+len(BUCKETS)} = {v2_calls:,} (pass-1 estimate ~100k for 4 buckets)")

def zs(M):
    mu, sd = M.mean(0), M.std(0); sd[sd == 0] = 1.0
    return (M - mu)/sd

def build(arm, win):
    if arm == 'combined':
        M = np.hstack([RAWP, V2_FIXED if win is None else V2_WIN[win]])
    else:
        M = V2_FIXED if win is None else V2_WIN[win]
    return zs(np.nan_to_num(M))

SPACES = {('combined', None): build('combined', None),
          ('v2_only', None): build('v2_only', None)}
for _, _, edge in BUCKETS:
    SPACES[('combined', edge)] = build('combined', edge)
    SPACES[('v2_only', edge)] = build('v2_only', edge)
print(f"spaces built: {len(SPACES)} | dims combined {SPACES[('combined',None)].shape[1]} "
      f"| v2_only {SPACES[('v2_only',None)].shape[1]}")

asets = {}
for i in DEV:
    p = POS[i]
    if p['src'] in pool and p['tgt'] in pool:
        asets[i] = valid_partners(p['src'], p['op'])
REAL = [i for i in DEV if i in asets and POS[i]['op'] != 'shift']
SHIFT = [i for i in DEV if i in asets and POS[i]['op'] == 'shift']

def top10(Z, sid):
    d = np.linalg.norm(Z - Z[idx_of[sid]], axis=1)
    d[idx_of[sid]] = np.inf
    return set(ids[j] for j in np.argsort(d, kind='stable')[:10])

def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 0.0)
    p = k/n; d = 1 + z*z/n
    c = (p + z*z/(2*n))/d
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/d
    return (round(c-h, 4), round(c+h, 4))

res = {'pool': NP, 'dev_pairs': len(DEV), 'real_op_pairs': len(REAL),
       'sanity': sane, 'v2_calls_over_pool': v2_calls,
       'raw_only_arm': {'W': 0.0, 'reason': 'raw@20 sits inside every pair guaranteed overlap '
                        '(0% of pairs have exact_terms < 20), so windowing cannot change it; '
                        'structurally zero, not computed'},
       'arms': {}}

for arm in ('combined', 'v2_only'):
    hf, hw = {}, {}
    for i in REAL + SHIFT:
        p = POS[i]
        hf[i] = bool(top10(SPACES[(arm, None)], p['src']) & asets[i])
        w = bucket_of(p['exact_terms'])
        hw[i] = bool(top10(SPACES[(arm, w)], p['src']) & asets[i])
    kf = sum(hf[i] for i in REAL); kw = sum(hw[i] for i in REAL); n = len(REAL)
    b = sum(1 for i in REAL if hw[i] and not hf[i])
    c = sum(1 for i in REAL if hf[i] and not hw[i])
    W = (b - c)/n
    se = math.sqrt(max((b + c) - (b - c)**2/n, 0))/n
    disc = (b + c)/n
    res['arms'][arm] = {
        'fixed': f"{kf}/{n}", 'fixed_rate': round(kf/n, 4), 'fixed_wilson': list(wilson(kf, n)),
        'windowed': f"{kw}/{n}", 'windowed_rate': round(kw/n, 4), 'windowed_wilson': list(wilson(kw, n)),
        'W': round(W, 4), 'b_windowed_only': b, 'c_fixed_only': c, 'n': n,
        'se_paired': round(se, 5), 'ci95_paired': [round(W-1.96*se, 4), round(W+1.96*se, 4)],
        'discordance': round(disc, 4),
        'shift_control_fixed': f"{sum(hf[i] for i in SHIFT)}/{len(SHIFT)}",
        'shift_control_windowed': f"{sum(hw[i] for i in SHIFT)}/{len(SHIFT)}"}
    a = res['arms'][arm]
    print(f"\n{arm}:  fixed {a['fixed']} = {a['fixed_rate']:.4f} CI {a['fixed_wilson']} | "
          f"windowed {a['windowed']} = {a['windowed_rate']:.4f} CI {a['windowed_wilson']}")
    print(f"  W = {W:+.4f} CI {a['ci95_paired']} (b={b} windowed-only, c={c} fixed-only, "
          f"discordance {disc:.4f})")
    print(f"  shift control: fixed {a['shift_control_fixed']} windowed {a['shift_control_windowed']}")

# ---- MDE RESTATED from the OBSERVED within-arm discordance
prim = res['arms']['combined']['discordance']
mde = 2*math.sqrt(prim/800) if prim > 0 else None
res['MDE'] = {'preregistered_P123': 0.0306, 'preregistered_assumed_discordance': 0.15,
              'observed_within_arm_discordance': prim,
              'restated_MDE_at_frozen_n800': (round(mde, 4) if mde else None),
              'note': 'frozen carries 800 four-real-operator pairs; the P123 figure assumed a '
                      'discordance never measured for a within-arm window comparison'}
print(f"\nMDE RESTATED: observed within-arm discordance {prim:.4f} -> MDE at frozen n=800 is "
      f"{mde:.4f} (P123 preregistered 0.0306 from an assumed 0.15)")
res['primary_experiment_on_frozen'] = False
(SEARCH / 'w_pass2_results.json').write_text(json.dumps(res, indent=1), encoding='utf-8')
print("\nFrozen and reserve untouched. W1-W5 not adjudicated.")
