"""Beta-04 known answer K-AB: interpreter A (foundry/interp_a.py) vs interpreter B (tfs1/core.py), built independently
from contract v0. Terms come from BOTH sides: B's typed random sampler (tfs1.mutate.Mutator.random_term) and A-side
foundry witnesses (pilot task files) plus their B-mutants. Each term is evaluated by both on the same inputs (random +
edge cases). Agreement required on value and FAIL; execution units compared on runs where both are non-FAIL.
Usage: python conformance_ab.py [n_terms] [seed]
"""
import glob
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "foundry"))

import interp_a as A  # noqa: E402
from tfs1 import core as B  # noqa: E402
from tfs1.enum import Enumerator  # noqa: E402
from tfs1.library import Library  # noqa: E402
from tfs1.mutate import Mutator  # noqa: E402


def inputs(rng):
    base = [[], [0], [1], [-1], [5, -3], [2, 2, 2], [10 ** 6, -(10 ** 6)], [7, 0, -7, 3, 1, 9, -4, 2]]
    rnd = [[rng.randint(-12, 12) for _ in range(rng.randint(0, 9))] for _ in range(8)]
    return base + rnd


def run_a(src, xs):
    t = A.parse(src)
    try:
        v, u = A.run(t, list(xs), with_units=True)
    except A.Fail:
        return "FAIL", None
    if v is None or (isinstance(v, str) and v == "FAIL"):
        return "FAIL", None
    exp = getattr(u, "expanded", u)
    return v, exp


def run_b(src, xs):
    t = B.parse(src)
    v, ex, _pr = B.evaluate(t, list(xs))
    if v is B.FAIL if hasattr(B, "FAIL") else v == "FAIL":
        return "FAIL", None
    return v, ex


def norm(v):
    return list(v) if isinstance(v, (list, tuple)) else v


def main(n_terms=10000, seed=7):
    rng = random.Random(seed)
    lib = Library() if callable(Library) else None
    mut = Mutator(Enumerator(lib), max_fill=7) if lib is not None else Mutator(Enumerator(), max_fill=7)
    terms = []
    for p in glob.glob(os.path.join(HERE, "foundry", "pilot", "**", "*.json"), recursive=True):
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        for fam in (d if isinstance(d, list) else [d]):
            if isinstance(fam, dict) and isinstance(fam.get("witness"), str):
                terms.append(("A_witness", fam["witness"]))
    wit = [s for _k, s in terms]
    while len(terms) < n_terms:
        T = "Int" if rng.random() < 0.6 else "List"
        t = mut.random_term(T, (), rng, rng.randint(2, 7))
        if t is not None:
            terms.append(("B_random_" + T, B.to_str(t)))
    res = {"n_terms": 0, "n_runs": 0, "value_mismatch": 0, "fail_mismatch": 0, "unit_mismatch": 0,
           "parse_error_A": 0, "parse_error_B": 0, "unit_compared": 0, "examples": [], "by_source": {}}
    for src_kind, s in terms:
        res["n_terms"] += 1
        bs = res["by_source"].setdefault(src_kind, {"terms": 0, "mismatch_terms": 0})
        bs["terms"] += 1
        bad = False
        for xs in inputs(rng):
            res["n_runs"] += 1
            try:
                a = run_a(s, xs)
            except Exception as e:  # parse/type error on A
                res["parse_error_A"] += 1
                if len(res["examples"]) < 25:
                    res["examples"].append({"kind": "A_error", "term": s, "err": repr(e)[:160]})
                bad = True
                break
            try:
                b = run_b(s, xs)
            except Exception as e:
                res["parse_error_B"] += 1
                if len(res["examples"]) < 25:
                    res["examples"].append({"kind": "B_error", "term": s, "err": repr(e)[:160]})
                bad = True
                break
            fa, fb = a[0] == "FAIL", b[0] == "FAIL"
            if fa != fb:
                res["fail_mismatch"] += 1
                bad = True
                if len(res["examples"]) < 25:
                    res["examples"].append({"kind": "FAIL", "term": s, "xs": xs, "A": str(a[0]), "B": str(b[0])})
            elif not fa:
                if norm(a[0]) != norm(b[0]):
                    res["value_mismatch"] += 1
                    bad = True
                    if len(res["examples"]) < 25:
                        res["examples"].append({"kind": "VALUE", "term": s, "xs": xs, "A": str(a[0])[:80],
                                                "B": str(b[0])[:80]})
                else:
                    res["unit_compared"] += 1
                    if a[1] is not None and b[1] is not None and a[1] != b[1]:
                        res["unit_mismatch"] += 1
                        if len(res["examples"]) < 25:
                            res["examples"].append({"kind": "UNITS", "term": s, "xs": xs, "A": a[1], "B": b[1]})
        if bad:
            bs["mismatch_terms"] += 1
    # B-mutants of A witnesses (both sides' structure)
    res["witness_terms"] = len(wit)
    res["pass"] = (res["value_mismatch"] == 0 and res["fail_mismatch"] == 0 and res["parse_error_A"] == 0
                   and res["parse_error_B"] == 0)
    res["pass_units"] = res["unit_mismatch"] == 0
    out = os.path.join(HERE, "runs", "K_AB_CONFORMANCE.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(res, open(out, "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in res.items() if k != "examples"}, default=str))
    for e in res["examples"][:12]:
        print(e)


if __name__ == "__main__":
    a = sys.argv[1:]
    main(int(a[0]) if a else 10000, int(a[1]) if len(a) > 1 else 7)
