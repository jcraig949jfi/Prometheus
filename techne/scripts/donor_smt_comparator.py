"""cvc5 vs the incumbent z3: what, mechanically, does the new donor add? Techne Gen-0.

    python -m techne.scripts.donor_smt_comparator --out techne/donor_smt_comparison_2026-08-31.json

z3 5.0.0.0 was already installed and already serves `techne/lib/sat_solver.py`. A second SMT
solver has to justify itself against that incumbent, and REDUNDANT_AT_GEN0 is an acceptable --
indeed a useful -- verdict. An arsenal that records "we already had this" is smaller and truer
than one that keeps a donor because installing it succeeded.

WHAT IS COMPARED. Only Gen-0 capability: decide a conjunction of linear integer constraints and
return a model. Both solvers are run on identical problems, and the comparison is on
AGREEMENT OF VERDICT, not on which model is returned.

WHY MODELS ARE NOT COMPARED FOR EQUALITY. A satisfiable constraint system generally has many
models. Two solvers returning different witnesses is not a disagreement -- it is two arbitrary
choices from the same solution set. Requiring identical models would manufacture a difference
out of nothing, so each returned model is instead CHECKED against the constraints it claims to
satisfy. A solver that returns a model violating its own constraints is a real defect; a solver
that returns a different valid model is not.

WHAT THIS DOES NOT MEASURE. Timing (a handful of tiny QF_LIA problems measures process startup,
not solver performance), theories neither is exercised on, and cvc5's SyGuS front end -- which
is a different capability class and has no Gen-0 consumer.
"""
from __future__ import annotations

import argparse
import json
import pathlib

#: (name, vars, constraints, expected) -- expected is 'sat' or 'unsat', known by hand so a
#: shared wrong answer cannot pass as agreement.
PROBLEMS = [
    ("simple_sat", ["x", "y"],
     [({"x": 1, "y": -1}, ">", 0), ({"x": 1, "y": 1}, "==", 10)], "sat"),
    ("contradiction", ["x"],
     [({"x": 1}, ">", 5), ({"x": 1}, "<", 3)], "unsat"),
    ("equality_chain", ["a", "b", "c"],
     [({"a": 1, "b": -1}, "==", 0), ({"b": 1, "c": -1}, "==", 0), ({"a": 1}, "==", 7)], "sat"),
    ("disequality", ["p", "q"],
     [({"p": 1, "q": -1}, "!=", 0), ({"p": 1}, "==", 4), ({"q": 1}, "==", 4)], "unsat"),
    ("bounded_box", ["u", "v"],
     [({"u": 1}, ">=", 0), ({"u": 1}, "<=", 3), ({"v": 1}, ">=", 0), ({"v": 1}, "<=", 3),
      ({"u": 2, "v": 3}, "==", 12)], "sat"),
    ("negative_coeffs", ["m", "n"],
     [({"m": -2, "n": 5}, "==", 1), ({"m": 1}, ">=", 1), ({"n": 1}, ">=", 1)], "sat"),
]


def _check_model(model, constraints) -> bool:
    """Verify a returned model against the constraints it claims to satisfy."""
    if model is None:
        return False
    ops = {"==": lambda a, b: a == b, "!=": lambda a, b: a != b,
           "<": lambda a, b: a < b, "<=": lambda a, b: a <= b,
           ">": lambda a, b: a > b, ">=": lambda a, b: a >= b}
    for lhs, op, rhs in constraints:
        val = sum(int(c) * int(model[n]) for n, c in lhs.items())
        if not ops[op](val, int(rhs)):
            return False
    return True


def solve_cvc5(names, constraints) -> dict:
    from techne.lib.donors import get
    art = get("cvc5").propose("check_int_constraints",
                              {"vars": names, "constraints": constraints})
    return {"result": art.payload["result"], "model": art.payload["model"]}


def solve_z3(names, constraints) -> dict:
    import z3
    sym = {n: z3.Int(n) for n in names}
    s = z3.Solver()
    for lhs, op, rhs in constraints:
        expr = z3.IntVal(0)
        for n, c in lhs.items():
            expr = expr + int(c) * sym[n]
        s.add({"==": expr == int(rhs), "!=": expr != int(rhs), "<": expr < int(rhs),
               "<=": expr <= int(rhs), ">": expr > int(rhs), ">=": expr >= int(rhs)}[op])
    r = s.check()
    if r == z3.sat:
        m = s.model()
        return {"result": "sat", "model": {n: m[sym[n]].as_long() for n in names}}
    return {"result": "unsat" if r == z3.unsat else "unknown", "model": None}


