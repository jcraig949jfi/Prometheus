"""W2-17 a4: in-world (realized) causal offspring per individual, by the side its parent copied from,
from the replay birth logs (r3_out). A node is 'S0-born' if its causal birth edge was written by a
parent sitting at side 0, 'S1-born' if at side 1. m = mean causal children of nodes born <= stop-15
(truncation guard). Also the heritability of copy side (P(child copies at side s | parent copied at s))
and the share of S0 edges among all causal edges by run class."""
import json, pathlib, sys
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from r2_replay import RUNS

out = {}
agg = {c: {"S0": [0, 0], "S1": [0, 0], "edges": [0, 0], "trans": {"00": 0, "01": 0, "10": 0, "11": 0}} for c in ("RUN", "CTL")}
for label in RUNS:
    f = HERE / "r3_out" / (label + ".json")
    d = json.loads(f.read_text())
    B = {int(k): v for k, v in d["births"].items()}
    stop = d["epochs_replayed"]
    kids = {}
    for k, v in B.items():
        if v["c"]:
            kids.setdefault(v["p"], []).append(k)
    cls = "RUN" if d["recorded_final_depth"] >= 22 else "CTL"
    rec = {"S0": [0, 0], "S1": [0, 0]}
    for k, v in B.items():
        if not v["c"] or v["e"] > stop - 15:
            continue
        t = "S%d" % v["pside"]
        n = len(kids.get(k, []))
        rec[t][0] += 1; rec[t][1] += n
        agg[cls][t][0] += 1; agg[cls][t][1] += n
        for kk in kids.get(k, []):
            agg[cls]["trans"]["%d%d" % (v["pside"], B[kk]["pside"])] += 1
    for v in B.values():
        if v["c"]:
            agg[cls]["edges"][v["pside"]] += 1
    out[label] = {"class": cls, "n_S0_born": rec["S0"][0], "m_S0": round(rec["S0"][1] / rec["S0"][0], 3) if rec["S0"][0] else None,
                  "n_S1_born": rec["S1"][0], "m_S1": round(rec["S1"][1] / rec["S1"][0], 3) if rec["S1"][0] else None}
    print(label, out[label])
summ = {}
for c, a in agg.items():
    t = a["trans"]
    summ[c] = {"m_S0_born": round(a["S0"][1] / max(1, a["S0"][0]), 3), "n_S0_born": a["S0"][0],
               "m_S1_born": round(a["S1"][1] / max(1, a["S1"][0]), 3), "n_S1_born": a["S1"][0],
               "share_S0_edges": round(a["edges"][0] / max(1, sum(a["edges"])), 3),
               "P_child_S0_given_parent_S0": round(t["00"] / max(1, t["00"] + t["01"]), 3),
               "P_child_S1_given_parent_S1": round(t["11"] / max(1, t["11"] + t["10"]), 3), "trans": t}
print(json.dumps(summ, indent=1))
(HERE / "a4_insitu_m.json").write_text(json.dumps({"per_run": out, "pooled": summ}, indent=1))
