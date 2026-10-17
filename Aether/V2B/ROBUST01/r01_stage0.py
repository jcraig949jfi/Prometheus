"""ROBUST01 stage 0: reproduction and planted controls, one law per process.

    python r01_stage0.py --law contest|fold --out STAGE0_<law>.json [--backend gpu|cpu]

--law contest runs the frozen aeth01.op_xor (a REPRODUCTION check: it must give back REACH01's certificates);
--law fold installs aeth01.op_xor_fold first.
  P  the R3 planted combiner (r3_planted.planted(), R3 geometry): r3_certify certificate, position-0 table vs a ^ b,
     held-out-alphabet table, invariance check.
  T  R4 task 1 transplant of component_planted.json (6 offsets x 256 positions), written in r4_reduce's format.
  D  the first certified COMBINE candidate of every REACH01 G1 arm-C seed that found one (LADDER01 + x4), certified
     again under this law (descriptive: these were discovered under the contest law).
"""

import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fold_physics as FP  # noqa: E402

DATA = "C:/Prometheus-data/aether_reach01"
DISCOVERED = (os.path.join(DATA, "LADDER01", "search"), os.path.join(DATA, "LADDERx4", "search"))


def jsonable(c):
    return {k: ([list(x) for x in v] if k in ("Na", "Nb") else v) for k, v in c.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--law", choices=("contest", "fold"), required=True)
    ap.add_argument("--backend", default="gpu")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.law == "fold":
        FP.install()
    import r01_lib as L
    import r3_certify as C
    import r3_frontier as F
    import r3_planted
    import r4_accum as A
    res = {"schema": "aether.robust01.stage0.v1", "law": a.law,
           "semantics_id": FP.SEMANTICS_ID if a.law == "fold" else FP.CONTROL_SEMANTICS_ID}

    F.set_geom("R3")
    p = r3_planted.planted()
    out = L.table(p, a.backend)
    xor = np.array([F.IN[c // 4] ^ F.IN[c % 4] for c in range(16)], np.uint8)
    res["P"] = {"certificate": jsonable(C.certify(p, "XOR", backend=a.backend)),
                "table": [int(v) for v in out], "table_is_a_xor_b": bool(np.array_equal(out, xor)),
                "rung": L.rung(out), "distinct_outputs": L.n_distinct(out),
                "heldout_rung": L.rung(L.table(p, a.backend, L.IN_H)),
                "invariance": L.invariance_check(p)}
    print("P", json.dumps({k: v for k, v in res["P"].items() if k != "certificate"}), file=sys.stderr)

    comp, _ = A.load_component(os.path.join(FP.REACH01, "R4", "component_planted.json"))
    res["T"] = L.transplant(comp[0], comp[1], a.backend)
    print("T", res["T"], file=sys.stderr)

    F.set_geom("G1")
    res["D"] = []
    for d in DISCOVERED:
        for path in sorted(glob.glob(os.path.join(d, "G1_C_s*.json"))):
            if path.endswith("_cert.json"):
                continue
            u = json.load(open(path))
            if not u.get("combine_npz"):
                continue
            z = np.load(os.path.join(d, u["combine_npz"]))
            q = z["patches"][0]
            t = L.table(q, a.backend)
            row = {"unit": os.path.basename(path), "seed": u["seed"], "hash": str(z["hashes"][0]),
                   "certificate": jsonable(C.certify(q, "XOR", backend=a.backend)),
                   "rung": L.rung(t), "distinct_outputs": L.n_distinct(t),
                   "heldout_rung": L.rung(L.table(q, a.backend, L.IN_H)), "invariance": L.invariance_check(q)}
            ref = {c["hash"]: c for c in json.load(open(path[:-5] + "_cert.json"))["certified"]}[row["hash"]]
            row["reach01_certificate"] = {k: ref[k] for k in ("COMPOSE", "AUTONOMOUS", "position_combine_frac")}
            res["D"].append(row)
            print("D", row["unit"], {k: row["certificate"][k] for k in ("COMPOSE", "AUTONOMOUS", "position_combine_frac")},
                  file=sys.stderr)
    if a.law == "contest":
        want = json.load(open(os.path.join(HERE, "RULES.json")))["stage0"]["reproduction_contest"]["planted_certificate"]
        trans = json.load(open(os.path.join(FP.REACH01, "R4", "transplant_task1.json")))
        checks = {"P": all(res["P"]["certificate"][k] == v for k, v in want.items()),
                  "T": res["T"] == trans,
                  "D": all({k: r["certificate"][k] for k in r["reach01_certificate"]} == r["reach01_certificate"]
                           for r in res["D"])}
        res["reproduction"] = {"checks": checks, "ok": all(checks.values())}
        print("REPRODUCTION", res["reproduction"], file=sys.stderr)
    json.dump(res, open(a.out + ".partial", "w"), indent=1)
    os.replace(a.out + ".partial", a.out)
    tr = os.path.join(os.path.dirname(os.path.abspath(a.out)), "transplant_task1_%s.json" % a.law)
    json.dump(res["T"], open(tr, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
