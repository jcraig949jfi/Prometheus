"""X4 (PLAN.md): does an emission cost select presence (fire) codes over
content codes? HOLD at M2's physics and env; arms A0 (as M2) and A1 (economy:
e_income=2, c_emit=1 per copy x fanout 8 = 8 per emission, e_max=64, i.e. at
most ~1 emission per 4 ticks). Deviation logged: PLAN's "c_emit=4 per copy"
contradicted its own "~1 per 4 ticks"; the stated rate is kept.

usage: python x4_evolve.py <arm A0|A1> <seed k> <device cpu|cuda> [reduced]
Writes out/x4_<arm>_<k>[_reduced].json with champion, held acc, X1 shares
and the X5 content-null / S-CT swaps of the champion.
"""
import dataclasses
import json
import pathlib
import sys
import time

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import wc_probe as P  # noqa: E402
import wc_probe2 as P2  # noqa: E402
from prometheus.ananke import c1b_run, lens, search  # noqa: E402
from prometheus.ananke.rng import H_int  # noqa: E402

ARMS = {"A0": {}, "A1": {"e_income": 2, "c_emit": 1, "e_max": 64}}


def main(arm, k, dev, reduced):
    P.DEV = dev
    P2.P.DEV = dev
    ph, env, _, row = c1b_run.load("4ab2ba014aac967e")
    ph = ph.replace(**ARMS[arm])
    sp = search.SearchSpec(**{kk: v for kk, v in row["search"].items()
                              if kk in {f.name for f in dataclasses.fields(search.SearchSpec)}})
    if reduced:
        sp = dataclasses.replace(sp, pop=24, gens=10, M_final=8, M_held=32)
    t = time.time()
    ev = search.evolve(ph, env, H_int(P.NS, 0x4, k), sp, device=dev)
    g = np.asarray(ev["champion"], dtype=np.int64)
    out = {"arm": arm, "k": k, "reduced": reduced, "physics": ph.to_dict(), "spec": sp.to_dict(),
           "held": ev["held"], "champion": ev["champion"], "evolve_wall_s": time.time() - t,
           "x1": P.x1(ph, env, g), "x1b": P2.x1b(ph, env, g), "x5": P2.x5(ph, env, g)}
    seeds = P.assays.world_seeds(P.NS, 64)
    ticks = P.swap_ticks(env)
    base = lens.run(ph, g, env, seeds, device=dev)
    nrm = lens.trial_acc(base, range(env.trials))
    for an, fn in {"inflight": lambda w: lens.swap(w, lens.FLIGHT_ARRAYS),
                   "sitestate": lambda w: lens.swap(w, lens.SITE_ARRAYS),
                   "payload": lambda w: lens.swap(w, ["Msum"]),
                   "counts": lambda w: lens.swap(w, ["Mcnt"])}.items():
        r = lens.run(ph, g, env, seeds, hooks={tt: fn for tt in ticks}, device=dev)
        pr = lens.trial_acc(r, range(env.trials))
        out[an] = {"acc": lens.ci(pr), "verdict": lens.swap_verdict(nrm, pr)}
    name = f"x4_{arm}_{k}{'_reduced' if reduced else ''}.json"
    (P.OUT / name).write_text(json.dumps(out, indent=1, default=float))
    print(name, out["held"]["acc"], out["held"]["lo99"], "fire", out["x1"]["fire_share"],
          "pres", out["x1"]["presence_share"], "x5", out["x5"]["verdict"],
          {a: out[a]["verdict"] for a in ("inflight", "sitestate", "payload", "counts")},
          "wall", round(out["evolve_wall_s"]), flush=True)


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]), sys.argv[3], len(sys.argv) > 4 and sys.argv[4] == "reduced")
