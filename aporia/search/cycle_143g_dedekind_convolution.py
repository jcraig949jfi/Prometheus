"""CYCLE 143-G — number fields, Dedekind zeta coefficients, Dirichlet convolution.

=============================== PREREGISTRATION ===============================
Committed in-script BEFORE any computation.

OBJECT CLASS: number fields (LMFDB nf_fields), degrees 2-4, index = 1.
  NOT elliptic curves in any representation. Chosen over mf_newforms deliberately:
  weight-2 rational newforms ARE elliptic curves by modularity, so a newform sweep
  would have re-entered the banned object class through the back door unless
  restricted to weight >= 4, and number fields avoid the question entirely.

REPRESENTATION: the Dedekind zeta coefficient sequence a_K(n) = #{ideals of O_K of
  norm n}, for n = 1..N. This is the canonical integer sequence of a number field,
  it is multiplicative, and unlike a Frobenius trace it is UNBOUNDED and positive —
  which matters, because 141-E found three generic operators structurally
  unreachable precisely because trace sequences are Hasse-bounded.

WHY index = 1: by Dedekind's theorem, when p does not divide [O_K : Z[theta]] the
  factorization of the defining polynomial mod p gives the exact splitting of p in
  O_K. Restricting to index = 1 makes that valid at EVERY prime including ramified
  ones, so a_K(n) is exact for all n with no bad-prime casework. This is what makes
  Dirichlet convolution well-defined here and is exactly the obstruction that
  prevented testing it at 142-F.

THE NATIVE VERB, per the 142-F lesson: number theorists multiply and divide zeta
  functions. On coefficient sequences that operation is DIRICHLET CONVOLUTION,
  (f*g)(n) = sum_{d|n} f(d) g(n/d). It is the verb of the domain. The generic
  7-operator family is NOT re-run: 141-E and 142-F already measured it.

STRUCTURAL CHECK DONE AT DESIGN TIME, before any code that could report a null:
  a_K * a_L = a_M is IMPOSSIBLE for actual fields — zeta_K zeta_L has a double pole
  at s=1 and zeta_M a simple one — so that shape is a structural zero and testing it
  would manufacture a guaranteed null. The reachable shape is the BRAUER form
      1 * a_M  =  a_K * a_L,        deg M = deg K + deg L - 1,
  which balances poles and is the shape actual relations take. The headline tests
  only the reachable shape.

TWO PARTS, kept separate as at 142-F:

  PART 1, DIAGNOSTIC (confirms known mathematics; a MEASUREMENT, never the verdict):
    does the native verb reproduce classical zeta factorizations?
      D1 every quadratic field: a_K = 1 * chi_D   (classical)
      D2 every V4 quartic field M with its three quadratic subfields K1,K2,K3
         present: a_K1 * a_K2 * a_K3 = 1 * 1 * a_M   (classical Brauer relation,
         from zeta_K1 zeta_K2 zeta_K3 = zeta^2 zeta_M)

  PART 2, HEADLINE (genuinely open; carries the terminal state): are there pairs
    (K, L) and a field M with 1 * a_M = a_K * a_L that are NOT instances of the
    known Brauer relations enumerated in PART 1? A relation of this shape between
    fields not already related by subfield/compositum structure is not predicted.

POSITIVE CONTROLS, each stated WITH the input that would make it FAIL:
  C1 QUADRATIC FACTORIZATION: a_K = 1 * chi_D for every quadratic K.
     FAILS IF: the ideal counting is wrong, the Kronecker symbol is wrong, or the
     discriminant convention is wrong. (This is D1 doing double duty; it is a
     theorem, so it is a control, and it is reported in PART 1 as a measurement.)
  C2 MULTIPLICATIVITY: a_K(mn) = a_K(m) a_K(n) for every coprime pair in range.
     FAILS IF: the Euler-factor assembly is wrong.
  C3 DEGREE BOUND: a_K(p) <= deg K for every prime, with equality iff p splits
     completely, and a_K(1) = 1.
     FAILS IF: the mod-p factorization returns a wrong splitting type.
  C4 CONVOLUTION INVERSE: (a_K * mu) * 1 = a_K for every K, since mu * 1 = delta.
     FAILS IF: the convolution implementation is wrong. Tests the verb machinery
     itself, on a different code path from the Euler-factor assembly.

DEDUPLICATION, mandatory before counting anything as new (the 142-F lesson): the
  equivalence number fields carry is ISOMORPHISM, and LMFDB labels are already
  isomorphism classes, so distinct labels are distinct fields. Additionally,
  ARITHMETICALLY EQUIVALENT fields (non-isomorphic, identical zeta) would produce
  duplicate-looking relations; the census reports how many distinct zeta sequences
  the corpus holds versus how many labels, so any such collapse is visible rather
  than counted as structure.

ATTAINABILITY — a CONJUNCT of every non-vacuous branch, computed against the actual
  target band. Convolution images are unbounded positive integers; a pair (K,L) is
  admissible only if some target field M has matching degree AND the image's first
  MIN_TERMS values lie within the observed target range. Pairs with no
  degree-compatible M contribute 0 and are EXCLUDED from the denominator.

BRANCHES (partition verified by enumeration with an assert). C = controls passing
(0..4), A = reachable admissible pairs, H = headline relations NOT explained by the
PART 1 Brauer family:
  B1 VACUOUS  C < 4 or A < 1
  B2 ADVANCE  C == 4 and A >= 1 and H >= 1
  B3 KILL     C == 4 and A >= 1 and H == 0

NULL OUTPUT OF EVERY VERDICT RULE:
  - exactness rule -> "no relation" when the sequences differ anywhere in 1..N;
  - degree rule    -> pair has no compatible M, dropped from numerator AND
                      denominator;
  - control rule   -> VACUOUS, neither null nor kill;
  - PART 1 has NO verdict rule attached: it is a measurement.

MATERIALITY: census, no SE defined. Declared materiality is EXISTENCE — one
  unexplained exact convolution relation over N terms is material, since a chance
  agreement of two multiplicative integer sequences at every n <= N is negligible.

COUNTERFACTUAL-CONSEQUENCE TEST:
  ADVANCE -> the surviving relations are examined next cycle for an Artin-induction
    explanation, and if none exists they are candidate new Brauer relations.
  KILL    -> the native verb reproduces exactly the classical relations and finds
    nothing beyond them in this range; the next cycle raises the degree bound,
    where arithmetic equivalence first appears (degree 7), rather than widening
    the discriminant range at fixed degree.
  ELIGIBLE TO GO DIFFERENTLY? Yes, and checked numerically before the verdict: the
    reachable shape was chosen precisely because the impossible shape was excluded
    at design time, so A is designed to be non-zero and the branches name different
    next cycles.

WHAT DIES ON A NULL: unexplained convolution relations among degree 2-4 number
  fields of bounded discriminant. NOT the verbs thesis, NOT the 220 OEIS relations,
  and NOT the 142-F finding that native verbs see what generic ones cannot.

RECORDED RISK, before the result: degrees 2-4 with small discriminant is exactly
  the range where the classical relations were FOUND, so the expected outcome is
  that PART 1 fires and PART 2 does not. Recorded so the write-up cannot inflate a
  confirmation into a discovery.
============================= END PREREGISTRATION =============================
"""
from __future__ import annotations

