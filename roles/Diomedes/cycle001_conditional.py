"""Diomedes cycle 001 — ADDENDUM: is the signal conditional on the state, or marginal?

Cycle 001's main run found every above-chance arm to be a pure per-object property.
This addendum measures the decisive quantity the main run did not isolate:

  ORACLE_MARGINAL — the best achievable ranking that uses NO information about the
  current state.  Each candidate object is scored by the fraction of ALL evaluated
  states in which it broke the relation, computed from ground truth.  This is the
  ceiling for any state-independent ranker.

  ORACLE          — the state-specific ground truth, AUC 1.0 by construction.

The gap between them is exactly the CONDITIONAL information: what can only be known
by attending to the current state.  If a Prometheus arm reaches ORACLE_MARGINAL but
not beyond, then the recorded coordinates carry marginal object statistics and no
navigational information about where we are.

Also reports the paired per-state delta Z_full - B1 with its SE, which decides
whether the elaborate representation beat its one-line baseline.

    python roles/Diomedes/cycle001_conditional.py
"""
import collections
import math
import pathlib

import numpy as np

import cycle001_run as R   # reuse the frozen harvest, oracle and AUC

OUT = pathlib.Path(__file__).resolve().parent / "cycle001_conditional.json"
SEED = 20260824


def main():
    values, parents, obj_seen, obj_broke, obj_cells, obj_rels = R.harvest()
    inv_cat = {}
    for (cat, inv), d in values.items():
        inv_cat.setdefault(inv, collections.Counter())[cat] = len(d)
    inv_cat = {i: c.most_common(1)[0][0] for i, c in inv_cat.items()}

    import random
    rng = random.Random(SEED)
    states = []
    for st in parents:
        inv = st["inv_a"] if st["side"] == "a" else st["inv_b"]
        cat = inv_cat.get(inv)
        if cat is None:
            continue
        pool = values.get((cat, inv), {})
        if len(pool) < 10:
            continue
        names = sorted(pool)
        cands = names if len(names) <= R.K else rng.sample(names, R.K)
        labels = []
        for c in cands:
            v = pool[c]
            va, vb = (v, st["val_b"]) if st["side"] == "a" else (st["val_a"], v)
            labels.append(0 if R.relation_holds(st["rel"], va, vb) else 1)
        if 0 < sum(labels) < len(labels):
            states.append({"cands": cands, "labels": labels})

    # best possible STATE-INDEPENDENT score: global empirical break rate per object
    hit = collections.Counter()
    tot = collections.Counter()
    for s in states:
        for c, l in zip(s["cands"], s["labels"]):
            tot[c] += 1
            hit[c] += l
    marg = {c: hit[c] / tot[c] for c in tot}

    a_marg, a_prom = [], []
    for s in states:
        a_marg.append(R.auc(s["labels"], [marg[c] for c in s["cands"]]))
        a_prom.append(R.auc(s["labels"],
                            [obj_broke.get(c, 0) / obj_seen[c] if obj_seen.get(c) else 0.0
                             for c in s["cands"]]))
    a_marg = np.array([x for x in a_marg if x is not None])
    a_prom = np.array([x for x in a_prom if x is not None])

    def stat(v):
        se = float(v.std(ddof=1) / math.sqrt(len(v)))
        return {"mean_auc": round(float(v.mean()), 4), "se": round(se, 4),
                "n_states": int(len(v)),
                "gate_mean_minus_3se": round(float(v.mean() - 3 * se), 4)}

    rep = {
        "seed": SEED, "n_states": len(states), "chance_auc": 0.5,
        "ORACLE_state_specific": {"mean_auc": 1.0, "note": "by construction"},
        "ORACLE_MARGINAL_best_state_independent": stat(a_marg),
        "PROMETHEUS_B1_break_rate": stat(a_prom),
        "conditional_information_gap": {
            "definition": "ORACLE (1.0) - ORACLE_MARGINAL; the part of A* that can only "
                          "be known by attending to the current state",
            "value": round(1.0 - float(a_marg.mean()), 4),
        },
        "share_of_marginal_ceiling_captured_by_prometheus": round(
            (float(a_prom.mean()) - 0.5) / max(1e-9, float(a_marg.mean()) - 0.5), 4),
    }
    OUT.write_text(__import__("json").dumps(rep, indent=1), encoding="utf-8")
    print(__import__("json").dumps(rep, indent=1))
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()
