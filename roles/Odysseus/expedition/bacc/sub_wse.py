"""bacc substrate S1: WSE/Proteus tape VM, W2_K2 shelf parents (origin: R4_A-001).

    python3 sub_wse.py [--smoke] [--skip-repro]    -> wse_result.json

A. recompute R4's counts from its committed-in-worktree runs_N.jsonl (read only)
B. re-run 2 parents x 8 walkers with R4's own walks.run_walker (in memory) and compare record-for-record
C. bacc run on all 19 shelf parents
"""
import json
import os
import sys
import time
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
R4 = os.path.abspath(os.path.join(HERE, "..", "..", "frontier", "poi", "runs", "R4_A-001"))
sys.path.insert(0, HERE)
sys.path.insert(0, R4)
import bacc  # noqa: E402
import r4lib as L  # noqa: E402
import walks  # noqa: E402

EPS = L.episodes()
EXP = L.expected_vector(EPS)
_TEMPLATE = None


def evaluate(m):
    a = L.answers(m, EPS)
    return a, L.score(a, EXP)


def mutate(m, rng, j):
    op = L.OPS[j % len(L.OPS)] if j >= 0 else None
    c, _ = L.one_edit(m, L.SplitMix64(rng.getrandbits(64)), name=op)
    return c


def gkey(m):
    return L.digest(m)


def neutral(s, s0):
    return abs(s - s0) <= L.BAND + L.EPS


def improving(s, s0):
    return s > s0 + L.BAND + L.EPS


def sample(rng):
    t = walks.shelf_parents()[0][1]
    c = dict(t)
    n = rng.randint(8, min(46, t["tape_words"] // 4))
    c["genome"] = [rng.getrandbits(32) for _ in range(4 * n)]
    return c


def hamming(a, b):
    return sum(1 for x, y in zip(a, b) if x != y)


SPEC = bacc.Spec("wse_w2k2", mutate, evaluate, gkey, neutral, improving, sample, hamming)


def part_a():
    rows = [json.loads(l) for l in open(os.path.join(R4, "runs_N.jsonl"))]
    g_all, b_all = set(), set()
    per_g, per_b = defaultdict(set), defaultdict(set)
    n_probes = 0
    for r in rows:
        for d in r["depths"]:
            n_probes += len(d["neutral_genos"])
            g_all.update(d["neutral_genos"]); b_all.update(d["neutral_phen"])
            per_g[r["pid"]].update(d["neutral_genos"]); per_b[r["pid"]].update(d["neutral_phen"])
    pb = sorted(len(v) for v in per_b.values())
    return {"walkers": len(rows), "neutral_probes": n_probes, "distinct_neutral_genotypes": len(g_all),
            "distinct_neutral_behaviours": len(b_all), "per_parent_behaviours": pb,
            "median_per_parent_behaviours": bacc.median(pb), "sum_per_parent_behaviours": sum(pb),
            "expected_R4": {"neutral_probes": 23365, "distinct_neutral_genotypes": 21948,
                            "distinct_neutral_behaviours": 91, "median_per_parent_behaviours": 3},
            "rows": rows}


def part_b(rows, n_parents=2):
    ps = walks.shelf_parents()[:n_parents]
    jobs = [{"arm": "N", "pid": pid, "pm": pm, "w": w, "P": 4} for pid, pm in ps for w in range(1, 9)]
    from multiprocessing import Pool
    with Pool(4) as pool:
        res = pool.map(walks.run_walker, jobs)
    ref = {(r["pid"], r["w"]): r for r in rows}
    same = 0
    for r in res:
        a = dict(r); a.pop("wall_s")
        b = dict(ref[(r["pid"], r["w"])]); b.pop("wall_s")
        same += int(json.loads(json.dumps(a, sort_keys=True)) == b)
    return {"rerun_walkers": len(res), "identical_to_runs_N": same}


def main():
    smoke = "--smoke" in sys.argv
    t0 = time.time()
    out = {"substrate": "WSE/Proteus v0.4 tape VM, W2_K2, 16 train CRN episodes", "EXPLORATORY": True}
    A = part_a()
    rows = A.pop("rows")
    out["repro_A_from_runs_N"] = A
    if not smoke and "--skip-repro" not in sys.argv:
        tb = time.time()
        out["repro_B_rerun"] = part_b(rows)
        out["repro_B_rerun"]["wall_s"] = round(time.time() - tb, 1)
    W, D, m, NN = (1, 2, 12, 20) if smoke else (1, 10, 24, 400)
    ps = walks.shelf_parents()
    if smoke:
        ps = ps[:2]
    tc = time.time()
    walkers, null = bacc.run_all(SPEC, ps, W, D, m, procs=4, null_n=NN)
    out["walk_wall_s"] = round(time.time() - tc, 1)
    per, summ = bacc.analyse(SPEC, walkers, null, D)
    nm = bacc.null_metrics(null)
    nm["share_improving_over_0.531"] = sum(1 for r in null if r["s"] > 17 / 32 + 1 / 16 + 1e-9) / len(null)
    nm["share_score_0"] = sum(1 for r in null if r["s"] <= 1e-9) / len(null)
    out.update({"design": {"W": W, "D": D, "m": m, "null_n": NN, "parents": len(ps)},
                "summary": summ, "null": nm, "per_parent": per, "wall_s": round(time.time() - t0, 1)})
    with open(os.path.join(HERE, "wse_result%s.json" % ("_smoke" if smoke else "")), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True, default=str)
    print(json.dumps(A), json.dumps(out.get("repro_B_rerun")))
    print(json.dumps({k: summ[k] for k in ("median_B_over_G", "median_DOM", "BEHAVIOURAL_POVERTY",
                                            "pooled_neutral_genotypes", "pooled_neutral_behaviours")}), out["wall_s"])


if __name__ == "__main__":
    main()
