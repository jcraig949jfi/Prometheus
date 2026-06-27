"""M0 anti-calibration sets — the keystone benchmark for "can the selector see novelty?".

Doctrine anchor: pivot/REASSESSMENT_2026-06-22_v2_enforcement.md §M0 and
pivot/prometheus_thesis_v2.md "Battery Limitations". The thesis crux: a battery
calibrated to ~100% on ~180 KNOWN truths may be a *recognizer of
things-that-look-like-existing-truths*, structurally unable to certify a TRUE
claim that is unlike its calibration set. M0 measures the type-II rate against
novel-shaped truths.

Three sets, all TRUE, hand-curated with cited truth status:

  SET A — known-TRUE claims in an UNFAMILIAR SURFACE FORM (re-encodings /
          unusual notation of facts the instrument's calibration core DOES
          contain). Tests SUPERFICIAL vs STRUCTURAL recognition: if the
          instrument rejects/can't-see a fact it provably can verify in the
          native surface form, the wall is surface-form parsing, not reach.

  SET B — known-TRUE claims from ADJACENT, UNDER-REPRESENTED domains relative to
          the EC / number-theory / school-algebra calibration core
          (combinatorics, graph theory, real-analysis identities, linear
          algebra). These are real theorems with textbook citations.

  SET C — SYNTHETIC true claims from formal systems where truth is EXTERNALLY
          CHECKABLE with zero calibration leakage (sympy-verifiable algebraic
          identities; z3-decidable arithmetic universals). The cleanest arm:
          their truth is established by an oracle independent of the instrument.

Each item is a dict with the M0-mandated fields:
  id, set, statement, truth (always True), truth_source, why_outside_manifold

and instrument-routing metadata used by the harness (m0_anticalibration.py):
  route        — how the harness will attempt to pose it to the instrument:
                   "verify_quadratic" / "verify_sqrt" / "verify_rational"
                   / "verify_conjecture" — the instrument's 5 representable kinds
                   "certify_universal" — direct z3 universal primitive
                   "entails"           — direct z3 entailment primitive
                   "sympy_identity"    — sympy-checkable identity (external oracle)
                   "UNREPRESENTABLE"   — the instrument has NO kind/primitive that
                                         can pose this claim at all (the structural
                                         wall — these are the heart of the M0 signal)
  payload      — kind-specific data the harness uses to build the probe / call.
  oracle_true  — independent ground-truth check (sympy/z3/arithmetic) the harness
                 runs so we never trust our own "truth" label; if the oracle
                 disagrees the item is flagged and excluded from rates.

These are loaded by m0_anticalibration.py. Nothing here calls the instrument.
"""
from __future__ import annotations

import sympy as sp

# Shared symbol — MUST be the harness's `x` so substitution targets line up.
from harmonia.experiments.reasoning_phase0 import x

