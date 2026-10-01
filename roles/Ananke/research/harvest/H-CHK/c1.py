"""C1: count-threshold plant (PLAN_ADDENDUM X2). python c1.py calib | tt | wv"""
import json, os, sys, time
import numpy as np
import hchk as H
from prometheus.ananke import assays, envs
from prometheus.ananke.engine import World, Controls
mode = sys.argv[1]
ph0, env, _ = H.champ()
ph = H.c1_physics(ph0)
H.threads1()
t0 = time.time()
if mode == "calib":
    seeds = assays.world_seeds(0xC4C1, 512)
    ep = envs.build(ph, env, seeds)
    g = H.c1_genome(ph, 1)
    ws1 = [seeds[m - (m % 2)] for m in range(len(seeds))]
    w = World(ph, np.repeat(g[None], len(seeds), 0), ws1, device=H.DEV, ctrl=Controls(), schedule=ep.schedule)
    for _ in range(env.T()):
        w.step()
    tr = w.trace.cpu().numpy()
    s0 = tr[ep.ro_tick, np.arange(len(seeds))[:, None], ep.ro_slot].astype(np.int64)
    cnt256 = s0 + H.theta_of(1)                       # = IN0_1 sum in the last wake window
    acc = {}
    for j in range(1, 41):
        v = cnt256 - H.theta_of(j)
        p = np.where(v == 0, .5, (np.sign(v) == ep.y).astype(float))
        acc[j] = float(p[ep.scored].mean())
    ok = [j for j in acc if acc[j] >= 0.70]
    jstar = min(ok) if ok else max(acc, key=acc.get)
    # reference: ideal majority of the 5 sensed signs
    sv = ep.schedule.sense_val.numpy()
    Pd = env.period()
    maj = np.stack([np.sign(sv[k * Pd:k * Pd + env.cue_len].sum(0).sum(-1)) for k in range(env.trials)], 1)
    res = {"acc_by_j": acc, "j": jstar, "theta": H.theta_of(jstar), "below_bar": not ok,
           "ideal_majority_acc": float((maj == ep.y)[ep.scored].mean()),
           "count_hist": np.unique(cnt256 // 256, return_counts=True), "wall_s": time.time() - t0,
           "physics": ph.to_dict()}
    H.dump(res, "c1_calib.json")
    print(json.dumps({k: res[k] for k in ("j", "theta", "below_bar", "ideal_majority_acc")}), {j: round(a, 3) for j, a in acc.items() if j <= 12}, flush=True)
    sys.exit(0)
cal = json.load(open(H.OUT / "c1_calib.json"))
g = H.c1_genome(ph, int(cal["j"]))
if mode == "tt":
    tt = H.mod("wp_tt")
    H.threads1()
    seeds = assays.world_seeds(0x610, 256)
    chk = tt.check_vs_lens(ph, g, env, seeds[:32], 5, 6, device=H.DEV)
    print("C1 bit-identity vs lens_swap", chk, flush=True)
    comps = tt.coarse_components(ph)
    names = list(comps)
    half = [z for z in tt.all_subsets(len(names)) if z[0] == 0]
    offs = list(range(1, 16))
    trials = [1, 2, 5, 6, 9, 10]
    save = {"names": np.array(names), "subs": np.array(half), "offsets": np.array(offs), "trials": np.array(trials)}
    for k in trials:
        res, ep = tt.run_table(ph, g, env, seeds, k, offs, comps, half, device=H.DEV)
        save[f"y_k{k}"] = ep.y[:, k]
        for o in offs:
            save[f"k{k}_o{o}"] = res[o].astype(np.int32)
        print("trial", k, round(time.time() - t0), "s", flush=True)
    np.savez_compressed(H.OUT / "c1_tt_raw.npz", **save)
    H.dump({"C1_bit_identity": chk, "names": names, "wall_s": time.time() - t0, "pid": os.getpid()}, "c1_tt_meta.json")
elif mode == "wv":
    wv = H.mod("wv_wv")
    H.threads1()
    seeds = assays.world_seeds(0x650, 128)
    offs = [2, 4, 6, 8, 10, 12, 14]
    r = wv.run(ph, g, env, seeds, offs, list(range(1, env.trials)), device=H.DEV)
    np.savez_compressed(H.OUT / "c1_wv_raw.npz", **{k: v for k, v in r.items() if k != "arms"})
    H.dump({"arms": r["arms"], "wall_s": time.time() - t0, "pid": os.getpid()}, "c1_wv_meta.json")
    print("done", round(time.time() - t0), flush=True)
