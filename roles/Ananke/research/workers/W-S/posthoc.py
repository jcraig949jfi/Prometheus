"""POST HOC (labelled; not in the frozen PLAN): re-run the champions with the same seeds (bit-identical
fork, same ns 0x630 M 256) and compute source-first-emission features for the offsets' pair-trials.
F1 predictor 'P8_srcfirst': only the cue-bearing copies to the readout a from the source's FIRST cue
emission tick (te1 = earliest te of a source->a cue-bearing copy with te >= t0): all delivered by tau -> S,
all after -> C, split -> M. Also counts held/flight among them, later source copies, and relay copies.
python posthoc.py <spec> <offsets> [ns_hex]"""
import json, os, pathlib, sys
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from collections import defaultdict
import numpy as np
import run as R
import probe, analyze
from prometheus.ananke import assays, lens_swap as LS


def main():
    name = sys.argv[1]
    offsets = [int(x) for x in sys.argv[2].split(",")]
    ph, env, g, _ = R.load(name)
    ns = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0x630
    seeds = assays.world_seeds(ns, 256)
    trials = list(range(1, env.trials))
    Pd = env.period()
    run = probe.fork(ph, g, env, seeds, offsets, trials, kinds=("site", "chan"))
    ep = run["ep"]
    M = 256
    P = M // 2
    src = ep.schedule.sense_idx[:, 0].numpy()
    rows = []
    for k in trials:
        wi = analyze.pair_index(run["cue_logs"][k], M)
        t0 = k * Pd
        ro = int(ep.ro_tick[0, k])
        for o in offsets:
            site, s0s = run["res"]["site"][o]
            chan, s0c = run["res"]["chan"][o]
            tab = LS.pair_trial_table(run["normal"], site, chan, s0s, s0c, [k])
            tau = t0 + o
            for p in range(P):
                if not tab["ok"][p, k]:
                    continue
                a, s = int(run["ro_site"][2 * p]), int(src[2 * p])
                # per side (normal world 2p, twin), copies to a: union over the pair's two worlds
                d = set()
                for m in (2 * p, 2 * p + 1):
                    d |= {x for x in wi[m].get(a, ()) if x[0] >= t0 and x[1] <= ro}
                srcc = sorted(x for x in d if x[2] == s)
                r = {"pair": p, "trial": k, "o": o, "q": tau % 2, "pat": str(tab["pat"][p, k]),
                     "y_same_prev": int(ep.y[2 * p, k] == ep.y[2 * p, k - 1])}
                if srcc:
                    te1 = srcc[0][0]
                    first = [x for x in srcc if x[0] == te1]
                    r["te1_rel"] = te1 - tau
                    r["n1_held"] = sum(x[1] <= tau for x in first)
                    r["n1_flight"] = sum(x[1] > tau for x in first)
                    r["P8_srcfirst"] = "S" if r["n1_flight"] == 0 else ("C" if r["n1_held"] == 0 else "M")
                    r["n_src_later_flight"] = sum(1 for x in srcc if x[0] > te1 and x[0] <= tau < x[1])
                    r["n_src_later_after"] = sum(1 for x in srcc if x[0] > tau)
                    r["arr1"] = sorted(x[1] - tau for x in first)
                else:
                    r["P8_srcfirst"] = "U"
                r["n_relay"] = sum(1 for x in d if x[2] != s)
                r["n_relay_flight"] = sum(1 for x in d if x[2] != s and x[0] <= tau < x[1])
                # normal-run readout value (magnitude) of both partners at ro
                r["ns0"] = [int(run["ns0"][2 * p, k]), int(run["ns0"][2 * p + 1, k])]
                r["site_s0"] = [int(s0s[2 * p, k]), int(s0s[2 * p + 1, k])]
                r["chan_s0"] = [int(s0c[2 * p, k]), int(s0c[2 * p + 1, k])]
                rows.append(r)
    (HERE / "out" / (f"posthoc_{name}.json" if ns == 0x630 else f"posthoc_{name}_ns{ns:x}.json")).write_text(json.dumps(rows))
    print(name, "rows", len(rows), flush=True)


if __name__ == "__main__":
    main()
