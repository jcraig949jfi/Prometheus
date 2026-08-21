"""PARADIGM-P18 worked example — Operadic / Categorical Composition, executed.

The paradigm's move: make the COMPOSITION STRUCTURE itself the object.
Executable instance: Mac Lane's pentagon coherence meeting group cohomology.
For G-graded lines with associator scalars omega: G^3 -> {+-1}, the pentagon
identity (five re-bracketings of a 4-fold product commute) holds iff omega is
a 3-COCYCLE. We verify this equivalence NON-TAUTOLOGICALLY by two routes over
ALL 256 candidate omegas for G = Z/2:

  Route 1 (categorical/matrix): build the five associator maps as literal
    16x16 diagonal matrices on the 4-fold graded product, COMPOSE the two
    pentagon paths, compare matrices entrywise.
  Route 2 (algebraic/formula): the cocycle condition
    omega(b,c,d) * omega(a,bc,d) * omega(a,b,c) == omega(ab,c,d) * omega(a,b,cd)
    evaluated pointwise.
The routes share no code path — index bookkeeping errors in the matrix route
would break the agreement. Then the cohomology census: cocycles / coboundaries
-> |H^3(Z/2, Z/2)| classes, with the coboundary count DERIVED by enumerating
all 2-cochains and applying the coboundary operator by definition.

Pre-stated readings (BEFORE run):
  COHERENCE-IS-COHOMOLOGY  route agreement on ALL 256 omegas; cocycle count a
                           power of 2; |H^3| = cocycles/coboundaries = 2
                           (the classical value ARRIVING, not assumed).
  ROUTE-DISAGREEMENT       instrument-first: matrix index order (the whole
                           point of the two-route design), coboundary sign
                           conventions (irrelevant over Z/2 — noted).
"""
from __future__ import annotations
import json
import pathlib
from itertools import product

import numpy as np

HERE = pathlib.Path(__file__).parent
OUT = HERE / "paradigm_p18_results.json"

G = [0, 1]                                  # Z/2, written additively
add = lambda a, b: (a + b) % 2
TRIPLES = list(product(G, G, G))            # 8 -> omega encoded as 8-bit vector
QUADS = list(product(G, G, G, G))           # 16 components of the 4-fold product


def omega_from_bits(bits):
    return {t: (-1) ** b for t, b in zip(TRIPLES, bits)}


def pentagon_matrix_route(om):
    """Five associator maps as diagonal 16x16 matrices over the 4-fold product."""
    def diag(scalar_fn):
        return np.diag([scalar_fn(q) for q in QUADS])
    # path 1: ((ab)c)d -> (ab)(cd) -> a(b(cd))   [alpha_{ab,c,d} then alpha_{a,b,cd}]
    m1 = diag(lambda q: om[(add(q[0], q[1]), q[2], q[3])])
    m2 = diag(lambda q: om[(q[0], q[1], add(q[2], q[3]))])
    path_short = m2 @ m1
    # path 2: ((ab)c)d -> (a(bc))d -> a((bc)d) -> a(b(cd))
    n1 = diag(lambda q: om[(q[0], q[1], q[2])])
    n2 = diag(lambda q: om[(q[0], add(q[1], q[2]), q[3])])
    n3 = diag(lambda q: om[(q[1], q[2], q[3])])
    path_long = n3 @ n2 @ n1
    return np.array_equal(path_short, path_long)


def cocycle_formula_route(om):
    return all(om[(b, c, d)] * om[(a, add(b, c), d)] * om[(a, b, c)]
               == om[(add(a, b), c, d)] * om[(a, b, add(c, d))]
               for a, b, c, d in QUADS)


agree = 0
cocycles = []
for bits in product([0, 1], repeat=8):
    om = omega_from_bits(bits)
    m = pentagon_matrix_route(om)
    f = cocycle_formula_route(om)
    agree += (m == f)
    if f:
        cocycles.append(bits)
print(f"route agreement: {agree}/256 omegas; cocycles found: {len(cocycles)}", flush=True)
assert agree == 256, "ROUTE-DISAGREEMENT — matrix bookkeeping fault"

# --- coboundaries by definition: (d beta)(a,b,c) = beta(b,c) beta(a, b+c) / (beta(a+b, c) beta(a,b))
PAIRS = list(product(G, G))
cob = set()
for bbits in product([0, 1], repeat=4):
    beta = {p: (-1) ** b for p, b in zip(PAIRS, bbits)}
    d = tuple(0 if beta[(b, c)] * beta[(a, add(b, c))] * beta[(add(a, b), c)] * beta[(a, b)] == 1
              else 1 for a, b, c in TRIPLES)
    # encode the coboundary's sign pattern as bits (omega = d beta)
    cob.add(d)
n_cob = len(cob)
n_coc = len(cocycles)
h3 = n_coc // n_cob
print(f"cocycles {n_coc}, distinct coboundaries {n_cob} -> |H^3(Z/2, Z/2)| = {h3}", flush=True)

verdict = ("COHERENCE-IS-COHOMOLOGY" if (agree == 256 and h3 == 2) else "ROUTE-DISAGREEMENT")
print(f"-> {verdict}", flush=True)
OUT.write_text(json.dumps({
    "protocol": "pentagon coherence vs 3-cocycle condition, two independent routes (16x16 diagonal-matrix path composition vs pointwise formula) over all 256 omega: (Z/2)^3 -> {+-1}; cohomology census with coboundaries enumerated by definition",
    "route_agreement": agree, "n_cocycles": n_coc, "n_coboundaries": n_cob,
    "H3_order": h3, "verdict": verdict,
    "meta_gap": "infinity-categories / topos-level structure has no executable local substrate — the decidable shadow is finite coherence, which is what this example runs (P14 hybrid pattern)"},
    indent=1), encoding="utf-8")
print(f"-> {OUT.name}", flush=True)
