"""Diomedes cycle 002 — RUNNER: are the missing 0.3746 reachable with stupid relational coordinates?

Executes exactly the family frozen in CYCLE_002_PREREG_relational_coordinates.md.
Reuses cycle 001's harvest, oracle and AUC unchanged.

Admissibility rule enforced in code: no arm except ORACLE may read the candidate's
TESTED invariant. Companion invariants are a different axis and are admissible.

    python roles/Diomedes/cycle002_run.py
"""
import collections
import json
import math
import pathlib
import random

import numpy as np
from sklearn.linear_model import LogisticRegression

import cycle001_run as R
from harvest_cache import load_verified

OUT = pathlib.Path(__file__).resolve().parent / "cycle002_result.json"
SEEDS = [20260824, 20260825, 20260826, 20260827, 20260828]
N_COMPANIONS = 3
CEILING = 0.6254          # state-independent information ceiling, cycle 001
DEP_GUARD = 0.90          # single-feature functional-dependency threshold


def qrank(sorted_vals, v):
    import bisect
    return bisect.bisect_left(sorted_vals, v) / max(1, len(sorted_vals))


def build(values, relations):
    inv_cat = {}
    for (cat, inv), d in values.items():
        inv_cat.setdefault(inv, collections.Counter())[cat] = len(d)
    inv_cat = {i: c.most_common(1)[0][0] for i, c in inv_cat.items()}
    by_cat = collections.defaultdict(list)
    for (cat, inv), d in values.items():
        by_cat[cat].append((len(d), inv))
    for cat in by_cat:
        by_cat[cat].sort(reverse=True)
    sortedvals = {k: sorted(v.values()) for k, v in values.items()}
    return inv_cat, by_cat, sortedvals


