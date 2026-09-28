#!/usr/bin/env python3
"""POST-HOC diagnostic 2 (NOT preregistered). diag.py showed ASSOC cannot even hold
a perfect compositional code (learnability 0.32 at g0): the naive-Bayes product lets
irrelevant features veto. Does an alignment-free factored learner with ADDITIVE
voting (score_c = sum_f P(c at p | f = m_f)) close and ratchet? B16, FILTER=1, mu 0.01,
20 chains from random and 10 from a perfect compositional code."""
import json, os, random, statistics as st
from collections import Counter
from multiprocessing import Pool
import il
from diag import compositional


def learn_add(train, rng):
    seen = {m: s for m, s in train}
    cnt = [[[[0] * il.A for _ in range(il.L)] for _ in range(il.V)] for _ in range(il.F)]
    nfv = [[0] * il.V for _ in range(il.F)]
    for m, s in train:
        for f in range(il.F):
            v = il.MEANINGS[m][f]
            nfv[f][v] += 1
            for p in range(il.L):
                cnt[f][v][p][s[p]] += 1
    out = []
    for m in range(il.N):
        if m in seen:
            out.append(seen[m]); continue
        sig = []
        for p in range(il.L):
            sc = [sum(cnt[f][il.MEANINGS[m][f]][p][c] / nfv[f][il.MEANINGS[m][f]]
                      for f in range(il.F) if nfv[f][il.MEANINGS[m][f]]) for c in range(il.A)]
            mx = max(sc)
            sig.append(rng.choice([c for c in range(il.A) if sc[c] >= mx - 1e-12]))
        out.append(tuple(sig))
    return out


_orig = il.learn


def patched(kind, train, rng):
    return learn_add(train, rng) if kind == "ADD" else _orig(kind, train, rng)


def chain(args):
    il.learn = patched
    start, ci = args
    rng = random.Random(880000 + ci + (start == "comp") * 500)
    mrng = random.Random(rng.random())
    lang = compositional(rng) if start == "comp" else [il.rand_sig(rng) for _ in range(il.N)]
    traj = {0: il.measure(lang, "ADD", mrng)}
    stab = []
    for g in range(1, 31):
        ms = rng.sample(range(il.N), 16)
        c = Counter(lang)
        train = [(m, lang[m]) for m in ms if c[lang[m]] == 1]
        new = il.noise(learn_add(train, rng), rng)
        stab.append(sum(a == b for a, b in zip(new, lang)) / il.N)
        lang = new
        if g in (1, 5, 30):
            traj[g] = il.measure(lang, "ADD", mrng)
    perm = il.learnability(lang, "ADD", mrng, permute=True)
    return {"start": start, "chain": ci, "traj": traj, "stab_last5": st.mean(stab[-5:]), "perm": perm}


def main():
    tasks = [("rand", c) for c in range(20)] + [("comp", c) for c in range(10)]
    with Pool(4) as p:
        out = p.map(chain, tasks, chunksize=1)
    summ = {}
    for start in ("rand", "comp"):
        cs = [r for r in out if r["start"] == start]
        summ[start] = {g: {k: round(st.mean(r["traj"][g][k] for r in cs), 3) for k in ("z", "expr", "learn_same")}
                       for g in (0, 1, 5, 30)}
        summ[start]["stab_last5"] = round(st.mean(r["stab_last5"] for r in cs), 3)
        summ[start]["perm_learn"] = round(st.mean(r["perm"] for r in cs), 3)
        summ[start]["z30_gt_z1"] = sum(r["traj"][30]["z"] > r["traj"][1]["z"] for r in cs)
        summ[start]["align30"] = dict(Counter(r["traj"][30]["align"] for r in cs))
        print(start, json.dumps(summ[start]))
    json.dump({"status": "POST-HOC EXPLORATORY", "summary": summ, "chains": out},
              open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "diag2.json"), "w"), indent=0)


if __name__ == "__main__":
    main()