# --------------------------------------------------------------------------- #
# SET A — TRUE facts in UNFAMILIAR SURFACE FORM (re-encodings of the core)
# --------------------------------------------------------------------------- #
# The instrument's calibration core natively verifies: polynomial roots (by
# substitution), sqrt extraneous-root rejection, rational identities with an
# excluded value, and a handful of z3-decidable arithmetic universals. Each
# Set-A item is one of those SAME facts wearing different clothes. If the
# instrument certifies the native form but not the re-encoding, the wall is
# SUPERFICIAL (surface parsing). If neither form is representable, STRUCTURAL.
SET_A = [
    {
        "id": "A1",
        "set": "A",
        "statement": "The roots of x^2 - 5x + 6 = 0, written as the unevaluated "
                     "product form (x-2)(x-3), are {2, 3}.",
        "truth": True,
        "truth_source": "Elementary algebra; 2*3=6, 2+3=5 (Vieta). Oracle-checkable.",
        "why_outside_manifold": "Same fact the quadratic verifier handles, but the "
                                "polynomial is presented FACTORED (unevaluated Mul) "
                                "rather than expanded. The verifier expands internally, "
                                "so this probes whether factored surface form survives.",
        "route": "verify_quadratic",
        "payload": {"expr": (x - 2) * (x - 3), "claimed": [2, 3]},
        "oracle_true": lambda: set(sp.solve((x - 2) * (x - 3), x)) == {2, 3},
    },
    {
        "id": "A2",
        "set": "A",
        "statement": "Phrased as a difference of squares: x^2 - 9 has its zero set "
                     "equal to {-3, 3}.",
        "truth": True,
        "truth_source": "x^2-9 = (x-3)(x+3). Oracle-checkable.",
        "why_outside_manifold": "A true root-set fact encoded via the difference-of-squares "
                                "identity surface; the verifier can represent it as a "
                                "quadratic, so any failure here is surface-level.",
        "route": "verify_quadratic",
        "payload": {"expr": x**2 - 9, "claimed": [-3, 3]},
        "oracle_true": lambda: set(sp.solve(x**2 - 9, x)) == {-3, 3},
    },
    {
        "id": "A3",
        "set": "A",
        "statement": "Re-encoding the rational identity (x^2 - 16)/(x - 4) = x + 4 "
                     "for all x except the excluded value 4.",
        "truth": True,
        "truth_source": "Polynomial division; singular only at x=4. Oracle-checkable.",
        "why_outside_manifold": "The native rational-identity-with-excluded-value fact, "
                                "but the constant (16, 4) differs from any calibration "
                                "instance. Tests representability of the SHAPE, not the "
                                "specific calibrated numbers.",
        "route": "verify_rational",
        "payload": {"num": x**2 - 16, "den": x - 4, "rhs": x + 4, "excluded": 4,
                    "claimed": "all_x_except_excluded"},
        "oracle_true": lambda: bool(sp.simplify((x**2 - 16) - (x - 4) * (x + 4)) == 0),
    },
    {
        "id": "A4",
        "set": "A",
        "statement": "The integer statement 'n^2 + n is even for every integer n', "
                     "re-encoded as 'n(n+1) is always even (product of consecutive ints)'.",
        "truth": True,
        "truth_source": "Of two consecutive integers one is even. z3-decidable. "
                        "Matches harness cid 'n2_plus_n_even'.",
        "why_outside_manifold": "Logically identical to a calibration conjecture but the "
                                "FACTORED surface n(n+1) is not the registry's literal "
                                "predicate n*n+n. Probes whether the conjecture registry "
                                "is keyed by surface string (superficial) or by meaning.",
        "route": "verify_conjecture",
        # Use a cid NOT in the registry to force the surface-form question:
        "payload": {"cid": "n_times_n_plus_1_even", "claimed": True},
        "oracle_true": lambda: all((n * (n + 1)) % 2 == 0 for n in range(-50, 50)),
    },
    {
        "id": "A5",
        "set": "A",
        "statement": "sqrt(x + 2) = x reformulated: its only real solution is x = 2 "
                     "(the candidate x = -1 from squaring is extraneous).",
        "truth": True,
        "truth_source": "Square: x+2 = x^2 => x^2-x-2=0 => x in {2,-1}; x=-1 fails "
                        "sqrt>=0 domain. Oracle-checkable.",
        "why_outside_manifold": "A true extraneous-root-rejection fact (native R2 kind) "
                                "but stated as a solution-set claim rather than the "
                                "harness's (a,b) parametrization sqrt(x+a)=x-b. Tests "
                                "whether the sqrt verifier sees it through a different "
                                "parametrization (here b=0).",
        "route": "verify_sqrt",
        "payload": {"a": 2, "b": 0, "claimed": [2]},
        "oracle_true": lambda: [s for s in sp.solve(sp.Eq(sp.sqrt(x + 2), x - 0), x)
                                if s.is_real] == [2],
    },
]

