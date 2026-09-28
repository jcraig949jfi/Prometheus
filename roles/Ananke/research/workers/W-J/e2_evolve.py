"""E2 (PLAN.md addendum): evolve under 4 receiver operators, then probe.
usage: python e2_evolve.py <device> [arms] [tasks] [seeds]
Writes out/e2_<arm>_<task>_<k>.json (one per search, resumable)."""
import dataclasses, json, os, pathlib, sys, time
import numpy as np, torch
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import arb
from prometheus.ananke import assays, c1b_run, envs, lens, search
from prometheus.ananke.rng import H_int
OUT = pathlib.Path(__file__).parent / "out"
NS = 0x5EF
ARMS = ["SUM", "SAT2", "ALOHA2", "ARB"]
TASKS = ["MAJ", "RELAY"]


def phys(base, arm):
    if arm == "SUM" or arm == "ARB":
        return base.replace(collision="none", cap=0)
    return base.replace(collision="saturate" if arm == "SAT2" else "aloha", cap=2)


def with_op(arm):
    arb.install(arm == "ARB")


def held_eval(base, arm, env, g, seeds, dev):
    with_op(arm)
    r = assays.evaluate(phys(base, arm), g[None], env, seeds, device=dev)
    p = r.pair_acc()[0]
    with_op("SUM")
    return lens.ci(p), {k: float(v[0]) for k, v in r.tel.items()}


def probes(base, arm, env, g, dev):
    """Own-operator mechanism probes on 64 held worlds (ns NS)."""
    with_op(arm)
    ph = phys(base, arm)
    seeds = assays.world_seeds(H_int(NS, 0xE2), 64)
    ep = envs.build(ph, env, seeds)
    ro = sorted(set(int(x) for x in ep.ro_tick[0][ep.scored[0]]))
    base_tr = lens.run(ph, g, env, seeds, device=dev)
    nrm = lens.trial_acc(base_tr, range(env.trials))
    out = {"normal": lens.ci(nrm)}

    def amnesia(w):
        a = w.read_idx[:, 0]; bi = torch.arange(w.B, device=w.dev)
        w.S[bi, a] = 0; w.Acc_sum[bi, a] = 0; w.Acc_cnt[bi, a] = 0
    arms = {"amnesia_ro-2": ({t - 2: amnesia for t in ro}),
            "payload_swap_ro-1": ({t - 1: (lambda w: lens.swap(w, ["Msum"])) for t in ro}),
            "count_swap_ro-1": ({t - 1: (lambda w: lens.swap(w, ["Mcnt"])) for t in ro}),
            "inbox_swap_ro-1": ({t - 1: (lambda w: lens.swap(w, ["Acc_sum", "Acc_cnt"])) for t in ro}),
            "site_S_swap_ro-1": ({t - 1: (lambda w: lens.swap(w, ["S"])) for t in ro})}
    for name, hooks in arms.items():
        tr = lens.run(ph, g, env, seeds, hooks=hooks, device=dev)
        p = lens.trial_acc(tr, range(env.trials))
        out[name] = {"acc": lens.ci(p), "verdict": lens.swap_verdict(nrm, p),
                     "identical": bool(np.array_equal(tr.trace, base_tr.trace))}
    with_op("SUM")
    return out


def main(dev, arms, tasks, ks):
    base, env0, _, row = c1b_run.load("f6b623cdb23afd2c")
    lossless = bool(os.environ.get("WJ_LOSSLESS"))
    if lossless:   # E6 (PLAN.md): the E5b physics
        base = base.replace(loss=0.0, dup=0.0, noise=0, update_mode="sync", update_period=1)
    pre = "e6" if lossless else "e2"
    sp = search.SearchSpec(**{k: v for k, v in row["search"].items()
                              if k in {f.name for f in dataclasses.fields(search.SearchSpec)}})
    for task in tasks:
        env = dataclasses.replace(env0, family=task)
        for arm in arms:
            for k in ks:
                f = OUT / f"{pre}_{arm}_{task}_{k}.json"
                if f.exists():
                    continue
                t0 = time.time()
                ss = H_int(NS, ARMS.index(arm), TASKS.index(task), k) if not lossless else H_int(NS, 6, ARMS.index(arm), TASKS.index(task), k)
                with_op(arm)
                ev = search.evolve(phys(base, arm), env, ss, sp, device=dev)
                with_op("SUM")
                g = np.asarray(ev["champion"], dtype=np.int64)
                hseeds = assays.world_seeds(H_int(ss, search.HELD_NS), sp.M_held)
                xfer = {}
                for a2 in ARMS:
                    ci, tel = held_eval(base, a2, env, g, hseeds, dev)
                    xfer[a2] = {"acc": ci, "emit_rate": tel.get("emit_rate"),
                                "collide_frac": tel.get("collide_frac")}
                out = {"arm": arm, "task": task, "k": k, "search_seed": ss,
                       "held": ev["held"], "held_tel": ev["held_tel"], "twin": ev["twin"],
                       "champion": ev["champion"], "curve_last": ev["curve"][-1],
                       "transfer": xfer, "probes": probes(base, arm, env, g, dev),
                       "wall_s": time.time() - t0}
                f.write_text(json.dumps(out, indent=1, default=float))
                print(arm, task, k, "held", round(ev["held"]["acc"], 3), round(ev["held"]["lo99"], 3),
                      "cd", round(ev["held"]["comm_delta"], 3),
                      "xfer", {a: round(v["acc"][0], 3) for a, v in xfer.items()},
                      {n: v["verdict"] for n, v in out["probes"].items() if n != "normal"},
                      "wall", round(out["wall_s"]), flush=True)


if __name__ == "__main__":
    dev = sys.argv[1]
    arms = sys.argv[2].split(",") if len(sys.argv) > 2 else ARMS
    tasks = sys.argv[3].split(",") if len(sys.argv) > 3 else TASKS
    ks = [int(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else [0, 1, 2, 3]
    torch.set_num_threads(2)
    main(dev, arms, tasks, ks)
