"""CRUCIBLE-C runner. Executes exactly PREREG_C_B.md section C. Imports the frozen Diomedes builders; fits only
sklearn logistic regressions (same family as cycle 003). Usage: python -m alien_circuitry.nursery.crucibles.crucible_c
"""
from __future__ import annotations
import collections, json, os, random, sys, time
import numpy as np
from sklearn.linear_model import LogisticRegression

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DIO = os.path.join(ROOT, "roles", "Diomedes")
sys.path.insert(0, DIO)
import cycle001_run as R        # noqa: E402  (frozen Diomedes code, imported not copied)
import cycle002_run as C2       # noqa: E402
import cycle003_run as C3       # noqa: E402  (holds the frozen C2_states builder)
from harvest_cache import load_verified  # noqa: E402

SEEDS = C2.SEEDS; MIN_PAIR_STATES = 200; N_PERM = 200; OUT = os.path.join(ROOT, "alien_circuitry", "results", "ac01d", "nursery", "crucible_c_result.json")


def X_of(states, feats):
    return np.concatenate([s["X"] for s in states]).astype(np.float64), np.array([l for s in states for l in s["labels"]])


class _Std:
    """Standardised logistic regression (same model family and capacity as cycle 003; scaling only aids lbfgs convergence)."""
    def __init__(self, mu, sd, clf): self.mu, self.sd, self.clf = mu, sd, clf
    def predict_proba(self, X): return self.clf.predict_proba((X - self.mu) / self.sd)


def fit(states, feats, seed):
    X, y = X_of(states, feats)
    if len(set(y.tolist())) < 2: return None
    mu = X.mean(0); sd = X.std(0) + 1e-9
    return _Std(mu, sd, LogisticRegression(max_iter=2000, random_state=int(seed) % (2**31)).fit((X - mu) / sd, y))


def cost_to_first_break(state, scores, rng):
    order = np.argsort(-np.asarray(scores) + 1e-9 * np.array([rng.random() for _ in scores]))  # seeded tie-break
    labels = state["labels"]
    for i, j in enumerate(order):
        if labels[j] == 1: return i + 1
    return len(labels)


def eval_costs(states, scorer, rng):
    return [cost_to_first_break(s, scorer(s), rng) for s in states]


