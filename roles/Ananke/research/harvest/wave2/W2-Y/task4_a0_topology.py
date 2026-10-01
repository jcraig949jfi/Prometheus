"""W2-Y task 4 (check on W2-U F4): is 'global is worst once ceiling-normalised' an artefact of the light-cone ceiling,
which lets a program address any site on global (engine: random destinations)?  30 A0 RELAY cells per topology
(rng 11), flood ceiling on each cell's exact plant seeds vs W2-U's exact-seed joint ceiling; normalised plant score
(acc-.5)/(ceil-.5) on cells with ceil > .55.  CPU, numpy MC, no engine runs."""
import sys, pathlib, json, collections
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-P"))
from w2p_common import np, envs, assays, hc, Physics, H_int, Clock  # noqa
import flood_ceil as FC
ck = Clock()
U = {o["cell"]: o["plant"]["joint"] for o in json.load(open(HERE.parent / "W2-U/out/task2_a0_ceil.json"))["rows"]}
A0 = [r for r in hc.rows() if r["wave"] == "A0" and r["env"]["family"] == "RELAY" and r["cell_id"] in U]
by = collections.defaultdict(list)
for r in A0: by[r["physics"]["topology"]].append(r)
rs = np.random.default_rng(11)
out = []
for topo, L in sorted(by.items()):
    pick = [L[i] for i in rs.choice(len(L), size=min(30, len(L)), replace=False)]
    for r in pick:
        ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
        seeds = assays.world_seeds(H_int(r["search_seed"], 0x9147), 32)
        f = FC.ceilings(ph, env, seeds, R=8, seed=int(r["cell_id"][:8], 16), envs=envs)
        out.append({"cell": r["cell_id"], "topology": topo, "dest_mode": ph.dest_mode, "plant": r["result"]["plant"]["acc"],
                    "lc_joint": U[r["cell_id"]], "flood": f})
    print(topo, len(pick), ck.done(), flush=True)
summ = {}
for topo in sorted(by):
    o = [x for x in out if x["topology"] == topo]
    def norm(key):
        v = [(x["plant"] - .5) / (x[key] - .5) for x in o if x[key] > .55]
        return round(float(np.mean(v)), 3) if v else None, len(v)
    summ[topo] = {"n": len(o), "mean_lc": round(float(np.mean([x["lc_joint"] for x in o])), 3),
                  "mean_flood": round(float(np.mean([x["flood"] for x in o])), 3),
                  "mean_plant": round(float(np.mean([x["plant"] for x in o])), 3),
                  "norm_lc": norm("lc_joint"), "norm_flood": norm("flood")}
    print(topo, summ[topo])
(HERE / "out/task4_a0_topology.json").write_text(json.dumps({"rows": out, "summary": summ, "compute": ck.done()}, indent=1))
print(ck.done())
