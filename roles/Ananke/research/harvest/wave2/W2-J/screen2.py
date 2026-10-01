"""DEV screen v2 (16 worlds, namespace W2JD; scoring uses W2JS) of W2-J plants on every uncapped XOR evolve
row with LC2 >= .55. Menu chosen from the row's physics only; constants are C1-genome-representable.
Minimal override. usage: python screen2.py [cell8 ...]"""
import sys, time
from wj_common import *
import plants_wj as pw
from prometheus.ananke import assays, envs
from prometheus.ananke.physics import Physics


def econ_heavy(ph):
    return ph.c_op > 0


def variants(ph, env):
    Pd, dl = env.period(), env.delta
    k = ph.decay_shift
    capped = ph.cap > 0 and ph.collision in ("aloha", "saturate")
    lat_min = max(1, ph.lat_base + ph.lat_hop * 1)
    We = max(2, min(4, dl // 2))
    out = []
    if ph.update_mode == "sync" and k in (0, 1, 6):
        out.append(("clk2", dict(p=ph.update_period, comp=k, emit="once")))
        out.append(("clk2", dict(p=ph.update_period, comp=k, emit="persist", lat_min=lat_min)))
        if capped:
            out.append(("clk2", dict(p=ph.update_period, comp=k, emit="persist", lat_min=lat_min, gossip=1)))
    ttl_ok = True
    try:
        pw.ttl2_thresholds(ph, Pd - 1, dl + 1, We)
    except AssertionError:
        ttl_ok = False
    if ttl_ok and (ph.update_mode == "async" or k == 3):
        out.append(("ttl2", dict(Ws=Pd - 1, Wf=dl + 1, We=We, emit="once")))
        out.append(("ttl2", dict(Ws=Pd - 1, Wf=dl + 1, We=We, emit="persist")))
        if capped:
            out.append(("ttl2", dict(Ws=Pd - 1, Wf=dl + 1, We=We, emit="persist", gossip=1)))
        if k in (3, 6):   # the 16-line C1-space plant (cnt evidence, 256-start decay timer)
            out.append(("ttl1", dict(Ws=Pd - 1, Wf=dl + 1)))
    if econ_heavy(ph):
        out = out[:2]
    return out


def build(ph, env, fam, o, readout="xor"):
    Pd, dl = env.period(), env.delta
    if fam == "clk2":
        return pw.clk2_lines(Pd, dl, o["p"], o["comp"], emit=o["emit"], lat_min=o.get("lat_min", 1),
                             gossip=o.get("gossip"), readout=readout), "payN", "clk"
    if fam == "ttl2":
        return pw.ttl2_lines(ph, o["Ws"], o["Wf"], o["We"], emit=o["emit"], gossip=o.get("gossip"),
                             readout=readout), "payN", "ttl"
    if fam == "clk3":
        return pw.clk3_lines(ph, Pd, dl, emit=o["emit"], gossip=o.get("gossip"), readout=readout), "payN", "clk3"
    if fam == "clk4":
        return pw.clk4_lines(ph, Pd, dl, emit=o["emit"], gossip=o.get("gossip"), readout=readout), "payN", "clk4"
    if fam == "ttl1":
        return pw.ttl_lines(ph, "cnt", o["Ws"], o["Wf"], "decay", readout), "cnt", "ttl"
    if fam == "clk1":
        return pw.clk_lines(Pd, o["p"], o["comp"], o["ev"], readout), o["ev"], "clk"
    raise KeyError(fam)


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
        for fam, o in variants(ph0, env):
            lines, ev, f2 = build(ph0, env, fam, o)
            ph, ov = pw.fit(ph0, lines, ev, f2, strict=False)
            e = hc.evaluate(ph, pw.genome(ph, lines), env, seeds)
            rec = {"cell": c, "fam": fam, "opts": o, "len": len(lines), "override": ov, "acc": e["acc"],
                   "lo99": e["lo99"], "stats": e["stats"]}
            res.append(rec)
            st = e["stats"]
            print(c[:8], fam, o, "len", len(lines), "ov", ov, "acc %.3f" % e["acc"],
                  "emit/aw %.3f deliv/att %.2f coll %d" % (st["emitters"] / max(1, st["awake"]),
                                                          st["delivered"] / max(1, st["attempted"]), st["collided"]),
                  flush=True)
    name = "screen2.json" if not only else "screen2_" + "_".join(only) + ".json"
    save(name, {"rows": res, "cpu_s": time.process_time() - t0})
    print("cpu_s", time.process_time() - t0)


if __name__ == "__main__":
    main()
