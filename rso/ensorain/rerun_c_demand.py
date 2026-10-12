"""C-016-T020 small re-run: does Ensorain WTP-05 family C reward lifetime state, and does a simpler competitor fail?

Read-only against ensorain/ (imported, never edited). NEW seeds only (16_020_xxx; none of the WTP-05 registered seeds).
Command (from the repo root, <= 1 process, ~minutes):
    python -m rso.ensorain.rerun_c_demand rso/ensorain/rerun_c_demand_result.json
Arms (all on the planted switch_C genome, ensorain/wtp5/planted.py:switch_C):
  plastic       plasticity ON  (the lawful reference; certify.py family C)
  frozen        plasticity OFF (same genome, theta = 0.2 never updated)  <- the simpler competitor
  hist_shuffle  plasticity ON but episode rewards shuffled within a block before the update (history_shuffle control)
Reported per arm, over N lifetimes: role-1 (switching law) accuracy before the switch, in the 3 blocks after, and
from switch+3 to the end (the SWITCH_TRACKED window); role-5 (never-switching law) accuracy; fraction SWITCH_TRACKED.
Plus the null ladder (ensorain/wtp5/nulls.py:ladder) on a new seed, role-1 and role-5 separately.
"""
import json
import sys

import numpy as np

from ensorain.wtp5.nulls import ladder
from ensorain.wtp5.planted import planted
from ensorain.wtp5.tape import lifetime
from ensorain.wtp5.worlds import make

SEED0 = 16_020_001
N_LIVES = 40
SPEC = "C-R2-desert"


def arm(name, kw, seed):
    w = make(SPEC)
    g = planted(w)
    pre, early, late, t2, tracked = [], [], [], [], []
    for i in range(N_LIVES):
        rng = np.random.default_rng(seed + i)
        w.new_life(rng)
        sw = w.sw
        life = lifetime(g, w, rng, K=64, **kw)
        bl = life["blocks"]
        pre += [b["acc"][1] for j, b in enumerate(bl) if j < sw and 1 in b["acc"]]
        early += [b["acc"][1] for j, b in enumerate(bl) if sw <= j < sw + 3 and 1 in b["acc"]]
        l = [b["acc"][1] for j, b in enumerate(bl) if j >= sw + 3 and 1 in b["acc"]]
        late += l
        t2.append(life["roles"][5])
        tracked.append(float(np.mean(l)) >= 0.75 and life["roles"][5] >= 0.90)
    return dict(arm=name, n_lives=N_LIVES, role1_pre=float(np.mean(pre)), role1_post_early=float(np.mean(early)),
                role1_late=float(np.mean(late)), role5=float(np.mean(t2)), frac_switch_tracked=float(np.mean(tracked)))


def main(out):
    res = dict(spec=SPEC, seed0=SEED0, arms=[])
    res["arms"].append(arm("plastic", dict(plasticity=True), SEED0))
    res["arms"].append(arm("frozen", dict(plasticity=False), SEED0))
    res["arms"].append(arm("hist_shuffle", dict(plasticity=True, history_shuffle=True), SEED0))
    lad = ladder(make(SPEC), SEED0 + 10_000)
    res["ladder"] = {k: v for k, v in lad.items()}
    json.dump(res, open(out, "w"), indent=1, default=lambda x: x.item() if hasattr(x, "item") else str(x))
    for a in res["arms"]:
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in a.items()})
    for k, v in lad.items():
        print(k, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in v.items()})


if __name__ == "__main__":
    main(sys.argv[1])
