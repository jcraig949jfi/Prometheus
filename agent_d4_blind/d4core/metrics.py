"""Census, operator causal census, graph metrics, target selection,
navigation experiments. All against the abstract interface only."""
from __future__ import annotations

import hashlib

import numpy as np

from .classifier import identifiability, wilson_ci
from .navigators import NAVIGATORS, EdgeStore


# ---------------------------------------------------------------- census ----
def run_census(sub, n: int, rng, store: EdgeStore, keep_viable: int = 3000) -> dict:
    sub.meter.set_component("census")
    viable_n = 0
    classes: dict = {}
    viable_pool: list = []
    curve = []
    for i in range(n):
        g = sub.random_genome(rng)
        f = sub.evaluate(g)
        store.see(sub, f)
        v = sub.viable(f)
        if v:
            viable_n += 1
            k = sub.pkey(f)
            classes[k] = classes.get(k, 0) + 1
            if len(viable_pool) < keep_viable:
                viable_pool.append((g, f))
        if (i + 1) % max(1, n // 20) == 0:
            curve.append([i + 1, len(classes)])
    f1 = sum(1 for c in classes.values() if c == 1)
    lo, hi = wilson_ci(viable_n, n)
    return {
        "n": n, "viable_n": viable_n, "viable_frac": viable_n / n,
        "viable_frac_ci95": [lo, hi],
        "n_classes_viable": len(classes),
        "good_turing_unseen_mass": (f1 / viable_n) if viable_n else None,
        "singleton_classes": f1,
        "coverage_curve": curve,
        "_viable_pool": viable_pool,
        "_class_counts": classes,
    }


# ------------------------------------------------- operator causal census ----
def op_census(sub, viable_pool, rng, n_parents: int, reps: int, store: EdgeStore,
              n_cross: int = 500, rev_sample: int = 400, rev_tries: int = 8) -> dict:
    sub.meter.set_component("operator_census")
    parents = viable_pool[:n_parents]
    rows_op, rows_same, rows_vch, rows_d1, rows_parent = [], [], [], [], []
    feats = []
    reach: dict[int, set] = {op: set() for op in range(sub.n_ops)}
    rev_pool: list = []
    for pi, (g, f) in enumerate(parents):
        pk = sub.pkey(f)
        for op in range(sub.n_ops):
            for _ in range(reps):
                child = sub.mutate(g, op, rng)
                fc = sub.evaluate(child)
                store.edge(sub, f, op, fc)
                same = sub.pkey(fc) == pk
                vch = sub.viable(fc)
                d = sub.d1(f, fc)
                rows_op.append(op)
                rows_same.append(same)
                rows_vch.append(vch)
                rows_d1.append(d)
                rows_parent.append(pi)
                feats.append(sub.disp_features(f, fc))
                if vch:
                    reach[op].add(sub.pkey(fc))
                if (not same) and len(rev_pool) < rev_sample * 4:
                    rev_pool.append((g, pk, child, op))
    rows_op = np.array(rows_op)
    rows_same = np.array(rows_same)
    rows_vch = np.array(rows_vch)
    rows_d1 = np.array(rows_d1)
    rows_parent = np.array(rows_parent)
    feats = np.array(feats)

    per_op = {}
    for op in range(sub.n_ops):
        m = rows_op == op
        nn = int(m.sum())
        ident = float(rows_same[m].mean()) if nn else None
        vfrac = float(rows_vch[m].mean()) if nn else None
        nonid_viable = float((~rows_same[m] & rows_vch[m]).mean()) if nn else None
        per_op[op] = {
            "n": nn, "identity_rate": ident, "child_viable_rate": vfrac,
            "effective_rate": nonid_viable,  # non-identity AND viable child
            "d1_mean": float(rows_d1[m].mean()) if nn else None,
            "d1_median": float(np.median(rows_d1[m])) if nn else None,
            "d1_p90": float(np.quantile(rows_d1[m], 0.9)) if nn else None,
            "reach_support": len(reach[op]),
        }
    # pairwise reach overlap (Jaccard)
    overlap = {}
    for a in range(sub.n_ops):
        for b in range(a + 1, sub.n_ops):
            u = reach[a] | reach[b]
            overlap[f"{a}-{b}"] = (len(reach[a] & reach[b]) / len(u)) if u else None

    # reversibility: from child, can ANY menu op recover the parent phenotype?
    sub.meter.set_component("reversibility")
    rev_results = {op: [0, 0] for op in range(sub.n_ops)}
    ridx = np.random.default_rng(9900).permutation(len(rev_pool))[:rev_sample]
    for i in ridx:
        g, pk, child, op = rev_pool[i]
        ok = False
        for _ in range(rev_tries):
            op2 = sub.sample_op(rng)
            g2 = sub.mutate(child, op2, rng)
            f2 = sub.evaluate(g2)
            if sub.pkey(f2) == pk:
                ok = True
                break
        rev_results[op][0] += int(ok)
        rev_results[op][1] += 1
    reversibility = {op: (rev_results[op][0] / rev_results[op][1]) if rev_results[op][1] else None
                     for op in rev_results}

    # crossover census (registered mechanism; two-parent)
    sub.meter.set_component("operator_census")
    x_same = x_viable = 0
    x_d1 = []
    npair = min(n_cross, len(parents) - 1)
    for i in range(npair):
        g1, f1 = parents[i]
        g2, f2 = parents[int(rng.integers(0, len(parents)))]
        child = sub.crossover(g1, g2, rng)
        fc = sub.evaluate(child)
        store.see(sub, fc)
        if sub.pkey(fc) == sub.pkey(f1) or sub.pkey(fc) == sub.pkey(f2):
            x_same += 1
        if sub.viable(fc):
            x_viable += 1
        x_d1.append(min(sub.d1(f1, fc), sub.d1(f2, fc)))

    pooled_identity = float(rows_same.mean())
    pooled_effective = float((~rows_same & rows_vch).mean())
    alive_ops = [op for op in range(sub.n_ops) if per_op[op]["effective_rate"] is not None
                 and per_op[op]["effective_rate"] >= 0.02]

    # identifiability on non-identity rows
    nonid = ~rows_same
    ident_res = identifiability(feats[nonid], rows_op[nonid], rows_parent[nonid], sub.n_ops)

    # anisotropy: top-1 covariance eigenshare of non-identity displacement features
    aniso = None
    if nonid.sum() > 50:
        Fnz = feats[nonid]
        C = np.cov(Fnz.T)
        ev = np.linalg.eigvalsh(C)
        tot = float(ev.sum())
        aniso = float(ev[-1] / tot) if tot > 1e-15 else None

    return {
        "per_op": per_op,
        "overlap_jaccard": overlap,
        "reversibility": reversibility,
        "pooled_identity_rate": pooled_identity,
        "pooled_effective_rate": pooled_effective,
        "n_transitions": int(len(rows_op)),
        "alive_ops": alive_ops,
        "n_alive_ops": len(alive_ops),
        "crossover": {
            "n": npair,
            "parent_identity_rate": (x_same / npair) if npair else None,
            "child_viable_rate": (x_viable / npair) if npair else None,
            "d1_to_nearest_parent_mean": float(np.mean(x_d1)) if x_d1 else None,
        },
        "identifiability": ident_res,
        "anisotropy_top_share": aniso,
    }


# ---------------------------------------------------------- graph metrics ----
def gini(x: np.ndarray) -> float:
    x = np.sort(np.asarray(x, dtype=float))
    n = len(x)
    if n == 0 or x.sum() == 0:
        return 0.0
    cum = np.cumsum(x)
    return float((n + 1 - 2 * np.sum(cum) / cum[-1]) / n)


def graph_metrics(store: EdgeStore) -> dict:
    edges = [(a, b) for (a, b) in store.edges if a != b]
    nodes = set()
    indeg: dict = {}
    outdeg: dict = {}
    for a, b in edges:
        nodes.add(a)
        nodes.add(b)
        indeg[b] = indeg.get(b, 0) + 1
        outdeg[a] = outdeg.get(a, 0) + 1
    n = len(nodes)
    if n == 0:
        return {"n_nodes": 0}
    parent = {v: v for v in nodes}

    def find(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v

    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    comp: dict = {}
    for v in nodes:
        r = find(v)
        comp[r] = comp.get(r, 0) + 1
    sizes = sorted(comp.values(), reverse=True)
    ind = np.array([indeg.get(v, 0) for v in nodes])
    k = max(1, n // 100)
    top = np.sort(ind)[-k:]
    return {
        "n_nodes": n, "n_edges": len(edges),
        "giant_component_share": sizes[0] / n,
        "n_components": len(sizes),
        "indegree_gini": gini(ind),
        "hub_top1pct_inedge_share": float(top.sum() / ind.sum()) if ind.sum() else 0.0,
        "self_loop_edges": int(len(store.edges) - len(edges)),
        "dead_end_share_observed": float(np.mean([outdeg.get(v, 0) == 0 for v in nodes])),
    }


# -------------------------------------------------------- target selection ----
def select_targets(sub, rng, n_walks: int, walk_len: int, n_ref: int,
                   eps_dens: float, k_low: int, k_high: int, store: EdgeStore,
                   dens_sample: int = 400, max_attempts_factor: int = 5) -> dict:
    sub.meter.set_component("target_generation")
    pool: dict = {}
    for _ in range(n_walks):
        g, f = None, None
        tries = 0
        while f is None and tries < 200:
            gg = sub.random_genome(rng)
            ff = sub.evaluate(gg)
            store.see(sub, ff)
            tries += 1
            if sub.viable(ff):
                g, f = gg, ff
        if f is None:
            continue
        pool.setdefault(sub.pkey(f), f)
        accepted = 0
        attempts = 0
        while accepted < walk_len and attempts < walk_len * max_attempts_factor:
            op = sub.sample_op(rng)
            child = sub.mutate(g, op, rng)
            fc = sub.evaluate(child)
            attempts += 1
            store.edge(sub, f, op, fc)
            if sub.viable(fc):
                g, f = child, fc
                accepted += 1
                pool.setdefault(sub.pkey(f), f)
    refs = []
    tries = 0
    while len(refs) < n_ref and tries < n_ref * 50:
        gg = sub.random_genome(rng)
        ff = sub.evaluate(gg)
        tries += 1
        if sub.viable(ff):
            refs.append(ff)
    pool_items = list(pool.items())
    if len(pool_items) < 3 * (k_low + k_high) or len(refs) < max(3, n_ref // 4):
        return {"status": "POOL_TOO_SMALL", "pool_size": len(pool_items),
                "n_refs": len(refs)}
    remoteness = np.array([np.mean([sub.d1m(f, r) for r in refs]) for _, f in pool_items])
    # density vs a deterministic subsample of the pool
    sidx = np.random.default_rng(8801).permutation(len(pool_items))[:dens_sample]
    density = np.zeros(len(pool_items))
    for i, (_, f) in enumerate(pool_items):
        density[i] = sum(1 for j in sidx if j != i and sub.d1m(f, pool_items[j][1]) <= eps_dens)
    t1, t2 = np.quantile(remoteness, [1 / 3, 2 / 3])
    targets = []
    for sname, mask in (("near", remoteness <= t1),
                        ("mid", (remoteness > t1) & (remoteness <= t2)),
                        ("far", remoteness > t2)):
        idx = np.where(mask)[0]

        def hkey(i):
            return hashlib.sha256(sub.fp_bytes(pool_items[i][1])).hexdigest()

        by_dens = sorted(idx, key=lambda i: (density[i], hkey(i)))
        chosen = list(by_dens[:k_low]) + list(by_dens[-k_high:]) if len(by_dens) >= k_low + k_high else list(by_dens)
        seen = set()
        for i in chosen:
            if i in seen:
                continue
            seen.add(i)
            targets.append({
                "target_id": f"{sname}_{hkey(i)[:12]}",
                "stratum": sname, "pkey": pool_items[i][0],
                "fp": pool_items[i][1],
                "remoteness": float(remoteness[i]), "density": int(density[i]),
            })
    return {"status": "OK", "pool_size": len(pool_items), "n_refs": len(refs),
            "remoteness_tertiles": [float(t1), float(t2)],
            "targets": targets}


# ------------------------------------------------------ navigation battery ----
def run_navigation(sub, targets, nav_plan, budget: int, eps_hit: float,
                   store: EdgeStore, component: str = "navigation",
                   base_seed: int = 5000) -> list:
    """nav_plan: list of (nav_name, n_seeds). Returns list of row dicts."""
    sub.meter.set_component(component)
    rows = []
    for nav_name, n_seeds in nav_plan:
        fn = NAVIGATORS[nav_name]
        for t in targets:
            for s in range(n_seeds):
                h = hashlib.sha256(f"{nav_name}|{t['target_id']}|{s}".encode()).digest()
                seed = base_seed + int.from_bytes(h[:4], "little")
                rng = np.random.default_rng(seed)
                res = fn(sub, rng, budget, target_fp=t["fp"], eps_hit=eps_hit,
                         store=store)
                rows.append({
                    "navigator": nav_name, "target_id": t["target_id"],
                    "stratum": t["stratum"], "seed": s,
                    "hit": res["hit"], "evals_to_hit": res["evals_to_hit"],
                    "best_d": res["best_d"], "evals_used": res["evals_used"],
                })
    return rows


def run_coverage(sub, nav_names, n_seeds: int, budget: int, store: EdgeStore,
                 base_seed: int = 6000) -> dict:
    sub.meter.set_component("navigation")
    out = {}
    for nav_name in nav_names:
        fn = NAVIGATORS[nav_name]
        curves = []
        for s in range(n_seeds):
            cov: list = []
            h = hashlib.sha256(f"cov|{nav_name}|{s}".encode()).digest()
            rng = np.random.default_rng(base_seed + int.from_bytes(h[:4], "little"))
            fn(sub, rng, budget, target_fp=None, store=store, coverage_out=cov)
            seen = set()
            curve = []
            for evals, pk in cov:
                seen.add(pk)
                curve.append((evals, len(seen)))
            # subsample curve
            step = max(1, len(curve) // 50)
            curves.append([list(curve[i]) for i in range(0, len(curve), step)] +
                          ([list(curve[-1])] if curve else []))
        out[nav_name] = curves
    return out


def summarize_navigation(rows, pair) -> dict:
    """Pooled/stratified hit rates, first-passage, re-findability."""
    out = {"per_navigator": {}}
    navs = sorted({r["navigator"] for r in rows})
    for nav in navs:
        rs = [r for r in rows if r["navigator"] == nav]
        n = len(rs)
        hits = sum(r["hit"] for r in rs)
        strata = {}
        for sname in ("near", "mid", "far"):
            ss = [r for r in rs if r["stratum"] == sname]
            if ss:
                k = sum(r["hit"] for r in ss)
                lo, hi = wilson_ci(k, len(ss))
                strata[sname] = {"n": len(ss), "hit_rate": k / len(ss), "ci95": [lo, hi]}
        # re-findability over targets with >=1 hit
        by_target: dict = {}
        for r in rs:
            by_target.setdefault(r["target_id"], []).append(r["hit"])
        once_hit = {t: v for t, v in by_target.items() if any(v)}
        refind = (float(np.mean([np.mean(v) for v in once_hit.values()]))
                  if once_hit else 0.0)
        fp_costs = [r["evals_to_hit"] for r in rs if r["hit"]]
        lo, hi = wilson_ci(hits, n)
        out["per_navigator"][nav] = {
            "n_runs": n, "pooled_hit_rate": hits / n if n else 0.0,
            "pooled_ci95": [lo, hi],
            "strata": strata,
            "n_targets_once_hit": len(once_hit),
            "n_targets": len(by_target),
            "refind_ratio": refind,
            "first_passage_median": float(np.median(fp_costs)) if fp_costs else None,
        }
    pair_stats = [out["per_navigator"].get(p) for p in pair if p in out["per_navigator"]]
    out["competitive_pair"] = list(pair)
    out["pair_pooled_hits"] = [p["pooled_hit_rate"] for p in pair_stats if p]
    out["best_pair_nav"] = None
    if pair_stats and any(p for p in pair_stats):
        best = max((p for p in pair_stats if p), key=lambda p: p["pooled_hit_rate"])
        for name, stats in out["per_navigator"].items():
            if stats is best:
                out["best_pair_nav"] = name
    return out
