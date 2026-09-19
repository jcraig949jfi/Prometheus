"""P-J09 [T-X20; serendipity; requires P-J02]: GEOMETRY OF CONDITIONAL MACHINERY. The P-F02 curve set (temporal
response geometry, 30 components) of the XOR-1 and XOR-15 witnesses against their plateau parents, and of
every crossed organism from P-J03 / P-J06 (if any) against its lineage's plateau tops: nearest manifold
shape and distance; whether acquiring conditional routing moves the program on the manifold. Computational
scope: integer programs on a bounded VM."""
from __future__ import annotations

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as CM            # noqa: E402
import manifold as MF          # noqa: E402
sys.path.insert(0, str(HERE.parent / "P-J02"))
from run_PJ02 import insert    # noqa: E402
A, L = CM.A, CM.L
PID, TID = "P-J09", "T-X20"


def shape(m):
    v = MF.curve(m)[0]
    if not all(x == x for x in v):
        return {"shape": "silent", "dist": None, "v": [None if x != x else round(float(x), 3) for x in v]}
    k, d = MF.nearest(v)
    return {"shape": "NEW" if d > 0.3 else MF.SHAPE[k], "cluster": k, "dist": round(float(d), 3), "v": [round(float(x), 3) for x in v]}


def main():
    t0 = time.time()
    wit = json.load(open(HERE.parent / "P-J02" / "witnesses.json", encoding="utf-8"))
    tops = json.load(open(HERE.parent / "P-I01" / "tops.json", encoding="utf-8"))
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "requires": ["P-J02"], "scope": CM.SCOPE, "claim_type": "serendipity-cross", "programs": "6 plateau genomes, their xor1 / xor15 witnesses, crossed organisms of P-J03 / P-J06 if any",
                         "readout": "nearest P-F02 shape and L1 distance; moved = shape changes or distance to the parent's curve > .3", "material_rule": "material if a witness or crossed organism changes shape relative to its parent in >= half the pairs", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    rows = []
    for w in wit:
        m0 = next(r for r in tops if r["world"] == "A" and r["control"] is None and r["seed"] == w["seed"])["tops"][w["rank"]]["m"]
        s0 = shape(m0)
        row = {"seed": w["seed"], "rank": w["rank"], "parent": s0}
        for k in ("xor1", "xor15"):
            if w[k]:
                s = shape(insert(m0, w[k]["pos"], w[k]["seq"]))
                s["moved"] = (s["shape"] != s0["shape"]) or (s["v"] and s0["v"] and all(x is not None for x in s["v"] + s0["v"]) and MF.dist(s["v"], s0["v"]) > 0.3)
                row[k] = s
        rows.append(row)
    crossed = []
    for pid in ("P-J03", "P-J06"):
        f = HERE.parent / pid / "RESULT.json"
        if f.exists():
            r = json.load(open(f, encoding="utf-8"))
            for x in r["rows"]:
                stages = x.get("stages", {}) if pid == "P-J03" else {x.get("transform"): x}
                for name, st in stages.items():
                    if st.get("crossed") and st.get("tops"):
                        crossed.append({"src": "%s|%s|%s" % (pid, x.get("chain", x.get("lineage")), name), "shape": shape(st["tops"][0]["m"])})
    pairs = [(row[k]["moved"]) for row in rows for k in ("xor1", "xor15") if k in row]
    material = bool(pairs) and sum(pairs) >= len(pairs) / 2
    summary = {"parent_shapes": [r["parent"]["shape"] for r in rows], "xor1_shapes": [r.get("xor1", {}).get("shape") for r in rows], "xor15_shapes": [r.get("xor15", {}).get("shape") for r in rows],
               "moved": {"xor1": [r.get("xor1", {}).get("moved") for r in rows], "xor15": [r.get("xor15", {}).get("moved") for r in rows]}, "crossed_organisms": crossed}
    out = {"perturbation_id": PID, "parent": TID, "summary": summary, "rows": rows, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    L.append_evidence(TID, PID, "geometry of conditional machinery: parent shapes %s; xor1 witnesses %s; xor15 witnesses %s; moved %s; crossed organisms %s" % (summary["parent_shapes"], summary["xor1_shapes"], summary["xor15_shapes"], summary["moved"], [(c["src"], c["shape"]["shape"]) for c in crossed]), material, detail=summary)
    print("DONE (%.0f s)" % (time.time() - t0), json.dumps(summary, default=CM.js)[:1200])


if __name__ == "__main__":
    main()
