"""DEV screen (16 worlds, namespace W2JD, disjoint from scoring W2JS) of W2-J plant variants on every
uncapped XOR evolve row whose LC2 bound is >= .55. Variant menu is chosen from the row's physics only.
Minimal override (prog_len/state_dim/payload_width/channels raised only where the plant needs it).
usage: python screen.py [cell8 ...]"""
import sys, time
from wj_common import *
import plants_wj as pw
from prometheus.ananke import assays, envs
from prometheus.ananke.physics import Physics


def variants(ph, env):
    Pd, dl = env.period(), env.delta
    k = ph.decay_shift
    noisy = ph.noise > 0 or (ph.cap > 0 and ph.collision == "saturate")
    evs = ["cnt"] + (["payN"] if noisy else ["pay"])
    out = []
    if ph.update_mode == "sync" and k in (0, 1, 6):
        for ev in evs:
            out.append(("clk", ev, dict(p=ph.update_period, comp=k)))
    for Ws in (Pd - 3, Pd - 1):
        if k in (3, 6):
            out.append(("ttl", "cnt", dict(Ws=Ws, Wf=dl + 1, timer="decay")))
        elif k == 1:
            try:
                pw.ttl_thresholds(ph, Ws, dl + 1, "decay", start=32640)
                out.append(("ttl", "cnt", dict(Ws=Ws, Wf=dl + 1, timer="decay", big=True)))
            except AssertionError:
                pass
        else:
            out.append(("ttl", "cnt", dict(Ws=Ws, Wf=dl + 1, timer="dec")))
    return out


def build(ph, env, fam, ev, o, readout="xor"):
    if fam == "clk":
        return pw.clk_lines(env.period(), o["p"], o["comp"], ev, readout)
    return pw.ttl_lines(ph, ev, o["Ws"], o["Wf"], o["timer"], readout, big=o.get("big", False))


def main():
    t0 = time.process_time()
    only = sys.argv[1:]
    L2 = {o["cell"]: o for o in json.load(open(OUT / "lc2.json"))["rows"]}
    LC = lc()
    seeds = assays.world_seeds(WJ_DEV, 16)
    res = []
    for r in xor_evolve():
        c = r["cell_id"]
        if LC[c]["bound"] < 0.6 or L2[c]["acc_ub"] < 0.55:
            continue
        if only and c[:8] not in only:
            continue
        ph0 = Physics.from_dict(r["physics"])
        env = envs.EnvSpec(**r["env"])
        for fam, ev, o in variants(ph0, env):
            lines = build(ph0, env, fam, ev, o)
            ph, ov = pw.fit(ph0, lines, ev, fam, strict=False)
            g = pw.genome(ph, lines)
            ev_ = hc.evaluate(ph, g, env, seeds)
            rec = {"cell": c, "fam": fam, "ev": ev, "opts": o, "len": len(lines), "override": ov,
                   "strict_fits": not ov, "acc": ev_["acc"], "lo99": ev_["lo99"],
                   "stats": ev_["stats"]}
            res.append(rec)
            print(c[:8], fam, ev, o, "len", len(lines), "ov", ov, "acc %.3f" % ev_["acc"], flush=True)
    name = "screen.json" if not only else "screen_" + "_".join(only) + ".json"
    save(name, {"rows": res, "cpu_s": time.process_time() - t0})
    print("cpu_s", time.process_time() - t0)


if __name__ == "__main__":
    main()
