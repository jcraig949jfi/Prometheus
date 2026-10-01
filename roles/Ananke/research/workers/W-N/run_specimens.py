"""PLAN s6: relative swap verdict on real low-accuracy champions (SINGLE arms, M=512)."""
import json, sys, time
import numpy as np, torch
TH = int(sys.argv[1]) if len(sys.argv) > 1 else 8
WHICH = sys.argv[2] if len(sys.argv) > 2 else "all"
torch.set_num_threads(TH)
import plants_rel as pr, swap_rel as sr
from prometheus.ananke import assays, rng, lens, lens_swap, c1b, c1b_run
M = 512
out = {}
t0 = time.time()


def verdicts(n, arms, extra=None):
    res = {}
    for k, a in arms.items():
        v = sr.swap_verdict_rel(n, a)
        v["absolute"] = sr.absolute_verdict(n, a)
        res[k] = v
        print(f"   {k:12s} n={v['normal'][0]:.3f}[{v['normal'][1]:.3f}] s={v['swap'][0]:.3f}[{v['swap'][1]:.3f},{v['swap'][2]:.3f}] "
              f"z={v['z'] if v['z'] is None else round(v['z'], 2)} f={v['flip_rate']['f']:.2f} pmin={v['p_min']} "
              f"REL={v['verdict']:13s} ungated={v['verdict_ungated']:13s} ABS={v['absolute']} {time.time()-t0:.0f}s", flush=True)
    return res


if WHICH in ("all", "wl"):
    pr.nb.install()
    ph = pr.nb.m2()[0]
    seeds = assays.world_seeds(rng.H_int(pr.NS_WN, 0x4E), M)
    for tag in ["n1_s0", "n1_s3", "n2_s1", "n2_s2", "n1_s2"]:
        d = json.load(open(pr.WL / "out" / f"search_{tag}.json"))
        n_ = d["n"]
        g = np.asarray(d["evolve"]["champion"], dtype=np.int64)
        env = pr.nb.spec(n_)
        TR = list(range(n_, env.trials))
        kinds = ["S", "site_all", "channel_all", "inbox", "Kp"]
        rec = {"n": n_, "SUCCESS": d["held_5F3"]["SUCCESS"]}
        backs = [0, 1] if n_ == 2 else [0]
        for back in backs:
            off = -1 - back * env.period()
            print(tag, f"back{back}", flush=True)
            ep, nrm, arms, n0, s0 = pr.run_fork(ph, g, env, seeds, kinds, TR, offset=off)
            rec[f"back{back}"] = verdicts(nrm, arms)
            rec["per_trial_normal"] = [float(x) for x in np.nanmean(nrm, 0)]
        out[tag] = rec
    json.dump(out, open("out/specimens_wl.json", "w"), indent=1, default=str)

if WHICH in ("all", "c1"):
    out = {}
    seeds = assays.world_seeds(rng.H_int(pr.NS_WN, 0xC1), M)
    for cid in ["0187372b391d9d4e", "11f3ac8548d931fd", "83d9d7b50cb7e409", "4271681452d29aee", "d3c0d182d3dbb735"]:
        ph, env, g, row = c1b_run.load(cid)
        tk = c1b.ticks(env)
        t0s = tk["t0"]
        mid_off = tk["mid"][0] - t0s[0]
        late_off = tk["late"][0] - t0s[0]
        assert all(m - t == mid_off for m, t in zip(tk["mid"], t0s))
        TR = [k for k in range(env.trials)]
        rec = {"family": env.family, "held": row["result"]["held"]}
        for lab, off, kinds in (("mid", mid_off, ["site_all", "channel_all", "joint"]),
                                ("late", late_off, ["site_all", "channel_all"])):
            print(cid[:8], env.family, lab, off, flush=True)
            ep, nrm, arms, n0, s0 = pr.run_fork(ph, g, env, seeds, kinds, TR, offset=off)
            rec[lab] = verdicts(nrm, arms)
            c = lens_swap.census(nrm, arms["site_all"], arms["channel_all"], s0["site_all"], s0["channel_all"], TR)
            c["class"] = lens_swap.classify(c)
            rec[lab + "_census"] = {k: c[k] for k in ("class", "eligible", "fS", "fC", "fN", "identity", "phi", "ci99")}
            print("   census", c["class"], {k: (None if c[k] is None else round(c[k], 3)) for k in ("fS", "fC", "fN", "identity")}, flush=True)
            if lab == "mid":
                # EVERY-trial comparison (W-F design, same seeds)
                base = lens.run(ph, g, env, seeds)
                ev = {}
                for k in kinds:
                    fn = pr.make_fn(k, M)
                    rows = torch.arange(M)
                    tr = lens.run(ph, g, env, seeds, hooks={t: (lambda w, fn=fn: fn(w, rows)) for t in tk["mid"]})
                    ev[k] = tr.per_trial.astype(float)
                nb_ = np.where(base.ep.scored, base.per_trial.astype(float), np.nan)
                print("   EVERY:", flush=True)
                rec["mid_every"] = verdicts(nb_, {k: np.where(base.ep.scored, v, np.nan) for k, v in ev.items()})
        out[cid] = rec
        json.dump(out, open("out/specimens_c1.json", "w"), indent=1, default=str)