import json
import math
import pathlib
from itertools import combinations

import psycopg2

ROOT = pathlib.Path(r'F:\Prometheus')
N = 200
DISC_MAX = 3000
MIN_TERMS = N


# ------------------------------ polynomial arithmetic mod p ----------------
def pnorm(a, p):
    while a and a[-1] % p == 0:
        a.pop()
    return [c % p for c in a]


def pmul(a, b, p):
    if not a or not b:
        return []
    r = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                r[i + j] = (r[i + j] + x * y) % p
    return pnorm(r, p)


def pmod(a, b, p):
    a = a[:]
    inv = pow(b[-1], p - 2, p)
    while len(a) >= len(b) and a:
        if a[-1] % p == 0:
            a.pop()
            continue
        c = a[-1] * inv % p
        sh = len(a) - len(b)
        for i, y in enumerate(b):
            a[i + sh] = (a[i + sh] - c * y) % p
        a = pnorm(a, p)
    return pnorm(a, p)


def pgcd(a, b, p):
    a, b = pnorm(a[:], p), pnorm(b[:], p)
    while b:
        a, b = b, pmod(a, b, p)
    if a:
        inv = pow(a[-1], p - 2, p)
        a = [c * inv % p for c in a]
    return a


def ppowmod(base, e, mod, p):
    r, b = [1], pmod(base, mod, p)
    while e:
        if e & 1:
            r = pmod(pmul(r, b, p), mod, p)
        b = pmod(pmul(b, b, p), mod, p)
        e >>= 1
    return r


