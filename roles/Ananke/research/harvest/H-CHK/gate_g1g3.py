"""Known-answer gate G1 (W-P pipeline on hold_latch / echo_hold, W-P run_ka design) and G3 (W-N P1S mirror
S swap). PLAN_ADDENDUM X1. -> out/gate_g1.json, out/gate_g3.json"""
import os, sys, time, json
import hchk as H
import numpy as np
H.threads1()
from prometheus.ananke import assays, envs, rng
tt, ana, PJ = H.mod("wp_tt"), H.mod("wp_ana"), H.mod("wp_pj")
H.threads1()
t0 = time.time()
HOLD = envs.EnvSpec(family="HOLD", gap=8, cue_len=2, trials=8)
SEEDS = assays.world_seeds(0x611, 64)
OFFS = [3, 4, 5, 6, 7, 8]
TRIALS = list(range(1, 8))
g1 = {"pid": os.getpid()}
ok = True
for nm, fx in (("latch", PJ.latch_fixture), ("echo", PJ.echo_fixture)):
    ph, g = fx()
    chk = tt.check_vs_lens(ph, g, HOLD, SEEDS[:32], 3, 5, device=H.DEV)
    comps = tt.coarse_components(ph)
    names = list(comps)
    n = len(names)
    half = [z for z in tt.all_subsets(n) if z[0] == 0]
    site_mask = [tt.is_site(comps[k]) for k in names]
    per_o = {o: [] for o in OFFS}
    for k in TRIALS:
        res, ep = tt.run_table(ph, g, HOLD, SEEDS, k, OFFS, comps, half, device=H.DEV)
        for o in OFFS:
            per_o[o].append((ana.full_a(res[o], half, n), ep.y[0::2, k], ep.y[1::2, k]))
    rows = {}
    for o in OFFS:
        s = ana.summarize(ana.analyse(per_o[o], names, site_mask), names, P=32, n_boot=500)
        rows[o] = {k: s.get(k) for k in ("eligible", "fS", "fC", "fN", "base_N", "class")}
        want = "fS" if nm == "latch" else "fC"
        good = s[want] == 1.0 and s["base_N"] == 0 and s["class"] == "UNDEFINED"
        rows[o]["pass"] = bool(good)
        ok &= good
        print(nm, o, rows[o], flush=True)
    ok &= all(chk)
    g1[nm] = {"C1_bit_identity": chk, "names": names, "offsets": rows}
g1["PASS"] = bool(ok)
g1["wall_s"] = time.time() - t0
H.dump(g1, "gate_g1.json")
print("G1 PASS", ok, round(time.time() - t0), "s", flush=True)

# G3: W-N P1S mirror S swap (PLAN_ADDENDUM X1/X4)
pr, sr = H.mod("wn_pr"), H.mod("wn_sr")
H.threads1()
pr.nb.install()
ph = pr.physics()
g = pr.body("P1S", ph)
env = pr.nb.spec(1)
seeds = assays.world_seeds(rng.H_int(pr.NS_WN, 0x4E), 512)
TR = list(range(1, env.trials))
t1 = time.time()
ep, nrm, arms, n0, s0 = pr.run_fork(ph, g, env, seeds, ["S1", "S"], TR, offset=-1, device=H.DEV)
g3 = {}
for kd in ("S1", "S"):
    v = sr.swap_verdict_rel(nrm, arms[kd])
    zc = H.z_ci(nrm, arms[kd])
    g3[kd] = {"verdict": v["verdict"], "normal": v["normal"], "swap": v["swap"], "z_wn": v["z"], "z": zc}
    print("G3", kd, v["verdict"], zc, flush=True)
g3["PASS"] = bool(all(g3[k]["verdict"] == "FLIP_REL" and g3[k]["z"]["z"] <= -0.95 for k in ("S1", "S")))
g3["wall_s"] = time.time() - t1
H.dump(g3, "gate_g3.json")
print("G3 PASS", g3["PASS"], flush=True)
