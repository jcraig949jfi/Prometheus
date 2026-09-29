"""W-R main run: SINGLE census stratified by update-clock phase.
python stratify.py <spec> [M]   (spec = cell id | E1 | E2 | PLANT2 | PLANT1)
Writes out/strat_<spec>.json and out/raw_<spec>.npz."""
import json, pathlib, sys, time
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import specs
import numpy as np, torch
torch.set_num_threads(2)
from prometheus.ananke import assays
import fork

NS = 0x620


def strat_period(ph):
    """True clock period for sync p > 1; pseudo-phase parity (2) otherwise (PLAN s1)."""
    if ph.update_mode == "sync" and ph.update_period > 1:
        return ph.update_period, "update_clock"
    return 2, "pseudo_parity"


def main(name, M=256, ns=None, tag=""):
    ns = NS if ns is None else ns
    t0 = time.time()
    ph, env, g, meta = specs.load(name)
    torch.set_num_threads(2)
    seeds = assays.world_seeds(ns, M)
    offs = list(range(0, specs.ro_off(env)))
    trials = list(range(1, env.trials))
    Pd = env.period()
    p, kind = strat_period(ph)
    log = lambda s: print(f"[{name} {time.time() - t0:7.1f}s] {s}", flush=True)
    ep, normal, ns0, site, chan, s0s, s0c = fork.fork_single(ph, g, env, seeds, offs, trials, log=log)
    np.savez_compressed(HERE / f"out/raw_{name}{tag}.npz", normal=normal, normal_s0=ns0, scored=ep.scored, y=ep.y,
                        **{f"{o}__site": site[o] for o in offs}, **{f"{o}__chan": chan[o] for o in offs},
                        **{f"{o}__s0_site": s0s[o] for o in offs}, **{f"{o}__s0_chan": s0c[o] for o in offs})
    t_sim = time.time() - t0
    res = fork.stratified(normal, ns0, ep.scored, site, chan, s0s, s0c, trials, offs, Pd, p, follow=True)
    # normal accuracy per phase of t0 (trial onset parity) for the record
    nacc = {}
    for q in range(p):
        ks = [k for k in trials if (k * Pd) % p == q]
        nacc[f"t0mod{p}={q}"] = None if not ks else float(np.nanmean(normal[:, ks]))
    out = {"spec": name, "meta": meta, "M": M, "ns": hex(ns), "Pd": Pd, "strat_period": p, "strat_kind": kind,
           "update_mode": ph.update_mode, "update_period": ph.update_period, "trials": trials, "offsets": offs,
           "ro_off": specs.ro_off(env), "normal_acc_by_t0_phase": nacc, "wall_sim_s": t_sim,
           "wall_s": time.time() - t0, "offsets_res": {str(o): r for o, r in res.items()}}
    if name.startswith("PLANT"):
        rng = np.random.default_rng(0)
        perm = {}
        for o in offs:
            labs = [fork.phase_of(k, o, Pd, p) for k in trials]
            rng.shuffle(labs)
            perm[o] = dict(zip(trials, labs))
        pr = fork.stratified(normal, ns0, ep.scored, site, chan, s0s, s0c, trials, offs, Pd, p, permute=perm)
        out["permuted_mustfail"] = {str(o): r for o, r in pr.items()}
    (HERE / f"out/strat_{name}{tag}.json").write_text(json.dumps(out, indent=1, default=float))
    log(f"done sim {t_sim:.0f}s total {time.time() - t0:.0f}s")
    for o, r in res.items():
        print(o, r["pooled"]["class"], r.get("q0", {}).get("class"), r.get("q1", {}).get("class"),
              "eff" if r.get("phase_effect") else "", r.get("resolution") or "", flush=True)


if __name__ == "__main__":
    ns = int(sys.argv[3], 16) if len(sys.argv) > 3 else None
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 256, ns, f"_ns{sys.argv[3]}" if ns is not None else "")
