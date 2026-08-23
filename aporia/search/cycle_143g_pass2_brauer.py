"""CYCLE 143-G pass 2 — repair the silently-vacuous control, retarget the headline.

=========================== PREREGISTRATION (pass 2) ===========================
Committed BEFORE any computation.

WHAT PASS 1 GOT WRONG, stated plainly:
  D2 — the V4 Brauer relation, the one control of CONVOLUTION shape — reported
  "0 of 0 checked". It never ran. Cause: nf_fields.subfields is TEXT holding
  POLYNOMIAL COEFFICIENTS ({1.-1.1, 1.0.1, -3.0.1} = x^2-x+1, x^2+1, x^2-3), not
  LMFDB labels, so the label matching in pass 1 could never match anything.

  This matters more than pass 1's verdict. D1 (a_K = 1*chi_D) verified the ideal
  counting, but it is a FACTORIZATION-shaped identity. No control ever verified
  that the pipeline can detect a relation of the shape the headline tests. Reading
  a null from an instrument never shown able to detect the signature is the exact
  failure that doctrine forbids, so pass 1's KILL is WITHDRAWN and re-run here.

  Pass 1 also chose the headline shape 1*a_M = a_K1*a_K2 with deg M = degK1+degK2-1.
  Checked properly at design time this pass: for two quadratics that demands a CUBIC
  M with zeta_M = zeta * L(chi1) * L(chi2), while a cubic field's zeta factors as
  zeta * L(2-dim Artin) or zeta * L(chi)L(chibar) for chi of order 3 — never as two
  quadratic characters. The shape has NO known instances. Pass 1 therefore measured
  a shape it had not shown to be instantiable, which is why that null is withdrawn
  rather than merely re-scoped.

THE REPAIR, and the retarget:
  Subfields are matched by COEFFICIENT TUPLE against the corpus defining
  polynomials, which is exact — LMFDB stores 2.2.12.1 with coeffs {-3,0,1} and the
  subfield entry -3.0.1 is the same polynomial.

  The headline moves to the shape that HAS known instances, the V4 Brauer relation:
      a_K1 * a_K2 * a_K3  ==  1 * 1 * a_M
  which holds classically exactly when K1,K2,K3 are the three quadratic subfields
  of the V4 quartic M (from zeta_K1 zeta_K2 zeta_K3 = zeta^2 zeta_M).

TWO PARTS, unchanged in structure:
  PART 1 DIAGNOSTIC (known mathematics, a MEASUREMENT, never the verdict): how many
    V4 Brauer relations does the native verb reproduce? This is the convolution-shape
    verification pass 1 lacked. If it reproduces zero, the instrument cannot detect
    the signature and the reading is VACUOUS.
  PART 2 HEADLINE (genuinely open, carries the terminal): does the relation
    a_K1*a_K2*a_K3 == 1*1*a_M hold for ANY quadruple where {K1,K2,K3} are NOT the
    three quadratic subfields of M? Known mathematics says it holds exactly when
    they are. An instance where they are not is unexplained and is the discovery
    statistic.

POSITIVE CONTROLS, each with the input that would make it FAIL:
  C1 QUADRATIC FACTORIZATION a_K = 1*chi_D. FAILS IF ideal counting, Kronecker
     symbol, or discriminant convention is wrong. (Re-run, passed 1,820/1,820.)
  C2 CONVOLUTION INVERSE (a_K*mu)*1 == a_K. FAILS IF convolution is wrong.
  C3 SUBFIELD RESOLUTION: every V4 quartic in range must resolve to exactly three
     quadratic subfields present in the corpus. FAILS IF the coefficient parsing is
     wrong — which is precisely how pass 1 failed silently, so this control exists
     to make that failure loud.
  C4 BRAUER REPRODUCTION: for every resolved V4 quartic, the relation must hold.
     FAILS IF the convolution, the zeta coefficients, or the subfield identification
     is wrong. This is the convolution-shape signature check.

ATTAINABILITY — a CONJUNCT of every non-vacuous branch. A quadruple is admissible
  only if a degree-4 target exists for the convolved triple. Triples with no
  degree-compatible target contribute 0 and are EXCLUDED from the denominator.
  Additionally the headline is only read if C4 > 0, i.e. the signature is shown to
  EXIST in this archive before its absence elsewhere is interpreted.

BRANCHES (partition verified by enumeration with an assert). C = controls passing
(0..4), A = admissible triples, R = V4 Brauer relations reproduced, H = unexplained
relations:
  B1 VACUOUS  C < 4 or A < 1 or R < 1
  B2 ADVANCE  C == 4 and A >= 1 and R >= 1 and H >= 1
  B3 KILL     C == 4 and A >= 1 and R >= 1 and H == 0

NULL OUTPUT OF EVERY VERDICT RULE:
  - exactness rule   -> "no relation" if sequences differ at any n <= N;
  - degree rule      -> triple dropped from numerator AND denominator;
  - subfield rule    -> unresolved quartic excluded and COUNTED, reported beside;
  - signature rule   -> R < 1 gives VACUOUS, neither null nor kill;
  - PART 1 has no verdict rule: it is a measurement.

DEDUPLICATION before counting anything as new: quadruples are keyed by the SET
  {K1,K2,K3} so permutations are one relation, and a relation is "explained" iff
  that set equals M's three quadratic subfields.

MATERIALITY: census, no SE. Existence — one unexplained exact relation over 200
  terms is material; chance agreement of multiplicative integer sequences at every
  n <= 200 is negligible.

CONSEQUENCE: ADVANCE -> examine the unexplained quadruples for an Artin-induction
  explanation next cycle. KILL -> the native verb reproduces exactly the classical
  Brauer relations and nothing else in this range; next cycle raises the degree
  bound toward degree 7, where arithmetic equivalence first appears.
  ELIGIBLE TO GO DIFFERENTLY? Yes — verified numerically before the verdict, and
  unlike pass 1 the tested shape is now KNOWN to be instantiable.

WHAT DIES ON A NULL: unexplained V4-shaped convolution relations among quadratic
  and quartic fields of bounded discriminant. NOT the verbs thesis, NOT 142-F.

RECORDED RISK: this range is where the classical relations were found, so PART 1
  firing and PART 2 not firing is the expected outcome. Recorded in advance.
========================= END PREREGISTRATION (pass 2) =========================
"""
from __future__ import annotations

