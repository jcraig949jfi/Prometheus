"""V instrument (ruler attainability) at 6f82f9c7: run the known-competent P-FLIP plant through C1's own
held-out protocol (HELD_NS seeds, M_held 64, zero-comm control, twin assay on 16) and campaign.classify.
Also: candidate stepping stones (relay_flood, hold_latch, plant ablations) on the same held worlds."""
from w2d_common import *
from prometheus.ananke.search import HELD_NS
from prometheus.ananke.engine import Controls
from prometheus.ananke import campaign, plants
r, ph, env, sp = flip_cell()
ck = Clock()
S = r["search_seed"]
hseeds = assays.world_seeds(H_int(S, HELD_NS), sp.M_held)
cands = {"plant": hp_plants.p_flip(ph), "mf_teacher": hp_plants.p_flip(ph, "mf_teacher"),
         "mf_readout_no_m": hp_plants.p_flip(ph, "mf_readout_no_m"),
         "relay_flood": plants.plant("relay_flood", ph), "hold_latch": plants.plant("hold_latch", ph)}
names = list(cands); pop = np.stack([cands[k] for k in names])
rh = assays.evaluate(ph, pop, env, hseeds, device="cpu")
rz = assays.evaluate(ph, pop, env, hseeds, ctrl=Controls(zero_comm=True), device="cpu")
out = {"held": {}}
for i, k in enumerate(names):
    pa, pz = rh.pair_acc()[i], rz.pair_acc()[i]
    m, lo, hi = assays.pair_ci(pa); dm, dlo, dhi = assays.pair_ci(pa - pz)
    out["held"][k] = {"acc": float(m), "lo99": float(lo), "hi99": float(hi), "zero_comm": float(pz.mean()),
                      "comm_delta": float(dm), "comm_delta_lo99": float(dlo), "comm_delta_hi99": float(dhi),
                      "sens_act": float(rh.sens_act[i]), "sens_any": float(rh.sens_any[i])}
    print(k, {kk: round(v, 3) for kk, v in out["held"][k].items()})
tw = assays.twin_assay(ph, pop[:1], env, hseeds[:16], device="cpu")
out["twin_plant"] = {k: float(v[0]) for k, v in tw.items()}
pseudo = {"env": r["env"], "result": {"held": out["held"]["plant"], "twin": out["twin_plant"]}}
out["labels_plant"] = campaign.classify(pseudo, campaign.CampaignConfig())
out["labels_recorded_champion"] = r["labels"]
out["compute"] = ck.done()
print(out["twin_plant"], out["labels_plant"], out["compute"])
save("t_v_ruler.json", out)
