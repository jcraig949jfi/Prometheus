"""a3_void_extension_stress.py — ROUND FINAL for Proposal B (Harmonia D, v2).

The Lean leg is not executable on this host (no lean/lake; external_deps has
only an unbuilt mathlib_repl shell) and would be vacuous anyway: certificates
are finite-domain statements already machine-verified, and the adjacent real
theorems (knot determinant odd; Mazur torsion) are not in mathlib.

This is the stronger substitute: CLOSURE-BASED FALSIFICATION BY EXTENSION.
v1 of this script used a finite table of documented out-of-catalog values and
was too weak (63 non-T1 "robust" survivors included cells that break at the
known rank-4 curves or signature -16 torus knots the table omitted). v2 does
it right: per invariant we declare the TRUE POPULATION CLOSURE — unbounded,
or bounded by a *named theorem* — propagate it symbolically through each
operator, and re-check the relation on the closure product. A void is

  THEOREM_BACKED       rel holds on the closure product; the certificate's
                       load-bearing bounds are theorems (cited), so the void
                       extends to the full mathematical population.
  SELECTION_ARTIFACT   rel fails on the closure product: the void is a fact
                       about THIS catalog's sampling window, guaranteed to
                       break under honest catalog extension.
  UNKNOWN_SEMANTICS    verdict hinges on trace_field_class, whose enum
                       semantics are undocumented; flagged, not guessed.

Pre-registered prediction (Harmonia D, before v2 run): the THEOREM_BACKED
non-T1 set is exactly the 6 cells (mod_3, log2_floor, ki, torsion,
abs_diff_le_3) — mod_3 side in {0,1,2} by arithmetic, torsion side in [0,3]
under log2_floor BY MAZUR'S TORSION THEOREM (orders in {1..10,12}).

Population closures (all standard facts, citations inline):
  crossing_number   unbounded above (knot tables to 19 crossings and beyond)
  signature         unbounded both ways, EVEN (theorem: knot signature is even)
  determinant       unbounded above, ODD (theorem: det(K) = |Delta_K(-1)| odd)
  three_genus       unbounded above (torus knots T(2,2n+1) have genus n)
  trace_field_class UNKNOWN enum semantics -> UNKNOWN
  nf_class_number   unbounded above (class numbers unbounded over number fields)
  rank              treated unbounded: rank >= 28 curves are KNOWN (Elkies
                    2006); boundedness is an open conjecture either way, and
                    known curves already exceed every catalog-derived bound
  torsion           FINITE {1..10, 12} — MAZUR'S THEOREM (the one genuine
                    finiteness theorem in this lattice's reach)
  conductor         unbounded above (min 11 = curve 11a1)
  tamagawa_product  unbounded above

Emits harmonia/experiments/a3_void_extension_stress.json (flushed from Python).
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from theseus.generators.a3_functional_identity import OPERATORS                 # noqa: E402
from theseus.generators.a1_catalog_cross_product import (                       # noqa: E402
    _load_catalog, _get_int, _evaluate_relation,
)
from theseus.config import KNOTS_DB_PATH, BSD_RICH_DB_PATH                      # noqa: E402
from harmonia.primitives.lattice_void_miner import LatticeSpec, mine            # noqa: E402


# ----------------------------------------------------------------------------
# Closures.  kind in {finite, nat_unbounded, neg_unbounded, int_unbounded,
# unknown}; optional parity in {0,1,None}; optional citation.
# ----------------------------------------------------------------------------
def C(kind, values=None, lo=None, hi=None, parity=None, citation=None):
    return {"kind": kind, "values": values, "lo": lo, "hi": hi,
            "parity": parity, "citation": citation}


POPULATION_CLOSURES = {
    ("a", "crossing_number"): C("nat_unbounded", lo=3),
    ("a", "signature"): C("int_unbounded", parity=0,
                          citation="knot signature is even"),
    ("a", "determinant"): C("nat_unbounded", lo=1, parity=1,
                            citation="det(K)=|Delta_K(-1)| is odd"),
    ("a", "three_genus"): C("nat_unbounded", lo=1),
    ("a", "trace_field_class"): C("unknown"),
    ("a", "nf_class_number"): C("nat_unbounded", lo=1),
    ("b", "rank"): C("nat_unbounded", lo=0,
                     citation="rank>=28 curves known (Elkies)"),
    ("b", "torsion"): C("finite", values=frozenset({1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12}),
                        citation="MAZUR: torsion order in {1..10,12}"),
    ("b", "conductor"): C("nat_unbounded", lo=11),
    ("b", "tamagawa_product"): C("nat_unbounded", lo=1),
}

_SQ_MOD_100_FULL = frozenset((r * r) % 100 for r in range(100))
_SQ_MOD_100_ODD = frozenset((r * r) % 100 for r in range(1, 100, 2))
_SQ_MOD_100_EVEN = frozenset((r * r) % 100 for r in range(0, 100, 2))


def apply_op_to_closure(op_name: str, cl: dict) -> dict:
    """Symbolic image of a closure under one a3 operator."""
    if cl["kind"] == "unknown":
        return C("unknown")
    if cl["kind"] == "finite":
        op = OPERATORS[op_name]
        return C("finite", values=frozenset(op(v) for v in cl["values"]),
                 citation=cl["citation"])
    # unbounded families
    if op_name == "identity":
        return dict(cl)
    if op_name == "abs":
        if cl["kind"] == "int_unbounded":
            return C("nat_unbounded", lo=0, parity=cl["parity"])
        if cl["kind"] == "neg_unbounded":
            return C("nat_unbounded", lo=max(0, -(cl["hi"])), parity=cl["parity"])
        return C("nat_unbounded", lo=max(0, cl["lo"]), parity=cl["parity"])
    if op_name == "neg":
        if cl["kind"] == "int_unbounded":
            return dict(cl)
        if cl["kind"] == "nat_unbounded":
            return C("neg_unbounded", hi=-cl["lo"], parity=cl["parity"])
        if cl["kind"] == "neg_unbounded":
            return C("nat_unbounded", lo=-cl["hi"], parity=cl["parity"])
    if op_name == "mod_3":
        return C("finite", values=frozenset({0, 1, 2}))   # pigeonhole, any int
    if op_name == "sq_mod_100":
        if cl["parity"] == 1:
            return C("finite", values=_SQ_MOD_100_ODD, parity=1,
                     citation=cl["citation"])
        if cl["parity"] == 0:
            return C("finite", values=_SQ_MOD_100_EVEN, parity=0,
                     citation=cl["citation"])
        return C("finite", values=_SQ_MOD_100_FULL)
    if op_name == "log2_floor":
        # log2_floor(v) = floor(log2 |v|), 0 -> 0; unbounded input -> unbounded
        return C("nat_unbounded", lo=0)
    raise ValueError(f"unhandled op/closure: {op_name} on {cl['kind']}")


def rel_holds_on_closures(ca: dict, cb: dict, rel: str):
    """Does rel hold for ALL (a, b) in the closure product?
    Returns (verdict, reason): verdict in {True, False, None=unknown}."""
    if ca["kind"] == "unknown" or cb["kind"] == "unknown":
        return None, "closure unknown (trace_field_class semantics)"
    fa = ca["kind"] == "finite"
    fb = cb["kind"] == "finite"
    if rel == "equal":
        if fa and fb and len(ca["values"]) == 1 and ca["values"] == cb["values"]:
            return True, "both closures the same singleton"
        return False, "closures not equal singletons"
    if rel == "equal_mod_2":
        pa = (next(iter({v % 2 for v in ca["values"]}))
              if fa and len({v % 2 for v in ca["values"]}) == 1
              else ca["parity"])
        pb = (next(iter({v % 2 for v in cb["values"]}))
              if fb and len({v % 2 for v in cb["values"]}) == 1
              else cb["parity"])
        if pa is not None and pa == pb:
            return True, f"both closures parity-constant == {pa}"
        return False, "parity not constant-and-equal on closures"
    if rel == "divides":
        if not fb:
            # b unbounded: need every a in closure(A) to divide all integers
            if fa and ca["values"] <= {1, -1}:
                return True, "A subset of {±1} divides everything"
            return False, "B unbounded and A not subset of {±1}"
        if not fa:
            return False, "A unbounded cannot uniformly divide finite B"
        return (all(_evaluate_relation(a, b, "divides")
                    for a in ca["values"] for b in cb["values"]),
                "finite x finite direct check")
    if rel.startswith("abs_diff_le_"):
        K = int(rel.split("_")[-1])
        def bounds(cl):
            if cl["kind"] == "finite":
                return min(cl["values"]), max(cl["values"])
            if cl["kind"] == "nat_unbounded":
                return cl["lo"], None
            if cl["kind"] == "neg_unbounded":
                return None, cl["hi"]
            return None, None
        lo_a, hi_a = bounds(ca)
        lo_b, hi_b = bounds(cb)
        if hi_a is None or hi_b is None or lo_a is None or lo_b is None:
            return False, "an unbounded side breaks any interval relation"
        ok = (hi_a - lo_b <= K) and (hi_b - lo_a <= K)
        return ok, (f"interval check: max(A)-min(B)={hi_a - lo_b}, "
                    f"max(B)-min(A)={hi_b - lo_a}, K={K}")
    raise ValueError(rel)


def build_spec() -> LatticeSpec:
    knots = _load_catalog(KNOTS_DB_PATH)
    ecs = _load_catalog(BSD_RICH_DB_PATH)
    KI = ("crossing_number", "signature", "determinant", "three_genus",
          "trace_field_class", "nf_class_number")
    EI = ("rank", "conductor", "tamagawa_product", "torsion")
    side_a = {ki: [v for v in (_get_int(k, ki) for k in knots) if v is not None]
              for ki in KI}
    side_b = {ei: [v for v in (_get_int(e, ei) for e in ecs) if v is not None]
              for ei in EI}
    return LatticeSpec(side_a_name="knot", side_b_name="ec",
                       side_a=side_a, side_b=side_b,
                       operators=dict(OPERATORS),
                       relations=("equal", "equal_mod_2", "divides", "abs_diff_le_3"),
                       eval_relation=_evaluate_relation)


def main():
    spec = build_spec()
    ecs = _load_catalog(BSD_RICH_DB_PATH)
    conductors = {_get_int(e, "conductor") for e in ecs}
    gaps = {"conductor_window": [min(conductors), max(conductors)],
            "has_5077": 5077 in conductors,
            "rank_support": sorted({_get_int(e, "rank") for e in ecs}),
            "note": "5077a1 (minimal rank-3) inside window but absent: "
                    "catalog rank support is selection, not theorem"}
    print("Selection gaps:", gaps)

    print("\nMining (exact)...")
    mined = mine(spec)
    voids = mined["voids"]
    print(f"  {len(voids)} exact voids to closure-stress\n")

    rows = []
    for v in voids:
        c = v["cell"]
        cl_a = apply_op_to_closure(c["f"], POPULATION_CLOSURES[("a", c["inv_a"])])
        cl_b = apply_op_to_closure(c["g"], POPULATION_CLOSURES[("b", c["inv_b"])])
        ok, reason = rel_holds_on_closures(cl_a, cl_b, c["rel"])
        citations = [x["citation"] for x in
                     (cl_a, cl_b,
                      POPULATION_CLOSURES[("a", c["inv_a"])],
                      POPULATION_CLOSURES[("b", c["inv_b"])])
                     if x.get("citation")]
        verdict = ("THEOREM_BACKED" if ok
                   else "UNKNOWN_SEMANTICS" if ok is None
                   else "SELECTION_ARTIFACT")
        rows.append({"cell_id": v["cell_id"],
                     "triviality_class": v["triviality_class"],
                     "closure_verdict": verdict,
                     "reason": reason,
                     "citations": sorted(set(citations)) if ok else []})

    census = Counter(r["closure_verdict"] for r in rows)
    by_class = {}
    for r in rows:
        by_class.setdefault(r["triviality_class"], Counter())[r["closure_verdict"]] += 1
    print("Closure-stress census:", dict(census))
    for cls, cnt in sorted(by_class.items()):
        print(f"  {cls}: {dict(cnt)}")

    tb = [r for r in rows if r["closure_verdict"] == "THEOREM_BACKED"]
    tb_non_t1 = [r for r in tb if r["triviality_class"] != "T1_PIGEONHOLE"]
    print(f"\nTHEOREM_BACKED: {len(tb)} total, {len(tb_non_t1)} non-T1:")
    for r in tb_non_t1:
        print(f"  {r['cell_id']}")
        print(f"    reason: {r['reason']}  citations: {r['citations']}")

    pred = {f"mod_3|log2_floor|{ki}|torsion|abs_diff_le_3"
            for ki in ("crossing_number", "signature", "determinant",
                       "three_genus", "trace_field_class", "nf_class_number")}
    got = {r["cell_id"] for r in tb_non_t1}
    print(f"\nPre-registered prediction check (exactly the 6 Mazur cells):")
    print(f"  predicted-and-found: {len(pred & got)}")
    print(f"  predicted-but-missing: {sorted(pred - got)}")
    print(f"  found-but-unpredicted: {sorted(got - pred)}")

    unk = [r for r in rows if r["closure_verdict"] == "UNKNOWN_SEMANTICS"]
    print(f"\nUNKNOWN_SEMANTICS (trace_field_class): {len(unk)}")

    out = Path(__file__).parent / "a3_void_extension_stress.json"
    out.write_text(json.dumps({
        "meta": {"date": "2026-06-10", "author": "Harmonia_M2_D", "version": 2,
                 "selection_gaps": gaps,
                 "preregistered_prediction": sorted(pred),
                 "note": "closure-based; v1 finite-table was too weak "
                         "(missed rank-4/signature-16 breaks)"},
        "census": dict(census),
        "by_class": {k: dict(v) for k, v in by_class.items()},
        "prediction_check": {"predicted_and_found": sorted(pred & got),
                             "predicted_but_missing": sorted(pred - got),
                             "found_but_unpredicted": sorted(got - pred)},
        "rows": rows,
    }, indent=1), encoding="utf-8")
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
