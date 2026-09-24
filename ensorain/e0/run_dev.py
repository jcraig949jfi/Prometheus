"""Dev-seed engineering runs (seeds 0-999 only; PREREG_E0 s6). Usage:
python -m ensorain.e0.run_dev <tag> <json-econ> [arms] [caps] [n_inst]"""
import json, sys
import numpy as np
from .arms import run_jobs, TT_FIXED_CONST


def main():
    tag = sys.argv[1]
    econ = json.loads(sys.argv[2])
    arms = sys.argv[3].split(",") if len(sys.argv) > 3 else ["RANDOM","NOMEM","LRU","HASH","KNN","ADDITIVE","RF","LOWRANK","TT_FIXED","TT_PLANTED","DICT_UNCAP","ORACLE","TT_SVD_INJECT"]
    caps = [int(c) for c in sys.argv[4].split(",")] if len(sys.argv) > 4 else [96, 168, 384]
    n_inst = int(sys.argv[5]) if len(sys.argv) > 5 else 8
    jobs = []
    for lam in (0.0, 1.0):
        for cap in caps:
            for arm in arms:
                for i in range(n_inst):
                    jobs.append(dict(arm=arm, cap=cap, lam=lam, class_seed=0, inst_seed=i, org_seed=0, econ=econ, tuned=dict(TT_FIXED_CONST)))
    rows = run_jobs(jobs, f"ensorain/runs/dev_{tag}.jsonl")
    import collections
    agg = collections.defaultdict(list)
    for r in rows:
        if r["status"] == "OK":
            agg[(r["lam"], r["cap"], r["arm"])].append(r)
    print(f"{'lam':>4} {'cap':>4} {'arm':<14} {'harv':>8} {'steps':>6} {'acc':>5} {'r2unv':>6} {'kflops':>7}")
    for k in sorted(agg):
        v = agg[k]
        print(f"{k[0]:>4} {k[1]:>4} {k[2]:<14} {np.mean([r['harvest'] for r in v]):8.1f} {np.mean([r['steps'] for r in v]):6.0f} {np.mean([r['dec_acc'] for r in v]):5.2f} {np.nanmean([r['r2_unv'] for r in v]):6.2f} {np.mean([r['flops'] for r in v])/1e3:7.1f}")


if __name__ == "__main__":
    main()
