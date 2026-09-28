"""bacc -- behavioural accessibility of neutral regions. Substrate-agnostic, stdlib only.

A substrate is a Spec with plain callables (module-level functions, so it pickles for multiprocessing):

    mutate(g, rng, j)    -> child genotype or None (edit not applied). rng: random.Random; j: probe index
    evaluate(g)          -> (behaviour, score): behaviour hashable signature over a DECLARED input set,
                            score = pi(behaviour) (the task projection)
    gkey(g)              -> hashable genotype identity
    neutral(s, s0)       -> bool   (anchored to the ORIGINAL parent score s0)
    improving(s, s0)     -> bool
    sample(rng)          -> random genotype (null distribution)
    bdist(b1, b2)        -> behaviour distance (optional; for "distance to nearest improving behaviour")
    extra(g, child)      -> optional dict of per-probe annotations (e.g. did the edit hit non-coding sites)

Design (PREREG.md): walker at g_d gets m probes; applied probes are classified; then one neutral step (<= 64
proposals). Everything below is computed from the logged probe rows, so metrics can be recomputed offline.
"""
from __future__ import annotations

import hashlib
import math
import random
from collections import Counter, defaultdict

MAX_PROPOSALS = 64


def rng_for(*parts):
    h = hashlib.sha256(repr(parts).encode()).digest()
    return random.Random(int.from_bytes(h[:8], "big"))


class Spec:
    def __init__(self, name, mutate, evaluate, gkey, neutral, improving, sample=None, bdist=None, extra=None):
        self.name, self.mutate, self.evaluate, self.gkey = name, mutate, evaluate, gkey
        self.neutral, self.improving, self.sample, self.bdist, self.extra = neutral, improving, sample, bdist, extra


# ------------------------------------------------------------------ walking
def walk(spec, parent, pid, w, D, m):
    """One walker. Returns a dict with the node list and probe rows (behaviours kept as python objects)."""
    b0, s0 = spec.evaluate(parent)
    cur, bcur = parent, b0
    nodes, probes = [], []
    stalled_at = None
    wrng = rng_for(spec.name, "walk", pid, w)
    for d in range(D + 1):
        nodes.append({"d": d, "g": spec.gkey(cur), "b": bcur})
        for j in range(m):
            prng = rng_for(spec.name, "probe", pid, w, d, j)
            c = spec.mutate(cur, prng, j)
            if c is None:
                continue
            b, s = spec.evaluate(c)
            row = {"d": d, "j": j, "src_b": bcur, "g": spec.gkey(c), "b": b, "s": s,
                   "neutral": bool(spec.neutral(s, s0)), "imp": bool(spec.improving(s, s0))}
            if spec.extra is not None:
                row.update(spec.extra(cur, c, b, s))
            probes.append(row)
        if d == D:
            break
        nxt = None
        for _ in range(MAX_PROPOSALS):
            c = spec.mutate(cur, wrng, -1)
            if c is None:
                continue
            b, s = spec.evaluate(c)
            if spec.neutral(s, s0):
                nxt, nb = c, b
                break
        if nxt is None:
            stalled_at = d
            break
        cur, bcur = nxt, nb
    return {"pid": pid, "w": w, "s0": s0, "b0": b0, "nodes": nodes, "probes": probes, "stalled_at": stalled_at}


def null_sample(spec, n, label="null"):
    out = []
    for i in range(n):
        g = spec.sample(rng_for(spec.name, label, i))
        b, s = spec.evaluate(g)
        out.append({"g": spec.gkey(g), "b": b, "s": s})
    return out


# ------------------------------------------------------------------ metric helpers
def entropy_bits(counter):
    n = sum(counter.values())
    if n == 0:
        return 0.0
    return -sum(c / n * math.log2(c / n) for c in counter.values() if c)


def rarefied_distinct(items, k, reps=20, seed=0):
    """Expected distinct count in a uniform subsample of size k (without replacement), Monte Carlo."""
    items = list(items)
    if k >= len(items):
        return float(len(set(items)))
    r = random.Random(seed)
    return sum(len(set(r.sample(items, k))) for _ in range(reps)) / reps


