"""K2 (frame E, ring-medium): is a copy op a property of a TAPE POSITION rather than of the content?

Prediction of the medium frame: every single-sided copy op is a tape operator 'make half t a copy of
half s' (s fixed in ring coordinates). When the content carrying it sits at s it spreads; when it
sits at 1-s the SAME op imports the partner over it. Hence, per copier:
  (i)   i_(1-s*) ~= c_(s*)   (self-import at the wrong side ~ conversion at the right side)
  (ii)  m_BASE = mean over sides of (#x-like halves) ~= 1  (structurally critical)
  (iii) m_ATOMIC ~= 1 + c_(s*)/2  (ATOMIC deletes the unpromoted self-import)
  (iv)  side-0 copiers: their product at half 1 is executed IN THE SAME CALL by the victim's context;
        survival of the product to the end of the call (post/pre) ~ 1 for STATE_FREE, < 1 otherwise,
        under foreign (random) victim contexts; ~1 for both under ZERO contexts.
The hereditary framing has no identity between 'reproduction' (c) and 'erosion' (i).
Copy errors and mutation off. 128 FOR corpus competent copiers (dense VM, C-A3 cells) + 7ae3 founder.
"""
import json
import random
import time

import common as C

N = 60
OUT = C.HERE / "k2_side_symmetry.json"


def stats(r, x, ctxmode, rng):
    acc = {s: {"conv": 0, "conv_prom": 0, "imp": 0, "imp_prom": 0, "keep": 0, "m_base": 0, "m_atomic": 0,
               "pre": 0, "post_given_pre": 0} for s in (0, 1)}
    for s in (0, 1):
        for k in range(N):
            y = C.rand_genome(rng, r.L)
            sx = C.ZERO if ctxmode == "ZERO" else C.rand_ctx(rng)
            sy = C.ZERO if ctxmode == "ZERO" else C.rand_ctx(rng)
            o = C.outcome(r, x, y, s, sx, sy, 0.0, rng, snap=True)
            a = acc[s]
            for f in ("conv", "conv_prom", "imp", "imp_prom", "keep"):
                a[f] += o[f]
            a["m_base"] += o["m_base"]
            a["m_atomic"] += o["m_atomic"]
            if s == 0:   # x at side 0: was half 1 already x-like after side 0 ran?
                pre = C.FID(x, o["raw"]["after0"][1]) >= 0.9
                a["pre"] += pre
                a["post_given_pre"] += pre and o["conv"]
    return {s: {f: v / N for f, v in acc[s].items()} for s in (0, 1)}


def main():
    t0 = time.time()
    rows = json.loads((C.FOR / "core_map.json").read_text())["rows"]
    cop = [x for x in rows if x["competent"] and x["vm"] == "DENSE"]
    runners = {c: C.corpus_runner(c) for c in ("7ae3", "ffa6")}
    out = []
    for j, x in enumerate(cop):
        r = runners[x["cell"]]
        g = bytes.fromhex(x["hex"])
        rng = random.Random("K2-%d" % j)
        rec = {"cell": x["cell"], "hex": x["hex"], "state_free": x["state_free"]}
        for cm in ("ZERO", "RAND"):
            rec[cm] = stats(r, g, cm, rng)
        out.append(rec)
    # the 7ae3 founder in its own cell (stock VM)
    r7 = C.runner_for_spec(C.run_ds.DONOR)
    g7 = C.run_ds.donor_genome()
    rec = {"cell": "7ae3_own_cell_stockVM", "hex": g7.hex(), "state_free": None}
    rng = random.Random("K2-7ae3")
    for cm in ("ZERO", "RAND"):
        rec[cm] = stats(r7, g7, cm, rng)
    out.append(rec)
    OUT.write_text(json.dumps({"N": N, "rows": out, "cpu_s": round(time.time() - t0, 1)}))
    print("done", len(out), round(time.time() - t0, 1))


if __name__ == "__main__":
    main()