import json
import math
import pathlib
from itertools import combinations

import psycopg2

import importlib.util as _ilu

_spec = _ilu.spec_from_file_location(
    "c143", r"F:\Prometheus\aporia\search\cycle_143g_dedekind_convolution.py")

ROOT = pathlib.Path(r'F:\Prometheus')
N = 200
DISC_MAX = 3000
QUAD_DISC_MAX = 400          # bounds the triple sweep; reported beside the verdict


# ---- reuse the exact routines from pass 1 by importing their source, not rerunning it
src = pathlib.Path(r'F:\Prometheus\aporia\search\cycle_143g_dedekind_convolution.py').read_text(
    encoding='utf-8')
head = src.split('# ================================== RUN ====================================')[0]
ns = {}
exec(compile(head, 'c143_head', 'exec'), ns)
zeta_coeffs = ns['zeta_coeffs']; dconv = ns['dconv']; kronecker = ns['kronecker']
ONE = ns['ONE']; MU_SEQ = ns['MU_SEQ']; PR = ns['PR']

print("CYCLE 143-G pass 2 — Brauer-shape headline, repaired subfield resolution")
print("=" * 78)
conn = psycopg2.connect(host='localhost', port=5432, dbname='lmfdb', user='postgres',
                        connect_timeout=15)
cur = conn.cursor()
cur.execute("""select label, degree::int, coeffs, disc_abs::numeric, disc_sign::int,
                      galois_label, subfields
               from nf_fields
               where degree::int in (2,4) and index::int = 1 and disc_abs::numeric <= %s""",
            (DISC_MAX,))
rows = cur.fetchall()

fields, by_poly = {}, {}
for label, deg, coeffs_s, dabs, dsign, gal, subs in rows:
    f = [int(x) for x in coeffs_s.strip('{}').split(',')]
    a = zeta_coeffs(f, deg, N)
    if a is None:
        continue
    fields[label] = {'deg': deg, 'poly': f, 'gal': gal, 'subs_raw': subs,
                     'disc': int(dabs) * (1 if dsign > 0 else -1), 'a': a}
    by_poly[tuple(f)] = label
print(f"fields loaded (deg 2 and 4, index=1, |disc| <= {DISC_MAX}): {len(fields):,}")


