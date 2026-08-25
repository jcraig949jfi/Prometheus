"""Diomedes — round-2 audits A1-NL, A1-NL-CORR, A2-BOOT, per REVIEW_ROUND2_PREREG_2026-08-25.md.

Exactly two calculations, both auditing claims already made. Neither continues reconnaissance.

  A1-NL     nonlinear, CROSS-FITTED proxy reconstruction of the withheld tested invariant.
            Folds are assigned by CANDIDATE OBJECT IDENTITY (not row, not state), because the
            same object recurs across many states inside a cell; a row-level split would let a
            candidate's tested invariant influence its own prediction. Scores are reported
            SEPARATELY BY RELATION with their exact definitions.
  A1-NL-CORR across the 24 cells, Spearman between per-cell proxy quality and per-cell local
            action-ranking AUC. The grand rho could conceal the phenomenon under debate.
  A2-BOOT   cluster bootstrap over held-out cells on LOCO, whose 0.0054 margin against a 0.57
            gate was never defensible once A3 showed the clustered interval was 52x the seed SE.

Hyperparameters are frozen in the pre-registration and NOTHING here is selected using the
action-ranking result.

    python roles/Diomedes/review_round2_run.py
"""
import collections
import gc
import json
import pathlib
import random

import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor

import cycle001_run as R
import cycle002_run as C2
import cycle005_armB_run as AB
from harvest_cache import load_verified, digest as pop_digest
from review_response_run import spearman

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "review_round2_result.json"
N_FOLDS = 5
N_BOOT = 2000
BOOT_SEED = 20260825
GB = dict(max_iter=300, learning_rate=0.1, max_depth=None, min_samples_leaf=20)


def cont_score(rel, vhat, par):
    """Exact continuous score definitions, published in the prereg.

    abs_diff_le_3 : |vhat - parent|                      (natural margin, larger => breaks)
    equal_mod_2   : distance to the NEAREST EVEN INTEGER (parity-native, NOT generic
                    Euclidean distance: 101 and 103 score identically against an odd parent)
    """
    if rel == "abs_diff_le_3":
        return np.abs(vhat - par)
    return np.abs(((vhat - par) + 1.0) % 2.0 - 1.0)


def bin_score(rel, vhat, par):
    """Exact relation predicate applied to the reconstruction; 1.0 = predicted to break."""
    if rel == "abs_diff_le_3":
        return (~(np.abs(vhat - par) <= 3)).astype(float)
    return (~(((np.rint(vhat - par).astype(np.int64) % 2) == 0))).astype(float)


