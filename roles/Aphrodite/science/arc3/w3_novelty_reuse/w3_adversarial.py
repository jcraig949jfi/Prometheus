"""W3 PART 1a -- adversarial single-hole schemas scored by RULER v2 vs G1.
Forensic only; imports ruler_v2 unmodified. Single core.
Usage: python w3_adversarial.py [G4|W5]
Writes W3_ADVERSARIAL_<world>.json next to this file.
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("A17_FASTEVAL", "1")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]                       # roles/Aphrodite
sys.path.insert(0, str(ROOT / "science" / "compounding" / "rb1"))
sys.path.insert(0, str(ROOT / "engine"))
sys.path.insert(0, str(ROOT / "engine" / "accel"))
import ruler_v2 as R        # noqa: E402
import tier3d as T3D        # noqa: E402

G1 = "(acc + {H})"

# (class, schema, expected NEW_FINAL, expected relation, rationale)
CASES = [
    # (a) algebraic re-expressions of G1 -- expected NOT novel
    ("a_reexpr", "(acc - (0 - {H}))", False, "REEXPR", "double sign: acc + H"),
    ("a_reexpr", "({H} - (0 - acc))", False, "REEXPR", "H + acc via subtraction"),
    ("a_reexpr", "(0 - ((0 - acc) - {H}))", False, "REEXPR", "double negation of accumulator"),
    ("a_reexpr", "(0 - (0 - (acc + {H})))", False, "REEXPR", "double negation of G1"),
    ("a_reexpr", "((acc + {H}) + 0)", False, "EQUAL", "neutral element"),
    ("a_reexpr", "(acc + ({H} + 0))", False, "EQUAL", "neutral element inside"),
    ("a_reexpr", "(({H} + acc) - 0)", False, "EQUAL", "commuted, neutral"),
    ("a_reexpr", "((acc + {H}) - (v - v))", False, "EQUAL", "cancelling term"),
    # re-expressions of a COMPOSITION of G1 (tests the structural relation, not novelty)
    ("a_reexpr_comp", "((acc * v) + ({H} * v))", True, "COMPOSES", "distributed ((acc + H) * v)"),
    ("a_reexpr_comp", "(v - (acc - {H}))", True, "COMPOSES", "SHAM_0 = (v - (acc + H')) with H' = 0 - H"),
    ("a_reexpr_comp", "((v - acc) - {H})", True, "COMPOSES", "(v - (acc + H)) re-associated"),
    ("a_reexpr_comp", "((v - {H}) - acc)", True, "COMPOSES", "(v - (acc + H)) commuted"),
    ("a_reexpr_comp", "(0 - (acc + {H}))", True, "COMPOSES", "negated G1 (alternating fold)"),
    ("a_reexpr_comp", "((0 - acc) - {H})", True, "COMPOSES", "negated G1 distributed"),
    # (b) domain-equivalent functions: equal on the ruler GRID (acc >= 0) but not on the
    # fold's reachable domain (acc can go negative)
    ("b_domain", "(math.gcd(abs(acc), abs(0)) - {H})", True, "COMPOSES?", "|acc| - H; = acc - H only for acc >= 0"),
    ("b_domain", "(math.gcd(abs(acc), abs(0)) + {H})", True, "COMPOSES?", "|acc| + H"),
    ("b_domain", "math.gcd(abs((acc + {H})), abs(0))", True, "COMPOSES", "|acc + H|"),
    ("b_domain", "(math.gcd(abs(acc), abs(acc)) + {H})", True, "none", "|acc| + H (gcd(a,a))"),
    ("b_domain", "(pow(acc, 1) + {H})", False, "EQUAL", "pow(.,1) neutral"),
    # (c) syntactically novel but behaviourally inert additions
    ("c_inert", "((acc + {H}) * 1)", False, "EQUAL", "*1"),
    ("c_inert", "pow((acc + {H}), 1)", False, "EQUAL", "pow 1"),
    ("c_inert", "((acc + {H}) // 1)", False, "EQUAL", "//1"),
    ("c_inert", "((acc + {H}) * (v // v))", False, "COMPOSES(inert)", "* (v//v) = *1 on v != 0"),
    ("c_inert", "((acc + {H}) * pow(v, 0))", False, "COMPOSES(inert)", "* v^0"),
    ("c_inert", "((acc + {H}) + (0 * v))", False, "EQUAL", "+ 0*v"),
    ("c_inert", "((acc + {H}) * math.gcd(abs(v), abs(1)))", False, "COMPOSES(inert)", "* gcd(v,1)=1"),
    ("c_inert", "((acc + {H}) // pow(v, 0))", False, "COMPOSES(inert)", "// 1 in disguise"),
    ("c_inert", "((acc + {H}) % (v - v))", False, "junk", "mod 0 -> always error"),
    ("c_inert", "((acc + {H}) - (first - first))", False, "EQUAL", "cancel"),
    # (d) useful specialisations -- expected NOT novel, REFINES
    ("d_special", "(acc + ({H} * v))", False, "REFINES", "K5 style"),
    ("d_special", "(acc + (v % {H}))", False, "REFINES", "K5 style"),
    ("d_special", "(acc + ({H} + v))", False, "REFINES", "K5 style"),
    ("d_special", "(acc - ({H} - v))", False, "REFINES", "acc + (v - H): specialisation via subtraction"),
    ("d_special", "((acc + v) + {H})", False, "REFINES", "assoc refinement"),
    ("d_special", "(acc - ({H} * first))", False, "REFINES", "acc + (-(H*first))"),
    ("d_special", "((acc - {H}) + v)", False, "REFINES", "re-expressed + specialised"),
    # (e) compositions that plausibly enable a new task family
    ("e_compose", "(v - (acc + {H}))", True, "COMPOSES", "CON1 selected (alternating)"),
    ("e_compose", "((acc + {H}) * v)", True, "COMPOSES", "CON7 selected (weighted product-sum)"),
    ("e_compose", "((acc + {H}) * last)", True, "COMPOSES", "scaling by query"),
    ("e_compose", "math.gcd(abs(first), abs((acc + {H})))", True, "COMPOSES", "CON0 selected"),
    ("e_compose", "(first + (acc + {H}))", False, "REFINES", "CON2 selected (additive)"),
    ("e_compose", "((acc + {H}) // v)", True, "COMPOSES", "running quotient"),
    ("e_compose", "((acc + {H}) % last)", True, "COMPOSES", "modular sum"),
    # (f) abstractions whose benefit is purely efficiency (every instance already in
    # the fallback space, and in PRISTINE-style reach)
    ("f_efficiency", "(acc * {H})", True, "none", "multiplicative; PRISTINE reachable"),
    ("f_efficiency", "((acc * v) + {H})", True, "none", "affine; depth-2 reachable"),
    ("f_efficiency", "(acc + ((v * v) + {H}))", False, "REFINES", "pins a common filler"),
    ("f_efficiency", "math.gcd(abs(acc), abs({H}))", True, "none", "gcd fold"),
]


def run(world):
    if world == "W5":
        import a18
        a18.use_world("W5")
    sp = R.span_of_schema(G1)
    tsp = R.traj_span(R.reexpression_bodies(G1))
    rows = []
    for cls, s, exp_new, exp_rel, why in CASES:
        inst = T3D.instantiate(s)
        if len(inst) == 0:
            rows.append({"class": cls, "schema": s, "instantiations": 0, "note": "no in-space instantiation",
                         "expected_NEW": exp_new, "expected_rel": exp_rel, "why": why})
            continue
        v = R.verdict_full(s, G1, sp, tsp, inst)
        acc_inst = [b for b in inst if R.accumulating(b)]
        fcl = {}
        for b in acc_inst:
            fcl[R.fclass(b)] = fcl.get(R.fclass(b), 0) + 1
        # witness overlap: do the grid-novel and trajectory-novel instances coincide?
        gnov = {b for b in acc_inst if R.vec(b) not in sp and R.fclass(b) != "ADDITIVE"}
        tnov = {b for b in acc_inst if any(R.traj_nondegenerate(R.traj(b, i)) and R.traj(b, i) not in tsp
                                           for i in ("0", "1"))}
        row = {"class": cls, "schema": s, "why": why, "expected_NEW": exp_new, "expected_rel": exp_rel,
               "instantiations": len(inst), "accumulating": len(acc_inst), "fclass_counts": fcl,
               "grid_novel": v["novel"], "traj_novel": v["novel_traj"],
               "grid_and_traj_novel": len(gnov & tnov),
               "NEW_V2": v["NEW_V2"], "NEW_TRAJ": v["NEW_TRAJ"], "NEW_FINAL": v["NEW_FINAL"],
               "EQUAL": v["EQUAL"], "REFINES": v["REFINES"], "COMPOSES": v["COMPOSES"],
               "examples": v["novel_examples"][:3], "traj_examples": v["novel_traj_examples"][:3]}
        got = row["NEW_FINAL"]
        row["novelty_error"] = ("OK" if got == exp_new else ("FALSE_POSITIVE" if got else "FALSE_NEGATIVE"))
        rows.append(row)
        print("%-14s %-44s acc=%3d g=%3d t=%3d both=%3d NEW=%-5s exp=%-5s %-14s EQ=%d RF=%d CO=%d" % (
            cls, s, row["accumulating"], row["grid_novel"], row["traj_novel"], row["grid_and_traj_novel"],
            got, exp_new, row["novelty_error"], v["EQUAL"], v["REFINES"], v["COMPOSES"]), flush=True)
    (HERE / ("W3_ADVERSARIAL_%s.json" % world)).write_text(json.dumps(rows, indent=1, default=str))


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "G4")