def main():
    # Charter S9: the cache is used ONLY via load_verified(), which refuses unless the
    # population-identity proof (determinism + fidelity) passed. Semantically identical
    # to R.harvest(); see harvest_cache_proof.json.
    values, parents, obj_seen, obj_broke, obj_cells, obj_rels = load_verified()
    inv_cat, by_cat, sortedvals = build(values, R.RELATIONS)

    def companions(cat, tested):
        return [inv for _, inv in by_cat[cat] if inv != tested][:N_COMPANIONS]

    FEATS = []
    for i in range(N_COMPANIONS):
        FEATS += [f"delta_{i}", f"absdelta_{i}", f"parity_match_{i}",
                  f"absdiff_target_{i}", f"absdiff_le3_{i}", f"rank_delta_{i}"]
    CARRY = ["B1_break_rate", "B2_freq", "n_cells", "n_rels"]
    ALL = FEATS + CARRY

    per_seed, dep_flags = [], collections.Counter()
    for seed in SEEDS:
        rng = random.Random(seed)
        states = []
        for st in parents:
            tested = st["inv_a"] if st["side"] == "a" else st["inv_b"]
            cat = inv_cat.get(tested)
            if cat is None:
                continue
            pool = values.get((cat, tested), {})
            if len(pool) < 10:
                continue
            comp = companions(cat, tested)
            pobj = st["obj_a"] if st["side"] == "a" else st["obj_b"]
            target = st["val_b"] if st["side"] == "a" else st["val_a"]
            names = sorted(pool)
            cands = names if len(names) <= R.K else rng.sample(names, R.K)
            labels, oracle, rows = [], [], []
            for c in cands:
                v = pool[c]
                va, vb = (v, st["val_b"]) if st["side"] == "a" else (st["val_a"], v)
                broke = not R.relation_holds(st["rel"], va, vb)
                labels.append(1 if broke else 0)
                oracle.append(1.0 if broke else 0.0)
                f = {}
                for i in range(N_COMPANIONS):
                    if i < len(comp):
                        j = comp[i]
                        tbl = values[(cat, j)]
                        u, p = tbl.get(c), tbl.get(pobj)
                    else:
                        u = p = None
                    if u is None:
                        f[f"delta_{i}"] = 0.0; f[f"absdelta_{i}"] = 0.0
                        f[f"parity_match_{i}"] = 0.0; f[f"absdiff_target_{i}"] = 0.0
                        f[f"absdiff_le3_{i}"] = 0.0; f[f"rank_delta_{i}"] = 0.0
                        continue
                    p = u if p is None else p
                    f[f"delta_{i}"] = float(u - p)
                    f[f"absdelta_{i}"] = float(abs(u - p))
                    f[f"parity_match_{i}"] = float(int(u - target) % 2 == 0)
                    f[f"absdiff_target_{i}"] = float(abs(u - target))
                    f[f"absdiff_le3_{i}"] = float(abs(u - target) <= 3)
                    sv = sortedvals[(cat, j)]
                    f[f"rank_delta_{i}"] = qrank(sv, u) - qrank(sv, p)
                seen = obj_seen.get(c, 0)
                f["B1_break_rate"] = obj_broke.get(c, 0) / seen if seen else 0.0
                f["B2_freq"] = math.log1p(seen)
                f["n_cells"] = float(len(obj_cells.get(c, ())))
                f["n_rels"] = float(len(obj_rels.get(c, ())))
                rows.append(f)
            if 0 < sum(labels) < len(labels):
                states.append({"labels": labels, "oracle": oracle, "F": rows,
                               "key": (st["inv_a"], st["inv_b"]), "rel": st["rel"]})
        if len(states) < 200:
            continue

        keys = sorted({s["key"] for s in states}); rng.shuffle(keys)
        cut = max(1, int(0.6 * len(keys)))
        trk = set(keys[:cut])
        tr = [s for s in states if s["key"] in trk]
        te = [s for s in states if s["key"] not in trk] or states

        def fit(names_):
            X = np.array([[f[n] for n in names_] for s in tr for f in s["F"]])
            y = np.array([l for s in tr for l in s["labels"]])
            if len(set(y.tolist())) < 2 or len(X) < 50:
                return None
            mu, sd = X.mean(0), X.std(0) + 1e-9
            return LogisticRegression(max_iter=3000).fit((X - mu) / sd, y), mu, sd, names_

        m_rel, m_all = fit(FEATS), fit(ALL)
        arms = collections.defaultdict(list)
        for s in te:
            lab = s["labels"]
            arms["ORACLE"].append(R.auc(lab, s["oracle"]))
            arms["RANDOM"].append(R.auc(lab, [rng.random() for _ in lab]))
            arms["SHUFFLE_cheat"].append(
                R.auc(rng.sample(lab, len(lab)), [f["B1_break_rate"] for f in s["F"]]))
            arms["CYCLE1_B1"].append(R.auc(lab, [f["B1_break_rate"] for f in s["F"]]))
            for n in ALL:
                arms[f"feat::{n}"].append(R.auc(lab, [f[n] for f in s["F"]]))
            for tag, m in (("PHI_REL", m_rel), ("PHI_ALL", m_all)):
                if m:
                    clf, mu, sd, nm = m
                    X = (np.array([[f[n] for n in nm] for f in s["F"]]) - mu) / sd
                    arms[tag].append(R.auc(lab, clf.predict_proba(X)[:, 1].tolist()))

        row = {"seed": seed, "n_states_eval": len(te), "arms": {}}
        for a, vals in arms.items():
            v = np.array([x for x in vals if x is not None], dtype=float)
            if not len(v):
                continue
            se = float(v.std(ddof=1) / math.sqrt(len(v))) if len(v) > 1 else float("nan")
            row["arms"][a] = {"mean_auc": round(float(v.mean()), 4), "se": round(se, 4),
                              "lo3": round(float(v.mean() - 3 * se), 4),
                              "hi3": round(float(v.mean() + 3 * se), 4), "n": int(len(v))}
            if a.startswith("feat::") and abs(v.mean() - 0.5) + 0.5 >= DEP_GUARD:
                dep_flags[a] += 1
        per_seed.append(row)

    agg = collections.defaultdict(list)
    for r in per_seed:
        for a, d in r["arms"].items():
            agg[a].append(d["mean_auc"])
    summary = {a: round(float(np.mean(v)), 4) for a, v in agg.items()}

    def band(tag):
        los = [r["arms"][tag]["lo3"] for r in per_seed if tag in r["arms"]]
        his = [r["arms"][tag]["hi3"] for r in per_seed if tag in r["arms"]]
        if not los:
            return "NO_DATA"
        lo, hi = float(np.mean(los)), float(np.mean(his))
        if lo > DEP_GUARD:
            return "STOP-AND-UNDERSTAND"
        if lo > CEILING:
            return "ELEMENTARY-COORDINATE-DEFECT"
        if hi <= CEILING:
            return "NOT-IN-SIMPLE-RELATIONAL"
        return "AMBIGUOUS-NEEDS-POWER"

    rep = {"prereg": "CYCLE_002_PREREG_relational_coordinates.md",
           "state_independent_ceiling": CEILING, "chance": 0.5, "seeds": SEEDS,
           "split": "held-out invariant pair (T3-grade)",
           "relations": sorted(R.RELATIONS),
           "band_PHI_REL": band("PHI_REL"), "band_PHI_ALL": band("PHI_ALL"),
           "functional_dependency_flags": dict(dep_flags),
           "summary_mean_auc": dict(sorted(summary.items(), key=lambda t: -t[1])),
           "per_seed": per_seed}
    OUT.write_text(json.dumps(rep, indent=1), encoding="utf-8")
    print("band PHI_REL:", rep["band_PHI_REL"], "| band PHI_ALL:", rep["band_PHI_ALL"])
    print("dependency flags:", dict(dep_flags) or "none")
    for a, v in list(rep["summary_mean_auc"].items())[:16]:
        print(f"  {a:32s} {v:.4f}")
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