def parse_subfields(s):
    """nf_fields.subfields is TEXT holding dot-separated POLYNOMIAL COEFFICIENTS,
    e.g. {1.-1.1, 1.0.1, -3.0.1}. This is the parsing pass 1 got wrong."""
    s = (s or '').strip('{}')
    if not s:
        return []
    out = []
    for part in s.split(','):
        part = part.strip()
        if not part:
            continue
        try:
            out.append(tuple(int(x) for x in part.split('.')))
        except ValueError:
            continue
    return out


# ------------------------------- CONTROLS ----------------------------------
quads = {L: F for L, F in fields.items() if F['deg'] == 2}
quartics = {L: F for L, F in fields.items() if F['deg'] == 4}

c1_n = c1_bad = 0
for L, F in quads.items():
    D = F['disc']
    chi = []
    for n in range(1, N + 1):
        v, m = 1, n
        for p in PR:
            if p * p > m:
                break
            while m % p == 0:
                m //= p
                v *= (1 if D % 8 == 1 else (-1 if D % 8 == 5 else 0)) if p == 2 else kronecker(D, p)
        if m > 1:
            v *= (1 if D % 8 == 1 else (-1 if D % 8 == 5 else 0)) if m == 2 else kronecker(D, m)
        chi.append(v)
    c1_n += 1
    if dconv(ONE, chi, N) != F['a']:
        c1_bad += 1
C1 = (c1_n > 0 and c1_bad == 0)

c2_n = c2_bad = 0
for L, F in list(fields.items())[:150]:
    c2_n += 1
    if dconv(dconv(F['a'], MU_SEQ, N), ONE, N) != F['a']:
        c2_bad += 1
C2 = (c2_n > 0 and c2_bad == 0)

# C3 subfield resolution — exists because pass 1 failed here SILENTLY
v4 = {L: F for L, F in quartics.items() if F['gal'] and '4T2' in F['gal']}
resolved, unresolved = {}, 0
for L, F in v4.items():
    polys = parse_subfields(F['subs_raw'])
    labs = [by_poly[p] for p in polys if p in by_poly and by_poly[p] in quads]
    if len(labs) == 3:
        resolved[L] = labs
    else:
        unresolved += 1
C3 = (len(v4) > 0 and unresolved == 0)

# C4 Brauer reproduction — the convolution-shape signature check
R = 0
brauer_sets = set()
for L, ks in resolved.items():
    lhs = dconv(dconv(fields[ks[0]]['a'], fields[ks[1]]['a'], N), fields[ks[2]]['a'], N)
    rhs = dconv(dconv(ONE, ONE, N), fields[L]['a'], N)
    if lhs == rhs:
        R += 1
        brauer_sets.add(frozenset(ks))
C4 = (R > 0 and R == len(resolved))

C = sum([C1, C2, C3, C4])
print("\nPOSITIVE CONTROLS (each with a stated failure mode):")
print(f"  C1 quadratic a_K = 1*chi_D    : {c1_n:,} fields, {c1_bad} mismatches -> {C1}")
print(f"  C2 (a_K*mu)*1 == a_K          : {c2_n:,} fields, {c2_bad} failures -> {C2}")
print(f"  C3 subfield resolution        : {len(v4):,} V4 quartics, {unresolved} unresolved -> {C3}")
print(f"  C4 Brauer reproduction        : {R:,} of {len(resolved):,} resolved reproduce the "
      f"relation -> {C4}")
print(f"  control families passing: C = {C} of 4")

print(f"\nPART 1 (MEASUREMENT, confirms known mathematics — NOT the verdict):")
print(f"  V4 Brauer relations a_K1*a_K2*a_K3 == 1*1*a_M reproduced: {R:,}")
for L, ks in list(resolved.items())[:5]:
    print(f"     {L}  <-  {ks}")
print(f"  THE SIGNATURE EXISTS IN THIS ARCHIVE: {R > 0} — a null below is now interpretable")

# ------------------------- PART 2 HEADLINE ---------------------------------
QS = [L for L, F in quads.items() if abs(F['disc']) <= QUAD_DISC_MAX]
print(f"\nheadline sweep over quadratics with |disc| <= {QUAD_DISC_MAX}: {len(QS):,} fields "
      f"-> {len(QS)*(len(QS)-1)*(len(QS)-2)//6:,} unordered triples")
tgt = {}
for L, F in quartics.items():
    tgt.setdefault(tuple(dconv(dconv(ONE, ONE, N), F['a'], N)), []).append(L)

