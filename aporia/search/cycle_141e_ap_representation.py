"""CYCLE 141-E — does the verbs thesis survive a change of REPRESENTATION?

=============================== PREREGISTRATION ===============================
Committed in-script BEFORE any computation. Nothing below the RUN banner changes
anything above it.

QUESTION (binary, about mathematical objects):
  CYCLE 140-D killed the operator vocabulary on elliptic-curve COUNTING sequences
  (H=0 over 590 triples, instrument verified). Its preregistered consequence was
  that any next attempt must change the REPRESENTATION rather than extend the
  operator family. So: does the exactly-verifiable operator vocabulary produce ANY
  non-trivial exact relation between the FROBENIUS TRACE sequences of two
  non-isogenous elliptic curves over Q?

WHY a_p IS THE NATURAL NEXT REPRESENTATION:
  A counting sequence is a fact about the CATALOGUE — how many curves happen to sit
  at each conductor. The trace sequence a_p = p + 1 - #E(F_p) is a fact about the
  OBJECT: it is the arithmetic content of the curve, determines its L-function, and
  is the sequence that actually carries the curve's identity (isogenous curves have
  identical a_p; Faltings/Tate say the a_p determine the isogeny class). If the
  verbs vocabulary reaches elliptic curves at all, this is where it must show.
  It is also exact-integer valued, which a floating-point Euler factor is not.

WHY NOT lfunc_lfunctions: checked first. For degree-2 motivic-weight-1 rows the
  dirichlet_coefficients column is NULL and euler_factors are stored as analytic
  (floating-point) normalizations. An exactness bar over 20 terms cannot be run on
  floats, so the coefficients are recomputed exactly from ainvs instead.

BUILD-VERSUS-RESEARCH, disclosed as a judgment call: a_p is computed here by
  counting points over F_p via the quadratic character. That is ~15 lines of exact
  arithmetic implementing the definition of the object, not an instrument build and
  not a modification of anything owned by another agent. The operator definitions
  and the nondeg guard are REUSED VERBATIM from campaign_v_widen.py. The judgment
  call is disclosed rather than hidden, and it is guarded by four positive controls
  below, any one of which would expose an incorrect point count.

OBJECTS: elliptic curves over Q, LMFDB ec_curvedata, conductor <= 2000.
REPRESENTATION: for each curve E, b_E(n) = a_{p_n}(E) where p_n is the n-th prime
  NOT dividing the conductor. Restricting to good primes avoids bad-reduction
  casework entirely and keeps every term exact.
WINDOW: 40 good primes per curve.

OPERATORS, split by the P133 trivial-class distinction (unchanged from 140-D):
  NON-TRIVIAL (7, headline): diff, partsum, binomial, moebius, inverse_binomial,
                             second_diff, stirling2
  TRIVIAL (5, reported separately, never headline): shift, runmax, aerate,
                             bisect_even, bisect_odd

EXACTNESS BAR: >= 20 consecutive exact terms, source passing nondeg() reused
  verbatim (>= 8 distinct values in the window, not constant over its last 6).

BY-CONSTRUCTION EXCLUSION: pairs of curves in the SAME isogeny class. Isogenous
  curves have identical a_p by construction, so any apparent relation between them
  is a restatement of that fact and is not a finding. Enumerated and excluded.

POSITIVE CONTROLS (4 families). ALL must fire or NO null may be read:
  C1 ISOGENY:      every pair of curves in the same isogeny class must have
                   IDENTICAL trace sequences over the full 40-term window.
  C2 HASSE:        |a_p| <= 2*sqrt(p) for every curve and every good prime. A
                   violated Hasse bound means the point count is wrong.
  C3 KNOWN VALUES: curve 11.a must give a_2=-2, a_3=-1, a_5=1, a_7=-2 (the
                   coefficients of the weight-2 level-11 newform).
  C4 INDEPENDENT ALGORITHM: an O(p^2) brute-force point count, a different
                   algorithm from the character-based one, must agree on every checked
                   (curve, prime). Two independent methods disagreeing means one is wrong.

ATTAINABILITY — a TERM IN THE BRANCH, not a printout beside it. 140-D's pass 1
  computed attainability, printed it, and still routed a forced zero to KILL
  because B1 tested only the controls. That was the second reachability defect
  caught at adjudication in two passes. Here `attainable >= 1` is a conjunct of
  every non-vacuous branch, written into the branch dict itself.

BRANCHES (partition verified by enumeration with an assert at run time). Let
C = number of control families passing (0..4), A = admissible triples, H = headline
non-trivial exact count:
  B1 VACUOUS  C < 4 or A < 1
  B2 ADVANCE  C == 4 and A >= 1 and H >= 1
  B3 KILL     C == 4 and A >= 1 and H == 0

NULL OUTPUT OF EVERY VERDICT RULE:
  - exactness rule -> "no relation" when overlap < 20;
  - nondeg rule    -> "source degenerate", pair removed from BOTH numerator and
                      the attainable denominator;
  - control rule   -> VACUOUS, which is neither a null nor a kill;
  - isogeny exclusion -> pair silently removed, counted in the exclusion tally.

EFFECT SIZE AND MATERIALITY: this is a census over all admissible triples, not a
  sample, so no SE is defined. The declared materiality threshold is ONE: a single
  exact 20-term operator relation between non-isogenous curves would be a genuine
  discovery, because the probability of 20 consecutive exact agreements between
  unrelated integer sequences with |a_p| ranging over the Hasse interval is
  negligible (the interval at p=173 alone has 53 values). There is no "small
  effect" regime here — the statistic is existence.

COUNTERFACTUAL-CONSEQUENCE TEST, stated in advance:
  ADVANCE -> the surviving triples are examined individually and the next cycle
    attempts to explain the relation arithmetically (twist? isogeny not recorded?
    congruence?). That is a different pass with a different question.
  KILL    -> two independent representations of the SAME objects (counting
    sequences at 140-D, trace sequences here) have both returned zero. The scoped
    conclusion becomes that this operator vocabulary does not reach elliptic curves,
    and the next cycle must change the OBJECT CLASS or abandon the vocabulary —
    not try a third representation of elliptic curves.
  ELIGIBLE TO GO DIFFERENTLY? Yes. A is designed to be large (thousands of triples,
    against 590 at 140-D), the bar is existence rather than a margin, and the two
    branches name different next cycles. Verified numerically before the verdict.

WHAT DIES ON A NULL: this operator family on elliptic-curve trace sequences. NOT
  the verbs thesis, NOT the 220 verified OEIS relations.

RECORDED RISK, before the result: a_p sequences are Sato-Tate distributed and
  "random-like", so a null is the expected outcome and would be weakly informative
  on its own. What makes it worth running is that it is the SECOND representation
  of the same objects — the pair of nulls is the finding, not either one alone.
  Recorded here so the write-up cannot later inflate a single expected null.
============================= END PREREGISTRATION =============================
"""
from __future__ import annotations

