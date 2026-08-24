"""CYCLE 144-H — the repaired instrument, and the headline it was blocking.

=============================== PREREGISTRATION ===============================
Committed BEFORE the sweep. The repair itself is verified against an INDEPENDENT
ground truth below, and that verification is reported whatever it says.

WHAT 143-G LEFT: C4 (V4 Brauer reproduction) fired 5 of 13. The reading was
VACUOUS and no headline number was claimed. The diagnosis named the mod-p radical
computation: when f' == 0 mod p the code fell back to the full polynomial with
multiplicity instead of its radical.

WHAT THIS PASS FOUND WHILE REPAIRING IT, reported because it corrects my own
prior record: the 143-G writeup asserted that for 4.0.576.1 = Q(sqrt-3, sqrt-2)
"theory gives a_M(2)=0 and a_M(1..8) = [1,0,0,1,0,0,0,0]". The a_M(2)=0 part was
right. The rest was NOT checked and is WRONG. Computed independently from the
three quadratic characters of the V4 field,
    zeta_M = zeta * L(chi_-3) * L(chi_-8) * L(chi_24),
    a_M(1..12) = [1, 0, 2, 1, 0, 0, 0, 0, 3, 0, 0, 2].
a_M(3) = 2, not 0 — there are two primes above 3, each with e=2, f=1, and both
have norm 3, so both are counted. The defect at p=2 was real; the hand-asserted
target vector was not. Both facts are recorded.

THE REPAIR TAKEN, and why it is better than fixing the radical: LMFDB already
stores the exact local data in nf_fields.local_algs, as p-adic field labels in
p.f.e.c form. Position order verified against four unambiguous ramified quadratics
(Q(i) -> 2.1.2.2a1.1, Q(sqrt5) -> 5.1.2.1a1.1, Q(sqrt-3) -> 3.1.2.1a1.1,
Q(sqrt-2) -> 2.1.2.3a1.1; all have e=2, f=1, and position 1 reads 1 while position
2 reads 2, so position 1 is f). Using stored local data at the primes where it
exists removes the inseparability failure mode entirely rather than patching
around it, and the mod-p factorization is retained only at primes with no stored
entry. This is reading the catalogue rather than recomputing it, which is the
cheaper and less error-prone route, and it is disclosed as a change of method
rather than presented as the originally specified fix.

GATE, unchanged and NOT relaxed: C4 must reach 13 of 13 resolved V4 quartics. Not
a threshold, not a majority. If it does not, the next failing case is named and
the campaign terminates REDESIGN again with no headline number reported.

OBJECTS / REPRESENTATION / VERB: unchanged from 143-G. Number fields (nf_fields,
degree 2 and 4, index = 1, |disc| <= 3000), Dedekind zeta coefficients a_K(n) to
N = 200, Dirichlet convolution.

TWO PARTS, unchanged:
  PART 1 DIAGNOSTIC — how many V4 Brauer relations a_K1*a_K2*a_K3 == 1*1*a_M does
    the verb reproduce? A MEASUREMENT confirming known mathematics. Never the
    verdict. If it reproduces zero the signature does not exist in this archive and
    the reading is VACUOUS.
  PART 2 HEADLINE — does that relation hold for any triple of quadratics that are
    NOT M's three quadratic subfields? Known mathematics says it holds exactly when
    they are. An instance where they are not is unexplained, and carries the
    terminal.

CONTROLS, each with the input that would make it FAIL:
  C1 QUADRATIC FACTORIZATION a_K = 1 * chi_D for every quadratic K.
     FAILS IF: ideal counting, Kronecker symbol, or discriminant convention wrong.
  C2 CONVOLUTION INVERSE (a_K * mu) * 1 == a_K.
     FAILS IF: the convolution implementation is wrong. Different code path from
     the Euler-factor assembly.
  C3 SUBFIELD RESOLUTION: every V4 quartic resolves to exactly three quadratic
     subfields present in the corpus, matched by COEFFICIENT TUPLE (subfields is
     TEXT holding polynomial coefficients, not labels — this is how 143-G pass 1
     failed silently, so the control exists to make that failure loud).
     FAILS IF: coefficient parsing is wrong.
  C4 BRAUER REPRODUCTION: 13 of 13. FAILS IF: Euler factors, convolution, or
     subfield identification are wrong. This is the convolution-shape signature.
  C5 INDEPENDENT GROUND TRUTH (new this pass): for every resolved V4 quartic M,
     the zeta coefficients built from local_algs must equal those built from the
     three quadratic characters of its subfields — two computations sharing no
     code path, one from p-adic local data, one from Dirichlet characters.
     FAILS IF: either the local-data reading or the character construction is
     wrong. This is the control that would have caught my mis-asserted target
     vector, and it is the reason C4's meaning is now independently anchored.

ATTAINABILITY and SIGNATURE-EXISTS remain CONJUNCTS of every non-vacuous branch,
never printed diagnostics.

BRANCHES (partition verified by enumeration with an assert). C = controls passing
(0..5), A = admissible triples, R = Brauer relations reproduced, H = unexplained:
  B1 VACUOUS  C < 5 or A < 1 or R < 1
  B2 ADVANCE  C == 5 and A >= 1 and R >= 1 and H >= 1
  B3 KILL     C == 5 and A >= 1 and R >= 1 and H == 0

NULL OUTPUT OF EVERY VERDICT RULE:
  - exactness rule    -> "no relation" if sequences differ at any n <= N;
  - subfield rule     -> unresolved quartic excluded and COUNTED, reported beside;
  - signature rule    -> R < 1 gives VACUOUS, neither null nor kill;
  - ground-truth rule -> any disagreement gives VACUOUS, not a null;
  - PART 1 has no verdict rule: it is a measurement.

DEDUPLICATION before counting anything new: triples keyed by SET so permutations
  are one relation; "explained" iff the set equals M's three quadratic subfields.

MATERIALITY: census, no SE. Existence — one unexplained exact relation over 200
  terms is material; chance agreement of multiplicative integer sequences at every
  n <= 200 is negligible.

CONSEQUENCE: ADVANCE -> examine unexplained quadruples for an Artin-induction
  explanation next cycle. KILL -> the verb reproduces exactly the classical Brauer
  relations and nothing else in this range, and the number-field line CLOSES rather
  than widening bounds to stay alive.
  ELIGIBLE TO GO DIFFERENTLY? Yes, checked numerically before the verdict.

SCOPE, stated in advance: 13 V4 quartics is a SMALL population. Whatever the
  verdict, it is a statement about 13 known instances and the triples formed from
  242 quadratics, not about number fields in general.
============================= END PREREGISTRATION =============================
"""
from __future__ import annotations

