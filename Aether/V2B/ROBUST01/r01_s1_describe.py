"""ROBUST01 S1, descriptive and post hoc (not part of the freeze): what do the discovered compositions compute?

    python r01_s1_describe.py --reduction REDUCTION_S1.json --fold-dir D --out S1_DESCRIBE.json [--backend cpu]

For the first COMPOSE candidate of each arm-C seed, under aeth01.op_xor_fold, this computes the position-0 output
table on the search alphabet IN and on the held-out alphabet IN_H (rows a, columns b). It then reports two
properties of each table:
  separable  f(a, b) = h1(a) ^ h2(b), i.e. XOR of two single-input features. Under the fold law, two independent
             detectors whose writes converge on the output cell produce exactly this, so the law performs the join.
  of_xor     f depends on a ^ b only.
It also reports one-sided Fisher exact p-values, fold arm C vs contest arm C, for the reducer's counts.
"""

import argparse
import json
import os
import sys
from math import comb

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fold_physics as FP  # noqa: E402


def separable(t):
    return all(t[i][j] ^ t[i][0] ^ t[0][j] ^ t[0][0] == 0 for i in range(4) for j in range(4))


def of_xor(t, al):
    m = {}
    for i in range(4):
        for j in range(4):
            if m.setdefault(al[i] ^ al[j], t[i][j]) != t[i][j]:
                return False
    return True


def fisher_one_sided(k1, k2, n):
    k = k1 + k2
    return sum(comb(n, i) * comb(n, k - i) for i in range(k1, k + 1)) / comb(2 * n, k)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reduction", required=True)
    ap.add_argument("--fold-dir", required=True)
    ap.add_argument("--backend", default="cpu")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    FP.install()
    import r01_lib as L
    import r3_frontier as F
    F.set_geom("G1")
    r = json.load(open(a.reduction))
    rows, seen = [], set()
    for c in r["candidates"]:
        if c["arm"] != "C" or not c["COMPOSE"] or c["seed"] in seen:
            continue
        seen.add(c["seed"])
        u = json.load(open(os.path.join(a.fold_dir, "G1_C_s%d.json" % c["seed"])))
        z = np.load(os.path.join(a.fold_dir, u["combine_npz"]))
        p = {str(h): z["patches"][i] for i, h in enumerate(z["hashes"])}[c["hash"]]
        t = [[int(v) for v in row] for row in L.table(p, a.backend).reshape(4, 4)]
        h = [[int(v) for v in row] for row in L.table(p, a.backend, L.IN_H).reshape(4, 4)]
        rows.append({"seed": c["seed"], "hash": c["hash"], "AUTONOMOUS": c["AUTONOMOUS"],
                     "table": t, "heldout_table": h,
                     "separable": separable(t), "of_xor": of_xor(t, F.IN),
                     "heldout_separable": separable(h), "heldout_of_xor": of_xor(h, L.IN_H),
                     "values": sorted({v for row in t for v in row}),
                     "heldout_values": sorted({v for row in h for v in row})})
        print("s%d separable %s of_xor %s | heldout separable %s of_xor %s" % (
            c["seed"], rows[-1]["separable"], rows[-1]["of_xor"], rows[-1]["heldout_separable"],
            rows[-1]["heldout_of_xor"]), file=sys.stderr)
    tab = r["table"]
    fisher = {key: fisher_one_sided(tab["fold_C_" + key]["k"], tab["contest_C_" + key]["k"], 40)
              for key in ("COMBINE", "COMPOSE", "AUTO_COMPOSE", "AUTO_ANY")}
    res = {"schema": "aether.robust01.s1.describe.v1", "post_hoc": True, "semantics_id": FP.SEMANTICS_ID,
           "alphabet": [int(x) for x in F.IN], "heldout_alphabet": [int(x) for x in L.IN_H],
           "compositions": rows, "fisher_one_sided_fold_vs_contest_armC": fisher}
    json.dump(res, open(a.out + ".partial", "w"), indent=1)
    os.replace(a.out + ".partial", a.out)
    print(json.dumps(fisher), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
