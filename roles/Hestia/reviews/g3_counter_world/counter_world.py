"""Hestia G3 construction: the FROZEN E1 code (blobs match FREEZE_E1.json), run on two
world ratios E1 did not include. No chiasma file is edited; this script lives in
Hestia's scratchpad. Ratios: R31 (18:6) and R13 (6:18), same 10 frozen eval seeds,
cap 1000, arms O1 O2 O4 O4R O0."""
import sys, json, os, time
sys.path.insert(0, r"C:/Prometheus-worktrees/hestia-boot-2026-10-06")
from multiprocessing import Pool
from chiasma.world import WorldSpec, make_world
from chiasma.runner import run, canonical
RAT = {"R31": dict(n_ydep=18, n_decoy=6), "R13": dict(n_ydep=6, n_decoy=18)}
SEEDS = [2187867196 + i for i in range(10)]
ARMS = ["O1", "O2", "O4", "O4R", "O0"]
def job(a):
    ratio, seed, arm = a
    w = make_world(WorldSpec(**RAT[ratio]), seed)
    r = run(w, arm, 1000)
    return {"ratio": ratio, "seed": seed, "arm": arm, "cap": 1000, "endpoints": r["endpoints"], "receipt_sha256": r["receipt_sha256"]}
if __name__ == "__main__":
    out = os.path.dirname(__file__)
    jobs = [(rt, s, a) for rt in RAT for s in SEEDS for a in ARMS]
    t0 = time.time()
    with Pool(8) as p:
        rows = list(p.imap_unordered(job, jobs))
    with open(os.path.join(out, "rows.jsonl"), "w") as fh:
        for r in rows: fh.write(json.dumps(r, sort_keys=True) + "\n")
    import collections
    c = collections.defaultdict(dict)
    for r in rows: c[(r["ratio"], r["arm"])][r["seed"]] = r["endpoints"]["err_CDE"]
    for rt in RAT:
        def w(a, b): return sum(1 for s in SEEDS if c[(rt, a)][s] < c[(rt, b)][s])
        print(rt, "O4>O1", w("O4", "O1"), "O4>O2", w("O4", "O2"), "O4>O4R", w("O4", "O4R"), "O4>O0", w("O4", "O0"), "O0>O4", w("O0", "O4"),
              "| medians O1 O2 O4 O4R O0:", [sorted(c[(rt, a)].values())[4] for a in ARMS])
    print("wall s", round(time.time() - t0, 1), "runs", len(rows))
