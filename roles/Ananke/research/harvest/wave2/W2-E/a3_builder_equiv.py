"""A3: Is W-L's n=0 HOLD builder equivalent to envs.build HOLD? Exact test:
envs.build with FAMILY_ID['HOLD'] rebound to NBACK_ID+0 must reproduce
build_nback(n=0) bit for bit (schedule, ro_tick, y, scored). Then cross-
evaluate M2 (4ab2ba01) and W-L n0_s0 champions under both builders."""
from w2e_common import *
sys.path.insert(0, str(ROOT / "roles/Ananke/research/workers/W-L"))
import nback as nb
ck = Clock()
ph, env, g_m2, r_m2 = nb.m2()
spec0 = nb.spec(0)
S = seeds(H_int(NS, 0xA3), 256)
epA = nb.build_nback(ph, spec0, S)
old = envs.FAMILY_ID["HOLD"]
envs.FAMILY_ID["HOLD"] = nb.NBACK_ID + 0
epB = envs.build(ph, env, S)
envs.FAMILY_ID["HOLD"] = old
same = {
    "sense_idx": bool(torch.equal(epA.schedule.sense_idx, epB.schedule.sense_idx)),
    "sense_val": bool(torch.equal(epA.schedule.sense_val, epB.schedule.sense_val)),
    "read_idx": bool(torch.equal(epA.schedule.read_idx, epB.schedule.read_idx)),
    "ro_tick": bool((epA.ro_tick == epB.ro_tick).all()),
    "y": bool((epA.y == epB.y).all()), "scored": bool((epA.scored == epB.scored).all()),
}
out = {"exact_identity_with_rekeyed_family_id": same, "env_m2": env.to_dict()}
wl = json.load(open(ROOT / "roles/Ananke/research/workers/W-L/out/search_n0_s0.json"))
g_wl = np.asarray(wl["evolve"]["champion"])
res = {}
for name, g in [("M2_4ab2ba01", g_m2), ("WL_n0_s0", g_wl)]:
    a_env, _, _, _ = run(ph, g, env, S)
    a_zc, _, _, _ = run(ph, g, env, S, ctrl=Controls(zero_comm=True))
    nb.install()
    a_nb, _, _, _ = run(ph, g, spec0, S)
    envs.build = nb._ORIG_BUILD
    res[name] = {"envs_HOLD": ci(pairs(a_env)), "wl_builder_n0": ci(pairs(a_nb)), "envs_zero_comm": ci(pairs(a_zc))}
out["cross_eval"] = res
out["wl_n0_s0_decompiled"] = decompile(ph, g_wl[0])
out["clock"] = ck.done(); save("a3_builder_equiv.json", out); print(json.dumps(out, indent=1))
