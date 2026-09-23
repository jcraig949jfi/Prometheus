"""P-F02 [T-X17, cycle-5 re-pose]: RESPONSE-GEOMETRY CENSUS as a MANIFOLD measurement.

Raw dose-response curves: 0-4 idle (empty) ticks at every construction position (W0D1 before the ask;
W0D2 between the PUTs / before the ask / before the first PUT; K2 between the PUTs / before the first
ask / before the second ask) plus two order variants (W0D1: noise-then-empty vs empty-then-noise) - a
30-dimensional self-displacement vector per program. Programs: parents, walkers at depth 4/8/16, C4-08
tops, P-F03's evolved and transplanted tops. Retained: curves, transition dose per position, lineage,
world, genome summaries. Clustering with k chosen by silhouette over 2-6; cluster shapes reported before
any label; an unseen stable shape is flagged for promotion. Computational scope: integer programs on a
bounded VM.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as CM            # noqa: E402
import ticks as TK             # noqa: E402
A, L = CM.A, CM.L
sys.path.insert(0, str(HERE.parent / "P-D01"))
from run_PD01 import c408_tops   # noqa: E402

PID, TID = "P-F02", "T-X17"
POS = [("W0D1", "before_first_ask"), ("W0D2", "between_puts"), ("W0D2", "before_first_ask"), ("W0D2", "before_first_put"), ("K2", "between_puts"), ("K2", "before_first_ask"), ("K2", "before_second_ask")]
DOSES = (1, 2, 3, 4)
KEYS = ["%s.%s.n%d" % (w, p, n) for w, p in POS for n in DOSES] + ["W0D1.order_ne", "W0D1.order_en"]
_C = {}


def worlds():
    if "W" not in _C:
        _C["W"] = {"W0D1": A.episodes("W0"), "W0D2": A.episodes_for(TK.W0D2, A.CAMPAIGN_SEED, "train", 1, A.C1.E), "K2": A.episodes("W2_K2")}
        V = {}
        for w, eps in _C["W"].items():
            V[w] = {"base": [TK.clone(e) for e in eps]}
            for _, pos in [x for x in POS if x[0] == w]:
                for n in DOSES:
                    out = []
                    for ep in eps:
                        puts, asks = TK.put_ticks(ep), TK.ask_ticks(ep)
                        at = {"before_first_ask": asks[0], "between_puts": puts[1] if len(puts) > 1 else puts[0], "before_first_put": puts[0], "before_second_ask": asks[1] if len(asks) > 1 else asks[0]}[pos]
                        out.append(TK.insert(ep, at, [[]] * n))
                    V[w]["%s.n%d" % (pos, n)] = out
        w0 = TK.w0_variants(_C["W"]["W0D1"])
        V["W0D1"]["order_ne"], V["W0D1"]["order_en"] = w0["ne"], w0["en"]
        _C["V"] = V
    return _C["W"], _C["V"]


def curve(m):
    W, V = worlds()
    vec, answered = {}, {}
    for w in W:
        a0 = A.C1.answers(m, V[w]["base"])
        answered[w] = any(x is not None for x in a0)
        for k, eps in V[w].items():
            if k == "base":
                continue
            name = "%s.%s" % (w, k)
            if not answered[w]:
                vec[name] = float("nan")
                continue
            a1 = A.C1.answers(m, eps)
            if w == "K2" and k.startswith("before_first_ask") or (w == "K2" and k.startswith("before_second_ask")):
                pos = 0 if k.startswith("before_first_ask") else 1
                vec[name] = A.C1.displacement(a1[pos::2], a0[pos::2])
            else:
                vec[name] = A.C1.displacement(a1, a0)
    return [vec[k] for k in KEYS], answered


def job(j):
    p = j["program"]
    m = A.canonical(p["manifest"])
    v, ans = curve(m)
    ev = A.evaluate(m, A.episodes(p.get("env", "W0")), rng_seed=0, reward_mode="per_ask")
    trans = {}
    for w, pos in POS:
        vals = [v[KEYS.index("%s.%s.n%d" % (w, pos, n))] for n in DOSES]
        t = next((n for n, x in zip(DOSES, vals) if x == x and x >= 0.1), None)
        trans["%s.%s" % (w, pos)] = t
    return {"pid": p["organism_id"], "lineage": p["lineage"], "world": p.get("env"), "vector": v, "answered": ans, "transition": trans,
            "n_instr": CM.n_instr(m), "persist": m["persist"], "persistent_words": ev["meter"].get("persistent_state_words", 0), "r0": ev["reward_per_ask"]}


def kmeans(X, k, seed=0, iters=50):
    rng = np.random.Generator(np.random.PCG64(seed))
    best = None
    for _ in range(10):
        C = X[rng.choice(len(X), k, replace=False)]
        for _ in range(iters):
            lab = np.argmin(((X[:, None, :] - C[None, :, :]) ** 2).sum(-1), axis=1)
            C2 = np.array([X[lab == i].mean(0) if (lab == i).any() else C[i] for i in range(k)])
            if np.allclose(C2, C):
                break
            C = C2
        sse = float(((X - C[lab]) ** 2).sum())
        if best is None or sse < best[0]:
            best = (sse, lab, C)
    return best[1], best[2]


def silhouette(X, lab):
    n = len(X)
    D = np.sqrt(((X[:, None, :] - X[None, :, :]) ** 2).sum(-1))
    s = []
    for i in range(n):
        own = lab == i * 0 + lab[i]
        a = D[i][own & (np.arange(n) != i)].mean() if own.sum() > 1 else 0.0
        b = min(D[i][lab == c].mean() for c in set(lab) if c != lab[i]) if len(set(lab)) > 1 else 0.0
        s.append((b - a) / max(a, b, 1e-9))
    return float(np.mean(s))


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "scope": CM.SCOPE, "claim_type": "manifold-measurement", "positions": POS, "doses": DOSES, "vector_keys": KEYS,
                         "programs": "parents (all strata), walkers at depth 4/8/16, C4-08 tops, P-F03 evolved (8 arms x 16) and transplanted (4 x 16) tops",
                         "retained": ["raw curves", "transition dose per position (first dose with displacement >= .1)", "order variants (hysteresis proxy)", "lineage", "world", "n_instr / persist / persistent words / reward"],
                         "clustering": "k-means on programs with complete vectors, k in 2..6 chosen by silhouette; cluster centroids and composition reported; a cluster is an UNSEEN shape if its centroid matches none of: immune (all < .1), ask-time (W0D1/K2 before-ask >= .5 and K2 between_puts < .1), schedule (K2 between_puts >= .5 and before-asks < .1)",
                         "material_rule": "an unseen stable shape (>= 8 members) exists, or transition doses differ from 1 (dose-dependence) in >= 10 percent of sensitive positions, or order variants differ by >= .1 in >= 10 percent of programs", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    parents = [p for p in CM.viable_parents() if not p["degenerate"]]
    programs = [dict(p, lineage="parent:" + p["stratum"]) for p in parents]
    for p in parents:
        wk = A.C5.walk(p["manifest"], p["organism_id"], 1, A.episodes(p["env"]), 16, 32)
        for d in (4, 8, 16):
            if d in wk["archived"]:
                programs.append({"organism_id": "%s/w1d%d" % (p["organism_id"], d), "lineage": "walker%d:%s" % (d, p["stratum"]), "manifest": wk["archived"][d], "env": p["env"]})
    programs += [dict(p, lineage="c408") for p in c408_tops()]
    tops = json.loads((HERE.parent / "P-F03" / "tops.json").read_text(encoding="utf-8"))
    for x in tops:
        for i, t in enumerate(x["tops"][:16]):
            programs.append({"organism_id": "pf03-%s-%s-%d-%s-%d" % (x["env"], x["mode"], x["seed"], x["stage"], i), "lineage": "pf03:%s:%s:%s" % (x["env"], x["mode"], x["stage"]), "manifest": t["m"], "env": x["env"]})
    with A.pool(8) as ex:
        rows = list(ex.map(job, [{"program": p} for p in programs]))
    full = [r for r in rows if all(x == x for x in r["vector"])]
    X = np.array([r["vector"] for r in full])
    sil, labs = {}, {}
    for k in range(2, 7):
        lab, C = kmeans(X, k)
        sil[k] = silhouette(X, lab)
        labs[k] = (lab, C)
    kbest = max(sil, key=sil.get)
    lab, C = labs[kbest]
    clusters = []
    for i in range(kbest):
        idx = np.flatnonzero(lab == i)
        c = C[i]
        g = lambda key: float(c[KEYS.index(key)])   # noqa: E731
        immune = bool((c < 0.1).all())
        ask = bool(g("W0D1.before_first_ask.n1") >= 0.5 and g("K2.before_first_ask.n1") >= 0.5 and g("K2.between_puts.n1") < 0.1)
        sched = bool(g("K2.between_puts.n1") >= 0.5 and g("K2.before_first_ask.n1") < 0.1 and g("K2.before_second_ask.n1") < 0.1)
        shape = "immune" if immune else "ask_time" if ask else "schedule" if sched else "UNSEEN"
        comp = {}
        for j in idx:
            comp[full[j]["lineage"]] = comp.get(full[j]["lineage"], 0) + 1
        clusters.append({"id": i, "n": int(len(idx)), "shape": shape, "centroid": {k: round(float(v), 3) for k, v in zip(KEYS, c)}, "composition": comp,
                         "mean_n_instr": float(np.mean([full[j]["n_instr"] for j in idx])), "mean_pw": float(np.mean([full[j]["persistent_words"] for j in idx]))})
    unseen = [c for c in clusters if c["shape"] == "UNSEEN" and c["n"] >= 8]
    sens_pos = [(r, k) for r in rows for k, t in r["transition"].items() if t is not None]
    dose_dep = float(np.mean([t != 1 for r, k in sens_pos for t in [r["transition"][k]]])) if sens_pos else 0.0
    order = float(np.mean([abs(r["vector"][KEYS.index("W0D1.order_ne")] - r["vector"][KEYS.index("W0D1.order_en")]) >= 0.1 for r in rows if r["vector"][KEYS.index("W0D1.order_ne")] == r["vector"][KEYS.index("W0D1.order_ne")]]))
    material = bool(unseen or dose_dep >= 0.10 or order >= 0.10)
    out = {"perturbation_id": PID, "parent": TID, "n_programs": len(rows), "n_complete": len(full), "silhouette_by_k": sil, "k": kbest, "clusters": clusters, "unseen_shapes": [c["id"] for c in unseen],
           "dose_dependence_share": dose_dep, "order_sensitive_share": order, "transition_hist": {pos: {str(t): sum(1 for r in rows if r["transition"][pos] == t) for t in (1, 2, 3, 4, None)} for pos in rows[0]["transition"]},
           "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "rows.json").write_text(json.dumps(rows, ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "response-geometry census (%d programs, %d complete): k=%d by silhouette %s; clusters %s; unseen shapes %s; dose-dependence share %.3f; order-sensitive share %.3f"
                      % (len(rows), len(full), kbest, {k: round(v, 3) for k, v in sil.items()}, [(c["id"], c["n"], c["shape"], c["composition"]) for c in clusters], out["unseen_shapes"], dose_dep, order), material,
                      detail={"clusters": clusters, "silhouette": sil})
    print("DONE material=%s k=%d (%.0f s) %s dose_dep %.3f order %.3f" % (material, kbest, time.time() - t0, [(c["n"], c["shape"]) for c in clusters], dose_dep, order))


if __name__ == "__main__":
    main()
