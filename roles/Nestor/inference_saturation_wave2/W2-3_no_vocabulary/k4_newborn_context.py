"""K4 (frame C, dynamical/context map): what context does newly written content first run in?

Code fact (world.py:799-812): side 0 runs, THEN side 1 runs on the same ring. If the writer sits at
side 0, the half it writes (half 1) is executed in the same call by the overwritten site's context.
So that site's context at its next call is G_x(c_victim): one step of x's OWN context map applied to
the victim's leftovers. If the writer sits at side 1, the overwritten half 0 already ran (its old
content) before being overwritten, so the next context is G_old(c_victim): noise from x's viewpoint.
Prediction (frame C): for side-0 writers, conversion by the newly written site (kappa_new) differs
from conversion from a random context (kappa_R); for side-1 writers kappa_new ~= kappa_R.
U-W7's reading ('the newborn runs in noise') is then right only for side-1 writers.
Copy errors and mutation off. Corpus copiers from FOR core_map.json (dense VM) + 7ae3 (own cell).
"""
import json
import random
import statistics as st
import time

import common as C

N = 60


def side_of(rec):
    s = rec["ZERO"]
    return 0 if s["0"]["conv"] >= s["1"]["conv"] else 1


def measure(r, x, s, rng):
    kR = kN = nb = 0
    zero_like = 0
    for _ in range(N):
        y = C.rand_genome(rng, r.L)
        o = C.outcome(r, x, y, s, C.rand_ctx(rng), C.rand_ctx(rng), 0.0, rng)
        kR += o["conv"]
    tries = 0
    while nb < N and tries < 6 * N:
        tries += 1
        y = C.rand_genome(rng, r.L)
        o = C.outcome(r, x, y, s, C.rand_ctx(rng), C.rand_ctx(rng), 0.0, rng)   # birth call
        if not o["conv_prom"]:
            continue
        nb += 1
        child, cctx = o["ny"], o["cy"]           # overwritten site: new content, its post-call context
        z = C.rand_genome(rng, r.L)
        o2 = C.outcome(r, child, z, s, cctx, C.rand_ctx(rng), 0.0, rng)
        kN += FIDX(x, o2)
    return kR / N, (kN / nb if nb else None), nb


def FIDX(x, o2):
    return C.FID(x, o2["ny"]) >= 0.9


def main():
    t0 = time.time()
    k2 = json.loads((C.HERE / "k2_side_symmetry.json").read_text())["rows"]
    runners = {c: C.corpus_runner(c) for c in ("7ae3", "ffa6")}
    rows = []
    for j, rec in enumerate(k2[:-1]):
        r = runners[rec["cell"]]
        x = bytes.fromhex(rec["hex"])
        s = side_of(rec)
        kR, kN, nb = measure(r, x, s, random.Random("K4-%d" % j))
        rows.append({"cell": rec["cell"], "side": s, "state_free": rec["state_free"], "kR": kR, "kN": kN, "nb": nb})
    r7 = C.runner_for_spec(C.run_ds.DONOR)
    kR, kN, nb = measure(r7, C.run_ds.donor_genome(), 1, random.Random("K4-7ae3"))
    out = {"rows": rows, "7ae3_own_cell_side1": {"kR": kR, "kN": kN, "nb": nb}}
    summ = {}
    for s in (0, 1):
        for sf in (True, False):
            rs = [q for q in rows if q["side"] == s and q["state_free"] == sf and q["kN"] is not None]
            if not rs:
                continue
            d = [q["kN"] - q["kR"] for q in rs]
            summ["side%d_statefree=%s" % (s, sf)] = {
                "n": len(rs), "kR_mean": round(st.mean(q["kR"] for q in rs), 3),
                "kN_mean": round(st.mean(q["kN"] for q in rs), 3), "diff_median": round(st.median(d), 3),
                "n_kN_gt_kR_by_0.2": sum(v > 0.2 for v in d), "n_kN_lt_kR_by_0.2": sum(v < -0.2 for v in d)}
    out["summary"] = summ
    out["cpu_s"] = round(time.time() - t0, 1)
    (C.HERE / "k4_newborn_context.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({"summary": summ, "7ae3": out["7ae3_own_cell_side1"], "cpu": out["cpu_s"]}, indent=1))


if __name__ == "__main__":
    main()
