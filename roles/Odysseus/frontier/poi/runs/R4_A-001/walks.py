"""R4_A-001 walks: arms N (neutral walk), RW (random walk), RS (random compound sampling),
controls POS (planted), NEG (shuffled evaluator). One job = one walker.

    python3 walks.py --arm N --walkers 8 --P 4 --out runs_N.jsonl [--pilot] [--procs 4]
    python3 walks.py --arm POS --walkers 16 --P 4 --out runs_POS.jsonl
    python3 walks.py --arm NEG --walkers 4 --P 4 --out runs_NEG.jsonl
"""
import argparse
import hashlib
import json
import os
import sys
import time
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r4lib as L

DEPTH_MAX = 5
MAX_PROPOSALS = 64
SUMMIT = 0.9


def shelf_parents():
    pop = json.load(open(os.path.join(L.REPO, "archaeon/campaign4/STARTING_POPULATION.json")))
    return [(o["organism_id"], o["manifest"]) for o in pop["organisms"] if o["class"] == "shelf"]


def permuted(vec, label):
    rng = L.SplitMix64(L.seed_from("r4a001.shuffle", label))
    idx = list(range(len(vec)))
    for i in range(len(idx) - 1, 0, -1):
        j = rng.randbelow(i + 1)
        idx[i], idx[j] = idx[j], idx[i]
    return [vec[i] for i in idx]


def targets(mode):
    exp = L.expected_vector(L.episodes())
    if mode == "train":
        return {"J": exp}
    return {"J": permuted(exp, "S_A"), "B": permuted(exp, "S_B")}      # NEG: judge on S_A, re-score on S_B


def phash(ans):
    return hashlib.sha1(repr(ans).encode()).hexdigest()[:12]


def run_walker(job):
    arm, pid, pm, w, P = job["arm"], job["pid"], job["pm"], job["w"], job["P"]
    walk_kind = {"N": "N", "POS": "N", "NEG": "N", "RW": "RW", "RS": "RS"}[arm]
    T = targets("neg" if arm == "NEG" else "train")
    eps = L.episodes()
    summit_g = L.summit_genome(0)
    a0 = L.answers(pm, eps)
    r0 = L.score(a0, T["J"])
    r0B = L.score(a0, T["B"]) if "B" in T else None
    wrng = L.SplitMix64(L.seed_from("r4a001", arm, pid, "walk", w))
    cur, r_cur = pm, r0
    depths = []
    stalled = False
    nevals = 1
    t0 = time.time()
    for d in range(DEPTH_MAX + 1):
        rec = {"d": d, "geno": L.digest(cur), "r_cur": r_cur, "len": len(cur["genome"]) // 4,
               "lev_summit": L.levenshtein_instr(cur["genome"], summit_g),
               "probes": 0, "applied": 0, "imp": 0, "anyup": 0, "imp_vs_cur": 0, "summit": 0, "neutral": 0,
               "lethal0": 0, "max_r": None, "max_ep": 0.0, "neutral_genos": [], "neutral_phen": [], "improvements": []}
        if "B" in T:
            rec.update({"B_imp": 0, "imp_and_B_imp": 0})
        for op in L.OPS:
            for j in range(P):
                prng = L.SplitMix64(L.seed_from("r4a001", arm, pid, w, d, op, j))
                rec["probes"] += 1
                base = pm if walk_kind == "RS" else cur
                child, _ = L.one_edit(base, prng, name=op)
                if child is not None and walk_kind == "RS" and d > 0:
                    child = L.compound(child, prng, d)
                if child is None:
                    continue
                rec["applied"] += 1
                a = L.answers(child, eps)
                nevals += 1
                r = L.score(a, T["J"])
                ep = L.episode_score(a, T["J"])
                rec["max_r"] = r if rec["max_r"] is None else max(rec["max_r"], r)
                rec["max_ep"] = max(rec["max_ep"], ep)
                if r <= L.EPS:
                    rec["lethal0"] += 1
                if abs(r - r0) <= L.BAND + L.EPS:
                    rec["neutral"] += 1
                    rec["neutral_genos"].append(L.digest(child))
                    rec["neutral_phen"].append(phash(a))
                if r >= r0 + 1 / 32 - L.EPS:
                    rec["anyup"] += 1
                if r > r_cur + L.BAND + L.EPS:
                    rec["imp_vs_cur"] += 1
                if r >= SUMMIT:
                    rec["summit"] += 1
                bimp = None
                if "B" in T:
                    bimp = L.score(a, T["B"]) > r0B + L.BAND + L.EPS
                    rec["B_imp"] += int(bimp)
                if r > r0 + L.BAND + L.EPS:
                    rec["imp"] += 1
                    if "B" in T:
                        rec["imp_and_B_imp"] += int(bimp)
                    rec["improvements"].append({"op": op, "j": j, "r": r, "ep": ep, "r_cur": r_cur,
                                                "child": child if arm != "NEG" else None})
        depths.append(rec)
        if d == DEPTH_MAX or walk_kind == "RS":
            if walk_kind == "RS" and d < DEPTH_MAX:
                continue
            break
        # take one step
        tries = 0
        nxt = None
        while tries < MAX_PROPOSALS:
            c, _ = L.one_edit(cur, wrng)
            if c is None:
                tries += 1 if _ is None else 0
                continue
            tries += 1
            if walk_kind == "RW":
                nxt = c
                break
            r = L.score(L.answers(c, eps), T["J"])
            nevals += 1
            if abs(r - r0) <= L.BAND + L.EPS:
                nxt = c
                break
        rec["step_proposals"] = tries
        if nxt is None:
            stalled = True
            break
        cur = nxt
        r_cur = L.score(L.answers(cur, eps), T["J"])
        nevals += 1
    return {"arm": arm, "pid": pid, "w": w, "P": P, "r0": r0, "stalled": stalled, "nevals": nevals,
            "wall_s": round(time.time() - t0, 2), "depths": depths}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=["N", "RW", "RS", "POS", "NEG"])
    ap.add_argument("--walkers", type=int, default=8)
    ap.add_argument("--P", type=int, default=4)
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.arm == "POS":
        parents = [("planted_2clobber", L.manifest_of(L.summit_genome(2)))]
    else:
        parents = shelf_parents()
    if a.pilot:
        parents = parents[:1]
    jobs = [{"arm": a.arm, "pid": pid, "pm": pm, "w": w, "P": a.P} for pid, pm in parents for w in range(1, a.walkers + 1)]
    t0 = time.time()
    n = 0
    with open(os.path.join(L.HERE, a.out), "w") as f, Pool(a.procs) as pool:
        for res in pool.imap_unordered(run_walker, jobs):
            f.write(json.dumps(res, sort_keys=True) + "\n")
            n += 1
    print(json.dumps({"arm": a.arm, "jobs": n, "wall_s": round(time.time() - t0, 1)}))


if __name__ == "__main__":
    main()
