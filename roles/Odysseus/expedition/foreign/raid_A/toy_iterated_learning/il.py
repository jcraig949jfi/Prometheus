#!/usr/bin/env python3
"""Iterated learning through a bottleneck with no installed semantics.
raid_A kill test (see PREREG.md). stdlib only. EXPLORATORY.

python3 il.py            -> writes result.json next to this file
python3 il.py --smoke    -> tiny run, prints summary, writes nothing
"""
import itertools, json, math, os, random, statistics, sys, time
from multiprocessing import Pool

F, V, L, A = 3, 4, 6, 4
MEANINGS = list(itertools.product(range(V), repeat=F))
N = len(MEANINGS)  # 64
PAIRS = [(i, j) for i in range(N) for j in range(i + 1, N)]
MD = [[sum(a != b for a, b in zip(MEANINGS[i], MEANINGS[j])) for j in range(N)] for i in range(N)]
MU = 0.01
G = 30
CHECK = [0, 1, 2, 5, 10, 20, 30]
NPERM = 100
LEARN_B = 16
LEARN_DRAWS = 5
MASTER = 20260928


def rand_sig(rng):
    return tuple(rng.randrange(A) for _ in range(L))


# ---------------------------------------------------------------- learners
def learn(kind, train, rng):
    """train: list of (meaning_index, signal). Returns full language (list of N signals)."""
    seen = {m: s for m, s in train}
    out = [None] * N
    if kind == "HOLISTIC":
        for m in range(N):
            out[m] = seen[m] if m in seen else rand_sig(rng)
    elif kind == "NNCOPY":
        keys = list(seen)
        for m in range(N):
            if m in seen:
                out[m] = seen[m]
            elif not keys:
                out[m] = rand_sig(rng)
            else:
                best = min(MD[m][k] for k in keys)
                out[m] = seen[rng.choice([k for k in keys if MD[m][k] == best])]
    elif kind == "ASSOC":
        cnt = [[[[0] * A for _ in range(L)] for _ in range(V)] for _ in range(F)]
        nfv = [[0] * V for _ in range(F)]
        for m, s in train:
            mv = MEANINGS[m]
            for f in range(F):
                nfv[f][mv[f]] += 1
                row = cnt[f][mv[f]]
                for p in range(L):
                    row[p][s[p]] += 1
        for m in range(N):
            if m in seen:
                out[m] = seen[m]
                continue
            mv = MEANINGS[m]
            sig = []
            for p in range(L):
                sc = []
                for c in range(A):
                    t = 0.0
                    for f in range(F):
                        n = nfv[f][mv[f]]
                        t += math.log((cnt[f][mv[f]][p][c] + 0.1) / (n + 0.1 * A))
                    sc.append(t)
                mx = max(sc)
                sig.append(rng.choice([c for c in range(A) if sc[c] >= mx - 1e-12]))
            out[m] = tuple(sig)
    elif kind == "PLANTED":
        # feature f hard-wired to positions (2f, 2f+1)
        tab = [[{} for _ in range(V)] for _ in range(F)]
        for m, s in train:
            mv = MEANINGS[m]
            for f in range(F):
                k = (s[2 * f], s[2 * f + 1])
                tab[f][mv[f]][k] = tab[f][mv[f]].get(k, 0) + 1
        for m in range(N):
            if m in seen:
                out[m] = seen[m]
                continue
            mv = MEANINGS[m]
            sig = []
            for f in range(F):
                d = tab[f][mv[f]]
                if d:
                    mx = max(d.values())
                    sig.extend(rng.choice(sorted(k for k in d if d[k] == mx)))
                else:
                    sig.extend((rng.randrange(A), rng.randrange(A)))
            out[m] = tuple(sig)
    else:
        raise ValueError(kind)
    return out


def noise(lang, rng):
    res = []
    for s in lang:
        s = list(s)
        for p in range(L):
            if rng.random() < MU:
                s[p] = rng.choice([c for c in range(A) if c != s[p]])
        res.append(tuple(s))
    return res