def run():
    t0 = time.perf_counter()
    values, parents, obj_seen, obj_broke, obj_cells, obj_rels = load_verified()
    inv_cat, by_cat, sortedvals = C2.build(values, R.RELATIONS)
    CARRY = ["B1_break_rate", "B2_freq", "n_cells", "n_rels"]
    # feature list exactly as cycle 002/003 (relational coordinates only)
    FEATS = []
    for i in range(C2.N_COMPANIONS):
        FEATS += [f"delta_{i}", f"absdelta_{i}", f"parity_match_{i}", f"absdiff_target_{i}", f"absdiff_le3_{i}", f"rank_delta_{i}"]
    CKPT = OUT.replace(".json", "_checkpoint.json")
    per_seed = json.load(open(CKPT)) if os.path.exists(CKPT) else []   # per-seed checkpoint: a host memory kill loses at most one seed
    done = {r["seed"] for r in per_seed}
    only = os.environ.get("CRUCIBLE_C_SEED")
    for seed in SEEDS:
        if seed in done: continue
        if only and seed != int(only): continue
        rng = random.Random(seed)
        states = C3.C2_states(values, parents, obj_seen, obj_broke, obj_cells, obj_rels, inv_cat, by_cat, sortedvals, rng, FEATS, CARRY)
        # memory: the dict-of-dicts state list is ~8.6 GB resident on this host; compact each state to float32 arrays (same values)
        states = [{"labels": s["labels"], "oracle": s["oracle"], "key": s["key"], "rel": s["rel"],
                   "X": np.array([[f[k] for k in FEATS] for f in s["F"]], dtype=np.float32), "B1": np.array([f["B1_break_rate"] for f in s["F"]], dtype=np.float32)} for s in states]
        import gc; gc.collect()
        by_pair = collections.defaultdict(list)
        for s in states: by_pair[s["key"]].append(s)
        qual = {k: v for k, v in by_pair.items() if len(v) >= MIN_PAIR_STATES}
        tr_all, te_all, tr_by, te_by = [], [], {}, {}
        for k, ss in qual.items():
            idx = list(range(len(ss))); rng.shuffle(idx); c = max(1, int(0.6 * len(idx)))
            tr_by[k] = [ss[i] for i in idx[:c]]; te_by[k] = [ss[i] for i in idx[c:]] or tr_by[k]
            tr_all += tr_by[k]; te_all += te_by[k]
        pooled = fit(tr_all, FEATS, seed)
        canon = {k: fit(v, FEATS, seed) for k, v in tr_by.items()}
        med_n = int(np.median([len(v) for v in tr_by.values()]))
        sub = rng.sample(tr_all, min(med_n, len(tr_all))); matched = fit(sub, FEATS, seed)
        def sc_model(m):
            return lambda s: (m.predict_proba(s["X"].astype(np.float64))[:, 1] if m is not None else np.zeros(len(s["labels"])))
        def sc_canon(s):
            m = canon.get(s["key"]); return sc_model(m)(s) if m is not None else sc_model(pooled)(s)
        # random-class control and permutation null: reassign held+train states to pseudo-classes of the same sizes
        def pseudo_costs(perm_seed):
            prng = random.Random(perm_seed); allst = tr_all + te_all; prng.shuffle(allst)
            sizes = [(k, len(tr_by[k]), len(te_by[k])) for k in tr_by]; pos = 0; costs = []
            for k, ntr, nte in sizes:
                ptr = allst[pos:pos + ntr]; pte = allst[pos + ntr:pos + ntr + nte]; pos += ntr + nte
                m = fit(ptr, FEATS, perm_seed); costs += eval_costs(pte, sc_model(m) if m is not None else sc_model(pooled), random.Random(perm_seed))
            return float(np.mean(costs))
        c_pooled = eval_costs(te_all, sc_model(pooled), random.Random(seed))
        c_canon = eval_costs(te_all, sc_canon, random.Random(seed))
        c_matched = eval_costs(te_all, sc_model(matched), random.Random(seed))
        c_oracle = eval_costs(te_all, lambda s: s["oracle"], random.Random(seed))
        c_random = eval_costs(te_all, lambda s: [rng.random() for _ in s["labels"]], random.Random(seed))
        c_b1 = eval_costs(te_all, lambda s: s["B1"], random.Random(seed))
        NCK = OUT.replace(".json", f"_null_seed{seed}.json")   # permutation-level checkpoint (host kills are frequent)
        null = json.load(open(NCK)) if os.path.exists(NCK) else []
        for p_ in range(len(null), N_PERM):
            null.append(pseudo_costs(seed * 1000 + p_))
            if p_ % 10 == 9: json.dump(null, open(NCK, "w"))
        json.dump(null, open(NCK, "w"))
        obs_diff = float(np.mean(c_pooled) - np.mean(c_canon)); null_diff = [float(np.mean(c_pooled) - n) for n in null]
        # AUC ties to cycle 003
        def auc(states, scorer):
            v = [R.auc(s["labels"], list(map(float, scorer(s)))) for s in states]; v = [x for x in v if x is not None]; return float(np.mean(v))
        # secondary: pair x relation classes
        tr_pr = collections.defaultdict(list)
        for s in tr_all: tr_pr[(s["key"], s["rel"])].append(s)
        canon_pr = {k: fit(v, FEATS, seed) for k, v in tr_pr.items()}
        def sc_pr(s):
            m = canon_pr.get((s["key"], s["rel"])); return sc_model(m)(s) if m is not None else sc_canon(s)
        c_pr = eval_costs(te_all, sc_pr, random.Random(seed))
        boot = np.random.default_rng(seed); diffs = np.array(c_pooled) - np.array(c_canon); se = float(np.std([boot.choice(diffs, len(diffs)).mean() for _ in range(500)]))
        per_seed.append({"seed": seed, "n_states": len(states), "n_qualifying_pairs": len(qual), "n_train": len(tr_all), "n_held": len(te_all), "median_train_per_pair": med_n,
                         "cost": {"oracle": float(np.mean(c_oracle)), "random": float(np.mean(c_random)), "B1": float(np.mean(c_b1)), "pooled": float(np.mean(c_pooled)),
                                  "matched_n_pooled": float(np.mean(c_matched)), "canonical_pair": float(np.mean(c_canon)), "canonical_pair_x_relation_SECONDARY": float(np.mean(c_pr))},
                         "auc": {"pooled": auc(te_all, sc_model(pooled)), "canonical_pair": auc(te_all, sc_canon), "matched_n_pooled": auc(te_all, sc_model(matched)), "B1": auc(te_all, lambda s: s["B1"].tolist())},
                         "observed_cost_reduction_canonical_vs_pooled": obs_diff, "bootstrap_se_of_reduction": se,
                         "null": {"n_perm": N_PERM, "mean": float(np.mean(null_diff)), "p95": float(np.percentile(null_diff, 95)), "p99": float(np.percentile(null_diff, 99)), "max": float(np.max(null_diff)),
                                  "rank_of_observed": int(sum(1 for d in null_diff if d >= obs_diff)), "p_value": (1 + sum(1 for d in null_diff if d >= obs_diff)) / (N_PERM + 1)},
                         "HC_canonical": (1 - (np.mean(c_canon) - 1) / max(1e-9, np.mean(c_pooled) - 1)), "HC_matched_n": (1 - (np.mean(c_matched) - 1) / max(1e-9, np.mean(c_pooled) - 1))})
        print(json.dumps({k: per_seed[-1][k] for k in ("seed", "n_qualifying_pairs", "n_held", "cost", "observed_cost_reduction_canonical_vs_pooled", "bootstrap_se_of_reduction", "HC_canonical", "HC_matched_n")}, default=float), flush=True)
        print("   null p95", round(per_seed[-1]["null"]["p95"], 4), "p", per_seed[-1]["null"]["p_value"], flush=True)
        os.makedirs(os.path.dirname(OUT), exist_ok=True); json.dump(per_seed, open(CKPT, "w"), default=float)
    if len(per_seed) < len(SEEDS):
        print(json.dumps({"seeds_done": sorted(r["seed"] for r in per_seed), "note": "partial; rerun for remaining seeds"})); return None
    agg = lambda path: float(np.mean([eval("r" + path, {"r": r}) for r in per_seed]))
    res = {"prereg": "alien_circuitry/nursery/crucibles/PREREG_C_B.md @ d3b9533", "governing": "alien_circuitry/nursery/CRUCIBLES.md @ 86a429e", "seeds": SEEDS, "per_seed": per_seed,
           "aggregate": {"cost_pooled": agg("['cost']['pooled']"), "cost_canonical": agg("['cost']['canonical_pair']"), "cost_matched_n": agg("['cost']['matched_n_pooled']"), "cost_oracle": agg("['cost']['oracle']"),
                         "cost_random": agg("['cost']['random']"), "cost_B1": agg("['cost']['B1']"), "cost_pair_x_relation_SECONDARY": agg("['cost']['canonical_pair_x_relation_SECONDARY']"),
                         "reduction_observed": agg("['observed_cost_reduction_canonical_vs_pooled']"), "reduction_null_p95": agg("['null']['p95']"), "reduction_null_max": agg("['null']['max']"),
                         "HC_canonical": agg("['HC_canonical']"), "HC_matched_n": agg("['HC_matched_n']"), "auc_pooled": agg("['auc']['pooled']"), "auc_canonical": agg("['auc']['canonical_pair']"),
                         "all_seeds_p_below_0.05": all(r["null"]["p_value"] < 0.05 for r in per_seed)},
           "decision_time_observability": "pair key (inv_a, inv_b) and relation are attributes of the state before any label; OBSERVABLE by construction",
           "seconds": round(time.perf_counter() - t0, 1)}
    a = res["aggregate"]; se_mean = float(np.mean([r["bootstrap_se_of_reduction"] for r in per_seed]))
    matched_gap = a["cost_matched_n"] - a["cost_canonical"]
    if not a["all_seeds_p_below_0.05"] or a["reduction_observed"] <= a["reduction_null_p95"]: verdict = "C-KILL (inside random-class null)"
    elif matched_gap <= se_mean: verdict = "C-KILL (matched-N pooled equals canonical: sample size, not structure)"
    elif a["HC_canonical"] >= 0.10: verdict = "C-PASS"
    else: verdict = "C-WEAK"
    res["verdict"] = verdict; res["verdict_inputs"] = {"matched_gap": matched_gap, "se_mean": se_mean}
    os.makedirs(os.path.dirname(OUT), exist_ok=True); json.dump(res, open(OUT, "w"), indent=1, default=float)
    print(json.dumps({"aggregate": a, "verdict": verdict, "verdict_inputs": res["verdict_inputs"], "seconds": res["seconds"]}, indent=1, default=float)); return res


if __name__ == "__main__":
    run()
