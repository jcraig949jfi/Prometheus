#!/usr/bin/env python3
"""POST-HOC diagnostic 3 (NOT preregistered). ASSOC and ADD cannot hold a perfect
compositional code at B=16 (small-sample confounding across features). SELECT learner:
per position p, pick the ONE feature with max mutual information with the symbol at p
in the training data (ties random), predict the majority symbol among training items
sharing that feature value. Installs the hypothesis class 'each position is a function
of one feature' but NOT which feature (alignment is inferred per learner).
B16, FILTER=1, mu 0.01; 20 chains from random, 10 from a perfect compositional code."""
import json, math, os, random, statistics as st
from collections import Counter
from multiprocessing import Pool
import il
from diag import compositional


def H(xs):
    n = len(xs); c = Counter(xs)
    return -sum(v / n * math.log2(v / n) for v in c.values())


def learn_select(train, rng):
    seen = {m: s for m, s in train}
    out = []
    if not train:
        return [il.rand_sig(rng) for _ in range(il.N)]
    choice = []
    for p in range(il.L):
        syms = [s[p] for _, s in train]
        hp = H(syms)
        best, bf = -1, []
        for f in range(il.F):
            groups = {}
            for m, s in train:
                groups.setdefault(il.MEANINGS[m][f], []).append(s[p])
            mi = hp - sum(len(g) / len(train) * H(g) for g in groups.values())
            if mi > best + 1e-12:
                best, bf = mi, [f]
            elif abs(mi - best) <= 1e-12:
                bf.append(f)
        choice.append(rng.choice(bf))
    for m in range(il.N):
        if m in seen:
            out.append(seen[m]); continue
        sig = []
        for p in range(il.L):
            f = choice[p]
            c = Counter(s[p] for mm, s in train if il.MEANINGS[mm][f] == il.MEANINGS[m][f])
            if c:
                mx = max(c.values())
                sig.append(rng.choice(sorted(k for k in c if c[k] == mx)))
            else:
                sig.append(rng.randrange(il.A))
        out.append(tuple(sig))
    return out


_orig = il.learn


def patched(kind, train, rng):
    return learn_select(train, rng) if kind == "SELECT" else _orig(kind, train, rng)


def chain(args):
    il.learn = patched
    start, ci = args
    rng = random.Random(990000 + ci + (start == "comp") * 500)
    mrng = random.Random(rng.random())
    lang = compositional(rng) if start == "comp" else [il.rand_sig(rng) for _ in range(il.N)]
    traj = {0: il.measure(lang, "SELECT", mrng)}
    stab = []
    for g in range(1, 31):
        ms = rng.sample(range(il.N), 16)
        c = Counter(lang)
        train = [(m, lang[m]) for m in ms if c[lang[m]] == 1]
        new = il.noise(learn_select(train, rng), rng)
        stab.append(sum(a == b for a, b in zip(new, lang)) / il.N)
        lang = new
        if g in (1, 5, 30):
            traj[g] = il.measure(lang, "SELECT", mrng)
    perm = il.learnability(lang, "SELECT", mrng, permute=True)
    return {"start": start, "chain": ci, "traj": traj, "stab_last5": st.mean(stab[-5:]), "perm": perm}


def main():
    tasks = [("rand", c) for c in range(20)] + [("comp", c) for c in range(10)]
    with Pool(4) as p:
        out = p.map(chain, tasks, chunksize=1)
    summ = {}
    for start in ("rand", "comp"):
        cs = [r for r in out if r["start"] == start]
        summ[start] = {g: {k: round(st.mean(r["traj"][g][k] for r in cs), 3) for k in ("z", "expr", "learn_same", "learn_assoc")}
                       for g in (0, 1, 5, 30)}
        summ[start]["stab_last5"] = round(st.mean(r["stab_last5"] for r in cs), 3)
        summ[start]["perm_learn"] = round(st.mean(r["perm"] for r in cs), 3)
        summ[start]["z30_gt_z1"] = sum(r["traj"][30]["z"] > r["traj"][1]["z"] for r in cs)
        summ[start]["align30"] = dict(Counter(r["traj"][30]["align"] for r in cs))
        print(start, json.dumps(summ[start]))
    json.dump({"status": "POST-HOC EXPLORATORY", "summary": summ, "chains": out},
              open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "diag3.json"), "w"), indent=0)


if __name__ == "__main__":
    main()
