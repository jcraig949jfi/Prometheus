"""V instrument (ruler attainability), W2-D t_v_ruler.py adapted: run the cell's plant through C1's own held-out
protocol (HELD_NS seeds, M_held 64, zero-comm control, twin assay on hseeds[:16]) and campaign.classify.
Extras: DICT control (W2-M dict_sched: only sensor 0 cued) for an integration certificate; the per-generation
plant-loss bound P(mean of M/2 resampled plant held pairs < thr) for thr in a grid (W2-D F4 method).
usage: python t_v_ruler.py 8743|f29c"""
from ak_common import *
from prometheus.ananke.search import HELD_NS
p = sys.argv[1]
r, ph, env, sp = cell(p)
ck = Clock()
S = r["search_seed"]
hseeds = assays.world_seeds(H_int(S, HELD_NS), sp.M_held)
pl = plant(p, ph)
rh = ev(ph, pl[None], env, hseeds)
rz = ev(ph, pl[None], env, hseeds, ctrl=Controls(zero_comm=True))
pa, pz = rh.pair_acc()[0], rz.pair_acc()[0]
m, lo, hi = assays.pair_ci(pa); dm, dlo, dhi = assays.pair_ci(pa - pz)
held = {"acc": float(m), "lo99": float(lo), "hi99": float(hi), "zero_comm": float(pz.mean()),
        "comm_delta": float(dm), "comm_delta_lo99": float(dlo), "comm_delta_hi99": float(dhi),
        "sens_act": float(rh.sens_act[0]), "sens_any": float(rh.sens_any[0])}
print("held", {k: round(v, 4) for k, v in held.items()}, flush=True)
# DICT: same plant, only sensor 0 cued (hp_common-style evaluate path via schedule edit)
ep = envs.build(ph, env, hseeds); wp.dict_sched(ep)
from prometheus.ananke.engine import World
M = len(hseeds); wsd = [hseeds[i - (i % 2)] for i in range(M)]
w = World(ph, np.repeat(pl[None], M, 0), wsd, device="cpu", schedule=ep.schedule); w.run(env.T(), graph=False)
dacc = envs.score(ep, w.trace.cpu().numpy()); dpairs = dacc.reshape(M // 2, 2).mean(-1)
dd = assays.pair_ci(pa - dpairs)
held_dict = {"DICT_acc": float(dpairs.mean()), "plant_minus_DICT_ci99": [float(x) for x in dd]}
print("DICT", held_dict, flush=True)
tw = assays.twin_assay(ph, pl[None], env, hseeds[:16], device="cpu")
twin = {k: float(v[0]) for k, v in tw.items()}
pseudo = {"env": r["env"], "result": {"held": held, "twin": twin}}
labels = campaign.classify(pseudo, campaign.CampaignConfig())
print("twin", twin, "\nlabels", labels, flush=True)
# per-generation loss bound: bootstrap M/2 pairs from the plant's 32 held pairs
g = np.random.default_rng(0x57324B4C)
bs = pa[g.integers(0, len(pa), size=(200000, sp.M // 2))].mean(1)
loss = {f"{t:.2f}": float((bs < t).mean()) for t in (0.55, 0.60, 0.62, 0.65, 0.68, 0.70)}
print("P(M-world plant mean < thr)", loss)
out = {"cell": r["cell_id"], "held": held, "held_pairs": pa, "dict": held_dict, "twin_plant": twin,
       "labels_plant": labels, "labels_recorded_champion": r["labels"], "loss_bound": loss, "compute": ck.done()}
print(out["compute"]); save(f"t_v_ruler_{p}.json", out)
