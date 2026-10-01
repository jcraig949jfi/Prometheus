"""W2-1 check B: in C-A3-INTERNALIZE (144 fresh runs, ATOMIC, CARRIED), does the founder LABEL (L) take over
without zero-state-competent genomes, and is world depth >= 20 aligned with L takeover?
Read-only over c_a3_internalize/results/*.json (fields: depth, d0_free, checkpoints[L_share, competent, free, free_in_L]).
"""
import json, pathlib, statistics as st
R = pathlib.Path(__file__).resolve().parents[2] / "campaigns/npe-arc3-2026-09-28/c_a3_internalize/results"
import sys
sys.path.insert(0, str(R.parent))
rows = [json.loads(p.read_text()) for p in sorted(R.glob("*.json"))]
def event(rec):
    last = next((c for c in reversed(rec["checkpoints"]) if c["free"] > 0), None)
    d0_not = bool(rec["d0_free"]) and not any(rec["d0_free"])
    return d0_not and last is not None and last["free_in_L"] >= 0.8 * last["free"] and last["L_share"] >= 0.5
tab = {}
detail = []
for r in rows:
    cps = r["checkpoints"]
    take = any(c["L_share"] >= 0.5 for c in cps)
    run = r["depth"] >= 20
    tab[(take, run)] = tab.get((take, run), 0) + 1
    if take:
        # checkpoint where L first >= 0.5, and competent counts up to then
        i = next(k for k, c in enumerate(cps) if c["L_share"] >= 0.5)
        comp_before = [c["competent"] for c in cps[:i + 1]]
        after = cps[i:]
        detail.append({"cell": r["cell"], "seed": r["seed"], "depth": r["depth"], "event": event(r),
                       "take_epoch": cps[i]["epoch"], "max_comp_upto_take": max(comp_before),
                       "comp_at_take": cps[i]["competent"],
                       "median_comp_after": st.median(c["competent"] for c in after),
                       "n_cp_after_zero_comp": sum(c["competent"] == 0 for c in after), "n_cp_after": len(after),
                       "final_L": cps[-1]["L_share"], "final_comp": cps[-1]["competent"]})
print("takeover(L>=0.5 ever) x runaway(depth>=20):", {str(k): v for k, v in tab.items()})
for d in detail:
    print(d)
ev = [d for d in detail if d["event"]]
print("events:", len(ev), "events with max competent <= 10 up to takeover:", sum(d["max_comp_upto_take"] <= 10 for d in ev))
print("takeovers:", len(detail), "with max competent <= 10 up to takeover:", sum(d["max_comp_upto_take"] <= 10 for d in detail))
print("takeovers ending with 0 competent:", sum(d["final_comp"] == 0 for d in detail))
pathlib.Path(__file__).with_suffix(".json").write_text(json.dumps({"tab": {str(k): v for k, v in tab.items()}, "detail": detail}, indent=1))
