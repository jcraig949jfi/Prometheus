"""KA1-KA3 (PLAN.md), each with a must-fail input.
KA1 W-L champion n1_s3: S, site_all SINGLE must be FLIP; channel_all NO-EFFECT.
KA2 hold_latch plant on 4ab2ba01 physics/env: channel_all NO-EFFECT, site_all FLIP.
KA3 latch site_all swap on a fixed random half of pairs must read CHANCE."""
import json, sys
import numpy as np, torch
import runner as R
torch.set_num_threads(1)
import plants_rel as pr  # W-N (imports W-L nback); imported, not edited
from prometheus.ananke import c1b, plants

out = {}
# ---------------- KA2 / KA3 first (plain envs.build)
ph, env, _ = R.load("c1_row", "4ab2ba014aac967e")
g = plants.plant("hold_latch", ph)
tk = c1b.ticks(env)
off = tk["mid"][0] - tk["t0"][0]
sd = R.seeds(512, R.NS ^ 0x2)
trials = list(range(env.trials))
ep, npt, apt, n0, s0 = R.fork_single(ph, g, env, sd, {"site_all": R.SITE, "channel_all": R.FLIGHT}, off, trials)
vs, vc = R.verdicts(npt, apt["site_all"], trials), R.verdicts(npt, apt["channel_all"], trials)
out["KA2"] = {"offset": off, "site_all": vs, "channel_all": vc,
              "pass": vs["abs"] == "FLIP" and vc["abs"] == "NO-EFFECT",
              "channel_identical_to_normal": bool(np.array_equal(np.nan_to_num(apt["channel_all"], nan=-1),
                                                                  np.nan_to_num(np.where(np.isnan(apt["channel_all"]), np.nan, npt), nan=-1))),
              "mustfail_NOEFFECT_check_fed_site_all": vs["abs"] == "NO-EFFECT"}
rng = np.random.default_rng(12345)
half = rng.random(len(sd) // 2) < 0.5
mask = np.repeat(half, 2)
mix = np.where(mask[:, None], apt["site_all"], np.where(np.isnan(apt["site_all"]), np.nan, npt))
vm = R.verdicts(npt, mix, trials)
out["KA3"] = {"half_frac": float(half.mean()), "mixture": vm, "pass": vm["abs"] == "CHANCE",
              "mustfail_all_pairs_reads_CHANCE": vs["abs"] == "CHANCE"}
print("KA2", out["KA2"]["pass"], vs["abs"], vc["abs"], vs["normal"], vs["swap"], vc["swap"], flush=True)
print("KA3", out["KA3"]["pass"], vm["abs"], vm["swap"], flush=True)
# ---------------- KA1: W-L champion (nback envs.build installed)
pr.nb.install()
phw = pr.nb.m2()[0]
d = json.load(open(pr.WL / "out" / "search_n1_s3.json"))
n_ = d["n"]
gw = np.asarray(d["evolve"]["champion"], dtype=np.int64)
envw = pr.nb.spec(n_)
TR = list(range(n_, envw.trials))
sdw = R.seeds(512, R.NS ^ 0x1)
ep, npt, apt, n0, s0 = R.fork_single(phw, gw, envw, sdw, {"S": ("S",), "site_all": R.SITE, "channel_all": R.FLIGHT}, -1, TR)
v = {k: R.verdicts(npt, apt[k], TR) for k in apt}
out["KA1"] = {"verdicts": v, "pass": v["S"]["abs"] == "FLIP" and v["site_all"]["abs"] == "FLIP" and v["channel_all"]["abs"] == "NO-EFFECT",
              "mustfail_FLIP_check_fed_channel_all": v["channel_all"]["abs"] == "FLIP"}
print("KA1", out["KA1"]["pass"], {k: (x["abs"], x["normal"][0], x["swap"]) for k, x in v.items()}, flush=True)
json.dump(out, open(R.HERE / "out" / "ka_plants.json", "w"), indent=1, default=float)
