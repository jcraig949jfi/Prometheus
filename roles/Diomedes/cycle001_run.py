"""Diomedes cycle 001 — RUNNER for the h1 counterfactual-hunt test.

Executes exactly the design frozen in CYCLE_001_PREREG_h1_counterfactual_hunt.md.
Read-only over theseus/corpus. No LLM. No network. Deterministic given the seeds.

Ground truth A*(x) is computed from an exact value table harvested from the corpus's
own payloads, using ONLY the two relations whose predicates reproduced the corpus's
own `holds` labels at 1.0000 in the pre-flight.

Hard rule enforced in code: no ranking arm except ORACLE may read the candidate's
invariant value.

    python roles/Diomedes/cycle001_run.py
"""
import collections
import glob
import gzip
import json
import math
import pathlib
import random

import numpy as np
from sklearn.linear_model import LogisticRegression

ROOT = pathlib.Path(__file__).resolve().parents[2]
CORPUS = ROOT / "theseus/corpus"
OUT = pathlib.Path(__file__).resolve().parent / "cycle001_result.json"

MAX_FILES = 12
MAX_LINES = 150_000
K = 100
SEEDS = [20260824, 20260825, 20260826, 20260827, 20260828]
RELATIONS = {"equal_mod_2", "abs_diff_le_3"}   # frozen: oracle validated at 1.0000
MIN_STATES_PER_ARM = 200


def relation_holds(rel, va, vb):
    if rel == "equal_mod_2":
        return (va - vb) % 2 == 0
    if rel == "abs_diff_le_3":
        return abs(va - vb) <= 3
    raise ValueError(rel)


def auc(labels, scores):
    """Rank-based AUC with tie handling. None if a class is absent."""
    lab = np.asarray(labels, dtype=float)
    npos, nneg = lab.sum(), (1 - lab).sum()
    if npos == 0 or nneg == 0:
        return None
    order = np.argsort(np.asarray(scores, dtype=float), kind="mergesort")
    ranks = np.empty(len(lab), dtype=float)
    s = np.asarray(scores, dtype=float)[order]
    r = np.arange(1, len(lab) + 1, dtype=float)
    i = 0
    while i < len(s):                      # average ranks within ties
        j = i
        while j + 1 < len(s) and s[j + 1] == s[i]:
            j += 1
        r[i:j + 1] = (i + 1 + j + 1) / 2.0
        i = j + 1
    ranks[order] = r
    return float((ranks[lab == 1].sum() - npos * (npos + 1) / 2) / (npos * nneg))


def harvest():
    files = sorted(glob.glob(str(CORPUS / "batch-*.jsonl.gz")))
    idx = [int(len(files) * k / MAX_FILES) for k in range(MAX_FILES)]
    values = collections.defaultdict(dict)          # (cat,inv) -> {obj: val}
    obj_seen = collections.Counter()                # obj -> appearances
    obj_broke = collections.Counter()               # obj -> times in a holds=False record
    obj_cells = collections.defaultdict(set)        # obj -> {cells}
    obj_rels = collections.defaultdict(set)         # obj -> {relations}
    parents = []
    for i in idx:
        f = files[min(i, len(files) - 1)]
        with gzip.open(f, "rt", encoding="utf-8", errors="replace") as fh:
            for j, line in enumerate(fh):
                if j >= MAX_LINES:
                    break
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                p = d.get("claim_payload") or {}
                cell = f"{d.get('generator_id')}/{d.get('claim_kind')}"
                holds = p.get("holds")
                rel = p.get("relation")
                for sfx in ("a", "b"):
                    cat, inv = p.get(f"catalog_{sfx}"), p.get(f"invariant_{sfx}")
                    obj, val = p.get(f"object_{sfx}"), p.get(f"value_{sfx}")
                    if obj is None:
                        continue
                    obj_seen[obj] += 1
                    obj_cells[obj].add(cell)
                    if rel:
                        obj_rels[obj].add(rel)
                    if holds is False:
                        obj_broke[obj] += 1
                    if cat and inv and isinstance(val, (int, float)):
                        values[(cat, inv)][obj] = val
                if d.get("generator_id") == "h1" and p.get("hunter_success") \
                        and p.get("hunter_varied_side") in ("a", "b") \
                        and p.get("parent_relation") in RELATIONS \
                        and isinstance(p.get("parent_value_a"), (int, float)) \
                        and isinstance(p.get("parent_value_b"), (int, float)):
                    parents.append({
                        "rel": p["parent_relation"], "side": p["hunter_varied_side"],
                        "inv_a": p.get("invariant_a"), "inv_b": p.get("invariant_b"),
                        "obj_a": p.get("parent_object_a"), "obj_b": p.get("parent_object_b"),
                        "val_a": p["parent_value_a"], "val_b": p["parent_value_b"],
                    })
    return values, parents, obj_seen, obj_broke, obj_cells, obj_rels


