"""TOY KNOWN-POSITIVE SENSITIVITY TEST -- INSTRUMENT CALIBRATION, NOT DISCOVERY.

A hand-built depth-2 toy task. The level-1 mechanism and the level-2 witness are PLANTED by the experimenter; nothing
here is learned or discovered. The only question is whether the TFS-1 enumerator is SENSITIVE to a correct promoted
level-1 primitive: with it, the depth-2 witness is reached within a budget at which enumeration without it (and with
a wrong, same-shape SHAM primitive) is not.

  level-1 (planted)    P1 := (lam x (add (mul x x) 1))                       v -> v^2 + 1
  level-2 task         y = sum_i P1(P1(xs_i))
  witness (promoted)   (sum (map (lam x (L_P1 (L_P1 x))) xs))                  size 6
  shortest base form we know  (sum (map (lam x (add (pow (add (mul x x) 1) 2) 1)) xs))   size 12
  SHAM (wrong level-1) (lam x (add (mul x x) 2))

Arms (identical task, dev/test, CRN seeds, budget): PRISTINE (no library), PROMOTED (P1), SHAM (P1'), and
PROMOTED+SHAM (both entries; the library-size control). Hitting cost = search charges until the first candidate that
is correct on all 8 dev AND all 32 test examples. Run:  python -m tfs1.toy_calibration  (from beta04/)
"""
import json
import os
import random
import sys
import time
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
from tfs1 import core as C                      # noqa: E402
from tfs1.enum import Enumerator, make_verifier  # noqa: E402
from tfs1.library import Library                # noqa: E402
from tfs1.membrane import flip_test, code_hashes  # noqa: E402
from tfs1.mutate import mutation_search         # noqa: E402

HERE = Path(__file__).resolve().parent
LABEL = "INSTRUMENT CALIBRATION (planted level-1 primitive and planted depth-2 witness); NOT DISCOVERY"


def task():
    f = lambda l: sum((((v * v + 1) ** 2) + 1) for v in l)     # noqa: E731
    rd, rt = random.Random(2026101001), random.Random(2026101002)

    def ins(r, k, seen):
        out = []
        while len(out) < k:
            l = [r.randint(-4, 9) for _ in range(r.randint(1, 6))]
            if tuple(l) not in seen:
                seen.add(tuple(l))
                out.append(l)
        return out
    seen = set()
    dev = [[i, f(i)] for i in ins(rd, 8, seen)]
    test = [[i, f(i)] for i in ins(rt, 32, seen)]
    return {"family_id": "TOY-D2-calibration", "output_type": "Int", "dev": dev, "test": test,
            "provenance": LABEL}


def libraries():
    p1 = Library()
    a, _ = p1.promote_lambda(C.parse("(lam x (add (mul x x) 1))"), {"planted": "P1 level-1 (calibration)"})
    sham = Library()
    s, _ = sham.promote_lambda(C.parse("(lam x (add (mul x x) 2))"), {"planted": "SHAM level-1 (calibration)"})
    both = Library.from_json({"format": p1.to_json()["format"], "contract": C.CONTRACT,
                              "entries": p1.records() + sham.records()})
    return {"PRISTINE": None, "PROMOTED": p1, "SHAM": sham, "PROMOTED+SHAM": both}, a.id


