"""CYCLE 140-D pass 2 — the same question, with the instrument aimed at the support.

=========================== PREREGISTRATION (pass 2) ===========================
Committed BEFORE any computation. Pass 1 returned VACUOUS: 0 of 18 sequences passed
the nondeg() guard, because the first 20 terms of a conductor-indexed sequence are
structurally zero — the smallest conductor of an elliptic curve over Q is 11. The
instrument was aimed at an index window where the objects do not exist.

THE ONE CHANGE, and why it is not outcome-tuning:
  Index over the SUPPORT. Let K = sorted list of conductors N <= 100000 carrying at
  least one curve; define a(n) = count at K[n]. This is the standard construction
  used whenever a counting function is indexed by the objects that exist (as one
  indexes by the n-th prime rather than by n). The change is forced by a
  MATHEMATICAL FACT fixed before the data was seen — min conductor = 11 — and NOT
  by inspecting which indexing produces hits. No threshold, operator, exactness bar,
  guard, exclusion or control is altered from pass 1.

EVERYTHING ELSE IS HELD FIXED FROM PASS 1:
  same 9 raw + 9 cumulative sequences, same 7 non-trivial operators, same 5
  trivial-class operators reported separately, same >= 20-term exactness bar, same
  nondeg() guard reused verbatim, same 18 by-construction exclusions, same 9
  positive controls.

ATTAINABILITY (doctrine P138): computed and printed BEFORE the verdict. If the
  admissible-triple count is 0 again, the reading is VACUOUS a second time and the
  campaign terminates REDESIGN — counting sequences are then the wrong
  representation, which is itself the finding, and a third pass is NOT spent
  hunting for an indexing that works.

BRANCHES (partition verified by enumeration; corrected form from pass 1):
  B1 VACUOUS  C < 9 or attainable < 1
  B2 ADVANCE  C == 9 and attainable >= 1 and H >= 1
  B3 KILL     C == 9 and attainable >= 1 and H == 0

CONSEQUENCE, unchanged from pass 1:
  ADVANCE -> next cycle repeats the sweep on mf_newforms (second object class).
  KILL    -> the operator vocabulary does not reach arithmetic objects through
             counting sequences; the representation is abandoned, not the thesis.
  VACUOUS -> campaign terminates REDESIGN.

WHAT DIES ON A NULL: this operator family on LMFDB counting sequences. NOT the
  verbs thesis and NOT the 220 verified OEIS relations.
========================= END PREREGISTRATION (pass 2) =========================
"""
from __future__ import annotations

import json
import math
import pathlib

import psycopg2

ROOT = pathlib.Path(r'F:\Prometheus')
CMAX = 20000
MIN_TERMS = 20

COMB = [[math.comb(n, k) for k in range(n + 1)] for n in range(30)]
S2T = [[0] * 30 for _ in range(30)]
S2T[0][0] = 1
for _n in range(1, 30):
    for _k in range(1, _n + 1):
        S2T[_n][_k] = _k * S2T[_n - 1][_k] + S2T[_n - 1][_k - 1]

NMU = 400
MU = [0] * (NMU + 2)
MU[1] = 1
for i in range(1, NMU + 1):
    for j in range(2 * i, NMU + 1, i):
        MU[j] -= MU[i]


def f_diff(a):    return [a[i + 1] - a[i] for i in range(len(a) - 1)]
def f_partsum(a):
    o, s = [], 0
    for x in a:
        s += x
        o.append(s)
    return o
def f_binom(a):
    b = a[:24]
    return [sum(COMB[n][k] * b[k] for k in range(n + 1)) for n in range(len(b))]
