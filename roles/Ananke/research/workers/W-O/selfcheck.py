"""W-O selfcheck: fork_single == lens_swap.run_arms SINGLE (readout S0, every trial),
lens_swap.selfcheck (EVERY + SINGLE vs lens.run), and a must-fail input (fork at
offset+1 compared against run_arms at offset must NOT be identical).
Also times one M=512 group. Usage: python selfcheck.py <threads>"""
import json, sys, time
import numpy as np, torch
import runner as R
from prometheus.ananke import lens_swap

TH = int(sys.argv[1]) if len(sys.argv) > 1 else 2
torch.set_num_threads(TH)
out = {}
cid = "4271681452d29aee"
ph, env, g = R.load("c1_row", cid)
off = 9
sd = R.seeds(64, R.NS ^ 0x5C)
trials = list(range(env.trials))
arms = {"site_all": R.SITE, "channel_all": R.FLIGHT, "S": ("S",), "pay0": ("pay", 0)}
ep, npt, apt, n0, s0 = R.fork_single(ph, g, env, sd, arms, off, trials)
al = [lens_swap.Arm("normal")]
for lab in ("site_all", "channel_all", "S"):
    al += [lens_swap.Arm(f"{lab}#{k}", tuple(arms[lab]), off, k) for k in trials]
r = lens_swap.run_arms(ph, g, env, sd, al, chunk=16)
ok = {"normal": bool(np.array_equal(n0, r.s0["normal"]))}
for lab in ("site_all", "channel_all", "S"):
    ok[lab] = all(np.array_equal(s0[lab][:, k], r.s0[f"{lab}#{k}"][:, k]) for k in trials)
# pay0 SINGLE vs lens.run with lens.swap(sub=0) at one trial each
Pd = env.period()
pay_ok = True
for k in trials[:4]:
    t = k * Pd + off
    if t < 0:
        continue
    tr = R.lens.run(ph, g, env, sd, hooks={t: lambda w: R.lens.swap(w, ["Msum"], sub=0)})
    ro = ep.ro_tick[:, k]
    pay_ok &= bool(np.array_equal(tr.trace[ro, np.arange(64), ep.ro_slot[:, k]], s0["pay0"][:, k]))
ok["pay0_first4"] = pay_ok
out["fork_vs_run_arms"] = ok
# must-fail: fork one tick later
_, _, _, _, s0b = R.fork_single(ph, g, env, sd, {"site_all": R.SITE}, off + 1, trials)
out["mustfail_offset_plus1_identical"] = all(np.array_equal(s0b["site_all"][:, k], r.s0[f"site_all#{k}"][:, k]) for k in trials)
out["lens_swap_selfcheck"] = lens_swap.selfcheck(ph, g, env, sd, off, 5)
# timing at M=512
sd5 = R.seeds()
t0 = time.time()
R.fork_single(ph, g, env, sd5, {"site_all": R.SITE, "channel_all": R.FLIGHT, "joint": R.SITE + R.FLIGHT}, off, trials)
out["t_fork_3arms_512"] = time.time() - t0
t0 = time.time()
R.every_arms(ph, g, env, sd5, {"site_all": R.SITE, "channel_all": R.FLIGHT, "joint": R.SITE + R.FLIGHT}, off)
out["t_every_3arms_512"] = time.time() - t0
out["T"], out["Pd"], out["trials"], out["threads"] = env.T(), Pd, env.trials, TH
print(json.dumps(out, indent=1))
json.dump(out, open(R.HERE / "out" / "selfcheck.json", "w"), indent=1)
