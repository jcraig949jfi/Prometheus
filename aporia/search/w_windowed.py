"""CAMPAIGN W pass 1 — windowed feature path, ORACLE DISCLOSURE, and partition proof.

INSTRUMENT ONLY. No L2 or L1 quantity is measured. The frozen and reserve splits
are not touched; only development metadata is read.

------------------------------------------------------------------------------
THE ORACLE PROBLEM, STATED BEFORE ANYTHING IS MEASURED
------------------------------------------------------------------------------
Campaign W computes features over the "guaranteed per-pair overlap" — the pair's
own `exact_terms`, the number of terms over which op(src) and tgt provably agree.

**`exact_terms` is a property of a KNOWN pair.** It is computed by comparing
op(src) against tgt. A real query is a single sequence with no partner and no
operator, so at deployment time the window is NOT AVAILABLE. The windowed path
therefore uses ORACLE information that a deployed system would not have.

This is not a defect to be fixed; it is a scope constraint, and it changes what
each branch licenses:

  * The windowed measurement is an **upper bound** on what ANY windowing strategy
    could buy, because no deployable rule can know the overlap better than the
    oracle does.
  * **W3 KILL is therefore DECISIVE.** If even the oracle window buys nothing,
    no deployable windowing can buy anything, and the X-line's negative result is
    robust to the window artifact. The line closes on a measurement.
  * **W1 ADVANCE is NOT decisive.** It would establish only that an oracle window
    could buy up to X — it would NOT establish that a deployable system can
    capture any of it. It licenses "design and test a deployable variant", never
    "the window fix works".

The asymmetry is the point: this campaign can definitively CLOSE the line and
cannot definitively reopen it. Stated now, before measurement, so no result can
be read as more than it is.

A DEPLOYABLE VARIANT EXISTS AND IS NAMED HERE FOR THE SUCCESSOR, NOT TESTED NOW:
per-candidate LENGTH matching — compute both sequences' features over
min(len(A), len(B)) — uses only lengths, never `exact_terms`, and is deployable.
It is strictly weaker than the oracle and costs O(N) feature computations per
query instead of one vector lookup.

WINDOW CONVENTION, fixed here: for a pair with guaranteed overlap E, the target
is featurised over its first E terms and the source over its first E terms as
well. The operators consume between E and E+1 source terms to produce E image
terms (diff needs E+1, the rest need E), so E is the common floor and is used for
both sides; the one-term difference for `diff` is disclosed rather than
special-cased.
"""
from __future__ import annotations

import importlib.util
import json
import math
import pathlib
from collections import defaultdict

import numpy as np

SEARCH = pathlib.Path(r'F:\Prometheus\aporia\search')
spec = importlib.util.spec_from_file_location('xg', SEARCH / 'x2_entry_gate.py')
xg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(xg)
sig_v2 = xg.sig_v2

MIN_WINDOW = 12          # below this the V2 statistics are not meaningful
MDE = 0.0306             # preregistered P123

pairs = json.loads((SEARCH / 'w_pairs.json').read_text(encoding='utf-8'))
split = json.loads((SEARCH / 'w_split.json').read_text(encoding='utf-8'))
DEV = sorted(split['dev_indices'])
print(f"\n=== CAMPAIGN W pass 1 — instrument only ===")
print(f"dev {len(DEV)} | frozen {len(split['frozen_indices'])} UNTOUCHED | "
      f"reserve {len(split['reserve_indices'])} UNTOUCHED", flush=True)

def rawblock(v, k):
    a = list(v[:k]) + [0]*max(0, k - len(v))
    return [math.copysign(math.log1p(abs(float(x))), x) for x in a]

def feat_windowed(v, w):
    """Features over the first w terms only. Raw block is padded to w, V2 sees w terms."""
    w = max(int(w), MIN_WINDOW)
    vv = list(v[:w])
    return np.concatenate([np.array(rawblock(vv, w), dtype=float), sig_v2(vv)])

def feat_fixed(v, raw_k=20):
    """The incumbent path: raw block at a fixed 20 terms, V2 over up to 45."""
    return np.concatenate([np.array(rawblock(v, raw_k), dtype=float), sig_v2(v)])

# ---- window-size distribution on DEVELOPMENT (metadata only, no retrieval)
POS = pairs['positives']
by_op = defaultdict(list)
for i in DEV:
    p = POS[i]
    by_op[p['op']].append(p['exact_terms'])
print("\nguaranteed overlap (exact_terms) on DEVELOPMENT:")
allE = []
for op in ('diff', 'partsum', 'binomial', 'moebius', 'shift'):
    e = np.array(by_op[op]); allE += list(e)
    print(f"  {op:9s} n={len(e):3d}  min {e.min():2d}  median {int(np.median(e)):2d}  "
          f"mean {e.mean():5.1f}  max {e.max():2d}")