def f_moebius(a):
    b = [0] + a[:NMU]
    return [sum(MU[n // d] * b[d] for d in range(1, n + 1) if n % d == 0)
            for n in range(1, len(b))]
def f_invbin(a):
    b = a[:24]
    return [sum(((-1) ** (n - k)) * COMB[n][k] * b[k] for k in range(n + 1)) for n in range(len(b))]
def f_sdiff(a):   return [a[i + 2] - 2 * a[i + 1] + a[i] for i in range(len(a) - 2)]
def f_stir2(a):
    b = a[:22]
    return [sum(S2T[n][k] * b[k] for k in range(n + 1)) for n in range(len(b))]
def f_shift(a):   return a[1:]
def f_rmax(a):
    o, m = [], a[0]
    for x in a:
        m = max(m, x)
        o.append(m)
    return o
def f_aer(a):
    o = []
    for x in a[:23]:
        o += [x, 0]
    return o[:-1]
def f_bise(a):    return a[0::2]
def f_biso(a):    return a[1::2]


NONTRIVIAL = {'diff': f_diff, 'partsum': f_partsum, 'binomial': f_binom,
              'moebius': f_moebius, 'inverse_binomial': f_invbin,
              'second_diff': f_sdiff, 'stirling2': f_stir2}
TRIVIAL = {'shift': f_shift, 'runmax': f_rmax, 'aerate': f_aer,
           'bisect_even': f_bise, 'bisect_odd': f_biso}


def nondeg(v):
    w = v[:MIN_TERMS]
    return len(set(w)) >= 8 and not all(x == w[-1] for x in w[-6:])


def overlap(a, b):
    n, i = min(len(a), len(b)), 0
    while i < n and a[i] == b[i]:
        i += 1
    return i


# ================================== RUN ====================================
print("CYCLE 140-D pass 2 — support-indexed")
print("=" * 74)
conn = psycopg2.connect(host='localhost', port=5432, dbname='lmfdb', user='postgres',
                        connect_timeout=15)
cur = conn.cursor()

SPECS = [('r_curves', "1=1"), ('r_classes', None), ('r_rank0', "rank::int = 0"),
         ('r_rank1', "rank::int = 1"), ('r_rank2p', "rank::int >= 2"),
         ('r_cm', "cm::int <> 0"), ('r_semistab', "semistable = 'True'"),
         ('r_torstriv', "torsion::int = 1"), ('r_torsnont', "torsion::int > 1")]

cur.execute("select distinct conductor::bigint from ec_curvedata where conductor::bigint <= %s "
            "order by 1", (CMAX,))
SUPPORT = [r[0] for r in cur.fetchall()]
print(f"support: {len(SUPPORT):,} conductors <= {CMAX:,} carrying >=1 curve "
      f"(min={SUPPORT[0]}, max={SUPPORT[-1]})")

seqs = {}
for name, where in SPECS:
    if name == 'r_classes':
        cur.execute("select conductor::bigint, count(distinct lmfdb_iso) from ec_curvedata "
                    "where conductor::bigint <= %s group by 1", (CMAX,))
    else:
        cur.execute(f"select conductor::bigint, count(*) from ec_curvedata "
                    f"where conductor::bigint <= %s and ({where}) group by 1", (CMAX,))
    d = dict(cur.fetchall())
    seqs[name] = [int(d.get(k, 0)) for k in SUPPORT]

RAW = [n for n, _ in SPECS]
for nm in RAW:
    seqs['c_' + nm[2:]] = f_partsum(seqs[nm])
NAMES = list(seqs.keys())
print(f"sequences built: {len(NAMES)}, length {len(SUPPORT):,} each")

print("\nDEGENERACY CENSUS:")
alive = []
for nm in NAMES:
    v = seqs[nm]
    ok = nondeg(v)
    if ok:
        alive.append(nm)
    print(f"  {nm:14s} first20={str(v[:8])[:38]:40s} distinct={len(set(v[:MIN_TERMS])):2d} nondeg={ok}")
print(f"  -> passing nondeg as SOURCE: {len(alive)} of {len(NAMES)}")

EXCL = set()
for nm in RAW:
    EXCL.add(('partsum', nm, 'c_' + nm[2:]))
    EXCL.add(('diff', 'c_' + nm[2:], nm))

controls = [(nm, 'c_' + nm[2:], overlap(f_partsum(seqs[nm]), seqs['c_' + nm[2:]])) for nm in RAW]
C = sum(1 for _, _, ov in controls if ov >= MIN_TERMS)
print(f"\nPOSITIVE CONTROLS firing: C = {C} of 9 (overlaps: {[ov for _,_,ov in controls]})")

# WINDOW: the exactness bar is 20 terms, so the sweep only needs a bounded prefix.
# Full-length sequences are retained for the positive controls (which ran on the
# complete support above). This is a compute bound, not a change to any threshold.
WINDOW = 200
for _k in list(seqs):
    seqs[_k] = seqs[_k][:WINDOW]
print(f"sweep window: first {WINDOW} terms (bar is {MIN_TERMS}; controls ran full-length)")

pairs = [(s, t) for s in alive for t in NAMES if s != t]
attainable = len(NONTRIVIAL) * len(pairs) - len([e for e in EXCL if e[0] in NONTRIVIAL and e[1] in alive])
print(f"\nATTAINABILITY: {len(alive)} sources x {len(NAMES)-1} targets x {len(NONTRIVIAL)} ops "
      f"- exclusions = {attainable:,} admissible triples")
print(f"  gate H >= 1 inside attainable range [0, {attainable:,}]? {attainable >= 1}")


def sweep(opset):
    hits = []
    for opname, fn in opset.items():
        for s, t in pairs:
            if (opname, s, t) in EXCL:
                continue
            try:
                img = fn(seqs[s])
            except Exception:
                continue
            if len(img) < MIN_TERMS:
                continue
            ov = overlap(img, seqs[t])
            if ov >= MIN_TERMS:
                hits.append({'operator': opname, 'source': s, 'target': t, 'exact_terms': ov})
    return hits


H_hits = sweep(NONTRIVIAL)
T_hits = sweep(TRIVIAL)
H = len(H_hits)
print(f"\nNON-TRIVIAL exact relations (headline): H = {H}")
for h in H_hits[:25]:
    print(f"    {h['operator']:18s} {h['source']:14s} -> {h['target']:14s} exact {h['exact_terms']} terms")
print(f"TRIVIAL-class hits (never headline): {len(T_hits)}")
for h in T_hits[:12]:
    print(f"    {h['operator']:18s} {h['source']:14s} -> {h['target']:14s} exact {h['exact_terms']} terms")

branches = {'B1_VACUOUS': (C < 9) or (attainable < 1),
            'B2_ADVANCE': C == 9 and attainable >= 1 and H >= 1,
            'B3_KILL':    C == 9 and attainable >= 1 and H == 0}
fired = [k for k, v in branches.items() if v]
print(f"\nBRANCHES: {branches}\n  exactly one fired? {len(fired)==1} -> {fired}")
assert len(fired) == 1
VERDICT = {'B1_VACUOUS': 'VACUOUS', 'B2_ADVANCE': 'ADVANCE', 'B3_KILL': 'KILL'}[fired[0]]

out = {'cycle': '140-D pass 2', 'index': 'support-indexed (conductors carrying >=1 curve)',
       'support_size': len(SUPPORT), 'conductor_max': CMAX,
       'sequences': NAMES, 'nondeg_survivors': alive,
       'controls_firing': C, 'attainable_triples': attainable,
       'gate_inside_attainable_range': bool(attainable >= 1),
       'headline_nontrivial_hits': H_hits, 'H': H, 'trivial_class_hits': T_hits,
       'branches': branches, 'branch_fired': fired[0], 'VERDICT': VERDICT}
(ROOT / 'aporia/search/cycle_140d_pass2_results.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
print(f"\n*** CYCLE 140-D pass 2 VERDICT: {VERDICT} ***")
