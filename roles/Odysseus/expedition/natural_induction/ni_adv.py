#!/usr/bin/env python3
"""Adversarial program against the 'natural induction' (NI) interpretation.
Stdlib only, deterministic (string-seeded RNG streams). See PREREG.md (frozen
before the main run). Dynamics/yield/eval copied from
roles/Odysseus/frontier/poi/spikes/S6_natural_induction/toy.py (not imported,
so nothing is written into that directory).

Usage: python3 ni_adv.py smoke   (timing on pilot seed 999 only; not a result)
       python3 ni_adv.py main    -> results_raw.json, results.json
"""
import json, os, random, sys, time, statistics, itertools, math
from multiprocessing import Pool
from operator import mul

HERE = os.path.dirname(os.path.abspath(__file__))
T = 10
N_EVAL = 100
MAX_EVAL_SWEEPS = 50
DELTA = {"MOD": 3e-4, "SK": 1e-4}         # fixed from S6 (MOD rate is S6 post-hoc)
R_TRAIN = 1000
A_SEEDS = (11, 12, 13, 14, 15)
N_B = 4                                    # same-family new instances per A
SCALES = (0.25, 0.5, 1.0, 2.0, 4.0)        # memory-model norm multipliers
H_EPS = (1e-3, 1e-2, 1e-1)                 # fatigue (sign-blind) rates
N_WORKERS = 4


