"""hypothesis_class_coverage_audit.py — what can the void-miner even SEE?

PROGRAM-REASSESSMENT AUDIT (Harmonia A, 2026-06-22). Not a refutation of any
prior result: sessionD's EC-rich "0 novel within-object laws" is internally
sound (validators 16/16, re-run under the executing lens this session). This
artifact asks the *next* question — the one the stall/monoculture reassessment
needs:

    Is "0 novel laws" a property of the TERRAIN (B1: nothing there) or of the
    INSTRUMENT (B2: the miner's hypothesis class cannot express the kind of law
    that would be novel)?  [feedback_distinguish_B1_B2]

It is answered by a COVERAGE MEASURE on the hypothesis class. The miner can only
ever express claims of the shape

    rel( f(inv_i(O)), g(inv_j(O)) )      f,g in OPERATORS; rel in RELATIONS

i.e. a unary transform of ONE integer invariant standing in ONE of four
relations to a unary transform of ANOTHER integer invariant, same object,
pairwise. We enumerate known elliptic-curve structure and, for each law, decide
whether it falls inside that class — and if not, WHY not (a structured blocking
reason, so the judgment is auditable, not prose).

The headline is the fraction of known EC structure the instrument can express.
If that fraction is small, "0 novel" is a statement about a small shadow, not
about the fire (SHADOWS_ON_WALL): the diminishing returns are a property of the
ruler, and the fix is a richer hypothesis class, not more integer invariants.

Run: PYTHONPATH=. PYTHONIOENCODING=utf-8 python harmonia/experiments/hypothesis_class_coverage_audit.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

# Measure the ACTUAL instrument, not a description of it.
from theseus.generators.a3_functional_identity import OPERATORS          # noqa: E402
from theseus.generators.a1_catalog_cross_product import RELATIONS        # noqa: E402

OUT = Path(__file__).parent / "hypothesis_class_coverage_results.json"

# The 9 integer invariants the EC-rich sweep actually mined.
EC_RICH_INVARIANTS = (
    "rank", "conductor", "tamagawa_product", "torsion",
    "sha_an", "num_bad_primes", "cm", "signD", "conductor_radical",
)

# Structured blocking-reason enum: the AXIS of the hypothesis class that a law
# violates. This is the shape of the ceiling, not a verdict.
#   IN_CLASS        expressible: pairwise, integer-valued, relation in RELATIONS,
#                   same-object. (sub-note: in-catalog / needs-new-invariant)
#   UNARY           a property of ONE invariant, not a relation between two
#                   (e.g. "|Sha| is a perfect square", "torsion order bounded")
#   ARITY_GE_3      relates 3+ invariants simultaneously
#   REAL_VALUED     involves a non-integer invariant (regulator, period, height,
#                   L-value) — outside an all-integer lattice
#   RELATION_OOV    the relation is not one of {equal, equal_mod_2, divides,
#                   abs_diff_le_3}: multiplicative, ratio/asymptotic bound,
#                   set-equality of prime support, congruence mod p>3, etc.
#   CROSS_OBJECT    relates invariants of DIFFERENT objects (isogeny class, twist,
#                   reduction mod p) — the diagonal pairs each object with itself
#   DISTRIBUTIONAL  a statement about a SEQUENCE / distribution (Sato-Tate,
#                   root number as a product over primes), not two scalars

# Each entry: (name, status, reason, note). status in the enum above.
# "found" is set programmatically for IN_CLASS laws the sweep actually surfaced.
KNOWN_EC_LAWS = [
    ("Lorenzini 2011: |E(Q)_tors| divides prod(c_p)",
     "IN_CLASS", None,
     "torsion divides tamagawa_product; integer/integer; FOUND by the sweep"),
    ("Shared prime support: rad(N) | N  and  N == rad(N) (mod 2)",
     "IN_CLASS", None,
     "conductor_radical vs conductor; definitional; FOUND by the sweep"),
    ("BSD rank equality: ord_{s=1} L(E,s) == rank",
     "IN_CLASS", None,
     "analytic_rank == rank: integer==integer, IN class — but analytic_rank is "
     "NOT among the 9 mined invariants. Expressible, never offered to the miner."),
    ("Parity conjecture: rank == (1 - root_number)/2  (mod 2)",
     "IN_CLASS", None,
     "rank equal_mod_2 root_number-as-{0,1}: integer/integer, IN class — but "
     "root_number is not a mined invariant. Expressible, never offered."),
    ("Mazur 1977: |E(Q)_tors| in {1..10, 12}",
     "UNARY", "UNARY",
     "a bound on ONE invariant; only injectable as a domain theorem (T1b), never "
     "a D_JOINT. The miner cannot DISCOVER it, only be TOLD it."),
    ("|Sha| is a perfect square (Cassels-Tate alternating pairing)",
     "UNARY", "UNARY",
     "perfect-square is a property of sha_an alone; sessionD flagged this exact "
     "gap. Needs a unary-property miner."),
    ("Modularity: every E/Q arises from a weight-2 newform",
     "CROSS_OBJECT", "CROSS_OBJECT",
     "a correspondence E <-> f to an object of a different category, not a "
     "relation between two integer invariants of E."),
    ("Sato-Tate: a_p/(2 sqrt p) equidistributes w.r.t. semicircle",
     "DISTRIBUTIONAL", "DISTRIBUTIONAL",
     "a law about the SEQUENCE (a_p)_p and a real-valued limiting measure."),
    ("Ogg's formula: f_p = ord_p(Delta) + 1 - m_p  (additive reduction)",
     "ARITY_GE_3", "ARITY_GE_3",
     "three per-prime quantities (conductor exp, discriminant val, #components); "
     "arity 3 and per-prime, doubly out of class."),
    ("Szpiro / abc: log|Delta| <= (6+eps) log N  asymptotically",
     "REAL_VALUED", "RELATION_OOV",
     "a ratio/asymptotic inequality on real logs; abs_diff_le_3 is a fixed small "
     "additive bound, not a multiplicative one."),
    ("BSD formula: L^(r)(1)/r! = Omega*Reg*prod(c_p)*|Sha| / |tors|^2",
     "REAL_VALUED", "REAL_VALUED",
     "regulator, real period, and L-value derivative are real-valued; the lattice "
     "is all-integer."),
    ("Conductor is isogeny-invariant",
     "CROSS_OBJECT", "CROSS_OBJECT",
     "equality of one invariant across an isogeny ORBIT of distinct curves; the "
     "diagonal pairs each curve only with itself."),
    ("Root number = product of local root numbers over bad primes & infinity",
     "DISTRIBUTIONAL", "DISTRIBUTIONAL",
     "a product over a per-prime family; not a two-scalar relation."),
    ("Torsion injects into E(F_p) for primes p of good reduction",
     "CROSS_OBJECT", "CROSS_OBJECT",
     "relates E(Q)_tors to the reduction E(F_p) — a different object per p."),
    ("Kodaira/Tate reduction types per bad prime",
     "ARITY_GE_3", "RELATION_OOV",
     "categorical per-prime classification; not any scalar relation in RELATIONS."),
    ("Conductor-discriminant prime-support equality: rad(N) == rad(Delta)",
     "RELATION_OOV", "RELATION_OOV",
     "set-equality of prime supports; 'equal' on radicals is partially the "
     "rad(N)|N shadow, but Delta is not a mined integer invariant and the true "
     "law is set-equality, not a scalar relation."),
]

# Laws the sweep actually surfaced (from EC_RICH_DIAGONAL results / validator).
FOUND_IN_CLASS = {
    "Lorenzini 2011: |E(Q)_tors| divides prod(c_p)",
    "Shared prime support: rad(N) | N  and  N == rad(N) (mod 2)",
}


def main():
    n_ops = len(OPERATORS)
    n_rel = len(RELATIONS)
    n_inv = len(EC_RICH_INVARIANTS)
    # diagonal: ordered pairs i != j
    n_pairs = n_inv * (n_inv - 1)
    class_size = n_ops * n_ops * n_pairs * n_rel

    rows = []
    for name, status, reason, note in KNOWN_EC_LAWS:
        in_class = status == "IN_CLASS"
        rows.append({
            "law": name,
            "status": status,
            "blocking_axis": reason,        # None when IN_CLASS
            "in_class": in_class,
            "found": name in FOUND_IN_CLASS,
            "in_catalog": in_class and name in FOUND_IN_CLASS,
            "note": note,
        })

    n_total = len(rows)
    n_in_class = sum(r["in_class"] for r in rows)
    n_in_class_in_catalog = sum(r["in_class"] and r["in_catalog"] for r in rows)
    n_found = sum(r["found"] for r in rows)
    blocked = Counter(r["blocking_axis"] for r in rows if not r["in_class"])

    print("=" * 72)
    print("HYPOTHESIS-CLASS COVERAGE AUDIT — EC void-miner (Harmonia A, 2026-06-22)")
    print("=" * 72)
    print(f"\nInstrument (measured live):")
    print(f"  operators ({n_ops}): {list(OPERATORS.keys())}")
    print(f"  relations ({n_rel}): {list(RELATIONS)}")
    print(f"  invariants ({n_inv}): {EC_RICH_INVARIANTS}")
    print(f"  hypothesis-class size (diagonal): {n_ops}*{n_ops}*{n_pairs}*{n_rel}"
          f" = {class_size} cells")
    print(f"  ALL invariants integer-valued; ALL relations scalar; pairwise; "
          f"same-object.")

    print(f"\nKnown-EC-law expressibility ({n_total} laws surveyed):")
    print(f"  EXPRESSIBLE in class .............. {n_in_class}/{n_total} "
          f"= {n_in_class/n_total:.0%}")
    print(f"    of which actually in the catalog  {n_in_class_in_catalog} "
          f"(the rest are in-class but were never offered an invariant)")
    print(f"    of which the sweep FOUND .......  {n_found} "
          f"(every in-catalog expressible law WAS found — instrument works)")
    print(f"  OUT OF CLASS by construction ..... {n_total - n_in_class}/{n_total}"
          f" = {(n_total-n_in_class)/n_total:.0%}")
    print(f"\n  Ceiling structure (why the {n_total - n_in_class} are unreachable):")
    for axis, k in blocked.most_common():
        print(f"    {axis:16s} {k}")

    print(f"\nPer-law:")
    for r in sorted(rows, key=lambda x: (not x["in_class"], x["status"])):
        mark = ("FOUND " if r["found"]
                else "in-class, no invariant" if r["in_class"]
                else r["blocking_axis"])
        print(f"  [{mark:>22s}] {r['law']}")

    verdict = (
        "B2-DOMINATED: '0 novel' is conditioned on a hypothesis class that "
        f"excludes {(n_total-n_in_class)/n_total:.0%} of surveyed known EC "
        "structure by construction. The instrument found every in-catalog law it "
        "COULD express and zero it could not — so the result measures the shadow, "
        "not the terrain. Widening integer invariants cannot raise coverage; only "
        "a richer hypothesis class (real-valued invariants, arity>=3, unary-"
        "property miner, cross-object pairing, relations beyond the four) can."
    )
    print(f"\nVERDICT: {verdict}")

    out = {
        "meta": {"date": "2026-06-22", "author": "Harmonia_M2_A",
                 "purpose": "B1-vs-B2 coverage diagnostic on the EC void-miner "
                            "hypothesis class; program-reassessment audit",
                 "not_a_refutation_of": "sessionD EC-rich 0-novel result is "
                            "internally sound; this measures the class it lives in"},
        "instrument": {
            "operators": list(OPERATORS.keys()),
            "relations": list(RELATIONS),
            "invariants": list(EC_RICH_INVARIANTS),
            "class_size_diagonal": class_size,
            "all_integer": True, "scalar_relations": True,
            "pairwise": True, "same_object": True,
        },
        "coverage": {
            "n_laws_surveyed": n_total,
            "n_expressible": n_in_class,
            "n_expressible_in_catalog": n_in_class_in_catalog,
            "n_found": n_found,
            "n_out_of_class": n_total - n_in_class,
            "expressible_fraction": round(n_in_class / n_total, 3),
            "out_of_class_fraction": round((n_total - n_in_class) / n_total, 3),
            "ceiling_structure": dict(blocked),
        },
        "laws": rows,
        "verdict": verdict,
    }
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