def main():
    values, parents, obj_seen, obj_broke, obj_cells, obj_rels = harvest()

    inv_cat = {}
    for (cat, inv), d in values.items():
        inv_cat.setdefault(inv, collections.Counter())[cat] = len(d)
    inv_cat = {i: c.most_common(1)[0][0] for i, c in inv_cat.items()}
    cat_order = {cat: {o: n for n, o in enumerate(sorted({o for (c, _), d in values.items()
                                                          if c == cat for o in d}))}
                 for cat in {c for (c, _) in values}}

    def feats(cand, st, pool_rank):
        seen = obj_seen.get(cand, 0)
        br = obj_broke.get(cand, 0) / seen if seen else 0.0
        pobj = st["obj_a"] if st["side"] == "a" else st["obj_b"]
        cat = inv_cat[st["inv_a"] if st["side"] == "a" else st["inv_b"]]
        adj = abs(cat_order[cat].get(cand, 0) - cat_order[cat].get(pobj, 0))
        return {
            "B1_break_rate": br,
            "B2_freq": math.log1p(seen),
            "B3_adjacency": -adj,
            "n_cells": len(obj_cells.get(cand, ())),
            "n_rels": len(obj_rels.get(cand, ())),
        }

    per_seed = []
    for seed in SEEDS:
        rng = random.Random(seed)
        states = []
        for st in parents:
            inv = st["inv_a"] if st["side"] == "a" else st["inv_b"]
            cat = inv_cat.get(inv)
            if cat is None:
                continue
            pool_src = values.get((cat, inv), {})
            if len(pool_src) < 10:
                continue
            names = sorted(pool_src)
            cands = names if len(names) <= K else rng.sample(names, K)
            labels, oracle, F = [], [], []
            for n_, c in enumerate(cands):
                v = pool_src[c]
                va, vb = (v, st["val_b"]) if st["side"] == "a" else (st["val_a"], v)
                broke = not relation_holds(st["rel"], va, vb)
                labels.append(1 if broke else 0)
                oracle.append(1.0 if broke else 0.0)
                F.append(feats(c, st, n_))
            if 0 < sum(labels) < len(labels):
                states.append({"st": st, "labels": labels, "oracle": oracle, "F": F,
                               "key": (st["inv_a"], st["inv_b"])})
        if len(states) < MIN_STATES_PER_ARM:
            continue

        keys = sorted({s["key"] for s in states})
        rng.shuffle(keys)
        cut = max(1, int(0.6 * len(keys)))
        train_k, test_k = set(keys[:cut]), set(keys[cut:])
        tr = [s for s in states if s["key"] in train_k]
        te = [s for s in states if s["key"] in test_k] or states

        names = ["B1_break_rate", "B2_freq", "B3_adjacency", "n_cells", "n_rels"]
        Xtr = np.array([[f[n] for n in names] for s in tr for f in s["F"]])
        ytr = np.array([l for s in tr for l in s["labels"]])
        zfull = None
        if len(set(ytr.tolist())) == 2 and len(Xtr) > 50:
            mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-9
            clf = LogisticRegression(max_iter=2000).fit((Xtr - mu) / sd, ytr)
            zfull = (clf, mu, sd)

        arms = collections.defaultdict(list)
        base_rates = []
        for s in te:
            lab = s["labels"]
            base_rates.append(sum(lab) / len(lab))
            arms["ORACLE"].append(auc(lab, s["oracle"]))
            arms["RANDOM"].append(auc(lab, [rng.random() for _ in lab]))
            arms["SHUFFLE_cheat"].append(
                auc(rng.sample(lab, len(lab)), [f["B1_break_rate"] for f in s["F"]]))
            for n in names:
                arms[n].append(auc(lab, [f[n] for f in s["F"]]))
            arms["Z_parent"].append(auc(lab, [1.0] * len(lab)))   # constant by construction
            if zfull:
                clf, mu, sd = zfull
                X = (np.array([[f[n] for n in names] for f in s["F"]]) - mu) / sd
                arms["Z_full"].append(auc(lab, clf.predict_proba(X)[:, 1].tolist()))

        row = {"seed": seed, "n_states_eval": len(te), "n_states_total": len(states),
               "mean_base_rate": round(float(np.mean(base_rates)), 4), "arms": {}}
        for a, vals in arms.items():
            v = np.array([x for x in vals if x is not None], dtype=float)
            if len(v) == 0:
                continue
            se = float(v.std(ddof=1) / math.sqrt(len(v))) if len(v) > 1 else float("nan")
            row["arms"][a] = {"mean_auc": round(float(v.mean()), 4),
                              "se": round(se, 4), "n": int(len(v)),
                              "gate_mean_minus_3se": round(float(v.mean() - 3 * se), 4)}
        per_seed.append(row)

    agg = collections.defaultdict(list)
    for r in per_seed:
        for a, d in r["arms"].items():
            agg[a].append(d["mean_auc"])
    summary = {a: {"mean_auc_across_seeds": round(float(np.mean(v)), 4),
                   "min": round(float(np.min(v)), 4), "max": round(float(np.max(v)), 4),
                   "n_seeds": len(v)}
               for a, v in sorted(agg.items())}

    rep = {"prereg": "CYCLE_001_PREREG_h1_counterfactual_hunt.md",
           "relations": sorted(RELATIONS), "K": K, "seeds": SEEDS,
           "scope": f"{MAX_FILES} stratified files, <={MAX_LINES} lines each",
           "chance_auc": 0.5, "split": "held-out INVARIANT PAIR (T3-grade)",
           "per_seed": per_seed, "summary": summary}
    OUT.write_text(json.dumps(rep, indent=1), encoding="utf-8")
    print(json.dumps(summary, indent=1))
    if per_seed:
        print("\nseed 1 detail:", json.dumps(per_seed[0], indent=1)[:1200])
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()