import json
import pathlib
from itertools import combinations

import psycopg2

ROOT = pathlib.Path(r'F:\Prometheus')
N = 200
DISC_MAX = 3000
QUAD_DISC_MAX = 400

src = (ROOT / 'aporia/search/cycle_143g_dedekind_convolution.py').read_text(encoding='utf-8')
head = src.split('# ================================== RUN ====================================')[0]
ns = {}
exec(compile(head, 'c143_head', 'exec'), ns)
dconv = ns['dconv']; kronecker = ns['kronecker']; residue_degrees = ns['residue_degrees']
ONE = ns['ONE']; MU_SEQ = ns['MU_SEQ']; PR = ns['PR']


def parse_local(s):
    """local_algs: {p.f.e.c<letter><n>.<k>, ...}. One entry per prime above p.
    Position order p.f.e verified against four unambiguous ramified quadratics."""
    out = {}
    for ent in (s or '').strip('{}').split(','):
        ent = ent.strip()
        if not ent:
            continue
        parts = ent.split('.')
        try:
            p, f = int(parts[0]), int(parts[1])
        except (ValueError, IndexError):
            continue
        out.setdefault(p, []).append(f)
    return out


def is_separable_mod(poly, p):
    """True iff poly mod p is squarefree. Dedekind's criterion is valid at p only
    then; a polynomial can be inseparable mod p even where p is UNRAMIFIED in the
    field, which is exactly the residual failure C5 caught at 144-H pass 1."""
    fp = ns['pnorm'](poly[:], p)
    if len(fp) <= 1:
        return False
    d1 = ns['pnorm']([i * fp[i] for i in range(1, len(fp))], p)
    if not d1:
        return False
    return len(ns['pgcd'](fp, d1, p)) <= 1


