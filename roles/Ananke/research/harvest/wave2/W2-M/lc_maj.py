"""MAJ light-cone bound (extends H-PLANT lightcone.py to k sensors) + realized placement, on each row's
own HELD worlds (64). For each scored trial: m = number of the 5 sensors whose cue can be processed at the
actuator by the readout tick under the fastest transport of the physics (no loss/caps/jitter, any
neighbour, every site relays at first awake tick; async optimistic). Any program's accuracy is bounded by
mean_trials Bayes(m) (exact k=5,p=.3 table; ties .5). Integration (>.70) needs m>=3 in some trials.
Placement: hop = radius on ring/torus, 1 on graphs/global (W2-A2 c6c rule); far = max sensor distance."""
import w2m_common as c
import numpy as np
from lightcone import earliest           # H-PLANT, unchanged
from prometheus.ananke import envs
from prometheus.ananke.physics import Physics

BT = c.bayes_table()

def row_lc(r, M=64):
    ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
    seeds = c.held_seeds(r, M)
    ep = envs.build(ph, env, seeds)
    si = ep.schedule.sense_idx.numpy(); ri = ep.schedule.read_idx.numpy()[:, 0]
    D = envs.dist_matrix(ph)
    hop = ph.radius if ph.topology in ("ring", "torus") else 1
    Pd = env.period()
    per = ph.update_period if ph.update_mode == "sync" else 1
    cache = {}
    ms = []; nhop1 = []
    for b in range(0, M, 2):
        dd = D[ri[b], si[b]]
        nhop1.append(int((dd <= hop).sum()))
        for k in range(env.trials):
            t0 = k * Pd; ro = int(ep.ro_tick[b, k]); ph0 = t0 % per
            m = 0
            for s in si[b]:
                key = (int(s), ph0)
                if key not in cache:
                    cache[key] = earliest(ph, int(s), ph0, env.cue_len) - ph0
                m += int(cache[key][ri[b]] + t0 <= ro)
            ms.append(m)
    ms = np.array(ms); nh = np.array(nhop1)
    far = D[ri[0::2, None], si[0::2]].max(1)
    frac_multi = float(np.mean(far > hop))
    place = "multi_all" if frac_multi == 1 else ("multi_some" if frac_multi > 0 else "one_hop")
    h = r["result"]["held"]
    return {"cell": r["cell_id"], "wave": r["wave"], "SIGNAL": r["labels"]["SIGNAL"],
            "held": h["acc"], "lo99": h["lo99"], "hi99": h["hi99"],
            "placement": place, "frac_multi": frac_multi, "mean_sensors_one_hop": float(nh.mean()),
            "m_hist": np.bincount(ms, minlength=6).tolist(),
            "lc_bound": float(np.mean([BT[m] for m in ms])),
            "lc_single_bound": float(np.mean([BT[min(m, 1)] for m in ms])),
            "frac_m_ge3": float(np.mean(ms >= 3))}

if __name__ == "__main__":
    ck = c.Clock(); out = []
    for r in c.maj_rows():
        out.append(row_lc(r))
    c.save("lc_maj.json", {"rows": out, "compute": ck.done()})
    import collections
    tab = collections.defaultdict(list)
    for o in out: tab[(o["placement"], o["SIGNAL"])].append(o)
    for k, v in sorted(tab.items()):
        print(k, len(v), "lc_bound median %.3f min %.3f max %.3f" % (np.median([x["lc_bound"] for x in v]), min(x["lc_bound"] for x in v), max(x["lc_bound"] for x in v)),
              "n(lc<=.70)=%d n(lc<.60)=%d" % (sum(x["lc_bound"] <= .70 + 1e-9 for x in v), sum(x["lc_bound"] < .60 for x in v)))
    print(ck.done())
