"""W2-1 check D: what do the 8 C-A3-INTERNALIZE events look like? For each event run: checkpoints with any state-free
genome, max state-free count, max state-free share of competent, SF share at the final checkpoint, and whether the first
SF checkpoint is strictly after the first L>=0.5 checkpoint. Read-only."""
import json, pathlib
R = pathlib.Path(__file__).resolve().parents[2] / "campaigns/npe-arc3-2026-09-28/c_a3_internalize"
ev = json.loads((R / "VERDICT.json").read_text())["event_runs"]
out = []
for cell, seed in ev:
    r = json.loads((R / "results" / ("%s_%d.json" % (cell, seed))).read_text())
    cps = r["checkpoints"]
    t = next(k for k, c in enumerate(cps) if c["L_share"] >= 0.5)
    f = next(k for k, c in enumerate(cps) if c["free_in_L"] > 0)
    sfc = [c for c in cps if c["free"] > 0]
    maj = [c for c in cps if c["competent"] >= 10 and c["free"] * 2 > c["competent"]]
    fin = cps[-1]
    out.append({"run": "%s %d" % (cell, seed), "d0_epoch": r["d0_epoch"], "takeover_epoch": cps[t]["epoch"],
                "first_SF_epoch": cps[f]["epoch"], "SF_strictly_after_takeover": f > t,
                "n_cp_with_SF": len(sfc), "max_SF": max(c["free"] for c in cps),
                "n_cp_SF_majority_of_competent(>=10)": len(maj),
                "final": (fin["L_share"], fin["competent"], fin["free"])})
for o in out: print(o)
print("strictly after:", sum(o["SF_strictly_after_takeover"] for o in out), "/", len(out))
print("events where SF ever majority (>=10 competent):", sum(o["n_cp_SF_majority_of_competent(>=10)"] > 0 for o in out))
print("events with max SF <= 3 genomes:", sum(o["max_SF"] <= 3 for o in out))
pathlib.Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1))
