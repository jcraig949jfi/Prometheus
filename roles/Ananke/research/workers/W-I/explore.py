"""EXPLORATORY (post hoc, not in PLAN): (1) census mid-tick class vs my label at the
same offset; (2) latency retention vs 'latch slack' (ticks between the last channel
carrier label and the readout)."""
import csv, json, pathlib
import numpy as np
from scipy.stats import spearmanr
HERE = pathlib.Path(__file__).parent
OUT = HERE / "out"
S = {s["cell"]: s for s in csv.DictReader(open(OUT / "traj_table.csv"))}
census = {r["cell"]: r for r in csv.DictReader(open(HERE.parent / "W-F/out/census_table.csv"))}
ret = json.load(open(OUT / "robust_tests.json"))["retention"]
res = {"mid": {}, "slack": {}}
for c, s in S.items():
    r = json.load(open(OUT / f"traj_{c}.json"))
    env = r["env"]
    cl = env["cue_len"]
    mid = cl + env["gap"] // 2 if env["family"] == "HOLD" else cl + max(1, (env["delta"] - cl) // 2)
    rows = {int(x["o"]): x for x in csv.DictReader(open(OUT / f"table_{c}.csv"))}
    res["mid"][c] = {"census": census[c]["class"], "mine_at_mid": rows[mid]["reader"], "mid": mid,
                     "trajectory": s["reader"]}
    iv = [o for o in sorted(rows) if o >= cl - 1]
    lastc = max([o for o in iv if rows[o]["reader"] in "CM"], default=None)
    if s["readable"] == "True":
        slack = None if lastc is None else (r["ro_off"] - 1 - lastc)
        res["slack"][c] = {"slack": slack, "ret_latency": ret[c]["latency"], "ret_jitter": ret[c]["jitter"],
                           "family": env["family"], "delta": env["delta"], "traj": s["reader"]}
xs = [(v["slack"], v["ret_latency"], v["ret_jitter"]) for v in res["slack"].values() if v["slack"] is not None]
res["spearman_slack_latency"] = spearmanr([a for a, _, _ in xs], [b for _, b, _ in xs]).correlation
res["spearman_slack_jitter"] = spearmanr([a for a, _, _ in xs], [c for _, _, c in xs]).correlation
res["n_channel_using"] = len(xs)
(OUT / "explore.json").write_text(json.dumps(res, indent=1, default=float))
for c, v in res["mid"].items():
    print(c, v)
for c, v in sorted(res["slack"].items(), key=lambda x: (x[1]["slack"] is None, x[1]["slack"] or 0)):
    print(c, v)
print("spearman slack~latency", res["spearman_slack_latency"], "slack~jitter", res["spearman_slack_jitter"], "n", len(xs))