def main():
    bundle = load_verified()
    assert pop_digest(bundle) == AB.POP_DIGEST, "population digest mismatch"
    values, parents, osee, obrk, ocel, orel = bundle
    inv_cat, by_cat, sortedvals = C2.build(values, R.RELATIONS)
    rels = sorted(R.RELATIONS)

    per_seed = []
    for seed in AB.SEEDS:
        states = AB.states_aug(values, parents, osee, obrk, ocel, orel,
                               inv_cat, by_cat, sortedvals, random.Random(seed))
        for s in states:
            tbl = values[(s["cat"], s["tested"])]
            s["v_tested"] = np.array([float(tbl[c]) for c in s["cands"]])
            s["v_parent"] = float(tbl.get(s["pobj"], 0.0))
            wc = np.zeros((len(s["cands"]), AB.NC))
            for i, inv in enumerate(s["comp"][:AB.NC]):
                ct = values[(s["cat"], inv)]
                for t, cnd in enumerate(s["cands"]):
                    u = ct.get(cnd)
                    if u is not None:
                        wc[t, i] = float(u)
            s["w_cand"] = wc

        cell = collections.defaultdict(list)
        for s in states:
            cell[(s["key"], s["rel"])].append(s)
        pairs = collections.defaultdict(set)
        for k_ in cell:
            if len(cell[k_]) >= AB.MIN_CELL:
                pairs[k_[0]].add(k_[1])
        mixed = sorted([k for k, rs in pairs.items() if len(rs) >= 2])
        cells = [(k, r) for k in mixed for r in rels if len(cell.get((k, r), [])) >= AB.MIN_CELL]

        TRs, EVs = {}, {}
        for c in cells:
            ss = cell[c]
            tri, evi = AB.split_idx(seed, c, len(ss))
            TRs[c], EVs[c] = [ss[t] for t in tri], [ss[t] for t in evi]

        # ---------------- A1-NL, cross-fitted by candidate object ----------------
        res = {v: collections.defaultdict(list) for v in ("literal", "full18")}
        percell = {}
        for c in cells:
            rel = c[1]
            allst = TRs[c] + EVs[c]                  # cross-fitting spans the whole cell
            objs = sorted({o for s in allst for o in s["cands"]})
            rngf = random.Random(hash((seed, AB.cellname(c))) & 0xFFFFFFFF)
            fold_of = {o: rngf.randrange(N_FOLDS) for o in objs}

            Wl = np.concatenate([np.hstack([s["w_cand"], s["has"]]) for s in allst])
            Wf = np.concatenate([AB.chart(AB.pack([s]), "T0", rel) for s in allst])
            V = np.concatenate([s["v_tested"] for s in allst])
            fold = np.concatenate([[fold_of[o] for o in s["cands"]] for s in allst])
            par = np.concatenate([np.full(len(s["cands"]), s["v_parent"]) for s in allst])
            y = np.concatenate([s["labels"] for s in allst])
            seg = np.array([len(s["labels"]) for s in allst], dtype=np.int64)
            # evaluate only on the held-out states, matching every other Arm-B number
            is_ev = np.concatenate([np.full(len(s["labels"]), i >= len(TRs[c]))
                                    for i, s in enumerate(allst)])

            for tag, X in (("literal", Wl), ("full18", Wf)):
                vhat = np.zeros(len(V))
                for f in range(N_FOLDS):
                    tr, te = fold != f, fold == f
                    if tr.sum() < 50 or te.sum() == 0:
                        continue
                    g = HistGradientBoostingRegressor(random_state=seed, **GB).fit(X[tr], V[tr])
                    vhat[te] = g.predict(X[te])
                # restrict to eval states, then re-segment
                evsegs, off, keep = [], 0, []
                for s in allst[len(TRs[c]):]:
                    pass
                idx = np.where(is_ev)[0]
                evseg = seg[len(TRs[c]):]
                bs = bin_score(rel, vhat[idx], par[idx])
                cs = cont_score(rel, vhat[idx], par[idx])
                res[tag][f"binary_{rel}"].append(float(np.nanmean(AB.batched_auc(y[idx], bs, evseg))))
                res[tag][f"continuous_{rel}"].append(float(np.nanmean(AB.batched_auc(y[idx], cs, evseg))))
                res[tag]["binary_all"].append(res[tag][f"binary_{rel}"][-1])
                res[tag]["continuous_all"].append(res[tag][f"continuous_{rel}"][-1])
                rho = spearman(vhat[idx], V[idx])
                if rho is not None:
                    res[tag]["rho"].append(rho)
                    if tag == "full18":
                        percell.setdefault(AB.cellname(c), {})["rho_c"] = rho

                # permuted-companion null (literal only; destroys w(a)->v_tested, keeps marginals)
                if tag == "literal":
                    pv = np.zeros(len(V))
                    for f in range(N_FOLDS):
                        tr, te = fold != f, fold == f
                        if tr.sum() < 50 or te.sum() == 0:
                            continue
                        pm = np.random.default_rng(seed + f).permutation(int(tr.sum()))
                        g = HistGradientBoostingRegressor(random_state=seed, **GB).fit(
                            X[tr][pm], V[tr])
                        pv[te] = g.predict(X[te])
                    res["literal"]["permuted_null"].append(float(np.nanmean(
                        AB.batched_auc(y[idx], bin_score(rel, pv[idx], par[idx]), evseg))))

            EVp = AB.pack(EVs[c]); TRp = AB.pack(TRs[c])
            m = AB.fit(AB.chart(TRp, "T0", rel), TRp["y"])
            if m:
                loc = float(np.nanmean(AB.batched_auc(
                    EVp["y"], AB.chart(EVp, "T0", rel) @ m["v"], EVp["seg"])))
                percell.setdefault(AB.cellname(c), {})["local_auc_c"] = loc
            gc.collect()

        # ---------------- A1-NL-CORR ----------------
        pc = [(v["rho_c"], v["local_auc_c"]) for v in percell.values()
              if "rho_c" in v and "local_auc_c" in v]
        corr = spearman(np.array([a for a, _ in pc]), np.array([b for _, b in pc])) if len(pc) > 2 else None

        # ---------------- A2 LOCO per held-out cell (for the bootstrap) ----------------
        loco = {}
        for rel in rels:
            group = [c for c in cells if c[1] == rel]
            for held in group:
                others = [c for c in group if c != held]
                if not others:
                    continue
                Xtr = np.concatenate([AB.chart(AB.pack(TRs[c]), "T0", rel) for c in others])
                ytr = np.concatenate([AB.pack(TRs[c])["y"] for c in others])
                m = AB.fit(Xtr, ytr)
                if m:
                    EVp = AB.pack(EVs[held])
                    loco[AB.cellname(held)] = float(np.nanmean(AB.batched_auc(
                        EVp["y"], AB.chart(EVp, "T0", rel) @ m["v"], EVp["seg"])))
                del Xtr, ytr
                gc.collect()

        def mn(v):
            v = [x for x in v if x is not None]
            return round(float(np.mean(v)), 4) if v else None

        row = {"seed": seed, "n_cells": len(cells),
               "A1NL": {t: {k: mn(v) for k, v in res[t].items()} for t in res},
               "A1NL_CORR_spearman_rho_c_vs_local_auc_c": round(corr, 4) if corr is not None else None,
               "A2_loco_mean": mn(list(loco.values())),
               "_loco": loco if seed == AB.SEEDS[0] else None,
               "_percell": percell if seed == AB.SEEDS[0] else None}
        per_seed.append(row)
        print(f"seed {seed}: A1NL literal bin/cont "
              f"{row['A1NL']['literal'].get('binary_all')}/{row['A1NL']['literal'].get('continuous_all')} "
              f"| full18 {row['A1NL']['full18'].get('binary_all')}/{row['A1NL']['full18'].get('continuous_all')} "
              f"rho {row['A1NL']['full18'].get('rho')} | null {row['A1NL']['literal'].get('permuted_null')} "
              f"| CORR {row['A1NL_CORR_spearman_rho_c_vs_local_auc_c']} | LOCO {row['A2_loco_mean']}")
        del states, cell, TRs, EVs
        gc.collect()

    # ---------------- A2-BOOT ----------------
    loco0 = per_seed[0]["_loco"]
    keys = sorted(loco0)
    vals = np.array([loco0[k] for k in keys])
    rngb = np.random.default_rng(BOOT_SEED)
    boots = np.array([vals[rngb.integers(0, len(vals), len(vals))].mean() for _ in range(N_BOOT)])
    lo, hi = np.percentile(boots, [2.5, 97.5])
    straddles = bool(lo <= 0.57 <= hi)

    def agg(path):
        out = []
        for p in per_seed:
            v = p["A1NL"]
            for k in path:
                v = v.get(k) if isinstance(v, dict) else None
            if v is not None:
                out.append(v)
        return round(float(np.mean(out)), 4) if out else None

    variants = {
        "literal_binary": agg(["literal", "binary_all"]),
        "literal_continuous": agg(["literal", "continuous_all"]),
        "full18_binary": agg(["full18", "binary_all"]),
        "full18_continuous": agg(["full18", "continuous_all"]),
    }
    per_rel = {}
    for rel in rels:
        for t in ("literal", "full18"):
            per_rel[f"{t}_binary_{rel}"] = agg([t, f"binary_{rel}"])
            per_rel[f"{t}_continuous_{rel}"] = agg([t, f"continuous_{rel}"])

    local = 0.7392
    best = max(v for v in variants.values() if v is not None)
    band = ("NAVIGATIONAL_READING_WITHDRAWN" if best >= 0.65 else
            "PROXY_NOT_CARRYING_LOCAL_SIGNAL" if best <= 0.55 else "PARTIAL")
    corr_m = [p["A1NL_CORR_spearman_rho_c_vs_local_auc_c"] for p in per_seed
              if p["A1NL_CORR_spearman_rho_c_vs_local_auc_c"] is not None]
    corr_mean = round(float(np.mean(corr_m)), 4) if corr_m else None
    corr_band = ("INTERPRETATION_2_STRENGTHENED" if corr_mean is not None and corr_mean >= 0.5 else
                 "PROXY_NOT_WHAT_MAKES_A_CELL_LEARNABLE" if corr_mean is not None and corr_mean <= 0.2
                 else "INDETERMINATE")

    rep = {"prereg": "REVIEW_ROUND2_PREREG_2026-08-25.md",
           "population_digest": AB.POP_DIGEST,
           "gradient_boosting_params": GB, "n_folds": N_FOLDS,
           "cross_fit_unit": "candidate object identity",
           "A1NL_variants": variants,
           "A1NL_best": best, "A1NL_band": band,
           "A1NL_span_equivalent_note":
               "X% below is the fraction of the LOCAL above-chance AUC span that this "
               "independent proxy mechanism reproduces. It is NOT a decomposition of the local "
               "model's performance and must not be written as variance attribution.",
           "A1NL_span_equivalent": {k: (round((v - 0.5) / (local - 0.5), 4) if v else None)
                                    for k, v in variants.items()},
           "A1NL_per_relation": per_rel,
           "A1NL_permuted_null": agg(["literal", "permuted_null"]),
           "A1NL_rho_full18": agg(["full18", "rho"]),
           "local_Zxa_reference": local,
           "A1NL_CORR_mean": corr_mean, "A1NL_CORR_band": corr_band,
           "A2_loco_point": round(float(vals.mean()), 4),
           "A2_BOOT": {"n_clusters": len(vals), "n_resamples": N_BOOT,
                       "ci95_lo": round(float(lo), 4), "ci95_hi": round(float(hi), 4),
                       "gate": 0.57, "straddles_gate": straddles,
                       "band": "UNRESOLVED_gate_within_interval" if straddles
                               else "RESOLVED_below_gate" if hi < 0.57 else "RESOLVED_above_gate"},
           "per_seed": [{k: v for k, v in p.items() if not k.startswith("_")} for p in per_seed],
           "seed0_per_cell": per_seed[0]["_percell"], "seed0_loco": loco0}
    OUT.write_text(json.dumps(rep, indent=1), encoding="utf-8")

    print()
    print("A1-NL variants      :", json.dumps(variants))
    print("A1-NL span-equiv    :", json.dumps(rep["A1NL_span_equivalent"]))
    print("A1-NL per relation  :", json.dumps(per_rel))
    print("A1-NL permuted null :", rep["A1NL_permuted_null"], "| rho", rep["A1NL_rho_full18"])
    print("   -> BAND:", band, "(best", best, "vs local", local, ")")
    print("A1-NL-CORR          :", corr_mean, "->", corr_band)
    print("A2 LOCO point       :", rep["A2_loco_point"])
    print("A2-BOOT 95% CI      :", rep["A2_BOOT"]["ci95_lo"], "..", rep["A2_BOOT"]["ci95_hi"],
          "| straddles 0.57:", straddles, "->", rep["A2_BOOT"]["band"])
    print("->", OUT)


if __name__ == "__main__":
    main()
