"""W-I robustness conditions (PLAN.md, frozen). Seeds 0x5EE^0x3."""
import json, math, os, pathlib, sys, time
HERE = pathlib.Path(__file__).parent
REPO = HERE.resolve().parents[4]
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(HERE))
import numpy as np, torch
from prometheus.ananke import assays, c1b_run, lens
from prometheus.ananke.engine import Controls
import main as M

DEV = os.environ.get("WI_DEV", "cpu")


def conditions(ph):
    if ph.topology in ("torus", "smallworld"):
        n2 = int(round(ph.side * math.sqrt(2))) ** 2
    else:
        n2 = 2 * ph.n_sites
    return {
        "base": (ph, None),
        "loss": (ph.replace(loss=min(0.9, ph.loss + 0.2)), None),
        "jitter": (ph.replace(lat_jitter=ph.lat_jitter + 2), None),
        "latency": (ph.replace(lat_base=ph.lat_base + 2), None),
        "distractor": (ph, Controls(distractor_chan=0)),
        "size": (ph.replace(n_sites=n2), None),
    }


if __name__ == "__main__":
    torch.set_num_threads(2)
    ids = M.full_ids()
    seeds = assays.world_seeds(0x5EE ^ 0x3, 64)
    f = HERE / "out" / "robust.json"
    res = json.loads(f.read_text()) if f.exists() else {}
    for c in M.PANEL + M.SPAN:
        if c in res:
            continue
        ph, env, g, row = c1b_run.load(ids[c])
        r = {}
        t = time.time()
        for name, (p2, ctrl) in conditions(ph).items():
            tr = lens.run(p2, g, env, seeds, device=DEV, ctrl=ctrl)
            r[name] = lens.ci(lens.trial_acc(tr, range(env.trials)))
        res[c] = r
        f.write_text(json.dumps(res, indent=1))
        print(c, {k: round(v[0], 3) for k, v in r.items()}, round(time.time() - t, 1), flush=True)