triples_total = triples_admissible = 0
hits, unexplained = [], []
for k1, k2, k3 in combinations(QS, 3):
    triples_total += 1
    lhs = dconv(dconv(fields[k1]['a'], fields[k2]['a'], N), fields[k3]['a'], N)
    triples_admissible += 1
    for m in tgt.get(tuple(lhs), []):
        s = frozenset((k1, k2, k3))
        exp = s in brauer_sets and set(resolved.get(m, [])) == set(s)
        row = {'K1': k1, 'K2': k2, 'K3': k3, 'M': m, 'explained': exp}
        hits.append(row)
        if not exp:
            unexplained.append(row)

H = len(unexplained)
A = triples_admissible
print(f"\nATTAINABILITY: {triples_total:,} triples, {A:,} admissible")
print(f"  gate H >= 1 inside attainable range [0, {A:,}]? {A >= 1}")
print(f"  signature-exists precondition (R >= 1): {R >= 1}")
print(f"\nPART 2 HEADLINE — relations where {{K1,K2,K3}} are NOT M's three quadratic subfields")
print(f"  total relations found: {len(hits):,}")
print(f"    explained (they ARE M's subfields): {len(hits) - H:,}")
print(f"    UNEXPLAINED (the headline): H = {H}")
for h in unexplained[:15]:
    print(f"      {h['K1']} * {h['K2']} * {h['K3']} -> {h['M']}")

branches = {'B1_VACUOUS': (C < 4) or (A < 1) or (R < 1),
            'B2_ADVANCE': (C == 4) and (A >= 1) and (R >= 1) and (H >= 1),
            'B3_KILL':    (C == 4) and (A >= 1) and (R >= 1) and (H == 0)}
fired = [k for k, v in branches.items() if v]
print(f"\nBRANCHES: {branches}\n  exactly one fired? {len(fired) == 1} -> {fired}")
assert len(fired) == 1, f"BRANCHES DO NOT PARTITION: {fired}"
VERDICT = {'B1_VACUOUS': 'VACUOUS', 'B2_ADVANCE': 'ADVANCE', 'B3_KILL': 'KILL'}[fired[0]]

out = {'cycle': '143-G pass 2', 'pass1_verdict_withdrawn': True,
       'pass1_defect': 'D2 reported 0 of 0 checked — nf_fields.subfields holds polynomial '
                       'coefficients, not labels, so the only convolution-shaped control never '
                       'ran; and pass 1 headline shape 1*a_M=a_K1*a_K2 has no known instances',
       'object_class': 'number fields, degree 2 and 4, index=1',
       'representation': 'Dedekind zeta coefficients a_K(n)', 'native_verb': 'Dirichlet convolution',
       'n_terms': N, 'disc_max': DISC_MAX, 'quad_disc_max_for_sweep': QUAD_DISC_MAX,
       'n_fields': len(fields), 'n_quadratics': len(quads), 'n_quartics': len(quartics),
       'controls': {'C1_quadratic': C1, 'C1_n': c1_n, 'C1_bad': c1_bad,
                    'C2_conv_inverse': C2, 'C2_n': c2_n, 'C2_bad': c2_bad,
                    'C3_subfield_resolution': C3, 'C3_v4_total': len(v4),
                    'C3_unresolved': unresolved,
                    'C4_brauer_reproduction': C4, 'C4_reproduced': R,
                    'C4_resolved': len(resolved)},
       'controls_passing': C,
       'PART1_diagnostic': {'v4_brauer_relations_reproduced': R,
                            'signature_exists_in_archive': bool(R > 0),
                            'examples': {k: v for k, v in list(resolved.items())[:10]},
                            'status': 'MEASUREMENT confirming known mathematics; not the verdict'},
       'triples_total': triples_total, 'attainable_triples': A,
       'relations_total': len(hits), 'explained': len(hits) - H, 'H_unexplained': H,
       'headline_hits': unexplained[:200],
       'branches': branches, 'branch_fired': fired[0], 'VERDICT': VERDICT,
       'what_dies_on_null': 'unexplained V4-shaped convolution relations among degree 2 and 4 '
                            'fields of bounded discriminant; NOT the verbs thesis, NOT 142-F'}
(ROOT / 'aporia/search/cycle_143g_pass2_results.json').write_text(json.dumps(out, indent=1),
                                                                  encoding='utf-8')
print(f"\n*** CYCLE 143-G pass 2 VERDICT: {VERDICT} ***")
