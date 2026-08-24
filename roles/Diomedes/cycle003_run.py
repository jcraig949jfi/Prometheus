"""Diomedes cycle 003 — RUNNER: split discriminator (was cycle 002's KILL transfer or coordinates?).

Executes exactly the design frozen in CYCLE_003_PREREG_split_discriminator.md.
Reuses the identity-proved harvest cache and cycle 002's frozen feature builder.
Only the SPLIT changes.

    python roles/Diomedes/cycle003_run.py
"""
import collections
import json
import math
import pathlib
import random

import numpy as np
from sklearn.linear_model import LogisticRegression

import cycle001_run as R
import cycle002_run as C2
from harvest_cache import load_verified

OUT = pathlib.Path(__file__).resolve().parent / "cycle003_result.json"
SEEDS = C2.SEEDS
MIN_PAIR_STATES = 200      # frozen in prereg S5.3


def fit_eval(tr, te, names, rng):
    X = np.array([[f[n] for n in names] for s in tr for f in s["F"]])
    y = np.array([l for s in tr for l in s["labels"]])
    if len(set(y.tolist())) < 2 or len(X) < 50:
        return None, None
    mu, sd = X.mean(0), X.std(0) + 1e-9
    clf = LogisticRegression(max_iter=3000).fit((X - mu) / sd, y)
    aucs = []
    for s in te:
        Z = (np.array([[f[n] for n in names] for f in s["F"]]) - mu) / sd
        a = R.auc(s["labels"], clf.predict_proba(Z)[:, 1].tolist())
        if a is not None:
            aucs.append(a)
    return aucs, clf.coef_[0].copy()


def stat(v):
    v = np.asarray([x for x in v if x is not None], dtype=float)
    if not len(v):
        return None
    se = float(v.std(ddof=1) / math.sqrt(len(v))) if len(v) > 1 else 0.0
    return {"mean_auc": round(float(v.mean()), 4), "se": round(se, 4),
            "lo3": round(float(v.mean() - 3 * se), 4),
            "hi3": round(float(v.mean() + 3 * se), 4), "n": int(len(v))}


def main():
    bundle = load_verified()
    values, parents, obj_seen, obj_broke, obj_cells, obj_rels = bundle
    inv_cat, by_cat, sortedvals = C2.build(values, R.RELATIONS)
    FEATS, CARRY = [], ["B1_break_rate", "B2_freq", "n_cells", "n_rels"]
    for i in range(C2.N_COMPANIONS):
        FEATS += [f"delta_{i}", f"absdelta_{i}", f"parity_match_{i}",
                  f"absdiff_target_{i}", f"absdiff_le3_{i}", f"rank_delta_{i}"]

    per_seed = []
    coef_by_pair_all = {}
    for seed in SEEDS:
        rng = random.Random(seed)
        states = C2_states(values, parents, obj_seen, obj_broke, obj_cells, obj_rels,
                           inv_cat, by_cat, sortedvals, rng, FEATS, CARRY)
        if len(states) < 500:
            continue
        by_pair = collections.defaultdict(list)
        for s in states:
            by_pair[s["key"]].append(s)

        # --- T3_ACROSS : held-out invariant pairs (replicates cycle 002) ---
        keys = sorted(by_pair); rng.shuffle(keys)
        cut = max(1, int(0.6 * len(keys)))
        trk = set(keys[:cut])
        tr3 = [s for s in states if s["key"] in trk]
        te3 = [s for s in states if s["key"] not in trk] or states
        a_t3, _ = fit_eval(tr3, te3, FEATS, rng)

        # --- T2_WITHIN : held-out states inside each invariant pair ---
        a_t2, a_t0, a_b1t2, coefs, train_ns = [], [], [], {}, []
        for k, ss in by_pair.items():
            if len(ss) < MIN_PAIR_STATES:
                continue
            idx = list(range(len(ss))); rng.shuffle(idx)
            c = max(1, int(0.6 * len(idx)))
            tr = [ss[i] for i in idx[:c]]
            te = [ss[i] for i in idx[c:]] or tr
            train_ns.append(len(tr))
            r2, cf = fit_eval(tr, te, FEATS, rng)
            if r2:
                a_t2 += r2
                coefs[str(k)] = cf.tolist()
            r0, _ = fit_eval(tr, tr, FEATS, rng)
            if r0:
                a_t0 += r0
            # mandatory control: break-rate alone, same within-pair split
            for s in te:
                v = R.auc(s["labels"], [f["B1_break_rate"] for f in s["F"]])
                if v is not None:
                    a_b1t2.append(v)

        # --- standing controls on the T3 eval set ---
        orc, shf, rnd, b1_t3 = [], [], [], []
        for s in te3:
            lab = s["labels"]
            orc.append(R.auc(lab, s["oracle"]))
            rnd.append(R.auc(lab, [rng.random() for _ in lab]))
            shf.append(R.auc(rng.sample(lab, len(lab)), [f["B1_break_rate"] for f in s["F"]]))
            b1_t3.append(R.auc(lab, [f["B1_break_rate"] for f in s["F"]]))

        coef_by_pair_all[seed] = coefs
        per_seed.append({"seed": seed, "n_states": len(states),
                         "n_pairs_used": len(coefs),
                         "median_train_states_per_pair": int(np.median(train_ns)) if train_ns else 0,
                         "arms": {"T3_ACROSS": stat(a_t3), "T2_WITHIN": stat(a_t2),
                                  "T0_INSAMPLE": stat(a_t0), "B1_T2": stat(a_b1t2),
                                  "B1_T3": stat(b1_t3), "ORACLE": stat(orc),
                                  "SHUFFLE_cheat": stat(shf), "RANDOM": stat(rnd)}})

    def agg(tag):
        v = [r["arms"][tag]["mean_auc"] for r in per_seed if r["arms"].get(tag)]
        return round(float(np.mean(v)), 4) if v else None

    t2, t3 = agg("T2_WITHIN"), agg("T3_ACROSS")
    b1t2, b1t3 = agg("B1_T2"), agg("B1_T3")
    delta = round((t2 - t3), 4) if (t2 and t3) else None
    b1_rise = round((b1t2 - b1t3), 4) if (b1t2 and b1t3) else None

    # --- mechanism test: per-pair coefficient agreement ---
    cos = []
    for seed, coefs in coef_by_pair_all.items():
        ks = sorted(coefs)
        for i in range(len(ks)):
            for j in range(i + 1, len(ks)):
                a, b = np.array(coefs[ks[i]]), np.array(coefs[ks[j]])
                na, nb = np.linalg.norm(a), np.linalg.norm(b)
                if na > 1e-9 and nb > 1e-9:
                    cos.append(float(a @ b / (na * nb)))
    cos_mean = round(float(np.mean(cos)), 4) if cos else None

    sign_agree = {}
    if coef_by_pair_all:
        allc = [np.array(v) for c in coef_by_pair_all.values() for v in c.values()]
        if allc:
            M = np.vstack(allc)
            modal = np.sign(np.median(M, axis=0))
            for n, col, m in zip(FEATS, M.T, modal):
                sign_agree[n] = round(float(np.mean(np.sign(col) == m)), 3)

    lo_t2 = float(np.mean([r["arms"]["T2_WITHIN"]["lo3"] for r in per_seed if r["arms"].get("T2_WITHIN")]))
    hi_t3 = float(np.mean([r["arms"]["T3_ACROSS"]["hi3"] for r in per_seed if r["arms"].get("T3_ACROSS")]))
    sep = lo_t2 > hi_t3

    if delta is None:
        band = "NO_DATA"
    elif delta > 0.03 and sep and (b1_rise is not None and b1_rise < delta / 2):
        band = "TRANSFER-FAILURE-CONFIRMED"
    elif delta > 0.03 and (b1_rise is not None and b1_rise >= delta / 2):
        band = "OBJECT-MEMORIZATION"
    elif delta <= 0.01 or not sep:
        band = "COORDINATES-INADEQUATE-CONFIRMED"
    else:
        band = "AMBIGUOUS-NEEDS-POWER"

    rep = {"prereg": "CYCLE_003_PREREG_split_discriminator.md",
           "band": band, "delta_T2_minus_T3": delta,
           "b1_control_rise": b1_rise, "t2_lo3_gt_t3_hi3": sep,
           "mean_pairwise_coef_cosine": cos_mean, "n_cosine_pairs": len(cos),
           "sign_agreement_by_feature": sign_agree,
           "aggregate": {"T2_WITHIN": t2, "T3_ACROSS": t3, "T0_INSAMPLE": agg("T0_INSAMPLE"),
                         "B1_T2": b1t2, "B1_T3": b1t3, "ORACLE": agg("ORACLE"),
                         "SHUFFLE_cheat": agg("SHUFFLE_cheat"), "RANDOM": agg("RANDOM")},
           "per_seed": per_seed}
    OUT.write_text(json.dumps(rep, indent=1), encoding="utf-8")
    print("BAND:", band)
    print(json.dumps({k: rep[k] for k in
                      ("delta_T2_minus_T3", "b1_control_rise", "t2_lo3_gt_t3_hi3",
                       "mean_pairwise_coef_cosine", "aggregate")}, indent=1))
    print(f"-> {OUT}")


