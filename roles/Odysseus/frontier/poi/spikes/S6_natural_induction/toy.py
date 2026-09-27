#!/usr/bin/env python3
"""S6 natural induction toy (stdlib only). See PREREG.md for the frozen protocol.

Usage: python3 toy.py pilot   -> pilot.json (primary delta per family)
       python3 toy.py main    -> results.json (needs pilot.json)
"""
import json, os, random, sys, time, statistics, itertools
from multiprocessing import Pool
from operator import mul

HERE = os.path.dirname(os.path.abspath(__file__))
T = 10                 # sweeps per reset
R = 1000               # resets per learning run
CHECKPOINTS = (100, 300, 1000)
DELTAS = (1e-4, 3e-4, 1e-3, 3e-3)
DELTA_FAST = 0.1
N_EVAL = 100
MAX_EVAL_SWEEPS = 50
SEEDS = (1, 2, 3, 4, 5)
PILOT_SEED = 999
FAMILIES = ("MOD", "SK")


# ---------------------------------------------------------------- instances
def make_instance(fam, seed):
    rng = random.Random("inst-%s-%d" % (fam, seed))
    if fam == "SK":
        n = 50
        W = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                w = 1.0 if rng.random() < 0.5 else -1.0
                W[i][j] = W[j][i] = w
        return W, {"n": n}
    n_mod, size, eps = 12, 5, 0.05
    n = n_mod * size
    mod = [i // size for i in range(n)]
    c = {}
    for a in range(n_mod):
        for b in range(a + 1, n_mod):
            c[(a, b)] = 1.0 if rng.random() < 0.5 else -1.0
    W = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            a, b = mod[i], mod[j]
            w = 1.0 if a == b else eps * c[(min(a, b), max(a, b))]
            W[i][j] = W[j][i] = w
    # exact ground state over module-consistent configurations
    best = None
    for bits in itertools.product((-1, 1), repeat=n_mod):
        s = [bits[mod[i]] for i in range(n)]
        e = energy(W, s)
        if best is None or e < best:
            best = e
    return W, {"n": n, "ground": best, "n_mod": n_mod}


def energy(W, s):
    e = 0.0
    for i, row in enumerate(W):
        e -= s[i] * sum(map(mul, row, s))
    return e / 2.0


# ---------------------------------------------------------------- dynamics
def sweep(W, s, rng):
    """One asynchronous sweep in random order. Returns True if any flip."""
    n = len(s)
    order = list(range(n))
    rng.shuffle(order)
    changed = False
    for i in order:
        h = sum(map(mul, W[i], s))
        if h > 0 and s[i] < 0:
            s[i] = 1; changed = True
        elif h < 0 and s[i] > 0:
            s[i] = -1; changed = True
    return changed


def relax(W, s, rng, max_sweeps):
    for _ in range(max_sweeps):
        if not sweep(W, s, rng):
            break
    return s


def yield_update(W, y, c):
    """W_ij += c*y_i*y_j for i != j (in place)."""
    for i, row in enumerate(W):
        ci = c * y[i]
        W[i] = [w + ci * yj for w, yj in zip(row, y)]
        W[i][i] -= ci * y[i]


def rand_state(rng, n):
    return [1 if rng.random() < 0.5 else -1 for _ in range(n)]


# ---------------------------------------------------------------- evaluation
def evaluate(W0, Weff, fam, seed):
    n = len(W0)
    rng = random.Random("eval-%s-%d" % (fam, seed))
    out_pre, out_post = [], []
    for _ in range(N_EVAL):
        s = rand_state(rng, n)
        srng = random.Random(rng.random())
        relax(Weff, s, srng, MAX_EVAL_SWEEPS)
        out_pre.append(energy(W0, s))
        relax(W0, s, srng, MAX_EVAL_SWEEPS)
        out_post.append(energy(W0, s))
    return out_pre, out_post


# ---------------------------------------------------------------- learning
def learn(job):
    fam, seed, cond, delta = job["fam"], job["seed"], job["cond"], job["delta"]
    W0, meta = make_instance(fam, seed)
    n = len(W0)
    Weff = [row[:] for row in W0]
    rng = random.Random("learn-%s-%d" % (fam, seed))   # shared across conditions
    prng = random.Random("perm-%s-%d" % (fam, seed))
    sign = -1.0 if cond == "anti" else 1.0
    record = [] if job.get("record") else None
    foreign = job.get("foreign")
    evals, traj = {}, []
    t0 = time.time()
    s = rand_state(rng, n)
    block = []
    for r in range(1, R + 1):
        if cond == "shuf_oth":
            for (y, cnt) in foreign[r - 1]:
                yield_update(Weff, y, delta * cnt)
        elif cond == "nodiss":
            for _ in range(T):
                yield_update(Weff, rand_state(rng, n), delta)
        else:
            if cond != "noreset" or r == 1:
                s = rand_state(rng, n)
            perm = None
            if cond == "perm":
                perm = list(range(n)); prng.shuffle(perm)
            rec = []
            for k in range(1, T + 1):
                changed = sweep(Weff, s, rng)
                cnt = 1 if changed else T - k + 1
                y = s if perm is None else [s[p] for p in perm]
                yield_update(Weff, y, sign * delta * cnt)
                if record is not None:
                    rec.append((list(y), cnt))
                if not changed:
                    break
            if record is not None:
                record.append(rec)
            block.append(energy(W0, s))
        if len(block) == 100:
            traj.append(statistics.mean(block)); block = []
        if r in CHECKPOINTS:
            pre, post = evaluate(W0, Weff, fam, seed)
            evals[r] = {"pre": pre, "post": post}
    res = {"fam": fam, "seed": seed, "cond": cond, "delta": delta,
           "traj_attractor_E0_per100": traj, "evals": evals,
           "secs": round(time.time() - t0, 1), "meta": meta}
    if record is not None:
        res["record"] = record
    return res


def learn_noyield(job):
    """Plain relaxation baseline + best-of-1000 reference."""
    fam, seed = job["fam"], job["seed"]
    W0, meta = make_instance(fam, seed)
    n = len(W0)
    rng = random.Random("learn-%s-%d" % (fam, seed))
    es = []
    t0 = time.time()
    for _ in range(R):
        s = rand_state(rng, n)
        relax(W0, s, rng, MAX_EVAL_SWEEPS)
        es.append(energy(W0, s))
    pre, post = evaluate(W0, W0, fam, seed)
    return {"fam": fam, "seed": seed, "cond": "noyield", "delta": 0.0,
            "evals": {c: {"pre": pre, "post": post} for c in CHECKPOINTS},
            "best_of_1000_plain": min(es), "mean_of_1000_plain": statistics.mean(es),
            "traj_attractor_E0_per100": [statistics.mean(es[i:i + 100]) for i in range(0, R, 100)],
            "secs": round(time.time() - t0, 1), "meta": meta}


def run_job(job):
    if job["cond"] == "noyield":
        return learn_noyield(job)
    return learn(job)


# ---------------------------------------------------------------- drivers
def M(res, c=1000, key="post"):
    return statistics.mean(res["evals"][c][key])


def pilot():
    jobs = [{"fam": f, "seed": PILOT_SEED, "cond": "NI", "delta": d}
            for f in FAMILIES for d in DELTAS]
    jobs += [{"fam": f, "seed": PILOT_SEED, "cond": "noyield", "delta": 0.0} for f in FAMILIES]
    with Pool(4) as p:
        out = p.map(run_job, jobs)
    summary = {}
    for f in FAMILIES:
        rows = {r["delta"]: M(r) for r in out if r["fam"] == f and r["cond"] == "NI"}
        base = [M(r) for r in out if r["fam"] == f and r["cond"] == "noyield"][0]
        best = min(sorted(rows), key=lambda d: (rows[d], d))
        summary[f] = {"M_by_delta": {str(d): rows[d] for d in sorted(rows)},
                      "M_noyield": base, "primary_delta": best}
    json.dump(summary, open(os.path.join(HERE, "pilot.json"), "w"), indent=1)
    print(json.dumps(summary, indent=1))


def main():
    pil = json.load(open(os.path.join(HERE, "pilot.json")))
    t0 = time.time()
    jobs = []
    for f in FAMILIES:
        dp = pil[f]["primary_delta"]
        for sd in SEEDS:
            for d in DELTAS:
                jobs.append({"fam": f, "seed": sd, "cond": "NI", "delta": d,
                             "record": d == dp})
            jobs.append({"fam": f, "seed": sd, "cond": "noyield", "delta": 0.0})
            for c in ("anti", "perm", "noreset", "nodiss"):
                jobs.append({"fam": f, "seed": sd, "cond": c, "delta": dp})
            jobs.append({"fam": f, "seed": sd, "cond": "fast", "delta": DELTA_FAST})
    with Pool(4) as p:
        out = p.map(run_job, jobs, chunksize=1)
    print("phase1 %.0fs" % (time.time() - t0), flush=True)
    recs = {(r["fam"], r["seed"]): r.pop("record") for r in out if "record" in r}
    jobs2 = []
    for f in FAMILIES:
        dp = pil[f]["primary_delta"]
        for i, sd in enumerate(SEEDS):
            other = SEEDS[(i + 1) % len(SEEDS)]
            jobs2.append({"fam": f, "seed": sd, "cond": "shuf_oth", "delta": dp,
                          "foreign": recs[(f, other)], "foreign_seed": other})
    with Pool(4) as p:
        out2 = p.map(run_job, jobs2, chunksize=1)
    out += out2
    print("phase2 %.0fs" % (time.time() - t0), flush=True)
    json.dump({"pilot": pil, "wall_secs": round(time.time() - t0, 1), "runs": out},
              open(os.path.join(HERE, "results_raw.json"), "w"))
    analyse(out, pil)


# ---------------------------------------------------------------- analysis
def analyse(out, pil):
    rep = {}
    for f in FAMILIES:
        dp = pil[f]["primary_delta"]
        runs = [r for r in out if r["fam"] == f]

        def get(sd, cond, d=None):
            for r in runs:
                if r["seed"] == sd and r["cond"] == cond and (d is None or r["delta"] == d):
                    return r
        per_seed = {}
        for sd in SEEDS:
            base = get(sd, "noyield")
            allE = []
            for r in runs:
                if r["seed"] == sd:
                    for c in r["evals"].values():
                        allE += c["post"]
            allE.append(base["best_of_1000_plain"])
            meta = base["meta"]
            target = meta.get("ground", min(allE))
            sdb = statistics.pstdev(base["evals"][1000]["post"])

            def summ(r, c=1000):
                post = r["evals"][c]["post"]; pre = r["evals"][c]["pre"]
                return {"M": round(statistics.mean(post), 3),
                        "M_prepolish": round(statistics.mean(pre), 3),
                        "min": round(min(post), 3),
                        "frac_target": sum(1 for e in post if e <= target + 1e-9) / len(post)}
            row = {"target_E0": target, "target_kind": "exact_ground" if "ground" in meta else "best_known",
                   "min_seen_any": min(allE), "SD_noyield": round(sdb, 3),
                   "best_of_1000_plain": base["best_of_1000_plain"],
                   "noyield": summ(base)}
            for c in ("anti", "perm", "shuf_oth", "noreset", "nodiss", "fast"):
                row[c] = summ(get(sd, c))
            row["NI_grid"] = {"%g" % d: {str(c): summ(get(sd, "NI", d), c) for c in CHECKPOINTS}
                              for d in DELTAS}
            row["NI"] = row["NI_grid"]["%g" % dp]["1000"]
            row["NI_traj_attractor_E0_per100"] = [round(x, 2) for x in get(sd, "NI", dp)["traj_attractor_E0_per100"]]
            per_seed[sd] = row
        # decision rules
        Mni = {sd: per_seed[sd]["NI"]["M"] for sd in SEEDS}
        Mc = lambda c: {sd: per_seed[sd][c]["M"] for sd in SEEDS}
        wins = lambda c: sum(1 for sd in SEEDS if Mni[sd] < Mc(c)[sd])
        effs = [(per_seed[sd]["noyield"]["M"] - Mni[sd]) / per_seed[sd]["SD_noyield"] for sd in SEEDS]
        D1 = wins("noyield") >= 4 and statistics.median(effs) >= 0.5
        D2 = wins("anti") >= 4
        D3 = sum(1 for sd in SEEDS if Mni[sd] < Mc("shuf_oth")[sd] and Mni[sd] < Mc("perm")[sd]) >= 4
        verdict = "REPRODUCED" if (D1 and D2 and D3) else ("PARTIAL" if D1 else "NOT REPRODUCED")
        G = statistics.median([per_seed[sd]["noyield"]["M"] - Mni[sd] for sd in SEEDS])
        abl = {}
        for c in ("fast", "noreset", "nodiss"):
            Gx = statistics.median([per_seed[sd]["noyield"]["M"] - per_seed[sd][c]["M"] for sd in SEEDS])
            if G <= 0:
                lab = "uninterpretable (D1 fails)"
            elif Gx <= 0.25 * G:
                lab = "carries the effect"
            elif Gx <= 0.75 * G:
                lab = "partially needed"
            else:
                lab = "not needed"
            abl[c] = {"G_x": round(Gx, 3), "ratio": round(Gx / G, 3) if G else None, "label": lab}
        rep[f] = {"primary_delta": dp, "per_seed": per_seed,
                  "wins_vs": {c: wins(c) for c in ("noyield", "anti", "perm", "shuf_oth")},
                  "effect_sizes_SD": [round(e, 2) for e in effs],
                  "median_effect_SD": round(statistics.median(effs), 3),
                  "D1": D1, "D2": D2, "D3": D3, "verdict": verdict,
                  "G_median_gain": round(G, 3), "ablations": abl}
    json.dump(rep, open(os.path.join(HERE, "results.json"), "w"), indent=1)
    for f in FAMILIES:
        r = rep[f]
        print(f, r["verdict"], "D1-3", r["D1"], r["D2"], r["D3"], "wins", r["wins_vs"],
              "effSD", r["effect_sizes_SD"], "abl", r["ablations"])


if __name__ == "__main__":
    {"pilot": pilot, "main": main}[sys.argv[1]]()
