"""W2-2 a2: is the depth gap a property of the lineage or of the ruler? (read-only)
Joins three rulers on the same runs: world depth (max P-11 chain anywhere), founder-certified births B,
and (X-TICKET only) anc0 occupancy. Sources: x_ticket, x_decay (f dose), x_stall_f0 (f=0), x_sterile.
python -B a2_rulers.py -> a2_rulers.json
"""
import json, glob, pathlib
HERE = pathlib.Path(__file__).resolve().parent
C = HERE.parents[1] / "campaigns" / "c9x-explore-2026-09-24"
L = lambda p: [json.load(open(f)) for f in sorted(glob.glob(str(C / p)))]
out = {}
TK = L("x_ticket/results/*.json")
rows = [dict(src="x_ticket", f=1.0, B=r["traj"][-1][2], depth=r["depth"], last=max([e + 1 for e in range(300) if r["traj"][e][2] > (r["traj"][e - 1][2] if e else 0)], default=0),
             A300=r["traj"][-1][1]) for r in TK]
rows += [dict(src="x_decay", f=r["f"], B=r["cbirths"], depth=r["depth"], last=r["last_birth"]) for r in L("x_decay/results/*.json")]
rows += [dict(src="x_stall_f0", f=0.0, B=r["cbirths"], depth=None, last=r["last_birth_epoch"], alive100=r["n_members"]) for r in L("x_stall_f0/results/*.json")]

def bins(v):
    edges = [1, 2, 3, 5, 9, 17, 33, 65, 129, 257, 10 ** 9]
    return {f"{edges[i]}-{edges[i+1]-1}": sum(edges[i] <= x < edges[i + 1] for x in v) for i in range(len(edges) - 1)}

out["B_hist_by_f"] = {}
for f in (1.0, 0.25, 0.0):
    v = [r["B"] for r in rows if r["f"] == f and r["B"] > 0]
    out["B_hist_by_f"][str(f)] = dict(n_copied=len(v), n_runs=sum(r["f"] == f for r in rows), hist=bins(v),
                                      intermediate_27_162=sum(27 <= x <= 162 for x in v), ge163=sum(x >= 163 for x in v))
out["last_birth_by_f"] = {str(f): sorted(r["last"] for r in rows if r["f"] == f and r["B"] > 0 and r["last"] >= 20) for f in (1.0, 0.25, 0.0)}
d = [r for r in rows if r["depth"] is not None]
out["depth_vs_B"] = dict(
    n=len(d),
    depth_ge20=sum(r["depth"] >= 20 for r in d),
    depth_ge20_with_B_lt20=[(r["src"], r["f"], r["B"], r["depth"]) for r in d if r["depth"] >= 20 and r["B"] < 20],
    depth_gt_B=sum(r["depth"] > r["B"] for r in d),
    depth5_19=[(r["src"], r["f"], r["B"], r["depth"]) for r in d if 5 <= r["depth"] < 20],
    B_ge27_depth_lt20=[(r["src"], r["f"], r["B"], r["depth"]) for r in d if r["B"] >= 27 and r["depth"] < 20])
# burst class: B in 1..26 regardless of depth; depth>=5 cut inside it
burst = [r for r in d if 1 <= r["B"] <= 26]
out["burst_class_depth_split"] = dict(n=len(burst), depth_ge5=sum(r["depth"] >= 5 for r in burst),
                                      depth_ge5_and_B_ge_depth=sum(r["depth"] >= 5 and r["B"] >= r["depth"] for r in burst))
# X-TICKET occupancy
out["ticket_A300"] = sorted((r["A300"], r["B"], r["depth"]) for r in rows if r["src"] == "x_ticket" and (r["B"] >= 5 or r["depth"] >= 5))
# stall_f0 large lineages with no certified member alive at 100
out["f0_large_lineages"] = sorted((r["B"], r["last"], r["alive100"]) for r in rows if r["src"] == "x_stall_f0" and r["B"] >= 15)
# x_sterile: run-level child fertility vs outcome (g=1 / g=0), cluster level
ST = L("x_sterile/results/*.json")
out["sterile_runlevel"] = {}
for g in (1.0, 0.0):
    for lab, cond in (("depth>=5", lambda r: r["depth"] >= 5), ("depth<5", lambda r: r["depth"] < 5)):
        sub = [r for r in ST if r["g"] == g and cond(r) and r["assayed"] > 0]
        fr = sorted(round(r["fertile"] / r["assayed"], 2) for r in sub)
        out["sterile_runlevel"][f"g{g}_{lab}"] = dict(n_runs=len(sub), fert_children=sum(r["fertile"] for r in sub),
                                                      assayed=sum(r["assayed"] for r in sub), run_fracs=fr,
                                                      median=fr[len(fr) // 2] if fr else None)
json.dump(out, open(HERE / "a2_rulers.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:6000])
