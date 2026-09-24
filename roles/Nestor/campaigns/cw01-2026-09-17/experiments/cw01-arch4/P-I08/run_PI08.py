"""P-I08 [T-ARCH4/W1 x T-X17 x T-X21, serendipity; requires P-I01]: GEOMETRY CENSUS of the P-I01 tops -
full curve set, nearest known shape, shapes outside the manifold reported raw with genomes; shape
shares per world; whether crossing coincides with a geometry. Computational scope: integer programs
on a bounded VM.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time
from collections import Counter

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as CM            # noqa: E402
import manifold as MF          # noqa: E402
import ctxevo as CE            # noqa: E402
A, L = CM.A, CM.L

PID, TID = "P-I08", "T-ARCH4/W1"


def job(j):
    v = MF.curve(j["m"])[0]
    ok = all(x == x for x in v)
    k, d = MF.nearest(v) if ok else (None, None)
    return {"world": j["world"], "seed": j["seed"], "control": j["control"], "rank": j["rank"], "held": j["held"], "vector": v, "nearest": (MF.SHAPE[k] if ok else "silent"), "d": d, "new": bool(ok and d > 0.3), "n_instr": CM.n_instr(j["m"]), "persist": j["m"]["persist"]}


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "co_parents": ["T-X17", "T-X21"], "requires": ["P-I01"], "scope": CM.SCOPE, "claim_type": "serendipity-census",
                         "programs": "P-I01 tops (every run, top-16)", "new": "> .3 from every P-F02 centroid", "readouts": "shape shares per world / control; crossing vs shape; NEW vectors reported raw with genomes",
                         "material_rule": "any NEW shape with >= 4 members, or crossing coincides with one shape (>= 80 percent of crossed tops in one shape)", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    runs = json.loads((HERE.parent / "P-I01" / "tops.json").read_text(encoding="utf-8"))
    jobs = [{"m": t["m"], "world": r["world"], "seed": r["seed"], "control": r["control"], "rank": i, "held": t["held"]} for r in runs for i, t in enumerate(r["tops"][:16])]
    with A.pool(8) as ex:
        rows = list(ex.map(job, jobs))
    shares = {}
    for w in "ABC":
        for c in (None, "destroyed"):
            rs = [r for r in rows if r["world"] == w and r["control"] == c]
            if rs:
                shares["%s|%s" % (w, c or "plain")] = dict(Counter(r["nearest"] if not r["new"] else "NEW" for r in rs))
    crossed = [r for r in rows if r["control"] is None and r["held"] >= CE.THRESH[r["world"]]]
    cshape = Counter(r["nearest"] if not r["new"] else "NEW" for r in crossed)
    coincide = bool(crossed and cshape.most_common(1)[0][1] >= 0.8 * len(crossed))
    new = [r for r in rows if r["new"]]
    newc = {}
    if len(new) >= 4:
        X = np.array([r["vector"] for r in new], float)
        cen = X.mean(axis=0)
        newc = {"n": len(new), "centroid": {k: round(float(x), 3) for k, x in zip(MF.KEYS, cen)}, "spread": float(np.mean([MF.dist(v, cen) for v in X])), "worlds": dict(Counter(r["world"] for r in new))}
    material = bool(len(new) >= 4 or coincide)
    out = {"perturbation_id": PID, "parent": TID, "shares": shares, "crossed_shapes": dict(cshape), "crossing_coincides_with_shape": coincide, "n_new": len(new), "new_cluster": newc, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "rows.json").write_text(json.dumps([dict(r, m=jobs[i]["m"]) for i, r in enumerate(rows)], ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "geometry census of context-evolved tops: shares %s; crossed tops' shapes %s (coincide %s); NEW %d %s" % (shares, dict(cshape), coincide, len(new), {k: v for k, v in newc.items() if k != "centroid"}), material, detail={"shares": shares, "new": newc})
    L.append_evidence("T-X17", PID, "cross: shapes of context-evolved organisms %s" % shares, material)
    print("DONE material=%s (%.0f s) %s crossed %s new %d" % (material, time.time() - t0, shares, dict(cshape), len(new)))


if __name__ == "__main__":
    main()
