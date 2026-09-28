"""Engine gap sweeps for every W-A condition (CPU, 2 threads, namespace 0x5E4).

Usage: python run_engine.py [cond ...]   (resumable; appends to out/engine.json)
"""
import dataclasses
import json
import sys
import time

import torch

import conditions as C
from prometheus.ananke import assays, lens

torch.set_num_threads(2)
SEEDS = assays.world_seeds(0x5E4, 64)
OUT = C.HERE / "out" / "engine.json"

if __name__ == "__main__":
    want = set(sys.argv[1:])
    res = json.loads(OUT.read_text()) if OUT.exists() else {}
    t0 = time.time()
    for cond, name, ph, env, g, prog in C.conditions():
        if want and cond not in want:
            continue
        key = f"{cond}:{name}"
        rec = res.setdefault(key, {})
        for gap in C.GAPS:
            if str(gap) in rec:
                continue
            e = dataclasses.replace(env, gap=gap)
            tr = lens.run(ph, g, e, SEEDS, device="cpu")
            rec[str(gap)] = lens.ci(lens.trial_acc(tr, range(e.trials)))
            OUT.write_text(json.dumps(res, indent=1))
        print(key, " ".join(f"{gp}:{rec[str(gp)][0]:.2f}" for gp in C.GAPS),
              f"[{time.time() - t0:.0f}s]", flush=True)
