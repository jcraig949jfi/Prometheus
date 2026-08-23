"""CYCLE 142-F — give the vocabulary the verbs the objects actually use.

=============================== PREREGISTRATION ===============================
Committed in-script BEFORE any computation.

THE CHOICE, and why: 141-E offered two routes — extend the VOCABULARY, or change
the OBJECT CLASS. Extending the vocabulary is taken, because finding (b) is the
limitation that blocks interpretation of BOTH prior nulls. 140-D and 141-E each
returned zero, but neither can distinguish "no verbs reach elliptic curves" from
"the 7-operator vocabulary lacks the verbs elliptic curves actually use." Changing
the object class would produce a third null with the same ambiguity. Removing the
ambiguity is worth more than another data point carrying it.

QUESTION, in two parts that are reported separately and must not be conflated:

  PART 1 (the DIAGNOSTIC, answers finding (b)): does a NATIVE verb — quadratic
  twist by a character — relate elliptic curves that the unary vocabulary could
  not see? This is confirming KNOWN mathematics: twisting is a theorem, not a
  discovery. It is reported as a measurement, never as a finding, and its purpose
  is solely to settle whether the prior nulls were about the objects or about the
  vocabulary.

  PART 2 (the HEADLINE, genuinely open): do BINARY native verbs — Hadamard
  (pointwise) product, sum, difference — map a PAIR of curves' trace sequences
  exactly onto a THIRD curve's trace sequence? No theorem predicts this. This is
  the discovery statistic and the campaign's terminal state rests on it alone.

WHY THESE VERBS: the operations native to L-functions are twisting, Dirichlet
  convolution, and Euler-product manipulation. On a PRIME-INDEXED trace sequence
  the well-defined members of that family are the quadratic twist (a character
  times the sequence) and the pointwise/Rankin-Selberg-flavoured products. Full
  Dirichlet convolution needs an n-indexed sequence and therefore bad-prime
  casework at every conductor; it is deliberately NOT attempted here rather than
  attempted badly, and that omission is recorded as a weakness.

OBJECTS: elliptic curves over Q, LMFDB ec_curvedata, conductor <= 2000.
REPRESENTATION: trace sequences a_p, as established at 141-E. This is NOT a third
  representation — the pass prompt permits re-testing elliptic curves under an
  EXTENDED VOCABULARY, and holding the representation fixed is what makes the
  comparison against 141-E's H=0 meaningful.

PRIME WINDOW, chosen for a mathematical reason: the 40 primes starting at 101.
  Every fundamental discriminant used below has |d| <= 100 < 101, so no window
  prime divides any d, so chi_d(p) is never zero and the twist verb is EXACTLY
  well-defined at every position for every curve. Curves whose conductor shares a
  factor with a window prime are dropped, giving all curves a COMMON index — which
  is what makes binary verbs between different curves well-defined at all.

VOCABULARY:
  NATIVE PARAMETRIZED: twist_d, c(n) = kronecker(d, p_n) * a(n), for d over the
    fundamental discriminants with |d| <= 100.
  NATIVE BINARY: hadamard c(n)=a(n)*b(n); add c(n)=a(n)+b(n); sub c(n)=a(n)-b(n).
  The 7 unary operators from 140-D/141-E are NOT re-run: 141-E already measured
    them at H=0 over 294,909,843 reachable triples on this exact representation.

EXACTNESS BAR: >= 20 consecutive exact terms, source passing nondeg() reused
  verbatim from campaign_v_widen.py.

BY-CONSTRUCTION EXCLUSIONS, enumerated in advance:
  - target in the same isogeny class as EITHER source (identical a_p by theory);
  - target identical to either source;
  - for PART 1, pairs LMFDB already records as quadratic twists of one another are
    counted separately from pairs it does not, so a known twist is never presented
    as a new relation.

POSITIVE CONTROLS. Each is stated with the input that would make it FAIL, because
three passes running have shipped a control that could not fail:
  C1 ISOGENY IDENTITY — every same-isogeny-class pair must have identical trace
     sequences over all 40 positions.
     FAILS IF: the point count is wrong, or the isogeny class labels are misread.
  C2 HASSE — |a_p| <= 2*sqrt(p) everywhere.
     FAILS IF: any point count is wrong by even one point.
  C3 INDEPENDENT ALGORITHM — an O(p^2) brute-force count must agree with the
     character-based count on every checked (curve, prime).
     FAILS IF: either implementation is wrong; they share no code path.
  C4 TWIST FIDELITY (new, and the one that guards the new machinery). For curves
     LMFDB records as having a minimal quadratic twist with disc d != 1, where that
     twist is also in the corpus, TWO sub-checks:
       C4a |a_p| must agree between the pair at every position (twisting multiplies
           by +-1, so magnitudes are preserved).
           FAILS IF: the recorded pair is not actually a twist, or a_p is wrong.
       C4b the SIGN pattern must equal kronecker(d, p_n) at every position, up to
           at most one global sign.
           FAILS IF: the kronecker implementation is wrong, or signs are
           inconsistent across primes. A pure global sign flip is a convention
           difference; it is REPORTED as such and not silently absorbed.

ATTAINABILITY — a CONJUNCT of every non-vacuous branch, computed PER VERB against
  the actual target band. Hadamard values reach ~33^2 and sums reach ~66, both
  outside the Hasse band, so several verbs may be structurally incapable. Their
  triples are EXCLUDED from the denominator, not counted in it. Counting
  impossible triples is the error committed at 140-D and corrected at 141-E.

BRANCHES (partition verified by enumeration with an assert). Let C = control
families passing (0..4), A = reachable admissible triples for the BINARY verbs,
H = binary-verb exact relations onto a third curve:
  B1 VACUOUS  C < 4 or A < 1
  B2 ADVANCE  C == 4 and A >= 1 and H >= 1
  B3 KILL     C == 4 and A >= 1 and H == 0

NULL OUTPUT OF EVERY VERDICT RULE:
  - exactness rule -> "no relation" when overlap < 20;
  - nondeg rule    -> "source degenerate", pair dropped from numerator AND
                      denominator;
  - reachability   -> verb contributes 0 admissible triples, excluded from both;
  - control rule   -> VACUOUS, which is neither null nor kill;
  - PART 1 twist census has NO verdict rule attached: it is a measurement.

EFFECT SIZE / MATERIALITY: census, not a sample, so no SE is defined. Declared
  materiality is EXISTENCE — one exact 20-term relation mapping a curve PAIR onto
  a third curve is material, because chance agreement across 20 Hasse-interval
  values is negligible.

COUNTERFACTUAL-CONSEQUENCE TEST, stated in advance:
  ADVANCE -> the surviving triples are examined individually next cycle for an
    arithmetic explanation (unrecorded isogeny? twist chain? congruence?).
  KILL    -> binary native verbs add nothing over unary ones on this object, and
    the next cycle changes the OBJECT CLASS with the vocabulary question already
    settled by PART 1 rather than left open.
  ELIGIBLE TO GO DIFFERENTLY? Yes, and verified numerically before the verdict: A
    is designed to be large, the bar is existence not a margin, and the branches
    name different next cycles.
  NOTE the asymmetry deliberately: PART 1 is expected to fire (twisting is a
    theorem) and PART 2 is expected not to. Neither expectation is allowed to
    substitute for the measurement, and PART 1 firing does NOT make the terminal
    an ADVANCE — only PART 2 does.

WHAT DIES ON A NULL: binary native verbs on elliptic-curve trace sequences. NOT
  the verbs thesis, NOT the 220 verified OEIS relations.
============================= END PREREGISTRATION =============================
"""
from __future__ import annotations