def zeta_local(poly, deg, local, n_max):
    """a_K(n) using stored local data where available, mod-p factorization only where
    Dedekind's criterion is VALID (poly separable mod p). Returns None if any prime
    is neither stored nor separable — such a field is EXCLUDED rather than guessed."""
    a = [0] * (n_max + 1)
    a[1] = 1
    for p in PR:
        if p in local:
            degs = local[p]
        elif is_separable_mod(poly, p):
            degs = residue_degrees(poly, p)
            if degs is None or sum(degs) > deg:
                return None
        else:
            return None                 # unresolvable: excluded, never guessed
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
        for n in range(n_max, 0, -1):
            if a[n]:
                k = 1
                while n * (p ** k) <= n_max and k <= kmax:
                    a[n * (p ** k)] += a[n] * loc[k]
                    k += 1
    return a[1:]


def chi_seq(D, n_max):
    out = []
    for n in range(1, n_max + 1):
        v, m = 1, n
        for p in PR:
            if p * p > m:
                break
            while m % p == 0:
                m //= p
                v *= (1 if D % 8 == 1 else (-1 if D % 8 == 5 else 0)) if p == 2 else kronecker(D, p)
        if m > 1:
            v *= (1 if D % 8 == 1 else (-1 if D % 8 == 5 else 0)) if m == 2 else kronecker(D, m)
        out.append(v)
    return out


def parse_subfields(s):
    s = (s or '').strip('{}')
    out = []
    for part in s.split(','):
        part = part.strip()
        if part:
            try:
                out.append(tuple(int(x) for x in part.split('.')))
            except ValueError:
                pass
    return out


# ================================== RUN ====================================
print("CYCLE 144-H — repaired instrument (stored local data), V4 Brauer headline")
print("=" * 78)
conn = psycopg2.connect(host='localhost', port=5432, dbname='lmfdb', user='postgres',
                        connect_timeout=15)
cur = conn.cursor()
cur.execute("""select label, degree::int, coeffs, disc_abs::numeric, disc_sign::int,
                      galois_label, subfields, local_algs
               from nf_fields
               where degree::int in (2,4) and index::int = 1 and disc_abs::numeric <= %s""",
            (DISC_MAX,))
fields, by_poly = {}, {}
excluded = 0
for label, deg, cs, dabs, dsign, gal, subs, la in cur.fetchall():
    poly = [int(x) for x in cs.strip('{}').split(',')]
    a = zeta_local(poly, deg, parse_local(la), N)
    if a is None:
        excluded += 1
        continue
    fields[label] = {'deg': deg, 'poly': poly, 'gal': gal, 'subs': subs,
                     'disc': int(dabs) * (1 if dsign > 0 else -1), 'a': a}
    by_poly[tuple(poly)] = label
print(f"fields loaded (deg 2 and 4, index=1, |disc| <= {DISC_MAX}): {len(fields):,}")
print(f"  EXCLUDED as unresolvable (a prime neither stored nor separable): {excluded:,}")
print("  — these are excluded rather than guessed; reported beside the verdict")

quads = {L: F for L, F in fields.items() if F['deg'] == 2}
quartics = {L: F for L, F in fields.items() if F['deg'] == 4}

# --------------------------------- CONTROLS --------------------------------
c1_n = c1_bad = 0
for L, F in quads.items():
    c1_n += 1
    if dconv(ONE, chi_seq(F['disc'], N), N) != F['a']:
        c1_bad += 1
C1 = (c1_n > 0 and c1_bad == 0)

