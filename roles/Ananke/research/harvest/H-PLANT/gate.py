"""Known-answer gate (PLAN s1). Exact original code paths, CPU."""
import hp_common as hc  # noqa: F401  (sets CUDA_VISIBLE_DEVICES=-1 first)
from hp_common import Clock, save, row
from prometheus.ananke import assays, campaign, c1b, envs, plants
from prometheus.ananke.physics import Physics

ck = Clock()
res = {}
# G1a: C1 plant_viability row (relay_flood at d9cc, RELAY d3 delta16)
r = row("29b7e63a5fa4a78b")
ph = Physics.from_dict(r["physics"])
env = envs.EnvSpec(**r["env"])
pv = campaign.plant_viability(ph, env, r["search_seed"], device="cpu")
res["G1a_relay_flood_C1_29b7e63a"] = {"recorded": r["result"]["plant"]["acc"], "reproduced": pv["acc"],
                                       "phys_digest": ph.digest(), "detail": pv}
# G1b: C1b F_DA normal (relay_flood)
seeds = assays.world_seeds(c1b.DEV_NS, c1b.H_WORLDS)
E = c1b.fixture_envs()
ph = plants.c1b_da_physics()
run = c1b.evaluate(ph, plants.plant("relay_flood", ph), E["relay_da"], seeds, device="cpu")
res["G1b_relay_flood_F_DA"] = {"recorded": 1.0, "reproduced": c1b.ci(run.pairs)[0]}
# G2: C1b F_echo normal (echo_hold)
ph = plants.c1b_echo_physics()
run = c1b.evaluate(ph, plants.echo_hold(ph)[None], E["hold"], seeds, device="cpu")
res["G2_echo_hold_F_echo"] = {"recorded": 1.0, "reproduced": c1b.ci(run.pairs)[0]}
ok = True
for k, v in res.items():
    v["diff"] = abs(v["reproduced"] - v["recorded"])
    v["pass"] = v["diff"] <= 0.02
    ok &= v["pass"]
    print(k, v["recorded"], v["reproduced"], "PASS" if v["pass"] else "FAIL")
res["GATE"] = "PASS" if ok else "FAIL"
res["compute"] = ck.done()
print(res["GATE"], res["compute"])
save("gate.json", res)
