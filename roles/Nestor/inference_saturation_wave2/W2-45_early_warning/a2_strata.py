"""W2-45 a2 (post hoc, descriptive; NOT rule-bearing): split EW false alarms by outcome stratum
(B < 27 vs intermediate 27-162) in each arm, incl. W2-2's in-sample X-TICKET; project FULL's unknown B<27 alarms from the
BANK arms' rates among comparably-unknown runs; intermediate-share comparison. python -B a2_strata.py -> a2_strata.json"""
import json, glob, math, pathlib
HERE = pathlib.Path(__file__).resolve().parent
W = HERE.parent
src = open(HERE / "a1_score.py").read().split("res = {}")[0]   # helpers only, no scoring side effects
ns = {"__file__": str(HERE / "a1_score.py")}
exec(compile(src, "a1_helpers", "exec"), ns)
load, from_traj, from_summary, wilson = ns["load"], ns["from_traj"], ns["from_summary"], ns["wilson"]
out = {}

# X-TICKET in-sample (W2-2 a1 source)
CAMP = W.parent / "campaigns" / "c9x-explore-2026-09-24" / "x_ticket" / "results"
xt = [json.load(open(f)) for f in sorted(glob.glob(str(CAMP / "*.json")))]
arms = {"X-TICKET (in-sample)": [dict(B=r["traj"][-1][2] if r["traj"] else 0, Bxk=None, traj=r["traj"], stop="", epochs=len(r["traj"]), maxA=99) for r in xt]}
for name, p in (("W2-22 FIELD BANK", "W2-22_second_regime/runs_FIELD.jsonl"), ("W2-22 FREE BANK", "W2-22_second_regime/runs_FREE.jsonl"),
                ("W2-37 FIELD BANK", "W2-37_fstar_k1/runs_FIELD.jsonl"), ("W2-37 FREE BANK", "W2-37_fstar_k1/runs_FREE.jsonl")):
    arms[name] = load(W / p)

proj = {}
for name, rs in arms.items():
    d = {"n": len(rs)}
    for strat, f in (("B<27", lambda B: B < 27), ("27-162", lambda B: 27 <= B < 163), (">=163", lambda B: B >= 163)):
        sub = [r for r in rs if f(r["B"])]
        row = {"n": len(sub)}
        for ob in ("EW1", "EW1b", "EW2"):
            k = u = 0
            for r in sub:
                a = from_traj(r["traj"]) if r.get("traj") else from_summary(r)
                if a[ob] is None: u += 1
                elif a[ob]: k += 1
            row[ob] = [k, u]
        d[strat] = row
    # among B<27 runs that WOULD be unknown from summary alone, how many fire (traj-bearing only)?
    unk = [r for r in rs if r["B"] < 27 and r.get("traj") and r["stop"] != "free_cap256"]
    for ob in ("EW1", "EW1b"):
        pool = [r for r in unk if from_summary(r)[ob] is None]
        fire = sum(from_traj(r["traj"])[ob] for r in pool)
        d["B<27 summary-unknown, traj-known " + ob] = [fire, len(pool)]
    out[name] = d
    print(name, json.dumps(d))

# FULL intermediate share vs W2-2 single-law prediction (0.024) and X-TICKET (0/128)
full = load(W / "W2-29_residue" / "runs_FULL.jsonl")
inter = sum(27 <= r["B"] < 163 for r in full); run = sum(r["B"] >= 163 for r in full)
out["FULL_bins"] = {"0": sum(r["B"] == 0 for r in full), "1-4": sum(1 <= r["B"] <= 4 for r in full),
                    "5-26": sum(5 <= r["B"] <= 26 for r in full), "27-162": inter, ">=163": run, "n": len(full),
                    "inter_wilson": wilson(inter, len(full)), "run_wilson": wilson(run, len(full))}
xtB = [a["B"] for a in arms["X-TICKET (in-sample)"]]
out["XT_bins"] = {"27-162": sum(27 <= b < 163 for b in xtB), ">=163": sum(b >= 163 for b in xtB), "n": len(xtB)}
# P(0 intermediates in 128 | FULL rate)
pf = inter / len(full)
out["P_zero_inter_in_128_at_FULL_rate"] = round((1 - pf) ** 128, 4)
# Fisher-ish: two-sided exact for 0/128 vs inter/600 (hypergeometric)
from math import comb
N1, N2, K = 128, len(full), inter
tot = comb(N1 + N2, K)
p0 = comb(N2, K) / tot
out["fisher_p_le_obs_XT0"] = round(p0, 4)
# projection of FULL unknown B<27 alarms using pooled BANK rate among summary-unknown B<27 traj runs
for ob in ("EW1", "EW1b"):
    f = sum(out[n]["B<27 summary-unknown, traj-known " + ob][0] for n in arms if "BANK" in n)
    m = sum(out[n]["B<27 summary-unknown, traj-known " + ob][1] for n in arms if "BANK" in n)
    proj[ob] = {"bank_rate": wilson(f, m), "fire_over_pool": [f, m]}
out["projection_rates"] = proj
json.dump(out, open(HERE / "a2_strata.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in ("FULL_bins", "XT_bins", "P_zero_inter_in_128_at_FULL_rate", "fisher_p_le_obs_XT0", "projection_rates")}, indent=1))
