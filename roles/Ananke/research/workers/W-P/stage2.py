"""Stage 2 (PLAN s6): refined parts of the modal minimal decisive set, every other coarse
component lumped into 'rest' (so the partition stays complete and b(z) = a(~z) holds).
python stage2.py <cell> <offset> <split: comma list of coarse comps to split> <trials...>
Writes out/s2_<cell>_o<o>_<split>.json."""
import json, sys, time
import numpy as np, torch
import common
from prometheus.ananke import assays
import tt, ana
torch.set_num_threads(2)
A = slice(None)
name, o, split = sys.argv[1], int(sys.argv[2]), sys.argv[3].split(",")
trials = [int(x) for x in sys.argv[4:]]
ph, env, g, _ = common.load(name)
coarse = tt.coarse_components(ph, include_inert=True)
P, C = ph.payload_width, ph.channels


def parts_of(c):
    if c == "S":
        return {f"S{i}": [("S", (A, i))] for i in range(ph.state_dim)}
    if c == "inbox":
        return {"Acc_sum": [("Acc_sum", (A,))], "Acc_cnt": [("Acc_cnt", (A,))]}
    if c == "Kp":
        L = ph.prog_len
        return {"Kp7": [("Kp", (A, 7))], "Kp_other": [("Kp", (A, slice(0, 7))), ("Kp", (A, slice(8, L)))]}
    if c == "Msum":       # batch-first view [B, LM, N, C, P]
        if C > 1:
            return {f"Msum_ch{k}": [("Msum", (A, A, k))] for k in range(C)}
        return {f"Msum_p{p}": [("Msum", (A, A, A, p))] for p in range(P)}
    if c == "Mcnt":
        if C > 1:
            return {f"Mcnt_ch{k}": [("Mcnt", (A, A, k))] for k in range(C)}
        return {"Mcnt": coarse["Mcnt"]}
    return {c: coarse[c]}


comps = {}
for c in split:
    comps.update(parts_of(c))
rest = [p for c, v in coarse.items() if c not in split for p in v]
if rest:
    comps["rest"] = rest
names = list(comps)
assert len(names) <= 7, names
site_mask = [tt.is_site(comps[k]) if k != "rest" else True for k in names]
half = [z for z in tt.all_subsets(len(names)) if z[0] == 0]
tabs = []
t = time.time()
for k in trials:
    res, ep = tt.run_table(ph, g, env, assays.world_seeds(common.SEED_NS, 256), k, [o], comps, half)
    y = ep.y[:, k]
    tabs.append((ana.full_a(res[o], half, len(names)), y[0::2], y[1::2]))
recs = ana.analyse(tabs, names, site_mask)
import pickle
st1 = pickle.load(open(common.HERE / f"out/recs_{name}.pkl", "rb"))[o]
isN = {(r["k"], r["pair"]) for r in st1 if r["pat"] == "N" and r.get("full")}
for r in recs:
    r["k"] = trials[r["trial"]]
recs = [r for r in recs if (r["k"], r["pair"]) in isN]      # stage-1 N pair-trials only
from collections import Counter
full = [r for r in recs if r.get("full")]
md = Counter(tuple(sorted(r["md"])) if r["md"] else None for r in full)
R = Counter((r["R"], r["fn"]) for r in full)
out = {"cell": name, "offset": o, "split": split, "names": names, "trials": trials, "eligible": len(recs),
       "full": len(full), "wall_s": time.time() - t,
       "md_top": [([list(s) for s in k] if k else None, v / len(full)) for k, v in md.most_common(6)],
       "fn_top": [(list(k[0]), k[1], v / len(full)) for k, v in R.most_common(8)],
       "comp_in_R": {nm: float(np.mean([nm in r["R"] for r in full])) for nm in names}}
print(json.dumps(out, indent=1, default=str))
json.dump(out, open(common.HERE / f"out/s2_{name}_o{o}_{'+'.join(split)}.json", "w"), indent=1, default=str)