# ------------------------------------------------------------------ instances
def mod_instance(tag, perm_seed=None):
    rng = random.Random("mod-" + tag)
    n_mod, size, eps = 12, 5, 0.05
    n = n_mod * size
    mod = [i // size for i in range(n)]
    if perm_seed is not None:
        pr = random.Random("modperm-" + perm_seed)
        pr.shuffle(mod)
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
    # exact ground state over module-consistent configurations (superspin sum)
    best, bestS = None, None
    for S in itertools.product((-1, 1), repeat=n_mod):
        e = 0.0
        for (a, b), cab in c.items():
            e -= cab * S[a] * S[b]
        if best is None or e < best:
            best, bestS = e, S
    s = [bestS[mod[i]] for i in range(n)]
    return W, {"n": n, "ground": energy(W, s), "ground_state": s, "mod": mod}


def sk_instance(tag, n):
    rng = random.Random("sk-" + tag)
    W = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            w = 1.0 if rng.random() < 0.5 else -1.0
            W[i][j] = W[j][i] = w
    return W, {"n": n}


def sk_perturbed(W, p, tag):
    rng = random.Random("skpert-" + tag)
    n = len(W)
    V = [row[:] for row in W]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                V[i][j] = V[j][i] = -V[i][j]
    return V, {"n": n}


def targets_for(fam, a):
    """Return list of (name, W0, meta) for instance A and its transfer targets."""
    out = []
    if fam == "MOD":
        WA, mA = mod_instance("A%d" % a)
        out.append(("A", WA, mA))
        for k in range(N_B):
            W, m = mod_instance("A%d-B%d" % (a, k))
            out.append(("B%d" % k, W, m))
        W, m = mod_instance("A%d-X" % a, perm_seed="A%d" % a)
        out.append(("Xperm", W, m))
        W, m = sk_instance("A%d-X60" % a, 60)
        out.append(("Xsk60", W, m))
    else:
        WA, mA = sk_instance("A%d" % a, 50)
        out.append(("A", WA, mA))
        for k in range(N_B):
            W, m = sk_instance("A%d-B%d" % (a, k), 50)
            out.append(("B%d" % k, W, m))
        for p in (0.1, 0.3):
            W, m = sk_perturbed(WA, p, "A%d-%g" % (a, p))
            out.append(("P%02d" % int(p * 100), W, m))
    return out


def energy(W, s):
    e = 0.0
    for i, row in enumerate(W):
        e -= s[i] * sum(map(mul, row, s))
    return e / 2.0


# ------------------------------------------------------------------ dynamics
def sweep(W, s, rng):
    n = len(s)
    order = list(range(n))
    rng.shuffle(order)
    flipped = []
    for i in order:
        h = sum(map(mul, W[i], s))
        if h > 0 and s[i] < 0:
            s[i] = 1; flipped.append(i)
        elif h < 0 and s[i] > 0:
            s[i] = -1; flipped.append(i)
    return flipped


def relax(W, s, rng, max_sweeps):
    for _ in range(max_sweeps):
        if not sweep(W, s, rng):
            break
    return s


def yield_update(W, y, c):
    for i, row in enumerate(W):
        ci = c * y[i]
        W[i] = [w + ci * yj for w, yj in zip(row, y)]
        W[i][i] -= ci * y[i]


def rand_state(rng, n):
    return [1 if rng.random() < 0.5 else -1 for _ in range(n)]


def add(A, B, c=1.0):
    return [[a + c * b for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]


def sub(A, B):
    return [[a - b for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]


def fro(A):
    return math.sqrt(sum(x * x for r in A for x in r))


def scaled(A, target):
    f = fro(A)
    c = target / f if f > 0 else 0.0
    return [[c * x for x in r] for r in A]


def outer_sum(states, n):
    C = [[0.0] * n for _ in range(n)]
    for s in states:
        for i in range(n):
            si = s[i]
            row = C[i]
            for j in range(n):
                if j != i:
                    row[j] += si * s[j]
    return C


def canon(s):
    return "".join("1" if (x if s[0] > 0 else -x) > 0 else "0" for x in s)


# ------------------------------------------------------------------ evaluation
def evaluate(W0, Weff, tag):
    n = len(W0)
    rng = random.Random("eval-" + tag)
    post, states = [], []
    for _ in range(N_EVAL):
        s = rand_state(rng, n)
        srng = random.Random(rng.random())
        relax(Weff, s, srng, MAX_EVAL_SWEEPS)
        relax(W0, s, srng, MAX_EVAL_SWEEPS)
        post.append(energy(W0, s))
        states.append(canon(s))
    return post, states


# ------------------------------------------------------------------ learners
def ni_run(W0, Weff, delta, R, rng, checkpoints=(), eval_tag=None, mode="NI", eps=0.0):
    """Reset/relax/yield (mode NI) or sign-blind fatigue (mode H). Modifies Weff.
    Returns dict of checkpoint evals (post energies)."""
    n = len(W0)
    evals = {}
    for r in range(1, R + 1):
        s = rand_state(rng, n)
        for k in range(1, T + 1):
            fl = sweep(Weff, s, rng)
            if mode == "NI":
                cnt = 1 if fl else T - k + 1
                yield_update(Weff, s, delta * cnt)
            elif mode == "H" and len(fl) > 1:
                f = 1.0 - eps
                for i in fl:
                    row = Weff[i]
                    for j in fl:
                        if j != i:
                            row[j] *= f
            if not fl:
                break
        if r in checkpoints:
            evals[r] = evaluate(W0, Weff, eval_tag)[0]
    return evals


def sa_run(W0, rng, sweeps=2000, t0=3.0, t1=0.05):
    n = len(W0)
    s = rand_state(rng, n)
    for k in range(sweeps):
        Tk = t0 * (t1 / t0) ** (k / (sweeps - 1))
        for i in range(n):
            h = sum(map(mul, W0[i], s))
            dE = 2.0 * s[i] * h
            if dE <= 0 or rng.random() < math.exp(-dE / Tk):
                s[i] = -s[i]
    relax(W0, s, rng, MAX_EVAL_SWEEPS)
    return s


# ------------------------------------------------------------------ jobs
def job_train(job):
    fam, a, kind = job["fam"], job["a"], job["kind"]
    tg = targets_for(fam, a)
    W0 = tg[0][1]
    n = len(W0)
    d = DELTA[fam]
    t0 = time.time()
    out = {"fam": fam, "a": a, "kind": kind}
    if kind in ("NI", "NI2", "NIslow"):
        Weff = [r[:] for r in W0]
        seedtag = {"NI": "learn", "NI2": "learn2", "NIslow": "learn3"}[kind]
        rng = random.Random("%s-%s-%d" % (seedtag, fam, a))
        if kind == "NIslow":
            ni_run(W0, Weff, d / 3.0, 3 * R_TRAIN, rng)
        else:
            ni_run(W0, Weff, d, R_TRAIN, rng)
        out["WL"] = sub(Weff, W0)
    elif kind.startswith("H"):
        eps = float(kind[1:])
        Weff = [r[:] for r in W0]
        rng = random.Random("learnH-%s-%d" % (fam, a))
        ni_run(W0, Weff, 0.0, R_TRAIN, rng, mode="H", eps=eps)
        out["WL"] = sub(Weff, W0)
        rng2 = random.Random("learnH2-%s-%d" % (fam, a))   # second history
        W2 = [r[:] for r in W0]
        ni_run(W0, W2, 0.0, R_TRAIN, rng2, mode="H", eps=eps)
        out["hist_dist_rel"] = fro(sub(W2, Weff)) / fro(W0)
    elif kind == "PLAIN":
        rng = random.Random("plain-%s-%d" % (fam, a))
        states, es = [], []
        for _ in range(R_TRAIN):
            s = rand_state(rng, n)
            relax(W0, s, rng, MAX_EVAL_SWEEPS)
            states.append(s); es.append(energy(W0, s))
        out["C"] = outer_sum(states, n)
        out["plain_best"] = min(es)
        out["plain_best_state"] = states[es.index(min(es))]
        out["plain_n_distinct"] = len(set(canon(s) for s in states))
    elif kind == "SA":
        rng = random.Random("sa-%s-%d" % (fam, a))
        s = sa_run(W0, rng)
        out["sa_state"] = s
        out["sa_E"] = energy(W0, s)
    out["secs"] = round(time.time() - t0, 1)
    return out


def job_bexp(job):
    """NI on a same-family target B: from scratch (R=1000, ckpts 100/300/1000)
    or warm-started from WL_A (R=300, ckpts 100/300)."""
    fam, a, tname, kind = job["fam"], job["a"], job["target"], job["kind"]
    tg = dict((x[0], (x[1], x[2])) for x in targets_for(fam, a))
    W0 = tg[tname][0]
    rng = random.Random("bexp-%s-%d-%s" % (fam, a, tname))  # same stream both kinds
    etag = "%s-%d-%s" % (fam, a, tname)
    t0 = time.time()
    if kind == "scratch":
        Weff = [r[:] for r in W0]
        ev = ni_run(W0, Weff, DELTA[fam], 1000, rng, (100, 300, 1000), etag)
    else:
        Weff = add(W0, job["WL"])
        ev = ni_run(W0, Weff, DELTA[fam], 300, rng, (100, 300), etag)
    return {"fam": fam, "a": a, "target": tname, "kind": kind,
            "M": {str(k): statistics.mean(v) for k, v in ev.items()},
            "evals": {str(k): v for k, v in ev.items()},
            "secs": round(time.time() - t0, 1)}


def job_eval(job):
    fam, a, tname = job["fam"], job["a"], job["target"]
    tg = dict((x[0], (x[1], x[2])) for x in targets_for(fam, a))
    W0, meta = tg[tname]
    etag = "%s-%d-%s" % (fam, a, tname)
    t0 = time.time()
    res = {}
    for mname, WL in job["models"].items():
        Weff = W0 if WL is None else add(W0, WL)
        post, states = evaluate(W0, Weff, etag)
        r = {"post": post, "M": statistics.mean(post)}
        if tname == "A":
            cnt = {}
            for st in states:
                cnt[st] = cnt.get(st, 0) + 1
            modal = max(sorted(cnt), key=lambda k: cnt[k])
            r["modal"] = modal
            r["modal_frac"] = cnt[modal] / len(states)
        res[mname] = r
    return {"fam": fam, "a": a, "target": tname, "res": res,
            "ground": meta.get("ground"), "secs": round(time.time() - t0, 1)}


# ------------------------------------------------------------------ driver
def build_models(fam, a, tr):
    """tr: dict kind -> train output for this (fam, a)."""
    n = len(tr["NI"]["WL"])
    WL = tr["NI"]["WL"]
    target = fro(WL)
    models = {"noyield": None, "NI": WL, "NI2": tr["NI2"]["WL"],
              "NIslow": tr["NIslow"]["WL"]}
    for e in H_EPS:
        models["H%g" % e] = tr["H%g" % e]["WL"]
    C = tr["PLAIN"]["C"]
    sa = tr["SA"]["sa_state"]
    tgA = targets_for(fam, a)[0]
    if fam == "MOD":
        best = tgA[2]["ground_state"]
    else:
        best = tr["PLAIN"]["plain_best_state"]   # best-of-1000 restarts (SK)
    Csa = outer_sum([sa], n)
    Cbest = outer_sum([best], n)
    for sc in SCALES:
        models["MEM_x%g" % sc] = scaled(C, sc * target)
        models["SAMEM_x%g" % sc] = scaled(Csa, sc * target)
        models["BESTMEM_x%g" % sc] = scaled(Cbest, sc * target)
    if fam == "MOD":
        mod = tgA[2]["mod"]
        models["NIblock"] = [[WL[i][j] if mod[i] == mod[j] else 0.0 for j in range(n)] for i in range(n)]
        models["NIinter"] = [[WL[i][j] if mod[i] != mod[j] else 0.0 for j in range(n)] for i in range(n)]
    return models


def run(fams, a_seeds, tag):
    t0 = time.time()
    kinds = ["NI", "NI2", "NIslow", "PLAIN", "SA"] + ["H%g" % e for e in H_EPS]
    jobs = [{"fam": f, "a": a, "kind": k} for f in fams for a in a_seeds for k in kinds]
    jobs.sort(key=lambda j: 0 if j["kind"] == "NIslow" else 1)
    bjobs = [{"fam": f, "a": a, "target": "B%d" % k, "kind": "scratch"}
             for f in fams for a in a_seeds for k in range(N_B)]
    with Pool(N_WORKERS) as p:
        out = p.map(job_train, jobs + [], chunksize=1)
        print("train %.0fs" % (time.time() - t0), flush=True)
        tr = {}
        for o in out:
            tr.setdefault((o["fam"], o["a"]), {})[o["kind"]] = o
        wjobs = [{"fam": f, "a": a, "target": "B%d" % k, "kind": "warm",
                  "WL": tr[(f, a)]["NI"]["WL"]}
                 for f in fams for a in a_seeds for k in range(N_B)]
        ejobs = []
        for f in fams:
            for a in a_seeds:
                models = build_models(f, a, tr[(f, a)])
                for (tname, _, _) in targets_for(f, a):
                    ejobs.append({"fam": f, "a": a, "target": tname, "models": models})
        bout = p.map(job_bexp, bjobs + wjobs, chunksize=1)
        print("bexp %.0fs" % (time.time() - t0), flush=True)
        eout = p.map(job_eval, ejobs, chunksize=1)
        print("eval %.0fs" % (time.time() - t0), flush=True)
    train_meta = []
    for o in out:
        m = {k: v for k, v in o.items() if k not in ("WL", "C", "plain_best_state", "sa_state")}
        if "WL" in o:
            m["WL_fro"] = fro(o["WL"])
        train_meta.append(m)
    raw = {"tag": tag, "wall_secs": round(time.time() - t0, 1), "train": train_meta,
           "bexp": bout, "eval": eout}
    return raw


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "smoke":
        R_TRAIN = 200
        t0 = time.time()
        o = job_train({"fam": "MOD", "a": 999, "kind": "NI"})
        print("MOD NI R=200 train secs", o["secs"])
        tg = targets_for("MOD", 999)
        t1 = time.time(); evaluate(tg[0][1], add(tg[0][1], o["WL"]), "x"); print("eval secs", time.time() - t1)
        o = job_train({"fam": "MOD", "a": 999, "kind": "H0.01"}); print("H secs", o["secs"])
        o = job_train({"fam": "MOD", "a": 999, "kind": "SA"}); print("SA secs", o["secs"], o["sa_E"], tg[0][2]["ground"])
        o = job_train({"fam": "MOD", "a": 999, "kind": "PLAIN"}); print("PLAIN secs", o["secs"])
    elif mode == "main":
        raw = run(("MOD", "SK"), A_SEEDS, "main")
        json.dump(raw, open(os.path.join(HERE, "results_raw.json"), "w"))
        print("wall", raw["wall_secs"])