def median(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


def slope(xs, ys):
    n = len(xs)
    if n < 2:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    vx = sum((x - mx) ** 2 for x in xs)
    return None if vx == 0 else sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / vx


def components(nodes, edges):
    parent = {v: v for v in nodes}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, b in edges:
        if a in parent and b in parent:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb
    comp = defaultdict(set)
    for v in nodes:
        comp[find(v)].add(v)
    return list(comp.values())


def walker_novelty(wk, D):
    """nov(d), nov_n(d), revisit(d>0), E(d) cumulative distinct behaviours, Gcum(d) cumulative distinct genotypes."""
    seen = {wk["b0"]}
    seen_g = {wk["nodes"][0]["g"]}
    by_d = defaultdict(list)
    for p in wk["probes"]:
        by_d[p["d"]].append(p)
    nov, nov_n, rev, E, G = {}, {}, {}, {}, {}
    for d in range(D + 1):
        rows = by_d.get(d, [])
        if d >= len(wk["nodes"]):
            break
        seen_g.add(wk["nodes"][d]["g"])
        seen.add(wk["nodes"][d]["b"])
        prior = set(seen)
        new = newn = nn = old = 0
        for p in rows:
            if p["b"] not in seen:
                new += 1
                if p["neutral"]:
                    newn += 1
            if p["neutral"]:
                nn += 1
            if d > 0 and p["b"] in prior:
                old += 1
            seen.add(p["b"])
            seen_g.add(p["g"])
        nov[d] = new / len(rows) if rows else None
        nov_n[d] = newn / nn if nn else None
        rev[d] = (old / len(rows) if rows else None) if d > 0 else None
        E[d] = len(seen)
        G[d] = len(seen_g)
    return nov, nov_n, rev, E, G


def parent_metrics(walkers, D, null=None, bdist=None):
    """Metrics M1..M7 for one parent (list of walker dicts from the same parent)."""
    b0, s0 = walkers[0]["b0"], walkers[0]["s0"]
    neut_g, neut_b = set(), set()
    neutral_probe_b = Counter()
    for wk in walkers:
        for nd in wk["nodes"]:
            neut_g.add(nd["g"]); neut_b.add(nd["b"])
        for p in wk["probes"]:
            if p["neutral"]:
                neut_g.add(p["g"]); neut_b.add(p["b"]); neutral_probe_b[p["b"]] += 1
    n_neut = sum(neutral_probe_b.values())
    applied = sum(len(wk["probes"]) for wk in walkers)
    # M4 / M7
    novs, novns, revs, Es, Gs = [], [], [], [], []
    for wk in walkers:
        a, b, c, e, g = walker_novelty(wk, D)
        novs.append(a); novns.append(b); revs.append(c); Es.append(e); Gs.append(g)

    def mean_at(dicts, d):
        xs = [x.get(d) for x in dicts if x.get(d) is not None]
        return sum(xs) / len(xs) if xs else None
    depths = list(range(D + 1))
    nov_curve = [mean_at(novs, d) for d in depths]
    novn_curve = [mean_at(novns, d) for d in depths]
    rev_curve = [mean_at(revs, d) for d in depths]
    E_curve = [mean_at(Es, d) for d in depths]
    G_curve = [mean_at(Gs, d) for d in depths]
    late = [x for x in nov_curve[-max(1, (D + 1) // 3):] if x is not None]
    decay = (sum(late) / len(late) / nov_curve[0]) if late and nov_curve[0] else None
    expansion = (E_curve[-1] / E_curve[0]) if E_curve[-1] and E_curve[0] else None
    pts = [(math.log(g), math.log(e)) for g, e in zip(G_curve, E_curve) if g and e]
    heaps = slope([p[0] for p in pts], [p[1] for p in pts]) if len(pts) >= 3 else None
    # M5 mutational distance and per-depth improvement rate
    first_L = []
    imp_rate = []
    for d in depths:
        rows = [p for wk in walkers for p in wk["probes"] if p["d"] == d]
        imp_rate.append(sum(p["imp"] for p in rows) / len(rows) if rows else None)
    for wk in walkers:
        ds = [p["d"] for p in wk["probes"] if p["imp"]]
        first_L.append(min(ds) + 1 if ds else None)
    n_found = sum(1 for x in first_L if x is not None)
    imp_b = {p["b"] for wk in walkers for p in wk["probes"] if p["imp"]}
    if null:
        imp_b |= {r["b"] for r in null if r.get("imp")}
    bd = min((bdist(b0, b) for b in imp_b), default=None) if bdist else None
    # M6 connectivity
    edges = Counter()
    for wk in walkers:
        for p in wk["probes"]:
            edges[(p["src_b"], p["b"])] += 1
    from_parent_class = [(a, b) for (a, b), c in edges.items() for _ in range(c) if a == b0]
    robust_parent = sum(1 for a, b in from_parent_class if b == b0) / len(from_parent_class) if from_parent_class else None
    pheno_evo = len({b for a, b in from_parent_class if b != b0})
    geno_evo = []
    geno_rob = []
    for wk in walkers:
        for nd in wk["nodes"]:
            rows = [p for p in wk["probes"] if p["d"] == nd["d"]]
            if rows:
                geno_evo.append(len({p["b"] for p in rows} - {nd["b"]}))
                geno_rob.append(sum(p["b"] == nd["b"] for p in rows) / len(rows))
    neutral_classes = set(neut_b)
    nedges = [(a, b) for (a, b) in edges if a in neutral_classes and b in neutral_classes and a != b]
    comps = components(neutral_classes, nedges)
    pc = next((c for c in comps if b0 in c), {b0})
    out = {
        "s0": s0, "applied_probes": applied, "neutral_probes": n_neut,
        "neutral_fraction": n_neut / applied if applied else None,
        "G": len(neut_g), "B": len(neut_b), "B_over_G": len(neut_b) / len(neut_g) if neut_g else None,
        "H_bits": entropy_bits(neutral_probe_b), "DOM": neutral_probe_b[b0] / n_neut if n_neut else None,
        "B_all_probes": len({p["b"] for wk in walkers for p in wk["probes"]}),
        "nov_curve": nov_curve, "nov_neutral_curve": novn_curve, "revisit_curve": rev_curve,
        "E_curve": E_curve, "Gcum_curve": G_curve, "novelty_decay": decay, "expansion_ratio": expansion,
        "heaps_exponent": heaps, "imp_rate_by_d": imp_rate, "first_improving_L": first_L,
        "walkers_with_improvement": n_found, "walkers": len(walkers),
        "behav_dist_to_nearest_improving": bd,
        "parent_class_robustness": robust_parent, "phenotype_evolvability_parent_class": pheno_evo,
        "genotype_evolvability_mean": sum(geno_evo) / len(geno_evo) if geno_evo else None,
        "genotype_robustness_mean": sum(geno_rob) / len(geno_rob) if geno_rob else None,
        "neutral_classes": len(neutral_classes), "neutral_components": len(comps),
        "share_neutral_classes_in_parent_component": len(pc) / len(neutral_classes) if neutral_classes else None,
        "stalls": sum(1 for wk in walkers if wk["stalled_at"] is not None),
    }
    if null:
        nb = [r["b"] for r in null]
        k = min(n_neut, len(nb))
        neut_list = [b for b, c in neutral_probe_b.items() for _ in range(c)]
        Bn = rarefied_distinct(neut_list, k) if k else None
        Bnull = rarefied_distinct(nb, k) if k else None
        out.update({"null_share_parent_behaviour": sum(1 for b in nb if b == b0) / len(nb),
                    "rarefied_k": k, "B_neutral_k": Bn, "B_null_k": Bnull,
                    "relative_poverty": (Bn / Bnull) if Bn is not None and Bnull else None})
    return out


def null_metrics(null, s0=None, improving=None):
    c = Counter(r["b"] for r in null)
    n = len(null)
    out = {"n": n, "distinct_behaviours": len(c), "B_over_n": len(c) / n if n else None,
           "H_bits": entropy_bits(c), "top_behaviour_share": max(c.values()) / n if n else None,
           "distinct_genotypes": len({r["g"] for r in null})}
    return out


def summarize(per_parent, D):
    keys = ["G", "B", "B_over_G", "H_bits", "DOM", "neutral_fraction", "novelty_decay", "expansion_ratio",
            "heaps_exponent", "behav_dist_to_nearest_improving", "parent_class_robustness",
            "phenotype_evolvability_parent_class", "genotype_evolvability_mean", "genotype_robustness_mean",
            "neutral_classes", "neutral_components", "share_neutral_classes_in_parent_component",
            "relative_poverty", "null_share_parent_behaviour", "B_all_probes"]
    s = {"median_" + k: median([p.get(k) for p in per_parent.values()]) for k in keys}
    s["pooled_G"] = None
    for curve in ("nov_curve", "nov_neutral_curve", "revisit_curve", "E_curve", "imp_rate_by_d"):
        cs = [p[curve] for p in per_parent.values()]
        s["mean_" + curve] = [round(sum(c[d] for c in cs if c[d] is not None) / max(1, sum(1 for c in cs if c[d] is not None)), 5)
                              if any(c[d] is not None for c in cs) else None for d in range(D + 1)]
    s["walkers_with_improvement"] = sum(p["walkers_with_improvement"] for p in per_parent.values())
    s["walkers"] = sum(p["walkers"] for p in per_parent.values())
    s["poverty_i"] = s["median_B_over_G"] is not None and s["median_B_over_G"] <= 0.05
    s["poverty_ii"] = s["median_DOM"] is not None and s["median_DOM"] >= 0.80
    s["BEHAVIOURAL_POVERTY"] = bool(s["poverty_i"] and s["poverty_ii"])
    return s


def pooled(walkers_all):
    g, b = set(), set()
    for wk in walkers_all:
        for nd in wk["nodes"]:
            g.add((wk["pid"], nd["g"])); b.add(nd["b"])
        for p in wk["probes"]:
            if p["neutral"]:
                g.add((wk["pid"], p["g"])); b.add(p["b"])
    return {"pooled_neutral_genotypes": len(g), "pooled_neutral_behaviours": len(b)}


def run_all(spec, parents, W, D, m, procs=1, null_n=0):
    """parents: list of (pid, genotype). Returns (walkers, null rows)."""
    jobs = [(pid, g, w) for pid, g in parents for w in range(W)]
    if procs > 1:
        from multiprocessing import Pool
        with Pool(procs) as pool:
            walkers = pool.starmap(_job, [(spec, pid, g, w, D, m) for pid, g, w in jobs])
    else:
        walkers = [walk(spec, g, pid, w, D, m) for pid, g, w in jobs]
    null = null_sample(spec, null_n) if null_n else []
    return walkers, null


def _job(spec, pid, g, w, D, m):
    return walk(spec, g, pid, w, D, m)


def analyse(spec, walkers, null, D):
    s0_by = {wk["pid"]: wk["s0"] for wk in walkers}
    by = defaultdict(list)
    for wk in walkers:
        by[wk["pid"]].append(wk)
    per = {}
    for pid, ws in by.items():
        nl = [dict(r, imp=spec.improving(r["s"], s0_by[pid])) for r in null] if null else None
        per[pid] = parent_metrics(ws, D, nl, spec.bdist)
    summ = summarize(per, D)
    summ.update(pooled(walkers))
    return per, summ


# ------------------------------------------------------------------ exact enumeration (small spaces; tests)
def exact_map(genotypes, neighbours, behaviour):
    """Exhaustive: per phenotype neutral-set size, phenotype robustness, Wagner phenotype evolvability; mean
    genotype robustness and genotype evolvability; class graph edges."""
    ph = {g: behaviour(g) for g in genotypes}
    size = Counter(ph.values())
    stay = Counter(); tot = Counter(); adj = defaultdict(set)
    grob, gevo = [], []
    for g in genotypes:
        nb = [ph[h] for h in neighbours(g)]
        p = ph[g]
        tot[p] += len(nb); stay[p] += sum(1 for q in nb if q == p)
        adj[p].update(q for q in nb if q != p)
        grob.append(sum(1 for q in nb if q == p) / len(nb)); gevo.append(len(set(nb) - {p}))
    edges = {tuple(sorted((a, b))) for a in adj for b in adj[a]}
    return {"n_phenotypes": len(size), "size": dict(size),
            "phen_robustness": {p: stay[p] / tot[p] for p in size},
            "phen_evolvability": {p: len(adj[p]) for p in size},
            "geno_robustness_mean": sum(grob) / len(grob), "geno_evolvability_mean": sum(gevo) / len(gevo),
            "edges": edges}
