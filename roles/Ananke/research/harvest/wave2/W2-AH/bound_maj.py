"""W2-AH: per-SENSOR energy capacity on the MAJ b1 economy 'high' row (each of the 5 sensors is an independent
emitter with its own E). N(k,m) = max #trials a sensor can vote in (exact DP; window cue onset .. ro - lat_base)."""
from w2ah_common import *
import itertools
r = [r for r in hc.rows() if r["wave"] == "B" and r["extra"].get("transect") == "economy" and r["env"]["family"] == "MAJ"
     and r["extra"]["base"] == 1 and r["levels"]["economy"] == "high"][0]
ph, env = cell(r)
win = relay_window(ph, env, ph.lat_base)
N = {f"k{k}m{m}": dp_max_served(ph, env, k, m, win) for k, m in itertools.product((1, 3, 4, 5, 6, 8, 12), (0, 1))}
print("cE", ph.c_emit * ph.copies(), "K", env.trials, "period", env.period(), N)
save("bound_maj.json", {"cell": r["cell_id"], "N": N})