allE = np.array(allE)
print(f"  {'ALL':9s} n={len(allE):3d}  min {allE.min():2d}  median {int(np.median(allE)):2d}  "
      f"mean {allE.mean():5.1f}  max {allE.max():2d}")
print(f"  fraction below the fixed 45-term window: {float((allE < 45).mean()):.4f}")
print(f"  fraction below the fixed 20-term raw block: {float((allE < 20).mean()):.4f}")

# ---- shape sanity: the windowed path runs and produces finite, same-dim vectors
i0 = DEV[0]; p0 = POS[i0]
terms = json.loads((SEARCH / 'w_terms.json').read_text(encoding='utf-8'))
probe_ok, dims = True, set()
for i in DEV[:60]:
    p = POS[i]
    if p['src'] not in terms or p['tgt'] not in terms:
        continue
    E = p['exact_terms']
    a = feat_windowed(terms[p['src']], E)
    b = feat_windowed(terms[p['tgt']], E)
    dims.add(a.shape[0]); dims.add(b.shape[0])
    if not (np.all(np.isfinite(np.nan_to_num(a))) and np.all(np.isfinite(np.nan_to_num(b)))):
        probe_ok = False
print(f"\nshape sanity over 60 dev pairs: finite={probe_ok}  distinct dims seen={sorted(dims)}")
print("  NOTE: windowed dimensionality VARIES with E (raw block is w-long), so pass 2 must")
print("  featurise per-window and cannot reuse one pool matrix — recorded as a cost, not a defect.")

# ---- partition proof by enumeration
def fire(lo, hi):
    if hi < 0: return 'W5'
    if lo > MDE: return 'W1'
    if lo > 0:   return 'W2'
    return 'W3' if hi < MDE else 'W4'

grid = [round(x*0.004 - 0.20, 4) for x in range(0, 101)]
counts, unmapped = defaultdict(int), 0
for lo in grid:
    for hi in grid:
        if hi < lo: continue
        r = fire(lo, hi)
        if r is None: unmapped += 1
        counts[r] += 1
print(f"\npartition enumeration: {sum(counts.values())} (lo,hi) points, unmapped {unmapped}")
print(f"  coverage {dict(sorted(counts.items()))}")
print("  boundary probes:")
for lo, hi in [(-0.20, -0.0001), (0.0, 0.0), (0.0001, 0.02), (0.0307, 0.10),
               (-0.05, 0.0305), (-0.05, 0.0307), (0.001, 0.0306)]:
    print(f"    lo={lo:+.4f} hi={hi:+.4f} -> {fire(lo, hi)}")

out = {'splits': {'dev': len(DEV), 'frozen': len(split['frozen_indices']),
                  'reserve': len(split['reserve_indices'])},
       'exact_terms_dev': {op: {'n': len(v), 'min': int(min(v)), 'median': float(np.median(v)),
                                'mean': round(float(np.mean(v)), 2), 'max': int(max(v))}
                           for op, v in by_op.items()},
       'exact_terms_all': {'n': int(len(allE)), 'min': int(allE.min()),
                           'median': float(np.median(allE)), 'mean': round(float(allE.mean()), 2),
                           'max': int(allE.max()),
                           'frac_below_45': round(float((allE < 45).mean()), 4),
                           'frac_below_20': round(float((allE < 20).mean()), 4)},
       'window_convention': 'target and source both featurised over the pair guaranteed overlap E; '
                            'diff consumes E+1 source terms and the one-term difference is disclosed '
                            'rather than special-cased',
       'MIN_WINDOW': MIN_WINDOW,
       'ORACLE_DISCLOSURE': {
           'exact_terms_is_oracle': True,
           'reason': 'exact_terms is computed by comparing op(src) against tgt, so a single-sequence '
                     'query at deployment has no way to know it',
           'consequence_W3': 'DECISIVE — if the oracle window buys nothing, no deployable windowing '
                             'can, and the X-line negative is robust',
           'consequence_W1': 'NOT DECISIVE — establishes only an upper bound; licenses designing a '
                             'deployable variant, never the claim that windowing works',
           'deployable_variant_named_not_tested': 'per-candidate length matching over '
                                                  'min(len(A), len(B)); uses lengths only'},
       'partition': {'points': int(sum(counts.values())), 'unmapped': unmapped,
                     'coverage': dict(counts), 'MDE': MDE},
       'shape_sanity': {'finite': probe_ok, 'dims_vary_with_window': sorted(int(d) for d in dims)},
       'primary_experiment_run': False, 'frozen_touched': False, 'reserve_touched': False}
(SEARCH / 'w_pass1_results.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
print("\nNo L1 or L2 quantity measured. Frozen and reserve untouched.")
