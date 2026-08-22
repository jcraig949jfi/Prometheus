"""CAMPAIGN W pass 3/3 — TERMINAL. frozen read ONCE. reserve NEVER opened.

Branches W1-W5 applied EXACTLY as preregistered in W_PASS1, with the ORIGINAL
MDE of 0.0306 — even though pass 2 measured the true MDE at 0.0106 and showed the
bar sits at roughly three times the achievable resolution. Moving a threshold
after seeing a development effect would void the campaign. The mismatch is
reported beside the verdict as an explicitly labelled COUNTERFACTUAL that changes
nothing.

Construction is byte-identical to w_pass2.py — same seeds, same pool, same
bucket edges, same raw block, same z-scoring — so nothing here is attributable to
a pipeline change. Development scoring is not repeated (it would add minutes and
is already recorded); the spaces are rebuilt by the same code path.

PASS-1 SCOPING, which bounds what any verdict may claim:
  the window is ORACLE information a real query cannot have, so
  W3 KILL is DECISIVE (no deployable rule beats the oracle), and
  W1 ADVANCE is an UPPER BOUND that licenses designing a deployable variant,
  never the claim that windowing works.
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

RAW_K, HASH_K, MIN_EXACT, MIN_TERMS, MAX_TERMS = 20, 12, 20, 25, 45
BUCKETS = [(20, 24, 20), (25, 32, 25), (33, 40, 33), (41, 45, 41)]
MDE_PREREG = 0.0306
MDE_MEASURED_DEV = 0.0106

pairs = json.loads((SEARCH / 'w_pairs.json').read_text(encoding='utf-8'))
split = json.loads((SEARCH / 'w_split.json').read_text(encoding='utf-8'))
terms = json.loads((SEARCH / 'w_terms.json').read_text(encoding='utf-8'))
FRO = sorted(split['frozen_indices'])
print(f"\n=== CAMPAIGN W TERMINAL — frozen READ ONCE: {len(FRO)} pairs | "
      f"reserve {len(split['reserve_indices'])} NEVER OPENED ===", flush=True)

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

def zs(M):
    mu, sd = M.mean(0), M.std(0); sd[sd == 0] = 1.0
    return (M - mu)/sd

RAWP = np.vstack([rawvec(pool[i]) for i in ids])
print("featurising pool: 1 fixed + 4 windows...", flush=True)
V2F = np.nan_to_num(np.vstack([sig_v2(pool[i]) for i in ids]))
V2W = {}
for _, _, e in BUCKETS:
    V2W[e] = np.nan_to_num(np.vstack([sig_v2(pool[i][:e]) for i in ids]))
SP = {('combined', None): zs(np.nan_to_num(np.hstack([RAWP, V2F]))),
      ('v2_only', None): zs(np.nan_to_num(V2F))}
for _, _, e in BUCKETS:
    SP[('combined', e)] = zs(np.nan_to_num(np.hstack([RAWP, V2W[e]])))
    SP[('v2_only', e)] = zs(np.nan_to_num(V2W[e]))
print(f"spaces built: {len(SP)}", flush=True)

# ---------------------------------------------- STEP 1: frozen answer sets
POS = pairs['positives']
asets = {}
for i in FRO:
    p = POS[i]
    if p['src'] in pool and p['tgt'] in pool:
        asets[i] = valid_partners(p['src'], p['op'])
missing = sum(1 for i in FRO if i in asets and POS[i]['tgt'] not in asets[i])
REAL = [i for i in FRO if i in asets and POS[i]['op'] != 'shift']
SHIFT = [i for i in FRO if i in asets and POS[i]['op'] == 'shift']
mV = float(np.mean([len(asets[i]) for i in REAL]))
ADJ = 10*mV/NP; THR = 3*ADJ
print(f"\nsanity: recorded target absent from own answer set = {missing}")
print(f"frozen mean |V| (four real ops) = {mV:.4f} -> adjusted chance {ADJ:.6f}, G-pos threshold {THR:.6f}")
print(f"per-draw granularity at n={len(REAL)}: 1 hit = {1/len(REAL):.6f}")

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

print("\nscoring frozen...", flush=True)
TOP = {}
for arm in ('combined', 'v2_only'):
    TOP[(arm, 'fixed')] = {i: top10(SP[(arm, None)], POS[i]['src']) for i in REAL + SHIFT}
    TOP[(arm, 'win')] = {i: top10(SP[(arm, bucket_of(POS[i]['exact_terms']))], POS[i]['src'])
                         for i in REAL + SHIFT}

# ---------------------------------------------- STEP 2: G-pos
prng = random.Random(20260831)
gp = {}
for variant in ('fixed', 'win'):
    vals = []
    for _ in range(20):
        perm = REAL[:]
        prng.shuffle(perm)
        while any(a == b for a, b in zip(REAL, perm)):
            prng.shuffle(perm)
        vals.append(sum(bool(TOP[('combined', variant)][i] & asets[j])
                        for i, j in zip(REAL, perm))/len(REAL))
    v = np.array(vals)
    gp[variant] = {'mean': round(float(v.mean()), 6), 'min': round(float(v.min()), 6),
                   'max': round(float(v.max()), 6)}
GPOS = bool(gp['fixed']['mean'] <= THR and gp['win']['mean'] <= THR)
print(f"\nG-pos (mean over 20 derangements, threshold {THR:.6f}):")
for k_, v in gp.items():
    print(f"  {k_:6s} mean {v['mean']:.6f} (min {v['min']:.6f} max {v['max']:.6f})")
print(f"  -> G-pos {'HOLDS' if GPOS else 'VIOLATED'}")

res = {'frozen_pairs': len(FRO), 'reserve_not_opened': len(split['reserve_indices']),
       'pool': NP, 'real_op_pairs': len(REAL),
       'recorded_target_absent_from_answer_set': missing,
       'frozen_mean_V': round(mV, 4), 'adjusted_chance': round(ADJ, 6),
       'G_pos_threshold': round(THR, 6), 'per_draw_granularity': round(1/len(REAL), 6),
       'G_pos': {**gp, 'HOLDS': GPOS}}

if not GPOS:
    res.update({'W_measured': False, 'TERMINAL': 'PARK', 'branch_fired': 'G-pos violated',
                'reason': 'G-pos violated on frozen; artifact suspected, nothing further computed'})
    print("\nG-pos violated. TERMINAL: PARK")
else:
    res['arms'] = {}
    for arm in ('combined', 'v2_only'):
        hf = {i: bool(TOP[(arm, 'fixed')][i] & asets[i]) for i in REAL}
        hw = {i: bool(TOP[(arm, 'win')][i] & asets[i]) for i in REAL}
        kf, kw, n = sum(hf.values()), sum(hw.values()), len(REAL)
        b = sum(1 for i in REAL if hw[i] and not hf[i])
        c = sum(1 for i in REAL if hf[i] and not hw[i])
        Wv = (b - c)/n
        se = math.sqrt(max((b + c) - (b - c)**2/n, 0))/n
        res['arms'][arm] = {
            'fixed': f"{kf}/{n}", 'fixed_rate': round(kf/n, 4), 'fixed_wilson': list(wilson(kf, n)),
            'windowed': f"{kw}/{n}", 'windowed_rate': round(kw/n, 4), 'windowed_wilson': list(wilson(kw, n)),
            'W': round(Wv, 4), 'b_windowed_only': b, 'c_fixed_only': c, 'n': n,
            'se_paired': round(se, 5),
            'ci95_paired': [round(Wv-1.96*se, 4), round(Wv+1.96*se, 4)],
            'discordance': round((b+c)/n, 4),
            'shift_fixed': f"{sum(bool(TOP[(arm,'fixed')][i] & asets[i]) for i in SHIFT)}/{len(SHIFT)}",
            'shift_windowed': f"{sum(bool(TOP[(arm,'win')][i] & asets[i]) for i in SHIFT)}/{len(SHIFT)}"}
        a = res['arms'][arm]
        print(f"\n{arm}: fixed {a['fixed']} = {a['fixed_rate']:.4f} CI {a['fixed_wilson']} | "
              f"windowed {a['windowed']} = {a['windowed_rate']:.4f} CI {a['windowed_wilson']}")
        print(f"  W = {a['W']:+.4f} CI {a['ci95_paired']} (b={b}, c={c}, discordance {a['discordance']:.4f})")
        print(f"  shift control: fixed {a['shift_fixed']} windowed {a['shift_windowed']}")

    prim = res['arms']['combined']
    lo, hi = prim['ci95_paired']
    disc = prim['discordance']
    mde_frozen = 2*math.sqrt(disc/len(REAL)) if disc > 0 else None
    res['discordance_transfer'] = {'dev': 0.0225, 'frozen': disc,
                                   'matched': bool(abs(disc - 0.0225) < 0.01),
                                   'frozen_MDE_from_observed': (round(mde_frozen, 4) if mde_frozen else None)}
    print(f"\ndiscordance transfer: dev 0.0225 -> frozen {disc:.4f} "
          f"({'MATCHED' if res['discordance_transfer']['matched'] else 'DID NOT MATCH'}); "
          f"frozen MDE from observed = {mde_frozen:.4f}")

    def fire(lo_, hi_, mde):
        if hi_ < 0: return 'W5', 'REDESIGN'
        if lo_ > mde: return 'W1', 'ADVANCE'
        if lo_ > 0: return 'W2', 'REDESIGN'
        return ('W3', 'KILL') if hi_ < mde else ('W4', 'PARK')

    br, term = fire(lo, hi, MDE_PREREG)
    res['W_measured'] = True
    res['branch_fired'] = br
    res['TERMINAL'] = term
    res['MDE_used'] = MDE_PREREG
    cf_br, cf_term = fire(lo, hi, 2*(mde_frozen or MDE_MEASURED_DEV))
    res['COUNTERFACTUAL_not_binding'] = {
        'threshold_as_2x_measured_MDE': round(2*(mde_frozen or MDE_MEASURED_DEV), 4),
        'branch': cf_br, 'terminal': cf_term,
        'note': 'reported for the record only; the preregistered threshold governs and was applied'}
    print(f"\nadjudication with PREREGISTERED MDE {MDE_PREREG}: {br} -> {term}")
    print(f"COUNTERFACTUAL (threshold = 2x measured MDE = "
          f"{res['COUNTERFACTUAL_not_binding']['threshold_as_2x_measured_MDE']}): {cf_br} -> {cf_term}"
          f"  [NOT BINDING]")

(SEARCH / 'w_terminal_results.json').write_text(json.dumps(res, indent=1), encoding='utf-8')
print(f"\n*** CAMPAIGN W TERMINAL: {res['TERMINAL']} ***")
print("reserve split never opened.")
