"""Aggregate task2_timing.json (+ task1) into the tables of the report."""
import json, collections, pathlib
import numpy as np
H = pathlib.Path(__file__).resolve().parent
d = json.load(open(H / "out/task2_timing.json"))
R = d["rows"]
# falsification check: no row may beat its ceiling
viol_sync = [o for o in R if o["update_mode"] == "sync" and o["held_acc"] > o["ceil_joint_heldset"] + 1e-12]
viol_async = [o for o in R if o["update_mode"] == "async" and o["held_lo99"] > o["ceil_joint"]]
print("sync rows held_acc > exact held-set ceiling:", len(viol_sync), [(o["cell"][:8], o["held_acc"], o["ceil_joint_heldset"]) for o in viol_sync])
print("async rows held lo99 > expected ceiling:", len(viol_async))
sig = [o for o in R if o["SIGNAL"]]
print("SIGNAL rows:", len(sig), "min margin ceil_joint - held_acc:", min(o["ceil_joint"] - o["held_acc"] for o in sig))
print("SIGNAL rows closest to ceiling:", sorted([(round(o["ceil_joint"] - o["held_acc"], 3), o["cell"][:8], o["family"], o["update_mode"], round(o["held_acc"], 3), round(o["ceil_joint"], 3)) for o in sig])[:5])
out = {}
tables = {}
for fam in ("RELAY", "MAJ"):
    N = [o for o in R if o["family"] == fam and not o["SIGNAL"]]
    def cap(o, key):
        return o[key] < o["signal_attainable"]
    rows_cap = [o for o in N if cap(o, "ceil_joint")]
    hard = [o for o in N if o["ceil_joint"] <= 0.55]
    lc_only = [o for o in N if cap(o, "ceil_lc")]
    cue_only = [o for o in N if cap(o, "ceil_cue")]
    hpl = [o for o in N if o["hplant_lc_bound"] is not None and o["hplant_lc_bound"] < 0.60]
    # cause attribution for joint-capped rows
    cause = collections.Counter()
    for o in rows_cap:
        a, b = cap(o, "ceil_lc"), cap(o, "ceil_cue")
        cause["lc alone caps" if a and not b else "cue alone caps" if b and not a else "both alone cap" if a and b else "only jointly"] += 1
    by = collections.Counter((o["topology"], o["update_mode"], o["update_period"] if o["update_mode"] == "sync" else o["update_p"]) for o in rows_cap)
    out[fam] = {"NULL_rows": len(N), "joint_capped_(ceil<SIGNAL-attainable)": len(rows_cap),
                "joint_ceiling_<=.55": len(hard), "lc_component_capped": len(lc_only),
                "cue_component_capped": len(cue_only), "H-PLANT lc_census bound<.60 (evolve, NULL)": len(hpl),
                "cause": dict(cause), "by_topology_mode": {str(k): v for k, v in by.items()},
                "signal_attainable_values": sorted(set(round(o["signal_attainable"], 4) for o in N))}
    if fam == "MAJ":
        G = [o for o in N if "ceil_joint_inward" in o]
        inw_cap = [o for o in G if o["ceil_joint_inward"] < o["signal_attainable"]]
        orig_cap = [o for o in G if o["ceil_joint"] < o["signal_attainable"]]
        out[fam]["graph_rows"] = len(G)
        out[fam]["graph_capped_orig_placement"] = len(orig_cap)
        out[fam]["graph_capped_inward_placement"] = len(inw_cap)
        out[fam]["placement_only_capped"] = len([o for o in orig_cap if o["ceil_joint_inward"] >= o["signal_attainable"]])
        out[fam]["graph_mean_ceiling_orig"] = float(np.mean([o["ceil_joint"] for o in G]))
        out[fam]["graph_mean_ceiling_inward"] = float(np.mean([o["ceil_joint_inward"] for o in G]))
    tables[fam] = sorted(rows_cap, key=lambda o: o["ceil_joint"])
print(json.dumps(out, indent=1))
for fam, T in tables.items():
    print(f"\n{fam} construction-capped NULL rows (joint ceiling < SIGNAL-attainable):")
    print("cell8 | wave | topo | mode | per/p | d | delta | lat b/h | held | lc | cue | joint | att | inward_joint")
    for o in T:
        print(f"{o['cell'][:8]} | {o['wave']} | {o['topology']} | {o['update_mode']} | "
              f"{o['update_period'] if o['update_mode']=='sync' else o['update_p']} | {o['d']} | {o['delta']} | "
              f"{o['lat_base']}/{o['lat_hop']} | {o['held_acc']:.3f} | {o['ceil_lc']:.3f} | {o['ceil_cue']:.3f} | "
              f"{o['ceil_joint']:.3f} | {o['signal_attainable']:.3f} | "
              f"{o.get('ceil_joint_inward', float('nan')):.3f}")
json.dump({"summary": out, "capped_rows": {f: [o["cell"] for o in T] for f, T in tables.items()}},
          open(H / "out/task2_summary.json", "w"), indent=1)