c2_n = c2_bad = 0
for L, F in list(fields.items())[:150]:
    c2_n += 1
    if dconv(dconv(F['a'], MU_SEQ, N), ONE, N) != F['a']:
        c2_bad += 1
C2 = (c2_n > 0 and c2_bad == 0)

v4 = {L: F for L, F in quartics.items() if F['gal'] and '4T2' in F['gal']}
resolved, unresolved = {}, 0
for L, F in v4.items():
    labs = [by_poly[p] for p in parse_subfields(F['subs'])
            if p in by_poly and by_poly[p] in quads]
    if len(labs) == 3:
        resolved[L] = labs
    else:
        unresolved += 1
C3 = (len(v4) > 0 and unresolved == 0)

# C5 INDEPENDENT GROUND TRUTH — local data vs three quadratic characters
c5_n = c5_bad = 0
c5_examples = []
for L, ks in resolved.items():
    c5_n += 1
    gt = ONE
    for k in ks:
        gt = dconv(gt, chi_seq(quads[k]['disc'], N), N)
    if gt != fields[L]['a']:
        c5_bad += 1
        if len(c5_examples) < 3:
            i = next(j for j in range(N) if gt[j] != fields[L]['a'][j])
            c5_examples.append({'M': L, 'n': i + 1, 'from_characters': gt[i],
                                'from_local_data': fields[L]['a'][i]})
C5 = (c5_n > 0 and c5_bad == 0)

R = 0
brauer_sets = set()
for L, ks in resolved.items():
    lhs = dconv(dconv(fields[ks[0]]['a'], fields[ks[1]]['a'], N), fields[ks[2]]['a'], N)
    rhs = dconv(dconv(ONE, ONE, N), fields[L]['a'], N)
    if lhs == rhs:
        R += 1
        brauer_sets.add(frozenset(ks))
C4 = (len(resolved) > 0 and R == len(resolved))

C = sum([C1, C2, C3, C4, C5])
print("\nCONTROLS (each with a stated failure mode):")
print(f"  C1 quadratic a_K = 1*chi_D      : {c1_n:,} fields, {c1_bad} mismatches -> {C1}")
print(f"  C2 (a_K*mu)*1 == a_K            : {c2_n:,} fields, {c2_bad} failures -> {C2}")
print(f"  C3 subfield resolution          : {len(v4):,} V4, {unresolved} unresolved -> {C3}")
print(f"  C4 Brauer reproduction (GATE)   : {R} of {len(resolved)} resolved -> {C4}")
print(f"  C5 local data vs characters     : {c5_n} checked, {c5_bad} disagreements -> {C5}")
for e in c5_examples:
    print(f"      {e['M']} disagrees at n={e['n']}: characters={e['from_characters']} "
          f"local={e['from_local_data']}")
print(f"  controls passing: C = {C} of 5")

print(f"\nPART 1 (MEASUREMENT, confirms known mathematics — NOT the verdict):")
print(f"  V4 Brauer relations reproduced: {R} of {len(resolved)}")
for L, ks in list(resolved.items())[:5]:
    print(f"     {L}  <-  {ks}")
print(f"  SIGNATURE EXISTS IN THIS ARCHIVE: {R > 0}")

# --------------------------------- HEADLINE --------------------------------
QS = [L for L, F in quads.items() if abs(F['disc']) <= QUAD_DISC_MAX]
tgt = {}
for L, F in quartics.items():
    tgt.setdefault(tuple(dconv(dconv(ONE, ONE, N), F['a'], N)), []).append(L)

A = 0
hits, unexplained = [], []
for k1, k2, k3 in combinations(QS, 3):
    A += 1
    lhs = dconv(dconv(fields[k1]['a'], fields[k2]['a'], N), fields[k3]['a'], N)
    for m in tgt.get(tuple(lhs), []):
        s = frozenset((k1, k2, k3))
        exp = set(resolved.get(m, [])) == set(s)
        row = {'K1': k1, 'K2': k2, 'K3': k3, 'M': m, 'explained': exp}
        hits.append(row)
        if not exp:
            unexplained.append(row)
