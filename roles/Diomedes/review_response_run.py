"""Diomedes — review-response audits A1/A2/A3, per REVIEW_RESPONSE_PREREG_2026-08-25.md.

Executes exactly the three audits frozen in that pre-registration, on the identity-proved
cycle-004 population (digest 1b4abb1a) with the frozen 18-feature family and the same
deterministic per-cell splits used by cycle005_armB_run.py.

  A1 PROXY RECONSTRUCTION - can the candidate's COMPANION invariants predict its withheld
     TESTED invariant well enough that applying the EXACT relation predicate to the
     prediction reproduces local ranking performance? Tests Interpretation 2.
     The tested invariant is used here as a DIAGNOSTIC of where predictive information came
     from, not as a ranking arm. It is not a leak; it is the audit.

  A2 LEAVE-ONE-CELL-OUT, RELATION HELD FIXED - train on all OTHER invariant pairs carrying
     the same relation, pooled, with NO cell-identity feature, evaluate on an unseen pair.
     Tests Interpretation 4 in the reviewer's stronger form (pooled-with-cell-ID is not
     decisive because a flexible model with indicators can contain 24 local models).

  A3 CLUSTER BOOTSTRAP OVER CELLS within stratum C, replacing the seed-level SE, which was
     computed across 5 re-splits of the same 24 cells and therefore measured split noise.

    python roles/Diomedes/review_response_run.py
"""
import collections
import gc
import json
import math
import pathlib
import random

import numpy as np
from sklearn.linear_model import LogisticRegression, Ridge

import cycle001_run as R
import cycle002_run as C2
import cycle005_armB_run as AB
from harvest_cache import load_verified, digest as pop_digest

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "review_response_result.json"
N_BOOT = 2000
BOOT_SEED = 20260825


def spearman(a, b):
    if len(a) < 3:
        return None
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    ra -= ra.mean(); rb -= rb.mean()
    d = float(np.sqrt((ra ** 2).sum() * (rb ** 2).sum()))
    return float((ra * rb).sum() / d) if d > 1e-12 else None


def pack_proxy(states):
    """The candidate's RAW companion invariant values, and the candidate's TESTED value.

    v1 of this audit used delta_i = w(candidate) - w(parent) as the proxy feature. That is
    parent-contaminated: the parent varies state-to-state inside a cell, so it is NOT the
    map w(a) -> v_tested(a) the reviewer specified, and the contamination weakens the proxy.
    A weakened proxy pushes A1 DOWN, which is the direction that flatters this thread, so it
    is not an acceptable way to obtain a favourable null. Fixed to use w(a) directly.
    """
    W, M, V, y, seg = [], [], [], [], []
    for s in states:
        W.append(np.asarray(s["w_cand"], dtype=float))     # raw companion values of candidate
        M.append(s["has"])
        V.append(np.asarray(s["v_tested"], dtype=float))
        y.append(s["labels"])
        seg.append(len(s["labels"]))
    return (np.concatenate(W), np.concatenate(M), np.concatenate(V),
            np.concatenate(y), np.array(seg, dtype=np.int64))


