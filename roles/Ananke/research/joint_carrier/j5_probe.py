"""J5 (addendum in PLAN.md, committed first): localize the necessary site state and map erase curves."""
import json
import pathlib
import sys

import numpy as np
import torch

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
import j_probe as J  # noqa: E402
from prometheus.ananke import assays, lens  # noqa: E402

torch.set_num_threads(2)
SEEDS = assays.world_seeds(0x5E8, 64)


def erase_S_mask(which):
    def f(w):
        a = w.read_idx[:, 0]
        sens = w.sch_idx                         # [B, K] sensor sites
        m = torch.zeros(w.B, w.N, dtype=torch.bool)
        bi = torch.arange(w.B)
        if which == "actuator":
            m[bi, a] = True
        elif which == "sensors":
            m.scatter_(1, sens, True)
        elif which == "others":
            m[:] = True
            m[bi, a] = False
            m.scatter_(1, sens, False)
        w.S.masked_fill_(m[..., None], 0)
    return f


def run(fn, ticks):
    tr = lens.run(J.PH, J.G, J.ENV, SEEDS, hooks={t: fn for t in ticks}, device="cpu")
    return lens.trial_acc(tr, J.TRIALS)


if __name__ == "__main__":
    nrm = lens.trial_acc(lens.run(J.PH, J.G, J.ENV, SEEDS, device="cpu"), J.TRIALS)
    res = {"normal": lens.ci(nrm), "J5a": {}, "J5b": {}}
    for which in ("actuator", "sensors", "others"):
        p = run(erase_S_mask(which), J.at(8))
        res["J5a"][which] = lens.ci(p)
        print("J5a", which, [round(x, 3) for x in res["J5a"][which]], flush=True)
    for off in range(1, J.ENV.delta):
        pS = run(J.erase(["S"]), J.at(off))
        pF = run(J.erase(["flush"]), J.at(off))
        res["J5b"][off] = {"erase_S": lens.ci(pS), "flush": lens.ci(pF)}
        print("J5b", off, round(res["J5b"][off]["erase_S"][0], 3), round(res["J5b"][off]["flush"][0], 3), flush=True)
    (HERE / "out_j5.json").write_text(json.dumps(res, indent=1))