def main(seeds=range(8), budget=200_000, pristine_deep_budget=None, deep_size=8):
    T = task()
    libs, p1_id = libraries()
    out = {"label": LABEL, "task": {"family_id": T["family_id"], "dev_n": len(T["dev"]), "test_n": len(T["test"])},
           "witness_promoted": "(sum (map (lam x (%s (%s x))) xs))" % (p1_id, p1_id),
           "witness_base_known": "(sum (map (lam x (add (pow (add (mul x x) 1) 2) 1)) xs))",
           "budget": budget, "arms": {}, "code_sha256": code_hashes()}
    wit = C.parse(out["witness_promoted"])
    lib = libs["PROMOTED"]
    check = all(C.same_value(C.evaluate(wit, i, lib)[0], o) for i, o in T["dev"] + T["test"])
    out["witness_checks_on_dev_and_test"] = check
    out["witness_sizes"] = {"promoted_form": C.size(wit), "expanded": C.size(lib.expand(wit)),
                            "known_base": C.size(C.parse(out["witness_base_known"]))}
    for arm, L in libs.items():
        E = Enumerator(L)
        rows = []
        for sd in seeds:
            t0 = time.perf_counter()
            r = E.search(T["dev"], "Int", sd, T["family_id"], budget, max_size=12, verify=make_verifier(T["test"], L))
            rows.append({"seed": sd, "hit": r["hit"], "hit_charge": r["hit_charge"], "program": r["program"],
                         "charges": r["charges"], "false_hits": len(r["false_hits"]),
                         "units_expanded": r["units_expanded"], "units_promoted": r["units_promoted"],
                         "complete_through_size": r["complete_through_size"],
                         "cpu_s": round(time.perf_counter() - t0, 2)})
        static = {"rank_of_witness_seed0": E.rank_of(wit, "Int", 0, T["family_id"]) if arm in
                  ("PROMOTED", "PROMOTED+SHAM") else None,
                  "class_sizes_Int_1_to_8": [E.count("Int", (), n) for n in range(1, 9)],
                  "cumulative_through_6": E.cumulative("Int", 6)}
        out["arms"][arm] = {"rows": rows, "hits": sum(r["hit"] for r in rows), "static": static}
        print(arm, [(r["seed"], r["hit_charge"]) for r in rows], flush=True)
    # paired CRN contrast PROMOTED vs PRISTINE, censored at budget
    cost = lambda arm: [r["hit_charge"] if r["hit"] else budget for r in out["arms"][arm]["rows"]]   # noqa: E731
    out["paired_PROMOTED_vs_PRISTINE"] = flip_test([a - b for a, b in zip(cost("PRISTINE"), cost("PROMOTED"))])
    out["paired_PROMOTED_vs_SHAM"] = flip_test([a - b for a, b in zip(cost("SHAM"), cost("PROMOTED"))])
    # deep pristine run: exhaustive through `deep_size` (one seed) to state what pristine cannot reach
    if pristine_deep_budget is not None:
        E = Enumerator(None)
        b = E.cumulative("Int", deep_size) if pristine_deep_budget == "exhaustive" else pristine_deep_budget
        t0 = time.perf_counter()
        r = E.search(T["dev"], "Int", 0, T["family_id"], b, max_size=deep_size, verify=make_verifier(T["test"]))
        out["pristine_deep"] = {"budget": b, "hit": r["hit"], "hit_charge": r["hit_charge"], "program": r["program"],
                                "charges": r["charges"], "dev_consistent_but_test_wrong": len(r["false_hits"]),
                                "complete_through_size": r["complete_through_size"],
                                "cpu_s": round(time.perf_counter() - t0, 1)}
        print("pristine deep", out["pristine_deep"], flush=True)
    # secondary: the stochastic mutator (start (sum xs), fixed archive), same budget per seed
    mut = {}
    for arm in ("PRISTINE", "PROMOTED", "SHAM"):
        L = libs[arm]
        E = Enumerator(L)
        rows = []
        for sd in seeds:
            r = mutation_search(T["dev"], "Int", ["(sum (map (lam x x) xs))"], 50_000, sd, T["family_id"], E,
                                policy="random", full_outputs=False, verify=make_verifier(T["test"], L))
            rows.append({"seed": sd, "hit": r["hit"], "hit_charge": r["hit_charge"], "program": r["program"]})
        mut[arm] = {"hits": sum(r["hit"] for r in rows), "rows": rows}
        print("mutation", arm, [(r["seed"], r["hit_charge"]) for r in rows], flush=True)
    out["mutation_secondary"] = {"budget_per_seed": 50_000, "start": "(sum (map (lam x x) xs))",
                                 "policy": "random archive (every evaluated child appended)", "arms": mut}
    return out


if __name__ == "__main__":
    deep = "exhaustive" if "--deep" in sys.argv else None
    res = main(pristine_deep_budget=deep)
    (HERE / "TOY_CALIBRATION_RESULT.json").write_text(json.dumps(res, indent=1, sort_keys=True))
    print("written", HERE / "TOY_CALIBRATION_RESULT.json")
