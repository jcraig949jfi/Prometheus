#!/usr/bin/env python3
"""POST-HOC (not preregistered), written after results.json. Question: is the
negative MOD zero-shot transfer only an artefact of WL_A's magnitude (|WL| ~ 3
per pair vs inter-module |W0| = 0.05)? Re-train NI on A (identical seeds -> the
same WL as the main run), then apply c * WL_A to B0..B3 for c in a grid, and
also its inter-module-only part. Output: posthoc_scale.json."""
import json, os, statistics
from multiprocessing import Pool
import ni_adv as X

CS = (0.003, 0.01, 0.03, 0.1, 0.3, 1.0)


def job(a):
    tr = X.job_train({"fam": "MOD", "a": a, "kind": "NI"})
    WL = tr["WL"]
    tg = X.targets_for("MOD", a)
    out = {"a": a, "WL_fro": X.fro(WL), "targets": {}}
    for (tname, W0, meta) in tg[:5]:
        etag = "MOD-%d-%s" % (a, tname)
        base = X.evaluate(W0, W0, etag)[0]
        sd = statistics.pstdev(base) or 1.0
        row = {"M_noyield": statistics.mean(base), "SD0": sd, "ground": meta["ground"]}
        for c in CS:
            Weff = X.add(W0, WL, c)
            post = X.evaluate(W0, Weff, etag)[0]
            row["z_c%g" % c] = (statistics.mean(base) - statistics.mean(post)) / sd
            row["frac_ground_c%g" % c] = sum(1 for e in post if e <= meta["ground"] + 1e-9) / len(post)
        out["targets"][tname] = row
    return out


if __name__ == "__main__":
    with Pool(4) as p:
        res = p.map(job, X.A_SEEDS, chunksize=1)
    summ = {}
    for c in CS:
        zs = [r["targets"]["B%d" % k]["z_c%g" % c] for r in res for k in range(4)]
        zA = [r["targets"]["A"]["z_c%g" % c] for r in res]
        summ["c=%g" % c] = {"B_median_z": round(statistics.median(zs), 3), "B_n_pos": sum(1 for z in zs if z > 0),
                            "B_min": round(min(zs), 3), "B_max": round(max(zs), 3),
                            "A_median_z": round(statistics.median(zA), 3)}
    json.dump({"summary": summ, "runs": res}, open(os.path.join(X.HERE, "posthoc_scale.json"), "w"), indent=1)
    print(json.dumps(summ, indent=1))