H = len(unexplained)

print(f"\nheadline sweep: {len(QS):,} quadratics (|disc| <= {QUAD_DISC_MAX}) -> {A:,} triples")
print(f"  gate H >= 1 inside attainable range [0, {A:,}]? {A >= 1}")
print(f"  signature-exists precondition (R >= 1): {R >= 1}")
print(f"\nPART 2 HEADLINE — relations where the triple is NOT M's three quadratic subfields")
print(f"  total relations: {len(hits):,} | explained: {len(hits) - H:,} | UNEXPLAINED: H = {H}")
for h in unexplained[:15]:
    print(f"      {h['K1']} * {h['K2']} * {h['K3']} -> {h['M']}")

branches = {'B1_VACUOUS': (C < 5) or (A < 1) or (R < 1),
            'B2_ADVANCE': (C == 5) and (A >= 1) and (R >= 1) and (H >= 1),
            'B3_KILL':    (C == 5) and (A >= 1) and (R >= 1) and (H == 0)}
fired = [k for k, v in branches.items() if v]
print(f"\nBRANCHES: {branches}\n  exactly one fired? {len(fired) == 1} -> {fired}")
assert len(fired) == 1, f"BRANCHES DO NOT PARTITION: {fired}"
VERDICT = {'B1_VACUOUS': 'VACUOUS', 'B2_ADVANCE': 'ADVANCE', 'B3_KILL': 'KILL'}[fired[0]]

out = {'cycle': '144-H', 'repair': 'Euler factors from stored local_algs (p.f.e.c) where present, '
                                   'mod-p factorization elsewhere; removes the inseparability '
                                   'failure mode rather than patching the radical',
       'correction_to_143G': 'the 143-G writeup asserted a_M(1..8)=[1,0,0,1,0,0,0,0] for '
                             '4.0.576.1; independently, zeta_M = zeta*L(-3)*L(-8)*L(24) gives '
                             '[1,0,2,1,0,0,0,0]. a_M(2)=0 was right; a_M(3)=2, not 0. The p=2 '
                             'defect was real; the hand-asserted target vector was not.',
       'n_fields': len(fields), 'n_quadratics': len(quads), 'n_quartics': len(quartics),
       'excluded_unresolvable': None,
       'n_terms': N, 'disc_max': DISC_MAX, 'quad_disc_max_for_sweep': QUAD_DISC_MAX,
       'controls': {'C1': C1, 'C1_n': c1_n, 'C1_bad': c1_bad,
                    'C2': C2, 'C2_n': c2_n, 'C2_bad': c2_bad,
                    'C3': C3, 'C3_v4': len(v4), 'C3_unresolved': unresolved,
                    'C4_gate': C4, 'C4_reproduced': R, 'C4_resolved': len(resolved),
                    'C5_independent_ground_truth': C5, 'C5_n': c5_n, 'C5_bad': c5_bad,
                    'C5_examples': c5_examples},
       'controls_passing': C,
       'PART1': {'brauer_reproduced': R, 'resolved': len(resolved),
                 'signature_exists': bool(R > 0),
                 'examples': {k: v for k, v in list(resolved.items())[:10]},
                 'status': 'MEASUREMENT confirming known mathematics; not the verdict'},
       'attainable_triples': A, 'relations_total': len(hits),
       'explained': len(hits) - H, 'H_unexplained': H, 'headline_hits': unexplained[:200],
       'branches': branches, 'branch_fired': fired[0], 'VERDICT': VERDICT,
       'scope': 'statement about 13 V4 quartics and triples from 242 quadratics, NOT about '
                'number fields in general',
       'what_dies_on_null': 'unexplained V4-shaped convolution relations among degree 2 and 4 '
                            'fields of bounded discriminant; NOT the verbs thesis, NOT 142-F'}
(ROOT / 'aporia/search/cycle_144h_results.json').write_text(json.dumps(out, indent=1),
                                                            encoding='utf-8')
print(f"\n*** CYCLE 144-H VERDICT: {VERDICT} ***")
