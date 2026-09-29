#!/usr/bin/env python3
"""POST-HOC diagnostic (NOT preregistered; written after result.json was analysed).
Question: is the K1 failure a CLOSURE failure (a perfect compositional code is not
a fixed point of the ASSOC chain) or a CONVERGENCE failure (it is a fixed point,
but chains from random codes do not reach it)? Also: does it depend on the
production noise mu and bottleneck size B? ASSOC learner, FILTER=1 only.
Nothing here changes the preregistered verdict."""
import json, os, random, statistics as st
from collections import Counter
from multiprocessing import Pool
import il

GD = 30


def compositional(rng):
    maps = []
    for f in range(il.F):
        pairs = rng.sample([(a, b) for a in range(il.A) for b in range(il.A)], il.V)
        maps.append(pairs)
    return [tuple(x for f in range(il.F) for x in maps[f][m[f]]) for m in il.MEANINGS]


def chain(args):
    start, B, mu, ci = args
    rng = random.Random(777000 + ci * 17 + B * 1000 + int(mu * 1000) * 7 + (start == "comp") * 99)
    mrng = random.Random(rng.random())
    il.MU = mu
    lang = compositional(rng) if start == "comp" else [il.rand_sig(rng) for _ in range(il.N)]
    first = il.measure(lang, "ASSOC", mrng)
    stab = []
    for g in range(GD):
        ms = rng.sample(range(il.N), B)
        cnt = Counter(lang)
        train = [(m, lang[m]) for m in ms if cnt[lang[m]] == 1]
        new = il.noise(il.learn("ASSOC", train, rng), rng)
        stab.append(sum(a == b for a, b in zip(new, lang)) / il.N)
        lang = new
    last = il.measure(lang, "ASSOC", mrng)
    return {"start": start, "B": B, "mu": mu, "chain": ci, "g0": first, "g30": last,
            "stab_last5": st.mean(stab[-5:])}


def main():
    tasks = []
    for start in ("comp", "rand"):
        for B in (16, 32, 48):
            for mu in (0.0, 0.01):
                for c in range(10):
                    tasks.append((start, B, mu, c))
    with Pool(4) as p:
        out = p.map(chain, tasks, chunksize=1)
    summ = []
    for start in ("comp", "rand"):
        for B in (16, 32, 48):
            for mu in (0.0, 0.01):
                cs = [r for r in out if r["start"] == start and r["B"] == B and r["mu"] == mu]
                row = {"start": start, "B": B, "mu": mu}
                for k in ("z", "expr", "learn_assoc"):
                    row["g0_" + k] = round(st.mean(r["g0"][k] for r in cs), 3)
                    row["g30_" + k] = round(st.mean(r["g30"][k] for r in cs), 3)
                row["stab"] = round(st.mean(r["stab_last5"] for r in cs), 3)
                summ.append(row)
                print(row)
    json.dump({"status": "POST-HOC EXPLORATORY", "summary": summ, "chains": out},
              open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "diag.json"), "w"), indent=0)


if __name__ == "__main__":
    main()
