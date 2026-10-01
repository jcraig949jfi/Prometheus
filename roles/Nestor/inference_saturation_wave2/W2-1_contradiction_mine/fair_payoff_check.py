"""W2-1 check A: does robust (state-free-like) copying APPEAR and SWEEP without payoff?
Read-only over X-A3-FAIR results (ATOMIC runner, cells 7ae3/ffa6, 24 seeds/cell/world, 2000 epochs).
ZERO world = registers of BOTH organisms reset to zero before EVERY pair interaction (lib/reset_axis.py:44-45,63-66),
so a newborn never runs in victim registers: state-freedom earns nothing there (no U-W7 payoff).
Unit: distinct donor genomes per checkpoint (run_fair.py:117-123). ROBUST = competent from R1 or R2 (run_fair.py:94-95).
"""
import json, pathlib, collections
R = pathlib.Path(__file__).resolve().parents[2] / "campaigns/npe-arc3-2026-09-28/x_a3_fair/results"
out = {}
for w in ("CARRIED", "ZERO", "CONST5A"):
    rows = [json.loads(p.read_text()) for p in sorted(R.glob(w + "_*.json"))]
    agg = collections.Counter()
    traj = []
    for r in rows:
        cps = [c for c in r["checkpoints"] if c["donors"] > 0]
        if not cps:
            continue
        agg["donor_runs"] += 1
        f = cps[0]
        f_rob = f["classes"]["ROBUST"]
        agg["first_cp_has_robust"] += f_rob > 0
        agg["first_cp_robust_majority"] += f_rob * 2 > f["donors"]
        # appearance: first checkpoint had no robust donor; robust appears later
        exp = 0; app = None
        if f_rob == 0:
            agg["eligible_for_appearance"] += 1
            for c in cps:
                if c["classes"]["ROBUST"] > 0:
                    app = c["epoch"]; break
                exp += c["donors"]
            agg["appeared_later"] += app is not None
            agg["exposure_donor_cp"] += exp if app is None else exp
        last = r["checkpoints"][-1]
        big = [c for c in cps if c["donors"] >= 25]
        traj.append({"seed": r["seed"], "cell": r["cell"], "depth": r["depth"], "first_epoch": f["epoch"],
                     "first": (f_rob, f["donors"]), "last": (last["classes"]["ROBUST"], last["donors"]),
                     "max_rob_share_big": max((c["classes"]["ROBUST"] / c["donors"] for c in big), default=None),
                     "appear_epoch": app})
        if r["depth"] >= 20:
            agg["L4"] += 1
            agg["L4_last_robust_majority"] += last["donors"] > 0 and last["classes"]["ROBUST"] * 2 > last["donors"]
            agg["L4_last_any_robust"] += last["classes"]["ROBUST"] > 0
        if big:
            agg["runs_with_big_cp"] += 1
            agg["big_any_robust"] += any(c["classes"]["ROBUST"] > 0 for c in big)
            agg["big_robust_majority_ever"] += any(c["classes"]["ROBUST"] * 2 > c["donors"] for c in big)
            agg["big_first_robust_majority"] += big[0]["classes"]["ROBUST"] * 2 > big[0]["donors"]
    tot_last = sum(t["last"][1] for t in traj); rob_last = sum(t["last"][0] for t in traj)
    out[w] = {"agg": dict(agg), "pooled_last_robust_share": round(rob_last / tot_last, 3) if tot_last else None,
              "runs": traj}
for w, v in out.items():
    print(w, v["agg"], "pooled_last_robust_share", v["pooled_last_robust_share"])
    for t in v["runs"]:
        if t["depth"] >= 20 or (t["max_rob_share_big"] or 0) > 0.5:
            print("   ", t)
pathlib.Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1))
