"""S-CT: carrier table over the 12 C1 D-wave adjudicated cells (log addendum 2)."""
import json
import pathlib
import sys

import numpy as np

REPO = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))
from prometheus.ananke import assays, c1b, c1b_run, envs, lens  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402

OUT = pathlib.Path(__file__).parent / "out"
SEEDS = assays.world_seeds(0x5E3, 64)
ARMS = {
    "inflight": lambda w: lens.swap(w, lens.FLIGHT_ARRAYS),
    "sitestate": lambda w: lens.swap(w, lens.SITE_ARRAYS),
    "payload": lambda w: lens.swap(w, ["Msum"]),
    "counts": lambda w: lens.swap(w, ["Mcnt"]),
    "delay+1": lambda w: lens.roll_slots(w, 1),
    "w": lambda w: lens.swap(w, ["w"]),
}

if __name__ == "__main__":
    res = {}
    for r in c1b_run.d_wave_cells():
        ph, env = Physics.from_dict(r["physics"]), envs.EnvSpec(**r["env"])
        g = np.asarray(r["extra"]["genome"], dtype=np.int64)
        tk = c1b.ticks(env)
        mid = tk["mid"] if env.family == "HOLD" else [t0 + max(1, env.delta // 2) for t0 in tk["t0"]]
        base = lens.run(ph, g, env, SEEDS)
        nrm = lens.trial_acc(base, range(env.trials))
        row = {"family": env.family, "normal": lens.ci(nrm), "dest_mode": ph.dest_mode}
        for an, fn in ARMS.items():
            tr = lens.run(ph, g, env, SEEDS, hooks={t: fn for t in mid})
            pr = lens.trial_acc(tr, range(env.trials))
            row[an] = {"acc": lens.ci(pr), "verdict": lens.swap_verdict(nrm, pr)}
        name = r["extra"]["source_cell"][:8]
        res[name] = row
        print(f"{name} {env.family:5s} n={row['normal'][0]:.2f} " +
              " ".join(f"{a}:{row[a]['verdict'][:4]}({row[a]['acc'][0]:.2f})" for a in ARMS), flush=True)
    (OUT / "s_ct.json").write_text(json.dumps(res, indent=1))
