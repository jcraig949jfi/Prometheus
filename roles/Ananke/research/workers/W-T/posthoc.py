"""W-T POST HOC (labelled; not in the frozen PLAN): where the first-broadcast rule fails, which source
emission (if any) does the readout follow? Re-runs the same fork (same ns 0x640, M 256, bit-identical
cue logs) and stores, per eligible pair-trial, the source's cue-bearing copies to the readout
(te - tau, arr - tau). Predictors (3-way S/C/M/U by held/flight of the chosen copies):
  E<j>   : copies from the j-th distinct source emission tick (j = 1 is P8)
  ELAST  : copies from the latest source emission with te <= tau
  ALAST  : the last-arriving source copies (max arrival <= ro)
python posthoc.py <spec> <offsets> <census frozen|follow> <units o:q,...>"""
import json
import pathlib
import sys
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np
import wt
import analyze as WSA
import probe
from prometheus.ananke import assays, lens_swap as LS
from followdiff import follow_table


def cls(xs, tau=0):
    if not xs:
        return "U"
    h = sum(a <= tau for _, a in xs)
    return "S" if h == len(xs) else ("C" if h == 0 else "M")


def main():
    name = sys.argv[1]
    offsets = [int(x) for x in sys.argv[2].split(",")]
    census = sys.argv[3]
    units = [tuple(int(y) for y in u.split(":")) for u in sys.argv[4].split(",")]
    ph, env, g, _ = wt.load(name)
    M, P = 256, 128
    seeds = assays.world_seeds(wt.NS, M)
    trials = list(range(1, env.trials))
    Pd = env.period()
    res = probe.fork(ph, g, env, seeds, offsets, trials, kinds=("site", "chan"))
    ep = res["ep"]
    src = ep.schedule.sense_idx[:, 0].numpy()
    rows = []
    for k in trials:
        wi = WSA.pair_index(res["cue_logs"][k], M)
        t0, ro = k * Pd, int(ep.ro_tick[0, k])
        for o in offsets:
            site, s0s = res["res"]["site"][o]
            chan, s0c = res["res"]["chan"][o]
            if census == "frozen":
                tab = LS.pair_trial_table(res["normal"], site, chan, s0s, s0c, [k])
            else:
                tab = follow_table(res["ns0"], s0s, s0c, ep.scored, [k])
            tau = t0 + o
            for p in range(P):
                if not tab["ok"][p, k]:
                    continue
                a, s = int(res["ro_site"][2 * p]), int(src[2 * p])
                d = set()
                for m in (2 * p, 2 * p + 1):
                    d |= {x for x in wi[m].get(a, ()) if x[0] >= t0 and x[1] <= ro}
                sc = sorted((x[0] - tau, x[1] - tau) for x in d if x[2] == s)
                rows.append({"pair": p, "trial": k, "o": o, "q": tau % 2, "pat": str(tab["pat"][p, k]), "src": sc,
                             "ro_rel": ro - tau})
    (HERE / "out" / f"posthoc_{name}.json").write_text(json.dumps(rows))
    out, lines = {}, []
    for o, q in units:
        rr = [r for r in rows if r["o"] == o and r["q"] == q]
        pat = np.array([r["pat"] for r in rr])
        pair = np.array([r["pair"] for r in rr])
        preds = {}
        for j in range(1, 9):
            v = []
            for r in rr:
                ticks = sorted({te for te, _ in r["src"]})
                v.append(cls([c for c in r["src"] if c[0] == ticks[j - 1]]) if len(ticks) >= j else "U")
            preds[f"E{j}"] = np.array(v)
        v = []
        for r in rr:
            le = [te for te, _ in r["src"] if te <= 0]
            v.append(cls([c for c in r["src"] if c[0] == max(le)]) if le else "U")
        preds["ELAST"] = np.array(v)
        v = []
        for r in rr:
            if not r["src"]:
                v.append("U")
                continue
            am = max(a for _, a in r["src"])
            v.append(cls([c for c in r["src"] if c[1] == am]))
        preds["ALAST"] = np.array(v)
        u = {"census": dict(Counter(pat.tolist()))}
        ln = [f"{name} o{o} q{q} census {u['census']}"]
        for nm, pr in preds.items():
            dec = np.isin(pr, ("S", "C"))
            sc = np.isin(pat, ("S", "C"))
            ra = WSA.accuracy(pr[dec], pat[dec], pair[dec])
            rs = WSA.accuracy(pr, pat, pair)
            cov = float(np.mean(dec[sc])) if sc.any() else 0.0
            u[nm] = {"decisive": ra, "strict": rs, "coverage": cov,
                     "xtab": {f"{a}>{b}": c for (a, b), c in sorted(Counter(zip(pat.tolist(), pr.tolist())).items())}}
            if ra["acc"] is not None:
                ln.append(f"   {nm:5s} dec {ra['acc']:.3f} [{ra['ci99'][0]:.3f},{ra['ci99'][1]:.3f}] cov {cov:.2f} | strict {rs['acc']:.3f}  {u[nm]['xtab']}")
        out[f"o{o}q{q}"] = u
        lines += ln
    (HERE / "out" / f"posthoc_summary_{name}.json").write_text(json.dumps(out, indent=1, default=float))
    (HERE / "out" / f"posthoc_summary_{name}.txt").write_text("\n".join(lines))
    print("\n".join(lines), flush=True)


if __name__ == "__main__":
    main()