def main():
    bundle = load_verified()
    assert pop_digest(bundle) == AB.POP_DIGEST, "population digest mismatch"
    values, parents, osee, obrk, ocel, orel = bundle
    inv_cat, by_cat, sortedvals = C2.build(values, R.RELATIONS)
    rels = sorted(R.RELATIONS)

    rep = {"prereg": "REVIEW_RESPONSE_PREREG_2026-08-25.md",
           "population_digest": AB.POP_DIGEST, "seeds": AB.SEEDS,
           "per_seed": []}

    for seed in AB.SEEDS:
        states = AB.states_aug(values, parents, osee, obrk, ocel, orel,
                               inv_cat, by_cat, sortedvals, random.Random(seed))
        # attach the candidate's TESTED invariant value (diagnostic only, per prereg A1)
        for s in states:
            cat, tested = s["cat"], s["tested"]
            tbl = values[(cat, tested)]
            s["v_tested"] = [float(tbl[c]) for c in s["cands"]]
            s["v_parent"] = float(tbl.get(s["pobj"], 0.0))
            # raw companion invariant values of each candidate: the reviewer's w(a)
            wc = np.zeros((len(s["cands"]), AB.NC))
            for i, inv in enumerate(s["comp"][:AB.NC]):
                ct = values[(cat, inv)]
                for t, cnd in enumerate(s["cands"]):
                    u = ct.get(cnd)
                    if u is not None:
                        wc[t, i] = float(u)
            s["w_cand"] = wc

        cell = collections.defaultdict(list)
        for s in states:
            cell[(s["key"], s["rel"])].append(s)
        pairs = collections.defaultdict(set)
        for (k, rl_) in cell:
            if len(cell[(k, rl_)]) >= AB.MIN_CELL:
                pairs[k].add(rl_)
        mixed = sorted([k for k, rs in pairs.items() if len(rs) >= 2])
        cells = [(k, r) for k in mixed for r in rels if len(cell.get((k, r), [])) >= AB.MIN_CELL]

        TRs, EVs = {}, {}
        for c in cells:
            ss = cell[c]
            tri, evi = AB.split_idx(seed, c, len(ss))
            TRs[c] = [ss[t] for t in tri]
            EVs[c] = [ss[t] for t in evi]

        # ---------------- A1: proxy reconstruction ----------------
        a1 = {"binary_predicate": [], "continuous": [], "permuted_null": [],
              "spearman_proxy_quality": [], "local_Zxa": [], "per_cell": {},
              "full18_binary": [], "full18_continuous": [], "full18_spearman": []}
        rng_perm = np.random.default_rng(seed)
        for c in cells:
            rel = c[1]
            Wtr, Mtr, Vtr, _, _ = pack_proxy(TRs[c])
            Wev, Mev, Vev, yev, sgev = pack_proxy(EVs[c])
            Xtr = np.hstack([Wtr, Mtr])
            Xev = np.hstack([Wev, Mev])
            if len(Xtr) < 50:
                continue
            h = Ridge(alpha=1.0).fit(Xtr, Vtr)
            vhat = h.predict(Xev)

            # exact predicate applied to the PREDICTION, per state's own parent value
            par = np.concatenate([np.full(len(s["labels"]), s["v_parent"]) for s in EVs[c]])
            if rel == "abs_diff_le_3":
                holds_hat = np.abs(vhat - par) <= 3
                cont = np.abs(vhat - par)                    # larger => more likely to break
            else:
                holds_hat = (np.rint(vhat - par).astype(np.int64) % 2) == 0
                cont = np.abs(((vhat - par) + 1.0) % 2.0 - 1.0)   # distance from even
            binscore = (~holds_hat).astype(float)

            a1["binary_predicate"].append(float(np.nanmean(AB.batched_auc(yev, binscore, sgev))))
            a1["continuous"].append(float(np.nanmean(AB.batched_auc(yev, cont, sgev))))
            sp = spearman(vhat, Vev)
            if sp is not None:
                a1["spearman_proxy_quality"].append(sp)

            # permuted-companion null: destroy the companion->tested relation, keep marginals
            perm = rng_perm.permutation(len(Xtr))
            hp = Ridge(alpha=1.0).fit(Xtr[perm], Vtr)
            vp = hp.predict(Xev)
            if rel == "abs_diff_le_3":
                bp = (~(np.abs(vp - par) <= 3)).astype(float)
            else:
                bp = (~(((np.rint(vp - par).astype(np.int64) % 2) == 0))).astype(float)
            a1["permuted_null"].append(float(np.nanmean(AB.batched_auc(yev, bp, sgev))))

            # A1b - STRONGEST form: give the proxy the ENTIRE frozen 18-feature family and
            # ask whether the admissible features can reconstruct the withheld variable at
            # all. This is the maximal version of "semantic proxy leakage".
            TRf, EVf = AB.pack(TRs[c]), AB.pack(EVs[c])
            hb = Ridge(alpha=1.0).fit(AB.chart(TRf, "T0", rel), Vtr)
            vb = hb.predict(AB.chart(EVf, "T0", rel))
            if rel == "abs_diff_le_3":
                bb = (~(np.abs(vb - par) <= 3)).astype(float)
                cb = np.abs(vb - par)
            else:
                bb = (~(((np.rint(vb - par).astype(np.int64) % 2) == 0))).astype(float)
                cb = np.abs(((vb - par) + 1.0) % 2.0 - 1.0)
            a1["full18_binary"].append(float(np.nanmean(AB.batched_auc(yev, bb, sgev))))
            a1["full18_continuous"].append(float(np.nanmean(AB.batched_auc(yev, cb, sgev))))
            spb = spearman(vb, Vev)
            if spb is not None:
                a1["full18_spearman"].append(spb)

            # the local Z(x,a) model on the SAME rows, for a like-for-like comparison
            TRp, EVp = AB.pack(TRs[c]), AB.pack(EVs[c])
            m = AB.fit(AB.chart(TRp, "T0", rel), TRp["y"])
            if m:
                loc = float(np.nanmean(AB.batched_auc(
                    EVp["y"], AB.chart(EVp, "T0", rel) @ m["v"], EVp["seg"])))
                a1["local_Zxa"].append(loc)
                a1["per_cell"][AB.cellname(c)] = {
                    "proxy_binary": round(a1["binary_predicate"][-1], 4),
                    "proxy_continuous": round(a1["continuous"][-1], 4),
                    "local_Zxa": round(loc, 4),
                    "spearman": round(sp, 4) if sp is not None else None}

        # ---------------- A2: leave-one-cell-out, relation fixed ----------------
        a2 = {"loco": [], "per_cell": {}}
        for rel in rels:
            group = [c for c in cells if c[1] == rel]
            for held in group:
                others = [c for c in group if c != held]
                if not others:
                    continue
                Xtr = np.concatenate([AB.chart(AB.pack(TRs[c]), "T0", rel) for c in others])
                ytr = np.concatenate([AB.pack(TRs[c])["y"] for c in others])
                m = AB.fit(Xtr, ytr)                  # NO cell-identity feature of any kind
                if m is None:
                    continue
                EVp = AB.pack(EVs[held])
                v = float(np.nanmean(AB.batched_auc(
                    EVp["y"], AB.chart(EVp, "T0", rel) @ m["v"], EVp["seg"])))
                a2["loco"].append(v)
                a2["per_cell"][AB.cellname(held)] = round(v, 4)
                del Xtr, ytr
                gc.collect()

        # ---------------- A3: per-target-cell stratum-C values, for the bootstrap ----------
        # raw and T4 transfer for every ordered pair in stratum C, kept per pair so the
        # bootstrap can resample CELLS rather than seeds.
        cpairs = []
        models0 = {c: AB.fit(AB.chart(AB.pack(TRs[c]), "T0", c[1]), AB.pack(TRs[c])["y"])
                   for c in cells}
        models4 = {c: AB.fit(AB.chart(AB.pack(TRs[c]), "T4", c[1]), AB.pack(TRs[c])["y"])
                   for c in cells}
        for j in cells:
            EVp = AB.pack(EVs[j])
            X0, X4 = AB.chart(EVp, "T0", j[1]), AB.chart(EVp, "T4", j[1])
            relearn = float(np.nanmean(AB.batched_auc(
                EVp["y"], X0 @ models0[j]["v"], EVp["seg"]))) if models0[j] else None
            for i in cells:
                if i == j or i[0] == j[0] or i[1] != j[1]:
                    continue                      # stratum C only: diff pair, SAME relation
                if not (models0[i] and models4[i]):
                    continue
                cpairs.append({
                    "src": AB.cellname(i), "tgt": AB.cellname(j),
                    "raw": float(np.nanmean(AB.batched_auc(EVp["y"], X0 @ models0[i]["v"], EVp["seg"]))),
                    "t4": float(np.nanmean(AB.batched_auc(EVp["y"], X4 @ models4[i]["v"], EVp["seg"]))),
                    "relearn_tgt": relearn})

        def mean(v):
            v = [x for x in v if x is not None]
            return round(float(np.mean(v)), 4) if v else None

        rep["per_seed"].append({
            "seed": seed, "n_cells": len(cells),
            "A1": {"proxy_binary_predicate": mean(a1["binary_predicate"]),
                   "proxy_continuous": mean(a1["continuous"]),
                   "permuted_companion_null": mean(a1["permuted_null"]),
                   "proxy_regression_spearman": mean(a1["spearman_proxy_quality"]),
                   "local_Zxa_same_rows": mean(a1["local_Zxa"]),
                   "full18_proxy_binary": mean(a1["full18_binary"]),
                   "full18_proxy_continuous": mean(a1["full18_continuous"]),
                   "full18_proxy_spearman": mean(a1["full18_spearman"]),
                   "n_cells": len(a1["binary_predicate"]),
                   "per_cell": a1["per_cell"] if seed == AB.SEEDS[0] else "seed 0 only"},
            "A2": {"loco_relation_fixed": mean(a2["loco"]), "n_held_out_cells": len(a2["loco"]),
                   "per_cell": a2["per_cell"] if seed == AB.SEEDS[0] else "seed 0 only"},
            "A3_stratumC_pairs": len(cpairs),
            "_cpairs": cpairs if seed == AB.SEEDS[0] else None,
        })
        print(f"seed {seed}: A1 proxy_bin={mean(a1['binary_predicate'])} "
              f"cont={mean(a1['continuous'])} null={mean(a1['permuted_null'])} "
              f"rho={mean(a1['spearman_proxy_quality'])} local={mean(a1['local_Zxa'])} | "
              f"A2 LOCO={mean(a2['loco'])} | C pairs={len(cpairs)}")
        del states, cell, TRs, EVs, models0, models4
        gc.collect()

    # ---------------- A3 bootstrap over CELLS ----------------
    cp = rep["per_seed"][0]["_cpairs"]
    tgts = sorted({p["tgt"] for p in cp})
    by_tgt = collections.defaultdict(list)
    for p in cp:
        by_tgt[p["tgt"]].append(p)
    rngb = np.random.default_rng(BOOT_SEED)

    def recovery_of(pairs):
        raw = np.mean([p["raw"] for p in pairs])
        t4 = np.mean([p["t4"] for p in pairs])
        rl = np.mean([p["relearn_tgt"] for p in pairs if p["relearn_tgt"] is not None])
        return (t4 - raw) / (rl - raw) if (rl - raw) > 1e-9 else np.nan

    point = float(recovery_of(cp))
    boots = []
    for _ in range(N_BOOT):
        pick = rngb.choice(len(tgts), size=len(tgts), replace=True)
        sample = [q for idx in pick for q in by_tgt[tgts[idx]]]
        v = recovery_of(sample)
        if not math.isnan(v):
            boots.append(v)
    boots = np.array(boots)
    lo, hi = np.percentile(boots, [2.5, 97.5])

    agg = {
        "A1_proxy_binary_predicate": round(float(np.mean(
            [p["A1"]["proxy_binary_predicate"] for p in rep["per_seed"]])), 4),
        "A1_proxy_continuous": round(float(np.mean(
            [p["A1"]["proxy_continuous"] for p in rep["per_seed"]])), 4),
        "A1_permuted_companion_null": round(float(np.mean(
            [p["A1"]["permuted_companion_null"] for p in rep["per_seed"]])), 4),
        "A1_proxy_regression_spearman": round(float(np.mean(
            [p["A1"]["proxy_regression_spearman"] for p in rep["per_seed"]])), 4),
        "A1_local_Zxa_same_rows": round(float(np.mean(
            [p["A1"]["local_Zxa_same_rows"] for p in rep["per_seed"]])), 4),
        "A1b_full18_proxy_binary": round(float(np.mean(
            [p["A1"]["full18_proxy_binary"] for p in rep["per_seed"]])), 4),
        "A1b_full18_proxy_continuous": round(float(np.mean(
            [p["A1"]["full18_proxy_continuous"] for p in rep["per_seed"]])), 4),
        "A1b_full18_proxy_spearman": round(float(np.mean(
            [p["A1"]["full18_proxy_spearman"] for p in rep["per_seed"]])), 4),
        "A2_loco_relation_fixed": round(float(np.mean(
            [p["A2"]["loco_relation_fixed"] for p in rep["per_seed"]])), 4),
        "A3_stratumC_recovery_point": round(point, 4),
        "A3_cluster_bootstrap_over_target_cells": {
            "n_resamples": int(len(boots)), "n_clusters": len(tgts),
            "ci95_lo": round(float(lo), 4), "ci95_hi": round(float(hi), 4),
            "half_width": round(float((hi - lo) / 2), 4),
            "seed_level_SE_for_comparison": 0.0025,
            "note": "the seed-level SE was computed across 5 re-splits of the SAME 24 cells "
                    "and measured split noise, not cell-to-cell variability"},
    }
    a1v, a2v = agg["A1_proxy_binary_predicate"], agg["A2_loco_relation_fixed"]
    a1c = agg["A1_proxy_continuous"]
    a1best = max(a1v, a1c, agg["A1b_full18_proxy_binary"], agg["A1b_full18_proxy_continuous"])
    if a1best >= 0.65:
        band_a1 = "INTERPRETATION_2_SUBSTANTIALLY_SUPPORTED"
    elif a1best <= 0.55:
        band_a1 = "INTERPRETATION_2_NOT_THE_EXPLANATION"
    else:
        band_a1 = "PARTIAL"
    if a2v >= 0.68:
        band_a2 = "SHARED_STRUCTURE_EXISTS_finding3_withdrawn"
    elif a2v <= 0.57:
        band_a2 = "NO_SHARED_STRUCTURE_locality_survives_this_attack"
    else:
        band_a2 = "PARTIAL"

    rep["aggregate"] = agg
    rep["band_A1"], rep["band_A2"] = band_a1, band_a2
    for p in rep["per_seed"]:
        p.pop("_cpairs", None)
    OUT.write_text(json.dumps(rep, indent=1), encoding="utf-8")

    print()
    print("A1 proxy (binary predicate) :", agg["A1_proxy_binary_predicate"])
    print("A1 proxy (continuous)       :", agg["A1_proxy_continuous"])
    print("A1 permuted-companion null  :", agg["A1_permuted_companion_null"])
    print("A1 proxy regression spearman:", agg["A1_proxy_regression_spearman"])
    print("A1 local Z(x,a), same rows  :", agg["A1_local_Zxa_same_rows"])
    print("A1b full-18 proxy (bin/cont):", agg["A1b_full18_proxy_binary"],
          "/", agg["A1b_full18_proxy_continuous"],
          " rho", agg["A1b_full18_proxy_spearman"])
    print("   -> BAND A1:", band_a1)
    print("A2 LOCO (relation fixed)    :", agg["A2_loco_relation_fixed"])
    print("   -> BAND A2:", band_a2)
    print("A3 stratum C recovery       :", agg["A3_stratumC_recovery_point"],
          "95% CI over cells", agg["A3_cluster_bootstrap_over_target_cells"]["ci95_lo"],
          "..", agg["A3_cluster_bootstrap_over_target_cells"]["ci95_hi"])
    print("->", OUT)


if __name__ == "__main__":
    main()