def run() -> dict:
    rows = []
    for name, names, cons, expected in PROBLEMS:
        row = {"problem": name, "expected": expected}
        for label, fn in (("cvc5", solve_cvc5), ("z3", solve_z3)):
            try:
                got = fn(names, cons)
                row[label] = got["result"]
                row[label + "_correct_verdict"] = (got["result"] == expected)
                if got["result"] == "sat":
                    row[label + "_model_valid"] = _check_model(got["model"], cons)
            except Exception as e:                                    # noqa: BLE001
                row[label + "_error"] = type(e).__name__ + ": " + str(e)
        row["VERDICTS_AGREE"] = row.get("cvc5") == row.get("z3")
        rows.append(row)

    agree = sum(1 for r in rows if r["VERDICTS_AGREE"])
    cvc5_ok = sum(1 for r in rows if r.get("cvc5_correct_verdict"))
    z3_ok = sum(1 for r in rows if r.get("z3_correct_verdict"))
    models_ok = all(r.get(k, True) for r in rows for k in ("cvc5_model_valid", "z3_model_valid"))

    if agree == len(rows) and cvc5_ok == z3_ok == len(rows) and models_ok:
        verdict = "REDUNDANT_AT_GEN0"
        rationale = (
            "On every Gen-0 capability exercised -- QF_LIA decision plus model extraction -- "
            "cvc5 and the already-installed z3 agree on all " + str(len(rows)) + " problems, "
            "both reach the hand-known verdict, and every returned model satisfies its own "
            "constraints. There is no Gen-0 capability cvc5 supplies that z3 does not. It is "
            "retained as VETTED and WRAPPED but NOT promoted to a dependency: the capabilities "
            "that could differentiate it (finite-field, sequence, bag and separation-logic "
            "theories; the SyGuS synthesis front end) have no consumer yet, and acquiring a "
            "second solver for capabilities nothing calls is how an arsenal accumulates weight "
            "without function.")
    elif agree < len(rows):
        verdict = "SOLVERS_DISAGREE"
        rationale = ("The two solvers returned different verdicts on at least one problem. "
                     "That is a defect in one of them and must be resolved before either is "
                     "used as an adversary instrument.")
    else:
        verdict = "INCONCLUSIVE"
        rationale = "At least one solver failed to produce a comparable reading."

    return {
        "generated": "2026-08-31",
        "question": "what Gen-0 capability, if any, does cvc5 expose that installed z3 does not?",
        "z3_version": _z3_version(),
        "cvc5_version": _cvc5_version(),
        "problems": len(rows),
        "verdicts_agree": agree,
        "cvc5_correct": cvc5_ok,
        "z3_correct": z3_ok,
        "all_returned_models_valid": models_ok,
        "rows": rows,
        "VERDICT": verdict,
        "rationale": rationale,
        "not_measured": [
            "wall-clock performance (these problems measure process startup, not solving)",
            "theories exercised by neither solver here",
            "cvc5 SyGuS synthesis -- a different capability class with no Gen-0 consumer",
        ],
    }


def _z3_version() -> str:
    try:
        import importlib.metadata as md
        return md.version("z3-solver")
    except Exception:                                                 # noqa: BLE001
        return "unknown"


def _cvc5_version() -> str:
    try:
        import importlib.metadata as md
        return md.version("cvc5")
    except Exception:                                                 # noqa: BLE001
        return "unknown"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="techne/donor_smt_comparison_2026-08-31.json")
    a = ap.parse_args()
    rep = run()
    for r in rep["rows"]:
        print("{:16s} expect={:6s} cvc5={:8s} z3={:8s} agree={}".format(
            r["problem"], r["expected"], str(r.get("cvc5", r.get("cvc5_error", "-")))[:8],
            str(r.get("z3", r.get("z3_error", "-")))[:8], r["VERDICTS_AGREE"]))
    print("\nVERDICT:", rep["VERDICT"])
    dest = pathlib.Path(a.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(rep, indent=2), encoding="utf-8")
    print("wrote", dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