import json
import math
import pathlib

import psycopg2

ROOT = pathlib.Path(r'F:\Prometheus')
CMAX = 2000
NPRIMES = 40
MIN_TERMS = 20

# ---------------- operators, reused verbatim from campaign_v_widen.py -------
COMB = [[math.comb(n, k) for k in range(n + 1)] for n in range(30)]
S2T = [[0] * 30 for _ in range(30)]
S2T[0][0] = 1
for _n in range(1, 30):
    for _k in range(1, _n + 1):
        S2T[_n][_k] = _k * S2T[_n - 1][_k] + S2T[_n - 1][_k - 1]
NMU = 64
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


# ---------------- exact a_p by point counting over F_p ----------------------
def primes_upto(n):
    s = [True] * (n + 1)
    s[0] = s[1] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            for j in range(i * i, n + 1, i):
                s[j] = False
    return [i for i, v in enumerate(s) if v]


PRIMES = primes_upto(4000)


def ap(ainvs, p):
    """a_p = p + 1 - #E(F_p), exact. Quadratic-character count for odd p."""
    a1, a2, a3, a4, a6 = ainvs
    if p == 2:
        cnt = 0
        for x in range(2):
            for y in range(2):
                if (y * y + a1 * x * y + a3 * y - (x ** 3 + a2 * x * x + a4 * x + a6)) % 2 == 0:
                    cnt += 1
        return 2 + 1 - (cnt + 1)
    npts = 0
    for x in range(p):
        # (2y + a1 x + a3)^2 = (a1 x + a3)^2 + 4(x^3 + a2 x^2 + a4 x + a6) =: D
        d = ((a1 * x + a3) ** 2 + 4 * (x ** 3 + a2 * x * x + a4 * x + a6)) % p
        if d == 0:
            npts += 1                       # exactly one y
        elif pow(d, (p - 1) // 2, p) == 1:
            npts += 2                       # D a non-zero square: two y
        # else D a non-residue: no y
    return p + 1 - (npts + 1)               # +1 for the point at infinity


def ap_bruteforce(ainvs, p):
    """Independent O(p^2) counter. Used ONLY as a control against ap()."""
    a1, a2, a3, a4, a6 = ainvs
    cnt = 0
    for x in range(p):
        rhs = (x ** 3 + a2 * x * x + a4 * x + a6) % p
        for y in range(p):
            if (y * y + a1 * x * y + a3 * y - rhs) % p == 0:
                cnt += 1
    return p + 1 - (cnt + 1)


# ================================== RUN ====================================
print("CYCLE 141-E — trace sequences a_p as the representation")
print("=" * 74)
conn = psycopg2.connect(host='localhost', port=5432, dbname='lmfdb', user='postgres',
                        connect_timeout=15)
cur = conn.cursor()
cur.execute("select lmfdb_label, lmfdb_iso, ainvs, conductor::bigint from ec_curvedata "
            "where conductor::bigint <= %s order by conductor::bigint, lmfdb_label", (CMAX,))
rows = cur.fetchall()
print(f"curves with conductor <= {CMAX}: {len(rows):,}")

curves = {}
for label, iso, ainvs_s, N in rows:
    ai = [int(float(x)) for x in json.loads(ainvs_s)]
    good = [p for p in PRIMES if N % p != 0][:NPRIMES]
    curves[label] = {'iso': iso, 'ainvs': ai, 'N': N, 'primes': good,
                     'b': [ap(ai, p) for p in good]}
print(f"trace sequences computed: {len(curves):,} curves x {NPRIMES} good primes")

# ---------------------------- POSITIVE CONTROLS ----------------------------
byiso = {}
for lab, c in curves.items():
    byiso.setdefault(c['iso'], []).append(lab)

c1_pairs = c1_bad = 0
for iso, labs in byiso.items():
    if len(labs) < 2:
        continue
    base = curves[labs[0]]['b']
    for L in labs[1:]:
        c1_pairs += 1
        if curves[L]['b'] != base:
            c1_bad += 1
C1 = (c1_pairs > 0 and c1_bad == 0)

c2_bad = 0
for lab, c in curves.items():
    for p, v in zip(c['primes'], c['b']):
        if abs(v) > 2 * math.isqrt(p) + 1:
            c2_bad += 1
C2 = (c2_bad == 0)

want = {2: -2, 3: -1, 5: 1, 7: -2}
c3lab = next((L for L in curves if L.startswith('11.a')), None)
C3 = False
if c3lab:
    got = dict(zip(curves[c3lab]['primes'], curves[c3lab]['b']))
    C3 = all(got.get(p) == v for p, v in want.items())

# C4 as first drafted compared pr[2]*pr[3] against ap(ainvs,2)*ap(ainvs,3) — the SAME
# quantity, so it could not fail. That is precisely the unfalsifiable-safeguard failure
# the external reviews flagged. Replaced with a genuinely independent check: an O(p^2)
# brute-force point count, a different algorithm, must agree with the character-based
# one on every curve for every good prime below 60.
c4_bad = c4_n = 0
for lab, c in list(curves.items())[:120]:
    for q, v in zip(c['primes'], c['b']):
        if q >= 60:
            break
        c4_n += 1
        if ap_bruteforce(c['ainvs'], q) != v:
            c4_bad += 1
C4 = (c4_n > 0 and c4_bad == 0)

C = sum([C1, C2, C3, C4])
print("\nPOSITIVE CONTROLS:")
print(f"  C1 isogeny-identity : {c1_pairs:,} same-class pairs, {c1_bad} mismatches -> {C1}")
print(f"  C2 Hasse bound      : {c2_bad} violations -> {C2}")
print(f"  C3 known 11.a values: {c3lab} gives "
      f"{[curves[c3lab]['b'][:4]] if c3lab else None} -> {C3}")
print(f"  C4 independent count: {c4_n:,} (curve,prime) checks vs brute force, {c4_bad} mismatches -> {C4}")
print(f"  control families passing: C = {C} of 4")

# ------------------------- degeneracy + attainability ----------------------
alive = [L for L, c in curves.items() if nondeg(c['b'])]
removed = len(curves) - len(alive)
print(f"\nDEGENERACY: {len(alive):,} of {len(curves):,} trace sequences pass nondeg "
      f"as SOURCE ({removed:,} removed by the guard)")

same_iso_pairs = sum(len(v) * (len(v) - 1) for v in byiso.values())
n_alive, n_all = len(alive), len(curves)

# PER-OPERATOR REACHABILITY. Every target is a trace sequence, so every target value
# obeys |a_p| <= 2*sqrt(p) — bounded by TMAX below. An operator whose image escapes
# that band cannot match ANY target, at any threshold, for structural reasons. Those
# triples are NOT admissible and must not inflate the denominator: counting them
# would repeat 140-D's error of reporting a gate as reachable when it is not.
TMAX = max(abs(v) for c in curves.values() for v in c['b'])
print("")
print(f"target band: every target value obeys |a_p| <= {TMAX} (Hasse over the window)")
print("PER-OPERATOR REACHABILITY (sources whose image stays inside the target band):")
reach_src = {}
for opname, fn in NONTRIVIAL.items():
    ok = 0
    for s in alive:
        try:
            img = fn(curves[s]['b'])
        except Exception:
            continue
        if len(img) >= MIN_TERMS and max(abs(v) for v in img[:MIN_TERMS]) <= TMAX:
            ok += 1
    reach_src[opname] = ok
    flag = '' if ok else '   <-- STRUCTURALLY INCAPABLE, contributes 0 admissible triples'
    print(f"  {opname:18s} {ok:>6,} of {n_alive:,} sources reachable{flag}")

# admissible = reachable sources x eligible targets, minus same-isogeny pairs, per operator
n_ops_live = sum(1 for o in NONTRIVIAL if reach_src[o])
attainable = max(sum(reach_src[o] * (n_all - 1) for o in NONTRIVIAL)
                 - same_iso_pairs * n_ops_live, 0)
print(f"ATTAINABILITY (reachable triples only): {attainable:,}")
print(f"  gate H >= 1 inside attainable range [0, {attainable:,}]? {attainable >= 1}")

# --------------------------------- sweep -----------------------------------
LAB = list(curves.keys())
IDX = {L: i for i, L in enumerate(LAB)}


def sweep(opset):
    hits = []
    tgt = [(L, curves[L]['b']) for L in LAB]
    for opname, fn in opset.items():
        for s in alive:
            try:
                img = fn(curves[s]['b'])
            except Exception:
                continue
            if len(img) < MIN_TERMS:
                continue
            head = tuple(img[:MIN_TERMS])
            siso = curves[s]['iso']
            for t, bt in tgt:
                if t == s or curves[t]['iso'] == siso:
                    continue
                if tuple(bt[:MIN_TERMS]) != head:
                    continue
                ov = overlap(img, bt)
                if ov >= MIN_TERMS:
                    hits.append({'operator': opname, 'source': s, 'target': t,
                                 'exact_terms': ov})
    return hits


H_hits = sweep(NONTRIVIAL)
T_hits = sweep(TRIVIAL)
H = len(H_hits)
print(f"\nNON-TRIVIAL exact relations (headline): H = {H}")
for h in H_hits[:25]:
    print(f"    {h['operator']:18s} {h['source']:12s} -> {h['target']:12s} exact {h['exact_terms']}")
print(f"TRIVIAL-class hits (never headline): {len(T_hits)}")
for h in T_hits[:12]:
    print(f"    {h['operator']:18s} {h['source']:12s} -> {h['target']:12s} exact {h['exact_terms']}")

# --------------------------- branches: attainability IS a term -------------
branches = {
    'B1_VACUOUS': (C < 4) or (attainable < 1),
    'B2_ADVANCE': (C == 4) and (attainable >= 1) and (H >= 1),
    'B3_KILL':    (C == 4) and (attainable >= 1) and (H == 0),
}
fired = [k for k, v in branches.items() if v]
print(f"\nBRANCHES: {branches}\n  exactly one fired? {len(fired) == 1} -> {fired}")
assert len(fired) == 1, f"BRANCHES DO NOT PARTITION: {fired}"
VERDICT = {'B1_VACUOUS': 'VACUOUS', 'B2_ADVANCE': 'ADVANCE', 'B3_KILL': 'KILL'}[fired[0]]

out = {'cycle': '141-E', 'representation': 'Frobenius trace sequence a_p at good primes',
       'objects': f'elliptic curves over Q, conductor <= {CMAX}',
       'n_curves': len(curves), 'n_primes': NPRIMES,
       'controls': {'C1_isogeny_identity': C1, 'C1_pairs': c1_pairs, 'C1_mismatches': c1_bad,
                    'C2_hasse': C2, 'C2_violations': c2_bad,
                    'C3_known_11a': C3, 'C3_label': c3lab,
                    'C4_independent_bruteforce': C4, 'C4_checked': c4_n, 'C4_mismatches': c4_bad},
       'controls_passing': C,
       'nondeg_survivors': len(alive), 'removed_by_guard': removed,
       'same_isogeny_pairs_excluded': same_iso_pairs,
       'attainable_triples': attainable,
       'target_band_max_abs': None,
       'per_operator_reachable_sources': None,
       'gate_inside_attainable_range': bool(attainable >= 1),
       'H': H, 'headline_hits': H_hits, 'trivial_class_hits': T_hits,
       'branches': branches, 'branch_fired': fired[0], 'VERDICT': VERDICT,
       'materiality': 'existence; one exact 20-term relation between non-isogenous curves is material',
       'what_dies_on_null': 'this operator family on elliptic-curve trace sequences; NOT the verbs '
                            'thesis and NOT the 220 verified OEIS relations'}
(ROOT / 'aporia/search/cycle_141e_results.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
print(f"\n*** CYCLE 141-E VERDICT: {VERDICT} ***")
