"""E1 dev runs (seeds 0-999 only). python -m ensorain.e1.run_dev <tag> <json spec>
spec: {"arms":[...], "caps":[...], "lams":[0,1], "n_inst":6, "cfg":{arm:{...}}, "econ":{...}}"""
import collections, json, sys
import numpy as np
from .arms import run_jobs


def main():
    tag, spec = sys.argv[1], json.loads(sys.argv[2])
    jobs = []
    for lam in spec.get("lams", [0.0]):
        for cap in spec["caps"]:
            for arm in spec["arms"]:
                for i in range(spec.get("inst0", 0), spec.get("inst0", 0) + spec.get("n_inst", 6)):
                    jobs.append(dict(arm=arm, cap=cap, lam=lam, inst_seed=i, org_seed=0,
                                     cfg=spec.get("cfg", {}).get(arm), econ=spec.get("econ"),
                                     transplant=spec.get("transplant", False)))
    rows = run_jobs(jobs, f"ensorain/runs/e1_dev_{tag}.jsonl")
    agg = collections.defaultdict(list)
    for r in rows:
        if r["status"] == "OK":
            agg[(r["lam"], r["cap"], r["arm"])].append(r)
        else:
            print("NOT OK", r["arm"], r["cap"], r["status"], r.get("reason"))
    print(f"{'lam':>4} {'cap':>4} {'arm':<10} {'U':>7} {'rew':>6} {'comp$':>6} {'steps':>5} {'L1':>5} {'L2':>5} {'L3s':>5} {'L3h':>5} {'r2ho':>6} {'r2s':>6} {'P':>4}")
    for k in sorted(agg):
        v = agg[k]
        f = lambda key: np.mean([r[key] for r in v])
        sr = lambda kk: np.mean([r["ok_" + kk] / max(r["n_" + kk], 1) for r in v])
        print(f"{k[0]:>4} {k[1]:>4} {k[2]:<10} {f('U'):7.0f} {f('reward'):6.0f} {f('comp_energy'):6.1f} {f('steps'):5.0f} {sr('L1'):5.2f} {sr('L2'):5.2f} {sr('L3s'):5.2f} {sr('L3h'):5.2f} {np.median([r['r2_ho'] for r in v]):6.2f} {np.median([r['r2_seen'] for r in v]):6.2f} {f('P_used'):4.0f}")


if __name__ == "__main__":
    main()
