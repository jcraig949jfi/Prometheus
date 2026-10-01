"""W2-AH energy bound for the RELAY economy rows (and MAJ b1), any program.
N(k,m) = max over all emission policies of #trials the SENSOR can serve with >= 1 emission in the useful window
(exact DP, w2ah_common.dp_max_served). Every information path sensor -> actuator starts with a sensor emission,
so per trial P(info) <= P(sensor emits in window). Expected-accuracy bounds (K = trials):
  TV  : acc <= .5 + min(.5, N/K)     any coding (absence may carry the bit: one-sided)
  2S  : acc <= .5 + .5*N/K           two-sided coding (absence uninformative)
KA: relay_flood k=12, m=1 at the sensor -> N must equal the recorded emission count per world (b1 high: 1)."""
from w2ah_common import *
import itertools
res = []
seen = set()
for r in hc.rows():
    if r["wave"] != "B" or r["extra"].get("transect") != "economy" or r["env"]["family"] != "RELAY": continue
    key = (r["extra"]["base"], r["levels"]["economy"])
    if key in seen: continue
    seen.add(key)
    ph, env = cell(r)
    if not ph.economy_on:
        continue
    # minimum sensor->actuator delay: global = lat_base; torus dest-all: actuator at env distance d is in the table
    dmin = ph.lat_base + ph.lat_hop * (1 if ph.topology == "global" else env.d)
    win = relay_window(ph, env, dmin)
    row = {"base": key[0], "economy": key[1], "cE": ph.c_emit * ph.copies(), "e_max": ph.e_max, "inc": ph.e_income,
           "c_op": ph.c_op, "c_mem": ph.c_mem, "period": ph.update_period, "dmin": dmin, "K": env.trials, "N": {}}
    for k, m in itertools.product((0, 1, 2, 3, 4, 5, 6, 12), (0, 1)):
        N = dp_max_served(ph, env, k, m, win)
        row["N"][f"k{k}m{m}"] = N
    res.append(row)
    print(row)
save("bound.json", res)