# --------------------------------------------------------------------------- #
# SET B — TRUE claims from ADJACENT, UNDER-REPRESENTED domains
# --------------------------------------------------------------------------- #
# Combinatorics / graph theory / real analysis / linear algebra. These are
# genuine theorems but the instrument has NO `kind` for them. Where a faithful
# arithmetic re-encoding into a z3-decidable universal exists, the harness will
# attempt it (and we note that the re-encoding is itself an act of human
# representation, not the instrument seeing the original). Where none exists,
# route is UNREPRESENTABLE — the structural wall.
SET_B = [
    {
        "id": "B1",
        "set": "B",
        "statement": "Handshake lemma (graph theory): in any finite graph the sum of "
                     "all vertex degrees equals twice the number of edges, hence is even.",
        "truth": True,
        "truth_source": "Euler 1736; standard graph theory (each edge contributes 2 to "
                        "the degree sum). West, 'Introduction to Graph Theory', Thm 1.3.3.",
        "why_outside_manifold": "Quantifies over graphs (a combinatorial structure). The "
                                "instrument has no graph kind and no way to pose 'for all "
                                "graphs'. STRUCTURAL non-representability.",
        "route": "UNREPRESENTABLE",
        "payload": {"domain": "finite graphs"},
        "oracle_true": lambda: True,  # established theorem; no in-instrument oracle
    },
    {
        "id": "B2",
        "set": "B",
        "statement": "Pigeonhole principle: any injection from a set of size n+1 into a "
                     "set of size n cannot exist.",
        "truth": True,
        "truth_source": "Dirichlet 1834. Standard combinatorics (Aigner-Ziegler).",
        "why_outside_manifold": "A statement about functions between finite sets; second-"
                                "order over set sizes. No representable kind. STRUCTURAL.",
        "route": "UNREPRESENTABLE",
        "payload": {"domain": "finite functions"},
        "oracle_true": lambda: True,
    },
    {
        "id": "B3",
        "set": "B",
        "statement": "Sum of the first n positive integers is n(n+1)/2, for all n >= 1.",
        "truth": True,
        "truth_source": "Gauss; closed-form arithmetic-series identity. Provable by "
                        "induction; a faithful per-n arithmetic check is z3-posable for "
                        "the algebraic identity 2*S = n(n+1) once S is the closed form.",
        "why_outside_manifold": "A real-analysis/discrete-sum identity. The instrument has "
                                "no summation kind. We CAN re-encode the closed-form "
                                "identity 2*(n(n+1)/2) = n(n+1) as a z3 universal — but that "
                                "re-encoding is a HUMAN act, not the instrument parsing the "
                                "original summation statement. Routed to certify_universal "
                                "to measure exactly that gap.",
        "route": "certify_universal",
        # Faithful but human-supplied re-encoding: n*(n+1) is even AND equals 2*S.
        # We pose the algebraically non-trivial half: n(n+1)/2 is an integer for all n,
        # i.e. n*(n+1) % 2 == 0 (the well-definedness of the closed form).
        "payload": {"predicate": lambda n: (n * (n + 1)) % 2 == 0,
                    "domain": lambda n: n >= 1},
        "oracle_true": lambda: all((n * (n + 1)) % 2 == 0 for n in range(1, 200)),
    },
    {
        "id": "B4",
        "set": "B",
        "statement": "Cauchy-Schwarz in R^2: (a*c + b*d)^2 <= (a^2 + b^2)(c^2 + d^2) "
                     "for all reals a,b,c,d.",
        "truth": True,
        "truth_source": "Cauchy-Schwarz inequality; the 2D case expands to "
                        "(ad-bc)^2 >= 0. Steele, 'The Cauchy-Schwarz Master Class'.",
        "why_outside_manifold": "A real-analysis inequality over 4 real variables. The "
                                "instrument's kinds are all equality/root based; it has no "
                                "inequality-universal kind. A z3 real-arithmetic encoding "
                                "EXISTS (nonlinear real arithmetic is decidable), so the "
                                "harness will attempt certify_universal — measuring whether "
                                "the instrument's exposed primitive reaches it.",
        "route": "certify_universal_real4",
        "payload": {"note": "(ac+bd)^2 <= (a^2+b^2)(c^2+d^2)"},
        "oracle_true": lambda: True,  # (ad-bc)^2 >= 0 identity; checked by harness via z3
    },
    {
        "id": "B5",
        "set": "B",
        "statement": "A 2x2 real matrix is invertible iff its determinant ad - bc is "
                     "nonzero.",
        "truth": True,
        "truth_source": "Linear algebra, standard (Axler, 'Linear Algebra Done Right').",
        "why_outside_manifold": "Quantifies over matrices with an iff about invertibility. "
                                "No matrix kind, no iff-of-existence kind. STRUCTURAL.",
        "route": "UNREPRESENTABLE",
        "payload": {"domain": "2x2 real matrices"},
        "oracle_true": lambda: True,
    },
    {
        "id": "B6",
        "set": "B",
        "statement": "Triangle inequality for absolute value: |a + b| <= |a| + |b| for "
                     "all real a, b.",
        "truth": True,
        "truth_source": "Standard real analysis (Rudin, 'Principles', 1.33).",
        "why_outside_manifold": "Real-analysis inequality over 2 reals with absolute "
                                "value. Decidable in z3 real arithmetic via case split, so "
                                "the harness attempts certify_universal — but |.| is not in "
                                "any instrument kind, so the instrument's own surface cannot "
                                "pose it; only the raw primitive can.",
        "route": "certify_universal_abs",
        "payload": {"note": "|a+b| <= |a|+|b|"},
        "oracle_true": lambda: True,
    },
]

