"""CYCLE 140-D — does the OEIS operator vocabulary reach arithmetic objects?

=============================== PREREGISTRATION ===============================
Committed in-script BEFORE any computation. Nothing below the RUN banner may
change anything above it.

QUESTION (binary, about mathematical objects, not about Aporia):
  The exactly-verifiable operator vocabulary produced 220 atomic relations among
  OEIS sequences (CANDIDATES_ATOMIC.jsonl). Does that same vocabulary produce ANY
  NON-TRIVIAL exact relation among counting sequences derived from LMFDB elliptic
  curves over Q?

WHY IT IS THE RIGHT OPERATIONALIZATION:
  The thesis is that mathematics has verbs — operations that bridge domains. Every
  test of it so far has lived inside OEIS, a corpus of integer sequences curated
  BECAUSE they are nice. If the operator vocabulary is a property of that curation
  rather than of arithmetic, it will not reach objects that were catalogued for
  entirely different reasons. Elliptic curves are such objects.

OBJECTS: elliptic curves over Q, LMFDB mirror table ec_curvedata, 3,824,372 rows.
INDEX:   conductor N = 1 .. 10000 (N with no curves contribute 0).

SEQUENCES (9 raw + their 9 cumulatives = 18), fixed here before extraction:
  r_curves     a(N) = # curves of conductor N
  r_classes    a(N) = # isogeny classes of conductor N
  r_rank0      a(N) = # curves of conductor N with rank 0
  r_rank1      a(N) = # curves of conductor N with rank 1
  r_rank2p     a(N) = # curves of conductor N with rank >= 2
  r_cm         a(N) = # curves of conductor N with CM
  r_semistab   a(N) = # semistable curves of conductor N
  r_torstriv   a(N) = # curves of conductor N with trivial torsion
  r_torsnont   a(N) = # curves of conductor N with non-trivial torsion
  c_<name>     cumulative counterpart of each raw sequence

OPERATORS (12), split by the P133 trivial-class distinction:
  NON-TRIVIAL (7, the headline): diff, partsum, binomial, moebius,
                                 inverse_binomial, second_diff, stirling2
  TRIVIAL     (5, reported separately, never in the headline):
                                 shift, runmax, aerate, bisect_even, bisect_odd
  Trivial-class operators are idempotent, subsequence-extracting, or zero-padding;
  P133 established that a relation built from one is not evidence of a bridge.

EXACTNESS BAR: agreement over >= 20 consecutive terms from the start of overlap,
  AND the source must pass the reused nondeg() guard (>= 8 distinct values in the
  compared window, not constant over its last 6 terms). Both reused verbatim from
  campaign_v_widen.py rather than reimplemented.

BY-CONSTRUCTION EXCLUSIONS, enumerated in advance (18 triples):
  (partsum, r_X, c_X) and (diff, c_X, r_X) for each of the 9 raw sequences.
  These are true by definition of the cumulative and are NOT findings.

POSITIVE CONTROL (S0), 9 of them: every (partsum, r_X, c_X) MUST be detected
  exact. These are the excluded pairs, used as controls precisely because they are
  known true. If fewer than 9 fire, the pipeline cannot detect a relation that is
  true by definition, the instrument is broken, and NO null may be read from it.

ATTAINABILITY (doctrine P138 — a gate must be shown REACHABLE before its null is
  read). Computed and printed BEFORE the verdict:
    max attainable headline count = 7 ops x 18 x 17 ordered pairs - 18 exclusions
  If the number of sequences surviving nondeg() is too small to make the headline
  statistic reach 1, the reading is VACUOUS, not null.

BRANCHES — verified to PARTITION by enumeration at run time. Let C = number of
positive controls firing (0..9) and H = headline non-trivial exact count (>=0):
  B1  C < 9                     -> VACUOUS. Instrument broken; no verdict on the
                                   question. Report and stop.
  B2  C == 9 and H >= 1         -> ADVANCE.
  B3  C == 9 and H == 0         -> KILL for this family.
  Exhaustive and mutually exclusive: C<9 or C==9 covers all C; given C==9, H>=1 or
  H==0 covers all non-negative integers H. Enumerated in code below.

NULL OUTPUT OF EVERY VERDICT RULE, stated as doctrine requires:
  - the exactness rule outputs "no relation" when overlap < 20 terms;
  - the nondeg rule outputs "source degenerate, pair not counted" and the pair is
    excluded from BOTH numerator and attainable denominator;
  - the control rule outputs VACUOUS, which is not a null and not a kill.

COUNTERFACTUAL-CONSEQUENCE TEST (doctrine P138), stated in advance:
  ADVANCE -> the next cycle extends the identical sweep to a SECOND object class
    (mf_newforms, 1,141,510 rows) to test whether the bridge is general or specific
    to elliptic curves. The 220 OEIS candidates gain a cross-corpus companion.
  KILL    -> the operator vocabulary is a property of the OEIS corpus and does not
    reach objects catalogued for other reasons. Counting sequences are abandoned as
    the representation for the verbs thesis, and later cycles must find verbs in a
    different representation rather than extending this operator family.
  IS THE DECISION ELIGIBLE TO GO DIFFERENTLY? Yes. Both branches are reachable
  (attainability is checked above), both name a different concrete next cycle, and
  neither is the status quo — this is not a capability that fires only where firing
  has no consequence.

WHAT DIES ON A NULL: this operator family applied to LMFDB COUNTING SEQUENCES.
  NOT the verbs thesis, and NOT the 220 OEIS relations, which are separately
  verified exact and stand on their own evidence.

KNOWN RISK, recorded before the result: counting sequences over conductor are
  zero-heavy and small-valued, so nondeg() may reject most raw sequences. That
  pushes the headline DOWN, i.e. toward KILL — the direction that flatters a tidy
  result. Per doctrine the zero-density and nondeg-survival counts are reported
  BESIDE the verdict, and if raw sequences are wiped out the reading is VACUOUS
  for those pairs rather than null.
============================= END PREREGISTRATION =============================
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

import psycopg2

ROOT = pathlib.Path(r'F:\Prometheus')
LIMIT = 10000
MIN_TERMS = 20

# ----------------------------------------------------------------- operators
# reused verbatim from aporia/search/campaign_v_widen.py (instrument reuse, not rebuild)
COMB = [[math.comb(n, k) for k in range(n + 1)] for n in range(30)]
S2T = [[0] * 30 for _ in range(30)]
S2T[0][0] = 1
for _n in range(1, 30):
    for _k in range(1, _n + 1):
        S2T[_n][_k] = _k * S2T[_n - 1][_k] + S2T[_n - 1][_k - 1]

MU = [0] * (LIMIT + 2)
MU[1] = 1
for i in range(1, LIMIT + 1):
    for j in range(2 * i, LIMIT + 1, i):
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
    # 1-indexed Moebius transform: b(n) = sum_{d|n} mu(n/d) a(d)
    b = [0] + a[:LIMIT]
    o = []
    for n in range(1, len(b)):
        o.append(sum(MU[n // d] * b[d] for d in range(1, n + 1) if n % d == 0))
    return o
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
    """reused verbatim from campaign_v_widen.py"""
    w = v[:MIN_TERMS]
    return len(set(w)) >= 8 and not all(x == w[-1] for x in w[-6:])


def overlap(a, b):
    n, i = min(len(a), len(b)), 0
    while i < n and a[i] == b[i]:
        i += 1
    return i


# ================================== RUN ====================================
print("CYCLE 140-D — OEIS operator vocabulary against LMFDB elliptic curves")
print("=" * 74)

conn = psycopg2.connect(host='localhost', port=5432, dbname='lmfdb', user='postgres',
                        connect_timeout=15)
cur = conn.cursor()

SPECS = [
    ('r_curves',    "1=1"),
    ('r_classes',   None),                       # counted via distinct isogeny class
    ('r_rank0',     "rank::int = 0"),
    ('r_rank1',     "rank::int = 1"),
    ('r_rank2p',    "rank::int >= 2"),
    ('r_cm',        "cm::int <> 0"),
    ('r_semistab',  "semistable = 'True'"),
    ('r_torstriv',  "torsion::int = 1"),
    ('r_torsnont',  "torsion::int > 1"),
]

seqs = {}
for name, where in SPECS:
    if name == 'r_classes':
        q = ("select conductor::bigint as n, count(distinct lmfdb_iso) from ec_curvedata "
             "where conductor::bigint <= %s group by 1")
        cur.execute(q, (LIMIT,))
    else:
        q = (f"select conductor::bigint as n, count(*) from ec_curvedata "
             f"where conductor::bigint <= %s and ({where}) group by 1")
        cur.execute(q, (LIMIT,))
    d = dict(cur.fetchall())
    seqs[name] = [int(d.get(n, 0)) for n in range(1, LIMIT + 1)]
    print(f"  extracted {name:12s} sum={sum(seqs[name]):>8,}")

RAW = [n for n, _ in SPECS]
for name in RAW:
    seqs['c_' + name[2:]] = f_partsum(seqs[name])
NAMES = list(seqs.keys())
print(f"\nsequences built: {len(NAMES)} ({len(RAW)} raw + {len(RAW)} cumulative)")

# ---- zero density and nondeg survival, reported BEFORE the verdict
print("\nDEGENERACY CENSUS (reported beside the verdict, per the recorded risk):")
alive = []
for nm in NAMES:
    v = seqs[nm]
    zf = sum(1 for x in v[:MIN_TERMS] if x == 0) / MIN_TERMS
    ok = nondeg(v)
    if ok:
        alive.append(nm)
    print(f"  {nm:14s} zero-frac(first20)={zf:4.2f}  distinct(first20)={len(set(v[:MIN_TERMS])):2d}  nondeg={ok}")
print(f"  -> sequences passing nondeg as SOURCE: {len(alive)} of {len(NAMES)}")

# ---- by-construction exclusions, enumerated in advance
EXCL = set()
for nm in RAW:
    EXCL.add(('partsum', nm, 'c_' + nm[2:]))
    EXCL.add(('diff', 'c_' + nm[2:], nm))
print(f"\nby-construction exclusions enumerated: {len(EXCL)}")

# ---- POSITIVE CONTROL: the 9 known-true partsum pairs must be detected
controls = []
for nm in RAW:
    tgt = 'c_' + nm[2:]
    img = f_partsum(seqs[nm])
    ov = overlap(img, seqs[tgt])
    controls.append((nm, tgt, ov, ov >= MIN_TERMS))
C = sum(1 for _, _, _, ok in controls if ok)
print("\nPOSITIVE CONTROL (partsum r_X -> c_X, true by definition):")
for a, b, ov, ok in controls:
    print(f"  {a:12s} -> {b:12s} overlap={ov:>5}  {'PASS' if ok else 'FAIL'}")
print(f"  controls firing: C = {C} of 9")

# ---- ATTAINABILITY, computed before the verdict (doctrine P138)
pairs = [(s, t) for s in alive for t in NAMES if s != t]
attainable = len(NONTRIVIAL) * len(pairs) - len([e for e in EXCL if e[0] in NONTRIVIAL and e[1] in alive])
print(f"\nATTAINABILITY: {len(alive)} eligible sources x {len(NAMES) - 1} targets x "
      f"{len(NONTRIVIAL)} non-trivial ops - exclusions = {attainable:,} admissible triples")
print(f"  headline gate is H >= 1; gate inside attainable range [0, {attainable:,}]? "
      f"{attainable >= 1}")

# ---- the sweep
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
for h in H_hits[:20]:
    print(f"    {h['operator']:18s} {h['source']:14s} -> {h['target']:14s} exact {h['exact_terms']} terms")
print(f"TRIVIAL-class exact relations (reported separately, never headline): {len(T_hits)}")
for h in T_hits[:10]:
    print(f"    {h['operator']:18s} {h['source']:14s} -> {h['target']:14s} exact {h['exact_terms']} terms")

# ---- branch enumeration, verified to partition
# NOTE (coding-error correction, pass 1): B1 as first written checked only the
# controls. The preregistration ALSO states that if too few sequences survive
# nondeg() for the headline to reach 1, the reading is VACUOUS rather than null.
# The attainability check found exactly that case (0 admissible triples) and the
# original branch code routed it to KILL — the very defect P138 doctrine was
# written about, committed one pass after writing the doctrine. Corrected here to
# match the preregistered semantics; the preregistration text is authoritative.
branches = {
    'B1_VACUOUS': (C < 9) or (attainable < 1),
    'B2_ADVANCE': C == 9 and attainable >= 1 and H >= 1,
    'B3_KILL':    C == 9 and attainable >= 1 and H == 0,
}
fired = [k for k, v in branches.items() if v]
print(f"\nBRANCH ENUMERATION: {branches}")
print(f"  exactly one branch fired? {len(fired) == 1}  -> {fired}")
assert len(fired) == 1, f"BRANCHES DO NOT PARTITION: {fired}"
VERDICT = {'B1_VACUOUS': 'VACUOUS', 'B2_ADVANCE': 'ADVANCE', 'B3_KILL': 'KILL'}[fired[0]]

out = {
    'cycle': '140-D',
    'question': ('does the exactly-verifiable OEIS operator vocabulary produce any NON-TRIVIAL '
                 'exact relation among LMFDB elliptic-curve counting sequences?'),
    'objects': 'elliptic curves over Q, LMFDB ec_curvedata, 3824372 rows',
    'index': f'conductor N = 1..{LIMIT}',
    'sequences': NAMES,
    'nondeg_survivors': alive,
    'degeneracy_census': {nm: {'zero_frac_first20': round(sum(1 for x in seqs[nm][:MIN_TERMS] if x == 0) / MIN_TERMS, 3),
                               'distinct_first20': len(set(seqs[nm][:MIN_TERMS])),
                               'nondeg': nondeg(seqs[nm])} for nm in NAMES},
    'exclusions_by_construction': sorted(list(EXCL)),
    'positive_controls': [{'source': a, 'target': b, 'overlap': ov, 'pass': ok} for a, b, ov, ok in controls],
    'controls_firing': C,
    'attainable_triples': attainable,
    'gate_inside_attainable_range': bool(attainable >= 1),
    'headline_nontrivial_hits': H_hits,
    'H': H,
    'trivial_class_hits': T_hits,
    'branches': branches,
    'branch_fired': fired[0],
    'vacuity_cause': ('0 of 18 sequences passed nondeg() as a source, because the first 20 terms of a '
                      'conductor-indexed sequence are dominated by zeros: the smallest conductor of an '
                      'elliptic curve over Q is 11, so terms 1-10 are structurally zero. The instrument '
                      'was aimed at an index window where the objects do not exist.'),
    'VERDICT': VERDICT,
    'what_dies_on_null': ('this operator family applied to LMFDB COUNTING SEQUENCES; NOT the verbs '
                          'thesis and NOT the 220 OEIS relations, which are separately verified'),
}
(ROOT / 'aporia/search/cycle_140d_results.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
print(f"\n*** CYCLE 140-D VERDICT: {VERDICT} ***")
