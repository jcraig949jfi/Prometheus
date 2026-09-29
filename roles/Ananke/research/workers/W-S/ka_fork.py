"""KA-F: probe.fork site/chan arms (with the LogWorld base) are bit-identical to W-R fork_single
(itself bit-identical to lens_swap.run_arms). MUST-FAIL: W-R fork_single with late=1."""
import json, os, pathlib, sys
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np
import run as R            # sets paths / threads
import probe
from prometheus.ananke import assays

out = {}
for name, offs in (("PLANT2J1", [0, 5, 6, 11, 12]), ("2dccdaa5", [4, 5]), ("e06701a5", [4, 5])):
    ph, env, g, _ = R.load(name)
    seeds = assays.world_seeds(0x630, 16)
    trials = [1, 2, 3]
    mine = probe.fork(ph, g, env, seeds, offs, trials, kinds=("site", "chan"))
    for late in (0, 1):
        ep, normal, ns0, site, chan, s0s, s0c = probe.WR.fork_single(ph, g, env, seeds, offs, trials, late=late)
        eq = []
        for o in offs:
            for kd, ref, refs0 in (("site", site, s0s), ("chan", chan, s0c)):
                p, s0 = mine["res"][kd][o]
                eq.append(bool(np.array_equal(p, ref[o], equal_nan=True) and np.array_equal(s0, refs0[o])))
        eq.append(bool(np.array_equal(mine["normal"], normal, equal_nan=True) and np.array_equal(mine["ns0"], ns0)))
        out[f"{name}_late{late}"] = {"arms_identical": sum(eq), "of": len(eq)}
        print(name, "late", late, sum(eq), "/", len(eq), flush=True)
(HERE / "out/ka_fork.json").write_text(json.dumps(out, indent=1))