def C2_states(values, parents, obj_seen, obj_broke, obj_cells, obj_rels,
              inv_cat, by_cat, sortedvals, rng, FEATS, CARRY):
    """Frozen cycle-002 state/feature construction, unchanged."""
    out = []
    for st in parents:
        tested = st["inv_a"] if st["side"] == "a" else st["inv_b"]
        cat = inv_cat.get(tested)
        if cat is None:
            continue
        pool = values.get((cat, tested), {})
        if len(pool) < 10:
            continue
        comp = [inv for _, inv in by_cat[cat] if inv != tested][:C2.N_COMPANIONS]
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
            for i in range(C2.N_COMPANIONS):
                u = p = None
                if i < len(comp):
                    tbl = values[(cat, comp[i])]
                    u, p = tbl.get(c), tbl.get(pobj)
                if u is None:
                    for nm in (f"delta_{i}", f"absdelta_{i}", f"parity_match_{i}",
                               f"absdiff_target_{i}", f"absdiff_le3_{i}", f"rank_delta_{i}"):
                        f[nm] = 0.0
                    continue
                p = u if p is None else p
                f[f"delta_{i}"] = float(u - p)
                f[f"absdelta_{i}"] = float(abs(u - p))
                f[f"parity_match_{i}"] = float(int(u - target) % 2 == 0)
                f[f"absdiff_target_{i}"] = float(abs(u - target))
                f[f"absdiff_le3_{i}"] = float(abs(u - target) <= 3)
                sv = sortedvals[(cat, comp[i])]
                f[f"rank_delta_{i}"] = C2.qrank(sv, u) - C2.qrank(sv, p)
            seen = obj_seen.get(c, 0)
            f["B1_break_rate"] = obj_broke.get(c, 0) / seen if seen else 0.0
            f["B2_freq"] = math.log1p(seen)
            f["n_cells"] = float(len(obj_cells.get(c, ())))
            f["n_rels"] = float(len(obj_rels.get(c, ())))
            rows.append(f)
        if 0 < sum(labels) < len(labels):
            out.append({"labels": labels, "oracle": oracle, "F": rows,
                        "key": (st["inv_a"], st["inv_b"]), "rel": st["rel"]})
    return out


if __name__ == "__main__":
    main()