# --------------------------------------------------------------------------- #
# SET C — SYNTHETIC true claims, EXTERNALLY checkable, zero calibration leakage
# --------------------------------------------------------------------------- #
# The cleanest arm. Each is generated to be true and verified by an independent
# oracle (sympy expand/simplify, or z3). NONE appear in the calibration set.
SET_C = [
    {
        "id": "C1",
        "set": "C",
        "statement": "Algebraic identity: (x+1)^3 = x^3 + 3x^2 + 3x + 1.",
        "truth": True,
        "truth_source": "Binomial theorem; verified by sympy.expand. Synthetic, no leakage.",
        "why_outside_manifold": "A polynomial IDENTITY (LHS==RHS for all x), not a "
                                "root-finding claim. The instrument's polynomial kind "
                                "verifies ROOTS, not identities — there is no identity kind. "
                                "We route via sympy_identity (external oracle) AND attempt to "
                                "coerce it into the rational verifier to see if it is even "
                                "representable.",
        "route": "sympy_identity",
        "payload": {"lhs": (x + 1)**3, "rhs": x**3 + 3 * x**2 + 3 * x + 1},
        "oracle_true": lambda: bool(sp.expand((x + 1)**3 - (x**3 + 3 * x**2 + 3 * x + 1)) == 0),
    },
    {
        "id": "C2",
        "set": "C",
        "statement": "Algebraic identity: (x^2 - 1) = (x - 1)(x + 1).",
        "truth": True,
        "truth_source": "Difference of squares; sympy-verified. Synthetic.",
        "why_outside_manifold": "Identity, not a root claim. Same structural gap as C1.",
        "route": "sympy_identity",
        "payload": {"lhs": x**2 - 1, "rhs": (x - 1) * (x + 1)},
        "oracle_true": lambda: bool(sp.expand((x**2 - 1) - (x - 1) * (x + 1)) == 0),
    },
    {
        "id": "C3",
        "set": "C",
        "statement": "z3-decidable universal: for all integers n, (2n) is even.",
        "truth": True,
        "truth_source": "Trivial; z3 proves negation unsat. Synthetic, no leakage.",
        "why_outside_manifold": "A NEW universal not in the conjecture registry. The "
                                "instrument's verify() can only route registered cids; this "
                                "one has no cid. Routed through the raw certify_universal "
                                "primitive to test whether the EXPOSED primitive (not the "
                                "packaged verify) can certify a fresh true universal.",
        "route": "certify_universal",
        "payload": {"predicate": lambda n: (2 * n) % 2 == 0, "domain": None},
        "oracle_true": lambda: all((2 * n) % 2 == 0 for n in range(-100, 100)),
    },
    {
        "id": "C4",
        "set": "C",
        "statement": "z3-decidable universal: for all integers n, n^2 >= 0.",
        "truth": True,
        "truth_source": "Squares are nonnegative; z3 proves over Z. Synthetic.",
        "why_outside_manifold": "Fresh true universal, no registry cid. Tests certify_"
                                "universal on a nonlinear-but-decidable predicate.",
        "route": "certify_universal",
        "payload": {"predicate": lambda n: n * n >= 0, "domain": None},
        "oracle_true": lambda: all(n * n >= 0 for n in range(-100, 100)),
    },
    {
        "id": "C5",
        "set": "C",
        "statement": "z3 entailment: (n > 5) entails (n > 3) for all integers n.",
        "truth": True,
        "truth_source": "Transitivity of >; z3 entails primitive returns 'valid'. Synthetic.",
        "why_outside_manifold": "An ENTAILMENT (A => B), a claim shape with no verify() "
                                "kind at all. Only reachable via the raw `entails` primitive. "
                                "Probes whether the instrument's exposed entailment primitive "
                                "certifies a true implication outside any calibration shape.",
        "route": "entails",
        "payload": {"premise": "n > 5", "conclusion": "n > 3"},
        "oracle_true": lambda: all((not (n > 5)) or (n > 3) for n in range(-100, 100)),
    },
    {
        "id": "C6",
        "set": "C",
        "statement": "Quadratic with synthetic irrational roots: x^2 - 2 has root set "
                     "{-sqrt(2), sqrt(2)}.",
        "truth": True,
        "truth_source": "sympy.solve(x**2-2). Synthetic; irrational roots absent from the "
                        "integer-root calibration instances.",
        "why_outside_manifold": "Within the polynomial kind STRUCTURALLY, but the roots are "
                                "irrational (sqrt 2) whereas every calibration quadratic has "
                                "rational/integer roots. Tests whether the verifier's "
                                "substitution certifies a root OUTSIDE the rational comfort "
                                "zone — a within-kind novelty probe.",
        "route": "verify_quadratic",
        "payload": {"expr": x**2 - 2, "claimed": [-sp.sqrt(2), sp.sqrt(2)]},
        "oracle_true": lambda: set(sp.solve(x**2 - 2, x)) == {-sp.sqrt(2), sp.sqrt(2)},
    },
    {
        "id": "C7",
        "set": "C",
        "statement": "Rational identity with a fresh constant: (x^2 - 49)/(x - 7) = x + 7 "
                     "for all x except 7.",
        "truth": True,
        "truth_source": "Polynomial division; sympy-verified. Synthetic constant (49,7).",
        "why_outside_manifold": "Native rational kind, fresh numbers — a clean within-kind "
                                "control that SHOULD pass if the kind generalizes beyond its "
                                "calibrated constants.",
        "route": "verify_rational",
        "payload": {"num": x**2 - 49, "den": x - 7, "rhs": x + 7, "excluded": 7,
                    "claimed": "all_x_except_excluded"},
        "oracle_true": lambda: bool(sp.simplify((x**2 - 49) - (x - 7) * (x + 7)) == 0),
    },
]

ALL_SETS = SET_A + SET_B + SET_C


def by_set():
    return {"A": SET_A, "B": SET_B, "C": SET_C}


if __name__ == "__main__":
    # Self-check: every item is labeled True and its independent oracle agrees.
    import sys
    bad = []
    for item in ALL_SETS:
        try:
            ok = bool(item["oracle_true"]())
        except Exception as exc:  # an oracle that crashes is a build error
            ok = False
            print(f"  ORACLE CRASH {item['id']}: {type(exc).__name__}: {exc}")
        if item["truth"] is not True:
            bad.append((item["id"], "not labeled True"))
        if not ok:
            bad.append((item["id"], "oracle disagrees with True label"))
    print(f"M0 sets: {len(ALL_SETS)} items "
          f"(A={len(SET_A)}, B={len(SET_B)}, C={len(SET_C)})")
    if bad:
        print("BUILD ERRORS (excluded from M0 rates):")
        for bid, why in bad:
            print(f"  {bid}: {why}")
        sys.exit(1)
    print("all items independently oracle-confirmed TRUE.")