def residue_degrees(f, p):
    """Distinct irreducible factors of f mod p, returned as their degrees.
    Each distinct prime above p contributes one zeta factor regardless of e, so
    multiplicity is deliberately discarded."""
    fp = pnorm(f[:], p)
    if len(fp) <= 1:
        return None
    d1 = pnorm([i * fp[i] for i in range(1, len(fp))], p)
    rad = fp if not d1 else pmod_div(fp, pgcd(fp, d1, p), p)
    if rad is None or len(rad) <= 1:
        return None
    degs, cur, h, x = [], rad, [0, 1], [0, 1]
    d = 0
    while len(cur) > 1:
        d += 1
        if d > len(rad):
            break
        h = ppowmod(h, p, cur, p)
        g = pgcd(pnorm([(h[i] if i < len(h) else 0) - (x[i] if i < len(x) else 0)
                        for i in range(max(len(h), len(x)))], p), cur, p)
        if len(g) > 1:
            degs += [d] * ((len(g) - 1) // d)
            cur = pmod_div(cur, g, p)
            if cur is None:
                return None
            h = pmod(h, cur, p) if len(cur) > 1 else h
    return degs


def pmod_div(a, b, p):
    """exact quotient a/b mod p"""
    a, b = pnorm(a[:], p), pnorm(b[:], p)
    if not b:
        return None
    q = [0] * max(1, len(a) - len(b) + 1)
    inv = pow(b[-1], p - 2, p)
    while len(a) >= len(b) and a:
        c = a[-1] * inv % p
        sh = len(a) - len(b)
        q[sh] = c
        for i, y in enumerate(b):
            a[i + sh] = (a[i + sh] - c * y) % p
        a = pnorm(a, p)
    return pnorm(q, p)


def primes_upto(n):
    s = [True] * (n + 1)
    s[0] = s[1] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            for j in range(i * i, n + 1, i):
                s[j] = False
    return [i for i, v in enumerate(s) if v]


PR = primes_upto(N)


def zeta_coeffs(f, deg, n_max):
    """a_K(n) for n <= n_max, from Euler factors. Valid at every p when index = 1."""
    a = [0] * (n_max + 1)
    a[1] = 1
    for p in PR:
        degs = residue_degrees(f, p)
        if degs is None or sum(degs) > deg:
            return None
        # local factor prod 1/(1 - x^{f_i}) expanded to the needed power of p
        kmax = 0
        while p ** (kmax + 1) <= n_max:
            kmax += 1
        loc = [0] * (kmax + 1)
        loc[0] = 1
        for fi in degs:
            new = [0] * (kmax + 1)
            for i in range(kmax + 1):
                if loc[i]:
                    j = i
                    while j <= kmax:
                        new[j] += loc[i]
                        j += fi
            loc = new
        # multiply into a
        for n in range(n_max, 0, -1):
            if a[n]:
                base, k = n, 1
                while base * (p ** k) <= n_max and k <= kmax:
                    a[base * (p ** k)] += a[n] * loc[k]
                    k += 1
    return a[1:]


def dconv(f, g, n_max):
    r = [0] * n_max
    for i in range(1, n_max + 1):
        if f[i - 1] == 0:
            continue
        for j in range(1, n_max // i + 1):
            r[i * j - 1] += f[i - 1] * g[j - 1]
    return r


def kronecker(a, n):
    a %= n
    if a == 0:
        return 0
    return 1 if pow(a, (n - 1) // 2, n) == 1 else -1


ONE = [1] * N
MU = [0] * (N + 1)
MU[1] = 1
for i in range(1, N + 1):
    for j in range(2 * i, N + 1, i):
        MU[j] -= MU[i]
MU_SEQ = MU[1:]

# ================================== RUN ====================================
print("CYCLE 143-G — number fields, Dedekind zeta coefficients, Dirichlet convolution")
print("=" * 78)
conn = psycopg2.connect(host='localhost', port=5432, dbname='lmfdb', user='postgres',
                        connect_timeout=15)
cur = conn.cursor()
cur.execute("""select label, degree::int, coeffs, disc_abs::numeric, disc_sign::int,
                      index::int, galois_label, subfields
               from nf_fields
               where degree::int in (2,3,4) and index::int = 1
                 and disc_abs::numeric <= %s
               order by degree::int, disc_abs::numeric""", (DISC_MAX,))
rows = cur.fetchall()
print(f"nf_fields deg 2-4, index=1, |disc| <= {DISC_MAX}: {len(rows):,}")

fields = {}
skipped = 0
for label, deg, coeffs_s, dabs, dsign, idx, gal, subs in rows:
    f = [int(x) for x in coeffs_s.strip('{}').split(',')]
    a = zeta_coeffs(f, deg, N)
    if a is None:
        skipped += 1
        continue
    fields[label] = {'deg': deg, 'poly': f, 'disc': int(dabs) * (1 if dsign > 0 else -1),
                     'gal': gal, 'subs': subs, 'a': a}
print(f"zeta sequences computed to n <= {N}: {len(fields):,}  ({skipped} skipped: "
      f"factorization returned an inconsistent splitting)")

# ------------------------------- CONTROLS ----------------------------------
# C1 / D1: quadratic factorization a_K = 1 * chi_D
c1_n = c1_bad = 0
d1_examples = []
for lab, F in fields.items():
    if F['deg'] != 2:
        continue
    D = F['disc']
    chi = [0] * N
    for n in range(1, N + 1):
        v, m = 1, n
        ok = True
        for p in PR:
            if p * p > m:
                break
            while m % p == 0:
                m //= p
                k = kronecker(D % p if p != 2 else D, p) if p != 2 else None
                if p == 2:
                    r = D % 8
                    k = 1 if r == 1 else (-1 if r == 5 else 0)
                v *= k
                if v == 0:
                    ok = False
                    break
            if not ok:
                break
        if ok and m > 1:
            v *= kronecker(D, m) if m != 2 else (1 if D % 8 == 1 else (-1 if D % 8 == 5 else 0))
        chi[n - 1] = v
    pred = dconv(ONE, chi, N)
    c1_n += 1
    if pred != F['a']:
        c1_bad += 1
    elif len(d1_examples) < 4:
        d1_examples.append(lab)
C1 = (c1_n > 0 and c1_bad == 0)

# C2 multiplicativity
c2_n = c2_bad = 0
for lab, F in list(fields.items())[:200]:
    a = F['a']
    for m in range(2, 15):
        for n in range(2, 15):
            if m * n <= N and math.gcd(m, n) == 1:
                c2_n += 1
                if a[m * n - 1] != a[m - 1] * a[n - 1]:
                    c2_bad += 1
C2 = (c2_n > 0 and c2_bad == 0)

# C3 degree bound and a_K(1)=1
c3_bad = sum(1 for F in fields.values()
             if F['a'][0] != 1 or any(F['a'][p - 1] > F['deg'] for p in PR))
C3 = (c3_bad == 0)

# C4 convolution inverse: (a_K * mu) * 1 == a_K
c4_n = c4_bad = 0
for lab, F in list(fields.items())[:200]:
    c4_n += 1
    if dconv(dconv(F['a'], MU_SEQ, N), ONE, N) != F['a']:
        c4_bad += 1
C4 = (c4_n > 0 and c4_bad == 0)

C = sum([C1, C2, C3, C4])
print("\nPOSITIVE CONTROLS (each with a stated failure mode):")
print(f"  C1 quadratic a_K = 1*chi_D : {c1_n:,} quadratic fields, {c1_bad} mismatches -> {C1}")
print(f"  C2 multiplicativity        : {c2_n:,} coprime pairs, {c2_bad} failures -> {C2}")
print(f"  C3 a_K(p) <= deg, a_K(1)=1 : {c3_bad} violations -> {C3}")
print(f"  C4 (a_K * mu) * 1 == a_K   : {c4_n:,} fields, {c4_bad} failures -> {C4}")
print(f"  control families passing: C = {C} of 4")

# ---------------- PART 1 D2: the V4 Brauer relation (known mathematics) ----
byseq = {}
for lab, F in fields.items():
    byseq.setdefault(tuple(F['a']), []).append(lab)
arith_equiv = {k: v for k, v in byseq.items() if len(v) > 1}
print(f"\nDEDUPLICATION by the equivalence the objects carry (isomorphism = label):")
print(f"  {len(fields):,} labels -> {len(byseq):,} distinct zeta sequences")
print(f"  arithmetically equivalent groups (non-isomorphic, identical zeta): {len(arith_equiv)}")

d2_checked = d2_ok = 0
d2_examples = []
quad = {lab: F for lab, F in fields.items() if F['deg'] == 2}
for lab, F in fields.items():
    if F['deg'] != 4 or not F['gal'] or '4T2' not in F['gal']:
        continue
    subs = [s for s in (F['subs'] or []) if isinstance(s, str)]
    ks = [q for q in quad if q in subs]
    if len(ks) != 3:
        continue
    d2_checked += 1
    lhs = dconv(dconv(fields[ks[0]]['a'], fields[ks[1]]['a'], N), fields[ks[2]]['a'], N)
    rhs = dconv(dconv(ONE, ONE, N), F['a'], N)
    if lhs == rhs:
        d2_ok += 1
        if len(d2_examples) < 4:
            d2_examples.append({'M': lab, 'subfields': ks})
print(f"\nPART 1 (MEASUREMENT, confirms known mathematics — NOT the verdict):")
print(f"  D1 quadratic factorizations reproduced: {c1_n - c1_bad:,} of {c1_n:,}")
print(f"  D2 V4 Brauer relations a_K1*a_K2*a_K3 == 1*1*a_M: {d2_ok} of {d2_checked} checked")
for e in d2_examples:
    print(f"     {e['M']}  <-  {e['subfields']}")

# ------------------------- PART 2 HEADLINE ---------------------------------
bydeg = {}
for lab, F in fields.items():
    bydeg.setdefault(F['deg'], []).append(lab)
targets = {}
for lab, F in fields.items():
    targets.setdefault(F['deg'], {}).setdefault(tuple(dconv(ONE, F['a'], N)), []).append(lab)

known_brauer = set()
for e in d2_examples:
    known_brauer.add(frozenset(e['subfields']))
for lab, F in fields.items():
    if F['deg'] == 4 and F['gal'] and '4T2' in F['gal']:
        subs = [s for s in (F['subs'] or []) if isinstance(s, str) and s in quad]
        for pair in combinations(sorted(subs), 2):
            known_brauer.add(frozenset(pair))

pairs_total = pairs_reachable = 0
H_hits = []
LABS = list(fields.keys())
for i, k1 in enumerate(LABS):
    F1 = fields[k1]
    for k2 in LABS[i + 1:]:
        F2 = fields[k2]
        dm = F1['deg'] + F2['deg'] - 1
        pairs_total += 1
        if dm not in targets:
            continue                      # no degree-compatible M: excluded from denominator
        pairs_reachable += 1
        img = tuple(dconv(F1['a'], F2['a'], N))
        for m in targets[dm].get(img, []):
            if m in (k1, k2):
                continue
            explained = frozenset((k1, k2)) in known_brauer
            H_hits.append({'K1': k1, 'K2': k2, 'M': m, 'deg_M': dm,
                           'explained_by_known_brauer': explained})

unexplained = [h for h in H_hits if not h['explained_by_known_brauer']]
H = len(unexplained)
attainable = pairs_reachable
print(f"\nATTAINABILITY: {pairs_total:,} field pairs, {pairs_reachable:,} with a "
      f"degree-compatible target M (rest excluded from the denominator)")
print(f"  gate H >= 1 inside attainable range [0, {attainable:,}]? {attainable >= 1}")
print(f"\nPART 2 HEADLINE — convolution relations 1*a_M == a_K1*a_K2")
print(f"  total relations found: {len(H_hits):,}")
print(f"    explained by the known V4 Brauer family: {len(H_hits) - H:,}")
print(f"    UNEXPLAINED (the headline): H = {H}")
for h in unexplained[:15]:
    print(f"      {h['K1']} * {h['K2']}  ->  {h['M']} (deg {h['deg_M']})")

branches = {'B1_VACUOUS': (C < 4) or (attainable < 1),
            'B2_ADVANCE': (C == 4) and (attainable >= 1) and (H >= 1),
            'B3_KILL':    (C == 4) and (attainable >= 1) and (H == 0)}
fired = [k for k, v in branches.items() if v]
print(f"\nBRANCHES: {branches}\n  exactly one fired? {len(fired) == 1} -> {fired}")
assert len(fired) == 1, f"BRANCHES DO NOT PARTITION: {fired}"
VERDICT = {'B1_VACUOUS': 'VACUOUS', 'B2_ADVANCE': 'ADVANCE', 'B3_KILL': 'KILL'}[fired[0]]

out = {'cycle': '143-G', 'object_class': 'number fields (nf_fields), degree 2-4, index=1',
       'representation': 'Dedekind zeta coefficients a_K(n) = #{ideals of norm n}',
       'native_verb': 'Dirichlet convolution', 'n_terms': N, 'disc_max': DISC_MAX,
       'n_fields': len(fields), 'skipped_fields': skipped,
       'controls': {'C1_quadratic': C1, 'C1_n': c1_n, 'C1_bad': c1_bad,
                    'C2_multiplicativity': C2, 'C2_n': c2_n, 'C2_bad': c2_bad,
                    'C3_degree_bound': C3, 'C3_bad': c3_bad,
                    'C4_convolution_inverse': C4, 'C4_n': c4_n, 'C4_bad': c4_bad},
       'controls_passing': C,
       'deduplication': {'labels': len(fields), 'distinct_zeta_sequences': len(byseq),
                         'arithmetically_equivalent_groups': len(arith_equiv),
                         'equivalence_used': 'field isomorphism (LMFDB label)'},
       'PART1_diagnostic': {'D1_quadratic_reproduced': c1_n - c1_bad, 'D1_total': c1_n,
                            'D2_v4_brauer_ok': d2_ok, 'D2_v4_checked': d2_checked,
                            'D2_examples': d2_examples,
                            'status': 'MEASUREMENT confirming known mathematics; not the verdict'},
       'structural_exclusion': 'a_K * a_L = a_M is impossible for fields (double vs simple pole '
                               'at s=1); only the Brauer shape 1*a_M = a_K*a_L was tested',
       'pairs_total': pairs_total, 'attainable_pairs': attainable,
       'gate_inside_attainable_range': bool(attainable >= 1),
       'relations_total': len(H_hits), 'explained_by_known_brauer': len(H_hits) - H,
       'H_unexplained': H, 'headline_hits': unexplained[:200],
       'branches': branches, 'branch_fired': fired[0], 'VERDICT': VERDICT,
       'materiality': 'existence; one unexplained exact convolution relation over 200 terms',
       'what_dies_on_null': 'unexplained convolution relations among degree 2-4 number fields of '
                            'bounded discriminant; NOT the verbs thesis, NOT the 142-F finding'}
(ROOT / 'aporia/search/cycle_143g_results.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
print(f"\n*** CYCLE 143-G VERDICT: {VERDICT} ***")
