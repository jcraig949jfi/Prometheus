"""KA5 + KA6 (PLAN.md). KA5: recorded CIs re-derive CHANCE under the rule.
KA6: re-run one inventory verdict per source at its ORIGINAL design (64 worlds,
original namespace, EVERY) and require the recorded swap acc to be reproduced
exactly; must-fail: offset+1 does not reproduce."""
import csv, json, sys
import numpy as np, torch
import runner as R
from prometheus.ananke import assays, lens

torch.set_num_threads(1)
rows = list(csv.DictReader(open(R.HERE / "out" / "inventory.csv")))


def rule_from_ci(nlo, slo, shi):
    if shi < 0.40:
        return "FLIP"
    if slo >= nlo - 0.05:
        return "NO-EFFECT"
    return "CHANCE"


# CIs are rounded to 4 dp in the inventory; allow the boundary to be checked on
# the rounded values, and report any disagreement.
ka5_bad = [r["vid"] for r in rows
           if rule_from_ci(float(r["normal_lo"]), float(r["swap_lo"]), float(r["swap_hi"])) != "CHANCE"]
ka5_mustfail = rule_from_ci(0.70, 0.30, 0.39) == "CHANCE"
out = {"KA5": {"rows": len(rows), "not_rederived": ka5_bad, "pass": not ka5_bad,
               "mustfail_hi039_reads_CHANCE": ka5_mustfail}}


def orig_run(r, off_shift=0):
    ph, env, g = R.load(r["loader"], r["specimen"])
    o = (R.sct_offset(env) if r["offset"] == "" else int(r["offset"])) + off_shift
    ns = int(r["seed_ns"], 16)
    sd = assays.world_seeds(ns, 64)
    Pd = env.period()
    names = R.arm_names(r["arm"]) if hasattr(R, "arm_names") else None
    lab = r["arm"]
    if lab.startswith("pay"):
        fn = lambda w: lens.swap(w, ["Msum"], sub=int(lab[3:]))
    else:
        nm = list(R.ARMS[lab])
        fn = lambda w: lens.swap(w, nm)
    hooks = {k * Pd + o: fn for k in range(env.trials) if k * Pd + o >= 0}
    tr = lens.run(ph, g, env, sd, hooks=hooks, device="cpu")
    trials = range(env.trials) if r["trial_set"] == "all" else range(1, env.trials)
    return lens.ci(lens.trial_acc(tr, trials))


ka6 = {}
for src, pick in (("WF", lambda r: r["source"] == "WF" and r["timing"] == "mid" and r["arm"] == "site_all"),
                  ("WF_pre", lambda r: r["source"] == "WF" and r["timing"] == "pre"),
                  ("WI", lambda r: r["source"] == "WI" and r["arm"] == "S"),
                  ("SCT", lambda r: r["source"] == "SCT")):
    r = next(x for x in rows if pick(x))
    acc = orig_run(r)
    rec = (float(r["swap_m"]), float(r["swap_lo"]), float(r["swap_hi"]))
    same = all(abs(a - b) < 1e-3 for a, b in zip(acc, rec))
    acc1 = orig_run(r, 1)
    same1 = all(abs(a - b) < 1e-3 for a, b in zip(acc1, rec))
    ka6[src] = {"vid": r["vid"], "specimen": r["specimen"][:8], "arm": r["arm"], "offset": r["offset"],
                "recorded": rec, "rerun": acc, "reproduced": same, "mustfail_offset+1_reproduced": same1}
    print(src, ka6[src], flush=True)
out["KA6"] = ka6
json.dump(out, open(R.HERE / "out" / "ka_repro.json", "w"), indent=1, default=float)
print(json.dumps(out["KA5"]))
