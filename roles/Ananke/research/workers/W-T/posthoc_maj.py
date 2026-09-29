"""W-T POST HOC (labelled): MAJ 4781b0a1 cue-bearing traffic to the readout by emitter class
(sensor 0 = P8's source, other 4 sensors, non-sensor relays), same ns 0x640 M 256, offsets 4,5,9,12.
python posthoc_maj.py"""
import json, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np
import wt, analyze as WSA, probe
from prometheus.ananke import assays, lens_swap as LS
from collections import Counter

ph, env, g, _ = wt.load("4781b0a1")
M, P = 256, 128
offsets = [4, 5, 9, 12]
trials = list(range(1, env.trials))
Pd = env.period()
res = probe.fork(ph, g, env, assays.world_seeds(wt.NS, M), offsets, trials, kinds=("site", "chan"))
ep = res["ep"]
sidx = ep.schedule.sense_idx.numpy()
acc = {}
for k in trials:
    wi = WSA.pair_index(res["cue_logs"][k], M)
    t0, ro = k * Pd, int(ep.ro_tick[0, k])
    for o in offsets:
        site, s0s = res["res"]["site"][o]; chan, s0c = res["res"]["chan"][o]
        tab = LS.pair_trial_table(res["normal"], site, chan, s0s, s0c, [k])
        tau = t0 + o
        for p in range(P):
            if not tab["ok"][p, k]:
                continue
            a = int(res["ro_site"][2 * p]); ss = list(sidx[2 * p])
            d = set()
            for m in (2 * p, 2 * p + 1):
                d |= {x for x in wi[m].get(a, ()) if x[0] >= t0 and x[1] <= ro}
            c = Counter()
            for x in d:
                cl = "s0" if x[2] == ss[0] else ("sens" if x[2] in ss else "relay")
                c[cl] += 1
                if x[0] <= tau < x[1]:
                    c[cl + "_fl"] += 1
                if x[1] <= tau:
                    c[cl + "_held"] += 1
            key = f"o{o}q{tau % 2}_{tab['pat'][p, k]}"
            acc.setdefault(key, []).append(c)
out = {}
for key, cs in sorted(acc.items()):
    n = len(cs)
    out[key] = {"n": n, **{f: round(sum(c[f] for c in cs) / n, 2) for f in
                            ("s0", "sens", "relay", "s0_fl", "sens_fl", "relay_fl", "s0_held", "sens_held", "relay_held")}}
    print(key, out[key], flush=True)
(HERE / "out" / "posthoc_maj_traffic.json").write_text(json.dumps(out, indent=1))
