"""A8: relay_flood (no adaptation; 'cannot solve FLIP by design', PREREG s11) scores
.734 / .336 on FLIP A0 cells. Reproduce on fresh worlds; split accuracy by block
mapping m (from the episode) and by trial position; zero_comm."""
from w2e_common import *
ck = Clock()
out = {}
for cid in ["926328ee", "a8185ca9"]:
    r = row(cid); ph, env = spec_of(r)
    p2 = ph.replace(prog_len=max(ph.prog_len, 12)).validate()
    g = plants.plant("relay_flood", p2)
    rec = r["result"]["plant"]
    res = {"recorded": rec, "env": env.to_dict()}
    rec_seeds = assays.world_seeds(H_int(r["search_seed"], 0x9147), 32)
    a, *_ = run(p2, g, env, rec_seeds); res["recheck_recorded_seeds"] = float(a.mean())
    S = seeds(H_int(NS, 0xA8, int(cid, 16) & 0xFFFF), 256)
    a, tr, ep, w = run(p2, g, env, S); res["fresh"] = ci(pairs(a))
    az, *_ = run(p2, g, env, S, ctrl=Controls(zero_comm=True)); res["fresh_zero_comm"] = ci(pairs(az))
    pt = envs.per_trial(ep, tr)
    # recover m per world/trial: y = sg*m*x; x from sensor schedule sign at cue tick
    Pd = env.period()
    x = np.stack([np.sign(ep.schedule.sense_val[k * Pd, :, 0].numpy()) for k in range(env.trials)], 1)
    m = ep.y * x                     # sg cancels (both x and y carry sg)
    sc = ep.scored
    res["acc_m+1"] = float(pt[sc & (m == 1)].mean()); res["acc_m-1"] = float(pt[sc & (m == -1)].mean())
    # lag-1 structure: agreement of readout sign with x_k, x_{k-1}, teacher_{k-1}
    s0 = tr[ep.ro_tick, np.arange(len(S))[:, None], ep.ro_slot]
    sg = np.sign(s0)
    res["P(sign==x_k)"] = float((sg[:, 1:] == x[:, 1:])[sg[:, 1:] != 0].mean())
    res["P(sign==x_k-1)"] = float((sg[:, 1:] == x[:, :-1])[sg[:, 1:] != 0].mean())
    res["P(sign==y_k-1)"] = float((sg[:, 1:] == ep.y[:, :-1])[sg[:, 1:] != 0].mean())
    res["frac_zero"] = float((s0 == 0).mean())
    out[cid] = res; print(cid, json.dumps(res), flush=True)
out["clock"] = ck.done(); save("a8_flip_plant.json", out)
