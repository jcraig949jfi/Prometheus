"""PLAN s5 known answers (before any specimen run). Writes out/ka_z.json. 1 torch thread, CPU only.
KA-A: W-L champion n1_s3 (W-O KA1 construction): S must read FLIP_REL with transfer COMPLETE.
KA-B: hold_latch plant on 4ab2ba01: channel_all must read NO_EFFECT_REL.
MUST-FAIL: the latch's site_all fed to the same check must read FLIP_REL (not NO_EFFECT_REL)."""
import json
import os
import sys
import time

import numpy as np
import torch

import zcommon as Z

torch.set_num_threads(1)
import runner as R  # noqa: E402  (W-O)
from prometheus.ananke import assays, c1b, plants  # noqa: E402
from prometheus.ananke import swap_rel as sr  # noqa: E402


def lab(npt, spt, trials):
    keep = np.zeros(npt.shape[1], bool)
    keep[list(trials)] = True
    n = np.where(keep[None], npt, np.nan)
    s = np.where(keep[None], spt, np.nan)
    both = ~np.isnan(n) & ~np.isnan(s)
    a = sr.pair_means(np.where(both, n, np.nan))
    b = sr.pair_means(np.where(both, s, np.nan))
    ok = ~np.isnan(a) & ~np.isnan(b)
    a, b = a[ok], b[ok]
    K = int(round(both.sum() / max(1, 2 * len(a))))
    o = Z.label_arm(a, b, K)
    return {k: o[k] for k in ("label", "certificate", "P", "K", "normal", "DF", "DN", "zci", "transfer", "p_min_used")}


t0, c0 = time.time(), time.process_time()
out = {"cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES")}
ph, env, _ = R.load("c1_row", "4ab2ba014aac967e")
g = plants.plant("hold_latch", ph)
tk = c1b.ticks(env)
off = tk["mid"][0] - tk["t0"][0]
sd = assays.world_seeds(Z.NS ^ 0x2, 512)
tr = list(range(env.trials))
ep, npt, apt, _, _ = R.fork_single(ph, g, env, sd, {"site_all": R.SITE, "channel_all": R.FLIGHT}, off, tr)
ch, si = lab(npt, apt["channel_all"], tr), lab(npt, apt["site_all"], tr)
out["KA_B_latch"] = {"offset": off, "channel_all": ch, "site_all": si, "pass": ch["label"] == "NO_EFFECT_REL"}
out["MUSTFAIL_latch_site_all"] = {"label": si["label"], "as_required": si["label"] == "FLIP_REL"}
print("KA-B", out["KA_B_latch"]["pass"], ch["label"], "| must-fail site_all:", si["label"], flush=True)

import plants_rel as pr  # noqa: E402  (W-N; installs W-L nback envs.build)
pr.nb.install()
phw = pr.nb.m2()[0]
d = json.load(open(pr.WL / "out" / "search_n1_s3.json"))
gw = np.asarray(d["evolve"]["champion"], dtype=np.int64)
envw = pr.nb.spec(d["n"])
TR = list(range(d["n"], envw.trials))
sdw = assays.world_seeds(Z.NS ^ 0x1, 512)
ep, npt, apt, _, _ = R.fork_single(phw, gw, envw, sdw, {"S": ("S",), "site_all": R.SITE, "channel_all": R.FLIGHT}, -1, TR)
v = {k: lab(npt, apt[k], TR) for k in apt}
out["KA_A_champion"] = {"arms": v, "pass": v["S"]["label"] == "FLIP_REL" and v["S"]["transfer"] == "COMPLETE"}
print("KA-A", out["KA_A_champion"]["pass"], {k: (x["label"], x["transfer"], x["zci"]["z"]) for k, x in v.items()}, flush=True)
out["all_pass"] = bool(out["KA_A_champion"]["pass"] and out["KA_B_latch"]["pass"] and out["MUSTFAIL_latch_site_all"]["as_required"])
out["wall_s"], out["cpu_s"] = round(time.time() - t0, 1), round(time.process_time() - c0, 1)
json.dump(out, open(Z.OUT / "ka_z.json", "w"), indent=1, default=float)
print("ALL_PASS", out["all_pass"], out["wall_s"], out["cpu_s"], flush=True)
sys.exit(0 if out["all_pass"] else 3)