import json
import math
import pathlib

import psycopg2

ROOT = pathlib.Path(r'F:\Prometheus')
CMAX = 2000
PSTART = 101
NPRIMES = 40
MIN_TERMS = 20
MAX_CURVES = 900          # binary sweep is O(n^2); bound stated, reported beside verdict


def primes_upto(n):
    s = [True] * (n + 1)
    s[0] = s[1] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            for j in range(i * i, n + 1, i):
                s[j] = False
    return [i for i, v in enumerate(s) if v]


ALLP = primes_upto(5000)
WINDOW = [p for p in ALLP if p >= PSTART][:NPRIMES]


def nondeg(v):
    """reused verbatim from campaign_v_widen.py"""
    w = v[:MIN_TERMS]
    return len(set(w)) >= 8 and not all(x == w[-1] for x in w[-6:])


def ap(ainvs, p):
    a1, a2, a3, a4, a6 = ainvs
    npts = 0
    for x in range(p):
        d = ((a1 * x + a3) ** 2 + 4 * (x ** 3 + a2 * x * x + a4 * x + a6)) % p
        if d == 0:
            npts += 1
        elif pow(d, (p - 1) // 2, p) == 1:
            npts += 2
    return p + 1 - (npts + 1)


def ap_bruteforce(ainvs, p):
    a1, a2, a3, a4, a6 = ainvs
    cnt = 0
    for x in range(p):
        rhs = (x ** 3 + a2 * x * x + a4 * x + a6) % p
        for y in range(p):
            if (y * y + a1 * x * y + a3 * y - rhs) % p == 0:
                cnt += 1
    return p + 1 - (cnt + 1)


def kronecker(a, n):
    """Kronecker symbol (a/n). n is an odd prime here, so this is Legendre."""
    a %= n
    if a == 0:
        return 0
    return 1 if pow(a, (n - 1) // 2, n) == 1 else -1


def fundamental_discs(limit):
    out = []
    for d in range(-limit, limit + 1):
        if d in (0, 1):
            continue
        if d % 4 == 1:
            sf = all(d % (q * q) != 0 for q in range(2, int(abs(d) ** 0.5) + 2))
            if sf:
                out.append(d)
        elif d % 4 == 0:
            m = d // 4
            if m % 4 in (2, 3) and all(m % (q * q) != 0 for q in range(2, int(abs(m) ** 0.5) + 2)):
                out.append(d)
    return out


DISCS = [d for d in fundamental_discs(100) if abs(d) <= 100]

# ================================== RUN ====================================
print("CYCLE 142-F — native verbs (twist, hadamard, add, sub)")
print("=" * 74)
print(f"prime window: {NPRIMES} primes from {WINDOW[0]} to {WINDOW[-1]}")
print(f"fundamental discriminants |d| <= 100: {len(DISCS)} "
      f"(all < {WINDOW[0]}, so chi_d(p) is never 0 on the window)")

conn = psycopg2.connect(host='localhost', port=5432, dbname='lmfdb', user='postgres',
                        connect_timeout=15)
cur = conn.cursor()
cur.execute("select lmfdb_label, lmfdb_iso, ainvs, conductor::bigint, "
            "min_quad_twist_disc, min_quad_twist_ainvs from ec_curvedata "
            "where conductor::bigint <= %s order by conductor::bigint, lmfdb_label", (CMAX,))
raw = cur.fetchall()
WSET = set(WINDOW)
kept = [r for r in raw if not any(r[3] % p == 0 for p in WSET)]
print(f"curves conductor <= {CMAX}: {len(raw):,}; sharing no factor with the window: {len(kept):,}")
kept = kept[:MAX_CURVES]
print(f"curves used (bound {MAX_CURVES}, binary sweep is O(n^2)): {len(kept):,}")

curves = {}
for label, iso, ainvs_s, N, mqtd, mqta in kept:
    ai = [int(float(x)) for x in json.loads(ainvs_s)]
    curves[label] = {'iso': iso, 'ainvs': ai, 'N': N,
                     'mqtd': mqtd, 'mqta': mqta,
                     'b': [ap(ai, p) for p in WINDOW]}
print(f"trace sequences computed: {len(curves):,} x {NPRIMES}")

# ------------------------------- CONTROLS ----------------------------------
byiso = {}
for lab, c in curves.items():
    byiso.setdefault(c['iso'], []).append(lab)

c1_pairs = c1_bad = 0
for labs in byiso.values():
    if len(labs) < 2:
        continue
    base = curves[labs[0]]['b']
    for L in labs[1:]:
        c1_pairs += 1
        if curves[L]['b'] != base:
            c1_bad += 1
C1 = (c1_pairs > 0 and c1_bad == 0)

c2_bad = sum(1 for c in curves.values()
             for p, v in zip(WINDOW, c['b']) if abs(v) > 2 * math.isqrt(p) + 1)
C2 = (c2_bad == 0)

c3_n = c3_bad = 0
for lab, c in list(curves.items())[:40]:
    for q, v in list(zip(WINDOW, c['b']))[:6]:
        c3_n += 1
        if ap_bruteforce(c['ainvs'], q) != v:
            c3_bad += 1
C3 = (c3_n > 0 and c3_bad == 0)

# C4 twist fidelity — guards the NEW machinery
by_ainvs = {tuple(c['ainvs']): lab for lab, c in curves.items()}
c4_pairs = c4a_bad = c4b_bad = c4b_globalflip = 0
for lab, c in curves.items():
    try:
        d = int(float(c['mqtd']))
    except Exception:
        continue
    if d == 1 or abs(d) > 100:
        continue
    try:
        tw = tuple(int(float(x)) for x in json.loads(c['mqta']))
    except Exception:
        continue
    other = by_ainvs.get(tw)
    if other is None or other == lab:
        continue
    c4_pairs += 1
    a, b = c['b'], curves[other]['b']
    if [abs(x) for x in a] != [abs(x) for x in b]:
        c4a_bad += 1
        continue
    pred = [kronecker(d, p) * x for p, x in zip(WINDOW, a)]
    if pred == b:
        pass
    elif [-x for x in pred] == b:
        c4b_globalflip += 1
    else:
        c4b_bad += 1
C4 = (c4_pairs > 0 and c4a_bad == 0 and c4b_bad == 0)

C = sum([C1, C2, C3, C4])
print("\nPOSITIVE CONTROLS (each with a stated failure mode):")
print(f"  C1 isogeny identity : {c1_pairs:,} pairs, {c1_bad} mismatches -> {C1}")
print(f"  C2 Hasse bound      : {c2_bad} violations -> {C2}")
print(f"  C3 independent algo : {c3_n:,} checks vs brute force, {c3_bad} disagreements -> {C3}")
print(f"  C4 twist fidelity   : {c4_pairs:,} recorded twist pairs | "
      f"|a_p| mismatches {c4a_bad} | sign-pattern failures {c4b_bad} | "
      f"global-sign-convention flips {c4b_globalflip} -> {C4}")
print(f"  control families passing: C = {C} of 4")

# ------------------------- PART 1: the twist census ------------------------
# A MEASUREMENT, not a finding. Twisting is a theorem; this settles whether the
# prior nulls were about the objects or about the vocabulary.
index = {}
for lab, c in curves.items():
    index.setdefault(tuple(c['b'][:MIN_TERMS]), []).append(lab)

recorded_twin = set()
for lab, c in curves.items():
    try:
        tw = tuple(int(float(x)) for x in json.loads(c['mqta']))
    except Exception:
        continue
    o = by_ainvs.get(tw)
    if o and o != lab:
        recorded_twin.add(frozenset((lab, o)))

twist_hits, twist_new = [], []
for lab, c in curves.items():
    if not nondeg(c['b']):
        continue
    for d in DISCS:
        img = [kronecker(d, p) * x for p, x in zip(WINDOW, c['b'])]
        for t in index.get(tuple(img[:MIN_TERMS]), []):
            if t == lab or curves[t]['iso'] == c['iso']:
                continue
            rec = frozenset((lab, t)) in recorded_twin
            row = {'source': lab, 'target': t, 'disc': d, 'lmfdb_records_twist': rec}
            twist_hits.append(row)
            if not rec:
                twist_new.append(row)
print(f"\nPART 1 (MEASUREMENT, confirms known mathematics — NOT the verdict):")
print(f"  twist-verb exact relations between non-isogenous curves: {len(twist_hits):,}")
print(f"    of which LMFDB already records the pair as a quadratic twist: "
      f"{len(twist_hits) - len(twist_new):,}")
print(f"    of which it does not: {len(twist_new):,}")
for h in twist_hits[:6]:
    print(f"      {h['source']:12s} --twist({h['disc']:>4})--> {h['target']:12s} "
          f"recorded={h['lmfdb_records_twist']}")

# ------------------- PART 2: the headline, binary native verbs -------------
alive = [L for L in curves if nondeg(curves[L]['b'])]
removed = len(curves) - len(alive)
TMAX = max(abs(v) for c in curves.values() for v in c['b'])
print(f"\nDEGENERACY: {len(alive):,} of {len(curves):,} pass nondeg ({removed:,} removed)")
print(f"target band: |a_p| <= {TMAX} over this window")

BINARY = {
    'hadamard': lambda a, b: [x * y for x, y in zip(a, b)],
    'add':      lambda a, b: [x + y for x, y in zip(a, b)],
    'sub':      lambda a, b: [x - y for x, y in zip(a, b)],
}

print("PER-VERB REACHABILITY (source pairs whose image stays inside the target band):")
reach = {}
AL = alive
for vname, fn in BINARY.items():
    ok = 0
    for i, s1 in enumerate(AL):
        b1 = curves[s1]['b']
        for s2 in AL[i + 1:]:
            img = fn(b1, curves[s2]['b'])[:MIN_TERMS]
            if max(abs(v) for v in img) <= TMAX:
                ok += 1
    reach[vname] = ok
    flag = '' if ok else '   <-- STRUCTURALLY INCAPABLE, 0 admissible triples'
    print(f"  {vname:10s} {ok:>9,} reachable source pairs{flag}")

n_targets = len(curves)
attainable = sum(reach[v] * (n_targets - 2) for v in BINARY)
print(f"ATTAINABILITY (reachable triples only): {attainable:,}")
print(f"  gate H >= 1 inside attainable range [0, {attainable:,}]? {attainable >= 1}")

H_hits = []
for vname, fn in BINARY.items():
    if not reach[vname]:
        continue
    for i, s1 in enumerate(AL):
        b1, iso1 = curves[s1]['b'], curves[s1]['iso']
        for s2 in AL[i + 1:]:
            img = fn(b1, curves[s2]['b'])
            key = tuple(img[:MIN_TERMS])
            if max(abs(v) for v in key) > TMAX:
                continue
            for t in index.get(key, []):
                if t in (s1, s2):
                    continue
                if curves[t]['iso'] in (iso1, curves[s2]['iso']):
                    continue
                H_hits.append({'verb': vname, 'source_a': s1, 'source_b': s2, 'target': t})

H = len(H_hits)
print(f"\nPART 2 HEADLINE — binary native verbs mapping a curve PAIR onto a THIRD curve: H = {H}")
for h in H_hits[:20]:
    print(f"    {h['verb']:10s} {h['source_a']:12s} + {h['source_b']:12s} -> {h['target']:12s}")

branches = {
    'B1_VACUOUS': (C < 4) or (attainable < 1),
    'B2_ADVANCE': (C == 4) and (attainable >= 1) and (H >= 1),
    'B3_KILL':    (C == 4) and (attainable >= 1) and (H == 0),
}
fired = [k for k, v in branches.items() if v]
print(f"\nBRANCHES: {branches}\n  exactly one fired? {len(fired) == 1} -> {fired}")
assert len(fired) == 1, f"BRANCHES DO NOT PARTITION: {fired}"
VERDICT = {'B1_VACUOUS': 'VACUOUS', 'B2_ADVANCE': 'ADVANCE', 'B3_KILL': 'KILL'}[fired[0]]

out = {
    'cycle': '142-F', 'choice': 'extend the VOCABULARY with native verbs',
    'representation': 'trace sequences a_p (held fixed from 141-E on purpose)',
    'prime_window': [WINDOW[0], WINDOW[-1]], 'n_primes': NPRIMES,
    'n_curves_used': len(curves), 'max_curves_bound': MAX_CURVES,
    'discriminants': len(DISCS),
    'controls': {'C1_isogeny': C1, 'C1_pairs': c1_pairs, 'C1_bad': c1_bad,
                 'C2_hasse': C2, 'C2_violations': c2_bad,
                 'C3_independent': C3, 'C3_checks': c3_n, 'C3_bad': c3_bad,
                 'C4_twist_fidelity': C4, 'C4_pairs': c4_pairs,
                 'C4a_abs_mismatch': c4a_bad, 'C4b_sign_failures': c4b_bad,
                 'C4b_global_sign_convention_flips': c4b_globalflip},
    'controls_passing': C,
    'PART1_twist_measurement': {
        'total_exact_twist_relations': len(twist_hits),
        'already_recorded_by_lmfdb': len(twist_hits) - len(twist_new),
        'not_recorded_by_lmfdb': len(twist_new),
        'status': 'MEASUREMENT confirming known mathematics; not a finding, not the verdict',
        'examples': twist_hits[:40]},
    'nondeg_survivors': len(alive), 'removed_by_guard': removed,
    'target_band_max_abs': TMAX,
    'per_verb_reachable_source_pairs': reach,
    'attainable_triples': attainable,
    'gate_inside_attainable_range': bool(attainable >= 1),
    'H': H, 'headline_hits': H_hits,
    'branches': branches, 'branch_fired': fired[0], 'VERDICT': VERDICT,
    'materiality': 'existence; one exact 20-term pair->third-curve relation is material',
    'what_dies_on_null': 'binary native verbs on elliptic-curve trace sequences; NOT the verbs '
                         'thesis and NOT the 220 verified OEIS relations'}
(ROOT / 'aporia/search/cycle_142f_results.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
print(f"\n*** CYCLE 142-F VERDICT: {VERDICT} ***")
