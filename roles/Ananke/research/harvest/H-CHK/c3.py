"""C3: mirror (a) vs single-cue-twin (b) S swap at k*Pd-1 (PLAN_ADDENDUM X4). python c3.py <spec> [mustfail]"""
import os, sys, time, json
import numpy as np
import hchk as H
from prometheus.ananke import assays, rng
pr, sr = H.mod("wn_pr"), H.mod("wn_sr")
H.threads1()
pr.nb.install()
spec = sys.argv[1]
mustfail = len(sys.argv) > 2 and sys.argv[2] == "mustfail"
if spec == "P1S":
    ph = pr.physics(); g = pr.body("P1S", ph); n = 1
else:
    ph = pr.nb.m2()[0]
    d = json.load(open(pr.WL / "out" / f"search_{spec}.json"))
    n = d["n"]; g = np.asarray(d["evolve"]["champion"], dtype=np.int64)
H.threads1()
env = pr.nb.spec(n)
seeds = assays.world_seeds(rng.H_int(pr.NS_WN, 0x4E), 512)
TR = list(range(n + (1 if mustfail else 0), env.trials))
t0 = time.time()
res = {"spec": spec, "n": n, "pid": os.getpid(), "trials": TR}


def summ(nrm, sw, s0n, s0s):
    v = sr.swap_verdict_rel(nrm, sw)
    z = H.z_ci(nrm, sw)
    return {"verdict": v["verdict"], "verdict_ungated": v["verdict_ungated"], "normal": v["normal"],
            "swap": v["swap"], "z_wn": v["z"], "z": z}


if not mustfail:
    ep, nrm, arms, n0, s0 = pr.run_fork(ph, g, env, seeds, ["S"], TR, offset=-1, device=H.DEV)
    res["a"] = summ(nrm, arms["S"], n0, s0["S"])
    print(spec, "mirror", res["a"], round(time.time() - t0), flush=True)
# twin mode (b), one episode per scored trial
be = 1 if mustfail else 0
nrm_b = np.full((512, env.trials), np.nan)
sw_b = np.full((512, env.trials), np.nan)
differ = []
for k in TR:
    ep = H.twin_episode(ph, env, seeds, k, n, back_extra=be)
    _, nk, ak, n0k, s0k = pr.run_fork(ph, g, env, seeds, ["S"], [k], offset=-1, device=H.DEV, ep=ep)
    nrm_b[:, k] = nk[:, k]
    sw_b[:, k] = ak["S"][:, k]
    differ.append(float(np.mean(np.sign(n0k[0::2, k]) != np.sign(n0k[1::2, k]))))
res["b_mustfail" if mustfail else "b"] = summ(nrm_b, sw_b, None, None)
res["twin_normal_output_differs_frac"] = dict(zip(TR, differ))
print(spec, "twin", "mustfail" if mustfail else "", res["b_mustfail" if mustfail else "b"], "differ", np.round(differ, 2), round(time.time() - t0), flush=True)
res["wall_s"] = time.time() - t0
H.dump(res, f"c3_{spec}{'_mustfail' if mustfail else ''}.json")