# ---------------------------------------------------------------- measures
def pearson(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    if sxx == 0 or syy == 0:
        return 0.0
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / math.sqrt(sxx * syy)


def struct_z(lang, rng):
    if len(set(lang)) <= 1:
        return 0.0, 0.0
    sd = [sum(a != b for a, b in zip(lang[i], lang[j])) for i, j in PAIRS]
    md = [MD[i][j] for i, j in PAIRS]
    r = pearson(md, sd)
    # Speed-up (identical statistic): permuting meaning labels leaves the
    # multiset of meaning distances unchanged, so its mean and variance are
    # constant; r_perm = sum(md_perm * sd_centred) / const.
    n = len(sd)
    msd = sum(sd) / n
    sdc = [b - msd for b in sd]
    syy = sum(b * b for b in sdc)
    mmd = sum(md) / n
    sxx = sum((a - mmd) ** 2 for a in md)
    den = math.sqrt(sxx * syy)
    null = []
    idx = list(range(N))
    for _ in range(NPERM):
        rng.shuffle(idx)
        rows = [MD[k] for k in idx]
        null.append(sum(rows[i][idx[j]] * c for (i, j), c in zip(PAIRS, sdc)) / den)
    m, s = statistics.mean(null), statistics.pstdev(null)
    return r, ((r - m) / s if s > 0 else 0.0)


def learnability(lang, reader, rng, permute=False):
    accs = []
    for _ in range(LEARN_DRAWS):
        ms = rng.sample(range(N), LEARN_B)
        sigs = [lang[m] for m in ms]
        if permute:
            rng.shuffle(sigs)
        out = learn(reader, list(zip(ms, sigs)), rng)
        unseen = [m for m in range(N) if m not in set(ms)]
        accs.append(sum(out[m] == lang[m] for m in unseen) / len(unseen))
    return statistics.mean(accs)


def entropy(counts):
    n = sum(counts)
    return -sum(c / n * math.log2(c / n) for c in counts if c)


def align(lang):
    sigp = []
    for p in range(L):
        hp = entropy([sum(1 for s in lang if s[p] == c) for c in range(A)])
        best, bf = 0.5, "-"
        for f in range(F):
            hc = 0.0
            for v in range(V):
                sub = [lang[m][p] for m in range(N) if MEANINGS[m][f] == v]
                hc += len(sub) / N * entropy([sub.count(c) for c in range(A)])
            mi = hp - hc
            if mi > best:
                best, bf = mi, str(f)
        sigp.append(bf)
    # canonicalise feature labels? NO: features are world-defined, so the raw
    # signature (which position carries which world feature) is the convention.
    return "".join(sigp)


def measure(lang, kind, rng):
    r, z = struct_z(lang, rng)
    return {
        "r": round(r, 4), "z": round(z, 3),
        "expr": len(set(lang)) / N,
        "learn_same": round(learnability(lang, kind, rng), 4),
        "learn_assoc": round(learnability(lang, "ASSOC", rng), 4),
        "align": align(lang),
    }


# ---------------------------------------------------------------- chain
def run_chain(args):
    kind, B, filt, ci = args
    seed = (MASTER + {"HOLISTIC": 1, "NNCOPY": 2, "ASSOC": 3, "PLANTED": 4}[kind] * 100000
            + B * 1000 + filt * 100 + ci)
    rng = random.Random(seed)
    mrng = random.Random(seed ^ 0x5A5A5A)  # measurement rng, separate stream
    lang = [rand_sig(rng) for _ in range(N)]
    lang0 = lang
    traj = {}
    stab = []
    if 0 in CHECK:
        traj[0] = measure(lang, kind, mrng)
    for g in range(1, G + 1):
        ms = rng.sample(range(N), B)
        train = [(m, lang[m]) for m in ms]
        if filt:
            from collections import Counter
            cnt = Counter(lang)
            train = [(m, s) for m, s in train if cnt[s] == 1]
        new = noise(learn(kind, train, rng), rng)
        stab.append(sum(a == b for a, b in zip(new, lang)) / N)
        lang = new
        if g in CHECK:
            traj[g] = measure(lang, kind, mrng)
    res = {"kind": kind, "B": B, "filter": filt, "chain": ci, "seed": seed,
           "traj": traj, "stab_last5": round(statistics.mean(stab[-5:]), 4)}
    if kind == "ASSOC" and B == 16:
        res["perm_assoc"] = round(learnability(lang, "ASSOC", mrng, permute=True), 4)
        # recompute arm: one learner, G*B samples of the random gen-0 language
        tr = {}
        for _ in range(G * B):
            m = rng.randrange(N)
            tr[m] = lang0[m]
        rec = learn("ASSOC", list(tr.items()), rng)
        res["recomp_learn_assoc"] = round(learnability(rec, "ASSOC", mrng), 4)
        res["recomp_z"] = round(struct_z(rec, mrng)[1], 3)
        res["recomp_seen"] = len(tr)
    return res


def main():
    smoke = "--smoke" in sys.argv
    kinds = ["HOLISTIC", "NNCOPY", "ASSOC", "PLANTED"]
    nch = 2 if smoke else 20
    global G, CHECK
    if smoke:
        G, CHECK = 6, [0, 1, 5, 6]
    tasks = [(k, B, f, c) for k in kinds for B in (16, 64) for f in (0, 1) for c in range(nch)]
    t0 = time.time()
    with Pool(4) as pool:
        out = pool.map(run_chain, tasks, chunksize=1)
    dt = time.time() - t0
    if smoke:
        for r in out:
            last = r["traj"][max(r["traj"])]
            print(r["kind"], r["B"], r["filter"], r["chain"], last)
        print("secs", round(dt, 1))
        return
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "result.json")
    with open(path, "w") as fh:
        json.dump({"status": "EXPLORATORY", "params": {"F": F, "V": V, "L": L, "A": A, "MU": MU, "G": G,
                   "NPERM": NPERM, "LEARN_B": LEARN_B, "LEARN_DRAWS": LEARN_DRAWS, "master": MASTER,
                   "chains_per_arm": nch}, "secs": round(dt, 1), "chains": out}, fh, indent=0)
    print("wrote", path, "secs", round(dt, 1))


if __name__ == "__main__":
    main()
